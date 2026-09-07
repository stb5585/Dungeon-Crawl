"""Canonical metadata used to build player ability trees.

Combat implementation remains in ``core.abilities``.  This module only owns
progression layout and stat-gate metadata, keeping progression concerns out of
the combat ability catalog.
"""

from __future__ import annotations

from .warrior import WEAPON_DISCIPLINE_ARTS

TREE_LANES = ("Martial", "Arcane", "Defense", "Support")

STAGE_SIZE_RANGES = {
    1: (10, 25),
    # First- and second-promotion trees need enough room for an actual build,
    # not only the handful of legacy abilities attached to many classes.
    2: (16, 20),
    3: (14, 18),
}

TREE_SIZE_OVERRIDES = {
    # Footpad has four six-node identity tracks and two five-node shared tracks.
    "Footpad": (34, 34),
    # Healer uses six complete authored tracks with three shared promotion joins.
    "Healer": (36, 36),
    # Seven authored tracks with two intentional blank development positions.
    "Pathfinder": (40, 40),
    # Six authored Mage columns plus the mutually exclusive Sorcerer fork.
    "Mage": (36, 36),
    # Four promotion routes plus two complete shared Warrior disciplines.
    "Warrior": (30, 30),
    # Six authored paths plus two mutually exclusive terminal promotions.
    "Warlock": (29, 29),
    # Five authored Demonologist disciplines.
    "Demonologist": (24, 24),
    # Five authored Shadowcaster disciplines, including four familiar masteries.
    "Shadowcaster": (21, 21),
    # Four authored Conjurer disciplines plus the terminal promotion.
    "Conjurer": (21, 21),
    # Seven Calling groups, seven choices, seven ultimates, utility, and Miracles.
    "Thaumaturgist": (29, 29),
    # Eight independent discipline-gated weapon arts sit beside the two
    # ordinary Weapon Master routes.
    "Weapon Master": (33, 33),
    # Four development paths and two columns of heavy weapon arts.
    "Berserker": (25, 25),
    # Eight three-rank weapon-art chains plus four floating mastery entries.
    "Grandmaster of Arms": (30, 30),
    # Six Lancer disciplines with split polearm assault and guard paths.
    "Lancer": (22, 22),
    # Dragoon retains all 23 Lancer development nodes and adds 11 mastery nodes.
    "Dragoon": (33, 33),
    # Four Sentinel capstone paths, two shared roots, and four unbound skills.
    "Sentinel": (24, 24),
    # Paladin has 22 development nodes plus its terminal promotion.
    "Paladin": (22, 22),
    # Four terminal Resolve/Burst mastery disciplines.
    "Stalwart Defender": (25, 25),
    # Four authored terminal paths with both melee-style expansions.
    "Crusader": (26, 26),
    # Three release disciplines plus independent universal weapon techniques.
    "Knight Enchanter": (28, 28),
    # Five six-row Assassin disciplines with four intentional blank positions.
    "Assassin": (25, 25),
    # Five Ninja disciplines with two intentional utility gaps.
    "Ninja": (28, 28),
    # Five authored schools of Sorcerer development with two specialization forks.
    "Sorcerer": (29, 29),
    # Five authored Wizard columns, including the quest-awarded ultimate spell.
    "Wizard": (28, 28),
    # Catalog-only promoted trees expose only their implemented abilities while
    # their sidecar decision blocks await authored expansion. Fake rating-family
    # padding was removed; these exact interim counts prevent it from returning
    # unnoticed.
    "Thief": (22, 22),
    "Rogue": (28, 28),
    # Casework and judgment lead to Seeker; six elemental wards remain optional.
    "Inquisitor": (23, 23),
    # Four complete terminal disciplines deepen Revelation and Wayfinding.
    "Seeker": (28, 28),
    # Compact stolen-magic trees use higher node costs to create build pressure.
    "Spell Stealer": (12, 12),
    # Enemy spells remain external; Neural Connection is an optional mastery leaf.
    "Arcane Trickster": (11, 11),
    # Four route disciplines and one shared ministry support both promotions.
    "Cleric": (26, 26),
    "Templar": (28, 28),
    "Hierophant": (28, 28),
    "Monk": (23, 23),
    # Dim Mak remains a Power Core quest reward; its six optional modifiers
    # are terminal leaves beside 21 ordinary Master Monk development nodes.
    "Master Monk": (27, 27),
    "Priest": (22, 22),
    "Archbishop": (29, 29),
    "Bard": (26, 26),
    "Troubadour": (27, 27),
    "Druid": (28, 28),
    "Lycan": (28, 28),
    "Archdruid": (28, 28),
    "Diviner": (22, 22),
    # Volcano remains witnessed enemy magic; Tephra is an optional mastery leaf.
    "Astromancer": (27, 27),
    # Totem is inherent; three routes and an optional omen branch contain 19 nodes.
    "Shaman": (19, 19),
    # Four seven-node Soulcatcher mastery routes total 30 development points.
    "Soulcatcher": (28, 28),
    # Five Ranger disciplines contain 24 development nodes plus one promotion.
    "Ranger": (24, 24),
    # Bonded Bulwark is the sole retained talent because it has an authored,
    # tested companion-bond payoff rather than a generic rating bonus.
    # Four Beast Master tracks contain 22 terminal development nodes.
    "Beast Master": (22, 22),
}

ABILITY_ICON_KEYS = frozenset(
    {
        "skill_offense",
        "skill_defense",
        "skill_control",
        "skill_support",
        "skill_mobility",
        "skill_passive",
        "skill_stealth",
        "skill_drain",
        "skill_martial_arts",
        "skill_truth",
        "skill_luck",
        "spell_arcane",
        "spell_fire",
        "spell_ice",
        "spell_lightning",
        "spell_water",
        "spell_earth",
        "spell_wind",
        "spell_holy",
        "spell_shadow",
        "spell_poison",
        "spell_heal",
        "spell_support",
        "spell_status",
        "spell_illusion",
        "spell_movement",
        "spell_time",
        "spell_summon",
        "spell_transform",
        "rating_attack",
        "rating_magic",
        "rating_defense",
        "rating_magic_defense",
        "promotion",
        "unknown",
    }
)

ABILITY_ICON_OVERRIDES = {
    "Adrenaline": "skill_support",
    "Battle Cry": "skill_support",
    "Charge": "skill_mobility",
    "Cripple": "skill_control",
    "Cross Block": "skill_defense",
    "Devastating Throw": "skill_offense",
    "Disarm": "skill_control",
    "Dishearten": "skill_control",
    "Dual Wield": "skill_passive",
    "Duelist": "skill_passive",
    "Driving Thrust": "skill_offense",
    "Goad": "skill_control",
    "Honed Attack": "skill_passive",
    "Maim": "skill_control",
    "Momentum": "skill_offense",
    "Natural Attunement": "skill_support",
    "Nullify Poison": "spell_earth",
    "Ray of Moonlight": "spell_earth",
    "Thorny Vine": "spell_earth",
    "Parry": "skill_defense",
    "Rally": "skill_support",
    "Shield Block": "skill_defense",
    "Shield Slam": "skill_defense",
    "Chastise": "skill_passive",
    "Weapon Focus": "skill_passive",
}

# Some upgraded ability classes intentionally retain their predecessor's
# runtime name for spellbook compatibility. Progression still needs to
# distinguish those purchases visually.
ABILITY_NODE_NAME_OVERRIDES = {
    "Heal2": "Heal II",
}


def _base_node(
    node_id: str,
    kind: str,
    identifier: str,
    lane: str,
    position: tuple[float, int],
    prerequisites: tuple[str, ...] = (),
    *,
    name: str | None = None,
    rating: str | None = None,
) -> dict[str, object]:
    """Declare one explicitly placed base-tree development node."""
    spec = {
        "id": node_id,
        "kind": kind,
        "identifier": identifier,
        "lane": lane,
        "position": position,
        "prerequisites": prerequisites,
    }
    if name is not None:
        spec["name"] = name
    if rating is not None:
        spec["rating"] = rating
    return spec


