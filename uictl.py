#!/usr/bin/env python
# -*- coding: utf-8 -*-



# Чужие модули
import os
import inspect
import gtk
import glib

import OpenGL
OpenGL.ERROR_CHECKING = False
OpenGL.ERROR_LOGGING = False
from OpenGL.GL import *
from datetime import datetime

# Свои модули
import gltools
import glwidgets
import tools
import callbacks


class UiCtl(object):
    """
    Управление виджетами
    """
    def __init__(self, width, hight, data_path, module_path):
        self.gda = gltools.create_drawning_area(width, hight)
        self.scene = list()
        self.data_path = data_path
        self.draw_callbacks = list()
        self.textures = dict()
        self.fonts = dict()
        self.mouse_pos = [0, 0]
        self.events = dict()  # Свои события
        self.time_now = datetime.now()
        user_module = tools.load_module(module_path)
        self.gda.connect_after('realize', callbacks.on_realize, self, user_module)
        self.gda.connect('expose-event', callbacks.on_expose_event, self, user_module)
        self.main_window = gtk.Window()
        self.main_window.set_reallocate_redraws(True)
        self.main_window.connect('delete-event', gtk.main_quit)
        self.main_window.set_title('GTKGLUI - Example')
        self.main_window.connect('key-press-event', glwidgets.key_dispatcher)
        self.main_window.connect('key-press-event',  callbacks.on_key_callback, self, user_module)
        glib.timeout_add(25, callbacks.on_timer_tick, self, user_module)
        vbox = gtk.VBox()
        self.main_window.add(vbox)
        vbox.pack_start(self.gda)
        self.main_window.show_all()
        self.main = gtk.main


    def on_expose_event(self, event):
        if glwidgets.GlWidget.force_redraw:
            glNewList(self.dl, GL_COMPILE)
            for item in self.scene:
                item.draw()
            glEndList()
            glwidgets.GlWidget.force_redraw = False

        glCallList(self.dl)

        # Пользовательские процедуры рисования
        for item in self.draw_callbacks:
            item[0](self, *item[1])

    def init(self):
        self.dl = glGenLists(1)
        assert glIsList(self.dl)

    def get_tick(self):
        """
        Возвращает грубое значение текущего тик-времени в мс
        """
        return (self.time_now.second << 10) | (self.time_now.microsecond >> 10) % 65535

    def connect_event(self, event_name, proc, *args):
        assert type(event_name) is str
        if event_name not in self.events.keys():
            self.events[event_name] = list()
        ecb_id = (proc, args)
        self.events[event_name].append(ecb_id)
        return ecb_id

    def emmit_event(self, event_name):
        assert type(event_name) is str
        if event_name in self.events.keys():
            for proc, args in self.events[event_name]:
                if proc(*args): break

    def disconnect_event(self, event_name, ecb_id):
        assert type(event_name) is str
        assert event_name in self.events.keys()
        assert ecb_id in self.events[event_name]
        self.events[event_name].remove(ecb_id)
        if len(self.events[event_name]) == 0:
            del self.events[event_name]

    def add_scene_item(self, item):
        """
        Добавляет элементы в сцену
        :param item:
        :return:
        """
        # TODO: Очень медленный метод: выражение "if item not in self.scene:" - использует итерацию по всему списку
        l0 = len(self.scene)
        items = list()
        if type(item) is not list:
            items.append(item)
        else:
            items = item
        for item in items:
            if item not in self.scene:
                self.scene.append(item)
                item.show()
        return len(self.scene) > l0

    def del_scene_item(self, item):
        """
        Удаляет элементы из сцены
        :param item:
        :return:
        """
        # TODO: Очень медленный метод: выражение "if item not in self.scene:" - использует итерацию по всему списку
        l0 = len(self.scene)
        items = list()
        if type(item) is not list:
            items.append(item)
        else:
            items = item
        for item in items:
            if item in self.scene:
                self.scene.remove(item)
                item.hide()
        return len(self.scene) < l0


    def add_draw_callback(self, callback, *args):
        """
        Добавляет пользовательский обработчик перерисовки
        :param callback: Процедура которая будет вызвана для перерисовки
        :param args: Аргументы передаваемые в процедуру
        :return: Идентификатор в обработчика в списке
        """
        assert inspect.isfunction(callback)  # callback - должно быть функцией
        cb_id = callback, args
        if cb_id not in self.draw_callbacks:
            self.draw_callbacks.append(cb_id)
        return cb_id

    def del_draw_callback(self, cb_id):
        """
        Удаляет пользовательскую процедуру рисования.
        :param cb_id: Идентификатор пользовательской процедуры рисования,
        возвращаемый UiCtl.add_draw_callback
        :return:
        """
        l0 = len(self.draw_callbacks)
        if cb_id in self.draw_callbacks:
            self.draw_callbacks.remove(cb_id)
        return l0 > len(self.draw_callbacks)

    def process_draw_callbacks(self):
        for item in self.draw_callbacks:
            item[0](self, *item[1])
        return len(self.draw_callbacks)

    def draw(self):
        glCallList(self.dl)

    def redraw(self):
        if glwidgets.GlWidget.force_redraw:
            glNewList(self.dl, GL_COMPILE)
            for item in self.scene:
                item.draw()
            glEndList()
            glwidgets.GlWidget.force_redraw = False

    def __motion_notify__(self, drawing_area, event):
        self.mouse_pos[0] = event.x
        self.mouse_pos[1] = event.y
        return False

    def get_texture(self, path):
        assert type(path) is str  # Должна быть строка
        path = os.path.join(self.data_path, path)
        if self.textures.get(path) is None:
            if os.path.exists(path) and os.path.isfile(path):
                self.textures[path] = gltools.texture_from_file(path)
            else:
                s = 'ошибка: файл \'%s\' - не найден.' % path
                raise ValueError(s)
        return self.textures[path]

    def get_textures(self, fmt, count=1, begin=0):
        """
        Загружает массив структур из файлов с именами, соответствующим
        заданной строке-формату, например 'image_%u.png' значит 'image_0.png',
        'image_1.png' ...
        :param fmt: Строка-формат, куда подставляются значения от begin до сount
        :param count: Количество
        :param begin: Начальное значение индекса в строке-формате
        :return: Список текстур
        """
        assert type(fmt) is str  # Дожна быть строка
        assert type(count) is int  # Должен быть целым
        assert count >= 1  # Нужо загрузить хотя бы одну текстуру
        textures = list()
        for i in range(count):
            path = fmt % (i + begin)
            texture = self.get_texture(path)
            textures.append(texture)
        return textures

    def uninit(self):
        glDeleteLists(self.dl, 1)
        for txr in self.textures:
            glDeleteTextures(txr[0])

    def __del__(self):
        self.uninit()
