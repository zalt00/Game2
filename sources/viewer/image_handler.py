# -*- coding:Utf-8 -*-

import pygame
pygame.init()


class ImageHandler:
    def __init__(self, res):
        self.res = res
        
    def update_image(self, _):
        raise NotImplementedError

class BgLayerImageHandler(ImageHandler):
    def update_image(self, sprite):
        return pygame.transform.scale2x(self.res.layers[sprite.layer])

class EntityImageHandler(ImageHandler):
    def __init__(self, res, end_animation_callback):
        super().__init__(res)
        self.end_animation_callback = end_animation_callback
        self.advance = 0
        self.previous_state = 'idle'
        
    def update_image(self, entity):
        if entity.state != self.previous_state:
            self.previous_state = entity.state
            self.advance = 0
        
        sheet = self.res.sheets[entity.state]
        if self.advance * self.res.width == sheet.get_width():
            self.advance = 0
            self.end_animation_callback(entity.state)
        rect = pygame.Rect(self.advance * self.res.width, 0, self.res.width, self.res.height)
        self.advance += 1
        return pygame.transform.scale2x(sheet.subsurface(rect))
    

