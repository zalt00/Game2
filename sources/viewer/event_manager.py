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
            on_key_release=self.keyup,
            on_joyaxis_motion=self.axis_motion,
            on_joybutton_press=self.joybuttondown,
            on_joybutton_release=self.joybuttonup,
            on_joyhat_motion=self.joyhatmotion
        )

        self._axis = {'x': 0, 'y': 1, 'z': 2, 'rx': 3, 'ry': 4}

    def joyhatmotion(self, hat_x, hat_y):
        if hat_x == 0:
            action1 = self.controls.get((11, 1), None)
            if action1 is not None:
                self.action_manager.stop(action1)
            action1 = self.controls.get((11, -1), None)
            if action1 is not None:
                self.action_manager.stop(action1)
        else:
            action1 = self.controls.get((11, hat_x), None)
            if action1 is not None:
                self.action_manager.do(action1)
        
        if hat_y == 0:
            action2 = self.controls.get((12, 1), None)
            if action2 is not None:
                self.action_manager.stop(action2)
            action2 = self.controls.get((12, -1), None)
            if action2 is not None:
                self.action_manager.stop(action2)
        else:
            action2 = self.controls.get((12, hat_y), None)
            if action2 is not None:
                self.action_manager.do(action2)

    def joybuttondown(self, button):
        action = self.controls.get((10, button), None)
        if action is not None:
            self.action_manager.do(action)
    
    def joybuttonup(self, button):
        action = self.controls.get((10, button), None)
        if action is not None:
            self.action_manager.stop(action)            
            
    def axis_motion(self, axis, value):
        if abs(value) > self.deadzones[self._axis[axis]]:
            if value > 0:
                action = self.controls.get((self._axis[axis], 1), None)
            else:
                action = self.controls.get((self._axis[axis], -1), None)
            if action is not None:
                self.action_manager.do(action)
        else:
            action = self.controls.get((self._axis[axis], 1), None)
            if action is not None:
                self.action_manager.stop(action)
            action = self.controls.get((self._axis[axis], -1), None)
            if action is not None:
                self.action_manager.stop(action)
    
    def keydown(self, symbol, modifiers):
        action = self.controls.get(symbol, None)
        if action is not None:
            self.action_manager.do(action)
        
    def keyup(self, symbol, modifiers):
        action = self.controls.get(symbol, None)
        if action is not None:
            self.action_manager.stop(action)


class DebugGameEventManager(GameEventManager):
    def keydown(self, symbol, modifier):
        action = self.controls.get(symbol, None)
        if action is not None:
            self.action_manager.do(action)
        elif symbol == pyglet.window.key.F1:
            try:
                self.action_manager.do(self.action_manager.TOGGLE_DEBUG_DRAW)
            except AttributeError:
                pass
        elif symbol == pyglet.window.key.F2:
            try:
                self.action_manager.do(self.action_manager.MANUALLY_RAISE_ERROR)
            except AttributeError:
                pass
        elif symbol == pyglet.window.key.F3:
            try:
                self.action_manager.do(self.action_manager.PAUSE)
            except AttributeError:
                pass
        elif symbol == pyglet.window.key.F4:
            try:
                self.action_manager.do(self.action_manager.RECORD)
            except AttributeError:
                pass
        elif symbol == pyglet.window.key.F12:
            try:
                self.action_manager.do(self.action_manager.DEV_COMMAND)
            except AttributeError:
                pass


class MenuEventManager(EventManager):
    def __init__(self, action_manager):
        super().__init__(action_manager)
        self.handlers = dict(
            on_mouse_motion=self.mousemotion,
            on_mouse_press=self.click,
            on_joyhat_motion=self.joyhatmotion,
            on_joybutton_press=self.joybuttondown
        )

        self.joyhatpressed = False
        
    def joyhatmotion(self, hat_x, hat_y):
        if hat_y == 1:
            if not self.joyhatpressed:
                self.action_manager.do(self.action_manager.UP)
                self.joyhatpressed = True
        elif hat_y == -1:
            if not self.joyhatpressed:
                self.action_manager.do(self.action_manager.DOWN)
                self.joyhatpressed = True
        elif hat_x == -1:
            if not self.joyhatpressed:
                self.action_manager.do(self.action_manager.LEFT)
                self.joyhatpressed = True            
        elif hat_x == 1:
            if not self.joyhatpressed:            
                self.action_manager.do(self.action_manager.RIGHT)
                self.joyhatpressed = True            
        
        if hat_x == hat_y == 0:
            self.joyhatpressed = False
        
    def joybuttondown(self, button):
        if button == 0:
            try:
                self.action_manager.do(self.action_manager.ACTIVATE)
            except AttributeError:
                pass
        elif button == 1:
            try:
                self.action_manager.do(self.action_manager.CANCEL)
            except AttributeError:
                pass
        elif button == 5:
            try:
                self.action_manager.do(self.action_manager.NEXT)
            except AttributeError:
                pass
        elif button == 4:
            try:
                self.action_manager.do(self.action_manager.PREVIOUS)
            except AttributeError:
                pass

    def mousemotion(self, x, y, dx, dy):
        self.action_manager.do(self.action_manager.MOUSEMOTION, (x, y))

    def click(self, x, y, button, modifiers):
        if button == 1:
            self.action_manager.do(self.action_manager.LEFT_CLICK, (x, y))


class ChangeCtrlsEventManager(EventManager):
    def __init__(self, action_manager, con_or_kb):
        super().__init__(action_manager)
        if con_or_kb == "kb":
            self.handlers['on_key_press'] = self.keydown
        else:
            self.handlers['on_key_press'] = self.keydown2
            self.handlers['on_joyaxis_motion'] = self.axis_motion
            self.handlers['on_joybutton_press'] = self.joybuttondown
            self.handlers['on_joyhat_motion'] = self.joyhatmotion

            self._axis = {'x': 0, 'y': 1, 'z': 2, 'rx': 3, 'ry': 4}
    
    def keydown(self, symbol, modifier):
        self.action_manager.do(self.action_manager.SET_CTRL, symbol)
        
    def keydown2(self, symbol, modifier):
        if symbol == pyglet.window.key.ESCAPE:
            self.action_manager.do(self.action_manager.SET_CTRL, (20, 20))
        
    def joyhatmotion(self, hat_x, hat_y):
        if hat_x:
            self.action_manager.do(self.action_manager.SET_CTRL, (11, hat_x))
        
        elif hat_y != 0:
            self.action_manager.do(self.action_manager.SET_CTRL, (12, hat_y))

    def joybuttondown(self, button):
        self.action_manager.do(self.action_manager.SET_CTRL, (10, button))
            
    def axis_motion(self, axis, value):
        if abs(value) > 0.5:
            if value > 0:
                self.action_manager.do(self.action_manager.SET_CTRL, (self._axis[axis], 1))
            else:
                self.action_manager.do(self.action_manager.SET_CTRL, (self._axis[axis], -1))