# These graphs separate visual lanes from promotion ownership. Shared tracks
# can therefore feed several promotions while every existing node ID remains
# stable for saves and documentation links.
BASE_TREE_NODE_SPECS = {
    "Footpad": (
        _base_node("footpad.ability.stumble-upon", "ability", "StumbleUpon", "Thief", (0, 0)),
        _base_node(
            "footpad.ability.steal",
            "ability",
            "Steal",
            "Thief",
            (0, 1),
            ("footpad.ability.stumble-upon",),
        ),
        _base_node(
            "footpad.ability.lockpick",
            "ability",
            "Lockpick",
            "Thief",
            (0, 2),
            ("footpad.ability.steal",),
        ),
        _base_node(
            "footpad.ability.avoid-traps",
            "ability",
            "AvoidTraps",
            "Thief",
            (0, 3),
            ("footpad.ability.lockpick",),
        ),
        _base_node(
            "footpad.ability.do-over",
            "ability",
            "DoOver",
            "Thief",
            (0, 4),
            ("footpad.ability.avoid-traps",),
        ),
        _base_node(
            "footpad.ability.serendipity",
            "ability",
            "Serendipity",
            "Thief",
            (0, 5),
            ("footpad.ability.do-over",),
        ),
        _base_node("footpad.ability.disarm", "ability", "Disarm", "Control", (1, 0)),
        _base_node(
            "footpad.ability.pocketsand",
            "ability",
            "PocketSand",
            "Control",
            (1, 1),
            ("footpad.ability.disarm",),
        ),
        _base_node(
            "footpad.ability.smokescreen",
            "ability",
            "SmokeScreen",
            "Control",
            (1, 2),
            ("footpad.ability.pocketsand",),
        ),
        _base_node(
            "footpad.ability.aggressive-pursuit",
            "ability",
            "AggressivePursuit",
            "Control",
            (1, 4),
            ("footpad.ability.smokescreen",),
        ),
        _base_node(
            "footpad.ability.sleepingpowder",
            "ability",
            "SleepingPowder",
            "Control",
            (1, 5),
            ("footpad.ability.aggressive-pursuit",),
        ),
        _base_node("footpad.ability.dual-wield", "ability", "DualWield", "Assassin", (2, 0)),
        _base_node(
            "footpad.ability.backstab",
            "ability",
            "Backstab",
            "Assassin",
            (2, 1),
            ("footpad.ability.dual-wield",),
        ),
        _base_node(
            "footpad.ability.cripple",
            "ability",
            "Cripple",
            "Assassin",
            (2, 2),
            ("footpad.ability.backstab",),
        ),
        _base_node(
            "footpad.ability.kidneypunch",
            "ability",
            "KidneyPunch",
            "Assassin",
            (2, 3),
            ("footpad.ability.cripple",),
        ),
        _base_node(
            "footpad.ability.doublestrike",
            "ability",
            "DoubleStrike",
            "Assassin",
            (2, 4),
            ("footpad.ability.kidneypunch",),
        ),
        _base_node(
            "footpad.ability.obscuration",
            "ability",
            "Obscuration",
            "Assassin",
            (2, 5),
            ("footpad.ability.doublestrike",),
        ),
        _base_node("footpad.ability.duelist", "ability", "Duelist", "Spell Stealer", (3, 0)),
        _base_node(
            "footpad.ability.incantation-comprehension",
            "ability",
            "IncantationComprehension",
            "Spell Stealer",
            (3, 1),
            ("footpad.ability.duelist",),
        ),
        _base_node(
            "footpad.rating.magic.1",
            "rating",
            "Magic",
            "Spell Stealer",
            (3, 2),
            ("footpad.ability.incantation-comprehension",),
        ),
        _base_node(
            "footpad.ability.mana-depletion",
            "ability",
            "ManaDepletion",
            "Spell Stealer",
            (3, 3),
            ("footpad.rating.magic.1",),
        ),
        _base_node(
            "footpad.ability.imbue-weapon",
            "ability",
            "ImbueWeapon",
            "Spell Stealer",
            (3, 4),
            ("footpad.ability.mana-depletion",),
        ),
        _base_node(
            "footpad.ability.disruption",
            "ability",
            "Disruption",
            "Spell Stealer",
            (3, 5),
            ("footpad.ability.imbue-weapon",),
        ),
        _base_node(
            "footpad.ability.piercing-strike", "ability", "PiercingStrike", "Inquisitor", (5, 0)
        ),
        _base_node(
            "footpad.ability.detect-animal",
            "ability",
            "DetectAnimal",
            "Inquisitor",
            (5, 1),
            ("footpad.ability.piercing-strike",),
        ),
        _base_node(
            "footpad.ability.inspect",
            "ability",
            "Inspect",
            "Inquisitor",
            (5, 2),
            ("footpad.ability.detect-animal",),
        ),
        _base_node(
            "footpad.ability.detect-humanoid",
            "ability",
            "DetectHumanoid",
            "Inquisitor",
            (5, 3),
            ("footpad.ability.inspect",),
        ),
        _base_node(
            "footpad.rating.magic-defense.1",
            "rating",
            "Magic Defense",
            "Inquisitor",
            (5, 4),
            ("footpad.ability.detect-humanoid",),
        ),
        _base_node(
            "footpad.ability.detect-slime",
            "ability",
            "DetectSlime",
            "Inquisitor",
            (5, 5),
            ("footpad.rating.magic-defense.1",),
        ),
        _base_node("footpad.ability.quickstep", "ability", "Quickstep", "Defense", (4, 0)),
        _base_node(
            "footpad.ability.parry",
            "ability",
            "Parry",
            "Defense",
            (4, 2),
            ("footpad.ability.quickstep",),
        ),
        _base_node(
            "footpad.ability.retort",
            "ability",
            "Retort",
            "Defense",
            (4, 3),
            ("footpad.ability.parry",),
        ),
        _base_node(
            "footpad.ability.evasiveguard",
            "ability",
            "EvasiveGuard",
            "Defense",
            (4, 4),
            ("footpad.ability.retort",),
        ),
        _base_node(
            "footpad.ability.mystical-evasion",
            "ability",
            "MysticalEvasion",
            "Defense",
            (4, 5),
            ("footpad.ability.evasiveguard",),
        ),
    ),
    "Healer": (
        _base_node("healer.ability.imbue-weapon", "ability", "ImbueWeapon", "Bard", (0, 0)),
        _base_node(
            "healer.ability.goad",
            "ability",
            "Goad",
            "Bard",
            (0, 1),
            ("healer.ability.imbue-weapon",),
        ),
        _base_node(
            "healer.ability.lullaby", "ability", "Lullaby", "Bard", (0, 2), ("healer.ability.goad",)
        ),
        _base_node(
            "healer.ability.beginners-luck",
            "ability",
            "BeginnersLuck",
            "Bard",
            (0, 3),
            ("healer.ability.lullaby",),
        ),
        _base_node(
            "healer.ability.mental-shard",
            "ability",
            "MentalShard",
            "Bard",
            (0, 4),
            ("healer.ability.beginners-luck",),
        ),
        _base_node(
            "healer.ability.cacophany",
            "ability",
            "Cacophany",
            "Bard",
            (0, 5),
            ("healer.ability.mental-shard",),
        ),
        _base_node("healer.ability.bless", "ability", "Bless", "Support", (1, 0)),
        _base_node(
            "healer.ability.tranquility",
            "ability",
            "Tranquility",
            "Support",
            (1, 1),
            ("healer.ability.bless",),
        ),
        _base_node(
            "healer.ability.courage",
            "ability",
            "Courage",
            "Support",
            (1, 2),
            ("healer.ability.tranquility",),
        ),
        _base_node(
            "healer.ability.vision",
            "ability",
            "Vision",
            "Support",
            (1, 3),
            ("healer.ability.courage",),
        ),
        _base_node(
            "healer.rating.magic-defense.1",
            "rating",
            "Magic Defense",
            "Support",
            (1, 4),
            ("healer.ability.vision",),
        ),
        _base_node(
            "healer.ability.tutelary",
            "ability",
            "Tutelary",
            "Support",
            (1, 5),
            ("healer.rating.magic-defense.1",),
        ),
        _base_node("healer.ability.smite", "ability", "Smite", "Cleric", (2, 0)),
        _base_node(
            "healer.rating.defense.1",
            "rating",
            "Defense",
            "Cleric",
            (2, 1),
            ("healer.ability.smite",),
        ),
        _base_node(
            "healer.ability.turnundead",
            "ability",
            "TurnUndead",
            "Cleric",
            (2, 2),
            ("healer.rating.defense.1",),
        ),
        _base_node(
            "healer.ability.detect-undead",
            "ability",
            "DetectUndead",
            "Cleric",
            (2, 3),
            ("healer.ability.turnundead",),
        ),
        _base_node(
            "healer.ability.divine-protection",
            "ability",
            "DivineProtection",
            "Cleric",
            (2, 4),
            ("healer.ability.detect-undead",),
        ),
        _base_node(
            "healer.ability.shield-slam",
            "ability",
            "ShieldSlam",
            "Cleric",
            (2, 5),
            ("healer.ability.divine-protection",),
        ),
        _base_node("healer.ability.heal", "ability", "Heal", "Healing", (3, 0)),
        _base_node("healer.health.25", "health", "HP", "Healing", (3, 1), ("healer.ability.heal",)),
        _base_node(
            "healer.ability.regen", "ability", "Regen", "Healing", (3, 2), ("healer.health.25",)
        ),
        _base_node("healer.mana.25", "mana", "MP", "Healing", (3, 3), ("healer.ability.regen",)),
        _base_node(
            "healer.ability.safeguarding",
            "ability",
            "Safeguarding",
            "Healing",
            (3, 4),
            ("healer.mana.25",),
        ),
        _base_node(
            "healer.ability.heal2",
            "ability",
            "Heal2",
            "Healing",
            (3, 5),
            ("healer.ability.safeguarding",),
        ),
        _base_node("healer.ability.holy", "ability", "Holy", "Priest", (4, 0)),
        _base_node(
            "healer.rating.magic.1", "rating", "Magic", "Priest", (4, 1), ("healer.ability.holy",)
        ),
        _base_node(
            "healer.ability.flash-blindness",
            "ability",
            "FlashBlindness",
            "Priest",
            (4, 2),
            ("healer.rating.magic.1",),
        ),
        _base_node(
            "healer.ability.defensive-regen",
            "ability",
            "DefensiveRegen",
            "Priest",
            (4, 3),
            ("healer.ability.flash-blindness",),
        ),
        _base_node(
            "healer.ability.incite-panic",
            "ability",
            "IncitePanic",
            "Priest",
            (4, 4),
            ("healer.ability.defensive-regen",),
        ),
        _base_node(
            "healer.ability.resist-shadow",
            "ability",
            "ResistShadow",
            "Priest",
            (4, 5),
            ("healer.ability.incite-panic",),
        ),
        _base_node("healer.ability.zen-accuracy", "ability", "ZenAccuracy", "Monk", (5, 0)),
        _base_node(
            "healer.ability.staff-proficiency",
            "ability",
            "StaffProficiency",
            "Monk",
            (5, 1),
            ("healer.ability.zen-accuracy",),
        ),
        _base_node(
            "healer.rating.attack.1",
            "rating",
            "Attack",
            "Monk",
            (5, 2),
            ("healer.ability.staff-proficiency",),
        ),
        _base_node(
            "healer.ability.delayed-reaction",
            "ability",
            "DelayedReaction",
            "Monk",
            (5, 3),
            ("healer.rating.attack.1",),
        ),
        _base_node(
            "healer.ability.leg-sweep",
            "ability",
            "LegSweep",
            "Monk",
            (5, 4),
            ("healer.ability.delayed-reaction",),
        ),
        _base_node(
            "healer.ability.meditation",
            "ability",
            "Meditation",
            "Monk",
            (5, 5),
            ("healer.ability.leg-sweep",),
        ),
    ),
    "Pathfinder": (
        _base_node("pathfinder.ability.poison-dart", "ability", "PoisonDart", "Druid", (0, 0)),
        _base_node(
            "pathfinder.ability.regrowth",
            "ability",
            "Regrowth",
            "Druid",
            (0, 1),
            ("pathfinder.ability.poison-dart",),
        ),
        _base_node(
            "pathfinder.ability.ray-of-moonlight",
            "ability",
            "RayOfMoonlight",
            "Druid",
            (0, 2),
            ("pathfinder.ability.regrowth",),
        ),
        _base_node(
            "pathfinder.ability.nullify-poison",
            "ability",
            "NullifyPoison",
            "Druid",
            (0, 3),
            ("pathfinder.ability.ray-of-moonlight",),
        ),
        _base_node(
            "pathfinder.ability.thorny-vine",
            "ability",
            "ThornyVine",
            "Druid",
            (0, 4),
            ("pathfinder.ability.nullify-poison",),
        ),
        _base_node(
            "pathfinder.ability.poison-strike",
            "ability",
            "PoisonStrike",
            "Druid",
            (0, 5),
            ("pathfinder.ability.thorny-vine",),
        ),
        _base_node(
            "pathfinder.ability.naturalattunement",
            "ability",
            "NaturalAttunement",
            "Naturalism",
            (1, 0),
        ),
        _base_node(
            "pathfinder.ability.razor-talons",
            "ability",
            "RazorTalons",
            "Naturalism",
            (1, 1),
            ("pathfinder.ability.naturalattunement",),
        ),
        _base_node(
            "pathfinder.ability.call-animal",
            "ability",
            "CallAnimal",
            "Naturalism",
            (1, 2),
            ("pathfinder.ability.razor-talons",),
        ),
        _base_node(
            "pathfinder.ability.detect-animal",
            "ability",
            "DetectAnimal",
            "Naturalism",
            (1, 4),
            ("pathfinder.ability.call-animal",),
        ),
        _base_node(
            "pathfinder.ability.creature-comforts",
            "ability",
            "CreatureComforts",
            "Naturalism",
            (1, 5),
            ("pathfinder.ability.detect-animal",),
        ),
        _base_node("pathfinder.ability.stumble-upon", "ability", "StumbleUpon", "Ranger", (2, 0)),
        _base_node(
            "pathfinder.ability.zephyrstrike",
            "ability",
            "Zephyrstrike",
            "Ranger",
            (2, 1),
            ("pathfinder.ability.stumble-upon",),
        ),
        _base_node(
            "pathfinder.ability.cautious-assault",
            "ability",
            "CautiousAssault",
            "Ranger",
            (2, 2),
            ("pathfinder.ability.zephyrstrike",),
        ),
        _base_node(
            "pathfinder.ability.honed-attack",
            "ability",
            "HonedAttack",
            "Ranger",
            (2, 3),
            ("pathfinder.ability.cautious-assault",),
        ),
        _base_node(
            "pathfinder.ability.unnatural-purge",
            "ability",
            "UnnaturalPurge",
            "Ranger",
            (2, 4),
            ("pathfinder.ability.honed-attack",),
        ),
        _base_node(
            "pathfinder.ability.bounce-back",
            "ability",
            "BounceBack",
            "Ranger",
            (2, 5),
            ("pathfinder.ability.unnatural-purge",),
        ),
        _base_node(
            "pathfinder.ability.piercingstrike", "ability", "PiercingStrike", "Melee", (3, 0)
        ),
        _base_node(
            "pathfinder.ability.quickstep",
            "ability",
            "Quickstep",
            "Melee",
            (3, 1),
            ("pathfinder.ability.piercingstrike",),
        ),
        _base_node(
            "pathfinder.rating.attack.1",
            "rating",
            "Attack",
            "Melee",
            (3, 2),
            ("pathfinder.ability.quickstep",),
        ),
        _base_node(
            "pathfinder.ability.parry",
            "ability",
            "Parry",
            "Melee",
            (3, 4),
            ("pathfinder.rating.attack.1",),
        ),
        _base_node(
            "pathfinder.ability.truestrike",
            "ability",
            "TrueStrike",
            "Melee",
            (3, 5),
            ("pathfinder.ability.parry",),
        ),
        _base_node("pathfinder.ability.spirit-strike", "ability", "SpiritStrike", "Shaman", (4, 0)),
        _base_node(
            "pathfinder.ability.conversion",
            "ability",
            "Conversion",
            "Shaman",
            (4, 1),
            ("pathfinder.ability.spirit-strike",),
        ),
        _base_node(
            "pathfinder.mana.25", "mana", "MP", "Shaman", (4, 2), ("pathfinder.ability.conversion",)
        ),
        _base_node(
            "pathfinder.ability.hydration",
            "ability",
            "Hydration",
            "Shaman",
            (4, 3),
            ("pathfinder.mana.25",),
        ),
        _base_node(
            "pathfinder.ability.very-superstitious",
            "ability",
            "VerySuperstitious",
            "Shaman",
            (4, 4),
            ("pathfinder.ability.hydration",),
        ),
        _base_node(
            "pathfinder.ability.primal-trance",
            "ability",
            "PrimalTrance",
            "Shaman",
            (4, 5),
            ("pathfinder.ability.very-superstitious",),
        ),
        _base_node("pathfinder.ability.tremor", "ability", "Tremor", "Elemental", (5, 0)),
        _base_node(
            "pathfinder.ability.waterjet",
            "ability",
            "WaterJet",
            "Elemental",
            (5, 1),
            ("pathfinder.ability.tremor",),
        ),
        _base_node(
            "pathfinder.ability.gust",
            "ability",
            "Gust",
            "Elemental",
            (5, 2),
            ("pathfinder.ability.waterjet",),
        ),
        _base_node(
            "pathfinder.ability.scorch",
            "ability",
            "Scorch",
            "Elemental",
            (5, 3),
            ("pathfinder.ability.gust",),
        ),
        _base_node(
            "pathfinder.ability.fundamental-harmony",
            "ability",
            "FundamentalHarmony",
            "Elemental",
            (5, 4),
            ("pathfinder.ability.scorch",),
        ),
        _base_node(
            "pathfinder.ability.detect-elemental",
            "ability",
            "DetectElemental",
            "Elemental",
            (5, 5),
            ("pathfinder.ability.fundamental-harmony",),
        ),
        _base_node(
            "pathfinder.ability.intensify-elements",
            "ability",
            "IntensifyElements",
            "Diviner",
            (6, 0),
        ),
        _base_node(
            "pathfinder.ability.chronology",
            "ability",
            "Chronology",
            "Diviner",
            (6, 1),
            ("pathfinder.ability.intensify-elements",),
        ),
        _base_node(
            "pathfinder.rating.magic.1",
            "rating",
            "Magic",
            "Diviner",
            (6, 2),
            ("pathfinder.ability.chronology",),
        ),
        _base_node(
            "pathfinder.ability.blinding-fog",
            "ability",
            "BlindingFog",
            "Diviner",
            (6, 3),
            ("pathfinder.rating.magic.1",),
        ),
        _base_node(
            "pathfinder.ability.geomancy",
            "ability",
            "Geomancy",
            "Diviner",
            (6, 4),
            ("pathfinder.ability.blinding-fog",),
        ),
        _base_node(
            "pathfinder.ability.control-z",
            "ability",
            "ControlZ",
            "Diviner",
            (6, 5),
            ("pathfinder.ability.geomancy",),
        ),
    ),
}

