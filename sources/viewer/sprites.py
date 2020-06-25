# -*- coding:Utf-8 -*-

from pymunk import Vec2d
import pygame
from pygame.locals import SRCALPHA
pygame.init()


class Sprite(pygame.sprite.Sprite):
    def __init__(self, image_handler, position_handler, dec=(0, 0), screen_dec=[0, 0], layer=0):
        super().__init__()

        self._layer = layer

        self.screen_dec = screen_dec
        self.image_handler = image_handler
        self.position_handler = position_handler
        
        self.image = image_handler.update_image(self)
        self.rect = self.image.get_rect()
        self.raw_dec = dec
        self.dec = (0 - dec[0], 800 - self.rect.height + dec[1])

        self.rect.x, self.rect.y = position_handler.update_position(self)

    def update(self, n=1):
        pass


class DynamicSprite(Sprite):
    def update(self, n=1):
        super().update(n)
        self.rect.x, self.rect.y = self.position_handler.update_position(self, n)


class AnimatedSprite(Sprite):   
    def update(self, n=1):
        super().update(n)
        self.image = self.image_handler.update_image(self, n)


class AnimatedDynamicSprite(DynamicSprite, AnimatedSprite):
    def update(self, n=1):
        super().update(n)


# BG
class BgLayer(Sprite):
    def __init__(self, image_handler, position_handler, layer):
        super().__init__(image_handler, position_handler, layer=layer)

    def get_layer(self):
        return self._layer


class DBgLayer(BgLayer):
    def __init__(self, image_handler, position_handler, layer):
        super(DBgLayer, self).__init__(image_handler, position_handler, layer)
        self.bi_rect = self.image.get_rect()
        self.bi_rect.width *= 2
        self.base_image = pygame.Surface((self.bi_rect.width, self.bi_rect.height), SRCALPHA)
        self.base_image.blit(self.image, (0, 0))
        self.width = self.bi_rect.width // 2
        self.base_image.blit(self.image, (self.width, 0))
        self.subsurface_rect = self.image.get_rect()

    def update(self, n=1):
        x, y = self.position_handler.update_position(self, n)
        self.rect.y = y
        x %= self.width
        self.subsurface_rect.x = self.width - x
        self.image = self.base_image.subsurface(self.subsurface_rect)


# ENTITY
class Entity(AnimatedDynamicSprite):
    def __init__(self, image_handler, position_handler, physics_updater, particles_handler, dec, screen_dec, layer=0):
        self.state = 'idle'
        self.secondary_state = ''
        self.air_control = 0
        self.can_air_control = True
        self.direction = 1
        self.thrust = Vec2d(0, 0)
        self.is_on_ground = False
        self.physics_updater = physics_updater
        self.particles_handler = particles_handler
        super().__init__(image_handler, position_handler, dec, screen_dec, layer=layer)
    
    def update(self, n=1):
        self.particles_handler.update(self)
        self.physics_updater.update(self, n)
        super().update(n)


class Particle(AnimatedSprite):
    def __init__(self, image_handler, position_handler, dec, screen_dec, state, direction):
        self.state = state
        self.direction = direction
        super().__init__(image_handler, position_handler, dec, screen_dec)
        
    def kill(self, *_, **__):
        super(Particle, self).kill()
        
    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)


class Structure(AnimatedDynamicSprite):
    def __init__(self, image_handler, position_handler, dec, screen_dec, state, layer=0):
        self.state = state
        super().__init__(image_handler, position_handler, dec, screen_dec, layer=layer)


class Text(AnimatedDynamicSprite):
    def __init__(self, image_handler, position_handler, dec):
        super(Text, self).__init__(image_handler, position_handler, dec, [0, 0])

        
class Button(AnimatedDynamicSprite):
    def __init__(self, image_handler, position_handler, action_name):
        self.state = 'idle'
        self.action = action_name
        super().__init__(image_handler, position_handler)

