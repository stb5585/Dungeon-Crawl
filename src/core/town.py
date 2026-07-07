###########################################
""" Town manager """

import random
import re

from . import enemies, items
from .data.data_loader import get_quests, get_patron_dialogues, get_response_map, get_tavern_flavor_dialogues


# Patron dialogue keyed by minimum total level (base + promotions)
# Loaded from external JSON file
PATRON_DIALOGUES = get_patron_dialogues()

# NPC responses to quest acceptance/rejection
# Loaded from external JSON file
RESPONSE_MAP = get_response_map()

# General tavern flavor comments used when no quests are available/active
# Loaded from external JSON file
TAVERN_FLAVOR_DIALOGUES = get_tavern_flavor_dialogues()


BOUNTY_RESTOCK_STEP_THRESHOLD = 200
BOUNTY_RESTOCK_ENEMY_THRESHOLD = 8

BOUNTY_BOARD_STATE_DEFAULTS = {
    "initialized": False,
    "last_restock_level": 0,
    "last_restock_steps": 0,
    "last_restock_enemies_defeated": 0,
}


def default_bounty_board_state():
    """Return fresh bounty-board restock state for a player/save."""
    return dict(BOUNTY_BOARD_STATE_DEFAULTS)


def _nonnegative_int(value, fallback=0):
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return fallback


def normalize_bounty_board_state(state=None):
    """Return a backward-compatible bounty-board restock state dictionary."""
    normalized = default_bounty_board_state()
    if isinstance(state, dict):
        normalized.update(state)

    normalized["initialized"] = bool(normalized.get("initialized", False))
    for key in (
        "last_restock_level",
        "last_restock_steps",
        "last_restock_enemies_defeated",
    ):
        normalized[key] = _nonnegative_int(
            normalized.get(key),
            BOUNTY_BOARD_STATE_DEFAULTS[key],
        )
    return normalized


def _player_level(player_char):
    if hasattr(player_char, "player_level"):
        try:
            return _nonnegative_int(player_char.player_level(), 1)
        except TypeError:
            pass
    level = getattr(player_char, "level", None)
    return _nonnegative_int(getattr(level, "level", 1), 1)


def _gameplay_stat(player_char, stat_name):
    stats = getattr(player_char, "gameplay_stats", {})
    if isinstance(stats, dict):
        return _nonnegative_int(stats.get(stat_name, 0))
    return 0


def ensure_bounty_board_state(player_char):
    """Attach normalized bounty-board restock state to the player."""
    state = normalize_bounty_board_state(
        getattr(player_char, "bounty_board_state", None)
    )
    player_char.bounty_board_state = state
    return state


def active_bounty_count(player_char):
    quest_dict = getattr(player_char, "quest_dict", {})
    bounty_dict = quest_dict.get("Bounty", {}) if isinstance(quest_dict, dict) else {}
    return len(bounty_dict)


def prior_bounty_target_defeats(player_char, bounty_data) -> int:
    """Return already-recorded defeats for the bounty target, across enemy types."""
    enemy = bounty_data.get("enemy") if isinstance(bounty_data, dict) else None
    target_name = getattr(enemy, "name", None)
    if not target_name and isinstance(enemy, str):
        target_name = enemy
    if not target_name and isinstance(bounty_data, dict):
        target_name = bounty_data.get("enemy_name")
    if not target_name:
        return 0

    kill_dict = getattr(player_char, "kill_dict", {}) or {}
    total = 0
    if isinstance(kill_dict, dict):
        for enemy_counts in kill_dict.values():
            if isinstance(enemy_counts, dict):
                try:
                    total += int(enemy_counts.get(target_name, 0) or 0)
                except (TypeError, ValueError):
                    continue
    return max(0, total)


def _split_boss_room_name(class_name: str) -> str:
    base_name = class_name.removesuffix("BossRoom")
    return re.sub(r"(?<!^)(?=[A-Z])", " ", base_name).strip()


def already_defeated_enemy(player_char, enemy_name: str) -> bool:
    """Return whether saved progress already proves this enemy was defeated."""
    target_name = str(enemy_name or "").strip()
    if not target_name:
        return False

    kill_dict = getattr(player_char, "kill_dict", {}) or {}
    if isinstance(kill_dict, dict):
        for enemy_counts in kill_dict.values():
            if not isinstance(enemy_counts, dict):
                continue
            try:
                if int(enemy_counts.get(target_name, 0) or 0) > 0:
                    return True
            except (TypeError, ValueError):
                continue

    world_dict = getattr(player_char, "world_dict", {}) or {}
    if not isinstance(world_dict, dict):
        return False
    for tile in world_dict.values():
        if not getattr(tile, "defeated", False):
            continue
        tile_class_name = type(tile).__name__
        candidates = {tile_class_name, _split_boss_room_name(tile_class_name)}
        tile_enemy = getattr(tile, "enemy", None)
        if tile_enemy is not None:
            candidates.add(str(getattr(tile_enemy, "name", "") or ""))
            candidates.add(str(getattr(tile_enemy, "__name__", "") or ""))
        if target_name in candidates:
            return True
    return False


def mark_bounty_board_restock(player_char):
    """Record the progress point used for the next intermittent restock."""
    player_char.bounty_board_state = {
        "initialized": True,
        "last_restock_level": _player_level(player_char),
        "last_restock_steps": _gameplay_stat(player_char, "steps_taken"),
        "last_restock_enemies_defeated": _gameplay_stat(
            player_char,
            "enemies_defeated",
        ),
    }
    return player_char.bounty_board_state


