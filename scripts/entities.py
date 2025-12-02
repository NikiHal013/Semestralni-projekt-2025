import pygame

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False} #collision states - remember if we are colliding in any direction
    
        self.action = ''
        self.anim_offset = (-3 , -3) #offset to center the animation properly / hitbox vs sprite size
        self.flip = False #for horizontal flipping of sprite based on movement direction
        self.set_action ('idle')

    def rect(self): #return the rectangle representing the entity's position and size
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action): #change animation based on action
        if self.action != action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + action].copy()
        
    def update(self, tilemap, movement=(0, 0)): #movement is a tuple (horizontal_movement, vertical_movement)
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1]) # Apply velocity to movement
        
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left # Handle right collision
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right # Handle left collision
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
        
        self.pos[1] += frame_movement[1]        #important to separate horizontal and vertical collision checks
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top # Handle down collision
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom # Handle up collision
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
        
        self.velocity[1] = min(5, self.velocity[1] + 0.1) # Gravity, limit falling speed (it chooses the smaller value between 5 and current velocity + 0.1)
        
        if self.collisions['down'] or self.collisions['up']: # Stop vertical velocity on collision
            self.velocity[1] = 0

        self.animation.update() #update animation frame

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1])) #draw current animation frame with offset and flipping (x and y)
        # Update animation after rendering to avoid frame skip on first render

class PlayerEntity(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, "player", pos, size)
        self.air_time = 0 #time spent in air counter


    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement) # Determine action based on movement and collisions
        

        self.air_time +=1 #time spent in air counter
        if self.collisions['down']:
            self.air_time = 0
        if self.air_time > 4:
            self.set_action('jump')
        elif movement[0] != 0:                
            self.set_action('run')
        else:
            self.set_action('idle')