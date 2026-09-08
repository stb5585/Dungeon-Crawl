#!/usr/bin/env python3
"""Fit and verify the approved one-roll contact curves from characterization."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Callable, cast

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "reports" / "foundational" / "contact_fit_v1.json"
SEED = 1337
REGULARIZATION = 0.001
REPORT_DECIMALS = 12


DEFAULT_INPUT = PROJECT_ROOT / "reports" / "foundational" / "contact_axes_characterization_v1.json"

# These coefficients are the approved contact model used by
# ``src.core.combat.contact``. The report verifies that fixed model against the
# seeded characterization; it does not rerun a platform-dependent optimizer in
# CI and then compare raw floating-point serialization byte-for-byte.
APPROVED_COEFFICIENTS = {
    "weapon": (
        2.196017117580274,
        1.0826241866516044,
        -1.1779354313213697,
        -0.5635489834499144,
        0.35108418067201397,
        0.00627346460331834,
        -0.017602861712730133,
        0.02510273086731499,
        0.050559870108057306,
        -0.02483345821977801,
        -0.03151720006974427,
        -0.052912455191929844,
        0.08089948276048431,
        0.030750816112461176,
    ),
    "spell": (
        2.083496322599882,
        0.08929383062312002,
        -0.07708612665683551,
        -0.06706465941156274,
        0.15574292349193025,
        0.05429918945446811,
        -0.058232975985693214,
        -0.13168434804004975,
        -0.035455780259402485,
        -0.02159167222110652,
    ),
}


def _stable_report_value(value: Any) -> Any:
    """Round report floats so supported platforms serialize identical evidence."""
    if isinstance(value, float):
        return round(value, REPORT_DECIMALS)
    if isinstance(value, list):
        return [_stable_report_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _stable_report_value(item) for key, item in value.items()}
    return value


def _weapon_features(cell: dict[str, Any]) -> list[float]:
    proficiency = float(cell["proficiency_difference"]) / 2.0
    speed = (float(cell["defender_speed"]) - 14.0) / 8.0
    armor = str(cell["armor_group"])
    armor_flags = [float(armor == group) for group in ("light", "medium", "heavy")]
    return [
        1.0,
        proficiency,
        speed,
        proficiency * speed,
        speed * speed,
        *armor_flags,
        *(flag * speed for flag in armor_flags),
        *(flag * speed * speed for flag in armor_flags),
    ]


def _spell_features(cell: dict[str, Any]) -> list[float]:
    intelligence = (float(cell["intelligence"]) - 14.0) / 8.0
    wisdom = (float(cell["wisdom"]) - 14.0) / 8.0
    charisma = float(cell["charisma_term"]) / 5.0
    return [
        1.0,
        intelligence,
        wisdom,
        charisma,
        intelligence * wisdom,
        intelligence * charisma,
        wisdom * charisma,
        intelligence * intelligence,
        wisdom * wisdom,
        charisma * charisma,
    ]


FeatureFunction = Callable[[dict[str, Any]], list[float]]


def report_matrix(
    cells: list[dict[str, Any]],
    feature_function: FeatureFunction,
    coefficients: tuple[float, ...],
) -> dict[str, Any]:
    """Report the approved curve's deterministic error against characterization cells."""
    predictions = [
        1.0
        / (1.0 + math.exp(-sum(weight * value for weight, value in zip(coefficients, features))))
        for features in (feature_function(cell) for cell in cells)
    ]
    observed = [float(cell["land_rate"]) for cell in cells]
    errors = [
        abs(prediction - observed_rate) for prediction, observed_rate in zip(predictions, observed)
    ]
    return {
        "coefficients": list(coefficients),
        "weighted_mean_error": sum(errors) / len(errors),
        "maximum_ordinary_cell_error": max(errors),
        "cells": [
            {
                "inputs": {key: value for key, value in cell.items() if key != "land_rate"},
                "observed": float(cell["land_rate"]),
                "fitted": float(prediction),
                "absolute_error": float(error),
            }
            for cell, prediction, error in zip(cells, predictions, errors)
        ],
    }


def fit_characterization(path: Path) -> dict[str, Any]:
    """Fit both contact families and enforce the approved error thresholds."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    characterization = payload.get("approved_contact_characterization", payload)
    if int(characterization["seed"]) != SEED:
        raise ValueError(f"characterization seed must be {SEED}")
    fits = {
        "weapon": report_matrix(
            characterization["weapon"]["cells"],
            _weapon_features,
            APPROVED_COEFFICIENTS["weapon"],
        ),
        "spell": report_matrix(
            characterization["spell"]["cells"],
            _spell_features,
            APPROVED_COEFFICIENTS["spell"],
        ),
    }
    for kind, fit in fits.items():
        if fit["weighted_mean_error"] > 0.03:
            raise RuntimeError(f"{kind} weighted mean error exceeds 0.03")
        if fit["maximum_ordinary_cell_error"] > 0.07:
            raise RuntimeError(f"{kind} ordinary-cell error exceeds 0.07")
    report = {
        "schema_version": 1,
        "seed": SEED,
        "regularization": REGULARIZATION,
        "feature_order": {
            "weapon": [
                "1",
                "proficiency",
                "speed",
                "proficiency_speed",
                "speed2",
                "armor_light",
                "armor_medium",
                "armor_heavy",
                "light_speed",
                "medium_speed",
                "heavy_speed",
                "light_speed2",
                "medium_speed2",
                "heavy_speed2",
            ],
            "spell": [
                "1",
                "intelligence",
                "wisdom",
                "charisma",
                "intelligence_wisdom",
                "intelligence_charisma",
                "wisdom_charisma",
                "intelligence2",
                "wisdom2",
                "charisma2",
            ],
        },
        "normalization": {"stat_center": 14.0, "stat_scale": 8.0, "charisma_scale": 5.0},
        "fits": fits,
    }
    return cast(dict[str, Any], _stable_report_value(report))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the committed report without rewriting it.",
    )
    args = parser.parse_args()
    report = fit_characterization(args.input)
    rendered = f"{json.dumps(report, indent=2)}\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            raise RuntimeError("committed contact fit report is stale; regenerate it before commit")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    for kind, fit in report["fits"].items():
        print(
            f"{kind}: mean={fit['weighted_mean_error']:.4%}; "
            f"max={fit['maximum_ordinary_cell_error']:.4%}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
