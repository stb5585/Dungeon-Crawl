"""Mechanics behavior for the popup menus package."""

from src.core import map_tiles
from src.core.classes import bard
from src.paths import PYGAME_ASSETS_DIR

from .base import BasePopupMenu

CHALICE_MAP_REVEALED_IMAGE_PATH = str(PYGAME_ASSETS_DIR / "key_items" / "chalice_map.png")


class SimpleListPopupMenu(BasePopupMenu):
    """Generic simple list popup for placeholders like Quests, Key Items, Specials, Class Menu."""

    def __init__(self, presenter, parent_screen, title, source_fn):
        super().__init__(presenter, parent_screen, title=title)
        self.source_fn = source_fn  # function(player_char) -> list[str]

    def build_items(self, player_char):
        raw = self.source_fn(player_char) or []
        # Handle case where raw is a callable (method) instead of a list
        if callable(raw):
            raw = raw()
        self.items = []
        for entry in raw or []:
            if (
                isinstance(entry, str)
                and entry.strip().startswith("---")
                and entry.strip().endswith("---")
            ):
                # Treat as header row
                self.items.append({"is_header": True, "text": entry})
            elif isinstance(entry, dict) and "text" in entry:
                # Entry is already a properly formatted dict (e.g., from _get_key_items_list with quantities)
                self.items.append(entry)
            else:
                if isinstance(entry, object) and not isinstance(entry, str):
                    self.items.append(
                        {
                            "is_header": False,
                            "text": getattr(entry, "name", str(entry)),
                            "value": entry,
                        }
                    )
                else:
                    self.items.append({"is_header": False, "text": str(entry), "value": entry})
        self.selected_index = 0
        self.scroll_offset = 0

    def item_display_text(self, item):
        if isinstance(item, dict):
            return item.get("text", "")
        return str(item)

    def draw_details(self, player_char):
        """Override to handle abilities/skills specially - don't show description in attrs."""
        item = self.items[self.selected_index] if self.items else None
        x = self.details_rect.left + 16
        y = self.details_rect.top + 12

        if item is None:
            self.screen.blit(self.normal_font.render("No items", True, self.GRAY), (x, y))
            return

        # Extract header/value metadata when present
        is_header = isinstance(item, dict) and item.get("is_header")
        value = item.get("value") if isinstance(item, dict) else item
        text_label = item.get("text") if isinstance(item, dict) else None

        if is_header:
            header_text = self.large_font.render(text_label or "", True, self.GOLD)
            self.screen.blit(header_text, (x, y))
            return

        if self._can_render_item_icon(value):
            self.draw_item_detail_layout(value, hide_zero_value=True, hide_zero_weight=True)
            return

        # Name
        name = getattr(value, "name", text_label if text_label else str(value))
        name_text = self.large_font.render(name, True, self.WHITE)
        self.screen.blit(name_text, (x, y))
        y += name_text.get_height() + 8

        # For abilities, skip showing description in attrs since we'll show it wrapped below
        # Custom details hook (will show description wrapped)
        self.draw_details_extra(player_char, value, x, y)

    def draw_details_extra(self, player_char, item, x, y):
        # Render description text for abilities if present; otherwise show a fallback
        desc = getattr(item, "description", None) or ""
        max_width = self.details_rect.width - 32

        if desc:
            y = self._draw_wrapped_detail_text(str(desc), x, y, max_width)
        else:
            text = self.normal_font.render("No description available.", True, self.GRAY)
            self.screen.blit(text, (x, y))
            y += self.line_height

        modifications = tuple(getattr(item, "presentation_modifications", ()) or ())
        if modifications:
            y += 8
            heading = self.normal_font.render("Modifications", True, self.GOLD)
            self.screen.blit(heading, (x, y))
            y += self.line_height
            for modification in modifications:
                name = str(getattr(modification, "name", "Modification") or "Modification")
                description = str(getattr(modification, "description", "") or "")
                y = self._draw_wrapped_detail_text(
                    f"{name}: {description}",
                    x,
                    y,
                    max_width,
                    color=self.LIGHT_GRAY,
                )
                y += 4

        # Add spacing
        y += 8

        # Show sub-type if available
        subtyp = getattr(item, "subtyp", None)
        if subtyp:
            subtyp_text = self.normal_font.render(f"Type: {subtyp}", True, self.LIGHT_GRAY)
            self.screen.blit(subtyp_text, (x, y))
            y += self.line_height

        # Show mana cost or "Passive" only for abilities (items with a 'cost' attribute)
        # This avoids showing mana cost for regular items like Key Items
        is_passive = getattr(item, "passive", False)
        has_cost_attr = hasattr(item, "cost")

        if is_passive or has_cost_attr:
            if is_passive:
                cost_text = self.normal_font.render("Passive", True, self.LIGHT_GRAY)
            else:
                cost = getattr(item, "cost", None)
                if cost is not None:
                    cost_text = self.normal_font.render(f"Mana Cost: {cost}", True, self.LIGHT_GRAY)
                else:
                    cost_text = self.normal_font.render("Mana Cost: —", True, self.LIGHT_GRAY)
            self.screen.blit(cost_text, (x, y))

    def _draw_wrapped_detail_text(self, text, x, y, max_width, *, color=None):
        """Draw wrapped ability-card text and return the next vertical position."""
        words = str(text).split()
        line = ""
        color = color or self.WHITE
        for word in words:
            candidate = f"{line} {word}".strip()
            if self.normal_font.size(candidate)[0] <= max_width:
                line = candidate
                continue
            if line:
                surface = self.normal_font.render(line, True, color)
                self.screen.blit(surface, (x, y))
                y += self.line_height
            line = word
        if line:
            surface = self.normal_font.render(line, True, color)
            self.screen.blit(surface, (x, y))
            y += self.line_height
        return y

    def on_select(self, player_char, item):
        value = item.get("value") if isinstance(item, dict) else item
        if getattr(value, "exploration_cast", False) and callable(getattr(value, "cast_out", None)):
            from . import ConfirmationPopup

            menu_background = self._capture_menu_surface(player_char)
            if player_char.mana.current < int(getattr(value, "cost", 0) or 0):
                notice = ConfirmationPopup(
                    self.presenter,
                    f"{player_char.name} does not have enough mana.",
                    show_buttons=False,
                )
                notice.show(
                    background_draw_func=lambda: self.screen.blit(
                        menu_background,
                        (0, 0),
                    ),
                    flush_events=True,
                    require_key_release=True,
                )
                return None
            confirm = ConfirmationPopup(
                self.presenter,
                f"Cast {value.name}?",
                show_buttons=True,
            )
            if not confirm.show(
                background_draw_func=lambda: self.screen.blit(
                    menu_background,
                    (0, 0),
                ),
                flush_events=True,
                require_key_release=True,
            ):
                return None
            result = value.cast_out(player_char)
            result_popup = ConfirmationPopup(
                self.presenter,
                result,
                show_buttons=False,
            )
            result_popup.show(
                background_draw_func=lambda: self.screen.blit(
                    menu_background,
                    (0, 0),
                ),
                flush_events=True,
                require_key_release=True,
            )
            return None
        if getattr(value, "name", "") == "Chalice Map":
            try:
                map_tiles.reveal_chalice_map_on_inspect(player_char, value)
                progress = map_tiles.get_chalice_progress(player_char) or {}
                if progress.get("Revealed"):
                    self.presenter.show_message(
                        "Hidden ink blooms across the parchment, revealing the altar location on the sixth floor.",
                        title="Chalice Map",
                        image_path=CHALICE_MAP_REVEALED_IMAGE_PATH,
                        split_layout=True,
                    )
                elif progress.get("Adventurer"):
                    self.presenter.show_message(
                        "The map's markings are faint. Keep inspecting it to draw out the hidden ink.",
                        title="Chalice Map",
                        split_layout=True,
                    )
                else:
                    self.presenter.show_message(
                        "The map is too faded to read. You need another clue before its markings can be revealed.",
                        title="Chalice Map",
                        split_layout=True,
                    )
            except Exception:
                pass
            return None
        return ("list_item_selected", item)


