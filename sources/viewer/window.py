# -*- coding:Utf-8 -*-

import pygame
pygame.init()
from pygame.locals import *
from .event_manager import INACTIVE_EVENT_MANAGER

class Window:
    def __init__(self, width, height, flags=0):
        self.screen = pygame.display.set_mode((width, height), flags)
        self.screen_rect = self.screen.get_rect()
        
        # LOOP
        self.loop_running = False
        
        # CLOCK
        self.fps = 60
        self.clock = pygame.time.Clock()
        
        # EVENTS
        self.event_manager = INACTIVE_EVENT_MANAGER
    
    def run(self):
        """Starts the main loop"""
        self.loop_running = True

        while self.loop_running:
            dt = self.clock.tick(self.fps)
            
            for event in pygame.event.get():
                self.event_manager.do(event)

            pygame.display.set_caption(str(self.clock.get_fps()))
            pygame.display.flip()    

