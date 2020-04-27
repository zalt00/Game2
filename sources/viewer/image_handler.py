# -*- coding:Utf-8 -*-

from time import perf_counter
import pygame
pygame.init()


class ImageHandler:
    def __init__(self, res):
        self.res = res
        
    def update_image(self, _, n=1):
        raise NotImplementedError


class BgLayerImageHandler(ImageHandler):
    def update_image(self, sprite, n=1):
        return self.res.layers[sprite.layer]


class EntityImageHandler(ImageHandler):
    def __init__(self, res, end_animation_callback):
        super().__init__(res)
        self.end_animation_callback = end_animation_callback
        self.advance = 0
        self.previous_state = 'idle'
    
    def update_image(self, _):
        raise NotImplementedError


class FBEntityImageHandler(EntityImageHandler):
    def update_image(self, entity, n=1):
        
        if entity.state != self.previous_state:
            self.previous_state = entity.state
            self.advance = 0
        
        a = self.advance // 6
        sheet = self.res.sheets[entity.state]
        if a * self.res.width == sheet.get_width():
            self.advance = 0
            a = 0
            self.end_animation_callback(entity.state)
            return self.update_image(entity)
        else:
            rect = pygame.Rect(a * self.res.width, 0, self.res.width, self.res.height)
            self.advance += 1
            
            img = pygame.transform.scale2x(sheet.subsurface(rect))
    
            if entity.direction == -1:
                return pygame.transform.flip(img, True, False)
            return img
        
        
class TBEntityImageHandler(EntityImageHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def update_image(self, entity, n=1):
        
        if entity.state != self.previous_state:
            self.previous_state = entity.state
            self.advance = 0
        
        self.advance += n
        a = self.advance // 6
        sheet = self.res.sheets[entity.state]
        if a * self.res.width >= sheet.get_width():
            self.advance = 0
            a = 0
            self.end_animation_callback(entity.state)
            return self.update_image(entity)
        else:
            rect = pygame.Rect(a * self.res.width, 0, self.res.width, self.res.height)
            
            img = pygame.transform.scale2x(sheet.subsurface(rect))  # TODO: mettre ça en cache
    
            if entity.direction == -1:
                return pygame.transform.flip(img, True, False)
            return img


class StructureImageHandler(ImageHandler):
    def update_image(self, struct, n=1):
        return self.res.sheets[struct.state]


class ButtonImageHandler(ImageHandler):
    def __init__(self, res, res_loader):
        super().__init__(res)
        self.res_loader = res_loader
        
    def change_res(self, new_res_name):
        self.res = self.res_loader.load(new_res_name)
        
    def update_image(self, button, n=1):
        img = self.res.sheets.get(button.state, None)
        if img is None:
            img = self.res.sheets['idle']
        return img


class TextImageHandler(ImageHandler):
    def __init__(self, res_getter):
        res = res_getter()
        self.res_getter = res_getter
        self.count = 0
        super(TextImageHandler, self).__init__(res)

    def update_image(self, text_object, n=1):
        if self.count == 0:
            self.res = self.res_getter()
            self.count = 0
        else:
            self.count -= 1
        return self.res.sheets['idle']
