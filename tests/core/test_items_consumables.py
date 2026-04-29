#!/usr/bin/env python3
"""Focused coverage for consumables, scrolls, and accessory rule helpers."""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))

from src.core import items
from src.core.combat.combat_result import CombatResult
from tests.test_framework import TestGameState


class TestItemConsumables:
    def test_health_potion_full_health_returns_early(self):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human", health=(100, 100))

        result = items.HealthPotion().use(player)

        assert result == "You are already at full health.\n"

    def test_health_potion_out_of_combat_heals_and_caps(self, monkeypatch):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human", health=(100, 40))
        calls = []
        player.modify_inventory = lambda item, subtract=False, **_kwargs: calls.append((item.name, subtract))
        monkeypatch.setattr("src.core.items.random.uniform", lambda _a, _b: 1.0)

        result = items.HealthPotion().use(player)

        assert calls == [("Health Potion", True)]
        assert player.health.current == 65
        assert "healed you for 25 life" in result

        player.health.current = 90
        result = items.HealthPotion().use(player)
        assert player.health.current == 100
        assert "You are at max health." in result

    def test_health_potion_dwarf_combat_use_applies_hangover(self, monkeypatch):
        player = TestGameState.create_player(class_name="Warrior", race_name="Dwarf", health=(100, 20))
        player.state = "fight"
        player.check_mod = lambda mod, luck_factor=None: 1 if mod == "luck" else 0
        player.modify_inventory = lambda *_args, **_kwargs: None
        monkeypatch.setattr("src.core.items.random.randint", lambda low, high: high)

        result = items.HealthPotion().use(player)

        assert player.health.current > 20
        assert player.status_effects["Hangover"].active is True
        assert player.status_effects["Hangover"].duration > 0
        assert "healed you" in result

    def test_mana_potion_full_mana_and_dwarf_out_of_combat_steps(self, monkeypatch):
        full_mana = TestGameState.create_player(class_name="Warrior", race_name="Human", mana=(50, 50))
        assert items.ManaPotion().use(full_mana) == "You are already at full mana.\n"

        dwarf = TestGameState.create_player(class_name="Warrior", race_name="Dwarf", mana=(80, 10))
        dwarf.state = "normal"
        dwarf.dwarf_hangover_steps = 0
        dwarf.modify_inventory = lambda *_args, **_kwargs: None
        monkeypatch.setattr("src.core.items.random.uniform", lambda _a, _b: 1.0)

        result = items.ManaPotion().use(dwarf)

        assert dwarf.mana.current == 32
        assert dwarf.dwarf_hangover_steps > 0
        assert "restored 22 mana points" in result

    def test_elixir_restores_health_and_mana_and_clamps(self, monkeypatch):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human", health=(100, 80), mana=(60, 50))
        player.state = "normal"
        player.modify_inventory = lambda *_args, **_kwargs: None

        result = items.Elixir().use(player)

        assert player.health.current == 100
        assert player.mana.current == 60
        assert "restored 50 health points and 30 mana points" in result
        assert "You are at max health." in result
        assert "You are at full mana." in result

        full = TestGameState.create_player(class_name="Warrior", race_name="Human", health=(100, 100), mana=(60, 60))
        assert items.Elixir().use(full) == "You are already at full health and mana.\n"

    @pytest.mark.parametrize(
        ("factory", "attr", "delta"),
        [
            (items.HPPotion, ("health", "max"), 10),
            (items.MPPotion, ("mana", "max"), 10),
            (items.StrengthPotion, ("stats", "strength"), 1),
            (items.IntelPotion, ("stats", "intel"), 1),
            (items.WisdomPotion, ("stats", "wisdom"), 1),
            (items.ConPotion, ("stats", "con"), 1),
            (items.CharismaPotion, ("stats", "charisma"), 1),
            (items.DexterityPotion, ("stats", "dex"), 1),
        ],
    )
    def test_stat_potions_increase_expected_stat(self, factory, attr, delta):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        player.modify_inventory = lambda *_args, **_kwargs: None
        player.in_town = lambda: True
        root = getattr(player, attr[0])
        before = getattr(root, attr[1])

        result = factory().use(player)

        assert getattr(root, attr[1]) == before + delta
        assert player.name in result

    def test_aard_of_being_increases_all_stats(self):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        player.modify_inventory = lambda *_args, **_kwargs: None
        before = (
            player.stats.strength,
            player.stats.intel,
            player.stats.wisdom,
            player.stats.con,
            player.stats.charisma,
            player.stats.dex,
        )

        result = items.AardBeing().use(player)

        after = (
            player.stats.strength,
            player.stats.intel,
            player.stats.wisdom,
            player.stats.con,
            player.stats.charisma,
            player.stats.dex,
        )
        assert after == tuple(value + 1 for value in before)
        assert "stats have been increased by 1" in result

    def test_status_items_cover_normal_dwarf_bandage_and_remedy_paths(self, monkeypatch):
        human = TestGameState.create_player(class_name="Warrior", race_name="Human", health=(100, 70))
        assert items.Antidote().use(human) == "You are not affected by poison.\n"

        dwarf = TestGameState.create_player(class_name="Warrior", race_name="Dwarf", health=(100, 60))
        dwarf.state = "fight"
        dwarf.status_effects["Poison"].active = True
        dwarf.status_effects["Poison"].duration = 3
        dwarf.status_effects["Poison"].extra = 5
        dwarf.modify_inventory = lambda *_args, **_kwargs: None
        monkeypatch.setattr("src.core.items.random.randint", lambda low, high: high)

        antidote_result = items.Antidote().use(dwarf)

        assert dwarf.status_effects["Poison"].active is False
        assert dwarf.status_effects["Hangover"].active is True
        assert "cured of poison" in antidote_result
        assert "healed for 10 health" in antidote_result

        human.physical_effects["Bleed"].active = True
        human.physical_effects["Bleed"].duration = 2
        human.physical_effects["Bleed"].extra = 4
        human.modify_inventory = lambda *_args, **_kwargs: None
        bandage_result = items.Bandage().use(human)
        assert human.physical_effects["Bleed"].active is False
        assert "cured of bleed" in bandage_result

        remedy_user = TestGameState.create_player(class_name="Warrior", race_name="Human", health=(100, 80))
        remedy_user.modify_inventory = lambda *_args, **_kwargs: None
        for status in ["Poison", "Blind", "Silence", "Doom"]:
            remedy_user.status_effects[status].active = True
            remedy_user.status_effects[status].duration = 2
        remedy_result = items.Remedy().use(remedy_user)
        assert all(not remedy_user.status_effects[status].active for status in ["Poison", "Blind", "Silence", "Doom"])
        assert "cured of poison" in remedy_result
        assert "cured of doom" in remedy_result

    def test_scroll_and_sanctuary_scroll_consume_last_charge(self):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        calls = []
        player.modify_inventory = lambda item, subtract=False, **_kwargs: calls.append((item.name, subtract))

        bless = items.BlessScroll()
        bless.spell = SimpleNamespace(cast=lambda user, target=None, special=True: "Blessed!\n")
        bless.charges = 1
        bless_result = bless.use(player)

        assert "uses Bless Scroll" in bless_result
        assert "Blessed!" in bless_result
        assert "crumbles to dust" in bless_result
        assert ("Bless Scroll", True) in calls

        sanctuary = items.SanctuaryScroll()
        sanctuary.spell = SimpleNamespace(cast_out=lambda user=None: "A safe light surrounds you.\n")
        sanctuary.charges = 1
        sanctuary_result = sanctuary.use(player)

        assert "uses Sanctuary Scroll" in sanctuary_result
        assert "safe light surrounds you" in sanctuary_result
        assert "crumbles to dust" in sanctuary_result
        assert ("Sanctuary Scroll", True) in calls

    def test_scroll_use_accepts_combat_result_spell_returns(self):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        player.modify_inventory = lambda *_args, **_kwargs: None

        holy = items.HolyScroll()
        holy.charges = 1
        holy.spell = SimpleNamespace(
            cast=lambda user, target=None, special=True: CombatResult(
                action="Holy",
                actor=user,
                target=target,
                message="Radiant light scorches the foe.\n",
            )
        )

        result = holy.use(player, target=SimpleNamespace(name="Skeleton"))

        assert "uses Holy Scroll" in result
        assert "Radiant light scorches the foe." in result
        assert "crumbles to dust" in result

    def test_class_ring_description_and_mod_branches(self):
        ring = items.ClassRing()
        assert ring.get_description() == ring.description

        berserker = TestGameState.create_player(class_name="Berserker", race_name="Human")
        berserker.equipment["Ring"] = ring
        ring.class_mod(berserker)
        assert berserker.equipment["Ring"].mod == "+15% Crit"
        assert "Berserker" in ring.get_description(berserker)

        rogue = TestGameState.create_player(class_name="Rogue", race_name="Human")
        rogue.equipment["Ring"] = items.ClassRing()
        before = rogue.stats.charisma
        rogue.equipment["Ring"].class_mod(rogue)
        assert rogue.stats.charisma == before + 2
        assert rogue.equipment["Ring"].mod == "+2 Luck"

        soulcatcher = TestGameState.create_player(class_name="Soulcatcher", race_name="Human")
        soulcatcher.equipment["Ring"] = items.ClassRing()
        soulcatcher.spellbook["Totem"] = SimpleNamespace(unlocked_aspects={"Soul": False})
        soulcatcher.equipment["Ring"].class_mod(soulcatcher)
        assert soulcatcher.spellbook["Totem"].unlocked_aspects["Soul"] is True
        assert soulcatcher.equipment["Ring"].mod == "Soul Aspect Unlock"

        unknown = TestGameState.create_player(class_name="Warrior", race_name="Human")
        unknown.equipment["Ring"] = items.ClassRing()
        assert unknown.equipment["Ring"].get_description(unknown) == ring.description
