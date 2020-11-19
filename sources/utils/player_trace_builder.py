# -*- coding:Utf-8 -*-

import numpy as np
import pygame
from pygame.locals import *
pygame.init()


def main():
    screen = pygame.display.set_mode((1200, 800))

    surf = screen.copy().convert_alpha()
    surf.fill((255, 255, 255, 0))

    arr = np.load('records.npy')

    pr_x, pr_y = 0, 0
    x, y = 0, 0
    offset = 111111111111
    for t in range(arr.shape[0]):
        pr_x, pr_y = x, y
        if offset == 111111111111:
            offset = arr[t, 0]
        x, y = arr[t, :]
        x -= offset
        if pr_x != 0 and x != 0:
            pygame.draw.line(surf, (162, 28, 239), (pr_x, 800 - pr_y), (x, 800 - y), 2)

    run = True
    while run:
        for evt in pygame.event.get():
            if evt.type == QUIT:
                run = False
        screen.blit(surf, (0, 0))
        pygame.display.flip()

    pygame.image.save(surf, 'test.png')
    pygame.quit()





