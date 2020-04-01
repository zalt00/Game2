# -*- coding:Utf-8 -*-


class Trigger:
    top = None
    left = None
    bottom = None
    right = None
    enabled = False


class DataContainer:
    @classmethod
    def get(cls, s):
        return getattr(cls, s)
