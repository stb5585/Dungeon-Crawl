"""Concrete Character class composed from focused behavior mixins."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .defense import CharacterDefenseMixin
from .events import CharacterEventsMixin
from .models import Combat, Level, Resource, Stats, StatusEffect
from .offense import CharacterOffenseMixin
from .status import CharacterStatusMixin
from .utility import CharacterUtilityMixin

if TYPE_CHECKING:
    from .models import AbilityBook, EffectMap, InventoryMap


class Character(
    CharacterEventsMixin,
    CharacterStatusMixin,
    CharacterOffenseMixin,
    CharacterDefenseMixin,
    CharacterUtilityMixin,
):
    """
    A class representing a character in a game, encapsulating attributes such as health,
    status effects, and combat-related properties.

    Attributes:
        name (str): The name of the character.
        race (object): The race of the character.
        cls (object): The class of the character.
        level (Level): A dataclass containing the level, promotion level, experience, and experience to gain of the character.
        health (Resource): A dataclass containing the maximum and current health of the character.
        mana (Resource): A dataclass containing the maximum and current mana of the character.
        stats (Stats): A dataclass containing the 6 primary statistics of the character.
        combat (Combat): A dataclass containing the 4 primary combat stats of the character.
        gold (int): how much gold the character possesses
        equipment (dict[str, object]): A dictionary containing the items which the character is currently equipped.
        inventory (dict[str, list[object, int]]): A dictionary containing the character's inventory, including the item
            and quantity.
        special_inventory (dict[str, list[object, int]]): A dictionary containing the character's special inventory,
            including the item and quantity. The special inventory stores items that are related to quests or the plot
            of the story.
        spellbook (dict[str, dict[str, Spell]]): A dictionary containing the spells and skills learned for the
            character to use.
        status_effects (dict[str, StatusEffect]): A dictionary containing the character's status effects.
        status_immunity (list[str]): A list of all status effects the character is immune against.
        resistance (dict[str, float]): A dictionary containing the elemental impact on the character.
        flying (bool): A boolean variable indicating whether the character is flying or not. Flying affects chance
            to hit and some elemental effect.
        invisible (bool): A boolean variable indicating whether the character is invisible or not. Invisibility
            affects chance to hit.
    Methods:
        __init__():
            Initializes a Character object.

        effects(end=False):
            Manages and updates the character's effects, applying their respective consequences/benefits
            and handling the end of combat.
    """

    def __init__(
        self, name: str, health: Resource, mana: Resource, stats: Stats, combat: Combat
    ) -> None:
        self.name = name
        self.race = None
        self.cls = None
        self.level = Level(1, 1, 0, 0)
        self.health = health
        self.mana = mana
        self.stats = stats
        self.combat = combat
        self.gold: int = 0
        self.equipment: dict[str, object] = {}
        self.inventory: InventoryMap = {}
        self.spellbook: AbilityBook = {"Spells": {}, "Skills": {}}
        self.status_effects: EffectMap = {
            "Berserk": StatusEffect(False, 0),
            "Blind": StatusEffect(False, 0),
            "Blind Rage": StatusEffect(False, 0),
            "Hangover": StatusEffect(False, 0),
            "Doom": StatusEffect(False, 0),
            "Poison": StatusEffect(False, 0, 0),
            "Silence": StatusEffect(False, 0),
            "Sleep": StatusEffect(False, 0),
            "Fear": StatusEffect(False, 0),
            "Fractured": StatusEffect(False, 0),
            "Stun": StatusEffect(False, 0),
            "Polymorph": StatusEffect(False, 0),
            "Defend": StatusEffect(False, 0, 0),
            "Steal Success": StatusEffect(False, 0),
            "Peaceful": StatusEffect(False, 0),
            "Shapeshifted": StatusEffect(False, 0),
        }
        self.physical_effects: EffectMap = {
            "Bleed": StatusEffect(False, 0, 0),
            "Cripple": StatusEffect(False, 0, 0),
            "Disarm": StatusEffect(False, 0),
            "Maim": StatusEffect(False, 0),
            "Prone": StatusEffect(False, 0),
        }
        self.stat_effects: EffectMap = {
            "Attack": StatusEffect(False, 0, 0),
            "Defense": StatusEffect(False, 0, 0),
            "Magic": StatusEffect(False, 0, 0),
            "Magic Defense": StatusEffect(False, 0, 0),
            "Speed": StatusEffect(False, 0, 0),
        }
        self.magic_effects: EffectMap = {
            "DOT": StatusEffect(False, 0, 0),
            "Duplicates": StatusEffect(False, 0),
            "Ice Block": StatusEffect(False, 0),
            "Mana Shield": StatusEffect(False, 0),
            "Reflect": StatusEffect(False, 0),
            "Regen": StatusEffect(False, 0, 0),
            "Resist Fire": StatusEffect(False, 0, 0),
            "Resist Ice": StatusEffect(False, 0, 0),
            "Resist Electric": StatusEffect(False, 0, 0),
            "Resist Water": StatusEffect(False, 0, 0),
            "Resist Earth": StatusEffect(False, 0, 0),
            "Resist Wind": StatusEffect(False, 0, 0),
            "Resist Shadow": StatusEffect(False, 0, 0),
            "Resist Holy": StatusEffect(False, 0, 0),
            "Hallowed Ground": StatusEffect(False, 0, 0),
            "Stone Skin": StatusEffect(False, 0),
            "Nature Shield": StatusEffect(False, 0, 0),
            "Tree of Life": StatusEffect(False, 0),
            "Totem": StatusEffect(False, 0),
            "Astral Shift": StatusEffect(False, 0),
        }
        self.class_effects: EffectMap = {
            "Jump": StatusEffect(False, 0),
            "Power Up": StatusEffect(False, 0, 0),
            "Drunken Brawler": StatusEffect(False, 0, 0),
            "Last Stand": StatusEffect(False, 0, 0),
        }
        self.status_immunity: list[str] = []
        self.persistent_curses: dict[str, dict[str, object]] = {}
        self.fractures: dict[str, int] = {}
        self.resistance: dict[str, float] = {
            "Fire": 0.0,
            "Ice": 0.0,
            "Electric": 0.0,
            "Water": 0.0,
            "Earth": 0.0,
            "Wind": 0.0,
            "Shadow": 0.0,
            "Holy": 0.0,
            "Nature": 0.0,
            "Poison": 0.0,
            "Physical": 0.0,
        }
        self.anti_magic_active = False
        self.flying = False
        self.invisible = False
        self.sight = False
        self.turtle = False
        self.tunnel = False
        self.enter_wall = False

        # Defensive stance settings
        self.defensive_stance_reduction = 0.25

        # Passive ability tracking
        self.maelstrom_hits = 0  # Track consecutive hits for Maelstrom Weapon ability
        # Evasive Guard (Footpad): stacks build when hit, reset on dodge.
        self.evasive_guard_stacks = 0
