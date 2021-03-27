# -*- coding:Utf-8 -*-

from utils.save_modifier import SaveComponent
from utils.types import DataContainer
from pymunk.vec2d import Vec2d
from pyglet.window.key import *


class Data(DataContainer):
    save_path = 'data/saves/save.data'
    default_save_path = 'data/saves/default_save.data'
    resources_path = './resources/'

    key_names = {
        LSHIFT: 'shift',
        RSHIFT: 'shift',
        LCTRL: 'ctrl',
        RCTRL: 'ctrl',
        LALT: 'alt',
        RALT: 'alt'
    }
    
    controller_values_name = {
        (0, -1): 'LX-',
        (0, 1): 'LX+',
        (1, -1): 'LY+',
        (1, 1): 'LY-',
        (2, 1): 'LT',
        (2, -1): 'RT',
        (3, 1): 'RX+',
        (3, -1): 'RX-',
        (4, -1): 'RY+',
        (4, 1): 'RY-',
        (10, 0): 'A',
        (10, 1): 'B',
        (10, 2): 'X',
        (10, 3): 'Y',
        (10, 4): 'LB',
        (10, 5): 'RB',
        (10, 6): 'BACK',
        (10, 7): 'START',
        (10, 8): 'TL',
        (10, 9): 'TR',
        (11, 1): 'DPADX+',
        (11, -1): 'DPADX-',
        (12, 1): 'DPADY+',
        (12, -1): 'DPADY-',
        (20, 20): '/'
    }

    menu_save_length = 20
    game_save_length = 8

    class Options(DataContainer):
        option_types = ('Video', 'Gameplay', 'Controls')
        default_values = (
            (SaveComponent(0), 1),
            (SaveComponent(1), 1280),
            (SaveComponent(2), 720),
            (SaveComponent(3), 0),
            (SaveComponent(4), (50, 50)),
            (SaveComponent(5), (0, 0)),
            (SaveComponent(6), 113),
            (SaveComponent(7), 100),
            (SaveComponent(8), 65505),
            (SaveComponent(9), 122),
            (SaveComponent(10), 32),
            (SaveComponent(11), 65307),
            (SaveComponent(12), 101),
            (SaveComponent(13), (0, -1)),
            (SaveComponent(14), (0, 1)),
            (SaveComponent(15), (10, 5)),
            (SaveComponent(16), (10, 2)),
            (SaveComponent(17), (10, 0)),
            (SaveComponent(18), (10, 7)),
            (SaveComponent(19), (10, 1))
        )

        class Video(DataContainer):
            display_mode = SaveComponent(0)
            width = SaveComponent(1)
            height = SaveComponent(2)
            resolution = width + height
            luminosity = SaveComponent(3)

        class Gameplay(DataContainer):
            deadzones = SaveComponent(4)
            invert_axis = SaveComponent(5)
            
        class Controls(DataContainer):
            actions = 'left', 'right', 'run', 'dash', 'jump', 'menu', 'interact'
            left = (SaveComponent(6), SaveComponent(13))
            right = (SaveComponent(7), SaveComponent(14))
            run = (SaveComponent(8), SaveComponent(15))
            dash = (SaveComponent(9), SaveComponent(16))
            jump = (SaveComponent(10), SaveComponent(17))
            menu = (SaveComponent(11), SaveComponent(18))
            interact = (SaveComponent(12), SaveComponent(19))
    
