# -*- coding:Utf-8 -*-


class ActionManager:
    def __init__(self):
        self.do_handlers = {}
        self.stop_handlers = {}
    
    def do(self, action, *args, **kwargs):
        try:
            self.do_handlers[action](*args, **kwargs)
        except KeyError:
            pass
        
    def stop(self, action, *args, **kwargs):
        try:
            self.stop_handlers[action](*args, **kwargs)
        except KeyError:
            pass

