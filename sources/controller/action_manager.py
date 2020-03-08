# -*- coding:Utf-8 -*-


from pymunk.vec2d import Vec2d

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

class MenuActionManager(ActionManager):
    MOUSEMOTION = 0
    RIGHT_CLICK = 1
    LEFT_CLICK = 2
    
    def __init__(self, buttons, start_game_callback, quit_game_callback):
        super().__init__()
        self.buttons = buttons
        self.play = start_game_callback
        self.quit = quit_game_callback
        self.do_handlers[self.MOUSEMOTION] = self.update_buttons
        self.do_handlers[self.RIGHT_CLICK] = self.right_click
    
    def update_buttons(self, mouse_pos):
        for button in self.buttons.sprites():
            if button.rect.collidepoint(mouse_pos):
                button.state = 'activated'
            else:
                button.state = 'idle'
                
    def right_click(self, mouse_pos):
        for button in self.buttons.sprites():
            if button.rect.collidepoint(mouse_pos):
                return getattr(self, button.action)()
    

class GameActionManager(ActionManager):
    WALK_RIGHT = 0
    WALK_LEFT = 1
    ATTACK = 2
    ATTACK2 = 3
    GESTURE = 4
    DASH = 5
    JUMP = 6
    RUN = 7
    SAVE = 8
    RETURN_TO_MAIN_MENU = 9
    
    def __init__(self, player, return_to_main_menu=lambda: None, save_callback=lambda: None):
        super().__init__()
        self.player = player
        
        self.save = save_callback
        
        self.do_handlers[self.WALK_RIGHT] = self.walk_right
        self.stop_handlers[self.WALK_RIGHT] = self.stop_walking_right
        
        self.do_handlers[self.WALK_LEFT] = self.walk_left
        self.stop_handlers[self.WALK_LEFT] = self.stop_walking_left     
        
        self.do_handlers[self.RUN] = self.run
        self.stop_handlers[self.RUN] = self.stop_running
        
        self.do_handlers[self.ATTACK] = self.attack
        self.do_handlers[self.ATTACK2] = self.attack2
        
        self.do_handlers[self.GESTURE] = self.gesture
        
        self.do_handlers[self.DASH] = self.dash
        self.do_handlers[self.JUMP] = self.jump
        
        self.do_handlers[self.SAVE] = self.save
        self.do_handlers[self.RETURN_TO_MAIN_MENU] = return_to_main_menu
        
        self.still_walking = False
        self.still_running = False
        
        self.next_state = 'idle'
        self.next_direction = 1
        self.next_tp = Vec2d(0, 0)
    
    def land(self):
        self.player.state = 'land'
        self.next_state = 'idle'
        self.player.is_on_ground = True
    
    def jump(self):
        if self.player.state in ('walk', 'run'):
            self.player.secondary_state = self.player.state
            self.player.state = 'prejump'
        else:
            self.next_state = 'prejump'
        
    def attack(self):
        if self.player.state == 'walk':
            self.player.state = 'attack'
        else:
            self.next_state = 'attack'
    
    def attack2(self):
        if self.player.state == 'walk':
            self.next_tp.x += 8 * self.player.direction
            self.player.state = 'attack2'
            self.next_tp.x += 60 * self.player.direction

        else:
            self.next_state = 'attack2'
            
    def gesture(self):
        if self.player.state == 'walk':
            self.player.state = 'gesture'
        else:
            self.next_state = 'gesture'
    
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
    
    def dash(self):
        if self.player.state == 'walk':
            self.player.state = 'dash'
            self.next_tp.x += 110 * self.player.direction
        else:
            self.next_state = 'dash'

    def set_state(self, *args, **kwargs):
        
        if self.player.state == 'prejump':
            self.next_state = 'jump'
            self.player.secondary_state = ''
            self.player.thrust.y = 500000 * 1
        self.player.direction = self.next_direction
        if self.player.air_control:
            self.player.air_control = self.player.direction
        
        if not self.player.is_on_ground and self.next_state in ('walk', 'run', 'idle', 'prejump'):
            self.next_state = 'fall'
        elif self.next_state == 'prejump':
            if self.still_walking:
                if self.still_running:
                    self.player.secondary_state = 'run'
                else:
                    self.player.secondary_state = 'walk'
            else:
                self.player.secondary_state = ''
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
                    self.next_state = 'fall'
        else:
            self.next_state = 'fall'
            if self.still_walking:
                self.player.air_control = self.player.direction
            