BASE_TREE_PROMOTION_SPECS = {
    "Footpad": (
        (
            "Thief",
            "Thief",
            (0.5, 6),
            ("footpad.ability.serendipity", "footpad.ability.sleepingpowder"),
        ),
        (
            "Assassin",
            "Assassin",
            (1.5, 6),
            ("footpad.ability.obscuration", "footpad.ability.sleepingpowder"),
        ),
        (
            "Spell Stealer",
            "Spell Stealer",
            (3.5, 6),
            ("footpad.ability.disruption", "footpad.ability.mystical-evasion"),
        ),
        (
            "Inquisitor",
            "Inquisitor",
            (4.5, 6),
            ("footpad.ability.detect-slime", "footpad.ability.mystical-evasion"),
        ),
    ),
    "Healer": (
        ("Bard", "Bard", (0.5, 6), ("healer.ability.cacophany", "healer.ability.tutelary")),
        ("Cleric", "Cleric", (2.5, 6), ("healer.ability.shield-slam", "healer.ability.heal2")),
        ("Priest", "Priest", (3.5, 6), ("healer.ability.resist-shadow", "healer.ability.heal2")),
        ("Monk", "Monk", (5, 6), ("healer.ability.meditation",)),
    ),
    "Pathfinder": (
        (
            "Druid",
            "Druid",
            (0.5, 6),
            ("pathfinder.ability.poison-strike", "pathfinder.ability.creature-comforts"),
        ),
        (
            "Ranger",
            "Ranger",
            (2, 6),
            (
                "pathfinder.ability.call-animal",
                "pathfinder.ability.bounce-back",
                "pathfinder.rating.attack.1",
            ),
        ),
        (
            "Shaman",
            "Shaman",
            (4, 6),
            (
                "pathfinder.rating.attack.1",
                "pathfinder.ability.primal-trance",
                "pathfinder.ability.gust",
            ),
        ),
        (
            "Diviner",
            "Diviner",
            (5.5, 6),
            ("pathfinder.ability.gust", "pathfinder.ability.control-z"),
        ),
    ),
}

