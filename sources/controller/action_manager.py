# -*- coding:Utf-8 -*-


class ActionManager:
    def __init__(self):
        self.do_handlers = {}
        self.stop_handlers = {}
    
    def do(self, action):
        try:
            self.do_handlers[action]()
        except KeyError:
            pass
        
    def stop(self, action):
        try:
            self.stop_handlers[action]()
        except KeyError:
            pass

