##########################################
""" character manager """

from __future__ import annotations

import random
from dataclasses import dataclass
from math import exp

from .constants import (
    ACCURACY_RING_BONUS,
    ARMOR_SCALING_FACTOR,
    MAGIC_DEF_SCALING_FACTOR,
    ASTRAL_SHIFT_REDUCTION,
    BASE_CRIT_PER_POINT,
    BASE_FLEE_CHANCE,
    BERSERK_HIT_PENALTY,
    BLIND_RAGE_HIT_PENALTY,
    BLIND_ACCURACY_PENALTY,
    DWARF_HANGOVER_DODGE_MULTIPLIER,
    ELF_BLIND_PENALTY_MULTIPLIER,
    ELF_HEALING_RECEIVED_MULTIPLIER,
    ELF_INVISIBLE_PENALTY_MULTIPLIER,
    GNOME_ENCUMBERED_DODGE_MULTIPLIER,
    GNOME_ENCUMBERED_HIT_MULTIPLIER,
    HALF_ELF_CRIT_SPIKE_MULTIPLIER,
    HALF_ELF_HEALING_RECEIVED_MULTIPLIER,
    DAMAGE_VARIANCE_HIGH,
    DAMAGE_VARIANCE_LOW,
    DISARM_HIT_PENALTY,
    ENCUMBERED_HIT_MULTIPLIER,
    FLYING_ACCURACY_PENALTY,
    HALF_ORC_BLIND_RAGE_CHANCE,
    HALF_ORC_BLIND_RAGE_DURATION,
    HALF_ORC_CRIT_DAMAGE_TAKEN_MULTIPLIER,
    HUMAN_STATUS_RESIST_MULTIPLIER,
    INVISIBLE_ACCURACY_PENALTY,
    MAELSTROM_CRIT_PER_HIT,
    MAX_DODGE_CHANCE,
    MAX_FLEE_CHANCE,
    PRO_LEVEL_HIT_MODIFIER,
    SEEKER_CRIT_BONUS,
    WEAPON_CRIT_WEIGHT,
    MAX_CRIT_CHANCE,
)

POISON_HEALING_MULTIPLIER = 0.70
BLEED_MELEE_DAMAGE_TAKEN_MULTIPLIER = 1.20
STUN_IMMUNITY_TURNS_AFTER_EXPIRY = 1
STUN_LEVEL_DIFF_SCALE = 0.04
STUN_LEVEL_DIFF_CAP = 8
STUN_LEVEL_DIFF_MULT_MIN = 0.70
STUN_LEVEL_DIFF_MULT_MAX = 1.30


def _combat_level(ch: object) -> int:
    """
    Best-effort combat level accessor.

    Player: ``player.level.level``
    Enemy: often ``enemy.level`` (int)
    """
    lvl = getattr(ch, "level", 1)
    if hasattr(lvl, "level"):
        try:
            return int(lvl.level)
        except Exception:
            return 1
    try:
        return int(lvl)
    except Exception:
        return 1


# functions
def sigmoid(x: float) -> float:
    return 1 / (1 + exp(-x))


def scaled_decay_function(x: float, rate: float = 0.1) -> float:
    """
    Returns a value between 0 and 1 that decreases as x increases.
    Used for shop price adjustments based on charisma.
    
    Args:
        x (float): The input value, must be >= 0.
        rate (float): The rate of decay; higher values make it decrease faster.

    Returns:
        float: A value between 0 and 1.
    """
    if x < 0:
        raise ValueError("x must be non-negative.")
    decay_value = 1 / (1 + rate * x)  # Exponential decay
    return 0.5 + decay_value * 0.75  # Scale and shift to fit [0.5, 1.25]


# Character dataclasses
@dataclass
class Stats:
    """
    Attributes:
        strength: The strength attribute of the character, influencing physical damage.
        intel: The intelligence attribute of a character, influencing magical damage.
        wisdom: The wisdom attribute of the character, influencing resistance to magical effects.
        con: The constitution attribute of the character, influencing resistance to certain effects.
        charisma: The charisma attribute of the character, influencing interactions with NPCs.
        dex: The dexterity attribute of the character, influencing speed and avoidance.
    """
    strength: int = 0
    intel: int = 0
    wisdom: int = 0
    con: int = 0
    charisma: int = 0
    dex: int = 0

@dataclass
class Combat:
    """
    Combat Stats:
        attack: base attack stat for calculating melee damage
        defense: base defense stat for calculating damage reduction
        magic: base stat for calculating magic damage
        magic_def: base stat for calculating magic damage reduction
    """
    attack: int = 0
    defense: int = 0
    magic: int = 0
    magic_def: int = 0

@dataclass
class Resource:
    max: int = 0
    current: int = 0

@dataclass
class Level:
    level: int = 1
    pro_level: int = 1
    exp: int = 0
    exp_to_gain: int = 25

@dataclass
class StatusEffect:
    active: bool = False
    duration: int = 0
    extra: int = 0


