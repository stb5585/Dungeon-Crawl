TITLE: Dungeon Crawl (working title)

AUTHOR: Shawn Thomas Booth

CREATION DATE: March 2020

LANGUAGE: Python 3.11.6

DEPENDENCIES:
Standard
- curses
- dataclasses
- glob
- math
- os
- dill
- random
- re
- sys
- time
- typing

3rd Party
- numpy 2.0.1

EXECUTION:
- source launch.sh
 
DESCRIPTION:
- A dungeon crawl, text-based RPG that takes inspiration from many games. The current iteration allows for character 
  creation options from race and class selection, random statistical rolls, interactive town format, and 5-level dungeon
  crawl.  
  - Charisma is essentially a luck statistic, lowering cost and improving chance of success

FUTURE DEVELOPMENT:
- Planned development
    - Make item comparison easier for the shop
    - Add special item(s) for each final class
    - implement a TUI for better gameplay
    - add logic to enemies to make them smarter

- Possible development
    - Add shop_inventory dictionary; lowest level items will be available by default and subsequent items will need to 
      be farmed
    - Require rare items for promotion
    - Add a tutorial so players can better understand the gameplay
    - Create battle arena
    - Create tile types that have different effects (i.e. Stud tile which spawns enemies from a lower floor)

FILES:
- abilities.py
- character.py
- classes.py
- combat.py
- companions.py
- enemies.py
- game.py
- items.py
- map_tiles.py
- races.py
- README.md
- town.py
- tutorial.py
- world.py

FILE DESCRIPTIONS:
- abilities.py
    - Main file for controlling spells and skills of the character classes
- character.py
    - Main file for controlling the all characters, players, enemies, and companions
- classes.py
    - File that controls the classes available for new characters to choose from; includes function that checks whether 
      an item can be equipped by a player's class
- combat.py
    - Controls the combat system between the player and enemy
- companions.py
    - File that defines class companions (currently only Warlock familiars) 
- enemies.py
    - Main file for controlling enemies, including the statistics and unique aspects of each enemy
- game.py
    - The primary file for the game; controls how and when the game functions
- items.py
    - Main file for controlling items, including randomly generating for chests and drops
- map_tiles.py
    - Defines the room tiles of the world and available movement per each tile
- player.py
    - File for controlling the playable character, including all actions/interactions with the world
- races.py
    - File that outlines the various racial options when creating a new character
- README.md
    - General description of program
- town.py
    - Controls the interactions of the character while in town
- tutorial.py
    - File that controls the tutorial; not yet implemented
