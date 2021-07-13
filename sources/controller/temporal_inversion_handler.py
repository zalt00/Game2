# -*- coding:Utf-8 -*-


import numpy as np
import math
from .position_handler import InvertedObjectPositionHandler, StaticPositionHandler
from .action_manager.sprite_action_manager import BaseEntityActionManager
from .physic_state_updater import InvertedEntityStateUpdater, InvertedGhostlyStructurePhysicStateUpdater
from .particles_handler import ParticleHandler
import dataclasses
import pymunk
from random import randint


class TemporalInversionHandler:

    @dataclasses.dataclass
    class PositionData:
        position: np.ndarray
        next_position: np.ndarray
        body_angle: float
        next_body_angle: float
        rotation: float

    @dataclasses.dataclass
    class EntityStateData:
        state: str
        direction: int

    def __init__(self, space, add_entity_callback, add_structure, page, **additional_data):
        self.objects = dict()
        self.array = None

        self.additional_data_for_entity_recordings = None

        self.kinematic_structures = dict()
        self.dynamic_structures = dict()
        self.entities = dict()
        self.constraints = dict()

        self.usual_position_handlers = dict()  # position handlers outside of the inversion
        self.inverted_object_position_handlers = dict()

        self.possible_states_for_each_entity = dict()

        self.usual_bodies = dict()
        self.inverted_object_bodies = dict()
        self.name_to_id = dict()
        self.entity_name_to_entity_id = dict()

        self.space = space

        self.add_ghost = add_entity_callback
        self.add_structure = add_structure
        self.page = page

        self.inversion_started = False

        self.t = 0

        self.inversion_effect_res = additional_data.get('inversion_effect', 'special_objects/inversion_effect.obj')

    def init_recording_array(self, kinematic_structures, dynamic_structures, entities, constraints):
        self.objects = dict()
        self.usual_position_handlers = dict()
        self.usual_bodies = dict()
        self.inverted_object_bodies = dict()
        self.inverted_object_position_handlers = dict()

        self.kinematic_structures = kinematic_structures.copy()
        self.dynamic_structures = dynamic_structures.copy()
        self.entities = entities.copy()
        self.constraints = constraints.copy()

        self.objects.update(kinematic_structures)
        self.objects.update(dynamic_structures)
        self.objects.update(entities)
        self.objects.update(constraints)

        self.name_to_id = dict()
        for i, obj_name in enumerate(self.objects):
            self.name_to_id[obj_name] = i

        self.possible_states_for_each_entity = dict()

        self.entity_name_to_entity_id = dict()
        for id_, (entity_name, entity) in enumerate(self.entities.items()):
            self.entity_name_to_entity_id[entity_name] = id_

            res = entity.image_handler.res
            states = dict()
            for i, state_name in enumerate(res.sheets):
                if not state_name.startswith('inverted_'):
                    states[i] = state_name
                    states[state_name] = i
            self.possible_states_for_each_entity[entity_name] = states

        shape = (len(self.entities), 32768, 2)
        self.additional_data_for_entity_recordings = np.zeros(shape, dtype=np.int8)

        shape = (len(self.objects), 32768, 4)
        self.array = np.zeros(shape, dtype=np.float64)
        self.t = 0

    def record(self):
        assert self.array is not None
        for i, obj in enumerate(self.objects.values()):
            position_handler = obj.position_handler
            if getattr(position_handler, 'body', None) is not None:
                position = position_handler.body.position
                angle = position_handler.body.angle
            else:
                position = position_handler.pos

                # if the object is a rope, stores the length in the angle attribute, as it is useless because there is
                # no body attached to the object
                if getattr(position_handler, 'is_rope_position_handler', False):
                    angle = position_handler.get_length(obj)
                else:
                    angle = -obj.rotation * math.pi / 180

            rotation = obj.rotation

            self.array[i, self.t, 0] = position[0]
            self.array[i, self.t, 1] = position[1]
            self.array[i, self.t, 2] = angle
            self.array[i, self.t, 3] = rotation

        for i, (obj_name, obj) in enumerate(self.entities.items()):
            state = obj.state
            direction = obj.direction
            state_id = self.possible_states_for_each_entity[obj_name][state]
            self.additional_data_for_entity_recordings[i, self.t, 0] = state_id
            self.additional_data_for_entity_recordings[i, self.t, 1] = int(direction)

        self.t += 1

        if self.t == 2**19:
            new_array = np.zeros(self.array.shape, dtype=np.float64)
            new_array[:, :2**18, :] = self.array[:, 2**18:2**19, :]

            self.array = new_array

            new_array2 = np.zeros(self.additional_data_for_entity_recordings.shape, dtype=np.int8)
            new_array2[:, :2**18, :] = self.additional_data_for_entity_recordings[:, 2**18:2**19, :]

            self.additional_data_for_entity_recordings = new_array2

            self.t = 2**18

        elif self.t == self.array.shape[1]:
            new_shape = list(self.array.shape)
            new_shape[1] *= 2

            new_array = np.zeros(new_shape, dtype=np.float64)
            new_array[:, :self.t, :] = self.array
            self.array = new_array

            new_shape2 = list(self.additional_data_for_entity_recordings.shape)
            new_shape2[1] *= 2

            new_array2 = np.zeros(new_shape2, dtype=np.int8)
            new_array2[:, :self.t, :] = self.additional_data_for_entity_recordings
            self.additional_data_for_entity_recordings = new_array2

    def setup_inversion(self):
        for obj_name, obj in self.kinematic_structures.items():
            self.setup_object(obj_name, obj)

        for obj_name, obj in self.dynamic_structures.items():
            self.setup_object(obj_name, obj)
            self.setup_ghostly_structure(obj_name, obj)

        for obj_name, obj in self.entities.items():
            self.setup_ghost(obj_name, obj)

        for obj_name, obj in self.constraints.items():
            self.setup_object(obj_name, obj)

    def setup_object(self, obj_name, obj):
        has_body = getattr(obj.position_handler, 'body', None) is not None

        if has_body:

            usual_body = obj.position_handler.body

            new_body = pymunk.body.Body(body_type=pymunk.body.Body.KINEMATIC)
            new_body.center_of_gravity = usual_body.center_of_gravity

            self.usual_bodies[obj_name] = usual_body
            self.inverted_object_bodies[obj_name] = new_body
        else:
            new_body = None

        get_position_callback = self.define_get_position_data_callback(self.name_to_id[obj_name])

        new_position_handler = InvertedObjectPositionHandler(new_body, get_position_callback, self.space)

        if getattr(obj.position_handler, 'correct_angle', False):
            new_position_handler.correct_position = True

        self.usual_position_handlers[obj_name] = obj.position_handler
        self.inverted_object_position_handlers[obj_name] = new_position_handler

    def setup_ghost(self, obj_name, obj):
        self._setup_ghost(obj_name, obj)

        for time_offset in (-10, 6, -5, -8, -6, 3, -15):
            self._setup_ghost(obj_name, obj, opacity=25, time_offset=time_offset)

    def _setup_ghost(self, obj_name, obj, opacity=120, time_offset=0):
        get_position_callback = self.define_get_position_data_callback(self.name_to_id[obj_name], time_offset)

        position_handler = InvertedObjectPositionHandler(None, get_position_callback, self.space, True)

        action_manager = BaseEntityActionManager()

        get_state_callback = self.define_get_state_data_callback(self.entity_name_to_entity_id[obj_name],
                                                                 obj_name, time_offset)
        state_updater = InvertedEntityStateUpdater(get_state_callback)

        ghost = self.add_ghost(self.page, -1, position_handler, obj.image_handler.res, state_updater,
                               ParticleHandler(lambda *_, **__: None), action_manager)
        action_manager.init_entity(ghost)
        ghost.base_opacity = opacity
        ghost.opacity = opacity
        self.page.ghosts.add(ghost)

    def setup_ghostly_structure(self, obj_name, obj):
        for time_offset in (-10, 6, -5, -8, -6, 3, -15):

            self._setup_ghostly_structure(obj_name, obj, 25, time_offset=time_offset)
            self._setup_ghostly_structure(obj_name, obj, 25, time_offset=time_offset - 60)

    def _setup_ghostly_structure(self, obj_name, obj, opacity=120, time_offset=0):
        get_position_callback = self.define_get_position_data_callback(self.name_to_id[obj_name], time_offset)

        position_handler = InvertedObjectPositionHandler(None, get_position_callback, self.space, True)

        action_manager = BaseEntityActionManager()

        state_updater = InvertedGhostlyStructurePhysicStateUpdater()

        ghost = self.add_ghost(self.page, -1, position_handler, obj.image_handler.res, state_updater,
                               ParticleHandler(lambda *_, **__: None), action_manager, default_state='base')

        ghost.color = (255, 255, 255)

        action_manager.init_entity(ghost)
        ghost.base_opacity = opacity
        ghost.opacity = opacity
        self.page.ghosts.add(ghost)

    def start_inversion(self):
        self.inversion_started = True

        for obj_name, body in self.inverted_object_bodies.items():
            previous_body = self.space.objects[obj_name][0]
            shape = self.space.objects[obj_name][1]
            self.space.objects[obj_name] = (body, shape)

            self.space.remove(previous_body)

            self.space.add(body)

            if isinstance(shape, list):
                self.space.remove(*shape)
                for s in shape:
                    s.body = body
                self.space.add(*shape)
            else:
                self.space.remove(shape)
                shape.body = body
                self.space.add(shape)

        for obj_name, position_handler in self.inverted_object_position_handlers.items():
            self.objects[obj_name].position_handler = position_handler

        # blue screen effect
        sprite = self.add_structure(self.page, 10, StaticPositionHandler((0, 0)), self.inversion_effect_res)
        sprite.opacity = 200
        sprite.affected_by_screen_offset = False
        self.page.special_inversion_effects.add(sprite)

    def stop_inversion(self):
        self.inversion_started = False

        for obj_name, body in self.usual_bodies.items():
            shape = self.space.objects[obj_name][1]

            previous_body = self.space.objects[obj_name][0]
            self.space.objects[obj_name] = (body, shape)

            self.space.remove(previous_body)
            self.space.add(body)

            if isinstance(shape, list):
                self.space.remove(*shape)
                for s in shape:
                    s.body = body
                self.space.add(*shape)

            else:
                self.space.remove(shape)
                shape.body = body
                self.space.add(shape)

        for obj_name, position_handler in self.usual_position_handlers.items():
            self.objects[obj_name].position_handler = position_handler

        self.page.special_inversion_effects.clear()

        self.t = 0

    def tick(self):
        if self.t != 0:
            self.t -= 1

    def define_get_position_data_callback(self, object_id, time_offset=0):
        assert self.array is not None

        def get_position_data():
            t = self.t + time_offset
            if t < 0:
                t = 0
            if t >= self.array.shape[1]:
                t = self.array.shape[1] - 1

            position = self.array[object_id, t, 0:2]
            body_angle = self.array[object_id, t, 2]
            rotation = self.array[object_id, t, 3]

            if t != 0:
                next_position = self.array[object_id, t - 1, 0:2]
                next_body_angle = self.array[object_id, t - 1, 2]
            else:
                next_position = position
                next_body_angle = body_angle

            position_data = self.PositionData(position, next_position, body_angle, next_body_angle, rotation)

            return position_data

        return get_position_data

    def define_get_state_data_callback(self, entity_id, entity_name, time_offset=0):
        assert self.array is not None

        def get_state_data():

            t = self.t + time_offset
            if t < 0:
                t = 0
            if t >= self.array.shape[1]:
                t = self.array.shape[1] - 1

            state_id = self.additional_data_for_entity_recordings[entity_id, t, 0]
            direction = self.additional_data_for_entity_recordings[entity_id, t, 1]
            state = self.possible_states_for_each_entity[entity_name][state_id]

            return self.EntityStateData('inverted_' + state, direction)

        return get_state_data






