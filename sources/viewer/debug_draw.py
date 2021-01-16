# -*- coding:Utf-8 -*-


import pymunk.pyglet_util


class DrawOptions(pymunk.pyglet_util.DrawOptions):
    def __init__(self, window, **kwargs):
        self.window = window
        self.vecs = list()
        super(DrawOptions, self).__init__(**kwargs)

    def _convert_pos(self, pos):
        if pos not in self.vecs:
            pos = pos + self.window.screen_offset
            self.vecs.append(pos)
        return pos

    def draw_circle(self, pos, *args, **kwargs):
        pos = self._convert_pos(pos)
        super(DrawOptions, self).draw_circle(pos, *args, **kwargs)

    def draw_segment(self, a, b, color):
        a = self._convert_pos(a)
        b = self._convert_pos(b)
        super(DrawOptions, self).draw_segment(a, b, color)

    def draw_fat_segment(self, a, b, *args, **kwargs):
        a = self._convert_pos(a)
        b = self._convert_pos(b)
        super(DrawOptions, self).draw_fat_segment(
            a, b, *args, **kwargs)

    def draw_polygon(self, verts, *args, **kwargs):
        super(DrawOptions, self).draw_polygon([self._convert_pos(vec) for vec in verts], *args, **kwargs)
        
    def draw_dot(self, size, pos, color):
        pos = self._convert_pos(pos)
        super(DrawOptions, self).draw_dot(size, pos, color)
