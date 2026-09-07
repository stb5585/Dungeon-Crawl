"""Named skill, spell, and power-up effect constructors."""

from __future__ import annotations

from src.core.effects import (
    AbsoluteZeroEffect,
    ArcaneBlastEffect,
    AstralJudgmentEffect,
    BlackjackEffect,
    BrainGorgeEffect,
    CataclysmEffect,
    ChargeEffect,
    ChooseFateEffect,
    ConsumeItemEffect,
    CounterspellEffect,
    CrushEffect,
    CrushingBlowEffect,
    DestroyMetalEffect,
    DetonateEffect,
    DevourEffect,
    DimMakEffect,
    DisintegrateEffect,
    DivineJudgmentEffect,
    DoublecastEffect,
    ElementalStrikeEffect,
    EruptionEffect,
    ExploitWeaknessEffect,
    GoldTossEffect,
    GrandHeistEffect,
    InspectEffect,
    JumpEffect,
    KidneyPunchEffect,
    LickEffect,
    MaelstromEffect,
    MaelstromVortexEffect,
    MugEffect,
    OblivionEffect,
    PoisonStrikeEffect,
    ResistImmunityEffect,
    ResurrectionEffect,
    RevealEffect,
    ShadowStrikeEffect,
    ShapeshiftEffect,
    ShieldSlamEffect,
    SlotMachineEffect,
    SoulDrainEffect,
    StealEffect,
    StompEffect,
    ThrowRockEffect,
    ThunderstrikeEffect,
    TitanicSlamEffect,
    TotemEffect,
    TransformEffect,
    VesperionChooseFateEffect,
    WindShrapnelEffect,
)


