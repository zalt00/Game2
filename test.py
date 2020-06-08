import pygame
from viewer.resources_loader import ResourceLoader
pygame.init()


screen = pygame.display.set_mode((800, 600))
rl = ResourceLoader('resources')

img = rl.load('base_tileset').sheets['base2']
while 1:
    screen.fill((255, 255, 255))
    screen.blit(img, (0, 0))
    pygame.display.flip()


