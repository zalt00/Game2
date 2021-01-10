# -*- coding:Utf-8 -*-

from .position_handler import StaticPositionHandler, \
    PlayerPositionHandler, BgLayerPositionHandler, DecorationPositionHandler, DynamicStructurePositionHandler
from .action_manager import GameActionManager,\
    MainMenuActionManager, OptionsActionManager, CharacterSelectionActionManager
from .physic_state_updater import PhysicStateUpdater
from .particles_handler import ParticleHandler
from .text_getter import FormatTextGetter, SimpleTextGetter
from .space import GameSpace
import pymunk.pyglet_util
from utils.save_modifier import SaveComponent
from .triggers import Trigger
from .trigger_action_getter import GameActionGetter
from time import perf_counter
import yaml
import threading
from viewer.transition import Transition
from .camera_handler import CameraHandler
from utils.logger import logger
from pyglet.window import key
import os


class App:
    def __init__(self, window, model, debug=False):
        self.window = window
        self.model = model
        print(os.path.abspath(self.model.resources_path))
        self.window.create_resources_loader(os.path.abspath(self.model.resources_path))
        self.current = Menu(window, model, self.start_game, debug=debug)

        self.debug = debug

        self.current_thread = None
        self.transition_finished = False
        self.transition = None

        self.current_save_id = 1

    def change_app_state(self, new_state):
        self.current.quit()
        self.window.update = lambda *_, **__: None
        self.window.after_draw = lambda *_, **__: None
        self.window.quit = lambda *_, **__: None

        del self.current

        if new_state == 'game':
            self.current = Game(self.window, self.model,
                                self.return_to_main_menu, self.game_loading_finished_check, self.current_save_id,
                                debug=self.debug)
        elif new_state == 'menu':
            self.current = Menu(self.window, self.model, self.start_game, debug=self.debug)

    def start_fade_in_transition(self):
        self.transition_finished = False
        self.transition = Transition(8, (0, 0, 0), (self.window.width, self.window.height),
                                     self.fade_in_transition_finished, 'in', False)

        self.window.add_transition(self.transition)

    def fade_in_transition_finished(self):
        self.transition_finished = True

    def delayed_start_game(self):
        self.current.start_game()
        self.start_fade_out_transition()

    def start_fade_out_transition(self):
        if self.transition is not None:
            self.transition.stop()
        self.transition = Transition(8, (0, 0, 0), (self.window.width, self.window.height),
                                     lambda: None, 'out', True)

        self.window.add_transition(self.transition)

    def game_to_menu_fade_in_transition(self):
        self.transition = Transition(8, (0, 0, 0), (self.window.width, self.window.height),
                                     self.game_to_menu_fade_out_transition, 'in', True)

        self.window.add_transition(self.transition)

    def game_to_menu_fade_out_transition(self):
        self.change_app_state('menu')
        self.transition = Transition(8, (0, 0, 0), (self.window.width, self.window.height),
                                     lambda: None, 'out', True)

        self.window.add_transition(self.transition)

    def start_game(self, current_save_id):
        if getattr(self.transition, 'state', None) != 1:
            self.current_save_id = current_save_id
            self.change_app_state('game')
            self.start_fade_in_transition()
            t = threading.Thread(target=self.current.load_resources)
            t.start()
            self.current_thread = t

    def game_loading_finished_check(self):
        if self.current_thread is not None:
            if not self.current_thread.is_alive():
                if self.transition_finished or True:
                    self.current.start_game()
                    self.transition.stop()
                    self.start_fade_out_transition()
                elif self.transition is not None:
                    self.transition.on_transition_end = self.delayed_start_game
                self.transition_finished = False

    def return_to_main_menu(self):
        if getattr(self.transition, 'state', None) != 1:
            self.game_to_menu_fade_in_transition()


