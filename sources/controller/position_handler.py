# -*- coding:Utf-8 -*-


class StaticPositionHandler:
    def __init__(self, pos):
        self.pos = pos
        
    def update_position(self, entity):
        return self.pos[0] + entity.dec[0], self.pos[1] + entity.dec[1]

