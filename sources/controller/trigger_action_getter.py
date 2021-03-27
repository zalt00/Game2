# -*- coding:Utf-8 -*-

from dataclasses import dataclass
from typing import Any
from utils.logger import logger
from viewer.transition import Transition


@dataclass
class AbstractAction:
    ag: Any

    def __call__(self, *_, **__):
        raise NotImplementedError


class ActionGetter:
    def __call__(self, type_, **kwargs):
        return getattr(self, type_)(ag=self, **kwargs)


class GameActionGetter(ActionGetter):
    def __init__(self, triggers, window, camera_handler, entities, model, current_save_id, load_map_callback):
        self.triggers = triggers
        self.window = window
        self.camera_handler = camera_handler
        self.model = model
        self.entities = entities
        self.current_save_id = current_save_id
        self.load_map = load_map_callback

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
    class RelativeMovecam(AbstractAction):
        dx: int
        dy: int
        total_duration: int
        fade_in: int
        fade_out: int

        def __call__(self):
            self.ag.camera_handler.add_trajectory((self.dx, self.dy), self.total_duration, self.fade_in, self.fade_out,
                                                  relative=True)

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
        moving_threshold: int = -1
        left_limit: int = 2_147_483_641
        right_limit: int = -2_147_483_641
        max_speed: int = 2_147_483_641

        def __call__(self):
            if self.follow_sensitivity != -1:
                self.ag.camera_handler.follow_sensitivity = self.follow_sensitivity
            if self.moving_threshold != -1:
                self.ag.camera_handler.moving_threshold = self.moving_threshold
            if self.left_limit != 2_147_483_641:
                self.ag.camera_handler.left_limit = self.left_limit
            if self.max_speed != 2_147_483_641:
                self.ag.camera_handler.max_speed = self.max_speed
            if self.right_limit != -2_147_483_641:
                self.ag.camera_handler.right_limit = self.right_limit

    @dataclass
    class SetCameraPosition(AbstractAction):
        x: int
        y: int

        def __call__(self):
            self.ag.camera_handler.move_to(self.x, self.y)

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
    class ActionOnEntity(AbstractAction):
        entity_name: str
        action_name: str
        arg: list

        def __call__(self):
            try:
                entity = self.ag.entities[self.entity_name]
            except KeyError:
                pass
            else:
                action = getattr(entity, self.action_name, None)
                if action is not None:
                    action(*self.arg)

    @dataclass
    class TPEntity(AbstractAction):
        entity_name: str
        npos: list

        def __call__(self):
            try:
                entity = self.ag.entities[self.entity_name]
            except KeyError:
                logger.warning(f'invalid entity name: {self.entity_name}')
            else:
                entity.position_handler.body.position = self.npos
                entity.position_handler.body.velocity = (0, 0)
                self.ag.model.Game.BasePlayerData.pos_x.set(self.npos[0], self.ag.current_save_id)
                self.ag.model.Game.BasePlayerData.pos_y.set(self.npos[1], self.ag.current_save_id)

    @dataclass
    class SetCheckpoint(AbstractAction):
        checkpoint_id: int

        def __call__(self):
            self.ag.model.Game.last_checkpoint.set(self.checkpoint_id, self.ag.current_save_id)
            current_map = self.ag.model.Game.current_map_id.get(self.ag.current_save_id)
            self.ag.model.Game.last_checkpoints_map.set(current_map, self.ag.current_save_id)

    @dataclass
    class LoadMap(AbstractAction):
        map_id: int

        def __call__(self):
            self.ag.load_map(self.map_id)

    @dataclass
    class CreateTransition(AbstractAction):
        fade: str
        color: list
        duration: int
        stop_after_end: bool = True
        trigger_to_enable: int = -1
        priority: int = 0

        def __call__(self):
            if self.trigger_to_enable >= 0:
                callback = GameActionGetter.EnableTrigger(self.ag, self.trigger_to_enable)
            else:
                def callback(*_, **__):
                    pass

            transition = Transition(self.duration, tuple(self.color), (1280, 800),
                                    callback, self.fade, self.stop_after_end, priority=self.priority)
            self.ag.window.add_transition(transition)


