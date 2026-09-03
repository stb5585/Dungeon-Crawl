"""Focused coverage for class progression and equipment rules."""

from __future__ import annotations

from types import SimpleNamespace

from src.core import abilities, classes, companions, items, races


def test_priest_learns_supplication_at_promotion_level():
    granted_skills = abilities.ability_classes_for_level(abilities.skill_dict, "Priest", 1)

    assert granted_skills == [abilities.Supplication]
    assert abilities.ability_classes_for_level(abilities.skill_dict, "Priest", 6) == []


def test_promotion_mechanic_guidance_points_to_relevant_character_surface():
    weapon_guidance = classes.promotion_mechanic_guidance("Weapon Master")
    assert "Weapon Discipline" in weapon_guidance
    assert "Intelligence" in weapon_guidance
    assert classes.promotion_mechanic_tab_label("Weapon Master") == "Weapon Discipline"

    thaumaturgist_guidance = classes.promotion_mechanic_guidance("Thaumaturgist")
    assert "Xenids" in thaumaturgist_guidance
    assert "conduit growth" in thaumaturgist_guidance
    assert classes.promotion_mechanic_tab_label("Thaumaturgist") == "Xenids"

    familiar_guidance = classes.promotion_mechanic_guidance("Warlock")
    assert "Familiar" in familiar_guidance
    assert "familiar" in familiar_guidance
    assert classes.promotion_mechanic_tab_label("Warlock") == "Familiar"

    assert "School Affinity" in classes.promotion_mechanic_guidance("Sorcerer")
    assert classes.promotion_mechanic_tab_label("Sorcerer") == "School Affinity"
    assert "School Affinity" in classes.promotion_mechanic_guidance("Wizard")
    assert classes.promotion_mechanic_tab_label("Wizard") == "School Affinity"
    assert "Umbral Debt" in classes.promotion_mechanic_guidance("Shadowcaster")
    assert classes.promotion_mechanic_tab_label("Shadowcaster") == ""
    assert "Contracts" in classes.promotion_mechanic_guidance("Demonologist")
    assert classes.promotion_mechanic_tab_label("Demonologist") == "Contracts"
    assert "Blade Charge" in classes.promotion_mechanic_guidance("Spellblade")
    assert classes.promotion_mechanic_tab_label("Spellblade") == ""
    assert "Foundation" in classes.promotion_mechanic_guidance("Knight Enchanter")
    assert "Accent" in classes.promotion_mechanic_guidance("Knight Enchanter")
    assert classes.promotion_mechanic_tab_label("Knight Enchanter") == ""

    assert "Misfortune" in classes.promotion_mechanic_guidance("Thief")
    assert classes.promotion_mechanic_tab_label("Thief") == ""
    assert "Loaded Dice" in classes.promotion_mechanic_guidance("Rogue")
    assert classes.promotion_mechanic_tab_label("Rogue") == ""
    assert "Revelation" in classes.promotion_mechanic_guidance("Inquisitor")
    assert classes.promotion_mechanic_tab_label("Inquisitor") == "Case Journal"
    assert "Wayfinding" in classes.promotion_mechanic_guidance("Seeker")
    assert classes.promotion_mechanic_tab_label("Seeker") == "Case Journal"
    assert "Death Mark" in classes.promotion_mechanic_guidance("Assassin")
    assert classes.promotion_mechanic_tab_label("Assassin") == ""
    assert "No-Trace Opener" in classes.promotion_mechanic_guidance("Ninja")
    assert classes.promotion_mechanic_tab_label("Ninja") == ""
    assert "combat Spells menu" in classes.promotion_mechanic_guidance("Spell Stealer")
    assert classes.promotion_mechanic_tab_label("Spell Stealer") == ""
    assert "Arcane Larceny" in classes.promotion_mechanic_guidance("Arcane Trickster")
    assert classes.promotion_mechanic_tab_label("Arcane Trickster") == ""

    assert "Sanctuary Ward" in classes.promotion_mechanic_guidance("Cleric")
    assert "Character Menu tab" not in classes.promotion_mechanic_guidance("Cleric")
    assert classes.promotion_mechanic_tab_label("Cleric") == ""
    assert "Ordered Blessings" in classes.promotion_mechanic_guidance("Templar")
    assert classes.promotion_mechanic_tab_label("Templar") == ""
    assert "Consecrated Conduit" in classes.promotion_mechanic_guidance("Hierophant")
    assert classes.promotion_mechanic_tab_label("Hierophant") == ""
    assert "Dim Mak" in classes.promotion_mechanic_guidance("Monk")
    assert classes.promotion_mechanic_tab_label("Monk") == ""
    assert "Martial Mastery" in classes.promotion_mechanic_guidance("Master Monk")
    assert classes.promotion_mechanic_tab_label("Master Monk") == ""
    assert "Supplication" in classes.promotion_mechanic_guidance("Priest")
    assert classes.promotion_mechanic_tab_label("Priest") == ""
    assert "Divine Intervention" in classes.promotion_mechanic_guidance("Archbishop")
    assert classes.promotion_mechanic_tab_label("Archbishop") == ""
    assert "Crescendo" in classes.promotion_mechanic_guidance("Bard")
    assert classes.promotion_mechanic_tab_label("Bard") == "Crescendo"
    assert "Encore" in classes.promotion_mechanic_guidance("Troubadour")
    assert classes.promotion_mechanic_tab_label("Troubadour") == "Crescendo"

    companion_guidance = classes.promotion_mechanic_guidance("Beast Master")
    assert "Companion" in companion_guidance
    assert classes.promotion_mechanic_tab_label("Beast Master") == "Companion & Hunt"

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
    assert classes.promotion_mechanic_tab_label("Ranger") == "Companion & Hunt"
    ranger_details = classes.promotion_mechanic_details("Ranger")
    assert ranger_details.startswith("Use it to review")
    assert "Companion & Hunt" not in ranger_details

    assert classes.promotion_mechanic_guidance("Knight") == ""
    assert classes.promotion_mechanic_details("Knight") == ""
    assert classes.promotion_mechanic_tab_label("Knight") == ""


