# -*- coding:Utf-8 -*-


import bisect
from .triggers import Trigger
from utils.logger import logger


class TriggerMapping:
    def __init__(self, tile_width):

        self.tile_width = tile_width

        self.tiles = [PlanTile(0, self.tile_width)]
        self.triggers_in_all_new_right_tiles = set()

        self._triggers = dict()

        self._invalid_position = False

    def __getitem__(self, trigger_id):
        assert isinstance(trigger_id, int)

        return self._triggers[trigger_id]

    def __setitem__(self, trigger_id, trigger):
        assert isinstance(trigger_id, int)
        assert isinstance(trigger, Trigger)

        assert trigger_id not in self._triggers

        if trigger.right is None:
            if trigger.left is not None:
                while trigger.left > self.tiles[-1].x2:
                    self.create_new_tile()
            self.triggers_in_all_new_right_tiles.add(trigger_id)

        else:
            while trigger.right > self.tiles[-1].x2:
                self.create_new_tile()

        left = trigger.left
        if left is None:
            left = -self.tile_width
        right = trigger.right
        if right is None:
            right = self.tiles[-1].x2 - 1

        i1 = self.get_tile_index(left)
        i2 = self.get_tile_index(right)
        for tile in self.tiles[i1:i2 + 1]:
            tile.add(trigger_id)

        self._triggers[trigger_id] = trigger

    def update(self, x, y):
        if x <= -self.tile_width:
            if not self._invalid_position:
                self._invalid_position = True
                logger.warning('invalid position')
        else:
            self._invalid_position = False
            tile_id = self.get_tile_index(x)
            if tile_id >= len(self.tiles):
                triggers = self.triggers_in_all_new_right_tiles
            else:
                triggers = self.tiles[tile_id].triggers

            for trigger_id in triggers:
                self._triggers[trigger_id].update(x, y)

    def create_new_tile(self):
        x = self.tiles[-1].x2
        self.tiles.append(PlanTile(self.get_tile_index(x),
                                   self.tile_width, triggers=self.triggers_in_all_new_right_tiles))

    def get_tile_index(self, x):
        return int(x // self.tile_width + 1)


class PlanTile:
    def __init__(self, tile_id, tile_width, triggers=()):
        self.x1 = (tile_id - 1) * tile_width
        self.x2 = self.x1 + tile_width

        self.triggers = set()
        self.triggers.update(triggers)

    def __contains__(self, x):
        if not isinstance(x, (int, float)):
            return NotImplemented
        return self.x1 <= x < self.x2

    def add(self, id_):
        self.triggers.add(id_)



