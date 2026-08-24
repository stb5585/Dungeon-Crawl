"""Regression coverage for persistent Warlock curses and familiar growth."""

from src.core import abilities
from src.core import curses
from src.core import enemies
from src.core import items
from src.core.companions import Fairy
from tests.test_framework import TestGameState


def _player(class_name="Warlock"):
    return TestGameState.create_player(class_name=class_name, race_name="Human")


def test_curses_persist_through_combat_cleanup_and_expel_together():
    player = _player()
    abilities.CurseUmbra().cast(player, player)
    abilities.CurseFrailty().cast(player, player)

    player.effects(end=True)

    assert curses.has_curse(player, "Umbra")
    assert player.check_mod("resist", typ="Shadow") < 0
    assert abilities.ExpelCurse().cast(player, player).startswith("The curses")
    assert not curses.has_curse(player, "Umbra")
    assert not curses.has_curse(player, "Frailty")


def test_water_bladders_hold_ten_sips_and_delay_polydipsia():
    player = _player()
    player.health.current = player.health.max // 2
    curses.apply_curse(player, "Polydipsia")
    bladder = items.WaterBladder()

    message = bladder.use(player)

    assert "recovers" in message
    assert bladder.charges == 9
    assert "holds" in curses.polydipsia_tick(player)
    assert curses.ensure_curses(player)["Polydipsia"]["turns"] == 0


def test_fairy_third_growth_gains_expel_curse():
    fairy = Fairy()
    fairy.level.pro_level = 2

    message = fairy.level_up()

    assert "Expel Curse" in message
    assert "Expel Curse" in fairy.spellbook["Spells"]


def test_necromancer_uses_polydipsia_without_mana_shield():
    enemy = enemies.Necromancer()

    assert "Curse of Polydipsia" in enemy.spellbook["Spells"]
    assert "Inflate Health" not in enemy.spellbook["Spells"]
    assert "Mana Shield" not in enemy.spellbook["Skills"]
