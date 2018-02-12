#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Пример использования gtkglui

# Чужие модули
import gtk
import glib
import sys

# Свои модули
import callbacks
import gltools
import glwidgets
import uictl
import tools

# Переопределить поведение pygtk своей процедурой для того, что бы
# программа закрывалась при возникновении исключения.
callbacks.saved_exception_hook = sys.excepthook
sys.excepthook = callbacks.exception_hook

window_width = 1280
window_height = 720
gda = gltools.create_drawning_area(window_width, window_height)

# Интерфейс
ui = uictl.UiCtl(gda, 'data')  # 'data' - путь к папке с медиафайлами

# Определяемая пользователем часть
user_module = tools.load_module('module0', 'mods')  # 'mods' - путь к папке с модулями пользователя

# Процедуры-обработчики инициализации, перерисовки и завершения
gda.connect_after('realize', callbacks.on_realize, ui, user_module)
gda.connect('expose-event', callbacks.on_expose_event, ui, user_module)

# Окно и главный цикл
main_window = gtk.Window()
main_window.set_reallocate_redraws(True)
main_window.connect('delete-event', gtk.main_quit)
main_window.set_title('GTKGLUI - Example')

main_window.connect('key-press-event', glwidgets.key_dispatcher)

# Расположение в окне
vbox = gtk.VBox()
main_window.add(vbox)
vbox.pack_start(gda)


# Установка положения окна
main_window.show_all()

# Таймер перерисовки окна, для анимации
redraw_rate = 20
glib.timeout_add(redraw_rate, callbacks.on_timer_tick, gda, ui, user_module)

# Вход в главный цикл
gtk.main()

# Выход из порграммы
print('%s: конец файла' % __file__)
quit(0)
