"""Focused coverage for the Inquisitor/Seeker investigation payoff."""

from types import MethodType

from src.core import abilities, enemies, items
from src.core.classes import class_rings, promotion_kits
from tests.test_framework import TestGameState


def _player(class_name="Inquisitor"):
    return TestGameState.create_player(
        class_name=class_name,
        race_name="Human",
        level=70,
        mana=(300, 300),
    )


def _awakened_seeker():
    player = _player("Seeker")
    player.equipment["Ring"] = items.ClassRing()
    state = class_rings.ensure_state(player)
    state["awakened"]["Seeker"] = True
    player.equipment["Ring"].class_mod(player)
    return player


def test_revelation_caps_are_fixed_and_target_specific():
    inquisitor = _player()
    seeker = _player("Seeker")
    target = enemies.Goblin()
    other = enemies.Goblin()

    for _ in range(5):
        promotion_kits.add_revelation(inquisitor, target)
        promotion_kits.add_revelation(seeker, target)
    promotion_kits.add_revelation(seeker, other)

    assert promotion_kits.cap_for(inquisitor, "revelation") == 2
    assert promotion_kits.cap_for(seeker, "revelation") == 3
    assert promotion_kits.revelation_stacks(inquisitor, target) == 2
    assert promotion_kits.revelation_stacks(seeker, target) == 3
    assert promotion_kits.revelation_stacks(seeker, other) == 1
    assert promotion_kits.cap_for(_player("Rogue"), "revelation") == 0


def test_inspect_discovers_studied_and_ring_insight_without_exposing_math():
    seeker = _awakened_seeker()
    target = enemies.Goblin()
    seeker.ensure_promotion_kit_state()["case_journal"][target.enemy_typ] = 25

    message = promotion_kits.record_inspect(seeker, target)
    second = promotion_kits.record_inspect(seeker, target)

    assert promotion_kits.revelation_stacks(seeker, target) == 3
    assert "familiar tell" in message
    assert "Hidden Cache insight" in message
    assert "Hidden Cache insight" not in second
    assert "/100" not in message


def test_payoff_consumes_before_resolution_and_applies_only_on_hit():
    player = _player()
    target = enemies.Goblin()
    promotion_kits.begin_action(player, action="Attack")
    promotion_kits.add_revelation(player, target, 2)

    accuracy, damage, message = promotion_kits.prepare_revelation_payoff(
        player,
        target,
        basic_attack=True,
    )

    assert accuracy == 0.08
    assert damage == 1.10
    assert "commits 2 Revelation" in message
    assert promotion_kits.revelation_stacks(player, target) == 0
    miss = promotion_kits.finish_revelation_payoff(player, target, hit=False)
    assert "lost on the miss" in miss
    assert not target.stat_effects["Defense"].active


def test_exploit_weakness_uses_its_inner_weapon_hit_result():
    player = _player()
    target = enemies.Goblin()
    player.weapon_damage = MethodType(
        lambda self, defender, **kwargs: ("The exploit misses.\n", False, 1),
        player,
    )
    promotion_kits.begin_action(player, action="Use Skill", choice="Exploit Weakness")

    skill = abilities.ExploitWeakness()
    skill.use(player, target)

    assert skill.result.hit is False
    assert promotion_kits.revelation_stacks(player, target) == 0
    assert promotion_kits.case_progress(player, target) == 0


def test_case_milestones_improve_exploit_and_visible_prediction():
    player = _player()
    target = enemies.Goblin()
    journal = player.ensure_promotion_kit_state()["case_journal"]
    journal[target.enemy_typ] = 75
    promotion_kits.begin_action(player, action="Use Skill", choice="Exploit Weakness")

    accuracy, damage, message = promotion_kits.prepare_revelation_payoff(player, target)
    assert accuracy == 0.10
    assert damage == 1.0
    assert "Weakness Brief" in message

    promotion_kits.begin_incoming_action(player, round_number=1, actor=target)
    read = promotion_kits.record_visible_telegraph(player, target, visible=True)
    assert "anticipates" in read
    promotion_kits.begin_incoming_action(player, round_number=2, actor=target)
    assert promotion_kits.case_prediction_dodge_bonus(player, target) == 0.10


def test_victory_progress_requires_visible_enemy_details():
    player = _player()
    target = enemies.Goblin()
    promotion_kits.start_combat(player)
    promotion_kits.end_combat(player, victory=True, enemy=target)
    assert promotion_kits.case_progress(player, target) == 0

    promotion_kits.start_combat(player)
    promotion_kits.combat_state(player)["visible_enemy_types"] = {target.enemy_typ}
    promotion_kits.end_combat(player, victory=True, enemy=target)
    assert promotion_kits.case_progress(player, target) == 4


def test_wayfinding_uses_route_context_and_ring_smoothing():
    seeker = _awakened_seeker()
    ordinary_cost, _ = promotion_kits.wayfinding_cost(seeker, 100)
    mapped_cost, message = promotion_kits.wayfinding_cost(
        seeker,
        100,
        mapping_progress=0.70,
    )
    seeker.ensure_promotion_kit_state()["case_journal"]["Monster"] = 100
    closed_cost, _ = promotion_kits.wayfinding_cost(
        seeker,
        100,
        enemy_type="Monster",
    )

    assert ordinary_cost == 95
    assert mapped_cost == 90
    assert closed_cost == 85
    assert "Wayfinding" in message

    promotion_kits.gain_case_progress(seeker, "Monster", 1, "a fresh route clue")
    focused_cost, _ = promotion_kits.wayfinding_cost(seeker, 100)
    assert focused_cost == 85


def test_hidden_cache_awards_one_real_item_per_mapped_level():
    seeker = _awakened_seeker()

    message = class_rings.award_hidden_cache(seeker, 3, 0.75)
    duplicate = class_rings.award_hidden_cache(seeker, 3, 1.0)

    assert "Hidden Cache discovered" in message
    assert len(seeker.inventory["Smoke Bomb"]) == 1
    assert duplicate == ""


def test_status_uses_selected_target_and_hides_journal_counter():
    seeker = _player("Seeker")
    selected = enemies.Goblin()
    other = enemies.Goblin()
    promotion_kits.add_revelation(seeker, selected, 1)
    promotion_kits.add_revelation(seeker, other, 3)
    seeker.ensure_promotion_kit_state()["case_journal"][selected.enemy_typ] = 50

    rows = dict(promotion_kits.status_summary_rows(seeker, target=selected))

    assert rows["Revelation"].startswith("1/3")
    assert rows["Case"] == "Weakness Brief"
    assert "/100" not in rows["Case"]
