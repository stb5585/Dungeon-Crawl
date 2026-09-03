"""Focused regression coverage for the Berserker Bloodied Momentum loop."""

from types import SimpleNamespace

import pytest

from src.core import abilities, enemies, items
from src.core.classes import ability_mechanics, berserker, class_rings, grandmaster, promotion_kits
from src.core.save_system import PlayerDataSerializer
from tests.test_framework import TestGameState


class _Always:
    def random(self):
        return 0.0


def _player(*, health=(100, 49)):
    player = TestGameState.create_player(
        class_name="Berserker",
        race_name="Human",
        level=80,
        pro_level=3,
        health=health,
        mana=(100, 100),
    )
    return player


def _set_scars(player, count):
    class_rings.ensure_state(player)["data"]["Berserker"]["battle_scars"] = count


def _unlock_rank(player, weapon_type, rank=1):
    xp = grandmaster.XP_THRESHOLDS[rank - 1]
    grandmaster.add_discipline_xp(player, weapon_type, xp)


def _weapon_event(actor, target):
    promotion_kits.record_damage_event(
        actor,
        target,
        10,
        "Physical",
        metadata={"attack_source": "weapon", "weapon_type": "Longsword"},
    )


def test_caps_are_berserker_only_and_exact_at_scar_milestones():
    player = _player()
    assert promotion_kits.cap_for(player, "bloodied_momentum") == 3

    _set_scars(player, 10)
    assert promotion_kits.cap_for(player, "bloodied_momentum") == 4

    _set_scars(player, 20)
    assert promotion_kits.cap_for(player, "bloodied_momentum") == 5

    player.cls = SimpleNamespace(name="Weapon Master")
    assert promotion_kits.cap_for(player, "bloodied_momentum") == 0


def test_weapon_hit_gain_is_once_per_action_and_critical_bonus_once_per_round():
    player = _player(health=(100, 24))
    _set_scars(player, 20)
    target = enemies.Goblin()

    promotion_kits.begin_action(player, action="Attack", round_number=2)
    _weapon_event(player, target)
    _weapon_event(player, target)
    assert promotion_kits.combat_state(player)["bloodied_momentum"] == 2

    promotion_kits.begin_action(player, action="Attack", round_number=2)
    _weapon_event(player, target)
    assert promotion_kits.combat_state(player)["bloodied_momentum"] == 3

    promotion_kits.begin_incoming_action(player, round_number=2)
    promotion_kits.record_damage_taken(player, 5, "Physical")
    promotion_kits.record_damage_taken(player, 5, "Physical")
    assert promotion_kits.combat_state(player)["bloodied_momentum"] == 4

    promotion_kits.begin_incoming_action(player, round_number=3)
    promotion_kits.record_damage_taken(player, 5, "Physical")
    assert promotion_kits.combat_state(player)["bloodied_momentum"] == 5


@pytest.mark.parametrize("current", [50, 25])
def test_thresholds_are_strict(current):
    player = _player(health=(100, current))
    target = enemies.Goblin()
    promotion_kits.begin_action(player, action="Attack", round_number=1)

    _weapon_event(player, target)

    expected = 0 if current == 50 else 1
    assert promotion_kits.combat_state(player)["bloodied_momentum"] == expected


def test_invalid_heavy_art_does_not_spend_but_valid_miss_does(monkeypatch):
    player = _player()
    target = enemies.Goblin()
    state = promotion_kits.combat_state(player)
    state["bloodied_momentum"] = 2
    _unlock_rank(player, "Longsword")

    message = grandmaster.perform_weapon_art(player, target, "Guard Cleaver")
    assert "requires an equipped Longsword" in message
    assert state["bloodied_momentum"] == 2

    player.equipment["Weapon"] = items.Bastard()
    calls = []

    def miss(_target, **kwargs):
        calls.append(kwargs)
        return "Miss.\n", False, 1

    monkeypatch.setattr(player, "weapon_damage", miss)
    message = grandmaster.perform_weapon_art(player, target, "Guard Cleaver")

    assert state["bloodied_momentum"] == 0
    assert calls[0]["accuracy_modifier"] == pytest.approx(0.06)
    assert calls[0]["dmg_mod"] == pytest.approx(1.15)
    assert "spends 2 Bloodied Momentum" in message
    assert "spent despite the miss" in message


