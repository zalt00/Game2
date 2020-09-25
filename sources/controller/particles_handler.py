# -*- coding:Utf-8 -*-

from .position_handler import StaticPositionHandler


class ParticleHandler:
    def __init__(self, spawn_particle_callback):
        self.spawn_particle = spawn_particle_callback
        self.a = 0
        
    def update_(self, entity):
        if entity.state == 'dash':
            res = entity.image_handler.res
            ph = StaticPositionHandler(entity.position_handler.pos)
            self.spawn_particle(res, ph, 'dash_effect', entity.raw_dec, entity.direction)



