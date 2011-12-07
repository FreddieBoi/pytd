'''
Towers.

@author: Freddie
'''

import pygame
from shared import Vector2D as v 

class Block(pygame.sprite.Sprite):
    def __init__(self, screen, bounds, pos):
        pygame.sprite.Sprite.__init__(self)

        self.rect = bounds

        self.image = pygame.Surface((self.rect.w-1, self.rect.h-1))
        self.image.fill((50, 50, 50))
        self.image.set_alpha(100)

        # A vector specifying the block position on the screen
        self.pos = v(pos)

class Tower(pygame.sprite.Sprite):
    def __init__(self, bounds, pos, color):
        pygame.sprite.Sprite.__init__(self)

        self.rect = bounds
        
        surface = pygame.Surface((self.rect.w-1, self.rect.h-1))

        self.image = pygame.Surface((self.rect.w-1, self.rect.h-1))
        self.image.fill(color)
        self.image.set_alpha(100)

        # A vector specifying the tower's position on the screen
        self.pos = v(pos)
