"""Keys, tools, scrolls, reagents, and quest-item implementations."""

from __future__ import annotations

import random
from textwrap import wrap
from typing import TYPE_CHECKING

from .. import abilities
from .base import Misc

if TYPE_CHECKING:
    from typing import Any

    from ..character import Character


class Key(Misc):
    """
    Opens locked chests
    """

    def __init__(self):
        super().__init__(name="Key", description="Unlocks a locked chest but is consumed.", value=500, rarity=0.9,
                         subtyp='Key')


class OldKey(Misc):
    """
    Opens locked doors
    """

    def __init__(self):
        super().__init__(name="Old Key", description="Unlocks doors that may lead to either valuable treasure or to "
                                                     "powerful enemies.",
                         value=50000, rarity=0.5, subtyp='Key')


class MasterKey(Misc):
    """
    Special item; Opens locked chest and doors; is not consumed upon use
    """

    def __init__(self):
        super().__init__(name="Master Key", description="Unlocks doors that may lead to either valuable treasure or to "
                                                     "powerful enemies.",
                         value=0, rarity=0, subtyp='Key')


class CrypticKey(Misc):
    """
    A mysterious key of unknown purpose; appears to be crafted with care and precision
    """

    def __init__(self):
        super().__init__(name="Cryptic Key",
                         description="A pristine key forged by Griswold. Its purpose is shrouded in mystery, "
                                     "but it feels important.",
                         value=0, rarity=0, subtyp='Key')


class LockpickKit(Misc):
    """
    Reusable tools required for Lockpick and Master Lockpick skills.
    """

    def __init__(self, charges: int = 3):
        self.charges = max(1, int(charges))
        super().__init__(
            name="Lockpick Kit",
            description=(
                "A compact set of picks, tension wrenches, and shims required to use "
                f"lockpicking skills. Durability: {self.charges}."
            ),
            value=1500,
            rarity=0.55,
            subtyp="Tool",
        )


class SmokeBomb(Misc):
    """
    One-use tool required for Smoke Screen.
    """

    def __init__(self):
        super().__init__(
            name="Smoke Bomb",
            description="A packed clay pellet that bursts into concealing smoke. Required and consumed by Smoke Screen.",
            value=750,
            rarity=0.65,
            subtyp="Tool",
        )


class Oculus(Misc):
    """
    Expensive magic lens that reveals fake walls.
    """

    def __init__(self):
        super().__init__(
            name="Oculus",
            description="An expensive arcane lens that reveals the telltale shimmer of fake walls.",
            value=35000,
            rarity=0.25,
            subtyp="Magic Tool",
        )


def _inventory_stack(character, item_name: str):
    inventory = getattr(character, "inventory", {}) or {}
    stack = inventory.get(item_name, [])
    return stack if isinstance(stack, list) else []


def has_lockpick_kit(character) -> bool:
    """Return whether a character carries the reusable lockpicking tools."""
    return bool(_inventory_stack(character, "Lockpick Kit"))


def has_smoke_bomb(character) -> bool:
    """Return whether a character carries a Smoke Bomb."""
    return bool(_inventory_stack(character, "Smoke Bomb"))


def has_oculus(character) -> bool:
    """Return whether a character carries an Oculus."""
    return bool(_inventory_stack(character, "Oculus"))


def can_detect_fake_walls(character) -> bool:
    """Return whether passive dungeon perception reveals nearby fake walls."""
    skills = getattr(character, "spellbook", {}).get("Skills", {})
    return "Keen Eye" in skills or has_oculus(character)


def lockpick_break_chance(character, *, master: bool = False) -> float:
    """Chance that a Lockpick Kit breaks after a successful lockpick use."""
    stats = getattr(character, "stats", None)
    dex = getattr(stats, "dex", getattr(stats, "dexterity", 10))
    try:
        dex_score = int(dex)
    except (TypeError, ValueError):
        dex_score = 10
    base = 0.18 if master else 0.35
    floor = 0.04 if master else 0.08
    chance = base - max(0, dex_score - 10) * 0.01
    return max(floor, min(base, chance))


