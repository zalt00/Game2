# -*- coding:Utf-8 -*-


import pygame
from pygame.locals import *
pygame.init()


class Tileset:
    def __init__(self, img, size, eraser, random_icon, tw, th, code):
        self.tw = tw
        self.th = th
        self.base_img = img
        self.size = size
        self.eraser = eraser
        self.random_icon = random_icon
        self.code = code

        self.tile_size = self.tw, self.th

        r = self.base_img.get_rect()
        r.width += tw * 2

        new_img = pygame.Surface((r.width, r.height), SRCALPHA)
        new_img.blit(self.base_img, (0, 0))
        new_img.blit(self.eraser, (size * tw, 0))
        new_img.blit(self.random_icon, ((size + 1) * tw, 0))

        self.img = new_img

        self.tile_data = []
        for i in range(size):
            self.tile_data.append(code + '{}{}' + '{:0>2}'.format(i))
        self.tile_data.append('NA0000')
        self.tile_data.append(code + '{}{}' + 'RD')

        self.index_random = len(self.tile_data) - 1
