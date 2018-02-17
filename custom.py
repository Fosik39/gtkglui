#!/usr/bin/env python
# -*- coding: utf-8 -*-


# User-defined module. Here you can add your own code

import glwidgets
import gltools



def on_realize(ui):
    """
    Is called during initialization. Create widgets *here only*
    :param ui:
    :return: None
    """
    txrs = ui.get_textures('btn%u.png', 2)  # 'btn0.png', 'btn1.png'
    btn1 = glwidgets.Button(ui.gda, (220, 10), 'Button1', txrs, user_proc=on_btn1_clicked, check_part=(0.25, 0.5))
    btn1.show()
    ui.scene.append(btn1)

    headers = ('Name', 'Age')
    rows = ('Bobby', '78'), ('Karl', '12'), ('Moony', '15')
    tbl1 = glwidgets.Table(ui.gda)


def on_btn1_clicked(btn1):
    print 'on_btn1_clicked(): btn.text:%s btn1.state:%u' % (btn1.text, btn1.state)


def on_key_callback(*args):
    """
    Called when you press a key. Handle input events here
    :param args:
    :return:
    """
    print 'on_key_callback():', args
    return False


def on_expose(*args):
    """
    Is called to redraw the window. Add the
    drawing code that uses OpenGL API here. This
    callback is assigned to custom draw purpose,
    if you *really* need it.
    :param args:
    :return:
    """
    for i in range(40):
        pos0 = 10, 20 + i * 20  # X and Y for line begin
        pos1 = 200, 20 + i * 20  # X and Y for line end
        color = (200, 200, 255, i * 20 + 30)  # Colors are: RGBA
        gltools.draw_line(pos0, pos1, color)  # Draw some nice line


def on_redraw_timer(*args):
    pass