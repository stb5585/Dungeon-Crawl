"""Core weapon, defensive, class, and composition skills."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from .base import (
    Class,
    Defensive,
    MartialArts,
    Offensive,
    _load_yaml_ability,
)

if TYPE_CHECKING:
    from typing import Any

    from ..character import Character


# Skills #
# Offensive
class ShieldSlam:
    """Data-driven (shield_slam.yaml) - str+shield damage + stun."""
    def __new__(cls):
        return _load_yaml_ability("shield_slam.yaml", cls_name="ShieldSlam")


class DoubleStrike:
    """Data-driven (double_strike.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("double_strike.yaml", cls_name="DoubleStrike")


class TripleStrike:
    """Data-driven (triple_strike.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("triple_strike.yaml", cls_name="TripleStrike")


class FlurryBlades:
    """Data-driven (flurry_blades.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("flurry_blades.yaml", cls_name="FlurryBlades")


class PiercingStrike:
    """Data-driven (piercing_strike.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("piercing_strike.yaml", cls_name="PiercingStrike")


class TrueStrike:
    """Data-driven (true_strike.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("true_strike.yaml", cls_name="TrueStrike")


class TruePiercingStrike:
    """Data-driven (true_piercing_strike.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("true_piercing_strike.yaml", cls_name="TruePiercingStrike")


class Jump:
    """Data-driven (jump.yaml) - leap attack with full modification system."""
    def __new__(cls):
        return _load_yaml_ability("jump.yaml", cls_name="Jump")


class Doublecast:
    """Data-driven (doublecast.yaml) - cast 2 spells in a single turn."""
    def __new__(cls):
        return _load_yaml_ability("doublecast.yaml", cls_name="Doublecast")


class Triplecast:
    """Data-driven (triplecast.yaml) - cast 3 spells in a single turn."""
    def __new__(cls):
        return _load_yaml_ability("triplecast.yaml", cls_name="Triplecast")


class MortalStrike:
    """Data-driven (mortal_strike.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("mortal_strike.yaml", cls_name="MortalStrike")


class MortalStrike2:
    """Data-driven (mortal_strike_2.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("mortal_strike_2.yaml", cls_name="MortalStrike2")


class BattleCry:
    """Data-driven (battle_cry.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("battle_cry.yaml", cls_name="BattleCry")


class Charge(Offensive):
    """Data-driven (charge.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("charge.yaml", cls_name="Charge")


class _PassiveSkill(Class):
    def __init__(self, name: str, description: str) -> None:
        super().__init__(name=name, description=description)
        self.passive = True
        self.cost = 0


class MonkeyGrip(_PassiveSkill):
    def __init__(self):
        super().__init__(
            "Monkey Grip",
            "Your two-handed dual wielding becomes steadier, reducing its accuracy and damage penalties.",
        )


class MonkeyGrip2(_PassiveSkill):
    def __init__(self):
        super().__init__(
            "Monkey Grip 2",
            "Your two-handed dual wielding is fully stabilized, removing its accuracy and damage penalties.",
        )


class PolearmProficiency(_PassiveSkill):
    def __init__(self):
        super().__init__(
            "Polearm Proficiency",
            "You can wield a two-handed polearm with a shield, but your accuracy and damage suffer.",
        )


class PolearmExcellence(_PassiveSkill):
    def __init__(self):
        super().__init__(
            "Polearm Excellence",
            "You can wield a two-handed polearm with a shield without accuracy or damage penalties.",
        )


class PolearmMastery(_PassiveSkill):
    def __init__(self):
        super().__init__(
            "Polearm Mastery",
            "Your one-handed polearm technique grants bonus accuracy and damage.",
        )


class _WeaponArt(Class):
    def __init__(self, name: str, weapon_type: str, description: str):
        super().__init__(name=name, description=f"Requires: {weapon_type}. {description}")
        self.cost = {
            "Iron Palm": 6,
            "Hemorrhage": 7,
            "Riposte Line": 7,
            "Low Sweep": 7,
            "Guard Cleaver": 9,
            "Reaver's Mark": 9,
            "Brace": 8,
            "Anvil Strike": 10,
        }.get(name, 0)
        self.weapon = True
        self.required_weapon_type = weapon_type

    def use(
        self,
        user: Character,
        target: Character | None = None,
        **kwargs: Any,
    ) -> str:
        from ..classes import grandmaster

        super().use(user, target, **kwargs)
        if target is None:
            return f"{self.name} needs a target.\n"
        return grandmaster.perform_weapon_art(user, target, self.name)


class IronPalm(_WeaponArt):
    def __init__(self):
        super().__init__(
            "Iron Palm",
            "Fist",
            "A fist discipline art that disrupts the target's attack and hardens your stance as mastery grows.",
        )


class Hemorrhage(_WeaponArt):
    def __init__(self):
        super().__init__(
            "Hemorrhage",
            "Dagger",
            "A dagger discipline art that opens and worsens bleeding wounds.",
        )


class RiposteLine(_WeaponArt):
    def __init__(self):
        super().__init__(
            "Riposte Line",
            "Sword",
            "A sword discipline art that strikes and prepares a brief counter line.",
        )


class LowSweep(_WeaponArt):
    def __init__(self):
        super().__init__(
            "Low Sweep",
            "Club",
            "A club discipline art that disrupts footing with speed pressure and prone chances.",
        )


class GuardCleaver(_WeaponArt):
    def __init__(self):
        super().__init__(
            "Guard Cleaver",
            "Longsword",
            "A longsword discipline art that cuts through and weakens guard.",
        )


class ReaversMark(_WeaponArt):
    def __init__(self):
        super().__init__(
            "Reaver's Mark",
            "Battle Axe",
            "A battle axe discipline art that marks a foe to take increased weapon pressure.",
        )


class Brace(_WeaponArt):
    def __init__(self):
        super().__init__(
            "Brace",
            "Polearm",
            "A polearm discipline art that prepares a defensive counter stance.",
        )


class AnvilStrike(_WeaponArt):
    def __init__(self):
        super().__init__(
            "Anvil Strike",
            "Hammer",
            "A hammer discipline art that crushes defense and can suppress guard at mastery.",
        )


class FavoredEnemy(Class):
    def __init__(self):
        super().__init__(
            "Favored Enemy",
            "Mark the current enemy type as your quarry. Keeping the same mark "
            "builds tracking mastery; changing quarry carries over only some practice.",
        )
        self.cost = 0

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import ability_mechanics

        super().use(user, target, **kwargs)
        user.mana.current -= self.cost
        return ability_mechanics.mark_favored_enemy(user, target)


class FinalAssault(_PassiveSkill):
    def __init__(self):
        super().__init__(
            "Final Assault",
            "When a melee blow would kill you, counterattack; if the attacker falls, stabilize at 1 HP.",
        )


class LastStand(_PassiveSkill):
    def __init__(self):
        super().__init__(
            "Last Stand",
            "Increase defense and block strength at the expense of attack power.",
        )


class _MartialStrike(MartialArts):
    status_name: str | None = None
    damage_mod: float = 1.0

    def __init__(self, name: str, description: str, cost: int = 8):
        super().__init__(name=name, description=description, weapon=True)
        self.cost = cost

    def _has_martial_weapon(self, user: Character) -> bool:
        return any(
            getattr(user.equipment.get(slot), "subtyp", None) in {"Fist", "None"}
            for slot in ("Weapon", "OffHand")
        )

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        super().use(user, target, **kwargs)
        if target is None:
            return "There is no target.\n"
        if not self._has_martial_weapon(user):
            return f"{user.name} needs a free hand or fist weapon to use {self.name}.\n"
        user.mana.current -= self.cost
        msg, hit, _crit = user.weapon_damage(target, dmg_mod=self.damage_mod, use_offhand=False)
        if hit and self.status_name and target.is_alive() and not target.has_status_protection(self.status_name):
            effect_dict = target.effect_handler(self.status_name)
            effect_dict[self.status_name].active = True
            effect_dict[self.status_name].duration = max(effect_dict[self.status_name].duration, 2)
            msg += f"{target.name} is affected by {self.status_name.lower()}.\n"
        return msg


class Uppercut(_MartialStrike):
    damage_mod = 1.25
    def __init__(self): super().__init__("Uppercut", "A rising martial strike that deals increased damage.", 8)


class Headbutt(_MartialStrike):
    status_name = "Stun"
    damage_mod = 1.0
    def __init__(self): super().__init__("Headbutt", "A close strike that can stun.", 6)


class DrunkenBrawler(_PassiveSkill):
    def __init__(self):
        super().__init__(
            "Drunken Brawler",
            "After using a potion, your next turn gains bonus damage and critical chance.",
        )


class Hyakuretsukyaku(_MartialStrike):
    def __init__(self): super().__init__("Hyakuretsukyaku", "A rushing flurry of kicks.", 14)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        MartialArts.use(self, user, target, **kwargs)
        if target is None:
            return "There is no target.\n"
        if not self._has_martial_weapon(user):
            return f"{user.name} needs a free hand or fist weapon to use {self.name}.\n"
        user.mana.current -= self.cost
        msg = ""
        for _ in range(4):
            hit_msg, _hit, _crit = user.weapon_damage(target, dmg_mod=0.45, use_offhand=False)
            msg += hit_msg
            if not target.is_alive():
                break
        return msg


class SpinningBackElbow(_MartialStrike):
    status_name = "Blind"
    damage_mod = 1.2
    def __init__(self): super().__init__("Spinning Back Elbow", "A turning blow that can blind.", 10)


class Suplex(_MartialStrike):
    status_name = "Prone"
    damage_mod = 1.35
    def __init__(self): super().__init__("Suplex", "A crushing throw that can knock the target prone.", 12)


class Hadouken(_MartialStrike):
    damage_mod = 1.4
    def __init__(self): super().__init__("Hadouken", "A focused chi strike delivered at range.", 16)


# Defensive skills
class ShieldBlock(Defensive):
    """
    Passive ability; increases damage blocked by 25% when using a shield
    """

    def __init__(self):
        super().__init__(
            name="Shield Block",
            description="You are much more proficient with a shield than most, "
            "increasing the amount of damage blocked by 25% when using "
            "a shield.",
        )
        self.passive = True


class StealSpell(Class):
    """Steal an enemy spell onto a Blank Scroll."""

    def __init__(self):
        super().__init__(
            name="Steal Spell",
            description="Inscribes one of the target's spells onto a Blank Scroll.",
        )
        self.cost = 8

    def use(
        self,
        user: Character,
        target: Character | None = None,
        **kwargs: Any,
    ) -> str:
        from ..classes import spell_stealer

        if target is None:
            return "There is no spell to steal.\n"
        _success, message = spell_stealer.steal_spell(user, target)
        if _success:
            from ..classes import promotion_kits

            message += promotion_kits.gain_stolen_charge(user, "Steal Spell")
        return message


class StealSpell2(Class):
    """Chance to permanently learn one stealable enemy spell."""

    def __init__(self):
        super().__init__(
            name="Steal Spell 2",
            description="Attempt to permanently learn one of the target's stealable spells.",
        )
        self.cost = 22

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import spell_stealer

        super().use(user, target, **kwargs)
        if target is None:
            return "There is no spell to steal.\n"
        spell_classes = spell_stealer.eligible_spell_classes(target)
        spell_classes = [
            spell_cls for spell_cls in spell_classes
            if spell_cls().name not in user.spellbook.get("Spells", {})
        ]
        if not spell_classes:
            return f"{target.name} has no new spell to learn.\n"
        user.mana.current -= self.cost
        chance = min(0.75, 0.20 + ((user.stats.intel + user.stats.dex) * 0.01))
        if random.random() > chance:
            return f"{user.name} fails to bind the stolen spell.\n"
        spell_cls = random.choice(spell_classes)
        spell = spell_cls()
        user.spellbook["Spells"][spell.name] = spell
        from ..classes import promotion_kits

        return (
            f"{user.name} permanently learns {spell.name}.\n"
            + promotion_kits.gain_stolen_charge(user, "Steal Spell 2")
        )


class StealAsWell(Class):
    """Marker skill used by the Steal As Well combat action."""

    def __init__(self):
        super().__init__(
            name="Steal As Well",
            description="Cast an attack spell and attempt to steal after it lands.",
        )
        self.cost = 0

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        return "Choose Steal As Well from the combat action menu to weave theft into a spell.\n"


class SongValor(Class):
    """Begin Song of Valor."""

    def __init__(self):
        super().__init__(
            name="Song of Valor",
            description="Perform a 3-turn song that raises weapon and magic damage.",
        )
        self.cost = 0

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import bard

        _success, message = bard.start_song(user, "Valor")
        return message


class SongShelter(Class):
    """Begin Song of Shelter."""

    def __init__(self):
        super().__init__(
            name="Song of Shelter",
            description="Perform a 3-turn song that reduces incoming damage.",
        )
        self.cost = 0

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import bard

        _success, message = bard.start_song(user, "Shelter")
        return message


class SongRenewal(Class):
    """Begin Song of Renewal."""

    def __init__(self):
        super().__init__(
            name="Song of Renewal",
            description="Perform a 3-turn song that restores HP and MP each turn.",
        )
        self.cost = 0

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import bard

        _success, message = bard.start_song(user, "Renewal")
        return message


class _ComposeSong(Class):
    sheet_cls_name = ""

    def __init__(self, name: str, sheet_cls_name: str):
        song_name = name.removeprefix("Compose ")
        super().__init__(
            name=name,
            description=f"Compose {song_name} into one-use sheet music from the character menu.",
        )
        self.cost = 0
        self.song_name = song_name
        self.sheet_cls_name = sheet_cls_name

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import bard

        _success, message = bard.compose_sheet_music(user, self.song_name)
        return message

    def use_out(self, game_or_user) -> str:
        user = getattr(game_or_user, "player_char", game_or_user)
        return self.use(user)


class ComposeBattleHymn(_ComposeSong):
    def __init__(self): super().__init__("Compose Battle Hymn", "BattleHymnSheet")


class ComposeOdeToTheRamparts(_ComposeSong):
    def __init__(self): super().__init__("Compose Ode to the Ramparts", "RampartsOdeSheet")


class ComposeSymphonyOfDisfunction(_ComposeSong):
    def __init__(self): super().__init__("Compose Symphony of Disfunction", "DysfunctionSymphonySheet")


class ComposeLowDefenseRhapsody(_ComposeSong):
    def __init__(self): super().__init__("Compose Low-defense-ian Rhapsody", "LowDefenseRhapsodySheet")


class ComposeSlowRide(_ComposeSong):
    def __init__(self): super().__init__("Compose Slow Ride", "SlowRideSheet")


class ComposeBonesThugsHarmony(_ComposeSong):
    def __init__(self): super().__init__("Compose Bones, Thugs, and Harmony", "BonesThugsHarmonySheet")


class ComposeScoresAndScoresScore(_ComposeSong):
    def __init__(self): super().__init__("Compose Scores and Scores Score", "ScoresAndScoresScoreSheet")


class ComposeGoldTrigger(_ComposeSong):
    def __init__(self): super().__init__("Compose Gold Trigger", "GoldTriggerSheet")


class ComposeChorusTime(_ComposeSong):
    def __init__(self): super().__init__("Compose Chorus Time", "ChorusTimeSheet")
