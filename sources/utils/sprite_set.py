# -*- coding:Utf-8 -*-


class SpriteSet:
    def __init__(self, *sprites):
        self._sprites = set()
        for sprite in sprites:
            self.add(sprite)

    def add(self, sprite):
        self._sprites.add(sprite)
        if hasattr(sprite, 'groups'):
            sprite.groups.add(self)

    def remove(self, sprite):
        self._sprites.remove(sprite)
        if hasattr(sprite, 'groups'):
            sprite.groups.remove(self)

    def sprites(self):
        return self._sprites

    def update(self, *args, **kwargs):
        for sprite in self._sprites:
            sprite.update_(*args, **kwargs)
