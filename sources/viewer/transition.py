# -*- coding:Utf-8 -*-

import pygame
from pygame.locals import *
from time import perf_counter
pygame.init()


class Transition:
    def __init__(self, duration, color, surf_size, end_of_transition_callback, fade, stop_after_end=True):
        self.duration = duration
        self.base_color = color
        self.current_surf = pygame.Surface(surf_size, SRCALPHA)
        self.on_transition_end = end_of_transition_callback
        self.fade = fade
        self.stop_after_end = stop_after_end
        self.t0 = perf_counter()
        self.state = 0

    def start(self):
        self.t0 = perf_counter()
        self.state = 1

    def update(self):
        if self.state == 2:
            return None
        elif self.state == 0:
            return self.current_surf

        dt = perf_counter() - self.t0
        n = round(dt * 60)
        if n <= self.duration:
            if self.fade == 'in':
                opacity = round(255 / self.duration * n)
            else:
                opacity = round(255 / self.duration * (self.duration - n))
            color = self.base_color + (opacity,)
            self.current_surf.fill(color)
            return self.current_surf

        else:
            self.on_transition_end()
            self.state = 0
            if self.stop_after_end:
                self.stop()
            return self.current_surf

    def stop(self):
        self.state = 2




