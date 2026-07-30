"""Ring and pendant implementations."""

from __future__ import annotations

from .base import Accessory


class NoRing(Accessory):

    def __init__(self):
        super().__init__(name="No Ring", description="No ring equipped.", value=0, rarity=0, mod="No Mod",
                         subtyp='None', unequip=True)


class IronRing(Accessory):

    def __init__(self):
        super().__init__(name="Iron Ring", description="A ring that improves the wearer's defense.",
                         value=2000, rarity=0.85, mod="+4 Physical Defense", subtyp="Ring", unequip=False)
        self.weight = 0.1


class PowerRing(Accessory):

    def __init__(self):
        super().__init__(name="Power Ring", description="A ring that improves the wearer's attack damage.",
                         value=5000, rarity=0.75, mod="+10 Physical Damage", subtyp="Ring", unequip=False)
        self.weight = 0.1


class BarrierRing(Accessory):
    """
    Increases block chance by 25%, even without a shield
    """

    def __init__(self):
        super().__init__(name="Barrier Ring", description="A ring that increases the wearer's chance to block attacks "
                                                          "by 25%, even without having a shield equipped.",
                         value=16000, rarity=0.5, mod="Block", subtyp="Ring", unequip=False)
        self.weight = 0.1


class SteelRing(Accessory):

    def __init__(self):
        super().__init__(name="Steel Ring", description="A ring that greatly improves the wearer's defense.",
                         value=20000, rarity=0.4, mod="+10 Physical Defense", subtyp="Ring", unequip=False)
        self.weight = 0.1


class MightRing(Accessory):

    def __init__(self):
        super().__init__(name="Might Ring", description="A ring that greatly improves the wearer's attack damage.",
                         value=24000, rarity=0.4, mod="+20 Physical Damage", subtyp="Ring", unequip=False)
        self.weight = 0.1


class AccuracyRing(Accessory):

    def __init__(self):
        super().__init__(name="Accuracy Ring", description="A ring that improves the wearer's weapon accuracy by 10%.",
                         value=25000, rarity=0.4, mod="Accuracy", subtyp="Ring", unequip=False)
        self.weight = 0.1


class EvasionRing(Accessory):
    """
    Increases chance to dodge
    """

    def __init__(self):
        super().__init__(name="Evasion Ring", description="A ring that improves the wearer's chance to dodge.",
                         value=40000, rarity=0.2, mod="Dodge", subtyp="Ring", unequip=False)
        self.weight = 0.1


class TitaniumRing(Accessory):

    def __init__(self):
        super().__init__(name="Titanium Ring", description="A ring that massively improves the wearer's defense.",
                         value=45000, rarity=0.2, mod="+20 Physical Defense", subtyp="Ring", unequip=False)
        self.weight = 0.1


class ForceRing(Accessory):

    def __init__(self):
        super().__init__(name="Force Ring", description="A ring that massively improves the wearer's attack damage.",
                         value=50000, rarity=0.1, mod="+50 Physical Damage", subtyp="Ring", unequip=False)
        self.weight = 0.1


