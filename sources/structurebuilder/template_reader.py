# -*- coding:Utf-8 -*-

import re


class TemplateReader:
    regex = re.compile(r'[a-z:-]\n+([A-Z0-9;\n]*)')
    order = 'top-left', 'bottom-left', 'top-right', 'bottom-right', 'filling'

    def read_from_string(self, s):
        data = self.regex.findall(s)
        dict_data = {}
        for i, s in enumerate(data):
            if s:
                if s.endswith('\n'):
                    s = s[:-1]
                lines = [line.split(';') for line in s.split('\n')]
                dict_data[self.order[i]] = lines
            else:
                dict_data[self.order[i]] = []
        return dict_data

    def build_region(self, width, height, data):
        region = [["NA0000"] * height for _ in range(width)]  # access with region[x][y]

        if data['top-left']:
            d = data['top-left']
            self._build_subregion(d, width, height, region, self._topleft_setter)
        if data['bottom-left']:
            d = data['bottom-left']
            self._build_subregion(d, width, height, region, self._bottomleft_setter)
        if data['top-right']:
            d = data['top-right']
            self._build_subregion(d, width, height, region, self._topright_setter)
        if data['bottom-right']:
            d = data['bottom-right']
            self._build_subregion(d, width, height, region, self._bottomright_setter)

        if data['filling']:
            d = data['filling']
            if len(d) == 1:
                w = min(len(d[0]), width)
                for x in range(w):
                    for y in range(height):
                        if region[x][y] == 'NA0000':
                            region[x][y] = d[0][x]

            else:
                h = min(len(d), height)
                for x in range(width):
                    for y in range(h):
                        if region[x][y] == 'NA0000':
                            region[x][y] = d[y][0]

        return region

    @staticmethod
    def region_to_string(region, width, height):
        txt = ''
        for y in range(height):
            if y != 0:
                txt += '\n'
            for x in range(width):
                if x != 0:
                    txt += ';'
                txt += region[x][y]
        return txt

    @staticmethod
    def _topleft_setter(region, x, y, d, w, h, rw, rh):
        region[x][y] = d[y][x]

    @staticmethod
    def _bottomleft_setter(region, x, y, d, w, h, rw, rh):
        if region[x][rh - h + y] == 'NA0000':
            region[x][rh - h + y] = d[y][x]

    @staticmethod
    def _topright_setter(region, x, y, d, w, h, rw, rh):
        if region[len(d[0]) - w + x][y] == 'NA0000':
            region[len(d[0]) - w + x][y] = d[y][x]

    @staticmethod
    def _bottomright_setter(region, x, y, d, w, h, rw, rh):
        if region[rw - w + x][rh - h + y] == 'NA0000':
            region[rw - w + x][rh - h + y] = d[y][x]

    @staticmethod
    def _build_subregion(d, width, height, region, setter):
        w = len(d[0])
        h = len(d)
        for x in range(min(w, width)):
            for y in range(min(h, height)):
                setter(region, x, y, d, min(w, width), min(h, height), width, height)
