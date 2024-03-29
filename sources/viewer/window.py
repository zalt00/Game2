# -*- coding:Utf-8 -*-

from . import event_manager as evtm
from .resources_loader import ResourcesLoader, OtherObjectsResource
import pyglet
import pyglet.window
from .sprites import SpriteMetaclass, GeneratedButton
from . import image_handler as ihdlr
from .page import Page
from utils import window_event
from pyglet import clock
from .ordered_groups import OrderedGroupList

pyglet.image.Texture.default_min_filter = pyglet.gl.gl.GL_NEAREST
pyglet.image.Texture.default_mag_filter = pyglet.gl.gl.GL_NEAREST


class Window(pyglet.window.Window):
    def __init__(self, width, height, display_mode, *args, **kwargs):
        super().__init__(width, height, fullscreen=display_mode, *args, **kwargs)

        self._screen_offset = [0, 0]  # offset between physic coords and display coords

        self.menu_page = self.new_page('menu')
        self.game_page = self.new_page('game')
        self.current_page = self.menu_page

        self.ordered_groups = OrderedGroupList(30)

        self.resource_loader = None

        self.event_manager = evtm.INACTIVE_EVENT_MANAGER

        self.current_transition = None

        self.joysticks = []
        self.init_joysticks()

        self.current_framerate = 60

        self.paused = False

        pyglet.clock.schedule_interval(self._update, 1 / 240.0)

    def create_resources_loader(self, dir_):
        self.resource_loader = ResourcesLoader(dir_)
        self.resource_loader.load_font('m3x6.ttf')
        self.resource_loader.load_font('m5x7.ttf')

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
        if not self.paused:
            self._update_image()
        self.current_page.draw()
        if self.current_transition is not None:
            if self.current_transition.state == 2:
                self.current_transition = None
            else:
                self.current_transition.update()
                self.current_transition.sprite.draw()
        self.after_draw()

        self.current_framerate = clock.get_fps()

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

    @staticmethod
    def schedule_once(func, delay):
        pyglet.clock.schedule_once(func, delay)

    @staticmethod
    def unschedule(func):
        pyglet.clock.unschedule(func)

    def _add_sprite(self, batch, sprite_type, layer, position_handler, image_handler, *args, **kwargs):
        constructor = SpriteMetaclass.get_constructor(sprite_type)
        layer_group = self.get_group(layer)

        sprite = constructor(batch, layer_group, position_handler, image_handler, self.screen_offset, *args, **kwargs)
        return sprite

    def add_bg_layer(self, page, layer, position_handler, res, parallax=False):
        if isinstance(res, str):
            res = self.resource_loader.load(res)
        batch = page.batch
        image_handler = ihdlr.BgLayerImageHandler(res, layer, parallax=parallax)
        sprite = self._add_sprite(batch, 'BgLayer', layer, position_handler, image_handler)
        return sprite

    def add_solid_color_background(self, page, layer, position_handler, color):
        img = pyglet.image.SolidColorImagePattern(color).create_image(self.width, self.height)
        batch = page.batch
        image_handler = ihdlr.StructureImageHandler(
            OtherObjectsResource({'base': img}, self.width, self.height, (0, 0)))

        sprite = self._add_sprite(batch, 'Structure', layer, position_handler, image_handler)
        return sprite

    def add_entity(self, page, layer, position_handler, res, physics_updater, particle_handler,
                   action_manager, *args, **kwargs):
        if isinstance(res, str):
            res = self.resource_loader.load(res)
        batch = page.batch
        image_handler = ihdlr.TBEntityImageHandler(res, lambda *_, **__: None)
        sprite = self._add_sprite(batch, 'Entity', layer, position_handler, image_handler,
                                  physics_updater, particle_handler, action_manager, *args, **kwargs)
        return sprite

    def add_structure(self, page, layer, position_handler, res, dynamic=False):
        if isinstance(res, str):
            res = self.resource_loader.load(res)
        batch = page.batch
        image_handler = ihdlr.StructureImageHandler(res)
        sprite = self._add_sprite(batch, 'Structure', layer, position_handler, image_handler, dynamic=dynamic)
        return sprite

    def add_rope(self, page, layer, position_handler, res):
        if isinstance(res, str):
            res = self.resource_loader.load(res)
        batch = page.batch
        image_handler = ihdlr.RopeImageHandler(res)
        sprite = self._add_sprite(batch, 'Rope', layer, position_handler, image_handler)
        return sprite

    def add_simple_image(self, page, layer, position_handler, res, state):
        if isinstance(res, str):
            res = self.resource_loader.load(res)
        batch = page.batch
        image_handler = ihdlr.StructureImageHandler(res)
        sprite = self._add_sprite(batch, 'SimpleImage', layer, position_handler, image_handler, state)
        return sprite

    def spawn_particle(self, page, layer, position_handler, res, state, direction, lifetime):
        img_hdlr = ihdlr.ParticleImageHandler(res, lifetime, None)
        particle = self._add_sprite(page.batch, 'Particle', layer, position_handler, img_hdlr, state, direction)
        img_hdlr.end_of_life = particle.hide
        return particle

    def add_bg(self, page, position_handlers, res, parallax=False):
        if isinstance(res, str):
            res = self.resource_loader.load(res)

        bg_layers = []
        i = 0
        for layer in res.bg:
            layer_id = layer['layer']
            bg_layers.append(self.add_bg_layer(page, layer_id, position_handlers[i], res, parallax=parallax))
            position_handlers[i].pos[0] += layer['relative_pos'][0]
            position_handlers[i].pos[1] += layer['relative_pos'][1]
            position_handlers[i].base_pos = tuple(position_handlers[i].pos)
            i += 1

        for layer in res.fg:
            layer_id = layer['layer']
            bg_layers.append(self.add_bg_layer(page, layer_id, position_handlers[i], res, parallax=parallax))
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
        constructor = SpriteMetaclass.get_constructor('GeneratedButton')
        sprite = constructor(batch, layer_group, font, size, text, position_handler, action_name, width, rectangle)
        return sprite

    def add_text(self, page, layer, font, size, text_getter, position_handler, color=(255, 255, 255, 255)):
        batch = page.batch
        layer_group = self.get_group(layer)
        constructor = SpriteMetaclass.get_constructor('Text')
        sprite = constructor(batch, layer_group, font, size, text_getter, position_handler, color)
        return sprite

    def build_structure(self, page, layer, position_handler, res, palette_name, dynamic=False):
        """builds and add a structure from a palette and a string buffer"""

        palette = self.resource_loader.load(palette_name)
        if isinstance(res, str):
            res = self.resource_loader.load(res)

        if not res.built:
            s = palette.build(res)

            sheets = {'base': s}
            res.build(sheets)
        return self.add_structure(page, layer, position_handler, res, dynamic=dynamic)

    def get_group(self, layer):
        return self.ordered_groups[layer]

    def set_event_manager(self, event_manager_name, *args, **kwargs):
        self.event_manager = getattr(evtm, event_manager_name)(*args, **kwargs)

    def reset_event_manager(self):
        self.event_manager = evtm.INACTIVE_EVENT_MANAGER

    def get_number_of_layers(self, res_name):
        res = self.resource_loader.load(res_name)
        return len(res.layers)

    def add_transition(self, transition):
        if self.current_transition is None or self.current_transition.state in {1, 2} or\
                transition.priority >= self.current_transition.priority:
            if self.current_transition is not None:
                self.current_transition.stop()
            self.current_transition = transition
            transition.start()

    def update(self, *_, **__):
        pass

    def update_image(self, *_, **__):
        pass

    def _update_image(self, *args, **kwargs):
        self.update_image(*args, **kwargs)

    def _update(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def after_draw(self, *_, **__):
        pass

    def set_display_mode(self, fullscreen):
        self.set_fullscreen(fullscreen, width=self.width, height=self.height)
