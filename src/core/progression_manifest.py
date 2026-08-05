"""Canonical metadata used to build player ability trees.

Combat implementation remains in ``core.abilities``.  This module only owns
progression layout and stat-gate metadata, keeping progression concerns out of
the combat ability catalog.
"""

from __future__ import annotations


TREE_LANES = ("Martial", "Arcane", "Defense", "Support")

STAGE_SIZE_RANGES = {
    1: (10, 25),
    2: (12, 20),
    3: (10, 18),
}

TREE_SIZE_OVERRIDES = {
    # Eight independent discipline-gated weapon arts sit beside the two
    # ordinary Weapon Master routes.
    "Weapon Master": (33, 33),
    # Two development paths, three independent nodes, and eight art upgrades.
    "Berserker": (21, 21),
    # Eight three-rank weapon-art chains plus three floating mastery entries.
    "Grandmaster of Arms": (27, 27),
    # Dragoon retains all 16 Lancer development nodes and adds 11 mastery nodes.
    "Dragoon": (27, 27),
    # Four compact terminal paths, including retained Repel the Wicked.
    "Crusader": (19, 19),
}

ABILITY_ICON_KEYS = frozenset({
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
})

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

# The Warrior tree is the first fully authored talent graph. Each tuple is:
# path name, promotion target, then ordered node specs of
# (kind, payload identifier, icon key). Path names remain useful metadata for
# diagnostics but are intentionally not rendered above Pygame columns.
WARRIOR_TREE_PATHS = (
    (
        "Arms",
        "Weapon Master",
        (
            ("ability", "PiercingStrike", "skill_offense"),
            ("ability", "Charge", "skill_mobility"),
            ("ability", "WeaponFocus", "skill_passive"),
            ("rating", "Attack", "rating_attack"),
            ("ability", "Cripple", "skill_control"),
            ("ability", "TrueStrike", "skill_offense"),
        ),
    ),
    (
        "Vanguard",
        "Lancer",
        (
            ("ability", "DrivingThrust", "skill_offense"),
            ("rating", "Defense", "rating_defense"),
            ("ability", "Retaliate", "skill_defense"),
        ),
    ),
    (
        "Bulwark",
        "Sentinel",
        (
            ("ability", "ShieldSlam", "skill_defense"),
            ("ability", "ShieldBlock", "skill_defense"),
            ("ability", "Rally", "skill_support"),
            ("rating", "Defense", "rating_defense"),
            ("ability", "Dishearten", "skill_control"),
            ("health", "Health", "skill_defense"),
        ),
    ),
    (
        "Command",
        "Paladin",
        (
            ("ability", "Goad", "skill_control"),
            ("rating", "Magic Defense", "rating_magic_defense"),
            ("ability", "Chastise", "skill_passive"),
        ),
    ),
)

# Paladin begins after the shared Bulwark/Command trunk has reached row three.
WARRIOR_PATH_ROW_OFFSETS = {
    "Lancer": 3,
    "Paladin": 3,
}

# Explicit geometry lets the defensive paths share a central trunk while
# keeping Shield Slam as an early Sentinel/Lancer side requirement.
WARRIOR_NODE_POSITION_OVERRIDES = {
    ("Weapon Master", "PiercingStrike"): (0.5, 1),
    ("Weapon Master", "Charge"): (0.5, 2),
    ("Weapon Master", "WeaponFocus"): (0.5, 3),
    ("Weapon Master", "Attack"): (0, 4),
    ("Weapon Master", "Cripple"): (0, 5),
    ("Weapon Master", "TrueStrike"): (0, 6),
    ("Lancer", "DrivingThrust"): (1, 4),
    ("Lancer", "Defense"): (1, 5),
    ("Lancer", "Retaliate"): (1, 6),
    ("Sentinel", "ShieldSlam"): (2.5, 1),
    ("Sentinel", "ShieldBlock"): (2.5, 2),
    ("Sentinel", "Rally"): (2.5, 3),
    ("Sentinel", "Defense"): (2, 4),
    ("Sentinel", "Dishearten"): (2, 5),
    ("Sentinel", "Health"): (2, 6),
}

WARRIOR_FLOATING_NODES = (
    ("ability", "Disarm", "skill_control", (4, 1)),
    ("ability", "BattleCry", "skill_support", (4, 2)),
    ("ability", "Adrenaline", "skill_support", (4, 3)),
    ("ability", "HonedAttack", "skill_passive", (4, 4)),
    ("ability", "DoubleStrike", "skill_offense", (4, 5)),
    ("ability", "Parry", "skill_defense", (4, 6)),
)

WARRIOR_NODE_LEVEL_REQUIREMENTS = {
    "Charge": 5,
    "WeaponFocus": 10,
    "Goad": 10,
    "Adrenaline": 10,
    "DrivingThrust": 15,
    "Dishearten": 15,
    "HonedAttack": 15,
    "Chastise": 20,
    "Cripple": 20,
    "DoubleStrike": 20,
    "TrueStrike": 25,
    "Retaliate": 25,
    "Parry": 25,
}

# Cross-path requirements can join an ordinary node or promotion. Required
# nodes use (promotion target, manifest identifier) so rating nodes can be
# referenced without depending on generated IDs.
WARRIOR_NODE_CROSS_REQUIREMENTS = {
    "Retaliate": (("Sentinel", "ShieldBlock"),),
    "Goad": (("Sentinel", "Rally"),),
}

# Cross-path connector channels are expressed as tree-column coordinates.
# Retaliate's Bulwark requirement routes between the Lancer and Sentinel
# columns instead of following Shield Block's half-column position.
WARRIOR_CONNECTOR_CHANNEL_OVERRIDES = {
    ("Retaliate", "ShieldBlock"): 1.5,
}

# Reserved for authored nodes that diverge from their manifest sequence.
WARRIOR_NODE_PREREQUISITE_OVERRIDES = {
    "DrivingThrust": (("Weapon Master", "WeaponFocus"),),
}

# Promotion nodes only require their completed authored path. Cross-path gates
# occur at the exact development node where the paths join.
WARRIOR_PROMOTION_CROSS_REQUIREMENTS = {}

