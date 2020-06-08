# -*- coding:Utf-8 -*-

from time import perf_counter
import pygame
pygame.init()
from pygame.locals import *

window = pygame.display.set_mode((1200, 800))
white_rect_1 = pygame.Surface((200, 200), SRCALPHA)
white_rect_1.fill((255, 255, 255, 0))

a = []

awindow = window.copy().convert()
awindow.fill((127, 127, 127))
awindow.set_colorkey((127, 127, 127))

# awindow.blit(white_rect_1, (0, 0))
# awindow.blit(white_rect_1, (200, 0))
# awindow.blit(white_rect_1, (400, 0))
# awindow.blit(white_rect_1, (600, 0))
# awindow.blit(white_rect_1, (0, 200))
# awindow.blit(white_rect_1, (200, 200))
# awindow.blit(white_rect_1, (400, 200))
# awindow.blit(white_rect_1, (600, 200))
# awindow.blit(white_rect_1, (0, 400))
# awindow.blit(white_rect_1, (200, 400))
# awindow.blit(white_rect_1, (400, 400))
# awindow.blit(white_rect_1, (600, 400))



run = True
while run:
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False

    window.fill((45, 0, 0))

    t1 = perf_counter()
    window.blit(white_rect_1, (0, 0))
    window.blit(white_rect_1, (200, 0))
    window.blit(white_rect_1, (400, 0))
    window.blit(white_rect_1, (600, 0))
    window.blit(white_rect_1, (0, 200))
    window.blit(white_rect_1, (200, 200))
    window.blit(white_rect_1, (400, 200))
    window.blit(white_rect_1, (600, 200))
    window.blit(white_rect_1, (0, 400))
    window.blit(white_rect_1, (200, 400))
    window.blit(white_rect_1, (400, 400))
    window.blit(white_rect_1, (600, 400))
    a.append(perf_counter() - t1)

    pygame.display.flip()

print(sum(a) / len(a))