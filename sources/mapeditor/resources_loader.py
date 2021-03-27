# -*- coding:Utf-8 -*-

import os
from glob import glob
import configparser
from dataclasses import dataclass
import json
import time
from typing import Any
from utils.logger import logger
from random import randint, shuffle
import numpy as np
from PIL import Image


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

    def load_from_path(self, local_dir, res_name='', return_name=False):
        """loads a resource from disk, directly from the absolute path or the path relative to the launcher

        :param local_dir: path of the resource directory or file
        :type local_dir: str
        :param res_name: name of the resource, automatically detected if not precised
        :type res_name: str
        :return: Resource object or name"""
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
                data = json.load(datafile)

            if res_name.endswith('.stsp'):
                res = StructTSPalette(data, res_name, self.dir_)
            elif res_name.endswith('.obj'):
                res = Object(data, res_name)
            elif res_name.endswith('.bg'):
                res = Background(data, res_name)

        if res is None:
            raise ValueError('invalid extension')
        self.cache[res_name] = res

        if return_name:
            return res_name
        return res

    @staticmethod
    def load_structure_from_string(s):
        """loads a structure from a string buffer"""
        return Structure(s)


class StructTSPalette:
    def __init__(self, data, directory, resources_directory='resources'):
        self.data = data
        tilesets_data = self.data['tile sets data']
        self.tilesets_data = tilesets_data
        tw, th = self.data['tile size']
        self.tw, self.th = tw, th
        for k, v in tilesets_data.items():
            filename = v['filename']
            cs = v['calibration_squares']
            path = os.path.join(directory, filename).replace('\\', '/')
            array = np.array(Image.open(f'{resources_directory}/{path}'))

            if cs:
                width = array.shape[1] - 2 * tw
                x = tw
                array = array[:, x:x + width, :]

            size = array.shape[1] // tw
            tilesets_data[k] = array, size

        self.rd_previous = -1

        self.resources_directory = resources_directory

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

        step_x = flip_x * -2 + 1
        step_y = flip_y * -2 + 1
        output_value = tileset[::step_y, tile_id * tw:(tile_id + 1) * tw, :][:, ::step_x, :]
        return output_value

    def build(self, res, img_format='texture'):
        """creates the structure's image with the string buffer and return it"""
        string_buffer = res.string_buffer
        w, h = res.dimensions
        array = np.zeros((h, w, 4), dtype=np.uint8)
        tw, th = self.tw, self.th
        for y, line in enumerate(string_buffer.splitlines()):
            if line:
                for x, tile in enumerate(line.split(';')):
                    if not tile.startswith('NA'):
                        tile_array = self.parse(tile)
                        array[y * th:(y + 1) * th, x * tw:(x + 1) * tw, :] = tile_array

        if img_format == 'array':
            img = array
        else:
            raise ValueError(f'invalid format: {img_format}')

        return img


class Object:
    def __init__(self, data, directory):
        self.data = data
        self.sheets = {}
        self.flipped_sheets = {}

        self.directory = directory

        scale = 2 ** self.data['scale2x']
        self.width = self.data['dimensions'][0] * scale
        self.height = self.data['dimensions'][1] * scale
        self.dec = self.data['dec'][0], self.data['dec'][1]

        self.scale = scale


class Background:
    def __init__(self, data, directory):
        self.data = data

        self.layers = {}
        scale = self.data['scale']

        self.scale = scale

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

        try:
            self.string_buffer = '\n'.join(lines[5:5 + length])
        except IndexError:
            raise ValueError('invalid string buffer length')

    def build(self, sheets):
        self.built = True
        self.sheets = sheets


@dataclass
class BgDecorationLayer:
    layers: dict
    width: int
    height: int
    dec: tuple
    scale: int = 1


@dataclass
class OtherObjectsResource:
    sheets: dict
    width: int
    height: int
    dec: tuple

