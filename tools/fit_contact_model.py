#!/usr/bin/env python3
"""Fit and verify the approved one-roll contact curves from characterization."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable, cast

import numpy as np
from scipy.optimize import minimize

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "reports" / "foundational" / "contact_fit_v1.json"
SEED = 1337
REGULARIZATION = 0.001


DEFAULT_INPUT = PROJECT_ROOT / "reports" / "foundational" / "contact_axes_characterization_v1.json"


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


def fit_matrix(cells: list[dict[str, Any]], feature_function: FeatureFunction) -> dict[str, Any]:
    """Fit one deterministic regularized logistic curve and report its errors."""
    matrix = np.asarray([feature_function(cell) for cell in cells])
    observed = np.asarray([float(cell["land_rate"]) for cell in cells])

    def objective(coefficients: np.ndarray[Any, Any]) -> float:
        logits = matrix @ coefficients
        cross_entropy: float = float(np.sum(np.logaddexp(0.0, logits) - (observed * logits)))
        return float(cross_entropy + REGULARIZATION * np.sum(coefficients[1:] ** 2))

    def gradient(coefficients: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
        logits = matrix @ coefficients
        predicted = 1.0 / (1.0 + np.exp(-logits))
        result = matrix.T @ (predicted - observed)
        result[1:] += 2.0 * REGULARIZATION * coefficients[1:]
        return cast(np.ndarray[Any, Any], result)

    fitted = minimize(
        objective,
        np.zeros(matrix.shape[1]),
        jac=gradient,
        method="L-BFGS-B",
        options={"ftol": 1e-15, "gtol": 1e-12, "maxiter": 10_000, "maxls": 100},
    )
    if not fitted.success:
        raise RuntimeError(f"contact fit failed: {fitted.message}")
    predictions = 1.0 / (1.0 + np.exp(-(matrix @ fitted.x)))
    errors = np.abs(predictions - observed)
    return {
        "coefficients": [float(value) for value in fitted.x],
        "weighted_mean_error": float(np.mean(errors)),
        "maximum_ordinary_cell_error": float(np.max(errors)),
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
        "weapon": fit_matrix(characterization["weapon"]["cells"], _weapon_features),
        "spell": fit_matrix(characterization["spell"]["cells"], _spell_features),
    }
    for kind, fit in fits.items():
        if fit["weighted_mean_error"] > 0.03:
            raise RuntimeError(f"{kind} weighted mean error exceeds 0.03")
        if fit["maximum_ordinary_cell_error"] > 0.07:
            raise RuntimeError(f"{kind} ordinary-cell error exceeds 0.07")
    return {
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
