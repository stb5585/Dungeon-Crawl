"""
Confirmation popup for character creation decisions.
"""

import pygame


class ConfirmationPopup:
    """
    A Yes/No confirmation popup that appears over the current screen.
    """
    
    def __init__(self, presenter, message: str, show_buttons: bool = True, slow_print: bool = False):
        self.presenter = presenter
        self.screen = presenter.screen
        self.width = presenter.width
        self.height = presenter.height
        self.message = message
        self.show_buttons = show_buttons
        # Slow print (typewriter) if True; disabled if debug mode is enabled
        self.slow_print = not getattr(presenter, "debug_mode", False) and slow_print
        self._start_ms = 10
        self._reveal_cps = 30  # characters per second
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GOLD = (218, 165, 32)  # Warm gold instead of bright yellow
        self.GRAY = (128, 128, 128)
        self.BORDER_COLOR = (200, 200, 200)
        self.HIGHLIGHT_BG = (60, 60, 80)
        self.POPUP_BG = (20, 20, 30)
        
        # Fonts
        self.normal_font = presenter.normal_font
        self.small_font = presenter.small_font
        self.message_font = presenter.normal_font
        self.instruction_font = presenter.small_font
        
        # State
        self.current_selection = 0  # 0 = Yes, 1 = No
        self.options = ["Yes", "No"]
        
        # Calculate popup size based on message content
        self.popup_width = 500
        # First, wrap text to calculate required height
        wrapped_lines = self._wrap_text(message, self.popup_width - 40)
        self._wrapped_lines = wrapped_lines
        self._full_text = "\n".join(wrapped_lines)
        # Each line takes approximately 30 pixels in height, plus padding
        min_height = 150 if show_buttons else 180
        content_height = len(wrapped_lines) * 30
        self.popup_height = max(min_height, content_height + 100)

        self.popup_x = (self.width - self.popup_width) // 2
        self.popup_y = (self.height - self.popup_height) // 2
        self.popup_rect = pygame.Rect(self.popup_x, self.popup_y, self.popup_width, self.popup_height)
    
    def _get_visible_lines(self):
        if not self.slow_print or not self._full_text:
            return self._wrapped_lines
        elapsed_ms = max(0, pygame.time.get_ticks() - self._start_ms)
        visible_chars = int((elapsed_ms / 1000.0) * self._reveal_cps)
        visible_text = self._full_text[:visible_chars]
        return visible_text.split("\n")

    def _reveal_complete(self) -> bool:
        if not self.slow_print:
            return True
        elapsed_ms = max(0, pygame.time.get_ticks() - self._start_ms)
        visible_chars = int((elapsed_ms / 1000.0) * self._reveal_cps)
        return visible_chars >= len(self._full_text)

    def draw_popup(self):
        """Draw the confirmation popup over the current screen."""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Draw popup background
        pygame.draw.rect(self.screen, self.POPUP_BG, self.popup_rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, self.popup_rect, 3)
        
        # Original compact confirmation layout
        y = self.popup_y + 30
        message_lines = self._get_visible_lines()
        for line in message_lines:
            text = self.normal_font.render(line, True, self.WHITE)
            text_rect = text.get_rect(centerx=self.popup_x + self.popup_width // 2)
            text_rect.y = y
            self.screen.blit(text, text_rect)
            y += 30

        if self.show_buttons:
            y = self.popup_y + self.popup_height - 70
            for i, option in enumerate(self.options):
                x = self.popup_x + (self.popup_width // 4) + i * (self.popup_width // 2)

                if i == self.current_selection:
                    option_rect = pygame.Rect(x - 50, y - 5, 100, 35)
                    pygame.draw.rect(self.screen, self.HIGHLIGHT_BG, option_rect)
                    pygame.draw.rect(self.screen, self.GOLD, option_rect, 2)
                    color = self.GOLD
                else:
                    color = self.WHITE

                text = self.normal_font.render(option, True, color)
                text_rect = text.get_rect(centerx=x, centery=y + 10)
                self.screen.blit(text, text_rect)
        else:
            instr_text = self.small_font.render("Press any key to continue...", True, self.GRAY)
            instr_rect = instr_text.get_rect(centerx=self.popup_x + self.popup_width // 2, bottom=self.popup_y + self.popup_height - 10)
            self.screen.blit(instr_text, instr_rect)

        pygame.display.flip()
    
    def _wrap_text(self, text, max_width):
        """Wrap text to fit within max_width while preserving explicit line breaks."""
        lines = []
        # First split by newlines to preserve explicit line breaks
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                # Preserve empty lines
                lines.append("")
                continue
            
            # Then wrap each paragraph by word
            words = paragraph.split()
            current_line = []
            
            for word in words:
                current_line.append(word)
                line = " ".join(current_line)
                line_width = self.message_font.size(line)[0]
                
                if line_width > max_width:
                    current_line.pop()
                    if current_line:
                        lines.append(" ".join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(" ".join(current_line))
        
        return lines
    
    def show(self, background_draw_func=None, flush_events: bool = False, require_key_release: bool = False, min_display_ms: int = 0) -> bool:
        """
        Show the popup and wait for user response.
        
        Args:
            background_draw_func: Optional function to redraw background screen
            
        Returns:
            True if Yes (or any key if no buttons), False if No
        """
        if flush_events:
            pygame.event.clear()

        background = None
        if background_draw_func is None:
            background = self._get_background_surface()
            background_draw_func = lambda: self.screen.blit(background, (0, 0))

        start_ms = pygame.time.get_ticks()
        self._start_ms = start_ms
        input_armed = not require_key_release

        def finish(result: bool) -> bool:
            if background_draw_func is not None:
                background_draw_func()
            elif background is not None:
                self.screen.blit(background, (0, 0))
            return result

        while True:
            # Draw background each frame
            if background_draw_func:
                background_draw_func()
            
            # Draw popup on top
            self.draw_popup()
            
            # Arm input once all keys are released (prevents buffered input from skipping popups)
            if require_key_release and not input_armed:
                if not any(pygame.key.get_pressed()):
                    input_armed = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if not input_armed:
                        continue
                    if self.slow_print and not self._reveal_complete():
                        continue
                    if min_display_ms and (pygame.time.get_ticks() - start_ms) < min_display_ms:
                        continue
                    if self.show_buttons:
                        # Yes/No button behavior
                        if event.key == pygame.K_LEFT:
                            self.current_selection = 0
                        elif event.key == pygame.K_RIGHT:
                            self.current_selection = 1
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            return finish(self.current_selection == 0)  # True for Yes, False for No
                        elif event.key == pygame.K_ESCAPE:
                            return finish(False)  # ESC = No
                    else:
                        # Message only - any key to dismiss
                        return finish(True)
            
            self.presenter.clock.tick(30)

    def _get_background_surface(self):
        if hasattr(self.presenter, "get_background_surface"):
            try:
                surface = self.presenter.get_background_surface()
                if surface is not None:
                    return surface
            except Exception:
                pass
        return self.screen.copy()


class ChoicePopup:
    """Popup for selecting one option from a list."""

    def __init__(self, presenter, title: str, options: list[str], header_message: str | None = None):
        self.presenter = presenter
        self.screen = presenter.screen
        self.width = presenter.width
        self.height = presenter.height
        self.title = title
        self.options = options
        self.header_message = header_message or ""

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GOLD = (218, 165, 32)
        self.GRAY = (128, 128, 128)
        self.BORDER_COLOR = (200, 200, 200)
        self.HIGHLIGHT_BG = (60, 60, 80)
        self.POPUP_BG = (20, 20, 30)

        # Fonts
        self.title_font = presenter.title_font
        self.normal_font = presenter.normal_font
        self.small_font = presenter.small_font

        # State
        self.current_selection = 0

        # Layout
        self.popup_width = 520
        max_content_width = self.popup_width - 60
        header_lines = self._wrap_text(self.header_message, max_content_width) if self.header_message else []
        self._header_lines = header_lines
        line_height = 30
        min_height = 220
        content_height = (len(header_lines) + len(self.options)) * line_height + 120
        self.popup_height = max(min_height, content_height)
        self.popup_x = (self.width - self.popup_width) // 2
        self.popup_y = (self.height - self.popup_height) // 2
        self.popup_rect = pygame.Rect(self.popup_x, self.popup_y, self.popup_width, self.popup_height)

    def _wrap_text(self, text: str, max_width: int) -> list[str]:
        if not text:
            return []
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            line = " ".join(current_line)
            if self.normal_font.size(line)[0] > max_width:
                current_line.pop()
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
        return lines

    def _get_background_surface(self):
        if hasattr(self.presenter, "get_background_surface"):
            try:
                surface = self.presenter.get_background_surface()
                if surface is not None:
                    return surface
            except Exception:
                pass
        return self.screen.copy()

    def draw_popup(self, background_surface, do_flip: bool = True):
        self.screen.blit(background_surface, (0, 0))

        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        pygame.draw.rect(self.screen, self.POPUP_BG, self.popup_rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, self.popup_rect, 3)

        title_text = self.title_font.render(self.title, True, self.GOLD)
        title_rect = title_text.get_rect(centerx=self.popup_rect.centerx, top=self.popup_y + 20)
        self.screen.blit(title_text, title_rect)

        y = self.popup_y + 70
        for line in self._header_lines:
            text = self.normal_font.render(line, True, self.WHITE)
            text_rect = text.get_rect(centerx=self.popup_rect.centerx)
            text_rect.y = y
            self.screen.blit(text, text_rect)
            y += 28

        y += 10
        for i, option in enumerate(self.options):
            if i == self.current_selection:
                option_rect = pygame.Rect(self.popup_x + 60, y - 4, self.popup_width - 120, 28)
                pygame.draw.rect(self.screen, self.HIGHLIGHT_BG, option_rect)
                pygame.draw.rect(self.screen, self.GOLD, option_rect, 2)
                color = self.GOLD
            else:
                color = self.WHITE
            text = self.normal_font.render(option, True, color)
            text_rect = text.get_rect(centerx=self.popup_rect.centerx)
            text_rect.y = y
            self.screen.blit(text, text_rect)
            y += 30

        instr = "UP/DOWN: Navigate  ENTER: Select  ESC: Cancel"
        instr_text = self.small_font.render(instr, True, self.GRAY)
        instr_rect = instr_text.get_rect(centerx=self.popup_rect.centerx, bottom=self.popup_rect.bottom - 10)
        self.screen.blit(instr_text, instr_rect)

        if do_flip:
            pygame.display.flip()

    def show(self) -> int | None:
        background = self._get_background_surface()
        clock = self.presenter.clock

        if not self.options:
            return None

        while True:
            self.draw_popup(background)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.current_selection = (self.current_selection - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.current_selection = (self.current_selection + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return self.current_selection
                    elif event.key == pygame.K_ESCAPE:
                        return None

            clock.tick(30)


class RewardSelectionPopup:
    """Popup for selecting a reward with details and inline confirmation."""

    def __init__(self, presenter, title: str, items: list, detail_provider):
        self.presenter = presenter
        self.screen = presenter.screen
        self.width = presenter.width
        self.height = presenter.height
        self.title = title
        self.items = items
        self.detail_provider = detail_provider

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GOLD = (218, 165, 32)
        self.GRAY = (128, 128, 128)
        self.BORDER_COLOR = (200, 200, 200)
        self.HIGHLIGHT_BG = (60, 60, 80)
        self.POPUP_BG = (20, 20, 30)

        # Fonts
        self.title_font = presenter.title_font
        self.normal_font = presenter.normal_font
        self.small_font = presenter.small_font

        # State
        self.selected_index = 0

        # Layout
        self.popup_rect = pygame.Rect(self.width // 10, self.height // 8, self.width * 8 // 10, self.height * 3 // 4)
        self.list_rect = pygame.Rect(self.popup_rect.left + 24, self.popup_rect.top + 72, self.popup_rect.width * 2 // 5, self.popup_rect.height - 120)
        self.details_rect = pygame.Rect(self.popup_rect.left + self.popup_rect.width * 2 // 5 + 40, self.popup_rect.top + 72, self.popup_rect.width * 3 // 5 - 64, self.popup_rect.height - 160)
        self.line_height = 24

    def _get_background_surface(self):
        if hasattr(self.presenter, "get_background_surface"):
            try:
                surface = self.presenter.get_background_surface()
                if surface is not None:
                    return surface
            except Exception:
                pass
        return self.screen.copy()

    def _wrap_text(self, text: str, max_width: int) -> list[str]:
        if not text:
            return []
        lines = []
        for paragraph in text.split("\n"):
            if not paragraph.strip():
                lines.append("")
                continue
            words = paragraph.split()
            current_line = []
            for word in words:
                current_line.append(word)
                line = " ".join(current_line)
                if self.normal_font.size(line)[0] > max_width:
                    current_line.pop()
                    if current_line:
                        lines.append(" ".join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(" ".join(current_line))
        return lines

    def draw_popup(self, background_surface, do_flip: bool = True):
        self.screen.blit(background_surface, (0, 0))

        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        pygame.draw.rect(self.screen, self.POPUP_BG, self.popup_rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, self.popup_rect, 2)

        title_text = self.title_font.render(self.title, True, self.GOLD)
        self.screen.blit(title_text, (self.popup_rect.centerx - title_text.get_width() // 2, self.popup_rect.top + 16))

        pygame.draw.rect(self.screen, self.BLACK, self.list_rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, self.list_rect, 2)
        pygame.draw.rect(self.screen, self.BLACK, self.details_rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, self.details_rect, 2)

        # List
        y = self.list_rect.top + 8
        text_max_width = self.list_rect.width - 32
        for idx, item in enumerate(self.items):
            name = getattr(item, "name", str(item))
            if self.normal_font.size(name)[0] > text_max_width:
                while name and self.normal_font.size(name + "...")[0] > text_max_width:
                    name = name[:-1]
                name = f"{name}..."
            row_rect = pygame.Rect(self.list_rect.left + 8, y - 2, self.list_rect.width - 16, self.line_height)
            if idx == self.selected_index:
                pygame.draw.rect(self.screen, self.HIGHLIGHT_BG, row_rect)
                color = self.GOLD
            else:
                color = self.WHITE
            text = self.normal_font.render(name, True, color)
            self.screen.blit(text, (self.list_rect.left + 16, y))
            y += self.line_height

        # Details
        if self.items:
            current_item = self.items[self.selected_index]
            details = self.detail_provider(current_item)
            x = self.details_rect.left + 12
            y = self.details_rect.top + 10
            max_width = self.details_rect.width - 24
            for line in self._wrap_text(details, max_width):
                text = self.normal_font.render(line, True, self.WHITE)
                self.screen.blit(text, (x, y))
                y += self.line_height

        help_str = "UP/DOWN: Navigate  ENTER: Select  ESC: Cancel"
        help_text = self.small_font.render(help_str, True, self.GRAY)
        self.screen.blit(help_text, (self.popup_rect.left + 16, self.popup_rect.bottom - help_text.get_height() - 12))

        if do_flip:
            pygame.display.flip()

    def show(self) -> int | None:
        background = self._get_background_surface()
        clock = self.presenter.clock

        if not self.items:
            return None

        while True:
            self.draw_popup(background)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.items)
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.items)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        current_item = self.items[self.selected_index]
                        name = getattr(current_item, "name", str(current_item))
                        confirm_popup = ConfirmationPopup(self.presenter, f"Take {name}?", show_buttons=True)
                        choice = confirm_popup.show(
                            background_draw_func=lambda: self.draw_popup(background, do_flip=False),
                            flush_events=True,
                            require_key_release=True,
                        )
                        if choice:
                            return self.selected_index
                    elif event.key == pygame.K_ESCAPE:
                        return None

            clock.tick(30)


def confirm_yes_no(presenter, message) -> bool:
    """
    Convenience helper for simple Yes/No confirmations.

    Args:
        presenter: Active presenter with screen/clock/fonts
        message: Prompt to display

    Returns:
        bool: True for Yes, False for No (ESC also returns False)
    """
    popup = ConfirmationPopup(presenter, message)
    return popup.show()


class QuantityPopup:
    """
    A popup for selecting quantity with incremental controls.
    UP/DOWN adjusts ones place, LEFT/RIGHT adjusts tens place.
    """
    
    def __init__(self, presenter, item_name, unit_cost=0, max_quantity=999, action="buy", default_quantity=0):
        self.presenter = presenter
        self.screen = presenter.screen
        self.width = presenter.width
        self.height = presenter.height
        self.item_name = item_name
        self.unit_cost = unit_cost
        self.max_quantity = max_quantity
        self.action = action  # "buy", "store", "retrieve", "sell"
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GOLD = (218, 165, 32)
        self.GRAY = (128, 128, 128)
        self.BORDER_COLOR = (200, 200, 200)
        self.HIGHLIGHT_BG = (60, 60, 80)
        self.POPUP_BG = (20, 20, 30)
        
        # Fonts
        self.title_font = presenter.title_font
        self.normal_font = presenter.normal_font
        self.small_font = presenter.small_font
        
        # State - quantity as [tens, ones], initialized from default_quantity
        default_quantity = min(default_quantity, max_quantity)  # Clamp to max
        self.tens = (default_quantity // 10) % 10
        self.ones = default_quantity % 10
        self.selected_place = 0  # 0 = ones, 1 = tens
        
        # Calculate popup position (centered)
        self.popup_width = 500
        self.popup_height = 300
        self.popup_x = (self.width - self.popup_width) // 2
        self.popup_y = (self.height - self.popup_height) // 2
        self.popup_rect = pygame.Rect(self.popup_x, self.popup_y, self.popup_width, self.popup_height)
    
    @property
    def quantity(self):
        """Get current quantity."""
        return self.tens * 10 + self.ones
    
    def draw_popup(self, background_draw_func=None):
        """Draw the quantity popup over the current screen."""
        # Draw background if provided
        if background_draw_func:
            background_draw_func()
        else:
            self.screen.fill(self.BLACK)
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Draw popup background
        pygame.draw.rect(self.screen, self.POPUP_BG, self.popup_rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, self.popup_rect, 3)
        
        # Title based on action
        if self.action == "store":
            title = f"Store {self.item_name}"
        elif self.action == "retrieve":
            title = f"Retrieve {self.item_name}"
        elif self.action == "sell":
            title = f"Sell {self.item_name}"
        else:
            title = f"Buy {self.item_name}"
        
        title_text = self.title_font.render(title, True, self.GOLD)
        title_rect = title_text.get_rect(centerx=self.popup_rect.centerx, top=self.popup_y + 20)
        self.screen.blit(title_text, title_rect)
        
        # Quantity selector with tens and ones
        qty_y = self.popup_y + 80
        qty_label = self.normal_font.render("Quantity:", True, self.WHITE)
        self.screen.blit(qty_label, (self.popup_x + 50, qty_y))
        
        # Tens place
        tens_x = self.popup_x + 250
        tens_highlight = pygame.Rect(tens_x - 30, qty_y - 10, 60, 50)
        if self.selected_place == 1:
            pygame.draw.rect(self.screen, self.HIGHLIGHT_BG, tens_highlight)
            pygame.draw.rect(self.screen, self.GOLD, tens_highlight, 2)
            tens_color = self.GOLD
        else:
            tens_color = self.WHITE
        
        tens_text = self.title_font.render(str(self.tens), True, tens_color)
        self.screen.blit(tens_text, (tens_x - tens_text.get_width() // 2, qty_y))
        
        # Ones place
        ones_x = self.popup_x + 320
        ones_highlight = pygame.Rect(ones_x - 30, qty_y - 10, 60, 50)
        if self.selected_place == 0:
            pygame.draw.rect(self.screen, self.HIGHLIGHT_BG, ones_highlight)
            pygame.draw.rect(self.screen, self.GOLD, ones_highlight, 2)
            ones_color = self.GOLD
        else:
            ones_color = self.WHITE
        
        ones_text = self.title_font.render(str(self.ones), True, ones_color)
        self.screen.blit(ones_text, (ones_x - ones_text.get_width() // 2, qty_y))
        
        # Total cost/value
        cost_y = self.popup_y + 160
        if self.unit_cost > 0:
            total_value = self.quantity * self.unit_cost
            if self.action == "sell":
                cost_text = self.normal_font.render(f"Total Value: {total_value}g", True, self.GOLD)
            elif self.action == "buy":
                cost_text = self.normal_font.render(f"Total Cost: {total_value}g", True, self.GOLD)
            else:
                cost_text = None
            
            if cost_text:
                cost_rect = cost_text.get_rect(centerx=self.popup_rect.centerx, top=cost_y)
                self.screen.blit(cost_text, cost_rect)
        
        # Instructions
        instr_y = self.popup_y + 220
        instr1 = self.small_font.render("UP/DOWN: Adjust | LEFT/RIGHT: Switch | ENTER: Confirm | ESC: Cancel", True, self.GRAY)
        instr_rect = instr1.get_rect(centerx=self.popup_rect.centerx, top=instr_y)
        self.screen.blit(instr1, instr_rect)
    
    def show(self, background_draw_func=None):
        """
        Show the quantity popup and return selected quantity or None if cancelled.
        
        Args:
            background_draw_func: Optional function to draw the background
            
        Returns:
            int: Selected quantity, or None if cancelled
        """
        background = None
        if background_draw_func is None:
            background = self._get_background_surface()
            background_draw_func = lambda: self.screen.blit(background, (0, 0))

        def finish(result):
            if background_draw_func is not None:
                background_draw_func()
            elif background is not None:
                self.screen.blit(background, (0, 0))
            return result

        while True:
            self.draw_popup(background_draw_func)
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return finish(None)
                    elif event.key == pygame.K_UP:
                        # Increase current digit (clamp to 0-9)
                        if self.selected_place == 0:  # Ones
                            self.ones = min(9, self.ones + 1)
                        else:  # Tens
                            self.tens = min(9, self.tens + 1)
                        
                        # Ensure we don't exceed max quantity
                        if self.quantity > self.max_quantity:
                            if self.selected_place == 0:
                                self.ones = max(0, self.ones - 1)
                            else:
                                self.tens = max(0, self.tens - 1)
                    
                    elif event.key == pygame.K_DOWN:
                        # Decrease current digit (clamp to 0-9)
                        if self.selected_place == 0:  # Ones
                            self.ones = max(0, self.ones - 1)
                        else:  # Tens
                            self.tens = max(0, self.tens - 1)
                    
                    elif event.key == pygame.K_LEFT:
                        # Switch to tens place
                        self.selected_place = 1
                    
                    elif event.key == pygame.K_RIGHT:
                        # Switch to ones place
                        self.selected_place = 0
                    
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # Confirm selection
                        if self.quantity > 0:
                            return finish(self.quantity)
            
            self.presenter.clock.tick(30)

    def _get_background_surface(self):
        if hasattr(self.presenter, "get_background_surface"):
            try:
                surface = self.presenter.get_background_surface()
                if surface is not None:
                    return surface
            except Exception:
                pass
        return self.screen.copy()


class CodeEntryPopup:
    """Popup for entering a 4-digit code."""

    def __init__(self, presenter, title: str, message: str):
        self.presenter = presenter
        self.screen = presenter.screen
        self.width = presenter.width
        self.height = presenter.height
        self.title = title
        self.message = message
        self.digits = [0, 0, 0, 0]
        self.selected_digit = 0

        self.WHITE = (255, 255, 255)
        self.GOLD = (218, 165, 32)
        self.GRAY = (128, 128, 128)
        self.BORDER_COLOR = (200, 200, 200)
        self.HIGHLIGHT_BG = (60, 60, 80)
        self.POPUP_BG = (20, 20, 30)

        self.title_font = presenter.title_font
        self.normal_font = presenter.normal_font
        self.small_font = presenter.small_font

        self.popup_width = 560
        self.popup_height = 260
        self.popup_x = (self.width - self.popup_width) // 2
        self.popup_y = (self.height - self.popup_height) // 2
        self.popup_rect = pygame.Rect(self.popup_x, self.popup_y, self.popup_width, self.popup_height)

    def draw_popup(self, background_draw_func):
        if background_draw_func:
            background_draw_func()

        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        pygame.draw.rect(self.screen, self.POPUP_BG, self.popup_rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, self.popup_rect, 3)

        title_text = self.title_font.render(self.title, True, self.GOLD)
        title_rect = title_text.get_rect(centerx=self.popup_rect.centerx, top=self.popup_y + 18)
        self.screen.blit(title_text, title_rect)

        message_text = self.normal_font.render(self.message, True, self.WHITE)
        message_rect = message_text.get_rect(centerx=self.popup_rect.centerx, top=self.popup_y + 72)
        self.screen.blit(message_text, message_rect)

        digit_y = self.popup_y + 130
        spacing = 72
        start_x = self.popup_rect.centerx - (spacing * 3) // 2
        for idx, digit in enumerate(self.digits):
            x = start_x + idx * spacing
            rect = pygame.Rect(x - 24, digit_y - 8, 48, 64)
            if idx == self.selected_digit:
                pygame.draw.rect(self.screen, self.HIGHLIGHT_BG, rect)
                pygame.draw.rect(self.screen, self.GOLD, rect, 2)
                color = self.GOLD
            else:
                pygame.draw.rect(self.screen, self.POPUP_BG, rect)
                pygame.draw.rect(self.screen, self.BORDER_COLOR, rect, 1)
                color = self.WHITE
            digit_text = self.title_font.render(str(digit), True, color)
            digit_rect = digit_text.get_rect(center=rect.center)
            self.screen.blit(digit_text, digit_rect)

        instructions = self.small_font.render(
            "UP/DOWN: Adjust | LEFT/RIGHT: Move | ENTER: Confirm | ESC: Cancel",
            True,
            self.GRAY,
        )
        instructions_rect = instructions.get_rect(centerx=self.popup_rect.centerx, top=self.popup_y + 220)
        self.screen.blit(instructions, instructions_rect)

        pygame.display.flip()

    def show(self, background_draw_func=None):
        background = None
        if background_draw_func is None:
            background = self.screen.copy()
            background_draw_func = lambda: self.screen.blit(background, (0, 0))

        def finish(result):
            if background_draw_func is not None:
                background_draw_func()
            elif background is not None:
                self.screen.blit(background, (0, 0))
            return result

        while True:
            self.draw_popup(background_draw_func)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                if event.type != pygame.KEYDOWN:
                    continue
                if event.key == pygame.K_ESCAPE:
                    return finish(None)
                if event.key == pygame.K_LEFT:
                    self.selected_digit = max(0, self.selected_digit - 1)
                elif event.key == pygame.K_RIGHT:
                    self.selected_digit = min(3, self.selected_digit + 1)
                elif event.key == pygame.K_UP:
                    self.digits[self.selected_digit] = min(9, self.digits[self.selected_digit] + 1)
                elif event.key == pygame.K_DOWN:
                    self.digits[self.selected_digit] = max(0, self.digits[self.selected_digit] - 1)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return finish("".join(str(digit) for digit in self.digits))
            self.presenter.clock.tick(30)
