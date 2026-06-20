"""
Combat Manager for Pygame GUI.
Handles combat flow with GUI rendering, delegating core game logic to BattleEngine.
"""
from __future__ import annotations

import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import random
import sys

import pygame

from src.core import enemies
from src.core.combat.battle_engine import BattleEngine
from src.core.character import Character
from src.core.combat.battle_logger import BattleLogger
from src.core.player import Player
from .combat_view import CombatView
from .input_guards import prepare_guarded_input, release_guard_allows_input, update_input_armed_from_event
from .level_up import LevelUpScreen

if TYPE_CHECKING:
    from src.core.map_tiles import MapTile
    from src.ui_pygame.game import PygameGame
    from src.ui_pygame.gui.dungeon_hud import DungeonHUD
    from src.ui_pygame.presentation.pygame_presenter import PygamePresenter

# Map display action names (pygame) back to engine action names
_DISPLAY_TO_ENGINE = {
    "Spells": "Cast Spell",
    "Skills": "Use Skill",
    "Items": "Use Item",
}

SLOT_SYMBOL_ATLAS = Path(__file__).resolve().parents[1] / "assets" / "ui" / "slot_machine_symbols.png"
SLOT_CARD_RANKS = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")
SLOT_CARD_SUITS = ("S", "H", "D", "C")
SLOT_CARD_DECK = [f"{rank}{suit}" for suit in SLOT_CARD_SUITS for rank in SLOT_CARD_RANKS]
SLOT_CARD_ORDER = {card: index for index, card in enumerate(SLOT_CARD_DECK)}
SLOT_CARD_VALUES = {
    "A": 14,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
}


def _battle_log_slug(value: object) -> str:
    """Return a filesystem-friendly token for debug battle-log filenames."""
    text = str(value or "unknown").strip().lower()
    slug = "".join(char if char.isalnum() else "-" for char in text)
    return "-".join(part for part in slug.split("-") if part) or "unknown"


