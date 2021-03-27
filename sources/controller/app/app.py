# -*- coding:Utf-8 -*-


import threading
from viewer.transition import Transition
import os
from .menu import Menu
from .game import Game
from utils.logger import logger


class App:
    def __init__(self, window, model, debug=False):
        self.window = window
        self.model = model
        logger.debug(f'resources directory: {os.path.abspath(self.model.resources_path)}')
        self.window.create_resources_loader(os.path.abspath(self.model.resources_path))
        self.current = Menu(window, model, self.start_game, debug=debug)

        self.debug = debug

        self.current_thread = None
        self.transition_finished = False
        self.transition = None

        self.current_save_id = 1

    def change_app_state(self, new_state, map_test_mode=False):
        self.current.quit()
        self.window.update = lambda *_, **__: None
        self.window.after_draw = lambda *_, **__: None
        self.window.quit = lambda *_, **__: None

        del self.current

        if new_state == 'game':
            if map_test_mode:
                self.current = Game(self.window, self.model,
                                    self.window.stop_loop, self.game_loading_finished_check, self.current_save_id,
                                    debug=self.debug)
            else:
                self.current = Game(self.window, self.model,
                                    self.return_to_main_menu, self.game_loading_finished_check, self.current_save_id,
                                    debug=self.debug)
        elif new_state == 'menu':
            self.current = Menu(self.window, self.model, self.start_game, debug=self.debug)

    def start_fade_in_transition(self):
        self.transition_finished = False
        self.transition = Transition(8, (0, 0, 0), (self.window.width, self.window.height),
                                     self.fade_in_transition_finished, 'in', False, priority=10)

        self.window.add_transition(self.transition)

    def fade_in_transition_finished(self):
        self.transition_finished = True

    def delayed_start_game(self):
        assert isinstance(self.current, Game)

        self.current.start_game()
        self.start_fade_out_transition()

    def start_fade_out_transition(self):
        if self.model.Game.fade_out_transition_when_starting_game:
            self.transition = Transition(8, (0, 0, 0), (self.window.width, self.window.height),
                                         lambda: None, 'out', True, priority=0)

        else:
            self.transition = Transition(1000, (0, 0, 0), (self.window.width, self.window.height),
                                         lambda: None, 'out', True, priority=0)

        self.window.add_transition(self.transition)

    def game_to_menu_fade_in_transition(self):
        self.transition = Transition(8, (0, 0, 0), (self.window.width, self.window.height),
                                     self.game_to_menu_fade_out_transition, 'in', True, priority=0)

        self.window.add_transition(self.transition)

    def game_to_menu_fade_out_transition(self):
        self.change_app_state('menu')
        self.transition = Transition(8, (0, 0, 0), (self.window.width, self.window.height),
                                     lambda: None, 'out', True, priority=0)

        self.window.add_transition(self.transition)

    def start_game(self, current_save_id, map_test_mode=False):
        if getattr(self.transition, 'state', None) != 1:
            self.current_save_id = current_save_id
            self.change_app_state('game', map_test_mode=map_test_mode)

            assert isinstance(self.current, Game)

            self.start_fade_in_transition()
            t = threading.Thread(target=self.current.load_resources)
            t.start()
            self.current_thread = t

    def game_loading_finished_check(self):
        assert isinstance(self.current, Game)

        if self.current_thread is not None:
            if not self.current_thread.is_alive():
                if self.transition_finished or True:
                    self.current.start_game()
                    self.transition.stop()
                    self.start_fade_out_transition()
                elif self.transition is not None:
                    self.transition.on_transition_end = self.delayed_start_game
                self.transition_finished = False

    def return_to_main_menu(self):
        if getattr(self.transition, 'state', None) != 1:
            self.game_to_menu_fade_in_transition()




