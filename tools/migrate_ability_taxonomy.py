#!/usr/bin/env python3
"""Add approved canonical metadata to every legacy YAML ability definition."""

from __future__ import annotations

import argparse
import ast
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

ABILITY_DIRECTORY = PROJECT_ROOT / "src" / "core" / "data" / "abilities"
ABILITY_SOURCE_DIRECTORY = PROJECT_ROOT / "src" / "core" / "abilities"
ALLOWLIST_PATH = ABILITY_DIRECTORY / "legacy_taxonomy_allowlist.txt"

SPECIALIZED_ALIASES = {
    "ball_lightning": ("BallLightning",),
    "calming_breeze": ("CalmingBreeze",),
    "nature_shield": ("NatureShield",),
    "primal_ascendance": ("PrimalAscendance",),
    "stone_skin": ("StoneSkin",),
    "windswept": ("Windswept",),
}
EXTRA_ALIASES = {"ultima": ("Ultima",)}

DIVINE_ABILITIES = frozenset(
    {
        "bless",
        "boost",
        "cleanse",
        "divine_aegis",
        "divine_judgment",
        "divine_protection",
        "great_gospel",
        "heal",
        "heal_2",
        "heal_3",
        "holy",
        "holy_2",
        "holy_3",
        "holy_retribution",
        "reflect",
        "regen",
        "regen_2",
        "regen_3",
        "resist_all",
        "resurrection",
        "sacred_overchannel",
        "shell",
        "smite",
        "smite_2",
        "smite_3",
        "turn_undead",
        "turn_undead_2",
    }
)
NATURAL_ABILITIES = frozenset(
    {
        "aqualung",
        "ball_lightning",
        "bolt",
        "calming_breeze",
        "earthquake",
        "gust",
        "hurricane",
        "hydration",
        "molten_rock",
        "mudslide",
        "nature_shield",
        "poison_breath",
        "poison_dart",
        "primal_ascendance",
        "regrowth",
        "scorch",
        "shapeshift",
        "stone_skin",
        "totem",
        "transform",
        "transform2",
        "transform3",
        "transform4",
        "tremor",
        "tornado",
        "tsunami",
        "volcano",
        "water_jet",
        "wind_speed",
        "windswept",
    }
)
SPIRITUAL_ABILITIES = frozenset({"chi_heal", "desoul", "dim_mak", "doom", "petrify", "soul_drain"})
EXTRAPLANAR_ABILITIES = frozenset(
    {
        "abyssal_covenant",
        "astral_judgment",
        "astral_shift",
        "corruption",
        "hellfire",
        "oblivion",
        "shadow_bolt",
        "shadow_bolt_2",
        "shadow_bolt_3",
        "shadow_strike",
        "terrify",
    }
)
ALCHEMICAL_ABILITIES = frozenset(
    {"consume_item", "poison_strike", "sleeping_powder", "smoke_screen"}
)
ARCANE_ABILITIES = frozenset(
    {
        "arcane_blast",
        "blizzard",
        "cataclysm",
        "electrocution",
        "fireball",
        "firebolt",
        "firestorm",
        "haste",
        "ice_block",
        "ice_lance",
        "icicle",
        "kinetic_explosion",
        "lightning",
        "maelstrom",
        "magic_missile",
        "magic_missile_2",
        "magic_missile_3",
        "mana_drain",
        "mana_shield",
        "mana_shield_2",
        "mana_slice",
        "mana_slice_2",
        "mana_tap",
        "meteor",
        "mirror_image",
        "mirror_image_2",
        "shock",
        "ultima",
        "vulcanize",
    }
)

REACTION_ABILITIES = frozenset({"counterspell", "resurrection"})
INFORMATION_ABILITIES = frozenset({"inspect", "reveal"})
SUMMONING_ABILITIES = frozenset({"totem"})
MOBILITY_ABILITIES = frozenset(
    {"haste", "jump", "sanctuary", "surface", "teleport", "tunnel", "wind_speed"}
)
RESTORATION_ABILITIES = frozenset(
    {
        "chi_heal",
        "cleanse",
        "great_gospel",
        "heal",
        "heal_2",
        "heal_3",
        "hydration",
        "regen",
        "regen_2",
        "regen_3",
        "regrowth",
        "resurrection",
    }
)
UTILITY_ABILITIES = frozenset(
    {
        "blackjack",
        "consume_item",
        "gold_toss",
        "shapeshift",
        "slot_machine",
        "steal",
        "transform",
        "transform2",
        "transform3",
        "transform4",
    }
)
PROTECTION_ABILITIES = frozenset(
    {
        "astral_shift",
        "battle_cry",
        "bless",
        "boost",
        "calming_breeze",
        "counterspell",
        "divine_aegis",
        "divine_protection",
        "haste",
        "ice_block",
        "imbue_weapon",
        "mana_shield",
        "mana_shield_2",
        "mirror_image",
        "mirror_image_2",
        "nature_shield",
        "primal_ascendance",
        "purity_body",
        "purity_body2",
        "reflect",
        "resist_all",
        "shell",
        "smoke_screen",
        "stone_skin",
        "vulcanize",
    }
)
CONTROL_ABILITIES = frozenset(
    {
        "blinding_fog",
        "berserk",
        "choose_fate",
        "destroy_metal",
        "dispel",
        "enfeeble",
        "hex",
        "howl",
        "ruin",
        "silence",
        "sleep",
        "stupefy",
        "vesperion_choose_fate",
        "weaken_mind",
        "windswept",
    }
)
DAMAGE_ABILITIES = frozenset({"arcane_blast", "astral_judgment", "gold_toss", "imbue_weapon"})
FIELD_ABILITIES = frozenset({"blinding_fog", "firestorm"})
TRANSFORMATION_ABILITIES = frozenset(
    {"shapeshift", "transform", "transform2", "transform3", "transform4"}
)
COMMAND_ABILITIES = frozenset({"choose_fate", "inspect", "steal", "vesperion_choose_fate"})
LOCKED_ABILITIES = frozenset(
    {
        "arcane_blast",
        "charge",
        "crushing_blow",
        "dragon_breath_fire",
        "dragon_breath_water",
        "dragon_breath_wind",
        "jump",
        "shadow_strike",
    }
)
SELF_TARGET_ABILITIES = frozenset({"smoke_screen"})


