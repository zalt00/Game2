# -*- coding:Utf-8 -*-

from utils.save_modifier import Save
from utils.types import Trigger, DataContainer
from pymunk import Vec2d
from pygame.color import THECOLORS
from pygame.constants import *


class Data(DataContainer):
    key_names = {
        K_LSHIFT: 'shift',
        K_RSHIFT: 'shift',
        K_LCTRL: 'ctrl',
        K_RCTRL: 'ctrl',
        K_LALT: 'alt',
        K_RALT: 'alt'
    }
    
    controller_values_name = {
        (0, -1): 'LX-',
        (0, 1): 'LX+',
        (1, -1): 'LY+',
        (1, 1): 'LY-',
        (2, 1): 'LT',
        (2, -1): 'RT',
        (4, -1): 'RX-',
        (4, 1): 'RX+',
        (3, -1): 'RY+',
        (3, 1): 'RY-',
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

    class Options(DataContainer):
        option_types = ('Video', 'Gameplay', 'Controls')

        class Video(DataContainer):
            display_mode = Save(3)
            width = Save(4)
            height = Save(5)
            resolution = width + height
            luminosity = Save(6)
        
        class Gameplay(DataContainer):
            deadzones = Save(7)
            invert_axis = Save(8)
            
        class Controls(DataContainer):
            actions = 'left', 'right', 'run', 'dash', 'jump', 'menu', 'interact'
            left = (Save(9), Save(16))
            right = (Save(10), Save(17))
            run = (Save(11), Save(18))
            dash = (Save(12), Save(19))
            jump = (Save(13), Save(20))
            menu = (Save(14), Save(21))
            interact = (Save(15), Save(22))
    
######################################################################################################
    
    class Menu(DataContainer):
        pages = ('MainMenu',)
        
        class MainMenu(DataContainer):
            bg_res = 'black_forest'
            bg_pos = (0, 0)

            class Objects(DataContainer):
                objects = ('PlayButton', 'OptionsButton', 'QuitButton',
                           'MainPanel', 'ControlsPanel', 'VideoPanel', 'GameplayPanel', 'ControlsButton', 'GameplayButton', 'VideoButton',
                           'ApplyButton', 'CancelButton', 'ResetButton')
                
                options_objects = {'MainPanel', 'ControlsButton', 'GameplayButton', 'VideoButton', 'ApplyButton', 'CancelButton', 'ResetButton'}
                main_menu_objects = {'PlayButton', 'OptionsButton', 'QuitButton'}
                menu_classic_buttons_order = (
                    ('play_button',),
                    ('options_button',),
                    ('quit_button',)
                )
                options_classic_buttons = set()
                panel_order = ('Video', 'Gameplay', 'Controls')
                
                class PlayButton:
                    typ = 'button'
                    res = 'buttons/play_button'
                    action = 'play'
                    pos = (40, 360)
                    button_name = 'play_button'

                class QuitButton:
                    typ = 'button'
                    res = 'buttons/quit_button'
                    action = 'quit'
                    pos = (40, 190)
                    button_name = 'quit_button'

                class OptionsButton:
                    typ = 'button'
                    res = 'buttons/open_options_button'
                    action = 'open_options_menu'
                    pos = (40, 270)
                    button_name = 'options_button'
                    
                class MainPanel:
                    typ = 'structure'
                    res = 'panels/options_main_panel'
                    pos = (50, 120 * 1000)

                class ControlsPanel:
                    typ = 'structure'
                    res = 'panels/options_controls_panel'
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
                        kb_left=dict(pos=(205, 500 * 1000), action='set_kbkey', arg='left', font=('nkb', 40, Save(9), "#eeeeee", "#888888", 100, 35, 5)),
                        kb_right=dict(pos=(205, 440 * 1000), action='set_kbkey', arg='right', font=('nkb', 40, Save(10), "#eeeeee", "#888888", 100, 35, 5)),
                        kb_run=dict(pos=(205, 380 * 1000), action='set_kbkey', arg='run', font=('nkb', 40, Save(11), "#eeeeee", "#888888", 100, 35, 5)),
                        kb_dash=dict(pos=(205, 320 * 1000), action='set_kbkey', arg='dash', font=('nkb', 40, Save(12), "#eeeeee", "#888888", 100, 35, 5)),
                        kb_jump=dict(pos=(205, 260 * 1000), action='set_kbkey', arg='jump', font=('nkb', 40, Save(13), "#eeeeee", "#888888", 100, 35, 5)),
                        kb_menu=dict(pos=(790, 500 * 1000), action='set_kbkey', arg='menu', font=('nkb', 40, Save(14), "#eeeeee", "#888888", 100, 35, 5)),
                        kb_interact=dict(pos=(790, 440 * 1000), action='set_kbkey', arg='interact', font=('nkb', 40, Save(15), "#eeeeee", "#888888", 100, 35, 5)),

                        
                        con_left=dict(pos=(430, 500 * 1000), action='set_conkey', arg='left', font=('ncon', 40, Save(16), "#eeeeee", "#888888", 100, 35, 5)),
                        con_right=dict(pos=(430, 440 * 1000), action='set_conkey', arg='right', font=('ncon', 40, Save(17), "#eeeeee", "#888888", 100, 35, 5)),                        
                        con_run=dict(pos=(430, 380 * 1000), action='set_conkey', arg='run', font=('ncon', 40, Save(18), "#eeeeee", "#888888", 100, 35, 5)),
                        con_dash=dict(pos=(430, 320 * 1000), action='set_conkey', arg='dash', font=('ncon', 40, Save(19), "#eeeeee", "#888888", 100, 35, 5)),  
                        con_jump=dict(pos=(430, 260 * 1000), action='set_conkey', arg='jump', font=('ncon', 40, Save(20), "#eeeeee", "#888888", 100, 35, 5)),
                        con_menu=dict(pos=(1025, 500 * 1000), action='set_conkey', arg='menu', font=('ncon', 40, Save(21), "#eeeeee", "#888888", 100, 35, 5)),
                        con_interact=dict(pos=(1025, 440 * 1000), action='set_conkey', arg='interact', font=('ncon', 40, Save(22), "#eeeeee", "#888888", 100, 35, 5)),

                    )
                    panel_name = 'Controls'

                class VideoPanel:
                    typ = 'structure'
                    res = 'panels/options_video_panel'
                    pos = (70, 404 * 1000)
                    buttons_order = (
                        ('display_mode', 'display_mode', None),
                        ('resolution', 'resolution', None),
                        ('luminosity', 'luminosity', None),
                        ('apply_button', 'cancel_button', 'reset_button'),
                    )                    
                    additional_buttons = dict(
                        display_mode=dict(pos=(320, 567 * 1000),
                                          arg=[0, ('buttons/fullscreen', 1), ('buttons/windowed', 0), 'display_mode'],
                                          action='change_option', res='buttons/fullscreen'),
                        resolution=dict(pos=(320, 489 * 1000),
                                        arg=[0, ('buttons/resolutions/1280 x 720', (1280, 800)), ('buttons/resolutions/1280 x 960', (1280, 960)), 'resolution'],
                                        action='change_option', res='buttons/resolutions/1280 x 720'),
                        luminosity=dict(pos=(320, 411 * 1000),
                                        arg=[0, ('buttons/luminosity/normal', 0), 'luminosity'],
                                        action='change_option', res='buttons/luminosity/normal'),
                    )
                    options_save = dict(display_mode={0: 1, 1: 0},
                                        resolution={(1280, 800): 0, (1280, 960): 1},
                                        luminosity={0: 0})  # permet de passer de la valeur de la save a l'indice du bouton a afficher
                    panel_name = 'Video'

                class GameplayPanel:
                    typ = 'structure'
                    res = 'panels/options_gameplay_panel'
                    pos = (70, 336 * 1000)
                    buttons_order = (
                        ('apply_button', 'cancel_button', 'reset_button'),
                    )
                    additional_buttons = dict()
                    panel_name = 'Gameplay'
                    
                class ControlsButton:
                    typ = 'button'
                    res = 'buttons/controls_button'
                    action = 'set_panel_to_controls'
                    pos = (521, 690 * 1000)

                class GameplayButton:
                    typ = 'button'
                    res = 'buttons/gameplay_button'
                    action = 'set_panel_to_gameplay'
                    pos = (280, 682 * 1000)

                class VideoButton:
                    typ = 'button'
                    res = 'buttons/video_button'
                    action = 'set_panel_to_video'
                    pos = (115, 690 * 1000)
                    
                class ApplyButton:
                    typ = 'button'
                    res = 'buttons/apply_button'
                    action = 'apply'
                    button_name = 'apply_button'
                    pos = (80, 142 * 1000)

                class CancelButton:
                    typ = 'button'
                    res = 'buttons/cancel_button'
                    action = 'cancel'
                    button_name = 'cancel_button'
                    pos = (220, 150 * 1000)

                class ResetButton:
                    typ = 'button'
                    res = 'buttons/reset_button'
                    action = 'reset'
                    button_name = 'reset_button'
                    pos = (1092, 150 * 1000)                    
                    
                    
