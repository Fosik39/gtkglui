#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Виджеты для OpenGL+GTK

# Чужие модули
import gtk
import cairo
import OpenGL
import copy
import inspect
import glib

OpenGL.ERROR_CHECKING = False
OpenGL.ERROR_LOGGING = False
from OpenGL.GL import *

# Свои модули
import gltools
import tools
import colors

__ehid__ = None
key_handler_proc = None
key_handler_args = list()

l_len = len

DEFAULT_FONT_FACE = 'Liberation Sans'
DEFAULT_FONT_SIZE = 18


# Реализация декоратора "@private" для методов классов
# http://blog.sujeet.me/2012/10/python-tinkering-a-decorator-to-implement-private-methods-I.html
def private(method):
    class_name = inspect.stack()[1][3]

    def privatized_method(*args, **kwargs):
        call_frame = inspect.stack()[1][0]
        # Only methods of same class should be able to call
        # private methods of the class, and no one else.
        if call_frame.f_locals.has_key('self'):
            caller_class_name = call_frame.f_locals['self'].__class__.__name__
            if caller_class_name == class_name:
                return method(*args, **kwargs)
        raise Exception("can't call private method")

    return privatized_method


def init(widget):
    global __ehid__
    __ehid__ = widget.connect('key-press-event', key_dispatcher)


def connect_key_handler(handler_proc, *args):
    """
    :param handler_proc: порцедура для обработки нажатия клавиши
    :param args: аргументы передаваемые в в процедуру handler_proc
    """
    global key_handler_proc, key_handler_args
    key_handler_proc = handler_proc
    key_handler_args = args


def disconnect_key_hadler():
    global key_handler_proc, key_handler_args
    key_handler_proc = __empty_key_handler_proc__
    key_handler_args = None


def __empty_key_handler_proc__(window, event, *key_handler_args):
    pass


def key_dispatcher(window, event):
    if key_handler_args is None:
        key_handler_proc(window, event)
        return False
    if key_handler_proc:
        key_handler_proc(window, event, *key_handler_args)
    return False


def ALIGN_H_CENTER(pos, width, xadvance, cpx):
    """
    Возвращает смещение по оси X, для выравнивания горизонтального
    по центру внутри заданной области
    :param pos: Точка верхнего левого угла области
    :param width: Ширина области
    :param xadvance: Ширина текста
    :param cpx: Относительная ширина оставляемого свободного места
    :return:
    """
    width0 = int(width + 0.5)
    x = int(pos[0] + (width - xadvance) * cpx + 0.5)
    if x < pos[0]: x = pos[0]
    return width0, x


def ALIGN_H_LEFT(pos, width, xadvance, cpx):
    """
    Возвращает смещение по оси X, для выравнивания горизонтального
    по левому краю внутри заданной области
    :param pos: Точка верхнего левого угла области
    :param width: Ширина области
    :param xadvance: Ширина текста
    :param cpx: Относительная ширина оставляемого свободного места
    :return:
    """
    width0 = int(width - width * cpx + 0.5)
    x = int(pos[0] + width * cpx + 0.5)
    return width0, x


def cc_draw_text_shadow(cc, text, ybearing):
    shadow_col = (0.0, 0.0, 0.0, 1.0)
    # тень справо
    cc.set_source_rgba(*shadow_col)
    cc.move_to(2, -ybearing + 1)
    cc.show_text(text)
    # тень внизу
    cc.set_source_rgba(*shadow_col)
    cc.move_to(1, -ybearing + 2)
    cc.show_text(text)
    # тень слево
    cc.set_source_rgba(*shadow_col)
    cc.move_to(0, -ybearing + 1)
    cc.show_text(text)
    # тень сверху
    cc.set_source_rgba(*shadow_col)
    cc.move_to(1, -ybearing)
    cc.show_text(text)
    return 1, 1


class GlFont(object):
    font_items = dict()

    def __init__(self, face=DEFAULT_FONT_FACE, size=DEFAULT_FONT_SIZE, predraw=None):
        assert type(face) is str
        assert type(size) is int
        self.cc0 = cairo.Context(gltools.__cis0__)  # Поверхность для вычисления размера текста
        self.cc0.select_font_face(face)
        self.cc0.set_font_size(size)
        self.face = face  # название начертания букв
        self.size = size  # размер букв
        self.texture_id = glGenTextures(1)
        if predraw is not None:
            assert inspect.isfunction(predraw)
            self.predraw = predraw

    def __new__(cls, face=DEFAULT_FONT_FACE, size=DEFAULT_FONT_SIZE, predraw=None):
        assert type(face) is str
        assert type(size) is int
        font_item = GlFont.font_items.get((face, size))
        if font_item is not None:
            print 'glwidget.py: шрифт из кэша: \'%s %u\'' % (face, size)
            return font_item
        else:
            font_item = super(GlFont, cls).__new__(cls)
            GlFont.font_items[(face, size)] = font_item
            print 'glwidget.py: шрифт создан \'%s %u\'' % (face, size)
            return font_item

    def get_text_width(self, text):
        xbearing, ybearing, width, height0, xadvance, yadvance = self.cc0.text_extents(text)
        return int(xadvance + 0.5)

    def get_text_hight(self):
        fascent, fdescent, fheight, fxadvance, fyadvance = self.cc0.font_extents()
        return int(fheight)

    def draw_text(self, pos, text, color=colors.WHITE):
        # Вычислить размер в пикселях который будет занимать текст
        xbearing, ybearing, width, height0, xadvance, yadvance = self.cc0.text_extents(text)
        fascent, fdescent, fheight, fxadvance, fyadvance = self.cc0.font_extents()
        height = (text.count('\n') + 1) * fheight
        # Нарисовать текcт в текстуру:
        # 1) создать изображение текста в буфере
        cis = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(xadvance), int(height))
        cc = cairo.Context(cis)
        cc.select_font_face(self.face)
        cc.set_font_size(self.size)
        cc.set_operator(cairo.OPERATOR_SOURCE)
        cc.set_source_rgba(1.0, 1.0, 1.0, 1.0)

        y = fascent
        for t in text.split('\n'):
            cc.move_to(0, y)
            cc.show_text(t)
            y += fheight  # -ybearing

        # 2) Назначить буфер в текстуру
        texture = gltools.data_to_texture(self.texture_id, cis.get_data(), int(xadvance), int(height))
        cis.finish()
        gltools.draw_texture(texture, (pos[0], pos[1] - fheight), color)
        return xbearing, fheight, int(xadvance), int(height), xadvance, yadvance


__redraw_queue__ = dict()


