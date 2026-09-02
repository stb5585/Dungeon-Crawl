"""Shield, tome, rod, and instrument implementations."""

from __future__ import annotations

from .base import OffHand


class NoOffHand(OffHand):

    def __init__(self):
        super().__init__(name="No OffHand", description="No off-hand equipped.", value=0, rarity=0, mod=0,
                         subtyp='None', unequip=True)


class Buckler(OffHand):

    def __init__(self):
        super().__init__(name="Buckler", description="A small round shield held by a handle or worn on the forearm.",
                         value=25, rarity=0.95, mod=0.05, subtyp='Shield', unequip=False)
        self.weight = 2


class Aspis(OffHand):

    def __init__(self):
        super().__init__(name="Aspis", description="An aspis is a heavy wooden shield with a handle at the edge and is "
                                                   "strapped to the forearm for greater mobility.",
                         value=100, rarity=0.9, mod=0.1, subtyp='Shield', unequip=False)
        self.weight = 10


class Targe(OffHand):

    def __init__(self):
        super().__init__(name="Targe", description="A targe is a circular, concave shield fitted with straps on the "
                                                   "inside to be attached to the forearm, featuring metal studs on the "
                                                   "face for durability and additional offensive power.",
                         value=500, rarity=0.85, mod=0.15, subtyp='Shield', unequip=False)
        self.weight = 7


class Glagwa(OffHand):

    def __init__(self):
        super().__init__(name="Glagwa", description="A glagwa is a bell-shaped shield made from iron and covered with "
                                                    "leather for improved durability.",
                         value=2500, rarity=0.75, mod=0.2, subtyp='Shield', unequip=False)
        self.weight = 13


class KiteShield(OffHand):

    def __init__(self):
        super().__init__(name="Kite Shield", description="A kite shield is a large, almond-shaped shield rounded at the"
                                                         " top and curving down to a point or rounded point at the "
                                                         "bottom. The term \"kite shield\" is a reference to the "
                                                         "shield's unique shape, and is derived from its supposed "
                                                         "similarity to a flying kite.",
                         value=15000, rarity=0.5, mod=0.25, subtyp='Shield', unequip=False)
        self.weight = 15


class Pavise(OffHand):

    def __init__(self):
        super().__init__(name="Pavise", description="A pavise is an oblong shield similar to a tower shield that "
                                                    "features a spike at the bottom to hold it in place to provide full"
                                                    " body protection.",
                         value=42000, rarity=0.4, mod=0.3, subtyp='Shield', unequip=False)
        self.weight = 20


class Svalinn(OffHand):

    def __init__(self):
        super().__init__(name="Svalinn", description="The svalinn is a mythical shield that symbolizes protection "
                                                     "and strength, often depicted as an essential element in the "
                                                     "cosmic balance.",
                         value=75000, rarity=0.2, mod=0.35, subtyp='Shield', unequip=False)
        self.weight = 18


class MedusaShield(OffHand):

    def __init__(self):
        super().__init__(name="Medusa Shield", description="A shield that has been polished to resemble a mirror. Said"
                                                           " to be used to defeat the Gorgon Medusa. Reflects back some"
                                                           " magic.",
                         value=150000, rarity=0.05, mod=0.4, subtyp='Shield', unequip=False)
        self.weight = 25


class NaturalShield(OffHand):

    def __init__(self, name: str, mod: float, subtyp: str) -> None:
        super().__init__(name=name, mod=mod, subtyp=subtyp, description="", rarity=0, unequip=False, value=0)
        self.name = name
        self.mod = mod
        self.subtyp = subtyp


class ForceField(NaturalShield):

    def __init__(self):
        super().__init__(name="Force Field", mod=0.1, subtyp="Shield")


class ForceField2(ForceField):

    def __init__(self):
        super().__init__()
        self.mod = 0.2


class ForceField3(ForceField):

    def __init__(self):
        super().__init__()
        self.mod = 0.3


