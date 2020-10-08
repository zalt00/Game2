# -*- coding:Utf-8 -*-


class Trigger:
    top = None
    left = None
    bottom = None
    right = None
    enabled = False


class DefaultObject:
    pass


_default_object = DefaultObject()


class DataContainer:
    @classmethod
    def get(cls, s, default=_default_object):
        if default is not _default_object:
            return getattr(cls, s, default)
        return getattr(cls, s)