# noinspection PyAttributeOutsideInit
class GlWidget(object):
    # TODO: Добавить использование свойств python, чтобы добавлять в очередь рисования
    # более изберательным способом, не опасаясь попасть на рекурсию, и тогда
    # можно будет менть атрибуты даже в redra(), а пока так:
    # В методе GlWidget:redraw атрибуты экземпляра можно только читать, но изменять нельзя
    image_surface0 = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)
    cairo_context = cairo.Context(image_surface0)
    cairo_context.select_font_face(DEFAULT_FONT_FACE)
    cairo_context.set_font_size(DEFAULT_FONT_SIZE)
    db = 0
    stil = True  # Флаг. Когда установлен, StaticText2 присутствует в очереди на рисование
    force_redraw = True

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        __redraw_queue__[id(self)] = self

    def put_to_redraw(self):
        __redraw_queue__[id(self)] = self

    def __draw_list__(self):
        glCallList(self.dl)

    def hide(self):
        if self.draw == self.__draw_list__:
            self.disconnect()
        self.draw = self.__draw_none__
        GlWidget.force_redraw = True

    # noinspection PyAttributeOutsideInit
    def show(self):
        """
        Элемент для которого show() был вызван последним, находится в фокусе,
        если использует key_handler_...
        :return:
        """
        if self.draw == self.__draw_none__:
            self.connect()
        self.draw = self.__draw_list__
        GlWidget.force_redraw = True

    def __draw_none__(self):
        pass

    def disconnect(self):
        pass

    def connect(self):
        pass

    def __del__(self):
        self.disconnect()
        self_id = id(self)
        if self_id in __redraw_queue__.keys():
            del __redraw_queue__[self_id]


def redraw_queue():
    for i in __redraw_queue__.values():
        i.redraw()
    __redraw_queue__.clear()


class StaticText(GlWidget):
    """
    Выводит текст на экран. Текст может содержать перевод строки
    """

    def __init__(self, gda, pos=(0, 0), text='', font=None, user_data=None, color=colors.GRID):
        self.draw = self.__draw_list__
        self.pos = pos
        self.parent_height = gda.allocation.height
        self.dl = glGenLists(1)
        self.text = text
        self.color = color
        self.user_data = user_data
        self.rdc = [GL_COMPILE_AND_EXECUTE]
        if font is None:
            self.font = GlFont()
        else:
            self.font = font

    def redraw(self):
        glNewList(self.dl, self.rdc[0])
        self.font.draw_text(self.pos, self.text, self.color)
        glEndList()
        self.rdc[0] = GL_COMPILE

    def __del__(self):
        super(StaticText, self).__del__()
        glDeleteLists(self.dl, 1)


class Picture(GlWidget):
    def __init__(self, gda, pos, texture, scale=[1.0, 1.0, 1.0], color=colors.WHITE, user_data=None):
        assert type(gda) is gtk.DrawingArea
        assert type(pos) is tuple
        assert l_len(pos) == 2
        assert type(pos[0]) is int
        assert type(pos[1]) is int
        assert type(scale) is list
        assert len(scale) == 3
        assert (type(scale[0]) is float) and (scale[0] >= 0)
        assert (type(scale[1]) is float) and (scale[1] >= 0)
        assert (type(scale[2]) is float) and (scale[2] >= 0)
        assert len(color) == 4
        for col in color:
            assert type(col) is int
            assert 0 <= col <= 255

        self.draw = self.__draw_list__
        self.pos = pos
        self.dl = glGenLists(1)
        assert glIsList(self.dl)
        self.scale = scale
        self.color = color

        self.texture = texture

        self.mirror = gltools.MIRROR_NONE  # Зеркалирование
        self.user_data = user_data

    def get_textures(self):
        return self.texture

    def __del__(self):
        super(Picture, self).__del__()
        glDeleteLists(self.dl, 1)

    def redraw(self):
        glNewList(self.dl, GL_COMPILE)
        gltools.draw_texture_scale(self.texture, self.pos, self.scale, self.color, self.mirror)
        glEndList()


class PictureRotate(Picture):
    def __init__(self, gda, pos, texture, ang=0, color=colors.WHITE):
        super(PictureRotate, self).__init__(gda, pos, texture, scale=[1.0, 1.0, 1.0], color=color)
        self.ang = ang

    def redraw(self):
        glNewList(self.dl, GL_COMPILE)
        gltools.draw_texture_rotate(self.texture, self.pos, self.ang, self.color, self.mirror, self.scale)
        glEndList()


class PictureState(Picture):
    def __init__(self, gda, pos, textures, state=0, color=colors.WHITE, user_data=None):
        super(PictureState, self).__init__(gda, pos, textures, color=color)
        self.state = state
        self.user_data = user_data

    def redraw(self):
        assert len(self.texture) > self.state
        glNewList(self.dl, GL_COMPILE)
        gltools.draw_texture(self.texture[self.state], self.pos, self.color)
        glEndList()


