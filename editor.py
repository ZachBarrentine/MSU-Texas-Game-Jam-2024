import sys
import pygame
import os

from scripts.utils import LoadImage, LoadImages
from scripts.Tilemap import Tilemap

SIZE = WIDTH, HEIGHT = (700, 700)
DISPLAY = pygame.display.set_mode(SIZE)
FPS = pygame.time.Clock()
BASE_SPEED = 7
BASE_HEALTH = 200
RED = (225, 0, 0)
GREEN = (0, 225, 0)
BLUE = (0, 0, 225)
OVERLAY = (200, 30, 30)

BG = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'Floor.png')).convert(), (WIDTH, HEIGHT))
WALL1 = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'Room1Wall.png')).convert(), (WIDTH, HEIGHT))
WALL1.set_colorkey((0, 0, 0))
WALL2 = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'Room2Wall.png')).convert(), (WIDTH, HEIGHT))
WALL2.set_colorkey((0, 0, 0))
WALL3 = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'Room3Wall.png')).convert(), (WIDTH, HEIGHT))
WALL3.set_colorkey((0, 0, 0))
GRASS = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'Grass.png')).convert(), (WIDTH, HEIGHT))
GRASS.set_colorkey((0, 0, 0))
SPAWN2 = (20, 150)

RENDER_SCALE = 2.0

class Editor:
    def __init__(self):
        pygame.init()
        self.display = DISPLAY

        pygame.display.set_caption('Editor')
        self.screen = pygame.display.set_mode(SIZE)
       # self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.asset = {
            'black': LoadImage('black.png'),
            'floor': LoadImage('floor.png'),
            'room': LoadImage('Room1Wall.png'),
        }


        self.movement = [False, False, False, False]

        self.tilemap = Tilemap(self, tile_size=16)

        try:
            self.tilemap.load('map.json')
        except FileNotFoundError:
            pass

        self.scroll = [0, 0]

        self.tile_list = list(self.asset)
        self.tile_group = 0
        #self.tile_variant = 0

        self.clicking = False
        self.rightclicking = False
        self.ongrid = True

    def run(self):         
        while True:
            self.display = DISPLAY


            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            render_scoll = (int(self.scroll[0]), int(self.scroll[1]))

            self.tilemap.render(self.display, offset=render_scoll)

            # current_tile_img = self.asset[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img = self.asset['black'].copy()

            current_tile_img.set_alpha(100)

            mpos = pygame.mouse.get_pos()
            #mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
            TilePos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size), 
                       int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size))

            if self.ongrid:
                 self.display.blit(current_tile_img, (TilePos[0] * self.tilemap.tile_size - self.scroll[0], TilePos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_img, mpos)     

            if self.clicking and self.ongrid:
                self.tilemap.tilemap[str(TilePos[0]) + ';' + str(TilePos[1])] = {'type': self.tile_list[self.tile_group], 'pos': TilePos}   
            if self.rightclicking:
                tile_loc = str(TilePos[0]) + ';' + str(TilePos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.asset['black']
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)
                
            self.display.blit(current_tile_img, (5, 5))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'pos': (mpos[0] + self.scroll[0], mpos[1] + self.scroll[1])})
                    if event.button == 3:
                        self.rightclicking = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.rightclicking = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                    if event.key == pygame.K_o:
                        self.tilemap.save('map1.json')

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False

            #self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)
            self.display.fill((255, 255, 255))
            self.display.blit(BG, (0, 0))
            self.display.blit(WALL1, (0, 0))
Editor().run()
