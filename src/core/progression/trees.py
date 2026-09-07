"""Ability-tree construction and immutable registry state."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .. import abilities
from ..classes import classes_dict
from ..progression_manifest import (
    ABILITY_BRANCH_OVERRIDES,
    ABILITY_ICON_OVERRIDES,
    ABILITY_NODE_NAME_OVERRIDES,
    ARCANE_TRICKSTER_TREE_NODE_SPECS,
    ARCHBISHOP_TREE_NODE_SPECS,
    ARCHDRUID_TREE_NODE_SPECS,
    ASSASSIN_TREE_NODE_SPECS,
    ASTROMANCER_TREE_NODE_SPECS,
    AUTHORED_PROMOTED_TALENT_KEYS,
    AUTHORED_TREE_CLASSES,
    BARD_TREE_NODE_SPECS,
    BASE_TREE_NODE_SPECS,
    BASE_TREE_PROMOTION_SPECS,
    BEAST_MASTER_TREE_NODE_SPECS,
    BERSERKER_TREE_NODE_SPECS,
    CLASS_KIT_TALENTS,
    CLASS_STAT_GROUPS,
    CLERIC_TREE_NODE_SPECS,
    CONJURER_CARRIED_NODE_IDS,
    CONJURER_TREE_NODE_SPECS,
    CRUSADER_TREE_NODE_SPECS,
    DEMONOLOGIST_TREE_NODE_SPECS,
    DIVINER_TREE_NODE_SPECS,
    DRAGOON_TREE_NODE_SPECS,
    DRUID_TREE_NODE_SPECS,
    EXTERNAL_ACQUISITION_ABILITIES,
    FIRST_PROMOTION_STAT_REQUIREMENT_OVERRIDES,
    GRANDMASTER_TREE_NODE_SPECS,
    HIEROPHANT_TREE_NODE_SPECS,
    INQUISITOR_TREE_NODE_SPECS,
    KNIGHT_ENCHANTER_TREE_NODE_SPECS,
    LANCER_TREE_NODE_SPECS,
    LYCAN_TREE_NODE_SPECS,
    MAGE_CARRIED_NODE_POSITIONS,
    MAGE_PROMOTION_SPECS,
    MAGE_TREE_NODE_SPECS,
    MASTER_MONK_TREE_NODE_SPECS,
    MONK_TREE_NODE_SPECS,
    NINJA_TREE_NODE_SPECS,
    PALADIN_TREE_NODE_SPECS,
    PRIEST_TREE_NODE_SPECS,
    PROMOTED_TREE_PATHS,
    PROMOTED_TREE_PROMOTION_PATHS,
    RANGER_TREE_NODE_SPECS,
    ROGUE_TREE_NODE_SPECS,
    SECOND_PROMOTION_STAT_REQUIREMENT_OVERRIDES,
    SEEKER_TREE_NODE_SPECS,
    SENTINEL_TREE_NODE_SPECS,
    SHADOWCASTER_TREE_NODE_SPECS,
    SHAMAN_TREE_NODE_SPECS,
    SORCERER_TREE_NODE_SPECS,
    SOULCATCHER_TREE_NODE_SPECS,
    SPELL_STEALER_TREE_NODE_SPECS,
    SPELLBLADE_TREE_NODE_SPECS,
    STAGE_SIZE_RANGES,
    STALWART_DEFENDER_TREE_NODE_SPECS,
    TALENT_KIT_EFFECTS,
    TEMPLAR_TREE_NODE_SPECS,
    THIEF_TREE_NODE_SPECS,
    TREE_LANES,
    TREE_SIZE_OVERRIDES,
    TROUBADOUR_TREE_NODE_SPECS,
    WARLOCK_TREE_NODE_SPECS,
    WARRIOR_CONNECTOR_CHANNEL_OVERRIDES,
    WARRIOR_FLOATING_NODES,
    WARRIOR_NODE_CROSS_REQUIREMENTS,
    WARRIOR_NODE_LEVEL_REQUIREMENTS,
    WARRIOR_NODE_POSITION_OVERRIDES,
    WARRIOR_NODE_PREREQUISITE_OVERRIDES,
    WARRIOR_PATH_ROW_OFFSETS,
    WARRIOR_PROMOTION_CROSS_REQUIREMENTS,
    WARRIOR_TREE_PATHS,
    WEAPON_MASTER_TREE_NODE_SPECS,
    WIZARD_TREE_NODE_SPECS,
)
from .models import RESOURCE_NODE_AMOUNTS, AbilityTree, AbilityTreeNode, NodeKind, _slug


def _flatten_classes() -> tuple[
    dict[str, tuple[type, int, str | None]],
    dict[str, tuple[str, ...]],
]:
    details: dict[str, tuple[type, int, str | None]] = {}
    children: dict[str, tuple[str, ...]] = {}

    def visit(entry: dict[str, Any], stage: int, parent: str | None) -> None:
        class_ctor = entry["class"]
        class_name = class_ctor().name
        details[class_name] = (class_ctor, stage, parent)
        child_names = tuple(child["class"]().name for child in entry.get("pro", {}).values())
        children[class_name] = child_names
        for child in entry.get("pro", {}).values():
            visit(child, stage + 1, class_name)

    for base_entry in classes_dict.values():
        visit(base_entry, 1, None)
    return details, children


CLASS_DETAILS, CLASS_CHILDREN = _flatten_classes()


def effective_node_level_requirement(
    node: AbilityTreeNode,
    class_name: str,
) -> int:
    """Return a node's nonredundant level gate in the displayed class tree.

    Promotion already proves the player reached level 30 for a first-promotion
    class and level 60 for a terminal class. An ability authored below that
    floor therefore needs neither another runtime check nor requirement text
    when it is carried into the promoted tree.
    """
    required_level = int(node.payload.get("level_requirement", 0) or 0)
    if node.kind != NodeKind.ABILITY or required_level <= 0:
        return required_level
    class_details = CLASS_DETAILS.get(class_name)
    if class_details is None:
        return required_level
    stage = int(class_details[1])
    promotion_floor = {1: 1, 2: 30, 3: 60}.get(stage, 1)
    if required_level < promotion_floor:
        return 0
    return required_level


def _ability_entries(class_name: str) -> list[tuple[int, int, str, type, Any]]:
    entries: list[tuple[int, int, str, type, Any]] = []
    for source_order, (book, source) in enumerate(
        (("Spells", abilities.spell_dict), ("Skills", abilities.skill_dict))
    ):
        for raw_level, raw_abilities in source.get(class_name, {}).items():
            for ability_order, ability_ctor in enumerate(
                abilities.ability_classes_for(raw_abilities)
            ):
                ability = ability_ctor()
                if ability.name in EXTERNAL_ACQUISITION_ABILITIES:
                    continue
                entries.append(
                    (
                        int(raw_level),
                        source_order * 100 + ability_order,
                        book,
                        ability_ctor,
                        ability,
                    )
                )
    entries.sort(key=lambda row: (row[0], row[1], row[4].name))
    return entries


def _ability_icon_key(book: str, ability: Any) -> str:
    """Return the semantic icon shared by abilities of the same type."""
    override = ABILITY_ICON_OVERRIDES.get(ability.name)
    if override:
        return override
    normalized_name = ability.name.lower()
    if "transform" in normalized_name or "shapeshift" in normalized_name:
        return "spell_transform"
    if any(token in normalized_name for token in ("summon", "familiar", "invoke", "tame")):
        return "spell_summon"
    subtype = str(getattr(ability, "subtyp", "") or "").strip().lower()
    if book == "Spells":
        spell_icons = {
            "death": "spell_shadow",
            "earth": "spell_earth",
            "electric": "spell_lightning",
            "fire": "spell_fire",
            "heal": "spell_heal",
            "holy": "spell_holy",
            "ice": "spell_ice",
            "illusion": "spell_illusion",
            "nature": "spell_earth",
            "movement": "spell_movement",
            "non-elemental": "spell_arcane",
            "offensive": "spell_arcane",
            "poison": "spell_poison",
            "shadow": "spell_shadow",
            "soul": "spell_shadow",
            "status": "spell_status",
            "support": "spell_support",
            "time": "spell_time",
            "water": "spell_water",
            "wind": "spell_wind",
        }
        return spell_icons.get(subtype, "spell_arcane")
    skill_icons = {
        "chi strike": "skill_martial_arts",
        "class": "skill_passive" if getattr(ability, "passive", False) else "skill_support",
        "defensive": "skill_defense",
        "drain": "skill_drain",
        "enhance": "skill_support",
        "luck": "skill_luck",
        "martial arts": "skill_martial_arts",
        "offensive": "skill_offense",
        "power up": "skill_passive",
        "stealth": "skill_stealth",
        "truth": "skill_truth",
    }
    return skill_icons.get(
        subtype,
        "skill_passive" if getattr(ability, "passive", False) else "skill_offense",
    )


def _ability_lane(book: str, ability: Any) -> str:
    override = ABILITY_BRANCH_OVERRIDES.get(ability.name)
    if override:
        return override
    if book == "Spells":
        support_names = {
            "Bless",
            "Calming Breeze",
            "Cleanse",
            "Divine Protection",
            "Heal",
            "Heal 2",
            "Heal 3",
            "Natural Attunement",
            "Regen",
            "Regen 2",
            "Regen 3",
            "Regrowth",
            "Resurrection",
            "Sanctuary",
            "Shell",
        }
        if (
            ability.name in support_names
            or getattr(ability, "subtyp", "") == "Support"
            or getattr(ability, "typ", "") == "Support"
        ):
            return "Support"
        return "Arcane"
    defensive_names = {
        "Brace Wall",
        "Bulwark",
        "Centered Guard",
        "Covering Guard",
        "Evasion",
        "Evasive Guard",
        "Goad",
        "Guard Partner",
        "Hold the Line",
        "Last Stand",
        "Mana Shield",
        "Parry",
        "Posturing",
        "Quickstep",
        "Retaliate",
        "Shield Block",
        "Shield Riposte",
        "Spell Reflection",
    }
    if ability.name in defensive_names or getattr(ability, "passive", False):
        return "Defense"
    return "Martial"


def _promotion_requirements(target_class: str, stage: int) -> dict[str, int]:
    if stage == 3 and target_class in SECOND_PROMOTION_STAT_REQUIREMENT_OVERRIDES:
        requirements = dict(SECOND_PROMOTION_STAT_REQUIREMENT_OVERRIDES[target_class])
    else:
        primary, secondary = CLASS_STAT_GROUPS[target_class]
        if stage == 2:
            primary_value = 17 if len(primary) == 1 else 14 if len(primary) == 2 else 13
            secondary_value = 13 if len(secondary) == 1 else 10
        else:
            primary_value = 24 if len(primary) == 1 else 20 if len(primary) == 2 else 18
            secondary_value = 19 if len(secondary) == 1 else 15
        requirements = {stat: primary_value for stat in primary}
        requirements.update({stat: secondary_value for stat in secondary})
        if stage == 2:
            requirements.update(
                FIRST_PROMOTION_STAT_REQUIREMENT_OVERRIDES.get(
                    target_class,
                    {},
                )
            )
    return {stat_name: required for stat_name, required in requirements.items() if required > 10}


def _tree_branch_specs(
    class_name: str,
    entries: list[tuple[int, int, str, type, Any]],
) -> tuple[tuple[str, ...], dict[str, str], dict[str, str]]:
    """Return branch order, ability assignments, and promotion assignments."""
    promoted_paths = PROMOTED_TREE_PATHS.get(class_name)
    if promoted_paths is not None:
        branches = tuple(branch_name for branch_name, _abilities in promoted_paths)
        ability_branches = {
            ability_name: branch_name
            for branch_name, ability_names in promoted_paths
            for ability_name in ability_names
        }
        expected = {
            ability_ctor.__name__ for _level, _tie, _book, ability_ctor, _ability in entries
        }
        missing = expected - set(ability_branches)
        extra = set(ability_branches) - expected
        if missing or extra:
            raise ValueError(
                f"{class_name} authored paths mismatch catalog; "
                f"missing={sorted(missing)}, extra={sorted(extra)}"
            )
        declared_promotions = PROMOTED_TREE_PROMOTION_PATHS.get(class_name, {})
        missing_promotions = set(CLASS_CHILDREN[class_name]) - set(declared_promotions)
        extra_promotions = set(declared_promotions) - set(CLASS_CHILDREN[class_name])
        if missing_promotions or extra_promotions:
            raise ValueError(
                f"{class_name} authored promotion paths mismatch registry; "
                f"missing={sorted(missing_promotions)}, "
                f"extra={sorted(extra_promotions)}"
            )
        return branches, ability_branches, dict(declared_promotions)

    raise ValueError(f"{class_name} has no explicit authored paths")


def _branch_rating_focus(class_name: str, branch: str) -> str:
    promoted = PROMOTED_TREE_PATHS.get(class_name, ())
    for branch_name, ability_names in promoted:
        if branch_name != branch:
            continue
        entries = {
            ability_ctor.__name__: (book, ability)
            for _level, _tie, book, ability_ctor, ability in _ability_entries(class_name)
        }
        lane_counts = {lane: 0 for lane in TREE_LANES}
        for ability_name in ability_names:
            book, ability = entries[ability_name]
            lane_counts[_ability_lane(book, ability)] += 1
        if any(lane_counts.values()):
            lane = max(
                TREE_LANES,
                key=lambda name: (
                    lane_counts[name],
                    -TREE_LANES.index(name),
                ),
            )
            return {
                "Martial": "Attack",
                "Arcane": "Magic",
                "Defense": "Defense",
                "Support": "Magic Defense",
            }[lane]
        normalized = branch.lower()
        if any(word in normalized for word in ("guard", "defense", "control", "body")):
            return "Defense"
        if any(word in normalized for word in ("grace", "ward", "shelter", "prayer")):
            return "Magic Defense"
        if any(
            word in normalized
            for word in ("magic", "arcane", "corruption", "rune", "constellation")
        ):
            return "Magic"
        return "Attack"
    return {
        "Martial": "Attack",
        "Arcane": "Magic",
        "Defense": "Defense",
        "Support": "Magic Defense",
    }.get(branch, "Defense")


def _rating_icon_key(rating_name: str) -> str:
    return f"rating_{_slug(rating_name).replace('-', '_')}"


def _development_level_requirement(stage: int, row: int) -> int | None:
    """Return the authored global-level milestone for a development row."""
    milestones = {
        1: (None, 10, 15, 20, 25),
        2: (35, 40, 45, 50, 55),
        3: (65, 70, 75, 80, 85, 90, 95),
    }[stage]
    return milestones[min(max(0, row), len(milestones) - 1)]


def _tree_size_range(class_name: str, stage: int) -> tuple[int, int]:
    """Return class-specific development bounds when a tree needs extra space."""
    return TREE_SIZE_OVERRIDES.get(class_name, STAGE_SIZE_RANGES[stage])


def _build_warrior_tree() -> AbilityTree:
    """Build the explicit Warrior prototype graph."""
    class_name = "Warrior"
    entries = {
        ability_ctor.__name__: (book, ability_ctor, ability)
        for _level, _tie, book, ability_ctor, ability in _ability_entries(class_name)
    }
    branches = (
        *(path[0] for path in WARRIOR_TREE_PATHS),
        "Independent",
    )
    all_nodes: list[AbilityTreeNode] = []
    rating_counts: dict[str, int] = {}
    ability_node_ids: dict[str, str] = {}
    path_node_ids: dict[tuple[str, str], str] = {}
    promotion_terminals: dict[str, str] = {}

    for column, (lane, target_name, specs) in enumerate(WARRIOR_TREE_PATHS):
        prerequisite: tuple[str, ...] = ()
        row_offset = WARRIOR_PATH_ROW_OFFSETS.get(target_name, 0)
        for row, (kind_name, identifier, icon_key) in enumerate(
            specs,
            start=row_offset + 1,
        ):
            if kind_name == "ability":
                try:
                    book, ability_ctor, ability = entries[identifier]
                except KeyError as exc:
                    raise ValueError(
                        f"Warrior tree references unknown ability {identifier}"
                    ) from exc
                node_id = f"warrior.ability.{_slug(identifier)}"
                kind = NodeKind.ABILITY
                payload = {
                    "name": ability.name,
                    "book": book,
                    "ability_class": ability_ctor,
                    "description": getattr(ability, "description", ""),
                }
                if identifier == "Commitment":
                    payload["closes_promotions"] = (
                        "Weapon Master",
                        "Lancer",
                        "Sentinel",
                    )
                ability_node_ids[identifier] = node_id
            elif kind_name == "rating":
                rating_counts[identifier] = rating_counts.get(identifier, 0) + 1
                node_id = f"warrior.rating.{_slug(identifier)}.{rating_counts[identifier]}"
                kind = NodeKind.RATING
                payload = {
                    "name": f"+10 {identifier}",
                    "rating": identifier,
                    "amount": 10,
                    "description": (f"Permanently increase {identifier} by 10."),
                }
            elif kind_name == "health":
                node_id = "warrior.health.25"
                kind = NodeKind.HEALTH
                payload = {
                    "name": "+25 HP",
                    "amount": 25,
                    "description": "Permanently increase maximum HP by 25.",
                }
            else:
                raise ValueError(f"Unknown Warrior node kind: {kind_name}")
            level_requirement = WARRIOR_NODE_LEVEL_REQUIREMENTS.get(identifier)
            if level_requirement:
                payload["level_requirement"] = level_requirement
            node = AbilityTreeNode(
                id=node_id,
                tree_id=class_name,
                kind=kind,
                lane=lane,
                position=WARRIOR_NODE_POSITION_OVERRIDES.get(
                    (target_name, identifier),
                    (column, row),
                ),
                icon_key=icon_key,
                prerequisites=prerequisite,
                payload=payload,
            )
            all_nodes.append(node)
            path_node_ids[(target_name, identifier)] = node.id
            prerequisite = (node.id,)
        promotion_terminals[target_name] = prerequisite[0]

    node_indexes = {node.id: index for index, node in enumerate(all_nodes)}
    for target_identifier, required_nodes in WARRIOR_NODE_PREREQUISITE_OVERRIDES.items():
        target_id = ability_node_ids[target_identifier]
        target_index = node_indexes[target_id]
        all_nodes[target_index] = replace(
            all_nodes[target_index],
            prerequisites=tuple(
                path_node_ids[(path_target, identifier)]
                for path_target, identifier in required_nodes
            ),
        )
    for target_identifier, required_nodes in WARRIOR_NODE_CROSS_REQUIREMENTS.items():
        target_id = ability_node_ids[target_identifier]
        target_index = node_indexes[target_id]
        target_node = all_nodes[target_index]
        cross_requirements = tuple(
            path_node_ids[(path_target, identifier)] for path_target, identifier in required_nodes
        )
        connector_channels = {
            path_node_ids[(path_target, identifier)]: WARRIOR_CONNECTOR_CHANNEL_OVERRIDES[
                (target_identifier, identifier)
            ]
            for path_target, identifier in required_nodes
            if (
                target_identifier,
                identifier,
            )
            in WARRIOR_CONNECTOR_CHANNEL_OVERRIDES
        }
        all_nodes[target_index] = replace(
            target_node,
            prerequisites=(
                *target_node.prerequisites,
                *cross_requirements,
            ),
            payload={
                **target_node.payload,
                **({"connector_channel_columns": connector_channels} if connector_channels else {}),
            },
        )

    floating_node_ids: dict[str, str] = {}
    for (
        kind_name,
        identifier,
        icon_key,
        position,
        prerequisite_identifier,
    ) in WARRIOR_FLOATING_NODES:
        if kind_name == "ability":
            try:
                book, ability_ctor, ability = entries[identifier]
            except KeyError as exc:
                raise ValueError(f"Warrior tree references unknown ability {identifier}") from exc
            node_id = f"warrior.ability.{_slug(identifier)}"
            kind = NodeKind.ABILITY
            payload = {
                "name": ability.name,
                "book": book,
                "ability_class": ability_ctor,
                "description": getattr(ability, "description", ""),
            }
            ability_node_ids[identifier] = node_id
        elif kind_name == "rating":
            rating_counts[identifier] = rating_counts.get(identifier, 0) + 1
            node_id = f"warrior.rating.{_slug(identifier)}.{rating_counts[identifier]}"
            kind = NodeKind.RATING
            payload = {
                "name": f"+10 {identifier}",
                "rating": identifier,
                "amount": 10,
                "description": f"Permanently increase {identifier} by 10.",
            }
        elif kind_name == "health":
            node_id = "warrior.health.25"
            kind = NodeKind.HEALTH
            payload = {
                "name": "+25 HP",
                "amount": 25,
                "description": "Permanently increase maximum HP by 25.",
            }
        else:
            raise ValueError(f"Unknown floating Warrior node kind: {kind_name}")
        level_requirement = WARRIOR_NODE_LEVEL_REQUIREMENTS.get(identifier)
        if level_requirement:
            payload["level_requirement"] = level_requirement
        prerequisite = (
            (floating_node_ids[prerequisite_identifier],)
            if prerequisite_identifier is not None
            else ()
        )
        all_nodes.append(
            AbilityTreeNode(
                id=node_id,
                tree_id=class_name,
                kind=kind,
                lane="Independent",
                position=position,
                icon_key=icon_key,
                prerequisites=prerequisite,
                payload=payload,
            )
        )
        floating_node_ids[identifier] = node_id

    promotion_row = max(node.position[1] for node in all_nodes) + 1
    for column, (lane, target_name, _specs) in enumerate(WARRIOR_TREE_PATHS):
        cross_requirements = tuple(
            ability_node_ids[identifier]
            for identifier in WARRIOR_PROMOTION_CROSS_REQUIREMENTS.get(
                target_name,
                (),
            )
        )
        all_nodes.append(
            AbilityTreeNode(
                id=f"warrior.promotion.{_slug(target_name)}",
                tree_id=class_name,
                kind=NodeKind.PROMOTION,
                lane=lane,
                position=(column, promotion_row),
                icon_key="promotion",
                prerequisites=(promotion_terminals[target_name], *cross_requirements),
                payload={
                    "name": f"Promote: {target_name}",
                    "target_class": target_name,
                    "target_class_ctor": CLASS_DETAILS[target_name][0],
                    "requirements": _promotion_requirements(target_name, 2),
                    "level_requirement": 30,
                },
                cost=2,
            )
        )

    return AbilityTree(
        id=class_name,
        class_name=class_name,
        stage=1,
        branches=branches,
        nodes=tuple(all_nodes),
    )


def _build_mage_tree() -> AbilityTree:
    """Build the explicit Mage specialization graph."""
    class_name = "Mage"
    entries = {
        ability_ctor.__name__: (book, ability_ctor, ability)
        for _level, _tie, book, ability_ctor, ability in _ability_entries(class_name)
    }
    branches = ("Elementalism", "Arcana", "Occultism", "Conjuration", "Universal")
    nodes: list[AbilityTreeNode] = []

    for spec in MAGE_TREE_NODE_SPECS:
        kind = NodeKind(str(spec["kind"]))
        identifier = str(spec["identifier"])
        if kind == NodeKind.ABILITY:
            book, ability_ctor, ability = entries[identifier]
            payload = {
                "name": ability.name,
                "book": book,
                "ability_class": ability_ctor,
                "description": getattr(ability, "description", ""),
            }
            icon_key = str(spec.get("icon_key", _ability_icon_key(book, ability)))
        elif kind == NodeKind.TALENT:
            payload = {
                "name": str(spec["name"]),
                "talent_key": identifier,
                "description": str(spec["description"]),
                "bonuses": spec["bonuses"],
            }
            icon_key = "skill_passive"
        elif kind == NodeKind.RATING:
            payload = {
                "name": f"+10 {identifier}",
                "rating": identifier,
                "amount": 10,
                "description": f"Permanently increase {identifier} by 10.",
            }
            icon_key = _rating_icon_key(identifier)
        elif kind in {NodeKind.HEALTH, NodeKind.MANA}:
            resource_name = "HP" if kind == NodeKind.HEALTH else "MP"
            payload = {
                "name": f"+25 {resource_name}",
                "amount": 25,
                "description": (f"Permanently increase maximum {resource_name} by 25."),
            }
            icon_key = "skill_defense" if kind == NodeKind.HEALTH else "spell_arcane"
        else:
            raise ValueError(f"Unsupported Mage node kind: {kind.value}")

        if spec.get("level") is not None:
            payload["level_requirement"] = int(spec["level"])
        if spec.get("prerequisite_mode"):
            payload["prerequisite_mode"] = str(spec["prerequisite_mode"])
        if spec.get("exclusive_group"):
            payload["exclusive_group"] = str(spec["exclusive_group"])
        if spec.get("connector_enter_from_top"):
            payload["connector_enter_from_top"] = True
        if spec.get("connector_channel_columns"):
            payload["connector_channel_columns"] = dict(spec["connector_channel_columns"])
        nodes.append(
            AbilityTreeNode(
                id=str(spec["id"]),
                tree_id=class_name,
                kind=kind,
                lane=str(spec["lane"]),
                position=tuple(spec["position"]),
                icon_key=icon_key,
                prerequisites=tuple(spec.get("prerequisites", ())),
                payload=payload,
            )
        )

    for target_name, lane, prerequisites, position, prerequisite_mode in MAGE_PROMOTION_SPECS:
        nodes.append(
            AbilityTreeNode(
                id=f"mage.promotion.{_slug(target_name)}",
                tree_id=class_name,
                kind=NodeKind.PROMOTION,
                lane=lane,
                position=position,
                icon_key="promotion",
                prerequisites=tuple(prerequisites),
                payload={
                    "name": f"Promote: {target_name}",
                    "target_class": target_name,
                    "target_class_ctor": CLASS_DETAILS[target_name][0],
                    "requirements": _promotion_requirements(target_name, 2),
                    "level_requirement": 30,
                    "prerequisite_mode": prerequisite_mode,
                },
                cost=2,
            )
        )

    return AbilityTree(
        id=class_name,
        class_name=class_name,
        stage=1,
        branches=branches,
        nodes=tuple(nodes),
    )


def _build_explicit_base_tree(class_name: str) -> AbilityTree:
    """Build one six-track base graph with shared promotion prerequisites."""
    specs = BASE_TREE_NODE_SPECS[class_name]
    entries = {
        ability_ctor.__name__: (book, ability_ctor, ability)
        for _level, _tie, book, ability_ctor, ability in _ability_entries(class_name)
    }
    branches = tuple(
        dict.fromkeys(
            str(spec["lane"]) for spec in sorted(specs, key=lambda entry: tuple(entry["position"]))
        )
    )
    nodes: list[AbilityTreeNode] = []

    for spec in specs:
        kind = NodeKind(str(spec["kind"]))
        identifier = str(spec["identifier"])
        lane = str(spec["lane"])
        position = tuple(spec["position"])
        if kind == NodeKind.ABILITY:
            try:
                book, ability_ctor, ability = entries[identifier]
            except KeyError as exc:
                raise ValueError(
                    f"{class_name} tree references unknown ability {identifier}"
                ) from exc
            payload = {
                "name": ABILITY_NODE_NAME_OVERRIDES.get(
                    identifier,
                    ability.name,
                ),
                "book": book,
                "ability_class": ability_ctor,
                "description": getattr(ability, "description", ""),
            }
            icon_key = str(spec.get("icon_key", _ability_icon_key(book, ability)))
        elif kind == NodeKind.TALENT:
            rating_name = str(spec["rating"])
            talent_name = str(spec["name"])
            payload = {
                "name": talent_name,
                "talent_key": identifier,
                "description": (
                    f"{talent_name} deepens the {lane} track and permanently "
                    f"increases {rating_name} by 10%."
                ),
                "bonuses": {
                    "rating_percentages": {rating_name: 0.10},
                },
            }
            icon_key = "skill_passive"
        elif kind == NodeKind.RATING:
            payload = {
                "name": f"+10 {identifier}",
                "rating": identifier,
                "amount": 10,
                "description": f"Permanently increase {identifier} by 10.",
            }
            icon_key = _rating_icon_key(identifier)
        elif kind == NodeKind.MANA:
            payload = {
                "name": "+25 MP",
                "amount": 25,
                "description": "Permanently increase maximum MP by 25.",
            }
            icon_key = "spell_arcane"
        elif kind == NodeKind.HEALTH:
            payload = {
                "name": "+25 HP",
                "amount": 25,
                "description": "Permanently increase maximum HP by 25.",
            }
            icon_key = "skill_defense"
        else:
            raise ValueError(f"Unsupported {class_name} base node kind: {kind.value}")

        if class_name in {"Footpad", "Healer", "Pathfinder"}:
            base_levels = (None, 5, 10, 15, 20, 25)
            level_requirement = base_levels[min(max(0, int(position[1])), len(base_levels) - 1)]
        else:
            level_requirement = _development_level_requirement(1, int(position[1]))
        if level_requirement:
            payload["level_requirement"] = level_requirement
        nodes.append(
            AbilityTreeNode(
                id=str(spec["id"]),
                tree_id=class_name,
                kind=kind,
                lane=lane,
                position=position,
                icon_key=icon_key,
                prerequisites=tuple(spec.get("prerequisites", ())),
                payload=payload,
                cost=int(spec.get("cost", 1)),
            )
        )

    promotions = BASE_TREE_PROMOTION_SPECS[class_name]
    declared_targets = {target for target, _lane, _position, _requirements in promotions}
    expected_targets = set(CLASS_CHILDREN[class_name])
    if declared_targets != expected_targets:
        raise ValueError(
            f"{class_name} explicit promotions mismatch registry; "
            f"missing={sorted(expected_targets - declared_targets)}, "
            f"extra={sorted(declared_targets - expected_targets)}"
        )
    for target_name, lane, position, prerequisites in promotions:
        nodes.append(
            AbilityTreeNode(
                id=f"{_slug(class_name)}.promotion.{_slug(target_name)}",
                tree_id=class_name,
                kind=NodeKind.PROMOTION,
                lane=lane,
                position=position,
                icon_key="promotion",
                prerequisites=tuple(prerequisites),
                payload={
                    "name": f"Promote: {target_name}",
                    "target_class": target_name,
                    "target_class_ctor": CLASS_DETAILS[target_name][0],
                    "requirements": _promotion_requirements(target_name, 2),
                    "level_requirement": 30,
                    "connector_join_at_target_row": len(prerequisites) > 1,
                },
                cost=2,
            )
        )

    return AbilityTree(
        id=class_name,
        class_name=class_name,
        stage=1,
        branches=branches,
        nodes=tuple(nodes),
    )


def _build_weapon_master_tree() -> AbilityTree:
    """Build Weapon Master's asymmetric routes and independent weapon arts."""
    class_name = "Weapon Master"
    branches = tuple(path[0] for path in PROMOTED_TREE_PATHS[class_name])
    entries = {
        ability_ctor.__name__: (book, ability_ctor, ability)
        for _level, _tie, book, ability_ctor, ability in _ability_entries(class_name)
    }
    nodes: list[AbilityTreeNode] = []
    local_ids: dict[str, str] = {}

    for spec in WEAPON_MASTER_TREE_NODE_SPECS:
        kind = NodeKind(spec["kind"])
        suffix = str(spec["id"])
        node_id = f"weapon-master.{kind.value}.{suffix}"
        local_ids[suffix] = node_id
        identifier = str(spec["identifier"])
        if kind == NodeKind.ABILITY:
            book, ability_ctor, ability = entries[identifier]
            payload = {
                "name": str(spec.get("name", ability.name)),
                "book": book,
                "ability_class": ability_ctor,
                "description": getattr(ability, "description", ""),
            }
        elif kind == NodeKind.RATING:
            amount = 20
            payload = {
                "name": f"+{amount} {identifier}",
                "rating": identifier,
                "amount": amount,
                "description": (f"Permanently increase {identifier} by {amount}."),
            }
        else:
            raise ValueError(f"Unsupported Weapon Master node kind: {kind.value}")
        if spec.get("level") is not None:
            payload["level_requirement"] = int(spec["level"])
        for key in (
            "exclusive_group",
            "owned_if_known",
            "prerequisite_mode",
            "stack_if_known",
            "weapon_specialization",
        ):
            if key in spec:
                payload[key] = spec[key]
        nodes.append(
            AbilityTreeNode(
                id=node_id,
                tree_id=class_name,
                kind=kind,
                lane=str(spec["lane"]),
                position=tuple(spec["position"]),
                icon_key=(
                    _ability_icon_key(book, ability)
                    if kind == NodeKind.ABILITY
                    else _rating_icon_key(identifier)
                ),
                prerequisites=tuple(
                    local_ids[prerequisite] for prerequisite in spec.get("prerequisites", ())
                ),
                payload=payload,
                cost=int(spec.get("cost", 1)),
            )
        )

    promotions = (
        ("Berserker", "Berserker", "brutish-strength", (0, 7)),
        (
            "Grandmaster of Arms",
            "Grandmaster",
            "true-piercing-strike",
            (1.5, 7),
        ),
    )
    for target_name, lane, prerequisite, position in promotions:
        nodes.append(
            AbilityTreeNode(
                id=f"weapon-master.promotion.{_slug(target_name)}",
                tree_id=class_name,
                kind=NodeKind.PROMOTION,
                lane=lane,
                position=position,
                icon_key="promotion",
                prerequisites=(local_ids[prerequisite],),
                payload={
                    "name": f"Promote: {target_name}",
                    "target_class": target_name,
                    "target_class_ctor": CLASS_DETAILS[target_name][0],
                    "requirements": _promotion_requirements(target_name, 3),
                    "level_requirement": 60,
                },
                cost=3,
            )
        )
    return AbilityTree(
        id=class_name,
        class_name=class_name,
        stage=2,
        branches=branches,
        nodes=tuple(nodes),
    )


