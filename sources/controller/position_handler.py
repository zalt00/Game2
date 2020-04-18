# -*- coding:Utf-8 -*-

from pymunk.vec2d import Vec2d
from .trajectory import CameraMovementTrajectory
from time import perf_counter


class StaticPositionHandler:
    def __init__(self, pos):
        self.pos = pos
        
    def update_position(self, entity, n=1):
        return self.pos[0] + entity.dec[0] + entity.screen_dec[0], -self.pos[1] + entity.dec[1] + entity.screen_dec[1]


class BgLayerPositionHandler:
    def __init__(self, pos, screen_dec_ref, end_trajectory_callback=None):
        self.sdr = screen_dec_ref
        self.pos = list(pos)
        self.base_pos = tuple(pos)
        self.trajectory = None
        self.trajectory_duration = 0
        self.advance = 0
        self.end_trajectory = end_trajectory_callback
        
    def add_trajectory(self, target, total_duration, fade_in, fade_out):
        npos = target[0] + self.base_pos[0], target[1] + self.base_pos[1]
        self.trajectory = CameraMovementTrajectory(tuple(self.pos), npos, total_duration, fade_in, fade_out)
        self.trajectory_duration = total_duration
        self.advance = 0
        
    def update_position(self, entity, n=1):
        if self.trajectory is not None:
            end = False
            
            self.advance += n
            if self.advance > self.trajectory_duration:
                self.advance = self.trajectory_duration
                end = True
            
            
            npos = self.trajectory(self.advance)
            self.pos[0], self.pos[1] = npos[0], npos[1]
            if end:
                self.trajectory_duration = 0
                t = self.trajectory
                self.trajectory = None
                self.advance = 0
                if self.end_trajectory is not None:
                    self.end_trajectory(t)

        self.sdr[0] = self.pos[0] - self.base_pos[0]
        self.sdr[1] = self.pos[1] - self.base_pos[1]
        
        n_layers = len(entity.image_handler.res.layers)
        i = (n_layers - entity.layer) ** 2

        return self.pos[0] / i + entity.dec[0], -self.pos[1] / i + entity.dec[1]
                

class EntityPositionHandler:
    def __init__(self, body):
        self.body = body
        self.pos = [0, 0]
    
    def update_position(self, entity, n=1):
        for _ in range(1):
            if entity.state == 'walk':
                if abs(self.body.velocity.x) < 60:
                    entity.thrust.x = 60000 * entity.direction
            elif entity.state == 'run':
                if abs(self.body.velocity.x) < 150:
                    entity.thrust.x = 60000 * entity.direction
            elif entity.secondary_state == 'slowly_walk':
                if abs(self.body.velocity.x) < 50:
                    entity.thrust.x = 60000 * entity.direction
            elif entity.secondary_state == 'slowly_run':
                if abs(self.body.velocity.x) < 130:
                    entity.thrust.x = 60000 * entity.direction
            elif entity.secondary_state == 'walk':
                if abs(self.body.velocity.x) < 60:
                    entity.thrust.x = 60000 * entity.direction
            elif entity.secondary_state == 'run':
                if abs(self.body.velocity.x) < 150:
                    entity.thrust.x = 60000 * entity.direction
            elif entity.state == 'dash':
                entity.thrust = Vec2d(0, 0)
                self.body.velocity = Vec2d(2000 * entity.direction, 0)
            
            elif entity.air_control:
                if (abs(self.body.velocity.x) < 60 or
                    (entity.direction == -1 and self.body.velocity.x > 0) or
                    (entity.direction == 1 and self.body.velocity.x < 0)):
                    
                    entity.thrust.x = 50000 * entity.air_control
                entity.air_control = 0
            
            self.body.apply_force_at_local_point(entity.thrust, (0, 0))
            entity.thrust = Vec2d(0, 0)
            
        self.pos = self.body.position
        return self.body.position.x + entity.dec[0] + entity.screen_dec[0], -self.body.position.y + entity.dec[1] + entity.screen_dec[1]
    
    

class PlayerPositionHandler(EntityPositionHandler):
    def __init__(self, body, triggers):
        self.triggers = triggers
        super().__init__(body)

    def update_position(self, entity, n=1):
        x, y = super().update_position(entity, n)
        for trigger in self.triggers:
            trigger.update(self.body.position.x, self.body.position.y)
        #print(x, y, '                                         ', end='\r')
        return x, y
    
    
