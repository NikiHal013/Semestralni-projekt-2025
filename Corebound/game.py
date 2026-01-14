import sys, pygame, math

from scripts.utils import load_image, load_images, Animation
from scripts.entities.BasicEntity import PhysicsEntity
import scripts.entities.Player.PlayerEntity as PlayerEntity
from scripts.entities.Player.PlayerAttack import PlayerAttack
from scripts.entities.Enemy.MushroomEntity import MushroomEntity
from scripts.entities.Enemy.EnemyEntity import EnemyEntity
from scripts.Powerup import Powerup
from scripts.Notification import Notification
from scripts.tilemap import Tilemap
from scripts.particle import Particle
from scripts.sparks import Spark

class Game:
    def __init__(self):
        pygame.init()

        screen_width, screen_height = 800, 600

        pygame.display.set_caption('Corebound')
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        # Use integer backbuffer size to avoid float surface dimensions
        self.display = pygame.Surface((int(screen_width / 2.5), int(screen_height / 2.5)))

        self.clock = pygame.time.Clock()
        self.movement = [False, False]  #left, right
        # HUD font for on-screen text (lives, etc.)
        self.font = pygame.font.Font(None, 24)

        self.assets = {
            'swamp': load_images('tiles/swamp'),
            'rocky_tiles': load_images('tiles/rocky_tiles'),
            'player': load_image('entities/player.png'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=8),
            'player/run': Animation(load_images('entities/player/run'), img_dur=6),
            'player/jump': Animation(load_images('entities/player/jump'), img_dur=10),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide'), img_dur=6),
            'particle': Animation(load_images('particles'), img_dur=6, loop=False),
            'big_rock': load_images('tiles/big_rock'),
            'mushs': load_images('tiles/mushs'),
            'rock_piles': load_images('tiles/rock_piles'),
            'signs': load_images('tiles/signs'),
            'rocks': load_images('tiles/rocks'),
            # Powerup sprites
            'powerup/base': load_image('power-ups/power-up.png'),
            'powerup/movement': load_image('power-ups/power-up_movement.png'),
            'powerup/fighting': load_image('power-ups/power-up_fighting_style.png'),
            # Powerup spawner tiles (variants map to specific pickups)
            'powerups': [
                load_image('power-ups/power-up_movement.png'),       # 0: double jump
                load_image('power-ups/power-up_movement.png'),       # 1: wall slide
                load_image('power-ups/power-up_movement.png'),       # 2: dash
                load_image('power-ups/power-up_fighting_style.png'), # 3: fighting style
                load_image('power-ups/power-up.png'),                # 4: life
            ],
            # Mushroom enemy animations
            'mushroom/idle': Animation(load_images('entities/enemy/mushroom/Idle'), img_dur=8),
            'mushroom/run': Animation(load_images('entities/enemy/mushroom/Run'), img_dur=6),
            'mushroom/attack': Animation(load_images('entities/enemy/mushroom/Attack'), img_dur=6, loop=False),
            'mushroom/hit': Animation(load_images('entities/enemy/mushroom/Hit'), img_dur=5, loop=False),
            'mushroom/die': Animation(load_images('entities/enemy/mushroom/Die'), img_dur=6, loop=False),
            # Skill text images
            'skill/double_jump': load_image('text/double_jump.png'),
            'skill/wall_slide': load_image('text/wall_slide.png'),
            'skill/dash': load_image('text/dash.png'),
            'skill/fighting_style': load_image('text/fighting_style.png'),
        }

        self.player = PlayerEntity.Player(self, (100, 100), pygame.Rect(self.assets['player'].get_rect()).size)
        self.player_attack = PlayerAttack(self, self.player)
        self.tilemap = Tilemap(self, tile_size=16)
        self.enemies = []  # List of enemy entities
        self.powerups = []  # List of powerup orbs
        self.notifications = []  # List of notifications
        self.screenshake = 0  # Screen shake for impact effects

        self.level = 2
        self.debug = True  # Toggle debug hitboxes overlay
        self.load_level(self.level)

        self.bg_images=[]
        for i in range(1,4):
            bg_image = load_image(f"backgrounds/BG_{i}.png")
            # Scale background to fit the display surface
            bg_scaled = pygame.transform.scale(bg_image, (int(self.display.get_width()), int(self.display.get_height())))
            self.bg_images.append(bg_scaled)
        
        self.bg_width = self.bg_images[0].get_width()

    def load_level(self, map_id):
        self.tilemap.load("Corebound/data/maps/" + str(map_id) + ".json")

        self.enemies = []
        self.powerups = []  # Reset powerups for new level
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 1:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(MushroomEntity(self, spawner['pos'], (8, 15)))

        # Spawn powerups from map variants
        powerup_map = {
            0: 'double_jump',
            1: 'wall_slide',
            2: 'dash',
            3: 'fighting_style',
            4: 'life',
        }
        for pu in self.tilemap.extract([('powerups', v) for v in powerup_map]):
            skill = powerup_map.get(pu['variant'])
            if skill:
                self.powerups.append(Powerup(self, pu['pos'], skill))

        self.particles = []
        self.sparks = []
        self.scroll = [0, 0]
        

    def draw_bg(self, render_scroll):
        # Tile each layer horizontally and vertically with parallax
        speed = 1.0
        base_y_offset = -30  # Move background up by 30 pixels
        for img in self.bg_images:
            # Compute wrapped offset for this parallax speed (horizontal)
            x = int((-(render_scroll[0] * speed)) % self.bg_width)
            # Compute vertical parallax offset
            y = int(base_y_offset - (render_scroll[1] * speed * 0.5))
            # Draw two copies to cover seam across the viewport
            self.display.blit(img, (x - self.bg_width, y))
            self.display.blit(img, (x, y))
            speed += 0.2

        #pygame.Rect(*self.img, self.img.get_size()) #player hitbox
        #self.clicking = False
        #self.right_clicking = False
        
    def run(self):
        while True:
            self.display.fill((0, 0, 0))
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.draw_bg(render_scroll)
            self.tilemap.render(self.display, offset=render_scroll)

            # Update enemies
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                if kill:
                    self.enemies.remove(enemy)
                else:
                    enemy.render(self.display, offset=render_scroll)
            
            # Update powerups and check for collection
            for powerup in self.powerups.copy():
                powerup.update(self.tilemap, (0, 0))
                powerup.render(self.display, offset=render_scroll)
                # Check collision with player
                if powerup.rect().colliderect(self.player.rect()):
                    powerup.collect(self.player)
                    self.powerups.remove(powerup)
            
            # Update player attack system
            self.player_attack.update(self.enemies)
            
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)

            # HUD: Player lives (top-left)
            lives_text = self.font.render(f"Lives: {getattr(self.player, 'lives', 0)}", True, (255, 255, 255))
            self.display.blit(lives_text, (6, 4))
            
            # Debug overlays
            if self.debug:
                # Tile hitboxes
                self.tilemap.render_debug_hitboxes(self.display, offset=render_scroll)
                # Enemy rects
                for enemy in self.enemies:
                    er = enemy.rect()
                    pygame.draw.rect(
                        self.display,
                        (255, 200, 0),
                        pygame.Rect(er.x - render_scroll[0], er.y - render_scroll[1], er.width, er.height),
                        1
                    )
                # Player rect
                pr = self.player.rect()
                pygame.draw.rect(
                    self.display,
                    (255, 0, 0),
                    pygame.Rect(pr.x - render_scroll[0], pr.y - render_scroll[1], pr.width, pr.height),
                    1
                )
                # Attack hitboxes
                self.player_attack.render_debug(self.display, offset=render_scroll)

            for particle in self.particles.copy(): 
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if kill:
                    self.particles.remove(particle)

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)
            
            # Update and render notifications
            for notification in self.notifications.copy():
                if notification.update():
                    self.notifications.remove(notification)
                else:
                    notification.render(self.display)

            for event in pygame.event.get(): #event handling
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  #left click
                         #self.clicking = True
                        pass
                    if event.button == 3:  #right click
                         #self.right_clicking = True
                        pass
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  #left click
                         #self.clicking = Falsed
                        pass
                    if event.button == 3:  #right click
                         #self.right_clicking = False
                        pass
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.player.jump()
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        self.player.dash()
                    if event.key == pygame.K_SPACE or event.key == pygame.K_j:
                        # Trigger player attack
                        self.player_attack.start_attack()
                    if event.key == pygame.K_F3:
                        # Toggle debug overlay
                        self.debug = not self.debug
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

Game().run()