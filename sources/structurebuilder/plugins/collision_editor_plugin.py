# -*- coding:Utf-8 -*-

from .plugin_base import PluginMeta, AbstractPlugin, command
import pygame
import json
import os
from collections import deque
pygame.init()

__plugin_name__ = 'CollisionEditorPlugin'


class CollisionEditorPlugin(AbstractPlugin, metaclass=PluginMeta):
    def __init__(self, app):
        super(CollisionEditorPlugin, self).__init__(app)
        self.point_a = []
        self.current_collision_segments = deque()
        self.multiplier = 1
        self.current_color = (1, 151, 181, 255), (237, 68, 99, 255)
        self.current_color_id = 0
        self.colors = [((1, 151, 181, 255), (237, 68, 99, 255)), ((72, 239, 26, 255), (172, 26, 239, 255))]

        self.kp_corres = {  # correspondance entre les touches et l'index de l'info recherchée renvoyée par
            '[7]': (0, 5),  # self.get_positions_info
            '[8]': (1, 5),
            '[9]': (2, 5),
            '[4]': (0, 4),
            '[5]': (1, 4),
            '[6]': (2, 4),
            '[1]': (0, 3),
            '[2]': (1, 3),
            '[3]': (2, 3),
        }

        self.kp_to_direction = {
            '[8]': [0, 1],
            '[6]': [1, 0],
            '[2]': [0, -1],
            '[4]': [-1, 0]
        }

    @command('ctrl-left')
    def move_focus_left(self):
        last_element = self.current_collision_segments.pop()
        self.current_collision_segments.appendleft(last_element)
        self.redraw()

    @command('ctrl-right')
    def move_focus_right(self):
        first_element = self.current_collision_segments.popleft()
        self.current_collision_segments.append(first_element)
        self.redraw()

    @command('[1]', '[2]', '[3]', '[4]', '[5]', '[6]', '[7]', '[8]', '[9]')
    def add_segment_position(self, key: str):
        pos_infos = self.get_position_infos(False)
        ix, iy = self.kp_corres[key]
        self.add_pos(pos_infos[ix], pos_infos[iy])

    @command('n')
    def print_collision_data(self):
        print(*[f'\n- {repr(v[0])}' for v in self.current_collision_segments], sep='')

    @command('space')
    def print_position_infos(self):
        self.get_position_infos()

    @command('ctrl-[4]', 'ctrl-[6]', 'ctrl-[8]', 'ctrl-[2]')
    def move_last_segement(self, key: str):
        self.stretch_last_segment(*self.kp_to_direction[key.split('-')[-1]])

    @command('alt-[4]', 'alt-[6]', 'alt-[8]', 'alt-[2]')
    def stretch_last_segment_point_a(self, key: str):
        dx1, dy1 = self.kp_to_direction[key.split('-')[-1]]
        self.stretch_last_segment(dx1, dy1, 0, 0)

    @command('ctrl-alt-[4]', 'ctrl-alt-[6]', 'ctrl-alt-[8]', 'ctrl-alt-[2]')
    def stretch_last_segment_point_b(self, key: str):
        dx2, dy2 = self.kp_to_direction[key.split('-')[-1]]
        self.stretch_last_segment(0, 0, dx2, dy2)

    @command('[0]')
    def reset_collision_data(self):
        self.current_collision_segments = deque()
        self.point_a = []
        self.app.collision_segments_surf.fill((255, 255, 255, 0))
        print('collision data reset')

    @command('[+]')
    def increase_multiplier(self):
        self.multiplier += 1
        print(f'multiplier: {self.multiplier}')

    @command('[-]')
    def decrease_multiplier(self):
        self.multiplier -= 1
        print(f'multiplier: {self.multiplier}')

    def get_position_infos(self, do_print=True):
        y = self.app.nwpos[1]
        x = (self.app.nwpos[0] + self.app.sepos[0]) / 2
        middle_x = (self.app.cursor[0] - x) * self.app.tw
        bottom_y = (y - self.app.cursor[1]) * self.app.th
        left_x = middle_x - self.app.tw / 2
        right_x = middle_x + self.app.tw / 2
        middle_y = bottom_y + self.app.th / 2
        top_y = bottom_y + self.app.th

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
        y2 = self.app.nwpos[1]
        x2 = (self.app.nwpos[0] + self.app.sepos[0]) / 2

        rl_pos_a = list(segment[0])
        rl_pos_a[0] += (x2 + 0.5) * self.app.tw
        rl_pos_a[1] = -rl_pos_a[1] + (y2 + 1) * self.app.th

        rl_pos_b = list(segment[1])
        rl_pos_b[0] += (x2 + 0.5) * self.app.tw
        rl_pos_b[1] = -rl_pos_b[1] + (y2 + 1) * self.app.th
        pygame.draw.line(self.app.collision_segments_surf, self.current_color[0], rl_pos_a, rl_pos_b, 1)

        self.current_collision_segments.append((segment, (rl_pos_a, rl_pos_b)))
        self.update_color()

    @command('backspace')
    def remove_last_pos(self, do_print=True):
        if len(self.current_collision_segments) != 0:
            _, last_rlpos = self.current_collision_segments.pop()
            rl_pos_a, rl_pos_b = last_rlpos

            pygame.draw.line(self.app.collision_segments_surf, (255, 255, 255, 0), rl_pos_a, rl_pos_b, 1)

            self.update_color()

            if do_print:
                print(*[f'\n- {repr(v[0])}' for v in self.current_collision_segments], sep='')

    @command('ctrl-alt-up')
    def move_all_up(self):
        self.move_all_segments(0, 1)

    @command('ctrl-alt-down')
    def move_all_down(self):
        self.move_all_segments(0, -1)

    @command('ctrl-alt-left')
    def move_all_left(self):
        self.move_all_segments(-1, 0)

    @command('ctrl-alt-right')
    def move_all_right(self):
        self.move_all_segments(1, 0)

    def move_all_segments(self, dx, dy):
        for _ in range(len(self.current_collision_segments)):
            self.stretch_last_segment(dx, dy)
            self.move_focus_left()

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
                pygame.draw.line(self.app.collision_segments_surf, self.current_color[0], rl_pos_a, rl_pos_b, 1)

            _, (rl_pos_a, rl_pos_b) = self.current_collision_segments[-1]
            if identify_last_segment:
                pygame.draw.line(self.app.collision_segments_surf, self.current_color[1], rl_pos_a, rl_pos_b, 1)
            else:
                pygame.draw.line(self.app.collision_segments_surf, self.current_color[0], rl_pos_a, rl_pos_b, 1)

    def redraw(self):
        for _, (rl_pos_a, rl_pos_b) in self.current_collision_segments:
            pygame.draw.line(self.app.collision_segments_surf, self.current_color[0], rl_pos_a, rl_pos_b, 1)
        self.update_color()

    @command('ctrl-alt-s')
    def save_collision_data(self, filename=None):
        if filename is None:
            filename = input('enter the name of the file: ')
        if filename[1] != ':':
            filename = '{BASE}/sources/structurebuilder/collisions_data/'.format(**dict(os.environ)) + filename
        if not filename.endswith('.json'):
            filename += '.json'

        with open(filename, 'w') as file:
            json.dump((list(self.current_collision_segments), self.app.nwpos, self.app.sepos), file)

    @command('ctrl-alt-l')
    def load_collision_data(self):
        filename = input('enter the name of the file: ')
        if filename[1] != ':':
            filename = '{BASE}/sources/structurebuilder/collisions_data/'.format(**dict(os.environ)) + filename
        if not filename.endswith('.json'):
            filename += '.json'

        try:
            with open(filename, 'r') as file:
                self.current_collision_segments, self.app.nwpos, self.app.sepos = json.load(file)
        except FileNotFoundError:
            print('no file has this name')
        else:
            self.current_collision_segments = deque(self.current_collision_segments)
            self.redraw()

    @command('ctrl-alt-q')
    def change_color(self):
        self.update_color(False)
        self.save_collision_data('_cache.json')

        self.current_color_id += 1
        self.current_color_id %= len(self.colors)
        self.current_color = self.colors[self.current_color_id]

        self.current_collision_segments = deque()

        self.redraw()
