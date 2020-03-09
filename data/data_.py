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
                    pos = (50, 370)
                class QuitButton:
                    typ = 'button'
                    res = 'quit_button'
                    action = 'quit'
                    pos = (40, 170)
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
            
            dynamic_layers = False
            animated_layers = False
            bg_pos = (0, 0)
            
            ground_height = 122
            ground_length = 10000
            
            class Objects:
                objects = ('Player',)
                player = 'Player'
                class Player:
                    typ = 'entity'
                    res = 'white_guy'
                    height = 64
                    width = 50
                    name = 'player'
                    pos_x = Save(0)
                    pos_y = Save(1)
            
            class Triggers:
                triggers = ('LeftBorderTrigger',)
                class LeftBorderTrigger:
                    form = (False, True, False, True)  # order: top, left, bottom, right
                    top = None
                    left = 1000
                    bottom = None
                    right = 1100
                    enabled = True
                    class Actions:
                        actions = ('Action1',)
                        class MoveCamera:
                            typ = 'absolute_movecam'
                            x = -1000
                            y = 0
                            vx = 100
                            vy = 0
                            fade_in = 5
                            fade_out = 5
                        class EnableRBT:
                            typ = 'enable/disable_trigger'
                            target = 'RightBorderTrigger'
                            disable = False
                        class SelfDisable:
                            typ = 'enable/disable_trigger'
                            targey = 'RightBorderTrigger'
                            disable = False
