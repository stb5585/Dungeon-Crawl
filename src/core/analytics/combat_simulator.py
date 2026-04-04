"""
Combat Analytics Module

This module provides tools for analyzing combat balance, simulating battles,
and generating reports for game balancing purposes.
"""

from __future__ import annotations

import copy
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from src.core.character import Character
    from src.core.player import Player


def _combat_level(ch: object) -> int:
    try:
        lvl = getattr(ch, "level", 1)
    except Exception:
        return 1
    try:
        nested_level = getattr(lvl, "level")
    except AttributeError:
        nested_level = None
    except Exception:
        return 1
    else:
        try:
            return int(nested_level)
        except Exception:
            return 1
    try:
        return int(lvl)
    except Exception:
        return 1


@dataclass
class CombatStats:
    """Statistics from a single combat encounter."""
    winner: str
    loser: str
    winner_class: str
    loser_class: str
    winner_level: int
    loser_level: int
    turns: int
    winner_hp_remaining: int
    winner_hp_max: int
    total_damage_dealt: int
    total_damage_taken: int
    abilities_used: dict[str, int] = field(default_factory=dict)
    status_effects_applied: dict[str, int] = field(default_factory=dict)
    critical_hits: int = 0
    misses: int = 0
    
    @property
    def hp_remaining_percent(self) -> float:
        """Percentage of HP remaining for winner."""
        if self.winner_hp_max == 0:
            return 0.0
        return (self.winner_hp_remaining / self.winner_hp_max) * 100
    
    @property
    def was_close(self) -> bool:
        """Was this a close fight? (winner had < 30% HP)"""
        return self.hp_remaining_percent < 30


