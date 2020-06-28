# -*- coding:Utf-8 -*-


class SimpleTextResGetter:
    def __init__(self, txt, render_txt_callback, color, size, font='m5x7.ttf'):
        self.text = txt
        self.render_txt = render_txt_callback
        self.color = color
        self.size = size
        self.font = font

    def __call__(self):
        return self.render_txt(self.text, self.color, self.size, self.font)


class FormatTextResGetter:
    def __init__(self, not_formatted_text, values, app, render_txt_callback, color, size, font='m5x7.ttf'):
        self.text = not_formatted_text
        self.values = values
        self.app = app
        self.render_txt = render_txt_callback
        self.color = color
        self.size = size
        self.font = font

        self.previous_res = None
        self.render = True

    def __call__(self):
        if self.render:
            self.render = False
            res = self.render_txt(
                self.text.format(*map(self.parse_attr, self.values)), self.color, self.size, self.font)
            self.previous_res = res
        else:
            res = self.previous_res
            self.render = True
        return res

    def parse_attr(self, value):
        a = self.app
        for attr_name in value:
            a = getattr(a, attr_name)
        return a
