# -*- coding:Utf-8 -*-

import pygame
import os
from glob import glob
import configparser
from dataclasses import dataclass
import json
import time
from typing import Any
from pygame.locals import SRCALPHA
from utils.logger import logger
from random import randint, shuffle

pygame.init()


class ResourcesLoader:
    def __init__(self, resources_directory):
        self.dir_ = resources_directory
        self.cache = {}

    def load(self, res_name):
        """loads a resource from cache or loads it from disk and caches it
        :param res_name: name of the resource, actually the path relative to the resource directory
        :type res_name: str
        :return: Resource object"""

        try:
            return self.cache[res_name]
        except KeyError:
            pass

        local_dir = os.path.normpath(self.dir_ + '\\' + res_name + '\\').replace('\\', '/')
        return self.load_from_path(local_dir, res_name)

    def load_from_path(self, local_dir, res_name=''):
        """loads a resource from disk, directly from the absolute path or the path relative to the launcher
        :param local_dir: path of the resource directory or file
        :type local_dir: str
        :param res_name: name of the resource, automatically detected if not precised
        :type res_name: str
        :return: Resource object"""
        if res_name == '':
            res_name = local_dir.split('/')[-1]

        logger.debug(f'Loads {res_name} from disk')

        res = None
        if res_name.endswith('st'):
            with open(local_dir, 'r', encoding='utf8') as file:
                s = file.read()
            res = Structure(s)  # only resource type which is stored in a single file

        else:
            datafile_path = os.path.join(local_dir, 'data.json').replace('\\', '/')
            with open(datafile_path, encoding='utf8') as datafile:
                data = json.load(datafile, encoding='utf8')

            if res_name.endswith('.stsp'):
                res = StructTSPalette(data, local_dir)
            elif res_name.endswith('.obj'):
                res = Object(data, local_dir)
            elif res_name.endswith('.bg'):
                res = Background(data, local_dir)
            elif res_name.endswith('.ts'):
                res = Tileset(data, local_dir)
            elif res_name.endswith('bgobj'):
                res = BackgroundObjectSet(data, local_dir)

        if res is None:
            raise ValueError('invalid extension')
        self.cache[res_name] = res

        return res

    @staticmethod
    def load_structure_from_string(s):
        """loads a structure from a string buffer"""
        return Structure(s)


class StructTSPalette:
    def __init__(self, data, directory):
        self.data = data
        tilesets_data = self.data['tile sets data']
        self.tilesets_data = tilesets_data
        tw, th = self.data['tile size']
        self.tw, self.th = tw, th
        for k, v in tilesets_data.items():
            filename = v['filename']
            cs = v['calibration_squares']
            path = os.path.join(directory, filename).replace('\\', '/')
            try:
                img = pygame.image.load(path).convert_alpha()
            except pygame.error:
                img = pygame.image.load(path)

            if cs:
                r = img.get_rect()
                r.width -= 2 * tw
                r.x = tw
                img = img.subsurface(r).copy()
            size = img.get_width() // tw
            tilesets_data[k] = img, size

        self.rd_previous = -1

    def parse(self, s):
        """parses a string buffer element and returns an image"""
        key = s[:2]
        flip_x = int(s[2])
        flip_y = int(s[3])
        tile_id = s[4:]
        tileset, size = self.tilesets_data.get(key, (None, None))
        if tile_id == 'RD':
            tile_id = randint(0, size - 1)
            if tile_id == self.rd_previous:
                if tile_id == size - 1:
                    tile_id -= 1
                else:
                    tile_id += 1
            self.rd_previous = tile_id
        elif tile_id == 'PR':
            tile_id = self.rd_previous

        else:
            tile_id = int(tile_id)
            if tile_id >= size:
                raise ValueError(f'invalid tile id for tileset of size {size}: {tile_id}')
        if tileset is None:
            raise ValueError('invalid key: ' + key)
        tw, th = self.data['tile size']
        r = pygame.Rect(tile_id * tw, 0, tw, th)
        return pygame.transform.flip(tileset.subsurface(r), flip_x, flip_y)

    def build(self, res):
        """creates the structure's image with the string buffer and return it"""
        string_buffer = res.string_buffer
        w, h = res.dimensions
        surf = pygame.Surface((w, h), SRCALPHA)
        surf.fill((255, 255, 255, 0))
        tw, th = self.tw, self.th
        for y, line in enumerate(string_buffer.splitlines()):
            if line:
                for x, tile in enumerate(line.split(';')):
                    if not tile.startswith('NA'):
                        tile_img = self.parse(tile)
                        surf.blit(tile_img, (x * tw, y * th))
        if res.scale >= 2 and False:
            surf = pygame.transform.scale2x(surf)
            surf = pygame.transform.scale(surf, (round(w * res.scale), round(h * res.scale)))
        else:
            surf = pygame.transform.scale(surf, (w * res.scale, h * res.scale))

        return surf


