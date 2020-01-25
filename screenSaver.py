import math
from copy import copy

import pygame
import random
from pygame import event, display, color, font
from pygame.constants import *
from abc import ABC, abstractmethod

class Vec2dConversionError(Exception):
    pass


class Vec2d:
    def __init__(self, x, y, speed=None):
    
        self.speed = speed
        self.x = float(x)
        self.y = float(y)

    def __str__(self):
        return f"Vec2d type object x={self.x}, y={self.y}"

    def __len__(self) -> int:
        return len(self)

    def len(self):
        return self.length

    def _to_vec(self, other, y=None):
        """преобразует, если это возможно, параметр other в обьект self.__class__
        выбрасывает исключение Vec2dConversionError
        возвращает обьект Vec2d

        """

        if y is not None:
            """если в метод (sub, add) передали точку (x,y) а не объект вектора"""
            return self.__class__(int(other), int(y))

        elif type(other) is self.__class__:
            return other

        elif type(other) is tuple or list:
            """если в оператор (-, +) передали точку (x,y) а не объект вектора"""
            x, y = other
            return self.__class__(x, y)

    @property
    def length(self):
        """возвращает длину вектора"""
        return math.sqrt(self.x**2 + self.y**2)

    @property
    def vec(self):
        """Возвращает координаты конца вектора в виде tuple(x, y)"""
        return self.x, self.y

    def int_pair(self):
        """возвращает целые координаты конца вектора в виде tuple(int, int)"""
        return int(self.x), int(self.y)

    def add(self, other, y=None):
        """возвращает сумму двух векторов"""
        other = self._to_vec(other, y)

        temp = copy(self)
        temp.x = self.x + other.x
        temp.y = self.y + other.y

        return temp
        # return self.__class__(self.x + other.x, self.y + other.y)

    def __add__(self, other):
        """ переопределяет оператор + ,
         возвращает вектор
         """
        return self.add(other)

    def __radd__(self, other):
        """ переопределяет оператор + , когда Vec2d стоит справа (1, 2) + Vec2d
         возвращает вектор
         """
        return self.add(other)

    def sub(self, other, y=None):
        """"возвращает разность двух векторов"""
        other = self._to_vec(other, y)

        temp = copy(self)
        temp.x = self.x - other.x
        temp.y = self.y - other.y

        return temp

        # return self.__class__(self.x - other.x, self.y - other.y)

    def __sub__(self, other, y=None):
        """ переопределяет оператор - ,
        возвращает вектор
        """
        return self.sub(other)

    def __rsub__(self, other, y=None):
        """ переопределяет оператор - , когда Vec2d стоит справа (1, 2) - Vec2d
         возвращает вектор
         """
        other = self._to_vec(other, y)
        return other.sub(self)

    def mul(self, other):
        """возвращает произведение вектора на число"""

        temp = copy(self)
        temp.x = self.x * other
        temp.y = self.y * other

        return temp

        #return self.__class__(self.x * other, self.y * other)

    def __mul__(self, other):
        """ переопределяет оператор * (умножение на скаляр),
         возвращает вектор
         """
        return self.mul(other)

    def __rmul__(self, other):
        """ переопределяет оператор * (умножение на скаляр) 2 * Vec2d,
        знак умножения стоит слева от вектора
         возвращает вектор
         """
        return self.mul(other)


