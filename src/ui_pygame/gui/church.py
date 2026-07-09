"""
Church system for GUI - handles promotion, saving, and quests.
Implements the core church logic from town.py adapted for Pygame presenter.
"""

import os

import pygame

from src.core import companions
from src.core.abilities import ability_classes_for_level, spell_dict, skill_dict
from src.core.classes import (
    classes_dict,
    apply_promotion_ability_rules,
    grant_summoner_initial_summon,
    class_rings,
    demonologist,
    paladin,
)
from src.core.items import remove_equipment
from .quest_manager import QuestManager
from .confirmation_popup import ConfirmationPopup
from .location_menu import LocationMenuScreen
from .mouse_helpers import hit_index, is_left_click, mouse_position
from .promotion_screen import PromotionScreen
from .town_base import TownColors, TownScreenBase, wrap_text_to_pixel_width
from .input_guards import prepare_guarded_input, release_guard_allows_input


class PaladinVowSelectionPopup:
    """Styled vow selector with detail text for the highlighted Paladin path."""

    DETAIL_LINES = {
        "Redemption": (
            "Mercy path focused on Redeem.",
            "Mercy still pays, but turns away from trophies and kill claims.",
            "Conviction makes mercy more persuasive and more rewarding.",
        ),
        "Conquest": (
            "Challenge path focused on naming a foe.",
            "Clean victories against chosen or hunted enemies feed your aura.",
            "Conviction sharpens the pressure on your chosen target.",
        ),
        "Protection": (
            "Guardian path focused on Interpose.",
            "Well-timed blocks turn defense into protective momentum.",
            "Conviction reinforces your next guarded stand.",
        ),
        "Retribution": (
            "Counter path focused on Judgment Riposte.",
            "Enemy aggression can be answered with holy retaliation.",
            "Conviction makes reprisal feel more certain and punishing.",
        ),
    }

    def __init__(self, presenter, *, title: str = "Choose Paladin Vow"):
        self.presenter = presenter
        self.screen = presenter.screen
        self.width = presenter.width
        self.height = presenter.height
        self.title_font = presenter.title_font
        self.large_font = presenter.large_font
        self.normal_font = presenter.normal_font
        self.small_font = presenter.small_font
        self.colors = TownColors
        self.title = title
        self.options = list(paladin.PATHS)
        self.current_selection = 0
        self.panel_rect = self._panel_rect()
        self.option_rects: list[pygame.Rect] = []
        self.list_rect: pygame.Rect | None = None
        self.detail_rect: pygame.Rect | None = None
        self.instruction_rect: pygame.Rect | None = None

    def _panel_rect(self) -> pygame.Rect:
        width = min(int(self.width * 0.82), 820)
        height = min(int(self.height * 0.72), 560)
        return pygame.Rect((self.width - width) // 2, (self.height - height) // 2, width, height)

    def _draw_text(self, text: str, font, color, x: int, y: int, max_width: int | None = None) -> int:
        if max_width is not None:
            text = self._fit_text(text, font, max_width)
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))
        return y + font.get_height()

    def _fit_text(self, text: str, font, max_width: int) -> str:
        if font.size(text)[0] <= max_width:
            return text
        ellipsis = "..."
        available = max(1, max_width - font.size(ellipsis)[0])
        fitted = ""
        for char in text:
            if font.size(fitted + char)[0] > available:
                break
            fitted += char
        return fitted.rstrip() + ellipsis

    def _draw_wrapped(self, text: str, font, color, x: int, y: int, max_width: int, *, max_lines: int = 4) -> int:
        for line in wrap_text_to_pixel_width(text, font, max_width)[:max_lines]:
            y = self._draw_text(line, font, color, x, y)
            y += 3
        return y

    def _option_rects(self, list_rect: pygame.Rect) -> list[pygame.Rect]:
        row_height = 48
        gap = 10
        total_height = len(self.options) * row_height + (len(self.options) - 1) * gap
        y = list_rect.centery - total_height // 2
        return [
            pygame.Rect(list_rect.left + 16, y + index * (row_height + gap), list_rect.width - 32, row_height)
            for index, _option in enumerate(self.options)
        ]

    def _detail_rows(self, vow: str) -> list[tuple[str, str]]:
        return [
            ("Signature", paladin.SKILL_NAMES[vow]),
            ("Aura", paladin.AURA_NAMES[vow]),
            ("Mark", paladin.MARK_NAMES[vow]),
        ]

    def draw(self, background_draw_func=None):
        if background_draw_func is not None:
            background_draw_func()

        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        panel = self.panel_rect
        panel_surface = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        panel_surface.fill((14, 14, 20, 238))
        self.screen.blit(panel_surface, panel)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, panel, 3)

        title_surface = self.title_font.render(self.title, True, self.colors.GOLD)
        self.screen.blit(title_surface, title_surface.get_rect(center=(panel.centerx, panel.top + 42)))

        content_top = panel.top + 82
        footer_top = panel.bottom - 56
        content_rect = pygame.Rect(
            panel.left + 18,
            content_top,
            panel.width - 36,
            max(240, footer_top - content_top - 14),
        )
        list_width = max(230, int(content_rect.width * 0.36))
        list_rect = pygame.Rect(content_rect.left, content_rect.top, list_width, content_rect.height)
        detail_rect = pygame.Rect(list_rect.right + 18, content_rect.top, content_rect.right - list_rect.right - 18, content_rect.height)
        self.list_rect = list_rect
        self.detail_rect = detail_rect

        pygame.draw.rect(self.screen, (20, 20, 28), list_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, list_rect, 1)
        pygame.draw.rect(self.screen, (20, 20, 28), detail_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, detail_rect, 1)

        self.option_rects = self._option_rects(list_rect)
        for index, vow in enumerate(self.options):
            row_rect = self.option_rects[index]
            selected = index == self.current_selection
            if selected:
                pygame.draw.rect(self.screen, self.colors.HIGHLIGHT_BG, row_rect)
                pygame.draw.rect(self.screen, self.colors.GOLD, row_rect, 2)
            color = self.colors.GOLD if selected else self.colors.WHITE
            label = self.normal_font.render(vow, True, color)
            self.screen.blit(label, label.get_rect(center=row_rect.center))

        vow = self.options[self.current_selection]
        x = detail_rect.left + 20
        y = detail_rect.top + 20
        y = self._draw_text(f"Vow of {vow}", self.large_font, self.colors.GOLD, x, y, detail_rect.width - 40)
        y += 12
        for label, value in self._detail_rows(vow):
            label_surface = self.small_font.render(label, True, self.colors.GRAY)
            value_surface = self.normal_font.render(value, True, self.colors.WHITE)
            self.screen.blit(label_surface, (x, y + 3))
            self.screen.blit(value_surface, (x + 104, y))
            y += self.normal_font.get_height() + 10
        pygame.draw.line(self.screen, self.colors.BORDER_COLOR, (x, y), (detail_rect.right - 20, y), 1)
        y += 14
        y = self._draw_wrapped(paladin.DESCRIPTIONS[vow], self.normal_font, self.colors.WHITE, x, y, detail_rect.width - 40, max_lines=4)
        y += 10
        for line in self.DETAIL_LINES.get(vow, ()):
            y = self._draw_wrapped(line, self.small_font, self.colors.GRAY, x, y, detail_rect.width - 40, max_lines=2)
            y += 4

        instructions = "UP/DOWN: Navigate   ENTER: Select   ESC: Cancel"
        instruction_surface = self.small_font.render(instructions, True, self.colors.GRAY)
        self.instruction_rect = instruction_surface.get_rect(center=(panel.centerx, panel.bottom - 26))
        self.screen.blit(instruction_surface, self.instruction_rect)

        pygame.display.flip()

    def show(self, *, flush_events: bool = False, require_key_release: bool = False, background_draw_func=None) -> str | None:
        background = None
        if background_draw_func is None and hasattr(self.screen, "copy"):
            background = self.screen.copy()
            background_draw_func = lambda: self.screen.blit(background, (0, 0))
        elif background_draw_func is None:
            background_draw_func = lambda: self.screen.fill(self.colors.BLACK)

        input_armed = prepare_guarded_input(
            flush_events=flush_events,
            require_key_release=require_key_release,
        )

        def finish(result: str | None) -> str | None:
            if background_draw_func is not None:
                background_draw_func()
                pygame.display.flip()
            return result

        while True:
            self.draw(background_draw_func)
            input_armed = release_guard_allows_input(require_key_release, input_armed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if not input_armed:
                        continue
                    if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                        return finish(None)
                    if event.key == pygame.K_UP:
                        self.current_selection = (self.current_selection - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.current_selection = (self.current_selection + 1) % len(self.options)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        return finish(self.options[self.current_selection])
                elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    if not input_armed:
                        continue
                    hovered = hit_index(self.option_rects, mouse_position(event))
                    if hovered is not None:
                        self.current_selection = hovered
                        if is_left_click(event):
                            return finish(self.options[self.current_selection])
            self.presenter.clock.tick(30)


class ChurchManager(TownScreenBase):
    """Manages church interactions with pygame presenter."""

    ARCANE_CLASS_RING_RITES = {
        "Wizard": {
            "label": "Four Formulae",
            "intro": (
                "The priest opens a lectern of four interlocked formulae. Solve the pattern, "
                "and the Class Ring will remember every failed spell rider as study rather than waste."
            ),
        },
        "Shadowcaster": {
            "label": "Debt Cap Trial",
            "intro": (
                "A black candle is lit beneath the altar. The rite teaches the ring to hold "
                "shadow debt without letting it swallow its bearer."
            ),
        },
        "Knight Enchanter": {
            "label": "Arcane Duel",
            "intro": (
                "The chapel floor becomes a dueling circle of warded light. Steel and mana must "
                "answer together before the ring accepts Mana Tap+."
            ),
        },
        "Grand Summoner": {
            "label": "Conduit Ritual",
            "intro": (
                "The priest marks a summoning circle around the Class Ring. A permanent sliver "
                "of life is offered so every summoned ally can carry more of your will."
            ),
        },
        "Templar": {
            "label": "Relic Defense",
            "intro": (
                "A relic is set upon the altar and every candle bends toward it. Stand before "
                "it, and the Class Ring will learn ordered blessings from your defense."
            ),
        },
        "Master Monk": {
            "label": "Purity Rite",
            "intro": (
                "The priest empties the chapel of weapons and armor. The rite asks whether your "
                "body and mind are enough for the Class Ring to answer."
            ),
        },
        "Archbishop": {
            "label": "Miracle Vigil",
            "intro": (
                "A night-long vigil is compressed into one breath of prayer. The ring listens "
                "for the moment where a miracle may choose to intervene."
            ),
        },
        "Troubadour": {
            "label": "Lost Ballad",
            "intro": (
                "An unfinished hymn is placed in your hands. Sing the missing ending, and the "
                "Class Ring will remember how a song can echo after silence."
            ),
        },
        "Lycan": {
            "label": "Control Rite",
            "intro": (
                "Silver dust marks a careful circle around the altar. The rite does not deny the "
                "beast; it teaches the ring how choice can guide the frenzy."
            ),
        },
        "Astromancer": {
            "label": "Star Chart",
            "intro": (
                "The chapel ceiling darkens into a field of stars. Trace the chart, and the ring "
                "will turn each constellation with your casting."
            ),
        },
        "Soulcatcher": {
            "label": "Ancestral Totem Rite",
            "intro": (
                "Old names are spoken over a quiet totem. The ring learns to carry ancestral "
                "aspects without letting any single spirit own the path."
            ),
        },
        "Beast Master": {
            "label": "Pack Trial",
            "intro": (
                "The priest sets two bowls of spring water side by side. The trial binds recovery "
                "to the pack, so healing one life can answer in another."
            ),
        },
    }
    
    def __init__(self, presenter, player_char):
        super().__init__(presenter)
        self.player_char = player_char
    
    def visit_church(self):
        """Visit the Church of Elysia."""
        church_options = ["Promotion", "Save Game", "Quests"]
        if self._legacy_paladin_vow_available():
            church_options.append("Swear Paladin Vow")
        if self._crusader_vow_trial_available():
            church_options.append("Vow Trial")
        if self._arcane_class_ring_rite_available():
            church_options.append(self._arcane_class_ring_rite_label())
        if demonologist.is_demonologist(self.player_char):
            church_options.append("Hidden Crypt")
        church_options.append("Leave")
        
        church_screen = LocationMenuScreen(self.presenter, "Church of Elysia")
        church_screen.set_location_portrait("Priest")
        self._popup_background_draw_func = lambda: church_screen.draw_frame(do_flip=False)
        
        while True:
            choice_idx = church_screen.navigate(
                church_options,
                reset_cursor=False,
                flush_events=True,
                require_key_release=True,
            )
            
            if choice_idx is None or church_options[choice_idx] == "Leave":
                popup = ConfirmationPopup(self.presenter, "Let the light of Elysia guide you.", show_buttons=False)
                popup.show(**self.popup_show_kwargs())
                break
            
            elif church_options[choice_idx] == "Promotion":
                self.handle_promotion()
            
            elif church_options[choice_idx] == "Save Game":
                self.save_game()
            
            elif church_options[choice_idx] == "Quests":
                qm = QuestManager(
                    self.presenter, 
                    self.player_char, 
                    quest_text_renderer=lambda text: church_screen.display_quest_text(text, npc_name="Priest"),
                    renderer_preserve_formatting=True,
                )
                qm.check_and_offer('Priest')

            elif church_options[choice_idx] == self._arcane_class_ring_rite_label():
                self.visit_arcane_class_ring_rite()

            elif church_options[choice_idx] == "Swear Paladin Vow":
                self.visit_legacy_paladin_vow_choice()

            elif church_options[choice_idx] == "Vow Trial":
                self.visit_crusader_vow_trial()

            elif church_options[choice_idx] == "Hidden Crypt":
                self.visit_hidden_crypt()

            if self._legacy_paladin_vow_available() and "Swear Paladin Vow" not in church_options:
                church_options.insert(-1, "Swear Paladin Vow")
            elif not self._legacy_paladin_vow_available() and "Swear Paladin Vow" in church_options:
                church_options.remove("Swear Paladin Vow")
            if self._crusader_vow_trial_available() and "Vow Trial" not in church_options:
                church_options.insert(-1, "Vow Trial")
            elif not self._crusader_vow_trial_available() and "Vow Trial" in church_options:
                church_options.remove("Vow Trial")
            rite_label = self._arcane_class_ring_rite_label()
            if self._arcane_class_ring_rite_available() and rite_label not in church_options:
                church_options.insert(-1, rite_label)
            elif not self._arcane_class_ring_rite_available() and rite_label in church_options:
                church_options.remove(rite_label)

    def _choose_paladin_vow(self):
        vow = PaladinVowSelectionPopup(self.presenter).show(
            flush_events=True,
            require_key_release=True,
        )
        if vow is None:
            return None

        confirm = ConfirmationPopup(
            self.presenter,
            f"Swear the Vow of {vow}?",
            show_buttons=True,
        )
        return vow if confirm.show(flush_events=True, require_key_release=True) else None

    def _remove_illegal_promotion_gear(self):
        """Move newly illegal promoted-class core gear back to inventory."""
        removed = []
        equipment = getattr(self.player_char, "equipment", {})
        can_equip = getattr(self.player_char, "can_equip_item", None)
        inventory = getattr(self.player_char, "modify_inventory", None)

        for slot in ("Weapon", "OffHand", "Armor", "Helmet"):
            item = equipment.get(slot)
            if item is None or getattr(item, "subtyp", None) == "None":
                continue
            try:
                legal = bool(can_equip(item, slot)) if callable(can_equip) else bool(self.player_char.cls.equip_check(item, slot))
            except Exception:
                legal = False
            if legal:
                continue
            if callable(inventory):
                try:
                    inventory(item, 1)
                except TypeError:
                    inventory(item)
            equipment[slot] = remove_equipment(slot)
            removed.append((slot, getattr(item, "name", str(item))))
        return removed

    def _apply_promotion_stat_bonuses(self, new_class):
        """Apply promoted class stat, resource, and combat bonuses."""
        self.player_char.stats.strength += getattr(new_class, "str_plus", 0)
        self.player_char.stats.intel += getattr(new_class, "int_plus", 0)
        self.player_char.stats.wisdom += getattr(new_class, "wis_plus", 0)
        self.player_char.stats.con += getattr(new_class, "con_plus", 0)
        self.player_char.stats.charisma += getattr(new_class, "cha_plus", 0)
        self.player_char.stats.dex += getattr(new_class, "dex_plus", 0)

        health_bonus = getattr(new_class, "con_plus", 0) * 2
        mana_bonus = getattr(new_class, "int_plus", 0) * 2
        self.player_char.health.max += health_bonus
        if hasattr(self.player_char.health, "current"):
            self.player_char.health.current = min(
                self.player_char.health.max,
                getattr(self.player_char.health, "current", 0) + health_bonus,
            )
        self.player_char.mana.max += mana_bonus
        if hasattr(self.player_char.mana, "current"):
            self.player_char.mana.current = min(
                self.player_char.mana.max,
                getattr(self.player_char.mana, "current", 0) + mana_bonus,
            )
        self.player_char.combat.attack += getattr(new_class, "att_plus", 0)
        self.player_char.combat.defense += getattr(new_class, "def_plus", 0)
        self.player_char.combat.magic += getattr(new_class, "magic_plus", 0)
        self.player_char.combat.magic_def += getattr(new_class, "magic_def_plus", 0)

    def _legacy_paladin_vow_available(self):
        return paladin.is_paladin_lineage(self.player_char) and not paladin.path(self.player_char)

    def visit_legacy_paladin_vow_choice(self):
        if not self._legacy_paladin_vow_available():
            popup = ConfirmationPopup(self.presenter, "No unanswered Paladin vow waits here.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
            return False
        vow = self._choose_paladin_vow()
        if not vow:
            popup = ConfirmationPopup(self.presenter, "The vow remains unspoken.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
            return False
        success, message = self.player_char.choose_paladin_vow(vow)
        popup = ConfirmationPopup(self.presenter, message.strip(), show_buttons=False)
        popup.show(**self.popup_show_kwargs())
        return success

    def _crusader_vow_trial_available(self):
        return (
            class_rings.class_name(self.player_char) == "Crusader"
            and class_rings.has_visible_class_ring(self.player_char)
            and not class_rings.is_awakened(self.player_char, "Crusader")
            and bool(paladin.path(self.player_char))
        )

    def visit_crusader_vow_trial(self):
        if not self._crusader_vow_trial_available():
            popup = ConfirmationPopup(self.presenter, "The Vow Trial does not answer yet.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
            return False
        vow = paladin.path(self.player_char)
        popup = ConfirmationPopup(
            self.presenter,
            f"The altar asks you to affirm the Vow of {vow}.",
            show_buttons=False,
        )
        popup.show(**self.popup_show_kwargs())
        success, message = self.player_char.awaken_class_ring("Crusader", vow=vow)
        ring = self.player_char.equipment.get("Ring")
        if success and getattr(ring, "name", None) == "Class Ring":
            ring.class_mod(self.player_char)
        popup = ConfirmationPopup(self.presenter, message.strip(), show_buttons=False)
        popup.show(**self.popup_show_kwargs())
        return success

    def _arcane_class_ring_rite_config(self):
        return self.ARCANE_CLASS_RING_RITES.get(class_rings.class_name(self.player_char))

    def _arcane_class_ring_rite_label(self):
        config = self._arcane_class_ring_rite_config()
        return config["label"] if config else "Class Ring Rite"

    def _arcane_class_ring_rite_available(self):
        class_name = class_rings.class_name(self.player_char)
        return (
            class_name in self.ARCANE_CLASS_RING_RITES
            and class_rings.has_visible_class_ring(self.player_char)
            and not class_rings.is_awakened(self.player_char, class_name)
        )

    def visit_arcane_class_ring_rite(self):
        """Complete non-Demonologist Mage-branch Class Ring rites."""
        class_name = class_rings.class_name(self.player_char)
        config = self._arcane_class_ring_rite_config()
        if not config:
            popup = ConfirmationPopup(self.presenter, "No Class Ring rite answers you here.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
            return False
        if not self._arcane_class_ring_rite_available():
            popup = ConfirmationPopup(self.presenter, "The Class Ring is not ready for this rite.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
            return False

        popup = ConfirmationPopup(self.presenter, config["intro"], show_buttons=False)
        popup.show(**self.popup_show_kwargs())

        success, message = self.player_char.awaken_class_ring(class_name)
        ring = self.player_char.equipment.get("Ring")
        if success and getattr(ring, "name", None) == "Class Ring":
            ring.class_mod(self.player_char)
        popup = ConfirmationPopup(
            self.presenter,
            message.strip() or f"The Class Ring awakens through {config['label']}.",
            show_buttons=False,
        )
        popup.show(**self.popup_show_kwargs())
        return success
    
    def handle_promotion(self):
        """Handle class promotion at level 30."""
        if self.player_char.level.level < 30 or self.player_char.level.pro_level >= 3:
            if self.player_char.level.pro_level == 3:
                popup = ConfirmationPopup(self.presenter, "You are at max promotion level and can no longer be promoted.", show_buttons=False)
            else:
                popup = ConfirmationPopup(self.presenter, "You need to be level 30 before you can promote your character.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
            return

        current_class = self.player_char.cls.name
        pro_level = self.player_char.level.pro_level

        options = []
        option_map = {}

        if pro_level == 1:
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
            popup = ConfirmationPopup(self.presenter, "No promotion options are currently available.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
            return

        promo_screen = PromotionScreen(
            self.presenter,
            self.player_char,
            options,
            option_map,
            current_class=current_class,
            pro_level=pro_level,
        )
        chosen_name = promo_screen.navigate()
        if not chosen_name:
            popup = ConfirmationPopup(self.presenter, "Promotion cancelled.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
            return

        chosen_ctor = option_map.get(chosen_name)
        if not chosen_ctor:
            popup = ConfirmationPopup(self.presenter, "Promotion option unavailable.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
            return

        chosen_vow = None
        if chosen_name == "Paladin":
            chosen_vow = self._choose_paladin_vow()
            if not chosen_vow:
                popup = ConfirmationPopup(self.presenter, "Promotion cancelled.", show_buttons=False)
                popup.show(**self.popup_show_kwargs())
                return

        try:
            new_class = chosen_ctor()
            self.player_char.cls = new_class
            self.player_char.level.pro_level += 1
            self.player_char.level.level = 1
            self._apply_promotion_stat_bonuses(new_class)

            try:
                self.player_char.level.exp_to_gain = self.player_char.level_exp()
            except Exception:
                pass

            try:
                removed_gear = self._remove_illegal_promotion_gear()
            except Exception:
                removed_gear = []

            if removed_gear:
                lines = ["Some equipped gear no longer fits your promoted class:"]
                lines.extend(f"{slot}: {name}" for slot, name in removed_gear)
                lines.append("Check your inventory and equip replacement gear before returning to the dungeon.")
                popup = ConfirmationPopup(self.presenter, "\n".join(lines), show_buttons=False)
                popup.show(**self.popup_show_kwargs())

            apply_promotion_ability_rules(self.player_char, chosen_name)

            # Grant level 1 abilities for the new class
            for spell_cls in ability_classes_for_level(spell_dict, chosen_name, self.player_char.level.level):
                spell_gain = spell_cls()
                self.player_char.spellbook["Spells"][spell_gain.name] = spell_gain
            
            for skill_cls in ability_classes_for_level(skill_dict, chosen_name, self.player_char.level.level):
                skill_gain = skill_cls()
                self.player_char.spellbook["Skills"][skill_gain.name] = skill_gain
                if skill_gain.name in ["Transform", "Reveal", "Purity of Body"]:
                    skill_gain.use(self.player_char)

            if chosen_vow:
                self.player_char.choose_paladin_vow(chosen_vow)

            if chosen_name == "Warlock":
                fam_options = ["Homunculus", "Fairy", "Mephit", "Jinkin"]
                fam_map = {
                    "Homunculus": companions.Homunculus,
                    "Fairy": companions.Fairy,
                    "Mephit": companions.Mephit,
                    "Jinkin": companions.Jinkin,
                }

                fam_confirmed = False
                while not fam_confirmed:
                    fam_idx = self.presenter.render_menu("Choose your familiar", fam_options)
                    if fam_idx is None:
                        break

                    fam_class = fam_map[fam_options[fam_idx]]
                    familiar = fam_class()
                    description = familiar.inspect()
                    self.presenter.show_message(description, title=familiar.race)

                    confirm = self.presenter.render_menu(
                        f"Bind with this {familiar.race}?",
                        ["Yes", "No"]
                    )
                    if confirm == 0:
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

            if chosen_name == "Summoner":
                grant_summoner_initial_summon(self.player_char)

            if chosen_name == "Demonologist":
                self.player_char.ensure_demonologist_contracts()

            popup = ConfirmationPopup(self.presenter, f"Congratulations! You are now a {chosen_name}.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
        except Exception as e:
            popup = ConfirmationPopup(self.presenter, f"Promotion failed: {e}", show_buttons=False)
            popup.show(**self.popup_show_kwargs())

    def visit_hidden_crypt(self):
        """Manage Demonologist contracts and Class Ring awakening."""
        if not demonologist.is_demonologist(self.player_char):
            popup = ConfirmationPopup(self.presenter, "The crypt door is nowhere to be found.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
            return False

        self.player_char.ensure_demonologist_contracts()
        unlocked = self.player_char.refresh_demonologist_contracts()
        state = self.player_char.demonologist_contracts
        options = ["Review Contracts"]
        if unlocked:
            options.append("Bind Patron")
        if demonologist.ring_can_awaken(self.player_char):
            options.append("Awaken Class Ring")
        options.append("Leave")

        while True:
            choice = self.presenter.render_menu("Hidden Church Crypt", options)
            if choice is None or options[choice] == "Leave":
                return True

            if options[choice] == "Review Contracts":
                if unlocked:
                    active = state.get("active_patron") or "None"
                    text = "Unlocked contracts: " + ", ".join(unlocked) + f"\nActive patron: {active}"
                else:
                    text = "No fiend has answered your name. Defeat an eligible fiend, then return."
                popup = ConfirmationPopup(self.presenter, text, show_buttons=False)
                popup.show(**self.popup_show_kwargs())

            elif options[choice] == "Bind Patron":
                bind_idx = self.presenter.render_menu("Bind which patron?", unlocked)
                if bind_idx is not None and 0 <= bind_idx < len(unlocked):
                    patron = unlocked[bind_idx]
                    demonologist.bind_patron(self.player_char, patron)
                    state = self.player_char.demonologist_contracts
                    popup = ConfirmationPopup(self.presenter, f"{patron} is now your active contract.", show_buttons=False)
                    popup.show(**self.popup_show_kwargs())

            elif options[choice] == "Awaken Class Ring":
                success, message = demonologist.awaken_ring(self.player_char)
                popup = ConfirmationPopup(self.presenter, message.strip(), show_buttons=False)
                popup.show(**self.popup_show_kwargs())
                if success:
                    options = [option for option in options if option != "Awaken Class Ring"]
    
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
            popup = ConfirmationPopup(self.presenter, f"Game saved successfully!", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
        except Exception as e:
            popup = ConfirmationPopup(self.presenter, f"Error saving game:\n\n{str(e)}", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
