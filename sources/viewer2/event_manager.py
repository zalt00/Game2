# -*- coding:Utf-8 -*-

import pyglet


class BaseEventManager:
    def __init__(self, *args, **kwargs):
        self.handlers = {}
    
    def do(self, *args, **kwargs):
        pass


INACTIVE_EVENT_MANAGER = BaseEventManager()


class EventManager(BaseEventManager):
    
    def __init__(self, action_manager):
        super(EventManager, self).__init__()
        self.action_manager = action_manager

    def do(self, event_type, *args, **kwargs):
        f = self.handlers.get(event_type, None)
        if f is not None:
            f(*args, **kwargs)


class GameEventManager(EventManager):
    def __init__(self, action_manager, controls, deadzones):
        super().__init__(action_manager)
        self.controls = controls
        self.deadzones = deadzones

        self.handlers = dict(
            on_key_press=self.keydown,
            on_key_release=self.keyup
        )

    def joyhatmotion(self, event):
        if event.value[0] == 0:
            action1 = self.controls.get((11, 1), None)
            if action1 is not None:
                self.action_manager.stop(action1)
            action1 = self.controls.get((11, -1), None)
            if action1 is not None:
                self.action_manager.stop(action1)
        else:
            action1 = self.controls.get((11, event.value[0]), None)
            if action1 is not None:
                self.action_manager.do(action1)
        
        if event.value[1] == 0:
            action2 = self.controls.get((12, 1), None)
            if action2 is not None:
                self.action_manager.stop(action2)
            action2 = self.controls.get((12, -1), None)
            if action2 is not None:
                self.action_manager.stop(action2)
        else:
            action2 = self.controls.get((12, event.value[1]), None)
            if action2 is not None:
                self.action_manager.do(action2)

    def joybuttondown(self, event):
        action = self.controls.get((10, event.button), None)
        if action is not None:
            self.action_manager.do(action)
    
    def joybuttonup(self, event):
        action = self.controls.get((10, event.button), None)
        if action is not None:
            self.action_manager.stop(action)            
            
    def axis_motion(self, event):
        if abs(event.value) > self.deadzones[event.axis]:
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
    
    def keydown(self, symbol, modifiers):
        print(symbol)
        action = self.controls.get(symbol, None)
        if action is not None:
            self.action_manager.do(action)
        
    def keyup(self, symbol, modifiers):
        action = self.controls.get(symbol, None)
        if action is not None:
            self.action_manager.stop(action)


class DebugGameEventManager(GameEventManager):
    def keydown2(self, event):
        action = self.controls.get(event.key, None)
        if action is not None:
            self.action_manager.do(action)
        elif event.key == K_F1:
            try:
                self.action_manager.do(self.action_manager.ACTIVATE_DEBUG_DRAW)
            except AttributeError:
                pass
        elif event.key == K_F2:
            try:
                self.action_manager.do(self.action_manager.DEACTIVATE_DEBUG_DRAW)
            except AttributeError:
                pass
        elif event.key == K_F3:
            try:
                self.action_manager.do(self.action_manager.MANUALLY_RAISE_ERROR)
            except AttributeError:
                pass


class MenuEventManager(EventManager):
    def __init__(self, action_manager):
        super().__init__(action_manager)
        self.handlers = dict(
            on_mouse_motion=self.mousemotion,
            on_mouse_press=self.click
        )

        self.joyhatpressed = False
        
    def joyhatmotion(self, event):
        if event.value[1] == 1:
            if not self.joyhatpressed:
                self.action_manager.do(self.action_manager.UP)
                self.joyhatpressed = True
        elif event.value[1] == -1:
            if not self.joyhatpressed:
                self.action_manager.do(self.action_manager.DOWN)
                self.joyhatpressed = True
        elif event.value[0] == -1:
            if not self.joyhatpressed:
                self.action_manager.do(self.action_manager.LEFT)
                self.joyhatpressed = True            
        elif event.value[0] == 1:
            if not self.joyhatpressed:            
                self.action_manager.do(self.action_manager.RIGHT)
                self.joyhatpressed = True            
        
        if not any(event.value):
            self.joyhatpressed = False
        
    def joybuttondown(self, event):
        if event.button == 0:
            try:
                self.action_manager.do(self.action_manager.ACTIVATE)
            except AttributeError:
                pass
        elif event.button == 1:
            try:
                self.action_manager.do(self.action_manager.CANCEL)
            except AttributeError:
                pass
        elif event.button == 5:
            try:
                self.action_manager.do(self.action_manager.NEXT)
            except AttributeError:
                pass
        elif event.button == 4:
            try:
                self.action_manager.do(self.action_manager.PREVIOUS)
            except AttributeError:
                pass

    def mousemotion(self, x, y, dx, dy):
        self.action_manager.do(self.action_manager.MOUSEMOTION, (x, y))

    def click(self, x, y, button, modifiers):
        print(button)
        if button == 1:
            self.action_manager.do(self.action_manager.LEFT_CLICK, (x, y))


class ChangeCtrlsEventManager(EventManager):
    def __init__(self, action_manager, con_or_kb):
        super().__init__(action_manager)
        if con_or_kb == "kb":
            self.handlers[KEYDOWN] = self.keydown
        else:
            self.handlers[KEYDOWN] = self.keydown2
            self.handlers[JOYAXISMOTION] = self.axis_motion
            self.handlers[JOYBUTTONDOWN] = self.joybuttondown
            self.handlers[JOYHATMOTION] = self.joyhatmotion
    
    def keydown(self, event):
        self.action_manager.do(self.action_manager.SET_CTRL, event.key)
        
    def keydown2(self, event):
        if event.key == K_ESCAPE:
            self.action_manager.do(self.action_manager.SET_CTRL, (20, 20))
        
    def joyhatmotion(self, event):
        if event.value[0] != 0:
            self.action_manager.do(self.action_manager.SET_CTRL, (11, event.value[0]))
        
        elif event.value[1] != 0:
            self.action_manager.do(self.action_manager.SET_CTRL, (12, event.value[1]))

    def joybuttondown(self, event):
        self.action_manager.do(self.action_manager.SET_CTRL, (10, event.button))
            
    def axis_motion(self, event):
        if abs(event.value) > 0.5:
            if event.value > 0:
                self.action_manager.do(self.action_manager.SET_CTRL, (event.axis, 1))                
            else:
                self.action_manager.do(self.action_manager.SET_CTRL, (event.axis, -1))  
    
    