@dataclass
class BalanceReport:
    """
    Comprehensive report on combat balance from multiple simulations.
    """
    total_battles: int
    results: list[CombatStats]
    
    def __post_init__(self):
        self._win_rates: dict[str, float] = {}
        self._calculate_metrics()
    
    def _calculate_metrics(self) -> None:
        """Pre-calculate common metrics."""
        if not self.results:
            return
        
        # Win rates by class
        wins_by_class = defaultdict(int)
        total_by_class = defaultdict(int)
        
        for result in self.results:
            wins_by_class[result.winner_class] += 1
            total_by_class[result.winner_class] += 1
            total_by_class[result.loser_class] += 1
        
        for cls, wins in wins_by_class.items():
            total = total_by_class[cls]
            self._win_rates[cls] = (wins / total) * 100 if total > 0 else 0
    
    @property
    def win_rates(self) -> dict[str, float]:
        """Win rate percentage by class."""
        return self._win_rates
    
    @property
    def average_turns(self) -> float:
        """Average number of turns per battle."""
        if not self.results:
            return 0.0
        return statistics.mean(r.turns for r in self.results)
    
    @property
    def median_turns(self) -> float:
        """Median number of turns per battle."""
        if not self.results:
            return 0.0
        return statistics.median(r.turns for r in self.results)
    
    @property
    def close_fight_rate(self) -> float:
        """Percentage of fights that were close (< 30% HP remaining)."""
        if not self.results:
            return 0.0
        close_fights = sum(1 for r in self.results if r.was_close)
        return (close_fights / len(self.results)) * 100
    
    @property
    def stomp_rate(self) -> float:
        """Percentage of fights that were stomps (> 90% HP remaining)."""
        if not self.results:
            return 0.0
        stomps = sum(1 for r in self.results if r.hp_remaining_percent > 90)
        return (stomps / len(self.results)) * 100
    
    def get_ability_usage(self) -> dict[str, int]:
        """Get total usage count for each ability across all battles."""
        usage = defaultdict(int)
        for result in self.results:
            for ability, count in result.abilities_used.items():
                usage[ability] += count
        return dict(usage)
    
    def get_most_used_abilities(self, limit: int = 10) -> list[tuple[str, int]]:
        """Get the most frequently used abilities."""
        usage = self.get_ability_usage()
        return sorted(usage.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_status_effect_frequency(self) -> dict[str, int]:
        """Get frequency of status effects applied across all battles."""
        freq = defaultdict(int)
        for result in self.results:
            for effect, count in result.status_effects_applied.items():
                freq[effect] += count
        return dict(freq)
    
    def identify_outliers(self, threshold: float = 2.0) -> dict[str, list]:
        """
        Identify statistical outliers in the data.
        
        Args:
            threshold: Number of standard deviations to consider an outlier
            
        Returns:
            Dictionary with 'overpowered' and 'underpowered' classes
        """
        if len(self._win_rates) < 2:
            return {'overpowered': [], 'underpowered': []}
        
        mean_wr = statistics.mean(self._win_rates.values())
        stdev_wr = statistics.stdev(self._win_rates.values())
        
        overpowered = []
        underpowered = []
        
        for cls, win_rate in self._win_rates.items():
            z_score = (win_rate - mean_wr) / stdev_wr if stdev_wr > 0 else 0
            
            if z_score > threshold:
                overpowered.append((cls, win_rate, z_score))
            elif z_score < -threshold:
                underpowered.append((cls, win_rate, z_score))
        
        return {
            'overpowered': sorted(overpowered, key=lambda x: x[2], reverse=True),
            'underpowered': sorted(underpowered, key=lambda x: x[2])
        }
    
    def generate_summary(self) -> str:
        """Generate a text summary of the balance report."""
        lines = [
            "=" * 60,
            "COMBAT BALANCE REPORT",
            "=" * 60,
            f"Total Battles: {self.total_battles}",
            f"Average Turns: {self.average_turns:.2f}",
            f"Median Turns: {self.median_turns:.2f}",
            f"Close Fight Rate: {self.close_fight_rate:.1f}%",
            f"Stomp Rate: {self.stomp_rate:.1f}%",
            "",
            "Win Rates by Class:",
            "-" * 40,
        ]
        
        for cls, win_rate in sorted(
            self._win_rates.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            lines.append(f"  {cls:20s} {win_rate:6.2f}%")
        
        outliers = self.identify_outliers()
        
        if outliers['overpowered']:
            lines.extend([
                "",
                "⚠️  Overpowered Classes:",
                "-" * 40,
            ])
            for cls, win_rate, z_score in outliers['overpowered']:
                lines.append(f"  {cls:20s} {win_rate:6.2f}% (z={z_score:.2f})")
        
        if outliers['underpowered']:
            lines.extend([
                "",
                "⚠️  Underpowered Classes:",
                "-" * 40,
            ])
            for cls, win_rate, z_score in outliers['underpowered']:
                lines.append(f"  {cls:20s} {win_rate:6.2f}% (z={z_score:.2f})")
        
        lines.extend([
            "",
            "Most Used Abilities:",
            "-" * 40,
        ])
        
        for ability, count in self.get_most_used_abilities(5):
            lines.append(f"  {ability:30s} {count:5d} uses")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


class CombatSimulator:
    """
    Simulates combat encounters for balance testing.
    
    This is a simplified simulator that doesn't require the full game infrastructure.
    """
    
    def __init__(self):
        self.results: list[CombatStats] = []

    def simulate_battle(
        self,
        char1: Player,
        char2: Character,
        max_turns: int = 200,
        *,
        seed: int | None = None,
        char1_policy: Callable | None = None,
        char2_policy: Callable | None = None,
        include_flee: bool = False,
    ) -> CombatStats:
        """
        Simulate a single battle using the real BattleEngine.

        Args:
            char1: Player-side combatant (BattleEngine expects a Player)
            char2: Enemy-side combatant (any Character)
            max_turns: Maximum turns before declaring a draw
            seed: Optional RNG seed for determinism
            char1_policy: Optional policy(engine) -> (action, choice)
            char2_policy: Optional policy(engine) -> (action, choice)
            include_flee: If True, allow Flee to be selected by policies

        Returns:
            Combat statistics from the battle
        """
        import random

        from src.core.combat.battle_engine import BattleEngine
        from src.core.events.event_bus import EventType, get_event_bus, reset_event_bus

        if seed is not None:
            random.seed(seed)

        # Isolate global event bus per simulation to avoid cross-test pollution.
        reset_event_bus()
        event_bus = get_event_bus()

        abilities_used: dict[str, int] = defaultdict(int)
        status_applied: dict[str, int] = defaultdict(int)
        crits = 0
        misses = 0
        damage_by_actor: dict[str, int] = defaultdict(int)

        def on_event(ev) -> None:
            nonlocal crits, misses
            try:
                if ev.type == EventType.SPELL_CAST:
                    nm = ev.data.get("spell_name")
                    if nm:
                        abilities_used[str(nm)] += 1
                elif ev.type == EventType.SKILL_USE:
                    nm = ev.data.get("skill_name")
                    if nm:
                        abilities_used[str(nm)] += 1
                elif ev.type == EventType.ATTACK:
                    abilities_used["Attack"] += 1
                elif ev.type == EventType.STATUS_APPLIED:
                    nm = ev.data.get("status_name")
                    if nm:
                        status_applied[str(nm)] += 1
                elif ev.type == EventType.CRITICAL_HIT:
                    crits += 1
                elif ev.type == EventType.MISS:
                    misses += 1
                elif ev.type == EventType.DAMAGE_DEALT:
                    actor = ev.data.get("actor")
                    dmg = int(ev.data.get("damage", 0) or 0)
                    if actor and dmg > 0:
                        damage_by_actor[str(actor)] += dmg
            except Exception:
                return

        for et in [
            EventType.SPELL_CAST,
            EventType.SKILL_USE,
            EventType.ATTACK,
            EventType.STATUS_APPLIED,
            EventType.CRITICAL_HIT,
            EventType.MISS,
            EventType.DAMAGE_DEALT,
        ]:
            event_bus.subscribe(et, on_event)

        class _SimTile:
            def __init__(self):
                self.enemy = char2
                self.defeated = False

            def available_actions(self, _player):
                actions = ["Attack", "Cast Spell", "Use Skill", "Defend", "Use Item"]
                if include_flee:
                    actions.append("Flee")
                if getattr(char1, "summons", None):
                    actions.append("Summon")
                    actions.append("Recall")
                # Totem/Transform are implemented as top-level actions in BattleEngine.
                try:
                    if "Totem" in getattr(char1, "spellbook", {}).get("Skills", {}):
                        actions.append("Totem")
                except Exception:
                    pass
                try:
                    if "Transform" in getattr(char1, "spellbook", {}).get("Skills", {}):
                        actions.append("Transform")
                        actions.append("Untransform")
                except Exception:
                    pass
                return actions

            def __str__(self) -> str:
                return "SimTile"

        tile = _SimTile()
        engine = BattleEngine(player=char1, enemy=char2, tile=tile)
        engine.start_battle()

        def default_policy(_engine: BattleEngine):
            attacker = _engine.attacker
            defender = _engine.defender
            if attacker is None or defender is None:
                return "Attack", None

            # Meta-actions (summons/totems) first: these are major class-defining levers.
            try:
                if (
                    attacker == char1
                    and "Summon" in _engine.available_actions
                    and getattr(char1, "summons", None)
                    and not getattr(_engine, "summon_active", False)
                ):
                    # Summon the first available companion deterministically.
                    choice = next(iter(char1.summons.keys()))
                    return "Summon", choice
            except Exception:
                pass
            try:
                if (
                    attacker == char1
                    and "Totem" in _engine.available_actions
                    and not (attacker.magic_effects.get("Totem") and attacker.magic_effects["Totem"].active)
                ):
                    return "Totem", None
            except Exception:
                pass

            def _is_combat_offense(ab) -> bool:
                """
                Best-effort classifier for "worth spending a turn on" actions.

                The base game has many non-damaging combat-legal abilities
                (buffs, utility, resource conversion). For analytics we want a
                policy that doesn't soft-lock on e.g. Mana Tap spam.
                """
                if ab is None or getattr(ab, "passive", False):
                    return False
                if getattr(ab, "combat", True) is False:
                    return False
                nm = str(getattr(ab, "name", "") or "")
                if nm in {"Inspect", "Reveal", "Teleport", "Sanctuary"}:
                    return False
                typ = str(getattr(ab, "typ", "") or "")
                sub = str(getattr(ab, "subtyp", "") or "")
                if typ == "Movement" or sub in {"Truth", "Movement"}:
                    return False
                # Treat explicit heals/support as non-offensive for selection.
                if sub in {"Heal", "Support"}:
                    return False

                # Weapon-based skills are almost always offensively useful.
                if bool(getattr(ab, "weapon", False)):
                    return True

                # Data-driven abilities expose effect objects; classify those.
                effects = getattr(ab, "_effects", None)
                if effects:
                    non_offense = {
                        "ResourceConvertEffect",
                        "HealEffect",
                        "RegenEffect",
                        "ShieldEffect",
                        "AttackBuffEffect",
                        "DefenseBuffEffect",
                        "MagicBuffEffect",
                        "SpeedBuffEffect",
                        "MultiStatBuffEffect",
                        "ResistanceEffect",
                        "DynamicStatBuffEffect",
                        "CleanseEffect",
                        "DispelEffect",
                        "FullDispelEffect",
                        "MagicEffectApplyEffect",
                        "MagicEffectToggleEffect",
                        "PowerUpActivateEffect",
                        "SetFlagEffect",
                        "InspectEffect",
                        "RevealEffect",
                        "TotemEffect",
                        "TransformEffect",
                        "ResurrectionEffect",
                        "ConsumeItemEffect",
                        "DestroyMetalEffect",
                    }
                    for eff in effects:
                        if type(eff).__name__ not in non_offense:
                            return True
                    return False

                return True

            def _is_damage_ability(ab) -> bool:
                """Return True if the ability is likely to affect enemy HP."""
                if ab is None:
                    return False
                if bool(getattr(ab, "weapon", False)):
                    return True
                effects = getattr(ab, "_effects", None)
                if not effects:
                    return False
                for eff in effects:
                    nm = type(eff).__name__
                    # Explicit non-damaging utility effects.
                    if nm in {"StealEffect", "MugEffect", "InspectEffect", "RevealEffect"}:
                        continue
                    # Common damage indicators.
                    if (
                        "Damage" in nm
                        or "Drain" in nm
                        or "Lifesteal" in nm
                        or "Kill" in nm
                        or nm in {
                            "GoldTossEffect",
                            "SlotMachineEffect",
                            "LickEffect",
                            "GoblinPunchEffect",
                            "CrushEffect",
                            "DisintegrateEffect",
                            "DevourEffect",
                            "StompEffect",
                            "BreathDamageEffect",
                        }
                        or any(k in nm for k in ("Punch", "Crush", "Lick", "Toss", "Breath", "Devour", "Stomp"))
                    ):
                        return True
                return False

            # Heal when low (self-targeting heal spells are handled by engine)
            try:
                hp_pct = attacker.health.current / max(1, attacker.health.max)
            except Exception:
                hp_pct = 1.0
            try:
                mp_pct = attacker.mana.current / max(1, attacker.mana.max)
            except Exception:
                mp_pct = 1.0

            # Use items under pressure (keeps simulator closer to real PvE play).
            # This is intentionally conservative: only fire when resources are critical.
            try:
                inv = getattr(attacker, "inventory", {}) or {}

                def _best_item(subtyp: str) -> str | None:
                    best_key = None
                    best_score = -1.0
                    for key, lst in inv.items():
                        if not lst:
                            continue
                        itm = lst[0]
                        if getattr(itm, "subtyp", None) != subtyp:
                            continue
                        # Prefer larger % potions when available.
                        score = float(getattr(itm, "percent", 0.0) or 0.0)
                        if score > best_score:
                            best_score = score
                            best_key = key
                    return best_key

                if "Use Item" in _engine.available_actions and inv:
                    # If both HP/MP are critical and we have an elixir, prefer it.
                    if hp_pct <= 0.25 and mp_pct <= 0.20:
                        el = _best_item("Elixir")
                        if el:
                            return "Use Item", el
                    if hp_pct <= 0.25:
                        hp = _best_item("Health")
                        if hp:
                            return "Use Item", hp
                    # Mana potions: only if we are resource-starved and could plausibly cast something.
                    if mp_pct <= 0.15 and (not attacker.status_effects.get("Silence") or not attacker.status_effects["Silence"].active):
                        mp = _best_item("Mana")
                        if mp:
                            return "Use Item", mp
            except Exception:
                pass

            if (
                hp_pct < 0.35
                and "Spells" in attacker.spellbook
                and not attacker.status_effects["Silence"].active
            ):
                for nm, sp in attacker.spellbook["Spells"].items():
                    if getattr(sp, "subtyp", "") in ["Heal", "Support"]:
                        if getattr(attacker, "mana", None) and attacker.mana.current >= getattr(sp, "cost", 0):
                            return "Cast Spell", nm

            # Note: "Smoke Screen" is primarily an escape tool (it triggers flee logic in BattleEngine),
            # so the simulator intentionally does not use it as a defensive/accuracy-denial opener.

            # Offensive spell if affordable
            if "Spells" in attacker.spellbook and not attacker.status_effects["Silence"].active:
                for nm, sp in attacker.spellbook["Spells"].items():
                    if _is_combat_offense(sp) and _is_damage_ability(sp):
                        if attacker.mana.current >= getattr(sp, "cost", 0):
                            return "Cast Spell", nm
                for nm, sp in attacker.spellbook["Spells"].items():
                    if _is_combat_offense(sp):
                        if attacker.mana.current >= getattr(sp, "cost", 0):
                            return "Cast Spell", nm

            # Offensive skill if affordable
            if "Skills" in attacker.spellbook:
                def _skill_score(name: str, ab) -> float:
                    # Avoid analytics degeneracy: these are valuable in the real game,
                    # but in the simulator they often waste turns and swamp results.
                    # Avoid analytics degeneracy: these are valuable in the real game,
                    # but in the simulator they waste turns or end fights early.
                    if name in {"Steal", "Mug", "Inspect", "Reveal", "Smoke Screen"}:
                        return -1e9
                    # Don't spam Disarm into natural weapons / already-disarmed targets.
                    if name == "Disarm":
                        try:
                            if getattr(defender, "physical_effects", {}).get("Disarm") and defender.physical_effects["Disarm"].active:
                                return -1e9
                            if hasattr(defender, "can_be_disarmed") and not defender.can_be_disarmed():
                                return -1e9
                        except Exception:
                            return -1e9
                    score = 0.0
                    if _is_damage_ability(ab):
                        score += 100.0
                    if bool(getattr(ab, "weapon", False)):
                        score += 50.0
                    # Prefer status/control over pure utility when it's the best available.
                    if name in {"Pocket Sand", "Sleeping Powder", "Disarm"}:
                        score += 10.0
                    return score

                best = None
                best_score = -1e9
                for nm, sk in attacker.spellbook["Skills"].items():
                    if not _is_combat_offense(sk):
                        continue
                    if attacker.mana.current < getattr(sk, "cost", 0):
                        continue
                    sc = _skill_score(nm, sk)
                    if sc > best_score:
                        best_score = sc
                        best = nm
                if best is not None and best_score > -1e8:
                    return "Use Skill", best

            return "Attack", None

        turns = 0
        while engine.battle_continues() and turns < max_turns:
            turns += 1
            pre = engine.pre_turn()
            if pre.can_act:
                forced = engine.get_forced_action()
                if forced:
                    action, choice = forced.action, forced.choice
                else:
                    if engine.is_player_turn():
                        policy = char1_policy or default_policy
                        try:
                            action, choice = policy(engine)
                        except Exception:
                            action, choice = "Attack", None
                    else:
                        # By default, let enemies use their real AI (action_stack / priority rules)
                        # rather than the player-centric default_policy.
                        if char2_policy is not None:
                            try:
                                action, choice = char2_policy(engine)
                            except Exception:
                                action, choice = "Attack", None
                        else:
                            action, choice = engine.get_enemy_action()
                engine.execute_action(action, choice)
            engine.companion_turn()
            engine.post_turn()
            engine.swap_turns()

        # Outcome (avoid engine.end_battle bookkeeping for analytics)
        if turns >= max_turns and char1.is_alive() and char2.is_alive():
            winner = "draw"
            loser = "draw"
            winner_obj = char1
            loser_obj = char2
        elif not char1.is_alive() and not char2.is_alive():
            winner = "draw"
            loser = "draw"
            winner_obj = char1
            loser_obj = char2
        elif char1.is_alive():
            winner = char1.name
            loser = char2.name
            winner_obj = char1
            loser_obj = char2
        else:
            winner = char2.name
            loser = char1.name
            winner_obj = char2
            loser_obj = char1

        winner_class = winner_obj.cls.name if hasattr(winner_obj, "cls") and winner_obj.cls else "Unknown"
        loser_class = loser_obj.cls.name if hasattr(loser_obj, "cls") and loser_obj.cls else "Unknown"
        winner_hp = max(0, winner_obj.health.current)
        winner_max = winner_obj.health.max

        return CombatStats(
            winner=winner,
            loser=loser,
            winner_class=winner_class,
            loser_class=loser_class,
            winner_level=_combat_level(winner_obj),
            loser_level=_combat_level(loser_obj),
            turns=turns,
            winner_hp_remaining=winner_hp,
            winner_hp_max=winner_max,
            total_damage_dealt=sum(damage_by_actor.values()),
            total_damage_taken=0,
            abilities_used=dict(abilities_used),
            status_effects_applied=dict(status_applied),
            critical_hits=crits,
            misses=misses,
        )
    
    def run_simulations(
        self,
        char1: Player | Callable[[], Player],
        char2: Character | Callable[[], Character],
        iterations: int = 1000,
        *,
        seed: int | None = None,
    ) -> BalanceReport:
        """
        Run multiple simulations between two characters.
        
        Args:
            char1: First combatant
            char2: Second combatant
            iterations: Number of battles to simulate
            
        Returns:
            Balance report with aggregated statistics
        """
        results = []

        base_seed = seed if seed is not None else None
        for i in range(iterations):
            # Seed *before* constructing factory characters so any randomized
            # initial stats/equipment are part of the deterministic run.
            if base_seed is not None:
                import random
                random.seed(base_seed + i)
            if callable(char1):
                c1 = char1()
            else:
                try:
                    c1 = copy.deepcopy(char1)
                except Exception:
                    c1 = char1

            if callable(char2):
                c2 = char2()
            else:
                try:
                    c2 = copy.deepcopy(char2)
                except Exception:
                    c2 = char2

            sim_seed = None if base_seed is None else (base_seed + i)
            result = self.simulate_battle(c1, c2, seed=sim_seed)
            results.append(result)
        
        self.results.extend(results)
        
        return BalanceReport(
            total_battles=iterations,
            results=results
        )


def quick_balance_test(class_name: str, level: int = 10) -> BalanceReport:
    """
    Quick helper function to test a class against all other classes.
    
    Args:
        class_name: Name of the class to test
        level: Level to test at
        
    Returns:
        Balance report
    """
    # This would need to be implemented with actual character creation
    # Placeholder for now
    pass
