# -*- coding:Utf-8 -*-

import pygame
pygame.init()

class Sprite(pygame.sprite.Sprite):
    def __init__(self, image_handler, position_handler):
        
        self.image_handler = image_handler
        self.position_handler = position_handler
        
        self.image = image_handler.update_image(self)
        self.rect = self.image.get_rect()
    
    def update(self):
        pass
    
class DynamicSprite(Sprite):
    def update(self):
        super().update()
        self.rect.x, self.rect.y = self.position_handler.update_position(self)

class AnimatedSprite(Sprite):   
    def update(self):
        super().update()
        self.image = self.image_handler.update_image(self)

class AnimatedDynamicSprite(DynamicSprite, AnimatedSprite):
    def update(self):
        super().update()

class BgLayer(Sprite):
    def __init__(self, image_handler, position_handler, layer):
        super().__init__(image_handler, position_handler)
        self.layer = layer

class ABgLayer(AnimatedSprite, BgLayer):
    pass

class DBgLayer(DynamicSprite, BgLayer):
    pass

class ADBgLayer(AnimatedDynamicSprite, BgLayer):
    pass
