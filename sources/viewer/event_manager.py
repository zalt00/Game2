# -*- coding:Utf-8 -*-


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