# Promoted trees may declare a talent here only when it has an authored runtime
# payoff. Generic rating-only families are not progression content.
CLASS_KIT_TALENTS = {
    "Beast Master": (("Bonded Bulwark", "beast-master.bonded-bulwark", "Defense"),),
}
AUTHORED_PROMOTED_TALENT_KEYS = frozenset(
    {
        "beast-master.bonded-bulwark",
    }
)

# These classes currently expose only their authored legacy ability catalog.
# Their decision blocks live
# beside the generated diagrams. They deliberately do not satisfy the normal
# breadth heuristic by manufacturing passive choices.
CATALOG_ONLY_PROMOTED_TREE_CLASSES = frozenset()

TALENT_KIT_EFFECTS = {
    "berserker.bloodied-ferocity": ("meter_cap", "bloodied_momentum", 1),
    "paladin.tempered-conviction": ("meter_cap", "oath_conviction", 1),
    "lancer.aerial-footwork": ("meter_cap", "aerial_tempo", 1),
    "beast-master.bonded-bulwark": ("bond_power", "companion", 10),
    "bard.crescendo-reserve": ("meter_cap", "crescendo", 1),
    "troubadour.crescendo-reserve": ("meter_cap", "crescendo", 2),
    "arcane-trickster.grand-larceny": ("meter_cap", "stolen_charge", 1),
    "cleric.overflowing-grace": ("meter_cap", "devotion", 1),
    "hierophant.abundant-grace": ("meter_cap", "devotion", 1),
    "soulcatcher.deep-resonance": ("meter_cap", "totem_resonance", 1),
}

