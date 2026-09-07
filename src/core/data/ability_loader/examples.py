"""Example ability definitions and YAML export helper."""

from pathlib import Path

import yaml

# Example ability definitions for testing
EXAMPLE_ABILITIES = {
    "fireball": {
        "name": "Fireball",
        "type": "Spell",
        "subtype": "Offensive",
        "description": "Launches a ball of fire at the enemy",
        "cost": 15,
        "damage_mod": 1.5,
        "effects": [
            {
                "type": "damage",
                "base": 25,
                "scaling": {"stat": "intelligence", "ratio": 1.5},
                "element": "Fire",
            },
            {
                "type": "chance",
                "chance": 0.3,
                "effect": {
                    "type": "dot",
                    "dot_type": "Burn",
                    "damage_per_tick": 5,
                    "duration": 3,
                    "element": "Fire",
                },
            },
        ],
    },
    "blessing": {
        "name": "Blessing",
        "type": "Spell",
        "subtype": "Support",
        "description": "Increases attack and defense",
        "cost": 12,
        "effects": [
            {"type": "buff", "stat": "attack", "amount": 10, "duration": 5},
            {"type": "buff", "stat": "defense", "amount": 8, "duration": 5},
        ],
    },
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
        with open(file_path, "w") as f:
            yaml.dump(ability_data, f, default_flow_style=False, sort_keys=False)
        print(f"Saved {ability_data['name']} to {file_path}")
