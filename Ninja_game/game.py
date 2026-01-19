import sys
import pygame
import random, math, os

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, PlayerEntity, EnemyEntity
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
from scripts.UI import UI
from scripts.menu import Menu
from scripts.leaderboard import Leaderboard


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

        # Menu and Leaderboard (initialize first for sfx_enabled check)
        self.leaderboard = Leaderboard()
        self.menu = Menu()
        
        self.sfx = {
            "jump": pygame.mixer.Sound("Ninja_game/data/sfx/jump.wav"),
            "dash": pygame.mixer.Sound("Ninja_game/data/sfx/dash.wav"),
            "hit": pygame.mixer.Sound("Ninja_game/data/sfx/hit.wav"),
            "shoot": pygame.mixer.Sound("Ninja_game/data/sfx/shoot.wav"),
            "ambience": pygame.mixer.Sound("Ninja_game/data/sfx/ambience.wav"),
        }

        if self.menu.sfx_enabled:
            self.sfx["ambience"].set_volume(0.2)
            self.sfx["shoot"].set_volume(0.4)
            self.sfx["hit"].set_volume(0.8)
            self.sfx["dash"].set_volume(0.3)
            self.sfx["jump"].set_volume(0.7)

        self.clouds = Clouds(self.assets["clouds"], count=16) #cloud entities

        self.player = PlayerEntity(self, (50, 50), (8, 15)) #player entity #size of player hitbox (width 8, height 15), (50, 50) = starting position
 
        self.tilemap = Tilemap(self, tile_size=16) #tile size in pixels

        self.level = 0
        self.current_level_id = None  # track current level for death counting
        self.load_level(self.level) 

        self.screenshake = 0
        
        self.ui = UI()
        self.attempts = 0
        self.level_start_time = pygame.time.get_ticks()
        self.level_deaths = 0  # Track deaths on current level
        self.game_state = "menu"  # menu, playing, end, paused
        self.setup_menu_callbacks()
        self.menu.setup_main_menu(self.display.get_width(), self.display.get_height())
        self.menu.setup_settings_menu(self.display.get_width(), self.display.get_height())
        self.menu.setup_end_menu(self.display.get_width(), self.display.get_height())
        self.menu.setup_pause_menu(self.display.get_width(), self.display.get_height())
        self.refresh_all_leaderboards()

        # Wire menu callbacks
        self.setup_menu_callbacks()

    def refresh_all_leaderboards(self):
        data = {
            "baby_mode": self.leaderboard.get_leaderboard("baby_mode"),
            "normal": self.leaderboard.get_leaderboard("normal"),
            "hard": self.leaderboard.get_leaderboard("hard"),
        }
        self.menu.set_all_leaderboards(data)

    def setup_menu_callbacks(self):
        """Assign menu button callbacks and difficulty change hook."""
        self.menu.callbacks["play"] = self.start_game
        self.menu.callbacks["settings"] = self.show_settings
        self.menu.callbacks["quit"] = self.quit_game
        self.menu.callbacks["back"] = self.show_main_menu
        self.menu.callbacks["resume"] = self.resume_game
        self.menu.callbacks["restart"] = self.start_game
        self.menu.difficulty_change_callback = self.update_leaderboard_for_difficulty
        self.menu.toggle_sfx_callback = self.handle_sfx_toggle

    
    def update_leaderboard_for_difficulty(self):
        self.refresh_all_leaderboards()
    
    def handle_sfx_toggle(self):
        if self.menu.sfx_enabled:
            pygame.mixer.music.unpause()
            self.sfx["ambience"].play(-1)
        else:
            pygame.mixer.music.pause()
            self.sfx["ambience"].stop()
    
    def play_sfx(self, sfx_name):
        if self.menu.sfx_enabled and sfx_name in self.sfx:
            self.sfx[sfx_name].play()
    
    def start_game(self):
        self.game_state = "playing"
        self.level = 0
        self.attempts = 0
        self.level_deaths = 0
        self.total_game_time = pygame.time.get_ticks()
        self.load_level(self.level)
    
    def pause_game(self):
        self.game_state = "paused"
        self.menu.state = "pause"
    
    def resume_game(self):
        self.game_state = "playing"
    
    def show_settings(self):
        self.menu.state = "settings"
    
    def show_main_menu(self):
        self.menu.state = "main"
        self.game_state = "menu"
        self.refresh_all_leaderboards()
    
    def show_end_screen(self, elapsed_time):
        self.game_state = "end"
        self.menu.state = "end"
        self.menu.set_end_game_info(elapsed_time, 3)  # Show level 3 as completed
        
        # Add score to leaderboard with current difficulty
        self.leaderboard.add_score(elapsed_time, 3, self.menu.difficulty)
        self.refresh_all_leaderboards()
    
    def quit_game(self):
        pygame.quit()
        sys.exit()
    
    def load_level(self, map_id):
        # Only reset death counter when moving to a different level
        if map_id != self.current_level_id:
            self.level_deaths = 0
            self.current_level_id = map_id

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
        
        if not self.menu.sfx_enabled:
            pygame.mixer.music.pause()

        if self.menu.sfx_enabled:
            self.sfx["ambience"].play(-1)  # loop indefinitely

        while True:
            self.display.blit(self.assets["background"], (0, 0))
            
            # Handle menu state
            if self.game_state == "menu":
                mouse_pos = pygame.mouse.get_pos()
                self.menu.update(mouse_pos)
                self.menu.render(self.display, self.display.get_width(), self.display.get_height())
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.menu.handle_click(pygame.mouse.get_pos())
                    if event.type == pygame.KEYDOWN:
                        self.menu.handle_key_press(event.key)
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
            
            # Handle end screen state
            elif self.game_state == "end":
                mouse_pos = pygame.mouse.get_pos()
                self.menu.update(mouse_pos)
                self.menu.render(self.display, self.display.get_width(), self.display.get_height())
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.menu.handle_click(pygame.mouse.get_pos())
                    if event.type == pygame.KEYDOWN:
                        self.menu.handle_key_press(event.key)
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
            
            # Handle paused state
            elif self.game_state == "paused":
                mouse_pos = pygame.mouse.get_pos()
                self.menu.update(mouse_pos)
                self.menu.render(self.display, self.display.get_width(), self.display.get_height())
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.menu.handle_click(pygame.mouse.get_pos())
                    if event.type == pygame.KEYDOWN:
                        self.menu.handle_key_press(event.key)
                        if event.key == pygame.K_ESCAPE:
                            self.resume_game()
            
            # Game playing state
            else:
                self.screenshake = max(0, self.screenshake - 1)

                if not len(self.enemies):
                    self.transition += 1
                    if self.transition > 30:
                        if self.level < 2:  # Levels 0, 1, 2 (3 total)
                            self.level += 1
                            self.transition = -30
                            self.load_level(self.level)
                        else:
                            # All 3 levels completed
                            elapsed_time = pygame.time.get_ticks() - self.total_game_time
                            self.show_end_screen(elapsed_time)
                        
                if self.transition < 0:
                    self.transition += 1

                if self.dead:
                    self.dead += 1
                    if self.dead >= 10:
                        self.level = min(self.level, len(os.listdir("Ninja_game/data/maps")) - 1)
                        self.transition = min(30, self.transition + 1)
                        self.screenshake = 32
                    if self.dead > 40:
                        self.attempts += 1
                        self.level_deaths += 1
                        
                        # Check difficulty-based level regression
                        should_regress = False
                        if self.menu.difficulty == "hard" and self.level_deaths >= 1:
                            # Hard mode: regress on first death
                            should_regress = True
                        elif self.menu.difficulty == "normal" and self.level_deaths >= 3:
                            # Normal mode: regress after 3 deaths
                            should_regress = True
                        
                        if should_regress and self.level > 0:
                            # Go back one level
                            self.level -= 1
                            self.level_deaths = 0
                        
                        self.load_level(self.level)

                self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) // 20
                self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) // 20
                render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

                for rect in self.leaf_spawners:
                    if random.random() * 49999 < rect.width * rect.height:
                        pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                        self.particles.append(Particle(self, "leaf", pos, velocity=[-0.1,0.3], frame=random.randint(0, 20)))

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

                for projectile in self.projectiles.copy():
                    projectile[0][0] += projectile[1]
                    projectile[2] += 1
                    img = self.assets["projectile"]
                    self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height()/2 - render_scroll[1]))
                    if self.tilemap.solid_check(projectile[0]):
                        self.projectiles.remove(projectile)
                        for i in range(4):
                            self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                    elif projectile[2] > 360:
                        self.projectiles.remove(projectile)
                    elif abs(self.player.dashing) < 50:
                        if self.player.rect().collidepoint(projectile[0]):
                            self.projectiles.remove(projectile)
                            self.dead += 1
                            self.play_sfx("hit")
                            self.screenshake = max(16, self.screenshake)
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
                        particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                    if kill:
                        self.particles.remove(particle)

                for event in pygame.event.get():
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
                                self.play_sfx("jump")
                        if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                            self.player.dash()
                        if event.key == pygame.K_ESCAPE:
                            self.pause_game()
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            self.movement[0] = False
                        if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            self.movement[1] = False

                if self.transition:
                    transition_surf = pygame.Surface(self.display.get_size())
                    pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), 30 - abs(self.transition) * 8)
                    transition_surf.set_colorkey((255, 255, 255))
                    self.display.blit(transition_surf, (0, 0))

                elapsed_time = pygame.time.get_ticks() - self.total_game_time
                self.ui.render(self.display, self.attempts, elapsed_time, self.level + 1)
            
            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), screenshake_offset)
            pygame.display.update()
            self.clock.tick(60)

Game().run()