######################################################################################################
    
    class Menu(DataContainer):
        pages = ('MainMenu', 'Options', 'CharacterSelectionMenu')

        y_offset = -50

        class Options(DataContainer):
            bg_res = 'backgrounds/black_forest.bg'
            bg_pos = (0, 0)
            action_manager = 'OptionsActionManager'

            class Objects(DataContainer):
                objects = ('MainStructure', 'ControlsButton', 'GameplayButton', 'VideoButton', 'ApplyButton',
                           'CancelButton', 'ResetButton', 'ControlsPanel', 'VideoPanel',
                           'GameplayPanel', 'ResetConfirmationText')

                panel_order = ('Video', 'Gameplay', 'Controls')
                classic_buttons_order = ()

                class ResetConfirmationText:
                    typ = 'text'
                    name = 'reset_confirmation_message'
                    font = 'm3x6'
                    text = 'Are you sure you want to reset the options?'
                    color = (255, 255, 255, 255)
                    size = 40
                    pos = (440, 145 * 1000)

                class MainStructure:
                    typ = 'structure'
                    res = 'panels/options_main_panel.obj'
                    pos = (50, 120)

                class ControlsPanel:
                    typ = 'structure'
                    res = 'panels/options_controls_panel.obj'
                    pos = (70, 220 * 1000)
                    buttons_order = (
                        ('kb_left', 'con_left', 'kb_menu', 'con_menu'),
                        ('kb_right', 'con_right', 'kb_interact', 'con_interact'),
                        ('kb_run', 'con_run', None, None),
                        ('kb_dash', 'con_dash', None, None),
                        ('kb_jump', 'con_jump', None, None),

                        ('apply_button', 'cancel_button', None, 'reset_button'),
                    )
                    additional_buttons = dict(
                        kb_left=dict(pos=(205, 500 * 1000), action='set_kbkey', arg='left',
                                     font=('nkb', 40, SaveComponent(6), "#eeeeee", "#888888", 100, 35, 3)),
                        kb_right=dict(pos=(205, 440 * 1000), action='set_kbkey', arg='right',
                                      font=('nkb', 40, SaveComponent(7), "#eeeeee", "#888888", 100, 35, 3)),
                        kb_run=dict(pos=(205, 380 * 1000), action='set_kbkey', arg='run',
                                    font=('nkb', 40, SaveComponent(8), "#eeeeee", "#888888", 100, 35, 3)),
                        kb_dash=dict(pos=(205, 320 * 1000), action='set_kbkey', arg='dash',
                                     font=('nkb', 40, SaveComponent(9), "#eeeeee", "#888888", 100, 35, 3)),
                        kb_jump=dict(pos=(205, 260 * 1000), action='set_kbkey', arg='jump',
                                     font=('nkb', 40, SaveComponent(10), "#eeeeee", "#888888", 100, 35, 3)),
                        kb_menu=dict(pos=(790, 500 * 1000), action='set_kbkey', arg='menu',
                                     font=('nkb', 40, SaveComponent(11), "#eeeeee", "#888888", 100, 35, 3)),
                        kb_interact=dict(pos=(790, 440 * 1000), action='set_kbkey', arg='interact',
                                         font=('nkb', 40, SaveComponent(12), "#eeeeee", "#888888", 100, 35, 3)),

                        con_left=dict(pos=(430, 500 * 1000), action='set_conkey', arg='left',
                                      font=('ncon', 40, SaveComponent(13), "#eeeeee", "#888888", 100, 35, 3)),
                        con_right=dict(pos=(430, 440 * 1000), action='set_conkey', arg='right',
                                       font=('ncon', 40, SaveComponent(14), "#eeeeee", "#888888", 100, 35, 3)),
                        con_run=dict(pos=(430, 380 * 1000), action='set_conkey', arg='run',
                                     font=('ncon', 40, SaveComponent(15), "#eeeeee", "#888888", 100, 35, 3)),
                        con_dash=dict(pos=(430, 320 * 1000), action='set_conkey', arg='dash',
                                      font=('ncon', 40, SaveComponent(16), "#eeeeee", "#888888", 100, 35, 3)),
                        con_jump=dict(pos=(430, 260 * 1000), action='set_conkey', arg='jump',
                                      font=('ncon', 40, SaveComponent(17), "#eeeeee", "#888888", 100, 35, 3)),
                        con_menu=dict(pos=(1025, 500 * 1000), action='set_conkey', arg='menu',
                                      font=('ncon', 40, SaveComponent(18), "#eeeeee", "#888888", 100, 35, 3)),
                        con_interact=dict(pos=(1025, 440 * 1000), action='set_conkey', arg='interact',
                                          font=('ncon', 40, SaveComponent(19), "#eeeeee", "#888888", 100, 35, 3)),

                    )
                    panel_name = 'Controls'

                class VideoPanel:
                    typ = 'structure'
                    res = 'panels/options_video_panel.obj'
                    pos = (70, 404 * 1000)
                    buttons_order = (
                        ('display_mode', 'display_mode', None),
                        ('resolution', 'resolution', None),
                        ('luminosity', 'luminosity', None),
                        ('apply_button', 'cancel_button', 'reset_button'),
                    )
                    additional_buttons = dict(
                        display_mode=dict(pos=(320, 567 * 1000),
                                          arg=[0, ('buttons/fullscreen.obj', 1), ('buttons/windowed.obj', 0),
                                               'display_mode'],
                                          action='change_change_display_mode', res='buttons/fullscreen.obj'),
                        resolution=dict(pos=(320, 489 * 1000),
                                        arg=[0, ('buttons/resolutions/1280 x 720.obj', (1280, 720)),
                                             ('buttons/resolutions/1280 x 800.obj', (1280, 800)),
                                             ('buttons/resolutions/1280 x 960.obj', (1280, 960)),
                                             'resolution'],
                                        action='change_option', res='buttons/resolutions/1280 x 720.obj'),
                        luminosity=dict(pos=(320, 411 * 1000),
                                        arg=[0, ('buttons/luminosity/normal.obj', 0), 'luminosity'],
                                        action='change_option', res='buttons/luminosity/normal.obj'),
                    )
                    options_save = dict(display_mode={0: 1, 1: 0},
                                        resolution={(1280, 720): 0, (1280, 800): 1, (1280, 960): 2},
                                        luminosity={0: 0})  # permet de passer de la valeur de la save a
                    # l'indice du bouton a afficher
                    panel_name = 'Video'

                class GameplayPanel:
                    typ = 'structure'
                    res = 'panels/options_gameplay_panel.obj'
                    pos = (70, 336 * 1000)
                    buttons_order = (
                        ('apply_button', 'cancel_button', None, 'reset_button'),
                    )
                    additional_buttons = dict()
                    panel_name = 'Gameplay'

                class ControlsButton:
                    typ = 'button'
                    res = 'buttons/controls_button.obj'
                    action = 'set_panel_to_controls'
                    pos = (521, 690)

                class GameplayButton:
                    typ = 'button'
                    res = 'buttons/gameplay_button.obj'
                    action = 'set_panel_to_gameplay'
                    pos = (280, 682)

                class VideoButton:
                    typ = 'button'
                    res = 'buttons/video_button.obj'
                    action = 'set_panel_to_video'
                    pos = (115, 690)

                class ApplyButton:
                    typ = 'button'
                    res = 'buttons/apply_button.obj'
                    action = 'apply'
                    button_name = 'apply_button'
                    pos = (80, 142)

                class CancelButton:
                    typ = 'button'
                    res = 'buttons/cancel_button.obj'
                    action = 'cancel'
                    button_name = 'cancel_button'
                    pos = (220, 150)

                class ResetButton:
                    typ = 'button'
                    res = 'buttons/reset_button.obj'
                    action = 'reset'
                    button_name = 'reset_button'
                    pos = (1092, 150)

        class MainMenu(DataContainer):
            bg_res = 'backgrounds/black_forest.bg'
            bg_pos = (0, 0)

            action_manager = 'MainMenuActionManager'

            class Objects(DataContainer):
                objects = ('PlayButton', 'OptionsButton', 'QuitButton')

                panel_order = ()

                classic_buttons_order = (
                    ('play_button',),
                    ('options_button',),
                    ('quit_button',)
                )

                class PlayButton:
                    typ = 'button'
                    res = 'buttons/play_button.obj'
                    action = 'play'
                    pos = (40, 360)
                    button_name = 'play_button'

                class QuitButton:
                    typ = 'button'

                    res = 'buttons/quit_button.obj'
                    action = 'quit'
                    pos = (40, 190)
                    button_name = 'quit_button'

                class OptionsButton:
                    typ = 'button'
                    res = 'buttons/open_options_button.obj'
                    action = 'open_options_menu'
                    pos = (40, 270)
                    button_name = 'options_button'

        class CharacterSelectionMenu(DataContainer):
            bg_res = 'backgrounds/black_forest.bg'
            bg_pos = (0, 0)

            action_manager = 'CharacterSelectionActionManager'

            class Objects(DataContainer):
                objects = ('Load1Button', 'Load2Button', 'Load3Button', 'CancelButton')

                classic_buttons_order = (
                    ('load1_button', 'cancel_button'),
                    ('load2_button', 'cancel_button'),
                    ('load3_button', 'cancel_button'),
                )
                panel_order = ()

                class Load1Button:
                    typ = 'button'

                    font = ('txt', 40, 'Load save 1', "#eeeeee", "#888888", 200, 35, 3)
                    action = 'load_save'
                    arg = 1
                    pos = (40, 350)
                    button_name = 'load1_button'

                class Load2Button:
                    typ = 'button'

                    font = ('txt', 40, 'Load save 2', "#eeeeee", "#888888", 200, 35, 3)
                    action = 'load_save'
                    arg = 2
                    pos = (40, 270)
                    button_name = 'load2_button'

                class Load3Button:
                    typ = 'button'

                    font = ('txt', 40, 'Load save 3', "#eeeeee", "#888888", 200, 35, 3)
                    action = 'load_save'
                    arg = 3
                    pos = (40, 190)
                    button_name = 'load3_button'

                class CancelButton:
                    typ = 'button'

                    font = ('txt', 35, 'Cancel', "#eeeeee", "#888888", 100, 30, 3)
                    action = 'return_to_mainmenu_callback'
                    pos = (1100, 120)
                    button_name = 'cancel_button'


