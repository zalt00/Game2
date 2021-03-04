# -*- coding:Utf-8 -*-

from ..position_handler import StaticPositionHandler, \
    PlayerPositionHandler, BgLayerPositionHandler, DecorationPositionHandler, DynamicStructurePositionHandler, \
    RopePositionHandler
from ..action_manager import GameActionManager
from ..physic_state_updater import PhysicStateUpdater
from ..particles_handler import ParticleHandler
from ..text_getter import FormatTextGetter, SimpleTextGetter
from ..space import GameSpace
import pymunk.pyglet_util
from viewer.debug_draw import DrawOptions
from utils.save_modifier import SaveComponent
from ..triggers import Trigger
from ..trigger_action_getter import GameActionGetter
from time import perf_counter
import yaml
from viewer.transition import Transition
from ..camera_handler import CameraHandler
from utils.logger import logger
import os
from ..trigger_mapping import TriggerMapping


class Game:
    def __init__(self, window, model, return_to_main_menu, loading_finished_check, current_save_id, debug=False):

        self.window = window

        self.model = model
        self.state = 'idle'
        self.return_to_main_menu = return_to_main_menu
        self.loading_finished_check = loading_finished_check
        self.debug_draw = False

        self.level_cache = dict()

        self.dash_particles = []

        self.debug = debug

        self.current_save_id = current_save_id

        self.t1 = self.count = self.number_of_space_updates = self.space = \
            self.player = self.entities = self.structures = self.triggers = self.ag = self.action_manager = None
        self.checkpoints = None
        self.camera_handler = None
        self.is_player_dead = False
        self.is_camera_handler_activated = True
        self.sprites_to_delete = []
        self.already_hidden = []
        self.scheduled_func = set()

        self.player_lives = 3

        self.additional_commands = []

        self.current_map_id = -1

        self.draw_options = None

        self.viewer_page = None

        self.player_debug_values = None

        self._paused = False
        self.debug_draw_activated = False

        self.hearts = []

        SaveComponent.load()
        self.level = self.load_map_file(self.model.Game.current_map_id.get(self.current_save_id))

        self.level_res = self.level['background_data']['res']

        self.window.reset_event_manager()

    def show_player_debug_values(self, hide=False):
        if self.player_debug_values is not None and hide:
            self.viewer_page.texts.remove(self.player_debug_values)
            self.player_debug_values.delete()
            self.player_debug_values = None
        elif not hide:
            self.player_debug_values = self.init_text(self.model.Game.PlayerDebugData)

    @property
    def paused(self):
        return self._paused

    @paused.setter
    def paused(self, v):
        self._paused = bool(v)
        self.window.paused = self.paused

    def load_resources(self):
        self.window.update = self.loading_update
        if 'resources' in self.level:
            logger.debug('pre-loading resources')
            for res_name in self.level['resources']:
                self.window.resource_loader.load(res_name)

    def start_game(self):

        self.current_map_id = self.model.Game.current_map_id.get(self.current_save_id)

        self.is_player_dead = False
        self.is_camera_handler_activated = True
        self.dash_particles = []
        self.sprites_to_delete = []
        self.already_hidden = []
        self.scheduled_func = set()

        try:
            self.window.game_page.remove_child('Game')
        except KeyError:
            pass

        self.viewer_page = self.window.new_page('Game')
        self.viewer_page.add_group('entities')
        self.viewer_page.add_group('bg_layers')
        self.viewer_page.add_group('structures')
        self.viewer_page.add_group('dash_particles')
        self.viewer_page.add_group('texts')
        self.viewer_page.add_group('hearts')
        self.hearts = []

        self.window.game_page.add_child(self.viewer_page)
        self.window.set_page(self.window.game_page)

        # self.window.res_loader.cache.clear()
        return_to_main_menu = self.return_to_main_menu

        if self.debug_draw:
            self.draw_options = DrawOptions(self.window)
        else:
            self.draw_options = None

        self.space = GameSpace()

        ### BG ###
        dynamic = True
        n_layers = self.window.get_number_of_layers(self.level_res)
        pos = self.level['background_data']['pos']
        position_handler = BgLayerPositionHandler(pos, self.window.screen_offset)
        pos_hdlrs = [position_handler for _ in range(n_layers)]

        bg_layers = self.window.add_bg(
            self.viewer_page,
            pos_hdlrs,
            self.level_res
        )
        self.viewer_page.bg_layers.update(bg_layers)

        if 'bg_decoration_object_set_res' in self.level['background_data']:
            deco_res = self.window.resource_loader.load(self.level['background_data']['bg_decoration_object_set_res'])
            layer_res = deco_res.build_bg_decoration_layer(
                self.level['background_data']['bg_decoration_sequence'],
                self.level['background_data']['bg_decoration_layer_id']
            )
            pos_hdlr = BgLayerPositionHandler(
                self.level['background_data']['bg_decoration_objects_pos'],
                self.window.screen_offset
            )
            pos_hdlrs.append(pos_hdlr)
            decoration_layer = self.window.add_bg_layer(
                self.viewer_page, self.level['background_data']['bg_decoration_layer_id'], pos_hdlr, layer_res)
            self.viewer_page.bg_layers.add(decoration_layer)

        ######

        self.entities = dict()
        self.structures = dict()

        ### CAMERA ###
        self.camera_handler = CameraHandler((0, 0), None)
        self.camera_handler.move_to(x=self.model.Game.BaseBGData.camera_pos_x.get(self.current_save_id),
                                    y=self.model.Game.BaseBGData.camera_pos_y.get(self.current_save_id))

        ### TRIGGERS ###
        self.triggers = TriggerMapping(100)
        self.ag = GameActionGetter(self.triggers, self.window, self.camera_handler, self.entities, self.model,
                                   self.current_save_id, self.load_map_on_next_frame)
        for trigdata in self.level['triggers_data'].values():
            self.triggers[trigdata['id']] = Trigger(trigdata, self.ag)

        #####

        action_manager = GameActionManager(
            None, return_to_main_menu, self.save_position, self.toggle_debug_draw, self.pause, self.tp_to_stable_ground,
            self.show_player_debug_values)
        self.action_manager = action_manager

        ### OBJECTS ###

        constraints = []
        for object_name, data in self.level['objects_data'].items():

            if data['type'] == 'player':
                self.init_player(data)
            elif data['type'] == 'structure':
                self.init_structure(data)
            elif data['type'] == 'text':
                self.init_text(data)
            elif data['type'] == 'constraint':
                constraints.append(data)

        for cons_data in constraints:
            self.init_constraint(cons_data)

        heart_resource = self.model.Game.get('heart_resource', None)
        if heart_resource is not None:
            for pos in self.model.Game.heart_positions:
                heart_position_handler = StaticPositionHandler(pos)
                sprite = self.window.add_simple_image(
                    self.viewer_page, 9, heart_position_handler, heart_resource, self.model.Game.full_heart_state)
                sprite.affected_by_screen_offset = False
                sprite.static = True
                sprite.position_changed = True
                self.viewer_page.hearts.add(sprite)
                self.hearts.append(sprite)

        #####


        ### EVENT MANAGER ###
        ctrls = {}
        for action in self.model.Options.Controls.actions:
            kb, controller = self.model.Options.Controls.get(action)
            action_id = getattr(GameActionManager, action.upper())

            ctrls[kb.get()] = action_id
            ctrls[controller.get_bytes()] = action_id

        if self.debug:
            self.window.set_event_manager('DebugGameEventManager', action_manager, ctrls,
                                          [0.35, 0.35, 0.3, 0.15, 0.15, 0.15])
        else:
            self.window.set_event_manager('GameEventManager', action_manager, ctrls,
                                          [0.35, 0.35, 0.3, 0.15, 0.15, 0.15])
        #####

        #  checkpoints
        self.checkpoints = self.level.get('checkpoints', [])

        if len(self.checkpoints) == 0:
            self.checkpoints.append(('base', self.model.Game.default_checkpoint_pos))

        self.t1 = -1
        self.count = 0  # every 4 space update ticks the position handler, the image handler
        # and the physic state updater must be updated
        self.number_of_space_updates = 0

        # Lives
        self.player_lives = self.model.Game.player_lives.get(self.current_save_id)
        if self.player_lives == 0:
            self.player_lives = 3
        else:
            lost = 3 - self.player_lives
            for i in range(lost):
                heart = self.hearts[-i - 1]
                heart.state = 'empty'

        self.window.update = self.update_positions
        self.window.update_image = self.update_images
        self.window.quit = self.dump_save

    def pause(self):
        self.paused = not self.paused

    def init_structure(self, data):
        name = data['name']
        is_decoration = '3d_effect_layer' in data
        dynamic = data.get('dynamic', False)
        correct_angle = data.get('correct_angle', True)

        if 'walls' in data:
            if 'action_on_touch' not in data:
                action_on_touch = None
            else:
                action_on_touch = data['action_on_touch']

            if 'is_slippery_slope' in data:
                is_slippery_slope = data['is_slippery_slope']
            else:
                is_slippery_slope = False

            if not dynamic:
                self.space.add_structure(data['pos'], data['walls'], data['ground'], name,
                                         action_on_touch, is_slippery_slope)
            else:
                try:
                    mass = data['mass']
                except KeyError:
                    logger.warning(f'unspecified mass for dynamic structure {name}, set to default value 20')
                    mass = 20

                try:
                    center_of_gravity = data['center_of_gravity']
                except KeyError:
                    logger.warning(
                        f'unspecified center of gravity for dynamic structure {name}, set to default value (0, 0)')
                    center_of_gravity = 0, 0

                self.space.add_dynamic_structure(data['pos'], data['walls'], data['ground'], name, mass,
                                                 center_of_gravity, action_on_touch, is_slippery_slope, correct_angle)
        else:
            assert not dynamic, f'dynamic structure {name} should have collision data'

        if is_decoration:
            pos_handler = DecorationPositionHandler(data['pos'], data['3d_effect_layer'], self.window.screen_offset)
        elif dynamic:
            pos_handler = DynamicStructurePositionHandler(self.space.objects[name][0], correct_angle)
        else:
            pos_handler = StaticPositionHandler(data['pos'])
        layer = data.get('layer', 0)
        if data['is_built']:
            struct = self.window.add_structure(self.viewer_page, layer, pos_handler, data['res'], dynamic=dynamic)
        else:
            struct = self.window.build_structure(
                self.viewer_page, layer, pos_handler, data['res'], self.level['palette'], dynamic=dynamic)

        if is_decoration:
            struct.affected_by_screen_offset = False
        self.viewer_page.structures.add(struct)

        self.structures[name] = struct

    def init_player(self, additional_data):
        player_data = self.model.Game.BasePlayerData
        name = player_data.name

        self.space.add_humanoid_entity(player_data.height,
                                       player_data.width, (player_data.pos_x.get(self.current_save_id),
                                                           player_data.pos_y.get(self.current_save_id)), name)

        self.player = self.window.add_entity(
            self.viewer_page, 0, PlayerPositionHandler(self.space.objects[name][0], self.triggers,
                                                       self.model.Game.BasePlayerData),
            additional_data['res'],
            PhysicStateUpdater(self.space.objects[name][0], self.action_manager.land, self.save_position, self.space,
                               player_data.StateDuration),
            ParticleHandler(self.spawn_particle), self.action_manager.set_state,
            self.player_loose_one_life
        )

        self.camera_handler.player = self.player
        self.player.position_handler.do_update_triggers = True

        self.viewer_page.entities.add(self.player)
        self.action_manager.player = self.player

        self.entities[name] = self.player

    def spawn_particle(self, pos, state, direction, particle_id, res):

        if len(self.dash_particles) != 0 and len(self.dash_particles) > particle_id:
            particle = self.dash_particles[particle_id]
            particle.direction = direction
            particle.image_changed = True
            particle.show()
            particle.change_position(*pos)
            particle.image_handler.revive()
        else:
            position_handler = StaticPositionHandler(pos)
            particle = self.window.spawn_particle(self.viewer_page, -1, position_handler, res, state, direction, 8)
            self.viewer_page.dash_particles.add(particle)
            self.dash_particles.append(particle)

    def init_text(self, data):
        text_getter = FormatTextGetter(data['text'], data['values'], self)
        position_handler = StaticPositionHandler(data['pos'])
        sprite = self.window.add_text(
            self.viewer_page, 0, 'm5x7', data['size'], text_getter, position_handler)
        self.viewer_page.texts.add(sprite)
        return sprite

    def init_constraint(self, data):
        self.structures[data['object_a']].constrained = True
        self.structures[data['object_b']].constrained = True

        self.space.add_constraint(data['object_a'], data['object_b'], data['anchor_a'], data['anchor_b'], data['name'])

        if 'res' in data:
            position_handler = RopePositionHandler(self.space.objects[data['name']][0])
            sprite = self.window.add_rope(self.viewer_page, -1, position_handler, data['res'])
            self.viewer_page.structures.add(sprite)

            self.structures[data['name']] = sprite

    @staticmethod
    def dump_save():
        SaveComponent.dump()

    def save_position(self):
        self.model.Game.BasePlayerData.pos_x.set(
            round(self.player.position_handler.body.position.x), self.current_save_id)
        self.model.Game.BasePlayerData.pos_y.set(
            round(self.player.position_handler.body.position.y), self.current_save_id)
        self.model.Game.BaseBGData.camera_pos_x.set(round(self.window.screen_offset[0]), self.current_save_id)
        self.model.Game.BaseBGData.camera_pos_y.set(round(self.window.screen_offset[1]), self.current_save_id)

    def player_loose_one_life(self):
        self.player_lives -= 1
        self.player.position_handler.body.position = self.player.position_handler.body.position.x, 5000

        heart = self.hearts[self.player_lives]
        heart.state = 'empty'

        if self.player_lives == 0:
            self.player_lives = 3
            self.player_death()
            self.model.Game.player_lives.set(self.player_lives, self.current_save_id)

            return True
        else:
            self.player.state = 'hit'
            self.model.Game.player_lives.set(self.player_lives, self.current_save_id)

            return False

    def tp_to_stable_ground(self):
        x = self.model.Game.BasePlayerData.pos_x.get(self.current_save_id)
        y = self.model.Game.BasePlayerData.pos_y.get(self.current_save_id)
        self.player.position_handler.body.position = x, y
        self.space.reindex_shapes_for_body(self.player.position_handler.body)

    def player_death(self):
        self.player.state = 'die'
        self.is_player_dead = True
        self.is_camera_handler_activated = False
        for sprite in self.viewer_page.get_all_sprites():
            if sprite != self.player:
                if sprite.visible:
                    sprite.hide()
                else:
                    self.already_hidden.append(sprite)

        bg = self.window.add_solid_color_background(
            self.viewer_page, -1, StaticPositionHandler((0, 0)), (245, 245, 245, 100))
        bg.affected_by_screen_offset = False
        bg.update_position()
        self.viewer_page.bg_layers.add(bg)

        self.sprites_to_delete.append(bg)

        self.scheduled_func.add(self.display_death_screen)
        self.window.schedule_once(self.display_death_screen, 1.8)

        cp_id = self.model.Game.last_checkpoint.get(self.current_save_id)
        map_id = self.model.Game.last_checkpoints_map.get(self.current_save_id)
        if map_id == self.current_map_id:
            try:
                _, new_pos = self.checkpoints[cp_id]
            except IndexError:
                _, new_pos = self.checkpoints[0]
                logger.warning(f'invalid checkpoint id: "{cp_id}" for map {map_id}')
        else:
            self.model.Game.current_map_id.set(map_id, self.current_save_id)
            level = self.load_map_file(self.model.Game.last_checkpoints_map.get(self.current_save_id))
            checkpoints = level.get('checkpoints', [])
            if len(checkpoints) == 0:
                checkpoints.append(('base', self.model.Game.default_checkpoint_pos))
            try:
                _, new_pos = checkpoints[cp_id]
            except IndexError:
                _, new_pos = checkpoints[0]
                logger.warning(f'invalid checkpoint id: "{cp_id}" for map {map_id}')

        self.player.position_handler.body.position = new_pos
        self.player.position_handler.body.velocity = (0, 0)

        self.model.Game.BasePlayerData.pos_x.set(new_pos[0], self.current_save_id)
        self.model.Game.BasePlayerData.pos_y.set(new_pos[1], self.current_save_id)

    def display_death_screen(self, *_, **__):

        bg = self.window.add_solid_color_background(
            self.viewer_page, -1, StaticPositionHandler((0, 0)), (245, 245, 245, 255))
        bg.affected_by_screen_offset = False
        bg.update_position()
        self.viewer_page.bg_layers.add(bg)

        death_screen = self.window.add_structure(
            self.viewer_page, 0, StaticPositionHandler((0, 0)), self.model.Game.death_screen_res_path
        )
        death_screen.affected_by_screen_offset = False
        death_screen.opacity = 0
        death_screen.fade_to(255)
        death_screen.update_position()
        self.viewer_page.structures.add(death_screen)

        self.sprites_to_delete.append(bg)
        self.sprites_to_delete.append(death_screen)

        self.scheduled_func.add(self.start_reviving_transition)
        self.window.schedule_once(self.start_reviving_transition, 3.4)

    def start_reviving_transition(self, *_, **__):
        self.is_camera_handler_activated = True

        if self.model.Game.last_checkpoints_map.get(self.current_save_id) == self.current_map_id:
            _, new_pos = self.checkpoints[self.model.Game.last_checkpoint.get(self.current_save_id)]
            self.player.position_handler.body.position = new_pos
            self.player.position_handler.body.velocity = (0, 0)

        transition = Transition(120, (0, 0, 0, 255), (1280, 720), self.reanimate_player, 'in')
        self.window.add_transition(transition)

    def reanimate_player(self, *_, **__):
        if self.model.Game.last_checkpoints_map.get(self.current_save_id) != self.current_map_id:
            self.window.screen_offset = self.camera_handler.get_camera_position_after_player_death(
                (self.model.Game.BasePlayerData.pos_x.get(self.current_save_id),
                 self.model.Game.BasePlayerData.pos_y.get(self.current_save_id))
            )
            self.model.Game.BaseBGData.camera_pos_x.set(self.window.screen_offset[0], self.current_save_id)
            self.model.Game.BaseBGData.camera_pos_y.set(self.window.screen_offset[1], self.current_save_id)

            self.load_map(self.model.Game.last_checkpoints_map.get(self.current_save_id))
        else:

            self.is_player_dead = False

            for _ in range(len(self.sprites_to_delete)):
                sprite = self.sprites_to_delete.pop()
                if sprite in self.viewer_page.bg_layers:
                    self.viewer_page.bg_layers.remove(sprite)
                elif sprite in self.viewer_page.structures:
                    self.viewer_page.structures.remove(sprite)
                sprite.delete()
                del sprite

            for sprite in self.viewer_page.get_all_sprites():
                if sprite not in self.already_hidden:
                    sprite.show()
            self.already_hidden = []

            self.player.dead = False
            self.player.state = 'idle'
            self.player.direction = 1
            self.action_manager.next_direction = 1

        for heart in self.hearts:
            heart.state = 'full'

        transition = Transition(300, (0, 0, 0, 255), (1280, 720), lambda *_, **__: None, 'out')
        self.window.add_transition(transition)

    def load_map_file(self, map_id):
        if map_id in self.level_cache:
            return self.level_cache[map_id]
        else:
            with open(self.model.Game.maps[map_id]) as datafile:
                level = yaml.safe_load(datafile)
            self.level_cache[map_id] = level
            return level

    def load_map_on_next_frame(self, map_id):
        self.additional_commands.append(lambda: self.load_map(map_id))

    def load_map(self, map_id):
        self.model.Game.current_map_id.set(map_id, self.current_save_id)

        self.level = self.load_map_file(self.model.Game.current_map_id.get(self.current_save_id))
        self.level_res = self.level['background_data']['res']

        self.window.reset_event_manager()

        self.start_game()

    def quit(self):
        for func in self.scheduled_func:
            self.window.unschedule(func)
        self.scheduled_func = set()
        self.dump_save()

    def update_positions(self, *_, **__):
        if self.t1 == -1:
            self.t1 = perf_counter()
        n1 = round((perf_counter() - self.t1) * 60 * 4) - self.number_of_space_updates

        sprites = self.viewer_page.get_all_sprites()
        for i in range(n1):
            if not self.paused:
                self.space.step(1/60/4)
                self.player.update_state(1/60/4)
                if self.count == 3:
                    self.count = 0
                    if self.is_camera_handler_activated:
                        self.window.screen_offset = self.camera_handler.update_camera_position(1)
                    for sprite in sprites:
                        last = i + 4 - self.count >= (n1 // 3 - 1)
                        sprite.update_position(last)
                else:
                    self.count += 1
        self.number_of_space_updates += n1

        for _ in range(len(self.additional_commands)):
            self.additional_commands.pop()()

    def update_images(self):
        sprites = self.viewer_page.get_all_sprites()
        for sprite in sprites:
            sprite.update_image()

    def loading_update(self, *_, **__):
        self.loading_finished_check()

    def toggle_debug_draw(self):
        self.debug_draw_activated = not self.debug_draw_activated
        if self.debug_draw_activated:
            self.draw_options = DrawOptions(self.window)
            self.window.after_draw = self.draw_space
        else:
            self.draw_options = None
            self.window.after_draw = lambda *_, **__: None

    def draw_space(self):
        if self.draw_options is not None:
            self.draw_options.vecs = list()

            self.space.debug_draw(self.draw_options)

