"""Regression coverage for authored Shaman and Soulcatcher progression."""

from src.core import abilities
from src.core.classes import nature_totems, promotion_kits
from src.core.progression import ABILITY_TREES, NodeKind, ProgressionState, _apply_promotion
from src.core.save_system import PlayerDataSerializer
from tests.test_framework import TestGameState


def _player(class_name: str, level: int = 90):
    player = TestGameState.create_player(class_name=class_name, level=level)
    player.progression = ProgressionState(level=level)
    return player


def _grant(player, *talent_keys: str) -> None:
    talents = {
        node.payload["talent_key"]: node
        for tree_name in ("Shaman", "Soulcatcher")
        for node in ABILITY_TREES[tree_name].nodes
        if node.kind == NodeKind.TALENT
    }
    for talent_key in talent_keys:
        player.progression.purchased_node_ids.add(talents[talent_key].id)


def _active_totem(player, aspect: str, resonance: int = 0) -> None:
    effect = player.magic_effects["Totem"]
    effect.active = True
    effect.duration = 5
    effect.extra = {"aspect": aspect, "resonance": resonance}


def test_shaman_and_soulcatcher_use_authored_budget_and_rows():
    shaman = ABILITY_TREES["Shaman"]
    development = [node for node in shaman.nodes if node.kind != NodeKind.PROMOTION]
    promotion = next(node for node in shaman.nodes if node.kind == NodeKind.PROMOTION)
    soulcatcher = ABILITY_TREES["Soulcatcher"]

    assert len(development) == 19
    assert sum(node.cost for node in development) == 21
    assert not any(node.name == "Totem" for node in development)
    assert promotion.cost == 3
    assert promotion.payload["prerequisite_mode"] == "any"
    assert len(promotion.prerequisites) == 3
    assert len(soulcatcher.nodes) == 28
    assert sum(node.cost for node in soulcatcher.nodes) == 30
    assert 0.60 <= 20 / 30 <= 0.70
    assert max(node.position[1] for node in shaman.nodes) <= 7
    assert max(node.position[1] for node in soulcatcher.nodes) <= 6


def test_totem_is_granted_by_shaman_promotion_instead_of_purchased():
    pathfinder = TestGameState.create_player(class_name="Pathfinder", level=60)
    promotion = next(
        node
        for node in ABILITY_TREES["Pathfinder"].nodes
        if node.kind == NodeKind.PROMOTION and node.payload["target_class"] == "Shaman"
    )
    pathfinder.progression = ProgressionState(level=60)
    pathfinder.spellbook["Skills"].pop("Totem", None)

    _apply_promotion(pathfinder, promotion, {})

    assert pathfinder.cls.name == "Shaman"
    assert pathfinder.spellbook["Skills"]["Totem"].name == "Totem"


def test_bad_omens_realizes_at_three_dread_and_respects_stun_protection():
    shaman = _player("Shaman", 60)
    enemy = _player("Warrior")
    _grant(shaman, "shaman.bad-omens")

    nature_totems.add_dread(shaman, enemy, "critical hit")
    nature_totems.add_dread(shaman, enemy, "failed attack")
    message = nature_totems.add_dread(shaman, enemy, "critical hit")

    assert enemy.status_effects["Stun"].active is True
    assert enemy.status_effects["Stun"].duration == 2
    assert "omen comes true" in message
    assert nature_totems.dread_stacks(shaman, enemy) == 0


def test_spirit_animal_uses_selected_form_and_spirit_claw_synergy():
    shaman = _player("Shaman", 60)
    enemy = _player("Warrior")
    shaman.spirit_animal = "Turtle"
    before_mana = shaman.mana.current

    blessing = abilities.SpiritAnimal().use(shaman)
    strike = abilities.SpiritClaw().use(shaman, enemy)

    assert blessing.hit is True
    assert shaman.mana.current == before_mana - 14
    assert shaman.stat_effects["Defense"].active is True
    assert strike.hit is not None


def test_spirit_animal_selection_round_trips_through_save_data():
    shaman = _player("Shaman", 60)
    shaman.spirit_animal = "Snake"

    restored = PlayerDataSerializer.deserialize(
        PlayerDataSerializer.serialize(shaman),
        skip_tiles=True,
    )

    assert restored.spirit_animal == "Snake"


def test_resonant_ward_spends_all_stacks_for_both_defenses():
    shaman = _player("Shaman", 60)
    _active_totem(shaman, "Earth", resonance=3)

    result = abilities.ResonantWard().use(shaman)

    assert result.hit is True
    assert promotion_kits.totem_resonance(shaman) == 0
    assert shaman.stat_effects["Defense"].extra == 18
    assert shaman.stat_effects["Magic Defense"].extra == 18


def test_soulcatcher_deep_resonance_and_harvest_masteries_are_live():
    soulcatcher = _player("Soulcatcher")
    _grant(
        soulcatcher,
        "soulcatcher.deep-resonance",
        "soulcatcher.varied-harvest",
        "soulcatcher.essence-shell",
        "soulcatcher.perfect-vessel",
        "soulcatcher.spirit-warrior",
    )
    _active_totem(soulcatcher, "Soul")
    from src.core.classes import class_rings

    class_rings.ensure_state(soulcatcher)["data"]["Soulcatcher"]["harvested_types"] = [
        "Animal", "Construct", "Dragon", "Fiend", "Humanoid", "Slime", "Undead"
    ]

    assert promotion_kits.cap_for(soulcatcher, "totem_resonance") == 4
    assert nature_totems.passive_rating_bonus(soulcatcher, "magic") == 10
    assert nature_totems.passive_rating_bonus(soulcatcher, "armor") == 10
    assert nature_totems.passive_rating_bonus(soulcatcher, "weapon") == 20
    assert nature_totems.passive_rating_bonus(soulcatcher, "magic def") == 10