class Menu:
    def __init__(self, window, model, start_game_callback, debug=False):
        self.window = window
        self.model = model
        self.state = 'menu'

        SaveComponent.load()

        self.debug = debug

        self.start_game_callback = start_game_callback

        self.window.screen_offset = 0, 0

        self.page_name = None
        self.page = None
        self.page_res = None
        self.pos_hdlrs = None
        self.panels = None
        self.menu_objects = None
        self.action_manager = None
        self.classic_buttons = None
        self.viewer_page = None

        self.window.set_page(self.window.menu_page)

        self.texts = None

        self.init_page('MainMenu')

        self.window.update = self.update

    def delete_current_page(self):
        self.window.menu_page.remove_child(self.page_name)
        self.page_name = None

    def init_page(self, page_name):
        self.page_name = page_name
        self.page = self.model.Menu.get(page_name)
        self.page_res = self.page.bg_res

        self.viewer_page = self.window.new_page(page_name)
        self.viewer_page.add_group('buttons')
        self.viewer_page.add_group('bg_layers')
        self.viewer_page.add_group('structures')
        self.viewer_page.add_group('texts')

        self.window.menu_page.add_child(self.viewer_page)

        n_layers = self.window.get_number_of_layers(self.page_res)
        pos = self.page.bg_pos

        position_handler = StaticPositionHandler(pos)
        pos_hdlrs = [BgLayerPositionHandler(pos, [0, 0]) for _ in range(n_layers)]

        bg_layers = self.window.add_bg(self.viewer_page, pos_hdlrs, self.page_res)
        self.viewer_page.bg_layers.update(bg_layers)

        self.pos_hdlrs = pos_hdlrs

        self.panels = {}
        self.menu_objects = []

        self.classic_buttons = {}

        self.texts = {}

        self.y_offset = self.model.Menu.y_offset

        for oname in self.page.Objects.objects:
            data = self.page.Objects.get(oname)
            obj = None
            if data.typ == 'button':
                if data.pos[1] > 2000:
                    offset = self.y_offset * 1000
                else:
                    offset = self.y_offset
                bpos_hdlr = StaticPositionHandler([data.pos[0], data.pos[1] + offset])
                if hasattr(data, 'res'):
                    obj = self.window.add_button(self.viewer_page, 0, bpos_hdlr, data.res, data.action)
                    self.viewer_page.buttons.add(obj)
                else:
                    font_data = data.font
                    obj = self.window.add_generated_button(
                        self.viewer_page, 0, 'm5x7', font_data[1], self.get_button_text_from_font_data(font_data),
                        StaticPositionHandler([data.pos[0], data.pos[1] + offset]),
                        data.action, font_data[5], font_data[-1])
                    self.viewer_page.buttons.add(obj)

                if hasattr(data, 'arg'):
                    obj.arg = data.arg
            elif data.typ == 'structure':
                if data.pos[1] > 2000:
                    offset = self.y_offset * 1000
                else:
                    offset = self.y_offset
                spos_hdlr = StaticPositionHandler([data.pos[0], data.pos[1] + offset])
                obj = self.window.add_structure(self.viewer_page, 0, spos_hdlr, data.res)
                self.viewer_page.structures.add(obj)
                if hasattr(data, 'panel_name'):
                    additional_buttons = self.init_panel_buttons(data)
                    self.panels[data.panel_name] = dict(structure=obj,
                                                        buttons=additional_buttons,
                                                        buttons_order=data.buttons_order, data=data)

            elif data.typ == 'text':
                if data.pos[1] > 2000:
                    offset = self.y_offset * 1000
                else:
                    offset = self.y_offset
                tpos_hdlr = StaticPositionHandler([data.pos[0], data.pos[1] + offset])
                obj = self.window.add_text(self.viewer_page, 0, data.font, data.size,
                                           SimpleTextGetter(data.text), tpos_hdlr)
                self.texts[data.name] = obj
                self.viewer_page.texts.add(obj)
            if obj is not None:
                self.menu_objects.append(obj)
                if hasattr(data, 'button_name'):
                    self.classic_buttons[data.button_name] = obj

        actionmanager = None
        if self.page.action_manager == 'MainMenuActionManager':
            actionmanager = MainMenuActionManager(
                self.window,
                self.viewer_page.buttons,
                self.classic_buttons,
                self.page.Objects.classic_buttons_order,
                self.panels,
                self.page.Objects.panel_order,
                self.texts,
                (),
                self.play,
                self.quit_game,
                self.open_options
            )

        elif self.page.action_manager == 'OptionsActionManager':
            actionmanager = OptionsActionManager(
                self.window,
                self.viewer_page.buttons,
                self.classic_buttons,
                self.page.Objects.classic_buttons_order,
                self.panels,
                self.page.Objects.panel_order,
                self.texts,
                (),
                self.return_to_main_menu,
                self.change_kb_ctrls,
                self.change_con_ctrls,
                self.set_ctrl,
                self.model.Options,
                self.reinit_page,
                self.window.set_display_mode
            )
        elif self.page.action_manager == 'CharacterSelectionActionManager':
            actionmanager = CharacterSelectionActionManager(
                self.window,
                self.viewer_page.buttons,
                self.classic_buttons,
                self.page.Objects.classic_buttons_order,
                self.panels,
                self.page.Objects.panel_order,
                self.texts,
                (),
                self.start_game_callback,
                self.return_to_main_menu
            )

        if actionmanager is None:
            raise ValueError(f'invalid action manager name: {self.page.action_manager}')
        self.window.set_event_manager('MenuEventManager', actionmanager)
        self.action_manager = actionmanager

    def update(self, *_, **__):
        for sprite in self.viewer_page.get_all_sprites():
            sprite.update_()
    
    def init_panel_buttons(self, panel_data):
        data = panel_data
        buttons_data = panel_data.additional_buttons
        ndict = {}
        for bname, bdata in buttons_data.items():
            res_name = bdata.get('res', None)
            if bdata['pos'][1] > 2000:
                offset = self.y_offset * 1000
            else:
                offset = self.y_offset
            if res_name is not None:
                button = self.window.add_button(
                    self.viewer_page, 0, StaticPositionHandler([bdata['pos'][0], bdata['pos'][1] + offset]),
                    res_name, bdata['action'])
                self.viewer_page.buttons.add(button)

            else:
                font_data = bdata['font']
                button = self.window.add_generated_button(
                    self.viewer_page, 0, 'm5x7', font_data[1], self.get_button_text_from_font_data(font_data),
                    StaticPositionHandler([bdata['pos'][0], bdata['pos'][1] + offset]),
                    bdata['action'], font_data[5], font_data[-1])
                self.viewer_page.buttons.add(button)

            if 'arg' in bdata:
                button.arg = bdata['arg']
                if hasattr(data, 'options_save'):
                    self.set_state(data, button, bname)
              
            ndict[bname] = button
        return ndict

    def get_button_text_from_font_data(self, font_data):
        if font_data[0] == 'nkb':
            txt = self.get_key_name(font_data[2].get())
        elif font_data[0] == 'ncon':
            txt = self.get_controller_value_name(font_data[2].get_shorts())

        elif font_data[0] == 'txt':
            txt = font_data[2]
        else:
            raise ValueError(f'font_data[0] must be either nkb, ncon or txt, not {font_data[0]}')
        return txt

    def reinit_page(self):
        if self.page_name is not None:
            page_name = self.page_name
            self.delete_current_page()
            self.init_page(page_name)

    def get_key_name(self, nkey):
        name = self.model.key_names.get(nkey, None)
        if name is None:
            name = key.symbol_string(nkey).lower()
        return name
    
    def get_controller_value_name(self, nvalue):
        name = self.model.controller_values_name.get(nvalue, None)
        if name is None:
            name = 'undef'
        return name
    
    def reinit_panel_buttons(self):
        for panel_name, p in self.panels.items():
            data = p['data']
            if hasattr(data, 'options_save'):
                for bname in p['buttons']:
                    self.set_state(data, p['buttons'][bname], bname)
            else:
                for bname, bdata in p['data'].additional_buttons.items():
                    res_name = bdata.get('res', None)
                    if res_name is None:
                        font_data = bdata['font']
                        txt = None
                        raise RuntimeError
                        res = self.window.render_font(
                            txt, font_data[1], font_data[3], font_data[4], font_data[5], font_data[6], font_data[7])
                    else:
                        res = self.window.res_loader.load(res_name)
                    p['buttons'][bname].image_handler.res = res
    
    def set_state(self, data, button, bname):
        button.arg[0] = data.options_save[bname][self.model.Options.get(data.panel_name).get(bname).get()]
        res, value = button.arg[button.arg[0] + 1]
        button.image_handler.change_res(res)  
        
    def open_options(self):
        self.delete_current_page()
        self.init_page('Options')

    def return_to_main_menu(self):
        self.delete_current_page()
        self.init_page('MainMenu')

    def play(self):
        self.delete_current_page()
        self.init_page('CharacterSelectionMenu')

    def change_kb_ctrls(self, button):
        button.label.text = ''
        self.window.set_event_manager('ChangeCtrlsEventManager', self.action_manager, 'kb')

    def change_con_ctrls(self, button):
        button.label.text = ''
        self.window.set_event_manager('ChangeCtrlsEventManager', self.action_manager, 'con')
        
    def set_ctrl(self, value, button):
        if isinstance(value, tuple):
            name = self.get_controller_value_name(value)
        else:
            name = self.get_key_name(value)
        
        button.change_text(name)
        self.window.set_event_manager('MenuEventManager', self.action_manager)

    def reverse_trajectory(self, t):
        if int(t.target[0]) == 0:
            for p in self.pos_hdlrs:
                p.add_trajectory((-2300, 0), 1500, 400, 400)
        else:
            for p in self.pos_hdlrs:
                p.add_trajectory((0, 0), 1500, 400, 400)            
    
    @staticmethod
    def dump_save():
        SaveComponent.dump()    
    
    def quit_game(self):
        self.dump_save()
        self.window.stop_loop()
    
    def quit(self):
        self.dump_save()


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

        self.additional_commands = []

        self.current_map_id = -1

        self.draw_options = None

        self.viewer_page = None

        self._paused = False
        self.debug_draw_activated = False

        SaveComponent.load()
        self.level = self.load_map_file(self.model.Game.current_map_id.get(self.current_save_id))

        self.level_res = self.level['background_data']['res']

        self.window.reset_event_manager()

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

        self.window.game_page.add_child(self.viewer_page)
        self.window.set_page(self.window.game_page)

        # self.window.res_loader.cache.clear()
        return_to_main_menu = self.return_to_main_menu

        if self.debug_draw:
            self.draw_options = pymunk.pyglet_util.DrawOptions()
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
        self.triggers = dict()
        self.ag = GameActionGetter(self.triggers, self.window, self.camera_handler, self.entities, self.model,
                                   self.current_save_id, self.load_map_on_next_frame)
        for trigdata in self.level['triggers_data'].values():
            self.triggers[trigdata['id']] = Trigger(trigdata, self.ag)

        #####

        action_manager = GameActionManager(
            None, return_to_main_menu, self.save_position, self.toggle_debug_draw, self.pause)
        self.action_manager = action_manager

        ### OBJECTS ###

        for object_name, data in self.level['objects_data'].items():

            if data['type'] == 'player':
                self.init_player(data)
            elif data['type'] == 'structure':
                self.init_structure(data)
            elif data['type'] == 'text':
                self.init_text(data)
        #####


        ### EVENT MANAGER ###
        ctrls = {}
        for action in self.model.Options.Controls.actions:
            kb, controller = self.model.Options.Controls.get(action)
            action_id = getattr(GameActionManager, action.upper())

            ctrls[kb.get()] = action_id
            ctrls[controller.get_shorts()] = action_id

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
            self.viewer_page, 0, PlayerPositionHandler(self.space.objects[name][0], self.triggers),
            additional_data['res'],
            PhysicStateUpdater(self.space.objects[name][0], self.action_manager.land, self.save_position, self.space,
                               player_data.StateDuration),
            ParticleHandler(self.spawn_particle), self.action_manager.set_state,
            self.player_death
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

    def player_death(self):
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
                if not self.is_player_dead:
                    self.space.step(1/60/4)
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
            self.draw_options = pymunk.pyglet_util.DrawOptions()
            self.window.after_draw = self.draw_space
        else:
            self.draw_options = None
            self.window.after_draw = lambda *_, **__: None

    def draw_space(self):
        if self.draw_options is not None:
            self.space.debug_draw(self.draw_options)




