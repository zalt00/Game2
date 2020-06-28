# -*- coding:Utf-8 -*-

from pymunk.vec2d import Vec2d
from .trajectory import CameraMovementTrajectory
from time import perf_counter
from queue import Queue


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
        self.trajectory_queue = Queue()

    def add_trajectory(self, target, total_duration, fade_in, fade_out):
        if self.trajectory is None:
            npos = target[0] + self.base_pos[0], target[1] + self.base_pos[1]
            self.trajectory = CameraMovementTrajectory(tuple(self.pos), npos, total_duration, fade_in, fade_out)
            self.trajectory_duration = total_duration
            self.advance = 0
        else:
            self.trajectory_queue.put([target, total_duration, fade_in, fade_out])

    def cancel_trajectory(self):
        self.trajectory = None
        self.trajectory_queue = Queue()

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
                if self.trajectory_queue.empty():
                    self.trajectory = None
                else:
                    self.add_trajectory(*self.trajectory_queue.get())

        self.sdr[0] = self.pos[0] - self.base_pos[0]
        self.sdr[1] = self.pos[1] - self.base_pos[1]
        
        n_layers = len(entity.image_handler.res.layers)
        i = abs(entity.get_layer()) ** 2

        if i == 0:
            i = 1
        return self.base_pos[0] + self.sdr[0] / i + entity.dec[0], -self.base_pos[1] - self.sdr[1] / i + entity.dec[1]
                

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
        return self.body.position.x + entity.dec[0] + entity.screen_dec[0], -self.body.position.y + entity.dec[1] + entity.screen_dec[1]
    

class PlayerPositionHandler(EntityPositionHandler):
    def __init__(self, body, triggers):
        self.triggers = triggers
        super().__init__(body)

    def update_position(self, entity, n=1):
        x, y = super().update_position(entity, n)
        self.update_triggers()
        return x, y

    def update_triggers(self):
        for trigger in self.triggers:
            trigger.update(self.body.position.x, self.body.position.y)

