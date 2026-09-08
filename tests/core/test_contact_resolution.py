"""Tests for fitted one-roll contact resolution."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.core.combat.contact import (
    CONTACT_MODIFIER_REGISTRY,
    ArmorGroup,
    ContactInputs,
    ContactKind,
    FailureAttribution,
    ModifierClassification,
    contact_chance,
    resolve_contact,
)


class CountingRandom:
    """Deterministic random source that records contact draw count."""

    def __init__(self, value: float) -> None:
        self.value = value
        self.calls = 0

    def random(self) -> float:
        self.calls += 1
        return self.value


def test_fitted_curves_match_committed_threshold_report():
    report_path = Path("reports/foundational/contact_fit_v1.json")
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["seed"] == 1337
    for fit in report["fits"].values():
        assert fit["weighted_mean_error"] <= 0.03
        assert fit["maximum_ordinary_cell_error"] <= 0.07


@pytest.mark.parametrize("kind", list(ContactKind))
def test_runtime_curve_matches_fitted_report(kind: ContactKind):
    report = json.loads(
        Path("reports/foundational/contact_fit_v1.json").read_text(encoding="utf-8")
    )
    for cell in report["fits"][kind.value]["cells"]:
        inputs = cell["inputs"]
        if kind is ContactKind.WEAPON:
            contact_inputs = ContactInputs(
                kind=kind,
                proficiency_difference=inputs["proficiency_difference"],
                defender_speed=inputs["defender_speed"],
                armor_group=ArmorGroup(inputs["armor_group"]),
            )
        else:
            contact_inputs = ContactInputs(
                kind=kind,
                intelligence=inputs["intelligence"],
                wisdom=inputs["wisdom"],
                charisma_term=inputs["charisma_term"],
            )
        assert contact_chance(contact_inputs) == pytest.approx(cell["fitted"], abs=1e-12)


def test_contact_uses_one_roll_and_always_hit_uses_none():
    rng = CountingRandom(0.5)
    ordinary = resolve_contact(ContactInputs(kind=ContactKind.WEAPON), rng=rng)
    guaranteed = resolve_contact(ContactInputs(kind=ContactKind.SPELL, always_hit=True), rng=rng)

    assert ordinary.hit is True
    assert ordinary.roll == 0.5
    assert rng.calls == 1
    assert guaranteed.hit is True
    assert guaranteed.roll is None


def test_counterfactual_attribution_uses_the_same_roll():
    inputs = ContactInputs(
        kind=ContactKind.WEAPON,
        defender_speed=22,
        armor_group=ArmorGroup.HEAVY,
    )
    dodge = resolve_contact(inputs, rng=CountingRandom(0.9))
    miss = resolve_contact(inputs, rng=CountingRandom(0.999))

    assert dodge.hit is False
    assert dodge.attribution is FailureAttribution.DODGE
    assert miss.hit is False
    assert miss.attribution is FailureAttribution.MISS


def test_contact_applies_the_committed_modifier_order():
    baseline = ContactInputs(kind=ContactKind.SPELL)
    modified = ContactInputs(
        kind=ContactKind.SPELL,
        accuracy_multiplier=0.8,
        accuracy_points=0.1,
        dodge_points=0.25,
    )

    expected = ((contact_chance(baseline) * 0.8) + 0.1) * 0.75
    assert contact_chance(modified) == pytest.approx(expected)


def test_registry_covers_every_approved_modifier_category():
    classifications = set(CONTACT_MODIFIER_REGISTRY.values())
    assert classifications == set(ModifierClassification)
    known_hooks = {
        "accuracy_ring",
        "blind",
        "weapon_focus",
        "threaded_accuracy",
        "totem_surge_reliability",
        "dodge_ring",
        "evasion_skill",
        "concealment",
        "magic_dodge",
        "quickstep",
        "live_and_learn",
        "case_prediction",
        "rope_a_dope",
        "arcane_trickster",
        "tricksters_gambit",
        "retribution",
        "parry",
        "reflect",
        "resistance",
        "immunity",
        "status_contest",
    }
    assert known_hooks <= CONTACT_MODIFIER_REGISTRY.keys()