class GUICombatManager:
    """Manages combat with pygame GUI rendering, delegating logic to BattleEngine."""
    
    def __init__(self, presenter: PygamePresenter, hud: DungeonHUD, game: PygameGame):
        self.presenter = presenter
        self.screen = presenter.screen
        self.hud = hud
        self.game = game
        self.combat_view = CombatView(self.screen, presenter)
        self.level_up_screen = LevelUpScreen(self.screen, presenter)
        self.logger = BattleLogger()
        self.running = False
        self.engine: BattleEngine | None = None
        # References to dungeon rendering (set by dungeon_manager)
        self.dungeon_renderer = None
        self.player_world_dict = None
        self._combat_background = None
        self.available_actions = []
        self._slot_symbol_cache = None
    
    def _capture_background(self):
        if hasattr(self.presenter, "get_background_surface"):
            try:
                surface = self.presenter.get_background_surface()
                if surface is not None:
                    return surface
            except Exception:
                pass
        return self.screen.copy()

    def _debug_mode_enabled(self) -> bool:
        """Return whether debug-only combat tools should be exposed."""
        return bool(
            getattr(self.game, "debug_mode", False)
            or getattr(self.presenter, "debug_mode", False)
        )

    def _slot_symbol_surfaces(self) -> list[pygame.Surface]:
        """Load and slice the slot-machine symbol atlas."""
        if self._slot_symbol_cache is not None:
            return self._slot_symbol_cache

        symbols: list[pygame.Surface] = []
        try:
            atlas = pygame.image.load(str(SLOT_SYMBOL_ATLAS))
            atlas_w, atlas_h = atlas.get_size()
            full_deck_grid = (
                atlas_w % 13 == 0
                and atlas_h % 4 == 0
                and atlas_w // 13 == atlas_h // 4
            )
            columns = 13 if full_deck_grid else 5
            rows = 4 if full_deck_grid else 2
            cell_w = atlas_w // columns
            cell_h = atlas_h // rows
            for index in range(columns * rows):
                col = index % columns
                row = index // columns
                rect = pygame.Rect(col * cell_w, row * cell_h, cell_w, cell_h)
                symbol = atlas.subsurface(rect).copy()
                bounds = symbol.get_bounding_rect(min_alpha=1)
                if bounds.width and bounds.height and bounds.size != symbol.get_size():
                    cropped = symbol.subsurface(bounds).copy()
                    padding = 6
                    padded = pygame.Surface(
                        (cropped.get_width() + padding * 2, cropped.get_height() + padding * 2),
                        pygame.SRCALPHA,
                    )
                    padded.blit(cropped, (padding, padding))
                    symbol = padded
                symbols.append(symbol)
        except Exception:
            symbols = []
        self._slot_symbol_cache = symbols
        return symbols

    @staticmethod
    def _slot_machine_result_label(spin: str) -> str:
        """Return the visible Slot Machine hand name for a spin."""
        cards = GUICombatManager._parse_slot_cards(spin)
        if cards:
            ranks = [rank for rank, _suit in cards]
            suits = [suit for _rank, suit in cards]
            values = sorted(SLOT_CARD_VALUES[rank] for rank in ranks)
            low_ace_values = sorted(1 if rank == "A" else SLOT_CARD_VALUES[rank] for rank in ranks)
            flush = len(set(suits)) == 1
            straight = (
                values[1] == values[0] + 1 and values[2] == values[1] + 1
            ) or low_ace_values == [1, 2, 3]
            if flush and straight:
                return "Straight Flush"
            if len(set(ranks)) == 1:
                return "3 of a Kind"
            if straight:
                return "Straight"
            if flush:
                return "Flush"
            if len(set(ranks)) == 2:
                return "Pair"
            return "Chance"

        if spin in {"666", "999"}:
            return "Death"
        if spin in {"000", "111", "222", "333", "444", "555", "777", "888"}:
            return "3 of a Kind"
        if "".join(sorted(spin)) in {"012", "123", "234", "345", "456", "567", "678", "789"}:
            return "Straight"
        if len(spin) == 3 and spin[0] == spin[2] and spin[0] != spin[1]:
            return "Palindrome"
        if len(set(spin)) == 2:
            return "Pairs"
        if all(int(digit) % 2 == 0 for digit in spin):
            return "Evens"
        if all(int(digit) % 2 == 1 for digit in spin):
            return "Odds"
        return "Chance"

    @staticmethod
    def _parse_slot_cards(spin: str) -> list[tuple[str, str]] | None:
        if not isinstance(spin, str) or "," not in spin:
            return None
        cards: list[tuple[str, str]] = []
        for raw_card in spin.split(","):
            card = raw_card.strip().upper()
            rank = card[:-1]
            suit = card[-1:] if card else ""
            if rank not in SLOT_CARD_VALUES or suit not in SLOT_CARD_SUITS:
                return None
            cards.append((rank, suit))
        if len(cards) != 3 or len(set(cards)) != 3:
            return None
        return cards

    def _handle_combat_log_scroll_event(self, event) -> bool:
        """Handle combat-log scrolling input. Returns True when handled."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                self.combat_view.scroll_log(-1)
                return True
            if event.key == pygame.K_PAGEDOWN:
                self.combat_view.scroll_log(1)
                return True
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self.combat_view.scroll_log(-1)
            elif event.y < 0:
                self.combat_view.scroll_log(1)
            return True
        return False

    def _clear_pending_input(self) -> bool:
        """Clear buffered events and require a fresh key release before selection input."""
        return prepare_guarded_input(flush_events=True, require_key_release=True)

    def _persist_debug_battle_log(self, result: str) -> Path | None:
        """Persist the current battle log when debug logging is enabled."""
        if not self._debug_mode_enabled():
            return None

        metadata = getattr(self.logger, "metadata", {}) or {}
        player_name = metadata.get("player", {}).get("name", "player")
        enemy_name = metadata.get("enemy", {}).get("name", "enemy")
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        filename = (
            f"{timestamp}-"
            f"{_battle_log_slug(player_name)}-vs-{_battle_log_slug(enemy_name)}-"
            f"{_battle_log_slug(result)}.json"
        )
        try:
            return self.logger.export_json_file(Path("debug_logs") / "battles" / filename)
        except Exception:
            return None

    @staticmethod
    def _arm_guarded_input(event, input_armed: bool) -> bool:
        return update_input_armed_from_event(event, True, input_armed)

    @staticmethod
    def _fit_text_to_width(font: pygame.font.Font, text: str, max_width: int) -> str:
        """Trim text to the rendered width available for compact combat overlays."""
        if max_width <= 0 or font.size(text)[0] <= max_width:
            return text

        ellipsis = "..."
        ellipsis_width = font.size(ellipsis)[0]
        if ellipsis_width >= max_width:
            return ellipsis

        trimmed = text
        while trimmed and font.size(trimmed)[0] + ellipsis_width > max_width:
            trimmed = trimmed[:-1]
        return f"{trimmed.rstrip()}{ellipsis}"

    @staticmethod
    def _combat_effect_kind(action: str, choice: str | None = None) -> str:
        if action in {"Spells", "Cast Spell"}:
            return "spell"
        if action in {"Skills", "Use Skill"}:
            return "skill"
        if choice and any(term in str(choice).lower() for term in ("spell", "bolt", "blast", "storm", "fire", "ice")):
            return "spell"
        return "weapon"

    @staticmethod
    def _combat_effect_element(choice: object = None, message: str = "") -> str | None:
        text = f"{choice or ''} {message or ''}".lower()
        element_terms = {
            "Fire": ("fire", "flame", "burn", "ember"),
            "Ice": ("ice", "frost", "freeze", "frozen"),
            "Electric": ("electric", "lightning", "storm", "thunder", "shock"),
            "Water": ("water", "wave", "flood"),
            "Earth": ("earth", "stone", "rock"),
            "Wind": ("wind", "air", "gale"),
            "Poison": ("poison", "venom", "toxin"),
            "Holy": ("holy", "light", "radiant"),
            "Dark": ("dark", "shadow", "void"),
            "Death": ("death", "doom", "fatal"),
        }
        for element, terms in element_terms.items():
            if any(term in text for term in terms):
                return element
        return None

    def _show_combat_damage_effect(
        self,
        target: str,
        action: str,
        choice: str | None,
        message: str,
        amount: int | None = None,
    ) -> None:
        kind = self._combat_effect_kind(action, choice)
        element = self._combat_effect_element(choice, message)
        self.combat_view.trigger_impact_effect(
            target,
            kind,
            element,
        )
        if amount:
            color = self.combat_view.colors.get("log_damage", (235, 120, 105))
            self.combat_view.trigger_floating_text(target, f"-{amount}", color)
        self.combat_view.show_damage_flash(
            target == "player",
            event_handler=self._handle_combat_log_scroll_event,
        )

    def _show_combat_heal_text(self, target: str, amount: int) -> None:
        if amount <= 0:
            return
        color = self.combat_view.colors.get("log_heal", (120, 210, 135))
        self.combat_view.trigger_floating_text(target, f"+{amount}", color)

    def _play_smoke_screen_visual(
        self,
        player_char: Player,
        enemy: Character,
        target: str,
        frames: int = 24,
    ) -> None:
        """Briefly show smoke for instant Smoke Screen escapes."""
        self.combat_view.trigger_smoke_screen_visual(target)
        clock = pygame.time.Clock()
        for _ in range(frames):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                self._handle_combat_log_scroll_event(event)
            self._render_combat_frame(player_char, enemy, [], -1)
            pygame.display.flip()
            clock.tick(60)

    def _show_slot_machine_reveal(self, user: Character, target: Character) -> str:
        """Animate a Slot Machine spin popup and reveal cards left-to-right."""
        cards = random.sample(SLOT_CARD_DECK, 3)
        spin = ",".join(cards)
        result_label = self._slot_machine_result_label(spin)
        symbols = self._slot_symbol_surfaces()
        clock = pygame.time.Clock()

        def draw_symbol(symbol_index: int, reel_rect: pygame.Rect, alpha: int = 255, y_offset: int = 0) -> None:
            if symbols:
                symbol = symbols[symbol_index]
                inset = reel_rect.inflate(-24, -20)
                scale = min(inset.width / symbol.get_width(), inset.height / symbol.get_height())
                scaled_size = (
                    max(1, int(symbol.get_width() * scale)),
                    max(1, int(symbol.get_height() * scale)),
                )
                symbol_surface = pygame.transform.smoothscale(symbol, scaled_size)
                symbol_surface.set_alpha(alpha)
                symbol_rect = symbol_surface.get_rect(center=(reel_rect.centerx, reel_rect.centery + y_offset))
                self.screen.blit(symbol_surface, symbol_rect)
                return

            fallback_font = pygame.font.Font(None, 62)
            fallback_text = SLOT_CARD_DECK[symbol_index] if 0 <= symbol_index < len(SLOT_CARD_DECK) else "?"
            fallback = fallback_font.render(fallback_text, True, (120, 20, 30))
            if hasattr(fallback, "set_alpha"):
                fallback.set_alpha(alpha)
            self.screen.blit(fallback, fallback.get_rect(center=(reel_rect.centerx, reel_rect.centery + y_offset)))

        def draw_overlay(revealed_count: int, final: bool = False) -> None:
            self._render_combat_frame(user, target, [], -1)

            overlay = pygame.Surface((self.combat_view.combat_width, self.combat_view.combat_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 185))
            self.screen.blit(overlay, (0, 0))

            popup_width = min(560, self.combat_view.combat_width - 40)
            popup_height = min(390, self.combat_view.combat_height - 40)
            popup_x = (self.combat_view.combat_width - popup_width) // 2
            popup_y = (self.combat_view.combat_height - popup_height) // 2
            popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

            pygame.draw.rect(self.screen, (42, 9, 16), popup_rect, border_radius=8)
            pygame.draw.rect(self.screen, (144, 24, 34), popup_rect.inflate(-14, -14), border_radius=6)
            pygame.draw.rect(self.screen, (236, 188, 72), popup_rect, 5, border_radius=8)
            pygame.draw.rect(self.screen, (72, 14, 24), popup_rect.inflate(-34, -32), border_radius=5)

            top_rect = pygame.Rect(popup_rect.left + 42, popup_rect.top + 22, popup_rect.width - 84, 64)
            pygame.draw.rect(
                self.screen,
                (122, 20, 34),
                top_rect,
                border_radius=6,
            )
            pygame.draw.rect(self.screen, (244, 202, 88), top_rect, 3, border_radius=6)

            for index in range(11):
                bulb_x = popup_rect.left + 28 + index * ((popup_rect.width - 56) // 10)
                bulb_color = (255, 228, 126) if (pygame.time.get_ticks() // 240 + index) % 2 == 0 else (178, 92, 46)
                pygame.draw.rect(self.screen, bulb_color, pygame.Rect(bulb_x - 5, popup_rect.top + 8, 10, 10), border_radius=5)

            title_font = pygame.font.Font(None, 46)
            subtitle_font = pygame.font.Font(None, 25)

            title_text = title_font.render("Slots", True, (255, 225, 106))
            title_rect = title_text.get_rect(center=(popup_rect.centerx, top_rect.centery - 2))
            self.screen.blit(title_text, title_rect)

            reel_area = pygame.Rect(popup_rect.left + 58, popup_rect.top + 104, popup_rect.width - 136, 158)
            pygame.draw.rect(self.screen, (25, 18, 22), reel_area.inflate(24, 20), border_radius=7)
            pygame.draw.rect(self.screen, (232, 192, 92), reel_area.inflate(24, 20), 3, border_radius=7)
            reel_gap = 14
            reel_width = (reel_area.width - reel_gap * 2) // 3
            for i in range(3):
                reel_rect = pygame.Rect(
                    reel_area.left + i * (reel_width + reel_gap),
                    reel_area.top,
                    reel_width,
                    reel_area.height,
                )
                pygame.draw.rect(self.screen, (232, 222, 190), reel_rect, border_radius=5)
                pygame.draw.rect(self.screen, (255, 250, 224), reel_rect.inflate(-8, -8), border_radius=4)
                pygame.draw.rect(self.screen, (40, 24, 30), reel_rect, 3, border_radius=5)

                symbol_index = SLOT_CARD_ORDER[cards[i]]
                if i >= revealed_count:
                    spin_index = (pygame.time.get_ticks() // 145 + i * 11) % len(SLOT_CARD_DECK)
                    draw_symbol((spin_index - 1) % len(SLOT_CARD_DECK), reel_rect, alpha=85, y_offset=-44)
                    draw_symbol(spin_index, reel_rect, alpha=210)
                    draw_symbol((spin_index + 1) % len(SLOT_CARD_DECK), reel_rect, alpha=85, y_offset=44)
                else:
                    draw_symbol(symbol_index, reel_rect)

            payout_rect = pygame.Rect(popup_rect.left + 120, popup_rect.bottom - 82, popup_rect.width - 240, 26)
            pygame.draw.rect(self.screen, (30, 22, 26), payout_rect, border_radius=4)
            pygame.draw.rect(self.screen, (178, 150, 84), payout_rect, 2, border_radius=4)
            payout_text = result_label if final else "..."
            payout = subtitle_font.render(payout_text, True, (245, 225, 150) if final else (120, 112, 116))
            self.screen.blit(payout, payout.get_rect(center=payout_rect.center))

            handle_x = popup_rect.right - 34
            pygame.draw.rect(self.screen, (86, 68, 54), (handle_x, popup_rect.top + 116, 10, 110), border_radius=4)
            pygame.draw.rect(self.screen, (218, 45, 54), (handle_x - 12, popup_rect.top + 98, 34, 34), border_radius=16)

            subtitle_text = "Press any key or click to continue" if final else "Reels spinning..."
            subtitle_color = (245, 225, 150) if final else (194, 182, 176)
            subtitle = subtitle_font.render(subtitle_text, True, subtitle_color)
            subtitle_rect = subtitle.get_rect(center=(popup_rect.centerx, popup_rect.bottom - 34))
            self.screen.blit(subtitle, subtitle_rect)

            pygame.display.flip()

        for reveal_idx in range(1, 4):
            frames = 18 + reveal_idx * 8
            for _ in range(frames):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
                draw_overlay(reveal_idx)
                clock.tick(90)

        input_armed = prepare_guarded_input(flush_events=False, require_key_release=True)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                input_armed = self._arm_guarded_input(event, input_armed)
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.JOYBUTTONDOWN) and input_armed:
                    waiting = False
                    break
            if waiting:
                if release_guard_allows_input(True, input_armed):
                    input_armed = True
                draw_overlay(3, final=True)
                clock.tick(18)

        return spin
        
    def start_combat(self, player_char: Player, enemy: Character, tile: MapTile) -> bool:
        """
        Initiate combat between player and enemy.
        
        Args:
            player_char: The player character
            enemy: The enemy to fight
            tile: The map tile where combat is occurring
        
        Returns:
            bool: True if player won, False if player fled/died
        """
        # Store tile for loot drops
        self.current_tile = tile

        # Ensure dungeon background has a valid world dict for rendering
        if not self.player_world_dict and hasattr(player_char, "world_dict"):
            self.player_world_dict = player_char.world_dict

        # Create the core engine (handles initiative, actions, bookkeeping)
        self.engine = BattleEngine(
            player=player_char,
            enemy=enemy,
            tile=tile,
            game=self.game,
            logger=self.logger,
        )
        
        # Build display-friendly action list from the engine's available actions
        self.available_actions = self._build_display_actions()

        # Initialize combat state
        self.running = True
        self.combat_view.reset_combat_log()
        self.combat_view.add_combat_message(f"Combat started with {enemy.name}!")
        self._combat_background = self._capture_background()
        self._prepare_enemy_combat_assets(enemy)
        
        # Show initial combat screen with brief transition delay (with animation updates)
        init_clock = pygame.time.Clock()
        for _ in range(48):  # 800ms at 60fps
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                self._handle_combat_log_scroll_event(event)
            self._render_combat_frame(player_char, enemy, [], -1)
            pygame.display.flip()
            init_clock.tick(60)
        
        # Determine who goes first (engine handles initiative)
        first, _ = self.engine.start_battle()
        if player_char.encumbered:
            self.combat_view.add_combat_message("You are ENCUMBERED! Enemy strikes first!")
        
        if first == player_char:
            self.combat_view.add_combat_message(f"{player_char.name} has the initiative!")
        else:
            self.combat_view.add_combat_message(f"{enemy.name} has the initiative!")
        
        clock = pygame.time.Clock()
        fled = False
        
        # Main combat loop
        while self.running and self.engine.battle_continues() and not player_char.in_town():
            if self.engine.is_player_turn():
                action_result = self._player_turn(player_char, enemy)
                if action_result == "flee":
                    fled = True
                    break
                elif not action_result:  # Closed combat
                    fled = True
                    break

                # Check if enemy died from special effects (e.g., self-healing that prevents death)
                if not enemy.is_alive():
                    self.combat_view.enemy_dies(enemy)
                    break
                
                # Check for Mad Waitress form change (below 10% health)
                self._check_enemy_form_change(player_char, enemy)
            else:
                # Double-check enemy is still alive before their turn
                if not enemy.is_alive():
                    self.combat_view.enemy_dies(enemy)
                    break
                    
                enemy_result = self._enemy_turn(player_char, enemy)
                if enemy_result == "flee":
                    fled = True
                    break
                
                # Check if player died
                if not player_char.is_alive():
                    break

                # Prevent Mad Waitress from dying before her forced transition
                self._preserve_waitress_for_transition(enemy)
                self._check_enemy_form_change(player_char, enemy)
                
                # Check if enemy died (e.g., from self-damaging skills like Widow's Wail)
                if not enemy.is_alive():
                    self.combat_view.enemy_dies(enemy)
                    break
            
            # Advance turn: post-turn processing + swap
            self._post_turn_processing(player_char, enemy)
            self.engine.swap_turns()
            self._refresh_combat_background(player_char, enemy)
            
            # Refresh available actions for next turn
            self.available_actions = self._build_display_actions()
            
            # Small delay between turns (with animation updates)
            for _ in range(18):  # 300ms at 60fps
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
                    self._handle_combat_log_scroll_event(event)
                self._render_combat_frame(player_char, enemy, [], -1)
                pygame.display.flip()
                clock.tick(60)
        
        # Combat ended - show result
        return self._handle_combat_end(player_char, enemy, fled)

    def _prepare_enemy_combat_assets(self, enemy: Character) -> None:
        """Warm the current enemy's combat sprites before the first combat frame."""
        prepare = getattr(self.combat_view, "prepare_enemy_assets", None)
        if callable(prepare):
            try:
                prepare(enemy)
            except Exception:
                pass

    def _build_display_actions(self) -> list[str]:
        """Build the pygame display-friendly action list from the engine's available actions."""
        raw_actions = self.engine.available_actions
        action_names = []
        for action in raw_actions:
            if isinstance(action, dict):
                action_name = action.get('name', str(action))
            else:
                action_name = str(action)
            # Rename for display
            action_name = action_name.replace("Cast Spell", "Spells") \
                                    .replace("Use Skill", "Skills") \
                                    .replace("Use Item", "Items")
            action_names.append(action_name)

        # Deduplicate while preserving order
        deduped = []
        seen = set()
        for name in action_names:
            normalized = name.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            deduped.append(normalized)

        # Add Defend if not already present
        if "Defend" not in deduped and "Attack" in deduped:
            deduped.insert(1, "Defend")

        # Add Pickup Weapon if disarmed
        if self.engine.player.is_disarmed() and "Pickup Weapon" not in deduped:
            idx = 2 if "Defend" in deduped else 1
            deduped.insert(idx, "Pickup Weapon")

        if self._debug_mode_enabled() and "Auto Kill" not in deduped:
            deduped.append("Auto Kill")

        return deduped

    def _refresh_display_actions(self) -> None:
        """Refresh the visible combat action list when turn-start effects change availability."""
        try:
            self.available_actions = self._build_display_actions()
        except AttributeError:
            return

    def _post_turn_processing(self, player_char: Player, enemy: Character) -> None:
        """Handle engine post-turn + display any messages."""
        visual_before = (getattr(enemy, "name", None), getattr(enemy, "picture", None))
        post = self.engine.post_turn()
        visual_after = (getattr(enemy, "name", None), getattr(enemy, "picture", None))
        added_message = False
        for msg in post.messages:
            if msg:
                for line in msg.strip().split('\n'):
                    if line.strip():
                        self.combat_view.add_combat_message(line)
                        added_message = True
        if added_message:
            self._flush_result_frame(player_char, enemy)
        if visual_after != visual_before:
            self._play_enemy_visual_transition(player_char, enemy, visual_before, visual_after)

    def _flush_result_frame(self, player_char, enemy) -> None:
        """Draw result log text before any impact animation or turn transition starts."""
        self._render_combat_frame(player_char, enemy, [], -1)
        pygame.display.flip()
        try:
            pygame.event.pump()
        except pygame.error:
            pass
        pygame.time.Clock().tick(60)

    def _play_enemy_visual_transition(
        self,
        player_char: Player,
        enemy: Character,
        visual_before: tuple[object, object],
        visual_after: tuple[object, object],
    ) -> None:
        """Briefly alternate old/new enemy visuals when a form changes."""
        before_picture = visual_before[1]
        after_picture = visual_after[1]
        if not before_picture or not after_picture or before_picture == after_picture:
            self.combat_view.reload_enemy_sprite(enemy)
            return

        original_offset = getattr(self.combat_view, "enemy_visual_offset", (0, 0))
        frames = [
            (before_picture, -8),
            (after_picture, 8),
            (before_picture, -6),
            (after_picture, 6),
            (before_picture, -3),
            (after_picture, 0),
        ]
        clock = pygame.time.Clock()
        try:
            for picture, offset_x in frames:
                enemy.picture = picture
                self.combat_view.reload_enemy_sprite(enemy)
                self.combat_view.enemy_visual_offset = (offset_x, 0)
                for _ in range(5):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit(0)
                        self._handle_combat_log_scroll_event(event)
                    self._render_combat_frame(player_char, enemy, [], -1)
                    pygame.display.flip()
                    clock.tick(60)
        finally:
            enemy.picture = after_picture
            self.combat_view.enemy_visual_offset = original_offset
            self.combat_view.reload_enemy_sprite(enemy)
    
    def _player_turn(self, player_char, enemy):
        """
        Handle player's turn with action selection.
        
        Returns:
            str/bool: "flee" if fled, False if cancelled, True if action taken
        """
        # Pre-turn: process status effects and check if player can act
        pre = self.engine.pre_turn()
        if pre.effects_text:
            for line in pre.effects_text.strip().split('\n'):
                if line.strip():
                    self.combat_view.add_combat_message(line)
            self._flush_result_frame(player_char, enemy)

        # If the player died from effects (poison, DOT, bleed), end turn immediately
        if pre.died_from_effects:
            return True

        if not pre.can_act:
            self.combat_view.add_combat_message(pre.inactive_reason.strip())
            self._flush_result_frame(player_char, enemy)
            return True  # Turn skipped

        self._refresh_display_actions()

        # Check for forced actions (berserk, charging, jump)
        forced = self.engine.get_forced_action()
        if forced:
            if forced.action == "Cancelled":
                for line in forced.cancel_message.strip().split('\n'):
                    if line.strip():
                        self.combat_view.add_combat_message(line)
                self._flush_result_frame(player_char, enemy)
                return True

            if forced.action == "Attack":
                self.combat_view.add_combat_message(f"{player_char.name} is BERSERKED and attacks wildly!")

            # Execute the forced action via engine
            enemy_hp_before = enemy.health.current
            result = self.engine.execute_action(forced.action, choice=forced.choice)

            for line in result.message.strip().split('\n'):
                if line.strip():
                    self.combat_view.add_combat_message(line)

            self._flush_result_frame(player_char, enemy)

            # Damage flash for attack/skill hits
            damage_to_enemy = max(0, enemy_hp_before - enemy.health.current)
            if damage_to_enemy > 0:
                self.combat_view.enemy_take_damage(enemy)
                self._show_combat_damage_effect("enemy", forced.action, forced.choice, result.message, damage_to_enemy)
                self._flush_result_frame(player_char, enemy)

            self._preserve_waitress_for_transition(enemy)

            if result.fled:
                return "flee"
            return True
        
        # Get available actions
        actions = self.available_actions
        selected_action = 0
        input_armed = self._clear_pending_input()
        
        action_taken = False
        
        while not action_taken:
            # Render combat scene
            self._render_combat_frame(player_char, enemy, actions, selected_action)
            
            # Handle input
            input_armed = release_guard_allows_input(True, input_armed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

                input_armed = self._arm_guarded_input(event, input_armed)
                if event.type == pygame.KEYDOWN and not input_armed:
                    continue

                if self._handle_combat_log_scroll_event(event):
                    continue
                
                elif event.type == pygame.KEYDOWN:
                    # Grid navigation: 3 actions per row
                    actions_per_row = 3
                    current_row = selected_action // actions_per_row
                    current_col = selected_action % actions_per_row
                    num_rows = (len(actions) + actions_per_row - 1) // actions_per_row
                    
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        # Move up one row
                        if current_row > 0:
                            selected_action -= actions_per_row
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        # Move down one row
                        new_action = selected_action + actions_per_row
                        if new_action < len(actions):
                            selected_action = new_action
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        # Move left one column
                        if current_col > 0:
                            selected_action -= 1
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        # Move right one column
                        if current_col < actions_per_row - 1 and selected_action + 1 < len(actions):
                            selected_action += 1
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # Execute selected action
                        action_result = self._execute_action(
                            actions[selected_action], 
                            player_char, 
                            enemy
                        )
                        if action_result == "flee":
                            return "flee"
                        elif action_result is not None:
                            action_taken = True
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6]:
                        # Number keys for quick selection
                        num = event.key - pygame.K_1
                        if num < len(actions):
                            action_result = self._execute_action(
                                actions[num], 
                                player_char, 
                                enemy
                            )
                            if action_result == "flee":
                                return "flee"
                            elif action_result is not None:
                                action_taken = True
            
            pygame.display.flip()

        # Companion / familiar turn
        companion_msg = self.engine.companion_turn()
        if companion_msg:
            for line in companion_msg.strip().split('\n'):
                if line.strip():
                    self.combat_view.add_combat_message(line)
        
        return True
    
    def _check_enemy_form_change(self, player_char, enemy):
        """
        Check if Mad Waitress should change form/state when health drops below 10%.
        When the transition happens, she becomes sane, changes sprite back to waitress.png,
        and attacks herself once before dying.
        """
        # Only applies to Mad Waitress (NightHag2)
        if not isinstance(enemy, enemies.NightHag2):
            return
        
        # Check if already transitioned
        if getattr(enemy, '_form_changed', False):
            return
        
        # Check health threshold (below 10%)
        health_pct = enemy.health.current / enemy.health.max
        if health_pct >= 0.1:
            return
        
        # Perform transition
        enemy._form_changed = True
        
        # Collect transition messages to display in popup
        transition_messages = [
            "The Mad Waitress momentarily comes to her senses...",
            "Her eyes clear. She sees what she has become.",
            "",
            "Recognizing the horror of her actions,",
            "she takes her own life, finally finding peace with Joffrey..."
        ]
        
        # Change name and sprite back to normal Waitress
        enemy.name = "Waitress"
        self.combat_view.reload_enemy_sprite(enemy)
        
        # Waitress takes her own life - deal lethal damage
        damage = enemy.health.current
        enemy.health.current = 0
        
        # Show popup with the wail/transition narrative
        from .confirmation_popup import ConfirmationPopup
        popup_text = "\n".join(transition_messages)
        popup = ConfirmationPopup(self.presenter, popup_text, show_buttons=False)
        popup.show(flush_events=True, require_key_release=True)

        # Show combat log messages for the self-attack
        self.combat_view.add_combat_message(
            f"{enemy.name} turns her weapon on herself in despair!"
        )
        self.combat_view.add_combat_message(
            f"{enemy.name} takes {damage} damage from the attack!"
        )
        
        # Enemy is now dead
        self.combat_view.enemy_dies(enemy)
    
    def _preserve_waitress_for_transition(self, enemy) -> None:
        """Prevent killing the Mad Waitress before her transition triggers."""
        if not isinstance(enemy, enemies.NightHag2):
            return
        if getattr(enemy, '_form_changed', False):
            return
        if enemy.health.current <= 0:
            enemy.health.current = 1
    
    def _execute_action(self, action, player_char, enemy):
        """Execute a player action by delegating to the engine."""
        if action == "Auto Kill":
            if not self._debug_mode_enabled():
                self.combat_view.add_combat_message("Auto Kill is only available in debug mode.")
                return None
            enemy_hp_before = enemy.health.current
            enemy.health.current = 0
            damage_to_enemy = max(0, enemy_hp_before - enemy.health.current)
            self.combat_view.add_combat_message(f"Debug: {enemy.name} defeated.")
            self.combat_view.enemy_take_damage(enemy)
            self._show_combat_damage_effect("enemy", "Attack", None, "", damage_to_enemy)
            return "action_taken"

        # Map display name back to engine name
        engine_action = _DISPLAY_TO_ENGINE.get(action, action)

        # Sub-menu actions need a selection UI first
        choice = None

        if action == "Items":
            selected_item = self._select_item(player_char, enemy)
            if not selected_item:
                return None  # Cancelled
            choice = selected_item.name

        elif action == "Spells":
            if player_char.abilities_suppressed():
                reason = "the anti-magic field" if getattr(player_char, "anti_magic_active", False) else "silence"
                self.combat_view.add_combat_message(
                    f"{player_char.name} cannot cast spells because of {reason}!"
                )
                return None
            selected_spell = self._select_spell(player_char, enemy)
            if not selected_spell:
                return None
            choice = selected_spell

        elif action == "Skills":
            if player_char.abilities_suppressed():
                reason = "the anti-magic field" if getattr(player_char, "anti_magic_active", False) else "silence"
                self.combat_view.add_combat_message(
                    f"{player_char.name} cannot use skills because of {reason}!"
                )
                return None
            selected_skill = self._select_skill(player_char, enemy)
            if not selected_skill:
                return None
            choice = selected_skill

        elif action == "Pickup Weapon":
            if not player_char.is_disarmed():
                self.combat_view.add_combat_message("Not disarmed!")
                return None

        if choice is not None:
            self._render_combat_frame(player_char, enemy, [], -1)
            pygame.display.flip()

        # Record HP before execution for damage flash
        enemy_hp_before = enemy.health.current
        player_hp_before = player_char.health.current
        enemy_name_before = enemy.name

        # Delegate to engine (handles attack rolls, spell casts, skill use, etc.)
        slot_cb = None
        if action == "Skills" and choice:
            skill_obj = player_char.spellbook.get('Skills', {}).get(choice)
            if skill_obj and skill_obj.name == "Slot Machine":
                slot_cb = lambda _u, _t: self._show_slot_machine_reveal(player_char, enemy)

        result = self.engine.execute_action(engine_action, choice=choice, slot_machine_callback=slot_cb)

        # Display result messages
        for line in result.message.strip().split('\n'):
            if line.strip():
                self.combat_view.add_combat_message(line)

        if engine_action == "Use Skill" and choice == "Smoke Screen":
            self._play_smoke_screen_visual(player_char, enemy, "player")
        else:
            self._flush_result_frame(player_char, enemy)

        # Show damage flash for enemy damage
        damage_to_enemy = max(0, enemy_hp_before - enemy.health.current)
        showed_damage_effect = False
        if damage_to_enemy > 0:
            self.combat_view.enemy_take_damage(enemy)
            self._show_combat_damage_effect("enemy", action, choice, result.message, damage_to_enemy)
            showed_damage_effect = True
        else:
            self._show_combat_heal_text("enemy", max(0, enemy.health.current - enemy_hp_before))

        # Show damage flash for player damage (from reflected/self-damage skills)
        damage_to_player = max(0, player_hp_before - player_char.health.current)
        if damage_to_player > 0:
            self._show_combat_damage_effect("player", action, choice, result.message, damage_to_player)
            showed_damage_effect = True
        else:
            self._show_combat_heal_text("player", max(0, player_char.health.current - player_hp_before))

        if showed_damage_effect:
            self._flush_result_frame(player_char, enemy)

        # Check if enemy shapeshifted (name changed)
        if enemy.name != enemy_name_before:
            self.combat_view.reload_enemy_sprite(enemy)

        self._preserve_waitress_for_transition(enemy)

        if result.fled or bool(getattr(self.engine, "flee", False)):
            return "flee"
        return "action_taken"
    
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
    
    def _select_item(self, player_char, enemy):
        """Show item selection menu and return selected item."""
        # Get usable items (Health, Mana, Elixir, Status potions)
        usable_types = ['Health', 'Mana', 'Elixir', 'Status', 'Scroll']
        items = []
        for item_name, item_list in player_char.inventory.items():
            if item_list and item_list[0].subtyp in usable_types:
                items.append((item_name, item_list[0], len(item_list)))
        
        if not items:
            self.combat_view.add_combat_message("No usable items!")
            self._pause_with_events(500)
            return None
        
        # Create selection menu
        selected = 0
        scroll_offset = 0
        input_armed = self._clear_pending_input()
        while True:
            # Render combat with item menu overlay
            self._render_combat_frame(player_char, enemy, [], -1)
            self._render_selection_menu(
                "Select Item",
                [f"{name} ({count})" for name, _, count in items],
                selected,
                scroll_offset
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
                        selected = (selected - 1) % len(items)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(items)
                    elif event.key == pygame.K_PAGEUP:
                        selected = max(0, selected - 10)
                    elif event.key == pygame.K_PAGEDOWN:
                        selected = min(len(items) - 1, selected + 10)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return items[selected][1]  # Return the item object
                    
                    # Update scroll to keep selection visible
                    max_visible = 3
                    if selected < scroll_offset:
                        scroll_offset = selected
                    elif selected >= scroll_offset + max_visible:
                        scroll_offset = selected - max_visible + 1
    
    def _select_spell(self, player_char, enemy):
        """Show spell selection menu and return selected spell name."""
        # Filter out passive spells
        spells = [name for name, spell in player_char.spellbook['Spells'].items() 
                  if not getattr(spell, 'passive', False)]
        
        if not spells:
            self.combat_view.add_combat_message("No spells learned!")
            self._pause_with_events(500)
            return None
        
        selected = 0
        scroll_offset = 0
        input_armed = self._clear_pending_input()
        while True:
            # Render combat with spell menu overlay
            self._render_combat_frame(player_char, enemy, [], -1)
            spell_options = []
            for spell_name in spells:
                spell = player_char.spellbook['Spells'][spell_name]
                cost = spell.cost
                spell_options.append(f"{spell_name} (MP: {cost})")
            
            self._render_selection_menu("Select Spell", spell_options, selected, scroll_offset)
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
                        selected = (selected - 1) % len(spells)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(spells)
                    elif event.key == pygame.K_PAGEUP:
                        selected = max(0, selected - 10)
                    elif event.key == pygame.K_PAGEDOWN:
                        selected = min(len(spells) - 1, selected + 10)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return spells[selected]  # Return spell name
                    
                    # Update scroll to keep selection visible
                    max_visible = 3
                    if selected < scroll_offset:
                        scroll_offset = selected
                    elif selected >= scroll_offset + max_visible:
                        scroll_offset = selected - max_visible + 1
    
    def _select_skill(self, player_char, enemy):
        """Show skill selection menu and return selected skill name."""
        # Filter out passive and currently unusable equipment-dependent skills.
        skills = [name for name, skill in player_char.spellbook['Skills'].items()
                  if self._skill_available_for_selection(player_char, skill)]
        
        if not skills:
            self.combat_view.add_combat_message("No skills learned!")
            self._pause_with_events(500)
            return None
        
        selected = 0
        scroll_offset = 0
        input_armed = self._clear_pending_input()
        while True:
            # Render combat with skill menu overlay
            self._render_combat_frame(player_char, enemy, [], -1)
            skill_options = []
            for skill_name in skills:
                skill = player_char.spellbook['Skills'][skill_name]
                cost = skill.cost
                skill_options.append(f"{skill_name} (MP: {cost})")
            
            self._render_selection_menu("Select Skill", skill_options, selected, scroll_offset)
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

    def _skill_available_for_selection(self, player_char, skill) -> bool:
        """Return whether a learned skill should be shown in the combat skill list."""
        if getattr(skill, 'passive', False):
            return False

        if getattr(skill, 'name', None) == "Shield Slam":
            offhand = getattr(player_char, 'equipment', {}).get('OffHand')
            return getattr(offhand, 'subtyp', None) == "Shield"

        if getattr(skill, 'weapon', False) and player_char.is_disarmed():
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
    
    def _enemy_turn(self, player_char, enemy):
        """Handle enemy's turn (automated), delegating logic to the engine."""
        # Pre-turn: process status effects and check activity
        pre = self.engine.pre_turn()
        if pre.effects_text:
            for line in pre.effects_text.strip().split('\n'):
                if line.strip():
                    self.combat_view.add_combat_message(line)
            self._flush_result_frame(player_char, enemy)

        # If the enemy died from its own effects (poison, DOT, bleed), end turn
        if pre.died_from_effects:
            return None

        if not pre.can_act:
            self.combat_view.add_combat_message(pre.inactive_reason.strip())
            self._flush_result_frame(player_char, enemy)
            return None  # Skip turn
        
        # Render current state and pause before enemy acts (with animation updates)
        enemy_clock = pygame.time.Clock()
        for _ in range(30):  # 500ms at 60fps
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                self._handle_combat_log_scroll_event(event)
            self._flush_result_frame(player_char, enemy)
            enemy_clock.tick(60)

        # Check for forced actions (charging skills, jump)
        forced = self.engine.get_forced_action()
        if forced:
            if forced.action == "Cancelled":
                for line in forced.cancel_message.strip().split('\n'):
                    if line.strip():
                        self.combat_view.add_combat_message(line)
                self._flush_result_frame(player_char, enemy)
                return None

            enemy_name_before = enemy.name
            enemy_hp_before = enemy.health.current
            player_hp_before = player_char.health.current
            player_stun_before = bool(player_char.status_effects["Stun"].active)

            result = self.engine.execute_action(forced.action, choice=forced.choice)
            self._record_bestiary_ability_if_visible(player_char, enemy, forced.choice or forced.action)
            for line in result.message.strip().split('\n'):
                if line.strip():
                    self.combat_view.add_combat_message(line)
            self._add_new_player_stun_message(player_char, player_stun_before, result.message)

            self._flush_result_frame(player_char, enemy)

            # Check if enemy shapeshifted
            if enemy.name != enemy_name_before:
                self.combat_view.reload_enemy_sprite(enemy)

            damage_to_player = max(0, player_hp_before - player_char.health.current)
            if damage_to_player > 0:
                self._show_combat_damage_effect("player", forced.action, forced.choice, result.message, damage_to_player)
                self._flush_result_frame(player_char, enemy)
            else:
                self._show_combat_heal_text("player", max(0, player_char.health.current - player_hp_before))
            self._show_combat_heal_text("enemy", max(0, enemy.health.current - enemy_hp_before))

            if result.fled:
                return "flee"
            return None

        # Enemy AI chooses action
        action, choice = self.engine.get_enemy_action()

        if action == "Nothing":
            self.combat_view.add_combat_message(f"{enemy.name} does nothing.")
            return None

        # Record state before execution
        player_hp_before = player_char.health.current
        player_stun_before = bool(player_char.status_effects["Stun"].active)
        enemy_name_before = enemy.name
        enemy_hp_before = enemy.health.current

        # Delegate to engine (handles Smoke Screen flee, Slot Machine, Doublecast, Jump, etc.)
        slot_cb = None
        skill_obj = None
        if action == "Use Skill" and choice:
            skill_obj = enemy.spellbook.get('Skills', {}).get(choice)
            if skill_obj and skill_obj.name == "Slot Machine":
                slot_cb = lambda _u, _t: self._show_slot_machine_reveal(player_char, enemy)

        result = self.engine.execute_action(action, choice=choice, slot_machine_callback=slot_cb)
        self._record_bestiary_ability_if_visible(player_char, enemy, choice or action)
        is_smoke_screen = (
            action == "Use Skill"
            and (choice == "Smoke Screen" or getattr(skill_obj, "name", "") == "Smoke Screen")
        )
        action_fled = result.fled or bool(getattr(self.engine, "flee", False))
        if action_fled and is_smoke_screen:
            self.combat_view.hide_enemy_for_flee()

        # Display messages
        for line in result.message.strip().split('\n'):
            if line.strip():
                self.combat_view.add_combat_message(line)
        self._add_new_player_stun_message(player_char, player_stun_before, result.message)

        if is_smoke_screen:
            self._play_smoke_screen_visual(player_char, enemy, "enemy")
        else:
            self._flush_result_frame(player_char, enemy)

        # Check if enemy shapeshifted (name changed)
        if enemy.name != enemy_name_before:
            self.combat_view.reload_enemy_sprite(enemy)

        # Show damage flash if player took damage
        damage_to_player = max(0, player_hp_before - player_char.health.current)
        if damage_to_player > 0:
            self._show_combat_damage_effect("player", action, choice, result.message, damage_to_player)
            self._flush_result_frame(player_char, enemy)
        else:
            self._show_combat_heal_text("player", max(0, player_char.health.current - player_hp_before))
        self._show_combat_heal_text("enemy", max(0, enemy.health.current - enemy_hp_before))

        if action_fled:
            return "flee"

        # Render updated state and show result (with animation updates)
        result_clock = pygame.time.Clock()
        for _ in range(48):  # 800ms at 60fps
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                self._handle_combat_log_scroll_event(event)
            self._render_combat_frame(player_char, enemy, [], -1)
            pygame.display.flip()
            result_clock.tick(60)

        return None

    def _add_new_player_stun_message(self, player_char, was_stunned: bool, result_message: str) -> None:
        """Ensure newly-applied player stun is visible even when an effect omits text."""
        stun = getattr(player_char, "status_effects", {}).get("Stun")
        is_stunned = bool(getattr(stun, "active", False))
        if is_stunned and not was_stunned and "stun" not in (result_message or "").lower():
            self.combat_view.add_combat_message(f"{player_char.name} is stunned and cannot act.")
    
    def _render_combat_frame(self, player_char, enemy, actions, selected_action):
        """Render a single frame of combat."""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Render the dungeon view as background (same as exploration)
        # This is passed from dungeon_manager
        if self.dungeon_renderer and self.player_world_dict:
            try:
                self.dungeon_renderer.render_dungeon_view(player_char, self.player_world_dict)
            except Exception as e:
                # Fallback to black screen if dungeon rendering fails
                self.screen.fill((0, 0, 0))
        
        current_turn = None
        if self.engine is not None and getattr(self.engine, "attacker", None) is not None:
            current_turn = "player" if self.engine.is_player_turn() else "enemy"
        show_enemy_details = None
        if self.engine is not None and hasattr(self.engine, "show_enemy_details"):
            show_enemy_details = self.engine.show_enemy_details()
        if show_enemy_details and hasattr(player_char, "record_bestiary_enemy"):
            player_char.record_bestiary_enemy(enemy, getattr(enemy, "enemy_typ", None))

        # Render enemy in the dungeon (in front of player)
        self.combat_view.render_enemy_in_dungeon(player_char, enemy, show_enemy_details=show_enemy_details)

        # Render combat HUD overlay (action menu and combat log)
        self.combat_view.render_combat_overlay(
            player_char,
            enemy,
            actions,
            selected_action,
            current_turn=current_turn,
            show_enemy_details=show_enemy_details,
        )
        
        # Render HUD (right 1/3) with combat mode indicator
        self.hud.render_hud(player_char, combat_mode=True, enemy=enemy)

    def _record_bestiary_ability_if_visible(self, player_char, enemy, ability_name) -> None:
        if self.engine is None or not hasattr(self.engine, "show_enemy_details"):
            return
        if not self.engine.show_enemy_details():
            return
        if hasattr(player_char, "record_bestiary_ability"):
            player_char.record_bestiary_ability(enemy, ability_name)

    def _refresh_combat_background(self, player_char, enemy):
        """Render and cache the latest combat frame for popups/overlays."""
        self._render_combat_frame(player_char, enemy, [], -1)
        pygame.display.flip()
        self._combat_background = self.screen.copy()
    
    def _handle_combat_end(self, player_char, enemy, fled):
        """Handle end of combat using the engine for bookkeeping."""

        def _show_end_popup(message_text: str, *, background=None, refresh_background: bool = True) -> None:
            if refresh_background:
                self._refresh_combat_background(player_char, enemy)
            background = background or self._combat_background or self._capture_background()
            draw_background = lambda: self.screen.blit(background, (0, 0))
            from .confirmation_popup import ConfirmationPopup
            popup = ConfirmationPopup(self.presenter, message_text, show_buttons=False)
            popup.show(
                background_draw_func=draw_background,
                flush_events=True,
                require_key_release=True,
            )

        # Handle Sanctuary (player got teleported to town during combat)
        if player_char.in_town():
            player_char.effects(end=True)
            self.logger.end_battle(result="Escaped", winner=None, boss=False)
            self._persist_debug_battle_log("escaped")
            self.combat_view.reset_combat_log()
            self._combat_background = None
            return False

        # Sync engine flee state (in case player fled via UI flow)
        if fled:
            self.engine.flee = True

        pre_outcome_background = self.screen.copy()

        # Let the engine handle all bookkeeping (exp, loot, quests, kill tracking, etc.)
        outcome = self.engine.end_battle()
        self._persist_debug_battle_log(outcome.result)

        if outcome.result == "defeat":
            self._pause_with_events(900)

            _show_end_popup(
                "You have been defeated!",
                background=pre_outcome_background,
                refresh_background=False,
            )
            self.combat_view.reset_combat_log()
            self._combat_background = None
            return False

        elif outcome.result == "victory":
            # Build end messages from outcome
            end_messages = [f"Victory! {enemy.name} defeated!"]
            # Parse the outcome message for display lines
            for line in outcome.message.strip().split('\n'):
                if line.strip():
                    end_messages.append(line)

            if outcome.level_up:
                end_messages.append("\nLEVEL UP!")

            # Render final combat state and let death animation complete.
            clock = pygame.time.Clock()
            for _ in range(70):
                self._render_combat_frame(player_char, enemy, [], -1)
                pygame.display.flip()
                clock.tick(60)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
                    self._handle_combat_log_scroll_event(event)

            self._pause_with_events(900)
            _show_end_popup("\n".join(end_messages))

            if outcome.level_up:
                self.level_up_screen.show_level_up(player_char, self.game)

            self.combat_view.reset_combat_log()
            self._combat_background = None
            return True

        elif outcome.result == "flee":
            self._render_combat_frame(player_char, enemy, [], -1)
            pygame.display.flip()
            self._pause_with_events(700)

            _show_end_popup("You fled from combat!")
            self.combat_view.reset_combat_log()
            self._combat_background = None
            return False

        # Fallback
        self.combat_view.reset_combat_log()
        self._combat_background = None
        return True

    def _pause_with_events(self, duration_ms: int) -> None:
        """Pause briefly while pumping events to avoid unresponsive window."""
        pause_clock = pygame.time.Clock()
        elapsed = 0
        while elapsed < duration_ms:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                self._handle_combat_log_scroll_event(event)
            pause_clock.tick(60)
            elapsed += pause_clock.get_time()
