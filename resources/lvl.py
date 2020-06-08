# -*- coding:Utf-8 -*-

from utils.types import DataContainer
from pymunk.vec2d import Vec2d


class Objects(DataContainer):
    objects = ('Structure1', 'Structure2', 'Structure3', 'Structure4')

    class Structure1:
        typ = 'structure'
        res = 'structures/s1.res'
        name = 'structure1'
        pos_x = 980
        pos_y = 178
        state = 'base'
        poly = [(Vec2d(-39, 0), Vec2d(-39, 110), Vec2d(39, 110), Vec2d(39, 0))]
        ground = [(Vec2d(38, 111), Vec2d(-38, 111))]

    class Structure2:
        typ = 'structure'
        res = 'structures/s1.res'
        name = 'structure2'
        pos_x = 278
        pos_y = 178
        state = 'base'
        poly = [(Vec2d(-39, 0), Vec2d(-39, 110), Vec2d(39, 110), Vec2d(39, 0))]
        ground = [(Vec2d(38, 111), Vec2d(-38, 111))]

    class Structure3:
        typ = 'structure'
        res = 'structures/s1.res'
        name = 'structure3'
        pos_x = 510
        pos_y = 178
        state = 'base'
        poly = [(Vec2d(-39, 0), Vec2d(-39, 110), Vec2d(39, 110), Vec2d(39, 0))]
        ground = [(Vec2d(38, 111), Vec2d(-38, 111))]

    class Structure4:
        typ = 'structure'
        res = 'structures/s1.res'
        name = 'structure4'
        pos_x = 771
        pos_y = 178
        state = 'base'
        poly = [(Vec2d(-39, 0), Vec2d(-39, 110), Vec2d(39, 110), Vec2d(39, 0))]
        ground = [(Vec2d(38, 111), Vec2d(-38, 111))]
