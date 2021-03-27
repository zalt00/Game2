# -*- coding:Utf-8 -*-

from .position_handler import StaticPositionHandler


class ParticleHandler:
    def __init__(self, spawn_particle_callback):
        self.spawn_particle = spawn_particle_callback
        self.a = 0
        self.particle_id = 0
        
    def update_(self, entity):
        if entity.state == 'dash':
            res = entity.image_handler.res
            self.spawn_particle(entity.position_handler.pos, 'dash_effect', entity.direction, self.particle_id, res,
                                -1, 8)
            self.particle_id += 1
        else:
            self.particle_id = 0



