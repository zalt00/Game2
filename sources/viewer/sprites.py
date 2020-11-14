# -*- coding:Utf-8 -*-

import pyglet
from pymunk import Vec2d


class SpriteMetaclass(type):
    instantiable_constructors = {}

    def __new__(mcs, name, bases, attrdict, instantiable=True):
        cls = type.__new__(mcs, name, bases, attrdict)
        if instantiable:
            mcs.instantiable_constructors[name] = cls
        return cls

    @classmethod
    def get_constructor(mcs, sprite_type_name):
        if sprite_type_name in mcs.instantiable_constructors:
            return mcs.instantiable_constructors[sprite_type_name]
        raise ValueError('no constructor with this name')


class BaseSprite(pyglet.sprite.Sprite, metaclass=SpriteMetaclass, instantiable=False):
    def __init__(self, batch, layer_group, position_handler, image_handler, screen_offset, state='idle'):
        self.state = state
        self.screen_offset = screen_offset

        self.__position = (0, 0)

        super().__init__(pyglet.image.Texture.create(0, 0), batch=batch, group=layer_group)

        self.image_handler = image_handler
        self.position_handler = position_handler

        self.animated = True
        self.static = False

        self.position_changed = False
        self.image_changed = False

        self.affected_by_screen_offset = True

        self._hide_next_update = False
        self._show_next_update = False

        self.image = image_handler.update_image(self)
        position = list(position_handler.update_position(self))
        if self.affected_by_screen_offset:
            position[0] += self.screen_offset[0]
            position[1] += self.screen_offset[1]
        self.position = position

        if hasattr(image_handler, 'res'):
            if hasattr(image_handler.res, 'scale'):
                self.scale = image_handler.res.scale

    def on_animation_end(self):
        try:
            self.image_handler.on_animation_end(self)
        except AttributeError:
            pass

    def update_position(self, last_update=True):
        if self._hide_next_update:
            self.hide(False)
            self._hide_next_update = False
        if self._show_next_update:
            self.show(False)
            self._show_next_update = False

        if not self.static or self.position_changed:
            position = list(self.position_handler.update_position(self))
            if self.affected_by_screen_offset:
                position[0] += self.screen_offset[0]
                position[1] += self.screen_offset[1]
            self.__position = position
            if last_update:
                self.position = position

    def update_image(self):
        if self.animated or self.image_changed:
            image = self.image_handler.update_image(self)
            if image is not None:
                self.image = image
        self.position_changed = self.image_changed = False

    def update_(self, n=1):
        self.update_position()
        self.update_image()

    def hide(self, wait_for_next_update=False):
        if wait_for_next_update:
            self._hide_next_update = True
        else:
            self.visible = False
            self.static = True
            self.animated = False

    def show(self, wait_for_next_update=True):
        if wait_for_next_update:
            self._show_next_update = True
        else:
            self.visible = True
            self.static = False
            self.animated = True


class Entity(BaseSprite, metaclass=SpriteMetaclass):
    def __init__(self, batch, layer_group, position_handler,
                 image_handler, screen_offset, physic_state_updater, particles_handler, end_of_state_callback):

        self.secondary_state = ''

        self.air_control = 0
        self.can_air_control = True

        self.thrust = Vec2d(0, 0)

        self.is_on_ground = False

        self.physic_state_updater = physic_state_updater
        self.particles_handler = particles_handler

        self._state = 'idle'
        self.end_of_state = end_of_state_callback

        self._direction = 1

        super().__init__(batch, layer_group, position_handler, image_handler, screen_offset)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self.physic_state_updater.change_physic_state(self, new_state)
        self._state = new_state

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        if value != self.direction:
            self._direction = value
            try:
                self.image_handler.direction_changed = True
            except AttributeError:
                pass

    def update_position(self, last_update=True):
        self.physic_state_updater.update_(self)
        super(Entity, self).update_position(last_update)

    def update_image(self):
        super(Entity, self).update_image()
        self.particles_handler.update_(self)


class BgLayer(BaseSprite, metaclass=SpriteMetaclass):
    def __init__(self, batch, layer_group, position_handler, image_handler, screen_offset):
        super().__init__(batch, layer_group, position_handler, image_handler, screen_offset)
        self.affected_by_screen_offset = False
        image_data = self.image.get_image_data()

        _image = pyglet.image.Texture.create(self.image.width * 2, self.image.height)
        _image.blit_into(image_data, 0, 0, 0)
        _image.blit_into(image_data, self.image.width, 0, 0)

        self.image = _image

        self.animated = False

    def get_layer(self):
        return self.image_handler.layer


