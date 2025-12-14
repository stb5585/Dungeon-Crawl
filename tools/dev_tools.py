#!/usr/bin/env python3
"""
Dungeon Crawl Development Tools CLI

This script provides command-line tools for development tasks:
- Balance testing and simulation
- Ability validation
- Combat analytics
- Event system testing
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def test_ability_loader(args):
    """Test loading abilities from data files."""
    from data.ability_loader import AbilityFactory
    
    print("Testing Ability Loader...")
    print("=" * 60)
    
    if args.directory:
        abilities = AbilityFactory.load_abilities_from_directory(args.directory)
        print(f"\nLoaded {len(abilities)} abilities:")
        for name, ability in abilities.items():
            print(f"  - {name}: {ability.description[:50]}...")
    
    if args.file:
        ability = AbilityFactory.create_from_yaml(args.file)
        print(f"\nLoaded ability: {ability.name}")
        print(f"Type: {ability.typ}")
        print(f"Cost: {ability.cost}")
        print(f"Description: {ability.description}")
        print(f"Effects: {len(getattr(ability, '_data_driven_effects', []))}")


def test_event_system(args):
    """Test the event system."""
    from events import EventBus, EventType, ConsoleEventLogger
    
    print("Testing Event System...")
    print("=" * 60)
    
    bus = EventBus()
    
    if args.verbose:
        # Add console logger
        logger = ConsoleEventLogger(bus)
    
    # Emit some test events
    bus.emit_simple(
        EventType.COMBAT_START,
        data={'player': 'TestPlayer', 'enemy': 'TestEnemy'}
    )
    
    bus.emit_simple(
        EventType.DAMAGE_DEALT,
        data={'actor': 'TestPlayer', 'target': 'TestEnemy', 'damage': 25}
    )
    
    bus.emit_simple(
        EventType.COMBAT_END,
        data={'winner': 'TestPlayer'}
    )
    
    print(f"\nEmitted {len(bus.get_history())} events")
    
    if not args.verbose:
        print("\nEvent History:")
        for event in bus.get_history():
            print(f"  - {event.type.name}: {event.data}")


def run_balance_test(args):
    """Run combat balance simulations."""
    from analytics import CombatSimulator
    
    print("Running Balance Tests...")
    print("=" * 60)
    
    print("\nNote: Full simulation requires actual character instances.")
    print("This is a placeholder for the balance testing framework.")
    
    simulator = CombatSimulator()
    print(f"\nSimulator initialized. Ready for {args.iterations} iterations.")
    
    # Would need actual character creation here
    # For now, just demonstrate the structure


def test_action_queue(args):
    """Test the action queue system."""
    from combat import ActionQueue, ActionType, ActionPriority
    
    print("Testing Action Queue System...")
    print("=" * 60)
    
    queue = ActionQueue()
    
    # Create mock actions
    def mock_action(**kwargs):
        actor = kwargs.get('actor')
        target = kwargs.get('target')
        return f"{actor} acts on {target}"
    
    # Mock characters
    class MockChar:
        def __init__(self, name, dex):
            self.name = name
            self.stats = type('obj', (object,), {'dex': dex})()
    
    char1 = MockChar("Fast Fighter", dex=18)
    char2 = MockChar("Slow Mage", dex=10)
    
    # Schedule some actions
    queue.schedule(
        char1, ActionType.ATTACK, mock_action,
        target=char2, priority=ActionPriority.HIGH
    )
    
    queue.schedule(
        char2, ActionType.SPELL, mock_action,
        target=char1, priority=ActionPriority.NORMAL,
        delay=1
    )
    
    queue.schedule(
        char1, ActionType.SKILL, mock_action,
        target=char2, priority=ActionPriority.NORMAL
    )
    
    print(f"\nScheduled {len(queue.queue)} actions")
    
    print("\nAction Queue (sorted by priority and speed):")
    for i, action in enumerate(queue.queue):
        print(f"  {i+1}. {action.actor.name}: {action.action_type.value} "
              f"(Priority: {action.priority.name}, Delay: {action.delay})")
    
    print("\nResolving actions...")
    round_num = 1
    while queue.has_ready_actions():
        action = queue.get_next_action()
        if action:
            print(f"  Round {round_num}: {action.actor.name} uses {action.action_type.value}")
            round_num += 1
        else:
            queue.next_round()


def test_effects(args):
    """Test the effect system."""
    from effects import (
        DamageEffect,
        AttackBuffEffect,
        CompositeEffect,
        ChanceEffect,
    )
    
    print("Testing Effect System...")
    print("=" * 60)
    
    print("\nAvailable Effect Types:")
    print("  - DamageEffect")
    print("  - HealEffect")
    print("  - BuffEffects (Attack, Defense, Magic, Speed)")
    print("  - DebuffEffects")
    print("  - StatusEffect")
    print("  - DamageOverTimeEffect")
    print("  - CompositeEffect (combine multiple effects)")
    print("  - ChanceEffect (probabilistic effects)")
    print("  - ConditionalEffect")
    print("  - LifestealEffect")
    print("  - ShieldEffect")
    
    print("\nExample: Composite Effect (Damage + Buff)")
    damage = DamageEffect(base_damage=20, scaling=1.5)
    buff = AttackBuffEffect(amount=10, duration=3)
    composite = CompositeEffect([damage, buff])
    print(f"  Created composite with {len(composite.effects)} effects")
    
    print("\nExample: Chance Effect (30% to apply status)")
    from effects import StatusEffect
    status = StatusEffect(name="Stun", duration=2)
    chance_effect = ChanceEffect(status, chance=0.3)
    print(f"  Created chance effect with {chance_effect.chance * 100}% probability")


def generate_sample_abilities(args):
    """Generate sample ability YAML files."""
    from data.ability_loader import save_example_abilities
    
    output_dir = args.output or 'data/abilities'
    
    print(f"Generating sample ability files in {output_dir}...")
    print("=" * 60)
    
    save_example_abilities(output_dir)
    
    print("\nGenerated sample abilities. You can modify these YAML files to create new abilities!")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Dungeon Crawl Development Tools',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test loading abilities from data files
  python dev_tools.py abilities --directory data/abilities
  
  # Test a specific ability file
  python dev_tools.py abilities --file data/abilities/fireball.yaml
  
  # Test the event system with verbose logging
  python dev_tools.py events --verbose
  
  # Test the action queue system
  python dev_tools.py queue
  
  # Test the effect system
  python dev_tools.py effects
  
  # Run balance simulations (placeholder)
  python dev_tools.py balance --iterations 1000
  
  # Generate sample ability YAML files
  python dev_tools.py generate --output data/abilities
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Abilities command
    abilities_parser = subparsers.add_parser('abilities', help='Test ability loader')
    abilities_parser.add_argument('--directory', '-d', help='Directory containing ability files')
    abilities_parser.add_argument('--file', '-f', help='Specific ability file to test')
    
    # Events command
    events_parser = subparsers.add_parser('events', help='Test event system')
    events_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    # Balance command
    balance_parser = subparsers.add_parser('balance', help='Run balance simulations')
    balance_parser.add_argument('--iterations', '-i', type=int, default=100, help='Number of simulations')
    balance_parser.add_argument('--class', dest='char_class', help='Class to test')
    balance_parser.add_argument('--level', type=int, default=10, help='Level to test at')
    
    # Queue command
    queue_parser = subparsers.add_parser('queue', help='Test action queue system')
    
    # Effects command
    effects_parser = subparsers.add_parser('effects', help='Test effect system')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate sample ability files')
    generate_parser.add_argument('--output', '-o', help='Output directory')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Route to appropriate function
    if args.command == 'abilities':
        test_ability_loader(args)
    elif args.command == 'events':
        test_event_system(args)
    elif args.command == 'balance':
        run_balance_test(args)
    elif args.command == 'queue':
        test_action_queue(args)
    elif args.command == 'effects':
        test_effects(args)
    elif args.command == 'generate':
        generate_sample_abilities(args)


if __name__ == '__main__':
    main()
