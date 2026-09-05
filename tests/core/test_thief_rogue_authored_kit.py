"""Focused coverage for the authored Thief and Rogue luck-and-loot kit."""

from types import SimpleNamespace

from src.core import abilities, enemies, items, map_tiles, player as player_module
from src.core.classes import class_rings, footpad, promotion_kits
from src.core.combat.combat_result import CombatResult
from src.core.progression import ABILITY_TREES, NodeKind, ProgressionState
from tests.test_framework import TestGameState


class _OrdinaryTile:
    pass


def _player(class_name="Thief", *, health=(500, 500), mana=(500, 500)):
    player = TestGameState.create_player(
        class_name=class_name,
        race_name="Human",
        level=70,
        health=health,
        mana=mana,
    )
    player.progression = ProgressionState(level=70)
    return player


def _grant(player, *talent_keys):
    talents = {
        node.payload["talent_key"]: node.id
        for tree_name in ("Thief", "Rogue")
        for node in ABILITY_TREES[tree_name].nodes
        if node.kind == NodeKind.TALENT
    }
    player.progression.purchased_node_ids.update(talents[key] for key in talent_keys)


def _closure_cost(tree, node):
    by_id = {entry.id: entry for entry in tree.nodes}
    seen = set()

    def visit(entry):
        if entry.id in seen:
            return 0
        seen.add(entry.id)
        return entry.cost + sum(visit(by_id[parent]) for parent in entry.prerequisites)

    return visit(node)


def test_thief_tree_has_four_routes_and_cross_training_budget():
    tree = ABILITY_TREES["Thief"]
    development = [node for node in tree.nodes if node.kind != NodeKind.PROMOTION]
    promotion = next(node for node in tree.nodes if node.kind == NodeKind.PROMOTION)

    assert tree.branches == ("Fortune", "Misfortune", "Tools", "Escape")
    assert len(development) == 22
    assert sum(node.cost for node in development) == 22
    assert promotion.payload["prerequisite_mode"] == "any"
    assert len(promotion.prerequisites) == 4
    assert {
        _closure_cost(tree, next(node for node in tree.nodes if node.id == endpoint))
        for endpoint in promotion.prerequisites
    } == {5, 6}
    assert 15 - promotion.cost - 5 == 7


def test_rogue_tree_has_normal_terminal_breadth_and_cost():
    tree = ABILITY_TREES["Rogue"]

    assert tree.branches == ("Loaded Odds", "Comebacks", "Cunning", "Escape")
    assert len(tree.nodes) == 28
    assert sum(node.cost for node in tree.nodes) == 30
    assert sum(node.cost > 1 for node in tree.nodes) == 2
    assert 0.60 <= 20 / 30 <= 0.70
    assert max(node.position[1] for node in tree.nodes) == 6


def test_thief_and_rogue_rows_use_standard_level_bands():
    for class_name, levels in (
        ("Thief", {1: 35, 2: 40, 3: 45, 4: 50, 5: 55}),
        ("Rogue", {1: 65, 2: 70, 3: 75, 4: 80, 5: 85, 6: 90}),
    ):
        for node in ABILITY_TREES[class_name].nodes:
            if node.kind == NodeKind.PROMOTION or node.position[1] == 0:
                continue
            assert node.payload["level_requirement"] == levels[node.position[1]]


def test_luck_caps_are_exact_and_ignore_obsolete_cap_talents():
    thief = _player("Thief")
    rogue = _player("Rogue")

    assert promotion_kits.cap_for(thief, "fortune") == 2
    assert promotion_kits.cap_for(thief, "misfortune") == 2
    assert promotion_kits.cap_for(rogue, "fortune") == 3
    assert promotion_kits.cap_for(rogue, "misfortune") == 3


