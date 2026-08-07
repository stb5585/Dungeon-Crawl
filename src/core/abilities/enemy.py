"""Enemy skills and companion ultimate attacks."""

from __future__ import annotations

from typing import Any

from .base import Skill, Spell, _load_yaml_ability


# Enemy skills
class RaiseUndeadAlly(Spell):
    """Raise a rewardless Ghoul reinforcement into a multi-enemy encounter."""

    def __init__(self) -> None:
        super().__init__(
            "Raise Dead",
            "Raise a Ghoul that fights beside the necromancer.",
            school="Shadow",
        )
        self.cost = 28
        self.subtyp = "Shadow"

    def cast(
        self,
        user: Any,
        target: Any | None = None,
        *,
        battle_engine: Any | None = None,
        **kwargs: Any,
    ) -> str:
        del target, kwargs
        if battle_engine is None:
            return "The grave answers, but no battle can hold the corpse.\n"
        from ..enemies.midgame import Ghoul

        ghoul = Ghoul()
        ghoul.name = "Raised Ghoul"
        ghoul.gold = 0
        ghoul.level.exp = 0
        ghoul.inventory = {}
        ghoul._raised_reinforcement = True
        if battle_engine.add_enemy_reinforcement(ghoul) is None:
            return "There is no room for another undead ally.\n"
        user.mana.current -= self.cost
        return "A Raised Ghoul claws its way into the battle.\n"


class Lick:
    """Data-driven (lick.yaml) - weapon hit + random status."""
    def __new__(cls):
        return _load_yaml_ability("lick.yaml", cls_name="Lick")


class AcidSpit:
    """Data-driven (acid_spit.yaml) - magic damage + DOT."""
    def __new__(cls):
        return _load_yaml_ability("acid_spit.yaml", cls_name="AcidSpit")


class Web:
    """Spider web that causes prone - data-driven (Batch 4)."""
    def __new__(cls):
        return _load_yaml_ability("web.yaml", cls_name="Web")


class Howl:
    """Wolf howl that stuns - data-driven (Batch 4)."""
    def __new__(cls):
        return _load_yaml_ability("howl.yaml", cls_name="Howl")


class Shapeshift:
    """Data-driven (shapeshift.yaml) - enemy transforms into random creature."""
    def __new__(cls):
        return _load_yaml_ability("shapeshift.yaml", cls_name="Shapeshift")


class Trip:
    """Trip the enemy prone - data-driven (Batch 4)."""
    def __new__(cls):
        return _load_yaml_ability("trip.yaml", cls_name="Trip")


class NightmareFuel:
    """Data-driven (nightmare_fuel.yaml) - sleep-conditional damage."""
    def __new__(cls):
        return _load_yaml_ability("nightmare_fuel.yaml", cls_name="NightmareFuel")


class WidowsWail:
    """Data-driven (widows_wail.yaml) - inverse-HP damage to both."""
    def __new__(cls):
        return _load_yaml_ability("widows_wail.yaml", cls_name="WidowsWail")