class Entry(GlWidget):
    def __init__(self, gda, pos, text=' ', size=(150, 17), font_name=DEFAULT_FONT_FACE,
                 font_size=DEFAULT_FONT_SIZE,
                 text_color=(255, 255, 255, 127), bg_color=(255, 127, 127, 255)):
        assert type(gda) is gtk.DrawingArea
        assert type(pos) is tuple
        assert l_len(pos) == 2
        assert type(size) is tuple
        assert l_len(size) == 2
        assert type(font_name) is str
        assert type(font_size) is int
        assert type(text_color) is tuple
        assert l_len(text_color) == 4
        assert type(bg_color) is tuple
        assert l_len(bg_color) == 4

        self.draw = self.__draw_list__
        self.gda = gda
        self.ancestor = self.gda.get_ancestor(gtk.Window)
        self.font_name = font_name
        self.font_size = font_size
        self.text_color = text_color
        self.bg_color = bg_color
        self.font = GlFont(font_name, font_size)
        self.pos = pos
        self.size = size
        self.text = text.encode('utf-8')
        self.dl = glGenLists(1)
        self.ehid0 = None
        self.ehid1 = None
        self.ehid2 = self.gda.connect('button_press_event', self.on_button_press)
        self.timer_id = None
        self.connect()
        self.cover = False
        self.cur_index = 0
        self.cur_tick = 0
        self.cur_pos = self.pos[0]
        self.cur_colors = ((255, 255, 255, 0), (255, 255, 255, 255))
        self.cur_col = self.cur_colors[self.cur_tick]
        self.on_edit_done = None

    def __del__(self):
        super(Entry, self).__del__()
        glDeleteLists(self.dl)

    def redraw(self):
        glNewList(self.dl, GL_COMPILE)
        pos = self.pos[0], self.pos[1]
        p0 = pos
        p1 = pos[0] + self.size[0], pos[1]
        p2 = pos[0] + self.size[0], pos[1] + self.size[1]
        p3 = pos[0], pos[1] + self.size[1]
        gltools.draw_lines((p0, p1, p2, p3, p0), self.bg_color, 1)
        pts = p1, p0, p3, p2
        # Подкладка
        gltools.draw_polygon(pts, (0, 0, 0, 240))
        # Введённый текст
        self.font.draw_text((self.pos[0], self.pos[1] + self.size[1] + 2), self.text)
        # Курсор
        gltools.draw_line((self.cur_pos, self.pos[1] + self.size[1]), (self.cur_pos, self.pos[1]), self.cur_col)
        # Рамка
        glEndList()

    def on_timer(self, *args):
        # Смена фаз курсора
        self.cur_tick += 1
        self.cur_tick %= l_len(self.cur_colors)
        self.cur_col = self.cur_colors[self.cur_tick]
        return True

    def on_button_press(self, event, *args):
        if self.cover:
            connect_key_handler(self.__on_key_press__)
        else:
            self.cur_tick = 0
            if self.timer_id:
                glib.source_remove(self.timer_id)
                self.timer_id = None
            if self.ehid1:
                self.ehid1 = None
        self.cur_pos = self.pos[0] + gltools.get_str_width(self.text[:self.cur_index], self.font_name, self.font_size)

    def __motion_notify__(self, *args):
        event = args[1]
        self.cover = tools.check_rect(self.size[0], self.size[1], self.pos, event.x, event.y)
        col = self.text_color
        self.text_color = col[0], col[1], col[2], 100 + 100 * self.cover
        return False

    def __on_key_press__(self, window, event):
        # Сохранить состояние, на случай если изменения будут не допустимыми
        save_text = copy.deepcopy(self.text)
        save_cur_index = self.cur_index
        save_cur_pos = self.cur_pos
        # Преобразовать данные события в распознаваемые константы
        char_code = gtk.gdk.keyval_to_unicode(event.keyval)
        char_name = gtk.gdk.keyval_name(event.keyval)
        cur_shift = 0
        if char_code != 0:
            text_l = list(self.text.decode('utf-8'))
            text_l.insert(self.cur_index, unichr(char_code))
            cur_shift = 1
            self.text = ''
            for c in text_l:
                self.text += c
        if char_name == 'Delete':
            if l_len(self.text.decode('utf-8')):
                text_l = list(self.text.decode('utf-8'))
                if self.cur_index < l_len(text_l):
                    text_l.pop(self.cur_index)
                self.text = ''
                for c in text_l:
                    self.text += c
        elif char_name == 'Return':
            if self.on_edit_done is not None:
                self.on_edit_done(self)
        elif char_name == 'Left':
            cur_shift = -1
        elif char_name == 'Right':
            cur_shift = 1
        elif char_name == 'BackSpace':
            if l_len(self.text.decode('utf-8')):
                text_l = list(self.text.decode('utf-8'))
                if self.cur_index > 0:
                    text_l.pop(self.cur_index - 1)
                self.text = ''
                for c in text_l:
                    self.text += c
                cur_shift = -1
        self.cur_index += cur_shift
        if self.cur_index < 0:
            self.cur_index = 0
        if l_len(self.text) > 0:
            max_index = l_len(self.text.decode('utf-8'))
            if self.cur_index > max_index:
                self.cur_index = max_index
        if l_len(self.text) == 0:
            self.cur_index = 0
        s0 = tools.str_cut(self.text, self.cur_index)
        self.cur_pos = self.pos[0] + self.font.get_text_width(s0)
        text_right_x = self.pos[0] + self.font.get_text_width(self.text)
        if (text_right_x >= self.pos[0] + self.size[0]) and (char_code != 0):
            self.text = save_text
            self.cur_index = save_cur_index
            self.cur_pos = save_cur_pos
        return True

    def connect(self):
        if self.ehid0 is None:
            self.ehid0 = self.gda.connect('motion_notify_event', self.__motion_notify__)
        connect_key_handler(self.__on_key_press__)
        if self.timer_id is None:
            self.timer_id = glib.timeout_add(150, self.on_timer)
        self.cur_pos = self.pos[0]
        self.cur_index = 0

    def disconnect(self):
        disconnect_key_hadler()
        if self.ehid0:
            self.gda.disconnect(self.ehid0)
            self.ehid0 = None
        if self.ehid1:
            self.ehid1 = None
        if self.timer_id:
            glib.source_remove(self.timer_id)
            self.timer_id = None


