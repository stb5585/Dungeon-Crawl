"""Regression coverage for the authored Healer base tree."""

from types import SimpleNamespace

import pytest

from src.core import abilities, enemies
from src.core.classes import healer
from src.core.progression import ABILITY_TREES, NodeKind
from tests.test_framework import TestGameState

EXPECTED_COLUMNS = (
    ("Imbue Weapon", "Goad", "Lullaby", "Beginner's Luck", "Mental Shard", "Cacophany"),
    ("Bless", "Tranquility", "Courage", "Vision", "+10 Magic Defense", "Tutelary"),
    ("Smite", "+10 Defense", "Turn Undead", "Detect Undead", "Divine Protection", "Shield Slam"),
    ("Heal", "+25 HP", "Regen", "+25 MP", "Safeguarding", "Heal II"),
    ("Holy", "+10 Magic", "Flash Blindness", "Defensive Regen", "Incite Panic", "Resist Shadow"),
    (
        "Zen Accuracy",
        "Staff Proficiency",
        "+10 Attack",
        "Delayed Reaction",
        "Leg Sweep",
        "Meditation",
    ),
)
EXPECTED_LEVELS = (
    (None, 5, 10, 15, 20, 25),
    (None, 5, 10, 15, None, 25),
    (None, None, 10, 15, 20, 25),
    (None, None, 10, None, 20, 25),
    (None, None, 10, 15, 20, 25),
    (None, 5, None, 15, 20, 25),
)


def _player():
    player = TestGameState.create_player(class_name="Healer", level=30)
    player.mana.current = player.mana.max = 200
    return player


def test_healer_tree_matches_requested_columns_gates_and_promotion_joins():
    tree = ABILITY_TREES["Healer"]
    development = [node for node in tree.nodes if node.kind != NodeKind.PROMOTION]
    by_position = {node.position: node for node in development}
    by_name = {node.name: node for node in tree.nodes}

    assert len(development) == 36
    for column, names in enumerate(EXPECTED_COLUMNS):
        assert tuple(by_position[(column, row)].name for row in range(6)) == names
    for column in range(6):
        assert (
            tuple(by_position[(column, row)].payload.get("level_requirement") for row in range(6))
            == EXPECTED_LEVELS[column]
        )
    assert by_name["Promote: Bard"].position == (0.5, 7)
    assert by_name["Promote: Cleric"].position == (2.5, 7)
    assert by_name["Promote: Priest"].position == (3.5, 7)
    assert by_name["Promote: Monk"].position == (5, 7)
    assert by_name["Tutelary"].id in by_name["Promote: Bard"].prerequisites
    assert by_name["Heal II"].id in by_name["Promote: Cleric"].prerequisites
    assert by_name["Heal II"].id in by_name["Promote: Priest"].prerequisites


def test_lullaby_and_mental_shard_apply_and_expire_their_control():
    player = _player()
    target = enemies.Goblin()
    lullaby = abilities.Lullaby().use(
        player,
        target,
        rng=SimpleNamespace(random=lambda: 0.0),
    )
    original_intelligence = target.stats.intel
    shard = abilities.MentalShard().use(player, target)

    assert target.status_effects["Sleep"].active is True
    assert "falls asleep" in lullaby.message
    assert shard.damage > 0
    assert target.stats.intel < original_intelligence
    healer.tick_combat_state(target)
    healer.tick_combat_state(target)
    healer.tick_combat_state(target)
    assert target.stats.intel == original_intelligence


def test_beginners_luck_improves_luck_for_the_remainder_of_combat():
    player = _player()
    before = player.check_mod("luck", luck_factor=10)

    abilities.BeginnersLuck().use(player)

    assert player.check_mod("luck", luck_factor=10) > before
    healer.start_combat(player)
    assert player.check_mod("luck", luck_factor=10) == before


