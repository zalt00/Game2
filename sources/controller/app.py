# -*- coding:Utf-8 -*-

from .position_handler import StaticPositionHandler, PlayerPositionHandler, BgLayerPositionHandler
from .action_manager import GameActionManager, MenuActionManager
from .physics_updater import PhysicsUpdater
from .particles_handler import ParticleHandler
from pygame.locals import *
import pygame.mouse
from .space import GameSpace
import pymunk.pygame_util
from utils.save_modifier import Save
from .triggers import Trigger
from .trigger_action_getter import GameActionGetter


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
        
        pygame.mouse.set_visible(True)
        
        Save.load('data/save.data')
        
        self.page = self.model.Menu.MainMenu
        self.page_res = self.page.bg_res
        
        n_layers = self.window.get_number_of_layers(self.page_res)
        pos = self.page.bg_pos
        
        
        position_handler = StaticPositionHandler(pos)
        
        pos_hdlrs = [BgLayerPositionHandler(pos, [0, 0]) for _ in range(n_layers)]
        
        self.window.add_bg(
            self.page_res,
            pos_hdlrs,
            True,
            False
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
        
        pb = self.page.Objects.PlayButton
        bpos_hdlr = StaticPositionHandler(pb.pos)
        self.window.add_button(pb.res, bpos_hdlr, pb.action)
        
        ob = self.page.Objects.OptionsButton
        opos_hdlr = StaticPositionHandler(ob.pos)
        self.window.add_button(ob.res, opos_hdlr, ob.action)   
        
        qb = self.page.Objects.QuitButton
        qpos_hdlr = StaticPositionHandler(qb.pos)
        self.window.add_button(qb.res, qpos_hdlr, qb.action)        
        
        actionmanager = MenuActionManager(self.window.button_group, start_game_callback, self.quit_game)
        self.window.set_menu_action_manager(actionmanager)
            
    def reverse_trajectory(self, t):
        if int(t.target[0]) == 0:
            for p in self.pos_hdlrs:
                p.add_trajectory((-2300, 0), 1500, 400, 400)
        else:
            for p in self.pos_hdlrs:
                p.add_trajectory((0, 0), 1500, 400, 400)            
    
    @staticmethod
    def dump_save():
        Save.dump('data/save.data')    
    
    def quit_game(self):
        self.window.stop_loop()
    
    def quit(self):
        self.dump_save()


class Game:
    def __init__(self, window, model, return_to_main_menu):
        self.window = window
        self.model = model
        self.state = 'in_game'
        
        pygame.mouse.set_visible(False)
        
        Save.load('data/save.data')
        
        self.level = getattr(self.model.Game, self.model.Game.maps[self.model.Game.current_map_id.get()])
        self.level_res = self.level.res      
         
        self.space = GameSpace(self.level.ground_height, self.level.ground_length)
        
        dynamic = self.level.dynamic_layers
        n_layers = self.window.get_number_of_layers(self.level_res)
        pos = self.level.bg_pos
        if not dynamic:
            position_handler = StaticPositionHandler(pos)
            pos_hdlrs = (position_handler for _ in range(n_layers))
        else:
            pos_hdlrs = [BgLayerPositionHandler(pos, self.window.screen_dec) for _ in range(n_layers)]
        
                
        self.window.add_bg(
            self.level_res,
            pos_hdlrs,
            dynamic,
            self.level.animated_layers
        )
        
        pos2 = pos[0] + self.window.get_length(self.level_res) * 2, pos[1]
        ph = BgLayerPositionHandler(pos2, self.window.screen_dec)
        pos_hdlrs.append(ph)
        self.window.add_bg_layer(self.level_res, 4, ph, foreground=True)
        
        self.entities = dict()
        
        self.triggers = [None] * len(self.level.Triggers.triggers)
        self.ag = GameActionGetter(self.triggers, self.window, pos_hdlrs, self.entities)
        for trig_name in self.level.Triggers.triggers:
            trigdata = getattr(self.level.Triggers, trig_name)
            self.triggers[trigdata.id_] = Trigger(trigdata, self.ag)          
        
        self.space.add_humanoid_entity(
            self.level.Objects.Player.height,
            self.level.Objects.Player.width,
            (self.level.Objects.Player.pos_x.get(), self.level.Objects.Player.pos_y.get()),
            self.level.Objects.Player.name)
        
        action_manager = GameActionManager(None, return_to_main_menu, self.save_position)
        
        name = self.level.Objects.Player.name
        self.player = self.window.add_entity(
            self.level.Objects.Player.res,
            PlayerPositionHandler(self.space.entities[name][0], self.triggers),
            PhysicsUpdater(self.space.entities[name][0], action_manager.land),
            ParticleHandler(self.window.spawn_particle),
            action_manager.set_state)
        
        self.entities[self.level.Objects.Player.name] = self.player
        
        self.window.set_game_event_manager(action_manager, {
            K_d: GameActionManager.WALK_RIGHT,
            K_a: GameActionManager.WALK_LEFT,
            K_LSHIFT: GameActionManager.RUN,
            K_w: GameActionManager.DASH,
            K_SPACE: GameActionManager.JUMP,
            K_F1: GameActionManager.SAVE,
            K_TAB: GameActionManager.RETURN_TO_MAIN_MENU,
            (0, 1): GameActionManager.WALK_RIGHT,
            (0, -1): GameActionManager.WALK_LEFT,
            0: GameActionManager.JUMP,
            1: GameActionManager.DASH,
            7: GameActionManager.RETURN_TO_MAIN_MENU,
            5: GameActionManager.RUN
        })
        action_manager.player = self.player
        
        
        self.window.on_draw = self.update
        self.window.quit = self.dump_save
    
    @staticmethod
    def dump_save():
        Save.dump('data/save.data')
    
    def save_position(self):
        self.level.Objects.Player.pos_x.set(round(self.player.position_handler.body.position.x))
        self.level.Objects.Player.pos_y.set(round(self.player.position_handler.body.position.y))
    
    def quit(self):
        self.save_position()
        self.dump_save()
    
    def update(self, dt):
        self.update_space(dt)
    
    def update_space(self, dt):
        n = round(dt * 60 * 4)
        for i in range(n):
            self.space.step(1/60/4)