def test_cleric_promotes_to_templar_and_hierophant():
    cleric_promotions = classes.classes_dict["Healer"]["pro"]["Cleric"]["pro"]

    assert set(cleric_promotions) == {"Templar", "Hierophant"}
    assert cleric_promotions["Hierophant"]["class"] is classes.Hierophant


def test_hierophant_available_to_all_templar_races():
    for race_cls in (races.Human, races.HalfElf, races.Gnome, races.Dwarf):
        second_promotions = race_cls().cls_res["Second"]
        assert "Templar" in second_promotions
        assert "Hierophant" in second_promotions


def test_hierophant_restrictions_and_stats_match_staff_caster_path():
    hierophant = classes.Hierophant()

    assert hierophant.pro_level == 3
    assert hierophant.restrictions["Weapon"] == ["Club", "Staff"]
    assert hierophant.restrictions["OffHand"] == ["Shield"]
    assert hierophant.restrictions["Armor"] == ["Cloth", "Light"]
    assert hierophant.restrictions["Helmet"] == ["Cloth", "Light"]
    assert hierophant.wis_plus == 3
    assert hierophant.magic_plus == 3
    assert hierophant.equip_check(items.Quarterstaff(), "Weapon") is True
    assert hierophant.equip_check(items.Sledgehammer(), "Weapon") is False
    assert hierophant.equip_check(items.LeatherArmor(), "Armor") is True
    assert hierophant.equip_check(items.ChainMail(), "Armor") is False


def test_weapon_discipline_classes_include_intelligence_promotion_bonus():
    weapon_master = classes.WeaponMaster()
    grandmaster = classes.GrandmasterOfArms()

    assert weapon_master.str_plus == 2
    assert weapon_master.int_plus == 1
    assert weapon_master.dex_plus == 2

    assert grandmaster.str_plus == 2
    assert grandmaster.int_plus == 1
    assert grandmaster.dex_plus == 2


def test_choose_xenid_initializes_patagon_and_closes_its_pair(monkeypatch):
    initialized = []

    class FakePatagon:
        name = "Patagon"

        def initialize_stats(self, player):
            initialized.append(player)

    monkeypatch.setattr("src.core.companions.Patagon", FakePatagon)
    player = SimpleNamespace(summons={})

    success, message = companions.choose_xenid(player, "Humanoid", "Patagon")
    repeat_success, repeat_message = companions.choose_xenid(
        player,
        "Humanoid",
        "Kobalos",
    )

    assert success
    assert "permanently bound" in message
    assert not repeat_success
    assert "already bound" in repeat_message
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
