import pygame

class PlayerAttack:
    def __init__(self, game, player):
        """
        Initialize attack system that uses pure white pixels in animations as hitboxes.
        
        Args:
            game: The game instance
            player: The player entity this attack belongs to
        """
        self.game = game
        self.player = player
        self.active = False
        self.attack_frames = []  # List of attack hitbox rects for current animation frame
        self.hit_enemies = []  # Track which enemies were hit in current attack to prevent multi-hit
        
    def extract_white_pixels(self, surface, flip=False):
        """
        Extract pure white (255, 255, 255) pixels from a surface and return collision rects.
        
        Args:
            surface: The pygame surface to analyze
            flip: Whether the surface is flipped horizontally
            
        Returns:
            List of pygame.Rect objects representing white pixel regions
        """
        width, height = surface.get_size()
        rects = []
        
        # Create a pixelarray for efficient pixel access
        try:
            pxarray = pygame.PixelArray(surface.copy())
            white_color = surface.map_rgb((255, 255, 255))
            
            # Track which pixels we've already added to rects
            checked = set()
            
            for y in range(height):
                for x in range(width):
                    if (x, y) in checked:
                        continue
                        
                    # Check if pixel is pure white
                    if pxarray[x, y] == white_color:
                        # Found white pixel - create a rect for it
                        # Could expand this to group adjacent white pixels into larger rects
                        rects.append(pygame.Rect(x, y, 1, 1))
                        checked.add((x, y))
            
            del pxarray  # Release the pixel array
            
        except Exception as e:
            # If extraction fails, return empty list
            print(f"Error extracting white pixels: {e}")
            return []
        
        return rects
    
    def extract_white_regions(self, surface, flip=False):
        """
        Extract contiguous regions of white pixels and return optimized rects.
        More efficient than individual pixels - groups adjacent white pixels.
        
        Args:
            surface: The pygame surface to analyze
            flip: Whether the surface is flipped
            
        Returns:
            List of pygame.Rect objects
        """
        width, height = surface.get_size()
        
        try:
            pxarray = pygame.PixelArray(surface.copy())
            white_color = surface.map_rgb((255, 255, 255))
            
            # Create a 2D grid to track white pixels
            white_grid = [[False for _ in range(width)] for _ in range(height)]
            
            for y in range(height):
                for x in range(width):
                    if pxarray[x, y] == white_color:
                        white_grid[y][x] = True
            
            del pxarray
            
            # Group adjacent white pixels into rectangular regions
            rects = []
            visited = [[False for _ in range(width)] for _ in range(height)]
            
            for y in range(height):
                for x in range(width):
                    if white_grid[y][x] and not visited[y][x]:
                        # Start of a new region - flood fill to find extent
                        min_x, max_x = x, x
                        min_y, max_y = y, y
                        
                        # Simple horizontal scan for this row
                        end_x = x
                        while end_x < width and white_grid[y][end_x] and not visited[y][end_x]:
                            visited[y][end_x] = True
                            max_x = end_x
                            end_x += 1
                        
                        # Create rect for this region
                        rect_width = max_x - min_x + 1
                        rect_height = max_y - min_y + 1
                        rects.append(pygame.Rect(min_x, min_y, rect_width, rect_height))
            
            return rects
            
        except Exception as e:
            print(f"Error extracting white regions: {e}")
            return []
    
    def get_attack_hitboxes(self, animation_frame, player_pos, flip):
        """
        Get attack hitboxes based on white pixels in current animation frame.
        
        Args:
            animation_frame: The current pygame surface of the player animation
            player_pos: Player's current position (x, y)
            flip: Whether player is flipped
            
        Returns:
            List of pygame.Rect objects in world coordinates
        """
        # Extract white pixel regions from the frame
        local_rects = self.extract_white_regions(animation_frame, flip)
        
        # Convert local coordinates to world coordinates
        world_rects = []
        for rect in local_rects:
            world_rect = rect.copy()
            
            # Apply player position offset
            if flip:
                # Mirror the x coordinate when flipped
                world_rect.x = player_pos[0] + (animation_frame.get_width() - rect.x - rect.width) + self.player.anim_offset[0]
            else:
                world_rect.x = player_pos[0] + rect.x + self.player.anim_offset[0]
            
            world_rect.y = player_pos[1] + rect.y + self.player.anim_offset[1]
            world_rects.append(world_rect)
        
        return world_rects
    
    def start_attack(self):
        """Begin an attack - call this when player initiates attack action"""
        self.active = True
        self.hit_enemies = []
        
    def end_attack(self):
        """End the attack - call when attack animation finishes"""
        self.active = False
        self.hit_enemies = []
        self.attack_frames = []
    
    def update(self, enemies):
        """
        Update attack hitboxes and check for collisions with enemies.
        Should be called every frame during an attack.
        
        Args:
            enemies: List of enemy entities to check collisions against
        """
        if not self.active:
            return
        
        # Get current animation frame if player has animation
        if hasattr(self.player, 'animation'):
            current_frame = self.player.animation.img()
            self.attack_frames = self.get_attack_hitboxes(
                current_frame, 
                self.player.pos, 
                self.player.flip
            )
            
            # Check collisions with enemies
            for enemy in enemies:
                # Skip if already hit this enemy in current attack
                if enemy in self.hit_enemies:
                    continue
                    
                enemy_rect = enemy.rect()
                
                # Check if any attack hitbox overlaps with enemy
                for attack_rect in self.attack_frames:
                    if attack_rect.colliderect(enemy_rect):
                        # Hit detected!
                        self.on_hit_enemy(enemy)
                        self.hit_enemies.append(enemy)
                        break  # Only hit once per enemy
    
    def on_hit_enemy(self, enemy):
        """
        Called when an attack successfully hits an enemy.
        Override or extend this for custom hit behavior.
        
        Args:
            enemy: The enemy entity that was hit
        """
        # Deal damage to enemy
        if hasattr(enemy, 'take_damage'):
            enemy.take_damage(1)
        elif hasattr(enemy, 'health'):
            enemy.health -= 1
        
        # Create hit effects (sparks, particles, etc.)
        # You can customize this based on your game's visual style
        
    def render_debug(self, surf, offset=(0, 0)):
        """
        Render attack hitboxes for debugging purposes.
        Shows white pixel hitboxes as red rectangles.
        
        Args:
            surf: Surface to render on
            offset: Camera offset
        """
        if self.active and self.attack_frames:
            for rect in self.attack_frames:
                debug_rect = pygame.Rect(
                    rect.x - offset[0],
                    rect.y - offset[1],
                    rect.width,
                    rect.height
                )
                pygame.draw.rect(surf, (255, 0, 0), debug_rect, 1)  # Red outline