# -*- coding:Utf-8 -*-

from pymunk.vec2d import Vec2d
from .trajectory import CameraMovementTrajectory
from time import perf_counter
from queue import Queue
import numpy as np
from math import pi
import math


class StaticPositionHandler:
    def __init__(self, pos):
        self.pos = pos
        
    def update_position(self, entity, n=1):
        return self.pos[0], self.pos[1]


class DecorationPositionHandler:
    def __init__(self, pos, _3d_effect_layer, screen_offset):
        self._3d_effect_layer = _3d_effect_layer
        if self._3d_effect_layer == 0:
            self._3d_effect_layer = 1
        elif self._3d_effect_layer < 0:
            self._3d_effect_layer = -1 / self._3d_effect_layer
        self.screen_offset = screen_offset
        self.base_pos = tuple(pos)

    def update_position(self, entity, n=1):
        return (self.base_pos[0] + self.screen_offset[0] * self._3d_effect_layer,
                self.base_pos[1] + self.screen_offset[1] * self._3d_effect_layer)


class DynamicStructurePositionHandler:
    def __init__(self, body, correct_angle=True):
        self.correct_angle = correct_angle
        self.body = body
        self.relative_angle = 0

        self._correct_angle = correct_angle

    def get_anchor_y(self, constrained=False):
        if constrained:
            self.correct_angle = False
        else:
            self.correct_angle = self._correct_angle

        if self.correct_angle:
            return self.body.center_of_gravity.y
        else:
            return 0

    def update_position(self, struct, n=1):

        if struct.constrained:
            self.body.velocity = self.body.velocity / 1.002

        if self.correct_angle:
            while self.body.angle > pi / 4:
                self.body.angle -= pi / 2
                self.relative_angle -= pi / 2
            while self.body.angle < -pi / 4:
                self.body.angle += pi / 2
                self.relative_angle += pi / 2
        struct.rotation = -(self.body.angle - self.relative_angle) / pi * 180
        if self.correct_angle:
            return self.body.local_to_world(self.body.center_of_gravity)
        else:
            return tuple(self.body.position)


class RopePositionHandler:
    def __init__(self, constraint):
        self.constraint = constraint

    def update_position(self, rope, n=1):
        pos1 = self.constraint.a.local_to_world(self.constraint.anchor_a)
        pos2 = self.constraint.b.local_to_world(self.constraint.anchor_b)

        dx, dy = pos2 - pos1
        angle = math.atan(abs(dx) / abs(dy))
        if dy < 0:
            angle += pi - 2 * angle
        if dx < 0:
            angle *= -1

        rope.rotation = (angle - pi / 2) / pi * 180
        return pos1


class BgLayerPositionHandler:
    def __init__(self, pos, screen_offset, end_trajectory_callback=None, _3d_effect_layer=None):
        self.sdr = screen_offset
        self.pos = list(pos)
        self.base_pos = tuple(pos)
        self._3d_effect_layer = _3d_effect_layer

    def get_layer(self, entity):
        if self._3d_effect_layer is None:
            return entity.get_layer()
        return self._3d_effect_layer

    def update_position(self, entity, n=1):
        i = abs(self.get_layer(entity))

        if i == 0:
            i = 1

        return self.base_pos[0] + self.sdr[0] / i * 2, self.base_pos[1] + self.sdr[1] / i * 2
                

