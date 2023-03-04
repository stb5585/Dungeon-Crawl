TITLE: Dungeon Crawl (working title)

AUTHOR: Shawn Thomas Booth

CREATION DATE: March 2020

LANGUAGE: Python 3.6.7, iPython 7.5.0

DEPENDENCIES:
- pyfiglet 0.8 (pos1)
- numpy
- simple_term_menu

EXECUTION:
- python game.py
 
DESCRIPTION:
- A dungeon crawl, text-based RPG that takes inspiration from many games. The current iteration allows for character 
  creation options from race and class selection, random statistical rolls, interactive town format, and 5-level dungeon
  crawl.  
  - Charisma is essentially a luck statistic, lowering cost and improving chance of success

FUTURE DEVELOPMENT:
- Planned development
    - Enhance storyline for a more immersive experience
    - Deepen the dungeon to allow for additional challenge
    - Make item comparison easier for the shop
    - add inspection of item in inventory (print item information)
    - Add shop_inventory dictionary; lowest level items will be available by default and subsequent items will need to 
      be farmed
    - Add quests to game; add tavern in town for obtaining quests
    - Add more accessories with various effects; special items for each final class
    - Create tile types that have different effects (i.e. Stud tile which spawns enemies from a lower floor)
    - Allow player to switch characters in-game (instead of exiting and re-loading)
    - multiple players and enemies in battle

- Possible development
    - create new ranged class (archer -> hunter (tracking, pet)/ranger (sword and arrow)/arcane trickster (magical arrows)
    - create 3rd promotion classes (likely crossover class)
    - Item identification
    - Add capability to have more than one playable character
    - Require rare items for promotion
    - Give players alignments (G/N/E) with item restrictions
    - Add a tutorial so players can better understand the gameplay
    - Implement map editor
    - Create battle arena

FILES:
- actions.py
- character.py
- classes.py
- combat.py
- enemies.py
- game.py
- items.py
- map.py
- races.py
- README.md
- spells.py
- storyline.py
- town.py
- tutorial.py
- world.py

FILE DESCRIPTIONS:
- actions.py
    - Defines the various user-inputted actions, including hotkeys
- character.py
    - Main file for controlling the playable character, including all actions/interactions with the world
- classes.py
    - File that controls the classes available for new characters to choose from; includes function that checks whether 
      an item can be equipped by a player's class
- combat.py
    - Controls the combat system between the player and enemy
- enemies.py
    - Main file for controlling enemies, including the statistics and unique aspects of each enemy
- game.py
    - The primary file for the game; controls how and when the game functions
- items.py
    - Main file for controlling items, including randomly generating for chests and drops
- map.py
    - Defines the room tiles of the world and available movement per each tile
- races.py
    - File that outlines the various racial options when creating a new character
- README.md
    - General description of program
- spells.py
    - Main file for controlling spells and skills of the character classes
- storyline.py
    - File that is primarily used for user-input function; will eventually house the storyline
- town.py
    - Controls the interactions of the character while in town
- tutorial.py
    - File that controls the tutorial; not yet implemented
- world.py
    - World manager that defines the map tiles and returns the world dictionary for save files