class JumpModsPopupMenu(BasePopupMenu):
    """Popup menu for toggling Jump ability modifications."""

    MOD_DESCRIPTIONS = {
        "Crit": "Increases critical factor but reduces weapon damage.",
        "Thrust": "After landing, thrust with reduced weapon damage if the target survives.",
        "Defend": "Increased damage reduction while preparing to Jump.",
        "Rend": "Chance to apply Bleed, dealing damage over time.",
        "Quake": "Chance to stun the enemy upon landing.",
        "Acrobat": "Gain an evasion bonus while preparing to Jump.",
        "Dragon's Fury": "Deals additional random elemental damage.",
        "Soaring Strike": "Takes two turns to charge, but deals increased damage.",
        "Quick Dive": "Removes charge time but reduces weapon damage.",
        "Retribution": "Taking damage while charging boosts the Jump damage.",
        "Unstoppable": "Jump cannot be interrupted once started.",
        "Recover": "Regain a small amount of health and mana upon landing.",
        "Skyfall": "Additional smaller hits fall on the target after landing.",
    }

    def __init__(self, presenter, parent_screen, title="Jump Modifications"):
        super().__init__(presenter, parent_screen, title=title)
        self.jump_skill = None

    def _get_jump_skill(self, player_char):
        skills = getattr(player_char, "spellbook", {}).get("Skills", {})
        if "Jump" in skills:
            return skills["Jump"]
        for skill in skills.values():
            if getattr(skill, "name", "") == "Jump":
                return skill
        return None

    def build_items(self, player_char):
        self.jump_skill = self._get_jump_skill(player_char)
        self.items = []

        if not self.jump_skill or not hasattr(self.jump_skill, "modifications"):
            self.items.append({"is_header": True, "text": "Jump not learned"})
            self.selected_index = 0
            self.scroll_offset = 0
            return

        # Show active/max count in header
        active_count = (
            self.jump_skill.get_active_count()
            if hasattr(self.jump_skill, "get_active_count")
            else 0
        )
        max_count = (
            self.jump_skill.get_max_active_modifications(player_char)
            if hasattr(self.jump_skill, "get_max_active_modifications")
            else 99
        )
        header_text = f"Toggle Modifications ({active_count}/{max_count} active)"
        self.items.append({"is_header": True, "text": header_text})

        # Only show unlocked modifications
        unlocked_mods = (
            self.jump_skill.get_unlocked_modifications()
            if hasattr(self.jump_skill, "get_unlocked_modifications")
            else list(self.jump_skill.modifications.keys())
        )

        for mod_name in unlocked_mods:
            active = self.jump_skill.modifications.get(mod_name, False)
            prefix = "[X]" if active else "[ ]"
            self.items.append(
                {
                    "is_header": False,
                    "text": f"{prefix} {mod_name}",
                    "value": mod_name,
                }
            )

        self.selected_index = 1 if len(self.items) > 1 else 0
        self.scroll_offset = 0

    def item_display_text(self, item):
        if isinstance(item, dict):
            return item.get("text", "")
        return str(item)

    def draw_details(self, player_char):
        item = self.items[self.selected_index] if self.items else None
        x = self.details_rect.left + 16
        y = self.details_rect.top + 12

        if item is None:
            self.screen.blit(self.normal_font.render("No items", True, self.GRAY), (x, y))
            return

        is_header = isinstance(item, dict) and item.get("is_header")
        value = item.get("value") if isinstance(item, dict) else item
        text_label = item.get("text") if isinstance(item, dict) else None

        if is_header:
            header_text = self.large_font.render(text_label or "", True, self.GOLD)
            self.screen.blit(header_text, (x, y))
            return

        mod_name = str(value)
        active = False
        if self.jump_skill and hasattr(self.jump_skill, "modifications"):
            active = self.jump_skill.modifications.get(mod_name, False)

        name_text = self.large_font.render(mod_name, True, self.WHITE)
        self.screen.blit(name_text, (x, y))
        y += name_text.get_height() + 8

        status_text = self.normal_font.render(
            f"Status: {'Active' if active else 'Inactive'}", True, self.LIGHT_GRAY
        )
        self.screen.blit(status_text, (x, y))
        y += self.line_height + 4

        # Show unlock requirement info
        if self.jump_skill and hasattr(self.jump_skill, "unlock_requirements"):
            req = self.jump_skill.unlock_requirements.get(mod_name, {})
            req_type = req.get("type", "")
            req_val = req.get("requirement")

            if req_type == "lancer_level":
                unlock_str = f"Unlocked: Lancer Level {req_val}"
            elif req_type == "dragoon_level":
                unlock_str = f"Unlocked: Dragoon Level {req_val}"
            elif req_type == "boss":
                unlock_str = f"Unlocked by defeating {req_val}"
            elif req_type == "item":
                unlock_str = f"Unlocked by finding {req_val}"
            else:
                unlock_str = "Initial modification"

            unlock_text = self.normal_font.render(unlock_str, True, self.GOLD)
            self.screen.blit(unlock_text, (x, y))
            y += self.line_height + 8

        desc = self.MOD_DESCRIPTIONS.get(mod_name, "")
        if desc:
            max_width = self.details_rect.width - 32
            words = desc.split()
            line = ""
            for w in words:
                test = f"{line} {w}".strip()
                if self.normal_font.size(test)[0] <= max_width:
                    line = test
                else:
                    self.screen.blit(self.normal_font.render(line, True, self.WHITE), (x, y))
                    y += self.line_height
                    line = w
            if line:
                self.screen.blit(self.normal_font.render(line, True, self.WHITE), (x, y))

    def on_select(self, player_char, item):
        if not self.jump_skill or not hasattr(self.jump_skill, "modifications"):
            return None
        if isinstance(item, dict) and item.get("is_header"):
            return None

        mod_name = item.get("value") if isinstance(item, dict) else str(item)
        current = self.jump_skill.modifications.get(mod_name, False)

        # Toggle the modification
        result = self.jump_skill.set_modification(mod_name, not current, player_char)

        # Handle the new tuple return format
        if isinstance(result, tuple):
            success, error_msg = result
            if not success and error_msg:
                # Could show error popup here if desired
                pass  # For now, just don't toggle if it failed

        self.build_items(player_char)
        return None