class Book(OffHand):

    def __init__(self):
        super().__init__(name="Book", description="A book of notes taken during the character's apprenticeship.",
                         value=25, rarity=0.95, mod=6, subtyp='Tome', unequip=False)
        self.weight = 1


class TomeKnowledge(OffHand):

    def __init__(self):
        super().__init__(name="Tome of Knowledge", description="A tome containing secrets to enhancing spells.",
                         value=500, rarity=0.9, mod=14, subtyp='Tome', unequip=False)
        self.weight = 3


class InfernalGrimoire(OffHand):

    def __init__(self):
        super().__init__(name="Infernal Grimoire", description="A blackened, flame-wreathed book that burns to the "
                                                                "touch but never turns to ash.",
                         value=2500, rarity=0.85, mod=22, subtyp='Tome', unequip=False)
        self.weight = 3


class ElementalPrimer(OffHand):

    def __init__(self):
        super().__init__(name="Elemental Primer", description="A multi-colored tome that shifts between elemental "
                                                              "motifs depending on its surroundings.",
                         value=10000, rarity=0.75, mod=30, subtyp='Tome', unequip=False)
        self.weight = 2


class TreatiseBalance(OffHand):

    def __init__(self):
        super().__init__(name="Treatise of Balance", description="A weathered tome, marked with a taijitu, better "
                                                                 "known as the yin and yang symbol. The pages are "
                                                                 "filled with intricate diagrams illustrating the "
                                                                 "harmony of opposing forces.",
                         value=16000, rarity=0.6, mod=36, subtyp='Tome', unequip=False)
        self.weight = 3


class DragonRouge(OffHand):

    def __init__(self):
        super().__init__(name="Dragon Rouge", description="French for \"Red Dragon\", this mythical tome contains "
                                                          "ancient knowledge passed down through the ages.",
                         value=21000, rarity=0.5, mod=42, subtyp='Tome', unequip=False)
        self.weight = 4


class Vedas(OffHand):

    def __init__(self):
        super().__init__(name="Vedas", description="A large body of religious texts, consisting of some of the oldest "
                                                   "holy teachings.",
                         value=50000, rarity=0.4, mod=54, subtyp='Tome', unequip=False)
        self.weight = 4


class CompendiumAncients(OffHand):

    def __init__(self):
        super().__init__(name="Compendium of the Ancients", description="A colossal tome filled with records of "
                                                                        "forgotten civilizations, written in a "
                                                                        "language lost to time.",
                         value=65000, rarity=0.2, mod=65, subtyp='Tome', unequip=False)
        self.weight = 5


class Necronomicon(OffHand):

    def __init__(self):
        super().__init__(name="Necronomicon", description="The Book of the Dead, a mystical grimoire written by an "
                                                          "unknown author.",
                         value=72000, rarity=0.2, mod=75, subtyp='Tome', unequip=False)
        self.weight = 6
        self.restriction = ['Warlock', 'Necromancer']


class Magus(OffHand):

    def __init__(self):
        super().__init__(name="Magus", description="A book of magical art written by a powerful wizard.",
                         value=90000, rarity=0.05, mod=90, subtyp='Tome', unequip=False)
        self.weight = 3


class CodexEternity(OffHand):
    """
    Rare drop from Merzhin in Realm of Cambion
    """

    def __init__(self):
        super().__init__(name="Codex of Eternity", description="A shimmering tome bound in starlight, with pages that "
                                                               "shift and reform endlessly.",
                         value=150000, rarity=0.01, mod=130, subtyp='Tome', unequip=False)


class WillowDiviningRod(OffHand):

    def __init__(self):
        super().__init__(name="Willow Divining Rod", description="A fresh willow switch wrapped in copper thread. "
                                                                 "It is humble work, but the forked tip answers "
                                                                 "many questions.",
                         value=12000, rarity=0.6, mod=30, subtyp='Rod', unequip=False)
        self.weight = 1


class CopperLeyRod(OffHand):

    def __init__(self):
        super().__init__(name="Copper Ley Rod", description="A straight copper rod etched with ley-line marks. "
                                                            "It steadies minor omens and strengthens early rune work.",
                         value=19000, rarity=0.5, mod=38, subtyp='Rod', unequip=False)
        self.weight = 2


