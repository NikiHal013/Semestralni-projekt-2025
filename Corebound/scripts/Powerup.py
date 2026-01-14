import pygame, math
from scripts.entities.BasicEntity import PhysicsEntity

class Powerup(PhysicsEntity):
    """Collectible powerup orb that unlocks skills or grants lives."""
    
    SKILL_COLORS = {
        'double_jump': (100, 150, 255),      # Blue
        'wall_slide': (150, 100, 255),       # Purple
        'dash': (255, 150, 100),             # Orange
        'fighting_style': (255, 100, 100),   # Red
        'life': (120, 220, 120),             # Green
    }

    SPRITE_KEYS = {
        'double_jump': 'powerup/movement',
        'wall_slide': 'powerup/movement',
        'dash': 'powerup/movement',
        'fighting_style': 'powerup/fighting',
        'life': 'powerup/base',
    }
    
    def __init__(self, game, pos, skill_type):
        # Don't call super().__init__ to avoid animation setup
        self.game = game
        self.type = 'powerup'
        self.pos = list(pos)
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        self.action = 'idle'
        self.anim_offset = (0, 0)
        self.flip = False
        self.manual_flip = False
        self.last_movement = [0, 0]
        
        self.skill_type = skill_type
        self.collected = False
        self.float_offset = 0
        self.float_speed = 0.1
        self.pulse = 0

        # Sprite lookup (falls back to default circle if missing)
        sprite_key = self.SPRITE_KEYS.get(skill_type, 'powerup/base')
        self.image = self.game.assets.get(sprite_key)
        self.size = self.image.get_size() if self.image else (8, 8)
    
    def set_action(self, action):
        """Override to prevent animation lookup."""
        self.action = action
        
    def update(self, tilemap, movement=(0, 0)):
        """Update powerup floating animation."""
        if self.collected:
            return
        
        # Floating animation
        self.pulse += self.float_speed
        self.float_offset = abs(math.sin(self.pulse) * 2)
        
        # Physics: gravity and collision
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        frame_movement = (movement[0] * 1.3 + self.velocity[0], movement[1] * 1.3 + self.velocity[1])
        
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos, self.size):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
        
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos, self.size):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
        
        self.last_movement = movement
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
    
    def rect(self):
        """Return collision rectangle."""
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def render(self, surf, offset=(0, 0)):
        """Render powerup as a colored circle."""
        if self.collected:
            return
        
        color = self.SKILL_COLORS.get(self.skill_type, (200, 200, 200))
        center_x = int(self.pos[0] + self.size[0] / 2 - offset[0])
        center_y = int(self.pos[1] - self.float_offset - offset[1])
        
        if self.image:
            img_y = center_y - self.image.get_height() // 2
            img_x = center_x - self.image.get_width() // 2
            surf.blit(self.image, (img_x, img_y))
        else:
            # Draw glow circle fallback
            pygame.draw.circle(surf, color, (center_x, center_y), 6, 2)
            pygame.draw.circle(surf, color, (center_x, center_y), 4)
    
    def collect(self, player):
        """Collect this powerup and unlock the associated skill."""
        if not self.collected:
            self.collected = True
            if self.skill_type == 'life':
                player.lives += 1
            else:
                player.skill_manager.unlock_skill(self.skill_type)

            # Show notification (fallback to font render if missing image)
            from scripts.Notification import Notification
            notif_image = player.game.assets.get(f'skill/{self.skill_type}')
            if notif_image is None:
                notif_image = player.game.font.render(self.skill_type.replace('_', ' ').title(), True, (255, 255, 255))
            player.game.notifications.append(Notification(player.game, notif_image, duration=120))

            return True
        return False
