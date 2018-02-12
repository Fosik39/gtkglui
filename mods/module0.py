import glwidgets


def init(*args):
    pass


def on_realize(ui):
    txr0 = ui.get_texture('0000000000.bmp')
    btn = glwidgets.Button(ui.drawing_area, (100, 100), 'ASDFG', txr0)
    btn.show()
    ui.scene.append(btn)


def on_key_callback(*args):
    pass


def on_expose(*args):
    pass

def on_redraw_timer(*args):
    pass