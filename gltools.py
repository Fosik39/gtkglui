#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Примитивы OpenGL

# Чужие модули
import os
import cairo
import pygtk
import gtk
import gtk.gdkgl
import OpenGL

OpenGL.ERROR_CHECKING = False
OpenGL.ERROR_LOGGING = False
from OpenGL.GL import *

# Свои модули
import colors

pygtk.require('2.0')

__textures__ = None
__flash_phase__ = 0
flash_alpha = 100
__ehid__ = None

def step_flash():
    global __flash_phase__, flash_alpha
    __flash_phase__ += 1
    flash_alpha = (100, 80)[(__flash_phase__ // 3) % 2]


__glerros__ = \
    {
        GL_NO_ERROR: "GL_NO_ERROR: No error has been recorded",
        GL_INVALID_ENUM: "GL_INVALID_ENUM: An unacceptable value is specified for an enumerated argument",
        GL_INVALID_VALUE: "GL_INVALID_VALUE: A numeric argument is out of range",
        GL_INVALID_OPERATION: "GL_INVALID_OPERATION: The specified operation is not allowed in the current state",
        # GL_INVALID_FRAMEBUFFER_OPERATION: "GL_INVALID_FRAMEBUFFER_OPERATION: The framebuffer object is not complete",
        GL_OUT_OF_MEMORY: "GL_OUT_OF_MEMORY: There is not enough memory left to execute the command",
        GL_STACK_UNDERFLOW: "GL_STACK_UNDERFLOW: An attempt has been made to perform an operation that would cause an internal stack to underflow",
        GL_STACK_OVERFLOW: "GL_STACK_OVERFLOW: An attempt has been made to perform an operation that would cause an internal stack to overflow"
    }

# TODO: Добавить матрицу вертикального отражения
MIRROR_NONE = (0, 1, 1, 1, 1, 0, 0, 0)  # Матрица без отражения
MIRROR_HORIZ = (1, 1, 0, 1, 0, 0, 1, 0)  # Матрица горизонтального отражения

l_len = len  # Кэширование адреса встроенной в питон функции, для ускорения её вызова


# TODO: Переделать на использование "Vertex array" вместо "Display list"

def get_str_width(s, font_name, font_size):
    """
    :param s: Строка
    :param font_name: Название шрифта
    :param font_size: Размер шрифта
    :return: Ширина строки в пикселях на экране
    """
    cc = cairo.Context(__cis0__)
    cc.select_font_face(font_name)
    cc.set_font_size(font_size)
    xbearing, ybearing, width, height, xadvance, yadvance = cc.text_extents(s)
    return int(xadvance + 0.5)


def draw_line(point1, point2, color, width=2):
    """
    Рисует линию между двумя точками
    :return: Ничего
    :param width: Толщина линий
    :param color: Цвет линий
    :param point1: Точка начала линии
    :param point2: Точка конца линии
    """
    glLineWidth(width)
    glColor4ub(*color)
    glBegin(GL_LINE_STRIP)
    glVertex2f(point1[0], __parent_height__ - point1[1])
    glVertex2f(point2[0], __parent_height__ - point2[1])
    glEnd()


def draw_lines(points, color, width=2):
    glPushMatrix()
    glLineWidth(width)
    glColor4ub(*color)
    glBegin(GL_LINE_STRIP)
    [glVertex2s(p0, __parent_height__ - p1) for p0, p1 in points]
    glEnd()
    glPopMatrix()


def draw_lines_rotated(rotor_point, points, color, width=2, tetha=0):
    glPushMatrix()
    glLineWidth(width)
    glColor4ub(*color)
    glTranslatef(rotor_point[0], __parent_height__ - rotor_point[1], 0)
    glRotatef(tetha, 0, 0, 1)  # rotating
    glBegin(GL_LINE_STRIP)
    [glVertex2s(*p) for p in points]
    glEnd()
    glPopMatrix()


def draw_table2(pos, head, lines, font, color_proc, cws, i_cur=None, line_width=2, focus=True):
    """
    Рисует таблицу с горизонтальным заголовком
    :param cws: Ширины колонок
    :param pos: Координаты вехнего левого угла
    :param head: Заголовок
    :param lines: Строки
    :param font: Шрифт
    :param color_proc: Процедура цвета ячейки
    :param i_cur: Положение курсора
    :param line_width: Толщина линий
    :param focus: Флаг. True - таблица в фокусе ввода,
    False - таблица вне фокуса ввода. Меняет цвет кусора
    :return: Ничего
    """
    assert type(focus) is bool
    assert l_len(cws) == l_len(head)

    row_height = font.get_text_hight()

    x0, y0 = pos
    x, y = x0, y0
    cx, cy = 0, 0

    # текст заголовков колонок
    for str0, cws_x in zip(head, cws):
        col = color_proc(cx, cy)  # Выбор цвета для ячейки
        text_width = font.get_text_width(str0)  # Горизонтальное выравнивание по центру ячейки
        dx = (cws_x - text_width) >> 1
        if dx < 0:
            dx = 0
        font.draw_text((x + line_width + dx, y + row_height + line_width), str0, col)
        cx += 1
        x += cws_x

    x_right = x
    j = 0
    for strs in lines:  # пробег по строкам
        cy += 1
        y += row_height + line_width
        i = 0
        pts = (x_right - line_width, y) \
            , (x0 + line_width, y) \
            , (x0 + line_width, y + row_height + line_width) \
            , (x_right - line_width, y + row_height + line_width)
        if i_cur == j:
            col = (colors.TABLE_SEL_INACTIVE, colors.TABLE_SEL_ACTIVE)[
                focus]  # Цвет курсора в неактивном и активном режимах
        else:
            col = colors.TABLE_BACK[j % l_len(colors.TABLE_BACK)]  # Цвет фона чётных и нечётных строк
        draw_polygon(pts, col)
        j += 1
        cx = 0
        x = x0
        for str0 in strs:  # пробег по столбцам
            # TODO: Добавить отсечение слишком длинного текста
            col = color_proc(cx, cy)  # Выбор цвета для ячейки
            font.draw_text((x + line_width, y + row_height + line_width), str0, col)
            x += cws[i]
            i += 1
            cx += 1

    n_lines = l_len(lines) + 1  # + 1 строка на заголовок

    # верхняя граница
    draw_line((x0, y0), (x_right, y0), colors.TABLE_LINES, line_width)

    # граница под заголовком
    y = y0 + row_height + line_width
    draw_line((x0, y), (x_right, y), colors.TABLE_LINES, line_width)

    # нижняя граница
    y = y0 + (row_height + line_width) * n_lines
    draw_line((x0, y), (x_right, y), colors.TABLE_LINES, line_width)

    # вертикальные границы
    x = x0
    for cws_x in cws:
        draw_line((x, y), (x, y0), colors.TABLE_LINES, line_width)
        x += cws_x

    # правая граница
    draw_line((x_right, y), (x_right, y0), colors.TABLE_LINES, line_width)


def draw_table_borders(pos, cws, rh, rn, lw):
    """
    Рисует границы таблицы
    :param pos: Координаты верхнего левого угла
    :param cws: Ширины колонок
    :param rh: Высота строки
    :param rn: Количество строк
    :param lw: Толщина линий
    :return:
    """
    # вертикальные границы
    x = pos[0]
    y = pos[1] + rh * rn + lw * 3
    for cws_x in cws:
        draw_line((x, y), (x, pos[1]), colors.TABLE_LINES, lw)
        x += cws_x
    width = x - pos[0]

    # правая граница
    x = pos[0] + width + lw
    draw_line((x, y), (x, pos[1]), colors.TABLE_LINES, lw)

    # верхняя граница
    draw_line(pos, (x, pos[1]), colors.TABLE_LINES, lw)

    # граница под заголовком
    y = pos[1] + rh + lw
    draw_line((pos[0], y), (x, y), colors.TABLE_LINES, lw)

    # нижняя граница
    y = pos[1] + lw * 2 + (rn + 2) * rh
    draw_line((pos[0], y), (x, y), colors.TABLE_LINES, lw)


def init(drawing_area):
    global __cis0__, __parent_height__, __cairo_texts__, __textures_ids__, \
        __cairo_texts_len_max__, __glyph_widths__, __textures__, __ehid__
    __cis0__ = cairo.ImageSurface(cairo.FORMAT_ARGB32, drawing_area.allocation.width, drawing_area.allocation.height)
    __parent_height__ = drawing_area.allocation.height
    __cairo_texts__ = dict()
    __cairo_texts_len_max__ = 2048
    __textures__ = list()

    print 'Версия привязки python OpenGL:', str(OpenGL.__version__)

    glEnable(GL_MULTISAMPLE)
    glViewport(0, 0, drawing_area.allocation.width, drawing_area.allocation.height)
    glOrtho(0, drawing_area.allocation.width, 0, drawing_area.allocation.height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_CULL_FACE)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_BLEND)
    glEnable(GL_DITHER)
    glEnable(GL_POLYGON_SMOOTH)
    glEnable(GL_POINT_SMOOTH)
    glCullFace(GL_BACK)
    glShadeModel(GL_SMOOTH)
    glDepthFunc(GL_LESS)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClearDepth(1.0)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
    glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    print 'Производитель: %s' % glGetString(GL_VENDOR)
    print 'Версия OpenGL: %s' % glGetString(GL_VERSION)
    print 'Версия GLSL: %s' % glGetString(GL_SHADING_LANGUAGE_VERSION)
    print 'Рендер: %s' % glGetString(GL_RENDERER)


def draw_sector(pointsIn, pointsOut, color):
    N = 0
    N1 = l_len(pointsOut)
    N2 = l_len(pointsIn)
    if (N1 < 2) | (N2 < 2):
        return
    if N1 < N2:
        N = N1
    else:
        N = N2
    glColor4ub(*color)
    i = 0
    iN = N - 1
    while i < iN:
        i1 = N - i - 1
        i2 = N - i - 2
        glBegin(GL_POLYGON)
        px, py = pointsOut[i]
        glVertex2s(px, __parent_height__ - py)
        px, py = pointsIn[i1]
        glVertex2s(px, __parent_height__ - py)
        px, py = pointsIn[i2]
        glVertex2s(px, __parent_height__ - py)
        glEnd()
        glBegin(GL_POLYGON)
        px, py = pointsIn[i]
        glVertex2s(px, __parent_height__ - py)
        px, py = pointsOut[i1]
        glVertex2s(px, __parent_height__ - py)
        px, py = pointsOut[i2]
        glVertex2s(px, __parent_height__ - py)
        glEnd()
        i += 1


def create_drawning_area(width, height):
    display_mode = gtk.gdkgl.MODE_RGBA | gtk.gdkgl.MODE_DEPTH | gtk.gdkgl.MODE_DOUBLE | gtk.gdkgl.MODE_MULTISAMPLE
    events_mask = gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.KEY_PRESS_MASK | gtk.gdk.KEY_RELEASE_MASK
    glconfig = gtk.gdkgl.Config(mode=display_mode)
    drawing_area = gtk.DrawingArea()
    drawing_area.set_double_buffered(False)
    drawing_area.glconfig = glconfig
    drawing_area.gldrawable = None
    drawing_area.glcontext = None
    drawing_area.set_size_request(width, height)
    drawing_area.add_events(events_mask)
    return drawing_area


def draw_line(point1, point2, color=(255, 255, 255, 255), width=2):
    glLineWidth(width)
    glColor4ub(*color)
    glBegin(GL_LINE_STRIP)
    glVertex2s(point1[0], __parent_height__ - point1[1])
    glVertex2s(point2[0], __parent_height__ - point2[1])
    glEnd()


def check_glerrors(title):
    err_cnt = 0
    while True:
        err0 = glGetError()
        if err0 != GL_NO_ERROR:
            print ('%s:%s' % (title, __glerros__[err0]))
            err_cnt += 1
            continue
        break
    if err_cnt:
        quit(1)
    return err_cnt


def generate_dls(size):
    first_dl = glGenLists(size)
    dls = range(first_dl, first_dl + size)
    return dls


def data_to_texture(texture_id, data, width, height, db=''):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    # assert glIsTexture(texture_id)  # You cannot include calls to glIsTexture in display lists.
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, str(data))
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glDisable(GL_TEXTURE_2D)
    return texture_id, width, height


