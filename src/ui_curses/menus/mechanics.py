"""Mechanics behavior for the menus package."""

import curses

import src.ui_curses.menus as menus
from .foundation import PopupMenu


class JumpModsPopupMenu(PopupMenu):
    """Popup menu for toggling Jump modifications."""

    MOD_DESCRIPTIONS = {
        "Crit": "Increases critical factor but reduces damage to 1.5x weapon damage.",
        "Thrust": "After landing, thrust for 3/4 weapon damage if the target survives.",
        "Defend": "Increased damage reduction while preparing to Jump.",
        "Rend": "Chance to apply Bleed, dealing damage over time.",
        "Quake": "Chance to stun the enemy upon landing.",
        "Acrobat": "Gain an evasion bonus while preparing to Jump.",
        "Dragon's Fury": "Deals additional random elemental damage.",
        "Soaring Strike": "Takes two turns to charge, but deals increased damage.",
        "Quick Dive": "Removes charge time but reduces damage to 0.75x.",
        "Retribution": "Taking damage while charging boosts the Jump damage.",
        "Unstoppable": "Jump cannot be interrupted once started.",
        "Recover": "Regain a small amount of health and mana upon landing.",
        "Skyfall": "Additional smaller hits fall on the target after landing.",
    }

    def __init__(self, game, header_message, box_height=20, box_width=50):
        super().__init__(game, header_message, box_height=box_height, box_width=box_width)
        self.jump_skill = None

    def _get_jump_skill(self):
        skills = getattr(self.game.player_char, "spellbook", {}).get("Skills", {})
        if "Jump" in skills:
            return skills["Jump"]
        for skill in skills.values():
            if getattr(skill, "name", "") == "Jump":
                return skill
        return None

    def _build_options(self):
        self.jump_skill = self._get_jump_skill()
        if not self.jump_skill or not hasattr(self.jump_skill, "modifications"):
            self.options_list = ["Jump not learned", "Go Back"]
            return

        options = []
        # Only show unlocked modifications
        unlocked_mods = self.jump_skill.get_unlocked_modifications() if hasattr(self.jump_skill, "get_unlocked_modifications") else list(self.jump_skill.modifications.keys())

        # Add active count info
        active_count = self.jump_skill.get_active_count() if hasattr(self.jump_skill, "get_active_count") else 0
        max_count = self.jump_skill.get_max_active_modifications(self.game.player_char) if hasattr(self.jump_skill, "get_max_active_modifications") else 99
        options.append(f"Active: {active_count}/{max_count}")
        options.append("---")

        for mod_name in unlocked_mods:
            active = self.jump_skill.modifications.get(mod_name, False)
            prefix = "[X]" if active else "[ ]"
            options.append(f"{prefix} {mod_name}")
        options.append("Go Back")
        self.options_list = options

    def _extract_mod_name(self, option: str) -> str:
        return option.replace("[X] ", "").replace("[ ] ", "").strip()

    def navigate_popup(self):
        self._build_options()
        self.draw_popup()
        while True:
            self.draw_popup()
            self.popup_win.refresh()
            key = self.game.stdscr.getch()

            if key == curses.KEY_UP:
                self.current_option -= 1
                if self.current_option < 0:
                    self.current_option = len(self.options_list) - 1
            elif key == curses.KEY_DOWN:
                self.current_option += 1
                if self.current_option > len(self.options_list) - 1:
                    self.current_option = 0
            elif key == curses.KEY_ENTER or key in [10, 13]:
                choice = self.options_list[self.current_option]
                if choice == "Go Back":
                    return

                # Skip non-toggleable items
                if choice.startswith("Active:") or choice == "---":
                    continue

                if not self.jump_skill or not hasattr(self.jump_skill, "modifications"):
                    return

                mod_name = self._extract_mod_name(choice)
                if not mod_name:  # Empty after extraction
                    continue

                current = self.jump_skill.modifications.get(mod_name, False)

                # Toggle the modification
                result = self.jump_skill.set_modification(mod_name, not current, self.game.player_char)

                # Handle the new tuple return format
                if isinstance(result, tuple):
                    success, error_msg = result
                    if not success and error_msg:
                        # Show error message
                        box = menus.TextBox(self.game)
                        box.print_text_in_rectangle(error_msg)
                        box.clear_rectangle()
                    elif success:
                        # Show description on successful toggle
                        desc = self.MOD_DESCRIPTIONS.get(mod_name, "")
                        if desc:
                            box = menus.TextBox(self.game)
                            box.print_text_in_rectangle(desc)
                            box.clear_rectangle()
                else:
                    # Backwards compatibility - old boolean return
                    desc = self.MOD_DESCRIPTIONS.get(mod_name, "")
                    if desc:
                        box = menus.TextBox(self.game)
                        box.print_text_in_rectangle(desc)
                        box.clear_rectangle()

                self._build_options()


class TotemAspectsPopupMenu(PopupMenu):
    """Popup menu for selecting active Totem aspects."""

    def __init__(self, game, header_message, box_height=16, box_width=50):
        super().__init__(game, header_message, box_height=box_height, box_width=box_width)
        self.totem_skill = None

    def _get_totem_skill(self):
        skills = getattr(self.game.player_char, "spellbook", {}).get("Skills", {})
        if "Totem" in skills:
            return skills["Totem"]
        for skill in skills.values():
            if getattr(skill, "name", "") == "Totem":
                return skill
        return None

    def _build_options(self):
        self.totem_skill = self._get_totem_skill()
        if not self.totem_skill or not hasattr(self.totem_skill, "get_unlocked_aspects"):
            self.options_list = ["Totem not learned", "Go Back"]
            return

        options = []
        active_aspect = getattr(self.totem_skill, "active_aspect", "")
        if active_aspect:
            options.append(f"Active: {active_aspect}")
            options.append("---")

        unlocked = self.totem_skill.get_unlocked_aspects(self.game.player_char)
        for aspect in unlocked:
            prefix = "[X]" if aspect == active_aspect else "[ ]"
            options.append(f"{prefix} {aspect}")

        options.append("Go Back")
        self.options_list = options

    def _extract_aspect_name(self, option: str) -> str:
        return option.replace("[X] ", "").replace("[ ] ", "").strip()

    def navigate_popup(self):
        self._build_options()
        self.draw_popup()
        while True:
            self.draw_popup()
            self.popup_win.refresh()
            key = self.game.stdscr.getch()

            if key == curses.KEY_UP:
                self.current_option -= 1
                if self.current_option < 0:
                    self.current_option = len(self.options_list) - 1
            elif key == curses.KEY_DOWN:
                self.current_option += 1
                if self.current_option > len(self.options_list) - 1:
                    self.current_option = 0
            elif key == curses.KEY_ENTER or key in [10, 13]:
                choice = self.options_list[self.current_option]
                if choice == "Go Back":
                    return None

                if choice.startswith("Active:") or choice == "---":
                    continue

                if not self.totem_skill:
                    return None

                aspect = self._extract_aspect_name(choice)
                if not aspect:
                    continue

                success, error_msg = self.totem_skill.set_active_aspect(aspect)
                if not success:
                    if error_msg:
                        box = menus.TextBox(self.game)
                        box.print_text_in_rectangle(error_msg)
                        box.clear_rectangle()
                    continue

                desc = ""
                if hasattr(self.totem_skill, "aspects"):
                    desc = self.totem_skill.aspects.get(aspect, {}).get("description", "")
                if desc:
                    box = menus.TextBox(self.game)
                    box.print_text_in_rectangle(desc)
                    box.clear_rectangle()

                self._build_options()
                return aspect
