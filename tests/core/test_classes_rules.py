"""Focused coverage for class progression and equipment rules."""

from __future__ import annotations

from types import SimpleNamespace

from src.core import abilities, classes, items


def _promotion_player(*, spells=None, skills=None):
    return SimpleNamespace(
        spellbook={
            "Spells": dict(spells or {}),
            "Skills": dict(skills or {}),
        }
    )


def test_promotion_rules_keep_clear_and_remove_spellbook_entries():
    enfeeble = abilities.Enfeeble()
    player = _promotion_player(
        spells={
            "Enfeeble": enfeeble,
            "Fireball": object(),
        },
        skills={"Shield Slam": object(), "Double Strike": object()},
    )

    message = classes.apply_promotion_ability_rules(player, "Warlock")

    assert message == "You lose all previously learned attack spells.\n"
    assert player.spellbook["Spells"] == {"Enfeeble": enfeeble}
    assert "Shield Slam" in player.spellbook["Skills"]

    message = classes.apply_promotion_ability_rules(player, "Weapon Master")

    assert message == ""
    assert "Shield Slam" not in player.spellbook["Skills"]
    assert "Double Strike" in player.spellbook["Skills"]

    player.spellbook["Spells"]["Heal"] = object()
    message = classes.apply_promotion_ability_rules(player, "Monk")

    assert message == "You lose all previously learned spells.\n"
    assert player.spellbook["Spells"] == {}


def test_promotion_rules_ignore_unknown_class_without_mutating_spellbook():
    player = _promotion_player(spells={"Spark": object()}, skills={"Feint": object()})

    message = classes.apply_promotion_ability_rules(player, "Unknown Class")

    assert message == ""
    assert set(player.spellbook["Spells"]) == {"Spark"}
    assert set(player.spellbook["Skills"]) == {"Feint"}


def test_job_equipment_defaults_and_equip_checks_cover_helmet_and_accessories():
    warrior = classes.Warrior()

    assert isinstance(warrior.equipment["Helmet"], items.NoHelmet)
    assert isinstance(warrior.equipment["Ring"], items.NoRing)
    assert isinstance(warrior.equipment["Pendant"], items.NoPendant)
    assert warrior.restrictions["Helmet"] == warrior.restrictions["Armor"]

    assert warrior.equip_check(items.IronHelm(), "Helmet") is True
    assert warrior.equip_check(items.MitreHat(), "Helmet") is False
    assert warrior.equip_check(items.IronRing(), "Ring") is True
    assert warrior.equip_check(items.VisionPendant(), "Ring") is False
    assert warrior.equip_check(items.VisionPendant(), "Pendant") is True
