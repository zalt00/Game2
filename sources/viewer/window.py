# -*- coding:Utf-8 -*-

import pygame
pygame.init()
from pygame.locals import *
from .event_manager import INACTIVE_EVENT_MANAGER, GameEventManager
from .sprites import BgLayer, ABgLayer, DBgLayer, ADBgLayer, Entity
from .image_handler import BgLayerImageHandler, EntityImageHandler
from .resources_loader import ResourceLoader

class Window:
    def __init__(self, width, height, flags=0):
        self.screen = pygame.display.set_mode((width, height), flags)
        self.screen_rect = self.screen.get_rect()
        
        # LOOP
        self.loop_running = False
        
        # CLOCK
        self.fps = 20
        self.clock = pygame.time.Clock()
        
        # EVENTS
        self.event_manager = INACTIVE_EVENT_MANAGER
        
        # RESOURCES
        self.res_loader = ResourceLoader('resources')
        
        # SPRITES
        self.global_group = pygame.sprite.Group()
        self.bg_group = pygame.sprite.LayeredUpdates()
        self.fg_group = pygame.sprite.LayeredUpdates()
        self.entity_group = pygame.sprite.Group()
        
    def run(self):
        """Starts the main loop"""
        self.loop_running = True

        while self.loop_running:
            dt = self.clock.tick(self.fps)
            
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    self.loop_running = False
                self.event_manager.do(event)
            
            self.global_group.update()
            self.bg_group.draw(self.screen)
            self.entity_group.draw(self.screen)
            self.fg_group.draw(self.screen)
            
            pygame.display.set_caption(str(self.clock.get_fps()))
            pygame.display.flip()    
    
    def get_number_of_layers(self, res_name):
        return len(self.res_loader.load(res_name).layers)
    
    def add_bg(self, res_name, position_handlers, all_dynamic=True, all_animated=False):
        res = self.res_loader.load(res_name)
        for i, pos_hdlr in enumerate(position_handlers):
            self.add_bg_layer(res, i, pos_hdlr, all_dynamic, all_animated)
        
        for i in range(res.foreground):
            ts = self.bg_group.get_top_sprite()
            self.bg_group.remove(ts)
            self.fg_group.add(ts)
            self.fg_group.move_to_back(ts)
            
    def add_bg_layer(self, res, layer_id, position_handler, dynamic=True, animated=False):
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
        self.bg_group.add(sprite)

    def add_entity(self, res_name, position_handler):
        res = self.res_loader.load(res_name)
        img_hdlr = EntityImageHandler(res, lambda _: None)
        entity = Entity(img_hdlr, position_handler)
        self.global_group.add(entity)
        self.entity_group.add(entity)

    def set_game_event_manager(self, am, ctrls):
        self.event_manager = GameEventManager(am, ctrls)
