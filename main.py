#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Пример использования gtkglui

# Свои модули
import uictl


# 1280, 720 - ширина и высота экраа
# 'data' - папка с файлами изображений
# 'module0' - файл питон-модуль, определяемый пользователем: module0.py
ui = uictl.UiCtl(1280, 720, 'data', 'module0')

# Главный цикл
ui.main()