def use_lockpick_kit(character, *, master: bool = False, roll: float | None = None) -> tuple[bool, str]:
    """Spend durability on a Lockpick Kit and possibly break it."""
    stack = _inventory_stack(character, "Lockpick Kit")
    if not stack:
        return False, "You need a Lockpick Kit."

    kit = stack[0]
    charges = int(getattr(kit, "charges", 3) or 3)
    kit.charges = max(0, charges - 1)
    if hasattr(kit, "description"):
        kit.description = (
            "A compact set of picks, tension wrenches, and shims required to use "
            f"lockpicking skills. Durability: {kit.charges}."
        )

    chance = lockpick_break_chance(character, master=master)
    break_roll = random.random() if roll is None else float(roll)
    if kit.charges <= 0 or break_roll < chance:
        character.modify_inventory(kit, subtract=True)
        return True, "The Lockpick Kit breaks."
    return True, f"The Lockpick Kit holds together. Durability: {kit.charges}."


def consume_smoke_bomb(character) -> tuple[bool, str]:
    """Consume one Smoke Bomb for Smoke Screen."""
    stack = _inventory_stack(character, "Smoke Bomb")
    if not stack:
        return False, "Smoke Screen requires a Smoke Bomb.\n"
    character.modify_inventory(stack[0], subtract=True)
    return True, "A Smoke Bomb bursts open.\n"


class JesterToken(Misc):
    """
    A shimmering token from the funhouse; collect all four to unlock the Jester's chamber
    """

    def __init__(self):
        super().__init__(name="Jester Token",
                         description="A carnival token that shimmers with magical energy. These are required to breach "
                                     "the Jester's inner sanctum.",
                         value=0, rarity=0, subtyp='Quest')


class Scroll(Misc):
    """
    Scrolls allow for a one-time use of a spell; scrolls can only be used in combat
    """

    def __init__(self):
        super().__init__(name="Scroll", description="Base class for scrolls.", value=0, rarity=0, subtyp='Scroll')
        self.spell = None
        self.charges = random.randint(2, 10)

    def use(self, user: Character, target: Character | None = None, tile: Any = None) -> str:
        use_str = f"{user.name} uses {self.name}.\n"
        use_str += str(self.spell.cast(user, target=target, special=True))
        self.charges -= 1
        if not self.charges:
            use_str += "The scroll crumbles to dust in your hands!\n"
            user.modify_inventory(self, subtract=True)
        return use_str


class BlessScroll(Scroll):
    """
    Bless
    """

    def __init__(self):
        super().__init__()
        self.name = "Bless Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast Bless, which"
                                          " increases attack damage for several turns. The scroll will be consumed "
                                          "when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 1000
        self.rarity = 0.9
        self.spell = abilities.Bless()


class SleepScroll(Scroll):
    """
    Sleep
    """

    def __init__(self):
        super().__init__()
        self.name = "Sleep Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast Sleep. The "
                                          "scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 2000
        self.rarity = 0.85
        self.spell = abilities.Sleep()


class FireScroll(Scroll):
    """
    Firebolt
    """

    def __init__(self):
        super().__init__()
        self.name = "Fire Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the fire "
                                          "spell Firebolt. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 3000
        self.rarity = 0.75
        self.spell = abilities.Firebolt()


class IceScroll(Scroll):
    """
    Ice Lance
    """

    def __init__(self):
        super().__init__()
        self.name = "Ice Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the ice "
                                          "spell Ice Lance. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 3000
        self.rarity = 0.75
        self.spell = abilities.IceLance()


class ElectricScroll(Scroll):
    """
    Shock
    """

    def __init__(self):
        super().__init__()
        self.name = "Electric Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the electric"
                                          " spell Shock. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 3000
        self.rarity = 0.75
        self.spell = abilities.Shock()


class WaterScroll(Scroll):
    """
    Water Jet
    """

    def __init__(self):
        super().__init__()
        self.name = "Water Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the water "
                                          "spell Water Jet. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 3000
        self.rarity = 0.75
        self.spell = abilities.WaterJet()


class EarthScroll(Scroll):
    """
    Tremor
    """

    def __init__(self):
        super().__init__()
        self.name = "Earth Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the earth "
                                          "spell Tremor. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 3000
        self.rarity = 0.75
        self.spell = abilities.Tremor()