# Weapon Master is intentionally asymmetric. The weapon-art column is
# independent of both promotion routes, while the Grandmaster route forks into
# permanently exclusive Dual Wield and Duelist styles before rejoining.
WEAPON_MASTER_TREE_NODE_SPECS = (
    {
        "id": "double-strike",
        "kind": "ability",
        "identifier": "DoubleStrike",
        "lane": "Berserker",
        "position": (0, 0),
        "owned_if_known": True,
    },
    {
        "id": "attack-1",
        "kind": "rating",
        "identifier": "Attack",
        "lane": "Berserker",
        "position": (0, 1),
        "prerequisites": ("double-strike",),
    },
    {
        "id": "two-handed-weapon-proficiency",
        "kind": "ability",
        "identifier": "TwoHandedWeaponProficiency",
        "lane": "Berserker",
        "position": (0, 2),
        "level": 35,
        "prerequisites": ("attack-1",),
    },
    {
        "id": "mortal-strike",
        "kind": "ability",
        "identifier": "MortalStrike",
        "lane": "Berserker",
        "position": (0, 4),
        "level": 45,
        "prerequisites": ("two-handed-weapon-proficiency",),
    },
    {
        "id": "devastating-throw",
        "kind": "ability",
        "identifier": "DevastatingThrow",
        "lane": "Berserker",
        "position": (0, 5),
        "level": 50,
        "prerequisites": ("mortal-strike",),
    },
    {
        "id": "brutish-strength",
        "kind": "ability",
        "identifier": "BrutishStrength",
        "lane": "Berserker",
        "position": (0, 6),
        "level": 55,
        "prerequisites": ("devastating-throw",),
    },
    {
        "id": "parry",
        "kind": "ability",
        "identifier": "Parry",
        "lane": "Grandmaster",
        "position": (1.5, 0),
        "owned_if_known": True,
    },
    {
        "id": "defense-1",
        "kind": "rating",
        "identifier": "Defense",
        "lane": "Grandmaster",
        "position": (1.5, 1),
        "prerequisites": ("parry",),
    },
    {
        "id": "dual-wield",
        "kind": "ability",
        "identifier": "DualWield",
        "lane": "Dual Wield",
        "position": (1, 2),
        "level": 35,
        "prerequisites": ("defense-1",),
        "exclusive_group": "weapon-master.style",
    },
    {
        "id": "honed-attack",
        "kind": "ability",
        "identifier": "HonedAttack",
        "lane": "Dual Wield",
        "position": (1, 3),
        "level": 40,
        "prerequisites": ("dual-wield",),
        "stack_if_known": True,
    },
    {
        "id": "momentum",
        "kind": "ability",
        "identifier": "Momentum",
        "lane": "Dual Wield",
        "position": (1, 4),
        "level": 45,
        "prerequisites": ("honed-attack",),
    },
    {
        "id": "cross-block",
        "kind": "ability",
        "identifier": "CrossBlock",
        "lane": "Dual Wield",
        "position": (1, 5),
        "level": 50,
        "prerequisites": ("momentum",),
    },
    {
        "id": "duelist",
        "kind": "ability",
        "identifier": "Duelist",
        "lane": "Duelist",
        "position": (2, 2),
        "level": 35,
        "prerequisites": ("defense-1",),
        "exclusive_group": "weapon-master.style",
    },
    {
        "id": "blind-fighting",
        "kind": "ability",
        "identifier": "BlindFighting",
        "lane": "Duelist",
        "position": (2, 3),
        "level": 40,
        "prerequisites": ("duelist",),
    },
    {
        "id": "retort",
        "kind": "ability",
        "identifier": "Retort",
        "lane": "Duelist",
        "position": (2, 4),
        "level": 45,
        "prerequisites": ("blind-fighting",),
    },
    {
        "id": "maim",
        "kind": "ability",
        "identifier": "Maim",
        "lane": "Duelist",
        "position": (2, 5),
        "level": 50,
        "prerequisites": ("retort",),
    },
    {
        "id": "true-piercing-strike",
        "kind": "ability",
        "identifier": "TruePiercingStrike",
        "lane": "Grandmaster",
        "position": (1.5, 6),
        "level": 55,
        "prerequisites": ("cross-block", "maim"),
        "prerequisite_mode": "any",
    },
    *(
        {
            "id": node_id,
            "kind": "ability",
            "identifier": identifier,
            "lane": "Weapon Arts",
            "position": (3, row),
            "weapon_specialization": (weapon_type, 1),
        }
        for row, (node_id, identifier, weapon_type) in enumerate((
            ("iron-palm", "IronPalm", "Fist"),
            ("hemorrhage", "Hemorrhage", "Dagger"),
            ("riposte-line", "RiposteLine", "Sword"),
            ("low-sweep", "LowSweep", "Club"),
            ("guard-cleaver", "GuardCleaver", "Longsword"),
            ("reavers-mark", "ReaversMark", "Battle Axe"),
            ("brace", "Brace", "Polearm"),
            ("anvil-strike", "AnvilStrike", "Hammer"),
        ))
    ),
    *(
        {
            "id": f"{node_id}-2",
            "kind": "ability",
            "identifier": f"{identifier}2",
            "lane": "Weapon Arts",
            "position": (4, row),
            "prerequisites": (node_id,),
            "weapon_specialization": (weapon_type, 5),
        }
        for row, (node_id, identifier, weapon_type) in enumerate((
            ("iron-palm", "IronPalm", "Fist"),
            ("hemorrhage", "Hemorrhage", "Dagger"),
            ("riposte-line", "RiposteLine", "Sword"),
            ("low-sweep", "LowSweep", "Club"),
            ("guard-cleaver", "GuardCleaver", "Longsword"),
            ("reavers-mark", "ReaversMark", "Battle Axe"),
            ("brace", "Brace", "Polearm"),
            ("anvil-strike", "AnvilStrike", "Hammer"),
        ))
    ),
)

WEAPON_DISCIPLINE_ARTS = (
    ("iron-palm", "IronPalm", "Fist"),
    ("hemorrhage", "Hemorrhage", "Dagger"),
    ("riposte-line", "RiposteLine", "Sword"),
    ("low-sweep", "LowSweep", "Club"),
    ("guard-cleaver", "GuardCleaver", "Longsword"),
    ("reavers-mark", "ReaversMark", "Battle Axe"),
    ("brace", "Brace", "Polearm"),
    ("anvil-strike", "AnvilStrike", "Hammer"),
)

BERSERKER_TREE_NODE_SPECS = (
    {
        "id": "final-assault",
        "kind": "ability",
        "identifier": "FinalAssault",
        "lane": "Survival",
        "position": (0, 1),
        "available_on_promotion": True,
    },
    {
        "id": "monkey-grip",
        "kind": "ability",
        "identifier": "MonkeyGrip",
        "name": "Monkey Grip 1",
        "lane": "Survival",
        "position": (0, 2),
        "level": 65,
        "prerequisites": ("final-assault",),
    },
    {
        "id": "attack-1",
        "kind": "rating",
        "identifier": "Attack",
        "lane": "Survival",
        "position": (0, 3),
        "prerequisites": ("monkey-grip",),
    },
    {
        "id": "reckless-onslaught",
        "kind": "ability",
        "identifier": "RecklessOnslaught",
        "lane": "Survival",
        "position": (0, 4),
        "level": 70,
        "prerequisites": ("attack-1",),
    },
    {
        "id": "monkey-grip-2",
        "kind": "ability",
        "identifier": "MonkeyGrip2",
        "lane": "Survival",
        "position": (0, 5),
        "level": 75,
        "prerequisites": ("reckless-onslaught",),
    },
    {
        "id": "frenzy",
        "kind": "ability",
        "identifier": "Frenzy",
        "lane": "Fury",
        "position": (1, 1),
        "available_on_promotion": True,
    },
    {
        "id": "health-1",
        "kind": "health",
        "identifier": "Health",
        "lane": "Fury",
        "position": (1, 2),
        "prerequisites": ("frenzy",),
    },
    {
        "id": "mortal-strike-2",
        "kind": "ability",
        "identifier": "MortalStrike2",
        "name": "Mortal Strike 2",
        "lane": "Fury",
        "position": (1, 3),
        "level": 65,
        "prerequisites": ("health-1",),
    },
    {
        "id": "boomerang-toss",
        "kind": "ability",
        "identifier": "BoomerangToss",
        "lane": "Fury",
        "position": (1, 4),
        "level": 70,
        "prerequisites": ("mortal-strike-2",),
    },
    {
        "id": "triple-strike",
        "kind": "ability",
        "identifier": "TripleStrike",
        "lane": "Fury",
        "position": (1, 5),
        "level": 75,
        "prerequisites": ("boomerang-toss",),
    },
    {
        "id": "parry",
        "kind": "ability",
        "identifier": "Parry",
        "lane": "Independent",
        "position": (2, 2),
        "owned_if_known": True,
    },
    {
        "id": "pain-tolerance",
        "kind": "ability",
        "identifier": "PainTolerance",
        "lane": "Independent",
        "position": (2, 3),
        "level": 65,
    },
    {
        "id": "hemorrhage-thirst",
        "kind": "ability",
        "identifier": "HemorrhageThirst",
        "lane": "Independent",
        "position": (2, 4),
        "level": 70,
    },
    *(
        {
            "id": node_id,
            "kind": "ability",
            "identifier": identifier,
            "lane": "Weapon Arts",
            "position": (3, row + 2),
            "owned_if_known": True,
            "weapon_specialization": (weapon_type, 1),
        }
        for row, (node_id, identifier, weapon_type) in enumerate(
            WEAPON_DISCIPLINE_ARTS[4:]
        )
    ),
    *(
        {
            "id": f"{node_id}-2",
            "kind": "ability",
            "identifier": f"{identifier}2",
            "lane": "Weapon Arts",
            "position": (4, row + 2),
            "prerequisites": (node_id,),
            "owned_if_known": True,
            "weapon_specialization": (weapon_type, 5),
        }
        for row, (node_id, identifier, weapon_type) in enumerate(
            WEAPON_DISCIPLINE_ARTS[4:]
        )
    ),
)

GRANDMASTER_TREE_NODE_SPECS = (
    *(
        {
            "id": node_id,
            "kind": "ability",
            "identifier": identifier,
            "lane": "Weapon Arts",
            "position": (0, row),
            "owned_if_known": True,
            "weapon_specialization": (weapon_type, 1),
        }
        for row, (node_id, identifier, weapon_type) in enumerate(
            WEAPON_DISCIPLINE_ARTS
        )
    ),
    *(
        {
            "id": f"{node_id}-2",
            "kind": "ability",
            "identifier": f"{identifier}2",
            "lane": "Weapon Arts",
            "position": (1, row),
            "prerequisites": (node_id,),
            "owned_if_known": True,
            "weapon_specialization": (weapon_type, 5),
        }
        for row, (node_id, identifier, weapon_type) in enumerate(
            WEAPON_DISCIPLINE_ARTS
        )
    ),
    *(
        {
            "id": f"{node_id}-3",
            "kind": "ability",
            "identifier": f"{identifier}3",
            "lane": "Weapon Arts",
            "position": (2, row),
            "prerequisites": (f"{node_id}-2",),
            "owned_if_known": True,
            "weapon_specialization": (weapon_type, 10),
        }
        for row, (node_id, identifier, weapon_type) in enumerate(
            WEAPON_DISCIPLINE_ARTS
        )
    ),
    {
        "id": "double-strike",
        "kind": "ability",
        "identifier": "DoubleStrike",
        "lane": "Mastery",
        "position": (3, 3),
        "owned_if_known": True,
    },
    {
        "id": "perfect-form",
        "kind": "talent",
        "identifier": "grandmaster.perfect-form",
        "name": "Perfect Form",
        "lane": "Mastery",
        "position": (3, 2),
        "available_on_promotion": True,
        "description": (
            "Increase weapon damage by 1% and hit chance by 0.5% per rank "
            "of the equipped weapon's discipline."
        ),
    },
    {
        "id": "adaptive-arsenal",
        "kind": "talent",
        "identifier": "grandmaster.adaptive-arsenal",
        "name": "Adaptive Arsenal",
        "lane": "Mastery",
        "position": (3, 5),
        "available_on_promotion": True,
        "description": (
            "Increase parry chance by 0.5% and counterattack critical chance "
            "by 1% per rank of the equipped weapon's discipline."
        ),
    },
)

