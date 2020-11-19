# -*- coding:Utf-8 -*-


from pymunk.vec2d import Vec2d
from utils.save_modifier import SaveComponent
import time
import numpy as np
from utils.logger import logger


class ActionManager:
    def __init__(self):
        self.do_handlers = {}
        self.stop_handlers = {}
    
    def do(self, action, *args, **kwargs):
        try:
            self.do_handlers[action](*args, **kwargs)
        except KeyError:
            pass
        
    def stop(self, action, *args, **kwargs):
        try:
            self.stop_handlers[action](*args, **kwargs)
        except KeyError:
            pass


class BaseMenuActionManager(ActionManager):
    def __init__(self, window, buttons, classic_buttons, classic_buttons_order, panels,
                 panel_order, additional_texts, additional_structures):

        """constructor of the class

        :param window: app.window
        :param buttons: button sprite group
        :param classic_buttons: base buttons, buttons which are always there even when the panel changes
        :param classic_buttons_order: order of the buttons, useful for the controller
        :param panels: dict which binds the name of the panel with the data of the panel
        :param panel_order: panel order, useful for the next_panel and previous_panel fonctions
        :param additional_texts: additional texts to display regardless of the panel
        :param additional_structures: not implemented yet, has currently no effect
        """

        super().__init__()

        self.additional_texts = additional_texts
        self.additional_structures = additional_structures

        self.window = window

        self.panels = panels
        self.panel_order = panel_order
        self.current_panel = ""

        self.base_classic_buttons = classic_buttons.copy()  # base
        self.classic_buttons_order = classic_buttons_order  # current
        self.classic_buttons = classic_buttons  # current
        self.buttons_sprite_group = buttons  # current
        self.additional_buttons = {}  # current

        self.confirmation_messages = {}  # current

        self.count = 0
        self.last_pos = (0, 0)
        self.controller = False
        self.focus = [0, 0]

        self.mouse_pos = (0, 0)
        
    def update_buttons(self, mouse_pos):
        """updates the text color of the buttons in function of the mouse's position"""
        self.mouse_pos = mouse_pos
        if not self.controller:
            self.count = 0
            for button in self.buttons_sprite_group:
                if button.collide_with(*mouse_pos):
                    button.state = 'activated'
                else:
                    button.state = 'idle'
                    self.remove_confirmation_messages(button)
        else:
            self.count += 1
            if self.count > 2:
                self.controller = False
                self.window.set_mouse_visible(True)

    def update_buttons2(self):
        """updates text color of the buttons using the "focus" attribute"""
        if not self.controller:
            self.last_pos = self.mouse_pos
        self.window.set_mouse_visible(False)
        self.controller = True
        button = self.classic_buttons[self.classic_buttons_order[self.focus[1]][self.focus[0]]]
        for b in self.classic_buttons.values():
            b.state = 'idle'
            if b is not button:
                self.remove_confirmation_messages(b)
        button.state = 'activated'

    def remove_confirmation_messages(self, button):
        """removes the confirmation messages of a specific action, or the button's action"""
        if isinstance(button, str):
            action = button
        else:
            action = button.action
        if action in self.confirmation_messages:
            for txto in self.confirmation_messages[action]:
                x, y = txto.position_handler.pos
                if y < 2000:
                    y *= 1000
                    txto.position_handler.pos = x, y
            self.confirmation_messages[action] = []

    def move_focus_up(self):
        b_order = self.classic_buttons_order
        if len(b_order) != 0:
            
            self.focus[1] -= 1
            if self.focus[1] == -1:
                self.focus[1] = len(b_order) - 1            
            while b_order[self.focus[1]][self.focus[0]] is None:
                self.focus[1] -= 1
                if self.focus[1] == -1:
                    self.focus[1] = len(b_order) - 1
            self.update_buttons2()
        
    def move_focus_down(self):
        b_order = self.classic_buttons_order
        if len(b_order) != 0:
            self.focus[1] += 1
            if self.focus[1] == len(b_order):
                self.focus[1] = 0
            i = 0
            while b_order[self.focus[1]][self.focus[0]] is None and i < 50:
                self.focus[1] += 1
                if self.focus[1] == len(b_order):
                    self.focus[1] = 0
                i += 1

            if i < 50:
                self.update_buttons2()

    def move_focus_left(self):
        b_order = self.classic_buttons_order
        if len(b_order) != 0:
            self.focus[0] -= 1
            if self.focus[0] == -1:
                self.focus[0] = len(b_order[self.focus[1]]) - 1            
            while b_order[self.focus[1]][self.focus[0]] is None:
                self.focus[0] -= 1
                if self.focus[0] == -1:
                    self.focus[0] = len(b_order[self.focus[1]]) - 1
            self.update_buttons2()

    def move_focus_right(self):
        b_order = self.classic_buttons_order
        if len(b_order) != 0:                
            self.focus[0] += 1
            if self.focus[0] == len(b_order[self.focus[1]]):
                self.focus[0] = 0          
            while b_order[self.focus[1]][self.focus[0]] is None:
                self.focus[0] += 1
                if self.focus[0] == len(b_order[self.focus[1]]):
                    self.focus[0] = 0
            self.update_buttons2()

    def button_activation(self):
        """executes the action of the focused button"""
        b_order = self.classic_buttons_order
        if len(b_order) != 0:
            button = self.classic_buttons[b_order[self.focus[1]][self.focus[0]]]
            if hasattr(button, 'arg'):
                getattr(self, button.action)(button.arg)
            else:
                getattr(self, button.action)()
                
    def left_click(self, mouse_pos):
        """executes the action of the buttons which are touching the mouse"""
        for button in frozenset(self.buttons_sprite_group):
            if button.collide_with(*mouse_pos):
                if hasattr(button, 'arg'):
                    getattr(self, button.action)(button.arg)
                else:
                    getattr(self, button.action)()
                    
    def remove_current_panel(self):
        """removes the current panel and all of its components"""
        if self.current_panel != "":
            for b in self.classic_buttons.values():
                self.remove_confirmation_messages(b)

            structure = self.panels[self.current_panel]['structure']
            x, y = structure.position_handler.pos
            y *= 1000
            structure.position_handler.pos = x, y
            self.current_panel = ""
            for button in self.additional_buttons.values():
                x, y = button.position_handler.pos
                y *= 1000
                button.position_handler.pos = x, y
            self.additional_buttons = dict()
            
    def _set_panel_to(self, panel_name):
        """removes the current panel and initialize the precised panel"""
        self.remove_current_panel()
            
        nstructure = self.panels[panel_name]['structure']
        x, y = nstructure.position_handler.pos
        y //= 1000
        nstructure.position_handler.pos = x, y
        self.current_panel = panel_name
        
        self.classic_buttons_order = self.panels[panel_name]['buttons_order']
        self.additional_buttons = self.panels[panel_name]['buttons']
        self.classic_buttons = self.additional_buttons.copy()

        self.classic_buttons.update(self.base_classic_buttons)

        for button in self.additional_buttons.values():
            x, y = button.position_handler.pos
            y //= 1000
            button.position_handler.pos = x, y

        self.focus[0] = min(self.focus[0], len(self.classic_buttons_order[0]) - 1)
        self.focus[1] = min(self.focus[1], len(self.classic_buttons_order) - 1)
        if self.classic_buttons_order[self.focus[1]][self.focus[0]] is None:
            self.move_focus_down()
        if self.classic_buttons_order[self.focus[1]][self.focus[0]] is None:
            self.move_focus_right()
        if self.controller:
            self.update_buttons2()

    def next_panel(self):
        if self.current_panel:
            i = 0
            p = self.panel_order[i]
            while p != self.current_panel:
                i += 1
                p = self.panel_order[i]
                
            if i + 1 == len(self.panel_order):
                j = 0
            else:
                j = i + 1
            npanel = self.panel_order[j]
            self._set_panel_to(npanel)
        
    def previous_panel(self):
        if self.current_panel:
            i = 0
            p = self.panel_order[i]
            while p != self.current_panel:
                i += 1
                p = self.panel_order[i]
                
            npanel = self.panel_order[i - 1]
            self._set_panel_to(npanel)
        
    def add_confirmation_message(self, name, associated_button_action):
        """adds the confirmation message of the precised name, associated with a specific button/button action"""
        msg = self.additional_texts[name]
        if associated_button_action in self.confirmation_messages:
            self.confirmation_messages[associated_button_action].append(msg)
        else:
            self.confirmation_messages[associated_button_action] = [msg]
        x, y = msg.position_handler.pos
        if y > 2000:
            y //= 1000
            msg.position_handler.pos = x, y


