# -*- coding:Utf-8 -*-

from utils.types import DataContainer
from pymunk.vec2d import Vec2d


class Objects(DataContainer):
    objects = ('RightStruct', 'LeftStruct', 'MidStruct')

    class RightStruct:
        typ = 'structure'
        res = 'structures/s1.res'
        name = 'right-struct'
        pos_x = 1487
        pos_y = 123
        state = 'base'
        poly = [(Vec2d(-39, 0), Vec2d(-39, 110), Vec2d(39, 110), Vec2d(39, 0))]
        ground = [(Vec2d(38, 111), Vec2d(-38, 111))]

    class LeftStruct:
        typ = 'structure'
        res = 'structures/s1.res'
        name = 'left-struct'
        pos_x = 348
        pos_y = 123
        state = 'base'
        poly = [(Vec2d(-39, 0), Vec2d(-39, 110), Vec2d(39, 110), Vec2d(39, 0))]
        ground = [(Vec2d(38, 111), Vec2d(-38, 111))]

    class MidStruct:
        typ = 'structure'
        res = 'structures/s1.res'
        name = 'mid-struct'
        pos_x = 716
        pos_y = 123
        state = 'base'
        poly = [(Vec2d(-39, 0), Vec2d(-39, 110), Vec2d(39, 110), Vec2d(39, 0))]
        ground = [(Vec2d(38, 111), Vec2d(-38, 111))]
