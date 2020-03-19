# -*- coding:Utf-8 -*-

from utils.save_modifier import Save


class Data:
    class Menu:
        pages = ('MainMenu',)
        
        class MainMenu:
            bg_res = 'black_forest'
            bg_pos = (0, 0)
            class Objects:
                objects = ('PlayButton', 'OptionsButton', 'QuitButton')
                class PlayButton:
                    typ = 'button'
                    res = 'play_button'
                    action = 'play'
                    pos = (40, 360)
                class QuitButton:
                    typ = 'button'
                    res = 'quit_button'
                    action = 'quit'
                    pos = (40, 190)
                class OptionsButton:
                    typ = 'button'
                    res = 'options_button'
                    action = 'open_options_menu'
                    pos = (40, 270)
               
    class Game:
        current_map_id = Save(2)
        maps = ('BlackForest',)
        
        class BlackForest:
            res = 'black_forest'
            space = True
            
            dynamic_layers = True
            animated_layers = False
            bg_pos = (0, 0)
            
            ground_height = 122
            ground_length = 10000
            
            class Objects:
                objects = ('Player',)
                player = 'Player'
                class Player:
                    typ = 'entity'
                    res = 'struct'
                    height = 64
                    width = 50
                    name = 'player'
                    pos_x = Save(0)
                    pos_y = Save(1)
            
            class Triggers:
                triggers = ('LeftBorderTrigger', 'RightBorderTrigger', 'BottomOfWorldTrigger')
                class RightBorderTrigger:
                    id_ = 0
                    top = None
                    left = 1255
                    bottom = None
                    right = None
                    enabled = True
                    class Actions:
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
                
                class LeftBorderTrigger:
                    id_ = 1
                    top = None
                    left = None
                    bottom = None
                    right = 1242
                    enabled = False
                    class Actions:
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
                            
                class BottomOfWorldTrigger:
                    id_ = 2
                    top = -100
                    left = None
                    bottom = None
                    right = None
                    enabled = True
                    class Actions:
                        actions = ('TP',)
                        class TP:
                            typ = 'TPEntity'
                            kwargs = dict(
                                npos=(500, 300),
                                entity_name='player'
                            )