def test_meaningful_luck_outcomes_are_deduplicated_per_action():
    thief = _player()
    promotion_kits.begin_action(thief, action="Attack", choice=None)

    first = promotion_kits.record_luck_roll(thief, True, "attack")
    duplicate = promotion_kits.record_luck_roll(thief, False, "critical")

    assert "Fortune" in first
    assert duplicate == ""
    assert promotion_kits.combat_state(thief)["fortune"] == 1
    assert promotion_kits.combat_state(thief)["misfortune"] == 0

    promotion_kits.begin_action(thief, action="Attack", choice=None)
    promotion_kits.record_luck_roll(thief, False, "miss")
    assert promotion_kits.combat_state(thief)["misfortune"] == 1


def test_successful_dodges_share_the_hostile_action_boundary():
    thief = _player()
    attacker = enemies.Goblin()
    promotion_kits.begin_incoming_action(thief, round_number=1)

    attacker._handle_dodge(thief, 20, "attacks")
    attacker._handle_dodge(thief, 20, "attacks")

    assert promotion_kits.combat_state(thief)["fortune"] == 1


def test_fortune_spends_before_a_risky_weapon_roll_and_modifies_accuracy(monkeypatch):
    thief = _player()
    target = enemies.Goblin()
    target.status_effects["Stun"].active = True
    target.status_effects["Stun"].duration = 2
    promotion_kits.gain_meter(thief, "fortune", 2, "test")
    promotion_kits.begin_action(thief, action="Use Skill", choice="Sneak Attack")
    captured = {}

    def weapon_damage(_target, **kwargs):
        captured.update(kwargs)
        return "hit\n", True, 2

    monkeypatch.setattr(thief, "weapon_damage", weapon_damage)
    abilities.SneakAttack().use(thief, target)

    assert captured["accuracy_modifier"] == 0.10
    assert promotion_kits.combat_state(thief)["fortune"] == 1


def test_unrelated_action_does_not_spend_fortune():
    thief = _player()
    promotion_kits.gain_meter(thief, "fortune", 2, "test")

    bonus, message = promotion_kits.consume_fortune_for_risky_action(
        thief,
        "Double Strike",
    )

    assert bonus == 0
    assert message == ""
    assert promotion_kits.combat_state(thief)["fortune"] == 2


def test_loaded_dice_preserves_fortune_only_after_a_clean_payoff():
    rogue = _player("Rogue")
    rogue.equipment["Ring"] = items.ClassRing()
    class_rings.ensure_state(rogue)["awakened"]["Rogue"] = True
    promotion_kits.gain_meter(rogue, "fortune", 2, "test")

    promotion_kits.consume_fortune_for_risky_action(rogue, "Steal")
    assert promotion_kits.finish_fortune_payoff(rogue, False) == ""
    assert promotion_kits.combat_state(rogue)["fortune"] == 0

    promotion_kits.gain_meter(rogue, "fortune", 2, "test")
    promotion_kits.consume_fortune_for_risky_action(rogue, "Steal")
    message = promotion_kits.finish_fortune_payoff(rogue, True)
    assert "preserves 1 spent fortune" in message
    assert promotion_kits.combat_state(rogue)["fortune"] == 1

    target = enemies.Goblin()
    promotion_kits.gain_meter(rogue, "misfortune", 2, "test")
    message = promotion_kits.resolve_misfortune_payoff(rogue, target, 50, "Mug")
    assert "preserves" not in message
    assert promotion_kits.combat_state(rogue)["misfortune"] == 0


def test_misfortune_bonus_uses_typed_defense_and_does_not_regenerate_itself():
    rogue = _player("Rogue")
    target = enemies.Goblin()
    target.health.max = target.health.current = 1000
    target.resistance["Physical"] = 0.50
    promotion_kits.gain_meter(rogue, "misfortune", 2, "test")
    before = target.health.current

    message = promotion_kits.resolve_misfortune_payoff(
        rogue,
        target,
        100,
        "Mug",
    )

    dealt = before - target.health.current
    assert 0 < dealt < 16
    assert "extra pressure" in message
    assert promotion_kits.combat_state(rogue)["fortune"] == 0