@pytest.mark.parametrize(
    "art_name",
    [
        "Guard Cleaver",
        "Guard Cleaver 2",
        "Guard Cleaver 3",
        "Reaver's Mark",
        "Reaver's Mark 2",
        "Reaver's Mark 3",
        "Brace",
        "Brace 2",
        "Brace 3",
        "Anvil Strike",
        "Anvil Strike 2",
        "Anvil Strike 3",
    ],
)
def test_only_named_heavy_arts_and_upgrades_prepare_a_payoff(art_name):
    player = _player()
    state = promotion_kits.combat_state(player)
    state["bloodied_momentum"] = 2

    payoff, message = berserker.prepare_heavy_art_payoff(player, art_name)

    assert payoff.stacks == 2
    assert "spends 2 Bloodied Momentum" in message
    state["bloodied_momentum"] = 2
    unrelated, unrelated_message = berserker.prepare_heavy_art_payoff(
        player,
        "Reckless Onslaught",
    )
    assert unrelated.stacks == 0
    assert unrelated_message == ""
    assert state["bloodied_momentum"] == 2


@pytest.mark.parametrize(
    ("art_name", "weapon_type", "weapon", "assert_rider"),
    [
        (
            "Guard Cleaver",
            "Longsword",
            items.Bastard,
            lambda player, target: target.stat_effects["Defense"].extra == -7,
        ),
        (
            "Reaver's Mark",
            "Battle Axe",
            items.Greataxe,
            lambda player, target: target._reavers_mark["bonus"] == pytest.approx(0.14),
        ),
        (
            "Brace",
            "Polearm",
            items.Halberd,
            lambda player, target: (
                player._brace_art["reduction"] == pytest.approx(0.24)
                and player._brace_art["counter"] == pytest.approx(0.49)
            ),
        ),
        (
            "Anvil Strike",
            "Hammer",
            items.Sledgehammer,
            lambda player, target: target.stat_effects["Defense"].extra == -8,
        ),
    ],
)
def test_heavy_art_mutations_apply_only_after_a_hit(
    monkeypatch,
    art_name,
    weapon_type,
    weapon,
    assert_rider,
):
    player = _player()
    target = enemies.Goblin()
    player.equipment["Weapon"] = weapon()
    _unlock_rank(player, weapon_type)
    promotion_kits.combat_state(player)["bloodied_momentum"] = 2
    monkeypatch.setattr(
        player,
        "weapon_damage",
        lambda _target, **_kwargs: ("Hit.\n", True, 1),
    )

    message = grandmaster.perform_weapon_art(player, target, art_name)

    assert assert_rider(player, target)
    assert "Bloodied Momentum mutates the art" in message


def test_scar_and_ring_preservation_are_independent(monkeypatch):
    player = _player(health=(100, 24))
    player.equipment["Weapon"] = items.Bastard()
    player.equipment["Ring"] = items.ClassRing()
    class_rings.ensure_state(player)["awakened"]["Berserker"] = True
    _set_scars(player, 10)
    _unlock_rank(player, "Longsword")
    target = enemies.Goblin()
    outcomes = iter([True, False, False])

    def resolve(_target, **_kwargs):
        hit = next(outcomes)
        return ("Hit.\n" if hit else "Miss.\n"), hit, 1

    monkeypatch.setattr(player, "weapon_damage", resolve)

    promotion_kits.combat_state(player)["bloodied_momentum"] = 3
    first = grandmaster.perform_weapon_art(player, target, "Guard Cleaver")
    assert "Battle Scars preserve 1" in first

    second = grandmaster.perform_weapon_art(player, target, "Guard Cleaver")
    assert "Bloodied Crits preserves 1" in second

    third = grandmaster.perform_weapon_art(player, target, "Guard Cleaver")
    assert "spent despite the miss" in third
    assert promotion_kits.combat_state(player)["bloodied_momentum"] == 0


def test_spending_heavy_art_cannot_rebuild_momentum_from_its_own_hit(monkeypatch):
    player = _player()
    player.equipment["Weapon"] = items.Bastard()
    _unlock_rank(player, "Longsword")
    target = enemies.Goblin()
    state = promotion_kits.combat_state(player)
    state["bloodied_momentum"] = 3
    promotion_kits.begin_action(
        player,
        action="Use Skill",
        choice="Guard Cleaver",
        round_number=1,
    )

    def hit(target, **_kwargs):
        _weapon_event(player, target)
        return "Hit.\n", True, 1

    monkeypatch.setattr(player, "weapon_damage", hit)

    grandmaster.perform_weapon_art(player, target, "Guard Cleaver")

    assert state["bloodied_momentum"] == 0
    promotion_kits.begin_action(player, action="Attack", round_number=1)
    _weapon_event(player, target)
    assert state["bloodied_momentum"] == 1