class Character:
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


    def __init__(self, name: str, health: Resource, mana: Resource, stats: Stats, combat: Combat):
        self.name = name
        self.race = None
        self.cls = None
        self.level = Level(1, 1, 0, 0)
        self.health = health
        self.mana = mana
        self.stats = stats
        self.combat = combat
        self.gold = 0
        self.equipment = {}
        self.inventory = {}
        self.spellbook = {'Spells': {},
                          'Skills': {}}
        self.status_effects = {"Berserk": StatusEffect(False, 0),
                                "Blind": StatusEffect(False, 0),
                                "Blind Rage": StatusEffect(False, 0),
                                "Hangover": StatusEffect(False, 0),
                                "Doom": StatusEffect(False, 0),
                                "Poison": StatusEffect(False, 0, 0),
                                "Silence": StatusEffect(False, 0),
                                "Sleep": StatusEffect(False, 0),
                                "Stun": StatusEffect(False, 0),
                                "Defend": StatusEffect(False, 0, 0),
                                "Steal Success": StatusEffect(False, 0),
                                "Shapeshifted": StatusEffect(False, 0)}
        self.physical_effects = {"Bleed": StatusEffect(False, 0, 0),
                                 "Disarm": StatusEffect(False, 0),
                                 "Prone": StatusEffect(False, 0)}
        self.stat_effects = {"Attack": StatusEffect(False, 0, 0),
                             "Defense": StatusEffect(False, 0, 0),
                             "Magic": StatusEffect(False, 0, 0),
                             "Magic Defense": StatusEffect(False, 0, 0),
                             "Speed": StatusEffect(False, 0, 0)}
        self.magic_effects = {"DOT": StatusEffect(False, 0, 0),
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
                              "Totem": StatusEffect(False, 0),
                              "Astral Shift": StatusEffect(False, 0)}
        self.class_effects = {"Jump": StatusEffect(False, 0),
                              "Power Up": StatusEffect(False, 0, 0)}
        self.status_immunity = []
        self.resistance = {'Fire': 0.,
                           'Ice': 0.,
                           'Electric': 0.,
                           'Water': 0.,
                           'Earth': 0.,
                           'Wind': 0.,
                           'Shadow': 0.,
                           'Holy': 0.,
                           "Poison": 0.,
                           'Physical': 0.}
        self.anti_magic_active = False
        self.flying = False
        self.invisible = False
        self.sight = False
        self.turtle = False
        self.tunnel = False

        # Defensive stance settings
        self.defensive_stance_reduction = 0.25

        # Passive ability tracking
        self.maelstrom_hits = 0  # Track consecutive hits for Maelstrom Weapon ability
        # Evasive Guard (Footpad): stacks build when hit, reset on dodge.
        self.evasive_guard_stacks = 0

    def abilities_suppressed(self) -> bool:
        return bool(self.status_effects["Silence"].active or getattr(self, "anti_magic_active", False))
    
    def _emit_damage_event(self, target: Character, damage: int, damage_type: str = "Physical", is_critical: bool = False) -> None:
        """Helper to emit damage dealt events."""
        try:
            from .events.event_bus import get_event_bus, create_combat_event, EventType
            event_bus = get_event_bus()
            event_bus.emit(create_combat_event(
                EventType.DAMAGE_DEALT if damage > 0 else EventType.MISS,
                actor=self,
                target=target,
                damage=damage,
                damage_type=damage_type,
                is_critical=is_critical
            ))
        except Exception:
            pass
    
    def _emit_healing_event(self, amount: int, source: str = "Unknown") -> None:
        """Helper to emit healing events."""
        try:
            from .events.event_bus import get_event_bus, create_combat_event, EventType
            event_bus = get_event_bus()
            event_bus.emit(create_combat_event(
                EventType.HEALING_DONE,
                actor=self,
                target=self,
                amount=amount,
                source=source
            ))
        except Exception:
            pass
    
    def _emit_status_event(self, target: Character, status_name: str, applied: bool, duration: int = 0, source: str = "Unknown") -> None:
        """Helper to emit status effect events."""
        try:
            from .events.event_bus import get_event_bus, create_combat_event, EventType
            event_bus = get_event_bus()
            event_bus.emit(create_combat_event(
                EventType.STATUS_APPLIED if applied else EventType.STATUS_REMOVED,
                actor=self,
                target=target,
                status_name=status_name,
                duration=duration,
                source=source
            ))
        except Exception:
            pass

    def _emit_status_tick_event(
        self,
        target: Character,
        status_name: str,
        amount: int,
        kind: str,
        source: str = "Unknown",
    ) -> None:
        """Emit a status tick (damage/heal) event for analytics/tests."""
        try:
            from .events.event_bus import get_event_bus, create_combat_event, EventType
            event_bus = get_event_bus()
            event_bus.emit(create_combat_event(
                EventType.STATUS_TICK,
                actor=self,
                target=target,
                status_name=status_name,
                amount=amount,
                kind=kind,
                source=source,
            ))
        except Exception:
            pass

    def enter_defensive_stance(self, duration: int = 1, reduction: float | None = None, source: str = "Defend") -> str:
        """
        Put the character into a defensive stance for a number of turns.

        Args:
            duration: Number of turns the stance lasts
            reduction: Optional damage reduction percentage (0.0 - 1.0)
            source: Source name for status event logging

        Returns:
            str: Message describing the stance
        """
        if reduction is None:
            reduction = self.defensive_stance_reduction

        self.status_effects["Defend"].active = True
        self.status_effects["Defend"].duration = max(self.status_effects["Defend"].duration, duration)
        self.status_effects["Defend"].extra = reduction
        self._emit_status_event(self, "Defend", applied=True, duration=duration, source=source)

        return f"{self.name} takes a defensive stance.\n"

    def get_defensive_reduction(self) -> float:
        """Return total defensive damage reduction from stances/modifiers."""
        reduction = 0.0
        if self.status_effects.get("Defend") and self.status_effects["Defend"].active:
            reduction += float(self.status_effects["Defend"].extra)
        if hasattr(self, "jump_defend_active") and self.jump_defend_active:
            reduction += 0.15
        return min(0.75, reduction)

    def incapacitated(self) -> bool:
        return any([self.status_effects["Sleep"].active,
                    self.physical_effects["Prone"].active,
                    self.status_effects["Stun"].active])

    def check_active(self) -> tuple[bool, str]:
        """
        Check if the character can act in combat this turn.
        
        Returns:
            tuple: (is_active: bool, message: str)
                  - (True, "") if character can act
                  - (False, reason) if character cannot act
        """
        if self.incapacitated():
            return False, f"{self.name} is incapacitated."
        if self.magic_effects["Ice Block"].active:
            return False, f"{self.name} is encased in ice and does nothing.\n"
        return True, ""

    def healing_received_multiplier(self) -> float:
        """Return multiplier applied to healing received (e.g., poison reduces healing)."""
        mult = 1.0
        if self.status_effects.get("Poison") and self.status_effects["Poison"].active:
            mult *= POISON_HEALING_MULTIPLIER
        # Racial traits (7 sins / 7 virtues)
        try:
            race_name = getattr(getattr(self, "race", None), "name", None)
            if race_name == "Elf":
                mult *= ELF_HEALING_RECEIVED_MULTIPLIER
            elif race_name == "Half Elf":
                mult *= HALF_ELF_HEALING_RECEIVED_MULTIPLIER
        except Exception:
            pass
        return mult

    # ── Economy helpers (used by both UIs) ────────────────────────────
    def shop_price_scale(self) -> float:
        """Return multiplicative scale applied to shop buy prices based on charisma (race-aware)."""
        cha = int(getattr(self.stats, "charisma", 0) or 0)
        try:
            if getattr(getattr(self, "race", None), "name", None) == "Gnome":
                from .constants import GNOME_GOLD_CHARISMA_MULTIPLIER
                cha = int(cha * GNOME_GOLD_CHARISMA_MULTIPLIER)
        except Exception:
            pass
        return scaled_decay_function(cha // 2)

    def shop_sell_price_multiplier(self) -> float:
        """Return multiplicative scale applied to shop sell prices based on charisma (race-aware)."""
        cha = int(getattr(self.stats, "charisma", 0) or 0)
        try:
            if getattr(getattr(self, "race", None), "name", None) == "Gnome":
                from .constants import GNOME_GOLD_CHARISMA_MULTIPLIER
                cha = int(cha * GNOME_GOLD_CHARISMA_MULTIPLIER)
        except Exception:
            pass
        return 1.0 + (0.025 * cha)

    def apply_stun(
        self,
        duration: int,
        *,
        source: str = "Unknown",
        applier: Character | None = None,
    ) -> bool:
        """
        Apply stun with basic stun-lock prevention.

        Uses ``status_effects["Stun"].extra`` as a short post-stun immunity
        counter (decremented in ``effects()`` each turn when not stunned).
        """
        stun = self.status_effects.get("Stun")
        if stun is None:
            return False
        if stun.active:
            return False
        if stun.extra > 0:
            return False

        stun.active = True
        stun.duration = max(int(duration), stun.duration)
        stun.extra = 0

        try:
            (applier or self)._emit_status_event(
                self, "Stun", applied=True, duration=stun.duration, source=source
            )
        except Exception:
            pass
        return True

    def stun_contest_success(
        self,
        applier: Character | None,
        attacker_roll: int,
        defender_roll: int,
    ) -> bool:
        """
        Resolve a stun contest roll with level-difference bias.

        The caller computes rolls (STR vs CON, SPD vs CON, etc.). This helper
        biases the attacker's roll based on applier-vs-target level gap.
        """
        if applier is None:
            return attacker_roll > defender_roll

        diff = _combat_level(applier) - _combat_level(self)
        diff = max(-STUN_LEVEL_DIFF_CAP, min(STUN_LEVEL_DIFF_CAP, diff))
        mult = 1.0 + (diff * STUN_LEVEL_DIFF_SCALE)
        mult = max(STUN_LEVEL_DIFF_MULT_MIN, min(STUN_LEVEL_DIFF_MULT_MAX, mult))
        adj_attacker = int(attacker_roll * mult)
        # Racial status-resist tuning: Humans are slightly more susceptible to control.
        try:
            if getattr(getattr(self, "race", None), "name", None) == "Human":
                defender_roll = int(defender_roll * HUMAN_STATUS_RESIST_MULTIPLIER)
        except Exception:
            pass
        return adj_attacker > defender_roll

    def effect_handler(self, effect: str) -> dict[str, StatusEffect]:
        effect_dicts = [self.status_effects,
                        self.physical_effects,
                        self.stat_effects,
                        self.magic_effects,
                        self.class_effects]
        for effect_dict in effect_dicts:
            if effect in effect_dict:
                return effect_dict
        raise NotImplementedError(f"{effect} does not exist in character attributes.")

    def can_be_disarmed(self) -> bool:
        weapon = self.equipment.get("Weapon") if isinstance(self.equipment, dict) else None
        if weapon is None:
            return False
        if getattr(weapon, "subtyp", None) in ["Natural", "Summon", "None"]:
            return False
        return bool(getattr(weapon, "disarm", True))

    def is_disarmed(self) -> bool:
        return bool(self.physical_effects["Disarm"].active and self.can_be_disarmed())

    def hit_chance(self, defender: Character, typ: str = 'weapon') -> float:
        """
        Calculate hit chance based on various factors.

        Things that affect hit chance
            Weapon attack: whether char is blind, if enemy is flying and/or invisible, enemy status effects,
                accessory bonuses, difference in pro level
            Spell attack: enemy status effects
        """

        # Defensive guard: speed stats can be 0 in synthetic/summon test states.
        a_speed = self.check_mod("speed", enemy=defender)
        d_speed = defender.check_mod("speed", enemy=self)
        num = random.randint(a_speed // 2, a_speed)
        den = random.randint(d_speed // 4, d_speed // 2)
        hit_mod = sigmoid(num / max(1, den))  # base hit percentage
        if typ == 'weapon':
            hit_mod *= 1 + (ACCURACY_RING_BONUS * ('Accuracy' in self.equipment['Ring'].mod))
            blind_pen = BLIND_ACCURACY_PENALTY
            try:
                if getattr(getattr(self, "race", None), "name", None) == "Elf":
                    blind_pen *= ELF_BLIND_PENALTY_MULTIPLIER
            except Exception:
                pass
            hit_mod *= 1 - (blind_pen * self.status_effects["Blind"].active)
            hit_mod *= 1 - FLYING_ACCURACY_PENALTY * defender.flying
            hit_mod *= 1 - (DISARM_HIT_PENALTY * self.is_disarmed())
            hit_mod *= 1 - (BERSERK_HIT_PENALTY * (self.status_effects['Berserk'].active))
            hit_mod *= 1 - (BLIND_RAGE_HIT_PENALTY * (self.status_effects["Blind Rage"].active))
        hit_mod += PRO_LEVEL_HIT_MODIFIER * (self.level.pro_level - defender.level.pro_level)
        invis_pen = INVISIBLE_ACCURACY_PENALTY
        try:
            if getattr(getattr(self, "race", None), "name", None) == "Elf":
                invis_pen *= ELF_INVISIBLE_PENALTY_MULTIPLIER
        except Exception:
            pass
        hit_mod *= 1 - invis_pen * defender.invisible
        if hasattr(self, "encumbered"):
            if self.encumbered:
                hit_mod *= ENCUMBERED_HIT_MULTIPLIER
                try:
                    if getattr(getattr(self, "race", None), "name", None) == "Gnome":
                        hit_mod *= GNOME_ENCUMBERED_HIT_MULTIPLIER
                except Exception:
                    pass
        return max(0, hit_mod)

    def dodge_chance(self, attacker: Character, spell: bool = False) -> float:
        a_stat = attacker.check_mod("speed", enemy=self)
        d_stat = self.check_mod("speed", enemy=attacker)
        if spell:
            a_stat = attacker.stats.intel
            # Spells are avoided via mental defense; low CHA/WIS should matter.
            cha_term = max(-5, min(5, int(self.stats.charisma) - 10))
            d_stat = max(0, int(self.stats.wisdom) + cha_term)
        armor_factor = {"None": 1, "Natural": 1, "Cloth": 1, "Light": 2, "Medium": 3, "Heavy": 4}
        a_chance = random.randint(a_stat // 2, a_stat) + \
            attacker.check_mod('luck', enemy=self, luck_factor=10)
        d_chance = random.randint(0, d_stat // 2) + self.check_mod('luck', enemy=attacker, luck_factor=15) + \
            (self.stat_effects["Speed"].active * self.stat_effects["Speed"].extra)
        denom = a_chance + d_chance
        if denom <= 0:
            return 0.0
        af = armor_factor.get(getattr(self.equipment.get("Armor"), "subtyp", "None"), 1)
        chance = max(0, (d_chance - a_chance) / denom / af)
        chance += 0.1 * ('Dodge' in self.equipment['Ring'].mod + "Evasion" in self.spellbook['Skills'])
        if spell:
            pendant_mod = getattr(self.equipment.get("Pendant"), "mod", "")
            chance += 0.25 * ("Magic Dodge" in pendant_mod)
        # Footpad-line passive: scale *weapon* dodge slightly with DEX so "glass cannon"
        # races/classes have a defensive path that doesn't require changing race resistances.
        # We intentionally do not apply this to spell-avoidance, which is governed by WIS/CHA.
        if (not spell) and "Quickstep" in self.spellbook.get("Skills", {}):
            dex = int(getattr(self.stats, "dex", 10))
            # +0.00 at DEX<=10, up to +0.15 at DEX>=25
            chance += min(0.15, max(0.0, (dex - 10) / 100))
        if self.cls.name == "Seeker" or (self.cls.name == "Templar" and self.class_effects["Power Up"].active):
            chance += (0.25 * self.power_up)
        # Dwarf Gluttony (in-combat hangover): reduced dodge while active.
        try:
            if self.status_effects.get("Hangover") and self.status_effects["Hangover"].active:
                chance *= DWARF_HANGOVER_DODGE_MULTIPLIER
        except Exception:
            pass
        if hasattr(self, "encumbered"):
            if self.encumbered:
                chance /= 2  # lower dodge chance by half if encumbered
                try:
                    if getattr(getattr(self, "race", None), "name", None) == "Gnome":
                        chance *= GNOME_ENCUMBERED_DODGE_MULTIPLIER
                except Exception:
                    pass
        return min(MAX_DODGE_CHANCE, chance)
    
    def critical_chance(self, att: str) -> float:
        base_crit = BASE_CRIT_PER_POINT * (
            self.check_mod("speed") + self.check_mod("luck", luck_factor=10)
        )
        crit_chance = base_crit
        if self.equipment.get(att) is not None:
            crit_chance += float(getattr(self.equipment[att], "crit", 0.0) or 0.0) * WEAPON_CRIT_WEIGHT
        if self.cls.name == "Seeker":
            crit_chance += (SEEKER_CRIT_BONUS * self.power_up)
        
        # Maelstrom Weapon: Add bonus critical chance for consecutive hits
        if "Maelstrom Weapon" in self.spellbook["Skills"]:
            # Backward compatibility for older runtime/save objects missing this field.
            maelstrom_hits = int(getattr(self, "maelstrom_hits", 0) or 0)
            maelstrom_bonus = maelstrom_hits * MAELSTROM_CRIT_PER_HIT
            crit_chance += maelstrom_bonus
        
        return max(0.0, min(MAX_CRIT_CHANCE, crit_chance))

    def weapon_damage(self, defender, dmg_mod=1.0, crit=1, ignore=False, cover=False, hit=False, use_offhand=True) -> tuple[str, bool, int]:
        """
        Function that controls melee attacks during combat
        defender(Character): the target of the attack
        dmg_mod(float): a percentage value that modifies the amount of damage done
        crit(int): the damage multiplier for a critical hit
        ignore(bool): whether the attack ignores the target's defenses
        cover(bool): whether the attack can be blocked by a familiar or pet
        hit(bool): guarantees hit if target doesn't dodge
        """
        from .combat.combat_result import CombatResult, CombatResultGroup

        if defender.magic_effects["Ice Block"].active or defender.tunnel:
            return f"{self.name}'s attack has no effect.\n", False, crit
        hits = []  # indicates if the attack was successful for means of ability/weapon affects
        crits = []
        attacks = ['Weapon']
        if use_offhand and self.equipment['OffHand'].typ == 'Weapon':
            attacks.append('OffHand')
        weapon_dam_str = ""
        for i, att in enumerate(attacks):
            hits.append(hit)
            crits.append(1)
            ignore = ignore or self.equipment[att].ignore
            damage = 0
            # attacker variables
            typ = 'attacks'
            if self.equipment[att].subtyp == 'Natural':
                typ = self.equipment[att].att_name
                if typ == 'leers':
                    hits[i] = True
                    result = CombatResult(
                        action="Leer", actor=self, target=defender,
                        hit=True, crit=1, damage=0
                    )
                    results = CombatResultGroup()
                    results.add(result)
                    self.equipment[att].special_effect(results)
                    weapon_dam_str += f"{self.name} leers at {defender.name}.\n"
                    break
            crits[i] = 2 if crit == 1 and self.critical_chance(att) > random.random() else crit
            dmg = max(1, int(dmg_mod * self.check_mod(att.lower(), enemy=defender)))
            crit_per = random.uniform(1, crits[i])
            # Half Elf racial sin: slightly reduced crit spike potential.
            try:
                if getattr(getattr(self, "race", None), "name", None) == "Half Elf" and crit_per > 1.0:
                    crit_per = 1.0 + ((crit_per - 1.0) * HALF_ELF_CRIT_SPIKE_MULTIPLIER)
            except Exception:
                pass
            damage = max(0, int(dmg * crit_per))

            # defender variables
            if not hit:
                dodge = defender.dodge_chance(self) > random.random()
                hit_per = self.hit_chance(defender, typ='weapon')
                hits[i] = hit_per > random.random()
            else:
                dodge = False
            if defender.incapacitated():
                dodge = False
                hits[i] = True

            # --- Phase 1: Dodge / Parry ---
            if dodge:
                hits[i] = False
                self._reset_maelstrom()
                msg, aborted = self._handle_dodge(defender, damage, typ)
                weapon_dam_str += msg
                if aborted:
                    return weapon_dam_str, any(hits), max(crits)
                continue

            # --- Phase 2: Duplicates check ---
            if hits[i] and defender.magic_effects["Duplicates"].active:
                hits[i], msg = self._handle_duplicates(defender, typ)
                weapon_dam_str += msg
                if not hits[i]:
                    continue

            if not hits[i]:
                weapon_dam_str += f"{self.name} {typ} {defender.name} but misses entirely.\n"
                self._reset_maelstrom()
                continue

            # --- Phase 3: Critical hit event ---
            if crits[i] > 1:
                self._emit_crit_event(defender, crits[i])
                self._reset_maelstrom()

            # --- Phase 4: Absorption layers (cover, block, shields, reflect) ---
            damage, msg, absorbed = self._apply_absorption(
                defender, damage, dmg, crit_per, att, cover, crits[i]
            )
            weapon_dam_str += msg
            if absorbed:
                hits[i] = False
                self._reset_maelstrom()

            # --- Phase 5: Resistance / armor / damage reduction ---
            if damage > 0:
                damage, msg = self._apply_damage_reduction(
                    defender, damage, att, ignore
                )
                weapon_dam_str += msg

            # --- Phase 6: Apply damage and on-hit effects ---
            if damage > 0:
                # Half Orc racial virtue: reduced critical damage taken (weapon crits only).
                try:
                    if (
                        crits[i] > 1
                        and getattr(getattr(defender, "race", None), "name", None) == "Half Orc"
                    ):
                        damage = max(0, int(damage * HALF_ORC_CRIT_DAMAGE_TAKEN_MULTIPLIER))
                except Exception:
                    pass
                defender.health.current -= damage
                weapon_dam_str += self._build_damage_message(
                    defender, damage, typ, crits[i], att
                )
                weapon_dam_str += self._apply_on_hit_effects(defender, damage, crits[i], att)
                # Evasive Guard: build stacks when you get hit; capped at 3.
                # This encourages "stay in the fight" play without altering race resistances.
                if "Evasive Guard" in defender.spellbook.get("Skills", {}):
                    defender.evasive_guard_stacks = min(3, int(getattr(defender, "evasive_guard_stacks", 0)) + 1)
                # Half Orc racial sin: small chance on taking damage to enter Blind Rage
                # (retains control, but reduced hit chance for a few turns).
                try:
                    if (
                        damage > 0
                        and getattr(getattr(defender, "race", None), "name", None) == "Half Orc"
                        and random.random() < HALF_ORC_BLIND_RAGE_CHANCE
                    ):
                        br = defender.status_effects.get("Blind Rage")
                        if br is not None:
                            br.active = True
                            br.duration = max(int(br.duration or 0), HALF_ORC_BLIND_RAGE_DURATION)
                            weapon_dam_str += f"{defender.name} flies into a blind rage!\n"
                except Exception:
                    pass
            else:
                defender.health.current -= damage  # 0 damage still needs to be "applied" for consistency
                weapon_dam_str += f"{self.name} {typ} {defender.name} but deals no damage.\n"
                hits[i] = False
                self._reset_maelstrom()

            # --- Phase 7: Equipment special effects on successful hit ---
            if hits[i]:
                weapon_dam_str += self._apply_equipment_effects(
                    defender, att, damage, crits[i]
                )
                if self.cls.name == "Dragoon" and self.power_up:
                    self.class_effects["Power Up"].active = True
                    self.class_effects["Power Up"].duration += 1
            else:
                if self.cls.name == "Dragoon" and self.power_up:
                    self.class_effects["Power Up"].active = False
                    self.class_effects["Power Up"].duration = 0

        return weapon_dam_str, any(hits), max(crits)

    # ------------------------------------------------------------------ #
    #  weapon_damage helper methods                                       #
    # ------------------------------------------------------------------ #

    def _reset_maelstrom(self) -> None:
        """Reset Maelstrom Weapon consecutive-hit counter."""
        if "Maelstrom Weapon" in self.spellbook["Skills"]:
            if not hasattr(self, "maelstrom_hits"):
                self.maelstrom_hits = 0
            self.maelstrom_hits = 0

    def _handle_dodge(self, defender: Character, damage: int, typ: str) -> tuple[str, bool]:
        """
        Handle dodge/parry outcome.

        Returns:
            (message, aborted) – *aborted* is True when the attacker died
            from a parry counter-attack and the caller should return early.
        """
        msg = ""
        # Evasive Guard stacks decay whenever the defender successfully dodges.
        if "Evasive Guard" in defender.spellbook.get("Skills", {}):
            defender.evasive_guard_stacks = max(
                0, int(getattr(defender, "evasive_guard_stacks", 0) or 0) - 1
            )
        if 'Parry' in defender.spellbook['Skills']:
            # Parry counter-attack chance scales with defender DEX.
            # This makes high-DEX archetypes more resilient without changing race resistances.
            dex = int(getattr(defender.stats, "dex", 10))
            parry_chance = max(0.10, min(0.85, 0.25 + (dex - 10) * 0.03))
            if random.random() < parry_chance:
                msg += f"{defender.name} parries {self.name}'s attack and counterattacks!\n"
                counter_str, _, _ = defender.weapon_damage(self)
                msg += counter_str
                if not self.is_alive():
                    return msg, True
            else:
                msg += f"{defender.name} evades {self.name}'s attack.\n"
        else:
            try:
                from .events.event_bus import get_event_bus, create_combat_event, EventType
                event_bus = get_event_bus()
                event_bus.emit(create_combat_event(
                    EventType.DODGE, actor=defender, target=self, damage=damage
                ))
            except Exception:
                pass
            msg += f"{defender.name} evades {self.name}'s attack.\n"
        return msg, False

    def _handle_duplicates(self, defender: Character, typ: str) -> tuple[bool, str]:
        """
        Check if the attack hits a mirror-image duplicate.

        Returns:
            (still_hit, message)
        """
        chance = defender.magic_effects["Duplicates"].duration - self.check_mod("luck", luck_factor=15)
        if random.randint(0, max(0, chance)):
            self._reset_maelstrom()
            msg = (f"{self.name} {typ} at {defender.name} but hits a mirror image and it "
                   f"vanishes from existence.\n")
            defender.magic_effects["Duplicates"].duration -= 1
            if not defender.magic_effects["Duplicates"].duration:
                defender.magic_effects["Duplicates"].active = False
            return False, msg
        return True, ""

    def _emit_crit_event(self, defender: Character, crit_mult: int) -> None:
        """Emit a CRITICAL_HIT event."""
        try:
            from .events.event_bus import get_event_bus, create_combat_event, EventType
            event_bus = get_event_bus()
            event_bus.emit(create_combat_event(
                EventType.CRITICAL_HIT, actor=self, target=defender, multiplier=crit_mult
            ))
        except Exception:
            pass

    def _apply_absorption(
        self, defender: Character, damage: int, raw_dmg: int,
        crit_per: float, att: str, cover: bool, crit: int
    ) -> tuple[int, str, bool]:
        """
        Apply cover, shield block, mana shield, class shields, and reflect.

        Returns:
            (remaining_damage, message, fully_absorbed)
        """
        msg = ""
        absorbed = False

        if cover:
            msg += (f"{defender.familiar.name} steps in front of the attack, "
                    f"taking the damage for {defender.name}.\n")
            return 0, msg, False  # damage zeroed but hit still counts

        # Shield block
        can_block = (
            (defender.equipment['OffHand'].subtyp == 'Shield' or
             'Dodge' in defender.equipment['Ring'].mod) and
            not defender.magic_effects["Mana Shield"].active and
            not (defender.cls.name == "Crusader" and defender.power_up and
                 defender.class_effects["Power Up"].active) and
            not defender.incapacitated()
        )
        if can_block:
            blk_chance = defender.check_mod('shield', enemy=self) / 100
            if blk_chance > random.random():
                blk_per = blk_chance + ((defender.stats.strength - self.stats.strength) / damage) if damage else 0
                if 'Shield Block' in defender.spellbook['Skills']:
                    blk_per *= 1.25
                if blk_per > 0:
                    blk_per = min(1, blk_per)
                    damage = int(damage * (1 - blk_per))
                    try:
                        from .events.event_bus import get_event_bus, create_combat_event, EventType
                        event_bus = get_event_bus()
                        event_bus.emit(create_combat_event(
                            EventType.BLOCK, actor=defender, target=self,
                            damage_blocked=int(raw_dmg * crit_per * blk_per)
                        ))
                    except Exception:
                        pass
                    blocked_pct = round(blk_per * 100)
                    if blocked_pct > 0:
                        msg += (f"{defender.name} blocks {self.name}'s attack and mitigates "
                                f"{blocked_pct} percent of the damage.\n")
            return damage, msg, False

        # Mana Shield
        if defender.magic_effects["Mana Shield"].active:
            damage, shield_msg, absorbed = self._apply_mana_shield(defender, damage)
            return damage, msg + shield_msg, absorbed

        # Crusader absorb shield
        if (defender.cls.name == "Crusader" and defender.power_up and
                defender.class_effects["Power Up"].active):
            damage, shield_msg, absorbed = self._apply_crusader_shield(defender, damage)
            return damage, msg + shield_msg, absorbed

        # Templar reflect
        if (defender.cls.name == "Templar" and defender.power_up and
                defender.class_effects["Power Up"].active):
            ref_dam = int(0.25 * damage)
            damage -= ref_dam
            self.health.current -= ref_dam
            defender._emit_damage_event(self, ref_dam, damage_type="Reflected", is_critical=False)
            msg += f"{ref_dam} is reflected back at {self.name}.\n"
            return damage, msg, False

        # Totem reflect
        if (defender.magic_effects["Totem"].active and
                isinstance(defender.magic_effects["Totem"].extra, dict) and
                defender.magic_effects["Totem"].extra.get("secondary") == "reflect"):
            ref_dam = int(0.25 * damage)
            damage -= ref_dam
            self.health.current -= ref_dam
            defender._emit_damage_event(self, ref_dam, damage_type="Reflected", is_critical=False)
            msg += f"{ref_dam} bounces off the totem's barrier back to {self.name}.\n"
            return damage, msg, False

        return damage, msg, False

    def _apply_mana_shield(self, defender: Character, damage: int) -> tuple[int, str, bool]:
        """Handle Mana Shield absorption. Returns (damage, msg, fully_absorbed)."""
        msg = ""
        mana_loss = damage // defender.magic_effects["Mana Shield"].duration
        if mana_loss > defender.mana.current:
            abs_dam = defender.mana.current * defender.magic_effects["Mana Shield"].duration
            msg += f"The mana shield around {defender.name} absorbs {abs_dam} damage.\n"
            damage -= abs_dam
            defender.mana.current = 0
            self._emit_status_event(defender, "Mana Shield", applied=False, source="Mana Depleted")
            defender.magic_effects["Mana Shield"].active = False
            msg += f"The mana shield dissolves around {defender.name}.\n"
            return damage, msg, False
        else:
            msg += f"The mana shield around {defender.name} absorbs {damage} damage.\n"
            defender.mana.current -= mana_loss
            return 0, msg, True

    def _apply_crusader_shield(self, defender: Character, damage: int) -> tuple[int, str, bool]:
        """Handle Crusader Power Up absorb shield. Returns (damage, msg, fully_absorbed)."""
        msg = ""
        if damage >= defender.class_effects["Power Up"].extra:
            msg += (f"The shield around {defender.name} absorbs "
                    f"{defender.class_effects['Power Up'].extra} damage.\n")
            damage -= defender.class_effects["Power Up"].extra
            defender.class_effects["Power Up"].active = False
            msg += f"The shield dissolves around {defender.name}.\n"
            return damage, msg, False
        else:
            msg += f"The shield around {defender.name} absorbs {damage} damage.\n"
            defender.class_effects["Power Up"].extra -= damage
            return 0, msg, True

    def _apply_damage_reduction(
        self, defender: Character, damage: int, att: str, ignore: bool
    ) -> tuple[int, str]:
        """Apply resistance, armor, defensive stance, and astral shift reductions."""
        msg = ""

        # Elemental + physical resistance
        e_resist = 0
        if self.equipment[att].element:
            e_resist = defender.check_mod('resist', enemy=self, typ=self.equipment[att].element)
        p_resist = defender.check_mod(
            'resist', enemy=self, typ='Physical', ultimate=self.equipment[att].ultimate
        )
        dam_red = defender.check_mod('armor', enemy=self, ignore=ignore)
        damage = max(0, int(
            damage * (1 - p_resist) * (1 - e_resist) * (1 - (dam_red / (dam_red + ARMOR_SCALING_FACTOR)))
        ))
        variance = random.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
        damage = int(damage * variance)

        # Bleed makes melee hits more punishing (before defensive stance reductions).
        if (
            damage > 0
            and hasattr(defender, "physical_effects")
            and defender.physical_effects.get("Bleed")
            and defender.physical_effects["Bleed"].active
        ):
            bonus = max(1, int(damage * (BLEED_MELEE_DAMAGE_TAKEN_MULTIPLIER - 1.0)))
            damage += bonus
            msg += f"{defender.name}'s bleeding leaves them vulnerable (+{bonus} damage).\n"

        # Defensive stance
        defensive_reduction = (
            defender.get_defensive_reduction()
            if hasattr(defender, "get_defensive_reduction") else 0.0
        )
        if defensive_reduction > 0 and damage > 0:
            reduced = max(1, int(damage * defensive_reduction))
            damage = max(0, damage - reduced)
            msg += f"{defender.name} braces defensively, reducing damage by {reduced}.\n"

        # Astral Shift (25%)
        if defender.magic_effects["Astral Shift"].active and damage > 0:
            astral_reduction = int(damage * ASTRAL_SHIFT_REDUCTION)
            damage = max(0, damage - astral_reduction)
            msg += f"{defender.name}'s astral form deflects {astral_reduction} damage.\n"

        # Footpad-line passive damage reduction (weapon hits only): stackable proc, DEX-scaling.
        # Stacks build when hit (max 3) and reset on dodge.
        # Applied late so it plays nicely with armor/resists/stance and stays readable.
        if damage > 0 and "Evasive Guard" in defender.spellbook.get("Skills", {}):
            dex = int(getattr(defender.stats, "dex", 10))
            stacks = int(getattr(defender, "evasive_guard_stacks", 0) or 0)
            if stacks > 0:
                # Per-stack reduction: 3% base + 0.2% per DEX above 10, capped at 8%.
                per_stack = min(0.08, max(0.03, 0.03 + max(0, dex - 10) * 0.002))
                guard_red = min(0.25, per_stack * min(3, stacks))
                reduced = max(1, int(damage * guard_red))
                damage = max(0, damage - reduced)
                msg += f"{defender.name}'s evasive guard reduces damage by {reduced}.\n"

        return damage, msg

    def _build_damage_message(
        self, defender: Character, damage: int, typ: str, crit: int, att: str
    ) -> str:
        """Build the main damage-dealt message string."""
        msg = f"{self.name} {typ} {defender.name} for {damage} damage"
        if crit > 1:
            msg += " (Critical hit!)"
        msg += ".\n"
        return msg

    def _apply_on_hit_effects(self, defender: Character, damage: int, crit: int, att: str = 'Weapon') -> str:
        """Apply post-damage triggers: Maelstrom tracking, sleep wakeup, life steal."""
        msg = ""

        # Update Maelstrom Weapon counter for non-critical hits
        if "Maelstrom Weapon" in self.spellbook["Skills"] and crit == 1:
            if not hasattr(self, "maelstrom_hits"):
                self.maelstrom_hits = 0
            self.maelstrom_hits += 1

        # Emit damage event
        damage_type = "Physical"
        if self.equipment[att].element:
            damage_type = self.equipment[att].element
        self._emit_damage_event(defender, damage, damage_type=damage_type, is_critical=(crit > 1))

        # Sleep wakeup
        if defender.status_effects["Sleep"].active and \
                not random.randint(0, defender.status_effects["Sleep"].duration):
            msg += f"The attack awakens {defender.name}!\n"
            self._emit_status_event(defender, "Sleep", applied=False, source="Awakened by Damage")
            defender.status_effects["Sleep"].active = False
            defender.status_effects["Sleep"].duration = 0

        # Ninja life steal
        if self.cls.name == "Ninja" and self.power_up:
            dam_abs = self.class_effects["Power Up"].active * damage
            dam_abs = int(dam_abs * self.healing_received_multiplier())
            dam_abs = min(dam_abs, self.health.max - self.health.current)
            self.health.current += dam_abs
            self._emit_healing_event(dam_abs, source="Ninja Life Steal")
            msg += f"{self.name} absorbs {dam_abs} from {defender.name}.\n"

        # Lycan life steal
        if self.cls.name == "Lycan" and self.power_up:
            dam_abs = damage // 2
            dam_abs = int(dam_abs * self.healing_received_multiplier())
            dam_abs = min(dam_abs, self.health.max - self.health.current)
            self.health.current += dam_abs
            if dam_abs > 0:
                self._emit_healing_event(dam_abs, source="Lycan Life Steal")
                msg += f"{self.name} absorbs {dam_abs} from {defender.name}.\n"

        return msg

    def _apply_equipment_effects(
        self, defender: Character, att: str, damage: int, crit: int
    ) -> str:
        """Process armor/weapon special effects on a successful hit."""
        from .combat.combat_result import CombatResult, CombatResultGroup

        msg = ""
        result = CombatResult(
            action=att, actor=self, target=defender,
            hit=True, crit=crit, damage=damage, healing=0
        )
        results = CombatResultGroup()
        results.add(result)

        # Armor special effects (thorns, reflection)
        defender.equipment['Armor'].special_effect(results)

        # Weapon special effects (life steal, elemental effects, instant death)
        if defender.is_alive() and damage > 0 and not defender.magic_effects["Mana Shield"].active:
            self.equipment[att].special_effect(results)

        # Process special effect results
        for res in results.results:
            if 'Drain' in res.extra and res.extra['Drain']:
                drain_amount = res.actor.health.current - (res.actor.health.current - res.damage)
                msg += f"{res.actor.name} drains {drain_amount} health from {res.target.name}.\n"
            if 'Instant Death' in res.extra and res.extra['Instant Death']:
                res.target.health.current = 0
                msg += f"{res.target.name} is instantly killed!\n"

        return msg

    def handle_defenses(self, attacker: Character, damage: int, cover: bool = False, typ: str = "Physical") -> tuple[bool, str, int]:
        """
        Stub method for handling defensive calculations.
        
        This method was planned but never fully implemented. Currently handles
        ManaShield logic, otherwise passes damage through unchanged.
        
        Args:
            attacker: The attacking character
            damage: Base damage value
            cover: Whether attack can be blocked by familiar/pet
            typ: Damage type ("Physical", "Magic", etc.)
            
        Returns:
            tuple: (hit: bool, message: str, damage: int)
        """
        message = ""
        hit = True
        
        # Handle Mana Shield
        if self.magic_effects["Mana Shield"].active:
            mana_loss = damage // self.magic_effects["Mana Shield"].duration
            if mana_loss > self.mana.current:
                abs_dam = self.mana.current * self.magic_effects["Mana Shield"].duration
                message += f"The mana shield around {self.name} absorbs {abs_dam} damage.\n"
                damage -= abs_dam
                self.mana.current = 0
                self.magic_effects["Mana Shield"].active = False
                message += f"The mana shield dissolves around {self.name}.\n"
            else:
                message += f"The mana shield around {self.name} absorbs {damage} damage.\n"
                self.mana.current -= mana_loss
                damage = 0
                hit = False
        
        return (hit, message, damage)

    def damage_reduction(self, damage: int, attacker: Character, typ: str = "Physical") -> tuple[bool, str, int]:
        """
        Stub method for calculating damage reduction.
        
        This method was planned but never fully implemented. For now, it applies
        basic resistance checks.
        
        Args:
            damage: Incoming damage value
            attacker: The attacking character
            typ: Damage type for resistance calculation
            
        Returns:
            tuple: (hit: bool, message: str, final_damage: int)
        """
        # Apply basic resistance only if typ is a valid resistance type
        resist = 0
        if typ in self.resistance:
            resist = self.check_mod('resist', enemy=attacker, typ=typ)
        
        final_damage = int(damage * (1 - resist))

        # Magic defense reduction: allow primary stats (WIS/CHA) to matter for
        # survival even on physical builds, by reducing incoming elemental/magic damage.
        if typ != "Physical" and final_damage > 0:
            mdef = int(self.check_mod("magic def", enemy=attacker) or 0)
            if mdef > 0:
                final_damage = int(final_damage * (1 - (mdef / (mdef + MAGIC_DEF_SCALING_FACTOR))))
        
        message = ""
        if resist > 0 and final_damage < damage:
            reduction = damage - final_damage
            message = f"{self.name}'s resistance reduces damage by {reduction}.\n"
        
        return True, message, final_damage

    def flee(self, enemy: Character, smoke: bool = False) -> tuple[bool, str]:
        blind = enemy.status_effects["Blind"].active
        success = False
        flee_message = f"{self.name} couldn't escape from the {enemy.name}."
        if smoke:
            if not enemy.sight or self.invisible:
                flee_message = f"{self.name} disappears in a cloud of smoke."
                self.state = 'normal'
                success = True
            else:
                flee_message = f"{enemy.name} is not fooled by cheap parlor tricks."
        else:
            chance = (self.check_mod('luck', enemy=enemy, luck_factor=10) + \
                (self.stat_effects["Speed"].active * self.stat_effects["Speed"].extra))
            chance = (chance / 100) + BASE_FLEE_CHANCE
            speed_factor = (self.check_mod("speed", enemy=enemy) - enemy.check_mod("speed", enemy=enemy)) / \
                (self.check_mod("speed", enemy=enemy) + enemy.check_mod("speed", enemy=enemy) + 1)
            pro_diff = self.level.pro_level / max(enemy.level.pro_level, 1)
            flee_chance = min(MAX_FLEE_CHANCE, chance + speed_factor * pro_diff)
            if random.random() < flee_chance or enemy.incapacitated() or blind:
                flee_message = f"{self.name} flees from the {enemy.name}."
                self.state = 'normal'
                success = True
        return success, flee_message

    def is_alive(self) -> bool:
        return self.health.current > 0

    def modify_inventory(self, item: object, num: int = 1, subtract: bool = False,
                         rare: bool = False, quest: bool = False, storage: bool = False) -> None:
        inventory = self.special_inventory if rare else self.inventory
        if subtract:
            for _ in range(num):
                inventory[item.name].pop(0)
                if storage:
                    if item.name not in self.storage:
                        self.storage[item.name] = []
                    self.storage[item.name].append(item)
            if not len(inventory[item.name]):
                del inventory[item.name]
        else:
            if item.name not in inventory:
                inventory[item.name] = []
            num = min(num, 99 - len(inventory[item.name]))
            for _ in range(num):
                inventory[item.name].append(item)
                if storage:
                    self.storage[item.name].pop(0)
                    if not len(self.storage[item.name]):
                        del self.storage[item.name]
        if quest:
            self.quests(item=item)

        # Update encumbered status for player characters
        if hasattr(self, 'max_weight'):
            self.encumbered = self.current_weight() > self.max_weight()

    def effects(self, end: bool = False) -> str | None:
        """
        Silence, Blind, and Disarm can be indefinite unless cured (duration=-1)
        """

        effect_dicts = [self.status_effects,
                        self.physical_effects,
                        self.stat_effects,
                        self.magic_effects,
                        self.class_effects]

        def default(effect=None, end_combat=False):
            if end_combat:
                for effect_dict in effect_dicts:
                    for effect in effect_dict.keys():
                        if effect_dict[effect].active:
                            self._emit_status_event(self, effect, applied=False, source="Combat End")
                        effect_dict[effect].active = False
                        effect_dict[effect].duration = 0
                        effect_dict[effect].extra = 0
            else:
                effect_dict = self.effect_handler(effect=effect)
                if effect_dict[effect].active:
                    self._emit_status_event(self, effect, applied=False, source="Duration Expired")
                effect_dict[effect].active = False
                effect_dict[effect].duration = 0
                effect_dict[effect].extra = 0

        if end:
            default(end_combat=True)
        else:
            status_text = ""
            if self.status_effects["Doom"].active:
                self.status_effects["Doom"].duration -= 1
                if not self.status_effects["Doom"].duration:
                    status_text += f"The Doom countdown has expired and so has {self.name}!\n"
                    self.health.current = 0
                    return status_text
            if self.magic_effects["Ice Block"].active:
                self.magic_effects["Ice Block"].duration -= 1
                gain_perc = 0.10 * (1 + (self.stats.intel / 30))
                health_gain = min(self.health.max - self.health.current, int(self.health.max * gain_perc))
                health_gain = int(health_gain * self.healing_received_multiplier())
                self.health.current += health_gain
                mana_gain = min(self.mana.max - self.mana.current, int(self.mana.max * gain_perc))
                self.mana.current += mana_gain 
                status_text += f"{self.name} regens {health_gain} health and {mana_gain} mana.\n"
                if health_gain > 0:
                    self._emit_status_tick_event(self, "Ice Block", health_gain, "healing", source="Ice Block")
                if not self.magic_effects["Ice Block"].duration:
                    status_text += f"The ice block around {self.name} melts.\n"
                    default(effect="Ice Block")
                else:
                    return status_text
            if self.physical_effects["Prone"].active and all([not self.status_effects["Stun"].active,
                                                              not self.status_effects["Sleep"].active]):
                if not random.randint(0, self.physical_effects["Prone"].duration) or \
                    random.randint(0, self.check_mod("luck", luck_factor=10)):
                    default(effect="Prone")
                    status_text += f"{self.name} is no longer prone.\n"
                else:
                    self.physical_effects["Prone"].duration -= 1
                    status_text += f"{self.name} is still prone.\n"
            if self.status_effects["Poison"].active:
                self.status_effects["Poison"].duration -= 1
                poison_damage = max(1, int(self.status_effects["Poison"].extra * 1.50))
                resist_div = max(0, self.stats.con // 15)
                if not random.randint(0, resist_div):
                    self.health.current -= poison_damage
                    status_text += f"The poison damages {self.name} for {poison_damage} health points.\n"
                    self._emit_status_tick_event(self, "Poison", poison_damage, "damage", source="Poison")
                else:
                    status_text += f"{self.name} resisted the poison.\n"
                if not self.status_effects["Poison"].duration:
                    default(effect="Poison")
                    status_text += f"The poison has left {self.name}.\n"
            if self.magic_effects["DOT"].active:
                self.magic_effects["DOT"].duration -= 1
                dot_damage = int(self.magic_effects["DOT"].extra or 0)
                if dot_damage <= 0:
                    # Defensive guard: DOT should always have positive damage,
                    # but some effect paths may leave .extra unset/zero.
                    default(effect="DOT")
                    self.magic_effects["DOT"].duration = 0
                else:
                    if not random.randint(0, self.check_mod("magic def") // dot_damage):
                        self.health.current -= dot_damage
                        status_text += f"The magic damages {self.name} for {dot_damage} health points.\n"
                        self._emit_status_tick_event(self, "DOT", dot_damage, "damage", source="DOT")
                    else:
                        status_text += f"{self.name} resisted the magic.\n"
                    if not self.magic_effects["DOT"].duration:
                        default(effect="DOT")
                        status_text += f"The magic affecting {self.name} has worn off.\n"
            if self.physical_effects["Bleed"].active:
                self.physical_effects["Bleed"].duration -= 1
                bleed_damage = max(1, int(self.physical_effects["Bleed"].extra * 0.75))
                if not random.randint(0, self.stats.con // 10):
                    self.health.current -= bleed_damage
                    status_text += f"The bleed damages {self.name} for {bleed_damage} health points.\n"
                    self._emit_status_tick_event(self, "Bleed", bleed_damage, "damage", source="Bleed")
                else:
                    status_text += f"{self.name} resisted the bleed.\n"
                if not self.physical_effects["Bleed"].duration:
                    default(effect="Bleed")
                    status_text += f"{self.name}'s wounds have healed and is no longer bleeding.\n"
            if self.status_effects["Blind"].active:
                self.status_effects["Blind"].duration -= 1
                if not self.status_effects["Blind"].duration:
                    status_text += f"{self.name} regains sight and is no longer blind.\n"
                    default(effect="Blind")
            if self.status_effects["Blind Rage"].active:
                self.status_effects["Blind Rage"].duration -= 1
                if not self.status_effects["Blind Rage"].duration:
                    status_text += f"{self.name} calms down.\n"
                    default(effect="Blind Rage")
            if self.status_effects["Hangover"].active:
                self.status_effects["Hangover"].duration -= 1
                if not self.status_effects["Hangover"].duration:
                    status_text += f"{self.name} shakes off the hangover.\n"
                    default(effect="Hangover")
            if (not self.status_effects["Stun"].active) and self.status_effects["Stun"].extra > 0:
                # Post-stun immunity countdown (stun-lock prevention).
                self.status_effects["Stun"].extra -= 1
            if self.status_effects["Stun"].active:
                self.status_effects["Stun"].duration -= 1
                if not self.status_effects["Stun"].duration:
                    status_text += f"{self.name} is no longer stunned.\n"
                    if self.status_effects["Stun"].active:
                        self._emit_status_event(self, "Stun", applied=False, source="Duration Expired")
                    self.status_effects["Stun"].active = False
                    self.status_effects["Stun"].duration = 0
                    self.status_effects["Stun"].extra = max(
                        self.status_effects["Stun"].extra, STUN_IMMUNITY_TURNS_AFTER_EXPIRY
                    )
            if self.status_effects["Sleep"].active:
                self.status_effects["Sleep"].duration -= 1
                if not self.status_effects["Sleep"].duration:
                    status_text += f"{self.name} is no longer asleep.\n"
                    default(effect="Sleep")
            if self.status_effects["Berserk"].active:
                self.status_effects["Berserk"].duration -= 1
                if not self.status_effects["Berserk"].duration:
                    status_text += f"{self.name} has regained their composure.\n"
                    default(effect="Berserk")
            if self.status_effects["Defend"].active:
                self.status_effects["Defend"].duration -= 1
                if not self.status_effects["Defend"].duration:
                    status_text += f"{self.name} lowers their guard.\n"
                    default(effect="Defend")
            if self.status_effects["Steal Success"].active:
                self.status_effects["Steal Success"].duration -= 1
                if not self.status_effects["Steal Success"].duration:
                    default(effect="Steal Success")
            if self.magic_effects["Reflect"].active:
                self.magic_effects["Reflect"].duration -= 1
                if not self.magic_effects["Reflect"].duration:
                    status_text += f"{self.name} is no longer reflecting magic.\n"
                    default(effect="Reflect")
            if self.magic_effects["Totem"].active:
                self.magic_effects["Totem"].duration -= 1
                if not self.magic_effects["Totem"].duration:
                    status_text += f"{self.name}'s totem crumbles to dust.\n"
                    default(effect="Totem")
            if self.magic_effects["Astral Shift"].active:
                self.magic_effects["Astral Shift"].duration -= 1
                if not self.magic_effects["Astral Shift"].duration:
                    status_text += f"{self.name} fully returns from the astral plane.\n"
                    default(effect="Astral Shift")
            for stat in ["Attack", "Defense", "Magic", "Magic Defense", "Speed"]:
                if self.stat_effects[stat].active:
                    self.stat_effects[stat].duration -= 1
                    if not self.stat_effects[stat].duration:
                        default(effect=stat)
            if self.magic_effects["Regen"].active:
                self.magic_effects["Regen"].duration -= 1
                heal = self.magic_effects["Regen"].extra
                heal = int(heal * self.healing_received_multiplier())
                heal = min(heal, self.health.max - self.health.current)
                self.health.current += heal
                status_text += f"{self.name}'s health has regenerated by {heal}.\n"
                if heal > 0:
                    self._emit_status_tick_event(self, "Regen", heal, "healing", source="Regen")
                if not self.magic_effects["Regen"].duration:
                    status_text += "Regeneration spell ends.\n"
                    default(effect="Regen")
            if self.class_effects["Power Up"].active:
                if self.cls.name == "Lycan":
                    self.class_effects["Power Up"].duration += 1
                elif self.cls.name == "Dragoon":
                    pass
                else:
                    self.class_effects["Power Up"].duration -= 1
                if self.cls.name == "Knight Enchanter" and self.power_up:
                    missing_mana = self.mana.max - self.mana.current
                    mana_regen = max(1, min(self.class_effects["Power Up"].extra, missing_mana)) if missing_mana > 0 else 0
                    self.mana.current += mana_regen
                    status_text += f"{self.name} regens {mana_regen} mana.\n"
                    if mana_regen > 0:
                        self._emit_status_tick_event(self, "Power Up", mana_regen, "mana", source="Power Up")
                if self.cls.name == "Archbishop" and self.power_up:
                    health_regen = min(int(self.health.max * 0.10), self.health.max - self.health.current)
                    health_regen = int(health_regen * self.healing_received_multiplier())
                    mana_regen = min(int(self.mana.max * 0.10), self.mana.max - self.mana.current)
                    self.health.current += health_regen
                    self.mana.current += mana_regen
                    status_text += f"{self.name} regens {health_regen} health and {mana_regen} mana.\n"
                    if health_regen > 0:
                        self._emit_status_tick_event(self, "Power Up", health_regen, "healing", source="Power Up")
                    if mana_regen > 0:
                        self._emit_status_tick_event(self, "Power Up", mana_regen, "mana", source="Power Up")
                if not self.class_effects["Power Up"].duration:
                    if self.cls.name == "Crusader" and self.power_up:
                        status_text += (f"The shield around {self.name} explodes, dealing "
                                        f"{self.class_effects['Power Up'].extra} damage to the enemy.\n")
                    default(effect="Power Up")
            return status_text

    def special_effects(self, target: Character) -> str:
        special_str = ""
        return special_str

    def familiar_turn(self, target: Character) -> str:
        familiar_str = ""
        return familiar_str

    def check_mod(self, mod: str, enemy: Character | None = None, typ: str | None = None,
                  luck_factor: int = 1, ultimate: bool = False, ignore: bool = False) -> int | float:
        class_mod = 0
        berserk_per = int(self.status_effects["Berserk"].active) * 0.1  # berserk increases damage by 10%
        disarm_damage_multiplier = 0.5 if self.is_disarmed() else 1.0
        
        # Totem bonus: +15% attack and defense when active (guard missing key)
        totem = self.magic_effects.get("Totem")
        totem_bonus = 1.15 if (totem and getattr(totem, "active", False)) else 1.0
        
        if mod == 'weapon':
            weapon_mod = (self.equipment['Weapon'].damage * int(not self.is_disarmed()))
            weapon_mod += self.stat_effects["Attack"].extra * self.stat_effects["Attack"].active
            total_mod = (weapon_mod + class_mod + self.combat.attack) * disarm_damage_multiplier
            return max(0, int(total_mod * (1 + berserk_per) * totem_bonus))
        if mod == 'shield':
            block_mod = 0
            if self.equipment['OffHand'].subtyp == 'Shield':
                block_mod = round(self.equipment['OffHand'].mod * (1 + ('Shield Block' in self.spellbook['Skills'])) * 100)
            if self.equipment['Ring'].mod == "Block":
                block_mod += 25
            return max(0, block_mod)
        if mod == 'offhand':
            try:
                off_mod = self.equipment['OffHand'].damage
                off_mod += self.stat_effects["Attack"].extra * self.stat_effects["Attack"].active
                return max(0, int((off_mod + class_mod + self.combat.attack) * (0.75 + berserk_per)))
            except AttributeError:
                return 0
        if mod == 'armor':
            armor_mod = self.equipment['Armor'].armor
            if self.turtle:
                class_mod += 99
            armor_mod += self.stat_effects["Defense"].extra * self.stat_effects["Defense"].active
            return max(0, int((armor_mod * int(not ignore)) + class_mod + self.combat.defense) * totem_bonus)
        if mod == 'magic':
            magic_mod = int(self.stats.intel // 4) * self.level.pro_level
            if self.equipment['OffHand'].subtyp == 'Tome':
                magic_mod += self.equipment['OffHand'].mod
            if self.equipment['Weapon'].subtyp == 'Staff':
                magic_mod += int(self.equipment['Weapon'].damage * 0.75)
            magic_mod += self.stat_effects["Magic"].extra * self.stat_effects["Magic"].active
            return max(0, magic_mod + class_mod + self.combat.magic)
        if mod == 'magic def':
            # Wisdom is the primary magic-defense stat; charisma provides a secondary
            # willpower component so "dump CHA/WIS" has a tangible downside.
            m_def_mod = int(self.stats.wisdom) + (int(self.stats.charisma) // 2)
            if self.turtle:
                class_mod += 99
            m_def_mod += self.stat_effects["Magic Defense"].extra * self.stat_effects["Magic Defense"].active
            return max(0, m_def_mod + class_mod + self.combat.magic_def)
        if mod == 'heal':
            heal_mod = self.stats.wisdom * self.level.pro_level
            if self.equipment['OffHand'].subtyp == 'Tome':
                heal_mod += self.equipment['OffHand'].mod
            elif self.equipment['Weapon'].subtyp == 'Staff':
                heal_mod += self.equipment['Weapon'].damage
            heal_mod += self.stat_effects["Magic"].extra * self.stat_effects["Magic"].active
            return max(0, heal_mod + class_mod + self.combat.magic)
        if mod == 'resist':
            if ultimate and typ == 'Physical':  # ultimate weapons bypass Physical resistance
                return -0.25
            res_mod = self.resistance[typ]
            if self.flying:
                if typ == 'Earth':
                    res_mod = 1
                elif typ == 'Wind':
                    res_mod = -0.25
            return res_mod
        if mod == 'luck':
            # "Luck" also acts as a general-purpose saving-throw modifier in many effects.
            # Include wisdom so low WIS/CHA builds pay a consistent penalty in combat.
            lf = max(1, int(luck_factor))
            base = int(self.stats.charisma) + int(self.stats.wisdom)
            return max(0, (base * 2) // lf)
        if mod == "speed":
            speed_mod = self.stats.dex
            speed_mod += self.stat_effects["Speed"].extra * self.stat_effects["Speed"].active
            return speed_mod
        return 0

    def buff_str(self) -> str:
        buffs = []
        if self.equipment['Ring'].mod in ["Accuracy", "Dodge"]:
            buffs.append(self.equipment['Ring'].mod)
        if self.equipment['Pendant'].mod in \
            ["Vision", "Flying", "Invisible",
             "Status-Poison", "Status-Berserk", "Status-Stone", "Status-Silence", "Status-Death", "Status-All"]:
            buffs.append(self.equipment['Pendant'].mod)
        if self.flying and "Flying" not in buffs:
            buffs.append("Flying")
        if self.invisible and "Invisible" not in buffs:
            buffs.append("Invisible")
        if self.sight and "Vision" not in buffs:
            buffs.append("Vision")
        if not buffs:
            buffs.append("None")
        return ", ".join(buffs)

    def level_up(self) -> None:
        raise NotImplementedError

    def special_attack(self, target: Character) -> str:
        raise NotImplementedError
