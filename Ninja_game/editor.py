import sys
import pygame

from scripts.utils import load_images
from scripts.tilemap import Tilemap

RENDER_SCALE = 2.0  # Scaling factor for rendering

class Editor:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Corebound - Editor")
        self.screen = pygame.display.set_mode((640, 480)) #window size = actual screen size (width 640, height 480)
        self.display = pygame.Surface((320, 240)) #scaled display surface = notice its a half of screen size

        self.clock = pygame.time.Clock() #frame rate controller -> limits fps to 60


        self.assets = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            "stone": load_images("tiles/stone"),
            "spawners": load_images("tiles/spawners"),
        }

        self.movement = [False, False, False, False] #left, right, up, down movement states

        self.tilemap = Tilemap(self, tile_size=16) #tile size in pixels

        self.current_map_id = 3  # track current map id

        try:
            self.load_level(self.current_map_id) #load default map
        except FileNotFoundError:
            pass

    def load_level(self, map_id):
        self.tilemap.load("beta/data/maps/" + str(map_id) + ".json") #for now only one map
        self.current_map_id = map_id
        self.scroll = [0, 0] 

        self.tile_list = list(self.assets)
        self.tile_group = 0 #index of current tile group
        self.tile_variant = 0 #index of current tile variant within the group

        self.clicking = False #to track mouse clicking state
        self.right_clicking = False #to track right mouse clicking state
        self.shift = False #to track shift key state
        self.ongrid = True #to track if placing on grid or offgrid

    def run(self):
        while True:
            self.display.fill((0, 0, 0))

            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2 
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
                            
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.tilemap.render(self.display, offset=render_scroll)

            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant] #get current tile image
            current_tile_img.set_alpha(100) #set transparency for preview

            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] // RENDER_SCALE, mpos[1] // RENDER_SCALE) #adjust mouse position for scroll and scale
            tile_pos = (int(mpos[0] + self.scroll[0]) // self.tilemap.tile_size, int(mpos[1] + self.scroll[1]) // self.tilemap.tile_size) #get tile coordinates under mouse

            if self.ongrid: #snap to grid if ongrid mode is active
                self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - render_scroll[0], tile_pos[1] * self.tilemap.tile_size - render_scroll[1])) #draw preview of current tile at mouse position
            else:
                self.display.blit(current_tile_img, mpos) #draw preview of current tile at mouse position


            if self.clicking and self.ongrid: #place tile on left click
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {"type": self.tile_list[self.tile_group], "variant": self.tile_variant, "pos": tile_pos}
            if self.right_clicking: #remove tile on right click
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height()) #get rect of offgrid tile
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)

            self.display.blit(current_tile_img, (5,5))

            for event in pygame.event.get(): #event handling
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: #left click to place tile
                        self.clicking = True
                        if not self.ongrid:
                            mouse_tile_pos = (int(mpos[0]) , int(mpos[1]))
                            self.tilemap.offgrid_tiles.append({"type": self.tile_list[self.tile_group], "variant": self.tile_variant, "pos": (mpos[0] + self.scroll[0], mpos[1] + self.scroll[1])}) #place offgrid tile
                    if event.button == 3: #right click to remove tile
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 4: #scroll up to change tile variant
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]]) #loop through tile groups
                        if event.button == 5: #scroll down to change tile variant
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4: #scroll up to change tile group
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list) #loop through tile groups
                            self.tile_variant = 0 #reset variant to 0 when changing group
                        if event.button == 5: #scroll down to change tile group
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0 #reset variant to 0 when changing group
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_TAB:
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_t:
                        self.tilemap.auto_tile()
                    if event.key == pygame.K_o:
                        self.tilemap.save("data/maps/" + str(self.current_map_id) + ".json")
                    if event.key == pygame.K_1:
                        self.load_level(0)
                    if event.key == pygame.K_2:
                        self.load_level(1)
                    if event.key == pygame.K_3:
                        self.load_level(2)
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_TAB:
                        pass
                    if event.key == pygame.K_LSHIFT:
                            self.shift = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()))
            pygame.display.update()
            self.clock.tick(60)

Editor().run()