class Button(GlWidget):
    pressed = False

    def __init__(self, gda, pos, text, textures,
                 text_color=colors.BUTTON_TEXT, auto=1, user_proc=None,
                 user_data=None, check_part=((1.0 / 6.0), 0.5)):
        assert type(text_color) is tuple  # Цвет должен состоять из четырёх компонент в кортеже
        assert l_len(text_color) == 4  # Цвет должен состоять из четырёх компонент в кортеже
        for c in text_color:
            assert type(c) is int  # Значение цвета должно быть целым
            assert 0 <= c <= 255  # Значение цвета должно быть от 0 до 255 включительно
        assert l_len(check_part) == 2  # Параметр выравнивания состоит из двух элементов типа float
        assert type(check_part[0]) is float  # Параметр выравнивания состоит из двух элемнтов типа float
        assert type(check_part[1]) is float  # Параметр выравнивания состоит из двух элемнтов типа float
        if user_proc is not None:
            assert inspect.isfunction(user_proc)  # Должна быть функция
        if text is not None:
            assert type(text) is str  # Должна быть строка
        assert type(gda) is gtk.DrawingArea
        assert type(pos) is tuple
        assert l_len(pos) == 2
        assert type(pos[0]) is int
        assert type(pos[1]) is int
        assert type(auto) is int

        self.draw = self.__draw_list__
        self.gda = gda

        self.pos = pos

        # Относительное положение надписи.
        # check_part[0]: 0.5 - посередине, меньше 0.5 - левее
        # check_part[1]: 0.5 - посередине, меньше 0.5 - выше
        self.check_part = check_part

        # Надпись
        if text is not None:
            self.text = text.encode('utf-8')
        else:
            self.text = None
        self.text_color = text_color

        # Display list
        self.dl = glGenLists(1)
        self.texture_id = glGenTextures(1)

        # Состояние кнопки и текстура
        self.state = 0
        self.pressed = False
        if type(textures[0]) is tuple:
            self.textures = textures
        else:
            self.textures = (textures,)
        for item in self.textures:
            assert glIsTexture(item[
                                   0])  # Должен быть дейсвительный идентификатор текстуры. Формат: (идентификатор текстуры openGL, ширина int, высота int), (,,))
            assert type(item[
                            1]) is int  # Должна быть ширина, целое. Формат: (идентификатор текстуры openGL, ширина int, высота int), (,,))
            assert type(item[
                            2]) is int  # Должна быть высота, целое. Формат: (идентификатор текстуры openGL, ширина int, высота int), (,,))

        # Наведение мыши
        self.cover = 0
        self.alphas = (190, 240)  # Прозрачность при наведённой и ненаведённой мыши
        self.color = (255, 255, 255, 255)

        # События
        self.ehid0, self.ehid1, self.ehid2 = None, None, None
        self.connect()

        # Пользовательская процедура и данные
        self.user_proc = user_proc
        self.user_data = user_data

        # Группа, если будет радиокнопкой
        self.group = None

        # Можно ли отжать кнопку радиогруппы
        self.unfixed = False

        # Режим отработки нажатий
        assert type(auto) is int  # Режим работы кнопки должен быть целым числом
        assert auto in (0, 1, 2)  # Режим работы кнопки может принимать только эти значения
        self.auto = auto  # 0 - не управляется(не меняется при нажатии), 1 - фиксируемая (меняется после нажатия), 2 - без фиксации (мигает при нажатии)
        self.idts = None  # Таймер для режима self.auto:2

        self.click_count = 0
        self.outlines = None
        self.align = ALIGN_H_LEFT  # Процедура выравнивания текста

        self.mirror = gltools.MIRROR_NONE

        self.texture2 = None
        self.text_height = DEFAULT_FONT_SIZE

    def connect(self):
        self.ehid0 = self.gda.connect('motion-notify-event', self.__motion_notify__)
        self.ehid1 = self.gda.connect('button-release-event', self.button_release)
        self.ehid2 = self.gda.connect('button-press-event', self.button_press)

    def button_press(self, *args):
        self.pressed = self.cover
        Button.pressed = True

    def disconnect(self):
        self.gda.disconnect(self.ehid0)
        self.gda.disconnect(self.ehid1)
        self.gda.disconnect(self.ehid2)
        if self.idts is not None:
            glib.source_remove(self.idts)

    def __del__(self):
        super(Button, self).__del__()
        glDeleteLists(self.dl, 1)
        glDeleteTextures(self.texture_id)
        self.cis.finish()

    def __on_timeout_state__(self):
        self.state = 0
        self.idts = None
        return False

    def button_release(self, *args):
        Button.pressed = False
        if not (self.cover and self.pressed):
            self.pressed = False
            return
        if self.group is None:
            if self.auto == 1:
                self.state = (self.state + 1) % l_len(self.textures)
            elif self.auto == 2:
                if self.idts is None:
                    self.idts = glib.timeout_add(100, self.__on_timeout_state__)
                    self.state = 1
            if self.user_proc is not None:
                self.user_proc(self)
                assert 0 <= self.state < l_len(
                    self.textures)  # Количество состояний должно быть не больше количества текстур
        else:
            assert l_len(self.textures) == 2  # Количество текстур радиокнопки должно быть равно двум
            if not self.unfixed:
                for btn in self.group:
                    state = btn.state
                    btn.state = int(id(btn) == id(self))  # Этот экземпляр кнопки включить, а другие выключить
                    if btn.state != state:
                        if btn.user_proc is not None:
                            btn.user_proc(btn)
                            assert 0 <= btn.state < l_len(
                                self.textures)  # Количество состояний должно быть не больше количества текстур
            else:
                for btn in self.group:
                    state = btn.state
                    if id(btn) == id(self):  # Этому экземпляру кнопки сменить состояние, а другие выключить
                        btn.state += 1
                        btn.state %= 2
                    else:
                        btn.state = 0
                    if btn.state != state:
                        if btn.user_proc is not None:
                            btn.user_proc(btn)
                            assert 0 <= btn.state < l_len(
                                self.textures)  # Количество состояний должно быть не больше количества текстур

    def __motion_notify__(self, *args):
        event = args[1]
        width = self.textures[self.state][1]
        height = self.textures[self.state][2]
        cover = tools.check_rect(width, height, self.pos, event.x, event.y)
        # Чтобы лишний раз не добавилось в очередь перерисовки
        if self.cover != cover:
            self.cover = cover
        return False  # False  # Returns: True to stop other handlers from being invoked for the event. False to propagate the event further.

    def redraw(self):
        if len(self.textures) < self.state:
            raise ValueError('%s:%s, state:%u, len(textures):%u' % (self, self.text, self.state, len(self.textures)))
        texture1 = self.textures[self.state][0]
        width = self.textures[self.state][1]
        height = self.textures[self.state][2]
        # изображение кнопки
        alpha = self.alphas[self.cover and (not Button.pressed)]
        color = self.color[0], self.color[1], self.color[2], alpha

        if self.text and (self.texture2 is None):
            # Вычислить размер в пикселях который будет занимать текст
            xbearing, ybearing, text_width, text_height, xadvance, yadvance = GlWidget.cairo_context.text_extents(
                self.text)
            fascent, fdescent, fheight, fxadvance, fyadvance = GlWidget.cairo_context.font_extents()

            # Выравнивание
            width_a, x_a = self.align(self.pos, width, xadvance, self.check_part[0])

            # Нарисовать текcт в текстуру:
            # 1) создать изображение текста в буфере
            cis = cairo.ImageSurface(cairo.FORMAT_ARGB32, width_a, height)
            cc = cairo.Context(cis)
            cc.select_font_face(DEFAULT_FONT_FACE)
            cc.set_font_size(self.text_height)

            # тень
            cc_draw_text_shadow(cc, self.text, ybearing)

            # центр
            cc.set_source_rgba(1.0, 1.0, 1.0, 0.8)
            cc.move_to(1, - ybearing + 1)
            cc.show_text(self.text)

            # 2) Назначить буфер с текстом в текстуру
            texture2 = gltools.data_to_texture(self.texture_id, cis.get_data(), width_a, height)
            cis.finish()

            y = int(self.pos[1] + (height - fheight + fdescent) * self.check_part[1] + 0.5)

        # Сборка потока команд в display list
        glNewList(self.dl, GL_COMPILE)
        # 3) Нарисовать фон кнопки
        gltools.draw_texture((texture1, width, height), self.pos, color, self.mirror)
        # 4) Нарисовать текстуру с текстом
        if self.text:
            gltools.draw_texture(texture2, (x_a, y), self.text_color)
        if self.outlines:
            gltools.draw_lines(self.outlines, self.outline_colors[self.outline_colori])
        glEndList()


class ButtonRing(Button):
    """
    Кнопка в форме кольца
    """

    def __init__(self, gda, pos, textures, r1, r2, state_colors=(colors.ALPHA0, colors.RED1), user_proc=None,
                 user_data=None):
        """
        :param gda: Контекст opengl-gtk
        :param pos: Координаты верхнего левого угла на экране в пикселях
        :param textures: Текстуры
        :param r1: Внутренний радиус в пикселях
        :param r2: Внешний радиус в пикселях
        :param state_colors: Цвета состояний
        :param user_proc: Пользовательская процедура
        :param user_data: Пользовательские данные
        """
        super(ButtonRing, self).__init__(gda, pos, None, textures, (255, 255, 255, 255), 0, user_proc, user_data)
        # Формальная проверка фходных данных
        assert (type(r1) is int) and (r1 > 0)  # r1 - внутренний радиус
        assert (type(r2) is int) and (r2 > 0)  # r2 - внешний радиус
        assert r2 > r1  # Внешний радиус должен быть больше внутреннего
        self.state_colors = state_colors
        self.auto = 0
        self.r1 = r1
        self.r2 = r2

    def __motion_notify__(self, *args):
        event = args[1]
        x = self.pos[0] + (self.textures[0][1] >> 1)
        y = self.pos[1] + (self.textures[0][2] >> 1)
        cover = tools.check_ring(self.r1, self.r2, x, y, event.x, event.y)
        # Чтобы лишний раз не добавилось в очередь перерерисовки
        if self.cover != cover:
            self.cover = cover
        return False  # False  # Returns: True to stop other handlers from being invoked for the event. False to propagate the event further.

    def redraw(self):
        assert len(self.textures) > self.state
        alpha = self.alphas[self.cover and (not Button.pressed)]
        r, g, b, a = self.state_colors[self.state]
        color = r, g, b, alpha
        glNewList(self.dl, GL_COMPILE)
        # print '->glwidgets.py:redraw():', self.textures[0], self.pos, color
        gltools.draw_texture(self.textures[0], self.pos, color)
        glEndList()

    def __del__(self):
        super(ButtonRing, self).__del__()


