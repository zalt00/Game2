# -*- coding:Utf-8 -*-

import pyglet


class Page:
    def __init__(self, page_name):
        self.name = page_name
        self.batch = pyglet.graphics.Batch()
        self._children = {}
        self._groups = set()

    def draw(self):
        self.batch.draw()
        for page in self._children.values():
            page.draw()

    def __contains__(self, item):
        if isinstance(item, str):
            return item in self._children
        return item in self._children.values()

    def add_child(self, page):
        if self.name not in page:
            self._children[page.name] = page
        else:
            raise ValueError('can not add page as a child to self because self if a child of page')

    def remove_child(self, page_or_name):
        if isinstance(page_or_name, str):
            name = page_or_name
        else:
            name = page_or_name.name

        self._children.pop(name)

    def add_group(self, group_name):
        setattr(self, group_name, set())
        self._groups.add(group_name)

    def get_all_sprites(self):
        parent_group = set()
        for group_name in self._groups:
            parent_group |= getattr(self, group_name)
        return parent_group

