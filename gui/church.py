"""
Church system for GUI - handles promotion, saving, and quests.
Implements the core church logic from town.py adapted for Pygame presenter.
"""

import os
from gui.quest_manager import QuestManager
from classes import classes_dict, apply_promotion_ability_rules
import companions
from items import remove_equipment


class ChurchManager:
    """Manages church interactions with pygame presenter."""
    
    def __init__(self, presenter, player_char):
        self.presenter = presenter
        self.player_char = player_char
    
    def visit_church(self):
        """Visit the Church of Elysia."""
        church_options = ["Promotion", "Save Game", "Quests", "Leave"]
        
        while True:
            choice = self.presenter.render_menu("Church of Elysia", church_options)
            
            if choice is None or choice == 3:  # Leave
                self.presenter.show_message("Let the light of Elysia guide you.")
                break
            
            elif choice == 0:  # Promotion
                self.handle_promotion()
            
            elif choice == 1:  # Save
                self.save_game()
            
            elif choice == 2:  # Quests
                self.show_quests()
    
    def _show_promotion_preview(self, class_name: str, class_ctor) -> bool:
        """Show promotion preview and confirm.
        
        Returns:
            bool: True if confirmed, False if user wants to go back
        """
        import pygame
        from presentation.pygame_presenter import BLACK, WHITE, YELLOW, GRAY
        
        try:
            new_class = class_ctor()
            
            # Get equipment list
            core_slots = ["Weapon", "OffHand", "Armor"]
            equipment_items = []
            for slot in core_slots:
                if slot in new_class.equipment:
                    item = new_class.equipment[slot]
                    equipment_items.append(f"{slot}: {item.name}")
            
            # Show preview with custom rendering
            self.presenter.screen.fill(BLACK)
            
            # Title
            title_text = self.presenter.title_font.render(class_name, True, YELLOW)
            title_rect = title_text.get_rect(centerx=self.presenter.width // 2, top=100)
            self.presenter.screen.blit(title_text, title_rect)
            
            # Description - left-aligned with wider wrapping
            y = 160
            left_margin = 80
            max_width = self.presenter.width - 160
            line_height = 35
            
            # Word wrap description
            words = new_class.description.split()
            current_line = []
            for word in words:
                current_line.append(word)
                test_line = " ".join(current_line)
                if self.presenter.normal_font.size(test_line)[0] > max_width:
                    current_line.pop()
                    if current_line:
                        line_text = self.presenter.normal_font.render(" ".join(current_line), True, WHITE)
                        self.presenter.screen.blit(line_text, (left_margin, y))
                        y += line_height
                    current_line = [word]
            if current_line:
                line_text = self.presenter.normal_font.render(" ".join(current_line), True, WHITE)
                self.presenter.screen.blit(line_text, (left_margin, y))
                y += line_height
            
            # Add spacing
            y += line_height // 2
            
            # "New Equipment:" header - centered and colored
            equipment_header = self.presenter.large_font.render("New Equipment:", True, YELLOW)
            header_rect = equipment_header.get_rect(centerx=self.presenter.width // 2, top=y)
            self.presenter.screen.blit(equipment_header, header_rect)
            y += line_height + 10
            
            # Equipment items - center-aligned
            for item_text in equipment_items:
                item_surface = self.presenter.normal_font.render(item_text, True, WHITE)
                item_rect = item_surface.get_rect(centerx=self.presenter.width // 2, top=y)
                self.presenter.screen.blit(item_surface, item_rect)
                y += line_height
            
            # Instructions
            help_text = self.presenter.small_font.render("Press any key to continue...", True, GRAY)
            help_rect = help_text.get_rect(centerx=self.presenter.width // 2, bottom=self.presenter.height - 20)
            self.presenter.screen.blit(help_text, help_rect)
            
            pygame.display.flip()
            
            # Wait for keypress
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        import sys
                        sys.exit()
                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        waiting = False
                self.presenter.clock.tick(30)
            
            # Then show confirmation menu
            choice = self.presenter.render_menu(
                f"Promote to {class_name}?",
                ["Confirm Promotion", "Go Back"]
            )
            
            return choice == 0  # True if confirmed, False if go back
        except Exception as e:
            self.presenter.show_message(f"Error previewing class: {e}")
            return False
    
    def handle_promotion(self):
        """Handle class promotion at level 30."""
        if self.player_char.level.level >= 30 and self.player_char.level.pro_level < 3:
            current_class = self.player_char.cls.name
            pro_level = self.player_char.level.pro_level

            # Build promotion options based on current class and promotion level
            options = []
            option_map = {}

            if pro_level == 1:
                # Find the base class entry matching current class
                base_entry = None
                for base_name, cls_entry in classes_dict.items():
                    try:
                        if cls_entry["class"]().name == current_class:
                            base_entry = cls_entry
                            break
                    except Exception:
                        continue
                if base_entry:
                    allowed = getattr(getattr(self.player_char, 'race', {}), 'cls_res', {}).get('First', [])
                    for pro_name, pro_entry in base_entry.get('pro', {}).items():
                        try:
                            class_name = pro_entry['class']().name
                            if not allowed or pro_name in allowed or class_name in allowed:
                                options.append(class_name)
                                option_map[class_name] = pro_entry['class']
                        except Exception:
                            continue
            elif pro_level == 2:
                # Find the first-tier class entry matching current class and list its nested promotions
                for base_name, cls_entry in classes_dict.items():
                    for pro_name, pro_entry in cls_entry.get('pro', {}).items():
                        try:
                            if pro_entry['class']().name == current_class:
                                for nested_name, nested_entry in pro_entry.get('pro', {}).items():
                                    class_name = nested_entry['class']().name
                                    options.append(class_name)
                                    option_map[class_name] = nested_entry['class']
                                break
                        except Exception:
                            continue

            if not options:
                self.presenter.show_message("No promotion options are currently available.")
                return

            # For level 3 promotion, if there's only one option, skip the selection menu
            if pro_level == 2 and len(options) == 1:
                chosen_name = options[0]
                chosen_ctor = option_map.get(chosen_name)
                
                # Show class preview and confirm (with early return if user backs out)
                if not self._show_promotion_preview(chosen_name, chosen_ctor):
                    self.presenter.show_message("Promotion cancelled.")
                    return
            else:
                # Loop to allow going back from preview
                while True:
                    header = (
                        f"Current Class: {self.player_char.cls.name}\n"
                        "\n"
                        "Choose your path:"
                    )
                    choice_idx = self.presenter.render_menu(header, options)
                    if choice_idx is None:
                        self.presenter.show_message("Promotion cancelled.")
                        return

                    chosen_name = options[choice_idx]
                    chosen_ctor = option_map.get(chosen_name)
                    
                    # Show class preview and confirm
                    if not self._show_promotion_preview(chosen_name, chosen_ctor):
                        # User chose to go back
                        continue
                    else:
                        # User confirmed, proceed with promotion
                        break
            
            try:
                # Set new class and increment promotion level
                self.player_char.cls = chosen_ctor()
                self.player_char.level.pro_level += 1
                
                # Reset character level to 1 after promotion
                self.player_char.level.level = 1
                
                # Reset xp threshold for next level based on new class progression
                try:
                    self.player_char.level.exp_to_gain = self.player_char.level_exp()
                except Exception:
                    pass
                
                # Auto-equip promotion gear: move current to inventory, then equip new class gear
                try:
                    # Move current core gear to inventory (Weapon, OffHand, Armor)
                    self.player_char.unequip(promo=True)
                    # Clear only core equipment slots to 'None' equipment
                    for slot in ["Weapon", "OffHand", "Armor"]:
                        try:
                            self.player_char.equipment[slot] = remove_equipment(slot)
                        except Exception:
                            pass
                    # Equip new class default equipment for core slots only, without inventory adjustments
                    core_slots = {"Weapon", "OffHand", "Armor"}
                    for slot, item in self.player_char.cls.equipment.items():
                        if slot not in core_slots:
                            continue
                        try:
                            self.player_char.equip(slot, item, check=True)
                        except Exception:
                            # Fallback: set directly
                            self.player_char.equipment[slot] = item
                except Exception:
                    # Ignore equip failures; player keeps existing gear
                    pass
                # Apply ability transition rules for this promotion
                ability_change_msg = apply_promotion_ability_rules(self.player_char, chosen_name)
                if ability_change_msg:
                    self.presenter.show_message(ability_change_msg.strip())
                # Special promotions
                # Warlock: choose a familiar
                if chosen_name == "Warlock":
                    fam_options = ["Homunculus", "Fairy", "Mephit", "Jinkin"]
                    fam_map = {
                        "Homunculus": companions.Homunculus,
                        "Fairy": companions.Fairy,
                        "Mephit": companions.Mephit,
                        "Jinkin": companions.Jinkin,
                    }
                    
                    # Familiar selection with description and confirmation
                    fam_confirmed = False
                    while not fam_confirmed:
                        fam_idx = self.presenter.render_menu("Choose your familiar", fam_options)
                        if fam_idx is None:
                            break
                        
                        # Show familiar description
                        fam_class = fam_map[fam_options[fam_idx]]
                        familiar = fam_class()
                        description = familiar.inspect()
                        self.presenter.show_message(description, title=familiar.race)
                        
                        # Confirm familiar selection
                        confirm = self.presenter.render_menu(
                            f"Bind with this {familiar.race}?",
                            ["Yes", "No"]
                        )
                        if confirm == 0:
                            # Ask for familiar name with confirmation loop
                            default_name = "Buddy"
                            name_confirmed = False
                            while not name_confirmed:
                                fam_name = self.presenter.get_text_input(
                                    "What is your familiar's name?", default_text=default_name
                                )
                                if not fam_name:
                                    fam_name = default_name
                                fam_name = fam_name.capitalize()
                                confirm_name = self.presenter.render_menu(
                                    f"Name your familiar '{fam_name}'?", ["Yes", "No"]
                                )
                                if confirm_name == 0:
                                    name_confirmed = True
                                    fam_confirmed = True
                                    familiar.name = fam_name
                                    self.player_char.familiar = familiar
                                    self.presenter.show_message(f"Your familiar {familiar.race} joins you as '{familiar.name}'.")
                        # If not confirmed, loop back to familiar selection

                # Summoner: grant starting summon Patagon
                if chosen_name == "Summoner":
                    try:
                        pet = companions.Patagon()
                        pet.initialize_stats(self.player_char)
                        self.player_char.summons[pet.name] = pet
                        self.presenter.show_message("You have learned to summon Patagon.")
                    except Exception:
                        pass

                self.presenter.show_message(f"Congratulations! You are now a {chosen_name}.")
            except Exception as e:
                self.presenter.show_message(f"Promotion failed: {e}")
        else:
            if self.player_char.level.pro_level == 3:
                self.presenter.show_message(
                    "You are at max promotion level and can no longer be promoted."
                )
            else:
                self.presenter.show_message(
                    "You need to be level 30 before you can promote your character."
                )
    
    def show_quests(self):
        """Show available quests from the priest."""
        qm = QuestManager(self.presenter, self.player_char)
        qm.check_and_offer('Priest')
    
    def save_game(self):
        """Save the game at the church."""
        save_dir = "save_files"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Use character name as filename (always overwrites)
        char_name = self.player_char.name.lower().replace(" ", "_")
        filename = f"{char_name}.save"
        filepath = os.path.join(save_dir, filename)
        
        try:
            # Save directly to filepath using the new Player.save signature
            self.player_char.save(filepath=filepath)
            self.presenter.show_message(f"Game saved successfully!")
        except Exception as e:
            self.presenter.show_message(f"Error saving game:\n\n{str(e)}")
