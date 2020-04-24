# -*- coding:Utf-8 -*-

from pymunk import Vec2d
import pygame
pygame.init()


class Sprite(pygame.sprite.Sprite):
    def __init__(self, image_handler, position_handler, dec=(0, 0), screen_dec=[0, 0]):
        super().__init__()
        
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
    def __init__(self, image_handler, position_handler, physics_updater, particles_handler, dec, screen_dec):
        self.state = 'idle'
        self.secondary_state = ''
        self.air_control = 0
        self.direction = 1
        self.thrust = Vec2d(0, 0)
        self.is_on_ground = False
        self.physics_updater = physics_updater
        self.particles_handler = particles_handler
        super().__init__(image_handler, position_handler, dec, screen_dec)
    
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
    def __init__(self, image_handler, position_handler, dec, screen_dec, state):
        self.state = state
        super().__init__(image_handler, position_handler, dec, screen_dec)


class Text(AnimatedDynamicSprite):
    def __init__(self, image_handler, position_handler, dec):
        super(Text, self).__init__(image_handler, position_handler, dec, [0, 0])

        
class Button(AnimatedDynamicSprite):
    def __init__(self, image_handler, position_handler, action_name):
        self.state = 'idle'
        self.action = action_name
        super().__init__(image_handler, position_handler)

