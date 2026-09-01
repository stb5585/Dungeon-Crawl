"""Regression coverage for the authored Pathfinder base tree."""

from types import SimpleNamespace

import pytest

from src.core import abilities, enemies
from src.core.classes import pathfinder
from src.core.combat.actor_cycle import initiative_rating
from src.core.progression import ABILITY_TREES, NodeKind
from tests.test_framework import TestGameState


EXPECTED_COLUMNS = (
    ("Poison Dart", "Regrowth", "Ray of Moonlight", "Nullify Poison", "Thorny Vine", "Poison Strike"),
    ("Natural Attunement", "Razor Talons", "Call Animal", None, "Detect Animal", "Creature Comforts"),
    ("Stumble Upon", "Zephyrstrike", "Cautious Assault", "Honed Attack", "Unnatural Purge", "Bounce Back"),
    ("Piercing Strike", "Quickstep", "+10 Attack", None, "Parry", "True Strike"),
    ("Spirit Strike", "Conversion", "+25 MP", "Hydration", "Very Superstitious", "Primal Trance"),
    ("Tremor", "Water Jet", "Gust", "Scorch", "Fundamental Harmony", "Detect Elemental"),
    ("Intensify Elements", "Chronology", "+10 Magic", "Blinding Fog", "Geomancy", "Control Z"),
)
EXPECTED_LEVELS = (None, 5, 10, 15, 20, 25)


def _player():
    player = TestGameState.create_player(class_name="Pathfinder", level=30)
    player.mana.current = player.mana.max = 200
    return player


def test_pathfinder_tree_matches_requested_columns_gaps_and_gates():
    tree = ABILITY_TREES["Pathfinder"]
    development = [node for node in tree.nodes if node.kind != NodeKind.PROMOTION]
    by_position = {node.position: node for node in development}
    promotions = {
        node.payload["target_class"]: node
        for node in tree.nodes
        if node.kind == NodeKind.PROMOTION
    }

    assert len(development) == 40
    assert tree.branches == (
        "Druid", "Naturalism", "Ranger", "Melee", "Shaman", "Elemental", "Diviner",
    )
    for column, names in enumerate(EXPECTED_COLUMNS):
        for row, name in enumerate(names):
            node = by_position.get((column, row))
            assert (node.name if node else None) == name
            if node is not None and node.kind not in {NodeKind.RATING, NodeKind.MANA}:
                assert node.payload.get("level_requirement") == EXPECTED_LEVELS[row]
    assert promotions["Druid"].position == (0.5, 6)
    assert promotions["Ranger"].position == (2, 6)
    assert promotions["Shaman"].position == (4, 6)
    assert promotions["Diviner"].position == (5.5, 6)


def test_nature_is_a_resistance_type_and_spells_can_have_multiple_types():
    player = _player()
    target = enemies.Goblin()
    target.resistance["Nature"] = 1.0
    poison_dart = abilities.PoisonDart()

    _message, damage = pathfinder.spell_damage(
        player,
        target,
        abilities.RayOfMoonlight(),
        damage_type="Nature",
        damage_modifier=1.0,
        rng=SimpleNamespace(random=lambda: 1.0),
    )

    assert damage == 0
    assert pathfinder.ability_damage_types(poison_dart) >= {"Nature", "Poison"}


def test_ray_of_moonlight_restores_and_suppresses_enemy_shapeshifting():
    player = _player()
    target = enemies.Quasit()
    original_name = target.name
    target._shapeshift_original_state = {
        "cls": target.cls,
        "stats": target.stats,
        "equipment": target.equipment,
        "spellbook": target.spellbook,
        "resistance": target.resistance,
        "flying": target.flying,
        "invisible": target.invisible,
        "sight": target.sight,
        "name": target.name,
        "picture": target.picture,
    }
    target.name = "Direwolf"
    target.status_effects["Shapeshifted"].active = True

    result = abilities.RayOfMoonlight().cast(
        player,
        target,
        rng=SimpleNamespace(random=lambda: 1.0),
    )

    assert result.damage > 0
    assert target.name == original_name
    assert target.shapeshift_suppressed is True
    assert target.status_effects["Shapeshifted"].active is False


def test_nullify_poison_and_thorny_vine_cover_nature_control():
    player = _player()
    target = enemies.Goblin()
    poison = target.status_effects["Poison"]
    poison.active = True
    poison.duration = 3
    poison.extra = 4

    cured = abilities.NullifyPoison().cast(player, target)
    vine = abilities.ThornyVine().cast(player, target)
    before = target.health.current
    tick = pathfinder.tick_thorny_vine(
        target,
        rng=SimpleNamespace(randint=lambda _low, _high: 1),
    )

    assert poison.active is False
    assert "cured" in cured.message
    assert "coils" in vine.message
    assert target.health.current < before
    assert "Nature damage" in tick


