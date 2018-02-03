#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Обратные вызовы gtk
# - отработка завершения при исключении
# - рисование по событию и таймеру
# - таймер обновления экрана
# - отработка инициализации gtk-opengl
# - отработка клавиши esc - завершение программы
# - глобальный обработчик нажатий на клавиатуру


# Чужие модули
import gc
import gtk
import gtk.gdkgl
import glib
import os
from datetime import datetime
import OpenGL

OpenGL.ERROR_CHECKING = False
OpenGL.ERROR_LOGGING = False
from OpenGL.GL import *

# Свои модули
import glwidgets
import gltools
import tools
import uictl

dt_draw_us = None
t_us = datetime.now().microsecond
saved_exception_hook = None
ms_new = 0

__quit_flag__ = False
__redraw_timer__ = 20
__timer_min_ms__ = 33


def exception_hook(etype, evalue, etb):
    saved_exception_hook(etype, evalue, etb)
    print '%s:\n- Завершено из за возникновения исключения.' % __file__
    quit(1)


def on_expose_event(gda, event, ui):
    global dt_draw_us, t_us, flash_alpha

    # Контроль времени перерисовки
    t0_us = datetime.now().microsecond

    # GTK начало рисования в контексте OpenGL
    # gda.gldrawable.wait_gdk()
    gda.gldrawable.gl_begin(gda.glcontext)

    if __quit_flag__:
        ui.uninit()
        glDeleteTextures(gltools.__textures__)
        # Контроль ошибок OpenGL
        gltools.check_glerrors('on_expose_event')
        gda.window.unset_gl_capability()
        # Завершение контекста OpenGL
        gda.gldrawable.wait_gl()
        gda.gldrawable.swap_buffers()
        gda.gldrawable.gl_end()
        gda.gldrawable = None
        gda.glcontext = None
        gc.collect()
        gtk.main_quit()

    # Обновить мигающий цвет
    gltools.step_flash()

    # Рисование в OpenGL
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Перерисовка обновившихся виджетов (компиляция display lists)
    glwidgets.redraw_queue()

    # Все управляемые элементы, компиляция в один display list
    ui.redraw()

    # Все управляемые элементы, рисование display list
    ui.draw()

    # Пользовательские процедуры рисования
    ui.process_draw_callbacks()

    # Контроль ошибок OpenGL
    gltools.check_glerrors('on_expose_event()')

    # Завершение контекста OpenGL
    if gda.gldrawable:
        gda.gldrawable.swap_buffers()
        gda.gldrawable.gl_end()

    # Контроль времени перерисовки
    ui.time_now = datetime.now()

    t1_us = ui.time_now.microsecond
    dt_draw_us = tools.delta_tick(t0_us, t1_us, 999999)

    return False


def on_realize(gda, ui):
    gtk.gdkgl.ext(gda.window)
    gda.gldrawable = gda.window.set_gl_capability(gda.glconfig)

    gda.glcontext = gtk.gdkgl.Context(gda.gldrawable)

    gda.gldrawable.wait_gdk()
    gda.gldrawable.gl_begin(gda.glcontext)

    # Своя инициализация
    gltools.opengl_init(gda)
    uictl.init(ui)

    gltools.check_glerrors('on_realize()')
    gda.gldrawable.wait_gl()
    gda.gldrawable.gl_end()


def on_escape_key(arg):
    global __quit_flag__
    print 'Оператор закрыл программу: %s' % __file__
    __quit_flag__ = True


def on_debug_key(arg):
    pass


def on_key_press(widget, event, key_callbacks):
    if gtk.gdk.keyval_name(event.keyval) in key_callbacks.keys():
        keyname = gtk.gdk.keyval_name(event.keyval)
        key_callbacks[keyname][0](key_callbacks[keyname][1])
    return False


def on_timer_tick(gda, ui):
    global __redraw_timer__, dt_timer_us, t_timer_us, ms_new
    rect = gtk.gdk.Rectangle(0, 0, gda.allocation.width, gda.allocation.height)
    gda.window.invalidate_rect(rect, True)
    gda.window.process_updates(True)
    ms_new = int((dt_draw_us * 1.1) // 1000.0)
    if ms_new < __timer_min_ms__:
        ms_new = __timer_min_ms__
    __redraw_timer__ = ms_new
    glib.timeout_add(ms_new, on_timer_tick, gda, ui)
    return False
