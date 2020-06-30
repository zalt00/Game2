# -*- coding:Utf-8 -*-


import pygame
from pygame.locals import *
from viewer.resources_loader import ResourcesLoader2
import tkinter as tk
from tkinter.filedialog import asksaveasfilename, askopenfilename
pygame.init()


class App:
    def __init__(self, width, height, res_directory):
        self.screen = pygame.display.set_mode((width, height))
        self.rl = ResourcesLoader2(res_directory)
        
        self.width = width

        self.tab = [['NA0000'] * 50 for _ in range(50)]

        self.bg = self.screen.copy().convert_alpha()
        self.bg.fill((255, 255, 255, 0))

        self.palette = self.rl.load('forest/forest_structure_tilesets.stsp')

        self.tileset = self.rl.load('forest/basetileset.ts')
        self.img = pygame.transform.scale2x(self.tileset.img)

        self.tile_data = self.tileset.tile_data
        self.eraser = self.tileset.eraser
        
        self.gcursor_img = self.rl.load('cursor.obj').sheets['green']
        self.rcursor_img = self.rl.load('cursor.obj').sheets['red']
        
        self.secursor_img = self.rl.load('cursor.obj').sheets['se']
        self.nwcursor_img = self.rl.load('cursor.obj').sheets['nw']
        
        self.button1down = False
        self.holded_b = 0
        
        self.sepos = [0, 1]
        self.nwpos = [0, 1]
        
        self.gc_dec = 0
        
        self.copied_image = None
        self.copied_subtab = None
        
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
            sub_img = self.img.subsurface(self.tile_rect)
        except ValueError:
            pass
        else:
            pos = coords[0] * self.tw, coords[1] * self.th
            img = pygame.transform.flip(pygame.transform.rotate(sub_img, rotate), x_flip, y_flip)

            r = Rect(*pos, self.tile_rect.width, self.tile_rect.height)

            self.bg.fill((255, 255, 255, 0), r)
            self.bg.blit(img, r)

            s = self.tile_data[self.tile_rect.x // self.tw]
            self.tab[coords[1]][coords[0]] = s.format(int(x_flip), int(y_flip))

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
        if key == K_a:
            self.draw_tile(self.cursor, x, y, 0)
            self.holded_b = K_a

    def copy(self):
        top = self.sepos[1] * self.th
        left = self.sepos[0] * self.tw
        width = (self.nwpos[0] + 1) * self.tw - left
        height = (self.nwpos[1] + 1) * self.th - top
        r = pygame.Rect(left, top, width, height)
        self.copied_image = self.bg.subsurface(r).copy()

        lines = self.tab[self.sepos[1]:self.nwpos[1] + 1]
        sub_tab = []
        for line in lines:
            sub_tab.append(line[self.sepos[0]:self.nwpos[0] + 1])
        self.copied_subtab = sub_tab
        print(sub_tab)

    def paste(self):
        if self.copied_image is not None and self.copied_subtab is not None:
            top = self.sepos[1] * self.th
            left = self.sepos[0] * self.tw
            self.bg.blit(self.copied_image, (left, top))

            lines = self.tab[self.sepos[1]:self.nwpos[1] + 1]
            width = len(self.copied_subtab[0])

            for i, line in enumerate(lines):
                line[self.sepos[0]:self.sepos[0] + width] = self.copied_subtab[i]

    def save(self):
        lines = self.tab[self.sepos[1]:self.nwpos[1] + 1]
        sub_tab = []
        for line in lines:
            sub_tab.append(line[self.sepos[0]:self.nwpos[0] + 1])

        root = tk.Tk()
        filename = asksaveasfilename(parent=root, filetypes=[("structure", "*.st"), ("all files", "*")])
        root.destroy()

        if filename:
            if not filename.endswith('.st'):
                filename += '.st'
            txt = self.generate_structure_file_content(sub_tab)
            with open(filename, 'w') as file:
                file.write(txt)

    def load(self):
        root = tk.Tk()
        path = askopenfilename(parent=root, filetypes=[("structure", "*.st"), ("all files", "*")])
        root.destroy()

        if path:
            res = self.rl.load_from_path(path)
            sb = res.string_buffer
            subtab = [line.split(';') for line in sb.splitlines()]
            img = self.palette.build(res)

            top = self.sepos[1] * self.th
            left = self.sepos[0] * self.tw
            self.bg.blit(img, (left, top))

            width = len(subtab[0])
            height = len(subtab)
            lines = self.tab[self.sepos[1]:self.sepos[1] + height]
            for i, line in enumerate(lines):
                line[self.sepos[0]:self.sepos[0] + width] = subtab[i]

    def rebuild(self):
        top = self.sepos[1] * self.th
        left = self.sepos[0] * self.tw
        width = (self.nwpos[0] + 1) * self.tw - left
        height = (self.nwpos[1] + 1) * self.th - top
        r = pygame.Rect(left, top, width, height)

        lines = self.tab[self.sepos[1]:self.nwpos[1] + 1]
        subtab = []
        for line in lines:
            subtab.append(line[self.sepos[0]:self.nwpos[0] + 1])

        txt = self.generate_structure_file_content(subtab)
        res = self.rl.load_structure_from_string(txt)
        img = self.palette.build(res)
        self.bg.fill((190, 190, 190), r)
        self.bg.blit(img, r)

    def generate_structure_file_content(self, sub_tab):
        s = '\n'.join((';'.join(line) for line in sub_tab))
        tw, th = self.tileset.tile_size
        w = len(sub_tab[0])
        h = len(sub_tab)
        txt = "dimensions={} {}\ndec={} {}\nscale={}\nlength={}\nstring-buffer:\n{}".format(
            tw * w, th * h, tw * w // 2, 0, 2, h, s)
        return txt

    def erase(self):
        if self.eraser is not None:
            self.change_tile(self.eraser)
            self.draw_tile(self.cursor, 0, 0, 0)
            self.change_tile(self.i)

    def keydown(self, key, shift, ctrl):
        if key == K_a:
            self.draw_tile(self.cursor, shift, ctrl, 0)
            self.holded_b = K_a
        elif key == K_DELETE:
            self.erase()
            self.holded_b = K_DELETE

        elif key == K_u:
            self.i -= 1
            self.change_tile(self.i)
        elif key == K_p:
            self.i += 5
            self.change_tile(self.i)
        elif key == K_o:
            self.i -= 5
            self.change_tile(self.i)
        elif key == K_i:
            self.i += 1
            self.change_tile(self.i)

        elif key == K_UP:
            self.cursor[1] -= 1
        elif key == K_DOWN:
            self.cursor[1] += 1
        elif key == K_LEFT:
            self.cursor[0] -= 1
        elif key == K_RIGHT:
            self.cursor[0] += 1

        elif ctrl:
            if key == K_c:
                self.copy()
            elif key == K_v:
                self.paste()
            elif key == K_s:
                self.save()
            elif key == K_l:
                self.load()
            elif key == K_b:
                self.rebuild()

        elif key == K_0:
            self.i = 0
            self.change_tile(self.i)

        elif key == K_SPACE:
            self.get_position_infos()

    def run(self):
        while not self.stop:
            for event in pygame.event.get():
                mods = pygame.key.get_mods()
                shift = ctrl = False
                if mods & KMOD_SHIFT:
                    shift = True
                if mods & KMOD_CTRL:
                    ctrl = True
                    
                if event.type == QUIT:
                    self.stop = True

                elif event.type == KEYDOWN:
                    self.keydown(event.key, shift, ctrl)

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
                        if shift:
                            self.nwpos[:] = coords
                            if self.nwpos[0] < self.sepos[0]:
                                self.sepos[0], self.nwpos[0] = self.nwpos[0], self.sepos[0]
                            if self.nwpos[1] < self.sepos[1]:
                                self.sepos[1], self.nwpos[1] = self.nwpos[1], self.sepos[1]
                        else:
                            self.sepos[:] = coords
                            if self.nwpos[0] < self.sepos[0]:
                                self.sepos[0], self.nwpos[0] = self.nwpos[0], self.sepos[0]
                            if self.nwpos[1] < self.sepos[1]:
                                self.sepos[1], self.nwpos[1] = self.nwpos[1], self.sepos[1]
                            
                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        self.button1down = False
                
                elif event.type == MOUSEMOTION:
                    coords = event.pos[0] // self.tw, event.pos[1] // self.th                    
                    if self.button1down:
                        self.cursor[:] = coords
                        if self.holded_b:
                            self.keydown(self.holded_b, shift, ctrl)

            self.screen.fill((190, 190, 190))
            self.screen.blit(self.bg, (0, 0))

            if self.i < 0:
                self.i = 0
                self.change_tile(self.i)

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

    def get_position_infos(self):
        y = self.nwpos[1]
        x = (self.nwpos[0] + self.sepos[0]) / 2
        middle_x = (self.cursor[0] - x) * self.tw
        bottom_y = (y - self.cursor[1]) * self.th
        left_x = middle_x - self.tw / 2
        right_x = middle_x + self.tw / 2
        middle_y = bottom_y + self.th / 2
        top_y = bottom_y + self.th

        print(f'\nX: left = {left_x}, middle = {middle_x}, right = {right_x}')
        print(f'Y: bottom = {bottom_y}, middle = {middle_y}, top = {top_y}')

