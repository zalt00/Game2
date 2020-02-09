# -*- coding:Utf-8 -*-

import pygame
import os
from glob import iglob
import configparser
from dataclasses import dataclass
from typing import Any

pygame.init()

class ResourceLoader:
    def __init__(self, resources_directory):
        self.dir_ = resources_directory
        self.cache = {}
        
    def load(self, name):
        """loads a resource from disk and cache it, or loads it from cache
        :param name: name of the resource, with or without .res extension
        :type name: str
        :return: Any"""
        
        raw_name = name.replace('.res', '')
        
        try:
            return self.cache[raw_name]
        except KeyError:
            pass
        
        suffix = '\\' if name.endswith('.res') else '.res\\'
        local_dir = os.path.normpath(self.dir_ + '\\' + name + suffix)
        cfg = configparser.ConfigParser()
        cfg.read(os.path.join(local_dir, 'data.ini'))
                
        if cfg['general'].getint('type') == 0:
            res = self._load_bg(local_dir, cfg)
        else:
            res = self._load_entity(local_dir, cfg)
        self.cache[raw_name] = res
        return res
    
    @staticmethod
    def _load_bg(directory, cfg):
        layers = []
        for layer_path in iglob(os.path.join(directory, '*.png').replace('\\', '/')):
            layers.append(pygame.image.load(layer_path).convert())
            
        return Background(layers, cfg['dimensions'].getint('width'), cfg['dimensions'].getint('height'))
    
    @staticmethod
    def _load_entity(directory, cfg):
        sheets = {}
        for sheet_path in iglob(os.path.join(directory, '*.png').replace('\\', '/')):
            name = os.path.basename(sheet_path)[:-4]
            sheets[name] = pygame.image.load(sheet_path).convert()
            
        return Entity(sheets, cfg['dimensions'].getint('width'), cfg['dimensions'].getint('height'))
    
    def clear_cache(self):
        self.cache = {}

@dataclass
class Background:
    layers: list
    width: int
    height: int


@dataclass
class Entity:
    sheets: dict
    width: int
    height: int