class Structure(BaseSprite, metaclass=SpriteMetaclass):
    def __init__(self, *args, **kwargs):
        super(Structure, self).__init__(*args, **kwargs)
        self.animated = False

    def __repr__(self):
        return f'Structure(image={self.image}, position={self.position})'


class Button(BaseSprite, metaclass=SpriteMetaclass):
    def __init__(self, batch, layer_group, position_handler, image_handler, screen_offset, action_name):
        self.action = action_name
        super().__init__(batch, layer_group, position_handler, image_handler, screen_offset)

    def collide_with(self, x, y):
        if self.x <= x <= (self.x + self.width):
            if self.y <= y <= (self.y + self.height):
                return True
        return False


class Particle(BaseSprite, metaclass=SpriteMetaclass):
    def __init__(self, batch, layer_group, position_handler, image_handler, screen_offset, state, direction):
        self.direction = direction
        self.__position = (0, 0)
        super().__init__(batch, layer_group, position_handler, image_handler, screen_offset, state)

    def update_position(self, last_update=True):
        if self.visible or self._show_next_update:
            super(Particle, self).update_position(last_update)
            self.__position = self.position

    @pyglet.sprite.Sprite.visible.setter
    def visible(self, value):
        if value:
            self.position = self.__position
        pyglet.sprite.Sprite.visible.fset(self, value)

    def change_position(self, x, y):
        self.position_handler.pos = [x, y]
        self.position_changed = True
        self.__position = x, y


class GeneratedButton(metaclass=SpriteMetaclass):
    def __init__(self, batch, layer_group, font, size, text, position_handler, action_name, width, rectangle=0):
        self.text = text
        self.position_handler = position_handler
        self.font = font
        self.batch = batch
        self.group = layer_group

        self.screen_offset = [0, 0]

        self.action = action_name

        self.state = 'idle'

        x, y = self.position_handler.update_position(self)
        self.previous_coords = [x, y]

        self.label = pyglet.text.Label(self.text, font, size, batch=self.batch, group=self.group)

        self.min_width = width

        width = max(width, self.label.content_width)
        height = self.label.content_height

        if rectangle:
            self.rectangle_outline_thickness = rectangle
            ht = round(rectangle / 2)
            dec_x = rectangle
            dec_y = rectangle
            self.rectangle = [
                pyglet.shapes.Line(x - ht - dec_x, y - dec_y, x + width + ht - 1 + dec_x, y - dec_y,  # bottom
                                   self.rectangle_outline_thickness,
                                   batch=self.batch, group=self.group),
                pyglet.shapes.Line(x + width + dec_x, y - dec_y, x + width + dec_x, y + height - dec_y,  # right
                                   self.rectangle_outline_thickness,
                                   batch=self.batch, group=self.group),
                pyglet.shapes.Line(x + width + dec_x + ht - 1, y + height - dec_y, x - ht - dec_x, y + height - dec_y,
                                   self.rectangle_outline_thickness,  # top
                                   batch=self.batch, group=self.group),
                pyglet.shapes.Line(x - dec_x, y + height - dec_y, x - dec_x, y - dec_y,  # left
                                   self.rectangle_outline_thickness,
                                   batch=self.batch, group=self.group)
            ]
        else:
            self.rectangle = []

        self.width = width
        self.height = height

    def update_(self):
        self.update_position()
        self.update_image()

    def update_image(self, *_, **__):
        #  un peu contradictoire avec la manière de faire des autres sprites, mais bon c'est vraiment pour un truc
        #  très spécifique
        if self.state == 'idle':
            color = (255, 255, 255, 255)
        else:
            color = (127, 127, 127, 255)
        self.label.color = color
        for line in self.rectangle:
            line.color = color[:-1]

    def update_position(self, _=None):
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

    def change_text(self, new_text):
        self.label.text = new_text
        new_width = max(self.label.content_width, self.min_width)
        dif = new_width - self.width
        self.width = new_width
        self.rectangle[0].x2 += dif
        self.rectangle[1].x += dif
        self.rectangle[1].x2 += dif
        self.rectangle[2].x += dif


class Text(pyglet.text.Label, metaclass=SpriteMetaclass):
    def __init__(self, batch, layer_group, font, size, text_getter, position_handler, color=(255, 255, 255, 255)):

        self.get_text = text_getter

        text = self.get_text()
        self.a = 0
        super(Text, self).__init__(text, font, size, batch=batch, group=layer_group, color=color, multiline=True, width=800)

        self.position_handler = position_handler

        self.update_()

    def update_position(self):
        self.x, self.y = self.position_handler.update_position(self)

    def update_image(self):
        self.a += 1
        self.a %= 12
        if self.a == -1:
            text = self.get_text()
            self.text = text

    def update_(self, *_, **__):
        self.update_position()
        self.update_image()

