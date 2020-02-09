# -*- coding:Utf-8 -*-

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
    