def test_support_spells_apply_existing_and_new_protections():
    player = _player()
    abilities.Tranquility().cast(player)
    courage = abilities.Courage().cast(player)
    abilities.Vision().cast(player)

    assert player.has_status_protection("Berserk") is True
    assert player.has_status_protection("Fear") is True
    assert player.temporary_health["amount"] == int(player.health.max * 0.15)
    assert player.sight is True
    assert "temporary health" in courage.message
    healer.tick_exploration(player, 50)
    player._vision_turns = 0
    healer.tick_exploration(player, 0)
    assert player.sight is False


def test_safeguarding_and_tutelary_reduce_incoming_damage():
    player = _player()
    player.spellbook["Skills"]["Safeguarding"] = abilities.Safeguarding()
    healer.apply_safeguarding(player, player, "Heal")

    guarded, guard_message = healer.reduce_incoming_damage(player, 40, melee=True)
    player._tutelary_turns = 3
    protected, spirit_message = healer.reduce_incoming_damage(
        player,
        40,
        melee=False,
        rng=SimpleNamespace(random=lambda: 0.0),
    )

    assert guarded == 30
    assert "Safeguarding" in guard_message
    assert protected == 20
    assert "tutelary spirit" in spirit_message


def test_flash_blindness_and_incite_panic_affect_nearby_enemies():
    player = _player()
    player.spellbook["Skills"]["Flash Blindness"] = abilities.FlashBlindness()
    targets = [enemies.Goblin(), enemies.Goblin()]
    message = healer.flash_blindness(
        player,
        targets,
        rng=SimpleNamespace(random=lambda: 0.0),
    )
    engine = SimpleNamespace(
        player=player,
        encounter=SimpleNamespace(
            living_members=[SimpleNamespace(enemy=target) for target in targets],
        ),
    )
    panic = abilities.IncitePanic().cast(
        player,
        targets[0],
        battle_engine=engine,
        rng=SimpleNamespace(random=lambda: 0.0),
    )

    assert all(target.status_effects["Blind"].active for target in targets)
    assert all(target.status_effects["Fear"].active for target in targets)
    assert "blinds 2" in message
    assert "2 target" in panic.message


def test_cacophany_resolves_once_across_an_all_enemy_group():
    player = _player()
    targets = [enemies.Goblin(), enemies.Goblin()]
    members = [SimpleNamespace(enemy=target) for target in targets]
    engine = SimpleNamespace(
        player=player,
        current_actor_id="player",
        encounter=SimpleNamespace(living_members=members),
    )
    mana_before = player.mana.current

    group = abilities.Cacophany().use_group(
        player,
        [(f"enemy-{index}", target) for index, target in enumerate(targets)],
        battle_engine=engine,
        rng=SimpleNamespace(randint=lambda _low, _high: 20),
    )

    assert player.mana.current == mana_before - 10
    assert len(group.results) == 2
    assert all(result.damage > 0 for result in group.results)
    assert group.message.count("psychic scream") == 1


def test_delayed_reaction_and_meditation_defer_then_release_damage():
    player = _player()
    player.spellbook["Skills"]["Delayed Reaction"] = abilities.DelayedReaction()
    immediate, message = healer.delay_critical_damage(
        player,
        30,
        rng=SimpleNamespace(random=lambda: 0.0),
    )

    assert immediate == 0
    assert player._delayed_reaction_damage == [10, 10, 10]
    assert "spreads" in message

    abilities.Meditation().use(player)
    absorbed, _message = healer.reduce_incoming_damage(player, 12, melee=False)
    healer.tick_combat_state(player)
    healer.tick_combat_state(player)
    assert absorbed == 0
    assert healer.meditation_release(player) == 24


def test_zen_accuracy_and_staff_proficiency_stack_for_staves():
    player = _player()
    player.spellbook["Skills"].update(
        {
            "Zen Accuracy": abilities.ZenAccuracy(),
            "Staff Proficiency": abilities.StaffProficiency(),
        }
    )

    assert healer.accuracy_bonus(player, "Staff") == pytest.approx(0.15)
    assert healer.staff_damage_multiplier(player, "Staff") == pytest.approx(1.10)