def _wrapper_aliases() -> tuple[dict[str, tuple[str, ...]], dict[str, str]]:
    aliases: dict[str, list[str]] = {}
    sources: dict[str, str] = {}
    for source_path in sorted(ABILITY_SOURCE_DIRECTORY.glob("*.py")):
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "_load_yaml_ability"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                continue
            ability_id = Path(node.args[0].value).stem
            alias: str | None = None
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                alias = str(node.args[1].value)
            for keyword in node.keywords:
                if keyword.arg == "cls_name" and isinstance(keyword.value, ast.Constant):
                    alias = str(keyword.value.value)
            if alias:
                aliases.setdefault(ability_id, []).append(alias)
            sources[ability_id] = source_path.name
    for ability_id, values in SPECIALIZED_ALIASES.items():
        aliases.setdefault(ability_id, []).extend(values)
        sources.setdefault(ability_id, "specialized")
    for ability_id, values in EXTRA_ALIASES.items():
        aliases.setdefault(ability_id, []).extend(values)
    return (
        {key: tuple(dict.fromkeys(values)) for key, values in aliases.items()},
        sources,
    )


def _origin(ability_id: str, source: str) -> str:
    if ability_id in DIVINE_ABILITIES:
        return "divine"
    if ability_id in NATURAL_ABILITIES:
        return "natural"
    if ability_id in SPIRITUAL_ABILITIES:
        return "spiritual"
    if ability_id in EXTRAPLANAR_ABILITIES:
        return "extraplanar"
    if ability_id in ALCHEMICAL_ABILITIES:
        return "alchemical"
    if ability_id in ARCANE_ABILITIES:
        return "arcane"
    if source == "enemy.py":
        return "innate"
    return "martial"


def _activation(ability_id: str, payload: dict[str, Any]) -> str:
    if ability_id in REACTION_ABILITIES:
        return "reaction"
    if payload.get("passive", False):
        return "passive"
    return "active"


def _intent(ability_id: str, payload: dict[str, Any]) -> str:
    if ability_id in DAMAGE_ABILITIES:
        return "damage"
    if ability_id in INFORMATION_ABILITIES:
        return "information"
    if ability_id in SUMMONING_ABILITIES:
        return "summoning"
    if ability_id in MOBILITY_ABILITIES:
        return "mobility"
    if ability_id in RESTORATION_ABILITIES:
        return "restoration"
    if ability_id in UTILITY_ABILITIES:
        return "utility"
    if ability_id in PROTECTION_ABILITIES:
        return "protection"
    if ability_id in CONTROL_ABILITIES or payload.get("type") in {"Status", "StatusSkill"}:
        return "control"
    if payload.get("type") == "Support":
        return "protection"
    if str(payload.get("subtype", "")).replace(" ", "").lower() == "powerup":
        return "protection"
    return "damage"


def _method(ability_id: str, payload: dict[str, Any]) -> str:
    ability_type = str(payload.get("type", "Skill"))
    if ability_id == "consume_item":
        return "consumption"
    if ability_id in TRANSFORMATION_ABILITIES:
        return "transformation"
    if ability_id in MOBILITY_ABILITIES:
        return "movement"
    if ability_id in COMMAND_ABILITIES:
        return "command"
    if ability_id in FIELD_ABILITIES or ability_id == "totem":
        return "manifestation"
    if ability_type in {"Status", "StatusSkill"}:
        return "binding"
    if ability_type in {"Heal", "Support"}:
        return "channeling"
    if ability_type in {"Spell", "MagicMissile", "CustomSpell"}:
        return "projection"
    if ability_type == "ChargingSkill" and ability_id.startswith("dragon_breath"):
        return "projection"
    if payload.get("weapon", False) or ability_type in {"WeaponSpell", "JumpSkill"}:
        return "strike"
    return "command"


