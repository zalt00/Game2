# -*- coding:Utf-8 -*-

import numpy as np
from resources_loader import ResourceLoader
import pygame
from PIL import Image
pygame.init()

pygame.display.set_mode()


def combine(a1, a2, coef):
    #  combination seulement aux endroits ou les deux sont opaques
    b1 = a1[:, :, 3] != 0
    b2 = a2[:, :, 3] != 0
    new_array = np.zeros(a1.shape, dtype=np.uint8) + 255
    new_array[:, :, 3] = 0
    c1, c2 = (b1 & b2).nonzero()  # indices ou les deux sont opaques
    d1, d2 = (b1 != b2).nonzero()
    for x, y in zip(c1, c2):
        new_array[x, y] = np.array(a1[x, y] * (1 - coef) + a2[x, y] * coef)

    for x, y in zip(d1, d2):
        if a1[x, y, 3] != 0:
            new_array[x, y, 3] = np.array(a1[x, y, 3] * (1 - coef))
            new_array[x, y, :3] = np.array(a1[x, y, :3])
        else:
            new_array[x, y, 3] = np.array(a2[x, y, 3] * coef)
            new_array[x, y, :3] = np.array(a2[x, y, :3])

    return new_array

def main():
    rl = ResourceLoader('./../../resources')
    res = rl.load('warrior')
    sheet = res.sheets['walk']
    width = res.width
    height = res.height
    
    sheet_length = sheet.get_width()
    
    new_sheet = pygame.Surface((sheet_length * 2 - width, height)).convert_alpha()
    new_sheet.fill((255, 255, 255, 0))
    for i in range(int(sheet_length // width)):
        rect1 = pygame.Rect(i * width, 0, width, height)
        rect2 = pygame.Rect(i * width + 1, 0, width, height)
        s1 = sheet.subsurface(rect1)
        try:
            s2 = sheet.subsurface(rect2)
        except ValueError:
            nr1 = pygame.Rect(i * width * 2, 0, width, height)
            new_sheet.blit(s1, nr1)
        else:
    
            a1 = np.zeros((width, height, 4), dtype=np.uint8) + 255
            a2 = np.zeros((width, height, 4), dtype=np.uint8) + 255
            
            
            pygame.pixelcopy.surface_to_array(a1[:, :, :3], s1, 'P')
            pygame.pixelcopy.surface_to_array(a1[:, :, 3], s1, 'A')
            
            pygame.pixelcopy.surface_to_array(a2[:, :, :3], s2, 'P')
            pygame.pixelcopy.surface_to_array(a2[:, :, 3], s2, 'A')   
            
            new_array = combine(a1, a2, 0.5)
            
            img = Image.fromarray(new_array)
            img.save('temp.png')
        
            ns = pygame.image.load('temp.png').convert_alpha()
            ns = pygame.transform.rotate(ns, 90)
            ns = pygame.transform.flip(ns, False, True)
            nr1 = pygame.Rect(i * width * 2, 0, width, height)
            nr2 = pygame.Rect(i * width * 2 + width, 0, width, height)
        
            new_sheet.blit(s1, nr1)
            new_sheet.blit(ns, nr2)
            
    pygame.image.save(new_sheet, 'aa.png')
        
    
if __name__ == '__main__':
    main()
    
    
    
    
