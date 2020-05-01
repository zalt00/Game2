# -*- coding:Utf-8 -*-


class Event:
    _i = 0

    def __init__(self):
        self.i = self.new_identifier()
        self.activated = False

    def activate(self):
        self.activated = True

    def deactivate(self):
        self.activated = False

    def __xor__(self, other):
        return self.activated ^ other.activated

    def __or__(self, other):
        return self.activated | other.activated

    def __and__(self, other):
        return self.activated & other.activated

    def __invert__(self):
        return not self

    def __bool__(self):
        return self.activated

    def __repr__(self):
        return 'Event(i={}, {}{})'.format(self.i, self.activated * 'activated', (not self.activated) * 'deactivated')

    @classmethod
    def new_identifier(cls):
        cls._i += 1
        return cls._i
