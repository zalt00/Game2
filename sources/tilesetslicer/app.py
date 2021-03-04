# -*- coding:Utf-8 -*-


import os
import pygame
import tkinter as tk
from tkinter.filedialog import askopenfilename
pygame.init()
from pygame.locals import *


class App:
    def __init__(self):
        self.tile_size = 64

        self.screen = pygame.display.set_mode((1000, 700))
        self.cursor = pygame.transform.scale2x(pygame.image.load(
            './../../resources/structure_builder_utils/cursor.obj/red.png')).convert_alpha()
        self.cursor_rect = self.cursor.get_rect()

        self.cursor_pos = [0, 0]

        root = tk.Tk()
        self.image_path = askopenfilename()
        root.destroy()

        self.image = pygame.image.load(self.image_path).convert_alpha()
        self.image_rect = self.image.get_rect()
        self.image_dir = os.path.dirname(self.image_path)

        self.tileset_image = None

        self.clock = pygame.time.Clock()

        self.stop = False

    @property
    def cursor_x(self):
        return self.cursor_pos[0]

    @cursor_x.setter
    def cursor_x(self, value):
        self.cursor_pos[0] = value
        self.cursor_rect.x = value * self.tile_size

    @property
    def cursor_y(self):
        return self.cursor_pos[1]

    @cursor_y.setter
    def cursor_y(self, value):
        self.cursor_pos[1] = value
        self.cursor_rect.y = value * self.tile_size

    def save(self):
        pygame.image.save(self.tileset_image, os.path.join(self.image_dir, f'{input("name of the file: ")}.png'))

    def add_tile(self):
        if self.tileset_image is None:
            self.tileset_image = self.image.subsurface(self.cursor_rect)
        else:
            rect = self.tileset_image.get_rect()
            new_surface = pygame.Surface((rect.width + self.tile_size, rect.height)).convert_alpha()
            new_surface.fill((255, 255, 255, 0))
            new_surface.blit(self.tileset_image, rect)
            new_surface.blit(self.image.subsurface(self.cursor_rect), (rect.width, 0))

            self.tileset_image = new_surface

    def run(self):
        while not self.stop:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.stop = True
                elif event.type == KEYDOWN:
                    if event.key == K_DOWN:
                        self.cursor_y += 1
                    elif event.key == K_UP:
                        self.cursor_y -= 1
                    elif event.key == K_RIGHT:
                        self.cursor_x += 1
                    elif event.key == K_LEFT:
                        self.cursor_x -= 1
                    elif event.key == K_RETURN:
                        self.add_tile()
                    elif event.key == K_s:
                        self.save()

            self.screen.fill((200, 200, 200))
            self.screen.blit(self.image, self.image_rect)
            self.screen.blit(self.cursor, self.cursor_rect)

            if self.tileset_image is not None:
                self.screen.blit(self.tileset_image, (0, 700 - self.tile_size))

            self.clock.tick(60)
            pygame.display.flip()


if __name__ == '__main__':
    app = App()
    app.run()