class CompositionPopupMenu(BasePopupMenu):
    """Select an inherent Bard composition for the equipped instrument."""

    def __init__(self, presenter, parent_screen, title="Compose Song"):
        super().__init__(presenter, parent_screen, title=title)
        self.last_message = ""

    def build_items(self, player_char):
        available = bard.available_compositions(player_char)
        self.items = [
            {
                "is_header": False,
                "text": song,
                "value": song,
                "available": song in available,
                "instrument": instrument,
            }
            for song, (instrument, _sheet) in bard.COMPOSITIONS.items()
        ]
        self.selected_index = 0
        self.scroll_offset = 0

    def item_display_text(self, item):
        if not isinstance(item, dict):
            return str(item)
        suffix = "" if item.get("available") else f" - needs {item.get('instrument')}"
        return f"{item.get('text', '')}{suffix}"

    def draw_details(self, player_char):
        del player_char
        item = self.items[self.selected_index] if self.items else None
        x = self.details_rect.left + 16
        y = self.details_rect.top + 12
        if not isinstance(item, dict):
            return
        song = str(item.get("value", ""))
        self.screen.blit(self.large_font.render(song, True, self.WHITE), (x, y))
        y += self.large_font.get_height() + 10
        y = self._draw_wrapped_lines(
            str(bard.SONGS.get(song, {}).get("description", "")),
            x,
            y,
            self.details_rect.width - 32,
        )
        status = "Ready to compose" if item.get("available") else "Matching instrument required"
        y += 8
        self.screen.blit(
            self.normal_font.render(
                f"Instrument: {item.get('instrument', '')}",
                True,
                self.LIGHT_GRAY,
            ),
            (x, y),
        )
        y += self.line_height
        self.screen.blit(self.normal_font.render(status, True, self.GOLD), (x, y))
        if self.last_message:
            self._draw_wrapped_lines(
                self.last_message.strip(),
                x,
                y + self.line_height + 8,
                self.details_rect.width - 32,
                color=self.GREEN,
            )

    def on_select(self, player_char, item):
        if not isinstance(item, dict):
            return None
        _success, self.last_message = bard.compose_sheet_music(
            player_char,
            str(item.get("value", "")),
        )
        return None


