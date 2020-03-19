# -*- coding:Utf-8 -*-

from dataclasses import dataclass
from typing import Any


class ActionGetter:
    def __call__(self, action_type, kwargs):
        return getattr(self, action_type)(ag=self, **kwargs)

class GameActionGetter(ActionGetter):
    def __init__(self, triggers, window, pos_handlers, entities):
        self.triggers = triggers
        self.window = window
        self.pos_hdlrs = pos_handlers
        self.entities = entities
        
    @dataclass
    class AbsoluteMovecam:
        ag: Any
        x: int
        y: int
        total_duration: int
        fade_in: int
        fade_out: int
        def __call__(self):
            for p in self.ag.pos_hdlrs:
                p.add_trajectory((self.x, self.y), self.total_duration, self.fade_in, self.fade_out)
    
    @dataclass
    class EnableTrigger:
        ag: Any
        target: int
        def __call__(self):
            try:
                self.ag.triggers[self.target].enabled = True
            except IndexError:
                pass
    
    @dataclass
    class DisableTrigger:
        ag: Any
        target: int
        def __call__(self):
            try:
                self.ag.triggers[self.target].enabled = False
            except IndexError:
                pass
    
    @dataclass
    class TPEntity:
        ag: Any
        entity_name: str
        npos: int
        def __call__(self):
            try:
                entity = self.ag.entities[self.entity_name]
            except KeyError:
                pass
            else:
                entity.position_handler.body.position = self.npos
                entity.position_handler.body.velocity = (0, 0)
        

