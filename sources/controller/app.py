# -*- coding:Utf-8 -*-

from .position_handler import StaticPositionHandler


class App:
    def __init__(self, window, model):
        self.window = window
        self.model = model
        self.state = 'in_game'
        self.level = 'black_forest'
        
        dynamic = self.model[self.state][self.level]['dynamic_layers']
        n_layers = self.window.get_number_of_layers(self.level)
        if not dynamic:
            x = self.model[self.state][self.level]['bg_pos_x']
            y = self.model[self.state][self.level]['bg_pos_y']
            if y == 'bottom':
                y = -self.window.res_loader.load(self.level).height * 2 + self.window.screen_rect.height
                y *= 0
            position_handler = StaticPositionHandler((x, y))
        
        pos_hdlrs = (position_handler for _ in range(n_layers))
        
        self.window.add_bg(
            self.level,
            pos_hdlrs,
            dynamic,
            self.model[self.state][self.level]['animated_layers']
        )
        
        self.window.add_entity('warrior', StaticPositionHandler(
            (200, -self.model[self.state][self.level]['ground_height'])))
        
