"""Character absorption, shielding, and damage-reduction behavior."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from ..constants import (
    ARMOR_SCALING_FACTOR,
    ASTRAL_SHIFT_REDUCTION,
    DAMAGE_VARIANCE_HIGH,
    DAMAGE_VARIANCE_LOW,
    MAGIC_DEF_SCALING_FACTOR,
)
from .models import BLEED_MELEE_DAMAGE_TAKEN_MULTIPLIER, _class_name

if TYPE_CHECKING:
    from .core import Character
    from .models import AbsorptionResult, DamageReductionResult, DefenseResolution


class CharacterDefenseMixin:
    def _apply_absorption(
        self, defender: Character, damage: int, raw_dmg: int,
        crit_per: float, att: str, cover: bool, crit: int
    ) -> AbsorptionResult:
        """
        Apply cover, shield block, mana shield, class shields, and reflect.

        Returns:
            (remaining_damage, message, fully_absorbed)
        """
        msg = ""
        absorbed = False
        from ..classes import ability_mechanics

        if cover:
            msg += (f"{defender.familiar.name} steps in front of the attack, "
                    f"taking the damage for {defender.name}.\n")
            return 0, msg, False  # damage zeroed but hit still counts

        # Shield block
        can_block = (
            (defender.equipment['OffHand'].subtyp == 'Shield' or
             'Dodge' in defender.equipment['Ring'].mod) and
            not defender.magic_effects["Mana Shield"].active and
            not (_class_name(defender) == "Crusader" and defender.power_up and
                 defender.class_effects["Power Up"].active) and
            not defender.incapacitated()
        )
        if can_block:
            blk_chance = defender.check_mod('shield', enemy=self) / 100
            try:
                from ..classes import paladin

                blk_chance += paladin.protection_block_bonus(defender)
            except Exception:
                pass
            if blk_chance > random.random():
                blk_per = blk_chance + ((defender.stats.strength - self.stats.strength) / damage) if damage else 0
                if 'Shield Block' in defender.spellbook['Skills']:
                    blk_per *= 1.25
                try:
                    from ..classes import paladin

                    blk_per += paladin.protection_mitigation_bonus(defender)
                except Exception:
                    pass
                if blk_per > 0:
                    blk_per = min(1, blk_per)
                    damage = int(damage * (1 - blk_per))
                    try:
                        from ..events.event_bus import get_event_bus, create_combat_event, EventType
                        event_bus = get_event_bus()
                        event_bus.emit(create_combat_event(
                            EventType.BLOCK, actor=defender, target=self,
                            damage_blocked=int(raw_dmg * crit_per * blk_per),
                            **self._weapon_event_metadata(att),
                        ))
                    except Exception:
                        pass
                    blocked_pct = round(blk_per * 100)
                    if blocked_pct > 0:
                        msg += (f"{defender.name} blocks {self.name}'s attack and mitigates "
                                f"{blocked_pct} percent of the damage.\n")
                    msg += ability_mechanics.retaliate_after_block(defender, self)
                    try:
                        from ..classes import paladin

                        msg += paladin.block_succeeded(defender)
                    except Exception:
                        pass
            return damage, msg, False

        # Mana Shield
        if defender.magic_effects["Mana Shield"].active:
            damage, shield_msg, absorbed = self._apply_mana_shield(defender, damage)
            return damage, msg + shield_msg, absorbed

        # Crusader absorb shield
        if (_class_name(defender) == "Crusader" and defender.power_up and
                defender.class_effects["Power Up"].active):
            damage, shield_msg, absorbed = self._apply_crusader_shield(defender, damage)
            return damage, msg + shield_msg, absorbed

        # Templar reflect
        if (_class_name(defender) == "Templar" and defender.power_up and
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

    def _apply_mana_shield(self, defender: Character, damage: int) -> AbsorptionResult:
        """Handle Mana Shield absorption. Returns (damage, msg, fully_absorbed)."""
        msg = ""
        if damage <= 0:
            return damage, msg, False

        duration = max(1, int(defender.magic_effects["Mana Shield"].duration or 1))
        available_mana = max(0, int(defender.mana.current))
        if available_mana <= 0:
            self._emit_status_event(defender, "Mana Shield", applied=False, source="Mana Depleted")
            defender.magic_effects["Mana Shield"].active = False
            msg += f"The mana shield dissolves around {defender.name}.\n"
            return damage, msg, False

        mana_loss = damage // duration
        if mana_loss > available_mana:
            abs_dam = available_mana * duration
            if abs_dam > 0:
                msg += f"The mana shield around {defender.name} absorbs {abs_dam} damage.\n"
            damage -= abs_dam
            defender.mana.current = 0
            self._emit_status_event(defender, "Mana Shield", applied=False, source="Mana Depleted")
            defender.magic_effects["Mana Shield"].active = False
            msg += f"The mana shield dissolves around {defender.name}.\n"
            return damage, msg, False
        else:
            msg += f"The mana shield around {defender.name} absorbs {damage} damage.\n"
            defender.mana.current = max(0, defender.mana.current - mana_loss)
            return 0, msg, True

    def _apply_crusader_shield(self, defender: Character, damage: int) -> AbsorptionResult:
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
    ) -> DamageReductionResult:
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
        try:
            from ..classes import paladin

            damage = int(damage * paladin.incoming_damage_multiplier(defender, "Physical"))
        except Exception:
            pass

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

        if defender.magic_effects.get("Stone Skin") and defender.magic_effects["Stone Skin"].active and damage > 0:
            reduced = max(1, int(damage * 0.35))
            damage = max(0, damage - reduced)
            msg += f"{defender.name}'s stone skin absorbs {reduced} damage.\n"

        try:
            from ..classes import wizard

            damage, frozen_message = wizard.frozen_armor_reduction(defender, damage)
            msg += frozen_message
        except Exception:
            pass

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

        try:
            from ..classes import promotion_kits

            damage, devotion_message = promotion_kits.devotion_guard_reduction(defender, damage)
            msg += devotion_message
        except Exception:
            pass

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
        self._emit_damage_event(
            defender,
            damage,
            damage_type=damage_type,
            is_critical=(crit > 1),
            **self._weapon_event_metadata(att),
        )
        try:
            from ..classes import promotion_kits

            msg += promotion_kits.pop_messages(self)
            msg += promotion_kits.pop_messages(defender)
        except Exception:
            pass

        # Sleep wakeup
        if defender.status_effects["Sleep"].active and \
                not random.randint(0, defender.status_effects["Sleep"].duration):
            msg += f"The attack awakens {defender.name}!\n"
            self._emit_status_event(defender, "Sleep", applied=False, source="Awakened by Damage")
            defender.status_effects["Sleep"].active = False
            defender.status_effects["Sleep"].duration = 0

        # Ninja life steal
        if _class_name(self) == "Ninja" and self.power_up:
            dam_abs = self.class_effects["Power Up"].active * damage
            dam_abs = int(dam_abs * self.healing_received_multiplier())
            dam_abs = min(dam_abs, self.health.max - self.health.current)
            self.health.current += dam_abs
            self._emit_healing_event(dam_abs, source="Ninja Life Steal")
            if hasattr(defender, "record_archdruid_life_drained"):
                defender.record_archdruid_life_drained()
            msg += f"{self.name} absorbs {dam_abs} from {defender.name}.\n"

        # Lycan life steal
        if _class_name(self) == "Lycan" and self.power_up:
            dam_abs = damage // 2
            dam_abs = int(dam_abs * self.healing_received_multiplier())
            dam_abs = min(dam_abs, self.health.max - self.health.current)
            self.health.current += dam_abs
            if dam_abs > 0:
                self._emit_healing_event(dam_abs, source="Lycan Life Steal")
                if hasattr(defender, "record_archdruid_life_drained"):
                    defender.record_archdruid_life_drained()
            msg += f"{self.name} absorbs {dam_abs} from {defender.name}.\n"

        return msg

    def _apply_equipment_effects(
        self, defender: Character, att: str, damage: int, crit: int
    ) -> str:
        """Process armor/weapon special effects on a successful hit."""
        from ..combat.combat_result import CombatResult, CombatResultGroup

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
            if res.message:
                msg += res.message
            if 'Drain' in res.extra and res.extra['Drain']:
                drain_amount = res.actor.health.current - (res.actor.health.current - res.damage)
                msg += f"{res.actor.name} drains {drain_amount} health from {res.target.name}.\n"
            if 'Instant Death' in res.extra and res.extra['Instant Death']:
                res.target.health.current = 0
                msg += f"{res.target.name} is instantly killed!\n"

        return msg

    def handle_defenses(
        self,
        attacker: Character,
        damage: int,
        cover: bool = False,
        typ: str = "Physical",
    ) -> DefenseResolution:
        """
        Resolve active pre-reduction defenses for spell/effect damage.

        This is the shared entry point used by legacy spells, YAML abilities,
        and composite effects before elemental or magic-defense reduction. It
        currently handles Mana Shield absorption and returns pass-through
        damage for callers without an active shield.

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
            damage, shield_message, fully_absorbed = attacker._apply_mana_shield(
                self, damage
            )
            message += shield_message
            hit = not fully_absorbed

        if hit and typ == "Magic":
            try:
                from src.core.classes import nature_totems

                damage, ward_message = nature_totems.water_ward_absorb(self, damage)
                message += ward_message
            except Exception:
                pass

        return (hit, message, damage)

    def damage_reduction(self, damage: int, attacker: Character, typ: str = "Physical") -> DefenseResolution:
        """
        Apply elemental resistance and magic-defense reduction to incoming damage.

        This is the shared post-defense reduction step for legacy spells, YAML
        abilities, and composite effects. Weapon attacks use
        ``_apply_damage_reduction()`` because they also need equipment and
        armor-specific context.

        Args:
            damage: Incoming damage value
            attacker: The attacking character
            typ: Damage type for resistance calculation

        Returns:
            tuple: (hit: bool, message: str, final_damage: int)
        """
        if typ != "Physical" and damage > 0:
            try:
                from ..classes import ability_mechanics

                if ability_mechanics.spend_nature_shield_orb(self):
                    healing = max(1, int(damage * 0.5))
                    self.health.current = min(self.health.max, self.health.current + healing)
                    return False, f"A Nature Shield orb intercepts the spell and heals {self.name} for {healing}.\n", 0
            except Exception:
                pass

        # Apply basic resistance only if typ is a valid resistance type
        resist = 0
        if typ in self.resistance:
            resist = self.check_mod('resist', enemy=attacker, typ=typ)

        message = ""
        final_damage = int(damage * (1 - resist))
        try:
            from ..classes import paladin

            final_damage = int(final_damage * paladin.incoming_damage_multiplier(self, typ))
        except Exception:
            pass
        try:
            from ..classes import bard

            final_damage = int(final_damage * (1 - bard.damage_reduction(self)))
        except Exception:
            pass

        # Magic defense reduction: allow primary stats (WIS/CHA) to matter for
        # survival even on physical builds, by reducing incoming elemental/magic damage.
        if typ != "Physical" and final_damage > 0:
            mdef = int(self.check_mod("magic def", enemy=attacker) or 0)
            if mdef > 0:
                final_damage = int(final_damage * (1 - (mdef / (mdef + MAGIC_DEF_SCALING_FACTOR))))
        try:
            from ..classes import wizard

            final_damage, frozen_message = wizard.frozen_armor_reduction(self, final_damage)
            message += frozen_message
        except Exception:
            pass

        if resist > 0 and final_damage < damage:
            reduction = damage - final_damage
            message += f"{self.name}'s resistance reduces damage by {reduction}.\n"

        try:
            from ..classes import promotion_kits

            final_damage, devotion_message = promotion_kits.devotion_guard_reduction(self, final_damage)
            message += devotion_message
        except Exception:
            pass

        return True, message, final_damage
