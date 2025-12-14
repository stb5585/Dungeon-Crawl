"""
Data-Driven Ability System

This module provides a factory for creating abilities from data files (YAML/JSON).
This allows for easy balancing and modding without changing code.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from effects import (
    DamageEffect,
    HealEffect,
    StatusEffect,
    AttackBuffEffect,
    DefenseBuffEffect,
    MagicBuffEffect,
    DamageOverTimeEffect,
    CompositeEffect,
    ChanceEffect,
)

if TYPE_CHECKING:
    from abilities import Ability
    from effects.base import Effect


class EffectFactory:
    """
    Factory for creating Effect objects from data definitions.
    """
    
    @staticmethod
    def create(effect_data: dict) -> Effect:
        """
        Create an Effect from a data dictionary.
        
        Args:
            effect_data: Dictionary containing effect definition
            
        Returns:
            Effect instance
            
        Example effect_data:
            {
                'type': 'damage',
                'base': 20,
                'scaling': {
                    'stat': 'strength',
                    'ratio': 1.5
                },
                'element': 'Fire'
            }
        """
        effect_type = effect_data.get('type', '').lower()
        
        if effect_type == 'damage':
            return EffectFactory._create_damage(effect_data)
        elif effect_type == 'heal':
            return EffectFactory._create_heal(effect_data)
        elif effect_type == 'status':
            return EffectFactory._create_status(effect_data)
        elif effect_type == 'buff':
            return EffectFactory._create_buff(effect_data)
        elif effect_type == 'debuff':
            return EffectFactory._create_debuff(effect_data)
        elif effect_type == 'dot':
            return EffectFactory._create_dot(effect_data)
        elif effect_type == 'composite':
            return EffectFactory._create_composite(effect_data)
        elif effect_type == 'chance':
            return EffectFactory._create_chance(effect_data)
        else:
            raise ValueError(f"Unknown effect type: {effect_type}")
    
    @staticmethod
    def _create_damage(data: dict) -> DamageEffect:
        """Create a damage effect."""
        base = data.get('base', 0)
        scaling = data.get('scaling', {})
        scaling_ratio = scaling.get('ratio', 0.0) if scaling else 0.0
        
        return DamageEffect(
            base_damage=base,
            scaling=scaling_ratio
        )
    
    @staticmethod
    def _create_heal(data: dict) -> HealEffect:
        """Create a healing effect."""
        base = data.get('base', 0)
        scaling = data.get('scaling', {})
        scaling_ratio = scaling.get('ratio', 0.0) if scaling else 0.0
        
        return HealEffect(
            base_healing=base,
            scaling=scaling_ratio
        )
    
    @staticmethod
    def _create_status(data: dict) -> StatusEffect:
        """Create a status effect."""
        name = data.get('name', 'Unknown')
        duration = data.get('duration', 1)
        
        return StatusEffect(name=name, duration=duration)
    
    @staticmethod
    def _create_buff(data: dict) -> Effect:
        """Create a buff effect."""
        stat = data.get('stat', 'attack').lower()
        amount = data.get('amount', 0)
        duration = data.get('duration', 3)
        
        if stat == 'attack':
            return AttackBuffEffect(amount, duration)
        elif stat == 'defense':
            return DefenseBuffEffect(amount, duration)
        elif stat == 'magic':
            return MagicBuffEffect(amount, duration)
        else:
            raise ValueError(f"Unknown buff stat: {stat}")
    
    @staticmethod
    def _create_debuff(data: dict) -> Effect:
        """Create a debuff effect."""
        # Similar to buff but with negative amounts
        stat = data.get('stat', 'attack').lower()
        amount = data.get('amount', 0)
        duration = data.get('duration', 3)
        
        from effects.buffs import AttackDebuffEffect, DefenseDebuffEffect, MagicDebuffEffect
        
        if stat == 'attack':
            return AttackDebuffEffect(amount, duration)
        elif stat == 'defense':
            return DefenseDebuffEffect(amount, duration)
        elif stat == 'magic':
            return MagicDebuffEffect(amount, duration)
        else:
            raise ValueError(f"Unknown debuff stat: {stat}")
    
    @staticmethod
    def _create_dot(data: dict) -> DamageOverTimeEffect:
        """Create a damage-over-time effect."""
        dot_type = data.get('dot_type', 'Poison')
        damage_per_tick = data.get('damage_per_tick', 5)
        duration = data.get('duration', 3)
        element = data.get('element', 'Physical')
        
        return DamageOverTimeEffect(
            dot_type=dot_type,
            damage_per_tick=damage_per_tick,
            duration=duration,
            element=element
        )
    
    @staticmethod
    def _create_composite(data: dict) -> CompositeEffect:
        """Create a composite effect (multiple effects combined)."""
        effect_list = data.get('effects', [])
        effects = [EffectFactory.create(e) for e in effect_list]
        return CompositeEffect(effects)
    
    @staticmethod
    def _create_chance(data: dict) -> ChanceEffect:
        """Create a chance-based effect."""
        chance = data.get('chance', 0.5)
        inner_effect_data = data.get('effect', {})
        inner_effect = EffectFactory.create(inner_effect_data)
        
        return ChanceEffect(inner_effect, chance)


class AbilityFactory:
    """
    Factory for creating Ability objects from data definitions.
    """
    
    @staticmethod
    def create_from_dict(ability_data: dict):
        """
        Create an Ability from a data dictionary.
        
        Args:
            ability_data: Dictionary containing ability definition
            
        Returns:
            Ability-like object (SimpleAbility dataclass)
            
        Example ability_data:
            {
                'name': 'Fireball',
                'type': 'Spell',
                'subtype': 'Offensive',
                'description': 'A powerful fire spell',
                'cost': 15,
                'damage_mod': 1.5,
                'effects': [...]
            }
        """
        from dataclasses import dataclass, field
        from typing import List, Any
        
        @dataclass
        class SimpleAbility:
            """Simplified ability structure for data-driven abilities."""
            name: str
            typ: str
            subtyp: str
            description: str
            cost: int
            dmg_mod: float
            effects: List[Any] = field(default_factory=list)
        
        name = ability_data.get('name', 'Unknown')
        description = ability_data.get('description', '')
        cost = ability_data.get('cost', 0)
        ability_type = ability_data.get('type', 'Skill')
        subtype = ability_data.get('subtype', 'Offensive')
        damage_mod = ability_data.get('damage_mod', 1.0)
        
        # Create effects
        effects = []
        if 'effects' in ability_data:
            for effect_data in ability_data['effects']:
                effects.append(EffectFactory.create(effect_data))
        
        # Create simple ability object
        ability = SimpleAbility(
            name=name,
            typ=ability_type,
            subtyp=subtype,
            description=description,
            cost=cost,
            dmg_mod=damage_mod,
            effects=effects
        )
        
        return ability
    
    @staticmethod
    def create_from_yaml(file_path: str | Path):
        """
        Load an ability from a YAML file.
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            Ability instance
        """
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return AbilityFactory.create_from_dict(data)
    
    @staticmethod
    def load_abilities_from_directory(directory: str | Path) -> dict:
        """
        Load all abilities from a directory of YAML files.
        
        Args:
            directory: Path to directory containing ability definitions
            
        Returns:
            Dictionary mapping ability names to Ability objects
        """
        directory_path = Path(directory)
        abilities = {}
        
        for file_path in directory_path.glob('*.yaml'):
            try:
                ability = AbilityFactory.create_from_yaml(file_path)
                abilities[ability.name] = ability
            except Exception as e:
                print(f"Error loading ability from {file_path}: {e}")
        
        return abilities


# Example ability definitions for testing
EXAMPLE_ABILITIES = {
    'fireball': {
        'name': 'Fireball',
        'type': 'Spell',
        'subtype': 'Offensive',
        'description': 'Launches a ball of fire at the enemy',
        'cost': 15,
        'damage_mod': 1.5,
        'effects': [
            {
                'type': 'damage',
                'base': 25,
                'scaling': {
                    'stat': 'intelligence',
                    'ratio': 1.5
                },
                'element': 'Fire'
            },
            {
                'type': 'chance',
                'chance': 0.3,
                'effect': {
                    'type': 'dot',
                    'dot_type': 'Burn',
                    'damage_per_tick': 5,
                    'duration': 3,
                    'element': 'Fire'
                }
            }
        ]
    },
    'power_strike': {
        'name': 'Power Strike',
        'type': 'Skill',
        'subtype': 'Offensive',
        'description': 'A powerful melee attack',
        'cost': 10,
        'damage_mod': 2.0,
        'effects': [
            {
                'type': 'damage',
                'base': 15,
                'scaling': {
                    'stat': 'strength',
                    'ratio': 2.0
                },
                'element': 'Physical'
            }
        ]
    },
    'blessing': {
        'name': 'Blessing',
        'type': 'Spell',
        'subtype': 'Support',
        'description': 'Increases attack and defense',
        'cost': 12,
        'effects': [
            {
                'type': 'buff',
                'stat': 'attack',
                'amount': 10,
                'duration': 5
            },
            {
                'type': 'buff',
                'stat': 'defense',
                'amount': 8,
                'duration': 5
            }
        ]
    }
}


def save_example_abilities(output_dir: str | Path) -> None:
    """
    Save example ability definitions to YAML files.
    Useful for creating initial data files.
    
    Args:
        output_dir: Directory to save the files to
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for ability_id, ability_data in EXAMPLE_ABILITIES.items():
        file_path = output_path / f"{ability_id}.yaml"
        with open(file_path, 'w') as f:
            yaml.dump(ability_data, f, default_flow_style=False, sort_keys=False)
        print(f"Saved {ability_data['name']} to {file_path}")
