from types import SimpleNamespace

from src.core import abilities, classes, companions, enemies, items
from src.core.classes import demonologist
from src.core.save_system import PlayerDataSerializer
from tests.test_framework import TestGameState


def _demonologist():
    player = TestGameState.create_player(
        class_name="Demonologist",
        race_name="Human",
        level=60,
        pro_level=3,
        stats={"strength": 12, "intel": 25, "wisdom": 20, "con": 18, "charisma": 30, "dex": 18},
    )
    player.gold = 5000
    player.spellbook["Skills"]["Call Contract"] = abilities.CallContract()
    player.equipment["Ring"] = items.ClassRing()
    player.kill_dict = {"Fiend": {"Imp": 1, "Succubus": 1}}
    return player


def test_classes_package_registers_demonologist_without_pruning_api():
    demonologist_class = classes.classes_dict["Mage"]["pro"]["Warlock"]["pro"][
        "Demonologist"
    ]["class"]

    assert demonologist_class is classes.Demonologist
    assert not hasattr(classes, "PROMOTION_ABILITY_RULES")
    assert not hasattr(classes, "apply_promotion_ability_rules")


def test_promotion_state_unlocks_crypt_and_contracts_from_kill_history():
    player = _demonologist()

    state = player.ensure_demonologist_contracts()
    unlocked = player.refresh_demonologist_contracts()

    assert state["crypt_unlocked"] is True
    assert unlocked == ["Imp", "Succubus"]
    assert player.demonologist_contracts["active_patron"] == "Imp"


def test_ring_awakening_imprisons_familiar_and_empowers_future_contracts():
    player = _demonologist()
    player.refresh_demonologist_contracts()
    demonologist.bind_patron(player, "Imp")
    dormant_description = player.equipment["Ring"].get_description(player)
    assert "dormant Class Ring for a Demonologist" in dormant_description
    assert "Ring location: equipped" in dormant_description
    assert "Basic contracts are available" in dormant_description
    assert "empowered contracts are inactive" in dormant_description
    assert "Active patron: Imp" in dormant_description

    familiar = companions.Homunculus()
    familiar.name = "Aegis"
    player.familiar = familiar

    success, message = demonologist.awaken_ring(player)

    assert success is True
    assert "sealed inside" in message
    assert player.familiar is None
    assert demonologist.empowered(player) is True
    assert player.demonologist_contracts["imprisoned_familiar"]["spec"] == "Defense"
    awakened_description = player.equipment["Ring"].get_description(player)
    assert "awakened Class Ring for a Demonologist" in awakened_description
    assert "Ring location: equipped" in awakened_description
    assert "Imprisoned echo:" in awakened_description
    assert "ring has empowered fiend contracts" in awakened_description
    assert "Active patron: Imp" in awakened_description

    player.kill_dict["Fiend"]["Balor"] = 1
    assert "Balor" in player.refresh_demonologist_contracts()
    assert demonologist.empowered(player) is True


def test_contract_quote_pay_and_resolve_with_charisma_weighting():
    player = _demonologist()
    player.refresh_demonologist_contracts()
    demonologist.bind_patron(player, "Imp")
    target = enemies.Goblin()
    target_hp = target.health.current

    high_cha = demonologist.misbehavior_chance(player, "Harm")
    player.stats.charisma = 1
    low_cha = demonologist.misbehavior_chance(player, "Harm")
    player.stats.charisma = 30

    assert high_cha < low_cha

    quote = demonologist.quote_contract(player, target, "Harm")
    assert quote["ok"] is True
    assert quote["patron"] == "Imp"
    assert demonologist.can_pay_quote(player, quote) is True

    msg = demonologist.resolve_contract(player, target, "Harm", rng=SimpleNamespace(random=lambda: 1.0))

    assert "accepts" in msg
    assert target.health.current < target_hp
    assert player.gold == 5000 - quote["costs"]["gold"]


def test_call_contract_skill_uses_pending_intent():
    player = _demonologist()
    player.kill_dict = {"Fiend": {"Succubus": 1}}
    player.refresh_demonologist_contracts()
    demonologist.bind_patron(player, "Succubus")
    skill = abilities.CallContract()
    skill.pending_intent = "Restore"
    player.health.current = max(1, player.health.current - 20)

    msg = skill.use(player, target=enemies.Goblin())

    assert "Succubus accepts" in msg
    assert player.health.current > player.health.max - 20


def test_demonologist_state_save_round_trip():
    player = _demonologist()
    player.refresh_demonologist_contracts()
    demonologist.bind_patron(player, "Succubus")
    familiar = companions.Jinkin()
    familiar.name = "Chance"
    player.familiar = familiar
    demonologist.awaken_ring(player)

    restored = PlayerDataSerializer.deserialize(
        PlayerDataSerializer.serialize(player),
        skip_tiles=True,
    )

    assert restored.demonologist_contracts["crypt_unlocked"] is True
    assert restored.demonologist_contracts["active_patron"] == "Succubus"
    assert restored.demonologist_contracts["ring_awakened"] is True
    assert restored.demonologist_contracts["imprisoned_familiar"]["spec"] == "Luck"


def test_new_contract_fiends_load_as_fiends():
    for enemy_cls in (enemies.Succubus, enemies.Maelephant, enemies.Balor):
        enemy = enemy_cls()
        assert enemy.enemy_typ == "Fiend"
        assert enemy.name in demonologist.PATRONS