class MoonlitHazelRod(OffHand):

    def __init__(self):
        super().__init__(name="Moonlit Hazel Rod", description="Hazel harvested under a clear moon and capped with "
                                                               "silver. It answers elemental signs with a quieter, "
                                                               "stronger pulse.",
                         value=45000, rarity=0.4, mod=45, subtyp='Rod', unequip=False)
        self.weight = 2


class DowsingRod(OffHand):

    def __init__(self):
        super().__init__(name="Dowsing Rod", description="Also known as a divining rod, this oak Y-shaped branch "
                                                         "is thought to help locate natural sources of water. But "
                                                         "this is no normal dowsing rod, enhanced by the power of "
                                                         "Poseidon. All water-based spells gain double the bonus to "
                                                         "spell damage.",
                         value=75000, rarity=0.2, mod=50, subtyp='Rod', unequip=False)
        self.weight = 2


class ScepterIfrit(OffHand):

    def __init__(self):
        super().__init__(name="Scepter of Ifrit", description="A flaming scepter imbued by the wrath of Ifrit. All "
                                                              "fire-based spells gain double the bonus to spell "
                                                              "damage.",
                         value=75000, rarity=0.2, mod=50, subtyp='Rod', unequip=False)
        self.weight = 3


class GaiasBranch(OffHand):

    def __init__(self):
        super().__init__(name="Gaia's Branch", description="Mother Earth embodies all the living things, including the"
                                                           " tree of life. As a sacrifice to combat those who try to "
                                                           "hurt her, a single branch was removed and infused with the "
                                                           "power of her domain. All earth-based spells gain double "
                                                           "the bonus to spell damage.",
                         value=75000, rarity=0.2, mod=50, subtyp='Rod', unequip=False)
        self.weight = 3


class Zephyruswand(OffHand):

    def __init__(self):
        super().__init__(name="Zephyruswand", description="As the God of the West Wind, Zephyrus lends his power to "
                                                          "user. All wind-based spells gain double the bonus to spell "
                                                          "damage.",
                         value=75000, rarity=0.2, mod=50, subtyp='Rod', unequip=False)
        self.weight = 1


class RainbowRod(OffHand):

    def __init__(self):
        super().__init__(name="Rainbow Rod", description="A radiant rod imbued with the essence of every elemental "
                                                         "power, the Rainbow Rod amplifies the user's spells across"
                                                         " all types, enhancing each with a vibrant, prismatic aura. "
                                                         "All elemental spells gain double the bonus to spell damage.",
                         value=200000, rarity=0.05, mod=80, subtyp='Rod', unequip=False)
        self.weight = 3


class UltimaScepter(OffHand):

    def __init__(self):
        super().__init__(name="Photon Sphere Scepter", description="Crafted to harness the pure, devastating power of the "
                                                            "Photon Sphere spell, this scepter is an artifact of forbidden "
                                                            "magic and unparalleled potency. The Photon Sphere Scepter "
                                                            "channels immense energy directly into the spell, "
                                                            "making it a weapon of unmatched finality in battle, "
                                                            "doubling the bonus to spell damage.",
                         value=250000, rarity=0.01, mod=100, subtyp='Rod', unequip=False)
        self.weight = 5


class Lute(OffHand):

    def __init__(self):
        super().__init__(name="Lute", description="",
                         value=5000, rarity=0.75, mod=20, subtyp="Musical Instrument", unequip=False)
        self.weight = 2


class Mbira(OffHand):

    def __init__(self):
        super().__init__(name="Mbira", description="",
                         value=8000, rarity=0.6, mod=25, subtyp="Musical Instrument", unequip=False)
        self.weight = 1

class Lyre(OffHand):

    def __init__(self):
        super().__init__(name="Lyre", description="",
                         value=16000, rarity=0.5, mod=30, subtyp="Musical Instrument", unequip=False)
        self.weight = 3


