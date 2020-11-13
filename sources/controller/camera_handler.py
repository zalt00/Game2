# -*- coding:Utf-8 -*-


from queue import Queue
from .trajectory import CameraMovementTrajectory


class CameraHandler:
    def __init__(self, pos):
        self.pos = list(pos)
        self.base_pos = tuple(pos)
        self.trajectory = None
        self.trajectory_duration = 0
        self.advance = 0
        self.end_trajectory = None
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
        return self.pos