# A class is considered authored only when its ability paths are explicit or
# it owns named kit talents. This set intentionally covers the complete
# registry; adding a class now requires adding progression identity here.
AUTHORED_TREE_CLASSES = frozenset(
    {
        "Mage",
        "Ninja",
        "Warrior",
        *BASE_TREE_NODE_SPECS,
        *CATALOG_ONLY_PROMOTED_TREE_CLASSES,
        *CLASS_KIT_TALENTS,
        "Weapon Master",
        "Berserker",
        "Grandmaster of Arms",
        "Paladin",
        "Crusader",
        "Lancer",
        "Dragoon",
        "Sentinel",
        "Stalwart Defender",
        "Sorcerer",
        "Wizard",
        "Warlock",
        "Shadowcaster",
        "Demonologist",
        "Spellblade",
        "Knight Enchanter",
        "Conjurer",
        "Thaumaturgist",
        "Assassin",
        "Ranger",
        "Beast Master",
        "Bard",
        "Troubadour",
        "Spell Stealer",
        "Arcane Trickster",
        "Cleric",
        "Templar",
        "Hierophant",
        "Thief",
        "Rogue",
        "Inquisitor",
        "Seeker",
        "Shaman",
        "Soulcatcher",
        "Monk",
        "Master Monk",
        "Priest",
        "Archbishop",
        "Druid",
        "Lycan",
        "Archdruid",
        "Diviner",
        "Astromancer",
    }
)

