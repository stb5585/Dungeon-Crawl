"""Coverage for the authored Warlock-family trees and shadow mechanics."""

import pytest

from src.core import abilities, enemies
from src.core import persistent_afflictions as afflictions
from src.core.classes import demonologist, mage_mechanics, warlock
from src.core.combat import CombatEncounter
from src.core.combat.battle_engine.outcomes import BattleOutcomeMixin
from src.core.combat.combat_result import CombatResult
from src.core.effects.enemy import DrainEffect
from src.core.progression import (
    ABILITY_TREES,
    NodeState,
    available_nodes,
    ensure_progression,
)
from tests.test_framework import TestGameState


def _player(class_name: str, *, level: int = 90):
    return TestGameState.create_player(
        class_name=class_name,
        race_name="Human",
        level=level,
        stats={
            "strength": 15,
            "intel": 35,
            "wisdom": 25,
            "con": 22,
            "charisma": 30,
            "dex": 24,
        },
    )


def _nodes(class_name: str):
    return {node.name: node for node in ABILITY_TREES[class_name].nodes}


def test_warlock_tree_has_authored_six_column_paths():
    tree = ABILITY_TREES["Warlock"]
    nodes = _nodes("Warlock")

    assert len(tree.nodes) == 31
    assert tree.branches == (
        "Shadow Control",
        "Draining",
        "Umbral Offense",
        "Curses",
        "Corruption",
        "Familiar",
    )
    assert nodes["Sleep"].position == (0, 1)
    assert nodes["Doom"].prerequisites == (nodes["Terrify"].id,)
    assert nodes["Resist Holy"].position == (1, 3)
    assert nodes["Resist Holy"].payload["level_requirement"] == 40
    assert nodes["Shadow Bolt II"].position == (2, 6)
    assert nodes["Hemorrhaging Curse"].position == (3, 3)
    assert nodes["Hemorrhaging Curse"].payload["level_requirement"] == 40
    assert nodes["Curse of Swarms"].position == (3, 5)
    assert nodes["Curse of Swarms"].payload["level_requirement"] == 50
    assert nodes["Life Tap"].position == (4, 6)
    assert nodes["Familiar Bond II"].prerequisites == (nodes["Familiar Bond"].id,)
    assert nodes["Familiar Bond II"].payload["connector_channel_columns"] == {
        nodes["Familiar Bond"].id: 5.5,
    }
    assert "connector_enter_from_top" not in nodes["Familiar Bond II"].payload
    assert nodes["Thorn By My Side"].prerequisites == ()
    assert nodes["Thorn By My Side"].payload["level_requirement"] == 45
    assert "Curse of Elijah" not in nodes
    assert "Curse of Dysarthria" not in nodes
    assert nodes["Promote: Shadowcaster"].prerequisites == (
        nodes["Doom"].id,
        nodes["Mana Drain"].id,
        nodes["Shadow Bolt II"].id,
    )
    assert nodes["Promote: Shadowcaster"].payload["prerequisite_groups"] == (
        (nodes["Doom"].id, nodes["Mana Drain"].id),
        (nodes["Shadow Bolt II"].id,),
    )
    assert nodes["Promote: Demonologist"].prerequisites == (
        nodes["Curse of Swarms"].id,
        nodes["Life Tap"].id,
    )
    assert nodes["Promote: Demonologist"].payload["prerequisite_mode"] == "any"


