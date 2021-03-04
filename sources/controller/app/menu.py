# -*- coding:Utf-8 -*-


from ..position_handler import StaticPositionHandler, BgLayerPositionHandler
from ..action_manager import MainMenuActionManager, OptionsActionManager, CharacterSelectionActionManager
from ..text_getter import FormatTextGetter, SimpleTextGetter
from utils.save_modifier import SaveComponent
from pyglet.window import key
import os


class Menu:
    def __init__(self, window, model, start_game_callback, debug=False):
        self.window = window
        self.model = model
        self.state = 'menu'

        SaveComponent.load()

        self.debug = debug

        self.start_game_callback = start_game_callback

        self.window.screen_offset = 0, 0

        self.page_name = None
        self.page = None
        self.page_res = None
        self.pos_hdlrs = None
        self.panels = None
        self.menu_objects = None
        self.action_manager = None
        self.classic_buttons = None
        self.viewer_page = None
        self.y_offset = 0

        self.window.set_page(self.window.menu_page)

        self.texts = None

        self.init_page('MainMenu')

        self.window.update = self.update

    def delete_current_page(self):
        self.window.menu_page.remove_child(self.page_name)
        self.page_name = None

    def init_page(self, page_name):
        self.page_name = page_name
        self.page = self.model.Menu.get(page_name)
        self.page_res = self.page.bg_res

        self.viewer_page = self.window.new_page(page_name)
        self.viewer_page.add_group('buttons')
        self.viewer_page.add_group('bg_layers')
        self.viewer_page.add_group('structures')
        self.viewer_page.add_group('texts')

        self.window.menu_page.add_child(self.viewer_page)

        n_layers = self.window.get_number_of_layers(self.page_res)
        pos = self.page.bg_pos

        pos_hdlrs = [BgLayerPositionHandler(pos, [0, 0]) for _ in range(n_layers)]

        bg_layers = self.window.add_bg(self.viewer_page, pos_hdlrs, self.page_res)
        self.viewer_page.bg_layers.update(bg_layers)

        self.pos_hdlrs = pos_hdlrs

        self.panels = {}
        self.menu_objects = []

        self.classic_buttons = {}

        self.texts = {}

        self.y_offset = self.model.Menu.y_offset

        for oname in self.page.Objects.objects:
            data = self.page.Objects.get(oname)
            obj = None
            if data.typ == 'button':
                if data.pos[1] > 2000:
                    offset = self.y_offset * 1000
                else:
                    offset = self.y_offset
                bpos_hdlr = StaticPositionHandler([data.pos[0], data.pos[1] + offset])
                if hasattr(data, 'res'):
                    obj = self.window.add_button(self.viewer_page, 0, bpos_hdlr, data.res, data.action)
                    self.viewer_page.buttons.add(obj)
                else:
                    font_data = data.font
                    obj = self.window.add_generated_button(
                        self.viewer_page, 0, 'm5x7', font_data[1], self.get_button_text_from_font_data(font_data),
                        StaticPositionHandler([data.pos[0], data.pos[1] + offset]),
                        data.action, font_data[5], font_data[-1])
                    self.viewer_page.buttons.add(obj)

                if hasattr(data, 'arg'):
                    obj.arg = data.arg
            elif data.typ == 'structure':
                if data.pos[1] > 2000:
                    offset = self.y_offset * 1000
                else:
                    offset = self.y_offset
                spos_hdlr = StaticPositionHandler([data.pos[0], data.pos[1] + offset])
                obj = self.window.add_structure(self.viewer_page, 0, spos_hdlr, data.res)
                self.viewer_page.structures.add(obj)
                if hasattr(data, 'panel_name'):
                    additional_buttons = self.init_panel_buttons(data)
                    self.panels[data.panel_name] = dict(structure=obj,
                                                        buttons=additional_buttons,
                                                        buttons_order=data.buttons_order, data=data)

            elif data.typ == 'text':
                if data.pos[1] > 2000:
                    offset = self.y_offset * 1000
                else:
                    offset = self.y_offset
                tpos_hdlr = StaticPositionHandler([data.pos[0], data.pos[1] + offset])
                obj = self.window.add_text(self.viewer_page, 0, data.font, data.size,
                                           SimpleTextGetter(data.text), tpos_hdlr)
                self.texts[data.name] = obj
                self.viewer_page.texts.add(obj)
            if obj is not None:
                self.menu_objects.append(obj)
                if hasattr(data, 'button_name'):
                    self.classic_buttons[data.button_name] = obj

        actionmanager = None
        if self.page.action_manager == 'MainMenuActionManager':
            actionmanager = MainMenuActionManager(
                self.window,
                self.viewer_page.buttons,
                self.classic_buttons,
                self.page.Objects.classic_buttons_order,
                self.panels,
                self.page.Objects.panel_order,
                self.texts,
                (),
                self.play,
                self.quit_game,
                self.open_options
            )

        elif self.page.action_manager == 'OptionsActionManager':
            actionmanager = OptionsActionManager(
                self.window,
                self.viewer_page.buttons,
                self.classic_buttons,
                self.page.Objects.classic_buttons_order,
                self.panels,
                self.page.Objects.panel_order,
                self.texts,
                (),
                self.return_to_main_menu,
                self.change_kb_ctrls,
                self.change_con_ctrls,
                self.set_ctrl,
                self.model.Options,
                self.reinit_page,
                self.window.set_display_mode
            )
        elif self.page.action_manager == 'CharacterSelectionActionManager':
            actionmanager = CharacterSelectionActionManager(
                self.window,
                self.viewer_page.buttons,
                self.classic_buttons,
                self.page.Objects.classic_buttons_order,
                self.panels,
                self.page.Objects.panel_order,
                self.texts,
                (),
                self.start_game_callback,
                self.return_to_main_menu
            )

        if actionmanager is None:
            raise ValueError(f'invalid action manager name: {self.page.action_manager}')
        self.window.set_event_manager('MenuEventManager', actionmanager)
        self.action_manager = actionmanager

    def update(self, *_, **__):
        for sprite in self.viewer_page.get_all_sprites():
            sprite.update_()

    def init_panel_buttons(self, panel_data):
        data = panel_data
        buttons_data = panel_data.additional_buttons
        ndict = {}
        for bname, bdata in buttons_data.items():
            res_name = bdata.get('res', None)
            if bdata['pos'][1] > 2000:
                offset = self.y_offset * 1000
            else:
                offset = self.y_offset
            if res_name is not None:
                button = self.window.add_button(
                    self.viewer_page, 0, StaticPositionHandler([bdata['pos'][0], bdata['pos'][1] + offset]),
                    res_name, bdata['action'])
                self.viewer_page.buttons.add(button)

            else:
                font_data = bdata['font']
                button = self.window.add_generated_button(
                    self.viewer_page, 0, 'm5x7', font_data[1], self.get_button_text_from_font_data(font_data),
                    StaticPositionHandler([bdata['pos'][0], bdata['pos'][1] + offset]),
                    bdata['action'], font_data[5], font_data[-1])
                self.viewer_page.buttons.add(button)

            if 'arg' in bdata:
                button.arg = bdata['arg']
                if hasattr(data, 'options_save'):
                    self.set_state(data, button, bname)

            ndict[bname] = button
        return ndict

    def get_button_text_from_font_data(self, font_data):
        if font_data[0] == 'nkb':
            txt = self.get_key_name(font_data[2].get())
        elif font_data[0] == 'ncon':
            txt = self.get_controller_value_name(font_data[2].get_bytes())

        elif font_data[0] == 'txt':
            txt = font_data[2]
        else:
            raise ValueError(f'font_data[0] must be either nkb, ncon or txt, not {font_data[0]}')
        return txt

    def reinit_page(self):
        if self.page_name is not None:
            page_name = self.page_name
            self.delete_current_page()
            self.init_page(page_name)

    def get_key_name(self, nkey):
        name = self.model.key_names.get(nkey, None)
        if name is None:
            name = key.symbol_string(nkey).lower()
        return name

    def get_controller_value_name(self, nvalue):
        name = self.model.controller_values_name.get(nvalue, None)
        if name is None:
            name = 'undef'
        return name

    def set_state(self, data, button, bname):
        button.arg[0] = data.options_save[bname][self.model.Options.get(data.panel_name).get(bname).get()]
        res, value = button.arg[button.arg[0] + 1]
        button.image_handler.change_res(res)

    def open_options(self):
        self.delete_current_page()
        self.init_page('Options')

    def return_to_main_menu(self):
        self.delete_current_page()
        self.init_page('MainMenu')

    def play(self):
        self.delete_current_page()
        self.init_page('CharacterSelectionMenu')

    def change_kb_ctrls(self, button):
        button.label.text = ''
        self.window.set_event_manager('ChangeCtrlsEventManager', self.action_manager, 'kb')

    def change_con_ctrls(self, button):
        button.label.text = ''
        self.window.set_event_manager('ChangeCtrlsEventManager', self.action_manager, 'con')

    def set_ctrl(self, value, button):
        if isinstance(value, tuple):
            name = self.get_controller_value_name(value)
        else:
            name = self.get_key_name(value)

        button.change_text(name)
        self.window.set_event_manager('MenuEventManager', self.action_manager)

    def reverse_trajectory(self, t):
        if int(t.target[0]) == 0:
            for p in self.pos_hdlrs:
                p.add_trajectory((-2300, 0), 1500, 400, 400)
        else:
            for p in self.pos_hdlrs:
                p.add_trajectory((0, 0), 1500, 400, 400)

    @staticmethod
    def dump_save():
        SaveComponent.dump()

    def quit_game(self):
        self.dump_save()
        self.window.stop_loop()

    def quit(self):
        self.dump_save()


