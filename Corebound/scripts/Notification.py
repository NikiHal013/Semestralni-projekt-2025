import pygame

class Notification:
    """Displays a centered notification that fades out over time."""
    
    def __init__(self, game, image, duration=120):
        self.game = game
        self.duration = duration  # frames
        self.timer = duration
        self.alpha = 255
        
        # Scale image to fit middle third of display width
        display_width = game.display.get_width()
        target_width = display_width // 3
        scale_factor = target_width / image.get_width()
        new_width = int(image.get_width() * scale_factor)
        new_height = int(image.get_height() * scale_factor)
        self.image = pygame.transform.scale(image, (new_width, new_height))
    
    def update(self):
        """Update notification fade."""
        self.timer -= 1
        # Fade out in last third of duration
        fade_start = self.duration // 3
        if self.timer < fade_start:
            self.alpha = int(255 * (self.timer / fade_start))
        return self.timer <= 0
    
    def render(self, surf):
        """Render notification centered on screen."""
        # Create surface with alpha
        img_copy = self.image.copy()
        img_copy.set_alpha(self.alpha)
        
        # Center on screen
        center_x = surf.get_width() // 2 - img_copy.get_width() // 2
        center_y = surf.get_height() // 2 - img_copy.get_height() // 2
        
        surf.blit(img_copy, (center_x, center_y))
