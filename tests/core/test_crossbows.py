"""Regression coverage for Ranger crossbows and bolt ammunition."""

from types import SimpleNamespace

from src.core import enemies, items
from src.core.classes import crossbow
from src.core.save_system import ItemSerializer
from tests.test_framework import TestGameState


class _Rng:
    def __init__(self, *values):
        self.values = iter(values)

    def random(self):
        return next(self.values)


def _ranger():
    return TestGameState.create_player(class_name="Ranger", level=40)


def test_only_ranger_line_can_equip_crossbows():
    ranger = _ranger()
    beast_master = TestGameState.create_player(class_name="Beast Master", level=70)
    warrior = TestGameState.create_player(class_name="Warrior", level=20)
    weapon = items.HandCrossbow()

    assert ranger.can_equip_item(weapon, "OffHand")
    assert beast_master.can_equip_item(weapon, "OffHand")
    assert not warrior.can_equip_item(weapon, "OffHand")


def test_crossbow_fires_selected_bolt_after_attack_and_can_recover_it():
    ranger = _ranger()
    target = enemies.Orc()
    ranger.equipment["OffHand"] = items.HandCrossbow()
    pack = items.MetalBolts()
    ranger.modify_inventory(pack)
    pack.use(ranger)
    before = target.health.current

    message, hit, damages = crossbow.fire_crossbow(ranger, target, rng=_Rng(0.0, 0.0))

    assert hit
    assert target.health.current < before
    assert damages
    assert pack.charges == 10
    assert "recovers" in message


def test_repeating_crossbow_spends_two_unrecovered_bolts():
    ranger = _ranger()
    target = enemies.Troll()
    ranger.equipment["OffHand"] = items.RepeatingCrossbow()
    pack = items.WoodenBolts()
    ranger.modify_inventory(pack)

    _message, hit, damages = crossbow.fire_crossbow(ranger, target, rng=_Rng(0.0, 1.0, 0.0, 1.0))

    assert hit
    assert len(damages) == 2
    assert pack.charges == 8


def test_delayed_bolt_explodes_on_the_next_target_turn():
    ranger = _ranger()
    target = enemies.Troll()
    ranger.equipment["OffHand"] = items.HeavyCrossbow()
    ranger.modify_inventory(items.DelayedBolts())

    crossbow.fire_crossbow(ranger, target, rng=_Rng(0.0, 1.0))
    before = target.health.current
    message = crossbow.tick_delayed_bolts(target)

    assert target.health.current < before
    assert "explodes" in message


def test_napalm_hits_every_living_enemy():
    ranger = _ranger()
    first = enemies.Troll()
    second = enemies.Troll()
    ranger.equipment["OffHand"] = items.MagicCrossbow()
    ranger.modify_inventory(items.NapalmBolts())
    encounter = SimpleNamespace(
        living_members=[SimpleNamespace(enemy=first), SimpleNamespace(enemy=second)]
    )
    before = (first.health.current, second.health.current)

    crossbow.fire_crossbow(ranger, first, encounter=encounter, rng=_Rng(0.0, 1.0))

    assert first.health.current < before[0]
    assert second.health.current < before[1]


def test_magic_bolts_add_arcane_damage_only_with_magic_crossbow():
    ranger = _ranger()
    target = enemies.Troll()
    ranger.modify_inventory(items.MagicBolts())

    ranger.equipment["OffHand"] = items.HandCrossbow()
    _message, _hit, ordinary_damages = crossbow.fire_crossbow(ranger, target, rng=_Rng(0.0, 1.0))
    ranger.equipment["OffHand"] = items.MagicCrossbow()
    _message, _hit, magic_damages = crossbow.fire_crossbow(ranger, target, rng=_Rng(0.0, 1.0))

    assert len(ordinary_damages) == 1
    assert len(magic_damages) == 2


def test_heat_seeking_bolts_exclude_cold_elementals_undead_and_slimes():
    fire_elemental = enemies.FlameWisp()
    cold_elemental = enemies.Xorn()

    assert crossbow._heat_seeking_bonus(fire_elemental) == 0.20
    assert crossbow._heat_seeking_bonus(cold_elemental) == 0.0
    assert crossbow._heat_seeking_bonus(enemies.Skeleton()) == 0.0
    assert crossbow._heat_seeking_bonus(SimpleNamespace(enemy_typ="Slime")) == 0.0


def test_bolt_packs_round_trip_charges_and_do_not_enter_random_loot():
    restored = ItemSerializer.deserialize(
        ItemSerializer.serialize(items.ArmorPiercingBolts(charges=4))
    )
    random_classes = {
        item_class for bucket in items._build_rarity_table().values() for item_class in bucket
    }

    assert restored.charges == 4
    assert items.WoodenBolts not in random_classes
    assert items.GoldenClaw in random_classes