def _build_terminal_weapon_tree(
    class_name: str,
    specs: tuple[dict[str, Any], ...],
) -> AbilityTree:
    """Build an authored terminal Weapon Discipline tree."""
    entries = {
        ability_ctor.__name__: (book, ability_ctor, ability)
        for _level, _tie, book, ability_ctor, ability in _ability_entries(class_name)
    }
    branches = tuple(dict.fromkeys(str(spec["lane"]) for spec in specs))
    nodes: list[AbilityTreeNode] = []
    local_ids: dict[str, str] = {}

    for spec in specs:
        kind = NodeKind(spec["kind"])
        suffix = str(spec["id"])
        node_id = f"{_slug(class_name)}.{kind.value}.{suffix}"
        local_ids[suffix] = node_id
        identifier = str(spec["identifier"])
        if kind == NodeKind.ABILITY:
            book, ability_ctor, ability = entries[identifier]
            payload = {
                "name": str(spec.get("name", ability.name)),
                "book": book,
                "ability_class": ability_ctor,
                "description": getattr(ability, "description", ""),
            }
            if spec.get("kit_effect"):
                payload["kit_effect"] = spec["kit_effect"]
            icon_key = str(spec.get("icon_key", _ability_icon_key(book, ability)))
        elif kind == NodeKind.TALENT:
            payload = {
                "name": str(spec["name"]),
                "talent_key": identifier,
                "description": str(spec["description"]),
            }
            icon_key = "skill_passive"
        elif kind == NodeKind.RATING:
            amount = 30
            payload = {
                "name": f"+{amount} {identifier}",
                "rating": identifier,
                "amount": amount,
                "description": (f"Permanently increase {identifier} by {amount}."),
            }
            icon_key = _rating_icon_key(identifier)
        elif kind == NodeKind.HEALTH:
            amount = RESOURCE_NODE_AMOUNTS[3]
            payload = {
                "name": f"+{amount} HP",
                "amount": amount,
                "description": (f"Permanently increase maximum HP by {amount}."),
            }
            icon_key = "skill_defense"
        else:
            raise ValueError(f"Unsupported {class_name} node kind: {kind.value}")
        if spec.get("level") is not None:
            payload["level_requirement"] = int(spec["level"])
        for key in (
            "available_on_promotion",
            "level_band_gate",
            "owned_if_known",
            "weapon_specialization",
        ):
            if key in spec:
                payload[key] = spec[key]
        nodes.append(
            AbilityTreeNode(
                id=node_id,
                tree_id=class_name,
                kind=kind,
                lane=str(spec["lane"]),
                position=tuple(spec["position"]),
                icon_key=icon_key,
                prerequisites=tuple(
                    local_ids.get(prerequisite, prerequisite)
                    for prerequisite in spec.get("prerequisites", ())
                ),
                payload=payload,
                cost=int(spec.get("cost", 1)),
            )
        )

    return AbilityTree(
        id=class_name,
        class_name=class_name,
        stage=3,
        branches=branches,
        nodes=tuple(nodes),
    )


