'''
Tower Defence.

@author: Freddie
'''

import pygame
from sys import exit
from pathfinder import GridPath
from towers import Block, Tower
from creep import Creep
from shared import TILE_SIZE, FIELD_RECT, xy2coord, coord2xy_mid, Vector2D as v
from random import randint

class Player(object):
    def __init__(self):
        self.money = 0
        self.stuns = 0

class Field(pygame.surface.Surface, GridPath):
    def __init__(self):
        pygame.Surface.__init__(self, FIELD_RECT.bottomright)
        self.convert()
        self.show_grid = True
        self.fill((100,100,100))
        self.bounds = self.get_rect()
        # define the entrance
        self.entrance = pygame.Rect(self.bounds.left+9*TILE_SIZE, self.bounds.top, 
                                    2*TILE_SIZE, TILE_SIZE)
        # define the exit
        self.exit = pygame.Rect(self.bounds.right-11*TILE_SIZE, 
                                self.bounds.bottom-TILE_SIZE,
                                2*TILE_SIZE,TILE_SIZE)
        
        # Create the grid-path representation of the field
        self.rows = self.bounds.h/TILE_SIZE
        self.cols = self.bounds.w/TILE_SIZE
        end = xy2coord(self.exit.topleft) # will be changed later upon creep spawn
        self.gridpath = GridPath(self.rows, self.cols, end)
        
    def get_next(self, coord):
        return self.gridpath.get_next(coord)
    
    def get_path(self, coord):
        return self.gridpath._compute_path(coord)
    
    def block(self, coord):
        self.gridpath.set_blocked(coord, True)
        
    def unblock(self, coord):
        self.gridpath.set_blocked(coord, False)
        
    def is_blocked(self, coord):
        return self.gridpath.map.is_blocked(coord)
    
    def draw(self, screen):
        self._draw_portals(screen)
        if self.show_grid:
            self._draw_grid(screen)
    
    def _draw_grid(self, screen):
        for y in range(self.rows+1):
            pygame.draw.line(screen, pygame.color.Color(50, 50, 50),
                (self.bounds.left, self.bounds.top + y * TILE_SIZE - 1),
                (self.bounds.right - 1, self.bounds.top + y * TILE_SIZE - 1))
        
        for x in range(self.cols+1):
            pygame.draw.line(screen,pygame.color.Color(50, 50, 50), 
                             (self.bounds.left+x * TILE_SIZE - 1, 
                              self.bounds.top),
                             (self.bounds.left + x * TILE_SIZE - 1, 
                              self.bounds.bottom - 1))
    
    def _draw_portals(self, screen):
        entrance_sf = pygame.Surface((self.entrance.w-1, self.entrance.h-1))
        entrance_sf.fill(pygame.color.Color(80, 200, 80))
        entrance_sf.set_alpha(150)
        screen.blit(entrance_sf, self.entrance)
        
        exit_sf = pygame.Surface((self.exit.w-1, self.exit.h-1))
        exit_sf.fill(pygame.color.Color(200, 80, 80))
        exit_sf.set_alpha(150)
        screen.blit(exit_sf, self.exit)
        
    def _get_goal(self):
        return self.gridpath.goal
    
    def _set_goal(self, coord):
        self.gridpath.goal = coord
        # path cahche invalid
        self.gridpath._path_cache = {}
        
    goal = property(_get_goal, _set_goal, "The goal coordinates.")