def test_shadowcaster_requires_umbral_offense_and_one_control_path():
    player = _player("Warlock")
    state = ensure_progression(player)
    state.unspent_points = 99
    nodes = _nodes("Warlock")
    by_id = {node.id: node for node in ABILITY_TREES["Warlock"].nodes}

    def closure(node_id):
        result = {node_id}
        for prerequisite in by_id[node_id].prerequisites:
            result.update(closure(prerequisite))
        return result

    def promotion_state():
        return next(
            status.state
            for status in available_nodes(player, "Warlock")
            if status.node.name == "Promote: Shadowcaster"
        )

    state.purchased_node_ids = closure(nodes["Shadow Bolt II"].id)
    assert promotion_state() == NodeState.BLOCKED

    state.purchased_node_ids.update(closure(nodes["Doom"].id))
    assert promotion_state() == NodeState.AVAILABLE

    state.purchased_node_ids = closure(nodes["Doom"].id) | closure(nodes["Mana Drain"].id)
    assert promotion_state() == NodeState.BLOCKED


def test_terminal_trees_replace_generic_padding_with_class_mechanics():
    shadow = _nodes("Shadowcaster")
    demon = _nodes("Demonologist")

    assert shadow["Night Terror"].prerequisites == (shadow["Nightmare"].id,)
    assert shadow["Night Terror"].payload["level_requirement"] == 75
    assert shadow["Shadow Curtain"].prerequisites == (shadow["Invisibility"].id,)
    assert shadow["Alacrity"].prerequisites == (shadow["Shadow Curtain"].id,)
    assert shadow["Alacrity"].payload["level_requirement"] == 70
    assert shadow["Top Off"].payload["level_requirement"] == 85
    assert shadow["Top Off"].cost == 2
    assert shadow["Death Becomes Us"].cost == 2
    assert shadow["Indiscriminate Provocation"].prerequisites == ()
    assert {
        shadow[name].cost
        for name in (
            "Indiscriminate Provocation",
            "Uno Reverse Card",
            "Night Moves",
            "Bullionaire",
        )
    } == {2}
    assert "Shade of Ahool" not in shadow
    assert "Eclipse" not in shadow
    assert abilities.ShadeOfAhool().name == "Shade of Ahool"
    assert abilities.Eclipse().school == "Shadow"
    assert {
        "Corruption 2",
        "Fine Print",
        "Controlled Corruption",
        "Patronage",
        "Abyssal Authority",
    } <= set(demon)
    assert demon["Soul Siphon"].prerequisites == ()
    assert demon["Dance of the Dead"].prerequisites == (demon["Soul Siphon"].id,)
    assert demon["Soul Asylum"].prerequisites == (demon["Desoul"].id,)
    assert "Corruption 2" not in _nodes("Warlock")
    assert not any(name.startswith("Tempered Corruption") for name in demon)


def test_demonologist_tree_has_five_authored_columns():
    nodes = _nodes("Demonologist")

    assert len(nodes) == 24
    assert nodes["Mystical Vitality"].position == (0, 0)
    assert nodes["Corruption 2"].payload["level_requirement"] == 70
    assert nodes["Persistent Corruption"].position == (0, 4)
    assert nodes["Controlled Corruption"].position == (1, 2)
    assert nodes["Patronage"].position == (1, 3)
    assert nodes["Abyssal Authority"].position == (1, 4)
    assert nodes["Contract Killer"].position == (1, 5)
    assert nodes["Firebolt"].position == (2, 0)
    assert nodes["Napalm"].payload["level_requirement"] == 75
    assert nodes["Soul Vessel"].position == (3, 3)
    assert nodes["Desoul"].position == (3, 4)
    assert nodes["Soul Asylum"].position == (3, 5)
    assert nodes["Soul Asylum"].payload["level_requirement"] == 85
    assert nodes["Flammable Affliction"].position == (4, 0)
    assert nodes["Demon Eyes"].prerequisites == (nodes["Monkey's Paw"].id,)
    assert nodes["Demon Eyes"].cost == 2
    assert nodes["Soul Asylum"].cost == 2
    assert nodes["Contract Killer"].cost == 2