class EntityPositionHandler:
    def __init__(self, body, entity_data):
        self.body = body
        self.pos = [0, 0]

        self.entity_data = entity_data

        self.running_max_speed = self.entity_data.running_max_velocity
        self.walking_max_speed = self.entity_data.walking_max_velocity
        self.jump_y_impulse = self.entity_data.jump_y_impulse
        self.air_control_max_speed = self.entity_data.air_control_max_velocity
        self.acceleration = self.entity_data.acceleration
        self.air_control_acceleration = self.entity_data.air_control_acceleration

        self.running_states = {'run', 'slowly_run'}
        self.walking_states = {'walk', 'slowly_walk'}

        self.jumped = False
        self.jump_counter_deactivation_states = {'fall', 'land', 'walk', 'idle', 'run'}

        self.mapping = dict(
            walk=50,
            run=130,
            slowly_walk=50,
            slowly_run=130,
        )

    def update_position(self, entity, n=1):
        if not entity.dead and not entity.sleeping:
            if entity.state in self.jump_counter_deactivation_states:
                self.jumped = False

            current_x_velocity = round(self.body.velocity.x)
            impulse = [0., 0.]

            if entity.state == 'jump' and entity.is_on_ground and not self.jumped:
                self.jumped = True
                impulse[1] = self.jump_y_impulse

            if entity.collide_with_dynamic_ground is not None:
                body = entity.collide_with_dynamic_ground
                ground_vx = body.velocity_at_world_point(self.body.position).x * entity.direction
            else:
                ground_vx = 0

            if entity.state in self.running_states or entity.secondary_state in self.running_states:
                if abs(current_x_velocity) <= self.running_max_speed + ground_vx and entity.is_on_ground:
                    abs_x_impulse = min(self.acceleration, self.running_max_speed - abs(current_x_velocity) + ground_vx)
                    impulse[0] = abs_x_impulse * entity.direction

            elif entity.state in self.walking_states or entity.secondary_state in self.walking_states:
                if abs(current_x_velocity) <= self.walking_max_speed + ground_vx and entity.is_on_ground:
                    abs_x_impulse = min(self.acceleration, self.walking_max_speed - abs(current_x_velocity) + ground_vx)
                    impulse[0] = abs_x_impulse * entity.direction

            elif entity.state == 'dash' and entity.can_dash_velocity_be_applied:
                self.body.velocity = Vec2d(2500 * entity.direction, 0)

            elif entity.air_control and entity.can_air_control and not entity.is_on_ground:
                if abs(current_x_velocity) <= self.air_control_max_speed - 1:
                    abs_x_impulse = min(self.air_control_acceleration,
                                        self.air_control_max_speed - abs(current_x_velocity))
                    impulse[0] = abs_x_impulse * entity.air_control
                elif ((entity.direction == -1 and self.body.velocity.x > 0) or
                        (entity.direction == 1 and self.body.velocity.x < 0)):
                    impulse[0] = self.air_control_acceleration * entity.direction
                entity.air_control = 0

            vector = Vec2d(*impulse)

            if entity.collide_with_dynamic_ground is not None and entity.state != 'dash':
                body = entity.collide_with_dynamic_ground

                if vector.y == 0:
                    vector = vector.rotated(body.angle)

                vx = vector.x * self.body.mass / body.mass
                vy = vector.y * self.body.mass / body.mass
                body.velocity = body.velocity + (-vx, -vy)

            self.body.velocity = self.body.velocity + vector
            self.pos = self.body.position
            return self.body.position.x, self.body.position.y
        return self.pos

    def end_of_dash(self, state, entity):
        if state == 'running':
            self.body.velocity = Vec2d((self.running_max_speed + self.acceleration) * entity.direction, 0)
        elif state == 'walking':
            self.body.velocity = Vec2d((self.walking_max_speed + self.acceleration) * entity.direction, 0)
        else:
            self.body.velocity = Vec2d(0, 0)


class PlayerPositionHandler(EntityPositionHandler):
    def __init__(self, body, triggers, entity_data):
        self.triggers = triggers
        self.do_update_triggers = False
        super().__init__(body, entity_data)

    def update_position(self, entity, n=1):
        if not entity.dead:
            x, y = super().update_position(entity, n)
            if self.do_update_triggers:
                self.update_triggers()
            return x, y
        return self.pos

    def update_triggers(self):
        self.triggers.update(self.body.position.x, self.body.position.y)