# Lancer and Dragoon use explicit graphs because Jump modifications are
# progression purchases rather than spellbook abilities. Modifier nodes keep
# stable ``*.jump-mod.*`` IDs and unlock configuration on the learned Jump.
LANCER_TREE_NODE_SPECS = (
    {
        "id": "jump",
        "kind": "ability",
        "identifier": "Jump",
        "lane": "Jump Core",
        "position": (1, 0),
        "available_on_promotion": True,
    },
    {
        "id": "aerial-footwork",
        "kind": "talent",
        "identifier": "lancer.aerial-footwork",
        "name": "Aerial Footwork",
        "lane": "Assault Mods",
        "position": (2, 1),
        "level": 35,
        "prerequisites": ("jump",),
        "description": (
            "Permanently increase Attack by 20 and Aerial Tempo capacity by 1."
        ),
        "bonuses": {"ratings": {"Attack": 20}},
        "kit_effect": ("meter_cap", "aerial_tempo", 1),
    },
    {
        "id": "grounded-landing",
        "kind": "talent",
        "identifier": "lancer.grounded-landing",
        "name": "Grounded Landing",
        "lane": "Guard Mods",
        "position": (0, 3),
        "level": 45,
        "prerequisites": ("acrobat",),
        "description": (
            "Permanently increase Defense by 20 and reduce final incoming "
            "damage by 10% while Jump is charging."
        ),
        "bonuses": {"ratings": {"Defense": 20}},
    },
    {
        "id": "polearm-proficiency",
        "kind": "ability",
        "identifier": "PolearmProficiency",
        "lane": "Polearm Discipline",
        "position": (4, 0),
        "available_on_promotion": True,
    },
    {
        "id": "lance-sweep",
        "kind": "ability",
        "identifier": "LanceSweep",
        "lane": "Polearm Discipline",
        "position": (4, 1),
        "level": 35,
        "prerequisites": ("polearm-proficiency",),
    },
    {
        "id": "zephyrstrike",
        "kind": "ability",
        "identifier": "Zephyrstrike",
        "lane": "Polearm Discipline",
        "position": (4, 3),
        "level": 40,
        "prerequisites": ("health-1",),
    },
    {
        "id": "health-1",
        "kind": "health",
        "identifier": "Health",
        "lane": "Polearm Discipline",
        "position": (4, 2),
        "prerequisites": ("lance-sweep",),
    },
    {
        "id": "defense-1",
        "kind": "rating",
        "identifier": "Defense",
        "lane": "Guard Mods",
        "position": (1, 2),
        "prerequisites": ("jump",),
    },
    {
        "id": "defend",
        "kind": "jump_mod",
        "identifier": "lancer.jump-mod.defend",
        "name": "Defend",
        "jump_modification": "Defend",
        "lane": "Guard Mods",
        "position": (0, 1),
        "level": 35,
        "prerequisites": ("jump",),
    },
    {
        "id": "acrobat",
        "kind": "jump_mod",
        "identifier": "lancer.jump-mod.acrobat",
        "name": "Acrobat",
        "jump_modification": "Acrobat",
        "lane": "Guard Mods",
        "position": (0, 2),
        "level": 40,
        "prerequisites": ("defend",),
    },
    {
        "id": "quick-dive",
        "kind": "jump_mod",
        "identifier": "lancer.jump-mod.quick-dive",
        "name": "Quick Dive",
        "jump_modification": "Quick Dive",
        "lane": "Assault Mods",
        "position": (2, 2),
        "level": 40,
        "prerequisites": ("aerial-footwork",),
    },
    {
        "id": "attack-1",
        "kind": "rating",
        "identifier": "Attack",
        "lane": "Assault Mods",
        "position": (1, 3),
        "prerequisites": ("defense-1",),
    },
    {
        "id": "thrust",
        "kind": "jump_mod",
        "identifier": "lancer.jump-mod.thrust",
        "name": "Thrust",
        "jump_modification": "Thrust",
        "lane": "Assault Mods",
        "position": (2, 3),
        "level": 45,
        "prerequisites": ("quick-dive",),
    },
    {
        "id": "rend",
        "kind": "jump_mod",
        "identifier": "lancer.jump-mod.rend",
        "name": "Rend",
        "jump_modification": "Rend",
        "lane": "Assault Mods",
        "position": (2, 4),
        "level": 50,
        "prerequisites": ("thrust",),
    },
    {
        "id": "parry",
        "kind": "ability",
        "identifier": "Parry",
        "lane": "Unbound",
        "position": (5, 2),
        "owned_if_known": True,
    },
    {
        "id": "true-strike",
        "kind": "ability",
        "identifier": "TrueStrike",
        "lane": "Unbound",
        "position": (5, 3),
        "owned_if_known": True,
    },
)

DRAGOON_TREE_NODE_SPECS = (
    {
        "id": "polearm-excellence",
        "kind": "ability",
        "identifier": "PolearmExcellence",
        "lane": "Polearm Discipline",
        "position": (4, 5),
        "available_on_promotion": True,
    },
    {
        "id": "attack-1",
        "kind": "rating",
        "identifier": "Attack",
        "lane": "Polearm Discipline",
        "position": (4, 6),
        "prerequisites": ("polearm-excellence",),
    },
    {
        "id": "true-piercing-strike",
        "kind": "ability",
        "identifier": "TruePiercingStrike",
        "lane": "Polearm Discipline",
        "position": (4, 7),
        "level": 70,
        "prerequisites": ("attack-1",),
    },
    {
        "id": "polearm-mastery",
        "kind": "ability",
        "identifier": "PolearmMastery",
        "lane": "Polearm Discipline",
        "position": (5, 7),
        "level": 75,
        "prerequisites": ("true-piercing-strike",),
    },
    {
        "id": "quake",
        "kind": "jump_mod",
        "identifier": "dragoon.jump-mod.quake",
        "name": "Quake",
        "jump_modification": "Quake",
        "lane": "Assault Mods",
        "position": (2, 6),
        "level": 65,
        "prerequisites": ("lancer.jump-mod.rend",),
    },
    {
        "id": "soaring-strike",
        "kind": "jump_mod",
        "identifier": "dragoon.jump-mod.soaring-strike",
        "name": "Soaring Strike",
        "jump_modification": "Soaring Strike",
        "lane": "Assault Mods",
        "position": (2, 7),
        "level": 70,
        "prerequisites": ("quake",),
    },
    {
        "id": "dragons-ascent",
        "kind": "talent",
        "identifier": "dragoon.dragons-ascent",
        "name": "Dragon's Ascent",
        "lane": "Assault Mods",
        "position": (1, 5),
        "prerequisites": ("lancer.rating.attack-1",),
        "available_on_promotion": True,
        "description": (
            "Permanently increase Attack by 30. A clean Soaring Strike "
            "landing grants 2 Aerial Tempo."
        ),
        "bonuses": {"ratings": {"Attack": 30}},
    },
    {
        "id": "dragon-dive",
        "kind": "ability",
        "identifier": "DragonDive",
        "lane": "Guard Mods",
        "position": (1, 7),
        "level": 80,
        "prerequisites": (
            "dragons-ascent",
            "soaring-strike",
            "unstoppable",
        ),
    },
    {
        "id": "defense-1",
        "kind": "rating",
        "identifier": "Defense",
        "lane": "Guard Mods",
        "position": (1, 6),
        "prerequisites": ("dragons-ascent",),
    },
    {
        "id": "retribution",
        "kind": "jump_mod",
        "identifier": "dragoon.jump-mod.retribution",
        "name": "Retribution",
        "jump_modification": "Retribution",
        "lane": "Guard Mods",
        "position": (0, 6),
        "level": 65,
        "prerequisites": ("lancer.talent.grounded-landing",),
    },
    {
        "id": "unstoppable",
        "kind": "jump_mod",
        "identifier": "dragoon.jump-mod.unstoppable",
        "name": "Unstoppable",
        "jump_modification": "Unstoppable",
        "lane": "Guard Mods",
        "position": (0, 7),
        "level": 70,
        "prerequisites": ("retribution",),
    },
)