class WindScroll(Scroll):
    """
    Gust
    """

    def __init__(self):
        super().__init__()
        self.name = "Wind Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the wind "
                                          "spell Gust. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 3000
        self.rarity = 0.75
        self.spell = abilities.Gust()


class ShadowScroll(Scroll):
    """
    Shadow Bolt
    """

    def __init__(self):
        super().__init__()
        self.name = "Shadow Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the "
                                          "shadow spell Shadow Bolt. The scroll will be consumed when it is out of "
                                          "charges.", 35, break_on_hyphens=False))
        self.value = 4000
        self.rarity = 0.7
        self.spell = abilities.ShadowBolt()


class HolyScroll(Scroll):
    """
    Holy
    """

    def __init__(self):
        super().__init__()
        self.name = "Holy Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the holy "
                                          "spell Holy. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 4000
        self.rarity = 0.7
        self.spell = abilities.Holy()


class CleanseScroll(Scroll):
    """
    Cleanse
    """

    def __init__(self):
        super().__init__()
        self.name = "Cleanse Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the holy"
                                          " spell Cleanse. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 4000
        self.rarity = 0.7
        self.spell = abilities.Cleanse()


class BoostScroll(Scroll):
    """
    Boost
    """

    def __init__(self):
        super().__init__()
        self.name = "Boost Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the heal "
                                          "spell Boost. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 8000
        self.rarity = 0.6
        self.spell = abilities.Boost()


class ShellScroll(Scroll):
    """
    Shell
    """

    def __init__(self):
        super().__init__()
        self.name = "Shell Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the heal "
                                          "spell Shell. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 8000
        self.rarity = 0.6
        self.spell = abilities.Shell()


class SilenceScroll(Scroll):
    """
    Silence
    """

    def __init__(self):
        super().__init__()
        self.name = "Silence Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast Silence, "
                                          "which can prevent an target from casting spell for a time. The scroll will"
                                          " be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 8000
        self.rarity = 0.6
        self.spell = abilities.Silence()


class DispelScroll(Scroll):
    """
    Dispel
    """

    def __init__(self):
        super().__init__()
        self.name = "Dispel Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast Dispel, "
                                          "which can remove all positive status effects from the target. The scroll"
                                          " will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 10000
        self.rarity = 0.5
        self.spell = abilities.Dispel()


class DeathScroll(Scroll):
    """
    Desoul
    """

    def __init__(self):
        super().__init__()
        self.name = "Death Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast Desoul, "
                                          "which can kill the target. The scroll will be consumed when it is out "
                                          "of charges.", 35, break_on_hyphens=False))
        self.value = 15000
        self.rarity = 0.4
        self.spell = abilities.Desoul()


class SanctuaryScroll(Scroll):
    """
    Sanctuary
    """

    def __init__(self):
        super().__init__()
        self.name = "Sanctuary Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast Sanctuary,"
                                          " which can return the user to town. The scroll will be consumed when it is"
                                          " out of charges.", 35, break_on_hyphens=False))
        self.value = 50000
        self.rarity = 0.25
        self.spell = abilities.Sanctuary()

    def use(
        self,
        user: Character,
        target: Character | None = None,
        tile: Any = None,
    ) -> str:
        use_str = f"{user.name} uses {self.name}.\n"
        use_str += self.spell.cast_out(user=user)
        self.charges -= 1
        if not self.charges:
            use_str += "The scroll crumbles to dust in your hands!\n"
            user.modify_inventory(self, subtract=True)
        return use_str


class UltimaScroll(Scroll):
    """
    Ultima
    """

    def __init__(self):
        super().__init__()
        self.name = "Ultima Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the powerful"
                                          " Ultima. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 100000
        self.rarity = 0.01
        self.spell = abilities.Ultima()


class SheetMusic(Misc):
    """
    Base sheet music item; sheet music is not purchasable, only created
    """

    def __init__(self, name: str, description: str, value: int, rarity: float, subtyp: str) -> None:
        super().__init__(name, description, value, rarity, subtyp)
        self.song_name = name.replace("Sheet Music: ", "")

    def use(
        self,
        user: Character,
        target: Character | None = None,
        tile: Any = None,
    ) -> str:
        from ..classes import bard

        success, message = bard.start_song(user, self.song_name, target=target)
        if success:
            user.modify_inventory(self, subtract=True)
            message += f"The sheet music for {self.song_name} is spent.\n"
        return message


