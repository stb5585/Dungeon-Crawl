"""
Character Screen for Pygame - matches curses terminal layout.
"""

import pygame

from .popup_menus import EquipmentPopupMenu, InventoryPopupMenu, JumpModsPopupMenu, TotemAspectsPopupMenu, SimpleListPopupMenu
from .town_base import TownScreenBase


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
    
    def _get_jump_skill(self, player_char):
        skills = getattr(player_char, "spellbook", {}).get("Skills", {})
        if "Jump" in skills:
            return skills["Jump"]
        for skill in skills.values():
            if getattr(skill, "name", "") == "Jump":
                return skill
        return None

    def _has_jump_mods(self, player_char):
        """Check if player can configure Jump modifications."""
        jump_skill = self._get_jump_skill(player_char)
        return bool(jump_skill and hasattr(jump_skill, "modifications"))

    def _get_totem_skill(self, player_char):
        skills = getattr(player_char, "spellbook", {}).get("Skills", {})
        if "Totem" in skills:
            return skills["Totem"]
        for skill in skills.values():
            if getattr(skill, "name", "") == "Totem":
                return skill
        return None

    def _has_totem_aspects(self, player_char):
        """Check if player can configure Totem aspects."""
        totem_skill = self._get_totem_skill(player_char)
        return bool(totem_skill and hasattr(totem_skill, "get_unlocked_aspects"))
    
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
        special_inv = getattr(player_char, "special_inventory", {})
        if not special_inv:
            return ["No key items"]
        # Return the actual item objects from the inventory
        # The special_inventory format is: {item_name: [item_obj, item_obj, ...]}
        key_items = []
        for item_name, item_list in special_inv.items():
            if item_list and len(item_list) > 0:
                # Get the first item object (all instances are the same)
                item_obj = item_list[0]
                # Store as dict with the item object and display the count if > 1
                quantity = len(item_list)
                if quantity > 1:
                    # Create a wrapper dict to show quantity in the name
                    key_items.append({
                        "text": f"{item_name} ({quantity})",
                        "value": item_obj,
                        "is_header": False
                    })
                else:
                    # Just return the item object directly
                    key_items.append(item_obj)
        return key_items if key_items else ["No key items"]
    
    def _get_specials_list(self, player_char):
        """Get list of special abilities from player character, separated by type."""
        result = []

        # Racial traits
        race = getattr(player_char, "race", None)
        virtue = getattr(race, "virtue", None) if race else None
        sin = getattr(race, "sin", None) if race else None
        if virtue and getattr(virtue, "name", ""):
            result.append("--- RACIAL TRAITS ---")
            result.append(virtue)
            if sin and getattr(sin, "name", ""):
                result.append(sin)

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
        else:
            # Append spells/skills after racial traits.
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
        y += 48

        if player_char.location_z == 0:
            location_str = "Town"
        else:
            location_str = f"Dungeon Level {player_char.location_z}"
        
        location_text = self.large_font.render(location_str, True, self.colors.WHITE)
        self.screen.blit(location_text, (x, y))

        # Show encumbered warning if applicable
        if getattr(player_char, 'encumbered', False):
            encumb_text = self.small_font.render("ENCUMBERED", True, self.colors.RED)
            self.screen.blit(encumb_text, (self.info_rect.right - encumb_text.get_width() - 10, y + 20))

        y += 38
        class_text = self.large_font.render(
            f"{player_char.race.name} {player_char.cls.name}", True, self.colors.WHITE
        )
        self.screen.blit(class_text, (x, y))

        # Racial traits (virtue/sin)
        try:
            virtue = getattr(getattr(player_char, "race", None), "virtue", None)
            sin = getattr(getattr(player_char, "race", None), "sin", None)
            if virtue and getattr(virtue, "name", ""):
                y += 28
                self.screen.blit(self.small_font.render(f"Virtue: {virtue.name}", True, self.colors.GRAY), (x, y))
                y += 18
            if sin and getattr(sin, "name", ""):
                self.screen.blit(self.small_font.render(f"Sin: {sin.name}", True, self.colors.GRAY), (x, y))
        except Exception:
            pass

        # Gold
        gold_amount = getattr(player_char, 'gold', 0)
        gold_text = self.large_font.render(f"{gold_amount}G", True, self.colors.GOLD)
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

        col_width = self.menu_rect.width // 3
        col1_x = self.menu_rect.centerx - col_width - 30
        col2_x = self.menu_rect.centerx + 30
        line_height = self.large_font.get_height() + 10
        y_start = self.menu_rect.centery - (4 * line_height) // 2  # Center vertically for 8 options

        for i, option in enumerate(self.menu_options):
            if i < 4:
                x = col1_x
                y = y_start + i * line_height
            else:
                x = col2_x
                y = y_start + (i - 4) * line_height

            highlight_rect = pygame.Rect(x - 12, y - 4, col_width, line_height + 4)
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
        padding = 20
        col_gap = 10
        col_width = (self.stats_rect.width - (padding * 2) - (col_gap * 2)) // 3
        col1_x = self.stats_rect.left + padding
        col2_x = col1_x + col_width + col_gap
        col3_x = col2_x + col_width + col_gap
        y_start = self.stats_rect.top + 24
        line_height = self.large_font.get_height() + 6
        
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
        
        max_label_width = 0
        for label, _ in stats:
            if label:
                max_label_width = max(max_label_width, self.large_font.size(label)[0])
        value_x = col1_x + max_label_width + 14

        for label, value in stats:
            if label:
                label_text = self.large_font.render(label, True, self.colors.WHITE)
                self.screen.blit(label_text, (col1_x, col1_y))
                
                value_text = self.large_font.render(value, True, self.colors.WHITE)
                self.screen.blit(value_text, (value_x, col1_y))
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

        max_label_width = 0
        max_value_width = 0
        for label, value in combat_stats:
            if label:
                max_label_width = max(max_label_width, self.large_font.size(label)[0])
            if value:
                max_value_width = max(max_value_width, len(value))
        combat_value_x = col2_x + max_label_width + 14

        for label, value in combat_stats:
            if label:
                label_text = self.large_font.render(label, True, self.colors.WHITE)
                self.screen.blit(label_text, (col2_x, col2_y))
                r_adjusted_value = f"{value:>{max_value_width}}" if max_value_width > 0 else value
                value_text = self.large_font.render(r_adjusted_value, True, self.colors.WHITE)
                self.screen.blit(value_text, (combat_value_x, col2_y))
            col2_y += line_height
        
        # Weight (at bottom of combat stats column)
        col2_y += line_height  # Add spacing
        weight = player_char.current_weight()
        max_weight = player_char.max_weight()
        weight_color = self.colors.RED if getattr(player_char, 'encumbered', False) else self.colors.WHITE
        
        weight_label_text = self.large_font.render("Weight/Max:", True, self.colors.WHITE)
        self.screen.blit(weight_label_text, (col2_x, col2_y))
        
        weight_value_text = self.large_font.render(f"{int(weight)}/{int(max_weight)}", True, weight_color)
        self.screen.blit(weight_value_text, (combat_value_x, col2_y))
        
        # Column 3: Equipped Gear
        col3_y = y_start
        
        # Header
        header_text = self.large_font.render("Equipped Gear", True, self.colors.GOLD)
        self.screen.blit(header_text, (col3_x, col3_y))
        col3_y += line_height + 5
        
        # Equipment slots
        equipment_slots = ["Weapon", "Armor", "OffHand", "Ring", "Pendant"]

        max_slot_width = 0
        for slot in equipment_slots:
            max_slot_width = max(max_slot_width, self.large_font.size(f"{slot}:")[0])
        gear_value_x = col3_x + max_slot_width + 12
        
        for slot in equipment_slots:
            item = player_char.equipment.get(slot)
            item_name = item.name if item else "(empty)"
            
            label_text = self.large_font.render(f"{slot}:", True, self.colors.WHITE)
            self.screen.blit(label_text, (col3_x, col3_y))
            
            value_text = self.large_font.render(item_name, True, self.colors.WHITE)
            self.screen.blit(value_text, (gear_value_x, col3_y))
            
            col3_y += line_height
        
        # Buffs
        col3_y += line_height
        buffs_label = self.large_font.render("Buffs:", True, self.colors.WHITE)
        self.screen.blit(buffs_label, (col3_x, col3_y))
        col3_y += line_height
        
        buff_names = []
        if hasattr(player_char, 'buffs') and player_char.buffs:
            for buff in player_char.buffs:
                name = getattr(buff, "name", str(buff))
                if name and name not in buff_names:
                    buff_names.append(name)

        pendant = player_char.equipment.get("Pendant") if hasattr(player_char, "equipment") else None
        if pendant and getattr(pendant, "mod", None) == "Vision" and "Vision" not in buff_names:
            buff_names.append("Vision")
        if getattr(player_char, "sight", False) and "Vision" not in buff_names:
            buff_names.append("Vision")

        if buff_names:
            for name in buff_names[:3]:  # Show up to 3 buffs
                buff_text = self.large_font.render(name, True, self.colors.WHITE)
                self.screen.blit(buff_text, (col3_x + 20, col3_y))
                col3_y += line_height - 2
        else:
            none_text = self.large_font.render("None", True, self.colors.GRAY)
            self.screen.blit(none_text, (col3_x + 20, col3_y))

        # Resistances
        resistance_text = self.large_font.render("Resistances", True, self.colors.GOLD)
        row_height = self.large_font.get_height() + 18
        resistance_title_y = self.stats_rect.bottom - (row_height * 2) - 32
        self.screen.blit(resistance_text, (self.stats_rect.centerx - resistance_text.get_width() // 2, resistance_title_y))

        resistance_names = [
            "Fire", "Electric", "Earth", "Shadow", "Poison",
            "Ice", "Water", "Wind", "Holy", "Physical"
        ]

        col_width = self.stats_rect.width // 5

        for i, resist_name in enumerate(resistance_names):
            row = i // 5
            col = i % 5
            col_x = self.stats_rect.left + col * col_width + padding
            resist_y = resistance_title_y + 32 + (row * row_height)

            resist_val = player_char.resistance.get(resist_name, 0.0)
            display = f"{resist_name}: {resist_val * 100:.1f}"

            text = self.large_font.render(display, True, self.colors.WHITE)
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
        
        # Only include Jump Mods if player has Jump customization
        if self._has_jump_mods(player_char):
            menu_options.insert(6, "Jump Mods")

        # Only include Totem Aspects if player has Totem customization
        if self._has_totem_aspects(player_char):
            menu_options.insert(7, "Totem Aspects")
        
        menu_options.append("Quit Game")
        self.menu_options = menu_options
        started_in_town = player_char.in_town()
        
        while True:
            if not started_in_town and player_char.in_town():
                return "Exit Menu"

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
                        if self.current_selection == 4:
                            self.current_selection = len(self.menu_options) - 1
                        elif self.current_selection == 0:
                            self.current_selection = 3
                        else:
                            self.current_selection -= 1
                    elif event.key == pygame.K_DOWN:
                        # Move down within column
                        if self.current_selection == len(self.menu_options) - 1:
                            self.current_selection = 4
                        elif self.current_selection == 3:
                            self.current_selection = 0
                        else:
                            self.current_selection += 1
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
                            popup.show(player_char, flush_events=True, require_key_release=True)
                        elif chosen == "Equipment":
                            popup = EquipmentPopupMenu(self.presenter, self)
                            _ = popup.show(player_char, flush_events=True, require_key_release=True)
                        elif chosen == "Quests":
                            from .popup_menus import QuestPopupMenu
                            popup = QuestPopupMenu(self.presenter, self)
                            _ = popup.show(player_char, flush_events=True, require_key_release=True)
                        elif chosen == "Key Items":
                            # Check if there are any key items
                            special_inv = getattr(player_char, "special_inventory", {})
                            
                            if not special_inv:
                                # Show popup message instead of empty list
                                from .confirmation_popup import ConfirmationPopup
                                # Capture current screen once to avoid redraw flicker
                                self.draw_all(player_char, do_flip=False)
                                popup = ConfirmationPopup(
                                    self.presenter,
                                    "You do not have any key items.",
                                    show_buttons=False
                                )
                                popup.show(flush_events=True, require_key_release=True)
                            else:
                                popup = SimpleListPopupMenu(
                                    self.presenter,
                                    self,
                                    title="Key Items",
                                    source_fn=self._get_key_items_list,
                                )
                                _ = popup.show(player_char, flush_events=True, require_key_release=True)
                        elif chosen == "Specials":
                            popup = SimpleListPopupMenu(
                                self.presenter,
                                self,
                                title="Special Abilities",
                                source_fn=self._get_specials_list,
                            )
                            _ = popup.show(player_char, flush_events=True, require_key_release=True)
                        elif chosen == "Jump Mods":
                            popup = JumpModsPopupMenu(self.presenter, self, title="Jump Modifications")
                            _ = popup.show(player_char, flush_events=True, require_key_release=True)
                        elif chosen == "Totem Aspects":
                            popup = TotemAspectsPopupMenu(self.presenter, self, title="Totem Aspects")
                            _ = popup.show(player_char, flush_events=True, require_key_release=True)
                        elif chosen == "Exit Menu":
                            return "Exit Menu"
                        elif chosen == "Quit Game":
                            return "Quit Game"
            
            self.presenter.clock.tick(30)