class MainMenuActionManager(BaseMenuActionManager):
    MOUSEMOTION = 0
    LEFT_CLICK = 1

    DOWN = 3
    UP = 4
    LEFT = 8
    RIGHT = 9

    ACTIVATE = 5

    def __init__(self, window, buttons, classic_buttons, classic_buttons_order, panels,
                 panel_order, additional_texts, additional_structures, start_game_callback,
                 quit_game_callback, open_options_callback):

        super(MainMenuActionManager, self).__init__(window, buttons, classic_buttons, classic_buttons_order, panels,
                                                    panel_order, additional_texts, additional_structures)

        self.play = start_game_callback
        self.quit = quit_game_callback
        self.open_options_menu = open_options_callback

        self.do_handlers[self.MOUSEMOTION] = self.update_buttons
        self.do_handlers[self.LEFT_CLICK] = self.left_click

        self.do_handlers[self.DOWN] = self.move_focus_down
        self.do_handlers[self.UP] = self.move_focus_up

        self.do_handlers[self.ACTIVATE] = self.button_activation

        self.update_buttons2()


class OptionsActionManager(BaseMenuActionManager):
    MOUSEMOTION = 0
    LEFT_CLICK = 1

    DOWN = 3
    UP = 4
    LEFT = 8
    RIGHT = 9

    ACTIVATE = 5
    CANCEL = 11

    NEXT = 6
    PREVIOUS = 7

    SET_CTRL = 10

    def __init__(self, window, buttons, classic_buttons, classic_buttons_order, panels,
                 panel_order, additional_texts, additional_structures,
                 close_options_callback, change_kb_ctrls_callback, change_con_ctrls_callback,
                 set_ctrl_callback, options_data, reinit_page_callback, set_fullscreen_callback):

        super(OptionsActionManager, self).__init__(window, buttons, classic_buttons, classic_buttons_order, panels,
                                                   panel_order, additional_texts, additional_structures)

        self._close_options = close_options_callback
        self.reinit_page = reinit_page_callback

        self.change_kb_ctrls = change_kb_ctrls_callback
        self.change_con_ctrls = change_con_ctrls_callback
        self._set_ctrl = set_ctrl_callback

        self.set_fullscreen = set_fullscreen_callback

        self.do_handlers[self.MOUSEMOTION] = self.update_buttons
        self.do_handlers[self.LEFT_CLICK] = self.left_click

        self.do_handlers[self.DOWN] = self.move_focus_down
        self.do_handlers[self.UP] = self.move_focus_up
        self.do_handlers[self.LEFT] = self.move_focus_left
        self.do_handlers[self.RIGHT] = self.move_focus_right

        self.do_handlers[self.ACTIVATE] = self.button_activation
        self.do_handlers[self.CANCEL] = self.cancel
        self.do_handlers[self.NEXT] = self.next_panel
        self.do_handlers[self.PREVIOUS] = self.previous_panel

        self.do_handlers[self.SET_CTRL] = self.set_ctrl

        self.options_data = options_data

        self.changing_ctrl = ''
        self.changing_ctrl_button = None

        self.set_panel_to_video()
        self.update_buttons2()

        self.apply_additional_actions = {}

    def change_change_display_mode(self, arg):
        self.change_option(arg)
        self.apply_additional_actions['set_fullscreen'] = [not arg[0]]

    def change_option(self, arg):
        if len(arg) == arg[0] + 3:
            arg[0] = 0
        else:
            arg[0] += 1
        res, value = arg[arg[0] + 1]
        self.classic_buttons[arg[-1]].image_handler.change_res(res)
        self.options_data.get(self.current_panel).get(arg[-1]).set(value)

    def close_options(self):
        for b in self.classic_buttons.values():
            self.remove_confirmation_messages(b)
        self._close_options()

    def set_panel_to_controls(self):
        self._set_panel_to('Controls')

    def set_panel_to_gameplay(self):
        self._set_panel_to('Gameplay')

    def set_panel_to_video(self):
        self._set_panel_to('Video')

    def apply(self):
        for action_type, args in self.apply_additional_actions.items():
            getattr(self, action_type)(*args)
        self.apply_additional_actions = {}
        SaveComponent.dump()
        self.close_options()

    def cancel(self):
        if self.current_panel:
            SaveComponent.load()
            self.close_options()

    def reset(self):
        txto = self.additional_texts['reset_confirmation_message']
        if txto.position_handler.pos[1] < 2000:
            self.remove_confirmation_messages('reset')
            for save, value in self.options_data.default_values:
                if isinstance(value, tuple):
                    save.set_shorts(*value)
                else:
                    save.set(value)
            self.reinit_page()
        else:
            self.add_confirmation_message('reset_confirmation_message', 'reset')

    def set_kbkey(self, arg):
        button = self.classic_buttons['kb_' + arg]
        self.changing_ctrl = arg
        self.changing_ctrl_button = button
        self.change_kb_ctrls(button)

    def set_conkey(self, arg):
        button = self.classic_buttons['con_' + arg]
        self.changing_ctrl = arg
        self.changing_ctrl_button = button
        self.change_con_ctrls(button)

    def set_ctrl(self, value):
        if isinstance(value, tuple):
            self.options_data.Controls.get(self.changing_ctrl)[1].set_shorts(*value)
        else:
            self.options_data.Controls.get(self.changing_ctrl)[0].set(value)

        self._set_ctrl(value, self.changing_ctrl_button)


