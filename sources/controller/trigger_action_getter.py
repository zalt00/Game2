# -*- coding:Utf-8 -*-

from dataclasses import dataclass
from typing import Any


@dataclass
class AbstractAction:
    ag: Any
    def __call__(self, *_, **__):
        raise NotImplementedError


class ActionGetter:
    def __call__(self, type_, **kwargs):
        return getattr(self, type_)(ag=self, **kwargs)


class GameActionGetter(ActionGetter):
    def __init__(self, triggers, window, camera_handler, entities):
        self.triggers = triggers
        self.window = window
        self.camera_handler = camera_handler
        self.entities = entities

    @dataclass
    class AbsoluteMovecam(AbstractAction):
        x: int
        y: int
        total_duration: int
        fade_in: int
        fade_out: int

        def __call__(self):
            self.ag.camera_handler.add_trajectory((self.x, self.y), self.total_duration, self.fade_in, self.fade_out)

    @dataclass
    class LockCamera(AbstractAction):
        x: bool
        y: bool
        mode: str

        def __call__(self):
            self.ag.camera_handler.lock_camera(self.x, self.y, self.mode)

    @dataclass
    class CameraSettings(AbstractAction):
        follow_sensitivity: int = -1

        def __call__(self):
            if self.follow_sensitivity != -1:
                self.ag.camera_handler.follow_sensitivity = self.follow_sensitivity

    @dataclass
    class EnableTrigger(AbstractAction):
        target: int

        def __call__(self):
            try:
                self.ag.triggers[self.target].enabled = True
            except IndexError:
                pass
    
    @dataclass
    class DisableTrigger(AbstractAction):
        target: int

        def __call__(self):
            try:
                self.ag.triggers[self.target].enabled = False
            except IndexError:
                pass
    
    @dataclass
    class TPEntity(AbstractAction):
        entity_name: str
        npos: int

        def __call__(self):
            try:
                entity = self.ag.entities[self.entity_name]
            except KeyError:
                pass
            else:
                entity.position_handler.body.position = self.npos
                entity.position_handler.body.velocity = (0, 0)
        

