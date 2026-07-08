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


def test_promotion_mechanic_guidance_points_to_relevant_character_tab():
    weapon_guidance = classes.promotion_mechanic_guidance("Weapon Master")
    assert "Weapon Discipline" in weapon_guidance
    assert "Intelligence" in weapon_guidance
    assert classes.promotion_mechanic_tab_label("Weapon Master") == "Weapon Discipline"

    summoner_guidance = classes.promotion_mechanic_guidance("Summoner")
    assert "Summons" in summoner_guidance
    assert "bond growth" in summoner_guidance
    assert classes.promotion_mechanic_tab_label("Summoner") == "Summons"

    companion_guidance = classes.promotion_mechanic_guidance("Warlock")
    assert "Companion" in companion_guidance
    assert "familiar" in companion_guidance
    assert classes.promotion_mechanic_tab_label("Warlock") == "Companion"

    assert classes.promotion_mechanic_guidance("Knight") == ""
    assert classes.promotion_mechanic_tab_label("Knight") == ""


def test_weapon_discipline_classes_include_intelligence_promotion_bonus():
    weapon_master = classes.WeaponMaster()
    grandmaster = classes.GrandmasterOfArms()

    assert weapon_master.str_plus == 2
    assert weapon_master.int_plus == 1
    assert weapon_master.dex_plus == 2

    assert grandmaster.str_plus == 2
    assert grandmaster.int_plus == 1
    assert grandmaster.dex_plus == 2


def test_grant_summoner_initial_summon_initializes_patagon(monkeypatch):
    initialized = []

    class FakePatagon:
        name = "Patagon"

        def initialize_stats(self, player):
            initialized.append(player)

    monkeypatch.setattr("src.core.companions.Patagon", FakePatagon)
    player = SimpleNamespace(summons={})

    message = classes.grant_summoner_initial_summon(player)
    repeat_message = classes.grant_summoner_initial_summon(player)

    assert message == "You have gained the summon Patagon.\n"
    assert repeat_message == ""
    assert "Patagon" in player.summons
    assert initialized == [player]


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
