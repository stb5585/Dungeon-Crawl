#!/usr/bin/env python3
"""Tests for the Devil's Cambion Acolyte companion support logic."""


def _make_player():
    from tests.test_framework import TestGameState
    return TestGameState.create_player(
        name="Hero",
        class_name="Warrior",
        race_name="Human",
        level=50,
        health=(999, 999),
        mana=(999, 999),
    )


def test_devil_familiar_turn_invokes_acolyte_support():
    from src.core.enemies import Devil

    devil = Devil()
    player = _make_player()

    # Ensure Shell is not already active.
    devil.stat_effects["Magic Defense"].active = False
    devil.stat_effects["Magic Defense"].duration = 0

    msg = devil.familiar_turn(player)
    assert msg
    assert "Cambion Acolyte" in msg
    assert devil.stat_effects["Magic Defense"].active is True


def test_acolyte_prefers_regen_when_shell_already_active_and_boss_low():
    from src.core.enemies import Devil

    devil = Devil()
    player = _make_player()

    # Pretend Shell already active.
    devil.stat_effects["Magic Defense"].active = True
    devil.stat_effects["Magic Defense"].duration = 5

    # Low HP to trigger Regen.
    devil.health.current = int(devil.health.max * 0.5)
    devil.magic_effects["Regen"].active = False
    devil.magic_effects["Regen"].duration = 0

    msg = devil.familiar_turn(player)
    assert msg
    assert "casts Regen" in msg
    assert devil.magic_effects["Regen"].active is True


def test_acolyte_no_crash_when_no_mana():
    from src.core.enemies import Devil

    devil = Devil()
    player = _make_player()

    devil.acolyte.mana.current = 0

    msg = devil.familiar_turn(player)
    assert msg == ""

