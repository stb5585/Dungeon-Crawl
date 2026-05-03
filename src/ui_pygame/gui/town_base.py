"""
Base class for all town UI screens.
Centralizes common functionality, colors, fonts, and background management.
"""

import os

import pygame


class TownColors:
    """Centralized color definitions for town UI."""
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GOLD = (218, 165, 32)  # Warm gold for highlights
    YELLOW = (255, 255, 0)  # Bright yellow for special cases
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    BLUE = (100, 149, 237)
    GREEN = (0, 200, 0)
    RED = (200, 0, 0)
    BORDER_COLOR = (200, 200, 200)
    HIGHLIGHT_BG = (60, 60, 80)
    DARK_OVERLAY = (0, 0, 0, 180)  # Semi-transparent black for overlays


class TownScreenBase:
    """
    Base class for all town-related UI screens.
    Manages the town background and provides common functionality.
    """
    
    def __init__(self, presenter):
        self.presenter = presenter
        self.screen = presenter.screen
        self.width = presenter.width
        self.height = presenter.height
        
        # Use centralized colors
        self.colors = TownColors
        
        # Fonts
        self.title_font = presenter.title_font
        self.large_font = presenter.large_font
        self.normal_font = presenter.normal_font
        self.small_font = presenter.small_font
        
        # Load background once
        self.background = None
        self._load_background()
    
    def _load_background(self):
        """Load and scale the town background image."""
        bg_path = os.path.join("src", "ui_pygame", "assets", "backgrounds", "town.png")
        if os.path.exists(bg_path):
            try:
                bg_image = pygame.image.load(bg_path)
                # Scale to fit screen while maintaining aspect ratio
                bg_width, bg_height = bg_image.get_size()
                scale_x = self.width / bg_width
                scale_y = self.height / bg_height
                scale = max(scale_x, scale_y)  # Use max to cover entire screen
                
                new_width = int(bg_width * scale)
                new_height = int(bg_height * scale)
                self.background = pygame.transform.scale(bg_image, (new_width, new_height))
            except Exception as e:
                print(f"Warning: Could not load town background: {e}")
                self.background = None
        else:
            print(f"Warning: Town background not found at {bg_path}")
    
    def draw_background(self):
        """Draw the town background image."""
        if self.background:
            # Center the background
            bg_rect = self.background.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(self.background, bg_rect)
        else:
            # Fallback: solid color
            self.screen.fill(self.colors.BLACK)

    def draw_top(self):
        """Draw the top area (can be overridden by subclasses)."""
        pass

    def draw_options(self):
        """Draw the options panel (can be overridden by subclasses)."""
        pass

    def draw_semi_transparent_panel(self, rect, alpha=180):
        """Draw a semi-transparent dark panel."""
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (rect.x, rect.y))
        return overlay

    def popup_show_kwargs(self):
        """Common modal-popup options for town screens."""
        return {
            "background_draw_func": self.draw_background,
            "flush_events": True,
            "require_key_release": True,
        }

    def display_quest_text(self, quest_text):
        """Display quest text in the content area with slow printing animation."""
        import time
        import pygame
        import textwrap

        # Normalize text and peel off a header line if present (====== Name ======)
        text = quest_text.replace("\r\n", "\n")
        header_text = None

        lines = text.split("\n", 1)
        first_line = lines[0].strip()
        if first_line.startswith("======") and first_line.endswith("======"):
            header_text = first_line.replace("=", "").strip()
            text = lines[1] if len(lines) > 1 else ""

        # Paginate by paragraph (blank line separated) so hints show one at a time
        paragraphs = text.split("\n\n")

        def draw_content_formatted(lines_to_draw):
            """Draw content with special formatting for headers."""
            nonlocal header_text
            top_height = self.height // 12
            content_width = 2 * self.width // 3
            content_height = self.height - top_height
            content_x = self.width // 3
            content_y = top_height
            content_rect = pygame.Rect(content_x, content_y, content_width, content_height)
            
            self.draw_semi_transparent_panel(content_rect)
            pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, content_rect, 2)
            
            if lines_to_draw:
                text_x = content_rect.left + 20
                text_y = content_rect.top + 20

                # Draw header (once per frame) if present
                if header_text:
                    surface = self.normal_font.render(header_text, True, self.colors.GOLD)
                    line_width = surface.get_width()
                    centered_x = content_rect.centerx - line_width // 2
                    self.screen.blit(surface, (centered_x, text_y))
                    text_y += self.normal_font.get_height() + 8
                for line in lines_to_draw:
                    if line == "":
                        text_y += self.large_font.get_height()
                        continue
                    
                    surface = self.large_font.render(line, True, self.colors.WHITE)
                    self.screen.blit(surface, (text_x, text_y))
                    text_y += self.large_font.get_height() + 4

        if getattr(self.presenter, "debug_mode", False):
            # Show everything at once in debug
            full_lines = []
            for para in paragraphs:
                if para.strip():
                    full_lines.extend(para.split("\n"))
                    full_lines.append("")
            while True:
                self.draw_background()
                self.draw_top()
                self.draw_options()
                draw_content_formatted(full_lines)
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        import sys
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        return
                self.presenter.clock.tick(30)
        else:
            # Drain any pending key presses before starting slow-print
            try:
                pygame.event.clear(pygame.KEYDOWN)
            except Exception:
                for _ in pygame.event.get():
                    pass
            for para in paragraphs:
                if not para.strip():
                    continue
                
                # Always wrap paragraphs while preserving intentional line breaks
                raw_lines = para.split("\n")
                wrapped_lines = []
                for raw_line in raw_lines:
                    # Keep explicit blank lines
                    if not raw_line.strip():
                        wrapped_lines.append("")
                        continue

                    # Wrap each raw line individually to avoid losing manual breaks
                    wrapped = textwrap.wrap(raw_line, width=52, break_on_hyphens=False)
                    if wrapped:
                        wrapped_lines.extend(wrapped)
                    else:
                        wrapped_lines.append(raw_line)
                
                displayed_lines = []
                skipped = False

                for wrapped_line in wrapped_lines:
                    displayed_chars = ""
                    for char in wrapped_line:
                        displayed_chars += char

                        # Redraw screen
                        self.draw_background()
                        self.draw_top()
                        self.draw_options()

                        draw_content_formatted(displayed_lines + [displayed_chars])
                        pygame.display.flip()

                        time.sleep(0.02)

                        # Skip current paragraph on SPACE/ENTER/ESC
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                import sys
                                sys.exit()
                            elif event.type == pygame.KEYDOWN:
                                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                                    skipped = True
                                    break
                        if skipped:
                            break

                    if skipped:
                        displayed_lines = wrapped_lines
                        break
                    else:
                        displayed_lines.append(wrapped_line)

                # Show full paragraph and wait for key to advance
                while True:
                    self.draw_background()
                    self.draw_top()
                    self.draw_options()
                    draw_content_formatted(displayed_lines)
                    pygame.display.flip()

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            import sys
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            # Advance to next paragraph on any key
                            break
                    else:
                        self.presenter.clock.tick(30)
                        continue
                    break

            # Done with all paragraphs
            return