class CharacterSelectionActionManager(BaseMenuActionManager):
    MOUSEMOTION = 0
    LEFT_CLICK = 1

    DOWN = 3
    UP = 4
    LEFT = 8
    RIGHT = 9

    ACTIVATE = 5

    def __init__(self, window, buttons, classic_buttons, classic_buttons_order, panels,
                 panel_order, additional_texts, additional_structures, start_game_callback,
                 return_to_mainmenu_callback):

        super(CharacterSelectionActionManager, self).__init__(window, buttons, classic_buttons, classic_buttons_order,
                                                              panels, panel_order, additional_texts,
                                                              additional_structures)

        self.start_game = start_game_callback
        self.return_to_mainmenu_callback = return_to_mainmenu_callback

        self.do_handlers[self.MOUSEMOTION] = self.update_buttons
        self.do_handlers[self.LEFT_CLICK] = self.left_click

        self.do_handlers[self.DOWN] = self.move_focus_down
        self.do_handlers[self.UP] = self.move_focus_up
        self.do_handlers[self.LEFT] = self.move_focus_left
        self.do_handlers[self.RIGHT] = self.move_focus_right

        self.do_handlers[self.ACTIVATE] = self.button_activation

        self.update_buttons2()

    def load_save(self, i):
        self.start_game(i)


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
    
    def __init__(self, player,
                 return_to_main_menu, save_callback, toggle_debug_draw_callback, pause_callback):
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

        self.do_handlers[self.DEV_COMMAND] = self.dev_command

        self.do_handlers[self.RECORD] = self.record

        self.still_walking = False
        self.still_running = False
        
        self.next_state = 'idle'
        self.next_direction = 1
        
        self.already_dashed = True

    def dev_command(self):
        logger.info('dev debug command')

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

    def land(self):
        if self.still_walking:
            if self.still_running:
                self.player.secondary_state = 'run'
            else:
                self.player.secondary_state = 'walk'
        self.player.state = 'land'
        self.next_state = 'idle'
        self.player.is_on_ground = True
        self.already_dashed = False

    def jump(self):
        if self.player.state in ('walk', 'run', 'idle'):
            self.player.secondary_state = ''
            self.player.state = 'jump'
        else:
            self.next_state = 'jump'
            
    def dash(self):
        if not self.already_dashed:
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
        
        if self.player.state == 'land':
            self.player.secondary_state = ''
        
        if self.player.state == 'dash':
            self.player.state = 'fall'
            if self.still_walking:
                if self.still_running:
                    self.player.position_handler.body.velocity = Vec2d(150 * self.player.direction, 0)
                else:
                    self.player.position_handler.body.velocity = Vec2d(100 * self.player.direction, 0)
            else:
                self.player.position_handler.body.velocity = Vec2d(0, 0)
        
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

