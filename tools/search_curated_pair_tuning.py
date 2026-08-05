#!/usr/bin/env python3
"""Screen same-floor enemy pairs and bounded local tuning modifiers."""

from __future__ import annotations

import argparse
from itertools import combinations, product
import json
from pathlib import Path
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core import enemies, items, races
from src.core.analytics.combat_simulator import CombatSimulator
from src.core.combat import CombatEncounter
from tests.test_framework import TestGameState
from tools import run_balance_suite


BASE_CLASSES = ("Warrior", "Mage", "Footpad", "Healer", "Pathfinder")
HARD_CONTROL_ABILITIES = {
    "Charge",
    "Crushing Blow",
    "Howl",
    "Sleep",
    "Sleeping Powder",
    "Stupefy",
}


def _make_player(class_name: str, level: int):
    """Build the same deterministic player profile as the balance suite."""
    race = races.Human()
    hp_max = 100 + (race.con * 10) + (level * 8)
    mp_max = 50 + (race.intel * 8) + (level * 4)
    player = TestGameState.create_player(
        name=class_name,
        class_name=class_name,
        race_name=race.name,
        level=level,
        health=(hp_max, hp_max),
        mana=(mp_max, mp_max),
        stats={
            "strength": race.strength,
            "intel": race.intel,
            "wisdom": race.wisdom,
            "con": race.con,
            "charisma": race.charisma,
            "dex": race.dex,
        },
    )
    player.resistance = dict(race.resistance)
    player.combat.attack = int(race.base_attack)
    player.combat.defense = int(race.base_defense)
    player.combat.magic = int(race.base_magic)
    player.combat.magic_def = int(race.base_magic_def)
    run_balance_suite._apply_auto_stat_ups(player, level)
    run_balance_suite._apply_expected_combat_scaling_progression(
        player,
        class_name,
        level,
    )
    run_balance_suite._populate_spellbook_for_progression(
        player,
        class_name,
        level,
        point_build="focus",
    )
    run_balance_suite._apply_meta_progression_loadouts(player, level)
    run_balance_suite._equip_tiered_from_items_dict(player, level)
    player.modify_inventory(items.HealthPotion(), num=2)
    player.modify_inventory(items.ManaPotion(), num=2)
    return player


def _ability_names(enemy) -> set[str]:
    return {
        str(name)
        for group in getattr(enemy, "spellbook", {}).values()
        for name in group
    }


def _has_support_loop(enemy) -> bool:
    return any(
        getattr(ability, "subtyp", "") in {"Heal", "Support"}
        for group in getattr(enemy, "spellbook", {}).values()
        for ability in group.values()
        if not getattr(ability, "passive", False)
    )


def _eligible_pair(first_factory, second_factory) -> bool:
    first = first_factory()
    second = second_factory()
    if first.name == second.name:
        return False
    if any(
        bool(getattr(enemy, flag, False))
        for enemy in (first, second)
        for flag in ("boss", "is_boss")
    ):
        return False
    controls = [
        bool(_ability_names(enemy) & HARD_CONTROL_ABILITIES)
        for enemy in (first, second)
    ]
    if all(controls):
        return False
    invisible = [
        getattr(enemy, "name", "") == "Invisible Stalker"
        for enemy in (first, second)
    ]
    if all(invisible):
        return False
    if _has_support_loop(first) and _has_support_loop(second):
        return False
    return True


def _encounter_factory(
    first_factory,
    second_factory,
    health_multiplier: float,
    offense_multiplier: float,
):
    def build():
        encounter = CombatEncounter.from_enemies(
            [first_factory(), second_factory()]
        )
        for member in encounter.members:
            enemy = member.enemy
            enemy.health.max = max(
                1,
                int(enemy.health.max * health_multiplier),
            )
            enemy.health.current = enemy.health.max
            enemy._encounter_offense_multiplier = offense_multiplier
        return encounter

    return build


def _band_distance(value: float, low: float, high: float) -> float:
    if low <= value <= high:
        return 0.0
    width = high - low
    return (low - value) / width if value < low else (value - high) / width


