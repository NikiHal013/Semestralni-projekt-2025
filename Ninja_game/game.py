import sys
import pygame
import random, math, os

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, PlayerEntity, EnemyEntity
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Ninja game")
        self.screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE) #window size, allow resizing
        self.pixel_scale = 2  #lower to 1 to make pixels smaller; raise to 3+ for chunkier pixels
        self.display = pygame.Surface((320, 240))  #internal pixel surface

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
            "enemy/idle": Animation(load_images("entities/enemy/idle"), img_dur=6),
            "enemy/run": Animation(load_images("entities/enemy/run"), img_dur=6),
            "player/idle": Animation(load_images("entities/player/idle"), img_dur=6),
            "player/run": Animation(load_images("entities/player/run"), img_dur=4),
            "player/jump": Animation(load_images("entities/player/jump")),
            "player/slide": Animation(load_images("entities/player/slide")),
            "player/wall_slide": Animation(load_images("entities/player/wall_slide")),
            "particle/leaf": Animation(load_images("particles/leaf"), img_dur=20, loop=False),
            "particle/particle": Animation(load_images("particles/particle"), img_dur=6, loop=False),
            "gun": load_image("gun.png"),
            "projectile": load_image("projectile.png"),
        }

        self.sfx = {
            "jump": pygame.mixer.Sound("Ninja_game/data/sfx/jump.wav"),
            "dash": pygame.mixer.Sound("Ninja_game/data/sfx/dash.wav"),
            "hit": pygame.mixer.Sound("Ninja_game/data/sfx/hit.wav"),
            "shoot": pygame.mixer.Sound("Ninja_game/data/sfx/shoot.wav"),
            "ambience": pygame.mixer.Sound("Ninja_game/data/sfx/ambience.wav"),
        }

        self.sfx["ambience"].set_volume(0.2)
        self.sfx["shoot"].set_volume(0.4)
        self.sfx["hit"].set_volume(0.8)
        self.sfx["dash"].set_volume(0.3)
        self.sfx["jump"].set_volume(0.7)

        self.clouds = Clouds(self.assets["clouds"], count=16) #cloud entities

        self.player = PlayerEntity(self, (50, 50), (8, 15)) #player entity #size of player hitbox (width 8, height 15), (50, 50) = starting position
 
        self.tilemap = Tilemap(self, tile_size=16) #tile size in pixels

        self.level = 0
        self.load_level(self.level) 

        self.screenshake = 0
    
    def load_level(self, map_id):
        self.tilemap.load("Ninja_game/data/maps/" + str(map_id) + ".json") #for now only one map

        self.leaf_spawners = []
        for tree in self.tilemap.extract ([("large_decor", 2)], keep=True): #extract large decor tiles to offgrid list for proper rendering
            self.leaf_spawners.append(pygame.Rect(4 + tree["pos"][0], 4 + tree["pos"][1], 23, 13)) #position of leaf spawner = offset within tree tile

        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(EnemyEntity(self, spawner['pos'], (8, 15)))

        self.projectiles = [] #list of active projectiles
        self.particles = [] #list of active particles
        self.sparks = [] #list of active spark particles

        self.scroll = [0, 0] #scroll offset for camera movement = theres no cake/camera (everythng else moves around player)
        self.dead = 0
        self.transition = -30 #screen transition effect timer

    def run(self):
        pygame.mixer.music.load("Ninja_game/data/music.wav")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)  #loop indefinitely

        self.sfx["ambience"].play(-1)  #loop indefinitely

        while True:
            self.display.blit(self.assets["background"], (0, 0))

            self.screenshake = max(0, self.screenshake - 1) #decrease screen shake effect over time

            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    self.level += 1
                    self.load_level(self.level)
            if self.transition < 0:
                self.transition += 1

            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.level = min(self.level, len(os.listdir("Ninja_game/data/maps")) - 1) #prevent loading non-existent levels
                    self.transition = min(30, self.transition + 1) #start transition effect on death
                    self.screenshake = 32 #big screenshake on death
                if self.dead > 40:
                    self.load_level(self.level)

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) // 20
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) // 20 #slow and nice camera movement towards player  
            render_scroll = (int(self.scroll[0]), int(self.scroll[1])) #convert to integer for pixel perfect rendering //important for pixel art games

            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height: #spawn chance based on area
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, "leaf", pos, velocity=[-0.1,0.3], frame=random.randint(0, 20))) #random starting frame for variety

            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)

            self.tilemap.render(self.display, offset=render_scroll)

            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)

            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)

            #[(x,y), direction timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1] #update position based on velocity
                projectile[2] += 1 #decrease timer
                img = self.assets["projectile"]
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height()/2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360: #lifetime limit
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.sfx["hit"].play()
                        self.screenshake = max(16, self.screenshake) #increase screenshake on hit
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, "particle", self.player.rect().center, velocity=[math.cos(angle + math.pi) + speed * 0.5,  math.sin(angle + math.pi) * speed], frame=random.randint(0, 7)))

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)

                                
            for particle in self.particles.copy(): 
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == "leaf":
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3 #sway effect
                if kill:
                    self.particles.remove(particle)


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
                            if self.player.jump():
                                self.sfx["jump"].play()
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        self.player.dash()
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False

            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), 30 - abs(self.transition) * 8) #draw circle that grows/shrinks based on transition timer
                transition_surf.set_colorkey((255, 255, 255)) #make white color transparent
                self.display.blit(transition_surf, (0, 0)) #apply circular mask for transition effect

            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)

            # Scale internal pixel surface to the current window size
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), screenshake_offset)
            pygame.display.update()
            self.clock.tick(60)

Game().run()