class Polyline(ABC):
    def __init__(self, scr):

        self._scr = scr    # пространство экрана отрисовки
        self._size = self._scr.get_size()  # размер экрана scr

        self._steps = 35     # число точек сглаживания

        self._width = 3

        self._hue = 0
        self.saturation = 50
        self._color = pygame.color.Color(0)

        self._points = []
        self._speeds = []

    def resize(self, new_size):
        self._size = new_size

    def reset(self):
        self._points = []
        self._speeds = []

    @property
    def increase_steps(self):
        self._steps += 1
        return self._steps

    @property
    def decrease_steps(self):
        if self._steps > 1:
            self._steps -= 1
        return self._steps

    @property
    def steps(self):
        return self._steps

    @property
    def color(self):

        hue = random.randint(1, 4)
        self._hue = (self._hue + hue) % 360
        self._color.hsla = (self._hue, self.saturation, 50, 100)

        return self._color

    def add_point(self, pos):
        """
        добавление одной опорной точки
        и её скорости
        эти точки летают по экрану, на их положении в пространстве
        рассчитываются координаты цветных линий
        изначально программа запускается с экраном 800:600,
        поэтому скорость точек совпадает вначале с заданием
        я добавил возможность менять размер экрана,
        скорость новой точки будет уменьшаться с уменьшением экрана
        """
        speed = Vec2d(random.random() * self._size[0] / 400,
                      random.random() * self._size[1] / 300)
        point = Vec2d(*pos, speed=speed)
        self._points.append(point)
        self._speeds.append(Vec2d(random.random() * self._size[0] / 400,
                                  random.random() * self._size[1] / 300))

    def _set_point_speed_attached(self, point: Vec2d):
        """функция перерасчета координат одной опорной точки"""
        ps = point + point.speed

        if ps.x <= 0:
            ps.x = 0
            ps.speed.x = -ps.speed.x
        elif ps.x >= self._size[0]:
            ps.x = self._size[0]
            ps.speed.x = -ps.speed.x

        if ps.y <= 0:
            ps.y = 0
            ps.speed.y = -ps.speed.y
        elif ps.y >= self._size[1]:
            ps.y = self._size[1]
            ps.speed.y = -ps.speed.y

        return ps

    def _set_point(self, point: Vec2d, speed: Vec2d):
        """функция перерасчета координат одной опорной точки"""
        ps = point + speed

        if ps.x <= 0:
            ps.x = 0
            speed.x = -speed.x
        elif ps.x >= self._size[0]:
            ps.x = self._size[0]
            speed.x = -speed.x

        if ps.y <= 0:
            ps.y = 0
            speed.y = -speed.y
        elif ps.y >= self._size[1]:
            ps.y = self._size[1]
            speed.y = -speed.y

        return ps, speed

    def set_points(self):
        """функция перерасчета координат всех опорных точек"""
        self._points = list(map(self._set_point_speed_attached, self._points))


    def get_points(self):
        return self._points

    def draw_points(self, pause_=True, color=(255, 255, 255)):
        """функция отрисовки опорных точек на экране"""

        for p in self._points:
            pygame.draw.circle(self._scr, color,
                               p.int_pair(), self._width)

        if not pause_:
            self.set_points()

    def draw_line(self, pause_=True):
        """функция отрисовки цветных загадочных линий на экране,
        используется абстрактная функция self.get_knot(), которая
        определяется в классе-наследнике

        """

        color_ = self.color
        knot_points = self.get_knot()

        for i in range(-1, len(knot_points) - 1):
            pygame.draw.line(self._scr, color_,
                             knot_points[i].vec,
                             knot_points[i+1].vec, self._width)

        if not pause_:
            self.set_points()

    def draw(self, pause_=True, kaleidoscope=False, lines_only=False):
        """рисовать и точки, и линии"""

        if not kaleidoscope and not lines_only:
            self.draw_points(pause_=True)

        self.draw_line(pause_=True)

        if not pause_:
            self.set_points()

    def remove_point(self):
        if len(self._points) > 4:
            del self._points[-1]

    def speed_up(self):
        for i, point in enumerate(self._points):
            self._points[i].speed *= 1.1

    def speed_down(self):
        for i, point in enumerate(self._points):
            self._points[i].speed *= 0.9

    @abstractmethod
    def get_knot(self):
        """по условию задания этот метод должет быть определен
        в классе-наследнике"""
        pass


