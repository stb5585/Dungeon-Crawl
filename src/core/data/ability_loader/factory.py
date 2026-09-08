"""Data-driven ability construction and directory loading."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from ...combat.targeting import TargetLossPolicy, TargetScope
from .cache import _load_yaml_definition
from .effects import EffectFactory


class AbilityFactory:
    """
    Factory for creating Ability objects from data definitions.

    When ``combat_ready=True`` (the default), the factory produces
    ``DataDrivenSpell`` / ``DataDrivenSkill`` instances whose ``cast()``
    and ``use()`` methods replicate the core combat pipeline and execute
    the composed effects.  These are fully usable in combat.

    When ``combat_ready=False``, a lightweight ``SimpleAbility`` dataclass
    is returned instead (useful for config loading and analytics only).
    """

    @staticmethod
    def create_from_dict(ability_data: dict, *, combat_ready: bool = True):
        """
        Create an Ability from a data dictionary.

        Args:
            ability_data: Dictionary containing ability definition
            combat_ready: If True, produce a DataDrivenSpell/DataDrivenSkill
                         that works in combat.  If False, produce a lightweight
                         SimpleAbility for config loading only.

        Returns:
            Ability instance (DataDrivenSpell, DataDrivenSkill, or SimpleAbility)
        """
        name = ability_data.get("name", "Unknown")
        description = ability_data.get("description", "")
        cost = ability_data.get("cost", 0)
        ability_type = ability_data.get("type", "Skill")
        subtype = ability_data.get("subtype", "Offensive")
        damage_mod = ability_data.get("damage_mod", 1.0)
        crit = ability_data.get("crit", 5)
        rank = ability_data.get("rank")
        charge_time = ability_data.get("charge_time")
        delay = ability_data.get("delay")
        telegraph_message = ability_data.get("telegraph_message")
        priority = ability_data.get("priority")
        notes = ability_data.get("notes")
        school = ability_data.get("school")
        weapon = ability_data.get("weapon", False)
        targeting = ability_data.get("targeting")
        if isinstance(targeting, dict):
            # Fully migrated definitions own their combat targeting contract.
            # The old top-level fields remain only for external legacy content.
            raw_target_scope = targeting.get("scope")
            raw_target_loss_policy = targeting.get("loss_policy")
            targeting_hostile = bool(targeting.get("hostile", False))
        else:
            raw_target_scope = ability_data.get("target_scope")
            raw_target_loss_policy = ability_data.get("target_loss_policy")
            targeting_hostile = True

        # Create Effect objects
        effects = []
        if "effects" in ability_data:
            for effect_data in ability_data["effects"]:
                effects.append(EffectFactory.create(effect_data))

        if not combat_ready:
            return AbilityFactory._create_simple(ability_data, effects)

        # ── Combat-ready instances ────────────────────────────────
        from src.core.data.data_driven_abilities import (
            DataDrivenChargingSkill,
            DataDrivenCustomSpell,
            DataDrivenHealSpell,
            DataDrivenJumpSkill,
            DataDrivenMagicMissileSpell,
            DataDrivenMovementSpell,
            DataDrivenSkill,
            DataDrivenSpell,
            DataDrivenStatusSkill,
            DataDrivenStatusSpell,
            DataDrivenSupportSpell,
            DataDrivenWeaponSpell,
        )

        if ability_type == "Heal":
            ability = DataDrivenHealSpell(
                name=name,
                description=description,
                cost=cost,
                heal=ability_data.get("heal", 0.3),
                crit=crit,
                turns=ability_data.get("turns", 0),
                effects=effects,
                rank=rank,
                instant_heal=ability_data.get("instant_heal", False),
            )
        elif ability_type == "Support":
            ability = DataDrivenSupportSpell(
                name=name,
                description=description,
                cost=cost,
                effects=effects,
                school=school,
                rank=rank,
                target_self=ability_data.get("target_self", True),
                wizard_free_cast=ability_data.get("wizard_free_cast", False),
                message=ability_data.get("message"),
                subtype=subtype,
            )
        elif ability_type == "Status":
            ability = DataDrivenStatusSpell(
                name=name,
                description=description,
                cost=cost,
                effects=effects,
                rank=rank,
                wizard_free_cast=ability_data.get("wizard_free_cast", False),
                messages=ability_data.get("messages"),
                subtype=ability_data.get("subtype"),
                school=ability_data.get("school"),
            )
        elif ability_type == "StatusSkill":
            ability = DataDrivenStatusSkill(
                name=name,
                description=description,
                cost=cost,
                effects=effects,
                subtyp=subtype,
                status_name=ability_data.get("status_name"),
                physical=ability_data.get("physical", False),
                actor_stat=ability_data.get("actor_stat", "strength"),
                actor_lo_divisor=ability_data.get("actor_lo_divisor", 2),
                actor_hi_divisor=ability_data.get("actor_hi_divisor", 1),
                actor_use_check_mod=ability_data.get("actor_use_check_mod"),
                actor_stat_alt=ability_data.get("actor_stat_alt"),
                target_stat=ability_data.get("target_stat", "wisdom"),
                target_lo_divisor=ability_data.get("target_lo_divisor", 2),
                target_hi_divisor=ability_data.get("target_hi_divisor", 1),
                target_use_check_mod=ability_data.get("target_use_check_mod"),
                duration=ability_data.get("duration", 3),
                duration_stat=ability_data.get("duration_stat"),
                duration_divisor=ability_data.get("duration_divisor", 5),
                duration_min=ability_data.get("duration_min", 3),
                skip_if_active=ability_data.get("skip_if_active", True),
                extend_if_active=ability_data.get("extend_if_active", 0),
                check_disarmable=ability_data.get("check_disarmable", False),
                check_flying=ability_data.get("check_flying", False),
                use_crit_multiplier=ability_data.get("use_crit_multiplier", False),
                messages=ability_data.get("messages"),
                add_luck_chance=ability_data.get("add_luck_chance", False),
                action_message=ability_data.get("action_message"),
                required_item=ability_data.get("required_item"),
            )
        elif ability_type == "Spell":
            ability = DataDrivenSpell(
                name=name,
                description=description,
                cost=cost,
                dmg_mod=damage_mod,
                crit=crit,
                subtyp=subtype,
                effects=effects,
                school=school,
                rank=rank,
                charge_time=charge_time,
                delay=delay,
                telegraph_message=telegraph_message,
                priority=priority,
                notes=notes,
                grounded_damage=ability_data.get("grounded_damage", False),
            )
        elif ability_type == "WeaponSpell":
            ability = DataDrivenWeaponSpell(
                name=name,
                description=description,
                cost=cost,
                dmg_mod=damage_mod,
                crit=crit,
                subtyp=ability_data.get("subtype", "Holy"),
                effects=effects,
                school=school,
                rank=rank,
                enemy_type_damage_modifiers=ability_data.get("enemy_type_damage_modifiers"),
            )
        elif ability_type == "CustomSpell":
            ability = DataDrivenCustomSpell(
                name=name,
                description=description,
                cost=cost,
                dmg_mod=damage_mod,
                crit=crit,
                subtyp=ability_data.get("subtype", "Holy"),
                effects=effects,
                school=school,
                rank=rank,
            )
        elif ability_type == "ChargingSkill":
            ability = DataDrivenChargingSkill(
                name=name,
                description=description,
                cost=cost,
                weapon=weapon,
                dmg_mod=damage_mod,
                effects=effects,
                subtyp=subtype,
                charge_time=charge_time,
                delay=delay,
                telegraph_message=telegraph_message,
                priority=priority,
                notes=notes,
                requires_any_mana=ability_data.get("requires_any_mana", False),
            )
        elif ability_type == "MagicMissile":
            ability = DataDrivenMagicMissileSpell(
                name=name,
                description=description,
                cost=cost,
                dmg_mod=damage_mod,
                crit=crit,
                subtyp=ability_data.get("subtype", "Non-elemental"),
                missiles=ability_data.get("missiles", 1),
                effects=effects,
                school=school,
                rank=rank,
            )
        elif ability_type == "JumpSkill":
            ability = DataDrivenJumpSkill(
                name=name,
                description=description,
                cost=cost,
                weapon=ability_data.get("weapon", True),
                dmg_mod=damage_mod,
                effects=effects,
                subtyp=subtype,
                charge_time=ability_data.get("charge_time", 1),
                telegraph_message=telegraph_message,
                prone_while_charging=ability_data.get("prone_while_charging", True),
                unlock_requirements=ability_data.get("unlock_requirements"),
                modifications_defaults=ability_data.get("modifications_defaults"),
                unlocked_defaults=ability_data.get("unlocked_defaults"),
                priority=priority,
                notes=notes,
            )
        elif ability_type == "Movement":
            ability = DataDrivenMovementSpell(
                name=name,
                description=description,
                cost=cost,
                movement_type=ability_data.get("movement_type", "sanctuary"),
                combat=ability_data.get("combat", True),
                effects=effects,
                notes=notes,
            )
        else:
            ability = DataDrivenSkill(
                name=name,
                description=description,
                cost=cost,
                weapon=weapon,
                dmg_mod=damage_mod,
                effects=effects,
                subtyp=subtype,
                charge_time=charge_time,
                delay=delay,
                telegraph_message=telegraph_message,
                priority=priority,
                notes=notes,
                ignore_armor=ability_data.get("ignore_armor", False),
                guaranteed_hit=ability_data.get("guaranteed_hit", False),
                crit_override=ability_data.get("crit_override"),
                strikes=ability_data.get("strikes", 1),
                requires_incapacitated=ability_data.get("requires_incapacitated", False),
                intel_dmg_mod=ability_data.get("intel_dmg_mod", False),
                ice_block_check=ability_data.get("ice_block_check", False),
                self_target=ability_data.get("self_target", False),
                use_out_enabled=ability_data.get("use_out_enabled", False),
                target_status_damage_multiplier=ability_data.get("target_status_damage_multiplier"),
                use_offhand=ability_data.get("use_offhand", False),
                repeat_until_miss=ability_data.get("repeat_until_miss", False),
                accuracy_penalty_per_strike=ability_data.get("accuracy_penalty_per_strike", 0.0),
            )

        # Stash raw data for inspection / analytics
        ability._raw_data = ability_data
        if ability_data.get("id"):
            ability.ability_id = str(ability_data["id"])
        ability.aliases = tuple(str(alias) for alias in ability_data.get("aliases", ()))
        ability.damage_types = tuple(ability_data.get("damage_types", ()))
        ability.target_scope = AbilityFactory._target_scope(
            ability_data,
            raw_target_scope,
        )
        ability.target_loss_policy = AbilityFactory._target_loss_policy(
            name,
            raw_target_loss_policy,
        )
        ability.targeting_hostile = targeting_hostile
        # Carry over passive flag from YAML
        if ability_data.get("passive", False):
            ability.passive = True
        return ability

    @staticmethod
    def _target_scope(ability_data: dict, raw_scope: str | None) -> TargetScope:
        """Load explicit targeting metadata or apply the migration default."""
        if raw_scope is not None:
            migrated_scopes = {
                "single_opponent": TargetScope.SINGLE_ENEMY,
                "all_opponents": TargetScope.ALL_ENEMIES,
            }
            normalized_scope = str(raw_scope).lower()
            if normalized_scope in migrated_scopes:
                return migrated_scopes[normalized_scope]
            return TargetScope(normalized_scope)
        if ability_data.get("passive", False) or not ability_data.get("combat", True):
            return TargetScope.NONE
        ability_type = ability_data.get("type", "Skill")
        if ability_type in {"Heal", "Support", "Movement"}:
            return TargetScope.SELF
        if ability_data.get("self_target", False):
            return TargetScope.SELF
        return TargetScope.SINGLE_ENEMY

    @staticmethod
    def _target_loss_policy(
        name: str,
        raw_policy: str | None,
    ) -> TargetLossPolicy:
        """Load explicit target retention or use the approved direct-action default."""
        if raw_policy is not None:
            return TargetLossPolicy(str(raw_policy).lower())
        del name
        return TargetLossPolicy.RETARGET_FOCUS

    @staticmethod
    def _create_simple(ability_data: dict, effects: list):
        """Produce a lightweight SimpleAbility (config loading only)."""
        from dataclasses import dataclass, field

        targeting = ability_data.get("targeting")
        if isinstance(targeting, dict):
            raw_target_scope = targeting.get("scope")
            raw_target_loss_policy = targeting.get("loss_policy")
        else:
            raw_target_scope = ability_data.get("target_scope")
            raw_target_loss_policy = ability_data.get("target_loss_policy")

        @dataclass
        class SimpleAbility:
            """Simplified ability structure for data-driven abilities."""

            name: str
            typ: str
            subtyp: str
            description: str
            cost: int
            dmg_mod: float
            effects: list = field(default_factory=list)
            charge_time: int | None = None
            delay: int | None = None
            telegraph_message: str | None = None
            priority: str | None = None
            prone_while_charging: bool | None = None
            notes: str | None = None
            raw_data: dict = field(default_factory=dict)
            ability_id: str | None = None
            aliases: tuple[str, ...] = ()
            target_scope: TargetScope = TargetScope.SINGLE_ENEMY
            target_loss_policy: TargetLossPolicy = TargetLossPolicy.RETARGET_FOCUS

        return SimpleAbility(
            name=ability_data.get("name", "Unknown"),
            typ=ability_data.get("type", "Skill"),
            subtyp=ability_data.get("subtype", "Offensive"),
            description=ability_data.get("description", ""),
            cost=ability_data.get("cost", 0),
            dmg_mod=ability_data.get("damage_mod", 1.0),
            effects=effects,
            charge_time=ability_data.get("charge_time"),
            delay=ability_data.get("delay"),
            telegraph_message=ability_data.get("telegraph_message"),
            priority=ability_data.get("priority"),
            prone_while_charging=ability_data.get("prone_while_charging"),
            notes=ability_data.get("notes"),
            raw_data=ability_data,
            ability_id=(str(ability_data["id"]) if ability_data.get("id") else None),
            aliases=tuple(str(alias) for alias in ability_data.get("aliases", ())),
            target_scope=AbilityFactory._target_scope(ability_data, raw_target_scope),
            target_loss_policy=AbilityFactory._target_loss_policy(
                ability_data.get("name", "Unknown"),
                raw_target_loss_policy,
            ),
        )

    @staticmethod
    def create_from_yaml(file_path: str | Path, *, combat_ready: bool = True):
        """
        Load an ability from a YAML file.

        Args:
            file_path: Path to the YAML file
            combat_ready: If True, produce combat-ready instances.

        Returns:
            Ability instance
        """
        path = Path(file_path).resolve()
        data = deepcopy(_load_yaml_definition(str(path), path.stat().st_mtime_ns))
        declared_id = data.get("id")
        if declared_id is not None and str(declared_id) != path.stem:
            raise ValueError(f"Ability id {declared_id!r} must match filename stem {path.stem!r}")
        ability = AbilityFactory.create_from_dict(data, combat_ready=combat_ready)
        ability.ability_id = path.stem
        return ability

    @staticmethod
    def load_abilities_from_directory(directory: str | Path, *, combat_ready: bool = True) -> dict:
        """
        Load all abilities from a directory of YAML files.

        Args:
            directory: Path to directory containing ability definitions
            combat_ready: If True, produce combat-ready instances.

        Returns:
            Dictionary mapping ability names to Ability objects
        """
        directory_path = Path(directory)
        abilities = {}

        for file_path in directory_path.glob("*.yaml"):
            try:
                ability = AbilityFactory.create_from_yaml(file_path, combat_ready=combat_ready)
                abilities[ability.name] = ability
            except Exception as e:
                print(f"Error loading ability from {file_path}: {e}")

        return abilities
