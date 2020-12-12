# -*- coding:Utf-8 -*-

from .plugin_base import PluginMeta, AbstractPlugin, command
import pygame
pygame.init()

__plugin_name__ = 'SelectionTransformPlugin'


class SelectionTransformPlugin(AbstractPlugin, metaclass=PluginMeta):
    def flip_selection(self, flip_x, flip_y):
        width = abs(self.app.sepos[0] - self.app.nwpos[0]) + 1
        height = abs(self.app.sepos[1] - self.app.nwpos[1]) + 1
        new_region = [['NA0000'] * width for _ in range(height)]  # access with new_region[y][x]
        for x in range(width):
            for y in range(height):
                tile_identifier = self.app.tab[y + self.app.sepos[1]][x + self.app.sepos[0]]
                if flip_x:
                    x = width - x - 1
                if flip_y:
                    y = height - y - 1

                code, flip_infos, id_ = tile_identifier[:2], tile_identifier[2:4], tile_identifier[4:]
                flip_x_2, flip_y_2 = flip_infos
                if flip_x:
                    flip_x_2 = int(flip_x_2) * -1 + 1
                if flip_y:
                    flip_y_2 = int(flip_y_2) * -1 + 1
                new_flip_infos = f'{flip_x_2}{flip_y_2}'
                new_tile_identifier = code + new_flip_infos + id_

                new_region[y][x] = new_tile_identifier

        for x in range(width):
            for y in range(height):
                self.app.tab[y + self.app.sepos[1]][x + self.app.sepos[0]] = new_region[y][x]

        self.app.rebuild()

    @command('shift-e')
    def flip_horizontally(self):
        self.flip_selection(True, False)

    @command('ctrl-e')
    def flip_vertically(self):
        self.flip_selection(False, True)
