#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Опредеяемый пользователем модуль. Здесь можно добавлять свой код

import glwidgets
import gltools


def init(*args):
    pass


def on_realize(ui):
    """
    Вызывается при инициализации. Создавай виджеты здесь
    :param ui:
    :return:
    """
    txrs = ui.get_textures('btn%u.png', 2)  # 'btn0.png', 'btn1.png'
    btn1 = glwidgets.Button(ui.gda, (220, 10), 'Button1', txrs, user_proc=on_btn1_clicked, check_part=(0.25, 0.5))
    btn1.show()
    ui.scene.append(btn1)


def on_btn1_clicked(btn1):
    print 'on_btn1_clicked(): btn.text:%s btn1.state:%u' % (btn1.text, btn1.state)


def on_key_callback(*args):
    """
    Вызывается при нажатии на клавиши. Обрабатывай события ввода здесь
    :param args:
    :return:
    """
    print 'on_key_callback():', args
    return False


def on_expose(*args):
    """
    Вызывается для перерисовки окна.
    Добавляйте код рисования использующий OpenGL API здесь
    :param args:
    :return:
    """
    for i in range(40):
        gltools.draw_line((10, 20 + i * 20), (200, 20 + i * 20), (200, 200, 255, i * 20 + 30))


def on_redraw_timer(*args):
    pass