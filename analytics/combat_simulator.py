"""
Combat Analytics Module

This module provides tools for analyzing combat balance, simulating battles,
and generating reports for game balancing purposes.
"""

from __future__ import annotations

import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from character import Character


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
            Dict with 'overpowered' and 'underpowered' classes
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
        char1: Character,
        char2: Character,
        max_turns: int = 100
    ) -> CombatStats:
        """
        Simulate a single battle between two characters.
        
        Args:
            char1: First combatant
            char2: Second combatant
            max_turns: Maximum turns before declaring a draw
            
        Returns:
            Combat statistics from the battle
        """
        # Clone characters so we don't modify originals
        # This is a simplified simulation - would need actual combat logic
        # For now, this is a placeholder structure
        
        turns = 0
        abilities_used = defaultdict(int)
        status_applied = defaultdict(int)
        crits = 0
        misses = 0
        
        # Placeholder: Simple turn-based damage calculation
        c1_hp = char1.health.current
        c2_hp = char2.health.current
        
        while c1_hp > 0 and c2_hp > 0 and turns < max_turns:
            turns += 1
            
            # Simplified: Each character attacks based on attack stat
            # This would be replaced with actual combat logic
            import random
            
            # Char1 attacks
            damage1 = max(0, char1.combat.attack - char2.combat.defense // 2)
            damage1 = int(damage1 * random.uniform(0.8, 1.2))
            c2_hp -= damage1
            
            if c2_hp <= 0:
                break
            
            # Char2 attacks
            damage2 = max(0, char2.combat.attack - char1.combat.defense // 2)
            damage2 = int(damage2 * random.uniform(0.8, 1.2))
            c1_hp -= damage2
        
        # Determine winner
        if c1_hp > 0:
            winner = char1.name
            loser = char2.name
            winner_class = char1.cls.name if hasattr(char1, 'cls') else 'Unknown'
            loser_class = char2.cls.name if hasattr(char2, 'cls') else 'Unknown'
            winner_hp = c1_hp
            winner_max = char1.health.max
        else:
            winner = char2.name
            loser = char1.name
            winner_class = char2.cls.name if hasattr(char2, 'cls') else 'Unknown'
            loser_class = char1.cls.name if hasattr(char1, 'cls') else 'Unknown'
            winner_hp = c2_hp
            winner_max = char2.health.max
        
        return CombatStats(
            winner=winner,
            loser=loser,
            winner_class=winner_class,
            loser_class=loser_class,
            winner_level=char1.level.level if winner == char1.name else char2.level.level,
            loser_level=char2.level.level if loser == char2.name else char1.level.level,
            turns=turns,
            winner_hp_remaining=winner_hp,
            winner_hp_max=winner_max,
            total_damage_dealt=0,  # Would track in real simulation
            total_damage_taken=0,
            abilities_used=dict(abilities_used),
            status_effects_applied=dict(status_applied),
            critical_hits=crits,
            misses=misses,
        )
    
    def run_simulations(
        self,
        char1: Character,
        char2: Character,
        iterations: int = 1000
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
        
        for _ in range(iterations):
            result = self.simulate_battle(char1, char2)
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