# Promoted classes use explicit identity paths. Constructor names are declared
# rather than inferred from ability type, so adding or moving a catalog entry
# requires an intentional manifest edit.
PROMOTED_TREE_PATHS = {
    "Weapon Master": (
        (
            "Berserker",
            (
                "DoubleStrike",
                "MortalStrike",
                "DevastatingThrow",
                "TwoHandedWeaponProficiency",
                "BrutishStrength",
            ),
        ),
        ("Grandmaster", ("Parry", "TruePiercingStrike")),
        (
            "Dual Wield",
            ("DualWield", "HonedAttack", "Momentum", "CrossBlock"),
        ),
        (
            "Duelist",
            ("Duelist", "BlindFighting", "Retort", "Maim"),
        ),
        (
            "Weapon Arts",
            (
                "IronPalm",
                "Hemorrhage",
                "RiposteLine",
                "LowSweep",
                "GuardCleaver",
                "ReaversMark",
                "Brace",
                "AnvilStrike",
                "IronPalm2",
                "Hemorrhage2",
                "RiposteLine2",
                "LowSweep2",
                "GuardCleaver2",
                "ReaversMark2",
                "Brace2",
                "AnvilStrike2",
            ),
        ),
    ),
    "Berserker": (
        (
            "Survival",
            ("FinalAssault", "MonkeyGrip", "PainTolerance", "MonkeyGrip2"),
        ),
        (
            "Fury",
            ("Frenzy", "MortalStrike2", "BoomerangToss", "TripleStrike"),
        ),
        (
            "Weapon Arts",
            (
                "GuardCleaver",
                "ReaversMark",
                "Brace",
                "AnvilStrike",
                "GuardCleaver2",
                "ReaversMark2",
                "Brace2",
                "AnvilStrike2",
            ),
        ),
    ),
    "Grandmaster of Arms": (
        (
            "Weapon Arts",
            tuple(
                identifier
                for _node_id, base_identifier, _weapon_type in WEAPON_DISCIPLINE_ARTS
                for identifier in (
                    base_identifier,
                    f"{base_identifier}2",
                    f"{base_identifier}3",
                )
            ),
        ),
        ("Mastery", ()),
    ),
    "Paladin": (
        ("Zeal", ("Smite",)),
        ("Grace", ("Heal", "DivineProtection")),
        ("Oathguard", ()),
    ),
    "Crusader": (
        (
            "Judgment",
            ("MortalStrike", "TripleStrike", "TruePiercingStrike", "Smite2", "Smite3", "Dispel"),
        ),
        ("Consecration", ("Heal2", "Cleanse", "Posturing")),
    ),
    "Lancer": (
        (
            "Polearm Assault",
            (
                "PolearmProficiency",
                "LanceSweep",
                "ExtendedReach",
                "Zephyrstrike",
                "SwingAndBash",
                "PolearmExcellence",
            ),
        ),
        (
            "Polearm Guard",
            ("Phalanx", "CriticalVigor", "DragonSoul"),
        ),
        (
            "Aerial Tempo",
            ("Jump", "Parry", "TrueStrike", "VigilantLanding"),
        ),
    ),
    "Dragoon": (
        (
            "Aerial Supremacy",
            ("PolearmMastery", "DragonDive", "Dragonheart"),
        ),
        ("Universal", ("TruePiercingStrike",)),
    ),
    "Sentinel": (
        (
            "Assault",
            (
                "Retaliate",
                "SwingAndBash",
                "FocusedAssault",
                "Repercussion",
            ),
        ),
        (
            "Bulwark",
            (
                "HoldTheLine",
                "ShieldRiposte",
                "BraceWall",
            ),
        ),
        (
            "Resistance",
            (
                "Adrenaline",
                "SpellBlock",
                "BulwarkGuard",
                "SpellReflection",
            ),
        ),
        (
            "Support",
            (
                "PurgeWeakness",
                "Boast",
            ),
        ),
        (
            "Universal",
            (
                "Goad",
                "Charge",
                "DoubleStrike",
            ),
        ),
    ),
    "Stalwart Defender": (
        (
            "Assault",
            (
                "Repercussion",
                "FocusedAssault",
                "CrushingVengeance",
                "DoublePayback",
            ),
        ),
        (
            "Bulwark",
            ("HoldTheLine", "BraceWall", "LastStand", "IronMaiden"),
        ),
        (
            "Resistance",
            ("SpellBlock", "BulwarkGuard", "SpellReflection"),
        ),
        ("Support", ("PurgeWeakness", "Boast")),
        (
            "Resolve Bursts",
            (
                "CitadelAegis",
                "IronwallReprisal",
                "LastBastionSurge",
                "Stronghold",
            ),
        ),
    ),
    "Sorcerer": (
        ("School Affinity", ("Dispel", "WeakenMind")),
        ("Metamagic", ("Doublecast", "IceBlock")),
    ),
    "Wizard": (
        (
            "Arcane Mastery",
            ("ManaShield2", "Triplecast", "MirrorImage2", "Volitation", "Teleport"),
        ),
        ("Countermagic", ()),
    ),
    "Warlock": (
        (
            "Umbral Magic",
            (
                "Sleep",
                "ShadowBolt",
                "Eclipse",
                "Corruption",
                "Terrify",
                "ShadowBolt2",
                "Doom",
                "Dispel",
                "Hex",
            ),
        ),
        ("Sacrifice", ("HealthDrain", "LifeTap", "ManaDrain", "ResistHoly")),
        ("Pacts", ()),
    ),
    "Shadowcaster": (
        ("Umbral Debt", ("ManaTap", "HealthManaDrain")),
        ("Deep Shadow", ("ShadowBolt3", "Invisibility", "Nightmare", "Desoul")),
    ),
    "Demonologist": (
        (
            "Contracts",
            (
                "Corruption2",
                "Firebolt",
                "Netherchar",
                "Napalm",
                "SoulSiphon",
                "Desoul",
                "CurseElijah",
                "CurseDysarthria",
                "DemonEyes",
            ),
        ),
        ("Corruption", ()),
    ),
    "Spellblade": (
        (
            "Weapon Enhancements",
            ("CounterCharge", "Breakdown", "ManaSlice", "EnhanceBlade"),
        ),
        ("Armor Enhancements", ("Reflect", "NovelShielding", "EnhanceArmor")),
        (
            "Spell Enhancements",
            (
                "Boost",
                "KineticExplosion",
                "ManaTap",
                "AmplifyArcane",
                "AmplifyElemental",
                "StorageCapacity",
            ),
        ),
        ("Universal / Extra Abilities", ("TrueStrike", "Parry", "DoubleStrike")),
    ),
    "Knight Enchanter": (
        (
            "Assault Release",
            (
                "DoubleStrike",
                "CleavingEdge",
                "ReDebuff",
                "ResonantStrike",
                "ManaSlice2",
                "QuickRecharge",
            ),
        ),
        (
            "Aegis Release",
            (
                "EnhanceArmor",
                "DefensiveRelease",
                "ThirdEye",
                "AegisWeave",
                "WeaveReservoir",
                "ArcaneRiposte",
            ),
        ),
        (
            "Spellbind Release",
            (
                "ManaTap",
                "DispelSlash",
                "StorageCapacity2",
                "Spellbind",
                "EchoingBlade",
            ),
        ),
        (
            "Universal / Extra Abilities",
            ("Parry", "TruePiercingStrike", "TripleStrike"),
        ),
    ),
    "Conjurer": (
        (
            "Constructs",
            ("FloatingCrystal", "Torchlight", "ConjureElixir", "BarrierWall"),
        ),
        ("Binding", ("Sleep", "Silence", "Banish", "WeakenMind", "ManaBarbs")),
        (
            "Illusion / Movement",
            (
                "MirrorImage",
                "NightmareFuel",
                "Volitation",
                "Teleport",
                "ExplosiveDecoy",
            ),
        ),
        (
            "Calling",
            (
                "ConjureHumanoid",
                "ConjureMonster",
                "ConjureSpirit",
                "ConjureFiend",
                "ConjureCelestial",
                "ConjureDragon",
            ),
        ),
    ),
    "Thaumaturgist": (
        ("Calling", ()),
        ("Xenid Choice", ()),
        ("Xenid Ultimate", ()),
        ("Conduit", ("HealSummon", "ConduitCommand", "RaiseSummon")),
        (
            "Miracles",
            (
                "MiracleBlade",
                "MiracleShackles",
                "MiraclePotion",
                "MiracleCrystal",
            ),
        ),
    ),
    "Thief": (
        ("Fortune", ("ScavengersEye", "GoldToss")),
        ("Misfortune", ("Mug", "TurnTheTables")),
        ("Tools", ("Lockpick", "PilferingStrike")),
        ("Escape", ("CutAndRun",)),
    ),
    "Rogue": (
        ("Loaded Odds", ("FindersKeepers", "SlotMachine", "TripleStrike", "AllIn")),
        ("Comebacks", ("SneakAttack", "Zephyrstrike", "SnakeEyes", "CheatDeath")),
        ("Cunning", ("KeenEye", "MasterLockpick", "DisarmTraps", "DirtyTrick")),
        ("Escape", ("TakeItOnTheRun", "CutAndRun", "SmokeScreen", "EvasiveGuard")),
    ),
    "Inquisitor": (
        ("Case Journal", ("Reveal", "Inspect", "TakeNotes", "ExploitWeakness", "KeenEye")),
        (
            "Judgment",
            (
                "PiercingStrike",
                "TrueStrike",
                "Dispel",
                "Silence",
                "Enfeeble",
                "ShieldBlock",
                "Reflect",
            ),
        ),
        (
            "Elemental Wards",
            (
                "ResistFire",
                "ResistIce",
                "ResistElectric",
                "ResistWater",
                "ResistEarth",
                "ResistWind",
            ),
        ),
    ),
    "Seeker": (
        (
            "Wayfinding",
            ("Cartography", "Wayfinding", "SurveyorsStep", "Teleport", "EnterWall"),
        ),
        (
            "Safe Passage",
            ("Volitation", "SafePassage", "Sanctuary", "ResistAll"),
        ),
        (
            "Revelation",
            ("Inspect", "DeductiveStrike", "ForegoneConclusion"),
        ),
        (
            "Judgment",
            ("ThirdEye", "WeakenMind", "TripleStrike", "TruePiercingStrike"),
        ),
    ),
    "Assassin": (
        ("Death Mark", ("TripleStrike", "DeathMark")),
        ("Shadowcraft", ("Invisibility", "Lockpick")),
    ),
    "Ninja": (
        ("Utility", ("SmokeScreen", "Mug", "FindTraps", "SmashAndGrab")),
        (
            "Combat",
            (
                "TripleStrike",
                "Momentum",
                "MarkedShuriken",
                "FlurryBlades",
                "ExecutionRhythm",
                "ThousandCuts",
            ),
        ),
        (
            "Toxin / Death",
            (
                "ToxicPrecision",
                "LingeringVenom",
                "DeathSentence",
                "CoatingConservation",
                "Potentiation",
                "BlackLotusMastery",
            ),
        ),
        (
            "Stealth",
            (
                "Haste",
                "Invisibility",
                "SilentWalking",
                "Alacrity",
                "ShadowEvasion",
                "GhostStep",
            ),
        ),
        (
            "Defense",
            (
                "Parry",
                "Riposte",
                "Quickstep",
                "EvasiveGuard",
                "ShadowCounter",
                "Untouchable",
            ),
        ),
    ),
    "Spell Stealer": (
        ("Spell Theft", ("StealSpell", "WindSpeed", "Silence")),
        (
            "Stolen Charge",
            ("ImbueWeapon", "SpellbreakersCut", "StealAsWell", "BorrowedWard"),
        ),
    ),
    "Arcane Trickster": (
        ("Spell Theft", ("StealSpell2", "ArcaneAmbush")),
        ("Stolen Spell Mastery", ()),
        ("Misdirection", ("ThirdEye", "VanishingAct", "FalseOpening")),
    ),
    "Cleric": (
        (
            "Devotion",
            ("SanctuaryWard", "Bless", "PiousBounty"),
        ),
        ("Sacred Office", ("Smite", "Smite2", "TurnUndead2", "Cleanse")),
        ("Bulwark", ("ShieldSlam", "ShieldBlock", "BastionPrayer")),
        ("Judgment", ("TrueStrike", "DevotionalRebuke", "Silence")),
        ("Shared Ministry", ("SacredMending", "HallowedReadiness")),
    ),
    "Templar": (
        (
            "Relic Discipline",
            ("RelicAegis", "ShieldBlock", "LastStand"),
        ),
        (
            "Vanguard",
            (
                "Charge",
                "Goad",
                "ShieldSlam",
                "Parry",
                "PiercingStrike",
                "DoubleStrike",
                "TruePiercingStrike",
            ),
        ),
        (
            "Sacred Rites",
            ("Smite3", "Regen2", "Bless", "Dispel"),
        ),
        (
            "Judgment",
            ("DevotionalRebuke", "TrueStrike", "Holy2", "TurnUndead2", "Cleanse", "BastionPrayer"),
        ),
        ("Ordered Blessings", ()),
    ),
    "Hierophant": (
        (
            "Consecrated Conduit",
            ("StaffConduit", "ConduitStrike", "ConsecratedConduit", "Holy2"),
        ),
        ("Devotional Grace", ("Regen2", "GracefulIntercession", "Dispel")),
        (
            "Radiant Office",
            ("Smite3", "ResistShadow", "DevotionalRebuke", "TurnUndead2", "Cleanse", "Silence"),
        ),
        (
            "Pastoral Office",
            ("Heal2", "Bless", "SanctuaryWard", "Shell", "Reflect", "BastionPrayer"),
        ),
    ),
    "Monk": (
        (
            "Ki Assault",
            (
                "DoubleStrike",
                "FlowingPalm",
                "LegSweep",
                "TrueStrike",
                "Uppercut",
                "Headbutt",
            ),
        ),
        (
            "Ki Discipline",
            (
                "ChiHeal",
                "UnarmedProficiency",
                "MirrorBreath",
                "PurgingKata",
            ),
        ),
        ("Centering", ("PurityBody", "CenteredGuard", "Parry")),
        ("Open Hand", ("Headbutt", "DrunkenBrawler")),
    ),
    "Master Monk": (
        (
            "Perfected Flurry",
            ("Hyakuretsukyaku", "TripleStrike", "SpinningBackElbow"),
        ),
        ("Final Art", ("Hadouken", "Suplex", "DimMak")),
        ("Diamond Body", ("Evasion", "PurityBody2")),
        ("Rope-a-Dope", ("MartialMastery", "RopeADope")),
    ),
    "Priest": (
        ("Prayer", ("Supplication", "Holy2", "DazedOrConfused")),
        ("Exorcism", ("Dispel", "ExpelCurse", "Berserk")),
        (
            "Grace",
            ("DefensiveRegen", "Regen2", "MagicalInvigoration"),
        ),
        ("Protection", ("ManaShield", "Shell", "Cleanse", "Bless")),
    ),
    "Archbishop": (
        ("Benediction", ("GreatBenediction",)),
        ("Great Gospel", ("Doublecast", "Holy3", "Silence", "ManaShield2")),
        ("Intervention", ("Heal3", "Resurrection", "ExpelCurse")),
        ("Sustaining Grace", ("Regen3",)),
        ("Perfect Supplication", ()),
        ("Divine Intervention", ()),
    ),
    "Bard": (
        ("Performance", ("SongValor", "SongShelter", "SongRenewal")),
        ("Composition", ()),
    ),
    "Troubadour": (("Finale", ()), ("Mastery", ())),
    "Druid": (
        ("Panther Form", ("Transform", "MortalStrike")),
        ("Direbear Form", ("Transform2",)),
        ("Venom and Stone", ("PoisonDart", "ResistPoison", "NoxiousMist", "StoneSkin")),
        ("Growth and Stars", ("Regrowth", "RestoringBoon", "CalmingBreeze", "Starfall")),
        ("Primal Practice", ("PrimalPractice",)),
    ),
    "Lycan": (
        ("Frenzy", ("Transform3", "Charge", "BattleCry")),
        ("Moon Hunt", ("MortalStrike2", "LunarRend")),
        ("Dragon Essence", ("WingedPounce", "DragonFang")),
        ("Control", ("Dispel", "CenterBeast")),
    ),
    "Archdruid": (
        (
            "Venom",
            ("VilePotion", "PoisonBreath"),
        ),
        ("Stone", ("NatureShield",)),
        ("Growth", ("PlantSeeds", "ExpelCurse", "GrovePulse")),
        ("Storm", ("Bolt", "Windswept", "BallLightning", "FourfoldSurge")),
    ),
    "Diviner": (
        ("Rune Lore", ("Vulcanize", "Enfeeble", "Dispel")),
        ("Rune Flow", ("Haste", "Doublecast")),
        ("Foresight", ("LearnSpell", "Berserk")),
        ("Chronomancy", ("TemporaryStasis",)),
    ),
    "Astromancer": (
        ("Foresight Threads", ("Foretell", "TwistFate", "ThreadedCast", "Rewind")),
        ("Runic Constellations", ("Vulcanize", "WeakenMind", "Boost", "LearnSpell2")),
        ("Celestial Force", ("Wormhole", "Triplecast")),
        ("Lucid Utility", ("AccessStorage", "SilentLucidity")),
        ("Witnessed Magic", ("Tephra",)),
    ),
    "Shaman": (
        ("Totems", ("TotemSurge", "MaelstromWeapon")),
        (
            "Elements",
            (
                "ElementalStrike",
                "PiercingStrike",
                "TrueStrike",
                "DoubleStrike",
                "Hex",
                "Hydration",
                "AstralShift",
            ),
        ),
    ),
    "Soulcatcher": (
        ("Soul Communion", ("SoulDrain", "Desoul", "AbsorbEssence")),
        (
            "Totem Resonance",
            ("TotemSurge", "TripleStrike", "TruePiercingStrike", "Dispel", "Parry"),
        ),
    ),
    "Ranger": (
        ("Hunt", ("FavoredEnemy", "WildSense", "AggressivePursuit")),
        ("Companion Bond", ("DetectAnimal", "CreatureComforts")),
        ("Duelist / Ranged", ("Duelist", "Vision", "UncannyVolley")),
        ("Two-Handed Fighting", ("TwoHandedWeaponProficiency", "QuarryCleave", "TrueStrike")),
        ("Defense", ("Parry", "HuntersSnare")),
    ),
    "Beast Master": (
        ("Pack Tactics", ("PackStrike", "HarryPrey", "MendWounds")),
        ("Commands", ("Cover", "Zephyrstrike", "GuardPartner")),
    ),
}