class TowerDefence(object):
    
    def __init__(self):
        # initialize screen
        pygame.init()
        title = "Tower Defence"
        version = "0.01"
        self.screen_size = (FIELD_RECT.w,FIELD_RECT.h)
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption(title+" v"+version)
        icon = pygame.image.load("../img/icon.png")
        pygame.display.set_icon(icon)
        # background
        self.background = pygame.Surface(self.screen_size).convert()
        self.background.fill((100,100,100))
        self.screen.blit(self.background, (0,0))
        # the field (playable area)
        self.field_rect = FIELD_RECT
        self.field_size = FIELD_RECT.bottomright
        self.tile_size = TILE_SIZE
        self.field = Field()
        self.screen.blit(self.field, (0,0))

        # clock
        self.clock = pygame.time.Clock()
        
        self.game_over = False
        self.round_over = False
        self.paused = False

        self.creeps = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()
        self.player_towers = pygame.sprite.Group()
        # contains all sprites in this game
        self.sprites = pygame.sprite.RenderUpdates()
        
        self._create_blocks()
        
        self.player = Player()
        self.player.money = randint(5,20)
        self.next = (0,0)
        
        self._create_random_towers()
        
        self.building_mode = False
        self.build_time = 0
        self.time = 0
        self.message_text = ""
        rect = pygame.Rect(self.field.bounds.left+1*self.tile_size, 
                               self.field.bounds.top+1*self.tile_size, 
                               2*self.tile_size, 2*self.tile_size)
        self.building_marker = Tower(rect, v(rect.topleft), 
                                     (255,255,200))
        self.sprites.add(self.building_marker)
        pygame.display.flip()
        
    def set_is_building(self, value):
        if value:
            self.build_time = 0
            self.building_mode = True
            self.sprites.add(self.building_marker)
        else:
            self.build_time = 0
            self.sprites.remove(self.building_marker)
            self.building_mode = False    
    
    def get_is_building(self):
        return self.building_mode
        
    is_building = property(get_is_building,set_is_building)
        
    def _create_blocks(self):
        rows = self.field_size[1]/self.tile_size
        cols = self.field_size[0]/self.tile_size
        for x in range(1,9)+range(11,cols-1):
            rect = pygame.Rect(self.field.bounds.left+x*self.tile_size, 
                               self.field.bounds.top, 
                               self.tile_size, self.tile_size)
            block = Block(self.screen, rect, v(rect.topleft))
            self.sprites.add(block)
            coord = xy2coord((self.field.bounds.left+x*self.tile_size, 
                              self.field.bounds.top))
            self.field.block(coord)
            rect = pygame.Rect(self.field.bounds.left+x*self.tile_size, 
                               self.field.bounds.bottom-self.tile_size, 
                               self.tile_size, self.tile_size)
            block = Block(self.screen, rect, v(rect.topleft))
            self.sprites.add(block)
            coord = xy2coord((self.field.bounds.left+x*self.tile_size, 
                                   self.field.bounds.bottom-self.tile_size))
            self.field.block(coord)
        for y in range(rows):
            rect = pygame.Rect(self.field.bounds.left, 
                               self.field.bounds.top+y*self.tile_size, 
                               self.tile_size, self.tile_size)
            block = Block(self.screen, rect, v(rect.topleft))
            self.sprites.add(block)
            coord = xy2coord((self.field.bounds.left, 
                                   self.field.bounds.top+y*self.tile_size))
            self.field.block(coord)
            rect = pygame.Rect(self.field.bounds.right-self.tile_size, 
                               self.field.bounds.top+y*self.tile_size, 
                               self.tile_size, self.tile_size)
            block = Block(self.screen, rect, v(rect.topleft))
            self.sprites.add(block)
            coord = xy2coord((self.field.bounds.right-self.tile_size, 
                                   self.field.bounds.top+y*self.tile_size))
            self.field.block(coord)
            
    def _create_random_towers(self):
        tower_count = randint(6,15)
        while len(self.towers) < tower_count:
            row = randint(1,18)
            col = randint(1,18)
            self.build_tower(coord2xy_mid((row,col)),
                             (255,200,50),
                             self.towers)

    def build_tower(self, pos, color, group):
        row,col = xy2coord(pos)

        #@todo: center tower over cursor?
