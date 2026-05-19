#!/usr/bin/env python3
"""Focused race-balance regression checks."""

from __future__ import annotations

from src.core import races


def test_half_giant_keeps_strength_identity_but_has_sharper_drawbacks():
    half_giant = races.HalfGiant()
    human = races.Human()

    assert half_giant.strength > human.strength
    assert half_giant.con > human.con
    assert half_giant.base_attack > human.base_attack

    assert half_giant.dex < human.dex
    assert half_giant.base_magic_def < human.base_magic_def
    assert half_giant.resistance["Holy"] <= -0.4
    assert half_giant.resistance["Shadow"] < human.resistance["Shadow"]
    assert all(
        half_giant.resistance[element] < human.resistance[element]
        for element in ("Fire", "Ice", "Electric", "Water", "Earth", "Wind")
    )


def test_half_giant_keeps_limited_physical_and_poison_resistances():
    half_giant = races.HalfGiant()

    assert 0 < half_giant.resistance["Physical"] <= 0.15
    assert 0 < half_giant.resistance["Poison"] <= 0.2
