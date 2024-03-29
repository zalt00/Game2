# -*- coding:Utf-8 -*-


from queue import Queue
from .trajectory import FadeInFadeOutTrajectory


class CameraHandler:
    def __init__(self, pos):
        self.pos = list(pos)  # position is ambiguous, it is actually the offset to apply to the sprites
        # that means that when the camera travels to the right, the x position of the camera actually decreases
        # TODO rename and add a position property which indicates the real position of the camera

        self.base_pos = tuple(pos)

        self.trajectory = None
        self.trajectory_duration = 0
        self.advance = 0
        self.end_trajectory = None
        self.trajectory_queue = Queue()
        self.is_current_trajectory_relative = False

        self.player = None

        self.relative_pos = [0, 0]  # relative to player
        self.locked = [False, False]
        self.lock_mode = ''
        self.possible_modes = {'follow', 'strict'}

        self.follow_sensitivity = 15  # speed of the camera in follow mode
        self.moving_threshold = 2  # minimal offset between the target and the current position to move the camera
        self.left_limit = 2_147_483_640
        self.right_limit = -2_147_483_640

        self.top_limit = -2_147_483_640
        self.bottom_limit = 2_147_483_640

        self.max_speed = 2_147_483_640

    def init_player(self, player):
        self.player = player

    def add_trajectory(self, target, total_duration, fade_in, fade_out, relative=False):
        target = list(target)
        if target[0] == 2_147_483_640:
            target[0] = self.pos[0]
        if target[1] == 2_147_483_640:
            target[1] = self.pos[1]

        if self.trajectory is None:
            if relative:
                self.trajectory = FadeInFadeOutTrajectory(
                    tuple(self.relative_pos), target, total_duration, fade_in, fade_out)
            else:
                npos = target[0] + self.base_pos[0], target[1] + self.base_pos[1]
                self.trajectory = FadeInFadeOutTrajectory(tuple(self.pos), npos, total_duration, fade_in, fade_out)
            self.trajectory_duration = total_duration
            self.advance = 0
            self.is_current_trajectory_relative = relative
        else:
            self.trajectory_queue.put([target, total_duration, fade_in, fade_out, relative])

    def cancel_trajectory(self):
        self.trajectory = None
        self.trajectory_queue = Queue()

    def move_to(self, x, y):
        self.pos[:] = x, y

    @property
    def x(self):
        return self.pos[0]

    @x.setter
    def x(self, value):
        self.pos[0] = value

    @property
    def y(self):
        return self.pos[1]

    @y.setter
    def y(self, value):
        self.pos[1] = value

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

    def recenter_camera(self, player_position):
        self.pos[:] = self.get_position_target(player_position)
        return self.pos

    def get_position_target(self, player_position):
        pos = list(self.pos)

        if self.locked[0]:
            pos[0] = self.relative_pos[0] - player_position[0]
            if pos[0] > self.left_limit:
                pos[0] = self.left_limit
            elif pos[0] < self.right_limit:
                pos[0] = self.right_limit

        if self.locked[1]:
            pos[1] = self.relative_pos[1] - player_position[1]
            if pos[1] > self.bottom_limit:
                pos[1] = self.bottom_limit
            elif pos[1] < self.top_limit:
                pos[1] = self.top_limit

        return pos

    def update_camera_position(self, n):
        if self.trajectory is not None:
            end = False

            self.advance += n
            if self.advance > self.trajectory_duration:
                self.advance = self.trajectory_duration
                end = True

            npos = self.trajectory(self.advance)
            if self.is_current_trajectory_relative:
                self.relative_pos[0], self.relative_pos[1] = npos[0], npos[1]
            else:
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

            if not self.is_current_trajectory_relative:
                if self.locked[0]:
                    self.relative_pos[0] = self.pos[0] + self.player.position_handler.body.position.x
                if self.locked[1]:
                    self.relative_pos[1] = self.pos[1] + self.player.position_handler.body.position.y

        if self.trajectory is None or self.is_current_trajectory_relative:

            pos_target = self.get_position_target(self.player.position_handler.body.position)

            if self.locked[0]:
                if self.lock_mode == 'strict':
                    self.pos[0] = pos_target[0]

                elif self.lock_mode == 'follow':
                    dif = -self.pos[0] + pos_target[0]

                    dx = dif / self.follow_sensitivity
                    if abs(dif) > self.moving_threshold:
                        if abs(dx) > self.max_speed:
                            dx = (dx / abs(dx)) * self.max_speed
                        self.pos[0] += dx

            if self.locked[1]:
                if self.lock_mode == 'strict':
                    self.pos[1] = pos_target[1]
                elif self.lock_mode == 'follow':
                    dif = -self.pos[1] + pos_target[1]

                    dy = dif / self.follow_sensitivity
                    if abs(dif) > self.moving_threshold:
                        if abs(dy) > self.max_speed:
                            dy = (dy / abs(dy)) * self.max_speed
                        self.pos[1] += dy
        return self.pos