def test_corruption_tick_can_jump_only_to_an_adjacent_enemy(monkeypatch):
    player = _player("Warlock")
    targets = [enemies.Goblin(), enemies.Goblin(), enemies.Goblin()]
    encounter = CombatEncounter.from_enemies(targets)
    player._combat_encounter = encounter
    source = targets[1]
    dot = source.magic_effects["DOT"]
    dot.active = True
    dot.duration = 2
    dot.extra = 7
    dot.source = "Corruption"
    warlock.mark_corruption(player, source)
    monkeypatch.setattr(warlock.random, "random", lambda: 0.0)
    monkeypatch.setattr(warlock.random, "choice", lambda choices: choices[0])
    monkeypatch.setattr("src.core.character.status.random.randint", lambda *_args: 0)

    message = source.effects()

    assert "Corruption jumps" in message
    assert targets[0].magic_effects["DOT"].active
    assert not targets[2].magic_effects["DOT"].active


def test_corruption_two_scales_with_unlocked_contracts():
    player = _player("Demonologist")
    player.demonologist_contracts = demonologist.default_state()
    player.demonologist_contracts["unlocked_contracts"] = [
        "Imp",
        "Quasit",
        "Incubus",
    ]
    player.demonologist_contracts["active_patron"] = "Imp"
    target = enemies.Goblin()

    abilities.Corruption2().cast(player, target)

    payload = target._corruption_payload
    assert payload["rank"] == 2
    assert payload["contracts"] == 3
    assert payload["jump_chance"] == pytest.approx(0.40)
    assert target.magic_effects["DOT"].duration == 4
    assert target.magic_effects["DOT"].extra >= 4


def test_resist_holy_uses_exploration_time_and_expires():
    player = _player("Warlock")
    spell = abilities.ResistHoly()
    mana_before = player.mana.current

    message = spell.cast_out(player)

    assert "100 steps" in message
    assert player.mana.current == mana_before - spell.cost
    assert player.check_mod("resist", typ="Holy") == pytest.approx(0.50)
    player.record_step(99)
    assert player.check_mod("resist", typ="Holy") == pytest.approx(0.50)
    player.record_step(1)
    assert player.check_mod("resist", typ="Holy") == pytest.approx(0.0)


def test_impending_demise_scales_shadow_bolt_by_remaining_doom_turns():
    player = _player("Warlock")
    target = enemies.Goblin()
    player.spellbook["Skills"]["Impending Demise"] = abilities.ImpendingDemise()
    doom = target.status_effects["Doom"]
    doom.active = True
    doom.duration = 2

    multiplier = mage_mechanics.spell_damage_multiplier(
        player,
        abilities.ShadowBolt(),
        target,
    )

    assert multiplier == pytest.approx(1.25)


def test_vim_and_rigor_strengthens_health_drain_against_a_full_target(monkeypatch):
    player = _player("Warlock")
    target = enemies.Goblin()
    player.health.current = player.health.max
    target.health.max = 100
    target.health.current = 100
    effect = DrainEffect()
    monkeypatch.setattr("random.randint", lambda _low, high: high)

    effect.apply(player, target, CombatResult("Health Drain"))
    baseline = 100 - target.health.current
    target.health.current = 100
    player.spellbook["Skills"]["Vim and Rigor"] = abilities.VimAndRigor()
    effect.apply(player, target, CombatResult("Health Drain"))

    assert 100 - target.health.current > baseline


def test_eclipse_is_a_warlock_shadow_spell_with_a_timed_form():
    player = _player("Warlock")
    base_speed = player.check_mod("speed")
    holy_before = player.check_mod("resist", typ="Holy")

    abilities.Eclipse().cast(player)

    assert player.warlock_eclipse_turns == 3
    assert player.check_mod("weapon") >= 0
    assert player.check_mod("speed") == int(base_speed * 1.10)
    assert player.check_mod("resist", typ="Holy") == pytest.approx(holy_before - 0.25)


