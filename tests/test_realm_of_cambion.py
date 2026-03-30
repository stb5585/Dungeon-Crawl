import random
from types import SimpleNamespace

from src.core.character import Combat, Level, Resource, Stats
from src.core import map_tiles
from src.core.player import Player, REALM_OF_CAMBION_LEVEL


def _build_player():
    player = Player(
        4,
        9,
        3,
        level=Level(),
        health=Resource(20, 20),
        mana=Resource(10, 10),
        stats=Stats(10, 10, 10, 10, 10, 10),
        combat=Combat(attack=10, defense=10, magic=5, magic_def=5),
        gold=100,
        resistance={},
    )
    player.load_tiles()
    return player


def test_realm_of_cambion_map_loads_as_side_area():
    player = _build_player()

    assert type(player.world_dict[(1, 28, REALM_OF_CAMBION_LEVEL)]).__name__ == "EmptyCavePath"
    assert type(player.world_dict[(5, 28, REALM_OF_CAMBION_LEVEL)]).__name__ == "Portal"
    assert type(player.world_dict[(11, 18, REALM_OF_CAMBION_LEVEL)]).__name__ == "Rotator"
    assert type(player.world_dict[(22, 2, REALM_OF_CAMBION_LEVEL)]).__name__ == "MerzhinBossRoom"


def test_portal_uses_cambion_pair_mapping():
    player = _build_player()
    game = SimpleNamespace(player_char=player)

    map_tiles.enter_realm_of_cambion(player)
    player.location_x = 5
    player.location_y = 28
    portal = player.world_dict[(5, 28, REALM_OF_CAMBION_LEVEL)]
    portal.modify_player(game)

    assert (player.location_x, player.location_y, player.location_z) == (17, 1, REALM_OF_CAMBION_LEVEL)
    assert player.facing == "east"


def test_rotator_pushes_to_a_walkable_neighbor():
    player = _build_player()
    game = SimpleNamespace(player_char=player)
    rotator = player.world_dict[(11, 18, REALM_OF_CAMBION_LEVEL)]

    player.location_x = 11
    player.location_y = 18
    player.location_z = REALM_OF_CAMBION_LEVEL
    player.previous_location = (10, 18, REALM_OF_CAMBION_LEVEL)

    random.seed(0)
    rotator.modify_player(game)

    assert (player.location_x, player.location_y, player.location_z) in {
        (11, 17, REALM_OF_CAMBION_LEVEL),
        (12, 18, REALM_OF_CAMBION_LEVEL),
        (11, 19, REALM_OF_CAMBION_LEVEL),
    }
    assert (player.location_x, player.location_y, player.location_z) != (10, 18, REALM_OF_CAMBION_LEVEL)


def test_anti_magic_switch_disables_field_with_correct_code():
    player = _build_player()
    game = SimpleNamespace(player_char=player)

    map_tiles.enter_realm_of_cambion(player)
    switch = player.world_dict[(12, 28, REALM_OF_CAMBION_LEVEL)]
    assert map_tiles.cambion_anti_magic_active(player) is True

    result = switch.attempt_disable(game, "2749")

    assert result is True
    assert map_tiles.cambion_anti_magic_active(player) is False
    assert player.anti_magic_active is False


def test_anti_magic_switch_wrong_code_triggers_alarm_combat():
    player = _build_player()
    game = SimpleNamespace(player_char=player)

    map_tiles.enter_realm_of_cambion(player)
    switch = player.world_dict[(12, 28, REALM_OF_CAMBION_LEVEL)]

    result = switch.attempt_disable(game, "0000")

    assert result is False
    assert player.state == "fight"
    assert switch.enemy is not None
    assert switch.enemy.anti_magic_active is True