######################################################################################################

    class Game(DataContainer):

        fade_out_transition_when_starting_game = False

        current_map_id = SaveComponent(4)
        last_checkpoint = SaveComponent(5)
        last_checkpoints_map = SaveComponent(6)
        default_checkpoint_pos = (200, 300)

        heart_resource = 'special_objects/heart.obj'
        full_heart_state = 'full'
        empty_heart_state = 'empty'

        player_lives = SaveComponent(7)

        _x_offset = 30
        _y = 670
        _spacing = 40
        _number = 3

        heart_positions = [(x_offset + spacing * i, y) for (i, x_offset, spacing, y)
                           in zip(range(_number), [_x_offset] * _number, [_spacing] * _number, [_y] * _number)]

        maps = ('data/maps/temp3.yml', 'data/maps/temp2.yml')

        death_screen_res_path = 'special_objects/death_screen.obj'

        class PlayerDebugData(DataContainer):
            pos = [1100, 690]
            text = ("x velocity: {}\n" +
                    "y velocity: {}\n" +
                    "x coordinate: {}\n" +
                    "y coordinate: {}\n" +
                    "camera x: {}\n" +
                    "camera y: {}\n" +
                    "framerate: {}\n" +
                    "map id: {}")

            values = [
                ['player', 'position_handler', 'body', 'velocity', 'x'],
                ['player', 'position_handler', 'body', 'velocity', 'y'],
                ['player', 'position_handler', 'body', 'position', 'x'],
                ['player', 'position_handler', 'body', 'position', 'y'],
                ['camera_handler', 'x'],
                ['camera_handler', 'y'],
                ['window', 'current_framerate'],
                ['current_map_id']
            ]

            color = "#ffffff"
            size = 18

        class BasePlayerData(DataContainer):
            height = 50
            width = 30
            name = "player"
            pos_x = SaveComponent(2)
            pos_y = SaveComponent(3)

            jump_y_impulse = 500
            walking_max_velocity = 50
            running_max_velocity = 132
            air_control_max_velocity = 100
            acceleration = 33
            air_control_acceleration = 15
            dash_speed = 2000
            dash_length = 6  # in ticks

            class StateDuration(DataContainer):
                idle = 0.017
                fall = 0.017
                jump = 0.017
                dash = 7 / 60

        class BaseBGData(DataContainer):
            camera_pos_x = SaveComponent(0)
            camera_pos_y = SaveComponent(1)