def test_awakened_ring_only_boosts_art_rider_below_quarter_health(monkeypatch):
    player = _player(health=(100, 24))
    player.equipment["Weapon"] = items.Bastard()
    player.equipment["Ring"] = items.ClassRing()
    class_rings.ensure_state(player)["awakened"]["Berserker"] = True
    _unlock_rank(player, "Longsword")
    target = enemies.Goblin()
    promotion_kits.combat_state(player)["bloodied_momentum"] = 2
    monkeypatch.setattr(
        player,
        "weapon_damage",
        lambda _target, **_kwargs: ("Hit.\n", True, 1),
    )

    grandmaster.perform_weapon_art(player, target, "Guard Cleaver")

    assert target.stat_effects["Defense"].extra == -8


def test_final_assault_spends_momentum_and_does_not_regenerate_it(monkeypatch):
    defender = _player(health=(100, 10))
    defender.spellbook["Skills"]["Final Assault"] = abilities.FinalAssault()
    attacker = enemies.Goblin()
    state = promotion_kits.combat_state(defender)
    state["bloodied_momentum"] = 3
    calls = []

    def counter(target, **kwargs):
        calls.append(kwargs)
        target.health.current = 0
        _weapon_event(defender, target)
        return "Counter.\n", True, 1

    monkeypatch.setattr(defender, "weapon_damage", counter)

    message, stabilized = ability_mechanics.final_assault_response(defender, attacker, 10)

    assert stabilized is True
    assert defender.health.current == 1
    assert state["bloodied_momentum"] == 0
    assert calls[0]["accuracy_modifier"] == pytest.approx(0.09)
    assert calls[0]["dmg_mod"] == pytest.approx(1.40)
    assert "spends 3 Bloodied Momentum on Final Assault" in message


def test_twenty_scar_threshold_reports_stability_and_combat_state_never_saves():
    player = _player(health=(100, 15))
    _set_scars(player, 20)
    promotion_kits.combat_state(player)["bloodied_momentum"] = 5

    gained, message = berserker.record_battle_scar(player, rng=_Always())
    restored = PlayerDataSerializer.deserialize(
        PlayerDataSerializer.serialize(player),
        skip_tiles=True,
    )

    assert gained is False
    assert "hold steady at the 15% victory threshold" in message
    assert promotion_kits.combat_state(restored)["bloodied_momentum"] == 0


def test_combat_cleanup_resets_meter_and_both_preservation_flags():
    player = _player()
    state = promotion_kits.combat_state(player)
    state["bloodied_momentum"] = 3
    state["battle_scar_momentum_preserved"] = True
    state["bloodied_ring_miss_preserved"] = True

    promotion_kits.end_combat(player, victory=False)
    cleared = promotion_kits.combat_state(player)

    assert cleared["bloodied_momentum"] == 0
    assert cleared["battle_scar_momentum_preserved"] is False
    assert cleared["bloodied_ring_miss_preserved"] is False


def test_death_clears_momentum_before_combat_settlement():
    player = _player(health=(100, 1))
    state = promotion_kits.combat_state(player)
    state["bloodied_momentum"] = 3
    state["battle_scar_momentum_preserved"] = True
    state["bloodied_ring_miss_preserved"] = True
    player.health.current = 0

    promotion_kits.record_damage_taken(player, 5, "Physical")

    assert state["bloodied_momentum"] == 0
    assert state["battle_scar_momentum_preserved"] is False
    assert state["bloodied_ring_miss_preserved"] is False


def test_status_surfaces_show_threshold_cap_and_preservation_readiness():
    player = _player(health=(100, 24))
    _set_scars(player, 10)
    promotion_kits.combat_state(player)["bloodied_momentum"] = 2

    rows = dict(promotion_kits.status_summary_rows(player))
    status = player._class_kit_status_str()

    assert rows["Bloodied Momentum"].startswith("2/4")
    assert rows["Bloodied State"] == "Critical (<25%)"
    assert rows["Scar Cap"] == "+1 from 10 scars"
    assert rows["Scar Preserve"] == "Ready"
    assert "Bloodied Momentum:" in status
    assert "Scar Threshold:" in status
