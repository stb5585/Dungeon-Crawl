"""Regression coverage for Shadowcaster Umbral Debt and Shade of Ahool."""

import pytest

from src.core import abilities, enemies, items
from src.core.classes import class_rings, promotion_kits
from src.core.companions import Fairy, Homunculus, Jinkin, Mephit
from src.core.save_system import PlayerDataSerializer
from tests.test_framework import TestGameState


def _shadowcaster(*, health=(200, 200), awakened=False):
    player = TestGameState.create_player(
        class_name="Shadowcaster",
        race_name="Human",
        level=90,
        health=health,
    )
    if awakened:
        player.equipment["Ring"] = items.ClassRing()
        class_rings.ensure_state(player)["awakened"]["Shadowcaster"] = True
    return player


def _shadow_data(player):
    return class_rings.ensure_state(player)["data"]["Shadowcaster"]


def test_shadowcaster_state_normalizes_and_load_clears_combat_fields():
    player = _shadowcaster()
    player.class_ring_awakening["data"]["Shadowcaster"] = {
        "debt": "bad",
        "backlash": -4,
        "eclipse_turns": 3,
        "familiar_echo_used": True,
    }

    data = _shadow_data(player)

    assert data == {
        "debt": 0,
        "backlash": 0,
        "eclipse_turns": 3,
        "familiar_echo_used": True,
    }
    restored = PlayerDataSerializer.deserialize(
        PlayerDataSerializer.serialize(player),
        skip_tiles=True,
    )
    restored_data = _shadow_data(restored)
    assert restored_data["eclipse_turns"] == 0
    assert restored_data["familiar_echo_used"] is False


def test_debt_cap_generation_and_mephit_overcap():
    player = _shadowcaster()
    data = _shadow_data(player)
    data["debt"] = 55

    promotion_kits.record_shadow_damage(player, 50)

    data = _shadow_data(player)
    assert promotion_kits.shadowcaster_debt_cap(player) == 60
    assert data["debt"] == 60
    assert data["backlash"] == 5

    player.familiar = Mephit()
    promotion_kits.record_shadow_damage(player, 40)
    data = _shadow_data(player)
    assert data["backlash"] == 15

    awakened = _shadowcaster(awakened=True)
    awakened_data = _shadow_data(awakened)
    awakened_data["debt"] = 88
    promotion_kits.record_shadow_damage(awakened, 50)
    awakened_data = _shadow_data(awakened)
    assert promotion_kits.shadowcaster_debt_cap(awakened) == 90
    assert awakened_data["backlash"] == 8


def test_shade_uses_one_timer_and_only_authored_direct_modifiers():
    player = _shadowcaster()
    data = _shadow_data(player)
    data["debt"] = 40
    base_weapon = player.check_mod("weapon")
    base_speed = player.check_mod("speed")
    base_holy = player.check_mod("resist", typ="Holy")
    base_crit = player.critical_chance("Weapon")

    assert "becomes the Shade" in abilities.ShadeOfAhool().use(player)

    data = _shadow_data(player)
    assert data["debt"] == 20
    assert data["eclipse_turns"] == 3
    assert not hasattr(player, "shade_of_ahool_turns")
    assert player.flying is True
    assert player.check_mod("weapon") == base_weapon
    assert player.check_mod("speed") == int(base_speed * 1.10)
    assert player.check_mod("resist", typ="Holy") == pytest.approx(base_holy - 0.25)
    expected_crit_delta = (player.check_mod("speed") - base_speed) * 0.005
    assert player.critical_chance("Weapon") == pytest.approx(base_crit + expected_crit_delta)

    target = enemies.Goblin()
    target.health.current = min(target.health.max, 20)
    player.health.current = 100
    target_before = target.health.current
    player._emit_damage_event(target, 10, "Physical")
    assert target.health.current == target_before
    assert player.health.current == 100


def test_homunculus_softens_only_the_shade_holy_penalty():
    player = _shadowcaster()
    player.familiar = Homunculus()
    data = _shadow_data(player)
    data["debt"] = 20
    holy_before = player.check_mod("resist", typ="Holy")

    promotion_kits.shade_of_ahool(player)

    assert player.check_mod("resist", typ="Holy") == pytest.approx(holy_before - 0.20)