class BattleHymnSheet(SheetMusic):
    def __init__(self):
        super().__init__("Sheet Music: Battle Hymn", "A martial hymn for battle.", 2500, 0, "Scroll")


class RampartsOdeSheet(SheetMusic):
    def __init__(self):
        super().__init__("Sheet Music: Ode to the Ramparts", "A protective ode.", 2500, 0, "Scroll")


class DysfunctionSymphonySheet(SheetMusic):
    def __init__(self):
        super().__init__("Sheet Music: Symphony of Disfunction", "A discordant enemy-breaking score.", 2500, 0, "Scroll")


class LowDefenseRhapsodySheet(SheetMusic):
    def __init__(self):
        super().__init__("Sheet Music: Low-defense-ian Rhapsody", "A tune that lowers defenses.", 2500, 0, "Scroll")


class SlowRideSheet(SheetMusic):
    def __init__(self):
        super().__init__("Sheet Music: Slow Ride", "A dragging song.", 2500, 0, "Scroll")


class BonesThugsHarmonySheet(SheetMusic):
    def __init__(self):
        super().__init__("Sheet Music: Bones, Thugs, and Harmony", "A graveyard harmony.", 2500, 0, "Scroll")


class ScoresAndScoresScoreSheet(SheetMusic):
    def __init__(self):
        super().__init__("Sheet Music: Scores and Scores Score", "A score about scoring.", 2500, 0, "Scroll")


class GoldTriggerSheet(SheetMusic):
    def __init__(self):
        super().__init__("Sheet Music: Gold Trigger", "A glittering trigger phrase.", 2500, 0, "Scroll")


class ChorusTimeSheet(SheetMusic):
    def __init__(self):
        super().__init__("Sheet Music: Chorus Time", "A looping chorus.", 2500, 0, "Scroll")


class BlankScroll(Misc):
    """
    Blank scroll used by Spell Stealer/Arcane Trickster to store spells.
    """

    def __init__(
        self,
        name: str = "Blank Scroll",
        description: str | None = None,
        value: int = 2500,
        rarity: float = 0.45,
        subtyp: str = "Scroll",
    ) -> None:
        super().__init__(
            name=name,
            description=description or "\n".join(wrap(
                    "A prepared scroll with enough receptive ink to hold one stolen spell.",
                    35,
                    break_on_hyphens=False,
                )),
            value=value,
            rarity=rarity,
            subtyp=subtyp,
        )


class InscribedSpellScroll(Scroll):
    """
    A stolen-spell scroll that preserves the original spell identity.
    """

    def __init__(self, spell_class_name: str = "MagicMissile", charges: int | None = None) -> None:
        super().__init__()
        self.spell_class_name = spell_class_name
        spell_cls = getattr(abilities, spell_class_name, abilities.MagicMissile)
        self.spell = spell_cls()
        self.name = f"Stolen {self.spell.name} Scroll"
        if charges is not None:
            self.charges = max(1, int(charges))
        self._refresh_description()
        self.value = max(3000, int(getattr(self.spell, "cost", 0) or 0) * 1000)
        self.rarity = 0.2

    def _refresh_description(self) -> None:
        self.description = (
            f"Scroll inscribed with a stolen copy of {self.spell.name}. "
            f"Charges: {self.charges}. The scroll crumbles when its charges run out."
        )

    def use(self, user: Character, target: Character | None = None, tile: Any = None) -> str:
        use_str = super().use(user, target=target, tile=tile)
        if self.charges > 0:
            self._refresh_description()
        return use_str


class RatTail(Misc):

    def __init__(self):
        super().__init__(name="Rat Tail", description="The tail of a rat.",
                         value=0, rarity=1, subtyp="Quest")


class MysteryMeat(Misc):

    def __init__(self):
        super().__init__(name="Mystery Meat", description="Unknown meat with a strange smell. Maybe you could do "
                                                          "something with this.",
                         value=0, rarity=0.5, subtyp="Quest")


