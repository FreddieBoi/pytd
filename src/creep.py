'''
Created on 13 mar 2010

@author: Freddie
'''
from random import randint, choice
from math import sin, cos, radians

import pygame
from shared import TILE_SIZE, xy2coord, coord2xy_mid, Vector2D as v


class Creep(pygame.sprite.Sprite):
    """ A creep sprite that bounces off walls and changes its
        direction from time to time.
    """
    def __init__(self, pos, bounds, direction, speed, next_coord_function):
        """ Create a new Creep.
                
            pos:
                A vec2d or a pair specifying the initial position
                of the creep on the screen.
            
            direction:
                A vec2d or a pair specifying the initial direction
                of the creep. Must have an angle that is a 
                multiple of 45 degres.
            
            speed: 
                Creep speed, in pixels/millisecond (px/ms)
        """
        pygame.sprite.Sprite.__init__(self)
        self.speed = int(speed)
        self.rect = bounds

        surface = pygame.Surface((self.rect.w-1, self.rect.h-1))
        surface.fill((0,0,0,0))
        pygame.draw.circle(surface, (0,0,255),((self.rect.w-1)/2+1,(self.rect.h-1)/2+1),
                           self.rect.w/2-1)
        surface.set_colorkey((0,0,0))
        self.image = surface
#        self.image = pygame.transform.rotate(pygame.image.load("..\img\creep_0.png"), -90)
        
        # A vector specifying the creep's position on the screen
        self.pos = v(pos)
        self.prev_pos = v(self.pos)

        # The direction is a normalized vector
        self.direction = v(direction).normalized()
        
        self.next_on_path = next_coord_function
    
    def update(self, time_passed):
        """ Update the creep.
        
            time_passed:
                The time passed (in ms) since the previous update.
        """
        # Maybe it's time to change the direction ?
        #
        self._compute_direction(time_passed)
        # Make the creep image point in the correct direction.
        # Note that two images are used, one for diagonals
        # and one for horizontals/verticals.
        #
        # round() on the angle is necessary, to make it 
        # exact, despite small deviations that may result from
        # floating-point calculations
        #
#        if int(round(self.direction.angle)) % 90 == 45:
#            self.image = pygame.transform.rotate(self.base_image_45,
#                                                 -(self.direction.angle + 45))
#        elif int(round(self.direction.angle)) % 90 == 0:
#            self.image = pygame.transform.rotate(self.base_image_0,
#                                                 -self.direction.angle)
#        else:
#            assert False
        
        # Compute and apply the displacement to the position 
        # vector. The displacement is a vector, having the angle
        # of self.direction (which is normalized to not affect
        # the magnitude of the displacement)
        #
        displacement = v(self.direction.x * self.speed,
                         self.direction.y * self.speed)
        self.prev_pos = v(self.pos)
        self.pos += displacement
        self.rect.center = self.pos
        
#        # When the image is rotated, its size is changed.
#        self.image_w, self.image_h = self.image.get_size()
        
#    def draw(self):
#        """ Blit the creep onto the screen that was provided in
#            the constructor.
#        """
#        # The creep image is placed at self.pos. To allow for 
#        # smooth movement even when the creep rotates and the 
#        # image size changes, its placement is always 
#        # centered.
#        #
#        self.draw_rect = self.image.get_rect().move(
#            self.pos.x - self.image_w / 2, 
#            self.pos.y - self.image_h / 2)
#        self.screen.blit(self.image, self.draw_rect)
#    
    def _compute_direction(self, time_passed):
        """ Finds out where to go
        """
        coord = xy2coord(self.pos)
        
        x_mid, y_mid = coord2xy_mid(coord)
#        if ((x_mid - self.pos.x) * (x_mid - self.prev_pos.x) < 0 or
#            (y_mid - self.pos.y) * (y_mid - self.prev_pos.y) < 0):
        if self.pos == (x_mid,y_mid):
            next_coord = self.next_on_path(coord)

            self.direction = v(next_coord[1] - coord[1],
                               next_coord[0] - coord[0]).normalized()