# Sentinel, Stalwart Defender, Paladin, and Crusader use compact authored
# graphs. First-promotion trees close after promotion; terminal trees contain
# only their new development nodes.
SENTINEL_TREE_NODE_SPECS = (
    {
        "id": "goad",
        "kind": "ability",
        "identifier": "Goad",
        "lane": "Counter",
        "position": (0, 0),
        "available_on_promotion": True,
        "owned_if_known": True,
    },
    {
        "id": "shield-check",
        "kind": "ability",
        "identifier": "ShieldBash",
        "lane": "Counter",
        "position": (0, 1),
        "level": 35,
        "prerequisites": ("goad",),
    },
    {
        "id": "retaliate",
        "kind": "ability",
        "identifier": "Retaliate",
        "lane": "Counter",
        "position": (0, 2),
        "level": 40,
        "prerequisites": ("shield-check",),
        "owned_if_known": True,
    },
    {
        "id": "shield-riposte",
        "kind": "ability",
        "identifier": "ShieldRiposte",
        "lane": "Counter",
        "position": (0, 3),
        "level": 45,
        "prerequisites": ("retaliate",),
    },
    {
        "id": "watchful-reprisal",
        "kind": "talent",
        "identifier": "sentinel.watchful-reprisal",
        "name": "Watchful Reprisal",
        "lane": "Counter",
        "position": (0, 4),
        "level": 50,
        "prerequisites": ("shield-riposte",),
        "description": (
            "Permanently increase Attack by 20 and Retaliate chance by "
            "10 percentage points."
        ),
        "bonuses": {"ratings": {"Attack": 20}},
    },
    {
        "id": "attack-1",
        "kind": "rating",
        "identifier": "Attack",
        "lane": "Counter",
        "position": (0, 5),
        "prerequisites": ("watchful-reprisal",),
    },
    {
        "id": "hold-the-line",
        "kind": "ability",
        "identifier": "HoldTheLine",
        "lane": "Wall",
        "position": (2, 0),
        "available_on_promotion": True,
    },
    {
        "id": "brace-wall",
        "kind": "ability",
        "identifier": "BraceWall",
        "lane": "Wall",
        "position": (2, 1),
        "level": 35,
        "prerequisites": ("hold-the-line",),
    },
    {
        "id": "covering-guard",
        "kind": "ability",
        "identifier": "CoveringGuard",
        "lane": "Wall",
        "position": (2, 2),
        "level": 40,
        "prerequisites": ("brace-wall",),
    },
    {
        "id": "bulwark",
        "kind": "ability",
        "identifier": "Bulwark",
        "lane": "Wall",
        "position": (2, 3),
        "level": 45,
        "prerequisites": ("covering-guard",),
    },
    {
        "id": "resolute-guard",
        "kind": "talent",
        "identifier": "sentinel.resolute-guard",
        "name": "Resolute Guard",
        "lane": "Wall",
        "position": (2, 4),
        "level": 50,
        "prerequisites": ("bulwark",),
        "description": (
            "Permanently increase Defense by 20 and improve Hold the Line's "
            "block and mitigation by 5 percentage points."
        ),
        "bonuses": {"ratings": {"Defense": 20}},
    },
    {
        "id": "defense-1",
        "kind": "rating",
        "identifier": "Defense",
        "lane": "Wall",
        "position": (2, 5),
        "prerequisites": ("resolute-guard",),
    },
    {
        "id": "deflect-spell",
        "kind": "ability",
        "identifier": "SpellReflection",
        "lane": "Spell Defense",
        "position": (4, 0),
        "available_on_promotion": True,
        "owned_if_known": True,
    },
    {
        "id": "magic-defense-1",
        "kind": "rating",
        "identifier": "Magic Defense",
        "lane": "Spell Defense",
        "position": (4, 1),
        "prerequisites": ("deflect-spell",),
    },
    {
        "id": "health-1",
        "kind": "health",
        "identifier": "Health",
        "lane": "Spell Defense",
        "position": (4, 2),
        "prerequisites": ("magic-defense-1",),
    },
)

STALWART_DEFENDER_TREE_NODE_SPECS = (
    {
        "id": "last-stand",
        "kind": "ability",
        "identifier": "LastStand",
        "lane": "Last Stand",
        "position": (0, 0),
        "available_on_promotion": True,
    },
    {
        "id": "unbroken-wall",
        "kind": "talent",
        "identifier": "stalwart.unbroken-wall",
        "name": "Unbroken Wall",
        "lane": "Last Stand",
        "position": (0, 1),
        "level": 65,
        "prerequisites": ("last-stand",),
        "description": (
            "Permanently increase Defense by 30. Last Stand gains 10 "
            "percentage points of block chance and 50% more Resolve gain."
        ),
        "bonuses": {"ratings": {"Defense": 30}},
    },
    {
        "id": "defense-1",
        "kind": "rating",
        "identifier": "Defense",
        "lane": "Last Stand",
        "position": (0, 2),
        "prerequisites": ("unbroken-wall",),
    },
    {
        "id": "health-1",
        "kind": "health",
        "identifier": "Health",
        "lane": "Last Stand",
        "position": (0, 3),
        "prerequisites": ("defense-1",),
    },
    {
        "id": "punishing-guard",
        "kind": "talent",
        "identifier": "stalwart.punishing-guard",
        "name": "Punishing Guard",
        "lane": "Counter Mastery",
        "position": (2, 0),
        "available_on_promotion": True,
        "description": (
            "Permanently increase Attack by 30 and raise Shield Riposte "
            "weapon damage to 1.0x."
        ),
        "bonuses": {"ratings": {"Attack": 30}},
    },
    {
        "id": "attack-1",
        "kind": "rating",
        "identifier": "Attack",
        "lane": "Counter Mastery",
        "position": (2, 1),
        "prerequisites": ("punishing-guard",),
    },
    {
        "id": "fortified-citadel",
        "kind": "talent",
        "identifier": "stalwart.fortified-citadel",
        "name": "Fortified Citadel",
        "lane": "Surge Mastery",
        "position": (3, 0),
        "level": 65,
        "description": (
            "Citadel Aegis grants a 125-point barrier and a four-turn "
            "defensive stance."
        ),
    },
    {
        "id": "crushing-reprisal",
        "kind": "talent",
        "identifier": "stalwart.crushing-reprisal",
        "name": "Crushing Reprisal",
        "lane": "Surge Mastery",
        "position": (3, 1),
        "level": 70,
        "description": (
            "Ironwall Reprisal deals heavy weapon damage and lowers enemy "
            "Attack and Speed for two turns."
        ),
    },
    {
        "id": "final-redoubt",
        "kind": "talent",
        "identifier": "stalwart.final-redoubt",
        "name": "Final Redoubt",
        "lane": "Surge Mastery",
        "position": (3, 2),
        "level": 80,
        "description": (
            "Last Bastion restores 40% maximum HP, grants a 75-point "
            "barrier, and enters a three-turn defensive stance."
        ),
    },
    {
        "id": "mirror-bastion",
        "kind": "talent",
        "identifier": "stalwart.mirror-bastion",
        "name": "Mirror Bastion",
        "lane": "Spell Defense",
        "position": (5, 0),
        "level": 65,
        "requires_known_ability": "Spell Reflection",
        "description": (
            "Triggered Spell Reflection grants 20 Resolve and +6 Magic "
            "Defense for two turns."
        ),
    },
    {
        "id": "magic-defense-1",
        "kind": "rating",
        "identifier": "Magic Defense",
        "lane": "Spell Defense",
        "position": (5, 1),
        "prerequisites": ("mirror-bastion",),
    },
)

