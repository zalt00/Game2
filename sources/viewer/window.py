# -*- coding:Utf-8 -*-

import pygame
pygame.init()
from pygame.locals import *
from .event_manager import INACTIVE_EVENT_MANAGER, GameEventManager, MenuEventManager
from .sprites import BgLayer, ABgLayer, DBgLayer, ADBgLayer, Entity, Button, Particle
from .image_handler import BgLayerImageHandler, TBEntityImageHandler, FBEntityImageHandler, ButtonImageHandler
from .resources_loader import ResourceLoader

class Window:
    def __init__(self, width, height, flags=0):
        self.screen = pygame.display.set_mode((width, height), flags)
        self.screen_rect = self.screen.get_rect()
        
        self.current_bg = self.screen.copy()
        self.is_bg_updated = False
        
        # LOOP
        self.loop_running = False
        
        # CLOCK
        self.fps = 130
        self.clock = pygame.time.Clock()
        
        # EVENTS
        self.event_manager = INACTIVE_EVENT_MANAGER
        
        # RESOURCES
        self.res_loader = ResourceLoader('resources')
        
        # SPRITES
        self.global_group = pygame.sprite.Group()
        self.bg_group = pygame.sprite.LayeredUpdates()
        self.fg_group = pygame.sprite.LayeredUpdates()
        self.particle_group = pygame.sprite.Group()
        self.entity_group = pygame.sprite.Group()
        self.button_group = pygame.sprite.OrderedUpdates()
        
        self.screen_dec = [0, 0]
        
        ##
        self.on_draw = lambda _: None
        
    def run(self):
        """Starts the main loop"""
        self.loop_running = True

        while self.loop_running:
            dt = self.clock.tick(self.fps)
            self.on_draw(dt / 1000)

            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    self.stop_loop()
                self.event_manager.do(event)
            
            self.global_group.update()
            self.bg_group.draw(self.screen)
            self.is_bg_updated = False
                
            #self.screen.blit(self.current_bg, (0, 0))
            self.particle_group.draw(self.screen)
            self.entity_group.draw(self.screen)
            self.button_group.draw(self.screen)
            self.fg_group.draw(self.screen)

            pygame.display.set_caption(str(self.clock.get_fps()))
            pygame.display.flip()
        self.quit()
    
    def stop_loop(self):
        self.loop_running = False
    
    def get_number_of_layers(self, res_name):
        return len(self.res_loader.load(res_name).layers)
    
    def get_length(self, res_name):
        return self.res_loader.load(res_name).width
    
    def add_bg(self, res_name, position_handlers, all_dynamic=True, all_animated=False):
        res = self.res_loader.load(res_name)
        for i, pos_hdlr in enumerate(position_handlers):
            self.add_bg_layer(res, i, pos_hdlr, all_dynamic, all_animated)
        
        for i in range(res.foreground):
            ts = self.bg_group.get_top_sprite()
            self.bg_group.remove(ts)
            self.fg_group.add(ts)
            
    def add_bg_layer(self, res, layer_id, position_handler, dynamic=True, animated=False, foreground=False):
        if isinstance(res, str):
            res = self.res_loader.load(res)

        if animated:
            raise NotImplemented
        
        imghdlr = BgLayerImageHandler(res)
        if dynamic:
            sprite = DBgLayer(imghdlr, position_handler, layer_id)
        else:
            sprite = BgLayer(imghdlr, position_handler, layer_id)
        
        self.global_group.add(sprite)
        if foreground:
            self.fg_group.add(sprite)
        else:
            self.bg_group.add(sprite)

    def add_entity(self, res_name, position_handler, physics_updater, particles_handler, end_animation_callback):
        res = self.res_loader.load(res_name)
        img_hdlr = TBEntityImageHandler(res, end_animation_callback)
        entity = Entity(img_hdlr, position_handler, physics_updater, particles_handler, res.dec, self.screen_dec)
        self.global_group.add(entity)
        self.entity_group.add(entity)
        
        return entity
    
    def add_button(self, res_name, position_handler, action_name):
        res = self.res_loader.load(res_name)
        img_handler = ButtonImageHandler(res)
        button = Button(img_handler, position_handler, action_name)
        
        self.global_group.add(button)
        self.button_group.add(button)
        
        return button
        
    def spawn_particle(self, res, position_handler, state, dec, direction):
        img_hdlr = TBEntityImageHandler(res, None)
        particle = Particle(img_hdlr, position_handler, dec, self.screen_dec, state, direction)
        img_hdlr.end_animation_callback = lambda *_, **__: particle.kill()
        
        self.global_group.add(particle)
        self.particle_group.add(particle)
    
    def set_menu_action_manager(self, am):
        self.event_manager = MenuEventManager(am)
    
    def set_game_event_manager(self, am, ctrls):
        self.event_manager = GameEventManager(am, ctrls)
    
    def on_draw(self, *_, **__):
        pass
    
    def quit(self, *_, **__):
        pass
    
    