def test_curse_of_swarms_ticks_repeatedly_and_spreads_afflictions(monkeypatch):
    player = _player("Warlock")
    targets = [enemies.Goblin(), enemies.Goblin()]
    player._combat_encounter = CombatEncounter.from_enemies(targets)
    source, nearby = targets
    abilities.CurseSwarms().cast(player, source)
    source.status_effects["Poison"].active = True
    source.status_effects["Poison"].duration = 3
    afflictions.apply_curse(source, "Frailty")
    monkeypatch.setattr(afflictions.random, "randint", lambda low, _high: low)
    monkeypatch.setattr(afflictions.random, "random", lambda: 0.0)
    monkeypatch.setattr(afflictions.random, "choice", lambda choices: choices[0])
    health_before = source.health.current

    message = afflictions.swarms_tick(source)

    assert source.health.current < health_before
    assert "4 times" in message
    assert nearby.status_effects["Poison"].active
    assert afflictions.has_curse(nearby, "Frailty")


def test_hemorrhaging_curse_deals_periodic_damage():
    player = _player("Warlock")
    target = enemies.Goblin()
    target.health.max = 100
    target.health.current = 100

    abilities.HemorrhagingCurse().cast(player, target)
    message = afflictions.hemorrhaging_tick(target)

    assert target.health.current == 96
    assert "open wounds bleed" in message


def test_mystical_vitality_reduces_spell_cost_after_life_tap():
    player = _player("Demonologist")
    player.spellbook["Skills"]["Mystical Vitality"] = abilities.MysticalVitality()
    player.mana.current = 0

    abilities.LifeTap().use(player, player)

    assert player.mystical_vitality_turns == 3
    assert mage_mechanics.spell_mana_cost(player, abilities.Netherchar()) == 21


def test_persistent_corruption_extends_and_strengthens_corruption_two():
    player = _player("Demonologist")
    target = enemies.Goblin()
    player.spellbook["Skills"]["Persistent Corruption"] = abilities.PersistentCorruption()

    abilities.Corruption2().cast(player, target)

    dot = target.magic_effects["DOT"]
    assert dot.duration >= 4
    assert dot.source == "Corruption"


def test_grease_missile_slows_and_amplifies_burn(monkeypatch):
    player = _player("Demonologist")
    target = enemies.Goblin()
    player.spellbook["Skills"]["Grease Missile"] = abilities.GreaseMissile()
    monkeypatch.setattr(demonologist.random, "random", lambda: 1.0)

    demonologist.process_spell_cast(player, abilities.ShadowBolt(), target)

    assert target.demon_grease_turns == 3
    assert target.stat_effects["Speed"].extra < 0


def test_contagious_blaze_damages_adjacent_enemies_and_spreads_corruption(monkeypatch):
    player = _player("Demonologist")
    targets = [enemies.Goblin(), enemies.Goblin()]
    source, nearby = targets
    player._combat_encounter = CombatEncounter.from_enemies(targets)
    player.spellbook["Skills"]["Contagious Blaze"] = abilities.ContagiousBlaze()
    source._corruption_payload = {"duration": 3, "damage": 4}
    monkeypatch.setattr(demonologist.random, "random", lambda: 0.0)
    health_before = nearby.health.current

    message = demonologist.process_spell_cast(player, abilities.Firebolt(), source)

    assert nearby.health.current < health_before
    assert nearby.magic_effects["DOT"].source == "Corruption"
    assert "explodes" in message


def test_napalm_consumes_netherchar_burn_for_immediate_damage():
    player = _player("Demonologist")
    target = enemies.Goblin()
    target.health.max = 500
    target.health.current = 500

    abilities.Netherchar().cast(player, target)
    health_after_char = target.health.current
    result = abilities.Napalm().cast(player, target)

    assert result.damage > 0
    assert target.health.current < health_after_char
    assert not target.magic_effects["DOT"].active