class ThrowRock:
    """Data-driven (throw_rock.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("throw_rock.yaml", cls_name="ThrowRock")


class Stomp:
    """Data-driven (stomp.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("stomp.yaml", cls_name="Stomp")


class Slam:
    """Knocks prone on a critical - data-driven (Batch 4)."""
    def __new__(cls):
        return _load_yaml_ability("slam.yaml", cls_name="Slam")


class Screech:
    """Data-driven (screech.yaml) - damage + permanent Silence."""
    def __new__(cls):
        return _load_yaml_ability("screech.yaml", cls_name="Screech")


class Detonate:
    """Data-driven (detonate.yaml) - self-destruct massive damage."""
    def __new__(cls):
        return _load_yaml_ability("detonate.yaml", cls_name="Detonate")


class Crush:
    """Data-driven (crush.yaml) - grab + crush + throw."""
    def __new__(cls):
        return _load_yaml_ability("crush.yaml", cls_name="Crush")


class ConsumeItem:
    """Data-driven (consume_item.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("consume_item.yaml", cls_name="ConsumeItem")


class DestroyMetal:
    """Data-driven (destroy_metal.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("destroy_metal.yaml", cls_name="DestroyMetal")


class Turtle(Skill):

    def __init__(self):
        super().__init__(
            name="Turtle",
            description="Hunker down into a ball, reducing all damage to 0 and regenerating"
            " health.",
        )
        self.passive = True


class Tunnel:
    """Data-driven (tunnel.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("tunnel.yaml", cls_name="Tunnel")


class Surface:
    """Data-driven (surface.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("surface.yaml", cls_name="Surface")


class GoblinPunch:
    """Data-driven (goblin_punch.yaml) - multi-hit str-diff damage."""
    def __new__(cls):
        return _load_yaml_ability("goblin_punch.yaml", cls_name="GoblinPunch")


class BrainGorge:
    """Data-driven (brain_gorge.yaml) - weapon hit + latch + intel drain."""
    def __new__(cls):
        return _load_yaml_ability("brain_gorge.yaml", cls_name="BrainGorge")


class Counterspell:
    """Data-driven (counterspell.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("counterspell.yaml", cls_name="Counterspell")


class ChooseFate:
    """Data-driven (choose_fate.yaml) - Devil lets player pick his action."""
    def __new__(cls):
        return _load_yaml_ability("choose_fate.yaml", cls_name="ChooseFate")


class VesperionChooseFate:
    """Data-driven (vesperion_choose_fate.yaml) - Vesperion's choice pressure."""
    def __new__(cls):
        return _load_yaml_ability("vesperion_choose_fate.yaml", cls_name="VesperionChooseFate")


class BreatheFire:
    """Data-driven (breathe_fire.yaml) - stat-based elemental breath."""
    def __new__(cls):
        return _load_yaml_ability("breathe_fire.yaml", cls_name="BreatheFire")


class DragonBreathFire:
    """Data-driven (dragon_breath_fire.yaml) - charging fire breath."""
    def __new__(cls):
        return _load_yaml_ability("dragon_breath_fire.yaml", cls_name="DragonBreathFire")


class DragonBreathWater:
    """Data-driven (dragon_breath_water.yaml) - charging water breath."""
    def __new__(cls):
        return _load_yaml_ability("dragon_breath_water.yaml", cls_name="DragonBreathWater")


class DragonBreathWind:
    """Data-driven (dragon_breath_wind.yaml) - charging wind breath."""
    def __new__(cls):
        return _load_yaml_ability("dragon_breath_wind.yaml", cls_name="DragonBreathWind")


# ── Companion Ultimate Attacks ────────────────────────────────────────


class TitanicSlam:
    """Data-driven (titanic_slam.yaml) - Patagon ultimate."""
    def __new__(cls):
        return _load_yaml_ability("titanic_slam.yaml", cls_name="TitanicSlam")


class Devour:
    """Data-driven (devour.yaml) - Dilong ultimate."""
    def __new__(cls):
        return _load_yaml_ability("devour.yaml", cls_name="Devour")


class AbsoluteZero:
    """Data-driven (absolute_zero.yaml) - Agloolik ultimate."""
    def __new__(cls):
        return _load_yaml_ability("absolute_zero.yaml", cls_name="AbsoluteZero")


class Eruption:
    """Data-driven (eruption.yaml) - Cacus ultimate."""
    def __new__(cls):
        return _load_yaml_ability("eruption.yaml", cls_name="Eruption")


class MaelstromVortex:
    """Data-driven (maelstrom_vortex.yaml) - Fuath ultimate."""
    def __new__(cls):
        return _load_yaml_ability("maelstrom_vortex.yaml", cls_name="MaelstromVortex")


class Thunderstrike:
    """Data-driven (thunderstrike.yaml) - Izulu ultimate."""
    def __new__(cls):
        return _load_yaml_ability("thunderstrike.yaml", cls_name="Thunderstrike")


class WindShrapnel:
    """Data-driven (wind_shrapnel.yaml) - Hala ultimate."""
    def __new__(cls):
        return _load_yaml_ability("wind_shrapnel.yaml", cls_name="WindShrapnel")


class DivineJudgment:
    """Data-driven (divine_judgment.yaml) - Seraphim ultimate."""
    def __new__(cls):
        return _load_yaml_ability("divine_judgment.yaml", cls_name="DivineJudgment")


class Oblivion:
    """Data-driven (oblivion.yaml) - Bardi ultimate."""
    def __new__(cls):
        return _load_yaml_ability("oblivion.yaml", cls_name="Oblivion")


class GrandHeist:
    """Data-driven (grand_heist.yaml) - Kobalos ultimate."""
    def __new__(cls):
        return _load_yaml_ability("grand_heist.yaml", cls_name="GrandHeist")


class Cataclysm:
    """Data-driven (cataclysm.yaml) - Zahhak ultimate."""
    def __new__(cls):
        return _load_yaml_ability("cataclysm.yaml", cls_name="Cataclysm")


class CrushingBlow(Skill):
    """Data-driven (crushing_blow.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("crushing_blow.yaml", cls_name="CrushingBlow")


"""
Spell section
"""