def _build_lancer_dragoon_tree(
    class_name: str,
    specs: tuple[dict[str, Any], ...],
) -> AbilityTree:
    """Build an authored Jump progression tree."""
    entries = {
        ability_ctor.__name__: (book, ability_ctor, ability)
        for _level, _tie, book, ability_ctor, ability in _ability_entries(class_name)
    }
    branches = tuple(dict.fromkeys(str(spec["lane"]) for spec in specs))
    nodes: list[AbilityTreeNode] = []
    local_ids: dict[str, str] = {}
    for spec in specs:
        raw_kind = str(spec["kind"])
        kind = NodeKind.TALENT if raw_kind == "jump_mod" else NodeKind(raw_kind)
        suffix = str(spec["id"])
        local_ids[suffix] = (
            f"{_slug(class_name)}.jump-mod.{suffix}"
            if raw_kind == "jump_mod"
            else f"{_slug(class_name)}.{kind.value}.{suffix}"
        )

    for spec in specs:
        raw_kind = str(spec["kind"])
        kind = NodeKind.TALENT if raw_kind == "jump_mod" else NodeKind(raw_kind)
        suffix = str(spec["id"])
        node_id = local_ids[suffix]
        identifier = str(spec["identifier"])

        if kind == NodeKind.ABILITY:
            book, ability_ctor, ability = entries[identifier]
            payload = {
                "name": str(spec.get("name", ability.name)),
                "book": book,
                "ability_class": ability_ctor,
                "description": getattr(ability, "description", ""),
            }
            icon_key = _ability_icon_key(book, ability)
        elif kind == NodeKind.TALENT:
            description = spec.get("description")
            if description is None:
                description = f"Unlock the {spec['jump_modification']} Jump modification."
            payload = {
                "name": str(spec["name"]),
                "talent_key": identifier,
                "description": str(description),
            }
            if spec.get("bonuses"):
                payload["bonuses"] = spec["bonuses"]
            if spec.get("kit_effect"):
                payload["kit_effect"] = spec["kit_effect"]
            if spec.get("jump_modification"):
                payload["jump_modification"] = str(spec["jump_modification"])
            icon_key = "skill_mobility"
        elif kind == NodeKind.RATING:
            amount = 20 if class_name == "Lancer" else 30
            payload = {
                "name": f"+{amount} {identifier}",
                "rating": identifier,
                "amount": amount,
                "description": (f"Permanently increase {identifier} by {amount}."),
            }
            icon_key = _rating_icon_key(identifier)
        elif kind == NodeKind.HEALTH:
            stage = CLASS_DETAILS[class_name][1]
            amount = RESOURCE_NODE_AMOUNTS[stage]
            payload = {
                "name": f"+{amount} HP",
                "amount": amount,
                "description": (f"Permanently increase maximum HP by {amount}."),
            }
            icon_key = "skill_defense"
        else:
            raise ValueError(f"Unsupported {class_name} node kind: {kind.value}")

        if spec.get("level") is not None:
            payload["level_requirement"] = int(spec["level"])
        for key in (
            "available_on_promotion",
            "level_band_gate",
            "owned_if_known",
            "requires_known_ability",
        ):
            if key in spec:
                payload[key] = spec[key]
        nodes.append(
            AbilityTreeNode(
                id=node_id,
                tree_id=class_name,
                kind=kind,
                lane=str(spec["lane"]),
                position=tuple(spec["position"]),
                icon_key=icon_key,
                prerequisites=tuple(
                    local_ids.get(prerequisite, prerequisite)
                    for prerequisite in spec.get("prerequisites", ())
                ),
                payload=payload,
                cost=int(spec.get("cost", 1)),
            )
        )

    stage = 2 if class_name == "Lancer" else 3
    if class_name == "Lancer":
        nodes.append(
            AbilityTreeNode(
                id="lancer.promotion.dragoon",
                tree_id=class_name,
                kind=NodeKind.PROMOTION,
                lane="Jump Core",
                position=(3, 7),
                icon_key="promotion",
                prerequisites=(
                    "lancer.ability.vigilant-landing",
                    "lancer.ability.polearm-excellence",
                ),
                payload={
                    "name": "Promote: Dragoon",
                    "target_class": "Dragoon",
                    "target_class_ctor": CLASS_DETAILS["Dragoon"][0],
                    "requirements": _promotion_requirements("Dragoon", 3),
                    "level_requirement": 60,
                    "connector_channel_columns": {
                        "lancer.ability.vigilant-landing": 1,
                        "lancer.ability.polearm-excellence": 4,
                    },
                },
                cost=3,
            )
        )
    else:
        lancer_tree = _build_lancer_dragoon_tree(
            "Lancer",
            LANCER_TREE_NODE_SPECS,
        )
        inherited_nodes = [node for node in lancer_tree.nodes if node.kind != NodeKind.PROMOTION]
        nodes = [*inherited_nodes, *nodes]
        branches = tuple(dict.fromkeys(node.lane for node in nodes))

    return AbilityTree(
        id=class_name,
        class_name=class_name,
        stage=stage,
        branches=branches,
        nodes=tuple(nodes),
    )