def should_restock_bounty_board(game, *, available_count=None):
    """Return whether the bounty board should refill at the current progress point."""
    player_char = game.player_char
    state = ensure_bounty_board_state(player_char)
    if available_count is None:
        available_count = len(getattr(game, "bounties", {}) or {})
    if active_bounty_count(player_char) > 0 or available_count > 0:
        return False
    if not state["initialized"]:
        return True

    current_level = _player_level(player_char)
    current_steps = _gameplay_stat(player_char, "steps_taken")
    current_defeats = _gameplay_stat(player_char, "enemies_defeated")

    return (
        current_level > state["last_restock_level"]
        or current_steps - state["last_restock_steps"] >= BOUNTY_RESTOCK_STEP_THRESHOLD
        or current_defeats - state["last_restock_enemies_defeated"] >= BOUNTY_RESTOCK_ENEMY_THRESHOLD
    )


# classes
class BountyBoard:
    MAX_ENEMY_ROLL_ATTEMPTS = 25

    def __init__(self):
        self.bounties = []

    def _existing_target_names(self, game):
        return set(game.player_char.quest_dict.get('Bounty', {})) | set(self.bounty_options())

    def _catalog_bounty_enemy(self, level, existing_names):
        catalog = enemies.random_enemy_catalog()
        if level not in catalog:
            level = max(catalog, key=int)
        candidates = [enemy for enemy in catalog[level] if enemy.name not in existing_names]
        if not candidates:
            candidates = catalog[level]
        return random.choice(candidates)

    def create_bounty(self, game):
        bounty = {"reward": None}
        level = str(min(6, game.player_char.player_level() // 10))
        existing_names = self._existing_target_names(game)
        enemy = None
        for _attempt in range(self.MAX_ENEMY_ROLL_ATTEMPTS):
            candidate = enemies.random_enemy(level)
            if candidate.name not in existing_names:
                enemy = candidate
                break
        if enemy is None:
            enemy = self._catalog_bounty_enemy(level, existing_names)
        bounty["enemy"] = enemy
        bounty["num"] = random.randint(3, 8)
        bounty["exp"] = random.randint(enemy.experience*bounty["num"] // 2, enemy.experience*bounty["num"]) * \
            game.player_char.level.pro_level
        bounty["gold"] = random.randint(25*bounty["num"], 50*bounty["num"]) * game.player_char.player_level()
        if random.randint(0, game.player_char.check_mod('luck', luck_factor=10)):
            item_level = min(8, game.player_char.level.pro_level + random.randint(0, game.player_char.level.pro_level))
            bounty["reward"] = items.random_item(item_level)
        return bounty

    def generate_bounties(self, game):
        available_count = len(getattr(game, "bounties", {}) or {})
        if (
            active_bounty_count(game.player_char) > 0
            or available_count > 0
        ):
            state = ensure_bounty_board_state(game.player_char)
            if not state["initialized"]:
                mark_bounty_board_restock(game.player_char)
            return False
        if not should_restock_bounty_board(game, available_count=available_count):
            return False
        num = random.randint(1, 4) - len(game.player_char.quest_dict['Bounty'])
        if num > 0:
            for _ in range(num):
                bounty = self.create_bounty(game)
                self.bounties.append(bounty)
        if self.bounties:
            mark_bounty_board_restock(game.player_char)
            return True
        return False

    def bounty_options(self):
        options = []
        for bounty in self.bounties:
            if "name" in bounty:
                options.append(bounty["name"])
                continue
            enemy = bounty.get("enemy")
            enemy_name = getattr(enemy, "name", None)
            if enemy_name:
                options.append(enemy_name)
        return options

    def accept_quest(self, quest):
        quest_idx = self.bounties.index(quest)
        self.bounties.pop(quest_idx)


# quest dict - loaded from external JSON file
# Using lazy loading to defer resolution of item classes until needed
_quest_dict_cache = None

def get_quest_dict():
    """Lazy load quests from JSON data file."""
    global _quest_dict_cache
    if _quest_dict_cache is None:
        _quest_dict_cache = get_quests()
    return _quest_dict_cache


def get_holy_grail_rotation_hints(player_char, speaker: str) -> list[str]:
    """Return repeatable Holy Grail progression hints for non-quest-giver dialogue rotation."""
    quest_data = player_char.quest_dict.get("Side", {}).get("The Holy Grail of Quests")
    if not quest_data or quest_data.get("Completed") or quest_data.get("Turned In"):
        return []

    progress = quest_data.setdefault("Chalice Progress", {})
    for key in ("Hooded", "Map", "Sergeant", "Adventurer", "Revealed", "Spawned"):
        progress.setdefault(key, False)

    hints: list[str] = []
    if speaker == "Hooded Figure" and progress.get("Hooded") and not progress.get("Map"):
        hints.append(
            "The Hooded Figure murmurs that a map to the Golden Chalice was last seen with an adventurer carrying an ugly sword."
        )
        hints.append("Revisit the boulder where you found Excaliper; the map may be hidden there.")

    if speaker == "Sergeant" and (progress.get("Map") or "Chalice Map" in player_char.special_inventory):
        if not progress.get("Adventurer"):
            hints.append(
                "The Sergeant studies your map and mutters, 'There's a hidden route somewhere on the third floor. Find the adventurer there.'"
            )
            hints.append("Search the third floor for a secret path; an adventurer there can help you decipher the map.")
        elif not progress.get("Revealed"):
            hints.append("The Sergeant says the hidden adventurer's trick should make the ink emerge if you inspect the Chalice Map carefully.")
            hints.append("Inspect the Chalice Map from your Key Items to reveal the hidden altar location.")
        else:
            hints.append("The Sergeant nods. 'The map marks somewhere on the sixth floor. Go claim the Golden Chalice.'")

    return hints


# For backward compatibility, create module-level variable
quest_dict = get_quest_dict()

# Note: The quest_dict has been moved to src/data/content/quests.json
# This module uses get_quests() from data_loader to load it with resolved item references