def _rank_modifier_results(
    results: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Rank passing modifiers by proximity and no-pass grids by metric score."""
    if any(result["passes"] for result in results):
        return sorted(
            results,
            key=lambda result: (
                not result["passes"],
                abs(float(result["health_multiplier"]) - 1)
                + abs(float(result["offense_multiplier"]) - 1),
                float(result["score"]),
                abs(float(result["health_multiplier"]) - 1),
                abs(float(result["offense_multiplier"]) - 1),
            ),
        )
    return sorted(
        results,
        key=lambda result: (
            float(result["score"]),
            abs(float(result["health_multiplier"]) - 1)
            + abs(float(result["offense_multiplier"]) - 1),
            abs(float(result["health_multiplier"]) - 1),
            abs(float(result["offense_multiplier"]) - 1),
        ),
    )


def _evaluate(
    first_factory,
    second_factory,
    *,
    level: int,
    iterations: int,
    seed: int,
    classes: tuple[str, ...] = BASE_CLASSES,
    health_multiplier: float = 1.0,
    offense_multiplier: float = 1.0,
    singleton_cache: dict[tuple[object, ...], float] | None = None,
) -> dict[str, object]:
    results = []
    ratios = []
    for class_name in classes:
        make_player = lambda name=class_name: _make_player(name, level)
        pair_report = CombatSimulator().run_simulations(
            make_player,
            encounter=_encounter_factory(
                first_factory,
                second_factory,
                health_multiplier,
                offense_multiplier,
            ),
            iterations=iterations,
            seed=seed,
        )
        results.extend(pair_report.results)
        singleton_turns = []
        for factory in (first_factory, second_factory):
            cache_key = (
                class_name,
                factory,
                level,
                iterations,
                seed,
            )
            cached = (
                singleton_cache.get(cache_key)
                if singleton_cache is not None
                else None
            )
            if cached is None:
                report = CombatSimulator().run_simulations(
                    make_player,
                    factory,
                    iterations=iterations,
                    seed=seed,
                )
                cached = statistics.mean(
                    result.actor_turns for result in report.results
                )
                if singleton_cache is not None:
                    singleton_cache[cache_key] = cached
            singleton_turns.append(cached)
        pair_turns = statistics.mean(
            result.actor_turns for result in pair_report.results
        )
        ratios.append(pair_turns / max(singleton_turns))

    winners = set(classes)
    wins = [result for result in results if result.winner in winners]
    win_rate = len(wins) * 100 / max(1, len(results))
    turn_ratio = statistics.mean(ratios)
    winning_hp = (
        statistics.median(
            result.player_hp_remaining * 100 / result.player_hp_max
            for result in wins
        )
        if wins
        else 0.0
    )
    invalid_intents = sum(result.invalid_intents for result in results)
    max_turn_loops = sum(result.max_turns_reached for result in results)
    unstable = bool(invalid_intents or max_turn_loops)
    score = (
        _band_distance(win_rate, 55.0, 75.0) ** 2
        + _band_distance(turn_ratio, 1.25, 2.0) ** 2
        + _band_distance(winning_hp, 20.0, 60.0) ** 2
    )
    if unstable:
        score += 1000
    return {
        "members": [first_factory().name, second_factory().name],
        "health_multiplier": health_multiplier,
        "offense_multiplier": offense_multiplier,
        "battles": len(results),
        "win_rate": round(win_rate, 2),
        "actor_turn_ratio": round(turn_ratio, 3),
        "winning_hp_median": round(winning_hp, 2),
        "invalid_intents": invalid_intents,
        "max_turn_loops": max_turn_loops,
        "score": round(score, 6),
        "passes": not unstable and score == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--floor", type=int, required=True)
    parser.add_argument("--level", type=int, required=True)
    parser.add_argument("--iters", type=int, default=5)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument(
        "--classes",
        nargs="+",
        default=list(BASE_CLASSES),
        help="Class names used for pair and singleton benchmarks.",
    )
    parser.add_argument("--modifier-search", action="store_true")
    parser.add_argument(
        "--members",
        nargs=2,
        metavar=("FIRST", "SECOND"),
        help=(
            "Restrict screening and modifier search to one named catalog pair."
        ),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    catalog = enemies.random_enemy_candidates(str(args.floor))
    if args.members:
        factories = dict(catalog)
        unknown = [name for name in args.members if name not in factories]
        if unknown:
            parser.error(
                "unknown floor catalog member(s): "
                + ", ".join(unknown)
            )
        first = (args.members[0], factories[args.members[0]])
        second = (args.members[1], factories[args.members[1]])
        if not _eligible_pair(first[1], second[1]):
            parser.error("the requested pair is excluded by pilot rules")
        candidates = [(first, second)]
    else:
        candidates = [
            (first, second)
            for first, second in combinations(catalog, 2)
            if _eligible_pair(first[1], second[1])
        ]
    results = []
    singleton_cache: dict[tuple[object, ...], float] = {}
    for index, (first, second) in enumerate(candidates, start=1):
        print(
            f"# candidate {index}/{len(candidates)}: "
            f"{first[0]} & {second[0]}",
            file=sys.stderr,
            flush=True,
        )
        results.append(
            _evaluate(
                first[1],
                second[1],
                level=args.level,
                iterations=args.iters,
                seed=args.seed,
                classes=tuple(args.classes),
                singleton_cache=singleton_cache,
            )
        )
    results.sort(key=lambda result: float(result["score"]))

    modifier_results = []
    if args.modifier_search and results:
        best_names = results[0]["members"]
        factories = {
            name: factory
            for name, factory in catalog
        }
        values = [value / 100 for value in range(80, 121, 5)]
        for health, offense in product(values, repeat=2):
            modifier_results.append(
                _evaluate(
                    factories[best_names[0]],
                    factories[best_names[1]],
                    level=args.level,
                    iterations=args.iters,
                    seed=args.seed,
                    classes=tuple(args.classes),
                    health_multiplier=health,
                    offense_multiplier=offense,
                    singleton_cache=singleton_cache,
                )
            )
        modifier_results = _rank_modifier_results(modifier_results)

    payload = {
        "floor": args.floor,
        "level": args.level,
        "iterations_per_class": args.iters,
        "seed": args.seed,
        "classes": args.classes,
        "candidate_count": len(candidates),
        "top_candidates": results[:args.top],
        "top_modifier_results": modifier_results[:args.top],
    }
    text = json.dumps(payload, indent=2)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