def test_misfortune_extends_a_successful_status_payoff():
    rogue = _player("Rogue")
    target = enemies.Goblin()
    target.status_effects["Stun"].active = True
    target.status_effects["Stun"].duration = 2
    result = CombatResult(
        action="Kidney Punch",
        actor=rogue,
        target=target,
        hit=True,
        effects_applied={"Status": ["Stun"]},
    )
    promotion_kits.gain_meter(rogue, "misfortune", 2, "test")

    message = promotion_kits.resolve_misfortune_payoff(
        rogue,
        target,
        0,
        "Kidney Punch",
        result=result,
    )

    assert target.status_effects["Stun"].duration == 4
    assert "extending Stun" in message


def test_fortune_changes_a_real_status_contest_and_misfortune_scales_duration(
    monkeypatch,
):
    thief = _player("Thief")
    target = enemies.Goblin()
    thief.stats.dex = 100
    original_check_mod = target.check_mod

    def target_check_mod(mod, *args, **kwargs):
        if mod == "speed":
            return 105
        if mod == "luck":
            return 0
        return original_check_mod(mod, *args, **kwargs)

    target.check_mod = target_check_mod
    monkeypatch.setattr("random.randint", lambda _low, high: high)
    promotion_kits.gain_meter(thief, "fortune", 2, "test")
    promotion_kits.gain_meter(thief, "misfortune", 2, "test")
    promotion_kits.begin_action(thief, action="Use Skill", choice="Pocket Sand")

    message = abilities.PocketSand().use(thief, target)

    assert "is blinded" in message
    assert target.status_effects["Blind"].duration == 5
    assert promotion_kits.combat_state(thief)["misfortune"] == 0


def test_slot_machine_scales_a_success_without_changing_its_outcome():
    plain = _player("Rogue")
    fueled = _player("Rogue")
    plain_target = enemies.Goblin()
    fueled_target = enemies.Goblin()
    for target in (plain_target, fueled_target):
        target.health.max = target.health.current = 10_000
    promotion_kits.gain_meter(fueled, "misfortune", 3, "test")
    callback = lambda _actor, _target: "2S,3S,4S"

    plain_message = abilities.SlotMachine().use(
        plain,
        plain_target,
        slot_machine_callback=callback,
    )
    fueled_message = abilities.SlotMachine().use(
        fueled,
        fueled_target,
        slot_machine_callback=callback,
    )

    plain_damage = plain_target.health.max - plain_target.health.current
    fueled_damage = fueled_target.health.max - fueled_target.health.current
    assert "Straight Flush" in plain_message
    assert "Straight Flush" in fueled_message
    assert fueled_damage > plain_damage
    assert promotion_kits.combat_state(fueled)["misfortune"] == 0


def test_cheat_death_requires_learning_and_loaded_dice_converts_a_failed_save(
    monkeypatch,
):
    rogue = _player("Rogue", health=(100, 0))
    promotion_kits.gain_meter(rogue, "misfortune", 2, "test")

    assert promotion_kits.cheat_death(rogue) == ""
    assert not promotion_kits.combat_state(rogue)["cheat_death_used"]

    rogue.spellbook["Skills"]["Cheat Death"] = abilities.CheatDeath()
    monkeypatch.setattr("random.random", lambda: 0.99)
    monkeypatch.setattr(class_rings, "loaded_dice_succeeds", lambda *_args, **_kwargs: True)

    message = promotion_kits.cheat_death(rogue)

    assert "Loaded Dice" in message
    assert rogue.health.current == 1
    assert promotion_kits.combat_state(rogue)["jinx_turns"] == 2
    assert promotion_kits.jinx_accuracy_modifier(rogue) < 0


def test_fatal_damage_hook_uses_learned_cheat_death(monkeypatch):
    rogue = _player("Rogue", health=(100, 0))
    rogue.spellbook["Skills"]["Cheat Death"] = abilities.CheatDeath()
    monkeypatch.setattr("random.random", lambda: 0.0)

    promotion_kits.record_damage_taken(rogue, 100, "Physical")

    assert rogue.health.current == 1
    assert promotion_kits.combat_state(rogue)["cheat_death_used"]


