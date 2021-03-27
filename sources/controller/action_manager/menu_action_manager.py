# -*- coding:Utf-8 -*-


from .base_action_manager import ActionManager
from utils.save_modifier import SaveComponent


class BaseMenuActionManager(ActionManager):
    def __init__(self, action_manager_data):

        """constructor of the class"""

        super().__init__()

        self.additional_texts = action_manager_data.additional_texts
        self.additional_structures = action_manager_data.additional_structures

        self.window = action_manager_data.window

        self.panels = action_manager_data.panels
        self.panel_order = action_manager_data.panel_order
        self.current_panel = ""

        self.base_classic_buttons = action_manager_data.classic_buttons.copy()  # base
        self.classic_buttons_order = action_manager_data.classic_buttons_order  # current
        self.classic_buttons = action_manager_data.classic_buttons  # current
        self.buttons_sprite_group = action_manager_data.buttons  # current
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

    def __init__(self, action_manager_data):
        super(MainMenuActionManager, self).__init__(action_manager_data)

        self.play = action_manager_data.play_callback
        self.quit = action_manager_data.quit_game_callback
        self.open_options_menu = action_manager_data.open_options_callback

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

    def __init__(self, action_manager_data):

        super(OptionsActionManager, self).__init__(action_manager_data)

        self._close_options = action_manager_data.return_to_mainmenu_callback
        self.reinit_page = action_manager_data.reinit_page_callback

        self.change_kb_ctrls = action_manager_data.change_kb_ctrls_callback
        self.change_con_ctrls = action_manager_data.change_con_ctrls_callback
        self._set_ctrl = action_manager_data.set_ctrl_callback

        self.set_fullscreen = action_manager_data.set_fullscreen_callback

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

        self.options_data = action_manager_data.options_data

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
                    save.set_bytes(*value)
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
            self.options_data.Controls.get(self.changing_ctrl)[1].set_bytes(*value)
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

    def __init__(self, action_manager_data):
        super(CharacterSelectionActionManager, self).__init__(action_manager_data)

        self.start_game = action_manager_data.start_game_callback
        self.return_to_mainmenu_callback = action_manager_data.return_to_mainmenu_callback

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