def _scope(ability_id: str, payload: dict[str, Any], activation: str) -> str:
    if activation in {"passive", "reaction"} or not payload.get("combat", True):
        return "none"
    if payload.get("target_scope") == "all_enemies":
        return "all_opponents"
    if (
        payload.get("self_target", False)
        or payload.get("target_self", False)
        or ability_id in SELF_TARGET_ABILITIES
        or payload.get("type") in {"Heal", "Support", "Movement"}
        or ability_id in SPECIALIZED_ALIASES
        and ability_id != "ball_lightning"
        and ability_id != "windswept"
    ):
        return "self"
    return "single_opponent"


def _traits(ability_id: str, payload: dict[str, Any], scope: str) -> list[str]:
    traits = []
    ability_type = str(payload.get("type", "Skill"))
    if payload.get("weapon", False) or ability_type in {"WeaponSpell", "JumpSkill"}:
        traits.append("combat.weapon")
    if ability_type == "ChargingSkill" or payload.get("charge_time") is not None:
        traits.append("combat.charged")
    if payload.get("delay") is not None:
        traits.append("combat.delayed")
    if payload.get("guaranteed_hit", False):
        traits.append("combat.always_hit")
    if int(payload.get("strikes", payload.get("missiles", 1)) or 1) > 1:
        traits.append("combat.multi_strike")
    if str(payload.get("subtype", "")) == "Drain":
        traits.append("combat.resource_drain")
    if ability_type in {"Status", "StatusSkill"}:
        traits.append("combat.status_contest")
    if scope == "all_opponents":
        traits.append("targeting.area")
    if payload.get("grounded_damage", False):
        traits.append("targeting.grounded")
    if str(payload.get("subtype", "")) == "Stealth":
        traits.append("visibility.stealth")
    if ability_id in SPECIALIZED_ALIASES or ability_type in {"CustomSpell", "JumpSkill"}:
        traits.append("internal.specialized_execution")
    return sorted(set(traits))


def canonical_metadata(
    ability_id: str,
    payload: dict[str, Any],
    *,
    aliases: tuple[str, ...],
    source: str,
) -> dict[str, Any]:
    """Return approved metadata for one legacy definition."""
    activation = _activation(ability_id, payload)
    intent = _intent(ability_id, payload)
    scope = _scope(ability_id, payload, activation)
    loss_policy = (
        "snapshot_roster"
        if scope == "all_opponents"
        else (
            "locked"
            if scope in {"none", "self"} or ability_id in LOCKED_ABILITIES
            else "retarget_focus"
        )
    )
    return {
        "id": ability_id,
        "aliases": list(dict.fromkeys((*aliases, str(payload.get("name", ability_id))))),
        "taxonomy": {
            "origin": _origin(ability_id, source),
            "method": _method(ability_id, payload),
            "primary_intent": intent,
            "activation": activation,
            "form": (
                "field"
                if ability_id in FIELD_ABILITIES
                else "summon" if ability_id in SUMMONING_ABILITIES else "direct"
            ),
            "traits": _traits(ability_id, payload, scope),
        },
        "targeting": {
            "scope": scope,
            "loss_policy": loss_policy,
            "hostile": scope in {"single_opponent", "all_opponents"} and intent != "information",
        },
    }


def migrate(*, write: bool = False) -> Counter[str]:
    """Validate sources and optionally prepend canonical metadata to all YAML files."""
    aliases_by_id, sources_by_id = _wrapper_aliases()
    yaml_paths = sorted(ABILITY_DIRECTORY.glob("*.yaml"))
    yaml_ids = {path.stem for path in yaml_paths}
    if set(aliases_by_id) != yaml_ids:
        missing = sorted(yaml_ids - set(aliases_by_id))
        extra = sorted(set(aliases_by_id) - yaml_ids)
        raise ValueError(f"wrapper alias inventory differs: missing={missing}, extra={extra}")

    counts: Counter[str] = Counter()
    for path in yaml_paths:
        original = path.read_text(encoding="utf-8")
        payload = yaml.safe_load(original)
        if not isinstance(payload, dict):
            raise ValueError(f"{path} must contain a mapping")
        if any(key in payload for key in ("id", "aliases", "taxonomy", "targeting")):
            raise ValueError(f"{path} already contains canonical metadata")
        metadata = canonical_metadata(
            path.stem,
            payload,
            aliases=aliases_by_id[path.stem],
            source=sources_by_id[path.stem],
        )
        counts[f"origin.{metadata['taxonomy']['origin']}"] += 1
        counts[f"intent.{metadata['taxonomy']['primary_intent']}"] += 1
        counts[f"activation.{metadata['taxonomy']['activation']}"] += 1
        if write:
            header = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True)
            path.write_text(f"{header}{original}", encoding="utf-8")

    if write:
        ALLOWLIST_PATH.write_text(
            "# Canonical taxonomy migration complete; no legacy IDs remain.\n",
            encoding="utf-8",
        )
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    counts = migrate(write=args.write)
    action = "Migrated" if args.write else "Would migrate"
    print(
        f"{action} {sum(value for key, value in counts.items() if key.startswith('origin.'))} abilities"
    )
    for key, value in sorted(counts.items()):
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