def _build_authored_kit_tree(
    class_name: str,
    specs: tuple[dict[str, Any], ...],
    *,
    promotion_target: str | None = None,
    promotion_position: tuple[float, int] | None = None,
    promotion_prerequisites: tuple[str, ...] = (),
    promotion_prerequisite_mode: str = "all",
    promotion_connector_join_at_target_row: bool = False,
) -> AbilityTree:
    """Build a compact authored first- or terminal-promotion class tree."""
    entries = {
        ability_ctor.__name__: (book, ability_ctor, ability)
        for _level, _tie, book, ability_ctor, ability in _ability_entries(class_name)
    }
    stage = CLASS_DETAILS[class_name][1]
    branches = tuple(dict.fromkeys(str(spec["lane"]) for spec in specs))
    nodes: list[AbilityTreeNode] = []
    local_ids: dict[str, str] = {}
    for spec in specs:
        kind = NodeKind(str(spec["kind"]))
        suffix = str(spec["id"])
        local_ids[suffix] = f"{_slug(class_name)}.{kind.value}.{suffix}"

    for spec in specs:
        kind = NodeKind(str(spec["kind"]))
        suffix = str(spec["id"])
        identifier = str(spec["identifier"])
        node_id = local_ids[suffix]
        if kind == NodeKind.ABILITY:
            book, ability_ctor, ability = entries[identifier]
            payload = {
                "name": str(spec.get("name", ability.name)),
                "book": book,
                "ability_class": ability_ctor,
                "description": str(spec.get("description", getattr(ability, "description", ""))),
            }
            icon_key = str(spec.get("icon_key", _ability_icon_key(book, ability)))
        elif kind == NodeKind.TALENT:
            payload = {
                "name": str(spec["name"]),
                "talent_key": identifier,
                "description": str(spec["description"]),
            }
            if spec.get("bonuses"):
                payload["bonuses"] = spec["bonuses"]
            if spec.get("kit_effect"):
                payload["kit_effect"] = spec["kit_effect"]
            icon_key = "skill_passive"
        elif kind == NodeKind.RATING:
            amount = 20 if stage == 2 else 30
            payload = {
                "name": f"+{amount} {identifier}",
                "rating": identifier,
                "amount": amount,
                "description": (f"Permanently increase {identifier} by {amount}."),
            }
            icon_key = _rating_icon_key(identifier)
        elif kind == NodeKind.HEALTH:
            amount = RESOURCE_NODE_AMOUNTS[stage]
            payload = {
                "name": f"+{amount} HP",
                "amount": amount,
                "description": (f"Permanently increase maximum HP by {amount}."),
            }
            icon_key = "skill_defense"
        elif kind == NodeKind.MANA:
            amount = RESOURCE_NODE_AMOUNTS[stage]
            payload = {
                "name": f"+{amount} MP",
                "amount": amount,
                "description": (f"Permanently increase maximum MP by {amount}."),
            }
            icon_key = "spell_arcane"
        else:
            raise ValueError(f"Unsupported {class_name} node kind: {kind.value}")

        if spec.get("level") is not None:
            payload["level_requirement"] = int(spec["level"])
        for key in (
            "available_on_promotion",
            "exclusive_group",
            "level_band_gate",
            "owned_if_known",
            "prerequisite_mode",
            "requires_known_ability",
            "school_affinity",
            "upgrade_without_source",
            "hidden_until_known",
            "quest_unlock",
            "revealed_name",
        ):
            if key in spec:
                payload[key] = spec[key]
        if spec.get("connector_enter_from_top"):
            payload["connector_enter_from_top"] = True
        if spec.get("connector_channel_columns"):
            payload["connector_channel_columns"] = {
                local_ids.get(prerequisite, prerequisite): column
                for prerequisite, column in spec["connector_channel_columns"].items()
            }
        nodes.append(
            AbilityTreeNode(
                id=node_id,
                tree_id=class_name,
                kind=kind,
                lane=str(spec["lane"]),
                position=tuple(spec["position"]),
                icon_key=icon_key,
                prerequisites=tuple(
                    local_ids.get(prerequisite, prerequisite)
                    for prerequisite in spec.get("prerequisites", ())
                ),
                payload=payload,
                cost=int(spec.get("cost", 1)),
            )
        )

    if promotion_target:
        if promotion_position is None:
            raise ValueError(f"{class_name} promotion position is required")
        nodes.append(
            AbilityTreeNode(
                id=f"{_slug(class_name)}.promotion.{_slug(promotion_target)}",
                tree_id=class_name,
                kind=NodeKind.PROMOTION,
                lane=branches[0],
                position=promotion_position,
                icon_key="promotion",
                prerequisites=tuple(
                    local_ids.get(prerequisite, prerequisite)
                    for prerequisite in promotion_prerequisites
                ),
                payload={
                    "name": f"Promote: {promotion_target}",
                    "target_class": promotion_target,
                    "target_class_ctor": CLASS_DETAILS[promotion_target][0],
                    "floating_promotion": not promotion_prerequisites,
                    "requirements": _promotion_requirements(
                        promotion_target,
                        3,
                    ),
                    "level_requirement": 60,
                    "prerequisite_mode": promotion_prerequisite_mode,
                    "connector_join_at_target_row": (promotion_connector_join_at_target_row),
                },
                cost=3,
            )
        )

    return AbilityTree(
        id=class_name,
        class_name=class_name,
        stage=stage,
        branches=branches,
        nodes=tuple(nodes),
    )


