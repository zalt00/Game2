# -*- coding:Utf-8 -*-

from .position_handler import StaticPositionHandler, PlayerPositionHandler, BgLayerPositionHandler
from .action_manager import GameActionManager, MainMenuActionManager, OptionsActionManager
from .physics_updater import PhysicsUpdater
from .particles_handler import ParticleHandler
from .res_getter import FormatTextResGetter, SimpleTextResGetter
from pygame.locals import *
import pygame.mouse
from .space import GameSpace
import pymunk.pygame_util
from utils.save_modifier import SaveComponent
from .triggers import Trigger
from .trigger_action_getter import GameActionGetter
from time import perf_counter
import yaml


class App:
    def __init__(self, window, model):
        self.window = window
        self.model = model
        self.current = Menu(window, model, self.start_game)
        
    def change_app_state(self, new_state):
        for sprite in self.window.global_group.sprites():
            sprite.kill()
        self.current.quit()
        self.window.on_draw = lambda *_, **__: None
        self.window.quit = lambda *_, **__: None
        
        del self.current
        
        if new_state == 'game':
            self.current = Game(self.window, self.model, self.return_to_main_menu)
        elif new_state == 'menu':
            self.current = Menu(self.window, self.model, self.start_game)
    
    def start_game(self):
        self.change_app_state('game')
        
    def return_to_main_menu(self):
        self.change_app_state('menu')
    

