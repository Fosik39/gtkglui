#!/usr/bin/env python
# -*- coding: utf-8 -*-

# An example of using gtkglui

# Own modules
import uictl


# Create the window for the interface
# 1280, 720, width and height of the window
# 'data' - folder with image files
# 'custom' - Python file-user-defined module: custom.py
# Look in 'custom.py' how to add your widgets and everything else
ui = uictl.UiCtl(640, 480, 'data', 'custom')

# Main loop
ui.main()

