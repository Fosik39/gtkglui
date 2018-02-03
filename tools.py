#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Примитивные и часто используемые операции

# Чужие модули
import imp
import math
import os
import struct
import time


def assert_byte(byte):
    # Выкидывает исключение, если byte не в диапазоне
    assert type(byte) is int
    assert 0 <= byte <= 255


def bytes_to_chrs(bytes):
    s = ''
    for b in bytes:
        s += chr(b)
    return s


def get_file_names(dir_path, head):
    """
    Получает список файлов в указанной папке
    :param head: Заголовки столбцов
    :param dir_path: Указанная папка
    :return: Таблица со списком файлов
    """
    rows2 = list()
    rows2.append(head)
    file_names = os.listdir(dir_path)
    for name in file_names:
        full_name = os.path.join(dir_path, name)
        if not os.path.isfile(full_name):
            continue
        t = time.gmtime(os.stat(full_name).st_mtime)
        s = '%04u' % t.tm_year + '-' + '%02u' % t.tm_mon + '-' + '%02u' % t.tm_mday + ' ' + '%02u' % t.tm_hour + ':' + '%02u' % t.tm_min
        rows2.append([name, str(os.stat(full_name).st_size), s])
    return rows2


def str_cut(s, i):
    """
    Отсекает строку по заданному индексу символа
    :param s: Отсекаемая строка
    :param i: Индекс символа с которого отсекается строка включительно
    :return: Отсечённая строка
    """
    sl = str()
    for c in list(s.decode('utf-8'))[:i]:
        sl += c
    return sl


def val_to_ibytes(data, i_data, val, i_bit, i_weght):
    """
    Записывает в буфер байтов data код значения val
    :param data: Буфер байтов
    :param i_data: Индекс первого байта в буфере
    :param val: Значение
    :param i_bit: Индекс значащего разряда
    :param i_weght: Вес значащего разряда
    :return: Ничего
    """
    val = int((val * float(1 << i_bit)) / float(i_weght))
    data[i_data] = val & 0xff
    data[i_data + 1] = (val >> 8) & 0xff


def ibytes_to_val(data, i_data, i_bit, i_weght):
    """
    Возвращает реальное значение поля из массива байтов
    :param data: Массив байтов в ввиде int
    :param i_data: Индекс первого байта слова в массиве data
    :param i_bit: Индекс значащего разряда
    :param i_weght: Вес значащего разряда
    :return: Реальное значение
    """
    nu = struct.unpack('=h', chr(data[i_data]) + chr(data[i_data + 1]))[0]
    return (nu * i_weght) / float(1 << i_bit)


def get_mask32(width, shift=0):
    """
    Возвращает битовую маску заданной ширины непрерывно заполненную еденицами.
    Максимальная ширина - 32 бита.
    :param width: Ширина битовой маски. int
    :param shift: Смещение битовой маски в лево, т.е. к старшим разрядам. int
    :return: Битовая маска. int
    """
    assert 0 <= shift <= 32
    assert 0 <= width <= 32
    mask = 0
    for i in range(width):
        mask |= 1 << i
    return mask << shift


def get_lbyte_from_word(data, i):
    """
    Возвращает младший байт массива 16 битных слов
    :param data: Массив слов
    :param i: Индекс слова в массиве
    :return: Младший байт
    """
    return data[i] & 0xff


def get_hbyte_from_word(data, i):
    """
    Возвращает старший байт из слова
    :param data: Массив слов
    :param i: Индекс слова в массиве
    :return: Старший байт
    """
    return (data[i] & 0xff00) >> 8


def load_module(name, dir_name=None):
    """
    Загружает модуль из файла
    :param name: Название модуля
    :param dir_name: Путь к папке с модулем
    :return: Модуль
    """
    assert type(name) is str  # Имя модуля должна быть строка
    if dir_name is None:
        fp, pathname, description = imp.find_module(name)
    else:
        fp, pathname, description = imp.find_module(name, [dir_name])
    return imp.load_module(name, fp, pathname, description)


def set_wordi(buf, index, val):
    """
    Возвращает слово из байтового массива
    :param buf: Байтовый массив
    :param index: Индекс младшего байта слова в массиве
    :param val: Значение слова для записи в батовый массив
    :return: None
    """
    buf[index] = val & 0xff
    buf[index + 1] = (val >> 8) & 0xff


def set_bit(bits, index, val, mask=0xffff):
    """
    :param bits: прежние значения
    :param index: индекс бита
    :param val: новое значение бита
    :param mask:
    :return:
    мастер
    """
    bits &= mask
    if val:
        bits |= 1 << index
    else:
        bits &= ~(1 << index)
    return bits & mask


# TODO: Проверить
def set_bits(old, new, mask):
    """
    Устанавливает биты в соответствии с маской
    :param old: Прежние значения бит
    :param new: Новые значения бит
    :param mask: Маска изменяемых бит
    :return: Изменённые значения бит
    """
    old ^= (-new ^ old) & mask
    return old



def get_bit(bits, index, mask=0xffff):
    bits &= mask
    return ((bits & mask) & (1 << index)) > 0


def set_bytes(b, i, w):
    """
    Записывает слово в байтовый массив
    """
    w = int(w)
    b[i] = w & 0xff
    b[i + 1] = (w & 0xff00) >> 8


def chrs_to_word(s, i):
    return ord(s[i]) | (ord(s[i + 1]) << 8)


def ibytes_to_word(b, i):
    return b[i] | (b[i + 1] << 8)


def delta_tick(tick0, tick1, tick_max=65535):
    if tick1 > tick0:
        dtick = tick1 - tick0
    else:
        dtick = tick_max - tick0 + tick1
    return dtick


def check_rect(width, height, pos, x1, y1):
    """
    Проверяет попадает ли точка в прямоугольник
    :param width: Ширина прямоугольника
    :param height: Высота прямоугольника
    :param pos: Левый верхний угол прямоугольника
    :param x1: Координаты точки на экране
    :param y1: Координаты точки на экране
    :return: True - если попадает, False - если не попадает
    """
    if pos[0] < x1 < (pos[0] + width):
        return pos[1] < y1 < (pos[1] + height)
    return False


def check_ring(r1, r2, x, y, ex, ey):
    """
    Проверяет попадает ли точка в кольцо
    :param r1: Внутренний радиус
    :param r2: Внешний радиус
    :param x: Центр кольца по оси X
    :param y: Центр кольца
    :param ex: Проверяемая точка
    :param ey: Проверяемая точка
    :return: True - если попадает, False - если не попадает
    """
    dx, dy = x - ex, y - ey
    r = math.sqrt(dx * dx + dy * dy)
    return r1 < r < r2


# return angl(degree's) and redius form coordinats
def pos_to_ang(x0, y0, x, y):
    x_ = x - x0
    y_ = y - y0
    ang = (math.atan2(y_, x_) * 180.0) / math.pi
    if ang < 0.0:
        ang += 360.0
    redius = math.sqrt(x_ * x_ + y_ * y_)
    return ang, redius


# return coordinats form angl(degree's) and redius
def ang_to_pos(x0, y0, a, r):
    ang = a
    if ang < 0.0:
        ang += 360.0
    ang_r = math.radians(ang)
    x = r * math.cos(ang_r)
    y = r * math.sin(ang_r)
    return x - x0, y - y0
