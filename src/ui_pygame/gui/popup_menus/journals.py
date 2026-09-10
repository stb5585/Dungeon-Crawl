"""Journals behavior for the popup menus package."""

import pygame

from src.core import enemies, items

from .base import BasePopupMenu


class QuestPopupMenu(BasePopupMenu):
    """Quest-specific popup that shows quest details."""

    def __init__(self, presenter, parent_screen):
        super().__init__(presenter, parent_screen, title="Quests")
        # Make quest popup larger for long descriptions
        self.popup_rect = pygame.Rect(
            int(self.width * 0.05),
            int(self.height * 0.08),
            int(self.width * 0.9),
            int(self.height * 0.82),
        )
        self.list_rect = pygame.Rect(
            self.popup_rect.left + 24,
            self.popup_rect.top + 72,
            int(self.popup_rect.width * 0.33),
            self.popup_rect.height - 120,
        )
        self.details_rect = pygame.Rect(
            self.popup_rect.left + int(self.popup_rect.width * 0.35),
            self.popup_rect.top + 72,
            int(self.popup_rect.width * 0.6) - 32,
            self.popup_rect.height - 120,
        )

    def draw_popup(self, player_char):
        super().draw_popup(player_char)

    def build_items(self, player_char):
        """Build list of quest objects from quest_dict."""
        self.items = []
        active_items = []
        completed_items = []  # completed but not turned in
        turned_in_items = []
        quest_dict = getattr(player_char, "quest_dict", {})

        if not quest_dict:
            return

        # Store quest data as tuples: (display_name, quest_type, quest_name, quest_data)
        for quest_type, quests_by_type in quest_dict.items():
            if quest_type == "Bounty":
                # Bounty quests: {name: [bounty_data, count, completed]}
                for quest_name, quest_info in quests_by_type.items():
                    if isinstance(quest_info, list) and len(quest_info) >= 3:
                        bounty_data, count, completed = quest_info[0], quest_info[1], quest_info[2]
                        entry = (
                            f"[{quest_type}] {quest_name}",
                            quest_type,
                            quest_name,
                            {"bounty_data": bounty_data, "count": count, "completed": completed},
                        )
                        if completed:
                            completed_items.append(entry)
                        else:
                            active_items.append(entry)
            else:
                # Main/Side quests: check if it's nested by level or flat structure
                for key, value in quests_by_type.items():
                    if isinstance(value, dict):
                        # Check if this looks like quest data (has quest properties) or nested structure
                        if "Type" in value or "Who" in value or "What" in value:
                            # This is quest data directly - flat structure
                            quest_name = key
                            quest_data = value
                            completed = quest_data.get("Completed", False)
                            turned_in = quest_data.get("Turned In", False)
                            display_name = f"[{quest_type}] {quest_name}"
                            entry = (display_name, quest_type, quest_name, quest_data)
                            if turned_in:
                                turned_in_items.append(entry)
                            elif completed:
                                completed_items.append(entry)
                            else:
                                active_items.append(entry)
                        else:
                            # This is a nested structure (level -> quests)
                            for quest_name, quest_data in value.items():
                                completed = quest_data.get("Completed", False)
                                turned_in = quest_data.get("Turned In", False)
                                display_name = f"[{quest_type}] {quest_name}"
                                entry = (display_name, quest_type, quest_name, quest_data)
                                if turned_in:
                                    turned_in_items.append(entry)
                                elif completed:
                                    completed_items.append(entry)
                                else:
                                    active_items.append(entry)

        self.items = active_items
        if completed_items:
            self.items.append({"is_header": True, "text": "Completed Quests"})
            self.items.extend(completed_items)
        if turned_in_items:
            self.items.append({"is_header": True, "text": "Turned In"})
            self.items.extend(turned_in_items)

        if not self.items:
            self.items = [("No quests available", None, None, None)]

        self.selected_index = 0
        self.scroll_offset = 0

    def item_display_text(self, item):
        """Return display name from tuple."""
        if isinstance(item, dict) and item.get("is_header"):
            return item.get("text", "")
        if isinstance(item, tuple):
            return item[0]
        return str(item)

    def draw_details(self, player_char):
        """Override to show quest details instead of generic item attributes."""
        item = self.items[self.selected_index] if self.items else None
        x = self.details_rect.left + 16
        y = self.details_rect.top + 12

        if item is None:
            self.screen.blit(self.normal_font.render("No quests", True, self.GRAY), (x, y))
            return

        if isinstance(item, dict) and item.get("is_header"):
            self.screen.blit(self.normal_font.render(item.get("text", ""), True, self.GRAY), (x, y))
            return

        if not isinstance(item, tuple) or item[1] is None:
            # No quest selected or no quests available
            self.screen.blit(self.normal_font.render(str(item[0]), True, self.GRAY), (x, y))
            return

        display_name, quest_type, quest_name, quest_data = item

        # Quest name as header
        name_text = self.large_font.render(quest_name, True, self.GOLD)
        self.screen.blit(name_text, (x, y))
        y += name_text.get_height() + 8

        if quest_type == "Bounty":
            self._draw_bounty_details(quest_data, x, y)
        else:
            self._draw_quest_details(player_char, quest_data, x, y)

    def _draw_bounty_details(self, quest_data, x, y):
        """Draw bounty quest details."""
        bounty_data = quest_data.get("bounty_data", {})
        count = quest_data.get("count", 0)
        completed = quest_data.get("completed", False)

        # Target - handle both enemy object and string
        if "enemy" in bounty_data:
            enemy = bounty_data["enemy"]
            if hasattr(enemy, "name"):
                target = enemy.name
            else:
                target = str(enemy)
        else:
            target = "Unknown"

        description = self._quest_description_text(bounty_data)
        if description:
            y = self._render_wrapped_attribute(
                "Description", description, x, y, self.quest_description_width()
            )
            y += self.line_height // 2

        lines = [
            f"Target: {target}",
            f"Required: {bounty_data.get('num', 1)}",
            f"Defeated: {count}",
            "",
            f"Status: {'Complete' if completed else 'In Progress'}",
            "",
        ]

        for line in lines:
            text = self.normal_font.render(line, True, self.WHITE)
            self.screen.blit(text, (x, y))
            y += self.line_height

        text = self.normal_font.render("Rewards:", True, self.GOLD)
        self.screen.blit(text, (x, y))
        y += self.line_height

        y = self._draw_reward_line(f"{bounty_data.get('gold', 0)} Gold", "Gold", x, y)
        y += self.line_height

        y = self._draw_reward_line(f"{bounty_data.get('exp', 0)} Experience", None, x, y)
        y += self.line_height

        reward = bounty_data.get("reward")
        if reward:
            reward_item = None
            reward_name = "Unknown Item"
            try:
                reward_item = reward() if callable(reward) else reward
                reward_name = getattr(reward_item, "name", str(reward_item))
            except Exception:
                reward_name = getattr(reward, "__name__", "Unknown Item")
            self._draw_reward_line(reward_name, reward_item, x, y)

    def _quest_description_text(self, quest_data) -> str:
        if not isinstance(quest_data, dict):
            return ""
        for key in ("Description", "Help Text", "Start Text", "End Text", "description"):
            text = quest_data.get(key)
            if text:
                return " ".join(str(text).split())
        return ""

    def quest_description_width(self) -> int:
        return max(260, min(self.details_rect.width - 140, self.details_rect.width * 2 // 3))

    def _draw_quest_details(self, player_char, quest_data, x, y):
        """Draw regular quest details."""
        if not isinstance(quest_data, dict):
            return

        # Quest type
        quest_type = quest_data.get("Type", "Unknown")
        text = self.normal_font.render(f"Type: {quest_type}", True, self.WHITE)
        self.screen.blit(text, (x, y))
        y += self.line_height

        description = self._quest_description_text(quest_data)
        if description:
            y = self._render_wrapped_attribute(
                "Description", description, x, y, self.quest_description_width()
            )
            y += self.line_height // 2

        # Quest objective
        if quest_type == "Defeat":
            what = quest_data.get("What", "Unknown")
            total = quest_data.get("Total", 1)
            objective = f"Defeat: {what}" if total == 1 else f"Defeat: {what} ({total})"
            text = self.normal_font.render(objective, True, self.WHITE)
            self.screen.blit(text, (x, y))
            y += self.line_height
        elif quest_type == "Collect":
            what = quest_data.get("What")

            # Resolve a readable target name and aliases for progress matching.
            item_name = None
            target_names = set()
            target_classes = set()

            if isinstance(what, str):
                if what == "Relics":
                    item_name = "Relics"
                    target_names.add("Relics")
                    target_classes.add("Relics")
                else:
                    target_names.add(what)
                    target_classes.add(what)
                    item_cls = getattr(items, what, None)
                    if item_cls and callable(item_cls):
                        try:
                            item_obj = item_cls()
                            item_name = getattr(item_obj, "name", what)
                            target_names.add(item_name)
                            target_classes.add(item_cls.__name__)
                        except Exception:
                            item_name = what
                    else:
                        item_name = what
            elif callable(what):
                try:
                    item_obj = what()
                    item_name = getattr(item_obj, "name", getattr(what, "__name__", str(what)))
                except Exception:
                    item_name = getattr(what, "__name__", str(what))
                target_names.add(item_name)
                target_classes.add(getattr(what, "__name__", item_name))
            elif hasattr(what, "name"):
                item_name = what.name
                target_names.add(item_name)
                target_classes.add(what.__class__.__name__)
            else:
                item_name = str(what)
                target_names.add(item_name)
                target_classes.add(item_name)

            total = quest_data.get("Total", 1)
            text = self.normal_font.render(f"Collect: {item_name}", True, self.WHITE)
            self.screen.blit(text, (x, y))
            y += self.line_height

            # Progress (parity with bounty-style visibility).
            if isinstance(what, str) and what == "Relics":
                relics = ["Triangulus", "Quadrata", "Hexagonum", "Luna", "Polaris", "Infinitas"]
                current = sum(1 for relic in relics if relic in player_char.special_inventory)
            else:
                current = 0
                for inventory_name in ("special_inventory", "inventory"):
                    inventory = getattr(player_char, inventory_name, {})
                    for key, item_list in inventory.items():
                        if not item_list:
                            continue
                        sample = item_list[0]
                        sample_name = getattr(sample, "name", key)
                        sample_class = sample.__class__.__name__
                        if (
                            key in target_names
                            or sample_name in target_names
                            or sample_class in target_classes
                        ):
                            current += len(item_list)

            displayed_current = total if quest_data.get("Turned In", False) else current
            text = self.normal_font.render(
                f"Collected: {displayed_current}/{total}",
                True,
                self.WHITE,
            )
            self.screen.blit(text, (x, y))
            y += self.line_height
        elif quest_type == "Locate":
            what = quest_data.get("What", "Unknown")
            text = self.normal_font.render(f"Locate: {what}", True, self.WHITE)
            self.screen.blit(text, (x, y))
            y += self.line_height

        y += self.line_height // 2

        # Status
        completed = quest_data.get("Completed", False)
        turned_in = quest_data.get("Turned In", False)
        if turned_in:
            status = "Turned In"
        elif completed:
            status = "Complete - Ready to Turn In"
        else:
            status = "In Progress"
        text = self.normal_font.render(
            f"Status: {status}", True, self.GOLD if completed and not turned_in else self.WHITE
        )
        self.screen.blit(text, (x, y))
        y += self.line_height * 1.5

        # Rewards
        text = self.normal_font.render("Rewards:", True, self.GOLD)
        self.screen.blit(text, (x, y))
        y += self.line_height

        exp = quest_data.get("Experience", 0)
        if exp:
            y = self._draw_reward_line(f"{exp} Experience", None, x, y)
            y += self.line_height

        reward = quest_data.get("Reward")
        reward_num = quest_data.get("Reward Number", 0)
        if reward:
            if isinstance(reward, list) and len(reward) > 0 and reward[0] == "Gold":
                y = self._draw_reward_line(f"{reward_num} Gold", "Gold", x, y)
                y += self.line_height
            elif isinstance(reward, list):
                for r in reward:
                    # Handle item classes/functions
                    name = None
                    item_obj = None

                    # Skip strings that are keywords like 'Gold'
                    if isinstance(r, str):
                        item_cls = getattr(items, r, None)
                        if callable(item_cls):
                            try:
                                item_obj = item_cls()
                                name = getattr(item_obj, "name", r)
                            except Exception:
                                name = r
                        else:
                            name = r

                    # Check if it's a class (type)
                    elif isinstance(r, type):
                        # It's a class, use __name__
                        name = r.__name__
                        try:
                            item_obj = r()
                            name = getattr(item_obj, "name", name)
                        except Exception:
                            pass
                    elif hasattr(r, "name"):
                        # It's an instance with a name attribute
                        name = r.name
                        item_obj = r
                    elif callable(r):
                        # It's callable but not a class, try to instantiate
                        try:
                            instance = r()
                            name = getattr(
                                instance, "name", r.__name__ if hasattr(r, "__name__") else None
                            )
                            item_obj = instance
                        except Exception:
                            name = r.__name__ if hasattr(r, "__name__") else None

                    # Last resort
                    if name is None:
                        name = "Unknown Item"

                    y = self._draw_reward_line(name, item_obj, x, y)
                    y += self.line_height

    def _draw_reward_line(self, text: str, icon_subject, x: int, y: int) -> int:
        icon_size = min(18, max(14, self.line_height - 6))
        text_x = x + 16
        if icon_subject is not None:
            icon = self.icon_manager.get_icon(icon_subject)
            icon_rect = pygame.Rect(
                text_x, y + max(0, (self.line_height - icon_size) // 2), icon_size, icon_size
            )
            self.screen.blit(pygame.transform.smoothscale(icon, icon_rect.size), icon_rect)
            text_x = icon_rect.right + 8
        rendered = self.normal_font.render(str(text), True, self.WHITE)
        self.screen.blit(rendered, (text_x, y))
        return y

    def _wrap_text(self, text, max_width):
        """Wrap text to fit within max_width pixels."""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if self.small_font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def on_select(self, player_char, item):
        """Quests are view-only for now."""
        return None  # Keep menu open


class BestiaryPopupMenu(BasePopupMenu):
    """Read-only per-save bestiary sourced from seen and defeated enemy records."""

    _enemy_class_index: dict[str, type[enemies.Enemy]] | None = None

    def __init__(self, presenter, parent_screen):
        super().__init__(presenter, parent_screen, title="Bestiary")
        self._enemy_cache: dict[str, enemies.Enemy | None] = {}
        self._hint_cache: dict[tuple[str, bool], tuple[list[str], list[str]]] = {}
        self.summary_text = "Seen: 0 | Defeated: 0 | Detailed: 0"
        self.popup_rect = pygame.Rect(
            int(self.width * 0.05),
            int(self.height * 0.08),
            int(self.width * 0.9),
            int(self.height * 0.82),
        )
        self.list_rect = pygame.Rect(
            self.popup_rect.left + 24,
            self.popup_rect.top + 72,
            int(self.popup_rect.width * 0.34),
            self.popup_rect.height - 120,
        )
        self.details_rect = pygame.Rect(
            self.popup_rect.left + int(self.popup_rect.width * 0.37),
            self.popup_rect.top + 72,
            int(self.popup_rect.width * 0.58) - 32,
            self.popup_rect.height - 120,
        )

    @staticmethod
    def _record_details_unlocked(record: dict) -> bool:
        if not isinstance(record, dict):
            return False
        if record.get("details_unlocked") is True:
            return True
        detail_keys = {
            "difficulty_level",
            "level",
            "pro_level",
            "resistances",
            "known_abilities",
            "features",
            "immunities",
        }
        return any(key in record for key in detail_keys)

    def build_items(self, player_char):
        kill_dict = getattr(player_char, "kill_dict", {}) or {}
        bestiary = getattr(player_char, "bestiary", {}) or {}
        entries_by_name = {}

        if isinstance(bestiary, dict):
            for enemy_name, record in bestiary.items():
                if not isinstance(record, dict):
                    continue
                display_name = str(record.get("name") or enemy_name or "").strip()
                if not display_name:
                    continue
                try:
                    seen_count = max(0, int(record.get("seen_count", 0) or 0))
                except (TypeError, ValueError):
                    seen_count = 0
                entries_by_name[display_name] = {
                    "is_header": False,
                    "enemy_name": display_name,
                    "enemy_type": str(record.get("type") or "Unknown"),
                    "seen_count": seen_count,
                    "count": 0,
                    "details_unlocked": self._record_details_unlocked(record),
                }

        for enemy_type, enemies_by_name in kill_dict.items():
            if not isinstance(enemies_by_name, dict):
                continue
            for enemy_name, count in enemies_by_name.items():
                try:
                    defeated_count = int(count)
                except (TypeError, ValueError):
                    defeated_count = 0
                if defeated_count <= 0:
                    continue
                display_name = str(enemy_name)
                entry = entries_by_name.setdefault(
                    display_name,
                    {
                        "is_header": False,
                        "enemy_name": display_name,
                        "enemy_type": str(enemy_type),
                        "seen_count": 0,
                        "count": 0,
                        "details_unlocked": False,
                    },
                )
                entry["enemy_type"] = str(entry.get("enemy_type") or enemy_type or "Unknown")
                if entry["enemy_type"] == "Unknown":
                    entry["enemy_type"] = str(enemy_type)
                entry["count"] = defeated_count

        entries = []
        for entry in entries_by_name.values():
            defeated_count = int(entry.get("count", 0) or 0)
            seen_count = int(entry.get("seen_count", 0) or 0)
            entry["display_seen_count"] = (
                seen_count
                if seen_count > 0
                else max(1 if defeated_count > 0 else 0, defeated_count)
            )
            entry["text"] = (
                f"{entry['enemy_name']} x{defeated_count}"
                if defeated_count > 0
                else f"{entry['enemy_name']} Seen"
            )
            entries.append(entry)

        seen_entries = len(entries)
        defeated_entries = sum(1 for entry in entries if int(entry.get("count", 0) or 0) > 0)
        detailed_entries = sum(1 for entry in entries if entry.get("details_unlocked"))
        self.summary_text = (
            f"Seen: {seen_entries} | Defeated: {defeated_entries} | Detailed: {detailed_entries}"
        )

        self.items = sorted(entries, key=lambda item: item["enemy_name"]) or [
            {"is_header": False, "text": "No bestiary entries", "empty": True}
        ]
        self.selected_index = 0
        self.scroll_offset = 0

    def item_display_text(self, item):
        if isinstance(item, dict):
            return item.get("text", "")
        return str(item)

    @staticmethod
    def observed_record(player_char, enemy_name: str) -> dict:
        bestiary = getattr(player_char, "bestiary", {}) or {}
        record = bestiary.get(enemy_name, {})
        return record if isinstance(record, dict) else {}

    def draw_popup(self, player_char):
        super().draw_popup(player_char)
        summary = self.small_font.render(self.summary_text, True, self.LIGHT_GRAY)
        self.screen.blit(
            summary, (self.popup_rect.centerx - summary.get_width() // 2, self.popup_rect.top + 48)
        )

    @classmethod
    def _build_enemy_class_index(cls) -> dict[str, type[enemies.Enemy]]:
        if cls._enemy_class_index is not None:
            return cls._enemy_class_index

        index: dict[str, type[enemies.Enemy]] = {}
        for attr_name in dir(enemies):
            attr = getattr(enemies, attr_name)
            if not isinstance(attr, type):
                continue
            try:
                if not issubclass(attr, enemies.Enemy):
                    continue
            except TypeError:
                continue
            index.setdefault(attr_name, attr)
        cls._enemy_class_index = index
        return index

    def enemy_instance(self, enemy_name: str):
        if enemy_name in self._enemy_cache:
            return self._enemy_cache[enemy_name]

        class_index = self._build_enemy_class_index()
        attr_name = "".join(str(enemy_name).split())
        candidate_cls = class_index.get(attr_name)
        if candidate_cls is not None:
            try:
                candidate = candidate_cls()
            except TypeError:
                if candidate_cls is getattr(enemies, "Mimic", None):
                    try:
                        candidate = candidate_cls(1)
                    except Exception:
                        candidate = None
                else:
                    candidate = None
            except Exception:
                candidate = None
            if candidate is not None and getattr(candidate, "name", None) == enemy_name:
                self._enemy_cache[enemy_name] = candidate
                return candidate

        for candidate_cls in class_index.values():
            try:
                candidate = candidate_cls()
            except Exception:
                continue
            if getattr(candidate, "name", None) == enemy_name:
                self._enemy_cache[enemy_name] = candidate
                return candidate
        self._enemy_cache[enemy_name] = None
        return None

    @staticmethod
    def _resource_max(resource) -> int | None:
        value = getattr(resource, "max", None)
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _format_resistance(value) -> str:
        try:
            return f"{int(float(value) * 100):+d}%"
        except (TypeError, ValueError):
            return str(value)

    @staticmethod
    def _display_list(values, empty_text="None") -> str:
        clean_values = [str(value) for value in (values or []) if str(value)]
        return ", ".join(clean_values) if clean_values else empty_text

    def _draw_enemy_sprite(self, enemy, rect: pygame.Rect, enemy_name: str | None = None) -> None:
        if rect.width <= 0 or rect.height <= 0:
            return
        try:
            from src.ui_pygame.assets.enemy_combat_sprite_manager import (
                get_enemy_combat_sprite_manager,
            )

            manager = get_enemy_combat_sprite_manager()
            sprite = (
                manager.get_scaled_sprite(enemy, rect.size)
                if enemy is not None
                else manager.get_scaled_sprite_by_name(str(enemy_name or ""), rect.size)
            )
        except Exception:
            return
        if sprite is not None:
            self.screen.blit(sprite, rect)

    def _draw_detail_line(self, label: str, value, x: int, y: int) -> int:
        self.screen.blit(self.normal_font.render(f"{label}: {value}", True, self.WHITE), (x, y))
        return y + self.line_height

    def _draw_detail_section(
        self, title: str, rows: list[str], x: int, y: int, empty_text: str = "None"
    ) -> int:
        self.screen.blit(self.normal_font.render(title, True, self.GOLD), (x, y))
        y += self.line_height
        for row in rows or [empty_text]:
            self.screen.blit(self.small_font.render(row, True, self.WHITE), (x + 12, y))
            y += self.line_height
        return y

    def bestiary_hints(self, enemy_name: str, enemy, boss: bool) -> tuple[list[str], list[str]]:
        """Return cached location/drop hints for repeated bestiary redraws."""
        key = (str(enemy_name), bool(boss))
        if key not in self._hint_cache:
            self._hint_cache[key] = (
                enemies.bestiary_location_hints(enemy_name),
                enemies.bestiary_drop_hints(enemy, boss=boss),
            )
        locations, drops = self._hint_cache[key]
        return list(locations), list(drops)

    def draw_details(self, player_char):
        item = self.items[self.selected_index] if self.items else None
        x = self.details_rect.left + 16
        y = self.details_rect.top + 12

        if not isinstance(item, dict) or item.get("empty"):
            self.screen.blit(
                self.normal_font.render("No bestiary entries recorded.", True, self.GRAY), (x, y)
            )
            return

        enemy_name = item["enemy_name"]
        observed = self.observed_record(player_char, enemy_name)
        details_unlocked = self._record_details_unlocked(observed)
        enemy = self.enemy_instance(enemy_name)
        name_text = self.large_font.render(enemy_name, True, self.WHITE)
        self.screen.blit(name_text, (x, y))

        sprite_rect = pygame.Rect(self.details_rect.right - 148, y, 128, 128)
        self._draw_enemy_sprite(enemy, sprite_rect, enemy_name=enemy_name)
        y += name_text.get_height() + 10

        y = self._draw_detail_line("Name", observed.get("name", enemy_name), x, y)
        status = "Detailed" if details_unlocked else ("Defeated" if item["count"] > 0 else "Seen")
        y = self._draw_detail_line("Status", status, x, y)
        difficulty = observed.get("difficulty_level")
        if difficulty is None:
            difficulty = observed.get("pro_level", observed.get("level", "Unknown"))
        y = self._draw_detail_line("Type", observed.get("type", item["enemy_type"]), x, y)
        y = self._draw_detail_line(
            "Seen", item.get("display_seen_count", item.get("seen_count", 0)), x, y
        )
        y = self._draw_detail_line("Defeated", item["count"], x, y)

        defeated_count = int(item.get("count", 0) or 0)
        if defeated_count > 0:
            y += 8
            boss_drop_rules = enemies.bestiary_uses_boss_drop_rules(enemy_name)
            locations, drop_rows = self.bestiary_hints(enemy_name, enemy, boss=boss_drop_rules)
            y = self._draw_detail_section("Locations", locations, x, y, empty_text="Unknown")
            y += 4
            y = self._draw_detail_section("Possible Drops", drop_rows, x, y, empty_text="None")

        if not details_unlocked:
            y += 8
            self.screen.blit(self.normal_font.render("Details unknown.", True, self.GRAY), (x, y))
            y += self.line_height
            boss_entry = enemies.bestiary_uses_boss_drop_rules(enemy_name) or "Boss" in set(
                observed.get("features", []) or []
            )
            if boss_entry:
                hint = "Boss details cannot be revealed with Vision."
            else:
                hint = "Use Vision while fighting this enemy to reveal bestiary details."
            for line in self._wrap_text(hint, self.details_rect.width - 32):
                self.screen.blit(self.small_font.render(line, True, self.LIGHT_GRAY), (x, y))
                y += self.line_height
            return

        y += 8
        y = self._draw_detail_line("Pro/Difficulty Level", difficulty, x, y)
        resistances = observed.get("resistances", {}) or {}
        if isinstance(resistances, dict):
            resistance_rows = [
                f"{name} {self._format_resistance(value)}" for name, value in resistances.items()
            ]
        else:
            resistance_rows = []
        y = self._draw_detail_section("Resistances", resistance_rows, x, y)
        y += 4
        y = self._draw_detail_line(
            "Known Abilities",
            self._display_list(observed.get("known_abilities"), "None observed"),
            x,
            y,
        )
        features = list(observed.get("features", []) or [])
        immunities = set(observed.get("immunities", []) or [])
        for feature in list(features):
            if str(feature).startswith("Immune:"):
                features.remove(feature)
                immunities.update(
                    part.strip()
                    for part in str(feature).removeprefix("Immune:").split(",")
                    if part.strip()
                )
        y = self._draw_detail_line("Immunities", self._display_list(sorted(immunities)), x, y)
        y = self._draw_detail_line("Features", self._display_list(features), x, y)

    def on_select(self, player_char, item):
        return None
