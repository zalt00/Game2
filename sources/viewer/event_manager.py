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
        self.handlers[JOYAXISMOTION] = self.axis_motion
        self.handlers[JOYBUTTONDOWN] = self.joybuttondown
        self.handlers[JOYBUTTONUP] = self.joybuttonup
    
    def joybuttondown(self, event):
        action = self.controls.get((10, event.button), None)
        if action is not None:
            self.action_manager.do(action)
    
    def joybuttonup(self, event):
        action = self.controls.get((10, event.button), None)
        if action is not None:
            self.action_manager.stop(action)            
            
    def axis_motion(self, event):
        if abs(event.value) > 0.3:
            if event.value > 0:
                action = self.controls.get((event.axis, 1), None)
            else:
                action = self.controls.get((event.axis, -1), None)
            if action is not None:
                self.action_manager.do(action)
        else:
            action = self.controls.get((event.axis, 1), None)
            if action is not None:
                self.action_manager.stop(action)
            action = self.controls.get((event.axis, -1), None)
            if action is not None:
                self.action_manager.stop(action)
    
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
        self.handlers[JOYHATMOTION] = self.joyhatmotion
        self.handlers[JOYBUTTONDOWN] = self.joybuttondown
        
    def joyhatmotion(self, event):
        if event.value[1] == 1:
            self.action_manager.do(self.action_manager.UP)
        elif event.value[1] == -1:
            self.action_manager.do(self.action_manager.DOWN)
        elif event.value[0] == -1:
            self.action_manager.do(self.action_manager.LEFT)
        elif event.value[0] == 1:
            self.action_manager.do(self.action_manager.RIGHT)

    def joybuttondown(self, event):
        if event.button == 0:
            self.action_manager.do(self.action_manager.ACTIVATE)
        elif event.button == 5:
            self.action_manager.do(self.action_manager.NEXT)
        elif event.button == 4:
            self.action_manager.do(self.action_manager.PREVIOUS)
            
    def mousemotion(self, event):
        self.action_manager.do(self.action_manager.MOUSEMOTION, event.pos)

    def click(self, event):
        if event.button == 1:
            self.action_manager.do(self.action_manager.RIGHT_CLICK, event.pos)
    