######################################################################################################

    class Game(DataContainer):

        current_map_id = Save(2)
        maps = ('BlackForest',)
        
        class BlackForest(DataContainer):
            res = 'black_forest'
            space = True
            
            dynamic_layers = True
            animated_layers = False
            bg_pos = (0, 0)
            
            ground_height = 122
            ground_length = 10000
            
            class Objects(DataContainer):
                objects = ('Player', 'S1', 'PlayerValues')
                player = 'Player'

                class Player:
                    typ = 'entity'
                    res = 'player/white_guy'
                    height = 50
                    width = 30
                    name = 'player'
                    pos_x = Save(0)
                    pos_y = Save(1)
                    
                class S1:
                    typ = 'structure'
                    res = 'structures/s1'
                    name = 's1'
                    pos_x = 600
                    pos_y = 122
                    state = 'base'
                    poly = [(Vec2d(-39, 0), Vec2d(-39, 110), Vec2d(39, 110), Vec2d(39, 0))]
                    ground = [(Vec2d(38, 111), Vec2d(-38, 111))]

                class PlayerValues:
                    typ = 'text'
                    pos = 20, 680
                    text = 'x velocity: {}\ny velocity: {}\nx coordinate: {}\ny coordinate: {}'
                    values = (('player', 'position_handler', 'body', 'velocity', 'x'),
                              ('player', 'position_handler', 'body', 'velocity', 'y'),
                              ('player', 'position_handler', 'body', 'position', 'x'),
                              ('player', 'position_handler', 'body', 'position', 'y'))
                    color = '#ffffff'
                    size = 30

            class Triggers(DataContainer):
                triggers = ('LeftBorderTrigger', 'RightBorderTrigger', 'BottomOfWorldTrigger')

                class RightBorderTrigger(Trigger, DataContainer):
                    id_ = 0
                    left = 1255
                    enabled = True

                    class Actions(DataContainer):
                        actions = ('MoveCamera', 'EnableLBT', 'SelfDisable')

                        class MoveCamera:
                            typ = 'AbsoluteMovecam'
                            kwargs = dict(
                                x=-1216,
                                y=0,
                                total_duration=80,  # in frames
                                fade_in=30,
                                fade_out=30)

                        class EnableLBT:
                            typ = 'EnableTrigger'
                            kwargs = dict(target=1)

                        class SelfDisable:
                            typ = 'DisableTrigger'
                            kwargs = dict(target=0)
                
                class LeftBorderTrigger(Trigger, DataContainer):
                    id_ = 1
                    right = 1242

                    class Actions(DataContainer):
                        actions = ('MoveCamera', 'EnableRBT', 'SelfDisable')

                        class MoveCamera:
                            typ = 'AbsoluteMovecam'
                            kwargs = dict(
                                x=0,
                                y=0,
                                total_duration=80,  # in frames
                                fade_in=30,
                                fade_out=30)

                        class EnableRBT:
                            typ = 'EnableTrigger'
                            kwargs = dict(target=0)

                        class SelfDisable:
                            typ = 'DisableTrigger'
                            kwargs = dict(target=1)           
                            
                class BottomOfWorldTrigger(Trigger, DataContainer):
                    id_ = 2
                    top = -100
                    enabled = True

                    class Actions(DataContainer):
                        actions = ('TP',)

                        class TP:
                            typ = 'TPEntity'
                            kwargs = dict(
                                npos=(500, 300),
                                entity_name='player'
                            )