class ButtonAnimated(Button):
    def __init__(self, gda, pos, textures, outline_colors, user_proc=None, user_data=None):
        self.__is_playing__ = False
        self.__timer_id__ = None
        super(ButtonAnimated, self).__init__(gda, pos, None, textures, (255, 255, 255, 255), False, user_proc,
                                             user_data)
        self.__on_timer__()
        self.outline_colors = outline_colors
        self.outline_colori = 0

    def play(self, rate_ms=150):
        if self.__timer_id__ is None:
            self.__timer_id__ = glib.timeout_add(rate_ms, self.__on_timer__)
            self.__is_playing__ = True
            self.__rate_ms__ = rate_ms

    def stop(self):
        if self.__timer_id__ is not None:
            self.__timer_id__ = None
            self.__is_playing__ = False

    def __on_timer__(self):
        self.state = (self.state + 1) % l_len(self.textures)
        width = self.textures[self.state][1]
        height = self.textures[self.state][2]
        self.outlines = self.pos \
            , (self.pos[0] + width, self.pos[1]) \
            , (self.pos[0] + width, self.pos[1] + height) \
            , (self.pos[0], self.pos[1] + height) \
            , self.pos
        return self.__is_playing__

    def __del__(self):
        super(ButtonAnimated, self).__del__()

    def connect(self):
        super(ButtonAnimated, self).connect()
        if self.__is_playing__:
            if self.__timer_id__ is None:
                self.__timer_id__ = glib.timeout_add(self.__rate_ms__, self.__on_timer__)

    def disconnect(self):
        super(ButtonAnimated, self).disconnect()
        if self.__timer_id__:
            if self.__timer_id__ is not None:
                glib.timeout_remove(self.__timer_id__)
                self.__timer_id__ = None


def __on_2button_press_default__(tbl, event):
    assert type(tbl) is Table
    x0, y0, w, h, ws, rh = tbl.__update_rect__()
    cover = tools.check_rect(w, h - rh, (tbl.pos[0], tbl.pos[1] + rh), event.x, event.y)
    if tbl.edit_proc(tbl.i_cur_column, tbl.i_cur_row) and cover:
        i, j = tbl.i_cur_row + 1, tbl.i_cur_column
        if i < l_len(tbl.__rows__):
            tbl.entry.text = copy.deepcopy(tbl.__rows__[i][j])
            ep_x = tbl.pos[0]
            for w in tbl.size[2][0:tbl.i_cur_column]:
                ep_x += w
            l_height = tbl.font.get_text_hight()
            tbl.entry.pos = ep_x + tbl.line_width, tbl.pos[1] + (tbl.i_cur_row + 1 - tbl.view_begin) * (
            l_height + tbl.line_width) + tbl.line_width * 2
            tbl.entry.size = tbl.size[2][tbl.i_cur_column] - tbl.line_width * 2, l_height - tbl.line_width * 2
            tbl.entry.show()
            tbl.ehid2 = None


