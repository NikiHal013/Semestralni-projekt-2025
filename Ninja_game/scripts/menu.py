import pygame
import os

class TextButton:
    def __init__(self, x, y, text, font, callback=None):
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.callback = callback
        self.selected = False
        self.color_text = (255, 255, 255)
        self.color_selected = (255, 100, 100)
    
    def activate(self):
        """Activate button (called when selected with keyboard or mouse)."""
        if self.callback:
            self.callback()
    
    def render(self, display):
        """Render button text with outline."""
        color = self.color_selected if self.selected else self.color_text
        text_surf = self.font.render(self.text, True, color)
        text_rect = text_surf.get_rect(center=(self.x, self.y))
        
        # Draw outline
        outline_width = 1
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    outline_text = self.font.render(self.text, True, (0, 0, 0))
                    display.blit(outline_text, (text_rect.x + dx, text_rect.y + dy))
        # Draw main text
        display.blit(text_surf, text_rect)
        return text_rect
    
    def is_clicked(self, pos, rect):
        """Check if button was clicked."""
        return rect.collidepoint(pos)


class Menu:
    def __init__(self):
        self.font = self._load_pixel_font()
        self.title_font = self._load_title_font()
        self.small_font = self._load_small_font()
        self.state = "main"  # main, settings, end, pause
        self.buttons = {}
        self.button_rects = {}
        self.selected_button_index = 0
        self.leaderboard_data = []
        self.leaderboard_data_by_mode = {
            "baby_mode": [],
            "normal": [],
            "hard": []
        }
        self.end_time = 0
        self.end_level = 0
        self.callbacks = {
            "play": None,
            "settings": None,
            "quit": None,
            "back": None
        }
        # Settings
        self.sfx_enabled = True
        self.difficulty = "normal"  # baby_mode, normal, hard
        self.difficulties = ["BABY MODE", "NORMAL", "HARD"]
        self.difficulty_names = ["baby_mode", "normal", "hard"]  # Actual difficulty names for leaderboard
        self.difficulty_index = 1  # Start with normal
        self.difficulty_change_callback = None
    def _load_pixel_font(self):
        """Load system font."""
        return pygame.font.SysFont("courier", 10, bold=True)
    
    def _load_title_font(self):
        """Load title font."""
        return pygame.font.SysFont("courier", 14, bold=True)
    
    def _load_small_font(self):
        """Load small font for leaderboard results."""
        return pygame.font.SysFont("courier", 8, bold=True)
    
    def _render_outlined_text(self, display, text, font, color, outline_color, x, y):
        """Draw text with black outline."""
        outline_width = 1
        # Draw outline by rendering text at offset positions
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    outline_text = font.render(text, True, outline_color)
                    display.blit(outline_text, (x + dx, y + dy))
        # Draw main text on top
        main_text = font.render(text, True, color)
        display.blit(main_text, (x, y))
    
    def setup_main_menu(self, width, height):
        center_x = width // 2
        button_y_start = height // 2 + 40
        button_spacing = 25
        
        self.buttons["main"] = [
            TextButton(center_x, button_y_start, "PLAY", self.font, self.callbacks["play"]),
            TextButton(center_x, button_y_start + button_spacing, "SETTINGS", self.font, self.callbacks["settings"]),
            TextButton(center_x, button_y_start + button_spacing * 2, "QUIT", self.font, self.callbacks["quit"])
        ]
        self.selected_button_index = 0
        self._update_button_selection()
    
    def setup_settings_menu(self, width, height):
        center_x = width // 2
        button_y_start = height // 2 - 20
        button_spacing = 25
        
        self.buttons["settings"] = [
            TextButton(center_x, button_y_start, "SFX: ON" if self.sfx_enabled else "SFX: OFF", self.font, self._toggle_sfx),
            TextButton(center_x, button_y_start + button_spacing, "DIFFICULTY", self.font, None),
            TextButton(center_x, button_y_start + button_spacing * 2, "BACK", self.font, self.callbacks["back"])
        ]
        self.selected_button_index = 0
        self._update_button_selection()
    
    def _toggle_sfx(self):
        self.sfx_enabled = not self.sfx_enabled
        self.buttons["settings"][0].text = "SFX: ON" if self.sfx_enabled else "SFX: OFF"
        # Call callback if set (for controlling ambience sound)
        if hasattr(self, 'toggle_sfx_callback') and self.toggle_sfx_callback:
            self.toggle_sfx_callback()
    
    def setup_end_menu(self, width, height):
        center_x = width // 2
        button_y = height // 2 + 80
        
        self.buttons["end"] = [
            TextButton(center_x, button_y, "MAIN MENU", self.font, self.callbacks["back"])
        ]
        self.selected_button_index = 0
        self._update_button_selection()
    
    def setup_pause_menu(self, width, height):
        center_x = width // 2
        button_y_start = height // 2 + 40
        button_spacing = 25
        
        self.buttons["pause"] = [
            TextButton(center_x, button_y_start, "RESUME", self.font, self.callbacks["resume"]),
            TextButton(center_x, button_y_start + button_spacing, "NEW RUN - PRESS R IN GAME", self.font, self.callbacks["restart"]),
            TextButton(center_x, button_y_start + button_spacing * 2, "MAIN MENU", self.font, self.callbacks["back"])
        ]
        self.selected_button_index = 0
        self._update_button_selection()
    
    def _update_button_selection(self):
        current_buttons = self.buttons.get(self.state, [])
        for i, button in enumerate(current_buttons):
            button.selected = (i == self.selected_button_index)
    
    def update(self, mouse_pos):
        pass
    
    def handle_click(self, mouse_pos):
        current_buttons = self.buttons.get(self.state, [])
        rects = self.button_rects.get(self.state, [])
        
        for button, rect in zip(current_buttons, rects):
            if button.is_clicked(mouse_pos, rect):
                button.activate()
    
    def handle_key_press(self, key):
        current_buttons = self.buttons.get(self.state, [])
        
        if not current_buttons:
            return
        
        if key == pygame.K_UP or key == pygame.K_w:
            self.selected_button_index = (self.selected_button_index - 1) % len(current_buttons)
            self._update_button_selection()
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.selected_button_index = (self.selected_button_index + 1) % len(current_buttons)
            self._update_button_selection()
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            current_buttons[self.selected_button_index].activate()
        elif (key == pygame.K_LEFT or key == pygame.K_a) and self.state == "settings" and self.selected_button_index == 1:
            # Cycle difficulty left
            self.difficulty_index = (self.difficulty_index - 1) % len(self.difficulties)
            self.difficulty = self.difficulty_names[self.difficulty_index]
            if self.difficulty_change_callback:
                self.difficulty_change_callback()
        elif (key == pygame.K_RIGHT or key == pygame.K_d) and self.state == "settings" and self.selected_button_index == 1:
            # Cycle difficulty right
            self.difficulty_index = (self.difficulty_index + 1) % len(self.difficulties)
            self.difficulty = self.difficulty_names[self.difficulty_index]
            if self.difficulty_change_callback:
                self.difficulty_change_callback()
            if self.difficulty_change_callback:
                self.difficulty_change_callback()
    
    def set_leaderboard(self, leaderboard_data):
        # Backward compatibility: set the active difficulty leaderboard
        self.leaderboard_data = leaderboard_data

    def set_all_leaderboards(self, data_by_mode):
        for key in self.leaderboard_data_by_mode.keys():
            self.leaderboard_data_by_mode[key] = data_by_mode.get(key, [])
    
    def set_end_game_info(self, time_ms, level):
        self.end_time = time_ms
        self.end_level = level
    
    def render(self, display, width, height):
        if self.state == "main":
            self._render_main_menu(display, width, height)
        elif self.state == "settings":
            self._render_settings_menu(display, width, height)
        elif self.state == "pause":
            self._render_pause_menu(display, width, height)
        elif self.state == "end":
            self._render_end_menu(display, width, height)
    
    def _render_main_menu(self, display, width, height):
        display.fill((30, 30, 30))
        
        # Title
        title_text = self.title_font.render("NINJA GAME", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(width // 2, 30))
        self._render_outlined_text(display, "NINJA GAME", self.title_font, (255, 255, 255), (0, 0, 0), title_rect.x, title_rect.y)
        
        # Leaderboards for all modes side by side
        column_centers = [width // 6, width // 2, width * 5 // 6]
        modes = [
            ("BABY MODE", "baby_mode", column_centers[0]),
            ("NORMAL", "normal", column_centers[1]),
            ("HARD", "hard", column_centers[2]),
        ]
        start_y = 60
        for title, key, cx in modes:
            data = self.leaderboard_data_by_mode.get(key, [])
            self._render_leaderboard_column(display, cx, start_y, title, data)
        
        # Buttons
        self.button_rects["main"] = []
        for button in self.buttons.get("main", []):
            rect = button.render(display)
            self.button_rects["main"].append(rect)
    
    def _render_settings_menu(self, display, width, height):
        display.fill((30, 30, 30))
        
        # Title
        title_text = self.title_font.render("SETTINGS", True, (255, 255, 255))
        title_x = width // 2 - title_text.get_width() // 2
        self._render_outlined_text(display, "SETTINGS", self.title_font, (255, 255, 255), (0, 0, 0), title_x, 30)
        
        # Display difficulty selection
        difficulty_text = f"Difficulty: {self.difficulties[self.difficulty_index]}"
        diff_surf = self.font.render(difficulty_text, True, (200, 200, 200))
        diff_x = width // 2 - diff_surf.get_width() // 2
        self._render_outlined_text(display, difficulty_text, self.font, (200, 200, 200), (0, 0, 0), diff_x, 60)
        self._render_outlined_text(display, "(Use LEFT/RIGHT to change)", self.font, (150, 150, 150), (0, 0, 0), width // 2 - 70, 75)
        
        # Buttons
        self.button_rects["settings"] = []
        for button in self.buttons.get("settings", []):
            rect = button.render(display)
            self.button_rects["settings"].append(rect)
    
    def _render_end_menu(self, display, width, height):
        display.fill((30, 30, 30))
        
        # Title
        title_surf = self.title_font.render("LEVEL COMPLETE!", True, (255, 255, 255))
        title_x = width // 2 - title_surf.get_width() // 2
        self._render_outlined_text(display, "LEVEL COMPLETE!", self.title_font, (255, 255, 255), (0, 0, 0), title_x, 30)
        
        # Display completion time
        time_str = self._format_time(self.end_time)
        time_text = f"Time: {time_str}"
        time_surf = self.font.render(time_text, True, (255, 255, 255))
        time_x = width // 2 - time_surf.get_width() // 2
        self._render_outlined_text(display, time_text, self.font, (255, 255, 255), (0, 0, 0), time_x, 70)
        
        level_text = f"Level: {self.end_level}"
        level_surf = self.font.render(level_text, True, (255, 255, 255))
        level_x = width // 2 - level_surf.get_width() // 2
        self._render_outlined_text(display, level_text, self.font, (255, 255, 255), (0, 0, 0), level_x, 90)
        
        # Leaderboard
        self._render_leaderboard(display, width, height, 110)
        
        # Buttons
        self.button_rects["end"] = []
        for button in self.buttons.get("end", []):
            rect = button.render(display)
            self.button_rects["end"].append(rect)
    
    def _render_leaderboard(self, display, width, height, start_y):
        """Render leaderboard columns for the end menu."""
        column_centers = [width // 6, width // 2, width * 5 // 6]
        modes = [
            ("BABY MODE", "baby_mode", column_centers[0]),
            ("NORMAL", "normal", column_centers[1]),
            ("HARD", "hard", column_centers[2]),
        ]
        for title, key, cx in modes:
            data = self.leaderboard_data_by_mode.get(key, [])
            self._render_leaderboard_column(display, cx, start_y, title, data)
    
    def _render_pause_menu(self, display, width, height):
        display.fill((30, 30, 30))
        
        # Title
        title_surf = self.title_font.render("PAUSED", True, (255, 255, 255))
        title_x = width // 2 - title_surf.get_width() // 2
        self._render_outlined_text(display, "PAUSED", self.title_font, (255, 255, 255), (0, 0, 0), title_x, height // 2 - 60)
        
        # Buttons
        self.button_rects["pause"] = []
        for button in self.buttons.get("pause", []):
            rect = button.render(display)
            self.button_rects["pause"].append(rect)
    
    def _render_leaderboard_column(self, display, center_x, start_y, title, data):
        """Render a single leaderboard column at center_x."""
        title_surf = self.title_font.render(title, True, (255, 255, 255))
        title_x = center_x - title_surf.get_width() // 2
        self._render_outlined_text(display, title, self.title_font, (255, 255, 255), (0, 0, 0), title_x, start_y)
        
        y_offset = start_y + 18
        for i, entry in enumerate(data[:8]):
            rank = i + 1
            time_str = entry.get("formatted_time", "00:00:000")
            att = entry.get("att:", 0)
            text = f"{rank}. {time_str} - {att}"
            text_surf = self.small_font.render(text, True, (200, 200, 200))
            text_x = center_x - text_surf.get_width() // 2
            self._render_outlined_text(display, text, self.small_font, (200, 200, 200), (0, 0, 0), text_x, y_offset)
            y_offset += 14
    
    def _format_time(self, time_ms):
        total_ms = int(time_ms)
        minutes = (total_ms // 60000) % 60
        seconds = (total_ms // 1000) % 60
        milliseconds = total_ms % 1000
        return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"

