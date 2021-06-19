# -*- coding:Utf-8 -*-

from time import perf_counter
import pyglet


class Transition:
    def __init__(self, duration, color, img_size, end_of_transition_callback, fade, stop_after_end=True, priority=0):
        self.duration = duration
        self.base_color = color
        if len(self.base_color) == 3:
            self.base_color += (255,)
        img = pyglet.image.SolidColorImagePattern(self.base_color).create_image(img_size[0], img_size[1])
        self.sprite = pyglet.sprite.Sprite(img.get_texture())

        self.on_transition_end = end_of_transition_callback
        self.fade = fade
        self.stop_after_end = stop_after_end

        self.t0 = perf_counter()
        self.state = 0

        self.priority = priority

    def start(self):
        self.t0 = perf_counter()

    def update(self):
        dt = perf_counter() - self.t0
        n = round(dt * 60)
        if n <= self.duration:
            if self.fade == 'in':
                opacity = round(255 / self.duration * n)
            else:
                opacity = round(255 / self.duration * (self.duration - n))
            self.sprite.opacity = opacity

        elif self.state == 0:
            self.state = 1
            if self.stop_after_end:
                self.stop()

            self.on_transition_end()

    def stop(self):
        self.state = 2




