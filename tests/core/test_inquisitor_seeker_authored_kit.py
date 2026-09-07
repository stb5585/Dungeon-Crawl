"""Regression coverage for authored Inquisitor and Seeker progression."""

from types import MethodType, SimpleNamespace

import pytest

from src.core import abilities, enemies
from src.core.classes import promotion_kits
from src.core.progression import ABILITY_TREES, NodeKind, ProgressionState
from tests.test_framework import TestGameState


def _player(class_name: str, level: int = 90):
    player = TestGameState.create_player(
        class_name=class_name,
        level=level,
        mana=(300, 300),
    )
    player.progression = ProgressionState(level=level)
    return player


def _grant(player, *talent_keys: str) -> None:
    talents = {
        node.payload["talent_key"]: node
        for tree_name in ("Inquisitor", "Seeker")
        for node in ABILITY_TREES[tree_name].nodes
        if node.kind == NodeKind.TALENT
    }
    for talent_key in talent_keys:
        player.progression.purchased_node_ids.add(talents[talent_key].id)


def _set_mapping(player, visited: int, total: int = 10) -> None:
    player.location_z = 1
    player.world_dict = {
        (index, 0, 1): SimpleNamespace(visited=index < visited, near=False)
        for index in range(total)
    }


def test_inquisitor_and_seeker_use_authored_budget_and_rows():
    inquisitor = ABILITY_TREES["Inquisitor"]
    development = [node for node in inquisitor.nodes if node.kind != NodeKind.PROMOTION]
    promotion = next(node for node in inquisitor.nodes if node.kind == NodeKind.PROMOTION)
    seeker = ABILITY_TREES["Seeker"]

    assert len(development) == 23
    assert sum(node.cost for node in development) == 24
    assert promotion.cost == 3
    assert promotion.payload["prerequisite_mode"] == "any"
    assert len(promotion.prerequisites) == 2
    assert len(seeker.nodes) == 28
    assert sum(node.cost for node in seeker.nodes) == 30
    assert 0.60 <= 20 / 30 <= 0.70
    assert max(node.position[1] for node in inquisitor.nodes) <= 7
    assert max(node.position[1] for node in seeker.nodes) <= 6


def test_warding_studies_extends_every_elemental_resist_spell():
    inquisitor = _player("Inquisitor", 60)
    _grant(inquisitor, "inquisitor.warding-studies")

    for ability_class, element in (
        (abilities.ResistFire, "Fire"),
        (abilities.ResistIce, "Ice"),
        (abilities.ResistElectric, "Electric"),
        (abilities.ResistWater, "Water"),
        (abilities.ResistEarth, "Earth"),
        (abilities.ResistWind, "Wind"),
    ):
        ability_class().cast(inquisitor)
        assert inquisitor.magic_effects[f"Resist {element}"].duration == 7


def test_take_notes_reports_ranks_without_advancing_cases():
    inquisitor = _player("Inquisitor", 60)
    journal = inquisitor.ensure_promotion_kit_state()["case_journal"]
    journal.update({"Animal": 25, "Slime": 75})

    message = abilities.TakeNotes().use_out(inquisitor)

    assert "Animal: Known Tells" in message
    assert "Slime: Pattern Lock" in message
    assert journal == {"Animal": 25, "Slime": 75}


def test_seeker_revelation_talents_improve_inspect_and_payoffs():
    seeker = _player("Seeker")
    target = enemies.Goblin()
    _grant(
        seeker,
        "seeker.practiced-inspection",
        "seeker.precise-revelation",
        "seeker.conserved-insight",
        "seeker.exposed-truth",
    )

    promotion_kits.record_inspect(seeker, target)
    assert promotion_kits.case_progress(seeker, target) == 4
    promotion_kits.add_revelation(seeker, target, 2)
    promotion_kits.begin_action(seeker, action="Attack")
    accuracy, damage, _ = promotion_kits.prepare_revelation_payoff(
        seeker,
        target,
        basic_attack=True,
    )
    assert accuracy == pytest.approx(0.15)
    assert damage == pytest.approx(1.15)
    promotion_kits.finish_revelation_payoff(seeker, target, hit=False)
    assert promotion_kits.revelation_stacks(seeker, target) == 1

    promotion_kits.begin_action(seeker, action="Attack")
    promotion_kits.prepare_revelation_payoff(seeker, target, basic_attack=True)
    promotion_kits.finish_revelation_payoff(seeker, target, hit=True)
    assert target.stat_effects["Defense"].extra == -2
    assert target.stat_effects["Defense"].duration == 3


def test_seeker_active_techniques_scale_from_case_and_mapping():
    seeker = _player("Seeker")
    target = enemies.Goblin()
    _grant(
        seeker,
        "seeker.patient-deduction",
        "seeker.proven-case",
        "seeker.inevitable-conclusion",
        "seeker.light-footed",
        "seeker.sanctuary-route",
        "seeker.master-cartographer",
    )
    seeker.ensure_promotion_kit_state()["case_journal"][target.enemy_typ] = 25
    seeker.weapon_damage = MethodType(
        lambda self, defender, **kwargs: ("Deduction lands.\n", True, 1),
        seeker,
    )

    strike = abilities.DeductiveStrike().use(seeker, target)
    assert strike.hit is True
    promotion_kits.add_revelation(seeker, target, 3)
    conclusion = abilities.ForegoneConclusion().use(seeker, target)
    assert conclusion.hit is True
    assert target.stat_effects["Attack"].extra == -24
    assert target.stat_effects["Attack"].duration == 4

    _set_mapping(seeker, 4)
    step = abilities.SurveyorsStep().use(seeker)
    passage = abilities.SafePassage().use(seeker)
    assert step.hit is True
    assert seeker.stat_effects["Speed"].extra == 17
    assert passage.hit is True
    assert seeker.stat_effects["Defense"].extra == 16
    assert seeker.stat_effects["Defense"].duration == 4


def test_wayfinding_talents_expand_mapping_discount():
    seeker = _player("Seeker")
    _grant(seeker, "seeker.early-bearings", "seeker.efficient-passage")

    assert promotion_kits.wayfinding_discount(seeker, mapping_progress=0.34) == 0.0
    assert promotion_kits.wayfinding_discount(seeker, mapping_progress=0.35) == 0.10
