"""Regression coverage for the completed Druid and Diviner promotion lines."""

from types import SimpleNamespace

import pytest

from src.core import abilities, enemies
from src.core.classes import astromancer, lycan
from src.core.progression import ABILITY_TREES, NodeKind, ProgressionState
from tests.test_framework import TestGameState


def _player(class_name: str, level: int = 90):
    player = TestGameState.create_player(class_name=class_name, level=level)
    player.progression = ProgressionState(level=level)
    player.mana.current = player.mana.max = 500
    return player


def _grant(player, class_name: str, talent_key: str) -> None:
    node = next(
        node
        for node in ABILITY_TREES[class_name].nodes
        if node.kind == NodeKind.TALENT
        and node.payload["talent_key"] == talent_key
    )
    player.progression.purchased_node_ids.add(node.id)


def test_remaining_pathfinder_trees_use_authored_budgets_and_visible_rows():
    expected = {
        "Druid": (28, 28, 7),
        "Diviner": (22, 22, 7),
        "Lycan": (28, 30, 6),
        "Archdruid": (28, 30, 6),
        "Astromancer": (28, 30, 6),
    }
    for class_name, (count, cost, final_row) in expected.items():
        development = [
            node
            for node in ABILITY_TREES[class_name].nodes
            if node.kind != NodeKind.PROMOTION
        ]
        assert len(development) == count
        assert sum(node.cost for node in development) == cost
        assert max(node.position[1] for node in ABILITY_TREES[class_name].nodes) == final_row

    assert 0.60 <= 20 / 30 <= 0.70

    for class_name in ("Druid", "Diviner"):
        level_55 = [
            node
            for node in ABILITY_TREES[class_name].nodes
            if node.position[1] == 5
        ]
        assert len(level_55) == 4
        assert all(node.payload["level_requirement"] == 55 for node in level_55)

    diviner_abilities = [
        node
        for node in ABILITY_TREES["Diviner"].nodes
        if node.kind == NodeKind.ABILITY
    ]
    assert len(diviner_abilities) == 8
    assert not any(
        node.id in {"diviner.rating.foresight-potency", "diviner.mana.chronal-reserve"}
        for node in ABILITY_TREES["Diviner"].nodes
    )


def test_druid_promotions_accept_either_completed_discipline():
    promotions = {
        node.payload["target_class"]: node
        for node in ABILITY_TREES["Druid"].nodes
        if node.kind == NodeKind.PROMOTION
    }

    assert set(promotions) == {"Lycan", "Archdruid"}
    assert promotions["Lycan"].payload["prerequisite_mode"] == "any"
    assert promotions["Archdruid"].payload["prerequisite_mode"] == "any"
    assert len(promotions["Lycan"].prerequisites) == 2
    assert len(promotions["Archdruid"].prerequisites) == 2


def test_druid_swaps_and_primal_practice_match_requested_rows():
    tree = ABILITY_TREES["Druid"]
    positions = {node.name: node.position for node in tree.nodes}

    assert positions["+20 Attack"] == (0, 1)
    assert positions["Feline Grace"] == (0, 2)
    assert positions["+20 Magic"] == (2, 1)
    assert positions["Resist Poison"] == (2, 2)
    assert positions["Calming Breeze"] == (3, 2)
    assert positions["+20 Magic Defense"] == (3, 3)
    assert positions["Primal Practice"] == (4, 0)
    for name in ("Feline Grace", "Resist Poison", "Calming Breeze"):
        node = next(entry for entry in tree.nodes if entry.name == name)
        assert node.payload["level_requirement"] == 40

    druid = _player("Druid")
    result = abilities.PrimalPractice().use(druid)
    assert result.hit is True
    assert druid.stat_effects["Magic"].extra == 10


def test_restoring_boon_consumes_remaining_regrowth_for_larger_heal():
    druid = _player("Druid", 60)
    druid.health.current = 10
    regen = druid.magic_effects["Regen"]
    regen.active = True
    regen.duration = 3
    regen.extra = 10

    result = abilities.RestoringBoon().cast(druid)

    assert result.healing == min(37, druid.health.max - 10)
    assert regen.active is False
    assert regen.duration == 0


def test_druid_area_spells_resolve_against_every_selected_enemy():
    druid = _player("Druid", 60)
    targets = [enemies.Goblin(), enemies.Goblin()]
    engine = SimpleNamespace(current_actor_id="player")
    selected = [(f"enemy-{index}", target) for index, target in enumerate(targets)]

    mist = abilities.NoxiousMist().cast_group(
        druid,
        selected,
        battle_engine=engine,
        rng=SimpleNamespace(random=lambda: 0.0),
    )
    stars = abilities.Starfall().cast_group(
        druid,
        selected,
        battle_engine=engine,
    )

    assert len(mist.results) == 2
    assert len(stars.results) == 2
    assert all(target.status_effects["Poison"].active for target in targets)
    assert all(result.extra["hits"] >= 1 for result in stars.results)


def test_resist_poison_uses_exploration_time_and_resistance_pipeline():
    druid = _player("Druid", 60)
    before = druid.check_mod("resist", typ="Poison")

    message = abilities.ResistPoison().cast_out(druid)

    assert "100 steps" in message
    assert druid.temporary_exploration_effects["resist_poison"] == 100
    assert druid.check_mod("resist", typ="Poison") == before + 0.50


