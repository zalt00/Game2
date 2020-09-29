# -*- coding:Utf-8 -*-

from . import event_manager as evtm
from .resources_loader import ResourcesLoader2, OtherObjectsResource
import pyglet
import pyglet.window
from .sprites import SpriteMetaclass, GeneratedButton
from . import image_handler as ihdlr
from .page import Page
from utils import window_event

pyglet.image.Texture.default_min_filter = pyglet.gl.gl.GL_NEAREST
pyglet.image.Texture.default_mag_filter = pyglet.gl.gl.GL_NEAREST


class Window(pyglet.window.Window):
    def __init__(self, width, height, display_mode, *args, **kwargs):
        super().__init__(width, height, fullscreen=display_mode, *args, **kwargs)

        self._screen_offset = [0, 0]

        self.menu_page = self.new_page('menu')
        self.game_page = self.new_page('game')
        self.current_page = self.menu_page

        self.ordered_groups = [pyglet.graphics.OrderedGroup(i) for i in range(20)]

        self.resource_loader = ResourcesLoader2('resources')

        self.event_manager = evtm.INACTIVE_EVENT_MANAGER

        self.current_transition = None

        self.joysticks = []
        self.init_joysticks()

        pyglet.clock.schedule_interval(self._update, 1 / 120.0)

    def init_joysticks(self):
        self.joysticks = pyglet.input.get_joysticks()
        for joy in self.joysticks:
            joy.open()
            @joy.event
            def on_joyaxis_motion(_, axis, value):
                self.on_joyaxis_motion(axis, value)

            @joy.event
            def on_joyhat_motion(_, hat_x, hat_y):
                self.on_joyhat_motion(hat_x, hat_y)

            @joy.event
            def on_joybutton_press(_, button):
                self.on_joybutton_press(button)

            @joy.event
            def on_joybutton_release(_, button):
                self.on_joybutton_release(button)

    def stop_loop(self):
        self.close()

    @property
    def screen_offset(self):
        return self._screen_offset

    @screen_offset.setter
    def screen_offset(self, value):
        if len(value) != 2:
            raise ValueError('value length must be 2')
        self._screen_offset[0] = value[0]
        self._screen_offset[1] = value[1]

    def on_draw(self):
        self.current_page.draw()
        if self.current_transition is not None:
            if self.current_transition.state == 2:
                self.current_transition = None
            else:
                self.current_transition.update()
                self.current_transition.sprite.draw()
        self.after_draw()

    @window_event.event
    def on_key_press(self, symbol, modifiers):
        pass

    @window_event.event
    def on_key_release(self, symbol, modifiers):
        pass

    @window_event.event
    def on_mouse_motion(self, x, y, dx, dy):
        pass

    @window_event.event
    def on_mouse_press(self, x, y, button, modifiers):
        pass

    @window_event.event
    def on_joyaxis_motion(self, axis, value):
        pass

    @window_event.event
    def on_joyhat_motion(self, hat_x, hat_y):
        pass

    @window_event.event
    def on_joybutton_press(self, button):
        pass

    @window_event.event
    def on_joybutton_release(self, button):
        pass

    @staticmethod
    def new_page(name):
        return Page(name)

    def set_page(self, page):
        self.current_page = page

    def _add_sprite(self, batch, sprite_type, layer, position_handler, image_handler, *args, **kwargs):
        constructor = SpriteMetaclass.get_constructor(sprite_type)
        layer_group = self.get_group(layer)

        sprite = constructor(batch, layer_group, position_handler, image_handler, self.screen_offset, *args, **kwargs)
        return sprite

    def add_bg_layer(self, page, layer, position_handler, res):
        if isinstance(res, str):
            res = self.resource_loader.load(res)
        batch = page.batch
        image_handler = ihdlr.BgLayerImageHandler(res, layer)
        sprite = self._add_sprite(batch, 'BgLayer', layer, position_handler, image_handler)
        return sprite

    def add_entity(self, page, layer, position_handler, res, physics_updater, particle_handler,
                   end_animation_callback):
        if isinstance(res, str):
            res = self.resource_loader.load(res)
        batch = page.batch
        image_handler = ihdlr.TBEntityImageHandler(res, end_animation_callback)
        sprite = self._add_sprite(batch, 'Entity', layer, position_handler, image_handler,
                                  physics_updater, particle_handler)
        return sprite

    def add_structure(self, page, layer, position_handler, res):
        if isinstance(res, str):
            res = self.resource_loader.load(res)
        batch = page.batch
        image_handler = ihdlr.StructureImageHandler(res)
        sprite = self._add_sprite(batch, 'Structure', layer, position_handler, image_handler)
        return sprite

    def spawn_particle(self, page, layer, position_handler, res, state, direction, lifetime):
        img_hdlr = ihdlr.ParticleImageHandler(res, lifetime, None)
        particle = self._add_sprite(page.batch, 'Particle', layer, position_handler, img_hdlr, state, direction)
        img_hdlr.end_of_life = particle.hide
        return particle

    def add_bg(self, page, position_handlers, res):
        if isinstance(res, str):
            res = self.resource_loader.load(res)

        bg_layers = []
        i = 0
        for layer in res.bg:
            layer_id = layer['layer']
            bg_layers.append(self.add_bg_layer(page, layer_id, position_handlers[i], res))
            position_handlers[i].pos[0] += layer['relative_pos'][0]
            position_handlers[i].pos[1] += layer['relative_pos'][1]
            position_handlers[i].base_pos = tuple(position_handlers[i].pos)
            i += 1

        for layer in res.fg:
            layer_id = layer['layer']
            bg_layers.append(self.add_bg_layer(page, layer_id, position_handlers[i], res))
            position_handlers[i].pos[0] += layer['relative_pos'][0]
            position_handlers[i].pos[1] += layer['relative_pos'][1]
            position_handlers[i].base_pos = tuple(position_handlers[i].pos)
            i += 1

        return bg_layers

    def add_button(self, page, layer, position_handler, res, action_name):
        if isinstance(res, str):
            res = self.resource_loader.load(res)
        batch = page.batch
        image_handler = ihdlr.ButtonImageHandler(res, self.resource_loader)
        sprite = self._add_sprite(batch, 'Button', layer, position_handler, image_handler, action_name)
        return sprite

    def add_generated_button(self, page, layer, font, size, text, position_handler, action_name, width, rectangle=0):
        batch = page.batch
        layer_group = self.get_group(layer)
        sprite = GeneratedButton(batch, layer_group, font, size, text, position_handler, action_name, width, rectangle)
        return sprite

    def build_structure(self, page, layer, position_handler, res, palette_name):
        """builds and add a structure from a palette and a string buffer"""

        palette = self.resource_loader.load(palette_name)
        if isinstance(res, str):
            res = self.resource_loader.load(res)

        if not res.built:
            s = palette.build(res)

            sheets = {'idle': s}
            res.build(sheets)
        return self.add_structure(page, layer, position_handler, res)

    def get_group(self, layer):
        return self.ordered_groups[layer + 10]

    def set_event_manager(self, event_manager_name, *args, **kwargs):
        self.event_manager = getattr(evtm, event_manager_name)(*args, **kwargs)

    def reset_event_manager(self):
        self.event_manager = evtm.INACTIVE_EVENT_MANAGER

    def get_number_of_layers(self, res_name):
        res = self.resource_loader.load(res_name)
        return len(res.layers)

    def add_transition(self, transition):
        self.current_transition = transition
        transition.start()

    def update(self, *_, **__):
        pass

    def _update(self, *_, **__):
        self.update(*_, **__)

    def after_draw(self, *_, **__):
        pass