def test_demonic_curse_passives_amplify_umbra_and_hemorrhaging():
    player = _player("Demonologist")
    target = enemies.Goblin()
    target.health.max = 100
    target.health.current = 100
    player.spellbook["Skills"]["Flammable Affliction"] = abilities.FlammableAffliction()
    player.spellbook["Skills"]["Monkey's Paw"] = abilities.MonkeysPaw()

    abilities.CurseUmbra().cast(player, target)
    abilities.HemorrhagingCurse().cast(player, target)

    assert target.check_mod("resist", typ="Fire") == pytest.approx(-0.50)
    afflictions.hemorrhaging_tick(target)
    assert target.health.current == 94


def test_soul_vessel_consumes_a_gem_and_stabilizes_fatal_damage():
    from src.core import items

    player = _player("Demonologist")
    player.modify_inventory(items.SoulGem())

    assert "5 turns" in abilities.SoulVessel().use(player)
    assert not player.inventory.get("Soul Gem")
    player.health.current = 0

    assert player.is_alive()
    assert player.health.current == int(player.health.max * 0.25)
    assert player.mana.current == int(player.mana.max * 0.25)


def test_soul_asylum_and_dance_of_the_dead_use_swapped_spells():
    player = _player("Demonologist")
    player.spellbook["Skills"]["Soul Asylum"] = abilities.SoulAsylum()
    player.spellbook["Skills"]["Dance of the Dead"] = abilities.DanceOfTheDead()
    outcome = BattleOutcomeMixin()
    outcome.player = player

    desouled = enemies.Goblin()
    desouled._killed_by_ability = "Desoul"
    outcome._warlock_soul_reward(desouled)
    doomed = enemies.Goblin()
    doomed._killed_by_ability = "Doom"
    outcome._warlock_soul_reward(doomed)

    assert len(player.inventory["Soul Gem"]) == 1
    assert player.temporary_undead_allies[0]["name"] == doomed.name


def test_night_terror_increases_terrify_damage_more_against_sleeping_targets():
    player = _player("Shadowcaster")
    target = enemies.Goblin()
    player.spellbook["Skills"]["Night Terror"] = abilities.NightTerror()
    terrify = abilities.Terrify()

    awake = mage_mechanics.spell_damage_multiplier(player, terrify, target)
    target.status_effects["Sleep"].active = True
    sleeping = mage_mechanics.spell_damage_multiplier(player, terrify, target)

    assert abilities.NightTerror().passive
    assert awake == pytest.approx(1.25)
    assert sleeping == pytest.approx(1.50)


def test_alacrity_increases_speed_only_while_invisible():
    player = _player("Shadowcaster")
    base_speed = player.check_mod("speed")
    player.spellbook["Skills"]["Alacrity"] = abilities.Alacrity()

    assert player.check_mod("speed") == base_speed
    player.invisible = True
    assert player.check_mod("speed") == int(base_speed * 1.25)


def test_contract_modifiers_change_quotes_corruption_favor_and_strength():
    player = _player("Demonologist")
    target = enemies.Goblin()
    player.gold = 10_000
    player.demonologist_contracts = demonologist.default_state()
    player.demonologist_contracts["unlocked_contracts"] = ["Imp"]
    player.demonologist_contracts["active_patron"] = "Imp"
    base_quote = demonologist.quote_contract(player, target, "Harm")
    base_strength = demonologist.contract_strength(player, base_quote)

    for ability_type in (
        abilities.FinePrint,
        abilities.ControlledCorruption,
        abilities.Patronage,
        abilities.AbyssalAuthority,
    ):
        ability = ability_type()
        player.spellbook["Skills"][ability.name] = ability
    modified_quote = demonologist.quote_contract(player, target, "Harm")

    assert modified_quote["costs"]["gold"] < base_quote["costs"]["gold"]
    assert demonologist.contract_strength(player, modified_quote) > base_strength
    demonologist.add_corruption(player, modified_quote)
    assert player.demonologist_contracts["corruption"] == 3
    demonologist.adjust_patron_mood(player, "Imp", 3)
    assert player.demonologist_contracts["patron_moods"]["Imp"] == 5
