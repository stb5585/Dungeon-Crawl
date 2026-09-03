"""Regression coverage for the authored Assassin and Ninja Death Mark loop."""

from types import MethodType, SimpleNamespace

from src.core import abilities, enemies, items, progression
from src.core.classes import class_rings, footpad, promotion_kits
from src.core.map_tiles import traps
from tests.test_framework import TestGameState


def _player(class_name="Ninja", *, skills=()):
    player = TestGameState.create_player(
        class_name=class_name,
        level=90,
        mana=(500, 500),
        skills=list(skills),
    )
    player.equipment["Weapon"] = items.Dirk()
    player.equipment["OffHand"] = items.Dirk()
    return player


def test_ninja_tree_has_five_authored_columns_and_planned_budget():
    tree = progression.ABILITY_TREES["Ninja"]
    nodes = [node for node in tree.nodes if node.kind.value != "promotion"]

    assert tree.branches == ("Utility", "Combat", "Toxin / Death", "Stealth", "Defense")
    assert len(nodes) == 28
    assert sum(node.cost for node in nodes) == 33
    assert 20 / sum(node.cost for node in nodes) == 0.6060606060606061
    assert "Desoul" not in {node.name for node in nodes}
    assert {node.name for node in nodes if node.cost == 2} == {
        "Smash and Grab",
        "Thousand Cuts",
        "Black Lotus Mastery",
        "Ghost Step",
        "Untouchable",
    }


def test_death_mark_registry_is_authored_and_action_token_idempotent():
    assert set(promotion_kits.DEATH_MARK_ACTION_REGISTRY) == (
        set(promotion_kits.DEATH_MARK_SETUP_ABILITIES)
        | set(promotion_kits.DEATH_MARK_FINISHERS)
    )
    ninja = _player()
    target = enemies.Goblin()
    promotion_kits.begin_action(ninja, action="Use Skill", choice="Momentum")

    first = promotion_kits.resolve_death_mark_setup(
        ninja, target, "Momentum", hit=True,
    )
    second = promotion_kits.resolve_death_mark_setup(
        ninja, target, "Momentum", hit=True,
    )

    assert "gains a Death Mark" in first
    assert second == ""
    assert promotion_kits.death_mark_stacks(ninja, target) == 1


def test_learning_death_mark_automatically_grants_deathblow():
    assassin = _player("Assassin")
    state = progression.ensure_progression(assassin)
    state.unspent_points = 1

    result = progression.purchase_node(assassin, "assassin.ability.deathmark")

    assert result.success
    assert "Death Mark" in assassin.spellbook["Skills"]
    assert "Deathblow" in assassin.spellbook["Skills"]


def test_setup_actions_apply_one_mark_plus_one_successful_status():
    ninja = _player()
    target = enemies.Goblin()

    msg = promotion_kits.resolve_death_mark_setup(
        ninja, target, "Kidney Punch", hit=True, status_applied=True,
    )

    assert msg.count("gains a Death Mark") == 2
    assert promotion_kits.death_mark_stacks(ninja, target) == 2
    assert promotion_kits.resolve_death_mark_setup(
        ninja, target, "Triple Strike", hit=True, status_applied=True,
    ) == ""


def test_setup_misses_dead_targets_and_assassin_cap_are_respected():
    assassin = _player("Assassin")
    target = enemies.Goblin()

    assert promotion_kits.resolve_death_mark_setup(
        assassin, target, "Backstab", hit=False, status_applied=True,
    ) == ""
    promotion_kits.resolve_death_mark_setup(
        assassin, target, "Backstab", hit=True, status_applied=True,
    )
    assert promotion_kits.death_mark_stacks(assassin, target) == 1
    target.health.current = 0
    assert promotion_kits.resolve_death_mark_setup(
        assassin, target, "Sneak Attack", hit=True,
    ) == ""


def test_deathblow_spends_on_miss_and_applies_shared_bonus_on_hit():
    ninja = _player(skills=("Execution Rhythm",))
    target = enemies.Goblin()
    promotion_kits.apply_death_mark(ninja, target, "test")
    promotion_kits.apply_death_mark(ninja, target, "test")

    def miss(self, defender, **kwargs):
        return "miss\n", False, 1

    ninja.weapon_damage = MethodType(miss, ninja)
    assert "spends 2" in abilities.Deathblow().use(ninja, target).message
    assert promotion_kits.death_mark_stacks(ninja, target) == 0

    promotion_kits.apply_death_mark(ninja, target, "test")
    target.health.current = 100

    def hit(self, defender, **kwargs):
        defender.health.current -= 50
        return "hit\n", True, 1

    ninja.weapon_damage = MethodType(hit, ninja)
    result = abilities.Deathblow().use(ninja, target)
    assert result.damage == 56
    assert "6 execution damage" in result.message
    assert "Execution Rhythm restores" in result.message


def test_death_contest_honors_weakness_immunity_and_bosses():
    ninja = _player()
    target = enemies.Goblin()
    ninja.stats.charisma = 100
    target.stats.con = 1
    target.resistance["Death"] = -0.5
    rng = SimpleNamespace(randint=lambda low, high: high)

    killed, immune = promotion_kits.resolve_death_contest(
        ninja, target, marks=3, rng=rng,
    )
    assert killed and not immune

    target.health.current = target.health.max
    target.resistance["Death"] = 1.0
    assert promotion_kits.resolve_death_contest(ninja, target, rng=rng) == (False, True)
    target.resistance["Death"] = 0.0
    target.boss = True
    assert promotion_kits.resolve_death_contest(ninja, target, rng=rng) == (False, True)


