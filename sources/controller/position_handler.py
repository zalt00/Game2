# -*- coding:Utf-8 -*-

from pymunk.vec2d import Vec2d
from .trajectory import CameraMovementTrajectory
from time import perf_counter
from queue import Queue


class StaticPositionHandler:
    def __init__(self, pos):
        self.pos = pos
        
    def update_position(self, entity, n=1):
        return self.pos[0], self.pos[1]


class BgLayerPositionHandler:
    def __init__(self, pos, screen_offset, end_trajectory_callback=None):
        self.sdr = screen_offset
        self.pos = list(pos)
        self.base_pos = tuple(pos)

    def update_position(self, entity, n=1):
        i = abs(entity.get_layer())

        if i == 0:
            i = 1

        return self.base_pos[0] + self.sdr[0] / i, self.base_pos[1] + self.sdr[1] / i
                

class EntityPositionHandler:
    def __init__(self, body):
        self.body = body
        self.pos = [0, 0]

        self.jumped = False
        self.jump_counter_deactivation_states = {'fall', 'land', 'walk', 'idle', 'run'}

        self.mapping = dict(
            walk=50,
            run=130,
            slowly_walk=50,
            slowly_run=130,
        )

    def update_position(self, entity, n=1):
        if entity.state in self.jump_counter_deactivation_states:
            self.jumped = False

        m = max(self.mapping.get(entity.state, -1),
                self.mapping.get(entity.secondary_state, -1))
        if abs(round(self.body.velocity.x)) <= m and entity.is_on_ground:
            entity.thrust.x = 200000 * entity.direction / max(abs(self.body.velocity.x * 5 / m), 1)

        if entity.state == 'jump' and entity.is_on_ground and not self.jumped:
            self.jumped = True
            entity.thrust.y = 1_250_000

        elif entity.state == 'dash':
            entity.thrust = Vec2d(0, 0)
            self.body.velocity = Vec2d(2500 * entity.direction, 0)

        elif entity.air_control and entity.can_air_control:
            if (abs(self.body.velocity.x) < 100 or
                    (entity.direction == -1 and self.body.velocity.x > 0) or
                    (entity.direction == 1 and self.body.velocity.x < 0)):

                v = max(min(100 * entity.air_control - self.body.velocity.x, 50), -50)
                self.body.velocity += Vec2d(v, 0)
            entity.air_control = 0

        self.body.apply_force_at_local_point(entity.thrust, self.body.center_of_gravity)
        entity.thrust = Vec2d(0, 0)

        self.pos = self.body.position
        return self.body.position.x, self.body.position.y
    

class PlayerPositionHandler(EntityPositionHandler):
    def __init__(self, body, triggers):
        self.triggers = triggers
        self.do_update_triggers = False
        super().__init__(body)

    def update_position(self, entity, n=1):
        x, y = super().update_position(entity, n)
        if self.do_update_triggers:
            self.update_triggers()
        return x, y

    def update_triggers(self):
        for trigger in self.triggers:
            trigger.update(self.body.position.x, self.body.position.y)

