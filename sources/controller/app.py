# -*- coding:Utf-8 -*-

from .position_handler import StaticPositionHandler, DynamicPositionHandler
from .action_manager import GameActionManager, MenuActionManager
from .physics_updater import PhysicsUpdater
from pygame.locals import *
import pygame.mouse
from .space import GameSpace
import pymunk.pygame_util
from utils.save_modifier import Save


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
        
        pos_hdlrs = (position_handler for _ in range(n_layers))
        
        self.window.add_bg(
            self.page_res,
            pos_hdlrs,
            False,
            False
        )
        
        pb = self.page.Objects.PlayButton
        bpos_hdlr = StaticPositionHandler(pb.pos)
        self.window.add_button(pb.res, bpos_hdlr, pb.action)
        
        qb = self.page.Objects.QuitButton
        qpos_hdlr = StaticPositionHandler(qb.pos)
        self.window.add_button(qb.res, qpos_hdlr, qb.action)
        
        ob = self.page.Objects.OptionsButton
        opos_hdlr = StaticPositionHandler(ob.pos)
        self.window.add_button(ob.res, opos_hdlr, ob.action)             
        
        actionmanager = MenuActionManager(self.window.button_group, start_game_callback, self.quit_game)
        self.window.set_menu_action_manager(actionmanager)
        
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
        if not dynamic:
            pos = self.level.bg_pos
            position_handler = StaticPositionHandler(pos)
        
        pos_hdlrs = (position_handler for _ in range(n_layers))
        
        self.window.add_bg(
            self.level_res,
            pos_hdlrs,
            dynamic,
            self.level.animated_layers
        )
        
        self.space.add_humanoid_entity(
            self.level.Objects.Player.height,
            self.level.Objects.Player.width,
            (self.level.Objects.Player.pos_x.get(), self.level.Objects.Player.pos_y.get()),
            self.level.Objects.Player.name)
        
        action_manager = GameActionManager(None, return_to_main_menu, self.save_position)
        
        name = self.level.Objects.Player.name
        self.player = self.window.add_entity(
            self.level.Objects.Player.res,
            DynamicPositionHandler(self.space.entities[name][0]),
            PhysicsUpdater(self.space.entities[name][0], action_manager.land),
            action_manager.set_state)
                
        self.window.set_game_event_manager(action_manager, {
            K_d: GameActionManager.WALK_RIGHT,
            K_a: GameActionManager.WALK_LEFT,
            K_LSHIFT: GameActionManager.RUN,
            K_o: GameActionManager.GESTURE,
            K_SPACE: GameActionManager.JUMP,
            K_F1: GameActionManager.SAVE,
            K_TAB: GameActionManager.RETURN_TO_MAIN_MENU
        })
        action_manager.player = self.player
        
        self.window.on_draw = self.update_space
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
    
    def update_space(self, dt):
        n = round(dt * 60 * 4)
        for i in range(n):
            self.space.step(1/60/4)


