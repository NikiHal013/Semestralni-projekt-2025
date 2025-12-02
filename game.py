import sys
import pygame

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, PlayerEntity
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Corebound - Demo")
        self.screen = pygame.display.set_mode((640, 480)) #window size = actual screen size (width 640, height 480)
        self.display = pygame.Surface((320, 240)) #scaled display surface = notice its a half of screen size

        self.clock = pygame.time.Clock() #frame rate controller -> limits fps to 60

        self.movement = [False, False] #left, right movement states

        self.assets = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            "stone": load_images("tiles/stone"),
            "player": load_image("entities/player.png"),
            "background": load_image("background.png"),
            "clouds": load_images("clouds"),
            "player/idle": Animation(load_images("entities/player/idle"), img_dur=6),
            "player/run": Animation(load_images("entities/player/run"), img_dur=4),
            "player/jump": Animation(load_images("entities/player/jump")),
            "player/slide": Animation(load_images("entities/player/slide")),
            "player/wall_slide": Animation(load_images("entities/player/wall_slide")),
        }


        self.clouds = Clouds(self.assets["clouds"], count=16) #cloud entities
        self.player = PlayerEntity(self, (50, 50), (8, 15)) #player entity
        self.tilemap = Tilemap(self, tile_size=16) #tile size in pixels
        self.scroll = [0, 0] #scroll offset for camera movement = theres no cake/camera (everythng else moves around player)

    def run(self):
        while True:
            self.display.blit(self.assets["background"], (0, 0))

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) // 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) // 30 #slow and nice camera movement towards player  
            render_scroll = (int(self.scroll[0]), int(self.scroll[1])) #convert to integer for pixel perfect rendering //important for pixel art games

            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)
            self.tilemap.render(self.display, offset=render_scroll)

            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)


            for event in pygame.event.get(): #event handling
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.player.velocity[1] = -3.15 # jump floatiness
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()))
            pygame.display.update()
            self.clock.tick(60)

Game().run()