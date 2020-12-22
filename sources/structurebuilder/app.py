# -*- coding:Utf-8 -*-


import pygame
from pygame.locals import *
from .structbuilder_resource_loader import ResourcesLoader
from .template_reader import TemplateReader
from .tileset import Tileset
import tkinter as tk
from tkinter.filedialog import asksaveasfilename, askopenfilename
import json
import os
import importlib
import sys
from . import plugins

pygame.init()


class App:
    def __init__(self, width, height, res_directory):
        self.screen = pygame.display.set_mode((width, height))
        self.rl = ResourcesLoader(res_directory)
        self.template_reader = TemplateReader()

        self.sleeping = False

        self.order = {k: i for (i, k) in enumerate((K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9))}

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
        self.bindings = {}

        self.last_opened = ''

        self.plugins = {}
        self.load_plugins()

    def load_plugins(self):
        for plugin_name in plugins.plugin_names:
            plugin_module = getattr(plugins, plugin_name.replace('\n', '') + '_plugin')
            class_name = plugin_module.__plugin_name__
            plugin = getattr(plugin_module, class_name)(self)
            self.plugins[plugin_name] = plugin

            for command_name, command in plugin.commands.items():
                if command.binding != ():
                    for bind in command.binding:
                        self.bindings.setdefault(bind, [])
                        self.bindings[bind].append(getattr(plugin, command_name))

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
        pos2 = self.nwpos[0] * self.tw, self.nwpos[1] * self.th

        rect = Rect(*pos1, pos2[0] - pos1[0] + self.tw, pos2[1] - pos1[1] + self.th)
        pygame.draw.rect(self.screen, (152, 156, 170), rect, width=1)

        self.screen.blit(self.secursor_img, pos1)
        self.screen.blit(self.nwcursor_img, pos2)

    def draw_buttons(self, key, x, y):
        if key == K_a:
            self.draw_tile(self.cursor, x, y, 0)
            self.holded_b = K_a

    def apply_template(self, region, width, height):
        for x in range(width):
            for y in range(height):
                self.tab[y + self.sepos[1]][x + self.sepos[0]] = region[x][y]
        self.rebuild()

    def load_template(self, name):
        with open('{BASE}/sources/structurebuilder/templates/'.format(**dict(os.environ)) + name) as file:
            raw_content = file.read()
        dict_data = self.template_reader.read_from_string(raw_content)
        width = abs(self.sepos[0] - self.nwpos[0]) + 1
        height = abs(self.sepos[1] - self.nwpos[1]) + 1

        self.apply_template(self.template_reader.build_region(width, height, dict_data), width, height)

    def flip_selection(self, flip_x, flip_y):
        width = abs(self.sepos[0] - self.nwpos[0]) + 1
        height = abs(self.sepos[1] - self.nwpos[1]) + 1
        new_region = [['NA0000'] * width for _ in range(height)]  # access with new_region[y][x]
        for x in range(width):
            for y in range(height):
                tile_identifier = self.tab[y + self.sepos[1]][x + self.sepos[0]]
                if flip_x:
                    x = width - x - 1
                if flip_y:
                    y = height - y - 1

                code, flip_infos, id_ = tile_identifier[:2], tile_identifier[2:4], tile_identifier[4:]
                flip_x_2, flip_y_2 = flip_infos
                if flip_x:
                    flip_x_2 = int(flip_x_2) * -1 + 1
                if flip_y:
                    flip_y_2 = int(flip_y_2) * -1 + 1
                new_flip_infos = f'{flip_x_2}{flip_y_2}'
                new_tile_identifier = code + new_flip_infos + id_

                new_region[y][x] = new_tile_identifier

        for x in range(width):
            for y in range(height):
                self.tab[y + self.sepos[1]][x + self.sepos[0]] = new_region[y][x]

        self.rebuild()

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
            res, res_name = self.rl.load_from_path(path, return_res_name=True)
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

            self.last_opened = res_name

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

        key_identifier = 'ctrl-' * ctrl + 'shift-' * shift + 'alt-' * alt + pygame.key.name(key)
        commands = self.bindings.get(key_identifier, None)
        if commands is not None:
            for command in commands:
                annotations = command.__annotations__
                kwargs = {}
                if 'key' in annotations:
                    kwargs['key'] = key_identifier
                command(**kwargs)
        else:

            if key == K_a:
                self.draw_tile(self.cursor, shift, ctrl, 0)
                self.holded_b = K_a
            elif key == K_z:
                self.move_gcursor = True
            elif key == K_DELETE:
                self.erase()
                self.holded_b = K_DELETE

            elif key in (K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9):
                with open('{BASE}/sources/structurebuilder/templates.json'.format(**dict(os.environ))) as datafile:
                    data = json.load(datafile)
                i = self.order[key]
                if i < len(data):
                    self.load_template(data[i])

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
                pass

            elif ctrl:
                if key == K_s:
                    self.save()
                elif key == K_l:
                    self.load()
                elif key == K_b:
                    self.rebuild()

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

                elif event.type == ACTIVEEVENT:
                    self.sleeping = not event.gain

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
                        self.tileset_selection_menu_y += 30
                    elif event.type == MOUSEBUTTONDOWN and event.button == 5:
                        self.tileset_selection_menu_y -= 30

            if not self.sleeping:
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