PALADIN_TREE_NODE_SPECS = (
    {
        "id": "oath-judgment",
        "kind": "ability",
        "identifier": "OathsJudgment",
        "name": "Oath's Judgment",
        "lane": "Zeal",
        "position": (1, 0),
        "available_on_promotion": True,
    },
    {
        "id": "double-strike",
        "kind": "ability",
        "identifier": "DoubleStrike",
        "lane": "Zeal",
        "position": (0, 1),
        "owned_if_known": True,
        "prerequisites": ("oath-judgment",),
    },
    {
        "id": "attack-1",
        "kind": "rating",
        "identifier": "Attack",
        "lane": "Zeal",
        "position": (0, 2),
        "prerequisites": ("double-strike",),
    },
    {
        "id": "tempered-conviction",
        "kind": "talent",
        "identifier": "paladin.tempered-conviction",
        "name": "Tempered Conviction",
        "lane": "Zeal",
        "position": (0, 4),
        "level": 45,
        "prerequisites": ("attack-1",),
        "description": (
            "Permanently increase Defense by 20 and Oath Conviction "
            "capacity by 1."
        ),
        "bonuses": {"ratings": {"Defense": 20}},
        "kit_effect": ("meter_cap", "oath_conviction", 1),
    },
    {
        "id": "true-strike",
        "kind": "ability",
        "identifier": "TrueStrike",
        "lane": "Zeal",
        "position": (0, 5),
        "owned_if_known": True,
        "prerequisites": ("tempered-conviction",),
    },
    {
        "id": "smite",
        "kind": "ability",
        "identifier": "Smite",
        "lane": "Zeal",
        "position": (2, 1),
        "available_on_promotion": True,
        "prerequisites": ("oath-judgment",),
    },
    {
        "id": "repel-the-wicked",
        "kind": "ability",
        "identifier": "RepelTheWicked",
        "name": "Repel the Wicked",
        "lane": "Zeal",
        "position": (2, 3),
        "level": 40,
        "prerequisites": ("smite",),
    },
    {
        "id": "magic-1",
        "kind": "rating",
        "identifier": "Magic",
        "lane": "Zeal",
        "position": (2, 4),
        "prerequisites": ("repel-the-wicked",),
    },
    {
        "id": "hallowed-ground",
        "kind": "ability",
        "identifier": "HallowedGround",
        "name": "Hallowed Ground",
        "lane": "Zeal",
        "position": (2, 6),
        "level": 55,
        "prerequisites": ("magic-1",),
    },
    {
        "id": "oath-shelter",
        "kind": "ability",
        "identifier": "OathsShelter",
        "name": "Oath's Shelter",
        "lane": "Grace",
        "position": (4, 0),
        "available_on_promotion": True,
    },
    {
        "id": "heal",
        "kind": "ability",
        "identifier": "Heal",
        "lane": "Grace",
        "position": (3, 1),
        "available_on_promotion": True,
        "prerequisites": ("oath-shelter",),
    },
    {
        "id": "mana-1",
        "kind": "mana",
        "identifier": "Mana",
        "lane": "Grace",
        "position": (3, 2),
        "prerequisites": ("heal",),
    },
    {
        "id": "sworn-purpose",
        "kind": "talent",
        "identifier": "paladin.sworn-purpose",
        "name": "Sworn Purpose",
        "lane": "Grace",
        "position": (3, 5),
        "level": 50,
        "prerequisites": ("resist-shadow",),
        "description": (
            "Permanently increase Magic and Magic Defense by 20."
        ),
        "bonuses": {
            "ratings": {
                "Magic": 20,
                "Magic Defense": 20,
            },
        },
    },
    {
        "id": "blessed-light",
        "kind": "ability",
        "identifier": "BlessedLight",
        "name": "Blessed Light",
        "lane": "Grace",
        "position": (3, 6),
        "level": 55,
        "prerequisites": ("sworn-purpose",),
    },
    {
        "id": "bless",
        "kind": "ability",
        "identifier": "Bless",
        "lane": "Sanctity",
        "position": (5, 1),
        "available_on_promotion": True,
        "prerequisites": ("oath-shelter",),
    },
    {
        "id": "magic-defense-1",
        "kind": "rating",
        "identifier": "Magic Defense",
        "lane": "Sanctity",
        "position": (5, 2),
    },
    {
        "id": "divine-protection",
        "kind": "ability",
        "identifier": "DivineProtection",
        "lane": "Sanctity",
        "position": (5, 5),
        "level": 50,
        "prerequisites": ("defense-1",),
    },
    {
        "id": "defense-1",
        "kind": "rating",
        "identifier": "Defense",
        "lane": "Sanctity",
        "position": (5, 4),
        "prerequisites": ("parry",),
    },
    {
        "id": "resist-shadow",
        "kind": "ability",
        "identifier": "ResistShadow",
        "name": "Resist Shadow",
        "lane": "Sanctity",
        "position": (3, 4),
        "level": 45,
        "prerequisites": ("mana-1",),
    },
    {
        "id": "parry",
        "kind": "ability",
        "identifier": "Parry",
        "lane": "Sanctity",
        "position": (5, 3),
        "owned_if_known": True,
        "prerequisites": ("magic-defense-1",),
    },
)

CRUSADER_TREE_NODE_SPECS = (
    {
        "id": "condemnation",
        "kind": "ability",
        "identifier": "Condemnation",
        "lane": "Melee",
        "position": (1, 0),
        "available_on_promotion": True,
    },
    {
        "id": "two-handed-proficiency",
        "kind": "ability",
        "identifier": "TwoHandedWeaponProficiency",
        "name": "Two-Handed Weapon Proficiency",
        "lane": "Melee",
        "position": (0, 1),
        "prerequisites": ("condemnation",),
        "exclusive_group": "crusader.melee-style",
        "available_on_promotion": True,
    },
    {
        "id": "attack-1",
        "kind": "rating",
        "identifier": "Attack",
        "lane": "Melee",
        "position": (0, 2),
        "prerequisites": ("two-handed-proficiency",),
    },
    {
        "id": "mortal-strike",
        "kind": "ability",
        "identifier": "MortalStrike",
        "lane": "Melee",
        "position": (0, 3),
        "level": 75,
        "prerequisites": ("attack-1",),
    },
    {
        "id": "righteous-advance",
        "kind": "talent",
        "identifier": "crusader.righteous-advance",
        "name": "Righteous Advance",
        "lane": "Melee",
        "position": (0, 4),
        "prerequisites": ("mortal-strike",),
        "available_on_promotion": True,
        "description": (
            "Permanently increase Attack by 30 and improve every form of "
            "Oath's Judgment."
        ),
        "bonuses": {"ratings": {"Attack": 30}},
    },
    {
        "id": "sword-and-board",
        "kind": "ability",
        "identifier": "SwordAndBoard",
        "name": "Sword & Board",
        "lane": "Melee",
        "position": (2, 1),
        "prerequisites": ("condemnation",),
        "exclusive_group": "crusader.melee-style",
        "available_on_promotion": True,
    },
    {
        "id": "true-piercing-strike",
        "kind": "ability",
        "identifier": "TruePiercingStrike",
        "lane": "Melee",
        "position": (2, 2),
        "level": 70,
        "prerequisites": ("sword-and-board",),
    },
    {
        "id": "triple-strike",
        "kind": "ability",
        "identifier": "TripleStrike",
        "lane": "Melee",
        "position": (2, 5),
        "level": 85,
        "prerequisites": ("true-piercing-strike",),
    },
    {
        "id": "smite-2",
        "kind": "ability",
        "identifier": "Smite2",
        "name": "Smite II",
        "lane": "Spells",
        "position": (3, 0),
        "available_on_promotion": True,
    },
    {
        "id": "repel-the-wicked",
        "kind": "ability",
        "identifier": "RepelTheWicked",
        "name": "Repel the Wicked",
        "lane": "Spells",
        "position": (3, 1),
        "prerequisites": ("smite-2",),
        "owned_if_known": True,
    },
    {
        "id": "smite-3",
        "kind": "ability",
        "identifier": "Smite3",
        "name": "Smite III",
        "lane": "Spells",
        "position": (3, 2),
        "level": 70,
        "prerequisites": ("smite-2",),
    },
    {
        "id": "heal-2",
        "kind": "ability",
        "identifier": "Heal2",
        "name": "Heal II",
        "lane": "Healing",
        "position": (4, 0),
        "available_on_promotion": True,
    },
    {
        "id": "cleanse",
        "kind": "ability",
        "identifier": "Cleanse",
        "lane": "Healing",
        "position": (4, 1),
        "level": 65,
        "prerequisites": ("heal-2",),
    },
    {
        "id": "dispel",
        "kind": "ability",
        "identifier": "Dispel",
        "lane": "Healing",
        "position": (4, 2),
        "level": 70,
        "prerequisites": ("cleanse",),
    },
    {
        "id": "consecrated-bulwark",
        "kind": "talent",
        "identifier": "crusader.consecrated-bulwark",
        "name": "Consecrated Bulwark",
        "lane": "Protection",
        "position": (5, 0),
        "available_on_promotion": True,
        "description": (
            "Permanently increase Magic Defense by 30 and improve every "
            "form of Oath's Shelter."
        ),
        "bonuses": {"ratings": {"Magic Defense": 30}},
    },
    {
        "id": "parry",
        "kind": "ability",
        "identifier": "Parry",
        "lane": "Protection",
        "position": (5, 1),
        "prerequisites": ("consecrated-bulwark",),
        "owned_if_known": True,
    },
    {
        "id": "posturing",
        "kind": "ability",
        "identifier": "Posturing",
        "lane": "Protection",
        "position": (5, 2),
        "level": 65,
        "prerequisites": ("parry",),
    },
    {
        "id": "magic-defense-1",
        "kind": "rating",
        "identifier": "Magic Defense",
        "lane": "Protection",
        "position": (5, 3),
        "prerequisites": ("posturing",),
    },
    {
        "id": "health-1",
        "kind": "health",
        "identifier": "Health",
        "lane": "Protection",
        "position": (5, 4),
        "prerequisites": ("magic-defense-1",),
    },
)