PROMOTED_TREE_PROMOTION_PATHS = {
    "Weapon Master": {
        "Berserker": "Berserker",
        "Grandmaster of Arms": "Grandmaster",
    },
    "Paladin": {"Crusader": "Zeal"},
    "Lancer": {"Dragoon": "Aerial Tempo"},
    "Sentinel": {"Stalwart Defender": "Resolve"},
    "Sorcerer": {"Wizard": "School Affinity"},
    "Warlock": {"Shadowcaster": "Umbral Magic", "Demonologist": "Pacts"},
    "Spellblade": {"Knight Enchanter": "Weapon Enhancements"},
    "Conjurer": {"Thaumaturgist": "Calling"},
    "Thief": {"Rogue": "Fortune"},
    "Inquisitor": {"Seeker": "Case Journal"},
    "Assassin": {"Ninja": "Death Mark"},
    "Spell Stealer": {"Arcane Trickster": "Spell Theft"},
    "Cleric": {"Templar": "Bulwark", "Hierophant": "Devotion"},
    "Monk": {"Master Monk": "Ki"},
    "Priest": {"Archbishop": "Prayer"},
    "Bard": {"Troubadour": "Performance"},
    "Druid": {"Lycan": "Panther Form", "Archdruid": "Growth and Stars"},
    "Diviner": {"Astromancer": "Rune Lore"},
    "Shaman": {"Soulcatcher": "Totems"},
    "Ranger": {"Beast Master": "Companion Bond"},
}

# Fallback classification for promoted-class trees. These paths are only
# created when the class actually has relevant abilities or promotion targets;
# an Arcane column is therefore absent from purely martial trees.
ABILITY_BRANCH_OVERRIDES = {
    "Battle Cry": "Support",
    "Disarm": "Defense",
    "Natural Attunement": "Support",
    "Shield Slam": "Defense",
}

