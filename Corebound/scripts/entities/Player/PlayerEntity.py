import pygame, math, random
from scripts.entities.BasicEntity import PhysicsEntity
from scripts.particle import Particle
from scripts.skills.SkillManager import SkillManager

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.skill_manager = SkillManager()
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0
        self.lives = 3  # Player starts with three lives
        self.invulnerable = 0  # frames of invulnerability after getting hit
    
    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)
        
        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0
            # Reset jumps based on double jump skill
            self.jumps = 2 if self.skill_manager.has_skill('double_jump') else 1
            
        self.wall_slide = False #reset wall slide state
        if self.skill_manager.has_skill('wall_slide') and (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5) #limit falling speed during wall slide
            if self.collisions['right']:
                self.flip = False
            elif self.collisions['left']:
                self.flip = True
            self.set_action('wall_slide')
        else:
            self.wall_slide = False

        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:                
                self.set_action('run')
            else:
                self.set_action('idle')

        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1) #decrease dashing state counter
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1) #increase dashing recovery counter
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 10 #maintain dash speed during dash
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1 #initial strong deceleration after dash endsmax(0, self.dashing - 1)
            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(Particle(self.game, "particle", self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))
        if abs(self.dashing) in {60, 50}:
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle)* speed, math.sin(angle)* speed]
                self.game.particles.append(Particle(self.game, "particle", self.rect().center, velocity=pvelocity, frame=random.randint(0, 7))) #dash particles

        # Decrement invulnerability timer
        if self.invulnerable > 0:
            self.invulnerable = max(0, self.invulnerable - 1)

        if self.velocity[0] > 0:
            self.velocity[0] = max(0, self.velocity[0] - 0.1, 0) #friction when moving right
        else:
            self.velocity[0] = min(0, self.velocity[0] + 0.1, 0) #friction when moving left

    def render(self, surf, offset=(0, 0)):
        if abs(self.dashing) <= 50:
            super().render(surf, offset=offset)
           

    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:  #jumping off left wall
                self.velocity[0] = 2 #horizontal jump boost
                self.velocity[1] = -2.7 #vertical jump strength
                self.air_time = 5 #set air time to prevent jump animation from flickering
                self.jumps = max(0, self.jumps - 1) #consume a jump
                return True #jump successful -> for animation later on
            
            elif not self.flip and self.last_movement[0] > 0:  #jumping off right wall
                self.velocity[0] = -2 #horizontal jump boost
                self.velocity[1] = -2.7 #vertical jump strength
                self.air_time = 5 #set air time to prevent jump animation from flickering
                self.jumps = max(0, self.jumps - 1) #consume a jump
                return True
            
        elif self.jumps:
            self.velocity[1] = -3 #jump strength
            self.jumps -= 1
            self.air_time = 5 #set air time to prevent jump animation from flickering

    def dash(self):
        if not self.dashing and self.skill_manager.has_skill('dash'):
            if self.flip:
                self.dashing = -60 #dash left
                self.velocity[0] = -2.6
            else:
                self.dashing = 60 #dash right
                self.velocity[0] = 2.6

    def take_damage(self, amount=1):
        """Reduce player lives and apply brief invulnerability and knockback."""
        if self.invulnerable:
            return False
        self.lives = max(0, self.lives - amount)
        self.invulnerable = 60  # 1 second at 60fps
        # Simple knockback opposite of current facing
        self.velocity[0] = -2 if not self.flip else 2
        # Visual feedback
        if hasattr(self.game, 'screenshake'):
            self.game.screenshake = max(10, getattr(self.game, 'screenshake', 0))
        for i in range(10):
            angle = random.random() * math.pi * 2
            speed = random.random() * 0.8
            pvelocity = [math.cos(angle)* speed, math.sin(angle)* speed]
            self.game.particles.append(Particle(self.game, "particle", self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))
        # TODO: handle player death (respawn or game over) when lives == 0
        return self.lives == 0