def test_shade_strengthens_only_shadow_damage():
    player = _shadowcaster()
    _shadow_data(player)["debt"] = 20
    promotion_kits.shade_of_ahool(player)

    assert class_rings.shadowcaster_shade_damage_multiplier(player, "Shadow") == 1.15
    assert class_rings.shadowcaster_shade_damage_multiplier(player, "Dark") == 1.15
    assert class_rings.shadowcaster_shade_damage_multiplier(player, "Physical") == 1.0


def test_shade_refreshes_then_expires_with_one_backlash_conversion():
    player = _shadowcaster(health=(200, 100))
    data = _shadow_data(player)
    data.update({"debt": 40, "backlash": 30})

    promotion_kits.shade_of_ahool(player)
    promotion_kits.tick_combat_state(player)
    promotion_kits.shade_of_ahool(player)
    data = _shadow_data(player)
    assert data["eclipse_turns"] == 3
    assert data["debt"] == 0

    promotion_kits.tick_combat_state(player)
    promotion_kits.tick_combat_state(player)
    message = promotion_kits.tick_combat_state(player)

    data = _shadow_data(player)
    assert data["eclipse_turns"] == 0
    assert data["backlash"] == 10
    assert player.health.current == 80
    assert player.flying is False
    assert message.count("Umbral backlash converts") == 1
    assert promotion_kits.tick_combat_state(player).count("Umbral backlash") == 0


def test_ring_stabilizes_conversion_at_resolution_not_generation():
    player = _shadowcaster(health=(200, 100), awakened=True)
    data = _shadow_data(player)
    data.update({"debt": 88, "backlash": 20})

    promotion_kits.record_shadow_damage(player, 50)
    data = _shadow_data(player)
    assert data["debt"] == 90
    assert data["backlash"] == 28

    message = promotion_kits.convert_shadow_backlash(
        player,
        fraction=0.10,
        reason="test",
    )
    data = _shadow_data(player)
    assert "converts 15" in message
    assert data["backlash"] == 13
    assert player.health.current == 85


def test_low_hp_ring_heal_spends_debt_then_converts_backlash_with_fairy():
    player = _shadowcaster(health=(200, 50), awakened=True)
    player.familiar = Fairy()
    data = _shadow_data(player)
    data.update({"debt": 40, "backlash": 30})

    healed = class_rings.trigger_umbral_debt(player)

    data = _shadow_data(player)
    assert healed == 40
    assert data["debt"] == 0
    assert data["backlash"] == 15
    assert player.health.current == 77
    messages = promotion_kits.pop_messages(player)
    assert "spends 40 debt" in messages
    assert "restores 2 extra HP" in messages
    assert "converts 15" in messages


def test_fairy_echoes_shade_spend_and_jinkin_gets_one_chance(monkeypatch):
    fairy = _shadowcaster(health=(200, 100))
    fairy.familiar = Fairy()
    fairy_data = _shadow_data(fairy)
    fairy_data.update({"debt": 20, "backlash": 20, "eclipse_turns": 1})

    promotion_kits.tick_combat_state(fairy)
    assert fairy.health.current == 81

    jinkin = _shadowcaster(health=(200, 100))
    jinkin.familiar = Jinkin()
    jinkin_data = _shadow_data(jinkin)
    jinkin_data["backlash"] = 40
    monkeypatch.setattr(
        "src.core.classes.promotion_kits.meters.random.random",
        lambda: 0.0,
    )

    promotion_kits.convert_shadow_backlash(jinkin, fraction=0.10, reason="first")
    promotion_kits.convert_shadow_backlash(jinkin, fraction=0.10, reason="second")

    jinkin_data = _shadow_data(jinkin)
    assert jinkin_data["familiar_echo_used"] is True
    assert jinkin_data["backlash"] == 10
    assert jinkin.health.current == 70


def test_combat_end_uses_five_percent_cap_and_clears_shade():
    player = _shadowcaster(health=(200, 100), awakened=True)
    data = _shadow_data(player)
    data.update({"debt": 20, "backlash": 30, "eclipse_turns": 2})
    player.flying = True

    message = promotion_kits.end_combat(player)

    data = _shadow_data(player)
    assert "converts 10" in message
    assert data["backlash"] == 20
    assert data["eclipse_turns"] == 0
    assert player.health.current == 90
    assert player.flying is False
