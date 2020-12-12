# -*- coding:Utf-8 -*-


from .plugin_base import PluginMeta, AbstractPlugin, command
import pygame
pygame.init()

__plugin_name__ = 'CopyPastePlugin'


class CopyPastePlugin(AbstractPlugin, metaclass=PluginMeta):
    def __init__(self, app):
        super(CopyPastePlugin, self).__init__(app)
        self.copied_subtab = None
        self.copied_image = None

    @command('ctrl-c')
    def copy(self):
        top = self.app.sepos[1] * self.app.th
        left = self.app.sepos[0] * self.app.tw
        width = (self.app.nwpos[0] + 1) * self.app.tw - left
        height = (self.app.nwpos[1] + 1) * self.app.th - top
        r = pygame.Rect(left, top, width, height)
        self.copied_image = self.app.bg.subsurface(r).copy()

        lines = self.app.tab[self.app.sepos[1]:self.app.nwpos[1] + 1]
        sub_tab = []
        for line in lines:
            sub_tab.append(line[self.app.sepos[0]:self.app.nwpos[0] + 1])
        self.copied_subtab = sub_tab

    @command('ctrl-v')
    def paste(self):
        if self.copied_image is not None and self.copied_subtab is not None:
            top = self.app.sepos[1] * self.app.th
            left = self.app.sepos[0] * self.app.tw
            self.app.bg.blit(self.copied_image, (left, top))
            width = len(self.copied_subtab[0])
            height = len(self.copied_subtab)
            lines = self.app.tab[self.app.sepos[1]:self.app.sepos[1] + height]

            for i, line in enumerate(lines):
                line[self.app.sepos[0]:self.app.sepos[0] + width] = self.copied_subtab[i]