class SpecialEffectFactoryMixin:
    @staticmethod
    def _create_shield_slam(data: dict) -> ShieldSlamEffect:
        return ShieldSlamEffect()

    @staticmethod
    def _create_kidney_punch(data: dict) -> KidneyPunchEffect:
        return KidneyPunchEffect(cost=data.get("cost", 12))

    @staticmethod
    def _create_poison_strike(data: dict) -> PoisonStrikeEffect:
        return PoisonStrikeEffect(damage_pct=data.get("damage_pct", 0.1))

    @staticmethod
    def _create_dim_mak(data: dict) -> DimMakEffect:
        return DimMakEffect()

    @staticmethod
    def _create_exploit_weakness(data: dict) -> ExploitWeaknessEffect:
        return ExploitWeaknessEffect()

    @staticmethod
    def _create_gold_toss(data: dict) -> GoldTossEffect:
        return GoldTossEffect()

    @staticmethod
    def _create_lick(data: dict) -> LickEffect:
        return LickEffect()

    @staticmethod
    def _create_brain_gorge(data: dict) -> BrainGorgeEffect:
        return BrainGorgeEffect()

    @staticmethod
    def _create_detonate(data: dict) -> DetonateEffect:
        return DetonateEffect()

    @staticmethod
    def _create_crush(data: dict) -> CrushEffect:
        return CrushEffect()

    @staticmethod
    def _create_maelstrom(data: dict) -> MaelstromEffect:
        return MaelstromEffect(
            success_pct=data.get("success_pct", 0.10),
            fail_pct=data.get("fail_pct", 0.25),
        )

    @staticmethod
    def _create_disintegrate(data: dict) -> DisintegrateEffect:
        return DisintegrateEffect()

    @staticmethod
    def _create_inspect(data: dict) -> InspectEffect:
        return InspectEffect()

    @staticmethod
    def _create_resist_immunity(data: dict) -> ResistImmunityEffect:
        return ResistImmunityEffect(
            resist_type=data.get("resist_type", "Poison"),
            min_resist=data.get("min_resist", 0.5),
            immunity_name=data.get("immunity_name", "Poison"),
        )

    @staticmethod
    def _create_resurrection(data: dict) -> ResurrectionEffect:
        return ResurrectionEffect(
            revive_pct=data.get("revive_pct", 0.1),
        )

    @staticmethod
    def _create_reveal(data: dict) -> RevealEffect:
        return RevealEffect(
            resist_bonus=data.get("resist_bonus", 0.25),
        )

    @staticmethod
    def _create_transform(data: dict) -> TransformEffect:
        return TransformEffect(
            creature=data.get("creature", "Panther"),
        )

    @staticmethod
    def _create_stomp(data: dict) -> StompEffect:
        return StompEffect()

    @staticmethod
    def _create_throw_rock(data: dict) -> ThrowRockEffect:
        return ThrowRockEffect()

    @staticmethod
    def _create_steal(data: dict) -> StealEffect:
        return StealEffect(
            gold_cap=data.get("gold_cap", 0.05),
        )

    @staticmethod
    def _create_mug(data: dict) -> MugEffect:
        return MugEffect()

    @staticmethod
    def _create_counterspell(data: dict) -> CounterspellEffect:
        return CounterspellEffect()

    @staticmethod
    def _create_elemental_strike(data: dict) -> ElementalStrikeEffect:
        return ElementalStrikeEffect()

    @staticmethod
    def _create_blackjack(data: dict) -> BlackjackEffect:
        return BlackjackEffect()

    @staticmethod
    def _create_doublecast(data: dict) -> DoublecastEffect:
        return DoublecastEffect(
            cast_count=data.get("cast_count", 2),
            exclude_spells=data.get("exclude_spells", ["Magic Missile"]),
            ability_cost=data.get("ability_cost", 0),
        )

    @staticmethod
    def _create_choose_fate(data: dict) -> ChooseFateEffect:
        return ChooseFateEffect(
            dmg_mod=data.get("dmg_mod", 1.5),
        )

    @staticmethod
    def _create_vesperion_choose_fate(data: dict) -> VesperionChooseFateEffect:
        return VesperionChooseFateEffect()

    @staticmethod
    def _create_shapeshift(data: dict) -> ShapeshiftEffect:
        return ShapeshiftEffect(
            status_name=data.get("status_name", "Shapeshifted"),
            status_duration=data.get("status_duration", 3),
        )

    @staticmethod
    def _create_astral_judgment(data: dict) -> AstralJudgmentEffect:
        return AstralJudgmentEffect(
            damage_mod=data.get("damage_mod", 3.0),
            rider_duration=data.get("rider_duration", 2),
        )

    @staticmethod
    def _create_consume_item(data: dict) -> ConsumeItemEffect:
        return ConsumeItemEffect()

    @staticmethod
    def _create_destroy_metal(data: dict) -> DestroyMetalEffect:
        return DestroyMetalEffect(
            metal_subtypes=data.get("metal_subtypes"),
        )

    @staticmethod
    def _create_slot_machine(data: dict) -> SlotMachineEffect:
        return SlotMachineEffect()

    @staticmethod
    def _create_totem(data: dict) -> TotemEffect:
        return TotemEffect(
            aspects=data.get("aspects"),
            unlock_requirements=data.get("unlock_requirements"),
            duration_base=data.get("duration_base", 5),
        )

    @staticmethod
    def _create_soul_drain(data: dict) -> SoulDrainEffect:
        return SoulDrainEffect(
            fraction=data.get("fraction", 0.10),
        )

    @staticmethod
    def _create_charge_execute(data: dict) -> ChargeEffect:
        return ChargeEffect(
            dmg_mod=data.get("dmg_mod", 1.25),
            stun_duration=data.get("stun_duration", 1),
        )

    @staticmethod
    def _create_crushing_blow(data: dict) -> CrushingBlowEffect:
        return CrushingBlowEffect(
            dmg_mod=data.get("dmg_mod", 3.0),
            crit_override=data.get("crit_override", 2),
            stun_chance=data.get("stun_chance", 0.5),
            stun_duration=data.get("stun_duration", 2),
        )

    @staticmethod
    def _create_arcane_blast(data: dict) -> ArcaneBlastEffect:
        return ArcaneBlastEffect(
            regen_turns=data.get("regen_turns", 4),
            regen_fraction=data.get("regen_fraction", 0.1),
        )

    @staticmethod
    def _create_jump_execute(data: dict) -> JumpEffect:
        return JumpEffect(
            base_dmg_mod=data.get("base_dmg_mod", 2.0),
        )

    @staticmethod
    def _create_shadow_strike_execute(data: dict) -> ShadowStrikeEffect:
        return ShadowStrikeEffect(
            dmg_mod=data.get("dmg_mod", 2.0),
            blind_chance=data.get("blind_chance", 0.6),
            blind_duration=data.get("blind_duration", 2),
        )

    @staticmethod
    def _create_titanic_slam(data: dict) -> TitanicSlamEffect:
        return TitanicSlamEffect(
            dmg_mod=data.get("dmg_mod", 4.0),
            crit_override=data.get("crit_override", 2),
            stun_duration=data.get("stun_duration", 2),
        )

    @staticmethod
    def _create_devour(data: dict) -> DevourEffect:
        return DevourEffect(
            num_bites=data.get("num_bites", 3),
            multiplier=data.get("multiplier", 1.5),
            element=data.get("element", "Earth"),
        )

    @staticmethod
    def _create_absolute_zero(data: dict) -> AbsoluteZeroEffect:
        return AbsoluteZeroEffect(
            damage_mod=data.get("damage_mod", 3.0),
            stun_duration=data.get("stun_duration", 3),
            def_reduction=data.get("def_reduction", 5),
        )

    @staticmethod
    def _create_eruption(data: dict) -> EruptionEffect:
        return EruptionEffect(
            damage_mod=data.get("damage_mod", 3.5),
            burn_duration=data.get("burn_duration", 3),
            vulcanize_duration=data.get("vulcanize_duration", 3),
        )

    @staticmethod
    def _create_maelstrom_vortex(data: dict) -> MaelstromVortexEffect:
        return MaelstromVortexEffect(
            damage_mod=data.get("damage_mod", 3.0),
            status_duration=data.get("status_duration", 3),
        )

    @staticmethod
    def _create_thunderstrike(data: dict) -> ThunderstrikeEffect:
        return ThunderstrikeEffect(
            damage_mod=data.get("damage_mod", 3.0),
            chain_hits=data.get("chain_hits", 2),
            chain_multiplier=data.get("chain_multiplier", 0.5),
            stun_duration=data.get("stun_duration", 2),
        )

    @staticmethod
    def _create_wind_shrapnel(data: dict) -> WindShrapnelEffect:
        return WindShrapnelEffect(
            num_hits=data.get("num_hits", 5),
            damage_mod=data.get("damage_mod", 1.2),
            crit_chance=data.get("crit_chance", 0.25),
            crit_multiplier=data.get("crit_multiplier", 2.0),
        )

    @staticmethod
    def _create_divine_judgment(data: dict) -> DivineJudgmentEffect:
        return DivineJudgmentEffect(
            damage_mod=data.get("damage_mod", 3.0),
            undead_multiplier=data.get("undead_multiplier", 2.0),
            heal_fraction=data.get("heal_fraction", 0.5),
        )

    @staticmethod
    def _create_oblivion(data: dict) -> OblivionEffect:
        return OblivionEffect(
            damage_mod=data.get("damage_mod", 4.0),
            kill_chance=data.get("kill_chance", 0.2),
            stat_drain=data.get("stat_drain", 3),
        )

    @staticmethod
    def _create_grand_heist(data: dict) -> GrandHeistEffect:
        return GrandHeistEffect(
            gold_multiplier=data.get("gold_multiplier", 2.0),
            debuff_duration=data.get("debuff_duration", 3),
        )

    @staticmethod
    def _create_cataclysm(data: dict) -> CataclysmEffect:
        return CataclysmEffect(
            spell_count=data.get("spell_count", 3),
            breath_multiplier=data.get("breath_multiplier", 2.0),
            power_up_duration=data.get("power_up_duration", 3),
        )