def _build_cleric_tree() -> AbilityTree:
    """Build Cleric's four disciplines and two independent promotions."""
    tree = _build_authored_kit_tree("Cleric", CLERIC_TREE_NODE_SPECS)
    promotions = (
        (
            "Hierophant",
            (0.5, 7),
            ("cleric.ability.pious-bounty", "cleric.talent.overflowing-grace"),
        ),
        (
            "Templar",
            (2.5, 7),
            ("cleric.talent.bastion-practice", "cleric.talent.consecrated-blows"),
        ),
    )
    nodes = list(tree.nodes)
    for target_name, position, prerequisites in promotions:
        nodes.append(
            AbilityTreeNode(
                id=f"cleric.promotion.{_slug(target_name)}",
                tree_id="Cleric",
                kind=NodeKind.PROMOTION,
                lane="Devotion" if target_name == "Hierophant" else "Bulwark",
                position=position,
                icon_key="promotion",
                prerequisites=prerequisites,
                payload={
                    "name": f"Promote: {target_name}",
                    "target_class": target_name,
                    "target_class_ctor": CLASS_DETAILS[target_name][0],
                    "requirements": _promotion_requirements(target_name, 3),
                    "level_requirement": 60,
                    "prerequisite_mode": "any",
                    "connector_join_at_target_row": True,
                },
                cost=3,
            )
        )
    return replace(tree, nodes=tuple(nodes))


