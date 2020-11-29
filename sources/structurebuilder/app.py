# -*- coding:Utf-8 -*-


import pygame
from pygame.locals import *
from .structbuilder_resource_loader import ResourcesLoader
import tkinter as tk
from tkinter.filedialog import asksaveasfilename, askopenfilename
import json
import os
pygame.init()


class Tileset:
    def __init__(self, img, size, eraser, random_icon, tw, th, code):
        self.tw = tw
        self.th = th
        self.base_img = img
        self.size = size
        self.eraser = eraser
        self.random_icon = random_icon
        self.code = code

        self.tile_size = self.tw, self.th

        r = self.base_img.get_rect()
        r.width += tw * 2

        new_img = pygame.Surface((r.width, r.height), SRCALPHA)
        new_img.blit(self.base_img, (0, 0))
        new_img.blit(self.eraser, (size * tw, 0))
        new_img.blit(self.random_icon, ((size + 1) * tw, 0))

        self.img = new_img

        self.tile_data = []
        for i in range(size):
            self.tile_data.append(code + '{}{}' + '{:0>2}'.format(i))
        self.tile_data.append('NA0000')
        self.tile_data.append(code + '{}{}' + 'RD')

        self.index_random = len(self.tile_data) - 1

class App:
    def __init__(self, width, height, res_directory):
        self.screen = pygame.display.set_mode((width, height))
        self.rl = ResourcesLoader(res_directory)
        
        self.width = width

        self.tab = [['NA0000'] * 100 for _ in range(100)]

        self.player_records = self.rl.load('structure_builder_utils/player_records.obj')
        self.jump_record = self.player_records.sheets['jump']
        self.walkoff_record = self.player_records.sheets['walkoff']
        self.dash_record = self.player_records.sheets['dash']
        self.show_jump_record = False
        self.show_walkoff_record = False
        self.show_dash_record = False
        self.flip_record = False

        self.bg = self.screen.copy().convert_alpha()
        self.bg.fill((255, 255, 255, 0))

        self.collision_segments_surf = self.bg.copy()

        self.palette = self.rl.load('forest/structure_builder_forest_tilesets.stsp')

        self.eraser_img = self.palette.eraser
        self.random_icon = self.palette.random_icon

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

        self.kp_corres = {  # correspondance entre les touches et l'index de l'info recherchée renvoyée par
            K_KP7: (0, 5),  # self.get_positions_info
            K_KP8: (1, 5),
            K_KP9: (2, 5),
            K_KP4: (0, 4),
            K_KP5: (1, 4),
            K_KP6: (2, 4),
            K_KP1: (0, 3),
            K_KP2: (1, 3),
            K_KP3: (2, 3),
        }

        self.kp_to_direction = {
            K_KP8: [0, 1],
            K_KP6: [1, 0],
            K_KP2: [0, -1],
            K_KP4: [-1, 0]
        }

        self.multiplier = 1

        self.point_a = []
        self.current_collision_segments = []

        self.current_color = (1, 151, 181, 255), (237, 68, 99, 255)
        self.current_color_id = 0
        self.colors = [((1, 151, 181, 255), (237, 68, 99, 255)), ((72, 239, 26, 255), (172, 26, 239, 255))]

        self.tileset_selection_menu = pygame.Surface((width, len(self.palette.tilesets_data) * self.palette.th * 2),
                                                     SRCALPHA)
        self.tileset_selection_menu.fill((255, 255, 255, 0))

        self.tileset_selection_menu_bg = self.tileset_selection_menu.copy()
        self.tileset_selection_menu_bg.fill((190, 190, 190))

        self.tileset_selection_menu_y = 0

        self.possible_tilesets = None

        self.is_selecting_tileset = False
        self.current_selection = -1

        self.eraser = self.tileset = self.tile_data = self.img = None

        self.move_gcursor = False

        self.open_tileset_selection_menu()

    def open_tileset_selection_menu(self):
        self.is_selecting_tileset = True
        colors = (190, 190, 190), (200, 200, 200)
        color_id = 0
        self.possible_tilesets = [data + (code,) for (code, data) in self.palette.tilesets_data.items()]
        for i, ts_data in enumerate(self.possible_tilesets):
            r = Rect(0, i * self.th, 1200, self.th)
            self.tileset_selection_menu_bg.fill(colors[color_id], r)
            color_id ^= 1

            img = ts_data[0]
            r = img.get_rect()
            img = pygame.transform.scale(img, (r.width * 2, r.height * 2))
            self.tileset_selection_menu.blit(img, (0, i * self.th))

    def get_selected_tileset(self, y):
        if self.is_selecting_tileset:
            i = (y - self.tileset_selection_menu_y) // self.tw
            if 0 <= i < len(self.possible_tilesets):
                return self.possible_tilesets[i], i
        raise IndexError('no tileset at this location')

    def change_tileset2(self, res_name):
        self.tileset = self.rl.load(res_name)
        rect = self.tileset.img.get_rect()
        self.img = pygame.transform.scale(self.tileset.img, (rect.width * 2, rect.height * 2))

        self.tile_data = self.tileset.tile_data
        self.eraser = self.tileset.eraser

    def change_tileset(self, i):
        if self.is_selecting_tileset:
            img, size, code = self.possible_tilesets[i]
            tileset = Tileset(img, size, self.eraser_img, self.random_icon, self.tw / 2, self.th / 2, code)
            rect = tileset.img.get_rect()
            self.img = pygame.transform.scale(tileset.img, (rect.width * 2, rect.height * 2))
            self.tileset = tileset
            self.eraser = size

            self.tile_data = self.tileset.tile_data

    def change_tile(self, i):
        self.tile_rect.x = i * self.tw

    def draw_tile(self, coords, x_flip, y_flip, rotate):
        try:
            sub_img = self.img.subsurface(self.tile_rect)
        except ValueError:
            pass
        else:
            i = self.tile_rect.x // self.tw
            pos = coords[0] * self.tw, coords[1] * self.th
            if i != self.tileset.index_random:
                img = pygame.transform.flip(pygame.transform.rotate(sub_img, rotate), x_flip, y_flip)
            else:
                img = pygame.transform.flip(pygame.transform.rotate(
                    self.img.subsurface(Rect(0, 0, self.tw, self.th)), rotate), x_flip, y_flip)

            r = Rect(*pos, self.tile_rect.width, self.tile_rect.height)

            self.bg.fill((255, 255, 255, 0), r)
            self.bg.blit(img, r)

            s = self.tile_data[i]
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
            width = len(self.copied_subtab[0])
            height = len(self.copied_subtab)
            lines = self.tab[self.sepos[1]:self.sepos[1] + height]

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
            int(tw * w), int(th * h), int(tw * w // 2), 0, 2, int(h), s)
        return txt

    def erase(self):
        if self.eraser is not None:
            self.change_tile(self.eraser)
            self.draw_tile(self.cursor, 0, 0, 0)
            self.change_tile(self.i)

    def keydown(self, key, shift, ctrl, alt):
        if key == K_a:
            self.draw_tile(self.cursor, shift, ctrl, 0)
            self.holded_b = K_a
        elif key == K_z:
            self.move_gcursor = True
        elif key == K_DELETE:
            self.erase()
            self.holded_b = K_DELETE

        elif key == K_j:
            self.show_jump_record ^= True
        elif key == K_h:
            self.show_walkoff_record ^= True
        elif key == K_g:
            self.show_dash_record ^= True
        elif key == K_k:
            self.flip_record ^= True
        elif key == K_F1:
            self.open_tileset_selection_menu()

        elif key == K_UP:
            self.cursor[1] -= 1
        elif key == K_DOWN:
            self.cursor[1] += 1
        elif key == K_LEFT:
            self.cursor[0] -= 1
        elif key == K_RIGHT:
            self.cursor[0] += 1

        elif alt:
            if ctrl:
                if key == K_s:
                    self.save_collision_data()
                elif key == K_l:
                    self.load_collision_data()
                elif key == K_q:
                    self.change_color()

            if key in (K_KP4, K_KP6, K_KP8, K_KP2):
                if ctrl:
                    dx2, dy2 = self.kp_to_direction[key]
                    self.stretch_last_segment(0, 0, dx2, dy2)
                else:
                    dx1, dy1 = self.kp_to_direction[key]
                    self.stretch_last_segment(dx1, dy1, 0, 0)

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

            elif key in (K_KP4, K_KP6, K_KP8, K_KP2):
                self.stretch_last_segment(*self.kp_to_direction[key])

        elif key == K_0:
            self.i = 0
            self.change_tile(self.i)

        elif key == K_SPACE:
            self.get_position_infos()

        elif key == K_n:
            print(*[f'\n- {repr(v[0])}' for v in self.current_collision_segments], sep='')

        elif key in (K_KP1, K_KP2, K_KP3, K_KP4, K_KP5, K_KP6, K_KP7, K_KP8, K_KP9):
            pos_infos = self.get_position_infos(False)
            ix, iy = self.kp_corres[key]
            self.add_pos(pos_infos[ix], pos_infos[iy])

        elif key == K_BACKSPACE:
            self.remove_last_pos()

        elif key == K_KP0:
            self.current_collision_segments = []
            self.point_a = []

        elif key == K_c:
            self.collision_segments_surf.fill((255, 255, 255, 0))

        elif key == K_KP_PLUS:
            self.multiplier += 1
            print(f'multiplier: {self.multiplier}')

        elif key == K_KP_MINUS:
            self.multiplier -= 1
            print(f'multiplier: {self.multiplier}')

    def run(self):
        while not self.stop:
            for event in pygame.event.get():
                mods = pygame.key.get_mods()
                shift = ctrl = alt = False
                if mods & KMOD_SHIFT:
                    shift = True
                if mods & KMOD_CTRL:
                    ctrl = True
                if mods & KMOD_ALT:
                    alt = True
                    
                if event.type == QUIT:
                    self.stop = True

                elif not self.is_selecting_tileset:
                    if event.type == KEYDOWN:
                        self.keydown(event.key, shift, ctrl, alt)

                    elif event.type == KEYUP:
                        self.holded_b = 0

                    elif event.type == MOUSEBUTTONDOWN:
                        coords = event.pos[0] // self.tw, event.pos[1] // self.th
                        if event.button == 1:
                            if not self.move_gcursor:
                                self.button1down = True
                                self.cursor[:] = coords
                            else:
                                self.move_gcursor = False
                                self.i = coords[0] - self.gc_dec
                                self.change_tile(self.i)
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
                                self.keydown(self.holded_b, shift, ctrl, alt)

                else:
                    if event.type == MOUSEMOTION:
                        try:
                            new_selection = self.get_selected_tileset(event.pos[1])
                        except IndexError:
                            new_selection = None, None
                        else:
                            r = Rect(0, new_selection[1] * self.th, 1200, self.th)
                            color = ((147, 162, 191), (157, 172, 201))[new_selection[1] % 2]
                            self.tileset_selection_menu_bg.fill(color, r)

                        if self.current_selection != -1 and self.current_selection != new_selection[1]:
                            color = ((190, 190, 190), (200, 200, 200))[self.current_selection % 2]
                            r = Rect(0, self.current_selection * self.th, 1200, self.th)
                            self.tileset_selection_menu_bg.fill(color, r)
                            self.current_selection = -1
                        if new_selection[1] is not None:
                            self.current_selection = new_selection[1]

                    elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                        if self.current_selection != -1:
                            self.change_tileset(self.current_selection)
                            self.is_selecting_tileset = False
                    elif event.type == MOUSEBUTTONDOWN and event.button == 4:
                        self.tileset_selection_menu_y += 16
                    elif event.type == MOUSEBUTTONDOWN and event.button == 5:
                        self.tileset_selection_menu_y -= 16

            self.screen.fill((190, 190, 190))
            if self.is_selecting_tileset:
                self.screen.blit(self.tileset_selection_menu_bg, (0, self.tileset_selection_menu_y))
                self.screen.blit(self.tileset_selection_menu, (0, self.tileset_selection_menu_y))

            else:
                self.screen.blit(self.bg, (0, 0))
                self.screen.blit(self.collision_segments_surf, (0, 0))

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
                if not self.move_gcursor:
                    self.draw_gcursor((self.i + self.gc_dec, 0))
                self.draw_rcursor(self.cursor)
                self.draw_senw_cursors()

                if self.show_jump_record:
                    x, y = pygame.mouse.get_pos()
                    if self.flip_record:
                        self.screen.blit(pygame.transform.flip(self.jump_record, 1, 0), (x - 250, y - 250))
                    else:
                        self.screen.blit(self.jump_record, (x - 250, y - 250))

                if self.show_walkoff_record:
                    x, y = pygame.mouse.get_pos()
                    if self.flip_record:
                        self.screen.blit(pygame.transform.flip(self.walkoff_record, 1, 0), (x - 250, y - 250))
                    else:
                        self.screen.blit(self.walkoff_record, (x - 250, y - 250))

                if self.show_dash_record:
                    x, y = pygame.mouse.get_pos()
                    if self.flip_record:
                        self.screen.blit(pygame.transform.flip(self.dash_record, 1, 0), (x - 250, y - 250))
                    else:
                        self.screen.blit(self.dash_record, (x - 250, y - 250))

            self.clock.tick(self.fps)
            
            pygame.display.flip()

    def get_position_infos(self, do_print=True):
        y = self.nwpos[1]
        x = (self.nwpos[0] + self.sepos[0]) / 2
        middle_x = (self.cursor[0] - x) * self.tw
        bottom_y = (y - self.cursor[1]) * self.th
        left_x = middle_x - self.tw / 2
        right_x = middle_x + self.tw / 2
        middle_y = bottom_y + self.th / 2
        top_y = bottom_y + self.th

        if do_print:
            print(f'\nX: left = {left_x}, middle = {middle_x}, right = {right_x}')
            print(f'Y: bottom = {bottom_y}, middle = {middle_y}, top = {top_y}')

        return left_x, middle_x, right_x, bottom_y, middle_y, top_y

    def add_pos(self, x, y):
        if len(self.point_a) == 0:
            self.point_a = [x, y]
        else:
            segment = [self.point_a, [x, y]]

            self.add_segment(segment)

            self.point_a = []
            print(*[f'\n- {repr(v[0])}' for v in self.current_collision_segments], sep='')

    def add_segment(self, segment):
        y2 = self.nwpos[1]
        x2 = (self.nwpos[0] + self.sepos[0]) / 2

        rl_pos_a = list(segment[0])
        rl_pos_a[0] += (x2 + 0.5) * self.tw
        rl_pos_a[1] = -rl_pos_a[1] + (y2 + 1) * self.th

        rl_pos_b = list(segment[1])
        rl_pos_b[0] += (x2 + 0.5) * self.tw
        rl_pos_b[1] = -rl_pos_b[1] + (y2 + 1) * self.th
        pygame.draw.line(self.collision_segments_surf, self.current_color[0], rl_pos_a, rl_pos_b, 1)

        self.current_collision_segments.append((segment, (rl_pos_a, rl_pos_b)))
        self.update_color()

    def remove_last_pos(self, do_print=True):
        if len(self.current_collision_segments) != 0:
            _, last_rlpos = self.current_collision_segments.pop()
            rl_pos_a, rl_pos_b = last_rlpos

            pygame.draw.line(self.collision_segments_surf, (255, 255, 255, 0), rl_pos_a, rl_pos_b, 1)

            self.update_color()

            if do_print:
                print(*[f'\n- {repr(v[0])}' for v in self.current_collision_segments], sep='')

    def stretch_last_segment(self, dx1, dy1, dx2=None, dy2=None):
        if len(self.current_collision_segments):
            last_segment, _ = self.current_collision_segments[-1]
            self.remove_last_pos(False)

            if dx2 is None:
                dx2 = dx1
            if dy2 is None:
                dy2 = dy1

            last_segment[0][0] += dx1 * self.multiplier
            last_segment[1][0] += dx2 * self.multiplier
            last_segment[0][1] += dy1 * self.multiplier
            last_segment[1][1] += dy2 * self.multiplier
            self.add_segment(last_segment)

            self.redraw()

            print(*[f'\n- {repr(v[0])}' for v in self.current_collision_segments], sep='')

    def update_color(self, identify_last_segment=True):
        if len(self.current_collision_segments) != 0:
            if len(self.current_collision_segments) > 1:
                _, (rl_pos_a, rl_pos_b) = self.current_collision_segments[-2]
                pygame.draw.line(self.collision_segments_surf, self.current_color[0], rl_pos_a, rl_pos_b, 1)

            _, (rl_pos_a, rl_pos_b) = self.current_collision_segments[-1]
            if identify_last_segment:
                pygame.draw.line(self.collision_segments_surf, self.current_color[1], rl_pos_a, rl_pos_b, 1)
            else:
                pygame.draw.line(self.collision_segments_surf, self.current_color[0], rl_pos_a, rl_pos_b, 1)

    def redraw(self):
        for _, (rl_pos_a, rl_pos_b) in self.current_collision_segments:
            pygame.draw.line(self.collision_segments_surf, self.current_color[0], rl_pos_a, rl_pos_b, 1)
        self.update_color()

    def save_collision_data(self, filename=None):
        if filename is None:
            filename = input('enter the name of the file: ')
        if filename[1] != ':':
            filename = '{BASE}/sources/structurebuilder/'.format(**dict(os.environ)) + filename
        if not filename.endswith('.json'):
            filename += '.json'

        with open(filename, 'w') as file:
            json.dump((self.current_collision_segments, self.nwpos, self.sepos), file)

    def load_collision_data(self):
        filename = input('enter the name of the file: ')
        if filename[1] != ':':
            filename = '{BASE}/sources/structurebuilder/'.format(**dict(os.environ)) + filename
        if not filename.endswith('.json'):
            filename += '.json'

        try:
            with open(filename, 'r') as file:
                self.current_collision_segments, self.nwpos, self.sepos = json.load(file)
        except FileNotFoundError:
            print('no file has this name')
        else:
            self.redraw()

    def change_color(self):
        self.update_color(False)
        self.save_collision_data('_cache.json')

        self.current_color_id += 1
        self.current_color_id %= len(self.colors)
        self.current_color = self.colors[self.current_color_id]

        self.current_collision_segments = []

        self.redraw()