class TotemAspectsPopupMenu(BasePopupMenu):
    """Popup menu for selecting active Totem aspects."""

    def __init__(self, presenter, parent_screen, title="Totem Aspects"):
        super().__init__(presenter, parent_screen, title=title)
        self.totem_skill = None
        self.spirit_skill = None

    def _get_totem_skill(self, player_char):
        skills = getattr(player_char, "spellbook", {}).get("Skills", {})
        if "Totem" in skills:
            return skills["Totem"]
        for skill in skills.values():
            if getattr(skill, "name", "") == "Totem":
                return skill
        return None

    def build_items(self, player_char):
        self.totem_skill = self._get_totem_skill(player_char)
        self.spirit_skill = next(
            (
                skill
                for skill in getattr(player_char, "spellbook", {}).get("Skills", {}).values()
                if getattr(skill, "name", "") == "Spirit Animal"
            ),
            None,
        )
        self.items = []

        if not self.totem_skill or not hasattr(self.totem_skill, "get_unlocked_aspects"):
            self.items.append({"is_header": True, "text": "Totem not learned"})
            self.selected_index = 0
            self.scroll_offset = 0
            return

        active = getattr(self.totem_skill, "active_aspect", "")
        header_text = f"Active Aspect: {active}" if active else "Active Aspect: None"
        self.items.append({"is_header": True, "text": header_text})

        unlocked = self.totem_skill.get_unlocked_aspects(player_char)
        for aspect in unlocked:
            prefix = "[X]" if aspect == active else "[ ]"
            self.items.append(
                {
                    "is_header": False,
                    "text": f"{prefix} {aspect}",
                    "value": aspect,
                    "kind": "aspect",
                }
            )

        if self.spirit_skill is not None:
            chosen = str(getattr(player_char, "spirit_animal", "Bear"))
            self.items.append({"is_header": True, "text": f"Spirit Animal: {chosen}"})
            for animal in self.spirit_skill.ANIMALS:
                prefix = "[X]" if animal == chosen else "[ ]"
                self.items.append(
                    {
                        "is_header": False,
                        "text": f"{prefix} {animal}",
                        "value": animal,
                        "kind": "spirit",
                    }
                )

        self.selected_index = 1 if len(self.items) > 1 else 0
        self.scroll_offset = 0

    def item_display_text(self, item):
        if isinstance(item, dict):
            return item.get("text", "")
        return str(item)

    def draw_details(self, player_char):
        item = self.items[self.selected_index] if self.items else None
        x = self.details_rect.left + 16
        y = self.details_rect.top + 12

        if item is None:
            self.screen.blit(self.normal_font.render("No items", True, self.GRAY), (x, y))
            return

        is_header = isinstance(item, dict) and item.get("is_header")
        value = item.get("value") if isinstance(item, dict) else item
        text_label = item.get("text") if isinstance(item, dict) else None

        if is_header:
            header_text = self.large_font.render(text_label or "", True, self.GOLD)
            self.screen.blit(header_text, (x, y))
            return

        aspect = str(value)
        name_text = self.large_font.render(aspect, True, self.WHITE)
        self.screen.blit(name_text, (x, y))
        y += name_text.get_height() + 8

        if self.totem_skill and hasattr(self.totem_skill, "aspects"):
            aspect_data = self.totem_skill.aspects.get(aspect, {})
            cost = aspect_data.get("cost")
            if cost is not None:
                cost_text = self.normal_font.render(f"Mana Cost: {cost}", True, self.LIGHT_GRAY)
                self.screen.blit(cost_text, (x, y))
                y += self.line_height + 6

            desc = aspect_data.get("description", "")
            if desc:
                max_width = self.details_rect.width - 32
                words = desc.split()
                line = ""
                for w in words:
                    test = f"{line} {w}".strip()
                    if self.normal_font.size(test)[0] <= max_width:
                        line = test
                    else:
                        self.screen.blit(self.normal_font.render(line, True, self.WHITE), (x, y))
                        y += self.line_height
                        line = w
                if line:
                    self.screen.blit(self.normal_font.render(line, True, self.WHITE), (x, y))

    def on_select(self, player_char, item):
        if isinstance(item, dict) and item.get("is_header"):
            return None

        if isinstance(item, dict) and item.get("kind") == "spirit":
            player_char.spirit_animal = str(item["value"])
            self.build_items(player_char)
            return None
        if not self.totem_skill or not hasattr(self.totem_skill, "set_active_aspect"):
            return None

        aspect = item.get("value") if isinstance(item, dict) else str(item)
        result = self.totem_skill.set_active_aspect(aspect)
        if isinstance(result, tuple):
            success, _ = result
            if not success:
                return None

        self.build_items(player_char)
        return None
