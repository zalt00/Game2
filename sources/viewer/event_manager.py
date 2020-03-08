# -*- coding:Utf-8 -*-

import pygame
pygame.init()
from pygame.locals import *

class BaseEventManager:
    def __init__(self, *args, **kwargs):
        pass
    
    def do(self, *args, **kwargs):
        pass

INACTIVE_EVENT_MANAGER = BaseEventManager()

class EventManager(BaseEventManager):
    
    def __init__(self, action_manager):
        self.action_manager = action_manager
        self.handlers = {}
        
    def do(self, event):
        f = self.handlers.get(event.type, None)
        if f is not None:
            f(event)

class GameEventManager(EventManager):
    def __init__(self, action_manager, controls):
        super().__init__(action_manager)
        self.controls = controls
        self.handlers[KEYDOWN] = self.keydown
        self.handlers[KEYUP] = self.keyup
        
    def keydown(self, event): 
        action = self.controls.get(event.key, None)
        if action is not None:
            self.action_manager.do(action)
        
    def keyup(self, event):
        action = self.controls.get(event.key, None)
        if action is not None:
            self.action_manager.stop(action)


class MenuEventManager(EventManager):
    def __init__(self, action_manager):
        super().__init__(action_manager)
        self.handlers[MOUSEMOTION] = self.mousemotion
        self.handlers[MOUSEBUTTONDOWN] = self.click
        
    def mousemotion(self, event):
        self.action_manager.do(self.action_manager.MOUSEMOTION, event.pos)

    def click(self, event):
        if event.button == 1:
            self.action_manager.do(self.action_manager.RIGHT_CLICK, event.pos)
    