class Menu:
    def __init__(self, window, model, start_game_callback):
        self.window = window
        self.model = model
        self.state = 'menu'
        
        SaveComponent.load()

        self.start_game_callback = start_game_callback

        self.empty_button_res = self.window.render_font('', 40, '#eeeeee', '#eeeeee', 100, 35, 5)
        
        self.window.screen_dec[:] = (0, 0)
        self.window.init_joys()
        self.window.fps = 25

        self.page_name = None
        self.page = None
        self.page_res = None
        self.pos_hdlrs = None
        self.panels = None
        self.menu_objects = None
        self.action_manager = None
        self.classic_buttons = None

        self.texts = None

        self.init_page('MainMenu')

        pygame.mouse.set_visible(True)
        
        self.window.on_draw = self.update

    def delete_current_page(self):
        self.page_name = None
        for sprite in self.window.global_group.sprites():
            sprite.kill()

    def init_page(self, page_name):
        self.page_name = page_name
        self.page = self.model.Menu.get(page_name)
        self.page_res = self.page.bg_res

        n_layers = self.window.get_number_of_layers(self.page_res)
        pos = self.page.bg_pos

        position_handler = StaticPositionHandler(pos)
        pos_hdlrs = [BgLayerPositionHandler(pos, [0, 0]) for _ in range(n_layers)]

        self.window.add_bg(
            self.page_res,
            pos_hdlrs,
            True,
            False,
            True
        )

        pos2 = pos[0] + self.window.get_length(self.page_res) * 2, pos[1]
        ph = BgLayerPositionHandler(pos2, [0, 0], self.reverse_trajectory)
        pos_hdlrs.append(ph)
        self.window.add_bg_layer(self.page_res, 4, ph, foreground=True)
        """
        for p in pos_hdlrs:
            p.add_trajectory((-2300, 0), 1500, 1, 100)
        """
        self.pos_hdlrs = pos_hdlrs

        self.panels = {}
        self.menu_objects = []

        self.classic_buttons = {}

        self.texts = {}

        for oname in self.page.Objects.objects:
            data = self.page.Objects.get(oname)
            obj = None
            if data.typ == 'button':
                bpos_hdlr = StaticPositionHandler(data.pos)
                obj = self.window.add_button(data.res, bpos_hdlr, data.action)
            elif data.typ == 'structure':
                spos_hdlr = StaticPositionHandler(data.pos)
                obj = self.window.add_structure(data.res, spos_hdlr, 'idle')
                if hasattr(data, 'panel_name'):
                    additional_buttons = self.init_panel_buttons(data)
                    self.panels[data.panel_name] = dict(structure=obj,
                                                        buttons=additional_buttons,
                                                        buttons_order=data.buttons_order, data=data)

            elif data.typ == 'text':
                tpos_hdlr = StaticPositionHandler(data.pos)
                obj = self.window.add_text(
                    SimpleTextResGetter(data.text, self.window.render_text,
                                        data.color, data.size, data.font), tpos_hdlr)
                self.texts[data.name] = obj

            if obj is not None:
                self.menu_objects.append(obj)
                if hasattr(data, 'button_name'):
                    self.classic_buttons[data.button_name] = obj

        actionmanager = None
        if self.page.action_manager == 'MainMenuActionManager':
            actionmanager = MainMenuActionManager(
                self.window.button_group,
                self.classic_buttons,
                self.page.Objects.classic_buttons_order,
                self.panels,
                self.page.Objects.panel_order,
                self.texts,
                (),
                self.start_game_callback,
                self.quit_game,
                self.open_options
            )

        elif self.page.action_manager == 'OptionsActionManager':
            actionmanager = OptionsActionManager(
                self.window.button_group,
                self.classic_buttons,
                self.page.Objects.classic_buttons_order,
                self.panels,
                self.page.Objects.panel_order,
                self.texts,
                (),
                self.close_options,
                self.change_kb_ctrls,
                self.change_con_ctrls,
                self.set_ctrl,
                self.model.Options,
                self.reinit_page
            )

        if actionmanager is None:
            raise ValueError(f'invalid action manager name: {self.page.action_manager}')
        self.window.set_menu_event_manager(actionmanager)
        self.action_manager = actionmanager

    def update(self, *_, **__):
        self.window.global_group.update()
    
    def init_panel_buttons(self, panel_data):
        data = panel_data
        buttons_data = panel_data.additional_buttons
        ndict = {}
        for bname, bdata in buttons_data.items():
            res_name = bdata.get('res', None)
            if res_name is None:
                font_data = bdata['font']
                if font_data[0] == 'nkb':
                    txt = self.get_key_name(font_data[2].get())
                if font_data[0] == 'ncon':
                    txt = self.get_controller_value_name(font_data[2].get_shorts())
                
                elif font_data[0] == 'txt':
                    txt = font_data[2]
                res = self.window.render_font(txt, font_data[1], font_data[3], font_data[4], font_data[5], font_data[6], font_data[7])
            else:
                res = self.window.res_loader.load(res_name)
            button = self.window.add_button(res, StaticPositionHandler(bdata['pos']), bdata['action'])
            if 'arg' in bdata:
                button.arg = bdata['arg']
                if hasattr(data, 'options_save'):
                    self.set_state(data, button, bname)
              
            ndict[bname] = button
        return ndict

    def reinit_page(self):
        if self.page_name is not None:
            page_name = self.page_name
            self.delete_current_page()
            self.init_page(page_name)

    def get_key_name(self, nkey):
        name = self.model.key_names.get(nkey, None)
        if name is None:
            name = pygame.key.name(nkey)
        return name
    
    def get_controller_value_name(self, nvalue):
        name = self.model.controller_values_name[nvalue]
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
                        if font_data[0] == 'nkb':
                            txt = self.get_key_name(font_data[2].get())
                        if font_data[0] == 'ncon':
                            txt = self.get_controller_value_name(font_data[2].get_shorts())
                        
                        elif font_data[0] == 'txt':
                            txt = font_data[2]
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

    def close_options(self):
        self.delete_current_page()
        self.init_page('MainMenu')
    
    def change_kb_ctrls(self, button):
        button.image_handler.res = self.empty_button_res
        self.window.set_change_ctrls_event_manager(self.action_manager, 'kb')
        
    def change_con_ctrls(self, button):
        button.image_handler.res = self.empty_button_res
        self.window.set_change_ctrls_event_manager(self.action_manager, 'con')
        
    def set_ctrl(self, value, button):
        if isinstance(value, tuple):
            name = self.get_controller_value_name(value)
        else:
            name = self.get_key_name(value)
        
        button.image_handler.res = self.window.render_font(name, 40, '#eeeeee', '#888888', 100, 35, 5)
        self.window.set_menu_event_manager(self.action_manager)

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
    def __init__(self, window, model, return_to_main_menu):
        self.window = window
        self.model = model
        self.state = 'in_game'

        self.window.current_bg.fill((0, 0, 0))

        # self.window.res_loader.cache.clear()

        self.t1 = perf_counter()
        self.count = 0  # every 4 space update ticks the position handler, the image handler
        # and the physic state updater must be updated
        self.number_of_space_updates = 0
        
        self.window.fps = 60

        self.window.init_joys()
        self.debug_draw = False

        if self.debug_draw:
            self.draw_options = pymunk.pygame_util.DrawOptions(self.window.screen)
        
        pygame.mouse.set_visible(False)
        
        SaveComponent.load()
        with open(self.model.Game.maps[self.model.Game.current_map_id.get(1)]) as datafile:
            self.level = yaml.safe_load(datafile)
        self.level_res = self.level['background_data']['res']
         
        self.space = GameSpace(0, 0)

        self.player = None

        ### BG ###
        dynamic = True
        n_layers = self.window.get_number_of_layers(self.level_res)
        pos = self.level['background_data']['pos']
        if not dynamic:
            position_handler = StaticPositionHandler(pos)
            pos_hdlrs = [position_handler for _ in range(n_layers)]
        else:
            pos_hdlrs = [BgLayerPositionHandler(pos, self.window.screen_dec) for _ in range(n_layers)]
        
        self.window.add_bg(
            self.level_res,
            pos_hdlrs,
            dynamic,
            False
        )
        
        # pos2 = pos[0] + self.window.get_length(self.level_res) * 2, pos[1]
        # ph = BgLayerPositionHandler(pos2, self.window.screen_dec)
        # pos_hdlrs.append(ph)
        # self.window.add_bg_layer(self.level_res, 4, ph, foreground=True)
        ######
        
        self.entities = dict()
        self.structures = dict()

        ### TRIGGERS ###
        self.triggers = [None] * len(self.level['triggers_data'])
        self.ag = GameActionGetter(self.triggers, self.window, pos_hdlrs, self.entities)
        for trigdata in self.level['triggers_data'].values():
            self.triggers[trigdata['id']] = Trigger(trigdata, self.ag)
        #####

        ### CAMERA ###

        self.ag('AbsoluteMovecam',
                x=self.model.Game.BaseBGData.camera_pos_x.get(1),
                y=self.model.Game.BaseBGData.camera_pos_y.get(1),
                total_duration=1,
                fade_in=0,
                fade_out=0
                )()
        #####

        action_manager = GameActionManager(None, return_to_main_menu, self.save_position)
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
        
        self.window.set_game_event_manager(action_manager, ctrls, [0.35, 0.35, 0.3, 0.15, 0.15, 0.15])
        #####

        self.window.on_draw = self.update
        self.window.quit = self.dump_save
    
    def init_structure(self, data):
        
        name = data['name']
        pos_handler = StaticPositionHandler(data['pos'])
        if data['is_built']:
            struct = self.window.add_structure(data['res'], pos_handler, data['state'])
        else:
            struct = self.window.build_structure(data['res'], self.level['palette'], pos_handler, data['state'])
        
        self.space.add_structure(data['pos'], data['poly'], data['ground'], name)
        
        self.structures[name] = struct
    
    def init_player(self, additional_data):
        player_data = self.model.Game.BasePlayerData
        name = player_data.name
        
        self.space.add_humanoid_entity(player_data.height,
                                       player_data.width, (player_data.pos_x.get(1), player_data.pos_y.get(1)), name)
        
        self.player = self.window.add_entity(
            additional_data['res'],
            PlayerPositionHandler(self.space.objects[name][0], self.triggers),
            PhysicsUpdater(self.space.objects[name][0], self.action_manager.land, self.save_position),
            ParticleHandler(self.window.spawn_particle),
            self.action_manager.set_state)
        self.action_manager.player = self.player
        
        self.entities[name] = self.player

    def init_text(self, data):
        res_getter = FormatTextResGetter(
            data['text'], data['values'], self, self.window.render_text, data['color'], data['size'])
        poshdlr = StaticPositionHandler(data['pos'])
        self.window.add_text(res_getter, poshdlr)

    @staticmethod
    def dump_save():
        SaveComponent.dump()
    
    def save_position(self):
        self.model.Game.BasePlayerData.pos_x.set(round(self.player.position_handler.body.position.x), 1)
        self.model.Game.BasePlayerData.pos_y.set(round(self.player.position_handler.body.position.y), 1)
        self.model.Game.BaseBGData.camera_pos_x.set(round(self.window.bg_pos[0]), 1)
        self.model.Game.BaseBGData.camera_pos_y.set(round(self.window.bg_pos[1]), 1)

    def quit(self):
        self.dump_save()
    
    def update(self, dt):
        pygame.display.set_caption(str(1/dt))
        self.update_space(dt)
    
    def update_space(self, _):
        if self.debug_draw:
            self.space.debug_draw(self.draw_options)
        n1 = round((perf_counter() - self.t1) * 60 * 4) - self.number_of_space_updates

        for i in range(n1):
            self.space.step(1/60/4)
            if self.count == 3:
                self.count = 0
                self.window.global_group.update(1)
            else:
                self.count += 1
        self.number_of_space_updates += n1