class Knot(Polyline):

    def _get_knot_point(self, base_points, alpha, deg=None):
        """ рисует одну точку в цветной линии"""

        if deg == 0:
            return base_points[0]

        elif deg is None:
            deg = len(base_points) - 1

        p1 = base_points[deg] * alpha
        p2 = self._get_knot_point(base_points, alpha, deg - 1) * (1 - alpha)

        result = p1 + p2
        return result

    def _get_knot_points(self, base_points):
        """ рисует кривую по трём опорным точкам
        base_points всегда три точки для отрисовки плавной линии"""
        res = []
        for i in range(self.steps):
            res.append(self._get_knot_point(base_points, i / self.steps))

        return res

    def get_knot(self):
        """ рисует полную замкнутую кривую по всем опорным точкам"""
        res = []

        if len(self._points) - 2 > 0:
            for i in range(-2, len(self._points) - 2):
                p = self._points[i]
                p2 = self._points[i + 1]
                p3 = self._points[i + 2]

                base_points = [
                    (p + p2) * 0.5,
                    p2,
                    (p2 + p3) * 0.5
                ]

                res.extend(self._get_knot_points(base_points))

        return res


class ScreenSaver:
    def __init__(self, knots):

        self._scr = self._init_surface()
        self._knots = [knot_obj(self._scr) for knot_obj in knots]
        self._steps = 35
        self._show_help = False
        self._kaleidoscope = False
        self._pause = True
        self._lines = 3     # число кривых на экране, можно регулировать <Alt+><Alt->

        self._lines_only = False

    @property
    def scr(self):
        return self._scr

    @staticmethod
    def _init_surface():
        """"инициализирует приложение, экран, библиотеки """

        pygame.init()

        screen_ = display.set_mode((0, 0), RESIZABLE)
        display.set_caption("NovozhilovScreenSaver")

        pygame.key.set_repeat(100, 100)
        return screen_

    def show_help(self):
        """функция отрисовки экрана справки программы"""

        self._scr.fill((50, 50, 50))
        font1 = pygame.font.SysFont("courier", 20)
        font2 = pygame.font.SysFont("serif", 20)
        data = [

            ["added:", "Kaleidoscope, Curves number, Resizable screen, Delete points"],

            ["L", "Beautiful lines only"],
            ["Alt+/-", "More or less Curves"],
            ["F1", "Show this Help"],
            ["R", "Restart"],
            ["P", "Pause/Play"],
            ["Num+/-", "More or less smoothing points"],
            ["Del", "Delete support points"],
            ["K", "Kaleidoscope"],
            ["Ctrl+/-", "Speed Up/Down the curves"],
            [" ", " "],
            [str(self._steps), "Current smoothing points"],
            [str(self._lines), "Lines on screen"],
        ]
        pygame.draw.lines(self._scr, (255, 50, 50, 255), True,
                          [(0, 0),
                           (self._scr.get_clip()[2], 0),
                           (self._scr.get_clip()[2], self._scr.get_clip()[3]),
                           (0, self._scr.get_clip()[3])
                           ], 5)

        for i, text in enumerate(data):
            self._scr.blit(font1.render(
                text[0], True, (128, 128, 255)), (100, 100 + 30 * i))
            self._scr.blit(font2.render(
                text[1], True, (128, 128, 255)), (220, 100 + 30 * i))

    def video_resize(self, new_size):
        """функция вызывается при каждом изменении размероов окна мышкой
        выставляет новые размеры рабочей поверхности в объектах Polyline
        опорные точки не будут вылетать за пределы этой зоны
        """
        self._scr.set_clip((0, 0), new_size)
        for knot in self._knots:
            knot.resize(new_size)

    def add_point(self, pos):
        """ставит новую опорную точку по клику левой мышки"""
        for knot in self._knots:
            if random.random() > .5:
                knot.add_point(pos)

    def draw(self):
        """отрисовка всех линий и точек
        здесь точки линии посылаются на физический экран"""

        if self._show_help:
            self.show_help()

        else:
            if not self._kaleidoscope:
                self._scr.fill((0, 0, 0))
            for knot in self._knots[:self._lines]:
                knot.draw(self._pause, self._kaleidoscope, self._lines_only)

        display.flip()

    def switch_kaleidoscope(self):
        """ переключает режим калейдоскопа"""
        self._scr.fill((0, 0, 0))

        self._kaleidoscope = not self._kaleidoscope

    def switch_pause(self):
        """ переключает паузу"""
        self._pause = not self._pause

    def switch_help(self):
        """переключает заставку омощи
        делает копию экрана и потом восстанавливает экран"""
        self._show_help = not self._show_help

        if self._show_help:
            self._copy_scr = self._scr.copy()
        else:
            self._scr.blit(self._copy_scr, (0, 0))

    def increase_steps(self):
        """увеличивает число сглаживающих точек
        но не до бесконечности, мне кажется, 100 достаточно"""
        if self._steps < 100:
            self._steps += 1

        for knot in self._knots:
            knot.increase_steps

    def decrease_steps(self):
        """уменьшает число сглаживающих точек"""
        if self._steps > 1:
            self._steps -= 1

        for knot in self._knots:
            knot.decrease_steps

    def increase_lines(self):
        """увеличивает число линий, отображаемых на экране"""
        if self._lines < len(self._knots):
            self._lines += 1

    def decrease_lines(self):
        """уменьшае линии на экране"""
        if self._lines > 1:
            self._lines -= 1

    def delete_point(self):
        """удаляет последнюю добавленную  опорную точку
        из каждого обьекта Knot"""
        for knot in self._knots:
            knot.remove_point()

    def speed_up(self):
        """ускоряет движение кривых"""
        for knot in self._knots:
            knot.speed_up()

    def speed_down(self):
        """замедляет кривые на экране"""
        for knot in self._knots:
            knot.speed_down()

    def lines_only(self):
        """выключает точки, оставляет на экране только линии"""
        self._lines_only = not self._lines_only

    def reset(self):
        """перезагружает все обьекты Knot
        очищает экран"""
        for knot in self._knots:
            knot.reset()