class ClassRing(Accessory):

    def __init__(self):
        super().__init__(name="Class Ring", description="A ring that changes depending on the wearer's specialty.",
                         value=0, rarity=0, mod="Special", subtyp="Ring", unequip=False)
        self.weight = 0.1

    def get_description(self, player_char=None):
        """Get dynamic description based on player's class."""
        if player_char is None:
            return self.description

        cls_name = player_char.cls.name
        from ..classes import class_rings
        if class_rings.is_legacy_class(cls_name):
            return class_rings.description(player_char)

        descriptions = {
            "Berserker": "A ring that grants +15% Critical Hit Chance when worn by a Berserker.",
            "Weapon Master": self._grandmaster_description(player_char),
            "Grandmaster of Arms": self._grandmaster_description(player_char),
            "Crusader": "A ring that grants +10% Holy damage when worn by a Crusader.",
            "Dragoon": "A ring that unlocks an additional Jump modification slot (max 6) when worn by a Dragoon.",
            "Stalwart Defender": "A ring that reduces damage taken by 10% when worn by a Stalwart Defender.",
            "Wizard": "A ring that increases the chance to trigger Arcane and elemental spell special effects when worn by a Wizard.",
            "Shadowcaster": "A ring that grants Shadow Bolt a special effect that heals the caster based on damage dealt when worn by a Shadowcaster.",
            "Demonologist": self._demonologist_description(player_char),
            "Knight Enchanter": "A ring that increases Mana Tap effectiveness (turns 10% mana into 20% heal) when worn by a Knight Enchanter.",
            "Grand Summoner": "A ring that increases HP and damage of summoned creatures by 30% when worn by a Grand Summoner.",
            "Rogue": "A ring that grants +2 Luck bonus when worn by a Rogue.",
            "Seeker": "A ring that grants a chance to find rare items based on dungeon level when worn by a Seeker.",
            "Ninja": "A ring that grants first round standard attack double damage if you have initiative when worn by a Ninja.",
            "Arcane Trickster": "A ring that grants a buff increasing Magic damage and dodge chance when a spell is stolen, when worn by an Arcane Trickster.",
            "Templar": "A ring that provides random blessings in combat (health/mana regen, attack/defense boost) when worn by a Templar.",
            "Hierophant": "A ring that preserves Devotion after a clean Consecrated Conduit payoff and improves staff-conduit holy damage when worn by a Hierophant.",
            "Master Monk": "A ring that increases damage and armor by 50% when unarmed and not wearing armor when worn by a Master Monk.",
            "Archbishop": "A ring that grants a random chance to heal 25% of health when below 50% health when worn by an Archbishop.",
            "Troubadour": "A ring that doubles the intelligence bonus to all songs when worn by a Troubadour.",
            "Lycan": "A ring that grants an attack bonus immediately after transforming when worn by a Lycan.",
            "Archdruid": self._archdruid_description(player_char),
            "Astromancer": "A ring that strengthens active-sign fate and rune boosts when worn by an Astromancer.",
            "Soulcatcher": "A ring that unlocks the Soul Aspect of the Totem ability when worn by a Soulcatcher, granting +20% Weapon damage and +20% Critical damage.",
            "Beast Master": "A ring that increases defense for you and your companion when covering the other when worn by a Beast Master.",
        }
        return descriptions.get(cls_name, self.description)

    def _grandmaster_description(self, player_char):
        from ..classes import grandmaster
        from ..classes import class_rings

        state = grandmaster.normalize_state(getattr(player_char, "grandmaster_discipline", None))
        if getattr(getattr(player_char, "cls", None), "name", None) == "Weapon Master":
            ranks = [
                f"{weapon_type} {grandmaster.discipline_rank(player_char, weapon_type)}"
                for weapon_type in grandmaster.WEAPON_TYPES
                if grandmaster.discipline_rank(player_char, weapon_type)
            ]
            progress = ", ".join(ranks) if ranks else "no ranked disciplines yet"
            return (
                f"A dormant Class Ring for a Weapon Master. {class_rings.presentation_summary(player_char, awakened=False)} "
                "Awakened effect: Grandmaster binding is not available until Grandmaster of Arms. "
                f"Current ranks: {progress}."
            )
        if not state["activated"]:
            return (
                f"A dormant Class Ring for a Grandmaster of Arms. {class_rings.presentation_summary(player_char, awakened=False)} "
                "Activation: Secret Master trial. Awakened effect: bind one weapon discipline. "
                f"{class_rings.active_effect_summary(player_char, awakened=False)}"
            )
        bound_weapon = state["bound_weapon"] or "chosen weapon"
        rank = grandmaster.discipline_rank(player_char, bound_weapon)
        chance = int(grandmaster.proc_chance(player_char, bound_weapon) * 100)
        accuracy = int(grandmaster.accuracy_bonus(player_char, bound_weapon) * 100)
        return (
            f"An awakened Class Ring for a Grandmaster of Arms. {class_rings.presentation_summary(player_char, awakened=True)} "
            f"bound to {bound_weapon} Discipline. Bound weapon: {bound_weapon}. "
            "Awakened effect: doubles that discipline's mastery bonus "
            f"while equipped (rank {rank}, +{accuracy}% accuracy, {chance}% technique chance) "
            f"and perfects that weapon's active art. {class_rings.active_effect_summary(player_char, awakened=True)}"
        )

    def _demonologist_description(self, player_char):
        from ..classes import demonologist
        from ..classes import class_rings

        state = demonologist.normalize_state(getattr(player_char, "demonologist_contracts", None))
        active = state["active_patron"] or "no active patron"
        if not state["ring_awakened"]:
            return (
                f"A dormant Class Ring for a Demonologist. {class_rings.presentation_summary(player_char, awakened=False)} "
                "Activation: hidden crypt familiar imprisonment. Basic contracts are available, "
                f"but empowered contracts are inactive. Active patron: {active}. "
                f"{class_rings.active_effect_summary(player_char, awakened=False)}"
            )
        familiar = state.get("imprisoned_familiar") or {}
        echo = familiar.get("race") or familiar.get("spec") or "familiar"
        return (
            f"An awakened Class Ring for a Demonologist. {class_rings.presentation_summary(player_char, awakened=True)} "
            f"Imprisoned echo: {echo}. Awakened effect: the ring has empowered fiend contracts. "
            f"Active patron: {active}."
        )

    def _archdruid_description(self, player_char):
        from ..classes import archdruid
        from ..classes import class_rings

        state = archdruid.normalize_state(getattr(player_char, "archdruid_attunement", None))
        attunement = ", ".join(
            f"{affinity} {state['attunement'][affinity]}"
            for affinity in archdruid.AFFINITIES
        )
        if not state["grove_unlocked"]:
            return (
                f"A dormant Class Ring for an Archdruid. {class_rings.presentation_summary(player_char, awakened=False)} "
                "Activation: Fourfold Balance and Ancient Grove rituals. "
                f"Attunement: {attunement}."
            )
        if not state["ring_awakened"]:
            aspects = archdruid.aspect_summary(player_char)
            return (
                f"A dormant Class Ring for an Archdruid. {class_rings.presentation_summary(player_char, awakened=False)} "
                "Activation: complete all four Grove aspects. "
                f"Aspects: {aspects}. {class_rings.active_effect_summary(player_char, awakened=False)}"
            )
        bonus = int(archdruid.harmony_bonus(player_char) * 100)
        total_attunement = sum(int(state["attunement"][affinity]) for affinity in archdruid.AFFINITIES)
        potential = (total_attunement // 25) * 0.01
        if all(int(state["attunement"][affinity]) >= 75 for affinity in archdruid.AFFINITIES):
            potential *= 2
        potential_bonus = int(min(0.40, potential) * 100)
        return (
            f"An awakened Class Ring for an Archdruid. {class_rings.presentation_summary(player_char, awakened=True)} "
            "Awakened through Venom, Stone, Growth, and Storm. "
            f"Current Harmony Bonus: +{bonus}%. Potential while equipped: +{potential_bonus}%. "
            f"{class_rings.active_effect_summary(player_char, awakened=True)}"
        )

    def class_mod(self, player_char):
        """Apply class-specific bonuses to the wearer."""
        cls_name = player_char.cls.name

        from ..classes import class_rings
        if class_rings.is_legacy_class(cls_name):
            player_char.equipment["Ring"].mod = class_rings.ring_mod(player_char)
            if cls_name == "Soulcatcher" and class_rings.is_awakened(player_char, "Soulcatcher"):
                try:
                    totem = player_char.spellbook.get("Skills", {}).get("Totem")
                    if totem is None:
                        totem = player_char.spellbook.get("Totem")
                    if totem is not None:
                        totem.unlocked_aspects["Soul"] = True
                except (AttributeError, KeyError):
                    pass
            return

        # Warrior Branch
        if cls_name == "Berserker":
            # +15% Critical Hit Chance
            if "Crit" not in player_char.equipment["Ring"].mod:
                player_char.equipment["Ring"].mod = "+15% Crit"

        elif cls_name in {"Weapon Master", "Grandmaster of Arms"}:
            from ..classes import grandmaster

            state = grandmaster.normalize_state(getattr(player_char, "grandmaster_discipline", None))
            bound_weapon = state["bound_weapon"]
            if cls_name == "Grandmaster of Arms" and state["activated"] and bound_weapon:
                player_char.equipment["Ring"].mod = f"{bound_weapon} Discipline x2"
            else:
                player_char.equipment["Ring"].mod = "Weapon Discipline"

        elif cls_name == "Crusader":
            # +10% Holy damage
            player_char.equipment["Ring"].mod = "+10% Holy Damage"

        elif cls_name == "Dragoon":
            # Unlock additional Jump modification slot (max 6)
            player_char.equipment["Ring"].mod = "+1 Jump Mod"

        elif cls_name == "Stalwart Defender":
            # Reduce damage taken by 10%
            player_char.equipment["Ring"].mod = "Damage Reduction"

        # Mage Branch
        elif cls_name == "Wizard":
            # Increased chance to trigger Arcane and elemental spell special effects
            player_char.equipment["Ring"].mod = "Spell Effect"

        elif cls_name == "Shadowcaster":
            # Shadow Bolt gains special effect that heals based on damage
            player_char.equipment["Ring"].mod = "Shadow Bolt Heal"

        elif cls_name == "Demonologist":
            from ..classes import demonologist

            state = demonologist.normalize_state(getattr(player_char, "demonologist_contracts", None))
            if state["ring_awakened"]:
                player_char.equipment["Ring"].mod = "Empowered Contracts"
            else:
                player_char.equipment["Ring"].mod = "Dormant Contract"

        elif cls_name == "Knight Enchanter":
            # Increase effectiveness of Mana Tap (10% mana → 20% heal)
            player_char.equipment["Ring"].mod = "Mana Tap+"

        elif cls_name == "Grand Summoner":
            # Increase HP and damage of summoned creatures by 30%
            player_char.equipment["Ring"].mod = "+30% Summons"

        # Footpad Branch
        elif cls_name == "Rogue":
            # +2 luck bonus
            player_char.stats.charisma += 2
            player_char.equipment["Ring"].mod = "+2 Luck"

        elif cls_name == "Seeker":
            # Chance to find rare items based on dungeon level
            player_char.equipment["Ring"].mod = "Rare Find"

        elif cls_name == "Ninja":
            # First round standard attack deals double damage if player has initiative
            player_char.equipment["Ring"].mod = "First Strike"

        elif cls_name == "Arcane Trickster":
            # Gain buff when spell is stolen (Magic damage + dodge)
            player_char.equipment["Ring"].mod = "Spell Steal Buff"

        # Healer Branch
        elif cls_name == "Templar":
            # Provides random blessing in combat
            player_char.equipment["Ring"].mod = "Random Blessing"

        elif cls_name == "Master Monk":
            # Damage and armor increased by 50% when unarmed and not wearing armor
            player_char.equipment["Ring"].mod = "Martial Master"

        elif cls_name == "Archbishop":
            # Random chance to heal 25% of health when below 50% health
            player_char.equipment["Ring"].mod = "Divine Intervention"

        elif cls_name == "Troubadour":
            # Double the intelligence bonus to all songs
            player_char.equipment["Ring"].mod = "Amplified Song"

        # Pathfinder Branch
        elif cls_name == "Lycan":
            # Gain attack bonus immediately after transforming
            player_char.equipment["Ring"].mod = "Transform Boost"

        elif cls_name == "Archdruid":
            from ..classes import archdruid

            state = archdruid.normalize_state(getattr(player_char, "archdruid_attunement", None))
            if state["ring_awakened"]:
                bonus = int(archdruid.harmony_bonus(player_char) * 100)
                player_char.equipment["Ring"].mod = f"Harmony +{bonus}%"
            elif state["grove_unlocked"]:
                player_char.equipment["Ring"].mod = "Grove Dormant"
            else:
                player_char.equipment["Ring"].mod = "Dormant Balance"

        elif cls_name == "Astromancer":
            # Boost terrain effect of spells
            player_char.equipment["Ring"].mod = "Terrain Master"

        elif cls_name == "Soulcatcher":
            # Unlock Soul Aspect of Totem ability
            try:
                if "Totem" in player_char.spellbook:
                    totem = player_char.spellbook["Totem"]
                    totem.unlocked_aspects["Soul"] = True
                player_char.equipment["Ring"].mod = "Soul Aspect Unlock"
            except (AttributeError, KeyError):
                player_char.equipment["Ring"].mod = "Soul Aspect Unlock"

        elif cls_name == "Beast Master":
            # Increased defense for wearer and companion when covering the other
            player_char.equipment["Ring"].mod = "Pack Bond"


class NoPendant(Accessory):

    def __init__(self):
        super().__init__(name="No Pendant", description="No pendant equipped.", value=0, rarity=0, mod="No Mod",
                         subtyp="None", unequip=True)


class VisionPendant(Accessory):

    def __init__(self):
        super().__init__(name="Pendant of Vision", description="A pendant that that gives information about the enemy.",
                         value=1200, rarity=0.9, mod="Vision", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class RubyLocket(Accessory):

    def __init__(self):
        super().__init__(name="Ruby Locket", description="A ruby necklace that improves the wearer's magic defense.",
                         value=1800, rarity=0.85, mod="+10 Magic Defense", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class SilverNecklace(Accessory):

    def __init__(self):
        super().__init__(name="Silver Necklace", description="A silver-chained necklace that improves the wearer's "
                                                             "magic damage.",
                         value=8000, rarity=0.75, mod="+10 Magic Damage", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class AntidotePendant(Accessory):

    def __init__(self):
        super().__init__(name="Antidote Pendant", description="Protects the wearer against the effects of poison.",
                         value=2500, rarity=0.85, mod="Status-Poison", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class CalmingPendant(Accessory):

    def __init__(self):
        super().__init__(name="Calming Pendant", description="Protects the wearer against the effects of berserk.",
                         value=5000, rarity=0.7, mod="Status-Berserk", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class ElementChain(Accessory):

    def __init__(self):
        super().__init__(name="Element Chain", description="Base class for the various element chains, each forged "
                                                           "around a focused elemental core.",
                         value=8000, rarity=0.6, mod="None", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class FireChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Fire Chain"
        self.description = ("A necklace set with a warm ember-stone that glows brighter near open flame.")
        self.mod = "Resist-Fire"


class IceChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Ice Chain"
        self.description = ("A necklace of pale crystal links that stay cold even in midsummer heat.")
        self.mod = "Resist-Ice"


class ElectricChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Electric Chain"
        self.description = ("A necklace strung with storm glass that hums softly before lightning strikes.")
        self.mod = "Resist-Electric"


class WaterChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Water Chain"
        self.description = ("A necklace of blue-green links that beads with dew in dry air.")
        self.mod = "Resist-Water"


class EarthChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Earth Chain"
        self.description = ("A necklace carved from polished stone, heavy with the patience of deep caverns.")
        self.mod = "Resist-Earth"


class WindChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Wind Chain"
        self.description = ("A necklace of feather-light silver links that stir when no breeze is present.")
        self.mod = "Resist-Wind"


class ElementalChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Elemental Chain"
        self.description = ("Fashioned from the cores of elementals, this necklace shifts color as nearby magic "
                            "changes shape.")
        self.value = 15000
        self.rarity = 0.4
        self.mod = "Resist-Elemental"


class SapphireLocket(Accessory):

    def __init__(self):
        super().__init__(name="Sapphire Locket", description="A sapphire necklace that greatly improves the wearer's "
                                                             "magic defense.",
                         value=16000, rarity=0.5, mod="+20 Magic Defense", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class GoldNecklace(Accessory):

    def __init__(self):
        super().__init__(name="Gold Necklace", description="A gold-chained necklace that greatly improves the "
                                                           "wearer's magic damage.",
                         value=22000, rarity=0.4, mod="+20 Magic Damage", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class GorgonPendant(Accessory):

    def __init__(self):
        super().__init__(name="Gorgon Pendant", description="Made from the scale of a Gorgon, this ring protects the "
                                                            "wearer against petrification.",
                         value=20000, rarity=0.4, mod="Status-Stone", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class GarfunkelPendant(Accessory):

    def __init__(self):
        super().__init__(name="Garfunkel Pendant", description="The Sound of Silence can be deafening but not with "
                                                              "this necklace.",
                         value=23000, rarity=0.3, mod="Status-Silence", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class DharmaPendant(Accessory):

    def __init__(self):
        super().__init__(name="Dharma Pendant", description="No need to fear the reaper while wearing this amulet, "
                                                            "giving the wearer immunity against instant death.",
                         value=25000, rarity=0.25, mod="Status-Death", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class DraconitePendant(Accessory):
    """Kaelenon's crafted pendant. Strengthens Jump Recover restoration."""

    def __init__(self):
        super().__init__(
            name="Draconite Pendant",
            description="A pendant cut from Kaelenon's Draconite. It strengthens the Recover Jump modification, "
                        "restoring more health and mana when the wearer lands.",
            value=0,
            rarity=0,
            mod="Jump Recover+",
            subtyp="Pendant",
            unequip=False,
        )
        self.weight = 0.1


class LevitationPendant(Accessory):

    def __init__(self):
        super().__init__(name="Levitation Pendant", description="Gives the wearer the ability to fly, making them "
                                                                 "harder to hit and immune to ground-based spells. "
                                                                 "The downfall is that Wind spells will hurt more.",
                         value=30000, rarity=0.25, mod="Flying", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class ElementAmulet(Accessory):

    def __init__(self):
        super().__init__(name="Element Amulet", description="Base class for the various element amulets, each shaped "
                                                           "around a concentrated warding jewel.",
                         value=40000, rarity=0.2, mod="None", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class FireAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Fire Amulet"
        self.description = ("An amulet with a ruby heart that burns like a banked coal.")
        self.mod = "Immune-Fire"


class IceAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Ice Amulet"
        self.description = ("An amulet with a frost-white gem that leaves a chill on the skin.")
        self.mod = "Immune-Ice"


class ElectricAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Electric Amulet"
        self.description = ("An amulet with a storm-bright gem that clicks with tiny sparks.")
        self.mod = "Immune-Electric"


class WaterAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Water Amulet"
        self.description = ("An amulet with a deep blue gem that seems to ripple beneath its surface.")
        self.mod = "Immune-Water"


class EarthAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Earth Amulet"
        self.description = ("An amulet with a dense green gem veined like ancient bedrock.")
        self.mod = "Immune-Earth"


class WindAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Wind Amulet"
        self.description = ("An amulet with a clear gem that feels almost weightless in the hand.")
        self.mod = "Immune-Wind"


class ElementalAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Elemental Amulet"
        self.description = ("Legend claims the jewel of this amulet is actually the heart of a god, still turning "
                            "with every color of creation.")
        self.value = 100000
        self.rarity = 0.05
        self.mod = "Immune-Elemental"


class InvisibilityPendant(Accessory):

    def __init__(self):
        super().__init__(name="Invisibility Pendant", description="Makes the wearer invisible and harder to hit.",
                         value=50000, rarity=0.1, mod="Invisible", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class DiamondLocket(Accessory):

    def __init__(self):
        super().__init__(name="Diamond Locket", description="A diamond necklace that massively improves the wearer's "
                                                            "magic damage.",
                         value=55000, rarity=0.1, mod="+50 Magic Defense", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class PlatinumNecklace(Accessory):

    def __init__(self):
        super().__init__(name="Platinum Necklace", description="A platinum-chained necklace that massively improves "
                                                               "the wearer's magic damage.",
                         value=60000, rarity=0.1, mod="+50 Magic Damage", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class RibbonPendant(Accessory):
    """
    Provides immunity to the following status effects: "Berserk", "Blind", "Doom", "Poison", "Silence", "Sleep", "Stun"
    """

    def __init__(self):
        super().__init__(name="Ribbon Pendant", description="Forged from a rare mineral, this pendant provides the "
                                                            "wearer with immunity from all negative status effects.",
                         value=150000, rarity=0.01, mod="Status-All", subtyp="Pendant", unequip=False)


class MagicPendant(Accessory):
    """
    Increases chance to dodge spells by 25%.
    """

    def __init__(self):
        super().__init__(name="Magic Pendant", description="An amulet that makes the wearer harder to hit with magic spells.",
                         value=150000, rarity=0.01, mod="Magic Dodge", subtyp="Pendant", unequip=False)
        self.weight = 0.2