class Tambourine(OffHand):

    def __init__(self):
        super().__init__(name="Tambourine", description="",
                         value=55000, rarity=0.4, mod=50, subtyp="Musical Instrument", unequip=False)
        self.weight = 1


class Accordina(OffHand):

    def __init__(self):
        super().__init__(name="Accordina", description="",
                         value=70000, rarity=0.3, mod=75, subtyp="Musical Instrument", unequip=False)
        self.weight = 5


class Didgeridoo(OffHand):

    def __init__(self):
        super().__init__(name="Didgeridoo", description="",
                         value=90000, rarity=0.2, mod=100, subtyp="Musical Instrument", unequip=False)
        self.weight = 4


class Sitar(OffHand):

    def __init__(self):
        super().__init__(name="Sitar", description="",
                         value=125000, rarity=0.1, mod=130, subtyp="Musical Instrument", unequip=False)
        self.weight = 4


class Bagpipes(OffHand):

    def __init__(self):
        super().__init__(name="Bagpipes", description="",
                         value=200000, rarity=0.05, mod=150, subtyp="Musical Instrument", unequip=False)
        self.weight = 7


class Shamisen(OffHand):

    def __init__(self):
        super().__init__(name="Shamisen", description="",
                         value=300000, rarity=0.01, mod=200, subtyp="Musical Instrument", unequip=False)
        self.weight = 6


class GrandPiano(OffHand):
    """
    TODO: remove this once implemented
    Not a lootable/equipable item; must be found and played in Cambion Realm to make Ultimate Score
    """

    def __init__(self):
        super().__init__(name="GrandPiano", description="",
                         value=0, rarity=0, mod=0, subtyp="Musical Instrument", unequip=False)
        self.weight = 40


class Crossbow(OffHand):
    """Base class for off-hand crossbows fueled by bolt packs."""

    shots_per_attack = 1

    def __init__(self, name, description, value, rarity, damage, weight):
        super().__init__(
            name=name,
            description=description,
            value=value,
            rarity=rarity,
            mod=damage,
            subtyp="Crossbow",
            unequip=False,
        )
        self.damage = damage
        self.weight = weight


class HandCrossbow(Crossbow):
    """Compact entry-level crossbow."""

    def __init__(self):
        super().__init__("Hand Crossbow", "A compact off-hand crossbow.", 4000, 0.75, 12, 3)


class LightCrossbow(Crossbow):
    """Lightweight crossbow with moderate damage."""

    def __init__(self):
        super().__init__(
            "Light Crossbow", "A light, dependable off-hand crossbow.",
            6000, 0.6, 16, 5,
        )


class HeavyCrossbow(Crossbow):
    """Heavy crossbow with substantial stopping power."""

    def __init__(self):
        super().__init__(
            "Heavy Crossbow", "A weighty crossbow with substantial force.",
            12000, 0.5, 20, 12,
        )


class PistolCrossbow(Crossbow):
    """Compact high-damage crossbow."""

    def __init__(self):
        super().__init__(
            "Pistol Crossbow", "A powerful crossbow in a compact frame.",
            48000, 0.4, 24, 6,
        )


class RepeatingCrossbow(Crossbow):
    """Crossbow that fires two bolts after each basic attack."""

    shots_per_attack = 2

    def __init__(self):
        super().__init__(
            "Repeating Crossbow",
            "Its magazine can fire two bolts after each basic attack.",
            65000,
            0.3,
            30,
            10,
        )


class MagicCrossbow(Crossbow):
    """Crossbow that unlocks the Arcane payload of Magic Bolts."""

    def __init__(self):
        super().__init__(
            "Magic Crossbow",
            "Magic Bolts fired from this crossbow also deal Arcane damage.",
            80000,
            0.2,
            35,
            4,
        )


class GoldenClaw(Crossbow):
    """Rare saintly crossbow with exceptional damage."""

    def __init__(self):
        super().__init__(
            "Golden Claw",
            "The Saintly Crossbow of the Supernaturally Luminous Golden Claw.",
            150000,
            0.01,
            45,
            8,
        )
