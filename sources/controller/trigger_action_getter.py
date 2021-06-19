# -*- coding:Utf-8 -*-

from dataclasses import dataclass
from typing import Any, Union
from utils.logger import logger
from viewer.transition import Transition
from .trajectory import FadeInFadeOutTrajectory
from pymunk import Vec2d


@dataclass
class AbstractAction:
    ag: Any

    def __call__(self, *_, **__):
        raise NotImplementedError


class ActionGetter:
    def __call__(self, type_, **kwargs):
        return getattr(self, type_)(ag=self, **kwargs)


class GameActionGetter(ActionGetter):
    def __init__(self, triggers, window, camera_handler, entities, model, current_save_id, load_map_callback,
                 schedule_function_callback, kinematic_structures, init_recording_array_callback,
                 start_recording_for_inversion_callback, start_inversion_callback, stop_inversion_callback):
        self.triggers = triggers
        self.window = window
        self.camera_handler = camera_handler
        self.model = model

        self.entities = entities
        self.kinematic_structures = kinematic_structures

        self.current_save_id = current_save_id

        self.load_map = load_map_callback
        self.schedule_function = schedule_function_callback

        self.init_recording_array = init_recording_array_callback
        self.start_inversion = start_inversion_callback
        self.start_recording_for_inversion = start_recording_for_inversion_callback

        self.stop_inversion = stop_inversion_callback

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
                entity.call_action(self.action_name, self.arg)

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
        relative: bool = False

        def __call__(self):
            if self.relative:
                current_map_id = self.ag.model.Game.current_map_id.get(self.ag.current_save_id)
                new_map_id = current_map_id + self.map_id
                if new_map_id < 0:
                    new_map_id = 0
                elif new_map_id >= len(self.ag.model.Game.maps):
                    new_map_id = len(self.ag.model.Game.maps) - 1
            else:
                new_map_id = self.map_id
                
            self.ag.load_map(new_map_id)

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

    @dataclass
    class ScheduleTriggerEnabling(AbstractAction):
        ticks: int
        trigger_to_enable: int
        function_id: Union[int, None] = None

        def __call__(self):
            if self.function_id is not None:
                if self.function_id < 0:
                    self.function_id = None
            self.ag.schedule_function(GameActionGetter.EnableTrigger(self.ag, self.trigger_to_enable),
                                      ticks=self.ticks,
                                      function_id=self.function_id)

    @dataclass
    class MoveKinematicStructure(AbstractAction):
        x: int
        y: int
        total_duration: int
        fade_in: int
        fade_out: int
        struct_name: str

        def __call__(self):
            struct = self.ag.kinematic_structures[self.struct_name]

            trajectory = FadeInFadeOutTrajectory(tuple(struct.position_handler.pos),
                                                 (self.x, self.y), self.total_duration,
                                                 self.fade_in, self.fade_out)

            struct.position_handler.add_trajectory(trajectory)

    @dataclass
    class MoveKinematicStructure2(AbstractAction):
        x: int
        y: int
        velocity: int
        struct_name: str

        def __call__(self):
            struct = self.ag.kinematic_structures[self.struct_name]

            current_pos = tuple(struct.position_handler.pos)
            vector = Vec2d(self.x - current_pos[0], self.y - current_pos[1])
            total_duration = round(vector.length / self.velocity * 60)
            if total_duration < 2:
                total_duration = 2

            trajectory = FadeInFadeOutTrajectory(current_pos, (self.x, self.y), total_duration, 1, 1)

            struct.position_handler.add_trajectory(trajectory)

    @dataclass
    class StartRecordingForInversion(AbstractAction):
        def __call__(self):
            self.ag.init_recording_array()
            self.ag.start_recording_for_inversion()

    @dataclass
    class StartInversion(AbstractAction):
        def __call__(self):
            self.ag.start_inversion()

    @dataclass
    class StopInversion(AbstractAction):
        def __call__(self):
            print(0)
            self.ag.stop_inversion()