if __name__ == "__main__":

    screen = ScreenSaver([Knot]*10)

    """
    Нажатие клавиатуры
    вся эта информация доступна в Помощи по нажатию  <F1>
    
    Я добавил 
        изменение размера экрана мышкой
        уменьшение/увеличение числа линий,
        скорость линий
        повтор клавиш, можно нажать и не отпускать, будут добавляться точки, ускоряться кривые и т.д.
        режим калейдоскопа (попробуйте, кнопка К)
        режим "только линии"
        удаление точек
        
           
    """
    key_handler = {
        (KMOD_NONE, K_r): screen.reset,                  # r, R перезагружает точки, начинает с пустого экрана
        (KMOD_NONE, K_p): screen.switch_pause,           # p, P пауза
        (KMOD_NONE, K_KP_PLUS):  screen.increase_steps,  # "NumLock+" увеличить плавность кривых, уменьшить скорость рисунка
        (KMOD_NONE, K_KP_MINUS): screen.decrease_steps,  # "NumLock-" уменьшить плавность кривых, увеличить скорость рисунка
        (KMOD_NONE, K_k): screen.switch_kaleidoscope,    # k, K режим калейдоскопа
        (KMOD_ALT, K_KP_PLUS): screen.increase_lines,    # "Alt+" увеличить число линий
        (KMOD_ALT, K_KP_MINUS): screen.decrease_lines,    # "Alt-" уменьшить число линий

        (KMOD_CTRL, K_KP_PLUS): screen.speed_up,          # "Ctrl+" ускорить кривые
        (KMOD_CTRL, K_KP_MINUS): screen.speed_down,       # "Ctrl-" замедлить кривые
        (KMOD_NONE, K_DELETE): screen.delete_point,       # "Delete" уменьшить число опорных точек
        (KMOD_NONE, K_l): screen.lines_only,              # "L" только линии

        (KMOD_NONE, K_F1): screen.switch_help            # <F1> экран справки
    }

    while True:

        for ev in pygame.event.get():
            if ev.type == QUIT or (ev.type == KEYDOWN and ev.key == K_ESCAPE):
                display.quit()
                pygame.quit()
                exit(0)

            elif ev.type == VIDEORESIZE:
                screen.video_resize(ev.size)

            elif ev.type == KEYDOWN:

                if ev.mod & KMOD_ALT:
                    key = (KMOD_ALT, ev.key)
                elif ev.mod & KMOD_CTRL:
                    key = (KMOD_CTRL, ev.key)

                else:
                    key = (KMOD_NONE, ev.key)

                if key in key_handler:
                    key_handler[key]()

            elif ev.type == MOUSEBUTTONDOWN:
                screen.add_point(ev.pos)

        screen.draw()