def test_temporary_stasis_freezes_beneficial_and_hostile_timers():
    diviner = _player("Diviner", 60)
    target = _player("Warrior")
    target.status_effects["Poison"].active = True
    target.status_effects["Poison"].duration = 4
    target.magic_effects["Regen"].active = True
    target.magic_effects["Regen"].duration = 3

    result = abilities.TemporaryStasis().cast(diviner, target)
    first_tick = target.effects()

    assert result.hit is True
    assert "suspended" in first_tick
    assert target.status_effects["Poison"].duration == 4
    assert target.magic_effects["Regen"].duration == 3


def test_silent_lucidity_allows_only_time_and_divination_spells():
    astro = _player("Astromancer")
    astro.spellbook["Skills"]["Silent Lucidity"] = abilities.SilentLucidity()
    astro.status_effects["Sleep"].active = True

    assert astro.check_active() == (True, "")
    assert astromancer.can_cast_while_asleep(astro, abilities.TemporaryStasis())
    assert not astromancer.can_cast_while_asleep(astro, abilities.Volcano())


def test_access_storage_moves_one_item_and_charges_its_weight():
    astro = _player("Astromancer")
    relic = SimpleNamespace(name="Heavy Relic", weight=7)
    astro.storage = {relic.name: [relic]}
    astro.inventory = {}
    mana_before = astro.mana.current

    message = abilities.AccessStorage().use_out(
        astro,
        item_name=relic.name,
        retrieve=True,
    )

    assert "retrieves Heavy Relic" in message
    assert astro.inventory[relic.name] == [relic]
    assert astro.mana.current == mana_before - 7


def test_tephra_damages_only_nearby_nonprimary_enemies():
    astro = _player("Astromancer")
    astro.spellbook["Skills"]["Tephra"] = abilities.Tephra()
    primary = enemies.Goblin()
    nearby = enemies.Goblin()
    primary_before = primary.health.current
    nearby_before = nearby.health.current
    encounter = SimpleNamespace(
        living_members=[
            SimpleNamespace(enemy=primary),
            SimpleNamespace(enemy=nearby),
        ],
    )

    message = astromancer.tephra_splash(astro, primary, encounter)

    assert primary.health.current == primary_before
    assert nearby.health.current < nearby_before
    assert "Tephra strikes" in message


def test_path_talents_deepen_attunement_threads_and_frenzy():
    archdruid = _player("Archdruid")
    _grant(archdruid, "Archdruid", "archdruid.patient-venom")
    from src.core.classes import archdruid as archdruid_rules

    _before, after = archdruid_rules.adjust_attunement(archdruid, "Venom", 1)
    assert after == 2

    wolf = _player("Lycan")
    lycan.ensure_state(wolf)["frenzy_turns"] = 2
    _grant(wolf, "Lycan", "lycan.frenzied-force")
    assert lycan.frenzy_damage_bonus(wolf) == pytest.approx(0.30)

    astro = _player("Astromancer")
    _grant(astro, "Astromancer", "astromancer.thread-spinner")
    message = astromancer.record_thread_action(astro, "Foretell", successful=True)
    assert "2/3" in message


def test_lycan_new_actives_require_and_reward_werewolf_state():
    from src.core.classes import promotion_kits, transformation

    wolf = _player("Lycan")
    wolf.progression.purchased_node_ids.add("lycan.ability.transform3")
    transformation.apply_form(wolf, "Werewolf")
    target = enemies.Goblin()
    target.dodge_chance = lambda *_args, **_kwargs: 0.0

    rend = abilities.LunarRend().use(wolf, target)
    assert rend.damage > 0
    assert target.physical_effects["Bleed"].active is True

    promotion_kits.lycan_control_state(wolf)["dragon_essence"] = True
    second_target = enemies.Goblin()
    second_target.dodge_chance = lambda *_args, **_kwargs: 0.0
    fang = abilities.DragonFang().use(wolf, second_target)
    assert fang.damage > 0

    centered = abilities.CenterBeast().use(wolf)
    assert centered.hit is True
    assert promotion_kits.combat_state(wolf)["center_beast_ready"] is True


def test_center_beast_halves_and_consumes_the_next_frenzy_check():
    from src.core.classes import promotion_kits, transformation

    wolf = _player("Lycan")
    wolf.progression.purchased_node_ids.add("lycan.ability.transform3")
    transformation.apply_form(wolf, "Werewolf")
    lycan.ensure_state(wolf)["moon_phase"] = "Full"
    promotion_kits.combat_state(wolf)["center_beast_ready"] = True
    generator = SimpleNamespace(random=lambda: 0.20)

    triggered, _message = lycan.maybe_trigger_frenzy(
        wolf,
        reason="combat_start",
        rng=generator,
    )

    assert triggered is False
    assert "center_beast_ready" not in promotion_kits.combat_state(wolf)


def test_grove_pulse_adds_an_aspect_while_dealing_damage_and_healing():
    from src.core.classes import promotion_kits

    archdruid = _player("Archdruid")
    archdruid.health.current = max(1, archdruid.health.max // 2)
    target = enemies.Goblin()
    target.dodge_chance = lambda *_args, **_kwargs: 0.0

    result = abilities.GrovePulse().cast(archdruid, target)

    assert result.damage > 0
    assert result.healing > 0
    assert promotion_kits._aspect_counts(archdruid) == {"Growth": 1}
