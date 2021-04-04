# -*- coding:Utf-8 -*-

from pymunk.vec2d import Vec2d
from .trajectory import FadeInFadeOutTrajectory
from time import perf_counter
from queue import Queue
import numpy as np
from utils.logger import logger
from math import pi
import math


class StaticPositionHandler:
    def __init__(self, pos):
        self.pos = pos
        
    def update_position(self, entity, n=1):
        return self.pos[0], self.pos[1]


class KinematicStructurePositionHandler:

    def __init__(self, pos, body=None):
        self.pos = pos
        self.current_trajectory = None
        self.t = 0

        self.body = body

    def update_position(self, entity, n=1):
        if self.current_trajectory is not None:
            if not self.current_trajectory.trajectory_ended:
                self.pos[:] = self.current_trajectory(self.t)

                if self.body is not None:
                    x, y = self.pos
                    bx, by = self.body.position
                    if abs(bx - x) > 5:
                        logger.warning(f'x desinc on kinematic structure of type {type(entity).__name__}')
                        bx = x
                        self.body.position = x, by
                    if abs(by - y) > 5:
                        logger.warning(f'y desinc on kinematic structure of type {type(entity).__name__}')
                        self.body.position = bx, y

                    if self.t != self.current_trajectory.duration:
                        npos = self.current_trajectory(self.t + 1)
                        vx = (npos[0] - self.pos[0]) * 60
                        vy = (npos[1] - self.pos[1]) * 60
                        self.body.velocity = vx, vy

                self.t += 1
            else:
                if self.body is not None:
                    self.body.velocity = (0, 0)
                self.current_trajectory = None
                self.t = 1

        return self.pos[0], self.pos[1]

    def add_trajectory(self, trajectory):
        self.t = 1
        self.current_trajectory = trajectory
        self.body.position = self.pos


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
            self.body.velocity = self.body.velocity / 1.001

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

        self.entity_base_width = -1

        self._unsure_width = True

    def get_layer(self, entity):
        if self._3d_effect_layer is None:
            return entity.get_layer()
        return self._3d_effect_layer

    def update_position(self, entity, n=1):
        i = abs(self.get_layer(entity))

        if i == 0:
            i = 1

        if entity.is_parallax():
            if self.entity_base_width == -1 or self._unsure_width:
                if self.entity_base_width != -1:
                    self._unsure_width = False
                self.entity_base_width = entity.get_base_width()

            d = self.sdr[0] / i * 2
            while -d > self.entity_base_width:
                d += self.entity_base_width

            x = self.base_pos[0] + d
        else:
            x = self.base_pos[0] + (self.sdr[0] / i * 2)
        y = self.base_pos[1] + self.sdr[1] / i * 2

        return x, y
                

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
        self.dash_speed = self.entity_data.dash_speed
        self.dash_length = self.entity_data.dash_length

        self.dash_ticks_counter = 0

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

            if entity.is_on_ground:
                if entity.state in self.running_states or entity.secondary_state in self.running_states:
                    max_speed = self.running_max_speed + ground_vx

                    if (entity.direction == 1 and current_x_velocity <= max_speed) or (
                            entity.direction == -1 and -current_x_velocity <= max_speed):
                        abs_x_impulse = min(self.acceleration, abs(max_speed * entity.direction - current_x_velocity))
                        impulse[0] = abs_x_impulse * entity.direction

                elif entity.state in self.walking_states or entity.secondary_state in self.walking_states:
                    max_speed = self.walking_max_speed + ground_vx

                    if (entity.direction == 1 and current_x_velocity <= max_speed) or (
                            entity.direction == -1 and -current_x_velocity <= max_speed):
                        abs_x_impulse = min(self.acceleration, abs(max_speed * entity.direction - current_x_velocity))
                        impulse[0] = abs_x_impulse * entity.direction

            if entity.state == 'dash':
                if self.dash_ticks_counter < self.dash_length:
                    if entity.can_dash_velocity_be_applied:
                        self.body.velocity = Vec2d(self.dash_speed * entity.direction, 0)

                    self.dash_ticks_counter += 1
                    if self.dash_ticks_counter == self.dash_length:
                        self.end_of_dash(entity)

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

            if entity.state != 'dash':
                self.dash_ticks_counter = 0

            self.body.velocity = self.body.velocity + vector
            self.pos = self.body.position
            return self.body.position.x, self.body.position.y
        return self.pos

    def end_of_dash(self, entity):
        if entity.secondary_state == 'run':
            self.body.velocity = Vec2d((self.running_max_speed + self.acceleration) * entity.direction, 0)
        elif entity.secondary_state == 'walk':
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