def test_death_sentence_spends_marks_against_full_immunity():
    ninja = _player()
    target = enemies.Goblin()
    target.health.current = max(target.health.current, 100)
    target.resistance["Death"] = 1.0
    promotion_kits.apply_death_mark(ninja, target, "test")

    def hit(self, defender, **kwargs):
        defender.health.current -= 10
        return "hit\n", True, 1

    ninja.weapon_damage = MethodType(hit, ninja)
    result = abilities.DeathSentence().use(ninja, target)

    assert "immune" in result.message
    assert promotion_kits.death_mark_stacks(ninja, target) == 0


def test_toxin_result_is_structured_and_conservation_keeps_immune_coating():
    ninja = _player(skills=("Coating Conservation",))
    target = enemies.Goblin()
    target.status_immunity.append("Poison")
    ninja._applied_toxin = {"name": "Mild Toxin", "slot": "Weapon"}

    outcome = footpad.apply_coated_toxin(ninja, target, "Weapon", critical=False)

    assert isinstance(outcome, footpad.ToxinReactionResult)
    assert outcome.coating_preserved
    assert ninja._applied_toxin
    assert not outcome.status_applied


def test_find_traps_warns_once_without_disarming():
    ninja = _player(skills=("Find Traps",))
    tile = SimpleNamespace(
        trap_type="Tripwire", trap_triggered=False, trap_warned=False, z=0,
    )
    rng = SimpleNamespace(random=lambda: 0.0)

    message = traps.find_trap_warning(tile, ninja, rng=rng)

    assert "stops before entering" in message
    assert tile.trap_warned is True
    assert tile.trap_triggered is False
    assert traps.find_trap_warning(tile, ninja, rng=rng) == ""


def test_combat_invisibility_conceals_until_an_attack():
    ninja = _player(skills=("Shadow Evasion",))
    target = enemies.Goblin()
    spell = abilities.Invisibility()

    assert "concealed" in spell.cast(ninja, target)
    assert ninja._combat_concealed is True
    assert footpad.concealment_dodge_bonus(ninja) == 0.25

    # Invoke the real attack setup while making the target harmless enough for a stable check.
    target.magic_effects["Ice Block"].active = True
    ninja.weapon_damage(target, use_offhand=False)
    assert ninja._combat_concealed is False
    assert footpad.concealment_dodge_bonus(ninja) == 0.15


def test_no_trace_opener_applies_and_spends_before_preserving_once():
    ninja = _player()
    target = enemies.Goblin()
    ninja.equipment["Weapon"] = items.Tanto()
    ninja.equipment["Ring"] = items.ClassRing()
    class_rings.ensure_state(ninja)["awakened"]["Ninja"] = True
    state = promotion_kits.combat_state(ninja)
    state["has_initiative"] = True
    promotion_kits.apply_death_mark(ninja, target, "setup")
    promotion_kits.apply_death_mark(ninja, target, "setup")

    marks, multiplier, message = promotion_kits.begin_no_trace_opener(ninja, target)

    assert marks == 3
    assert multiplier == 2.0
    assert "spends 3" in message
    assert promotion_kits.death_mark_stacks(ninja, target) == 0
    assert "preserves 1" in promotion_kits.finish_no_trace_opener(
        ninja, target, marks=marks, hit=True,
    )
    assert promotion_kits.death_mark_stacks(ninja, target) == 1
    assert promotion_kits.finish_no_trace_opener(
        ninja, target, marks=marks, hit=True,
    ) == ""


def test_no_trace_miss_consumes_marks_without_preservation():
    ninja = _player()
    target = enemies.Goblin()
    ninja.equipment["Weapon"] = items.Tanto()
    ninja.equipment["Ring"] = items.ClassRing()
    class_rings.ensure_state(ninja)["awakened"]["Ninja"] = True
    promotion_kits.combat_state(ninja)["has_initiative"] = True

    marks, multiplier, _message = promotion_kits.begin_no_trace_opener(ninja, target)

    assert (marks, multiplier) == (1, 2.0)
    assert promotion_kits.finish_no_trace_opener(
        ninja, target, marks=marks, hit=False,
    ) == ""
    assert promotion_kits.death_mark_stacks(ninja, target) == 0


def test_untouchable_rerolls_accuracy_dodge_and_parry_once():
    attacker = _player()
    defender = _player(skills=("Parry", "Untouchable"))
    calls = {"parry": 0}

    attacker.hit_chance = MethodType(lambda self, target, typ="weapon": 1.0, attacker)
    defender.dodge_chance = MethodType(lambda self, target: 0.0, defender)

    def parry(self, target, damage):
        calls["parry"] += 1
        if calls["parry"] == 1:
            return damage, "", False, False
        return 0, "reroll parry\n", True, False

    attacker._apply_parry = MethodType(parry, attacker)
    message, hit, _crit = attacker.weapon_damage(defender, use_offhand=False)

    assert "Untouchable rerolls the attack" in message
    assert calls["parry"] == 2
    assert hit is False
    assert defender._untouchable_used is True


def test_death_mark_status_uses_selected_target_instead_of_highest_enemy():
    ninja = _player()
    marked = enemies.Goblin()
    selected = enemies.Goblin()
    promotion_kits.apply_death_mark(ninja, marked, "setup")
    promotion_kits.apply_death_mark(ninja, marked, "setup")

    rows = promotion_kits.status_summary_rows(ninja, target=selected)

    assert ("Death Mark", "0/3 Building") in rows