class Table(GlWidget):
    @staticmethod
    def column_auto_width_proc(font, s, cx):
        """
        Используется для определения ширины колонки
        :param font: Шрифт используемый в таблице
        :param s: Строка ячейки заголовка таблицы
        :param cx: Индекс колонки
        :return: Ширина колонки
        """
        return font.get_text_width(s)

    @staticmethod
    def edit_proc_default(cx, cy):
        """
        Используется для проверки разрешения на редактирование ячейки
        :param cx: Индекс колонки
        :param cy: Индекс строки
        :return: True - если редактирование в ячейке разрешено, False - если редактирование запрещено
        """
        return True

    @staticmethod
    def color_proc_horiz(cx, cy):
        """
        Используется для определения цвета текста ячейки.
        :param cx: Индекс колонки
        :param cy: Индекс строки
        :return: Цвет ячейки
        """
        if cy > 0:
            return colors.TABLE_TEXT
        return colors.SAND

    @staticmethod
    def color_proc_vert(cx, cy):
        """
        Используется для определения цвета текста ячейки.
        :param cx: Индекс колонки
        :param cy: Индекс строки
        :return: Цвет ячейки
        """
        if cy == 0:
            return colors.SAND
        if cx & 1:
            return colors.TABLE_TEXT
        return colors.SAND

    def __init__(self, gda, pos, rows, view_max=5, font_name=DEFAULT_FONT_FACE, font_size=DEFAULT_FONT_SIZE,
                 column_width_proc=None):
        assert type(gda) is gtk.DrawingArea
        assert type(rows) is list
        assert l_len(rows) > 0
        assert l_len(rows[0]) > 0

        self.ehid1 = None
        self.ehid2 = None

        self.draw = self.__draw_list__
        self.gda = gda
        self.pos = pos
        self.line_width = 2

        l = l_len(rows[0])
        i = 0
        # Проверка количества колонок в каждом ряду
        for row in rows[1:]:
            i += 1
            if l != l_len(row):
                raise ValueError(
                    'Ряд %u имеет отличное количество колонок - %u, вместо %u:\n%s' % (i, l_len(row), l, rows))

        self.dl = glGenLists(1)
        self.i_cur_row = None  # Индекс текущей выбранной строки
        self.view_max = view_max  # Максимальное количество отображаемых строк
        self.view_begin = 0
        self.font = GlFont(font_name, font_size)
        if column_width_proc is None:
            self.column_width_proc = Table.column_auto_width_proc  # Процедура определяющая ширину колонки
        else:
            self.column_width_proc = column_width_proc
        # x, y, w, h, ws, rh = self.__update_rect__()
        # self.size = w, h, ws
        self.set_rows(rows)
        self.i_cur_column = 0
        self.edit_proc = Table.edit_proc_default  # Процедура проверяющая резрешение редактирования ячейки
        self.entry = Entry(gda, self.pos, '', (100, 20))  # Поле ввода. Используется для редактирования ячеек
        self.entry.hide()
        self.entry.font = self.font
        self.entry.on_edit_done = self.__on_edit_done__
        self.on_edit_done = None
        # Обработчик кнопки Delete. Должен возвращать False если нужно продолжить
        # обработку события встроенным методами класса. Встроенный метод класса удаляет выбранную строку.
        self.on_delete = None
        self.user_data = None
        # Обработчик события изменения выбора текущей строки
        self.on_sel_change = None
        self.__entry_text__ = self.__rows__[0][0]
        self.on_2button_press = __on_2button_press_default__
        self.put_to_redraw()
        self.__rdc__ = [
            GL_COMPILE_AND_EXECUTE]  # Что бы можно было в redraw() поменять флаг, не попадая на рекурсию перерисовки
        self.focus = False
        self.color_proc = Table.color_proc_horiz  # Процедура определяющая цвет текста для ячейки

    def __update_rect__(self):
        """
        Возвращает размеры таблицы в пикселях
        :return:
        """
        width, height = 0, 0
        ws = list()
        cx = 0
        for s in self.__rows__[0]:
            xw = self.column_width_proc(self.font, s, cx) + self.line_width
            ws.append(xw)
            width += xw
            cx += 1

        width += self.line_width
        row_height = self.font.get_text_hight()
        height = (row_height + self.line_width) \
                 * (l_len(self.__rows__[self.view_begin + 1: self.view_begin + 1 + self.view_max]) + 1)
        return self.pos[0], self.pos[1], width, height, ws, row_height

    def set_rows(self, rows):
        """
        Устанавливает новые строки
        :param rows:
        :return: Ничего
        """
        self.__rows__ = rows
        self.size = self.__update_rect__()[2:5]
        self.put_to_redraw()

    def get_rows(self):
        """
        Возвращает строки
        :return: Список строк
        """
        return self.__rows__

    def add_row(self, row):
        """
        Добавляет новый ряд
        :param row: новый ряд
        :return: ничего
        """
        self.__rows__.append(row)
        self.size = self.__update_rect__()[2:5]
        self.put_to_redraw()

    def __on_edit_done__(self, entry):
        """
        Вызывается после завершения редактирования ячейки таблицы
        :param entry:
        :return:
        """
        i, j = self.i_cur_row + 1, self.i_cur_column
        prev_val = copy.deepcopy(self.__rows__[i][j])
        self.__rows__[i][j] = copy.deepcopy(self.entry.text)
        self.entry.hide()
        self.put_to_redraw()
        connect_key_handler(self.__on_key_press__)
        if self.on_edit_done is not None:
            self.on_edit_done(self, prev_val)

    def __on_key_press__(self, widget, event, *args):
        """
        Вызывается при нажатии на кнопку клавиатуры
        :param widget:
        :param event:
        :param args:
        :return:
        """
        prev_i_cur_row = self.i_cur_row
        char_name = gtk.gdk.keyval_name(event.keyval)
        if char_name == 'Delete':
            if self.on_delete is not None:
                if self.on_delete(self):
                    i = self.i_cur_row + 1
                    if i < l_len(self.__rows__):
                        del self.__rows__[i]
                        if l_len(self.__rows__) > 1:
                            if (self.i_cur_row + 1) > l_len(self.__rows__):
                                self.i_cur_row = l_len(self.__rows__) - 1
                        else:
                            self.i_cur_row = 0
                        if self.on_edit_done is not None:
                            self.on_edit_done(self, None)
                        self.put_to_redraw()
        elif char_name == 'Up':
            self.i_cur_row -= 1
            if self.i_cur_row < 0:
                self.i_cur_row = 0
            if self.view_begin > self.i_cur_row:
                self.view_begin -= 1
        elif char_name == 'Down':
            self.i_cur_row += 1
            if (self.i_cur_row + 2) > l_len(self.__rows__):
                self.i_cur_row = l_len(self.__rows__) - 2
            if self.i_cur_row > ((self.view_begin + self.view_max) - 1):
                self.view_begin += 1
            if self.i_cur_row < 0:
                self.i_cur_row = 0
        if prev_i_cur_row != self.i_cur_row:
            if self.on_sel_change is not None:
                self.on_sel_change(self)
        return True

    def __on_mbutton_press__(self, *args):
        """
        Вызывается при нажатии кнопки мыши
        :param args:
        :return:
        """
        prev_i_cur_row = self.i_cur_row
        event = args[1]
        # noinspection PyProtectedMember
        if event.type == gtk.gdk.BUTTON_PRESS:
            # Поиск строки, которую кликнули
            self.entry.hide()
            x, y, w, h, ws, rh = self.__update_rect__()
            if not tools.check_rect(w, h, self.pos, event.x, event.y):
                self.focus = False
                return False
            self.focus = True
            connect_key_handler(self.__on_key_press__)
            dy = event.y - self.pos[1]
            i_cur_row = int(dy // (self.font.get_text_hight() + self.line_width))
            self.i_cur_row = i_cur_row - 1 + self.view_begin
            if self.i_cur_row < 0:
                self.i_cur_row = 0
            ws = self.size[2]
            x0 = self.pos[0]
            # Поиск колонки, которую кликнули
            for i_column in range(l_len(self.__rows__[0])):
                x1 = x0 + ws[i_column]
                if x0 < event.x < x1:
                    self.i_cur_column = i_column
                    break
                x0 += ws[i_column]
        elif event.type == gtk.gdk._2BUTTON_PRESS:
            self.on_2button_press(self, event)
        # Вызвать обработчик перемещения курсора
        if prev_i_cur_row != self.i_cur_row:
            if self.on_sel_change is not None:
                self.on_sel_change(self)
        return False

    def redraw(self):
        glNewList(self.dl, self.__rdc__[0])
        # Таблица
        i_cur_row = None
        if self.i_cur_row is not None:
            i_cur_row = self.i_cur_row - self.view_begin
        gltools.draw_table2(self.pos,
                            self.__rows__[0],
                            self.__rows__[self.view_begin + 1: self.view_begin + 1 + self.view_max],
                            self.font,
                            self.color_proc,
                            self.size[2],  # Ширины колонок
                            i_cur_row,
                            self.line_width,
                            focus=self.focus)

        # Индикаторы не отображаемых строк таблицы:
        x0 = self.pos[0] + self.line_width - 1  # левая координата x
        y0 = self.pos[1] + self.font.get_text_hight() + self.line_width * 2  # верхняя координата y
        x1 = self.pos[0] - self.line_width + self.size[0] - 1  # правая координата x
        y1 = self.pos[1] + self.size[1] - self.line_width * 2  # нижняя координата y
        # :верхних строк
        if (self.view_begin + 1) > 1:
            gltools.draw_line((x0, y0), (x1, y0), colors.GREEN, self.line_width)
        # :нижних строк
        if (self.view_begin + 1 + self.view_max) < l_len(self.__rows__):
            gltools.draw_line((x0, y1), (x1, y1), colors.GREEN, self.line_width)

        glEndList()
        self.__rdc__[0] = GL_COMPILE

    def __del__(self):
        glDeleteLists(self.dl, 1)
        self.disconnect()

    def connect(self):
        if self.ehid1 is None:
            self.ehid1 = self.gda.connect('button-press-event', self.__on_mbutton_press__)
        connect_key_handler(self.__on_key_press__)

    def disconnect(self):
        if self.ehid1 is not None:
            self.gda.disconnect(self.ehid1)
            self.ehid1 = None
        if self.ehid2:
            self.ehid2 = None
        self.entry.hide()


def clear_cairo_surface(cc):
    cc.save()
    cc.set_source_rgba(0, 0, 0, 0)
    cc.set_operator(cairo.OPERATOR_SOURCE)
    cc.paint()
    cc.set_operator(cairo.OPERATOR_OVER)
    cc.restore()


class CairoFrame(GlWidget):
    """
    Создаёт рамку с заголовком и разделительными линиями.
    # TODO: Добавить события типа "курсор мыши в рамке", "курсор мыши вне рамки", "нажатие мыши в рамке"
    """
    frame_count = 0

    def __init__(self, pos=(0, 0), width=100, height=100, title=None):
        self.draw = self.__draw_list__
        self.cis = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.cc = cairo.Context(self.cis)
        self.pos = pos
        self.txtr_id = glGenTextures(1)
        self.width, self.height = width, height
        self.dl = glGenLists(1)
        self.color_line = colors.GRIDF[0] / 4, colors.GRIDF[1] / 4, colors.GRIDF[2] / 4, 1.0
        self.color_text = colors.GRIDF[0] / 1.5 - 0.05, colors.GRIDF[1] / 1.5, colors.GRIDF[2] / 1.5, 0.95
        self.color_frame_bk = 0.0, 0.0, 0.0, 0.0
        self.color_head_bk = 0.75, 0.25, 0.25, 0.75
        self.header_height = 23
        self.font_name = DEFAULT_FONT_FACE
        self.line_width = 3
        CairoFrame.frame_count += 1
        self.title = title
        self.lines = list()

    def set_title(self, title):
        self.title = title

    def add_line(self, pos0, pos1):
        self.lines.append((pos0, pos1))

    def redraw(self):
        # Очистка поверхности
        clear_cairo_surface(self.cc)

        # Заливка
        self.cc.rectangle(self.line_width, self.header_height, self.width - self.line_width * 2,
                          self.height - self.header_height - self.line_width)
        self.cc.set_source_rgba(*self.color_frame_bk)
        self.cc.fill()

        # Линии
        self.cc.set_line_width(self.line_width)
        self.cc.move_to(self.line_width, self.line_width)
        self.cc.line_to(self.line_width, self.height - self.line_width)
        self.cc.line_to(self.width - self.line_width, self.height - self.line_width)
        self.cc.line_to(self.width - self.line_width, self.line_width)
        self.cc.line_to(self.line_width, self.line_width)
        self.cc.move_to(self.line_width, self.header_height)
        self.cc.line_to(self.width - self.line_width, self.header_height)
        self.cc.set_source_rgba(*self.color_line)
        self.cc.stroke()

        # Разделительные линии
        for poss in self.lines:
            pos0, pos1 = poss
            self.cc.move_to(pos0[0], pos0[1])
            self.cc.line_to(pos1[0], pos1[1])
            self.cc.stroke()

        # Заливка заголовка
        pat = cairo.LinearGradient(self.line_width, self.line_width, self.line_width, self.header_height)
        pat.add_color_stop_rgba(0.7, 0.7, 0.7, 0.7, 0.5)
        pat.add_color_stop_rgba(0.7, 0.7, 0.7, 0.7, 0.5)
        hatch = 2
        self.cc.rectangle(self.line_width + hatch, self.line_width + hatch,
                          self.width - self.line_width * 2 - hatch - 2, self.header_height - self.line_width * 2 - 1)
        self.cc.set_source(pat)
        self.cc.fill()

        # Заголовок
        if self.title:
            self.cc.set_source_rgba(*self.color_text)
            font_heght = DEFAULT_FONT_SIZE  # self.header_height - self.line_width * 2
            self.cc.set_font_size(font_heght)
            self.cc.select_font_face(self.font_name, cairo.FONT_SLANT_NORMAL)  # , cairo.FONT_WEIGHT_BOLD)
            xbearing, ybearing, text_width, text_height, xadvance, yadvance = self.cc.text_extents(self.title)
            fascent, fdescent, fheight, fxadvance, fyadvance = self.cc.font_extents()
            x_pos = (self.width - text_width) // 2
            y_pos = self.header_height - (self.header_height - fheight) / 2 - fdescent - self.line_width / 2
            self.cc.move_to(x_pos, y_pos)
            self.cc.show_text(self.title)

        txtr = gltools.data_to_texture(self.txtr_id, self.cis.get_data(), self.width, self.height)

        # Вывод в opengl
        glNewList(self.dl, GL_COMPILE)
        gltools.draw_texture(txtr, self.pos)
        glEndList()

    def __del__(self):
        glDeleteLists(self.dl, 1)
        glDeleteTextures([self.txtr_id])


class StaticText2(GlWidget):
    ref_cnt = 0

    def __new__(cls, pos, text, face=DEFAULT_FONT_FACE, size=DEFAULT_FONT_SIZE, color=(1.0, 1.0, 1.0, 1.0)):
        self = super(StaticText2, cls).__new__(cls)
        if StaticText2.ref_cnt == 0:
            # OpenGL
            StaticText2.dl = glGenLists(1)
            StaticText2.txr_id = glGenTextures(1)
            # Cairo
            StaticText2.cc = cairo.Context(gltools.__cis0__)
            # Чтобы стирать поверхность прозрачным цветом - .cc.set_operator(cairo.OPERATOR_SOURCE)
            StaticText2.cc.set_operator(cairo.OPERATOR_SOURCE)
            txtr = StaticText2.txr_id, gltools.__cis0__.get_width(), gltools.__cis0__.get_height()
            # Нарисовать текстуру в dispaly list
            glNewList(StaticText2.dl, GL_COMPILE)
            gltools.draw_texture(txtr, (0, 0))
            glEndList()

        StaticText2.ref_cnt += 1
        return self

    def __del__(self):
        if StaticText2.ref_cnt:
            StaticText2.ref_cnt -= 1
        else:
            glDeleteLists(StaticText2.dl)
            glDeleteTextures([StaticText2.txtr[0]])

    def __init__(self, pos, text, face=DEFAULT_FONT_FACE, size=DEFAULT_FONT_SIZE, color=(1.0, 1.0, 1.0, 1.0)):
        self.draw = self.__draw_list__
        self.pos = pos
        self.text = text
        self.color = color
        self.set_font(face, size)

    def set_font(self, face, size):
        # Параметры шрифта
        StaticText2.cc.select_font_face(face)
        StaticText2.cc.set_font_size(size)
        fascent, fdescent, self.fheight, fxadvance, fyadvance = StaticText2.cc.font_extents()

    def redraw(self):
        xbearing, ybearing, self.width, height, xadvance, yadvance = StaticText2.cc.text_extents(self.text)
        # Стереть область под текстом
        StaticText2.cc.set_source_rgba(0.0, 0.0, 0.0, 0.0)
        StaticText2.cc.rectangle(self.pos[0], self.pos[1] - self.fheight, self.width, self.fheight)
        StaticText2.cc.fill()
        # Нарисовать текст
        StaticText2.cc.set_source_rgba(*self.color)
        StaticText2.cc.move_to(self.pos[0], self.pos[1])
        StaticText2.cc.show_text(self.text)


class TextRegulator(StaticText):
    """
    Ввод данных движением мыши
    """

    def __init__(self, gda, pos=(0, 0), fmt='%03f', val_min=0, val_max=100, val=50, size=(40, DEFAULT_FONT_SIZE),
                 scale=0.01,
                 axis=1, font=None, color=(255, 255, 255, 150), user_proc=None, user_data=None):
        """
        :param gda: Контекст gtk-opengl
        :param pos: Координаты на экране в пикселях
        :param fmt: Текстовой фрмат отображения, например 'Масштаб %s км'
        :param val_min: Начальное значение регулятора
        :param val_max: Конечное значение регулятора
        :param scale: Шаг изменения значения на один пиксель перемещения мыши
        :param axis: Ось координат используемая для изменения параметра: 0 - ось X, 1 - ось Y
        :param val: Текущее значение регулятора
        :param font: Шрифт текста
        :param color: Цвет текста
        :param user_proc: Процедура вызываемая при изменения значения
        :param user_data: Данные пользователя
        :return:
        """
        assert type(color) is tuple  # Цвет должен состоять из четырёх компонент в кортеже
        assert l_len(color) == 4  # Цвет должен состоять из четырёх компонент в кортеже
        for c in color:
            assert type(c) is int  # Значение цвета должно быть целым
            assert 0 <= c <= 255  # Значение цвета должно быть от 0 до 255 включительно
        assert type(gda) is gtk.DrawingArea
        assert type(pos) is tuple
        assert l_len(pos) == 2
        assert type(pos[0]) is int
        assert type(pos[1]) is int
        assert type(fmt) is str
        assert type(axis) is int
        assert 0 <= axis <= 1  # 0 - ось X, 1 - ось Y
        assert type(size) is tuple
        assert l_len(size) == 2
        assert type(size[0]) is int
        assert type(size[1]) is int
        if user_proc is not None:
            assert (inspect.isfunction(user_proc))  # Должна быть функцией

        super(TextRegulator, self).__init__(gda, pos, fmt, font, color)
        self.drawing_area = gda
        self.format = fmt
        self.min = val_min
        self.max = val_max
        self.scale = scale
        self.val = val
        self.axis = axis
        self.prev = pos[axis]
        self.ehid0 = self.drawing_area.connect('button-press-event', self.__button_press__)
        self.text = self.get_text()
        self.size = size
        self.ehid1 = None
        self.ehid2 = None
        self.user_proc = user_proc
        self.user_data = user_data

    def __button_press__(self, *args):
        event = args[1]
        pos = event.x, event.y + self.size[1]
        cover = tools.check_rect(self.size[0], self.size[1], self.pos, pos[0], pos[1])
        if cover:
            if self.ehid1 is None:
                self.ehid1 = self.drawing_area.connect('motion-notify-event', self.__motion_notify__)
            if self.ehid2 is None:
                self.ehid2 = self.drawing_area.connect('button-release-event', self.__button_release__)
            self.prev = pos[self.axis]
            self.text = self.get_text()
            r, g, b, a = self.color
            self.color = r, g, b, 210

    def __button_release__(self, *args):
        if self.ehid1 is not None:
            self.drawing_area.disconnect(self.ehid1)
            self.ehid1 = None
            self.prev = self.pos[self.axis]
            self.text = self.get_text()
            r, g, b, a = self.color
            self.color = r, g, b, 180
        if self.ehid2 is not None:
            self.drawing_area.disconnect(self.ehid2)
            self.ehid2 = None

    def __motion_notify__(self, *args):
        event = args[1]
        pos = event.x, event.y
        delta = self.prev - pos[self.axis]
        self.val += float(delta) * self.scale
        self.pass_limits()
        self.prev = pos[self.axis]
        cur_text = self.get_text()
        if self.text != cur_text:
            self.text = cur_text
            if self.user_proc:
                self.user_proc(self)
        return False

    def get_text(self):
        return self.format % self.val

    def get_val(self):
        return self.val

    def pass_limits(self):
        if self.val > self.max:
            self.val = float(self.max)
        if self.val < self.min:
            self.val = float(self.min)


class CairoGlFont(object):
    # TODO: Не использовать, т.к. не работает. Предназначено для вывода больших текстов
    # Карта символов
    symbols = u'`1234567890-=\\~!@#$%^&*()_+|Ё"№;:?/ \n' \
              + u'qwertyuiop[]QWERTYUIOP{}йцукенгшщзхъЙЦУКЕНГШЩЗХЪ' \
              + u'asdfghjkl\'ASDFGHJKL\"фывапролджэФЫВАПРОЛДЖЭ' \
              + u'zxcvbnm,.ZXCVBNM<>ячсмитьбюЯЧСМИТЬБЮ' \
              + u'\u2190' + u'\u2191' + u'\u2192' + u'\u2193'

    def __init__(self):
        self.sd = dict()
        cis0 = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)  # Поверхность для вычисления размера текста
        cc0 = cairo.Context(cis0)  # Контекст для вычисления размера текста
        fascent, fdescent, fheight, fxadvance, fyadvance = cc0.font_extents()
        for ks in CairoGlFont.symbols:
            dl = glGenLists(1)
            txrid = glGenTextures(1)
            xbearing, ybearing, width, height, xadvance, yadvance = cc0.text_extents(ks)
            cis0.finish()
            cis = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(fheight))
            cc = cairo.Context(cis)
            cc.set_source_rgba(1.0, 1.0, 1.0, 1.0)
            cc.move_to(0, fascent)
            cc.show_text(ks)
            txr = gltools.data_to_texture(txrid, cis.get_data(), int(width), int(fheight))
            cis.finish()
            glNewList(dl, GL_COMPILE)
            gltools.draw_texture(txr, (0, 0))
            glEndList()
            self.sd[ks] = [dl, width, height, txrid]

    def draw_text(self, pos, text, color):
        x, y = pos
        textu = u'%s' % text
        for sk in textu:
            val = self.sd.get(sk)
            if val is None:
                dl, width, height, txrid = self.sd['?']
            else:
                dl, width, height, txrid = val
            glPushMatrix()
            glTranslatef(x, y, 0)
            glCallList(dl)
            glPopMatrix()
            x += width