def _build_druid_tree() -> AbilityTree:
    """Build Druid's four disciplines and two independent promotions."""
    tree = _build_authored_kit_tree("Druid", DRUID_TREE_NODE_SPECS)
    promotions = (
        (
            "Lycan",
            "Panther Form",
            (0.5, 7),
            ("druid.talent.apex-prowler", "druid.talent.guardian-beast"),
        ),
        (
            "Archdruid",
            "Growth and Stars",
            (2.5, 7),
            ("druid.talent.earthen-toxins", "druid.ability.starfall"),
        ),
    )
    nodes = list(tree.nodes)
    for target_name, lane, position, prerequisites in promotions:
        nodes.append(
            AbilityTreeNode(
                id=f"druid.promotion.{_slug(target_name)}",
                tree_id="Druid",
                kind=NodeKind.PROMOTION,
                lane=lane,
                position=position,
                icon_key="promotion",
                prerequisites=prerequisites,
                payload={
                    "name": f"Promote: {target_name}",
                    "target_class": target_name,
                    "target_class_ctor": CLASS_DETAILS[target_name][0],
                    "requirements": _promotion_requirements(target_name, 3),
                    "level_requirement": 60,
                    "prerequisite_mode": "any",
                    "connector_join_at_target_row": True,
                },
                cost=3,
            )
        )
    return replace(tree, nodes=tuple(nodes))


def _build_warlock_tree() -> AbilityTree:
    """Build the Warlock development paths and its two terminal promotions."""
    base_tree = _build_authored_kit_tree("Warlock", WARLOCK_TREE_NODE_SPECS)
    promotions = (
        AbilityTreeNode(
            id="warlock.promotion.shadowcaster",
            tree_id="Warlock",
            kind=NodeKind.PROMOTION,
            lane="Umbral Offense",
            position=(0.5, 7),
            icon_key="promotion",
            prerequisites=(
                "warlock.ability.doom",
                "warlock.ability.mana-drain",
                "warlock.ability.shadow-bolt-2",
            ),
            payload={
                "name": "Promote: Shadowcaster",
                "target_class": "Shadowcaster",
                "target_class_ctor": CLASS_DETAILS["Shadowcaster"][0],
                "floating_promotion": False,
                "requirements": _promotion_requirements("Shadowcaster", 3),
                "level_requirement": 60,
                "prerequisite_groups": (
                    (
                        "warlock.ability.doom",
                        "warlock.ability.mana-drain",
                    ),
                    ("warlock.ability.shadow-bolt-2",),
                ),
                "connector_join_at_target_row": True,
            },
            cost=3,
        ),
        AbilityTreeNode(
            id="warlock.promotion.demonologist",
            tree_id="Warlock",
            kind=NodeKind.PROMOTION,
            lane="Curses",
            position=(3.5, 7),
            icon_key="promotion",
            prerequisites=(
                "warlock.ability.curse-swarms",
                "warlock.ability.life-tap",
            ),
            payload={
                "name": "Promote: Demonologist",
                "target_class": "Demonologist",
                "target_class_ctor": CLASS_DETAILS["Demonologist"][0],
                "floating_promotion": False,
                "requirements": _promotion_requirements("Demonologist", 3),
                "level_requirement": 60,
                "prerequisite_mode": "any",
                "connector_join_at_target_row": True,
            },
            cost=3,
        ),
    )
    return replace(base_tree, nodes=(*base_tree.nodes, *promotions))


THAUMATURGIST_XENID_GROUPS = (
    ("Animal", "Hodag", "Caladrius"),
    ("Humanoid", "Patagon", "Kobalos"),
    ("Monster", "Dilong", "Cacus"),
    ("Spirit", "Agloolik", "Izulu"),
    ("Fiend", "Hala", "Lamashtu"),
    ("Celestial", "Seraphim", "Bardi"),
    ("Dragon", "Tiamat", "Zahhak"),
)


def _build_thaumaturgist_tree() -> AbilityTree:
    """Build Callings, Xenid choices, conduit utility, and Miracles explicitly."""
    class_name = "Thaumaturgist"
    branches = (
        "Calling",
        "Xenid Choice",
        "Xenid Ultimate",
        "Conduit",
        "Miracles",
    )
    nodes: list[AbilityTreeNode] = []

    mage_animal = next(
        node for node in _build_mage_tree().nodes if node.id == "mage.ability.conjure-animal"
    )
    conjurer_tree = _build_authored_kit_tree(
        "Conjurer",
        CONJURER_TREE_NODE_SPECS,
    )
    calling_nodes = [
        replace(
            mage_animal,
            lane="Calling",
            position=(0, 1),
            payload={
                **mage_animal.payload,
                "available_on_promotion": True,
                "owned_if_known": True,
            },
            prerequisites=(),
        )
    ]
    calling_nodes.extend(
        replace(node, position=(0, row))
        for row, node in enumerate(
            (
                node
                for node_id in (
                    "conjurer.ability.conjure-humanoid",
                    "conjurer.ability.conjure-monster",
                    "conjurer.ability.conjure-spirit",
                    "conjurer.ability.conjure-fiend",
                    "conjurer.ability.conjure-celestial",
                    "conjurer.ability.conjure-dragon",
                )
                for node in conjurer_tree.nodes
                if node.id == node_id
            ),
            start=2,
        )
    )
    nodes.extend(calling_nodes)

    for row, ((category, first, second), calling) in enumerate(
        zip(THAUMATURGIST_XENID_GROUPS, calling_nodes)
    ):
        choice_id = f"thaumaturgist.talent.bind-{_slug(category)}"
        nodes.append(
            AbilityTreeNode(
                id=choice_id,
                tree_id=class_name,
                kind=NodeKind.TALENT,
                lane="Xenid Choice",
                position=(1, row + 1),
                icon_key="skill_passive",
                prerequisites=(calling.id,),
                payload={
                    "name": f"Bind Xenid - {category}",
                    "talent_key": f"thaumaturgist.bind-{_slug(category)}",
                    "xenid_category": category,
                    "xenid_options": (first, second),
                    "available_on_promotion": True,
                    "description": (
                        f"Permanently choose either {first} or {second} as the "
                        f"{category} Xenid for this Calling."
                    ),
                },
            )
        )
        nodes.append(
            AbilityTreeNode(
                id=f"thaumaturgist.talent.{_slug(category)}-ultimate",
                tree_id=class_name,
                kind=NodeKind.TALENT,
                lane="Xenid Ultimate",
                position=(2, row + 1),
                icon_key="skill_passive",
                prerequisites=(choice_id,),
                payload={
                    "name": f"{category} Ultimate",
                    "talent_key": f"thaumaturgist.{_slug(category)}-ultimate",
                    "xenid_ultimate_category": category,
                    "available_on_promotion": True,
                    "description": (f"Unlock the ultimate ability of the chosen {category} Xenid."),
                },
            )
        )

    ability_entries = {
        ability_ctor.__name__: (book, ability_ctor, ability)
        for _level, _tie, book, ability_ctor, ability in _ability_entries(class_name)
    }
    previous_id: str | None = None
    for row, (identifier, level) in enumerate(
        (
            ("HealSummon", 65),
            ("ConduitCommand", 70),
            ("RaiseSummon", 75),
        ),
        start=2,
    ):
        book, ability_ctor, ability = ability_entries[identifier]
        node_id = f"thaumaturgist.ability.{_slug(identifier)}"
        nodes.append(
            AbilityTreeNode(
                id=node_id,
                tree_id=class_name,
                kind=NodeKind.ABILITY,
                lane="Conduit",
                position=(3, row),
                icon_key=_ability_icon_key(book, ability),
                prerequisites=(previous_id,) if previous_id else (),
                payload={
                    "name": ability.name,
                    "book": book,
                    "ability_class": ability_ctor,
                    "description": getattr(ability, "description", ""),
                    "level_requirement": level,
                },
            )
        )
        previous_id = node_id
    nodes.append(
        AbilityTreeNode(
            id="thaumaturgist.talent.conduit-mastery",
            tree_id=class_name,
            kind=NodeKind.TALENT,
            lane="Conduit",
            position=(3, 5),
            icon_key="skill_passive",
            prerequisites=(previous_id,),
            payload={
                "name": "Conduit Mastery",
                "talent_key": "thaumaturgist.conduit-mastery",
                "level_requirement": 80,
                "description": (
                    "Amplifies the effects the Thaumaturgist's chosen Xenids have on the caster."
                ),
            },
            cost=2,
        )
    )
    previous_id = None
    for row, (identifier, level) in enumerate(
        (
            ("MiracleBlade", 65),
            ("MiracleShackles", 70),
            ("MiraclePotion", 75),
            ("MiracleCrystal", 80),
        ),
        start=2,
    ):
        book, ability_ctor, ability = ability_entries[identifier]
        node_id = f"thaumaturgist.ability.{_slug(identifier)}"
        nodes.append(
            AbilityTreeNode(
                id=node_id,
                tree_id=class_name,
                kind=NodeKind.ABILITY,
                lane="Miracles",
                position=(4, row),
                icon_key=_ability_icon_key(book, ability),
                prerequisites=(previous_id,) if previous_id else (),
                payload={
                    "name": ability.name,
                    "book": book,
                    "ability_class": ability_ctor,
                    "description": getattr(ability, "description", ""),
                    "level_requirement": level,
                },
                cost=2,
            )
        )
        previous_id = node_id
    return AbilityTree(
        id=class_name,
        class_name=class_name,
        stage=3,
        branches=branches,
        nodes=tuple(nodes),
    )


