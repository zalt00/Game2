# -*- coding:Utf-8 -*-

from dataclasses import dataclass
from typing import Any, Union
from utils.logger import logger
from viewer.transition import Transition
from .trajectory import FadeInFadeOutTrajectory
from pymunk import Vec2d
import weakref


@dataclass
class AbstractAction:
    ag: Any

    def __call__(self, *_, **__):
        raise NotImplementedError


class ActionGetter:
    def __call__(self, type_, **kwargs):
        return getattr(self, type_)(ag=self, **kwargs)


class GameActionGetter(ActionGetter):

    def __init__(self, game_app):
        self._game_app_ref = weakref.ref(game_app)

    @property
    def game_app(self):
        return self._game_app_ref()

    @dataclass
    class AbsoluteMovecam(AbstractAction):
        x: int
        y: int
        total_duration: int
        fade_in: int
        fade_out: int

        def __call__(self):
            self.ag.game_app.camera_handler.add_trajectory((self.x, self.y), self.total_duration, self.fade_in,
                                                           self.fade_out)

    @dataclass
    class RelativeMovecam(AbstractAction):
        dx: int
        dy: int
        total_duration: int
        fade_in: int
        fade_out: int

        def __call__(self):
            self.ag.game_app.camera_handler.add_trajectory((self.dx, self.dy), self.total_duration, self.fade_in,
                                                           self.fade_out, relative=True)

    @dataclass
    class LockCamera(AbstractAction):
        x: bool
        y: bool
        mode: str

        def __call__(self):
            self.ag.game_app.camera_handler.lock_camera(self.x, self.y, self.mode)

    @dataclass
    class CameraSettings(AbstractAction):
        follow_sensitivity: int = -1
        moving_threshold: int = -1
        left_limit: int = 2_147_483_641
        right_limit: int = -2_147_483_641
        top_limit: int = -2_147_483_641
        bottom_limit: int = 2_147_483_641
        max_speed: int = 2_147_483_641

        def __call__(self):
            if self.follow_sensitivity != -1:
                self.ag.game_app.camera_handler.follow_sensitivity = self.follow_sensitivity
            if self.moving_threshold != -1:
                self.ag.game_app.camera_handler.moving_threshold = self.moving_threshold
            if self.left_limit != 2_147_483_641:
                self.ag.game_app.camera_handler.left_limit = self.left_limit
            if self.max_speed != 2_147_483_641:
                self.ag.game_app.camera_handler.max_speed = self.max_speed
            if self.right_limit != -2_147_483_641:
                self.ag.game_app.camera_handler.right_limit = self.right_limit

            if self.top_limit != -2_147_483_641:
                self.ag.game_app.camera_handler.top_limit = self.top_limit
            if self.bottom_limit != 2_147_483_641:
                self.ag.game_app.camera_handler.bottom_limit = self.bottom_limit

    @dataclass
    class SetCameraPosition(AbstractAction):
        x: int
        y: int

        def __call__(self):
            self.ag.game_app.camera_handler.move_to(self.x, self.y)

    @dataclass
    class EnableTrigger(AbstractAction):
        target: int

        def __call__(self):
            try:
                self.ag.game_app.triggers[self.target].enabled = True
            except IndexError:
                pass
    
    @dataclass
    class DisableTrigger(AbstractAction):
        target: int

        def __call__(self):
            try:
                self.ag.game_app.triggers[self.target].enabled = False
            except IndexError:
                pass

    @dataclass
    class ActionOnEntity(AbstractAction):
        entity_name: str
        action_name: str
        arg: list

        def __call__(self):
            try:
                entity = self.ag.game_app.entities[self.entity_name]
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
                entity = self.ag.game_app.entities[self.entity_name]
            except KeyError:
                logger.warning(f'invalid entity name: {self.entity_name}')
            else:
                entity.position_handler.body.position = self.npos
                entity.position_handler.body.velocity = (0, 0)
                self.ag.game_app.model.Game.BasePlayerData.pos_x.set(self.npos[0], self.ag.game_app.current_save_id)
                self.ag.game_app.model.Game.BasePlayerData.pos_y.set(self.npos[1], self.ag.game_app.current_save_id)

    @dataclass
    class SetCheckpoint(AbstractAction):
        checkpoint_id: int

        def __call__(self):
            self.ag.game_app.model.Game.last_checkpoint.set(self.checkpoint_id, self.ag.game_app.current_save_id)
            current_map = self.ag.game_app.model.Game.current_map_id.get(self.ag.game_app.current_save_id)
            self.ag.game_app.model.Game.last_checkpoints_map.set(current_map, self.ag.game_app.current_save_id)

    @dataclass
    class LoadMap(AbstractAction):
        map_id: int
        relative: bool = False
        tp_to_checkpoint: int = -42

        def __call__(self):
            if self.relative:
                current_map_id = self.ag.game_app.model.Game.current_map_id.get(self.ag.game_app.current_save_id)
                new_map_id = current_map_id + self.map_id
                if new_map_id < 0:
                    new_map_id = 0
                elif new_map_id >= len(self.ag.game_app.model.Game.maps):
                    new_map_id = len(self.ag.game_app.model.Game.maps) - 1
            else:
                new_map_id = self.map_id

            if self.tp_to_checkpoint != -42:
                self.ag.game_app.load_map_on_next_frame(new_map_id, self.tp_to_checkpoint)
            else:
                self.ag.game_app.load_map_on_next_frame(new_map_id)

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
            self.ag.game_app.window.add_transition(transition)

    @dataclass
    class ScheduleTriggerEnabling(AbstractAction):
        ticks: int
        trigger_to_enable: int
        function_id: Union[int, None] = None

        def __call__(self):
            if self.function_id is not None:
                if self.function_id < 0:
                    self.function_id = None
            self.ag.game_app.schedule_function(GameActionGetter.EnableTrigger(self.ag, self.trigger_to_enable),
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
            struct = self.ag.game_app.kinematic_structures[self.struct_name]

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
            struct = self.ag.game_app.kinematic_structures[self.struct_name]

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
            self.ag.game_app.init_inversion_handler_recording_array()
            self.ag.game_app.start_recording_for_inversion()

    @dataclass
    class StartInversion(AbstractAction):
        def __call__(self):
            self.ag.game_app.start_inversion()

    @dataclass
    class StopInversion(AbstractAction):
        def __call__(self):
            self.ag.game_app.stop_inversion()