def test_loaded_dice_is_called_by_a_failed_theft(monkeypatch):
    rogue = _player("Rogue")
    target = enemies.Goblin()
    target.gold = 100
    rolls = iter((0, 10, 1))
    monkeypatch.setattr("random.choice", lambda _values: "Gold")
    monkeypatch.setattr("random.randint", lambda _low, _high: next(rolls))
    monkeypatch.setattr(class_rings, "loaded_dice_succeeds", lambda *_args, **_kwargs: True)

    message = abilities.Steal().use(rogue, target)

    assert "Loaded Dice turns the failed theft" in message
    assert "steals 1 gold" in message


def test_loaded_dice_converted_risky_attack_records_the_success(monkeypatch):
    rogue = _player("Rogue")
    target = enemies.Goblin()
    target.status_effects["Stun"].active = True
    target.status_effects["Stun"].duration = 2
    outcomes = iter((False, True))

    def weapon_damage(_target, **_kwargs):
        hit = next(outcomes)
        return ("hit\n" if hit else "miss\n"), hit, 2 if hit else 1

    monkeypatch.setattr(rogue, "weapon_damage", weapon_damage)
    monkeypatch.setattr(class_rings, "loaded_dice_succeeds", lambda *_args, **_kwargs: True)
    promotion_kits.begin_action(rogue, action="Use Skill", choice="Sneak Attack")

    message = abilities.SneakAttack().use(rogue, target)

    assert "Loaded Dice turns" in message.message
    assert promotion_kits.combat_state(rogue)["fortune"] == 1
    assert promotion_kits.combat_state(rogue)["misfortune"] == 0


def test_jinx_reduces_real_luck_checks_until_it_fades():
    rogue = _player("Rogue")
    baseline = rogue.check_mod("luck", luck_factor=4)
    promotion_kits.combat_state(rogue)["jinx_turns"] = 2

    assert rogue.check_mod("luck", luck_factor=4) < baseline

    promotion_kits.tick_combat_state(rogue)
    promotion_kits.tick_combat_state(rogue)
    assert rogue.check_mod("luck", luck_factor=4) == baseline


def test_scavengers_eye_requires_learning_and_can_create_the_drop(monkeypatch):
    thief = _player("Thief")
    item = SimpleNamespace(
        name="Rare Knife",
        subtyp="Dagger",
        rarity=0.01,
        ultimate=False,
    )
    base = footpad.ordinary_loot_threshold(thief, item, 1.0)
    thief.spellbook["Skills"]["Scavenger's Eye"] = abilities.ScavengersEye()
    improved = footpad.ordinary_loot_threshold(thief, item, 1.0)

    assert base == 0.01
    assert improved > base


def test_finders_keepers_grants_only_an_eligible_extra_find(monkeypatch):
    rogue = _player("Rogue")
    rogue.spellbook["Skills"]["Finders Keepers"] = abilities.FindersKeepers()
    ordinary = SimpleNamespace(
        name="Loose Dagger",
        subtyp="Dagger",
        rarity=0.0,
        ultimate=False,
        weight=1.0,
    )
    ultimate = SimpleNamespace(
        name="Forbidden Edge",
        subtyp="Sword",
        rarity=0.0,
        ultimate=True,
        weight=1.0,
    )
    quest = SimpleNamespace(
        name="Quest Relic",
        subtyp="Quest",
        rarity=0.0,
        ultimate=False,
        weight=1.0,
    )
    enemy = SimpleNamespace(
        name="Bandit",
        gold=0,
        inventory={"drops": [ordinary, ultimate, quest]},
    )
    rogue.quests = lambda enemy=None, item=None: ""
    monkeypatch.setattr(player_module.random, "random", lambda: 0.0)
    monkeypatch.setattr(player_module.random, "choice", lambda values: values[0])

    message = rogue.loot(enemy, _OrdinaryTile())

    assert "extra Loose Dagger" in message
    assert "Loose Dagger" in rogue.inventory
    assert "Forbidden Edge" not in rogue.inventory
    assert "Quest Relic" not in rogue.inventory