# Base trees are deliberately authored as specialization paths instead of
# forcing every lineage into the same four combat categories. Ability entries
# use constructor names so upgraded abilities with the same display name remain
# distinct and preserve their catalog order.
BASE_TREE_BRANCHES = {
    "Mage": (
        (
            "Elementalism",
            "Sorcerer",
            ("Firebolt", "Tremor", "MagicMissile", "IceLance", "Shock", "WaterJet", "Gust"),
            "Magic",
        ),
        ("Occultism", "Warlock", ("Enfeeble",), "Magic"),
        ("Battlemagic", "Spellblade", ("ManaShield",), "Defense"),
        ("Conjuration", "Summoner", (), "Magic Defense"),
    ),
    "Footpad": (
        (
            "Subterfuge",
            "Thief",
            ("Quickstep", "SmokeScreen", "Steal", "SleepingPowder"),
            "Magic Defense",
        ),
        ("Vigilance", "Inquisitor", ("Disarm", "EvasiveGuard", "Parry"), "Defense"),
        (
            "Assassination",
            "Assassin",
            ("PocketSand", "KidneyPunch", "Backstab", "DoubleStrike"),
            "Attack",
        ),
        ("Spellcraft", "Spell Stealer", (), "Magic"),
    ),
    "Healer": (
        ("Devotion", "Cleric", ("Holy", "TurnUndead"), "Magic"),
        ("Discipline", "Monk", (), "Defense"),
        ("Restoration", "Priest", ("Heal", "Regen", "Heal2"), "Magic Defense"),
        ("Inspiration", "Bard", (), "Magic Defense"),
    ),
    "Pathfinder": (
        ("Wilds", "Druid", ("NaturalAttunement",), "Defense"),
        ("Divination", "Diviner", ("Tremor", "WaterJet", "Gust", "Scorch"), "Magic"),
        ("Totemism", "Shaman", (), "Magic Defense"),
        (
            "Huntsmanship",
            "Ranger",
            ("Quickstep", "PiercingStrike", "Parry", "TrueStrike"),
            "Attack",
        ),
    ),
}

# Base-tree rating nodes are authored explicitly. Repeated entries represent
# distinct purchases and preserve stable numbered node IDs.
BASE_TREE_RATING_NODES = {
    "Mage": (
        ("Battlemagic", "Defense"),
        ("Conjuration", "Magic Defense"),
    ),
    "Footpad": (
        ("Subterfuge", "Magic Defense"),
        ("Vigilance", "Defense"),
        ("Spellcraft", "Magic"),
    ),
    "Healer": (
        ("Devotion", "Magic"),
        ("Discipline", "Defense"),
        ("Discipline", "Defense"),
        ("Restoration", "Magic Defense"),
        ("Inspiration", "Magic Defense"),
    ),
    "Pathfinder": (
        ("Wilds", "Defense"),
        ("Totemism", "Magic Defense"),
    ),
}

# Every non-prototype tree owns named passive talents instead of being padded
# exclusively with anonymous rating nodes.  Each entry is
# (display name, stable talent key, permanent +5 rating focus).
CLASS_KIT_TALENTS = {
    "Weapon Master": (),
    "Berserker": (),
    "Grandmaster of Arms": (
        ("Perfect Form", "grandmaster.perfect-form", "Attack"),
        ("Adaptive Arsenal", "grandmaster.adaptive-arsenal", "Defense"),
    ),
    "Paladin": (
        ("Sworn Purpose", "paladin.sworn-purpose", "Magic Defense"),
        ("Tempered Conviction", "paladin.tempered-conviction", "Defense"),
    ),
    "Crusader": (
        ("Righteous Advance", "crusader.righteous-advance", "Attack"),
        ("Consecrated Bulwark", "crusader.consecrated-bulwark", "Magic Defense"),
    ),
    "Lancer": (),
    "Dragoon": (),
    "Sentinel": (
        ("Resolute Guard", "sentinel.resolute-guard", "Defense"),
        ("Watchful Reprisal", "sentinel.watchful-reprisal", "Attack"),
    ),
    "Stalwart Defender": (
        ("Unbroken Wall", "stalwart.unbroken-wall", "Defense"),
        ("Last Bastion", "stalwart.last-bastion", "Magic Defense"),
    ),
    "Mage": (
        ("Arcane Fundamentals", "mage.arcane-fundamentals", "Magic"),
        ("Warded Casting", "mage.warded-casting", "Magic Defense"),
    ),
    "Sorcerer": (
        ("Elemental Affinity", "sorcerer.elemental-affinity", "Magic"),
        ("Reactive Ward", "sorcerer.reactive-ward", "Magic Defense"),
    ),
    "Wizard": (
        ("Perfected Formula", "wizard.perfected-formula", "Magic"),
        ("Layered Countermagic", "wizard.layered-countermagic", "Magic Defense"),
    ),
    "Warlock": (
        ("Umbral Hunger", "warlock.umbral-hunger", "Magic"),
        ("Pact Resilience", "warlock.pact-resilience", "Magic Defense"),
    ),
    "Shadowcaster": (
        ("Deepening Shadow", "shadowcaster.deepening-shadow", "Magic"),
        ("Debt Control", "shadowcaster.debt-control", "Defense"),
    ),
    "Demonologist": (
        ("Tempered Corruption", "demonologist.tempered-corruption", "Magic"),
        ("Patron's Shelter", "demonologist.patrons-shelter", "Magic Defense"),
    ),
    "Spellblade": (
        ("Arcane Edge", "spellblade.arcane-edge", "Attack"),
        ("Spellguard", "spellblade.spellguard", "Defense"),
    ),
    "Knight Enchanter": (
        ("Charged Blade", "knight-enchanter.charged-blade", "Attack"),
        ("Runic Plate", "knight-enchanter.runic-plate", "Defense"),
    ),
    "Summoner": (
        ("Shared Focus", "summoner.shared-focus", "Magic"),
        ("Bonded Shelter", "summoner.bonded-shelter", "Magic Defense"),
    ),
    "Grand Summoner": (
        ("Conduit Mastery", "grand-summoner.conduit-mastery", "Magic"),
        ("True Name Ward", "grand-summoner.true-name-ward", "Magic Defense"),
    ),
    "Footpad": (
        ("Cunning Footwork", "footpad.cunning-footwork", "Defense"),
        ("Opportunist", "footpad.opportunist", "Attack"),
    ),
    "Thief": (
        ("Fortune's Favor", "thief.fortunes-favor", "Attack"),
        ("Escape Route", "thief.escape-route", "Defense"),
    ),
    "Rogue": (
        ("Loaded Odds", "rogue.loaded-odds", "Attack"),
        ("Cheater's Guard", "rogue.cheaters-guard", "Defense"),
    ),
    "Inquisitor": (
        ("Methodical Inquiry", "inquisitor.methodical-inquiry", "Attack"),
        ("Prepared Defense", "inquisitor.prepared-defense", "Magic Defense"),
    ),
    "Seeker": (
        ("Revelatory Strike", "seeker.revelatory-strike", "Attack"),
        ("Wayfinder's Ward", "seeker.wayfinders-ward", "Magic Defense"),
    ),
    "Assassin": (
        ("Lethal Preparation", "assassin.lethal-preparation", "Attack"),
        ("Veiled Retreat", "assassin.veiled-retreat", "Defense"),
    ),
    "Ninja": (
        ("No-Trace Opener", "ninja.no-trace-opener", "Attack"),
        ("Shadow Evasion", "ninja.shadow-evasion", "Defense"),
    ),
    "Spell Stealer": (
        ("Stolen Momentum", "spell-stealer.stolen-momentum", "Magic"),
        ("Arcane Escape", "spell-stealer.arcane-escape", "Defense"),
    ),
    "Arcane Trickster": (
        ("Arcane Larceny", "arcane-trickster.arcane-larceny", "Magic"),
        ("Misdirection", "arcane-trickster.misdirection", "Defense"),
    ),
    "Healer": (
        ("Steady Hands", "healer.steady-hands", "Magic"),
        ("Protective Grace", "healer.protective-grace", "Magic Defense"),
    ),
    "Cleric": (
        ("Devoted Guard", "cleric.devoted-guard", "Defense"),
        ("Consecrated Focus", "cleric.consecrated-focus", "Magic"),
    ),
    "Templar": (
        ("Ordered Blessing", "templar.ordered-blessing", "Magic Defense"),
        ("Relic Discipline", "templar.relic-discipline", "Defense"),
    ),
    "Hierophant": (
        ("Sacred Conduit", "hierophant.sacred-conduit", "Magic"),
        ("Devotional Ward", "hierophant.devotional-ward", "Magic Defense"),
    ),
    "Monk": (
        ("Centered Breath", "monk.centered-breath", "Defense"),
        ("Focused Ki", "monk.focused-ki", "Attack"),
    ),
    "Master Monk": (
        ("Perfected Ki", "master-monk.perfected-ki", "Attack"),
        ("Diamond Body", "master-monk.diamond-body", "Defense"),
    ),
    "Priest": (
        ("Answered Prayer", "priest.answered-prayer", "Magic"),
        ("Sheltering Litany", "priest.sheltering-litany", "Magic Defense"),
    ),
    "Archbishop": (
        ("Benediction Mastery", "archbishop.benediction-mastery", "Magic"),
        ("Intervening Grace", "archbishop.intervening-grace", "Magic Defense"),
    ),
    "Bard": (
        ("Practiced Refrain", "bard.practiced-refrain", "Magic"),
        ("Harmonic Shelter", "bard.harmonic-shelter", "Magic Defense"),
    ),
    "Troubadour": (
        ("Resonant Finale", "troubadour.resonant-finale", "Magic"),
        ("Sustained Chorus", "troubadour.sustained-chorus", "Magic Defense"),
    ),
    "Pathfinder": (
        ("Trail Instinct", "pathfinder.trail-instinct", "Defense"),
        ("Wild Insight", "pathfinder.wild-insight", "Magic Defense"),
    ),
    "Druid": (
        ("Primal Balance", "druid.primal-balance", "Magic"),
        ("Living Bark", "druid.living-bark", "Defense"),
    ),
    "Lycan": (
        ("Frenzy Control", "lycan.frenzy-control", "Attack"),
        ("Moonlit Hide", "lycan.moonlit-hide", "Defense"),
    ),
    "Archdruid": (
        ("Aspect Harmony", "archdruid.aspect-harmony", "Magic"),
        ("Ancient Growth", "archdruid.ancient-growth", "Magic Defense"),
    ),
    "Diviner": (
        ("Runic Focus", "diviner.runic-focus", "Magic"),
        ("Foreseen Defense", "diviner.foreseen-defense", "Magic Defense"),
    ),
    "Astromancer": (
        ("Threaded Fate", "astromancer.threaded-fate", "Magic"),
        ("Celestial Shelter", "astromancer.celestial-shelter", "Magic Defense"),
    ),
    "Shaman": (
        ("Totemic Rhythm", "shaman.totemic-rhythm", "Magic"),
        ("Spirit Ward", "shaman.spirit-ward", "Magic Defense"),
    ),
    "Soulcatcher": (
        ("Resonant Soul", "soulcatcher.resonant-soul", "Attack"),
        ("Spirit Vessel", "soulcatcher.spirit-vessel", "Magic Defense"),
    ),
    "Ranger": (
        ("Disciplined Hunt", "ranger.disciplined-hunt", "Attack"),
        ("Companion Guard", "ranger.companion-guard", "Defense"),
    ),
    "Beast Master": (
        ("Pack Tactics", "beast-master.pack-tactics", "Attack"),
        ("Shared Recovery", "beast-master.shared-recovery", "Defense"),
    ),
}

