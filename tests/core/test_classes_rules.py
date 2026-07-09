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

    familiar_guidance = classes.promotion_mechanic_guidance("Warlock")
    assert "Familiar" in familiar_guidance
    assert "familiar" in familiar_guidance
    assert classes.promotion_mechanic_tab_label("Warlock") == "Familiar"

    assert "School Affinity" in classes.promotion_mechanic_guidance("Sorcerer")
    assert classes.promotion_mechanic_tab_label("Sorcerer") == "School Affinity"
    assert "School Affinity" in classes.promotion_mechanic_guidance("Wizard")
    assert classes.promotion_mechanic_tab_label("Wizard") == "School Affinity"
    assert "Umbral Debt" in classes.promotion_mechanic_guidance("Shadowcaster")
    assert classes.promotion_mechanic_tab_label("Shadowcaster") == "Umbral Debt"
    assert "Contracts" in classes.promotion_mechanic_guidance("Demonologist")
    assert classes.promotion_mechanic_tab_label("Demonologist") == "Contracts"
    assert "Blade Charge" in classes.promotion_mechanic_guidance("Spellblade")
    assert classes.promotion_mechanic_tab_label("Spellblade") == "Blade Charge"
    assert "Arcane Tempo" in classes.promotion_mechanic_guidance("Knight Enchanter")
    assert classes.promotion_mechanic_tab_label("Knight Enchanter") == "Arcane Tempo"

    assert "Misfortune" in classes.promotion_mechanic_guidance("Thief")
    assert classes.promotion_mechanic_tab_label("Thief") == "Fortune"
    assert "Loaded Dice" in classes.promotion_mechanic_guidance("Rogue")
    assert classes.promotion_mechanic_tab_label("Rogue") == "Fortune"
    assert "Revelation" in classes.promotion_mechanic_guidance("Inquisitor")
    assert classes.promotion_mechanic_tab_label("Inquisitor") == "Case Journal"
    assert "Wayfinding" in classes.promotion_mechanic_guidance("Seeker")
    assert classes.promotion_mechanic_tab_label("Seeker") == "Case Journal"
    assert "Death Mark" in classes.promotion_mechanic_guidance("Assassin")
    assert classes.promotion_mechanic_tab_label("Assassin") == "Death Mark"
    assert "No-Trace Opener" in classes.promotion_mechanic_guidance("Ninja")
    assert classes.promotion_mechanic_tab_label("Ninja") == "Death Mark"
    assert "Stolen Charge" in classes.promotion_mechanic_guidance("Spell Stealer")
    assert classes.promotion_mechanic_tab_label("Spell Stealer") == "Stolen Charge"
    assert "Arcane Larceny" in classes.promotion_mechanic_guidance("Arcane Trickster")
    assert classes.promotion_mechanic_tab_label("Arcane Trickster") == "Stolen Charge"

    assert "Sanctuary Ward" in classes.promotion_mechanic_guidance("Cleric")
    assert classes.promotion_mechanic_tab_label("Cleric") == "Devotion"
    assert "Ordered Blessings" in classes.promotion_mechanic_guidance("Templar")
    assert classes.promotion_mechanic_tab_label("Templar") == "Devotion"
    assert "Dim Mak" in classes.promotion_mechanic_guidance("Monk")
    assert classes.promotion_mechanic_tab_label("Monk") == "Ki"
    assert "Martial Mastery" in classes.promotion_mechanic_guidance("Master Monk")
    assert classes.promotion_mechanic_tab_label("Master Monk") == "Ki"
    assert "Supplication" in classes.promotion_mechanic_guidance("Priest")
    assert classes.promotion_mechanic_tab_label("Priest") == "Prayer"
    assert "Divine Intervention" in classes.promotion_mechanic_guidance("Archbishop")
    assert classes.promotion_mechanic_tab_label("Archbishop") == "Prayer"
    assert "Crescendo" in classes.promotion_mechanic_guidance("Bard")
    assert classes.promotion_mechanic_tab_label("Bard") == "Crescendo"
    assert "Encore" in classes.promotion_mechanic_guidance("Troubadour")
    assert classes.promotion_mechanic_tab_label("Troubadour") == "Crescendo"

    companion_guidance = classes.promotion_mechanic_guidance("Beast Master")
    assert "Companion" in companion_guidance
    assert classes.promotion_mechanic_tab_label("Beast Master") == "Companion"

    assert "Oath Conviction" in classes.promotion_mechanic_guidance("Paladin")
    assert classes.promotion_mechanic_tab_label("Paladin") == "Oath Conviction"
    assert "Aerial Tempo" in classes.promotion_mechanic_guidance("Lancer")
    assert classes.promotion_mechanic_tab_label("Lancer") == "Aerial Tempo"
    assert "Resolve" in classes.promotion_mechanic_guidance("Sentinel")
    assert classes.promotion_mechanic_tab_label("Sentinel") == "Resolve"

    assert "Runes" in classes.promotion_mechanic_guidance("Diviner")
    assert classes.promotion_mechanic_tab_label("Diviner") == "Runes"
    assert "Totems" in classes.promotion_mechanic_guidance("Shaman")
    assert classes.promotion_mechanic_tab_label("Shaman") == "Totems"
    assert "Companion" in classes.promotion_mechanic_guidance("Ranger")
    assert classes.promotion_mechanic_tab_label("Ranger") == "Companion"

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
