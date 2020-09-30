# -*- coding:Utf-8 -*-


class SimpleTextGetter:
    def __init__(self, text):
        self.text = text

    def __call__(self):
        return self.text


class FormatTextGetter:
    def __init__(self, not_formatted_text, values, app):
        self.text = not_formatted_text
        self.values = values
        self.app = app

    def __call__(self):
        return self.text.format(*map(self.parse_attr, self.values))

    def parse_attr(self, value):
        a = self.app
        for attr_name in value:
            a = getattr(a, attr_name)
            if isinstance(a, float):
                a = round(a, 2)
        return a
