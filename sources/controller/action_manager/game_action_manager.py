# -*- coding:Utf-8 -*-


from .base_action_manager import ActionManager
from pymunk.vec2d import Vec2d
from utils.save_modifier import SaveComponent
import time
import numpy as np
from utils.logger import logger
import pyglet
import os
import glob


class GameActionManager(ActionManager):
    RIGHT = 0
    LEFT = 1
    ATTACK = 2
    ATTACK2 = 3
    DASH = 4
    JUMP = 6
    RUN = 7
    SAVE = 8
    MENU = 9
    INTERACT = 10
    TOGGLE_DEBUG_DRAW = 11
    MANUALLY_RAISE_ERROR = 13
    PAUSE = 14
    DEV_COMMAND = 15
    RECORD = 16
    GOD = 17
    SCREENSHOT = 18
    TOGGLE_PLAYER_DEBUG_VALUES = 19

    def __init__(self, player,
                 return_to_main_menu, save_callback, toggle_debug_draw_callback, pause_callback,
                 show_player_debug_values):
        super().__init__()
        self.player = player

        self.save = save_callback

        self.toggle_debug_draw = toggle_debug_draw_callback
        self.pause = pause_callback

        self.do_handlers[self.RIGHT] = self.walk_right
        self.stop_handlers[self.RIGHT] = self.stop_walking_right

        self.do_handlers[self.LEFT] = self.walk_left
        self.stop_handlers[self.LEFT] = self.stop_walking_left

        self.do_handlers[self.RUN] = self.run
        self.stop_handlers[self.RUN] = self.stop_running

        self.do_handlers[self.DASH] = self.dash
        self.do_handlers[self.JUMP] = self.jump

        self.do_handlers[self.SAVE] = self.save
        self.do_handlers[self.MENU] = return_to_main_menu

        self.do_handlers[self.TOGGLE_DEBUG_DRAW] = self.toggle_debug_draw
        self.do_handlers[self.MANUALLY_RAISE_ERROR] = self.manually_raise_error
        self.do_handlers[self.PAUSE] = self.pause

        self.do_handlers[self.TOGGLE_PLAYER_DEBUG_VALUES] = self.toggle_player_debug_values

        self.do_handlers[self.DEV_COMMAND] = self.dev_command
        self.do_handlers[self.GOD] = self.toggle_god_mod

        self.do_handlers[self.RECORD] = self.record

        self.do_handlers[self.SCREENSHOT] = self.screenshot

        self.are_player_debug_values_hidden = False

        self.show_player_debug_values = show_player_debug_values

    def dev_command(self):
        self.player.call_action('die')
        logger.info('dev debug command')

    def toggle_god_mod(self):
        self.player.call_action('toggle_god_mod')

    def toggle_player_debug_values(self):
        self.show_player_debug_values(self.are_player_debug_values_hidden)
        self.are_player_debug_values_hidden = not self.are_player_debug_values_hidden

    @staticmethod
    def screenshot():
        name = 'screenshots/screenshot-{}.png'
        i = 0
        try:
            os.mkdir('screenshots')
        except FileExistsError:
            i = len(glob.glob('screenshots/screenshot*.png'))

        pyglet.image.get_buffer_manager().get_color_buffer().save(name.format(i))

        logger.debug(f'screenshot taken and saved as {name.format(i)}')

    def call_action(self, action_name, arg=(), stop=False):
        if self.player is not None:
            self.player.call_action(action_name, arg, stop)

    def record(self):
        self.call_action('record')

    def manually_raise_error(self):
        raise RuntimeError('Error manually raised')

    def sleep(self):
        time.sleep(2)

    def land(self, landing_strength=3200):
        self.call_action('land', [landing_strength])

    def jump(self):
        self.call_action('jump')

    def dash(self):
        self.call_action('dash')

    def run(self):
        self.call_action('run')

    def stop_running(self):
        self.call_action('run', stop=True)

    def walk_left(self):
        self.call_action('walk_left')

    def walk_right(self):
        self.call_action('walk_right')

    def stop_walking_right(self):
        self.call_action('walk_right', stop=True)

    def stop_walking_left(self):
        self.call_action('walk_left', stop=True)