def texture_from_gtkimage(image):
    assert type(image) is gtk.Image
    pb = image.get_pixbuf()
    image.get_colormap()
    glEnable(GL_TEXTURE_2D)
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, pb.get_width(), pb.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE,
                 pb.get_pixels())
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glDisable(GL_TEXTURE_2D)
    return texture_id, pb.get_width(), pb.get_height()


def textures_from_files(fmt, count):
    textures = list()
    for i in range(count):
        file_name = fmt % i
        texture = texture_from_file(file_name)
        textures.append(texture)
    return textures


def texture_from_file(file_name):
    global db_ts
    assert type(file_name) is str
    image = gtk.Image()
    if not os.path.exists(file_name):
        raise ArgumentError('Файл: \'%s\' - не найден.' % file_name)
    image.set_from_file(file_name)
    texture = texture_from_gtkimage(image)
    print 'Загружено: \'%s\', %ux%u' % (file_name, texture[1], texture[2])
    return texture


def draw_texture(texture, pos, col=(255, 255, 255, 255), mirror=MIRROR_NONE):
    """
    Рисует текстуру
    :param texture: Текстура
    :param pos: Коррдинаты на экране
    :param col: Окрашивающий цвет
    :param mirror: Матрица отражения. Смотри MIRROR_*
    :return:
    """
    glEnable(GL_TEXTURE_2D)
    glColor4ub(*col)
    glPushMatrix()
    glTranslatef(pos[0], __parent_height__ - pos[1] - texture[2], 0)
    glBindTexture(GL_TEXTURE_2D, texture[0])

    glBegin(GL_QUADS)
    glTexCoord2s(mirror[0], mirror[1])
    glVertex2s(0, 0)
    glTexCoord2s(mirror[2], mirror[3])
    glVertex2s(texture[1], 0)
    glTexCoord2s(mirror[4], mirror[5])
    glVertex2s(texture[1], texture[2])
    glTexCoord2s(mirror[6], mirror[7])
    glVertex2s(0, texture[2])
    glEnd()

    glPopMatrix()
    glDisable(GL_TEXTURE_2D)


