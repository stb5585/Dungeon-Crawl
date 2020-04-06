TITLE: Dungeon Crawl (working title)

AUTHOR: Shawn Thomas Booth

CREATION DATE: March 2020

LANGUAGE: Python 3.6.7, iPython 7.5.0

DEPENDENCIES: pygame 2.0 or greater

EXECUTION:
- ipython game.py
 
DESCRIPTION:
- A dungeon crawl, text-based RPG that takes inspiration from many different games. The current iteration allows for character creation options from race and class selection, random statistical rolls, interactive town format, and 5-level dungeon crawl.  

FUTURE DEVELOPMENT:
- Planned development
    - Enhance storyline for a more immersive experience
    - Add promotion to other classes available to characters once they reach a certain level; may require a particular item to complete
    - Deepen the dungeon to allow for additional challenge
    - Balance the character/dungeon difficulty to improve playability
    - Add a tutorial so players can better understand the gameplay
    - Adapt skill functionality for non-mage characters that do not cast spells
    - Add graphical representation for a more complete game experience
    - Make item comparison easier for both equipping and the shop
    - Add shop_inventory dictionary; online lowest level items will be available by default and subsequent items will need to be farmed
    - Have enemies respawn (either when entering town or after an amount of time); reset world tiles

- Possible development
    - Status effects
    - Item identification
    - Add capability to have more than one playable character
    - Make the dungeon tiles all random (even the map creation)

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
