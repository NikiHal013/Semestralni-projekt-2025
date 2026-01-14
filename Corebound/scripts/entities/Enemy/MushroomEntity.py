import pygame, math, random
from scripts.entities.Enemy.EnemyEntity import EnemyEntity
from scripts.particle import Particle
from scripts.sparks import Spark

class MushroomEntity(EnemyEntity):
    def __init__(self, game, pos, size):
        # Get size from sprite
        sprite_size = game.assets['mushroom/idle'].images[0].get_size()
        super().__init__(game, pos, sprite_size)
        
        self.type = 'mushroom'
        self.health = 2  # Takes 2 hits to kill
        self.detection_range = 100  # Distance to detect player
        self.chase_speed = 0.7  # Speed when chasing
        self.set_action('idle')
    
    def can_see_player(self):
        """Check if player is within detection range"""
        player_center_x = self.game.player.rect().centerx
        my_center_x = self.rect().centerx
        distance_x = player_center_x - my_center_x
        
        # Check horizontal distance
        if abs(distance_x) > self.detection_range:
            return False
        
        return True
    
    def update(self, tilemap, movement=(0, 0)):
        # Check if we can see the player and should chase
        if self.can_see_player():
            player_center_x = self.game.player.rect().centerx
            my_center_x = self.rect().centerx
            distance_x_signed = player_center_x - my_center_x
            
            # Chase the player
            if distance_x_signed > 0:
                self.flip = False  # Face right
                movement = (movement[0] + self.chase_speed, movement[1])
            else:
                self.flip = True  # Face left
                movement = (movement[0] - self.chase_speed, movement[1])
        else:
            # Normal patrol behavior when not chasing
            if self.walking:
                # Check for ground ahead
                check_x = self.rect().centerx + (-7 if self.flip else 7)
                check_y = self.pos[1] + self.size[1]
                
                if tilemap.solid_check((check_x, check_y)):
                    # Ground ahead, move if not hitting wall
                    if (self.collisions['right'] or self.collisions['left']):
                        self.flip = not self.flip
                    else:
                        movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
                else:
                    # No ground, turn around
                    self.flip = not self.flip
                
                self.walking = max(0, self.walking - 1)
            elif random.random() < 0.01:
                # Randomly start walking
                self.walking = random.randint(30, 120)
        
        # Call BasicEntity update directly, skip EnemyEntity's update to avoid double walking logic
        from scripts.entities.BasicEntity import PhysicsEntity
        PhysicsEntity.update(self, tilemap, movement=movement)
        
        # Set animation
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
    
    def take_damage(self, damage=1, attacker_flip=False):
        """
        Called when enemy takes damage from player attack.
        
        Args:
            damage: Amount of damage to take
            attacker_flip: Direction attacker is facing (for knockback)
            
        Returns:
            True if enemy died, False otherwise
        """
        self.health -= damage
        
        # Create hit effects
        if hasattr(self.game, 'screenshake'):
            self.game.screenshake = max(12, self.game.screenshake)
        
        for i in range(15):
            angle = random.random() * math.pi * 2
            speed = random.random() * 3
            self.game.sparks.append(Spark(self.rect().center, angle, 1 + random.random()))
            self.game.particles.append(Particle(
                self.game, "particle", self.rect().center,
                velocity=[math.cos(angle) * speed * 0.5, math.sin(angle) * speed],
                frame=random.randint(0, 7)
            ))
        
        # Check if dead
        if self.health <= 0:
            self.set_action('die')
            # More intense death effects
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 4
                self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                self.game.particles.append(Particle(
                    self.game, "particle", self.rect().center,
                    velocity=[math.cos(angle) * speed, math.sin(angle) * speed],
                    frame=random.randint(0, 7)
                ))
            return True  # Signal to remove this enemy
        
        # Knockback from hit
        self.velocity[0] = 3 if attacker_flip else -3
        return False
    
    def set_action(self, action):
        """Override to use mushroom-specific animations"""
        if action != self.action:
            self.action = action
            # Map action names to asset paths
            asset_map = {
                'idle': 'mushroom/idle',
                'run': 'mushroom/run',
                'attack': 'mushroom/attack',
                'hit': 'mushroom/hit',
                'die': 'mushroom/die'
            }
            if action in asset_map and asset_map[action] in self.game.assets:
                self.animation = self.game.assets[asset_map[action]].copy()
                # Adjust anim_offset based on animation
                anim_offsets = {
                    'idle': (0, 0),
                    'run': (0, -3),  # Lift 3 pixels when running
                    'hit': (0, 0),
                    'die': (0, 0)
                }
                self.anim_offset = anim_offsets.get(action, (0, 0))
    
    def render(self, surf, offset=(0, 0)):
        """Render the mushroom with its animation"""
        if hasattr(self, 'animation'):
            surf.blit(
                pygame.transform.flip(self.animation.img(), self.flip, False),
                (self.pos[0] - offset[0] + self.anim_offset[0], 
                 self.pos[1] - offset[1] + self.anim_offset[1])
            )