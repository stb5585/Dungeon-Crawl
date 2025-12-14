# Development Tools

## dev_tools.py

Command-line interface for testing and developing game systems.

### Usage

```bash
# From project root
python3 tools/dev_tools.py [command] [options]

# Or with virtual environment
.venv/bin/python tools/dev_tools.py [command] [options]
```

### Commands

#### Test Effect System
```bash
python3 tools/dev_tools.py effects
```
Shows all available effect types and demonstrates composite effects.

#### Test Action Queue
```bash
python3 tools/dev_tools.py queue
```
Demonstrates priority-based turn ordering and action scheduling.

#### Test Event System
```bash
python3 tools/dev_tools.py events [--verbose]
```
Shows event emission and subscription. Use `--verbose` for detailed logging.

#### Test Ability Loader
```bash
# Load all abilities from directory
python3 tools/dev_tools.py abilities --directory data/abilities

# Load specific ability file
python3 tools/dev_tools.py abilities --file data/abilities/fireball.yaml
```
Tests YAML ability loading and displays parsed ability data.

#### Generate Sample Abilities
```bash
python3 tools/dev_tools.py generate --output data/abilities
```
Creates example ability YAML files for reference.

#### Balance Simulations
```bash
python3 tools/dev_tools.py balance --iterations 1000
```
Runs combat simulations for balance testing (requires Character instances).

### Help
```bash
python3 tools/dev_tools.py --help
python3 tools/dev_tools.py [command] --help
```

## modify_save.py

Utility script for modifying save files.

### Usage

Edit the script to specify:
- `save_file` - Path to save file to modify
- Player attribute modifications

```bash
python3 tools/modify_save.py
```

**⚠️ Warning**: Always backup save files before modifying!

## Running from Different Directories

Both tools expect to be run from the project root directory. If you need to run from elsewhere:

```bash
cd /path/to/Dungeon-Crawl
python3 tools/dev_tools.py [command]
```

Or adjust Python path:
```python
import sys
sys.path.insert(0, '/path/to/Dungeon-Crawl')
```
