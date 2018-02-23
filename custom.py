#!/usr/bin/env python
# -*- coding: utf-8 -*-


# User-defined module. Here you can add your own code

import glwidgets
import gltools


def on_realize(ui):
    """
    Called during initialization. Create your widgets *here only*
    :param ui:
    :return: None
    """
    # Загрузить текстуры. Количество текстур равно количеству
    # состояний кнопки. Поле Button.state хранит текущее состояие кнопки
    txrs = ui.get_textures('btn%u.png', 2)  # 'btn0.png', 'btn1.png'
    btn1 = glwidgets.Button(ui.gda, (220, 10), 'Button1', txrs, user_proc=on_btn1_clicked, check_part=(0.25, 0.5))
    btn1.show()
    ui.scene.append(btn1)

    rows = [['  Name  ', ' Age '], ['Bobby', '78'], ['Carl', '12'], ['Moony', '15']]
    tbl1 = glwidgets.Table(ui.gda, (220, 100), rows)
    tbl1.show()
    ui.scene.append(tbl1)

    font1 = glwidgets.GlFont('Liberation Serif', 55)
    txt = glwidgets.StaticText(ui.gda, (220, 250), 'Static Text with\nline separator, e.g. \nwith \'\\n\' symbols', font1, color=(255, 127, 63, 255))
    ui.scene.append(txt)

    reg1 = glwidgets.TextRegulator(ui.gda, (30, 140), fmt=u'%0.3f\u2190Click and\nmove up and down')
    ui.scene.append(reg1)

    entry1 = glwidgets.Entry(ui.gda, (400, 10), 'type here')
    ui.scene.append(entry1)

    # Also, instead of using ui.scene.append(), you can add new items
    # to the scene with this maner: ui.scene += [btn1, tbl1]


def on_btn1_clicked(btn1):
    """
    'Button1' click handler. Try to do something here
    :param btn1:
    :return:
    """
    print 'on_btn1_clicked(): btn1.text:%s btn1.state:%u' % (btn1.text, btn1.state)


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
    Called to redraw the window. Add the
    drawing code that uses OpenGL API here. This
    callback is assigned to custom draw purpose,
    if you *really* need it.
    :param args:
    :return:
    """
    for i in range(12):
        pos0 = 10, 20 + i * 20  # X and Y for line begin
        pos1 = 200, 20 + i * 20  # X and Y for line end
        color = (200, 200, 255, i * 20 + 30)  # Colors are: RGBA
        gltools.draw_line(pos0, pos1, color)  # Draw some nice line


def on_redraw_timer(*args):
    """
    Called to custom animations when redraw timer is fired
    :param args:
    :return:
    """
    pass