def draw_texture_rotate(texture, pos, a=0, col=(255, 255, 255, 255), mirror=MIRROR_NONE, scale=(1.0, 1.0, 1.0)):
    glEnable(GL_TEXTURE_2D)
    glColor4ub(*col)
    glPushMatrix()
    glTranslatef(pos[0], __parent_height__ - pos[1], 0)
    glRotate(a, 0, 0, -1)
    glBindTexture(GL_TEXTURE_2D, texture[0])
    glScalef(*scale)
    glBegin(GL_QUADS)
    sx, sy = texture[1] >> 1, texture[2] >> 1
    glTexCoord2s(mirror[0], mirror[1])
    glVertex2s(-sx, -sy)
    glTexCoord2s(mirror[2], mirror[3])
    glVertex2s(sx, -sy)
    glTexCoord2s(mirror[4], mirror[5])
    glVertex2s(sx, sy)
    glTexCoord2s(mirror[6], mirror[7])
    glVertex2s(-sx, sy)
    glEnd()
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)


def draw_texture_scale(texture, pos, scale, col=(255, 255, 255, 255), mirror=MIRROR_NONE):
    glEnable(GL_TEXTURE_2D)
    glColor4ub(*col)
    glPushMatrix()
    glTranslatef(pos[0], __parent_height__ - pos[1] - texture[2], 0)
    glBindTexture(GL_TEXTURE_2D, texture[0])
    glScalef(scale[0], scale[1], 1.0)

    glBegin(GL_QUADS)
    glTexCoord2s(mirror[0], mirror[1])
    glVertex2s(0, 0)
    glTexCoord2s(mirror[2], mirror[3])
    glVertex2s(texture[1], 0)
    glTexCoord2s(mirror[4], mirror[5])
    glVertex2s(texture[1], texture[2])
    glTexCoord2s(mirror[6], mirror[7])
    glVertex2s(0, texture[2])
    glEnd()

    glPopMatrix()
    glDisable(GL_TEXTURE_2D)


def draw_polygon(points, color):
    glColor4ub(*color)
    glBegin(GL_POLYGON)
    for p in points:
        glVertex2s(p[0], __parent_height__ - p[1])
    glEnd()
