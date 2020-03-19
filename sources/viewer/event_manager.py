# -*- coding:Utf-8 -*-

import pygame
pygame.init() 
from pygame.locals import *

pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
for j in joysticks:
    j.init()


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
        action = self.controls.get(event.button, None)
        if action is not None:
            self.action_manager.do(action)
    
    def joybuttonup(self, event):
        action = self.controls.get(event.button, None)
        if action is not None:
            self.action_manager.stop(action)            
            
    def axis_motion(self, event):
        if abs(event.value) > 0.35:
            if event.value > 0:
                action = self.controls.get((event.axis, 1), None)
            else:
                action = self.controls.get((event.axis, -1), None)
            if action is not None:
                self.action_manager.do(action)
        else:
            if event.value > 0:
                action = self.controls.get((event.axis, 1), None)
            else:
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

    def joybuttondown(self, event):
        if event.button == 0:
            self.action_manager.do(self.action_manager.ACTIVATE)
            
    def mousemotion(self, event):
        self.action_manager.do(self.action_manager.MOUSEMOTION, event.pos)

    def click(self, event):
        if event.button == 1:
            self.action_manager.do(self.action_manager.RIGHT_CLICK, event.pos)
    
