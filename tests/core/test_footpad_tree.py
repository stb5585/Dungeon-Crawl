"""Regression coverage for the authored Footpad tree and its new mechanics."""

from types import SimpleNamespace

from src.core import abilities, enemies, items
from src.core.classes import footpad
from src.core.progression import ABILITY_TREES, NodeKind
from tests.test_framework import TestGameState


EXPECTED_COLUMNS = (
    ("Stumble Upon", "Steal", "Lockpick", "Avoid Traps", "Do-over", "Serendipity"),
    ("Disarm", "Pocket Sand", "Smoke Screen", None, "Aggressive Pursuit", "Sleeping Powder"),
    ("Dual Wield", "Backstab", "Cripple", "Kidney Punch", "Double Strike", "Obscuration"),
    ("Duelist", "Incantation Comprehension", "+10 Magic", "Mana Depletion", "Imbue Weapon", "Disruption"),
    ("Quickstep", None, "Parry", "Retort", "Evasive Guard", "Mystical Evasion"),
    ("Piercing Strike", "Detect Animal", "Inspect", "Detect Humanoid", "+10 Magic Defense", "Detect Slime"),
)
EXPECTED_LEVELS = (
    (None, 5, 10, 15, 20, 25),
    (None, 5, 10, None, 20, 25),
    (None, 5, 10, 15, 20, 25),
    (None, 5, None, 15, 20, 25),
    (None, None, 10, 15, 20, 25),
    (None, 5, 10, 15, None, 25),
)


def _player():
    return TestGameState.create_player(class_name="Footpad", level=30)


def test_footpad_tree_matches_the_six_authored_columns_and_gates():
    development = [
        node for node in ABILITY_TREES["Footpad"].nodes
        if node.kind != NodeKind.PROMOTION
    ]
    by_position = {node.position: node for node in development}

    assert len(development) == 34
    for column, expected_names in enumerate(EXPECTED_COLUMNS):
        assert tuple(
            by_position[(column, row)].name if (column, row) in by_position else None
            for row in range(6)
        ) == expected_names
        assert tuple(
            by_position[(column, row)].payload.get("level_requirement")
            if (column, row) in by_position else None
            for row in range(6)
        ) == EXPECTED_LEVELS[column]


def test_footpad_promotions_join_identity_and_shared_tracks():
    by_name = {node.name: node for node in ABILITY_TREES["Footpad"].nodes}

    assert by_name["Promote: Thief"].position == (0.5, 7)
    assert by_name["Promote: Assassin"].position == (1.5, 7)
    assert by_name["Promote: Spell Stealer"].position == (3.5, 7)
    assert by_name["Promote: Inquisitor"].position == (4.5, 7)
    assert by_name["Sleeping Powder"].id in by_name["Promote: Thief"].prerequisites
    assert by_name["Sleeping Powder"].id in by_name["Promote: Assassin"].prerequisites
    assert by_name["Mystical Evasion"].id in (
        by_name["Promote: Spell Stealer"].prerequisites
    )
    assert by_name["Mystical Evasion"].id in by_name["Promote: Inquisitor"].prerequisites


def test_obscuration_requires_the_reusable_magic_shop_censer():
    player = _player()
    player.mana.current = 100
    skill = abilities.Obscuration()

    assert "requires a Censer" in skill.use(player).message
    censer = items.CenserOfChokingAsh()
    player.modify_inventory(censer)
    result = skill.use(player)

    assert player.obscuration_steps == footpad.OBSCURATION_STEPS
    assert player.inventory[censer.name][0] is censer
    assert footpad.encounter_rate_multiplier(player) == 0.5
    assert "50 steps" in result.message
    footpad.tick_exploration(player, 50)
    assert footpad.encounter_rate_multiplier(player) == 1.0


def test_avoid_traps_can_avoid_or_halve_a_triggered_effect():
    player = _player()
    player.spellbook["Skills"]["Avoid Traps"] = abilities.AvoidTraps()

    avoided, message = footpad.trap_damage(
        player,
        20,
        rng=SimpleNamespace(random=lambda: 0.0),
    )
    halved, half_message = footpad.trap_damage(
        player,
        20,
        rng=SimpleNamespace(random=lambda: 1.0),
    )

    assert avoided == 0
    assert "avoids" in message
    assert halved == 10
    assert "halves" in half_message


def test_mana_depletion_only_drains_through_the_basic_attack_hook():
    player = _player()
    target = enemies.Goblin()
    target.mana.current = 20
    player.spellbook["Skills"]["Mana Depletion"] = abilities.ManaDepletion()

    assert footpad.drain_basic_attack_mana(player, target, 50) == 5
    assert target.mana.current == 15


def test_footpad_passive_multipliers_are_scoped_to_their_effects():
    player = _player()
    assert footpad.loot_drop_multiplier(player) == 1.0
    assert footpad.scroll_effectiveness_multiplier(player) == 1.0
    assert footpad.spell_dodge_bonus(player) == 0.0

    player.spellbook["Skills"].update({
        "Serendipity": abilities.Serendipity(),
        "Incantation Comprehension": abilities.IncantationComprehension(),
        "Mystical Evasion": abilities.MysticalEvasion(),
    })

    assert footpad.loot_drop_multiplier(player) == 1.25
    assert footpad.scroll_effectiveness_multiplier(player) == 1.25
    assert footpad.spell_dodge_bonus(player) == 0.15


def test_do_over_is_limited_to_one_successful_proc_per_battle():
    player = _player()
    player.spellbook["Skills"]["Do-over"] = abilities.DoOver()
    footpad.start_combat(player)
    always_proc = SimpleNamespace(random=lambda: 0.0)

    assert footpad.try_do_over(player, rng=always_proc) is True
    assert footpad.try_do_over(player, rng=always_proc) is False
    footpad.start_combat(player)
    assert footpad.try_do_over(player, rng=always_proc) is True
