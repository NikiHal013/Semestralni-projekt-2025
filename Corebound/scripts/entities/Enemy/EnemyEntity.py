import random
from scripts.entities.BasicEntity import PhysicsEntity

class EnemyEntity(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, "enemy", pos, size)
        self.manual_flip = True  # EnemyEntity controls flipping with patrol behavior
        self.walking = 0 #walking state counter

    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)): #check for ground in front of enemy
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip #turn around on wall collision
                else: 
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip #turn around if no ground ahead
            self.walking = max(0, self.walking - 1)
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement=movement) # Determine action based on movement and collisions

        if movement[0] != 0:                
            self.set_action('run')
        else:
            self.set_action('idle')


    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)