def test_poison_strike_is_a_main_hand_nature_spell_with_poison_damage(monkeypatch):
    player = _player()
    target = enemies.Goblin()
    calls = []
    original = player.weapon_damage

    def tracked_weapon_damage(defender, **kwargs):
        calls.append(kwargs)
        return original(defender, **kwargs)

    monkeypatch.setattr(player, "weapon_damage", tracked_weapon_damage)
    rolls = iter((1.0, 0.0))
    result = abilities.PoisonStrike().cast(
        player,
        target,
        rng=SimpleNamespace(random=lambda: next(rolls)),
    )

    assert abilities.PoisonStrike().typ == "Spell"
    assert result.damage > 0
    assert calls[0]["use_offhand"] is False
    assert target.status_effects["Poison"].active is True


def test_shared_passives_modify_melee_elemental_and_initiative_rules():
    player = _player()
    player.spellbook["Skills"].update({
        "Razor Talons": abilities.RazorTalons(),
        "Conversion": abilities.Conversion(),
        "Fundamental Harmony": abilities.FundamentalHarmony(),
        "Intensify Elements": abilities.IntensifyElements(),
        "Chronology": abilities.Chronology(),
    })
    spell = abilities.Scorch()
    baseline_initiative = (
        player.check_mod("speed", enemy=enemies.Goblin())
        + player.check_mod("luck", enemy=enemies.Goblin(), luck_factor=10)
    )

    pathfinder.record_elemental_spell_damage(player, "Fire")
    pathfinder.record_elemental_damage_taken(player, "Fire")

    assert pathfinder.melee_damage_multiplier(player) == pytest.approx(1.10)
    assert pathfinder.consume_conversion(player) == pytest.approx(0.50)
    assert pathfinder.spell_output_multiplier(player, spell) == pytest.approx(1.62)
    assert initiative_rating(player, enemies.Goblin()) == pytest.approx(
        max(0, baseline_initiative + pathfinder.chronology_initiative_bonus(player))
    )


def test_creature_comforts_and_call_animal_use_existing_encounter_companion_system():
    player = _player()
    player.location_z = 0
    called = abilities.CallAnimal().cast_out(player)
    animal = enemies.Panther()
    member = SimpleNamespace(enemy=animal)
    engine = SimpleNamespace(encounter=SimpleNamespace(living_members=[member]))
    pacified = pathfinder.pacify_combat_animals(player, engine, 0)

    assert player.transient_companion is not None
    assert "answers" in called
    assert animal.health.current == 0
    assert animal.no_victory_rewards is True
    assert "1 animal" in pacified


def test_very_superstitious_barrier_and_control_z_restore_damage_state():
    player = _player()
    player.spellbook["Skills"]["Very Superstitious"] = abilities.VerySuperstitious()
    barrier = pathfinder.activate_superstitious_barrier(
        player,
        "Fear",
        3,
        rng=SimpleNamespace(random=lambda: 0.0),
    )
    remaining, absorbed = pathfinder.absorb_superstitious_barrier(player, 10)
    original_health = player.health.current
    pathfinder.record_incoming_action_start(player)
    player.health.current -= 20
    player.status_effects["Fear"].active = True
    pathfinder.record_incoming_action_end(player, original_health)
    rewound = abilities.ControlZ().cast(player)

    assert remaining == 0
    assert "barrier" in barrier
    assert "absorbs 10" in absorbed
    assert player.health.current == original_health
    assert player.status_effects["Fear"].active is False
    assert "Time rewinds" in rewound


def test_primal_trance_charges_then_escalates_elemental_casts(monkeypatch):
    player = _player()
    target = TestGameState.create_player(class_name="Warrior", level=30)
    target.health.current = target.health.max = 1_000
    trance = abilities.PrimalTrance()
    ranks = []

    def record_cast(_player, _target, rank, **_kwargs):
        ranks.append(rank)
        return f"elemental cast {rank}\n"

    monkeypatch.setattr(pathfinder, "primal_trance_cast", record_cast)

    started = trance.use(player, target)
    casts = [trance.use(player, target) for _ in range(4)]

    assert "begins charging" in started
    assert ranks == [1, 2, 3, 4]
    assert all("elemental cast" in message for message in casts)
    assert player._primal_trance_active is False
    assert player.physical_effects["Prone"].active is False


def test_geomancy_reports_quest_targets_and_points_to_useful_tiles():
    player = _player()
    target = enemies.Goblin()
    player.quest_dict["Bounty"][target.name] = [{"num": 1}, 0, False]
    player.location_x = player.location_y = player.location_z = 0
    player.world_dict = {
        (0, 0, 0): SimpleNamespace(visited=True, enter=True),
        (2, 0, 0): SimpleNamespace(visited=False, enter=True),
    }

    combat = pathfinder.geomancy_combat(player, target)
    exploration = pathfinder.geomancy_exploration(player)

    assert "useful quest or bounty" in combat
    assert "east" in exploration
    assert player._geomancy_target == (2, 0, 0)
