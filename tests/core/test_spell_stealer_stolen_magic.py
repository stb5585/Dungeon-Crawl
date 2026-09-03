"""Focused coverage for Stolen Charge and Arcane Larceny."""

from types import SimpleNamespace

from src.core import abilities, enemies, items
from src.core.classes import class_rings, promotion_kits
from src.core.combat.combat_result import CombatResult, CombatResultGroup
from src.core.save_system import PlayerDataSerializer
from tests.test_framework import TestGameState


def _player(class_name: str, **kwargs):
    return TestGameState.create_player(
        class_name=class_name,
        race_name="Human",
        level=30,
        **kwargs,
    )


def _result(actor, target, damage: int, *, hit: bool = True) -> CombatResult:
    return CombatResult(
        action="test",
        actor=actor,
        target=target,
        hit=hit,
        damage=damage,
    )


def test_stolen_charge_has_fixed_class_caps_and_combat_cleanup():
    stealer = _player("Spell Stealer")
    trickster = _player("Arcane Trickster")
    outsider = _player("Thief")

    for _unused in range(5):
        promotion_kits.gain_stolen_charge(stealer, "test")
        promotion_kits.gain_stolen_charge(trickster, "test")
    assert promotion_kits.combat_state(stealer)["stolen_charge"] == 2
    assert promotion_kits.combat_state(trickster)["stolen_charge"] == 3
    assert promotion_kits.gain_stolen_charge(outsider, "test") == ""

    promotion_kits.end_combat(trickster)
    assert promotion_kits.combat_state(trickster)["stolen_charge"] == 0


def test_payoff_spends_on_attempt_aggregates_action_and_uses_arcane_damage():
    trickster = _player("Arcane Trickster")
    target = enemies.Goblin()
    target.health.current = target.health.max = 200
    seen_types = []
    original_reduction = target.damage_reduction

    def capture_type(damage, attacker, typ="Physical"):
        seen_types.append(typ)
        return original_reduction(damage, attacker, typ=typ)

    target.damage_reduction = capture_type
    promotion_kits.combat_state(trickster)["stolen_charge"] = 2
    spend = promotion_kits.prepare_stolen_charge_payoff(trickster, "Attack")
    group = CombatResultGroup(action="Attack")
    group.add(_result(trickster, target, 10))
    group.add(_result(trickster, target, 20))

    message = promotion_kits.record_action_resolution(trickster, group)

    assert "commits 2 Stolen Charge" in spend
    assert "9 Arcane damage" in message
    assert target.health.current == 191
    assert seen_types == ["Arcane"]
    assert promotion_kits.combat_state(trickster)["stolen_charge"] == 0


def test_miss_consumes_charge_and_unrelated_actions_retain_it():
    stealer = _player("Spell Stealer")
    target = enemies.Goblin()
    state = promotion_kits.combat_state(stealer)
    state["stolen_charge"] = 2

    assert promotion_kits.prepare_stolen_charge_payoff(
        stealer,
        "Use Skill",
        SimpleNamespace(weapon=False),
    ) == ""
    assert state["stolen_charge"] == 2

    promotion_kits.prepare_stolen_charge_payoff(stealer, "Attack")
    message = promotion_kits.record_action_resolution(
        stealer,
        _result(stealer, target, 0, hit=False),
    )
    assert "dissipates" in message
    assert state["stolen_charge"] == 0


def test_stolen_scroll_gain_stays_separate_from_charge_spent_by_its_cast():
    stealer = _player("Spell Stealer")
    state = promotion_kits.combat_state(stealer)
    state["stolen_charge"] = 2
    spell = abilities.Firebolt()

    promotion_kits.prepare_stolen_charge_payoff(stealer, "Cast Spell", spell)
    promotion_kits.gain_stolen_charge(stealer, "stolen spell scroll")
    assert state["stolen_charge"] == 1


def test_theft_validates_mana_before_mutating_inventory_or_spellbook(monkeypatch):
    target = SimpleNamespace(
        name="Acolyte",
        spellbook={"Spells": {"Firebolt": abilities.Firebolt()}},
        class_ring_trial_enemy=False,
    )
    stealer = _player("Spell Stealer", mana=(100, 0))
    stealer.modify_inventory(items.BlankScroll())

    message = abilities.StealSpell().use(stealer, target)

    assert "not have enough mana" in message
    assert "Blank Scroll" in stealer.inventory
    assert not any(name.startswith("Stolen ") for name in stealer.inventory)

    trickster = _player("Arcane Trickster", mana=(100, 0))
    monkeypatch.setattr("src.core.abilities.skills.random.random", lambda: 0.0)
    message = abilities.StealSpell2().use(trickster, target)
    assert "not have enough mana" in message
    assert "Firebolt" not in trickster.spellbook["Spells"]


def test_arcane_larceny_requires_equipment_ticks_and_preserves_once():
    trickster = _player("Arcane Trickster")
    trickster.equipment["Ring"] = items.ClassRing()
    trickster.awaken_class_ring()
    trickster.equipment["Ring"] = items.NoRing()
    class_rings.activate_spell_steal_buff(trickster)
    data = class_rings.ensure_state(trickster)["data"]["Arcane Trickster"]
    assert data["buff_turns"] == 0

    trickster.equipment["Ring"] = items.ClassRing()
    class_rings.activate_spell_steal_buff(trickster)
    data = class_rings.ensure_state(trickster)["data"]["Arcane Trickster"]
    assert data["buff_turns"] == 3
    assert promotion_kits.tick_combat_state(trickster) == ""
    assert class_rings.ensure_state(trickster)["data"]["Arcane Trickster"]["buff_turns"] == 3
    promotion_kits.tick_combat_state(trickster)
    promotion_kits.tick_combat_state(trickster)
    assert class_rings.ensure_state(trickster)["data"]["Arcane Trickster"]["buff_turns"] == 1
    assert "fades" in promotion_kits.tick_combat_state(trickster)

    target = enemies.Goblin()
    target.health.current = target.health.max = 200
    state = promotion_kits.combat_state(trickster)
    state["stolen_charge"] = 2
    promotion_kits.prepare_stolen_charge_payoff(trickster, "Attack")
    message = promotion_kits.record_action_resolution(
        trickster,
        _result(trickster, target, 20),
    )
    assert "preserves 1" in message
    assert state["stolen_charge"] == 1

    state["stolen_charge"] = 2
    promotion_kits.prepare_stolen_charge_payoff(trickster, "Attack")
    message = promotion_kits.record_action_resolution(
        trickster,
        _result(trickster, target, 20),
    )
    assert "preserves 1" not in message
    assert state["stolen_charge"] == 0


def test_stolen_magic_is_not_restored_from_a_save_and_status_is_discreet():
    trickster = _player("Arcane Trickster")
    trickster.equipment["Ring"] = items.ClassRing()
    trickster.awaken_class_ring()
    class_rings.activate_spell_steal_buff(trickster)
    promotion_kits.combat_state(trickster)["stolen_charge"] = 3

    rows = promotion_kits.status_summary_rows(trickster)
    assert any(label == "Stolen Charge" and "3/3" in value for label, value in rows)
    assert ("Arcane Larceny", "Active · 3 turns") in rows
    assert ("Ring Preserve", "Arcane Larceny ready") in rows

    restored = PlayerDataSerializer.deserialize(
        PlayerDataSerializer.serialize(trickster),
        skip_tiles=True,
    )
    assert promotion_kits.combat_state(restored)["stolen_charge"] == 0
    assert class_rings.ensure_state(restored)["data"]["Arcane Trickster"][
        "buff_turns"
    ] == 0
