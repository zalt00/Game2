# -*- coding:Utf-8 -*-


class PhysicsUpdater:
    def __init__(self, body, landing_callback):
        self.body = body
        self.on_ground = False
        self.land = landing_callback
       
    def is_on_ground(self, arbiter):
        shapes = arbiter.shapes
        for shape in shapes:
            if getattr(shape, 'is_solid_ground', False):
                self.on_ground = True
                return
    
    def update(self, entity):
        self.on_ground = False
        self.body.each_arbiter(self.is_on_ground)
        
        landed = (not entity.is_on_ground) and self.on_ground
        entity.is_on_ground = self.on_ground
        if landed:
            self.land()