def _build_authored_tree(class_name: str) -> AbilityTree:
    """Build one declared class tree from its catalog and authored identity."""
    if class_name not in AUTHORED_TREE_CLASSES:
        raise ValueError(f"{class_name} has no authored ability-tree identity")
    if class_name == "Warrior":
        return _build_warrior_tree()
    if class_name == "Mage":
        return _build_mage_tree()
    if class_name in BASE_TREE_NODE_SPECS:
        return _build_explicit_base_tree(class_name)
    if class_name == "Weapon Master":
        return _build_weapon_master_tree()
    if class_name == "Berserker":
        return _build_terminal_weapon_tree(
            class_name,
            BERSERKER_TREE_NODE_SPECS,
        )
    if class_name == "Grandmaster of Arms":
        return _build_terminal_weapon_tree(
            class_name,
            GRANDMASTER_TREE_NODE_SPECS,
        )
    if class_name == "Lancer":
        return _build_lancer_dragoon_tree(
            class_name,
            LANCER_TREE_NODE_SPECS,
        )
    if class_name == "Dragoon":
        return _build_lancer_dragoon_tree(
            class_name,
            DRAGOON_TREE_NODE_SPECS,
        )
    if class_name == "Sentinel":
        return _build_authored_kit_tree(
            class_name,
            SENTINEL_TREE_NODE_SPECS,
            promotion_target="Stalwart Defender",
            promotion_position=(1.5, 8),
            promotion_prerequisites=(
                "watchful-reprisal",
                "resolute-guard",
                "shielding-ward",
                "braggadocious",
            ),
            promotion_prerequisite_mode="any",
            promotion_connector_join_at_target_row=True,
        )
    if class_name == "Assassin":
        return _build_authored_kit_tree(
            class_name,
            ASSASSIN_TREE_NODE_SPECS,
            promotion_target="Ninja",
            promotion_position=(2, 6),
            promotion_prerequisites=("cutthroat",),
        )
    if class_name == "Thief":
        return _build_authored_kit_tree(
            class_name,
            THIEF_TREE_NODE_SPECS,
            promotion_target="Rogue",
            promotion_position=(1.5, 7),
            promotion_prerequisites=(
                "fortune-favors-bold",
                "reversal",
                "master-tools",
                "clean-getaway",
            ),
            promotion_prerequisite_mode="any",
            promotion_connector_join_at_target_row=True,
        )
    if class_name == "Rogue":
        return _build_authored_kit_tree(class_name, ROGUE_TREE_NODE_SPECS)
    if class_name == "Inquisitor":
        return _build_authored_kit_tree(
            class_name,
            INQUISITOR_TREE_NODE_SPECS,
            promotion_target="Seeker",
            promotion_position=(1.5, 7),
            promotion_prerequisites=("keen-eye", "true-strike"),
            promotion_prerequisite_mode="any",
            promotion_connector_join_at_target_row=True,
        )
    if class_name == "Seeker":
        return _build_authored_kit_tree(class_name, SEEKER_TREE_NODE_SPECS)
    if class_name == "Druid":
        return _build_druid_tree()
    if class_name == "Lycan":
        return _build_authored_kit_tree(class_name, LYCAN_TREE_NODE_SPECS)
    if class_name == "Archdruid":
        return _build_authored_kit_tree(class_name, ARCHDRUID_TREE_NODE_SPECS)
    if class_name == "Diviner":
        return _build_authored_kit_tree(
            class_name,
            DIVINER_TREE_NODE_SPECS,
            promotion_target="Astromancer",
            promotion_position=(1.5, 7),
            promotion_prerequisites=(
                "open-sigils",
                "doublecast",
                "berserk",
                "temporary-stasis",
            ),
            promotion_prerequisite_mode="any",
            promotion_connector_join_at_target_row=True,
        )
    if class_name == "Astromancer":
        return _build_authored_kit_tree(class_name, ASTROMANCER_TREE_NODE_SPECS)
    if class_name == "Shaman":
        return _build_authored_kit_tree(
            class_name,
            SHAMAN_TREE_NODE_SPECS,
            promotion_target="Soulcatcher",
            promotion_position=(1.5, 7),
            promotion_prerequisites=(
                "totem-surge",
                "astral-shift",
                "double-strike",
            ),
            promotion_prerequisite_mode="any",
            promotion_connector_join_at_target_row=True,
        )
    if class_name == "Soulcatcher":
        return _build_authored_kit_tree(class_name, SOULCATCHER_TREE_NODE_SPECS)
    if class_name == "Ranger":
        return _build_authored_kit_tree(
            class_name,
            RANGER_TREE_NODE_SPECS,
            promotion_target="Beast Master",
            promotion_position=(1, 6),
            promotion_prerequisites=("companion-bond",),
        )
    if class_name == "Beast Master":
        return _build_authored_kit_tree(
            class_name,
            BEAST_MASTER_TREE_NODE_SPECS,
        )
    if class_name == "Bard":
        return _build_authored_kit_tree(
            class_name,
            BARD_TREE_NODE_SPECS,
            promotion_target="Troubadour",
            promotion_position=(2, 7),
            promotion_prerequisites=(
                "resonant-hall",
                "crescendo-reserve",
                "copyist",
                "prismatic-flourish",
            ),
            promotion_prerequisite_mode="any",
            promotion_connector_join_at_target_row=True,
        )
    if class_name == "Troubadour":
        return _build_authored_kit_tree(
            class_name,
            TROUBADOUR_TREE_NODE_SPECS,
        )
    if class_name == "Spell Stealer":
        return _build_authored_kit_tree(
            class_name,
            SPELL_STEALER_TREE_NODE_SPECS,
            promotion_target="Arcane Trickster",
            promotion_position=(0.5, 7),
            promotion_prerequisites=("perfect-forgery", "controlled-discharge"),
            promotion_prerequisite_mode="any",
            promotion_connector_join_at_target_row=True,
        )
    if class_name == "Arcane Trickster":
        return _build_authored_kit_tree(
            class_name,
            ARCANE_TRICKSTER_TREE_NODE_SPECS,
        )
    if class_name == "Cleric":
        return _build_cleric_tree()
    if class_name == "Templar":
        return _build_authored_kit_tree(
            class_name,
            TEMPLAR_TREE_NODE_SPECS,
        )
    if class_name == "Hierophant":
        return _build_authored_kit_tree(
            class_name,
            HIEROPHANT_TREE_NODE_SPECS,
        )
    if class_name == "Monk":
        return _build_authored_kit_tree(
            class_name,
            MONK_TREE_NODE_SPECS,
            promotion_target="Master Monk",
            promotion_position=(1, 7),
            promotion_prerequisites=("uppercut", "mirror-stillness", "guarded-purity"),
            promotion_prerequisite_mode="any",
            promotion_connector_join_at_target_row=True,
        )
    if class_name == "Master Monk":
        return _build_authored_kit_tree(class_name, MASTER_MONK_TREE_NODE_SPECS)
    if class_name == "Priest":
        return _build_authored_kit_tree(
            class_name,
            PRIEST_TREE_NODE_SPECS,
            promotion_target="Archbishop",
            promotion_position=(1.5, 7),
            promotion_prerequisites=(
                "holy-disorientation",
                "fervent-supplication",
                "arcane-renewal",
                "merciful-prayer",
            ),
            promotion_prerequisite_mode="any",
            promotion_connector_join_at_target_row=True,
        )
    if class_name == "Archbishop":
        return _build_authored_kit_tree(class_name, ARCHBISHOP_TREE_NODE_SPECS)
    if class_name == "Ninja":
        return _build_authored_kit_tree(
            class_name,
            NINJA_TREE_NODE_SPECS,
        )
    if class_name == "Stalwart Defender":
        return _build_authored_kit_tree(
            class_name,
            STALWART_DEFENDER_TREE_NODE_SPECS,
        )
    if class_name == "Paladin":
        return _build_authored_kit_tree(
            class_name,
            PALADIN_TREE_NODE_SPECS,
            promotion_target="Crusader",
            promotion_position=(2.5, 7),
            promotion_prerequisites=(
                "oath-judgment",
                "oath-shelter",
            ),
            promotion_prerequisite_mode="any",
            promotion_connector_join_at_target_row=True,
        )
    if class_name == "Crusader":
        return _build_authored_kit_tree(
            class_name,
            CRUSADER_TREE_NODE_SPECS,
        )
    if class_name == "Spellblade":
        return _build_authored_kit_tree(
            class_name,
            SPELLBLADE_TREE_NODE_SPECS,
            promotion_target="Knight Enchanter",
            promotion_position=(1.5, 7),
            promotion_prerequisites=(
                "enhance-blade",
                "enhance-armor",
                "storage-capacity",
            ),
            promotion_prerequisite_mode="any",
            promotion_connector_join_at_target_row=True,
        )
    if class_name == "Sorcerer":
        return _build_authored_kit_tree(
            class_name,
            SORCERER_TREE_NODE_SPECS,
            promotion_target="Wizard",
            promotion_position=(1, 7),
            promotion_prerequisites=(
                "classical-enrichment",
                "arcane-ritual",
            ),
            promotion_prerequisite_mode="any",
            promotion_connector_join_at_target_row=True,
        )
    if class_name == "Wizard":
        return _build_authored_kit_tree(
            class_name,
            WIZARD_TREE_NODE_SPECS,
        )
    if class_name == "Warlock":
        return _build_warlock_tree()
    if class_name == "Shadowcaster":
        return _build_authored_kit_tree(
            class_name,
            SHADOWCASTER_TREE_NODE_SPECS,
        )
    if class_name == "Demonologist":
        return _build_authored_kit_tree(
            class_name,
            DEMONOLOGIST_TREE_NODE_SPECS,
        )
    if class_name == "Knight Enchanter":
        return _build_authored_kit_tree(
            class_name,
            KNIGHT_ENCHANTER_TREE_NODE_SPECS,
        )
    if class_name == "Conjurer":
        return _build_authored_kit_tree(
            class_name,
            CONJURER_TREE_NODE_SPECS,
            promotion_target="Thaumaturgist",
            promotion_position=(1.5, 7),
            promotion_prerequisites=(
                "barrier-wall",
                "mana-barbs",
                "explosive-decoy",
                "conjure-dragon",
            ),
            promotion_prerequisite_mode="any",
            promotion_connector_join_at_target_row=True,
        )
    if class_name == "Thaumaturgist":
        return _build_thaumaturgist_tree()
    _ctor, stage, _parent = CLASS_DETAILS[class_name]
    entries = _ability_entries(class_name)
    branches, ability_branches, promotion_branches = _tree_branch_specs(
        class_name,
        entries,
    )
    lane_nodes: dict[str, list[AbilityTreeNode]] = {lane: [] for lane in branches}
    all_nodes: list[AbilityTreeNode] = []

    for _old_level, _tie, book, ability_ctor, ability in entries:
        lane = ability_branches.get(ability_ctor.__name__, _ability_lane(book, ability))
        node_id = f"{_slug(class_name)}.ability.{_slug(ability_ctor.__name__)}"
        if lane_nodes[lane]:
            prerequisites = (lane_nodes[lane][-1].id,)
        else:
            prerequisites = ()
        row = len(lane_nodes[lane])
        level_requirement = _development_level_requirement(stage, row)
        payload = {
            "name": ABILITY_NODE_NAME_OVERRIDES.get(
                ability_ctor.__name__,
                ability.name,
            ),
            "book": book,
            "ability_class": ability_ctor,
            "description": getattr(ability, "description", ""),
            **({"level_requirement": level_requirement} if level_requirement else {}),
        }
        if class_name == "Knight Enchanter" and ability.name in {"Mana Tap", "Enhance Armor"}:
            payload["owned_if_known"] = True
        node = AbilityTreeNode(
            id=node_id,
            tree_id=class_name,
            kind=NodeKind.ABILITY,
            lane=lane,
            position=(branches.index(lane), row),
            icon_key=_ability_icon_key(book, ability),
            prerequisites=prerequisites,
            payload=payload,
        )
        lane_nodes[lane].append(node)
        all_nodes.append(node)

    minimum, maximum = _tree_size_range(class_name, stage)
    if stage == 1:
        authored_talents = ()
    else:
        authored_talents = tuple(
            (name, talent_key, rating_name, None)
            for name, talent_key, rating_name in CLASS_KIT_TALENTS.get(class_name, ())
            if talent_key in AUTHORED_PROMOTED_TALENT_KEYS
        )
    advanced_talent_key = authored_talents[-1][1] if stage == 3 and authored_talents else None

    def talent_mechanic_text(talent_key: str) -> str:
        if talent_key == "summoner.conduit-mastery":
            return " It also increases permanent-summon damage by 5%."
        if talent_key == "summoner.true-name-ward":
            return " It also increases permanent-summon maximum HP by 5%."
        effect = TALENT_KIT_EFFECTS.get(talent_key)
        if effect and effect[0] == "meter_cap":
            return f" It also increases the associated class-kit meter cap by {effect[2]}."
        if effect and effect[0] == "control_progress":
            return " It also records one extra successful Lycan control response."
        if effect and effect[0] == "bond_power":
            return (
                "Increases the companion's bond-derived combat bonus "
                f"by {effect[2]} percentage points."
            )
        raise ValueError(f"{talent_key} has no authored class-kit effect")

    for talent_name, talent_key, rating_name, authored_lane in authored_talents[
        : max(0, maximum - len(all_nodes))
    ]:
        preferred = authored_lane or next(
            (
                branch
                for branch in branches
                if _branch_rating_focus(class_name, branch) == rating_name
            ),
            min(branches, key=lambda branch: len(lane_nodes[branch])),
        )
        row = len(lane_nodes[preferred])
        level_requirement = _development_level_requirement(stage, row)
        node = AbilityTreeNode(
            id=f"{_slug(class_name)}.talent.{_slug(talent_key)}",
            tree_id=class_name,
            kind=NodeKind.TALENT,
            lane=preferred,
            position=(branches.index(preferred), row),
            icon_key="skill_passive",
            prerequisites=((lane_nodes[preferred][-1].id,) if lane_nodes[preferred] else ()),
            payload={
                "name": talent_name,
                "talent_key": talent_key,
                "description": talent_mechanic_text(talent_key),
                **(
                    {"kit_effect": TALENT_KIT_EFFECTS[talent_key]}
                    if talent_key in TALENT_KIT_EFFECTS
                    else {}
                ),
                **({"level_requirement": level_requirement} if level_requirement else {}),
            },
            cost=2 if talent_key == advanced_talent_key else 1,
        )
        lane_nodes[preferred].append(node)
        all_nodes.append(node)

    terminal_by_lane = {
        lane: (nodes[-1].id if nodes else None) for lane, nodes in lane_nodes.items()
    }
    promotion_row = max((len(nodes) for nodes in lane_nodes.values()), default=0)
    promotions_in_lane: dict[str, int] = {lane: 0 for lane in branches}
    for target_name in CLASS_CHILDREN[class_name]:
        lane = promotion_branches[target_name]
        terminal = terminal_by_lane[lane]
        row = promotion_row + promotions_in_lane[lane]
        promotions_in_lane[lane] += 1
        node = AbilityTreeNode(
            id=f"{_slug(class_name)}.promotion.{_slug(target_name)}",
            tree_id=class_name,
            kind=NodeKind.PROMOTION,
            lane=lane,
            position=(branches.index(lane), row),
            icon_key="promotion",
            prerequisites=(terminal,) if terminal else (),
            payload={
                "name": f"Promote: {target_name}",
                "target_class": target_name,
                "target_class_ctor": CLASS_DETAILS[target_name][0],
                "requirements": _promotion_requirements(target_name, stage + 1),
                "level_requirement": 30 if stage == 1 else 60,
                **(
                    {"floating_promotion": True}
                    if class_name == "Conjurer" and terminal is None
                    else {}
                ),
            },
            cost=2 if stage == 1 else 3,
        )
        lane_nodes[lane].append(node)
        all_nodes.append(node)

    if class_name in {"Sorcerer", "Wizard"}:
        mage_tree = _build_mage_tree()
        carried_nodes = [
            replace(
                node,
                position=MAGE_CARRIED_NODE_POSITIONS[node.id],
            )
            for node in mage_tree.nodes
            if node.id in MAGE_CARRIED_NODE_POSITIONS
        ]
        all_nodes.extend(carried_nodes)
        branches = (*branches, "Elementalism", "Arcana")
    development_node_count = sum(node.kind != NodeKind.PROMOTION for node in all_nodes)
    if not minimum <= development_node_count <= maximum:
        raise ValueError(
            f"{class_name} tree has {development_node_count} development nodes; "
            f"expected {minimum}-{maximum}"
        )
    return AbilityTree(
        id=class_name,
        class_name=class_name,
        stage=stage,
        branches=branches,
        nodes=tuple(all_nodes),
    )