def test_combat_state_cleanup_removes_both_luck_meters_and_jinx():
    rogue = _player("Rogue")
    state = promotion_kits.combat_state(rogue)
    state["fortune"] = 3
    state["misfortune"] = 3
    state["jinx_turns"] = 2

    promotion_kits.clear_combat_state(rogue)

    state = promotion_kits.combat_state(rogue)
    assert state["fortune"] == 0
    assert state["misfortune"] == 0
    assert state["jinx_turns"] == 0


def test_turn_the_tables_and_cut_and_run_are_resource_and_combat_choices(monkeypatch):
    thief = _player()
    target = enemies.Goblin()
    _grant(
        thief,
        "thief.reversal",
        "thief.fleet-footed",
        "thief.lasting-head-start",
    )
    promotion_kits.gain_meter(thief, "misfortune", 2, "test")

    tables = abilities.TurnTheTables().use(thief)

    assert tables.hit is True
    assert thief.stat_effects["Attack"].extra == 10
    assert thief.stat_effects["Defense"].duration == 4
    assert promotion_kits.combat_state(thief)["misfortune"] == 0

    def weapon_hit(enemy, **_kwargs):
        enemy.health.current -= 10
        return "hit\n", True, 1

    monkeypatch.setattr(thief, "weapon_damage", weapon_hit)
    result = abilities.CutAndRun().use(thief, target)
    assert result.damage == 10
    assert thief.stat_effects["Speed"].extra == 12
    assert thief.stat_effects["Speed"].duration == 3


def test_all_in_spends_both_meters_and_can_preserve_fortune(monkeypatch):
    rogue = _player("Rogue")
    target = enemies.Goblin()
    _grant(rogue, "rogue.house-always-wins")
    promotion_kits.gain_meter(rogue, "fortune", 2, "test")
    promotion_kits.gain_meter(rogue, "misfortune", 3, "test")
    captured = {}

    def weapon_hit(enemy, **kwargs):
        captured.update(kwargs)
        enemy.health.current -= 20
        return "hit\n", True, 1

    monkeypatch.setattr(rogue, "weapon_damage", weapon_hit)
    result = abilities.AllIn().use(rogue, target)

    assert result.hit is True
    assert captured["dmg_mod"] == 1.6
    assert captured["accuracy_modifier"] == 0.10
    assert promotion_kits.combat_state(rogue)["fortune"] == 1
    assert promotion_kits.combat_state(rogue)["misfortune"] == 0


def test_detected_trap_can_be_disarmed_on_the_second_approach():
    rogue = _player("Rogue")
    rogue.stats.dex = 20
    rogue.spellbook["Skills"].update({
        "Find Traps": abilities.FindTraps(),
        "Disarm Traps": abilities.DisarmTraps(),
    })
    tile = SimpleNamespace(
        trap_type="Tripwire",
        trap_triggered=False,
        trap_warned=False,
        z=1,
    )
    rng = SimpleNamespace(random=lambda: 0.0)

    warning = map_tiles.find_trap_warning(tile, rogue, rng=rng)
    disarmed = map_tiles.find_trap_warning(tile, rogue, rng=rng)

    assert "stops before entering" in warning
    assert "disarms the hidden Tripwire" in disarmed
    assert tile.trap_triggered is True


def test_impossible_job_caps_disarm_chance_and_softens_failure():
    rogue = _player("Rogue")
    rogue.stats.dex = 10
    rogue.spellbook["Skills"]["Disarm Traps"] = abilities.DisarmTraps()
    _grant(rogue, "rogue.impossible-job")
    tile = SimpleNamespace(
        trap_type="Tripwire",
        trap_triggered=False,
        trap_warned=True,
        trap_forced_initiative=False,
        z=6,
    )
    rng = SimpleNamespace(
        random=lambda: 0.99,
        randint=lambda _low, _high: 20,
    )
    before = rogue.health.current

    message = map_tiles.disarm_tile_trap(tile, rogue, rng=rng)

    assert "fails to disarm" in message
    assert "halves" in message
    assert 0 < before - rogue.health.current <= 10