#        pos = pos[0]-self.tile_size/2,pos[1]-self.tile_size/2
#        row,col = xy2coord(pos)

        rect = pygame.Rect(self.field.bounds.left+col*self.tile_size, 
                               self.field.bounds.top+row*self.tile_size, 
                               2*self.tile_size, 2*self.tile_size)

        buildable, message = self._is_buildable(row,col)
        if buildable:
            tower = Tower(rect, v(rect.topleft), color)
            group.add(tower)
            self.sprites.add(tower)
        return (buildable,message)
            
    def _is_buildable(self,row,col):
        if self.player.money == 0:
            self.is_building = False
            return (False, "insufficient funds")
        coords = []
        for i in range(2):
            for j in range(2):
                coords.append(xy2coord((self.field.bounds.left+(col+i)*self.tile_size, 
                                       self.field.bounds.top+(row+j)*self.tile_size)))
                if self.field.is_blocked((row+i,col+j)):
                    return (False, "invalid placement")
        
        for coord in coords:
            self.field.block(coord)
        start = xy2coord(self.field.entrance.topleft)
        
        # if no path is found; tower is blocking the creep path
        if self.field.get_next(start) == None:
            # unblock all tower coords
            for coord in coords:
                self.field.unblock(coord)
            return (False, "blocking")

        return (True, "")

    def spawn_creep(self):
        self.is_building = False
        self.next = (0,0)
        start = self._get_start_coord()
        direction = (0,1)
        speed = 2
        bounds = pygame.Rect(start[0],
                             start[1],
                             self.tile_size,self.tile_size)
        self.creep = Creep(start,bounds,direction,speed,self.field.get_next)
        self.creeps.add(self.creep)
        self.sprites.add(self.creep)
        
    def _get_start_coord(self):
        start = (self.field.entrance.left+TILE_SIZE/2,
                  self.field.entrance.top+TILE_SIZE/2)
        row, col = xy2coord(start)
        if self.field.is_blocked((row+1,col)):
            start = (self.field.entrance.left+TILE_SIZE+TILE_SIZE/2,
                     self.field.entrance.top+TILE_SIZE/2)
        end = self.field.goal
        row, col = end
        if self.field.is_blocked((row-1,col)):
            end = (self.field.entrance.left-TILE_SIZE+TILE_SIZE/2,
                   self.field.entrance.top+TILE_SIZE/2)
            self.field.goal = (row,col+1)
        return start

    def pause(self):
        self.paused = not self.paused
        
    def restart(self):
        TowerDefence().run()
        self.quit()

    def quit(self):
        pygame.quit()
        exit()

    def draw(self):
        pygame.display.update()
        # clear
        self.sprites.clear(self.screen, self.field)
        # draw
        self.field.draw(self.screen)
        dirty = self.sprites.draw(self.screen)
        # print the player money
        font = pygame.font.Font(None, 20)
        money_text = font.render("$"+str(self.player.money), True, (255,255,0))
        money = self.screen.blit(money_text, (12*TILE_SIZE,3))
        dirty.append(money)
        # print pause text if game is paused
        if self.paused:
            paused_text = font.render("||", True, (255,255,255))
        else:
            paused_text = font.render(">", True, (255,255,255))
        paused = self.screen.blit(paused_text, (3,3))
        dirty.append(paused)
        # print build time text
        if self.build_time > 0:
            time_left = (45000-self.build_time)/1000.0
            time_text = font.render("s"+str(time_left), True, (255,255,255))
            time = self.screen.blit(time_text, (14*TILE_SIZE,3))
            dirty.append(time)
        # print creep time text
        if self.time > 0:
            time_left = (self.time)/1000.0
            time_text = font.render("s"+str(time_left), True, (255,255,255))
            time = self.screen.blit(time_text, (14*TILE_SIZE,3))
            dirty.append(time)
        # print message
        message_text = font.render(self.message_text, True, (255,50,50))
        message = self.screen.blit(message_text, (1*TILE_SIZE,3))
        dirty.append(message)
        # update display
        pygame.display.update(dirty)

    def update(self, time_passed):
        if self.build_time < 45000 and self.is_building:
            self.build_time += time_passed
        elif self.time == 0 and not self.round_over:
            self.time += time_passed
            self.is_building = False
            self.spawn_creep()
        else:
            self.time += time_passed

#        # update all creeps positions
        for creep in self.creeps:
            if xy2coord(creep.pos) == self.field.goal:
                self.creeps.remove(creep)
                self.sprites.remove(creep)
#                lap_time = float(self.time)/1000.0
#                print "Creep finished in",lap_time,"seconds"
                self.round_over = True
            creep.update(time_passed)

    def run(self):
        self.is_building = True
        while not self.game_over:
            # wating; 60 FPS
            time_passed = self.clock.tick(60)
            # If too long has passed between two frames, don't update (the game 
            # must have been suspended for some reason, and we don't want it to 
            # "jump forward" suddenly)
            if time_passed > 100:
                continue
            # handle user input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.paused:
                    # left click
                    if event.button == 1:
                        built,message = self.build_tower(event.pos,
                                                         (255,255,50),
                                                         self.player_towers)
                        if built:
                            self.player.money -= 1
                            self.message_text = ""
                        else:
                            self.message_text = message
#                    # right click
#                    elif event.button == 3:
#                        print xy2coord(event.pos)
                # show building marker
                elif event.type == pygame.MOUSEMOTION:
                    if self.is_building:
                        dx = event.pos[0]-self.building_marker.rect.left
                        dy = event.pos[1]-self.building_marker.rect.top
                        row, col = xy2coord((dx,dy))
                        x = col*TILE_SIZE
                        y = row*TILE_SIZE
    #                    rect = self.building_marker.rect.copy()
    #                    rect.move_ip(x,y)
    #                    xmax = FIELD_RECT.w-TILE_SIZE
    #                    ymax = FIELD_RECT.h-TILE_SIZE
    #                    if (rect.top >= TILE_SIZE and rect.bottom <= ymax and 
    #                        rect.left >= TILE_SIZE and rect.right <= xmax):
                        self.building_marker.rect.move_ip(x,y)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.quit()
                    elif event.key == pygame.K_r or event.key == pygame.K_F2 or event.key == pygame.K_SPACE:
                        self.restart()
                    elif event.key == pygame.K_p or event.key == pygame.K_PAUSE:
                        self.pause()
                    elif event.key == pygame.K_m:
                        self.field.gridpath.map.printme()
            # update if not paused
            if not self.paused and not self.round_over:
                self.update(time_passed)
#            if self.round_over:
#                pygame.time.wait(10*1000)
#                self.player_towers.empty()
#                self.is_building = True
            # draw
            self.draw()

if __name__ == '__main__':
    td = TowerDefence()
    td.run()