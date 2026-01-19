import pygame
import os

class UI:
    def __init__(self):
        # Use system courier font (pixel_font.ttf is corrupted)
        self.font = pygame.font.SysFont("courier", 10, bold=True)
        
    def render(self, display, attempts, elapsed_time, level):
        width = display.get_width()
        
        # Format time: milliseconds to mm:ss:ms format
        total_ms = int(elapsed_time)
        minutes = (total_ms // 60000) % 60
        seconds = (total_ms // 1000) % 60
        milliseconds = total_ms % 1000
        time_str = f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"
        
        # Text colors
        text_color = (255, 255, 255)
        outline_color = (0, 0, 0)
        outline_width = 1
        
        def render_outlined_text(text_surface, pos):
            """Draw text with black outline"""
            # Draw outline by rendering text at offset positions
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        outline_text = self.font.render(text_surface, True, outline_color)
                        display.blit(outline_text, (pos[0] + dx, pos[1] + dy))
            # Draw main text on top
            main_text = self.font.render(text_surface, True, text_color)
            display.blit(main_text, pos)
        
        # Top left: Attempts
        render_outlined_text(f"Attempts: {attempts}", (5, 5))
        
        # Top middle: Timer
        timer_text = self.font.render(time_str, True, text_color)
        timer_x = (width - timer_text.get_width()) // 2
        render_outlined_text(time_str, (timer_x, 5))
        
        # Top right: Level
        level_text = self.font.render(f"Level: {level}", True, text_color)
        level_x = width - level_text.get_width() - 5
        render_outlined_text(f"Level: {level}", (level_x, 5))

