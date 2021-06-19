# -*- coding:Utf-8 -*-


class Trigger:
    def __init__(self, data, action_getter):
        self.top = data.get('top', None)
        self.bottom = data.get('bottom', None)
        self.right = data.get('right', None)
        self.left = data.get('left', None)
        self.enabled = data['enabled']

        self.id = data['id']

        self.actions = []
        for action_data in data['actions']:
            action = action_getter(**action_data)
            self.actions.append(action)

    def is_global(self):
        return self.top is self.bottom is self.right is self.left is None

    def activate(self):
        if self.enabled:
            for action in self.actions:
                action()

    def update(self, x, y):
        if self.enabled:
            if self.collide(x, y):
                for action in self.actions:
                    action()

    def collide(self, x, y):
        return self._collide(x, y)

    def _collide(self, x, y):
        if self.top is not None:
            if y >= self.top:
                return False
        if self.bottom is not None:
            if y <= self.bottom:
                return False
        if self.right is not None:
            if x >= self.right:
                return False
        if self.left is not None:
            if x <= self.left:
                return False
        return True
