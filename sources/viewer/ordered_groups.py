# -*- coding:Utf-8 -*-


import pyglet


class OrderedGroupList:
    def __init__(self, size):
        assert size > 2
        self._groups = list()
        for i in range(size):
            self._groups.append(pyglet.graphics.OrderedGroup(i))

        self._group_of_player = size // 2

    def get_min_layer(self):
        return -self._group_of_player

    def get_max_layer(self):
        return len(self._groups) - 1 - self._group_of_player

    def get_group(self, layer_id):
        if layer_id < self.get_min_layer():
            raise IndexError(f'layer {layer_id} bellow the minimum layer {self.get_min_layer()}')
        if layer_id > self.get_max_layer():
            raise IndexError(f'layer {layer_id} above the maximum layer {self.get_max_layer()}')

        index = layer_id + self._group_of_player

        return self._groups[index]

    def __getitem__(self, item):
        return self.get_group(item)



