"""
GUI Quest Manager: offers and turns in quests using Pygame presenter.
Adapts core quest data from town.quest_dict without relying on curses.
"""
from __future__ import annotations

import copy
import random
import textwrap
from typing import Any

from src.core import items
from src.core.town import quest_dict, RESPONSE_MAP
from .confirmation_popup import ConfirmationPopup
from .level_up import LevelUpScreen


class QuestManager:
    def __init__(self, presenter, player_char, quest_text_renderer=None, wrap_width=52):
        self.presenter = presenter
        self.screen = presenter.screen
        self.player_char = player_char
        self.quest_text_renderer = quest_text_renderer
        self.wrap_width = wrap_width  # characters

    def get_random_help_hint(self, giver: str) -> str | None:
        """Return a single random help hint for active quests from the given giver.
        Does not render anything; returns None if no applicable hints.
        """
        def flatten(lst):
            out = []
            for d in lst:
                for name, q in d.items():
                    out.append((name, q))
            return out

        mains, sides = self._eligible_quests(giver)
        hints: list[str] = []
        for name, _ in flatten(mains):
            pdata = self.player_char.quest_dict.get('Main', {}).get(name)
            if pdata and not pdata.get('Turned In'):
                ht = pdata.get('Help Text', '')
                if isinstance(ht, str) and ht.strip():
                    hints.append(ht)
        for name, _ in flatten(sides):
            if name == 'Debug' and not getattr(self.presenter, 'debug_mode', False):
                continue
            pdata = self.player_char.quest_dict.get('Side', {}).get(name)
            if pdata and not pdata.get('Turned In'):
                ht = pdata.get('Help Text', '')
                if isinstance(ht, str) and ht.strip():
                    hints.append(ht)
        return random.choice(hints) if hints else None

    def _eligible_quests(self, giver: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        data = quest_dict.get(giver, {"Main": {}, "Side": {}})
        level = self.player_char.player_level()
        main_list: list[dict[str, Any]] = []
        side_list: list[dict[str, Any]] = []
        for lvl, q in data.get("Main", {}).items():
            if level >= int(lvl):
                main_list.append(q)
        for lvl, q in data.get("Side", {}).items():
            if level >= int(lvl):
                side_list.append(q)
        return main_list, side_list

    def _turn_in(self, quest_name: str, typ: str) -> None:
        loc_bg = self.screen.copy()
        # Prevent Debug quest interactions in non-debug mode
        if quest_name == 'Debug' and not getattr(self.presenter, 'debug_mode', False):
            popup = ConfirmationPopup(self.presenter, "This quest cannot be turned in.", show_buttons=False)
            popup.show(background_draw_func=lambda: self.screen.blit(loc_bg, (0, 0)))
            return
        
        qdata = self.player_char.quest_dict[typ][quest_name]
        # Show end-of-quest text from quest giver if available
        end_text = qdata.get('End Text', '')
        if end_text:
            # Add quest name header for visibility
            header_text = f"====== {quest_name} ======\n\n"
            wrapped_end = "\n".join(textwrap.wrap(end_text, width=self.wrap_width))
            header_text += wrapped_end
            if self.quest_text_renderer:
                self.quest_text_renderer(header_text)
            else:
                wrapped_end = "\n".join(textwrap.wrap(header_text, width=self.wrap_width))
                popup = ConfirmationPopup(self.presenter, wrapped_end, show_buttons=False)
                popup.show(background_draw_func=lambda: self.screen.blit(loc_bg, (0, 0)))

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
                wrapped_desc = textwrap.wrap(item.description, width=self.wrap_width)
                info_lines.extend(wrapped_desc)
            info_lines.append("")
            info_lines.append(f"Value: {getattr(item, 'value', 0)}g")
            return "\n".join(info_lines)

        # Handle special Debug quest: grants massive exp for leveling
        if quest_name == 'Debug' and qdata.get('Type') == 'Debug':
            # Show reward first
            message = f"You've been granted {exp:,} experience points! This quest can be used again."
            wrapped_message = "\n".join(textwrap.wrap(message, width=self.wrap_width))
            if self.quest_text_renderer:
                self.quest_text_renderer(wrapped_message)
            else:
                popup = ConfirmationPopup(self.presenter, wrapped_message, show_buttons=False)
                popup.show(background_draw_func=lambda: self.screen.blit(loc_bg, (0, 0)))

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
        reward_str = ""
        if reward == ["Gold"]:
            self.player_char.gold += reward_num
            reward_str = f"{reward_num} gold"
        elif reward == ["Warp Point"]:
            # Special flag for warp point access
            setattr(self.player_char, 'warp_point', True)
            reward_str = "Warp Point access"
        elif reward and isinstance(reward, list) and len(reward) == 1:
            # Single item reward: can be either [ItemClass] or [ItemInstance]
            item_or_cls = reward[0]
            
            # Check if it's a class or an instance
            if isinstance(item_or_cls, type):
                # It's a class, instantiate it Reward Number times
                for _ in range(reward_num):
                    try:
                        item = item_or_cls()
                        self.player_char.modify_inventory(item)
                        if not reward_str or reward_str == "":
                            reward_str = f"{item.name} x{reward_num}"
                    except Exception:
                        pass
            else:
                # It's an instance, grant Reward Number copies of the same type
                for _ in range(reward_num):
                    try:
                        # Create a new instance of the same class
                        item = item_or_cls.__class__()
                        self.player_char.modify_inventory(item)
                        if not reward_str or reward_str == "":
                            reward_str = f"{item.name} x{reward_num}"
                    except Exception:
                        pass
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
                        if self.quest_text_renderer:
                            self.quest_text_renderer(format_item_info(item))
                        else:
                            popup = ConfirmationPopup(self.presenter, format_item_info(item), show_buttons=False)
                            popup.show(background_draw_func=lambda: self.screen.blit(loc_bg, (0, 0)))
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
        combined_msg = "\n".join(message)
        if self.quest_text_renderer:
            self.quest_text_renderer(combined_msg)
        else:
            popup = ConfirmationPopup(self.presenter, combined_msg, show_buttons=False)
            popup.show(background_draw_func=lambda: self.screen.blit(loc_bg, (0, 0)))

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
        loc_bg = self.screen.copy()
        # Offer quest via presenter
        text = q.get('Start Text', '')
        # Add quest name header for visibility
        header_text = f"====== {quest_name} ======\n\n"
        # Wrap text to 60 characters for readability
        wrapped_text = "\n".join(textwrap.wrap(text, width=self.wrap_width))
        wrapped_text = header_text + wrapped_text
        
        # Display quest text - use renderer if available, otherwise the standard confirmation popup
        if self.quest_text_renderer:
            self.quest_text_renderer(wrapped_text)
        else:
            popup = ConfirmationPopup(self.presenter, wrapped_text, show_buttons=False)
            popup.show(background_draw_func=lambda: self.screen.blit(loc_bg, (0, 0)))
        
        # Separate Accept/Decline menu as popup
        popup = ConfirmationPopup(self.presenter, "Accept this quest?")
        if popup.show(background_draw_func=lambda: self.screen.blit(loc_bg, (0, 0))):
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

            # Use personalized response from RESPONSE_MAP
            response = RESPONSE_MAP.get(giver, ["Quest accepted! Check your quest log for details.", "Maybe next time."])[0]
            # Special case for Sergeant's Relics quest
            if giver == "Sergeant" and quest_name == "The Holy Relics":
                response += "\n\nMake sure to grab the health potions out of your storage locker if you haven't already."
            
            popup = ConfirmationPopup(
                self.presenter,
                response,
                show_buttons=False,
            )
            popup.show(background_draw_func=lambda: self.screen.blit(loc_bg, (0, 0)))
            return True
        else:
            # Use personalized rejection response from RESPONSE_MAP
            response = RESPONSE_MAP.get(giver, ["Quest accepted! Check your quest log for details.", "Maybe next time."])[1]
            popup = ConfirmationPopup(self.presenter, response, show_buttons=False)
            popup.show(background_draw_func=lambda: self.screen.blit(loc_bg, (0, 0)))
            return False

    def check_and_offer(self, giver: str, show_help: bool = True, suppress_no_quests_message: bool = False) -> tuple[bool, bool]:
        """Return (did_action, showed_message).

        did_action: quest turned in or accepted.
        showed_message: any popup/help/no-quest message was shown.
        """
        did_action = False
        showed_message = False
        quest_was_offered = False
        mains, sides = self._eligible_quests(giver)
        loc_bg = self.screen.copy()

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
                showed_message = True
                return did_action, showed_message
        for name, q in flatten(sides):
            pdata = self.player_char.quest_dict.get('Side', {}).get(name)
            # Skip Debug quest in non-debug mode
            if name == 'Debug' and not getattr(self.presenter, 'debug_mode', False):
                continue
            if pdata and pdata.get('Completed') and not pdata.get('Turned In'):
                self._turn_in(name, 'Side')
                did_action = True
                showed_message = True
                return did_action, showed_message

        # Offer new quests, main first then side
        for name, q in flatten(mains):
            if name not in self.player_char.quest_dict.get('Main', {}):
                quest_was_offered = True
                if self._offer(giver, name, q, 'Main'):
                    return True, True
                showed_message = True  # declined quest still showed a popup
        for name, q in flatten(sides):
            # Skip debug-only pandora/ultima style special cases
            if name == "Pandora's Box" and 'Ultima' not in self.player_char.spellbook.get('Spells', {}):
                continue
            # Skip Debug quest in non-debug mode
            if name == 'Debug' and not getattr(self.presenter, 'debug_mode', False):
                continue
            
            if name not in self.player_char.quest_dict.get('Side', {}):
                quest_was_offered = True
                if self._offer(giver, name, q, 'Side'):
                    return True, True
                showed_message = True  # declined quest still showed a popup

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
        if help_texts and show_help:
            # Show a single random hint per interaction instead of all at once
            candidates = [ht for ht in help_texts if isinstance(ht, str) and ht.strip()]
            if candidates:
                hint = random.choice(candidates)
                wrapped_hint = "\n".join(textwrap.wrap(hint, width=self.wrap_width))
                if self.quest_text_renderer:
                    self.quest_text_renderer(wrapped_hint)
                else:
                    popup = ConfirmationPopup(self.presenter, wrapped_hint, show_buttons=False)
                    popup.show(background_draw_func=lambda: self.screen.blit(loc_bg, (0, 0)))
                showed_message = True
        elif not quest_was_offered and not suppress_no_quests_message:
            # Only show "no quests" if no quest was offered at all and not suppressed
            popup = ConfirmationPopup(self.presenter, "I have no new quests for you at this time.", show_buttons=False)
            popup.show(background_draw_func=lambda: self.screen.blit(loc_bg, (0, 0)))
            showed_message = True
        return did_action, showed_message