class TicketPiece(Misc):

    def __init__(self):
        super().__init__(name="Ticket Piece", description="A scrap of a lottery ticket with a few numbers on it.",
                         value=0, rarity=0, subtyp="Quest")


class DeadSoldier(Misc):

    def __init__(self):
        super().__init__(name="Dead Soldier", description="The partially eaten body of a very green soldier. He never "
                                                          "stood a chance...",
                         value=0, rarity=0, subtyp="Quest")
        self.weight = 100


class Leather(Misc):

    def __init__(self):
        super().__init__(name="Leather", description="The dried skin of an animal, used for various purposes.",
                         value=0, rarity=0.5, subtyp="Quest")


class Feather(Misc):

    def __init__(self):
        super().__init__(name="Feather", description="The feather of a bird.",
                         value=0, rarity=0.5, subtyp="Quest")


class SnakeSkin(Misc):

    def __init__(self):
        super().__init__(name="Snake Skin", description="The skin of a snake.",
                         value=0, rarity=1, subtyp="Quest")


class ScrapMetal(Misc):

    def __init__(self):
        super().__init__(name="Scrap Metal", description="A chunk of metal.",
                         value=0, rarity=0.5, subtyp="Quest")


class CursedHops(Misc):

    def __init__(self):
        super().__init__(name="Cursed Hops", description="Hops from a cursed tree, these flower are used primarily in"
                                                         " the creation of beer and other beverages, as well as herbal "
                                                         "medicines.",
                         value=0, rarity=1, subtyp="Quest")


class BirdFat(Misc):

    def __init__(self):
        super().__init__(name="Bird Fat", description="The fat from a bird, used as a fuel for lamps.",
                         value=0, rarity=0.1, subtyp="Quest")


class ElementalMote(Misc):

    def __init__(self):
        super().__init__(name="Elemental Mote", description="The elemental core of a Myrmidon.",
                         value=0, rarity=1, subtyp="Quest")


class Acorn(Misc):

    def __init__(self):
        super().__init__(name="Acorn", description="A hardy oak seed prized by druids for growth rites.",
                         value=25, rarity=0.5, subtyp="Reagent")


class VineSeed(Misc):

    def __init__(self):
        super().__init__(name="Vine Seed", description="A coiled seed that hums with grasping green life.",
                         value=25, rarity=0.5, subtyp="Reagent")


class FungusSpore(Misc):

    def __init__(self):
        super().__init__(name="Fungus Spore", description="A powdery spore bundle useful in poison and decay rites.",
                         value=25, rarity=0.5, subtyp="Reagent")


class HemlockRoot(Misc):

    def __init__(self):
        super().__init__(name="Hemlock Root", description="A bitter root gathered for dangerous druidic mixtures.",
                         value=25, rarity=0.5, subtyp="Reagent")


class PowerCore(Misc):

    def __init__(self):
        super().__init__(name="Power Core", description="The power source of a Golem.",
                         value=0, rarity=1, subtyp="Quest")


class Phylactery(Misc):

    def __init__(self):
        super().__init__(name="Phylactery", description="The soul artifcat of a Lich, given up willingly to achieve "
                                                        "immortality.",
                         value=0, rarity=0.05, subtyp="Quest")


class LuckyLocket(Misc):
    """
    Momento given to the warrior Joffrey by the waitress, his betrothed
    """

    def __init__(self):
        super().__init__(name="Lucky Locket", description="A simple gold necklace with a locket containing the picture "
                                                          "of a fair lass.",
                         value=0, rarity=0, subtyp="Special")


class BrassKey(Misc):
    """
    Special key believed to be for opening the tavern but actually opens Joffrey's locker in barracks
    """

    def __init__(self):
        super().__init__(name="Brass Key", description="A brass key, similar to the key for your storage locker in the"
                                                       " barracks.",
                         value=0, rarity=0, subtyp="Special")


class ThievesGuildSignet(Misc):
    """
    Proof recovered from the Thieves Guild initiation trial.
    """

    def __init__(self):
        super().__init__(
            name="Thieves Guild Signet",
            description="A blackened silver signet taken from the guild's hidden initiation trial.",
            value=0,
            rarity=1,
            subtyp="Special",
        )


