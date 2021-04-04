# -*- coding:Utf-8 -*-


import pyglet


class ImageHandler:
    def __init__(self, res):
        self.res = res

    def update_image(self, _, n=1):
        raise NotImplementedError


class BgLayerImageHandler(ImageHandler):
    def __init__(self, res, layer, parallax=False):
        super().__init__(res)
        self.layer = layer

        self.parallax = parallax

        self.image = self.res.layers[self.layer]

        if parallax:
            image_data = self.image.get_image_data()

            _image = pyglet.image.Texture.create(self.image.width * 2, self.image.height)
            _image.blit_into(image_data, 0, 0, 0)
            _image.blit_into(image_data, self.image.width, 0, 0)

            self.image = _image

    def update_image(self, sprite, n=1):
        return self.image

    def is_parallax(self):
        return self.parallax


class EntityImageHandler(ImageHandler):
    def __init__(self, res, end_animation_callback):
        super().__init__(res)
        self.end_animation_callback = end_animation_callback
        self.advance = 0
        self.previous_state = 'idle'

    def update_image(self, _, __=1):
        raise NotImplementedError


class TBEntityImageHandler(EntityImageHandler):
    def __init__(self, res, end_animation_callback):
        super(TBEntityImageHandler, self).__init__(res, end_animation_callback)

        self.animation_changed = True
        self.direction_changed = True

    def on_animation_end(self, entity):
        self.end_animation_callback(entity.state)

    def update_image(self, entity, n=1):
        if entity.state != self.previous_state:
            self.previous_state = entity.state
            self.animation_changed = True

        if self.animation_changed or self.direction_changed:

            if entity.direction == 1:
                animation = self.res.sheets[entity.state]
            else:
                animation = self.res.flipped_sheets[entity.state]
            self.animation_changed = False
            self.direction_changed = False
            return animation
        return None

    def get_state_duration(self, state):
        animation = self.res.sheets[state]
        return animation.get_duration()


class StructureImageHandler(ImageHandler):
    def update_image(self, struct, n=1):
        img = self.res.sheets[struct.state]
        img.anchor_x = self.res.dec[0]
        img.anchor_y = getattr(struct, 'anchor_y', 0)
        return img


class RopeImageHandler(ImageHandler):
    def update_image(self, rope, n=1):
        img = self.res.sheets[rope.state]
        img.anchor_x = 0
        img.anchor_y = 2
        return img


class ButtonImageHandler(ImageHandler):
    def __init__(self, res, res_loader):
        super().__init__(res)
        self.res_loader = res_loader

    def change_res(self, new_res_name):
        self.res = self.res_loader.load(new_res_name)

    def update_image(self, button, n=1):
        img = self.res.sheets.get(button.state, None)
        if img is None:
            img = self.res.sheets['idle']
        return img


class TextImageHandler(ImageHandler):
    def __init__(self, res_getter):
        res = res_getter()
        self.res_getter = res_getter
        self.count = 0
        super(TextImageHandler, self).__init__(res)

    def update_image(self, text_object, n=1):
        if self.count == 0:
            self.res = self.res_getter()
            self.count = 0
        else:
            self.count -= 1
        return self.res.sheets['idle']


class ParticleImageHandler(ImageHandler):
    def __init__(self, res, lifetime, end_of_life):
        super().__init__(res)
        self.total_lifetime = lifetime
        self.current_lifetime = 0
        self.end_of_life = end_of_life
        self.dead = False

    def revive(self):
        self.dead = False
        self.current_lifetime = 0

    def update_image(self, entity, n=1):
        if not self.dead:
            self.current_lifetime += n
            if self.current_lifetime >= self.total_lifetime:
                self.dead = True
                self.end_of_life()

        if entity.direction == 1:
            img = self.res.sheets[entity.state]
        else:
            img = self.res.flipped_sheets[entity.state]
        return img

