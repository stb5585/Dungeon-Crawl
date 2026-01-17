"""
GUI Quest Manager: offers and turns in quests using Pygame presenter.
Adapts core quest data from town.quest_dict without relying on curses.
"""
from __future__ import annotations

import copy
import textwrap
from typing import Any

import items
from gui.level_up import LevelUpScreen
from town import quest_dict


class QuestManager:
    def __init__(self, presenter, player_char):
        self.presenter = presenter
        self.player_char = player_char
    def _slow_print_message(self, message: str, title: str = "", char_delay: float = 0.03):
        """Display a message with slow character-by-character printing effect."""
        import pygame
        import time
        
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        YELLOW = (255, 255, 0)
        GRAY = (128, 128, 128)
        
        self.presenter.screen.fill(BLACK)
        
        # Display title if provided
        y = 200
        if title:
            title_text = self.presenter.title_font.render(title, True, YELLOW)
            title_rect = title_text.get_rect(centerx=self.presenter.width // 2, top=200)
            self.presenter.screen.blit(title_text, title_rect)
            y = 300
        else:
            y = 250
            
        # Split message into lines
        lines = message.split('\n')
        displayed_text = []
        
        for line_idx, line in enumerate(lines):
            displayed_chars = ""
            for char in line:
                displayed_chars += char
                
                # Clear and redraw
                self.presenter.screen.fill(BLACK)
                
                # Redraw title
                if title:
                    title_text = self.presenter.title_font.render(title, True, YELLOW)
                    title_rect = title_text.get_rect(centerx=self.presenter.width // 2, top=200)
                    self.presenter.screen.blit(title_text, title_rect)
                
                # Redraw all previously completed lines
                current_y = y
                for prev_line in displayed_text:
                    text_surface = self.presenter.normal_font.render(prev_line, True, WHITE)
                    text_rect = text_surface.get_rect(centerx=self.presenter.width // 2, top=current_y)
                    self.presenter.screen.blit(text_surface, text_rect)
                    current_y += 40
                
                # Draw current line being typed at the next y position
                text = self.presenter.normal_font.render(displayed_chars, True, WHITE)
                text_rect = text.get_rect(centerx=self.presenter.width // 2, top=current_y)
                self.presenter.screen.blit(text, text_rect)
                
                pygame.display.flip()
                time.sleep(char_delay)
                
                # Check for events to allow skipping
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        import sys
                        sys.exit()
                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        # Skip to end
                        displayed_chars = line
                        break
                        
            displayed_text.append(displayed_chars)
        
        # Show "Press any key to continue" message
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
    def _eligible_quests(self, giver: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        data = quest_dict.get(giver, {"Main": {}, "Side": {}})
        level = self.player_char.player_level()
        main_list: list[dict[str, Any]] = []
        side_list: list[dict[str, Any]] = []
        for lvl, q in data.get("Main", {}).items():
            if level >= lvl:
                main_list.append(q)
        for lvl, q in data.get("Side", {}).items():
            if level >= lvl:
                side_list.append(q)
        return main_list, side_list

    def _turn_in(self, quest_name: str, typ: str) -> None:
        # Prevent Debug quest interactions in non-debug mode
        if quest_name == 'Debug' and not getattr(self.presenter, 'debug_mode', False):
            self.presenter.show_message("This quest cannot be turned in.", "Error")
            return
        
        qdata = self.player_char.quest_dict[typ][quest_name]
        # Show end-of-quest text from quest giver if available
        end_text = qdata.get('End Text', '')
        if end_text:
            wrapped_end = "\n".join(textwrap.wrap(end_text, width=60))
            self.presenter.show_message(wrapped_end, title=quest_name)

        # Rewards
        exp = qdata.get('Experience', 0) * max(1, getattr(self.player_char.level, 'pro_level', 1))
        reward = qdata.get('Reward', [])
        reward_num = qdata.get('Reward Number', 1)

        def format_item_info(item) -> str:
            info_lines = []
            info_lines.append(f"Type: {getattr(item, 'typ', 'Item')}")
            if hasattr(item, 'subtyp'):
                info_lines.append(f"Subtype: {item.subtyp}")
            info_lines.append("")
            if getattr(item, 'damage', 0):
                info_lines.append(f"Damage: {item.damage}")
            if getattr(item, 'armor', 0):
                info_lines.append(f"Armor: {item.armor}")
            if getattr(item, 'magic', 0):
                info_lines.append(f"Magic: {item.magic:+d}")
            if getattr(item, 'magic_defense', 0):
                info_lines.append(f"Magic Defense: {item.magic_defense:+d}")
            if getattr(item, 'description', ''):
                info_lines.append("")
                wrapped_desc = textwrap.wrap(item.description, width=50)
                info_lines.extend(wrapped_desc)
            info_lines.append("")
            info_lines.append(f"Value: {getattr(item, 'value', 0)}g")
            return "\n".join(info_lines)

        # Handle special Debug quest: grants massive exp for leveling
        if quest_name == 'Debug' and qdata.get('Type') == 'Debug':
            # Show reward first
            message = [
                f"You've been granted {exp:,} experience points!",
                "This quest can be used again."
            ]
            self.presenter.show_message("\n".join(message), "Debug Mode")

            # Then apply experience and trigger level-up(s)
            self.player_char.level.exp += exp
            if not self.player_char.max_level():
                try:
                    self.player_char.level.exp_to_gain -= exp
                except Exception:
                    pass
            level_up_screen = LevelUpScreen(self.presenter.screen, self.presenter)
            while not self.player_char.max_level() and self.player_char.level.exp_to_gain <= 0:
                level_up_screen.show_level_up(self.player_char, None)
            # Do not mark as turned in so it can be repeated
            return

        # Gold or items
        if reward == ["Gold"]:
            self.player_char.gold += reward_num
            reward_str = f"{reward_num} gold"
        elif reward == ["Warp Point"]:
            # Special flag for warp point access
            setattr(self.player_char, 'warp_point', True)
            reward_str = "Warp Point access"
        else:
            # If multiple reward choices, let player pick one (with inspect) instead of granting all
            chosen_names = []
            if reward and all(isinstance(r, type) for r in reward) and len(reward) > 1:
                try:
                    reward_items = [cls() for cls in reward]
                except Exception:
                    reward_items = []
                if reward_items:
                    while True:
                        options = [item.name for item in reward_items]
                        choice = self.presenter.render_menu("Choose your reward", options)
                        if choice is None:
                            # If user backs out of menu, keep asking until a choice is made
                            continue
                        item = reward_items[choice]
                        # Show details before confirming
                        self.presenter.show_message(format_item_info(item), title=item.name)
                        confirm = self.presenter.render_menu(f"Take {item.name}?", ["Take", "Back"])
                        if confirm == 0:
                            for _ in range(reward_num):
                                self.player_char.modify_inventory(item)
                                chosen_names.append(item.name)
                            break
                        else:
                            continue
                reward_str = ", ".join(chosen_names)
            else:
                names = []
                for _ in range(reward_num):
                    for cls in reward:
                        try:
                            item = cls()
                            self.player_char.modify_inventory(item)
                            names.append(item.name)
                        except Exception:
                            pass
                reward_str = ", ".join(names) if names else ""

        # Show quest completion and rewards first
        message = [f"Quest turned in: {quest_name}"]
        if exp:
            message.append(f"Experience: {exp}")
        if reward_str:
            message.append(f"Reward: {reward_str}")
        self.presenter.show_message("\n".join(message), "Quest Complete")

        # Then apply experience and trigger level-up(s)
        self.player_char.level.exp += exp
        if not self.player_char.max_level():
            try:
                self.player_char.level.exp_to_gain -= exp
            except Exception:
                pass
        level_up_screen = LevelUpScreen(self.presenter.screen, self.presenter)
        while not self.player_char.max_level() and self.player_char.level.exp_to_gain <= 0:
            level_up_screen.show_level_up(self.player_char, None)
        qdata['Turned In'] = True

    def _already_killed(self, enemy_name: str) -> bool:
        kill_dict = getattr(self.player_char, 'kill_dict', {})
        for typ_dict in kill_dict.values():
            if enemy_name in typ_dict:
                return True
        return False

    def _offer(self, giver: str, quest_name: str, q: dict[str, Any], typ: str) -> bool:
        # Offer quest via presenter
        text = q.get('Start Text', '')
        # Wrap text to 50 characters for readability
        wrapped_text = "\n".join(textwrap.wrap(text, width=50))
        
        # Display quest text with slow printing (if not in debug mode)
        quest_header = f"{giver} offers a quest: {quest_name}"
        if hasattr(self.presenter, 'debug_mode') and self.presenter.debug_mode:
            # Debug mode: instant display
            self.presenter.show_message(wrapped_text, title=quest_header)
        else:
            # Normal mode: slow print with instant header
            self._slow_print_message(wrapped_text, title=quest_header)
        
        # Separate Accept/Decline menu
        choice = self.presenter.render_menu(
            "Accept this quest?",
            ["Accept", "Decline"]
        )
        if choice == 0:
            # Add a copy of quest to player quest log
            if typ not in self.player_char.quest_dict:
                self.player_char.quest_dict[typ] = {}
            self.player_char.quest_dict[typ][quest_name] = copy.deepcopy(q)

            # If it's a defeat quest and player already killed the target, mark complete
            if q.get('Type') == 'Defeat' and isinstance(q.get('What'), str):
                if self._already_killed(q['What']):
                    self.player_char.quest_dict[typ][quest_name]['Completed'] = True

            # If it's the Relics collection quest and player already has all relics,
            # mark as completed immediately so it can be turned in.
            if q.get('Type') == 'Collect' and q.get('What') == 'Relics':
                try:
                    if getattr(self.player_char, 'has_relics')() and not self.player_char.quest_dict[typ][quest_name].get('Completed'):
                        self.player_char.quest_dict[typ][quest_name]['Completed'] = True
                except Exception:
                    pass

            # Debug quest is always immediately completed when accepted
            if quest_name == 'Debug' and q.get('Type') == 'Debug':
                self.player_char.quest_dict[typ][quest_name]['Completed'] = True

            # If quest grants an initial item (e.g., Naivete empty vial in curses version),
            # replicate minimal cases here if needed.
            if quest_name == 'Naivete':
                try:
                    self.player_char.modify_inventory(items.EmptyVial(), rare=True)
                except Exception:
                    pass

            self.presenter.show_message("Quest accepted! Check your quest log for details.")
            return True
        else:
            self.presenter.show_message("Maybe next time.")
            return False

    def check_and_offer(self, giver: str) -> bool:
        """Return True if a quest was turned in or accepted; False otherwise."""
        did_action = False
        mains, sides = self._eligible_quests(giver)

        # Turn-in checks, then offers
        # Build flat (name, data) lists
        def flatten(lst):
            out = []
            for d in lst:
                for name, q in d.items():
                    out.append((name, q))
            return out

        for name, q in flatten(mains):
            # Safety: auto-complete Relics collect quest if already fulfilled but not marked
            pdata = self.player_char.quest_dict.get('Main', {}).get(name)
            if pdata and not pdata.get('Completed') and q.get('Type') == 'Collect' and q.get('What') == 'Relics':
                try:
                    if getattr(self.player_char, 'has_relics')():
                        pdata['Completed'] = True
                except Exception:
                    pass
            pdata = self.player_char.quest_dict.get('Main', {}).get(name)
            if pdata and pdata.get('Completed') and not pdata.get('Turned In'):
                self._turn_in(name, 'Main')
                did_action = True
                return True
        for name, q in flatten(sides):
            pdata = self.player_char.quest_dict.get('Side', {}).get(name)
            # Skip Debug quest in non-debug mode
            if name == 'Debug' and not getattr(self.presenter, 'debug_mode', False):
                continue
            if pdata and pdata.get('Completed') and not pdata.get('Turned In'):
                self._turn_in(name, 'Side')
                did_action = True
                return True

        # Offer new quests, main first then side
        for name, q in flatten(mains):
            if name not in self.player_char.quest_dict.get('Main', {}):
                if self._offer(giver, name, q, 'Main'):
                    return True
        for name, q in flatten(sides):
            # Skip debug-only pandora/ultima style special cases
            if name == "Pandora's Box" and 'Ultima' not in self.player_char.spellbook.get('Spells', {}):
                continue
            # Skip Debug quest entirely (never show in production)
            if name == 'Debug':
                continue
            
            if name not in self.player_char.quest_dict.get('Side', {}):
                if self._offer(giver, name, q, 'Side'):
                    return True

        # If no actions, show help text from active quests for this giver if any
        help_texts = []
        for name, q in flatten(mains):
            pdata = self.player_char.quest_dict.get('Main', {}).get(name)
            if pdata and not pdata.get('Turned In'):
                help_texts.append(pdata.get('Help Text', ''))
        for name, q in flatten(sides):
            # Skip Debug quest in non-debug mode
            if name == 'Debug' and not getattr(self.presenter, 'debug_mode', False):
                continue
            pdata = self.player_char.quest_dict.get('Side', {}).get(name)
            if pdata and not pdata.get('Turned In'):
                help_texts.append(pdata.get('Help Text', ''))
        if help_texts:
            wrapped_help = "\n".join(textwrap.wrap(help_texts[0], width=50))
            self.presenter.show_message(wrapped_help)
        else:
            self.presenter.show_message("I have no new quests for you at this time.")
        return did_action