class JoffreysLetter(Misc):
    """
    A letter written from Joffrey to the waitress; maybe there is some use of this
    """

    def __init__(self):
        super().__init__(name="Joffrey's Letter", description="A letter written from Joffrey to the waitress; maybe "
                                                              "there is some use of this.",
                         value=0, rarity=0, subtyp="Special")


class EmptyVial(Misc):
    """
    Given by Alchemist; used to collect Spring Water from Underground Spring
    """

    def __init__(self):
        super().__init__(name="Empty Vial", description="An empty vial, perfect for storing liquids and other "
                                                        "tinctures.",
                         value=0, rarity=0, subtyp='Special')


class SpringWater(Misc):
    """
    Obtained when you visit the Underground Spring during quest Naivete from Alchemist
    """

    def __init__(self):
        super().__init__(name="Spring Water", description="A vial of the finest spring water.",
                         value=0, rarity=0, subtyp='Special')


class Unobtainium(Misc):
    """
    Magical ore that can be used to forge ultimate weapons at the blacksmith; only one in the game
    """

    def __init__(self):
        super().__init__(name="Unobtainium", description="The legendary ore that has only been theorized. Can be used "
                                                         "to create ultimate weapons.",
                         value=0, rarity=0, subtyp='Special')


class Relic1(Misc):
    """
    The first of six relics required to unlock the final boss
    """

    def __init__(self):
        super().__init__(name="Triangulus", description="The holy trinity of mind, body, and spirit are represented by "
                                                        "the Triangulus relic.",
                         value=0, rarity=0, subtyp='Special')


class Relic2(Misc):
    """
    The second of six relics required to unlock the final boss
    """

    def __init__(self):
        super().__init__(name="Quadrata", description="The Quadrata relic symbolizes order, trust, stability, and "
                                                      "logic, the hallmarks of a well-balanced person.",
                         value=0, rarity=0, subtyp='Special')


class Relic3(Misc):
    """
    The third of six relics required to unlock the final boss
    """

    def __init__(self):
        super().__init__(name="Hexagonum", description="The Hexagonum relic represents the natural world, since the "
                                                       "hexagon is the considered the strongest shape and regularly "
                                                       "found in nature.",
                         value=0, rarity=0, subtyp='Special')


class Relic4(Misc):
    """
    The fourth of six relics required to unlock the final boss
    """

    def __init__(self):
        super().__init__(name="Luna", description="The Moon, our celestial partner, is the inspiration for the Luna "
                                                  "relic and represents love for others.",
                         value=0, rarity=0, subtyp='Special')


class Relic5(Misc):
    """
    The fifth of six relics required to unlock the final boss
    """

    def __init__(self):
        super().__init__(name="Polaris", description="The Polaris relic resembles the shape of a star and represents "
                                                     "the guiding light of the North Star.",
                         value=0, rarity=0, subtyp='Special')


class Relic6(Misc):
    """
    The sixth and final of six relics required to unlock the final boss
    """

    def __init__(self):
        super().__init__(name="Infinitas", description="Shaped like a circle, the Infinitas relic represents the never-"
                                                       "ending struggle between good and evil.",
                         value=0, rarity=0, subtyp='Special')


class Excaliper(Misc):
    """
    item used to summon Maid of the Spring Nimue at the UndergroundSpring at 3:E10
    """

    def __init__(self):
        super().__init__(name="Excaliper", description="The broken fragments of a failed experiment. It appears "
                                                       "someone tried to forge the legendary sword Excalibur using "
                                                       "a caliper tool. It did not go well...",
                        value=0, rarity=0, subtyp="Special")


class ChaliceMap(Misc):
    """
    A worn map tied to the Golden Chalice questline.
    """

    def __init__(self):
        super().__init__(
            name="Chalice Map",
            description="A weathered map whose ink appears almost completely faded.",
            value=0,
            rarity=0,
            subtyp="Special",
        )