# The first two structured groups from docs/CLASS_STAT_PRIORITIES.md.  These
# groups are data rather than prose because promotion requirements consume them.
CLASS_STAT_GROUPS = {
    "Weapon Master": (("strength",), ("dex", "intel")),
    "Berserker": (("strength",), ("dex", "con")),
    "Grandmaster of Arms": (("dex",), ("strength", "intel")),
    "Paladin": (("con", "wisdom"), ("strength", "charisma")),
    "Crusader": (("strength", "con", "wisdom"), ("charisma",)),
    "Lancer": (("strength", "con"), ("dex", "charisma")),
    "Dragoon": (("strength", "con", "dex"), ("charisma",)),
    "Sentinel": (("con",), ("strength",)),
    "Stalwart Defender": (("con",), ("strength",)),
    "Sorcerer": (("intel",), ("wisdom",)),
    "Wizard": (("intel",), ("wisdom",)),
    "Warlock": (("intel", "charisma"), ("wisdom", "con")),
    "Shadowcaster": (("intel",), ("wisdom",)),
    "Demonologist": (("charisma", "intel", "wisdom"), ("con",)),
    "Spellblade": (("strength", "con"), ("intel", "charisma")),
    "Knight Enchanter": (("strength", "con"), ("intel", "dex", "charisma")),
    "Conjurer": (("charisma", "intel", "wisdom"), ("con", "dex")),
    "Thaumaturgist": (("charisma",), ("intel", "wisdom")),
    "Thief": (("dex", "charisma"), ("con", "intel")),
    "Rogue": (("dex",), ("charisma",)),
    "Inquisitor": (("strength", "con"), ("dex", "charisma")),
    "Seeker": (("strength", "con"), ("dex", "charisma", "intel")),
    "Assassin": (("dex",), ("charisma",)),
    "Ninja": (("dex",), ("charisma", "wisdom")),
    "Spell Stealer": (("intel", "dex"), ("wisdom", "charisma")),
    "Arcane Trickster": (("intel",), ("dex",)),
    "Cleric": (("wisdom", "con"), ("strength", "charisma")),
    "Templar": (("strength", "con"), ("wisdom", "dex", "charisma")),
    "Hierophant": (("wisdom", "intel"), ("con", "charisma")),
    "Monk": (("dex", "wisdom"), ("con",)),
    "Master Monk": (("dex", "wisdom"), ("con",)),
    "Priest": (("wisdom",), ("intel",)),
    "Archbishop": (("wisdom", "intel"), ("charisma",)),
    "Bard": (("charisma", "wisdom", "intel", "dex"), ("con", "strength")),
    "Troubadour": (("dex",), ("charisma", "wisdom", "intel", "con", "strength")),
    "Druid": (("wisdom", "dex"), ("intel", "con")),
    "Lycan": (("con", "dex"), ("strength", "wisdom", "charisma")),
    "Archdruid": (("intel",), ("wisdom",)),
    "Diviner": (("intel", "wisdom"), ("con", "charisma")),
    "Astromancer": (("intel",), ("wisdom",)),
    "Shaman": (("dex",), ("strength", "wisdom", "con", "charisma")),
    "Soulcatcher": (("strength", "dex"), ("wisdom", "con", "charisma")),
    "Ranger": (("strength", "dex"), ("con", "charisma")),
    "Beast Master": (("strength", "dex", "charisma"), ("con",)),
}

# Authored exceptions keep first-promotion paths comparable in total point
# investment without changing the shared rules for every other class.
FIRST_PROMOTION_STAT_REQUIREMENT_OVERRIDES = {
    "Weapon Master": {"strength": 14, "dex": 12, "intel": 11},
    "Lancer": {"strength": 13},
    "Sentinel": {"con": 15},
    "Paladin": {"wisdom": 13},
    "Sorcerer": {"intel": 15, "wisdom": 13},
    "Spellblade": {
        # A value at the baseline explicitly suppresses the generated
        # Strength requirement when promotion requirements are normalized.
        "strength": 10,
        "con": 11,
        "intel": 13,
        "charisma": 12,
    },
    "Warlock": {"intel": 13},
    "Conjurer": {"charisma": 12, "wisdom": 12},
    "Thief": {"charisma": 13},
    "Assassin": {"dex": 15, "charisma": 12},
    "Spell Stealer": {"dex": 13},
    "Inquisitor": {
        "strength": 13,
        "con": 13,
    },
    "Bard": {"charisma": 12, "wisdom": 12, "intel": 12, "dex": 12},
    "Cleric": {"con": 13},
    "Priest": {"wisdom": 14},
    "Druid": {
        "intel": 11,
        "wisdom": 13,
        "dex": 13,
    },
    "Monk": {
        "dex": 13,
        "wisdom": 12,
        # Suppress the generated Constitution requirement.
        "con": 10,
    },
    "Ranger": {"strength": 13, "dex": 13},
    "Shaman": {"dex": 14, "intel": 12},
}

# Complete second-promotion gates are authored independently so identity-heavy
# routes remain reachable with at least three unspent points at global level
# 60 from their documented Human lineage build.
SECOND_PROMOTION_STAT_REQUIREMENT_OVERRIDES = {
    "Berserker": {"strength": 18, "dex": 16, "con": 14},
    "Grandmaster of Arms": {"dex": 16, "intel": 13},
    "Crusader": {"strength": 15, "con": 17, "wisdom": 16, "charisma": 13},
    "Dragoon": {"strength": 17, "dex": 13},
    "Stalwart Defender": {"con": 20},
    "Wizard": {"intel": 20, "wisdom": 17},
    "Shadowcaster": {"intel": 18, "wisdom": 14},
    "Demonologist": {"charisma": 18, "intel": 17, "wisdom": 13},
    "Knight Enchanter": {
        "strength": 16,
        "con": 16,
        "intel": 15,
        "dex": 11,
    },
    "Thaumaturgist": {"charisma": 17, "intel": 16, "wisdom": 16},
    "Rogue": {"dex": 18, "charisma": 17},
    "Seeker": {
        "strength": 17,
        "con": 17,
        "dex": 14,
        "charisma": 14,
        "intel": 12,
    },
    "Ninja": {"dex": 21, "charisma": 16},
    "Arcane Trickster": {"intel": 17, "dex": 17},
    "Templar": {"strength": 13, "con": 18, "wisdom": 17},
    "Hierophant": {"wisdom": 18, "intel": 13, "con": 17, "charisma": 14},
    "Master Monk": {"strength": 20, "con": 14, "wisdom": 14, "dex": 12},
    "Archbishop": {"wisdom": 22, "intel": 16, "charisma": 14},
    "Troubadour": {"dex": 16, "charisma": 16, "wisdom": 15, "intel": 15},
    "Lycan": {"con": 15, "dex": 16, "strength": 14},
    "Archdruid": {"intel": 15, "wisdom": 14},
    "Astromancer": {"intel": 18, "wisdom": 17},
    "Soulcatcher": {"strength": 13, "dex": 21, "wisdom": 13},
    "Beast Master": {"strength": 17, "dex": 17, "charisma": 14, "con": 13},
}

# These abilities remain owned by their dedicated reward/bond systems.  They
# are intentionally excluded from point-purchased ordinary catalog coverage.
EXTERNAL_ACQUISITION_ABILITIES = frozenset(
    {
        "Abyssal Covenant",
        "Arcane Blast",
        "Arsenal Mastery",
        "Astral Judgment",
        "Blade of Fatalities",
        "Blood Rage",
        "Call Contract",
        "Citadel Aegis",
        "Dim Mak",
        "Divine Aegis",
        "Draconic Onslaught",
        "Eternal Conduit",
        "Eyes of the Unseen",
        "Familiar",
        "Great Gospel",
        "Holy Retribution",
        "Invoke Agloolik",
        "Invoke Bardi",
        "Invoke Caladrius",
        "Invoke Cacus",
        "Invoke Dilong",
        "Invoke Hala",
        "Invoke Hodag",
        "Invoke Izulu",
        "Invoke Kobalos",
        "Invoke Lamashtu",
        "Invoke Patagon",
        "Invoke Seraphim",
        "Invoke Tiamat",
        "Invoke Zahhak",
        "Ironwall Reprisal",
        "Ironwall Revenge",
        "Last Bastion",
        "Lunar Frenzy",
        "Melody of Inspiration",
        "Pack Bond",
        "Primal Ascendance",
        "Sacred Overchannel",
        "Shade of Ahool",
        "Shield Mastery",
        "Soul Harvest",
        "Spell Mastery",
        "Stroke of Luck",
        "Stronghold",
        "Tame",
        "Totem",
        "Trickster's Gambit",
    }
)
