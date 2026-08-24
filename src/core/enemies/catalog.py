"""Static encounter and Bestiary metadata.

This module intentionally stores enemy class names instead of importing enemy
implementations. The ``enemies`` package façade resolves the names after all classes are
defined, avoiding circular imports and constructor work during metadata reads.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence


EnemySpec = tuple[str, str]
ResolvedEnemySpec = tuple[str, Callable[[], object]]


CURATED_PAIR_SPECS: dict[
    str,
    tuple[str, int, tuple[str, str]]
    | tuple[str, int, tuple[str, str], tuple[float, float]],
] = {
    "carrion_crawl": (
        "Giant Hornet & Battle Toad",
        1,
        ("GiantHornet", "BattleToad"),
        (0.95, 1.0),
    ),
    "wing_and_mattock": (
        "Electric Bat & Battle Toad",
        1,
        ("ElectricBat", "BattleToad"),
    ),
    "fang_and_spear": (
        "Twisted Dwarf & Vampire Bat",
        2,
        ("TwistedDwarf", "VampireBat"),
    ),
    "grave_web": (
        "Zombie & Quasit",
        1,
        ("Zombie", "Quasit"),
        (0.85, 1.2),
    ),
    "lesser_conspiracy": (
        "Battle Toad & Satyr",
        1,
        ("BattleToad", "Satyr"),
        (0.8, 1.1),
    ),
    "hoof_and_howl": (
        "Twisted Dwarf & Xorn",
        2,
        ("TwistedDwarf", "Xorn"),
        (0.9, 1.1),
    ),
    "rot_and_raptor": (
        "Ghoul & Golden Eagle",
        3,
        ("Ghoul", "GoldenEagle"),
    ),
    "venomous_dream": (
        "Night Hag & Pit Viper",
        3,
        ("NightHag", "PitViper"),
        (0.8, 1.2),
    ),
    "burrow_and_bone": (
        "Antlion & Troll",
        4,
        ("Antlion", "Troll"),
        (0.9, 0.95),
    ),
}


RANDOM_ENEMY_SPECS: dict[str, tuple[EnemySpec, ...]] = {
    "0": (
        ("Green Slime", "GreenSlime"),
        ("Goblin", "Goblin"),
        ("Giant Rat", "GiantRat"),
        ("Bandit", "Bandit"),
        ("Skeleton", "Skeleton"),
        ("Scarecrow", "Scarecrow"),
    ),
    "1": (
        ("Giant Centipede", "GiantCentipede"),
        ("Giant Hornet", "GiantHornet"),
        ("Electric Bat", "ElectricBat"),
        ("Zombie", "Zombie"),
        ("Imp", "Imp"),
        ("Giant Spider", "GiantSpider"),
        ("Quasit", "Quasit"),
        ("Panther", "Panther"),
        ("Twisted Dwarf", "TwistedDwarf"),
        ("Battle Toad", "BattleToad"),
        ("Satyr", "Satyr"),
    ),
    "2": (
        ("Acolyte", "Acolyte"),
        ("Panther", "Panther"),
        ("Twisted Dwarf", "TwistedDwarf"),
        ("Battle Toad", "BattleToad"),
        ("Satyr", "Satyr"),
        ("Gnoll", "Gnoll"),
        ("Giant Owl", "GiantOwl"),
        ("Orc", "Orc"),
        ("Vampire", "Vampire"),
        ("Vampire Bat", "VampireBat"),
        ("Direwolf", "Direwolf"),
        ("Red Slime", "RedSlime"),
        ("Giant Snake", "GiantSnake"),
        ("Giant Scorpion", "GiantScorpion"),
        ("Warrior", "Warrior"),
        ("Harpy", "Harpy"),
        ("Naga", "Naga"),
        ("Wererat", "Wererat"),
        ("Xorn", "Xorn"),
        ("Steel Predator", "SteelPredator"),
    ),
    "3": (
        ("War Turtle", "WarTurtle"),
        ("Wayward Priest", "WaywardPriest"),
        ("Clannfear", "Clannfear"),
        ("Ghoul", "Ghoul"),
        ("Troll", "Troll"),
        ("Direbear", "Direbear"),
        ("Owlbear", "Owlbear"),
        ("Evil Crusader", "EvilCrusader"),
        ("Ogre", "Ogre"),
        ("Black Slime", "BlackSlime"),
        ("Golden Eagle", "GoldenEagle"),
        ("Pit Viper", "PitViper"),
        ("Alligator", "Alligator"),
        ("Disciple", "Disciple"),
        ("Werewolf", "Werewolf"),
        ("Antlion", "Antlion"),
        ("Invisible Stalker", "InvisibleStalker"),
        ("Night Hag", "NightHag"),
        ("Treant", "Treant"),
        ("Ankheg", "Ankheg"),
    ),
    "4": (
        ("Antlion", "Antlion"),
        ("Invisible Stalker", "InvisibleStalker"),
        ("Night Hag", "NightHag"),
        ("Brown Slime", "BrownSlime"),
        ("Troll", "Troll"),
        ("Giant", "Giant"),
        ("Owlbear", "Owlbear"),
        ("Gargoyle", "Gargoyle"),
        ("Necromancer", "Necromancer"),
        ("Chimera", "Chimera"),
        ("Dragonkin", "Dragonkin"),
        ("Griffin", "Griffin"),
        ("Drow Assassin", "DrowAssassin"),
        ("Cyborg", "Cyborg"),
        ("Dark Knight", "DarkKnight"),
        ("Fire Myrmidon", "FireMyrmidon"),
        ("Ice Myrmidon", "IceMyrmidon"),
        ("Storm Myrmidon", "StormMyrmidon"),
        ("Water Myrmidon", "WaterMyrmidon"),
        ("Earth Myrmidon", "EarthMyrmidon"),
        ("Wind Myrmidon", "WindMyrmidon"),
        ("Displacer Beast", "DisplacerBeast"),
    ),
    "5": (
        ("Unicorn", "Unicorn"),
        ("Fire Myrmidon", "FireMyrmidon"),
        ("Ice Myrmidon", "IceMyrmidon"),
        ("Storm Myrmidon", "StormMyrmidon"),
        ("Water Myrmidon", "WaterMyrmidon"),
        ("Earth Myrmidon", "EarthMyrmidon"),
        ("Wind Myrmidon", "WindMyrmidon"),
        ("Displacer Beast", "DisplacerBeast"),
        ("Shadow Serpent", "ShadowSerpent"),
        ("Aboleth", "Aboleth"),
        ("Beholder", "Beholder"),
        ("Behemoth", "Behemoth"),
        ("Basilisk", "Basilisk"),
        ("Hydra", "Hydra"),
        ("Lich", "Lich"),
        ("Mind Flayer", "MindFlayer"),
        ("Sandworm", "Sandworm"),
        ("Warforged", "Warforged"),
        ("Wyrm", "Wyrm"),
        ("Wyvern", "Wyvern"),
        ("Archvile", "Archvile"),
        ("Brain Gorger", "BrainGorger"),
    ),
    "6": (
        ("Beholder", "Beholder"),
        ("Behemoth", "Behemoth"),
        ("Lich", "Lich"),
        ("Mind Flayer", "MindFlayer"),
        ("Wyvern", "Wyvern"),
        ("Archvile", "Archvile"),
        ("Brain Gorger", "BrainGorger"),
    ),
}

FUNHOUSE_ENEMY_SPECS: tuple[EnemySpec, ...] = (
    ("Puppet", "Puppet"),
    ("Harlequin", "Harlequin"),
    ("Trickster", "Trickster"),
    ("Copycat", "Copycat"),
)

FIXED_LOCATION_HINTS: dict[str, tuple[str, ...]] = {
    "Flame Wisp": ("Fire Path",),
    "Mimic": ("Chests", "Funhouse Mimic Chest"),
    "Fuath": ("Underground Spring",),
    "Warforged": ("Realm of Cambion Terminal",),
    "Minotaur": ("Minotaur Boss Room",),
    "Barghest": ("Barghest Boss Room",),
    "Pseudodragon": ("Pseudodragon Boss Room",),
    "Nightmare": ("Nightmare Boss Room",),
    "Cockatrice": ("Cockatrice Boss Room",),
    "Wendigo": ("Wendigo Boss Room",),
    "Iron Golem": ("Iron Golem Boss Room",),
    "Golem": ("Golem Boss Room",),
    "Jester": ("Funhouse Boss Room",),
    "Domingo": ("Domingo Boss Room",),
    "Red Dragon": ("Red Dragon Boss Room",),
    "Circe": ("Circe Boss Room",),
    "Merzhin": ("Realm of Cambion",),
    "Cerberus": ("Cerberus Boss Room",),
    "Incubus": ("Incubus Lair",),
    "Vesperion": ("Final Chamber",),
    "Reflection Psychopomp": ("Liminal Gap",),
}

BOSS_DROP_ENEMY_NAMES = frozenset(
    {
        "Minotaur",
        "Barghest",
        "Pseudodragon",
        "Nightmare",
        "Cockatrice",
        "Wendigo",
        "Iron Golem",
        "Golem",
        "Jester",
        "Domingo",
        "Red Dragon",
        "Circe",
        "Merzhin",
        "Cerberus",
        "Vesperion",
    }
)

BOSS_ENEMY_NAMES = frozenset(
    name
    for name, locations in FIXED_LOCATION_HINTS.items()
    if any(
        marker in location
        for location in locations
        for marker in ("Boss Room", "Lair", "Final Chamber", "Liminal Gap")
    )
)


def is_boss_enemy(enemy: object) -> bool:
    """Return whether an enemy is a boss for gameplay-rule purposes."""
    if bool(getattr(enemy, "boss", False) or getattr(enemy, "is_boss", False)):
        return True
    class_name = type(enemy).__name__
    if class_name.endswith("Boss"):
        return True
    return str(getattr(enemy, "name", "") or "") in BOSS_ENEMY_NAMES


def resolve_enemy_specs(
    specs: Sequence[EnemySpec],
    namespace: Mapping[str, object],
) -> tuple[ResolvedEnemySpec, ...]:
    """Resolve class-name specs against the fully initialized enemy module."""
    resolved: list[ResolvedEnemySpec] = []
    for display_name, class_name in specs:
        factory = namespace.get(class_name)
        if not callable(factory):
            raise RuntimeError(f"Enemy catalog references unknown class: {class_name}")
        resolved.append((display_name, factory))
    return tuple(resolved)


def resolve_random_enemy_catalog(
    namespace: Mapping[str, object],
) -> dict[str, tuple[ResolvedEnemySpec, ...]]:
    """Resolve every floor catalog after enemy classes have been defined."""
    return {
        level: resolve_enemy_specs(specs, namespace)
        for level, specs in RANDOM_ENEMY_SPECS.items()
    }
