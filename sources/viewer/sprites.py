# -*- coding:Utf-8 -*-

from pymunk import Vec2d
import pyglet


class Sprite(pyglet.sprite.Sprite):
    def __init__(self, image_handler,
                 position_handler, batch, get_group, groups=(), dec=(0, 0), screen_dec=[0, 0], layer=0):
        self._layer = layer

        super().__init__(pyglet.image.Texture.create(0, 0), batch=batch, group=get_group(layer))
        self.group = get_group(layer)

        self.image = image_handler.update_image(self)

        self.scale = image_handler.res.scale

        self.groups = groups if groups != () else set()
        for grp in self.groups:
            grp.add(self)

        self.screen_dec = screen_dec
        self.image_handler = image_handler
        self.position_handler = position_handler

        self.raw_dec = dec
        self.dec = (0 - dec[0], dec[1])

        self.x, self.y = position_handler.update_position(self)

    def update_(self, n=1):
        pass

    def kill(self):
        for grp in frozenset(self.groups):
            grp.remove(self)
        self.delete()


class DynamicSprite(Sprite):
    def update_(self, n=1):
        super().update_(n)
        self.x, self.y = self.position_handler.update_position(self, n)


class AnimatedSprite(Sprite):   
    def update_(self, n=1):
        super().update_(n)
        self.image = self.image_handler.update_image(self, n)


class AnimatedDynamicSprite(DynamicSprite, AnimatedSprite):
    def update_(self, n=1):
        super().update_(n)


# BG
class BgLayer(Sprite):
    def __init__(self, image_handler, position_handler, layer, batch, get_group, groups=()):
        super().__init__(image_handler, position_handler, batch, get_group, groups=groups, layer=layer)

    def get_layer(self):
        return self._layer


class DBgLayer(BgLayer):
    def __init__(self, image_handler, position_handler, layer, batch, get_group, groups=()):
        super(DBgLayer, self).__init__(image_handler, position_handler, layer, batch, get_group, groups=groups)
        _image = pyglet.image.Texture.create(self.image.width * 2, self.image.height)
        _image.blit_into(self.image.get_image_data(), 0, 0, 0)
        _image.blit_into(self.image.get_image_data(), self.image.width, 0, 0)
        self.image = _image

    def update_(self, n=1):
        x, y = self.position_handler.update_position(self, n)
        self.y = y
        self.x = x % self.image.width // 2


# ENTITY
class Entity(AnimatedDynamicSprite):
    def __init__(self, image_handler,
                 position_handler, physics_updater, particles_handler,
                 batch, get_group, dec, screen_dec, layer=0, groups=()):
        self.state = 'idle'
        self.secondary_state = ''
        self.air_control = 0
        self.can_air_control = True
        self.direction = 1
        self.thrust = Vec2d(0, 0)
        self.is_on_ground = False
        self.physics_updater = physics_updater
        self.particles_handler = particles_handler
        super().__init__(
            image_handler, position_handler, batch, get_group, groups=groups, dec=dec, screen_dec=screen_dec, layer=layer)
    
    def update_(self, n=1):
        self.particles_handler.update_(self)
        self.physics_updater.update_(self, n)
        super().update_(n)


class Particle(AnimatedSprite):
    def __init__(self,
                 image_handler,
                 position_handler, batch, get_group, dec, screen_dec, state, direction, groups=()):
        self.state = state
        self.direction = direction
        super().__init__(image_handler, position_handler, batch, get_group, groups=groups, dec=dec, screen_dec=screen_dec)
        
    def update_(self, *args, **kwargs):
        super().update_(*args, **kwargs)


class Structure(AnimatedDynamicSprite):
    def __init__(self, image_handler, position_handler, batch, get_group, dec, screen_dec, state, layer=0, groups=()):
        self.state = state
        super().__init__(
            image_handler, position_handler, batch, get_group, groups=groups, dec=dec, screen_dec=screen_dec, layer=layer)


class Text(AnimatedDynamicSprite):
    def __init__(self, image_handler, position_handler, batch, get_group, dec, groups=()):
        super(Text, self).__init__(
            image_handler, position_handler, batch, get_group, groups=groups, dec=dec, screen_dec=[0, 0])

        
class Button(AnimatedDynamicSprite):
    def __init__(self, image_handler, position_handler, batch, get_group, action_name, groups=()):
        self.state = 'idle'
        self.action = action_name
        super().__init__(image_handler, position_handler, batch, get_group, groups=groups, layer=9)
        self._width = self.image.width
        self._height = self.image.height

    def collide_with(self, x, y):
        if self.image is None:
            print(0)
        if self.x <= x <= (self.x + self._width):
            if self.y <= y <= (self.y + self._height):
                return True

        return False

    def kill(self):
        super(Button, self).kill()
        print('killing', self.action)


class GeneratedButton:
    def __init__(self, text, position_handler, font, size, batch, get_group, action_name, width,
                 rectangle=0, layer=9, groups=()):
        self.dec = (0, 0)
        self.screen_dec = [0, 0]
        self.text = text
        self.position_handler = position_handler
        self.font = font
        self.batch = batch
        self.group = get_group(layer)
        for grp in groups:
            grp.add(self)
        self.groups = groups if groups != () else set()
        self.action = action_name

        self.state = 'idle'

        x, y = self.position_handler.update_position(self)
        self.previous_coords = [x, y]

        self.label = pyglet.text.Label(self.text, font, size, batch=self.batch, group=self.group)

        width = max(width, self.label.content_width)
        height = self.label.content_height

        if rectangle:

            self.rectangle_width = rectangle
            self.rectangle = {
                pyglet.shapes.Line(x, y, x + width, y, self.rectangle_width, batch=self.batch, group=self.group),
                pyglet.shapes.Line(
                    x + width, y, x + width, y + height, self.rectangle_width, batch=self.batch, group=self.group),
                pyglet.shapes.Line(
                    x + width, y + height, x, y + height, self.rectangle_width, batch=self.batch, group=self.group),
                pyglet.shapes.Line(x, y + height, x, y, self.rectangle_width, batch=self.batch, group=self.group)
            }
        else:
            self.rectangle = {}

        self.width = width
        self.height = height

    def kill(self):
        print('killing', self.action)
        for grp in frozenset(self.groups):
            grp.remove(self)
        self.label.delete()
        for line in self.rectangle:
            line.delete()

    def update_(self, *_, **__):

        #  un peu contradictoire avec la manière de faire des autres sprites, mais bon c'est vraiment pour un truc
        #  très spécifique
        if self.state == 'idle':
            color = (255, 255, 255, 255)
        else:
            color = (127, 127, 127, 255)
        self.label.color = color
        for line in self.rectangle:
            line.color = color[:-1]

        x, y = self.position_handler.update_position(self)
        self.label.x = x
        self.label.y = y
        dx = x - self.previous_coords[0]
        dy = y - self.previous_coords[1]
        for line in self.rectangle:
            line.x += dx
            line.x2 += dx
            line.y += dy
            line.y2 += dy
        self.previous_coords = x, y

    def collide_with(self, x, y):
        if self.label.x <= x <= (self.label.x + self.width):
            if self.label.y <= y <= (self.label.y + self.height):
                return True

        return False



