# -*- coding:Utf-8 -*-


from queue import Queue
from .trajectory import CameraMovementTrajectory


class CameraHandler:
    def __init__(self, pos, player):
        self.pos = list(pos)
        self.base_pos = tuple(pos)
        self.trajectory = None
        self.trajectory_duration = 0
        self.advance = 0
        self.end_trajectory = None
        self.trajectory_queue = Queue()
        self.player = player
        self.relative_pos = [0, 0]
        self.locked = [False, False]
        self.lock_mode = ''
        self.possible_modes = {'follow', 'strict'}
        self.follow_sensitivity = 15
        self.moving_threshold = 2

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

    def move_to(self, x, y):
        self.pos[:] = x, y

    def lock_camera(self, x_bool, y_bool, mode):
        if x_bool:
            self.relative_pos[0] = self.pos[0] + self.player.position_handler.body.position.x
        if y_bool:
            self.relative_pos[1] = self.pos[1] + self.player.position_handler.body.position.y
        self.locked[:] = x_bool, y_bool
        if mode in self.possible_modes:
            self.lock_mode = mode
        else:
            self.lock_mode = 'strict'

    def update_camera_position(self, n):
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

            if self.locked[0]:
                self.relative_pos[0] = self.pos[0] + self.player.position_handler.body.position.x
            if self.locked[1]:
                self.relative_pos[1] = self.pos[1] + self.player.position_handler.body.position.y
        else:
            if self.locked[0]:
                if self.lock_mode == 'strict':
                    self.pos[0] = self.relative_pos[0] - self.player.position_handler.body.position.x
                elif self.lock_mode == 'follow':
                    dif = self.relative_pos[0] - self.player.position_handler.body.position.x - self.pos[0]
                    if abs(dif) > self.moving_threshold:
                        self.pos[0] += dif / self.follow_sensitivity
            if self.locked[1]:
                if self.lock_mode == 'strict':
                    self.pos[1] = self.relative_pos[1] - self.player.position_handler.body.position.y
                elif self.lock_mode == 'follow':
                    dif = self.relative_pos[1] - self.player.position_handler.body.position.y - self.pos[1]
                    if abs(dif) > self.moving_threshold:
                        self.pos[1] += dif / self.follow_sensitivity
        return self.pos


