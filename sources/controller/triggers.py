# -*- coding:Utf-8 -*-


class Trigger:
    def __init__(self, data, action_getter):
        self.top = data.top
        self.bottom = data.bottom
        self.right = data.right
        self.left = data.left
        self.enabled = data.enabled
        
        self.actions = []
        for action_name in data.Actions.actions:
            action_data = getattr(data.Actions, action_name)
            action = action_getter(action_data.typ, action_data.kwargs)
            self.actions.append(action)
    
    
    def update(self, x, y):
        if self.enabled:
            if self.collide(x, y):
                for action in self.actions:
                    action()
    
    
    def collide(self, x, y):
        if self.top is not None:
            if y > self.top:
                return False
        if self.bottom is not None:
            if y < self.bottom:
                return False
        if self.right is not None:
            if x > self.right:
                return False
        if self.left is not None:
            if x < self.left:
                return False
        return True
