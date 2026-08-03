"""Selections behavior for the combat manager package."""

from __future__ import annotations

import sys

import pygame

from src.core.classes import (
    ability_mechanics,
    astromancer,
    demonologist,
    grandmaster,
    paladin,
    promotion_kits,
)
from src.core.combat.battle_engine import STOLEN_SCROLL_CHOICE_PREFIX
import src.ui_pygame.gui.combat_manager as combat_manager
from ..input_guards import release_guard_allows_input
from .constants import _DISPLAY_TO_ENGINE


class CombatSelectionMixin:
    def _prompt_for_tamed_companion_name(self, player_char, enemy, background_surface=None) -> None:
        """Ask for an optional nickname after a successful tame."""
        state = ability_mechanics.normalize_tamed_companion(getattr(player_char, "tamed_companion", None))
        companion_name = str(state.get("name") or getattr(enemy, "name", "Companion"))
        screen = combat_manager.CompanionNamingScreen(
            self.presenter,
            companion_name,
            species=str(state.get("species") or ""),
            form=str(state.get("evolution") or ""),
            special=str(state.get("special_ability") or ""),
        )
        nickname = screen.navigate(
            default="",
            flush_events=True,
            require_key_release=True,
            background_surface=background_surface,
        )
        nickname = str(nickname or "").strip()
        if not nickname:
            return
        ability_mechanics.rename_tamed_companion(player_char, nickname)
        display_name = ability_mechanics.tamed_companion_display_name(getattr(player_char, "tamed_companion", None))
        original_name = getattr(enemy, "name", "companion")
        if display_name and display_name != original_name:
            self.combat_view.add_combat_message(f"{original_name} answers to {display_name}.")

    def _select_summoner_support_action(self, player_char, enemy):
        """Show the active-summon support menu and return display/action/choice seeds."""
        if self.engine is None:
            return None
        raw_actions = self.engine.summoner_support_actions()
        if not raw_actions:
            self.combat_view.add_combat_message("No summon support actions are available.")
            self._pause_with_events(500)
            return None
        display_actions = [
            str(action).replace("Use Skill", "Skills").replace("Use Item", "Items")
            for action in raw_actions
        ]
        selected = 0
        input_armed = self._clear_pending_input()
        while True:
            self._render_combat_frame(player_char, enemy, [], -1)
            self._render_selection_menu("Summoner Support", display_actions, selected)
            pygame.display.flip()

            input_armed = release_guard_allows_input(True, input_armed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                input_armed = self._arm_guarded_input(event, input_armed)
                if event.type == pygame.KEYDOWN and not input_armed:
                    continue
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        return None
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(display_actions)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(display_actions)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        display = display_actions[selected]
                        return display, _DISPLAY_TO_ENGINE.get(display, display), None
                elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    selected, _scroll_offset, confirmed = self._selection_menu_mouse_update(
                        event,
                        display_actions,
                        selected,
                        0,
                        input_armed,
                    )
                    if confirmed:
                        display = display_actions[selected]
                        return display, _DISPLAY_TO_ENGINE.get(display, display), None

    def _select_totem_aspect(self, player_char, enemy, totem_skill):
        """Show Totem aspect selection menu and return aspect name."""
        if not totem_skill or not hasattr(totem_skill, "get_unlocked_aspects"):
            return None

        aspects = totem_skill.get_unlocked_aspects(player_char)
        if not aspects:
            self.combat_view.add_combat_message("No Totem aspects unlocked!")
            self._pause_with_events(500)
            return None

        selected = 0
        active = getattr(totem_skill, "active_aspect", "")
        input_armed = self._clear_pending_input()
        while True:
            self._render_combat_frame(player_char, enemy, [], -1)
            options = []
            for aspect in aspects:
                suffix = " (Active)" if aspect == active else ""
                options.append(f"{aspect}{suffix}")

            self._render_selection_menu("Select Totem Aspect", options, selected)
            pygame.display.flip()

            input_armed = release_guard_allows_input(True, input_armed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                input_armed = self._arm_guarded_input(event, input_armed)
                if event.type == pygame.KEYDOWN and not input_armed:
                    continue
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        return None
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(aspects)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(aspects)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return aspects[selected]
                elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    selected, _scroll_offset, confirmed = self._selection_menu_mouse_update(
                        event,
                        options,
                        selected,
                        0,
                        input_armed,
                    )
                    if confirmed:
                        return aspects[selected]

    def _select_item(self, player_char, enemy, *, support_only=False):
        """Show item selection menu and return selected item."""
        items = []
        for item_name, item_list in player_char.inventory.items():
            if item_list and self._combat_item_is_usable(item_list[0], support_only=support_only):
                items.append((item_name, item_list[0], len(item_list)))

        if not items:
            self.combat_view.add_combat_message("No usable items!")
            self._pause_with_events(500)
            return None

        selected = 0
        scroll_offset = 0
        input_armed = self._clear_pending_input()
        frame_player = self._selection_frame_player(player_char)
        while True:
            self._render_combat_frame(frame_player, enemy, [], -1)
            item_options = [f"{name} ({count})" for name, _, count in items]
            item_descriptions = [getattr(item, "description", "") for _, item, _ in items]
            self._render_described_selection_menu(
                "Select Item",
                item_options,
                selected,
                scroll_offset,
                item_descriptions,
            )
            pygame.display.flip()

            input_armed = release_guard_allows_input(True, input_armed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                input_armed = self._arm_guarded_input(event, input_armed)
                if event.type == pygame.KEYDOWN and not input_armed:
                    continue
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        return None  # Cancel
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(items)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(items)
                    elif event.key == pygame.K_PAGEUP:
                        selected = max(0, selected - 10)
                    elif event.key == pygame.K_PAGEDOWN:
                        selected = min(len(items) - 1, selected + 10)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return items[selected][1]
                    scroll_offset = self._scroll_offset_for_selection(selected, scroll_offset)
                elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    selected, scroll_offset, confirmed = self._selection_menu_mouse_update(
                        event,
                        item_options,
                        selected,
                        scroll_offset,
                        input_armed,
                    )
                    if confirmed:
                        return items[selected][1]

    @staticmethod
    def _combat_item_is_usable(item, *, support_only=False) -> bool:
        """Return whether an inventory item belongs in the combat item picker."""
        subtyp = getattr(item, "subtyp", "")
        if subtyp in {"Health", "Mana", "Elixir", "Status"}:
            return True
        if support_only:
            return False
        if subtyp == "Scroll":
            return hasattr(item, "spell")
        return False

    def _select_spell(self, player_char, enemy):
        """Show spell selection menu and return selected spell name."""
        from src.core import items as core_items

        spell_entries = [
            (
                name,
                f"{name} (MP: {getattr(spell, 'cost', 0)})",
                getattr(spell, "description", ""),
            )
            for name, spell in player_char.spellbook['Spells'].items()
            if not getattr(spell, 'passive', False)
            and not getattr(spell, "exploration_cast", False)
            and (getattr(spell, "subtyp", None) != "Movement" or name == "Volitation")
        ]
        scroll_entries = [
            (
                f"{STOLEN_SCROLL_CHOICE_PREFIX}{item_name}",
                f"{item_name} (Scroll)",
                getattr(item_list[0], "description", ""),
            )
            for item_name, item_list in player_char.inventory.items()
            if item_list and isinstance(item_list[0], core_items.InscribedSpellScroll)
        ]
        entries = spell_entries + scroll_entries

        if not entries:
            self.combat_view.add_combat_message("No spells learned!")
            self._pause_with_events(500)
            return None

        selected = 0
        scroll_offset = 0
        input_armed = self._clear_pending_input()
        frame_player = self._selection_frame_player(player_char)
        while True:
            self._render_combat_frame(frame_player, enemy, [], -1)
            spell_options = [label for _choice, label, _description in entries]
            spell_descriptions = [description for _choice, _label, description in entries]

            self._render_described_selection_menu(
                "Select Spell", spell_options, selected, scroll_offset, spell_descriptions
            )
            pygame.display.flip()

            input_armed = release_guard_allows_input(True, input_armed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                input_armed = self._arm_guarded_input(event, input_armed)
                if event.type == pygame.KEYDOWN and not input_armed:
                    continue
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        return None  # Cancel
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(entries)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(entries)
                    elif event.key == pygame.K_PAGEUP:
                        selected = max(0, selected - 10)
                    elif event.key == pygame.K_PAGEDOWN:
                        selected = min(len(entries) - 1, selected + 10)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return entries[selected][0]
                    scroll_offset = self._scroll_offset_for_selection(selected, scroll_offset)
                elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    selected, scroll_offset, confirmed = self._selection_menu_mouse_update(
                        event,
                        spell_options,
                        selected,
                        scroll_offset,
                        input_armed,
                    )
                    if confirmed:
                        return entries[selected][0]

    def _select_skill(self, player_char, enemy, *, allowed_names=None):
        """Show skill selection menu and return selected skill name."""
        # Filter out passive and currently unusable equipment-dependent skills.
        skills = self._available_skill_names(player_char, enemy, allowed_names=allowed_names, resolve=False)

        if not skills:
            self.combat_view.add_combat_message("No skills learned!")
            self._pause_with_events(500)
            return None

        selected = 0
        scroll_offset = 0
        input_armed = self._clear_pending_input()
        frame_player = self._selection_frame_player(player_char)
        while True:
            # Render combat with skill menu overlay
            self._render_combat_frame(frame_player, enemy, [], -1)
            skill_options = []
            for skill_name in skills:
                skill = player_char.spellbook['Skills'][skill_name]
                cost = skill.cost
                if getattr(skill, "resource_type", None) == "Oath Conviction":
                    conviction = int(
                        promotion_kits.combat_state(player_char).get(
                            "oath_conviction",
                            0,
                        )
                        or 0
                    )
                    skill_options.append(
                        f"{skill_name} (Conviction: all {conviction})"
                    )
                else:
                    skill_options.append(f"{skill_name} (MP: {cost})")
            skill_descriptions = []
            for skill_name in skills:
                skill = player_char.spellbook['Skills'][skill_name]
                if getattr(skill, "resource_type", None) == "Oath Conviction":
                    skill_descriptions.append(
                        paladin.oath_technique_description(
                            player_char,
                            skill_name,
                        )
                    )
                else:
                    skill_descriptions.append(
                        getattr(skill, "description", "")
                    )

            self._render_described_selection_menu(
                "Select Skill", skill_options, selected, scroll_offset, skill_descriptions
            )
            pygame.display.flip()

            # Handle input
            input_armed = release_guard_allows_input(True, input_armed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                input_armed = self._arm_guarded_input(event, input_armed)
                if event.type == pygame.KEYDOWN and not input_armed:
                    continue
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        return None  # Cancel
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(skills)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(skills)
                    elif event.key == pygame.K_PAGEUP:
                        selected = max(0, selected - 10)
                    elif event.key == pygame.K_PAGEDOWN:
                        selected = min(len(skills) - 1, selected + 10)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return skills[selected]  # Return skill name

                    # Update scroll to keep selection visible
                    max_visible = 3
                    if selected < scroll_offset:
                        scroll_offset = selected
                    elif selected >= scroll_offset + max_visible:
                        scroll_offset = selected - max_visible + 1
                elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    selected, scroll_offset, confirmed = self._selection_menu_mouse_update(
                        event,
                        skill_options,
                        selected,
                        scroll_offset,
                        input_armed,
                    )
                    if confirmed:
                        return skills[selected]

    def _select_companion_command(self, player_char, enemy):
        """Show Beast Master companion command selection and return command name."""
        commands = ability_mechanics.available_beast_companion_commands(player_char)
        if not commands:
            self.combat_view.add_combat_message("No companion commands available!")
            self._pause_with_events(500)
            return None

        selected = 0
        scroll_offset = 0
        input_armed = self._clear_pending_input()
        frame_player = self._selection_frame_player(player_char)
        while True:
            self._render_combat_frame(frame_player, enemy, [], -1)
            command_options = list(commands)
            descriptions = [
                getattr(player_char.spellbook["Skills"].get(name), "description", "")
                for name in commands
            ]
            self._render_described_selection_menu(
                "Command Companion",
                command_options,
                selected,
                scroll_offset,
                descriptions,
            )
            pygame.display.flip()

            input_armed = release_guard_allows_input(True, input_armed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                input_armed = self._arm_guarded_input(event, input_armed)
                if event.type == pygame.KEYDOWN and not input_armed:
                    continue
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        return None
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(commands)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(commands)
                    elif event.key == pygame.K_PAGEUP:
                        selected = max(0, selected - 10)
                    elif event.key == pygame.K_PAGEDOWN:
                        selected = min(len(commands) - 1, selected + 10)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return commands[selected]
                    scroll_offset = self._scroll_offset_for_selection(selected, scroll_offset)
                elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    selected, scroll_offset, confirmed = self._selection_menu_mouse_update(
                        event,
                        command_options,
                        selected,
                        scroll_offset,
                        input_armed,
                    )
                    if confirmed:
                        return commands[selected]

    def _select_resolve_ability(self, player_char, enemy):
        """Show Resolve ability selection menu and return selected skill name."""
        skills = self._available_skill_names(player_char, enemy, resolve=True)
        if not skills:
            self.combat_view.add_combat_message("No Resolve abilities available!")
            self._pause_with_events(500)
            return None

        selected = 0
        scroll_offset = 0
        input_armed = self._clear_pending_input()
        frame_player = self._selection_frame_player(player_char)
        while True:
            self._render_combat_frame(frame_player, enemy, [], -1)
            resolve_options = []
            for skill_name in skills:
                skill = player_char.spellbook["Skills"][skill_name]
                display_name = self._canonical_resolve_skill_name(getattr(skill, "name", skill_name))
                cost = getattr(skill, "resolve_cost", 0)
                current = promotion_kits.current_resolve(player_char)
                if str(cost).lower() == "full":
                    readiness = "Ready"
                else:
                    missing = max(0, int(cost or 0) - current)
                    readiness = "Ready" if missing == 0 else f"Need {missing}"
                resolve_options.append(
                    f"{display_name} "
                    f"({self._resolve_skill_cost_label(skill)}; {readiness})"
                )
            descriptions = [
                getattr(player_char.spellbook["Skills"][skill_name], "description", "")
                for skill_name in skills
            ]
            self._render_described_selection_menu(
                "Select Resolve", resolve_options, selected, scroll_offset, descriptions
            )
            pygame.display.flip()

            input_armed = release_guard_allows_input(True, input_armed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                input_armed = self._arm_guarded_input(event, input_armed)
                if event.type == pygame.KEYDOWN and not input_armed:
                    continue
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        return None
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(skills)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(skills)
                    elif event.key == pygame.K_PAGEUP:
                        selected = max(0, selected - 10)
                    elif event.key == pygame.K_PAGEDOWN:
                        selected = min(len(skills) - 1, selected + 10)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return skills[selected]
                    scroll_offset = self._scroll_offset_for_selection(selected, scroll_offset)
                elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    selected, scroll_offset, confirmed = self._selection_menu_mouse_update(
                        event,
                        resolve_options,
                        selected,
                        scroll_offset,
                        input_armed,
                    )
                    if confirmed:
                        return skills[selected]

    def _select_summon(self, player_char, enemy):
        """Show summon selection menu and return selected summon name."""
        summons = getattr(player_char, "summons", {}) or {}
        summon_names = [
            name for name, summon in summons.items()
            if self._living_summon_available(summon)
        ]

        if not summon_names:
            self.combat_view.add_combat_message("No summons available!")
            self._pause_with_events(500)
            return None

        selected = 0
        scroll_offset = 0
        input_armed = self._clear_pending_input()
        while True:
            self._render_combat_frame(player_char, enemy, [], -1)
            summon_options = []
            for summon_name in summon_names:
                summon = summons[summon_name]
                level = getattr(getattr(summon, "level", None), "level", None)
                suffix = f" (Lv {level})" if level is not None else ""
                summon_options.append(f"{summon_name}{suffix}")

            self._render_selection_menu("Select Summon", summon_options, selected, scroll_offset)
            pygame.display.flip()

            input_armed = release_guard_allows_input(True, input_armed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                input_armed = self._arm_guarded_input(event, input_armed)
                if event.type == pygame.KEYDOWN and not input_armed:
                    continue
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        return None
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(summon_names)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(summon_names)
                    elif event.key == pygame.K_PAGEUP:
                        selected = max(0, selected - 10)
                    elif event.key == pygame.K_PAGEDOWN:
                        selected = min(len(summon_names) - 1, selected + 10)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return summon_names[selected]
                    scroll_offset = self._scroll_offset_for_selection(selected, scroll_offset)
                elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    selected, scroll_offset, confirmed = self._selection_menu_mouse_update(
                        event,
                        summon_options,
                        selected,
                        scroll_offset,
                        input_armed,
                    )
                    if confirmed:
                        return summon_names[selected]

    @staticmethod
    def _living_summon_available(summon) -> bool:
        is_alive = getattr(summon, "is_alive", None)
        return bool(is_alive()) if callable(is_alive) else True

    def _select_runic_boost_spell(self, player_char, enemy):
        """Show Runic Boost spell selection and return selected spell name."""
        spells = astromancer.boostable_spells(player_char)
        if not spells:
            self.combat_view.add_combat_message("No rune-boostable spells are ready!")
            self._pause_with_events(500)
            return None

        selected = 0
        scroll_offset = 0
        input_armed = self._clear_pending_input()
        while True:
            self._render_combat_frame(player_char, enemy, [], -1)
            spell_options = []
            for spell_name in spells:
                spell = player_char.spellbook["Spells"][spell_name]
                sign = astromancer.sign_for_spell(spell) or "Rune"
                spell_options.append(f"{sign}: {spell_name} (MP: {spell.cost})")
            spell_descriptions = [
                getattr(player_char.spellbook["Spells"][spell_name], "description", "")
                for spell_name in spells
            ]

            self._render_described_selection_menu(
                "Runic Boost", spell_options, selected, scroll_offset, spell_descriptions
            )
            pygame.display.flip()

            input_armed = release_guard_allows_input(True, input_armed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                input_armed = self._arm_guarded_input(event, input_armed)
                if event.type == pygame.KEYDOWN and not input_armed:
                    continue
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        return None
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(spells)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(spells)
                    elif event.key == pygame.K_PAGEUP:
                        selected = max(0, selected - 10)
                    elif event.key == pygame.K_PAGEDOWN:
                        selected = min(len(spells) - 1, selected + 10)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return spells[selected]

                    max_visible = 3
                    if selected < scroll_offset:
                        scroll_offset = selected
                    elif selected >= scroll_offset + max_visible:
                        scroll_offset = selected - max_visible + 1
                elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    selected, scroll_offset, confirmed = self._selection_menu_mouse_update(
                        event,
                        spell_options,
                        selected,
                        scroll_offset,
                        input_armed,
                    )
                    if confirmed:
                        return spells[selected]

    def _select_steal_as_well_spell(self, player_char, enemy):
        """Show Steal As Well spell/scroll selection and return the selected name."""
        from src.core import items as core_items

        options = [
            name for name, spell in player_char.spellbook["Spells"].items()
            if spell.subtyp not in {"Support", "Movement"} and spell.cost <= player_char.mana.current
        ]
        options.extend(
            item_name for item_name, item_list in player_char.inventory.items()
            if item_list and isinstance(item_list[0], core_items.InscribedSpellScroll)
        )
        if not options:
            self.combat_view.add_combat_message("No spell theft options are ready!")
            self._pause_with_events(500)
            return None

        selected = 0
        scroll_offset = 0
        input_armed = self._clear_pending_input()
        while True:
            self._render_combat_frame(player_char, enemy, [], -1)
            descriptions = []
            for option in options:
                spell = player_char.spellbook["Spells"].get(option)
                if spell is not None:
                    descriptions.append(getattr(spell, "description", ""))
                    continue
                item_list = player_char.inventory.get(option, [])
                descriptions.append(getattr(item_list[0], "description", "") if item_list else "")
            self._render_described_selection_menu("Steal As Well", options, selected, scroll_offset, descriptions)
            pygame.display.flip()

            input_armed = release_guard_allows_input(True, input_armed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                input_armed = self._arm_guarded_input(event, input_armed)
                if event.type == pygame.KEYDOWN and not input_armed:
                    continue
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        return None
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(options)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_PAGEUP:
                        selected = max(0, selected - 10)
                    elif event.key == pygame.K_PAGEDOWN:
                        selected = min(len(options) - 1, selected + 10)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return options[selected]

                    max_visible = 3
                    if selected < scroll_offset:
                        scroll_offset = selected
                    elif selected >= scroll_offset + max_visible:
                        scroll_offset = selected - max_visible + 1
                elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    selected, scroll_offset, confirmed = self._selection_menu_mouse_update(
                        event,
                        options,
                        selected,
                        scroll_offset,
                        input_armed,
                    )
                    if confirmed:
                        return options[selected]

    def _select_contract_intent(self, player_char, enemy):
        """Choose and confirm a Demonologist contract intent."""
        intents = demonologist.available_intents(player_char)
        if not intents:
            self.combat_view.add_combat_message("No active fiend contract is bound.")
            self._pause_with_events(500)
            return None

        selected = 0
        scroll_offset = 0
        input_armed = self._clear_pending_input()

        def confirm_intent(intent):
            quote = demonologist.quote_contract(player_char, enemy, intent)
            if not quote.get("ok"):
                self.combat_view.add_combat_message(quote.get("reason", "The patron refuses."))
                self._pause_with_events(700)
                return None
            costs = quote["costs"]
            lines = [
                f"{quote['patron']} demands {costs['gold']} gold.",
                f"Misbehavior risk: {int(quote['misbehavior_chance'] * 100)}%",
            ]
            if costs.get("item"):
                lines.append("Additional demand: one potion.")
            permanent = costs.get("permanent")
            if permanent:
                lines.append(f"Additional demand: permanent {permanent['amount']} {permanent['stat']}.")
            if not demonologist.can_pay_quote(player_char, quote):
                self.combat_view.add_combat_message("You cannot pay that price.")
                self._pause_with_events(700)
                return None
            if self.presenter.render_menu("\n".join(lines), ["Accept", "Refuse"]) == 0:
                return intent
            return None

        while True:
            self._render_combat_frame(player_char, enemy, [], -1)
            self._render_selection_menu("Ask Fiend", intents, selected, scroll_offset)
            pygame.display.flip()

            input_armed = release_guard_allows_input(True, input_armed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                input_armed = self._arm_guarded_input(event, input_armed)
                if event.type == pygame.KEYDOWN and not input_armed:
                    continue
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        return None
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(intents)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(intents)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return confirm_intent(intents[selected])

                    max_visible = 3
                    if selected < scroll_offset:
                        scroll_offset = selected
                    elif selected >= scroll_offset + max_visible:
                        scroll_offset = selected - max_visible + 1
                elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    selected, scroll_offset, confirmed = self._selection_menu_mouse_update(
                        event,
                        intents,
                        selected,
                        scroll_offset,
                        input_armed,
                    )
                    if confirmed:
                        return confirm_intent(intents[selected])

    def _skill_available_for_selection(self, player_char, skill, target=None) -> bool:
        """Return whether a learned skill should be shown in the combat skill list."""
        if getattr(skill, 'passive', False):
            return False
        if not promotion_kits.combat_skill_visible(player_char, skill):
            return False

        if getattr(skill, 'name', None) == "Shield Slam":
            offhand = getattr(player_char, 'equipment', {}).get('OffHand')
            return getattr(offhand, 'subtyp', None) == "Shield"

        if self._is_resolve_skill(skill):
            offhand = getattr(player_char, 'equipment', {}).get('OffHand')
            if getattr(offhand, 'subtyp', None) != "Shield":
                return False

        if getattr(skill, 'weapon', False) and player_char.is_disarmed():
            return False

        art_name = getattr(skill, 'name', None)
        if art_name in grandmaster.ART_WEAPON_TYPES:
            return grandmaster.matching_weapon_for_art_equipped(player_char, art_name)

        if art_name in {entry["name"] for entry in promotion_kits.RESOLVE_SURGES}:
            return promotion_kits.resolve_surge_available(player_char, art_name)

        if getattr(skill, '_requires_incapacitated', False):
            incapacitated = getattr(target, 'incapacitated', None)
            if target is None or not callable(incapacitated) or not incapacitated():
                return False

        return True

    def _render_selection_menu(self, title, options, selected, scroll_offset=0):
        """Render an in-combat selection panel without covering the enemy view."""
        view_width = int(self.screen.get_width() * 0.65)
        panel_width = max(420, view_width)
        panel_height = 176
        panel_x = 0
        panel_y = self.screen.get_height() - panel_height
        max_visible = 3

        max_scroll = max(0, len(options) - max_visible)
        scroll_offset = max(0, min(scroll_offset, max_scroll))
        start_idx = scroll_offset
        end_idx = min(len(options), scroll_offset + max_visible)

        panel = pygame.Surface((panel_width, panel_height))
        panel.set_alpha(228)
        panel.fill((20, 20, 25))
        self.screen.blit(panel, (panel_x, panel_y))
        pygame.draw.rect(
            self.screen,
            (124, 99, 62),
            pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            3,
        )

        font_large = pygame.font.Font(None, 30)
        font_medium = pygame.font.Font(None, 24)
        font_small = pygame.font.Font(None, 18)
        title_surf = font_large.render(title, True, (232, 218, 186))
        self.screen.blit(title_surf, (panel_x + 20, panel_y + 12))
        descriptions = getattr(self, "_selection_menu_descriptions", None)
        if descriptions and 0 <= selected < len(descriptions):
            title_width = title_surf.get_width() if hasattr(title_surf, "get_width") else font_large.size(title)[0]
            description = self._fit_text_to_width(
                font_small,
                str(descriptions[selected] or ""),
                max(80, panel_width - title_width - 58),
            )
            if description:
                desc_surf = font_small.render(description, True, (188, 188, 176))
                self.screen.blit(desc_surf, (panel_x + title_width + 34, panel_y + 18))

        option_y = panel_y + 50
        option_rect_width = panel_width - 58

        for i in range(start_idx, end_idx):
            option = options[i]
            if i == selected:
                highlight_rect = pygame.Rect(panel_x + 18, option_y - 4, option_rect_width, 30)
                pygame.draw.rect(self.screen, (72, 64, 48), highlight_rect)
                pygame.draw.rect(self.screen, (188, 150, 86), highlight_rect, 1)

            prefix = f"{i+1}. "
            option = self._fit_text_to_width(
                font_medium,
                option,
                option_rect_width - 18 - font_medium.size(prefix)[0],
            )

            color = (255, 255, 255) if i == selected else (220, 220, 220)
            option_surf = font_medium.render(f"{prefix}{option}", True, color)
            self.screen.blit(option_surf, (panel_x + 28, option_y))
            option_y += 34

        if len(options) > max_visible:
            track_rect = pygame.Rect(panel_x + panel_width - 22, panel_y + 50, 6, 102)
            pygame.draw.rect(self.screen, (58, 58, 66), track_rect)
            scrollbar_height = int(track_rect.height * max_visible / len(options))
            scrollbar_height = max(20, scrollbar_height)
            scrollbar_y = track_rect.y + int((track_rect.height - scrollbar_height) * scroll_offset / max_scroll)
            pygame.draw.rect(
                self.screen,
                (170, 138, 82),
                pygame.Rect(track_rect.x, scrollbar_y, track_rect.width, scrollbar_height),
            )

        if len(options) > max_visible:
            instructions = "Up/Down or W/S: Navigate | PgUp/PgDn: Scroll | Enter: Select | Esc: Cancel"
        else:
            instructions = "Up/Down or W/S: Navigate | Enter/Space: Select | Esc: Cancel"
        instr_surf = font_small.render(instructions, True, (176, 176, 176))
        self.screen.blit(instr_surf, (panel_x + 20, panel_y + panel_height - 24))
