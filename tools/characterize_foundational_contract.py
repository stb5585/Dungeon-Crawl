#!/usr/bin/env python3
"""Characterize the pre-foundation ability and contact-resolution contracts."""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

ABILITY_DIRECTORY = PROJECT_ROOT / "src" / "core" / "data" / "abilities"
CONTACT_STATS = (6, 10, 14, 18, 22)
PROFICIENCY_DIFFERENCES = (-2, -1, 0, 1, 2)
CHARISMA_TERMS = (-5, 0, 5)
ARMOR_GROUPS = {
    "none": "None",
    "light": "Light",
    "medium": "Medium",
    "heavy": "Heavy",
}


def ability_inventory(directory: Path = ABILITY_DIRECTORY) -> dict[str, Any]:
    """Return counts that describe the legacy YAML ability metadata."""
    paths = sorted(directory.glob("*.yaml"))
    definitions = []
    for path in paths:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(payload, dict):
            raise ValueError(f"{path} must contain a YAML mapping")
        definitions.append((path, payload))

    legacy_fields = ("type", "subtype", "school", "target_scope", "target_loss_policy")
    return {
        "ability_count": len(definitions),
        "filename_slugs_unique": len({path.stem for path, _payload in definitions})
        == len(definitions),
        "legacy_value_counts": {
            field: dict(
                sorted(
                    Counter(
                        str(payload[field]) for _path, payload in definitions if field in payload
                    ).items()
                )
            )
            for field in legacy_fields
        },
        "missing_legacy_fields": {
            field: sum(field not in payload for _path, payload in definitions)
            for field in legacy_fields
        },
    }


def _neutral_character(name: str, *, primary_stat: int) -> Any:
    """Build a character without class, race, status, or equipment bonuses."""
    from src.core.character import Character, Combat, Resource, Stats
    from src.core.items import NoArmor, NoHelmet, NoOffHand, NoPendant, NoRing, NoWeapon

    character = Character(
        name,
        Resource(100, 100),
        Resource(100, 100),
        Stats(
            strength=10,
            intel=primary_stat,
            wisdom=primary_stat,
            con=10,
            charisma=10,
            dex=primary_stat,
        ),
        Combat(),
    )
    character.equipment = {
        "Weapon": NoWeapon(),
        "Armor": NoArmor(),
        "OffHand": NoOffHand(),
        "Helmet": NoHelmet(),
        "Ring": NoRing(),
        "Pendant": NoPendant(),
    }
    return character


def contact_matrix(*, samples: int = 10_000, seed: int = 1337) -> dict[str, Any]:
    """Sample current independent hit-and-dodge rolls for neutral actors."""
    if samples <= 0:
        raise ValueError("samples must be positive")

    matrices: dict[str, list[dict[str, int | float]]] = {}
    for contact_index, contact_type in enumerate(("weapon", "spell")):
        cells: list[dict[str, int | float]] = []
        for attack_index, attack_stat in enumerate(CONTACT_STATS):
            for defense_index, defense_stat in enumerate(CONTACT_STATS):
                attacker = _neutral_character("Attacker", primary_stat=attack_stat)
                defender = _neutral_character("Defender", primary_stat=defense_stat)
                cell_seed = seed + (contact_index * 10_000) + (attack_index * 100) + defense_index
                random.seed(cell_seed)
                landed = 0
                hit_total = 0.0
                dodge_total = 0.0
                for _sample in range(samples):
                    spell = contact_type == "spell"
                    dodge = defender.dodge_chance(attacker, spell=spell)
                    dodged = dodge > random.random()
                    hit = attacker.hit_chance(defender, typ="magic" if spell else "weapon")
                    made_contact = hit > random.random()
                    hit_total += hit
                    dodge_total += dodge
                    landed += made_contact and not dodged
                cells.append(
                    {
                        "attack_stat": attack_stat,
                        "defense_stat": defense_stat,
                        "mean_hit_roll": round(hit_total / samples, 6),
                        "mean_dodge_roll": round(dodge_total / samples, 6),
                        "land_rate": round(landed / samples, 6),
                    }
                )
        matrices[contact_type] = cells

    return {
        "seed": seed,
        "samples_per_cell": samples,
        "ordinary_stats": list(CONTACT_STATS),
        "resolution": "hit > U(0,1) and not dodge > U(0,1)",
        "matrices": matrices,
    }


