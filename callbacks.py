#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Callbacks for gtk
# - workaround for exceptions
# - redraw for timer and events
# - screen refresh timer
# - initialization gtk-opengl
# - workaround esc key - program cancelation
# - global keyboard handler


# Foren modules
import gc
import gtk
import gtk.gdkgl
import glib
from datetime import datetime
import OpenGL

OpenGL.ERROR_CHECKING = False
OpenGL.ERROR_LOGGING = False
from OpenGL.GL import *

# Native modules
import glwidgets
import gltools
import tools


dt_draw_us = None
t_us = datetime.now().microsecond
saved_exception_hook = None
_ms_new = 0
_ms_prev = 0

_quit_flag = False
_redraw_timer = 20
_timer_min_ms = 33


def on_key_callback(window, event, ui, user_module):
      user_module.on_key_callback(window, event, ui)
      return False


def on_expose_event(gda, event, ui, user_module):
    global dt_draw_us, t_us, flash_alpha

    # Monitor redraw time
    t0_us = datetime.now().microsecond

    # GTK begin draw in OpenGL context
    gda.gldrawable.gl_begin(gda.glcontext)

    if _quit_flag:
        ui.uninit()
        glDeleteTextures(gltools.__textures__)
        # Error handling in OpenGL
        gltools.check_glerrors('on_expose_event')
        gda.window.unset_gl_capability()
        # OpenGL context cancelation
        gda.gldrawable.wait_gl()
        gda.gldrawable.swap_buffers()
        gda.gldrawable.gl_end()
        gda.gldrawable = None
        gda.glcontext = None
        gc.collect()
        gtk.main_quit()

    # Update flashing light
    gltools.step_flash()

    # Direct OpenGL draw
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Redraw widgets if needed (display lists compilation)
    glwidgets.redraw_queue()

    ui.on_expose_event(event)
    user_module.on_expose(ui, event)

    # Error handling
    gltools.check_glerrors('on_expose_event()')

    # Switch out from OpenGL context
    if gda.gldrawable:
        gda.gldrawable.swap_buffers()
        gda.gldrawable.gl_end()

    ui.time_now = datetime.now()

    # Monitor redraw time
    t1_us = ui.time_now.microsecond
    dt_draw_us = tools.delta_tick(t0_us, t1_us, 999999)

    return False


def on_realize(gda, ui, user_module):
    gtk.gdkgl.ext(gda.window)
    gda.gldrawable = gda.window.set_gl_capability(gda.glconfig)

    gda.glcontext = gtk.gdkgl.Context(gda.gldrawable)

    gda.gldrawable.wait_gdk()
    gda.gldrawable.gl_begin(gda.glcontext)

    # Initialization
    gltools.init(gda)
    ui.init()
    user_module.on_realize(ui)

    gltools.check_glerrors('on_realize()')
    gda.gldrawable.wait_gl()
    gda.gldrawable.gl_end()


def on_timer_tick(ui, user_module):
    # Make a trick with go ahead redraw timer: low down refresh rate,
    # if redraw timer fired before redraw procedure complits.
    global _redraw_timer, dt_timer_us, t_timer_us, _ms_new, _ms_prev
    rect = gtk.gdk.Rectangle(0, 0, ui.gda.allocation.width, ui.gda.allocation.height)
    ui.gda.window.invalidate_rect(rect, True)
    ui.gda.window.process_updates(True)
    _ms_new = int((dt_draw_us * 2) // 1000.0)
    if _ms_new < _timer_min_ms:
        _ms_new = _timer_min_ms
    _redraw_timer = _ms_new
    user_module.on_redraw_timer(ui, _ms_prev)
    _ms_prev = _ms_new
    glib.timeout_add(_ms_new, on_timer_tick, ui, user_module)
    return False