class Object:
    def __init__(self, data, directory):
        self.data = data
        self.sheets = {}
        for name, v in self.data['animations'].items():
            fn = v['filename']
            path = os.path.join(directory, fn).replace('\\', '/')
            try:
                img = pygame.image.load(path).convert_alpha()
            except pygame.error:
                img = pygame.image.load(path)

            for i in range(self.data['scale2x']):
                img = pygame.transform.scale2x(img)
            self.sheets[name] = img

        scale = 2 ** self.data['scale2x']
        self.width = self.data['dimensions'][0] * scale
        self.height = self.data['dimensions'][1] * scale
        self.dec = self.data['dec'][0] * scale, self.data['dec'][1] * scale


class Background:
    def __init__(self, data, directory):
        self.data = data
        self.bg = self.data['background']
        self.fg = self.data['foreground']

        self.layers = {}
        scale = self.data['scale']

        for s in ('background', 'foreground'):
            for v in self.data[s]:
                fn = v['filename']
                path = os.path.join(directory, fn).replace('\\', '/')
                try:
                    img = pygame.image.load(path).convert_alpha()
                except pygame.error:
                    img = pygame.image.load(path)
                if scale >= 2:
                    img = pygame.transform.scale2x(img)
                    img = pygame.transform.scale(
                        img, (round(img.get_width() * (scale / 2)), round(img.get_height() * (scale / 2))))
                else:
                    img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
                v['img'] = img
                self.layers[v['layer']] = img

        self.width = self.data['max_dimensions'][0] * scale
        self.height = self.data['max_dimensions'][1] * scale


class Structure:
    def __init__(self, s):

        lines = s.splitlines()

        self.sheets = None
        self.built = False

        try:
            self.dimensions = tuple(map(int, lines[0].split('=')[1].split(' ')))
            self.width, self.height = self.dimensions
            self.dec = list(map(int, lines[1].split('=')[1].split(' ')))

            self.scale = int(lines[2].split('=')[1])
            length = int(lines[3].split('=')[1])
        except IndexError:
            raise ValueError('invalid syntax')
        except ValueError:
            raise ValueError('invalid values')
        else:
            self.dec[0] *= self.scale
            self.dec[1] *= self.scale

        try:
            self.string_buffer = '\n'.join(lines[5:5 + length])
        except IndexError:
            raise ValueError('invalid string buffer length')

    def build(self, sheets):
        self.built = True
        self.sheets = sheets


class Tileset:
    def __init__(self, data, directory):
        path = os.path.join(directory, data['filename']).replace('\\', '/')
        self.img = pygame.image.load(path).convert_alpha()
        self.tile_data = data['tile data']
        self.tile_size = data['tile size']
        self.eraser = data.get("eraser", None)


class BackgroundObjectSet:
    def __init__(self, data, directory):
        scale = data['scale']
        self.scale = scale
        self.max_height = data['max_height']
        for name, odata in data['bg_objects'].items():
            path = os.path.join(directory, odata['filename']).replace('\\', '/')
            img = pygame.image.load(path).convert_alpha()
            if scale >= 2:
                img = pygame.transform.scale2x(img)
                img = pygame.transform.scale(
                    img, (round(img.get_width() * (scale / 2)), round(img.get_height() * (scale / 2))))
            else:
                img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
            odata['img'] = img
            odata.pop('filename')

        self.bg_objects = data['bg_objects']

    def build_bg_decoration_layer(self, sequence, layer_id):
        total_width = sum((self.bg_objects[oname]['size'][0] for oname in sequence))

        surf = pygame.Surface((total_width * self.scale, self.max_height * self.scale), SRCALPHA)
        current_x = 0
        for obj_name in sequence:
            odata = self.bg_objects[obj_name]
            surf.blit(odata['img'], (current_x, 0))
            current_x += odata['size'][0] * self.scale

        res = BgDecorationLayer({layer_id: surf}, total_width * self.scale, self.max_height * self.scale, (0, 0))
        return res


@dataclass
class BgDecorationLayer:
    layers: dict
    width: int
    height: int
    dec: tuple


@dataclass
class OtherObjectsResource:
    sheets: dict
    width: int
    height: int
    dec: tuple