def approved_contact_matrix(*, samples: int = 10_000, seed: int = 1337) -> dict[str, Any]:
    """Sample legacy combined contact outcomes across approved replacement axes."""
    if samples <= 0:
        raise ValueError("samples must be positive")

    def character(name: str) -> Any:
        return _neutral_character(name, primary_stat=14)

    weapon_cells: list[dict[str, int | float | str]] = []
    for proficiency_index, proficiency_difference in enumerate(PROFICIENCY_DIFFERENCES):
        for speed_index, defender_speed in enumerate(CONTACT_STATS):
            for armor_index, (armor_group, armor_subtype) in enumerate(ARMOR_GROUPS.items()):
                attacker = character("Attacker")
                defender = character("Defender")
                attacker.level.pro_level = 3 + proficiency_difference
                defender.level.pro_level = 3
                defender.stats.dex = defender_speed
                defender.equipment["Armor"] = SimpleNamespace(subtyp=armor_subtype)
                cell_seed = seed + (proficiency_index * 10_000) + (speed_index * 100) + armor_index
                random.seed(cell_seed)
                landed = 0
                for _sample in range(samples):
                    dodge = defender.dodge_chance(attacker)
                    hit = attacker.hit_chance(defender, typ="weapon")
                    landed += hit > random.random() and not dodge > random.random()
                weapon_cells.append(
                    {
                        "proficiency_difference": proficiency_difference,
                        "defender_speed": defender_speed,
                        "armor_group": armor_group,
                        "land_rate": round(landed / samples, 6),
                    }
                )

    spell_cells: list[dict[str, int | float]] = []
    for intelligence_index, intelligence in enumerate(CONTACT_STATS):
        for wisdom_index, wisdom in enumerate(CONTACT_STATS):
            for charisma_index, charisma_term in enumerate(CHARISMA_TERMS):
                attacker = character("Attacker")
                defender = character("Defender")
                attacker.stats.intel = intelligence
                defender.stats.wisdom = wisdom
                defender.stats.charisma = 10 + charisma_term
                cell_seed = (
                    seed
                    + 100_000
                    + (intelligence_index * 10_000)
                    + (wisdom_index * 100)
                    + charisma_index
                )
                random.seed(cell_seed)
                landed = 0
                for _sample in range(samples):
                    dodge = defender.dodge_chance(attacker, spell=True)
                    hit = attacker.hit_chance(defender, typ="magic")
                    landed += hit > random.random() and not dodge > random.random()
                spell_cells.append(
                    {
                        "intelligence": intelligence,
                        "wisdom": wisdom,
                        "charisma_term": charisma_term,
                        "land_rate": round(landed / samples, 6),
                    }
                )

    return {
        "seed": seed,
        "samples_per_cell": samples,
        "reference_profile": {
            "fixed_primary_stats": 14,
            "luck_and_unrelated_stats": 10,
            "class_race_status_and_equipment_bonuses": "none",
        },
        "weapon": {
            "proficiency_differences": list(PROFICIENCY_DIFFERENCES),
            "defender_speeds": list(CONTACT_STATS),
            "armor_groups": list(ARMOR_GROUPS),
            "cells": weapon_cells,
        },
        "spell": {
            "intelligence": list(CONTACT_STATS),
            "wisdom": list(CONTACT_STATS),
            "charisma_terms": list(CHARISMA_TERMS),
            "cells": spell_cells,
        },
    }


def foundational_characterization(
    *,
    samples: int = 10_000,
    approved_samples: int = 1_000,
    seed: int = 1337,
) -> dict[str, Any]:
    """Return the complete deterministic pre-refactor characterization."""
    return {
        "source_revision": "f7a4b25e5a405ba6d9c5006b84d92584d818ebc3",
        "ability_inventory": ability_inventory(),
        "contact_characterization": contact_matrix(samples=samples, seed=seed),
        "approved_contact_characterization": approved_contact_matrix(
            samples=approved_samples,
            seed=seed,
        ),
        "retained_reports": [
            "reports/balance_baselines/multi_enemy_slice0_pre_refactor.txt",
            "reports/balance_baselines/multi_enemy_slice6_pilot.txt",
            "reports/balance_baselines/multi_enemy_pilot3_floor3.txt",
            "reports/balance_baselines/multi_enemy_pilot3_floor4.txt",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=10_000)
    parser.add_argument("--approved-samples", type=int, default=1_000)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(
        foundational_characterization(
            samples=args.samples,
            approved_samples=args.approved_samples,
            seed=args.seed,
        ),
    )
    if args.output is None:
        print(rendered)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(f"{rendered}\n", encoding="utf-8")
        print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
