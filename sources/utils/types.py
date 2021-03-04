# -*- coding:Utf-8 -*-


import dataclasses
import typing
from .save_modifier import SaveComponent


class DefaultObject:
    pass


_default_object = DefaultObject()


class MetaDataContainer(type):
    def __getitem__(cls, item):
        return cls.get(item)

    def get(cls, s, default=_default_object):
        if default is not _default_object:
            return getattr(cls, s, default)
        return getattr(cls, s)


class DataContainer(metaclass=MetaDataContainer):
    pass


@dataclasses.dataclass
class GameEvent:
    name: str
    id_: int
    save: SaveComponent
    bool_id: int

    def is_enabled(self, current_save_id):
        return self.save.get_single_boolean(self.bool_id, current_save_id)
    get = is_enabled

    def set_enabled(self, enabled, current_save_id):
        self.save.set_single_boolean(bool(enabled), self.bool_id, current_save_id)
    set = set_enabled

