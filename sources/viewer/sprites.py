# -*- coding:Utf-8 -*-

from pymunk import Vec2d
import pygame
pygame.init()

class Sprite(pygame.sprite.Sprite):
    def __init__(self, image_handler, position_handler, dec=(0, 0)):
        super().__init__()
        
        self.image_handler = image_handler
        self.position_handler = position_handler
        
        self.image = image_handler.update_image(self)
        self.rect = self.image.get_rect()
        self.dec = (0 - dec[0], 800 - self.rect.height + dec[1])
        
        self.rect.x, self.rect.y = position_handler.update_position(self)
        
        
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


# BG
class BgLayer(Sprite):
    def __init__(self, image_handler, position_handler, layer):
        self.layer = layer
        super().__init__(image_handler, position_handler)

class ABgLayer(AnimatedSprite, BgLayer):
    pass

class DBgLayer(DynamicSprite, BgLayer):
    pass

class ADBgLayer(AnimatedDynamicSprite, BgLayer):
    pass


# ENTITY
class Entity(AnimatedDynamicSprite):
    def __init__(self, image_handler, position_handler, physics_updater, dec):
        self.state = 'idle'
        self.secondary_state = ''
        self.air_control = 0
        self.direction = 1
        self.thrust = Vec2d(0, 0)
        self.is_on_ground = False
        self.physics_updater = physics_updater
        super().__init__(image_handler, position_handler, dec)
    
    def update(self):
        self.physics_updater.update(self)
        super().update()


class Button(AnimatedSprite):
    def __init__(self, image_handler, position_handler, action_name):
        self.state = 'idle'
        self.action = action_name
        super().__init__(image_handler, position_handler)