TALENT_KIT_EFFECTS = {
    "astromancer.threaded-fate": ("meter_cap", "foresight_threads", 1),
    "berserker.bloodied-ferocity": ("meter_cap", "bloodied_momentum", 1),
    "paladin.tempered-conviction": ("meter_cap", "oath_conviction", 1),
    "lancer.aerial-footwork": ("meter_cap", "aerial_tempo", 1),
    "thief.fortunes-favor": ("meter_cap", "fortune", 1),
    "rogue.loaded-odds": ("meter_cap", "fortune", 1),
    "inquisitor.methodical-inquiry": ("meter_cap", "revelation", 1),
    "seeker.revelatory-strike": ("meter_cap", "revelation", 1),
    "assassin.lethal-preparation": ("meter_cap", "death_marks", 1),
    "ninja.no-trace-opener": ("meter_cap", "death_marks", 1),
    "spell-stealer.stolen-momentum": ("meter_cap", "stolen_charge", 1),
    "arcane-trickster.arcane-larceny": ("meter_cap", "stolen_charge", 1),
    "cleric.devoted-guard": ("meter_cap", "devotion", 1),
    "templar.ordered-blessing": ("meter_cap", "devotion", 1),
    "hierophant.devotional-ward": ("meter_cap", "devotion", 1),
    "priest.answered-prayer": ("meter_cap", "prayer", 1),
    "archbishop.benediction-mastery": ("meter_cap", "prayer", 1),
    "monk.focused-ki": ("meter_cap", "ki", 1),
    "master-monk.perfected-ki": ("meter_cap", "ki", 1),
    "bard.practiced-refrain": ("meter_cap", "crescendo", 1),
    "troubadour.resonant-finale": ("meter_cap", "crescendo", 1),
    "archdruid.aspect-harmony": ("meter_cap", "aspect_harmony", 1),
    "shaman.totemic-rhythm": ("meter_cap", "totem_resonance", 1),
    "soulcatcher.resonant-soul": ("meter_cap", "totem_resonance", 1),
}

