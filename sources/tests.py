# -*- coding:Utf-8 -*-

import pygame
from pygame.locals import *
import multiprocessing as mp
pygame.init()

screen = []
screen2 = []


def flip():
    import pygame
    pygame.init()

    while True:
        pygame.display.flip()


class App:

    def __init__(self):
        global screen, screen2
        self.screen = pygame.display.set_mode((1200, 800))
        self.screen2 = self.screen.copy()
        self.screen2.fill((255, 255, 255))
        self.screen2.convert()

        self.screen3 = self.screen2.copy()
        self.screen4 = self.screen2.copy()
        self.screen5 = self.screen2.copy()

        screen.append(self.screen)
        screen2.append(self.screen5)

        print(screen)
        self.fps = []

        self.stop = False
        self.clock = pygame.time.Clock()

    def run(self):
        p = mp.Process(target=flip)
        p.start()
        while not self.stop:

            for evt in pygame.event.get():
                if evt.type == QUIT:
                    self.stop = True
                    self.stop_ref = True

            pygame.display.flip()
            self.clock.tick()
            self.fps.append(self.clock.get_fps())
            pygame.display.set_caption(str(sum(self.fps) / len(self.fps)))


if __name__ == '__main__':
    a = App()
    a.run()












