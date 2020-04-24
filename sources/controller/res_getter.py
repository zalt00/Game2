# -*- coding:Utf-8 -*-


class TextResGetter:
    def __init__(self, not_formatted_text, values, app, render_txt_callback, color, size):
        self.text = not_formatted_text
        self.values = values
        self.app = app
        self.render_txt = render_txt_callback
        self.color = color
        self.size = size

    def __call__(self):
        return self.render_txt(self.text.format(*map(self.parse_attr, self.values)), self.color, self.size)

    def parse_attr(self, value):
        a = self.app
        for attr_name in value:
            a = getattr(a, attr_name)
        return a
