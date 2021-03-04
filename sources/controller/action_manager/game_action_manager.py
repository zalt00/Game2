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
                 return_to_main_menu, save_callback, toggle_debug_draw_callback, pause_callback, tp_to_stable_ground,
                 show_player_debug_values):
        super().__init__()
        self.player = player

        self.save = save_callback

        self.toggle_debug_draw = toggle_debug_draw_callback
        self.pause = pause_callback

        self.tp_to_stable_ground = tp_to_stable_ground

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

        self.still_walking = False
        self.still_running = False

        self.next_state = 'idle'
        self.next_direction = 1

        self.already_dashed = True

        self.are_player_debug_values_hidden = False
        self.god = False

        self.show_player_debug_values = show_player_debug_values

    def dev_command(self):
        logger.info('dev debug command')

    def toggle_god_mod(self):
        self.god = not self.god

    def toggle_player_debug_values(self):
        self.show_player_debug_values(self.are_player_debug_values_hidden)
        self.are_player_debug_values_hidden = not self.are_player_debug_values_hidden

    def screenshot(self):
        name = 'screenshots/screenshot-{}.png'
        i = 0
        try:
            os.mkdir('screenshots')
        except FileExistsError:
            i = len(glob.glob('screenshots/screenshot*.png'))

        pyglet.image.get_buffer_manager().get_color_buffer().save(name.format(i))

        logger.debug(f'screenshot taken and saved as {name.format(i)}')

    def record(self):
        if self.player.record_position:
            logger.debug('stop recording player position, it will be saved to "record.npy"')
            self.player.stop_recording_position()
            np.save('records.npy', self.player.position_records[:self.player.last_index])
        else:
            logger.debug('start recording player position')
            self.player.start_recording_position()

    def manually_raise_error(self):
        raise RuntimeError('Error manually raised')

    def sleep(self):
        time.sleep(2)

    def land(self, landing_strength=3200):
        if landing_strength > 1800:
            if self.still_walking:
                if self.still_running:
                    self.player.secondary_state = 'run'
                else:
                    self.player.secondary_state = 'walk'
            self.player.state = 'land'
            self.next_state = 'idle'
        else:
            if self.still_walking:
                if self.still_walking:
                    if self.still_running:
                        self.player.state = 'run'
                        self.next_state = 'run'
                    else:
                        self.player.state = 'walk'
                        self.next_state = 'walk'
            else:
                self.player.state = 'land'
                self.next_state = 'idle'
        self.player.is_on_ground = True
        self.already_dashed = False

    def jump(self):
        if not self.god:
            if self.player.state in ('walk', 'run', 'idle', 'land'):
                self.player.secondary_state = ''
                self.player.state = 'jump'
            else:
                self.next_state = 'jump'
        else:
            self.player.position_handler.body.apply_force_at_local_point(
                (0, 1_250_000), self.player.position_handler.body.center_of_gravity)

    def dash(self):
        if not self.already_dashed or self.god:
            if self.player.state == 'fall' or self.player.state == 'jump':
                self.player.state = 'dash'
                self.already_dashed = True

    def run(self):
        self.still_running = True
        if self.player.state == 'walk':
            self.player.state = 'run'
            self.next_state = 'run'
        elif self.next_state == 'walk':
            self.next_state = 'run'

    def stop_running(self):
        self.still_running = False
        self._stop_running()

    def _stop_running(self):
        if self.player.state == 'run':
            self.player.state = 'walk'
            self.next_state = 'walk'
        elif self.next_state == 'run' and self.still_walking:
            self.next_state = 'walk'

    def walk_left(self):
        self.still_walking = True

        if self.player.state == 'walk' or self.player.state == 'run':
            self.player.direction = -1
        self.next_direction = -1
        if self.player.state == 'run':
            self.next_state = 'run'
        else:
            self.next_state = 'walk'

        if self.still_running:
            self.run()

    def walk_right(self):
        self.still_walking = True

        if self.player.state == 'walk' or self.player.state == 'run':
            self.player.direction = 1
        self.next_direction = 1
        if self.player.state == 'run':
            self.next_state = 'run'
        else:
            self.next_state = 'walk'

        if self.still_running:
            self.run()

    def stop_walking_right(self):
        if self.player.direction == 1 or self.next_direction == 1:
            self.stop_walking()

    def stop_walking_left(self):
        if self.player.direction == -1 or self.next_direction == -1:
            self.stop_walking()

    def stop_walking(self):
        self._stop_running()
        self.still_walking = False
        if self.player.state == 'walk':
            self.player.state = 'idle'
        self.next_state = 'idle'

    def set_state(self, *args, **kwargs):

        if not self.player.dead and not self.player.sleeping:
            if self.player.state == 'land':
                self.player.secondary_state = ''

            if self.player.state == 'dash':
                self.player.state = 'fall'
                if self.still_walking:
                    if self.still_running:
                        self.player.position_handler.end_of_dash('running', self.player)
                    else:
                        self.player.position_handler.end_of_dash('walking', self.player)
                else:
                    self.player.position_handler.end_of_dash('', self.player)

            if not self.player.is_on_ground:
                if self.player.state in ('jump',) or self.next_state in ('walk', 'run', 'prejump'):
                    self.next_state = self.player.state
                else:
                    self.next_state = 'fall'

            if self.player.state == 'jump' and self.player.is_on_ground:
                self.next_state = 'jump'
            self.player.direction = self.next_direction
            if self.player.air_control:
                self.player.air_control = self.player.direction

            self.player.state = self.next_state

            if self.player.is_on_ground:
                if self.still_walking:
                    if self.still_running:
                        self.next_state = 'run'
                    else:
                        self.next_state = 'walk'
                else:
                    if self.player.state != 'jump':
                        self.next_state = 'idle'
                    else:
                        self.next_state = 'jump'
            else:
                if self.player.state in ('jump',):
                    self.next_state = self.player.state
                else:
                    self.next_state = 'fall'
                if self.still_walking:
                    self.player.air_control = self.player.direction

        elif self.player.dead:
            if self.player.state != 'die':
                self.player.state = 'die'
                self.next_state = 'die'
            else:
                self.player.hide()

        else:
            if self.player.state == 'hit':
                self.tp_to_stable_ground()
                self.player.state = 'idle'
                self.player.sleeping = False
            else:
                self.player.state = 'hit'


