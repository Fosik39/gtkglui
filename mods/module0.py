import glwidgets


def init(*args):
    pass


def on_realize(ui):
    txrs = ui.get_textures('btn%u.png', 2)
    btn = glwidgets.Button(ui.drawing_area, (100, 100), 'Button', txrs, check_part=(0.25, 0.5))
    btn.show()
    ui.scene.append(btn)


def on_key_callback(*args):
    pass


def on_expose(*args):
    pass

def on_redraw_timer(*args):
    pass