# A class is considered authored only when its ability paths are explicit or
# it owns named kit talents. This set intentionally covers the complete
# registry; adding a class now requires adding progression identity here.
AUTHORED_TREE_CLASSES = frozenset({
    "Warrior",
    *BASE_TREE_BRANCHES,
    *CLASS_KIT_TALENTS,
})

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
                for _node_id, base_identifier, _weapon_type
                in WEAPON_DISCIPLINE_ARTS
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
        ("Aerial Tempo", ("Jump", "Zephyrstrike")),
        ("Polearm Discipline", ("PolearmProficiency",)),
    ),
    "Dragoon": (
        ("Aerial Supremacy", ("TruePiercingStrike", "PolearmExcellence")),
        ("Landing Guard", ("ShieldBlock",)),
    ),
    "Sentinel": (
        (
            "Resolve",
            (
                "ShieldBash",
                "ShieldBlock",
                "Goad",
                "HoldTheLine",
                "BraceWall",
                "Retaliate",
                "ShieldRiposte",
                "CoveringGuard",
                "SpellReflection",
                "Bulwark",
            ),
        ),
        ("Watch", ()),
    ),
    "Stalwart Defender": (
        ("Bastion", ("CitadelAegis", "IronwallReprisal", "LastBastionSurge", "LastStand")),
        ("Unbroken Guard", ()),
    ),
    "Sorcerer": (
        ("School Affinity", ("Sleep", "Dispel", "WeakenMind", "FrozenArmor")),
        ("Metamagic", ("Doublecast", "MirrorImage", "Reflect", "IceBlock")),
    ),
    "Wizard": (
        (
            "Arcane Mastery",
            ("ManaShield2", "Triplecast", "MirrorImage2", "Volitation", "Teleport", "Boost"),
        ),
        ("Countermagic", ()),
    ),
    "Warlock": (
        ("Umbral Magic", ("ShadowBolt", "Corruption", "Terrify", "ShadowBolt2", "Doom", "Dispel")),
        ("Sacrifice", ("HealthDrain", "LifeTap", "ManaDrain")),
        ("Pacts", ()),
    ),
    "Shadowcaster": (
        ("Umbral Debt", ("ManaTap", "Eclipse", "HealthManaDrain")),
        ("Deep Shadow", ("ShadowBolt3", "Invisibility", "Nightmare", "Desoul")),
    ),
    "Demonologist": (("Contracts", ("Corruption2",)), ("Corruption", ())),
    "Spellblade": (
        (
            "Channeling",
            ("ManaSlice", "ImbueWeapon", "ElementalStrike", "TrueStrike", "EnhanceBlade"),
        ),
        ("Spellguard", ("Parry", "Reflect")),
    ),
    "Knight Enchanter": (
        (
            "Arcane Tempo",
            ("ManaTap", "DoubleStrike", "ManaSlice2", "DispelSlash", "TruePiercingStrike"),
        ),
        ("Enchantment", ("EnhanceArmor",)),
    ),
    "Summoner": (("Summon Bond", ("HealSummon",)), ("Conjuration", ())),
    "Grand Summoner": (
        ("Conduit", ("ConduitCommand", "RaiseSummon")),
        ("True Names", ()),
    ),
    "Thief": (
        ("Fortune", ("GoldToss", "Mug", "PoisonStrike", "ScavengersEye")),
        ("Tools", ("Lockpick",)),
    ),
    "Rogue": (
        (
            "Loaded Odds",
            ("SneakAttack", "SlotMachine", "TripleStrike", "FindersKeepers", "CheatDeath"),
        ),
        ("Cunning", ("Zephyrstrike", "KeenEye", "MasterLockpick")),
    ),
    "Inquisitor": (
        ("Case Journal", ("Inspect", "ExploitWeakness", "Reveal", "KeenEye")),
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
            ("Teleport", "Volitation", "EnterWall", "Cartography", "Wayfinding", "ThirdEye"),
        ),
        (
            "Revelation",
            ("TripleStrike", "TruePiercingStrike", "WeakenMind", "ResistAll", "Sanctuary"),
        ),
    ),
    "Assassin": (
        ("Death Mark", ("PoisonStrike", "TripleStrike", "DeathMark")),
        ("Shadowcraft", ("Invisibility", "Lockpick")),
    ),
    "Ninja": (
        ("Execution", ("Mug", "FlurryBlades", "Desoul")),
        ("No Trace", ("Haste",)),
    ),
    "Spell Stealer": (
        ("Spell Theft", ("StealSpell", "StealAsWell", "ImbueWeapon")),
        ("Stolen Charge", ("Silence", "WindSpeed")),
    ),
    "Arcane Trickster": (
        ("Arcane Larceny", ("StealSpell2", "WeakenMind")),
        ("Misdirection", ("ThirdEye",)),
    ),
    "Cleric": (
        (
            "Devotion",
            ("SanctuaryWard", "Smite", "Silence", "Smite2", "TurnUndead2", "Bless", "Cleanse"),
        ),
        ("Bulwark", ("TrueStrike", "ShieldSlam", "ShieldBlock", "PiousBounty")),
    ),
    "Templar": (
        (
            "Relic Discipline",
            ("PiercingStrike", "RelicAegis", "Charge", "DoubleStrike", "TruePiercingStrike", "Parry", "Goad"),
        ),
        ("Ordered Blessings", ("Smite3", "Dispel", "Regen2")),
    ),
    "Hierophant": (
        ("Sacred Conduit", ("ConsecratedConduit", "StaffConduit", "Holy2")),
        ("Devotional Grace", ("Dispel", "Regen2")),
    ),
    "Monk": (
        (
            "Ki",
            (
                "ChiHeal",
                "DoubleStrike",
                "LegSweep",
                "TrueStrike",
                "Uppercut",
                "MirrorBreath",
                "Headbutt",
                "PurgingKata",
            ),
        ),
        ("Centering", ("PurityBody", "CenteredGuard", "DrunkenBrawler", "Parry", "Shell")),
    ),
    "Master Monk": (
        (
            "Perfected Ki",
            ("Hyakuretsukyaku", "TripleStrike", "SpinningBackElbow", "Suplex", "Hadouken", "DimMak"),
        ),
        ("Diamond Body", ("Dispel", "Evasion", "PurityBody2", "MartialMastery", "Reflect")),
    ),
    "Priest": (
        ("Prayer", ("Supplication", "Holy2", "Dispel", "Berserk")),
        (
            "Grace",
            ("DefensiveRegen", "ManaShield", "Regen2", "Shell", "Cleanse", "Bless"),
        ),
    ),
    "Archbishop": (
        ("Benediction", ("Doublecast", "GreatBenediction", "ManaShield2", "Holy3", "Silence")),
        ("Intervention", ("Heal3", "Regen3", "Resurrection")),
    ),
    "Bard": (
        ("Performance", ("SongValor", "SongShelter", "SongRenewal")),
        ("Composition", ()),
    ),
    "Troubadour": (("Finale", ()), ("Mastery", ())),
    "Druid": (
        ("Forms", ("Transform", "Transform2", "MortalStrike")),
        ("Nature Rites", ("PoisonDart", "StoneSkin", "Regrowth", "CalmingBreeze")),
    ),
    "Lycan": (
        ("Frenzy", ("Transform3", "Charge", "WingedPounce", "MortalStrike2", "BattleCry")),
        ("Control", ("Dispel",)),
    ),
    "Archdruid": (
        (
            "Fourfold Balance",
            ("FourfoldSurge", "PlantSeeds", "Bolt", "VilePotion", "Windswept", "BallLightning", "NatureShield"),
        ),
        ("Aspect Harmony", ()),
    ),
    "Diviner": (
        ("Runes", ("Doublecast", "Enfeeble", "Dispel", "Berserk", "LearnSpell", "Haste")),
        ("Foresight", ()),
    ),
    "Astromancer": (
        ("Foresight Threads", ("ThreadedCast", "Triplecast", "Foretell", "TwistFate", "Rewind")),
        ("Constellations", ("Vulcanize", "WeakenMind", "Wormhole", "LearnSpell2", "Boost")),
    ),
    "Shaman": (
        ("Totems", ("Totem", "TotemSurge", "MaelstromWeapon")),
        (
            "Elements",
            ("ElementalStrike", "PiercingStrike", "TrueStrike", "DoubleStrike", "Hex", "Hydration", "AstralShift"),
        ),
    ),
    "Soulcatcher": (
        ("Soul Communion", ("SoulDrain", "Desoul", "AbsorbEssence")),
        ("Totem Resonance", ("TotemSurge", "TripleStrike", "TruePiercingStrike", "Dispel", "Parry")),
    ),
    "Ranger": (("Hunt", ("FavoredEnemy",)), ("Companion Bond", ())),
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
    "Spellblade": {"Knight Enchanter": "Channeling"},
    "Summoner": {"Grand Summoner": "Summon Bond"},
    "Thief": {"Rogue": "Fortune"},
    "Inquisitor": {"Seeker": "Case Journal"},
    "Assassin": {"Ninja": "Death Mark"},
    "Spell Stealer": {"Arcane Trickster": "Spell Theft"},
    "Cleric": {"Templar": "Bulwark", "Hierophant": "Devotion"},
    "Monk": {"Master Monk": "Ki"},
    "Priest": {"Archbishop": "Prayer"},
    "Bard": {"Troubadour": "Performance"},
    "Druid": {"Lycan": "Forms", "Archdruid": "Nature Rites"},
    "Diviner": {"Astromancer": "Runes"},
    "Shaman": {"Soulcatcher": "Totems"},
    "Ranger": {"Beast Master": "Hunt"},
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
    "Summoner": (("charisma", "intel", "wisdom"), ("con", "dex", "strength")),
    "Grand Summoner": (("charisma",), ("intel", "wisdom")),
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
    "Monk": (("strength",), ("wisdom", "con", "dex", "charisma")),
    "Master Monk": (("strength", "con"), ("wisdom", "dex", "charisma")),
    "Priest": (("wisdom",), ("intel",)),
    "Archbishop": (("wisdom", "intel"), ("charisma",)),
    "Bard": (("charisma", "wisdom", "intel", "dex"), ("con", "strength")),
    "Troubadour": (("dex",), ("charisma", "wisdom", "intel", "con", "strength")),
    "Druid": (
        ("strength", "intel", "wisdom", "con", "charisma", "dex"),
        (),
    ),
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
    "Weapon Master": {"strength": 15, "dex": 12, "intel": 11},
    "Lancer": {"strength": 13},
    "Sentinel": {"con": 16},
    "Paladin": {"wisdom": 13},
    "Sorcerer": {"intel": 15, "wisdom": 13},
    "Spellblade": {
        "strength": 13,
        "con": 13,
        "intel": 10,
        "charisma": 10,
    },
    "Inquisitor": {
        "strength": 12,
        "con": 13,
        "dex": 10,
        "charisma": 10,
    },
    "Druid": {
        "strength": 12,
        "intel": 12,
        "wisdom": 12,
        "con": 12,
        "charisma": 12,
        "dex": 13,
    },
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
        "strength": 17,
        "con": 17,
        "intel": 15,
        "dex": 11,
        "charisma": 12,
    },
    "Grand Summoner": {"charisma": 17, "intel": 16, "wisdom": 16},
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
EXTERNAL_ACQUISITION_ABILITIES = frozenset({
    "Call Contract",
    "Citadel Aegis",
    "Familiar",
    "Invoke Agloolik",
    "Invoke Bardi",
    "Invoke Cacus",
    "Invoke Dilong",
    "Invoke Fuath",
    "Invoke Grigori",
    "Invoke Hala",
    "Invoke Izulu",
    "Invoke Kobalos",
    "Invoke Patagon",
    "Invoke Zahhak",
    "Ironwall Reprisal",
    "Last Bastion",
    "Summon",
    "Tame",
})