def _remove_numeric_node_level_gates(tree: AbilityTree) -> AbilityTree:
    """Apply the global rule that plain rating/resource nodes are path-gated only."""
    normalized = []
    for node in tree.nodes:
        if (
            node.kind in {NodeKind.RATING, NodeKind.HEALTH, NodeKind.MANA}
            and "level_requirement" in node.payload
            and not node.payload.get("level_band_gate")
        ):
            payload = dict(node.payload)
            payload.pop("level_requirement", None)
            node = replace(node, payload=payload)
        normalized.append(node)
    return replace(tree, nodes=tuple(normalized))


def _add_promotion_routing_row(tree: AbilityTree) -> AbilityTree:
    """Reserve an eighth layout row beneath development in seven-row trees."""
    if tree.class_name == "Sentinel":
        return replace(
            tree,
            nodes=tuple(
                replace(
                    node,
                    position=(
                        node.position[0],
                        (7 if node.kind == NodeKind.PROMOTION else node.position[1] - 2),
                    ),
                )
                for node in tree.nodes
            ),
        )
    if tree.class_name == "Conjurer":
        return replace(
            tree,
            nodes=tuple(
                (
                    node
                    if node.kind == NodeKind.PROMOTION
                    else replace(
                        node,
                        position=(node.position[0], node.position[1] - 1),
                    )
                )
                for node in tree.nodes
            ),
        )
    if not tree.nodes or max(node.position[1] for node in tree.nodes) != 6:
        return tree
    if not any(node.kind == NodeKind.PROMOTION for node in tree.nodes):
        return tree
    return replace(
        tree,
        nodes=tuple(
            (
                replace(node, position=(node.position[0], 7))
                if node.kind == NodeKind.PROMOTION and node.position[1] == 6
                else node
            )
            for node in tree.nodes
        ),
    )


ABILITY_TREES = {
    name: _add_promotion_routing_row(_remove_numeric_node_level_gates(_build_authored_tree(name)))
    for name in CLASS_DETAILS
}
TREE_NODES = {node.id: node for tree in ABILITY_TREES.values() for node in tree.nodes}
CARRIED_NODE_IDS_BY_CLASS = {
    "Dragoon": frozenset(
        node.id for node in ABILITY_TREES["Dragoon"].nodes if node.tree_id == "Lancer"
    ),
    "Sorcerer": frozenset(),
    "Wizard": frozenset(),
    "Thaumaturgist": frozenset(
        {
            *CONJURER_CARRIED_NODE_IDS,
            "mage.ability.conjure-animal",
        }
    ),
}
TALENT_NODES = {
    str(node.payload["talent_key"]): node
    for node in TREE_NODES.values()
    if node.kind == NodeKind.TALENT
}