class GoldenChalice(Misc):
    """
    Quest item to complete "The Holy Grail of Quests"; requires visiting several locations in town and in the dungeon to uncover the hidden location

    Places to visit with quest active to get location:
    - talk with Hooded Figure at tavern in town; tells player to locate map last seen with adventurer carrying an ugly sword
    - revisit boulder where Excaliper was found; find map hidden in crevice
    - visit Sergeant at barracks with map in inventory; Sergeant tells player to find the adventurer
    - find adventurer at secret location at 3:12,14; adventurer gives player the location of the Golden Chalice
    - visit location at 6:2,17 to find Golden Chalice and complete quest
    """

    def __init__(self):
        super().__init__(name="Golden Chalice", description="A golden chalice that once held the Holy Grail. It is said "
                                                          "that the chalice can grant immense power to those who drink "
                                                          "from it, but it is also cursed with a terrible thirst.",
                         value=0, rarity=0, subtyp="Special")


class SerpentVenomHeart(Misc):
    """Archdruid Venom ritual catalyst."""

    def __init__(self):
        super().__init__(
            name="Serpent Venom Heart",
            description="A pulsing knot of venom that refuses to die.",
            value=0,
            rarity=0,
            subtyp="Special",
        )


class HeartstoneShard(Misc):
    """Archdruid Stone ritual catalyst."""

    def __init__(self):
        super().__init__(
            name="Heartstone Shard",
            description="A mineral fragment that beats once when held still.",
            value=0,
            rarity=0,
            subtyp="Special",
        )


class VerdantSeed(Misc):
    """Archdruid Growth ritual catalyst."""

    def __init__(self):
        super().__init__(
            name="Verdant Seed",
            description="A sleeping seed warm with impossible spring.",
            value=0,
            rarity=0,
            subtyp="Special",
        )


class StormglassFeather(Misc):
    """Archdruid Storm ritual catalyst."""

    def __init__(self):
        super().__init__(
            name="Stormglass Feather",
            description="A translucent feather with lightning trapped along its spine.",
            value=0,
            rarity=0,
            subtyp="Special",
        )


class Joker(Misc):
    """
    Dropped by Jester; used to obtain the trickster summon Kobalos
    """

    def __init__(self):
        super().__init__(name="Joker", description="They say that Joker's are wild; you'll see how wild this one is.",
                         value=0, rarity=1, subtyp="Special")
        self.restricted_classes = ["Summoner", "Grand Summoner", "Spell Stealer", "Arcane Trickster"]


class ChiryuKoma(Misc):
    """
    Needed to unlock Dilong summon; visit 1:I17 with item in inventory
    """

    def __init__(self):
        super().__init__(name="Chiryu Koma", description="A game piece used for shogi, depicting an earth dragon.",
                         value=0, rarity=0.1, subtyp="Summon - Dilong")
        self.restricted_classes = ["Summoner", "Grand Summoner"]


class BlacksmithsHammer(Misc):
    """
    Needed to unlock Cacus summon; gained after obtaining first 2 relics and visiting Griswold; visit 2:F13 with item
      in inventory
    """

    def __init__(self):
        super().__init__(name="Blacksmith's Hammer", description="It looks like a normal blacksmithing hammer but "
                                                                 "something seems...special about this one.",
                         value=0, rarity=0, subtyp="Summon - Cacus")
        self.restricted_classes = ["Summoner", "Grand Summoner"]


class DragonTear(Misc):
    """
    Super rare drop from Dragon-type enemies. Unlocks the Recover modification for the Jump ability.
    Only available to Lancer and Dragoon classes.
    """

    def __init__(self):
        super().__init__(name="Dragon's Tear",
                         description="A crystallized tear shed by a dragon. Said to contain the essence "
                                   "of draconic vitality and regeneration. Extremely rare.",
                         value=0, rarity=0.01, subtyp="Ability")
        self.restricted_classes = ["Lancer", "Dragoon"]


class KaelenonPortalKey(Misc):
    """Quest item used to return Kaelenon home."""

    def __init__(self):
        super().__init__(
            name="Kaelenon's Portal Key",
            description="A glass-dark key printed from the Realm of Cambion terminal for Kaelenon's return home.",
            value=0,
            rarity=0,
            subtyp="Special",
        )


class Draconite(Misc):
    """Quest material left by Kaelenon after returning home."""

    def __init__(self):
        super().__init__(
            name="Draconite",
            description="A red-black shard from Kaelenon's home realm, warm with restored draconic power.",
            value=0,
            rarity=0,
            subtyp="Special",
        )
