# -*- coding:Utf-8 -*-


import pygame
from pygame.locals import *
from viewer.resources_loader import ResourceLoader
import os
pygame.init()


class App:
    def __init__(self, width, height, res_directory):
        self.screen = pygame.display.set_mode((width, height))
        self.rl = ResourceLoader(res_directory)
        
        self.width = width
        
        self.bg = self.screen.copy()
        
        self.tileset = self.rl.load('base_tileset')
        #self.img = pygame.transform.scale2x(pygame.transform.scale2x(self.tileset.sheets['base']))
        self.img = pygame.transform.scale(self.tileset.sheets['base2'], (self.tileset.width * 2, self.tileset.height * 2))
        self.img = pygame.transform.scale2x(self.img)
        
        self.gcursor_img = self.rl.load('cursor').sheets['green']
        self.rcursor_img = self.rl.load('cursor').sheets['red']
        
        self.secursor_img = self.rl.load('cursor').sheets['se']
        self.nwcursor_img = self.rl.load('cursor').sheets['nw']
        
        self.button1down = False
        self.holded_b = 0
        
        self.sepos = [0, 1]
        self.nwpos = [0, 1]
        
        self.gc_dec = 0
        
        self.copied_image = None
        
        self.fps = 200
        self.stop = False
        self.clock = pygame.time.Clock()

        self.tw = 8 * 4
        self.th = 8 * 4
        self.cursor = [0, 0]
        self.tile_rect = Rect(0, 0, self.tw, self.th)
        
        self.nw = self.tw
        
        self.i = 0
        
    def change_tile(self, i):
        self.tile_rect.x = i * self.tw
    
    def draw_tile(self, coords, x_flip, y_flip, rotate):
        try:
            pos = coords[0] * self.tw, coords[1] * self.th
            sub_img = self.img.subsurface(self.tile_rect)
            img = pygame.transform.flip(pygame.transform.rotate(sub_img, rotate), x_flip, y_flip)
            self.bg.blit(img, pos)
        except ValueError:
            pass
        
    def draw_gcursor(self, coords):
        pos = coords[0] * self.tw, coords[1] * self.th
        self.screen.blit(self.gcursor_img, pos)
        
    def draw_rcursor(self, coords):
        pos = coords[0] * self.tw, coords[1] * self.th
        self.screen.blit(self.rcursor_img, pos)
        
    def draw_senw_cursors(self):
        pos1 = self.sepos[0] * self.tw, self.sepos[1] * self.th
        self.screen.blit(self.secursor_img, pos1)
        pos2 = self.nwpos[0] * self.tw, self.nwpos[1] * self.th
        self.screen.blit(self.nwcursor_img, pos2)
        
    def draw_buttons(self, key, x, y):
        a = False
        if key == K_a:
            self.draw_tile(self.cursor, x, y, 0)
            self.holded_b = K_a
            a = True
        elif key == K_s:
            self.draw_tile(self.cursor, x, y, 90)
            self.holded_b = K_s
            a = True
        elif key == K_d:
            self.draw_tile(self.cursor, x, y, -90)
            self.holded_b = K_d
            a = True
        
    def copy(self):
        top = self.sepos[1] * self.th
        left = self.sepos[0] * self.tw
        width = (self.nwpos[0] + 1) * self.tw - left
        height = (self.nwpos[1] + 1) * self.th - top
        r = pygame.Rect(left, top, width, height)
        self.copied_image = self.bg.subsurface(r).copy()
        
    def paste(self):
        if self.copied_image is not None:
            top = self.sepos[1] * self.th
            left = self.sepos[0] * self.tw
            self.bg.blit(self.copied_image, (left, top))
        
    def run(self):
        while not self.stop:
            for event in pygame.event.get():
                mods = pygame.key.get_mods()
                y = x = False
                if mods & KMOD_SHIFT:
                    x = True
                if mods & KMOD_CTRL:
                    y = True
                    
                if event.type == QUIT:
                    self.stop = True
                elif event.type == KEYDOWN:
                    if self.draw_buttons(event.key, x, y):
                        pass
                    elif event.key == K_q:
                        self.i -= 1
                        self.change_tile(self.i)
                    elif event.key == K_r:
                        self.i += 5
                        self.change_tile(self.i)
                    elif event.key == K_e:
                        self.i -= 5
                        self.change_tile(self.i)
                    elif event.key == K_w:
                        self.i += 1
                        self.change_tile(self.i)
                        
                    elif event.key == K_UP:
                        self.cursor[1] -= 1
                    elif event.key == K_DOWN:
                        self.cursor[1] += 1
                    elif event.key == K_LEFT:
                        self.cursor[0] -= 1
                    elif event.key == K_RIGHT:
                        self.cursor[0] += 1
                        
                    elif event.key == K_c:
                        if y:
                            self.copy()
                    elif event.key == K_v:
                        if y:
                            self.paste()
                        
                    elif event.key == K_0:
                        self.i = 0
                        self.change_tile(self.i)
                        
                    elif event.key == K_RETURN:
                        top = self.sepos[1] * self.th
                        left = self.sepos[0] * self.tw
                        width = (self.nwpos[0] + 1) * self.tw - left
                        height = (self.nwpos[1] + 1) * self.th - top
                        r = pygame.Rect(left, top, width, height)
                        
                        i = 2
                        stop = False
                        while not stop:
                            try:
                                os.rename('StructureBuilder/save/save.png', f'StructureBuilder/save/save{i}.png')
                            except FileExistsError:
                                i += 1
                            except FileNotFoundError:
                                stop = True
                            else:
                                stop = True
                        
                        pygame.image.save(self.bg.subsurface(r), "StructureBuilder/save/save.png")
                        print('image saved')
                    
                    elif event.key == K_SPACE:
                        top = self.sepos[1] * self.th
                        left = self.sepos[0] * self.tw
                        img = pygame.image.load('StructureBuilder/save/save.png').convert()
                        self.bg.blit(img, (left, top))
                    
                elif event.type == KEYUP:
                    self.holded_b = 0
                
                elif event.type == MOUSEBUTTONDOWN:
                    coords = event.pos[0] // self.tw, event.pos[1] // self.th
                    if event.button == 1:
                        self.button1down = True
                        self.cursor[:] = coords
                    elif event.button == 4:
                        self.i += 1
                        self.change_tile(self.i)
                    elif event.button == 5:
                        self.i -= 1
                        self.change_tile(self.i)
                    elif event.button == 3:
                        if mods & KMOD_SHIFT:
                            self.nwpos[:] = coords
                            if self.nwpos[0] < self.sepos[0]:
                                self.sepos[0] = self.nwpos[0]
                            if self.nwpos[1] < self.sepos[1]:
                                self.sepos[1] = self.nwpos[1]
                        else:
                            self.sepos[:] = coords
                            if self.nwpos[0] < self.sepos[0]:
                                self.nwpos[0] = self.sepos[0]
                            if self.nwpos[1] < self.sepos[1]:
                                self.nwpos[1] = self.sepos[1]
                            
                elif event.type ==  MOUSEBUTTONUP:
                    if event.button == 1:
                        self.button1down = False
                
                elif event.type == MOUSEMOTION:
                    coords = event.pos[0] // self.tw, event.pos[1] // self.th                    
                    if self.button1down:
                        self.cursor[:] = coords
                        if self.holded_b:
                            self.draw_buttons(self.holded_b, x, y)
                    
            self.screen.blit(self.bg, (0, 0))
            
            if self.i > self.nw:
                a = (self.nw - self.i + 1)
                self.gc_dec = a
                self.screen.blit(self.img, (a * self.tw, 0))
            else:
                self.gc_dec = 0
                self.screen.blit(self.img, (0, 0))
            self.draw_gcursor((self.i + self.gc_dec, 0))
            self.draw_rcursor(self.cursor)
            self.draw_senw_cursors()
            self.clock.tick(self.fps)
            
            pygame.display.flip()
    
