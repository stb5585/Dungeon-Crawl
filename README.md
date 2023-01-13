TITLE: Dungeon Crawl (working title)

AUTHOR: Shawn Thomas Booth

CREATION DATE: March 2020

LANGUAGE: Python 3.6.7, iPython 7.5.0

DEPENDENCIES:
- pygame 2.0.0 (dev4)
- pyfiglet 0.8 (pos1)
- jsonpickle 1.3
- numpy

EXECUTION:
- ipython game.py
 
DESCRIPTION:
- A dungeon crawl, text-based RPG that takes inspiration from many different games. The current iteration allows for character creation options from race and class selection, random statistical rolls, interactive town format, and 5-level dungeon crawl.  

FUTURE DEVELOPMENT:
- Planned development
    - Enhance storyline for a more immersive experience
    - Deepen the dungeon to allow for additional challenge
    - Add graphical representation (in terminal) for a more complete game experience; already improved minimap
    - Make item comparison easier for the shop
    - Add shop_inventory dictionary; lowest level items will be available by default and subsequent items will need to be farmed
    - Add quests to game; add tavern in town for obtaining quests
    - Enhance enemies to make them more dynamic (resistance/weakness, etc)
    - Add more accessories with various effects; special items for each final class
    - Create tile types that have different effects (i.e. Stud tile which spawns enemies from a lower floor)
    - Allow player to switch characters in-game (instead of exiting and re-loading)

- Possible development
    - Item identification
    - Add capability to have more than one playable character
    - Require rare items for promotion
    - Allow a character to change class
    - Give players alignments (G/N/E) with item restrictions
    - Add a tutorial so players can better understand the gameplay
    - Implement map editor 


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
    - File that controls the classes available for new characters to choose from; includes function that checks whether an item can be equipped by a player's class
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
    - General desciption of program
- spells.py
    - Main file for controlling spells and skills of the character classes
- storyline.py
    - File that is primarily used for user-input function; will eventually house the storyline
- town.py
    - Controls the iteractions of the character while in town
- tutorial.py
    - File that controls the tutorial; not yet implemented
- world.py
    - World manager that defines the map tiles and returns the world dictionary for save files
