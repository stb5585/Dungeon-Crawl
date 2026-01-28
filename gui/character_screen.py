"""
Character Screen for Pygame - matches curses terminal layout.
"""

import pygame
from gui.town_base import TownScreenBase
from .popup_menus import (
    InventoryPopupMenu,
    EquipmentPopupMenu,
    SimpleListPopupMenu,
)


class CharacterScreen(TownScreenBase):
    """
    Character screen with menu options and character stats.
    Layout:
    - Top Left: Options Menu
    - Top Right Top: Character Info (name, location, class, level, gold, weight)
    - Top Right Bottom: Additional Info (exp, to next level)
    - Bottom: Three columns (stats, combat stats, equipped gear) with Resistances at bottom
    """
    
    def __init__(self, presenter):
        super().__init__(presenter)
        
        # State
        self.current_selection = 0
        self.menu_options = [
            "Inventory",
            "Equipment",
            "Quests",
            "Exit Menu",
            "Key Items",
            "Specials",
            "Class Menu",
            "Quit Game"
        ]
        
        # Calculate window positions
        self.calculate_rects()
    
    def calculate_rects(self):
        """Calculate rectangles for each section."""
        # Use generous heights so all rows fit even on smaller windows
        info_height = max(128, self.height // 6)
        exp_height = max(64, self.height // 12)
        menu_height = max(192, self.height // 4)
        stats_height = max(576, 3 * self.height // 4)

        self.menu_rect = pygame.Rect(0, 0, 3 * self.width // 5, menu_height)
        self.info_rect = pygame.Rect(self.menu_rect.right, 0, 2 * self.width // 5, info_height)
        self.exp_rect = pygame.Rect(self.menu_rect.right, self.info_rect.bottom, 2 * self.width // 5, exp_height)
        self.stats_rect = pygame.Rect(0, self.menu_rect.bottom, self.width, stats_height)
    
    def _has_class_features(self, player_char):
        """Check if player's class has special features (companions, summons, familiar, etc.)"""
        cls = getattr(player_char, "cls", None)
        if not cls:
            return False
        
        # Check for class-specific attributes that indicate special features
        cls_name = getattr(cls, "name", "").lower()
        
        # Classes with special features
        special_classes = [
            "warlock",      # familiars
            "summoner",     # summons
            "necromancer",  # minions
            "ranger",       # companions
            "druid",        # animal companion
        ]
        
        # Check if class name matches special classes
        for special in special_classes:
            if special in cls_name:
                return True
        
        # Check for actual features on the class object
        if (hasattr(cls, "companions") or 
            hasattr(cls, "summons") or 
            hasattr(cls, "familiar") or 
            hasattr(cls, "minions")):
            return True
        
        # Check if player has any companions/summons/familiars
        if (hasattr(player_char, "companions") and player_char.companions) or \
           (hasattr(player_char, "summons") and player_char.summons) or \
           (hasattr(player_char, "familiar") and player_char.familiar) or \
           (hasattr(player_char, "minions") and player_char.minions):
            return True
        
        return False
    
    def _get_quests_list(self, player_char):
        """Get list of quests from player character."""
        # Try multiple attribute names
        quests = getattr(player_char, "quest_dict", None)
        if quests and isinstance(quests, dict):
            # Return quest categories and names
            result = []
            for quest_type, quests_by_type in quests.items():
                for quest_name in quests_by_type.keys():
                    result.append(f"[{quest_type}] {quest_name}")
            return result if result else ["No quests available"]
        
        quests = getattr(player_char, "quests", [])
        if callable(quests):
            quests = quests()
        return quests if quests else ["No quests available"]
    
    def _get_key_items_list(self, player_char):
        """Get list of key items from player character."""
        key_items = getattr(player_char, "key_items", [])
        if callable(key_items):
            key_items = key_items()
        if not key_items:
            return ["No key items"]
        # Extract names if objects
        return [getattr(ki, "name", str(ki)) for ki in key_items]
    
    def _get_specials_list(self, player_char):
        """Get list of special abilities from player character, separated by type."""
        result = []

        # Primary source: player spellbook (Spells/Skills dictionaries)
        if not result:
            spellbook = getattr(player_char, "spellbook", None)
            if spellbook and isinstance(spellbook, dict):
                spells = spellbook.get("Spells", {}) or {}
                skills = spellbook.get("Skills", {}) or {}
                if spells:
                    result.append("--- SPELLS ---")
                    for spell in spells.values():
                        result.append(spell)
                if skills:
                    result.append("--- SKILLS ---")
                    for skill in skills.values():
                        result.append(skill)
                # If spellbook present but empty, fall through to specials check

        return result if result else ["No special abilities"]

    def draw_info(self, player_char):
        """Draw character info header."""
        self.draw_semi_transparent_panel(self.info_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, self.info_rect, 2)

        x = self.info_rect.left + 20
        y = self.info_rect.top + 12

        name_text = self.title_font.render(player_char.name, True, self.colors.GOLD)
        self.screen.blit(name_text, (x, y))

        # Location
        y += 50

        location_text = self.normal_font.render(getattr(player_char, 'location', 'Town'), True, self.colors.WHITE)
        self.screen.blit(location_text, (x, y))

        # Calculate weight from inventory
        weight = sum(item.weight for items in player_char.inventory.values() for item in items)
        max_weight = player_char.stats.strength * 10
        weight_max = f"Weight/Max: {int(weight)}/{int(max_weight)}"
        weight_text = self.normal_font.render(weight_max, True, self.colors.WHITE)
        self.screen.blit(weight_text, (self.info_rect.right - weight_text.get_width() - 10, y))

        y += 40
        class_text = self.normal_font.render(
            f"{player_char.race.name} {player_char.cls.name}", True, self.colors.WHITE
        )
        self.screen.blit(class_text, (x, y))

        # Gold
        gold_amount = getattr(player_char, 'gold', 0)
        gold_text = self.normal_font.render(f"{gold_amount}G", True, self.colors.GOLD)
        self.screen.blit(gold_text, (self.info_rect.right - gold_text.get_width() - 10, y))

    def draw_exp(self, player_char):
        """Draw experience info."""
        self.draw_semi_transparent_panel(self.exp_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, self.exp_rect, 2)

        x = self.exp_rect.left + 20
        y = self.exp_rect.top + 12

        # Level
        level_text = self.large_font.render(f"Level: {player_char.level.level}", True, self.colors.WHITE)
        self.screen.blit(level_text, (x, self.exp_rect.centery - level_text.get_height() // 2))

        # Experience and to next level
        exp_str = f"Experience: {player_char.level.exp}"
        exp_text = self.normal_font.render(exp_str, True, self.colors.WHITE)
        self.screen.blit(exp_text, (self.exp_rect.right - exp_text.get_width() - 10, y))
        y += 22

        to_next = player_char.level.exp_to_gain
        to_next_str = f"To Next Level: {to_next}"
        next_level_text = self.normal_font.render(to_next_str, True, self.colors.WHITE)
        self.screen.blit(next_level_text, (self.exp_rect.right - next_level_text.get_width() - 10, y))

    def draw_menu(self):
        """Draw menu options in two columns."""
        self.draw_semi_transparent_panel(self.menu_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, self.menu_rect, 2)

        col_width = self.menu_rect.width // 4
        col1_x = self.menu_rect.centerx - col_width - 30
        col2_x = self.menu_rect.centerx + 30
        y_start = self.menu_rect.centery - 4 * 18  # Center vertically for 8 options
        line_height = 36

        for i, option in enumerate(self.menu_options):
            if i < 4:
                x = col1_x
                y = y_start + i * line_height
            else:
                x = col2_x
                y = y_start + (i - 4) * line_height

            highlight_rect = pygame.Rect(x - 12, y - 3, col_width, line_height + 2)
            if i == self.current_selection:
                pygame.draw.rect(self.screen, self.colors.HIGHLIGHT_BG, highlight_rect)
                text = self.large_font.render(option, True, self.colors.GOLD)
            else:
                text = self.large_font.render(option, True, self.colors.WHITE)
            self.screen.blit(text, (x, y))
    
    def draw_stats(self, player_char):
        """Draw character stats in three columns."""
        self.draw_semi_transparent_panel(self.stats_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, self.stats_rect, 2)
        
        # Three columns: base stats, combat stats, equipped gear
        col1_x = self.stats_rect.left + 20
        col2_x = self.stats_rect.left + self.stats_rect.width // 3 + 20
        col3_x = self.stats_rect.left + 2 * self.stats_rect.width // 3 + 20
        y_start = self.stats_rect.top + 20
        line_height = 18
        
        # Column 1: Base Stats
        col1_y = y_start
        
        stats = [
            ("Hit Points:", f"{player_char.health.current}/{player_char.health.max}"),
            ("Mana Points:", f"{player_char.mana.current}/{player_char.mana.max}"),
            ("", ""),  # Blank line
            ("Strength:", str(player_char.stats.strength)),
            ("Intelligence:", str(player_char.stats.intel)),
            ("Wisdom:", str(player_char.stats.wisdom)),
            ("Constitution:", str(player_char.stats.con)),
            ("Charisma:", str(player_char.stats.charisma)),
            ("Dexterity:", str(player_char.stats.dex)),
        ]
        
        for label, value in stats:
            if label:
                label_text = self.normal_font.render(label, True, self.colors.WHITE)
                self.screen.blit(label_text, (col1_x, col1_y))
                
                value_text = self.normal_font.render(value, True, self.colors.WHITE)
                self.screen.blit(value_text, (col1_x + 150, col1_y))
            col1_y += line_height
        
        # Column 2: Combat Stats
        col2_y = y_start
        
        combat_stats = [
            ("Attack:", str(player_char.combat.attack)),
            ("Critical Chance:", f"{player_char.critical_chance('Weapon') * 100:.1f}%"),
            ("Defense:", str(player_char.combat.defense)),
            ("Block Chance:", f"{player_char.check_mod('shield')}%"),
            ("Spell Defense:", str(player_char.check_mod('magic def'))),
            ("Spell Modifier:", str(player_char.check_mod('magic'))),
            ("Heal Modifier:", str(player_char.check_mod('heal'))),
        ]
        
        for label, value in combat_stats:
            if label:
                label_text = self.normal_font.render(label, True, self.colors.WHITE)
                self.screen.blit(label_text, (col2_x, col2_y))
                
                value_text = self.normal_font.render(value, True, self.colors.WHITE)
                self.screen.blit(value_text, (col2_x + 150, col2_y))
            col2_y += line_height
        
        # Column 3: Equipped Gear
        col3_y = y_start
        
        # Header
        header_text = self.normal_font.render("Equipped Gear", True, self.colors.GOLD)
        self.screen.blit(header_text, (col3_x, col3_y))
        col3_y += line_height + 5
        
        # Equipment slots
        equipment_slots = ["Weapon", "Armor", "OffHand", "Ring", "Pendant"]
        
        for slot in equipment_slots:
            item = player_char.equipment.get(slot)
            item_name = item.name if item else "(empty)"
            
            label_text = self.normal_font.render(f"{slot}:", True, self.colors.WHITE)
            self.screen.blit(label_text, (col3_x, col3_y))
            
            value_text = self.normal_font.render(item_name, True, self.colors.WHITE)
            self.screen.blit(value_text, (col3_x + 100, col3_y))
            
            col3_y += line_height
        
        # Buffs
        col3_y += line_height
        buffs_label = self.normal_font.render("Buffs:", True, self.colors.WHITE)
        self.screen.blit(buffs_label, (col3_x, col3_y))
        col3_y += line_height
        
        if hasattr(player_char, 'buffs') and player_char.buffs:
            for buff in player_char.buffs[:3]:  # Show up to 3 buffs
                buff_text = self.normal_font.render(buff.name, True, self.colors.WHITE)
                self.screen.blit(buff_text, (col3_x + 20, col3_y))
                col3_y += line_height - 2
        else:
            none_text = self.normal_font.render("None", True, self.colors.GRAY)
            self.screen.blit(none_text, (col3_x + 20, col3_y))

        # Resistances
        resistance_text = self.normal_font.render("Resistances", True, self.colors.GOLD)
        self.screen.blit(resistance_text, (self.stats_rect.centerx - 50, self.stats_rect.bottom - 150))

        resistance_names = [
            "Fire", "Electric", "Earth", "Shadow", "Poison",
            "Ice", "Water", "Wind", "Holy", "Physical"
        ]

        col_width = self.stats_rect.width // 5
        row_height = 50

        for i, resist_name in enumerate(resistance_names):
            row = i // 5
            col = i % 5
            col_x = self.stats_rect.left + col * col_width + 50
            resist_y = self.stats_rect.bottom + (row + 1) * row_height - 150

            resist_val = player_char.resistance.get(resist_name, 0.0)
            display = f"{resist_name}: {resist_val * 100:.1f}"

            text = self.normal_font.render(display, True, self.colors.WHITE)
            self.screen.blit(text, (col_x, resist_y))

    def draw_all(self, player_char, do_flip=True):
        """Draw all UI elements. Set do_flip=False when drawing as a background for overlays."""
        self.draw_background()
        self.draw_info(player_char)
        self.draw_menu()
        self.draw_stats(player_char)
        self.draw_exp(player_char)
        if do_flip:
            pygame.display.flip()

    def navigate(self, player_char):
        """
        Navigate the character menu and return selected option.
        
        Returns:
            str: Selected menu option, or None if cancelled
        """
        # Build menu options dynamically based on class features
        menu_options = [
            "Inventory",
            "Equipment",
            "Quests",
            "Exit Menu",
            "Key Items",
            "Specials",
        ]
        
        # Only include Class Menu if class has special features
        if self._has_class_features(player_char):
            menu_options.insert(6, "Class Menu")
        
        menu_options.append("Quit Game")
        self.menu_options = menu_options
        self.current_selection = 0
        
        while True:
            self.draw_all(player_char)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    # Calculate dynamic rows for 2-column layout
                    rows = (len(self.menu_options) + 1) // 2
                    
                    if event.key == pygame.K_ESCAPE:
                        return "Exit Menu"
                    elif event.key == pygame.K_UP:
                        # Move up within column
                        if self.current_selection > 0:
                            self.current_selection -= 1
                        else:
                            self.current_selection = len(self.menu_options) - 1
                    elif event.key == pygame.K_DOWN:
                        # Move down within column
                        if self.current_selection < len(self.menu_options) - 1:
                            self.current_selection += 1
                        else:
                            self.current_selection = 0
                    elif event.key == pygame.K_LEFT:
                        # Move from right column to left column
                        if self.current_selection >= rows:
                            self.current_selection -= rows
                        # If in left column, wrap to right column if possible
                        else:
                            new_pos = self.current_selection + rows
                            if new_pos < len(self.menu_options):
                                self.current_selection = new_pos
                    elif event.key == pygame.K_RIGHT:
                        # Move from left column to right column
                        new_pos = self.current_selection + rows
                        if new_pos < len(self.menu_options):
                            self.current_selection = new_pos
                        # If in right column or move would go out of bounds, wrap to left
                        else:
                            self.current_selection = self.current_selection % rows
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        chosen = self.menu_options[self.current_selection]
                        # Open popup overlays for relevant menus; keep loop after closing
                        if chosen == "Inventory":
                            popup = InventoryPopupMenu(self.presenter, self)
                            _ = popup.show(player_char)
                        elif chosen == "Equipment":
                            popup = EquipmentPopupMenu(self.presenter, self)
                            _ = popup.show(player_char)
                        elif chosen == "Quests":
                            from gui.popup_menus import QuestPopupMenu
                            popup = QuestPopupMenu(self.presenter, self)
                            _ = popup.show(player_char)
                        elif chosen == "Key Items":
                            # Check if there are any key items
                            key_items = getattr(player_char, "key_items", [])
                            if callable(key_items):
                                key_items = key_items()
                            
                            if not key_items:
                                # Show popup message instead of empty list
                                from gui.confirmation_popup import ConfirmationPopup
                                # Capture current screen once to avoid redraw flicker
                                self.draw_all(player_char, do_flip=False)
                                background_surface = self.presenter.screen.copy()
                                popup = ConfirmationPopup(
                                    self.presenter,
                                    "You do not have any key items.",
                                    show_buttons=False
                                )
                                popup.show(background_draw_func=lambda: self.presenter.screen.blit(background_surface, (0, 0)))
                            else:
                                popup = SimpleListPopupMenu(
                                    self.presenter,
                                    self,
                                    title="Key Items",
                                    source_fn=self._get_key_items_list,
                                )
                                _ = popup.show(player_char)
                        elif chosen == "Specials":
                            popup = SimpleListPopupMenu(
                                self.presenter,
                                self,
                                title="Special Abilities",
                                source_fn=self._get_specials_list,
                            )
                            _ = popup.show(player_char)
                        elif chosen == "Class Menu":
                            popup = SimpleListPopupMenu(
                                self.presenter,
                                self,
                                title="Class Options",
                                source_fn=lambda pc: [getattr(pc.cls, "name", "Class"), f"Level {pc.level.level}"]
                            )
                            _ = popup.show(player_char)
                        elif chosen == "Exit Menu":
                            return "Exit Menu"
                        elif chosen == "Quit Game":
                            return "Quit Game"
            
            self.presenter.clock.tick(30)
