# -*- coding:Utf-8 -*-

from pymunk.vec2d import Vec2d


class StaticPositionHandler:
    def __init__(self, pos):
        self.pos = pos
        
    def update_position(self, entity):
        return self.pos[0] + entity.dec[0], -self.pos[1] + entity.dec[1]

class DynamicPositionHandler:
    def __init__(self, body):
        self.body = body
    
    def update_position(self, entity):
        if entity.state == 'walk':
            if abs(self.body.velocity.x) < 70:
                entity.thrust.x = 60000 * entity.direction
        elif entity.state == 'run':
            if abs(self.body.velocity.x) < 110:
                entity.thrust.x = 60000 * entity.direction
        elif entity.secondary_state == 'walk':
            if abs(self.body.velocity.x) < 70:
                entity.thrust.x = 60000 * entity.direction
        elif entity.secondary_state == 'run':
            if abs(self.body.velocity.x) < 110:
                entity.thrust.x = 60000 * entity.direction

        elif entity.air_control:
            if (abs(self.body.velocity.x) < 60 or
                (entity.direction == -1 and self.body.velocity.x > 0) or
                (entity.direction == 1 and self.body.velocity.x < 0)):
                
                entity.thrust.x = 30000 * entity.air_control
            entity.air_control = 0
        
        self.body.apply_force_at_local_point(entity.thrust, (0, 0))
        entity.thrust = Vec2d(0, 0)

        return self.body.position.x + entity.dec[0], -self.body.position.y + entity.dec[1]

