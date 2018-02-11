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

# Переопределить поведение pygtk своей процедурой для того, что бы
# программа закрывалась при возникновении исключения.
callbacks.saved_exception_hook = sys.excepthook
sys.excepthook = callbacks.exception_hook

window_width = 1280
window_height = 720
gda = gltools.create_drawning_area(window_width, window_height)

# Интерфейс
ui = uictl.UiCtl(gda, 'data')

# Процедуры-обработчики инициализации, перерисовки и завершения
gda.connect_after('realize', callbacks.on_realize, ui)
gda.connect('expose-event', callbacks.on_expose_event, ui)

# Окно и главный цикл
main_window = gtk.Window()
main_window.set_reallocate_redraws(True)
main_window.connect('delete-event', gtk.main_quit)
main_window.set_title('GTKGLUI - Example')

# Расположение в окне
vbox = gtk.VBox()
main_window.add(vbox)
vbox.pack_start(gda)

# Глобальные обработчики клавиш. Один обработчик для всех клавиш, глобальный
key_callbacks = dict()  # Словарь клавиш и соответсвующих им процедур
key_callbacks['Escape'] = callbacks.on_escape_key, 'Нормальное завершение', ui
key_callbacks['q'] = callbacks.on_debug_key, ui
main_window.connect('key-press-event', callbacks.on_key_press, key_callbacks)
glwidgets.init(main_window)

# Установка положения окна
main_window.move(0, 0)
main_window.show_all()

# Таймер перерисовки окна, для анимации
redraw_rate = 20
glib.timeout_add(redraw_rate, callbacks.on_timer_tick, gda, ui)

# Вход в главный цикл
gtk.main()

# Выход из порграммы
print('%s: конец файла' % __file__)
quit(0)
