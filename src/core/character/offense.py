"""Character hit, dodge, critical-hit, and weapon-damage behavior."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from ..constants import (
    ACCURACY_RING_BONUS,
    BASE_CRIT_PER_POINT,
    BERSERK_HIT_PENALTY,
    BLIND_ACCURACY_PENALTY,
    BLIND_RAGE_HIT_PENALTY,
    DISARM_HIT_PENALTY,
    DWARF_HANGOVER_DODGE_MULTIPLIER,
    ELF_BLIND_PENALTY_MULTIPLIER,
    ELF_INVISIBLE_PENALTY_MULTIPLIER,
    ENCUMBERED_HIT_MULTIPLIER,
    FLYING_ACCURACY_PENALTY,
    GNOME_ENCUMBERED_DODGE_MULTIPLIER,
    GNOME_ENCUMBERED_HIT_MULTIPLIER,
    HALF_ELF_CRIT_SPIKE_MULTIPLIER,
    HALF_ORC_BLIND_RAGE_CHANCE,
    HALF_ORC_BLIND_RAGE_DURATION,
    HALF_ORC_CRIT_DAMAGE_TAKEN_MULTIPLIER,
    INVISIBLE_ACCURACY_PENALTY,
    MAELSTROM_CRIT_PER_HIT,
    MAX_CRIT_CHANCE,
    MAX_DODGE_CHANCE,
    PRO_LEVEL_HIT_MODIFIER,
    SEEKER_CRIT_BONUS,
    WEAPON_CRIT_WEIGHT,
)
from .models import _class_name, sigmoid

if TYPE_CHECKING:
    from .core import Character
    from .models import WeaponDamageResult


class CharacterOffenseMixin:
    def _honed_attack_critical_multiplier(self, multiplier: float) -> float:
        """Increase only the bonus portion of weapon critical damage."""
        honed_attack = self.spellbook.get("Skills", {}).get("Honed Attack")
        if multiplier > 1 and honed_attack is not None:
            ranks = max(1, int(getattr(honed_attack, "ranks", 1) or 1))
            return 1 + ((multiplier - 1) * (1 + (0.25 * ranks)))
        return multiplier

    def hit_chance(self, defender: Character, typ: str = "weapon") -> float:
        """
        Calculate hit chance based on various factors.

        Things that affect hit chance
            Weapon attack: whether char is blind, if enemy is flying and/or invisible, enemy status effects,
                accessory bonuses, difference in pro level
            Spell attack: enemy status effects
        """
        from ..classes import ability_mechanics, footpad, healer, paladin, warrior

        # Defensive guard: speed stats can be 0 in synthetic/summon test states.
        a_speed = self.check_mod("speed", enemy=defender)
        d_speed = defender.check_mod("speed", enemy=self)
        num = random.randint(a_speed // 2, a_speed)
        den = random.randint(d_speed // 4, d_speed // 2)
        hit_mod = sigmoid(num / max(1, den))  # base hit percentage
        if typ == "weapon":
            hit_mod *= 1 + (ACCURACY_RING_BONUS * ("Accuracy" in self.equipment["Ring"].mod))
            blind_pen = BLIND_ACCURACY_PENALTY
            try:
                if getattr(getattr(self, "race", None), "name", None) == "Elf":
                    blind_pen *= ELF_BLIND_PENALTY_MULTIPLIER
            except Exception:
                pass
            if ability_mechanics.has_skill(self, "Blind Fighting"):
                blind_pen *= 0.50
            hit_mod *= 1 - (blind_pen * self.status_effects["Blind"].active)
            extended_reach = bool(
                defender.flying
                and getattr(self.equipment.get("Weapon"), "subtyp", None) == "Polearm"
                and "Extended Reach" in self.spellbook.get("Skills", {})
            )
            hit_mod *= 1 - FLYING_ACCURACY_PENALTY * (defender.flying and not extended_reach)
            hit_mod *= 1 - (DISARM_HIT_PENALTY * self.is_disarmed())
            hit_mod *= 1 - (BERSERK_HIT_PENALTY * (self.status_effects["Berserk"].active))
            hit_mod *= 1 - (BLIND_RAGE_HIT_PENALTY * (self.status_effects["Blind Rage"].active))
            if self.status_effects.get("Peaceful") and self.status_effects["Peaceful"].active:
                hit_mod += 0.10
        hit_mod += PRO_LEVEL_HIT_MODIFIER * (self.level.pro_level - defender.level.pro_level)
        invis_pen = INVISIBLE_ACCURACY_PENALTY
        try:
            if getattr(getattr(self, "race", None), "name", None) == "Elf":
                invis_pen *= ELF_INVISIBLE_PENALTY_MULTIPLIER
        except Exception:
            pass
        hit_mod *= 1 - invis_pen * defender.invisible
        hit_mod -= footpad.obscuration_accuracy_penalty(defender)
        hit_mod += footpad.surprise_accuracy_bonus(self)
        weapon_type = getattr(self.equipment.get("Weapon"), "subtyp", None)
        hit_mod += healer.accuracy_bonus(
            self,
            weapon_type if typ == "weapon" else None,
        )
        if hasattr(self, "encumbered"):
            if self.encumbered:
                hit_mod *= ENCUMBERED_HIT_MULTIPLIER
                try:
                    if getattr(getattr(self, "race", None), "name", None) == "Gnome":
                        hit_mod *= GNOME_ENCUMBERED_HIT_MULTIPLIER
                except Exception:
                    pass
        if typ == "weapon" and "Weapon Focus" in self.spellbook.get("Skills", {}):
            hit_mod += 0.05
        if typ == "weapon":
            hit_mod += ability_mechanics.duelist_accuracy_bonus(self)
            hit_mod += paladin.sword_and_board_accuracy_bonus(self)
            hit_mod += warrior.commitment_accuracy_bonus(self)
            try:
                from ..classes import mage_mechanics

                hit_mod += mage_mechanics.melee_accuracy_bonus(self)
            except Exception:
                pass
        elif typ == "magic":
            try:
                from ..classes import astromancer

                hit_mod += astromancer.threaded_bonus(self, "accuracy")
            except Exception:
                pass
            hit_mod += max(0.0, float(getattr(self, "_totem_surge_reliability", 0.0) or 0.0))
        return max(0, hit_mod)

    def dodge_chance(self, attacker: Character, spell: bool = False) -> float:
        from ..classes import ability_mechanics, footpad

        a_stat = attacker.check_mod("speed", enemy=self)
        d_stat = self.check_mod("speed", enemy=attacker)
        if spell:
            a_stat = attacker.stats.intel
            # Spells are avoided via mental defense; low CHA/WIS should matter.
            cha_term = max(-5, min(5, int(self.stats.charisma) - 10))
            d_stat = max(0, int(self.stats.wisdom) + cha_term)
        d_stat += ability_mechanics.third_eye_intelligence(self)
        armor_factor = {"None": 1, "Natural": 1, "Cloth": 1, "Light": 2, "Medium": 3, "Heavy": 4}
        a_chance = random.randint(a_stat // 2, a_stat) + attacker.check_mod(
            "luck", enemy=self, luck_factor=10
        )
        d_chance = (
            random.randint(0, d_stat // 2)
            + self.check_mod("luck", enemy=attacker, luck_factor=15)
            + (self.stat_effects["Speed"].active * self.stat_effects["Speed"].extra)
        )
        denom = a_chance + d_chance
        if denom <= 0:
            return 0.0
        af = armor_factor.get(getattr(self.equipment.get("Armor"), "subtyp", "None"), 1)
        chance = max(0, (d_chance - a_chance) / denom / af)
        chance += 0.1 * (
            "Dodge" in self.equipment["Ring"].mod + "Evasion" in self.spellbook["Skills"]
        )
        chance += footpad.concealment_dodge_bonus(self)
        if spell:
            pendant_mod = getattr(self.equipment.get("Pendant"), "mod", "")
            chance += 0.25 * ("Magic Dodge" in pendant_mod)
            try:
                from ..classes import footpad

                chance += footpad.spell_dodge_bonus(self)
            except Exception:
                pass
            chance -= max(
                0.0,
                float(getattr(attacker, "_totem_surge_reliability", 0.0) or 0.0),
            )
            try:
                from ..classes import astromancer

                chance -= astromancer.threaded_bonus(attacker, "accuracy")
            except Exception:
                pass
        # Footpad-line passive: scale *weapon* dodge slightly with DEX so "glass cannon"
        # races/classes have a defensive path that doesn't require changing race resistances.
        # We intentionally do not apply this to spell-avoidance, which is governed by WIS/CHA.
        if (not spell) and "Quickstep" in self.spellbook.get("Skills", {}):
            dex = int(getattr(self.stats, "dex", 10))
            # +0.00 at DEX<=10, up to +0.15 at DEX>=25
            chance += min(0.15, max(0.0, (dex - 10) / 100))
        if not spell:
            chance += footpad.live_and_learn_dodge_bonus(self)
        try:
            from ..classes import promotion_kits

            chance += promotion_kits.case_prediction_dodge_bonus(self, attacker)
            chance += promotion_kits.rope_a_dope_dodge_bonus(self)
        except Exception:
            pass
        cls_name = _class_name(self)
        if cls_name == "Seeker" or (
            cls_name == "Templar" and self.class_effects["Power Up"].active
        ):
            chance += 0.25 * self.power_up
        try:
            from ..classes import class_rings

            chance += class_rings.arcane_trickster_dodge_bonus(self)
        except Exception:
            pass
        chance += ability_mechanics.tricksters_gambit_dodge_bonus(self)
        try:
            from ..classes import paladin

            chance += paladin.retribution_dodge_bonus(self)
        except Exception:
            pass
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
        return max(0.0, min(MAX_DODGE_CHANCE, chance))

    def critical_chance(self, att: str) -> float:
        from ..classes import ability_mechanics, footpad

        base_crit = BASE_CRIT_PER_POINT * (
            self.check_mod("speed")
            + self.check_mod("luck", luck_factor=10)
            + ability_mechanics.third_eye_intelligence(self)
        )
        crit_chance = base_crit
        if self.equipment.get(att) is not None:
            weapon = self.equipment[att]
            weapon_crit = getattr(weapon, "crit_chance", getattr(weapon, "crit", 0.0))
            crit_chance += float(weapon_crit or 0.0) * WEAPON_CRIT_WEIGHT
        if _class_name(self) == "Seeker":
            crit_chance += SEEKER_CRIT_BONUS * self.power_up
        try:
            from ..classes import class_rings

            crit_chance += class_rings.bloodied_crit_bonus(self)
        except Exception:
            pass

        # Maelstrom Weapon: Add bonus critical chance for consecutive hits
        if "Maelstrom Weapon" in self.spellbook["Skills"]:
            # Backward compatibility for older runtime/save objects missing this field.
            maelstrom_hits = int(getattr(self, "maelstrom_hits", 0) or 0)
            maelstrom_bonus = maelstrom_hits * MAELSTROM_CRIT_PER_HIT
            crit_chance += maelstrom_bonus
        crit_chance += ability_mechanics.drunken_brawler_crit_bonus(self)
        crit_chance += ability_mechanics.tricksters_gambit_crit_bonus(self)
        crit_chance += ability_mechanics.duelist_critical_bonus(self)
        crit_chance += footpad.surprise_critical_bonus(self)
        crit_chance += footpad.toxic_precision_bonus(self, att)
        berserk = self.status_effects.get("Berserk")
        if berserk is not None and berserk.active and int(getattr(berserk, "extra", 0) or 0) == 1:
            crit_chance += 0.15
        try:
            from ..classes import mage_mechanics

            crit_chance += mage_mechanics.fire_inside_critical_bonus(self)
        except Exception:
            pass
        try:
            from ..classes import paladin

            crit_chance += paladin.undead_hunter_critical_bonus(self)
            crit_chance += paladin.penalization_critical_bonus(self)
        except Exception:
            pass

        return max(0.0, min(MAX_CRIT_CHANCE, crit_chance))

    def weapon_damage(
        self,
        defender: Character,
        dmg_mod: float = 1.0,
        crit: int = 1,
        ignore: bool = False,
        cover: bool = False,
        hit: bool = False,
        use_offhand: bool = True,
        attack_slots: tuple[str, ...] | None = None,
        accuracy_modifier: float = 0.0,
        critical_chance_modifier: float = 0.0,
        critical_multiplier: int | None = None,
        damage_type_override: str | None = None,
        basic_attack: bool = False,
        counterattack: bool = False,
    ) -> WeaponDamageResult:
        """
        Function that controls melee attacks during combat
        defender(Character): the target of the attack
        dmg_mod(float): a percentage value that modifies the amount of damage done
        crit(int): the damage multiplier for a critical hit
        ignore(bool): whether the attack ignores the target's defenses
        cover(bool): whether the attack can be blocked by a familiar or pet
        hit(bool): guarantees hit if target doesn't dodge
        """
        from ..combat.combat_result import CombatResult, CombatResultGroup
        from ..classes import (
            ability_mechanics,
            footpad,
            grandmaster,
            healer,
            paladin,
            pathfinder,
            warrior,
        )

        revelation_message = ""
        dmg_mod *= pathfinder.melee_damage_multiplier(self)
        dmg_mod *= pathfinder.ranger_weapon_damage_multiplier(self, defender)
        if getattr(defender, "_distracted_turns", 0):
            defender._distracted_turns = 0
        concealed_attack = bool(getattr(self, "_combat_concealed", False))
        self._surprise_attack = bool(getattr(self, "_surprise_ready", False) or concealed_attack)
        self._surprise_ready = False
        if concealed_attack:
            self._combat_concealed = False
            if "Shadow Evasion" in self.spellbook.get("Skills", {}):
                self._shadow_evasion_turns = 2
        conversion_bonus = pathfinder.consume_conversion(self)

        try:
            from ..classes import mage_mechanics

            dmg_mod *= mage_mechanics.melee_damage_multiplier(self)
            fire_inside_active = random.random() < mage_mechanics.fire_inside_critical_bonus(self)
            mage_mechanics.consume_fire_inside(self)
        except Exception:
            fire_inside_active = False
        self._last_attack_parried = False
        self._last_weapon_primary_damage = 0
        self._last_weapon_primary_damage_instances = []
        if defender.magic_effects["Ice Block"].active or defender.tunnel:
            self._surprise_attack = False
            return f"{self.name}'s attack has no effect.\n", False, crit
        warrior.record_attack(self, defender)
        if getattr(self, "_twist_fate_success", False):
            hit = True
            self._twist_fate_success = False
        hits = []  # indicates if the attack was successful for means of ability/weapon affects
        crits = []
        if attack_slots is not None:
            attacks = list(attack_slots)
        else:
            attacks = []
            maim = self.physical_effects.get("Maim")
            if maim is None or not maim.active:
                attacks.append("Weapon")
            if use_offhand and self.equipment["OffHand"].typ == "Weapon":
                attacks.append("OffHand")
        if not attacks:
            self._surprise_attack = False
            return f"{self.name} cannot use their main-hand weapon.\n", False, crit
        try:
            from ..classes import promotion_kits

            revelation_accuracy, revelation_damage, revelation_message = (
                promotion_kits.prepare_revelation_payoff(
                    self,
                    defender,
                    basic_attack=basic_attack,
                )
            )
            accuracy_modifier += revelation_accuracy
            dmg_mod *= revelation_damage
        except Exception:
            pass
        weapon_dam_str = revelation_message
        electrified_triggered = False
        for i, att in enumerate(attacks):
            hits.append(hit)
            crits.append(1)
            ignore = ignore or self.equipment[att].ignore
            damage = 0
            # attacker variables
            typ = "attacks"
            if self.equipment[att].subtyp == "Natural":
                typ = self.equipment[att].att_name
                if typ == "leers":
                    hits[i] = True
                    result = CombatResult(
                        action="Leer", actor=self, target=defender, hit=True, crit=1, damage=0
                    )
                    results = CombatResultGroup()
                    results.add(result)
                    self.equipment[att].special_effect(results)
                    weapon_dam_str += f"{self.name} leers at {defender.name}.\n"
                    break
            natural_crit = crit == 1 and (
                fire_inside_active
                or self.critical_chance(att) + critical_chance_modifier > random.random()
            )
            crits[i] = int(critical_multiplier or 2) if natural_crit else crit
            weapon_type = getattr(self.equipment[att], "subtyp", None)
            style_modifier = (
                ability_mechanics.duelist_damage_multiplier(self)
                * grandmaster.two_handed_damage_multiplier(self, att)
                * paladin.sword_and_board_damage_multiplier(self)
                * grandmaster.perfect_form_damage_multiplier(
                    self,
                    weapon_type,
                )
                * healer.staff_damage_multiplier(self, weapon_type)
            )
            cripple = self.physical_effects.get("Cripple")
            cripple_modifier = (
                1.0 - min(0.90, max(0.0, float(cripple.extra or 0)))
                if cripple is not None and cripple.active
                else 1.0
            )
            dmg = max(
                1,
                int(
                    dmg_mod
                    * style_modifier
                    * cripple_modifier
                    * self.check_mod(att.lower(), enemy=defender)
                ),
            )
            crit_per = random.uniform(1, crits[i])
            crit_per = self._honed_attack_critical_multiplier(crit_per)
            crit_per = warrior.commitment_critical_multiplier(self, crit_per)
            if crits[i] > 1:
                crit_per += conversion_bonus
            try:
                from ..classes import promotion_kits

                crit_per = promotion_kits.focused_assault_critical_multiplier(
                    self,
                    crit_per,
                )
            except Exception:
                pass
            crit_per = grandmaster.brutish_critical_multiplier(
                self,
                weapon_type,
                crit_per,
            )
            if crit_per > 1:
                try:
                    from ..classes import paladin

                    crit_per *= paladin.retribution_crit_damage_multiplier(self)
                except Exception:
                    pass
            if weapon_type == "Sword":
                precision = getattr(self, "grandmaster_technique_stacks", {}).get(
                    "Sword Precision", {}
                )
                stacks = int(precision.get("stacks", 0) or 0)
                if stacks and crit_per > 1:
                    crit_per += 0.05 * min(3, stacks)
            # Half Elf racial sin: slightly reduced crit spike potential.
            try:
                if (
                    getattr(getattr(self, "race", None), "name", None) == "Half Elf"
                    and crit_per > 1.0
                ):
                    crit_per = 1.0 + ((crit_per - 1.0) * HALF_ELF_CRIT_SPIKE_MULTIPLIER)
            except Exception:
                pass
            damage = max(0, int(dmg * crit_per))

            # defender variables
            if not hit:
                dodge_chance = defender.dodge_chance(self)
                if counterattack:
                    dodge_chance += pathfinder.counterattack_dodge_bonus(defender)
                dodge = dodge_chance > random.random()
                hit_per = self.hit_chance(defender, typ="weapon")
                hit_per += accuracy_modifier
                hit_per += ability_mechanics.dual_wield_accuracy_modifier(self, att)
                hit_per += grandmaster.accuracy_bonus(self, weapon_type)
                hit_per += grandmaster.two_handed_accuracy_bonus(self, att)
                hit_per += grandmaster.perfect_form_accuracy_bonus(
                    self,
                    weapon_type,
                )
                hit_per += ability_mechanics.polearm_accuracy_modifier(self, weapon_type)
                hit_per += ability_mechanics.monkey_grip_accuracy_modifier(self, att)
                from ..classes import promotion_kits

                hit_per += promotion_kits.aerial_accuracy_bonus(self)
                hit_per += promotion_kits.focused_assault_accuracy(self)
                hit_per += promotion_kits.jinx_accuracy_modifier(self)
                hits[i] = hit_per > random.random()
            else:
                dodge = False
            if defender.incapacitated():
                dodge = False
                hits[i] = True
            if (dodge or not hits[i]) and footpad.try_do_over(self):
                dodge = defender.dodge_chance(self) > random.random()
                hits[i] = (hit_per > random.random()) and not dodge
                weapon_dam_str += f"{self.name} uses Do-over to reroll the missed attack.\n"

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

            damage, msg, parried, aborted = self._apply_parry(defender, damage)
            weapon_dam_str += msg
            if (
                not parried
                and "Untouchable" in defender.spellbook.get("Skills", {})
                and not getattr(defender, "_untouchable_used", False)
                and not defender.incapacitated()
            ):
                defender._untouchable_used = True
                reroll_dodge = defender.dodge_chance(self) > random.random()
                reroll_hit = (hit_per if not hit else 1.0) > random.random()
                weapon_dam_str += f"{defender.name}'s Untouchable rerolls the attack.\n"
                if reroll_dodge or not reroll_hit:
                    hits[i] = False
                    self._reset_maelstrom()
                    if reroll_dodge:
                        dodge_message, dodge_aborted = self._handle_dodge(
                            defender,
                            damage,
                            typ,
                        )
                        weapon_dam_str += dodge_message
                        if dodge_aborted:
                            return weapon_dam_str, any(hits), max(crits)
                    else:
                        weapon_dam_str += (
                            f"{self.name} {typ} {defender.name} but misses entirely.\n"
                        )
                    continue
                damage, parry_message, parried, aborted = self._apply_parry(
                    defender,
                    damage,
                )
                weapon_dam_str += parry_message
            if parried and damage <= 0:
                hits[i] = False
                self._reset_maelstrom()
            if aborted:
                return weapon_dam_str, any(hits), max(crits)
            if not hits[i]:
                continue

            # --- Phase 3: Critical hit event ---
            if crits[i] > 1:
                self._emit_crit_event(defender, crits[i])
                footpad.record_live_and_learn(defender)
                self._reset_maelstrom()
                weapon_dam_str += ability_mechanics.trigger_zephyrstrike(self)

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
                damage, msg = self._apply_damage_reduction(defender, damage, att, ignore)
                weapon_dam_str += msg
                if crits[i] > 1:
                    damage, msg = healer.delay_critical_damage(defender, damage)
                    weapon_dam_str += msg
                release = healer.meditation_release(self)
                if release:
                    damage += release
                    weapon_dam_str += f"{self.name} releases {release} stored meditation damage.\n"
            # --- Phase 6: Apply damage and on-hit effects ---
            if damage > 0:
                mark = getattr(defender, "_reavers_mark", None)
                if isinstance(mark, dict) and int(mark.get("turns", 0) or 0) > 0:
                    damage = int(damage * (1.0 + float(mark.get("bonus", 0.0) or 0.0)))
                    weapon_dam_str += f"Reaver's Mark bites into {defender.name}.\n"
                brace = getattr(defender, "_brace_art", None)
                if isinstance(brace, dict) and int(brace.get("turns", 0) or 0) > 0:
                    reduction = max(0.0, min(0.75, float(brace.get("reduction", 0.0) or 0.0)))
                    blocked = int(damage * reduction)
                    damage = max(0, damage - blocked)
                    try:
                        delattr(defender, "_brace_art")
                    except AttributeError:
                        pass
                    weapon_dam_str += f"{defender.name}'s Brace absorbs {blocked} damage.\n"
                    if damage > 0 and defender.is_alive() and self.is_alive():
                        counter_mod = max(0.1, float(brace.get("counter", 0.45) or 0.45))
                        counter, _counter_hit, _counter_crit = defender.weapon_damage(
                            self,
                            dmg_mod=counter_mod,
                            cover=False,
                            use_offhand=False,
                        )
                        weapon_dam_str += counter
                # Half Orc racial virtue: reduced critical damage taken (weapon crits only).
                try:
                    if (
                        crits[i] > 1
                        and getattr(getattr(defender, "race", None), "name", None) == "Half Orc"
                    ):
                        damage = max(0, int(damage * HALF_ORC_CRIT_DAMAGE_TAKEN_MULTIPLIER))
                except Exception:
                    pass
                if damage > 0:
                    try:
                        from ..classes import promotion_kits

                        damage, msg, fully_absorbed = promotion_kits.absorb_novel_shield(
                            defender,
                            damage,
                            source="weapon",
                        )
                        weapon_dam_str += msg
                        if fully_absorbed:
                            hits[i] = False
                            self._reset_maelstrom()
                            if _class_name(self) == "Dragoon" and self.power_up:
                                self.class_effects["Power Up"].active = False
                                self.class_effects["Power Up"].duration = 0
                            continue
                    except Exception:
                        pass
                damage, temporary_health_message = defender._apply_temporary_health(
                    defender,
                    damage,
                )
                weapon_dam_str += temporary_health_message
                lethal_msg = ""
                try:
                    from ..classes import paladin

                    lethal_msg = paladin.mercy_lethal_message(defender, damage)
                except Exception:
                    pass
                if lethal_msg:
                    weapon_dam_str += lethal_msg
                else:
                    final_msg, stabilized = ability_mechanics.final_assault_response(
                        defender, self, damage
                    )
                    if final_msg:
                        weapon_dam_str += final_msg
                    if stabilized:
                        hits[i] = True
                        continue
                    defender.health.current -= damage
                    self._last_weapon_primary_damage += damage
                    self._last_weapon_primary_damage_instances.append(damage)
                    weapon_dam_str += self._build_damage_message(
                        defender, damage, typ, crits[i], att
                    )
                    try:
                        from ..classes import mage_mechanics

                        if not electrified_triggered:
                            retaliation = mage_mechanics.electrified_retaliation(
                                self, defender, damage
                            )
                            weapon_dam_str += retaliation
                            electrified_triggered = bool(retaliation)
                    except Exception:
                        pass
                    riposte = getattr(defender, "_riposte_line", None)
                    if (
                        isinstance(riposte, dict)
                        and int(riposte.get("turns", 0) or 0) > 0
                        and defender.is_alive()
                        and self.is_alive()
                    ):
                        try:
                            delattr(defender, "_riposte_line")
                        except AttributeError:
                            pass
                        counter, _counter_hit, _counter_crit = defender.weapon_damage(
                            self,
                            dmg_mod=max(0.1, float(riposte.get("multiplier", 0.45) or 0.45)),
                            crit=int(riposte.get("crit", 1) or 1),
                            cover=False,
                            use_offhand=False,
                        )
                        weapon_dam_str += f"{defender.name} answers with Riposte Line.\n"
                        weapon_dam_str += counter
                    if hasattr(self, "record_grandmaster_weapon_hit"):
                        before_rank, after_rank, discipline_xp = self.record_grandmaster_weapon_hit(
                            weapon_type,
                            defender,
                            reason="crit" if crits[i] > 1 else "hit",
                        )
                        weapon_dam_str += grandmaster.discipline_xp_text(
                            self,
                            weapon_type,
                            discipline_xp,
                            before_rank,
                            after_rank,
                        )
                    weapon_dam_str += self._apply_on_hit_effects(
                        defender,
                        damage,
                        crits[i],
                        att,
                        damage_type_override=damage_type_override,
                    )
                    weapon_dam_str += grandmaster.apply_weapon_technique(
                        self, defender, weapon_type
                    )
                # Evasive Guard: build stacks when you get hit; capped at 3.
                # This encourages "stay in the fight" play without altering race resistances.
                if "Evasive Guard" in defender.spellbook.get("Skills", {}):
                    defender.evasive_guard_stacks = min(
                        3, int(getattr(defender, "evasive_guard_stacks", 0)) + 1
                    )
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
                defender.health.current -= (
                    damage  # 0 damage still needs to be "applied" for consistency
                )
                weapon_dam_str += f"{self.name} {typ} {defender.name} but deals no damage.\n"
                hits[i] = False
                self._reset_maelstrom()

            # --- Phase 7: Equipment special effects on successful hit ---
            if hits[i]:
                weapon_dam_str += self._apply_equipment_effects(defender, att, damage, crits[i])
                toxin_result = footpad.apply_coated_toxin(self, defender, att, crits[i] > 1)
                weapon_dam_str += toxin_result.message
                if _class_name(self) == "Dragoon" and self.power_up:
                    self.class_effects["Power Up"].active = True
                    self.class_effects["Power Up"].duration += 1
            else:
                if _class_name(self) == "Dragoon" and self.power_up:
                    self.class_effects["Power Up"].active = False
                    self.class_effects["Power Up"].duration = 0

        if basic_attack:
            drained = footpad.drain_basic_attack_mana(
                self,
                defender,
                self._last_weapon_primary_damage,
            )
            if drained:
                weapon_dam_str += f"Mana Depletion drains {drained} MP from {defender.name}.\n"
        if self._surprise_attack and not defender.is_alive():
            defender._surprise_bonus_experience = True
        try:
            from ..classes import promotion_kits

            choice = str(promotion_kits.combat_state(self).get("action_choice") or "")
            if choice not in promotion_kits.RISKY_LUCK_ACTIONS:
                weapon_dam_str += promotion_kits.record_luck_roll(
                    self,
                    any(hits),
                    "attack",
                )
        except Exception:
            pass
        try:
            from ..classes import promotion_kits

            weapon_dam_str += promotion_kits.finish_revelation_payoff(
                self,
                defender,
                hit=any(hits),
            )
        except Exception:
            pass
        self._surprise_attack = False
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
        """Handle a normal dodge independently of Parry."""
        from ..classes import footpad

        # Evasive Guard stacks reset whenever the defender successfully dodges.
        if "Evasive Guard" in defender.spellbook.get("Skills", {}):
            defender.evasive_guard_stacks = 0
        try:
            from ..events.event_bus import get_event_bus, create_combat_event, EventType

            get_event_bus().emit(
                create_combat_event(EventType.DODGE, actor=defender, target=self, damage=damage)
            )
        except Exception:
            pass
        ghost = footpad.restore_ghost_step(defender)
        try:
            from ..classes import promotion_kits

            ghost += promotion_kits.record_ki_reaction(defender, "successful dodge")
            ghost += promotion_kits.record_rope_a_dope_dodge(defender, self)
            ghost += promotion_kits.add_aspect(defender, "Stone", incoming=True)
            ghost += promotion_kits.record_luck_roll(
                defender,
                True,
                "dodge",
                incoming=True,
            )
        except Exception:
            pass
        return f"{defender.name} evades {self.name}'s attack.\n" + ghost, False

    def _apply_parry(self, defender: Character, damage: int) -> tuple[int, str, bool, bool]:
        """Attempt a shield-incompatible melee deflection and optional Riposte."""
        from ..classes import ability_mechanics, footpad, grandmaster

        skills = getattr(defender, "spellbook", {}).get("Skills", {})
        offhand = getattr(defender, "equipment", {}).get("OffHand")
        if "Parry" not in skills or getattr(offhand, "subtyp", None) == "Shield":
            return damage, "", False, False
        dex = int(getattr(defender.stats, "dex", 10))
        chance = max(0.10, min(0.85, 0.25 + (dex - 10) * 0.03))
        chance = min(
            0.95,
            chance
            + ability_mechanics.posturing_parry_bonus(defender)
            + ability_mechanics.retort_parry_bonus(defender)
            + grandmaster.adaptive_arsenal_parry_bonus(defender)
            + footpad.main_gauche_parry_bonus(defender),
        )
        if random.random() >= chance:
            return damage, "", False, False
        self._last_attack_parried = True
        deflect_ratio = 1.0 if random.random() < 0.20 else random.uniform(0.50, 0.85)
        deflected = max(1, int(damage * deflect_ratio))
        remaining = max(0, damage - deflected)
        msg = f"{defender.name} parries and deflects {deflected} damage.\n"
        msg += footpad.restore_ghost_step(defender)
        try:
            from ..classes import promotion_kits

            msg += promotion_kits.record_ki_reaction(defender, "successful parry")
            msg += promotion_kits.add_aspect(defender, "Stone", incoming=True)
            msg += promotion_kits.record_luck_roll(
                defender,
                True,
                "parry",
                incoming=True,
            )
        except Exception:
            pass
        riposte_chance = min(0.80, 0.20 + max(0, dex - 10) * 0.02)
        if "Riposte" not in skills or random.random() >= riposte_chance:
            return remaining, msg, True, False
        counter_crit = (
            2 if random.random() < grandmaster.adaptive_arsenal_counter_crit_chance(defender) else 1
        )
        arcane_riposte = "Arcane Riposte" in skills
        if arcane_riposte:
            from ..classes import promotion_kits

            arcane_riposte = promotion_kits.weave_release_available(defender)
        shadow_counter = "Shadow Counter" in skills
        counter, _, _ = defender.weapon_damage(
            self,
            dmg_mod=1.25 if shadow_counter else 1.0,
            crit=counter_crit,
            hit=arcane_riposte,
            use_offhand=False,
            counterattack=True,
            accuracy_modifier=0.20 if shadow_counter else 0.0,
        )
        msg += f"{defender.name} ripostes!\n"
        if arcane_riposte:
            msg += f"{defender.name}'s Arcane Riposte releases the stored weave.\n"
        msg += counter
        return remaining, msg, True, not self.is_alive()

    def consume_mirror_image(self, attacker: Character, rng=None, luck_factor: int = 15) -> bool:
        """Return whether an incoming hit consumes one active mirror image."""
        effect = self.magic_effects.get("Duplicates")
        if not effect or not effect.active:
            return False

        try:
            image_count = int(effect.duration)
        except (TypeError, ValueError):
            image_count = 0
        if image_count <= 0:
            effect.active = False
            effect.duration = 0
            return False

        try:
            luck_mod = int(attacker.check_mod("luck", enemy=self, luck_factor=luck_factor))
        except Exception:
            luck_mod = 0
        effective_images = max(1, image_count - luck_mod)
        roller = rng or random
        if not roller.randint(0, effective_images):
            return False

        effect.duration = max(0, image_count - 1)
        if effect.duration <= 0:
            effect.active = False
            effect.duration = 0
        return True

    def _handle_duplicates(self, defender: Character, typ: str) -> tuple[bool, str]:
        """
        Check if the attack hits a mirror-image duplicate.

        Returns:
            (still_hit, message)
        """
        if defender.consume_mirror_image(self):
            self._reset_maelstrom()
            msg = (
                f"{self.name} {typ} at {defender.name} but hits a mirror image and it "
                f"vanishes from existence.\n"
            )
            return False, msg
        return True, ""

    def _emit_crit_event(self, defender: Character, crit_mult: int) -> None:
        """Emit a CRITICAL_HIT event."""
        try:
            from ..events.event_bus import get_event_bus, create_combat_event, EventType

            event_bus = get_event_bus()
            event_bus.emit(
                create_combat_event(
                    EventType.CRITICAL_HIT, actor=self, target=defender, multiplier=crit_mult
                )
            )
        except Exception:
            pass

    def _weapon_event_metadata(self, slot: str) -> dict[str, str]:
        """Return presentation/audio metadata for the equipped attack source."""
        weapon = self.equipment.get(slot)
        if weapon is None:
            return {
                "source": "weapon_damage",
                "attack_source": "weapon",
                "weapon_slot": slot,
            }
        weapon_type = str(getattr(weapon, "subtyp", "") or "")
        return {
            "source": "weapon_damage",
            "attack_source": "natural_weapon" if weapon_type == "Natural" else "weapon",
            "weapon_name": str(getattr(weapon, "name", "") or ""),
            "weapon_slot": slot,
            "weapon_type": weapon_type,
        }
