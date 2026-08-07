"""Player familiar, transformation, combat-end, and special-power behavior."""

import random

from .. import abilities, enemies
from ..character import armor_resistance_modifier, armor_spell_modifier
from ..classes import (
    ability_mechanics,
    archdruid,
    bard,
    class_rings,
    lycan,
    paladin,
    promotion_kits,
    wizard,
)
from .persistence import load_char


class PlayerCombatMixin:
    def available_transform_forms(self) -> tuple[str, ...]:
        """Return the forms currently available to the permanent class."""
        class_name = (
            getattr(self, "_normal_class_name", "")
            if getattr(self, "_transformed", False)
            else getattr(getattr(self, "cls", None), "name", "")
        )
        if class_name != "Druid":
            return ()
        forms = ["Panther"]
        if int(getattr(getattr(self, "level", None), "pro_level", 1) or 1) >= 15:
            forms.append("Direbear")
        return tuple(forms)

    def select_transform_form(self, form_name: str) -> bool:
        """Select an unlocked Druid form without transforming immediately."""
        constructors = {
            "Panther": enemies.Panther,
            "Direbear": enemies.Direbear,
        }
        if form_name not in self.available_transform_forms():
            return False
        self.transform_type = constructors[form_name]()
        return True

    def familiar_turn(self, enemy):
        familiar_str = ""
        if self.familiar:
            special = None
            target = enemy
            if getattr(self.familiar, "spec", "") == "Tamed":
                command_text = ability_mechanics.resolve_tamed_companion_command(self, target)
                if command_text:
                    return command_text
                if not ability_mechanics.tamed_companion_should_auto_act(self):
                    return ""
                familiar_str += f"{self.familiar.name} attacks {target.name}.\n"
                attack_str, _hit, _crit = self.familiar.weapon_damage(target, dmg_mod=0.75)
                familiar_str += attack_str
                familiar_str += ability_mechanics.tamed_companion_special_turn(
                    self,
                    target,
                    hit=_hit,
                    crit=_crit,
                )
                return familiar_str

            if not random.randint(0, 3):
                if self.familiar.spec == "Defense":  # skills and spells
                    while True:
                        if not random.randint(0, 1):
                            special_list = list(self.familiar.spellbook['Spells'])
                            special_type = "Spells"
                        else:
                            special_list = list(self.familiar.spellbook['Skills'])
                            special_type = "Skills"
                        if len(special_list) == 1:
                            special = self.familiar.spellbook[special_type][special_list[0]]
                        else:
                            choice = random.choice(special_list)
                            special = self.familiar.spellbook[special_type][choice]
                        if special.name not in ['Resurrection', 'Cover']:
                            break
                if self.familiar.spec == "Support":  # just spells
                    target = self
                    if not random.randint(0, 4) and self.mana.current < self.mana.max:
                        mana_regen = int(self.mana.max * 0.05)
                        mana_regen = min(mana_regen, self.mana.max - self.mana.current)
                        self.mana.current += mana_regen
                        familiar_str += f"{self.familiar.name} restores {self.name}'s mana by {mana_regen}.\n"
                    else:
                        if self.health.current < self.health.max and random.randint(0, 1):
                            if random.randint(0, 1):
                                special = self.familiar.spellbook['Spells']['Heal']
                            else:
                                special = self.familiar.spellbook['Spells']["Regen"]
                        elif not self.stat_effects["Attack"].active:
                            special = self.familiar.spellbook['Spells']['Bless']
                        elif self.familiar.level.level > 1 and not self.magic_effects["Reflect"].active:
                            special = self.familiar.spellbook['Spells']["Reflect"]
                        elif self.familiar.level.level == 3 and random.randint(0, 1):
                            special = self.familiar.spellbook['Spells']['Cleanse']
                        else:
                            if random.randint(0, 1):
                                special = self.familiar.spellbook['Spells']['Heal']
                            else:
                                special = self.familiar.spellbook['Spells']["Regen"]
                if self.familiar.spec == "Arcane":  # just spells
                    spell_list = list(self.familiar.spellbook['Spells'])
                    choice = random.choice(spell_list)
                    if choice == "Boost" and not random.randint(0, 1) and not self.stat_effects["Magic"].active:
                        special = self.familiar.spellbook['Spells']['Boost']
                        target = self
                    else:
                        special = self.familiar.spellbook['Spells'][choice]
                if self.familiar.spec == "Luck":
                    if not random.randint(0, 1):
                        spell_list = list(self.familiar.spellbook['Spells'])
                        choice = random.choice(spell_list)
                        special = self.familiar.spellbook['Spells'][choice]
                    else:
                        while True:
                            skill_list = list(self.familiar.spellbook['Skills'])
                            choice = random.choice(skill_list)
                            if choice == 'Lockpick':
                                pass
                            else:
                                special = self.familiar.spellbook['Skills'][choice]
                                break
                if special is not None:
                    if special.typ == 'Skill':
                        familiar_str += f"{self.familiar.name} uses {special.name}.\n"
                        familiar_str += special.use(self, target=target, fam=True)
                    elif special.typ == 'Spell':
                        familiar_str += f"{self.familiar.name} casts {special.name}.\n"
                        familiar_str += special.cast(self, target=target, fam=True)
        return familiar_str

    def transform(self, back=False):
        transform_str = ""
        if back:
            try:
                player_char_dict = load_char(char=self)
                if player_char_dict is None:
                    # No tmp file exists (player never transformed or already reverted)
                    return ""
                health_diff = self.health.max - self.health.current
                mana_diff = self.mana.max - self.mana.current
                self.cls = player_char_dict.cls
                if self.is_alive():
                    self.health.current = max(1, player_char_dict.health.max - health_diff)
                self.health.max = player_char_dict.health.max
                self.mana.current = max(0, player_char_dict.mana.max - mana_diff)
                self.mana.max = player_char_dict.mana.max
                self.stats = player_char_dict.stats
                self.equipment = player_char_dict.equipment
                self.spellbook = player_char_dict.spellbook
                self.resistance = player_char_dict.resistance
                self.transform_type = player_char_dict.transform_type
                self._transformed = False
                transform_str = f"{self.name} transforms back into their normal self."
            except FileNotFoundError:
                pass
        else:
            self.save(tmp=True)
            self._normal_class_name = self.cls.name
            transform_str = f"{self.name} transforms into a {self.transform_type.name}."
            self.cls = self.transform_type
            self.health.current += self.transform_type.health.max
            self.health.max += self.transform_type.health.max
            self.mana.current += self.transform_type.mana.max
            self.mana.max += self.transform_type.mana.max
            self.stats.strength += self.transform_type.stats.strength
            self.stats.intel += self.transform_type.stats.intel
            self.stats.wisdom += self.transform_type.stats.wisdom
            self.stats.con += self.transform_type.stats.con
            self.stats.charisma += self.transform_type.stats.charisma
            self.stats.dex += self.transform_type.stats.dex
            self.equipment['Weapon'] = self.transform_type.equipment['Weapon']
            self.equipment['Armor'] = self.transform_type.equipment['Armor']
            self.equipment['OffHand'] = self.transform_type.equipment['OffHand']
            self.spellbook = self.transform_type.spellbook
            self.resistance = self.transform_type.resistance
            self._transformed = True
            if self.power_up:
                self.class_effects["Power Up"].active = True
                self.class_effects["Power Up"].duration = 1
        return transform_str

    def check_mod(self, mod, enemy=None, typ=None, luck_factor=1, ultimate=False, ignore=False):
        class_mod = 0
        berserk_per = int(self.status_effects["Berserk"].active) * 0.1  # berserk increases damage by 10%
        disarm_damage_multiplier = 0.5 if self.is_disarmed() else 1.0
        if self.cls.name == "Soulcatcher" and self.power_up:
            if enemy and getattr(enemy, "enemy_typ", None) in self.kill_dict:
                class_mod += (sum(self.kill_dict[enemy.enemy_typ].values()) // 20)
        class_mod += ability_mechanics.favored_enemy_bonus(self, enemy)
        if mod == 'weapon':
            weapon_mod = (self.equipment['Weapon'].damage * int(not self.is_disarmed()))
            class_mod += promotion_kits.xenid_caster_attribute_bonus(
                self,
                "strength",
            )
            if 'Monk' in self.cls.name:
                class_mod += self.stats.wisdom
            # Footpad-line weapon damage is DEX-forward.
            if self.cls.name in ["Footpad", "Thief", "Rogue", "Assassin", "Ninja"]:
                class_mod += self.stats.dex
            if self.cls.name in ['Spellblade', 'Knight Enchanter']:
                class_mod += weapon_mod * int(2 * (self.mana.current / self.mana.max))
            if self.cls.name == "Berserker" and self.power_up:
                class_mod += int(min(self.health.max / self.health.current, 10) * (self.player_level() // 11))
            if self.cls.name in ['Dragoon', "Shadowcaster"] and self.power_up:
                class_mod += weapon_mod * self.class_effects["Power Up"].active * self.class_effects["Power Up"].duration
            if self.cls.name == "Ninja" and self.power_up:
                class_mod += self.class_effects["Power Up"].active * self.class_effects["Power Up"].extra
            if self.cls.name == "Templar" and self.power_up and self.class_effects["Power Up"].active:
                class_mod += (self.player_level() // 5)
            if (
                self.cls.name == "Hierophant"
                and self.power_up
                and self.class_effects["Power Up"].active
                and self.equipment["Weapon"].subtyp == "Staff"
            ):
                class_mod += max(1, self.stats.wisdom // 3)
            if self.cls.name == "Lycan" and self.power_up:
                class_mod += ((self.player_level() // 10) * self.class_effects["Power Up"].duration)
            if 'Physical Damage' in self.equipment['Ring'].mod:
                weapon_mod += int(self.equipment['Ring'].mod.split(' ')[0])
            weapon_mod += self.stat_effects["Attack"].extra * self.stat_effects["Attack"].active
            total_mod = (weapon_mod + class_mod + self.combat.attack) * disarm_damage_multiplier
            total_mod *= class_rings.weapon_damage_multiplier(self)
            total_mod *= ability_mechanics.polearm_damage_multiplier(self)
            total_mod *= ability_mechanics.monkey_grip_damage_multiplier(self, "Weapon")
            total_mod *= 1 + ability_mechanics.drunken_brawler_damage_bonus(self)
            total_mod *= ability_mechanics.last_stand_attack_multiplier(self)
            total_mod *= 1 + bard.damage_bonus(self)
            total_mod *= ability_mechanics.arsenal_mastery_weapon_multiplier(self)
            total_mod *= ability_mechanics.pack_bond_multiplier(self)
            total_mod *= 1 + ability_mechanics.melody_inspiration_bonus(self)
            total_mod *= 1 + lycan.phase_damage_bonus(self) + lycan.frenzy_damage_bonus(self)
            total_mod *= paladin.conquest_damage_multiplier(self, enemy)
            total_mod *= promotion_kits.xenid_caster_multiplier(self, "melee")
            if (
                self.stat_effects["Attack"].active
                and self.stat_effects["Attack"].source == "Dishearten"
            ):
                total_mod *= 0.75
            return max(0, int(total_mod * (1 + berserk_per)))
        if mod == 'shield':
            if int(getattr(self, "_guard_suppressed", 0) or 0) > 0:
                return 0
            block_mod = 0
            if self.equipment['OffHand'] and self.equipment['OffHand'].subtyp == 'Shield':
                block_mod = round(self.equipment['OffHand'].mod * 100)
            if self.equipment['Ring'] and self.equipment['Ring'].mod == "Block":
                block_mod += 25
            block_mod += ability_mechanics.last_stand_block_bonus(self)
            block_mod += ability_mechanics.shield_mastery_block_bonus(self)
            try:
                from ..progression import has_talent

                if (
                    int(
                        promotion_kits.combat_state(self).get(
                            "hold_the_line",
                            0,
                        )
                        or 0
                    )
                    > 0
                ):
                    block_mod += 10
                    if has_talent(self, "sentinel.resolute-guard"):
                        block_mod += 5
            except Exception:
                pass
            return max(0, block_mod)
        if mod == 'offhand':
            if 'Monk' in self.cls.name:
                class_mod += self.stats.wisdom
            if self.cls.name in ['Spellblade', 'Knight Enchanter']:
                class_mod += (self.level.level + ((self.level.pro_level - 1) * 20)) * (self.mana.current / self.mana.max)
            if self.cls.name in ['Thief', 'Rogue', 'Assassin', 'Ninja', 'Druid', 'Lycan']:
                class_mod += (self.stats.dex // 2)
            try:
                class_mod += promotion_kits.xenid_caster_attribute_bonus(
                    self,
                    "strength",
                )
                off_mod = self.equipment['OffHand'].damage
                if self.equipment['Ring'] is not None and 'Physical Damage' in self.equipment['Ring'].mod:
                    off_mod += int(self.equipment['Ring'].mod.split(' ')[0])
                off_mod += self.stat_effects["Attack"].extra * self.stat_effects["Attack"].active
                total_offhand = (off_mod + class_mod + self.combat.attack) * (0.75 + berserk_per)
                total_offhand *= ability_mechanics.monkey_grip_damage_multiplier(self, "OffHand")
                total_offhand *= ability_mechanics.arsenal_mastery_weapon_multiplier(self)
                total_offhand *= ability_mechanics.pack_bond_multiplier(self)
                total_offhand *= promotion_kits.xenid_caster_multiplier(
                    self,
                    "melee",
                )
                if (
                    self.stat_effects["Attack"].active
                    and self.stat_effects["Attack"].source == "Dishearten"
                ):
                    total_offhand *= 0.75
                return max(0, int(total_offhand))
            except AttributeError:
                return 0
        if mod == 'armor':
            armor_mod = self.equipment['Armor'].armor
            helmet = self.equipment.get("Helmet")
            if helmet is not None and getattr(helmet, "subtyp", "None") != "None":
                armor_mod += getattr(helmet, "armor", 0)
            if self.cls.name == 'Knight Enchanter':
                class_mod += int(armor_mod * max(0, min(5, self.mana.max / (self.mana.current + 1))))
            if self.cls.name in ['Warlock', 'Shadowcaster']:
                if self.familiar and self.familiar.spec == 'Homunculus' and random.randint(0, 1) and self.familiar.level.pro_level > 1:
                    fam_mod = random.randint(0, 3) ** self.familiar.level.pro_level
                    class_mod += fam_mod
            if self.cls.name == "Berserker" and self.power_up and (self.health.current / self.health.max) < 0.3:
                class_mod += (self.player_level() // 11)
            if self.cls.name == 'Dragoon' and self.power_up:
                class_mod = armor_mod * self.class_effects["Power Up"].active * self.class_effects["Power Up"].duration
            if self.equipment['Ring'] is not None and 'Physical Defense' in self.equipment['Ring'].mod:
                armor_mod += int(self.equipment['Ring'].mod.split(' ')[0])
            armor_mod += self.stat_effects["Defense"].extra * self.stat_effects["Defense"].active
            class_mod += ability_mechanics.last_stand_defense_bonus(self)
            if archdruid.mastery_unlocked(self, "Stone"):
                class_mod += max(1, int((armor_mod + self.combat.defense) * 0.08))
            armor_total = ((armor_mod * int(not ignore)) + class_mod + self.combat.defense)
            armor_total *= class_rings.armor_multiplier(self)
            armor_total *= ability_mechanics.primal_ascendance_multiplier(self, "Stone")
            armor_total *= ability_mechanics.pack_bond_multiplier(self)
            armor_total *= promotion_kits.xenid_caster_multiplier(
                self,
                "armor",
            )
            armor_total *= 1 + ability_mechanics.melody_inspiration_bonus(self)
            if self.magic_effects.get("Tree of Life") and self.magic_effects["Tree of Life"].active:
                armor_total *= 1.75
            return max(0, int(armor_total))
        if mod == 'magic':
            conduit_intel = promotion_kits.xenid_caster_attribute_bonus(
                self,
                "intel",
            )
            magic_mod = int((self.stats.intel + conduit_intel) // 4) * self.level.pro_level
            if self.equipment['OffHand'] is not None and self.equipment['OffHand'].subtyp == 'Tome':
                magic_mod += self.equipment['OffHand'].mod
            if self.equipment['Weapon'] is not None and self.equipment['Weapon'].subtyp == 'Staff':
                magic_mod += int(self.equipment['Weapon'].damage * 0.75)
            magic_mod += armor_spell_modifier(self.equipment.get("Armor"))
            if self.equipment['Pendant'] is not None and 'Magic Damage' in self.equipment['Pendant'].mod:
                magic_mod += int(self.equipment['Pendant'].mod.split(' ')[0])
            magic_mod += self.stat_effects["Magic"].extra * self.stat_effects["Magic"].active
            if self.cls.name == "Shadowcaster" and self.class_effects["Power Up"].active:
                class_mod += magic_mod
            harmony = archdruid.harmony_bonus(self)
            if harmony:
                class_mod += int((magic_mod + self.combat.magic) * harmony)
            trickster = class_rings.arcane_trickster_magic_bonus(self)
            if trickster:
                class_mod += int((magic_mod + self.combat.magic) * trickster)
            gambit = ability_mechanics.tricksters_gambit_magic_bonus(self)
            if gambit:
                class_mod += int((magic_mod + self.combat.magic) * gambit)
            abyssal = ability_mechanics.abyssal_covenant_magic_bonus(self)
            if abyssal:
                class_mod += int((magic_mod + self.combat.magic) * abyssal)
            if ability_mechanics.power_up_active(self, "Sacred Overchannel", "Hierophant"):
                class_mod += int((magic_mod + self.combat.magic) * 0.15)
            astro = class_rings.constellation_bonus(self, typ)
            if astro:
                class_mod += int((magic_mod + self.combat.magic) * astro)
            affinity = wizard.affinity_damage_bonus(self, typ)
            if affinity:
                class_mod += int((magic_mod + self.combat.magic) * affinity)
            song = bard.damage_bonus(self)
            if song:
                class_mod += int((magic_mod + self.combat.magic) * song)
            total_magic = magic_mod + class_mod + self.combat.magic
            if typ in {"Poison", "Venom"}:
                total_magic = int(total_magic * ability_mechanics.primal_ascendance_multiplier(self, "Venom"))
            elif typ in {"Electric", "Wind", "Water"}:
                total_magic = int(total_magic * ability_mechanics.primal_ascendance_multiplier(self, "Storm"))
            total_magic = int(total_magic * (1 + ability_mechanics.melody_inspiration_bonus(self)))
            total_magic *= paladin.conquest_damage_multiplier(self, enemy)
            total_magic *= promotion_kits.xenid_caster_multiplier(
                self,
                "magic",
            )
            return max(0, int(total_magic))
        if mod == 'magic def':
            # Wisdom is the primary magic-defense stat; charisma provides a secondary
            # willpower component so low-CHA physical builds have a tangible downside.
            conduit_wisdom = promotion_kits.xenid_caster_attribute_bonus(
                self,
                "wisdom",
            )
            conduit_charisma = promotion_kits.xenid_caster_attribute_bonus(
                self,
                "charisma",
            )
            m_def_mod = (
                self.stats.wisdom
                + conduit_wisdom
                + ((self.stats.charisma + conduit_charisma) // 2)
            ) * self.level.pro_level
            if self.equipment['Pendant'] is not None and "Magic Defense" in self.equipment['Pendant'].mod:
                m_def_mod += int(self.equipment['Pendant'].mod.split(' ')[0])
            m_def_mod += self.stat_effects["Magic Defense"].extra * self.stat_effects["Magic Defense"].active
            total_magic_def = m_def_mod + class_mod + self.combat.magic_def
            try:
                from ..classes import nature_totems

                if nature_totems.active_totem_aspect(self) == "Water":
                    total_magic_def = int(total_magic_def * (1 + nature_totems.WATER_WARD_MAGIC_DEFENSE_BONUS))
            except Exception:
                pass
            total_magic_def = int(total_magic_def * ability_mechanics.primal_ascendance_multiplier(self, "Stone"))
            total_magic_def = int(total_magic_def * (1 + ability_mechanics.melody_inspiration_bonus(self)))
            if self.magic_effects.get("Tree of Life") and self.magic_effects["Tree of Life"].active:
                total_magic_def = int(total_magic_def * 1.75)
            total_magic_def = int(
                total_magic_def
                * promotion_kits.xenid_caster_multiplier(
                    self,
                    "magic_defense",
                )
            )
            return max(0, total_magic_def)
        if mod == 'heal':
            conduit_wisdom = promotion_kits.xenid_caster_attribute_bonus(
                self,
                "wisdom",
            )
            heal_mod = (self.stats.wisdom + conduit_wisdom) * self.level.pro_level
            if self.equipment['OffHand'] is not None and self.equipment['OffHand'].subtyp == 'Tome':
                heal_mod += self.equipment['OffHand'].mod
            elif self.equipment['Weapon'] is not None and self.equipment['Weapon'].subtyp == 'Staff':
                heal_mod += self.equipment['Weapon'].damage
            heal_mod += self.stat_effects["Magic"].extra * self.stat_effects["Magic"].active
            harmony = archdruid.harmony_bonus(self)
            if harmony:
                class_mod += int((heal_mod + self.combat.magic) * harmony)
            if ability_mechanics.power_up_active(self, "Sacred Overchannel", "Hierophant"):
                class_mod += int((heal_mod + self.combat.magic) * 0.15)
            total_heal = heal_mod + class_mod + self.combat.magic
            total_heal = int(total_heal * ability_mechanics.primal_ascendance_multiplier(self, "Growth"))
            total_heal = int(
                total_heal
                * promotion_kits.xenid_caster_multiplier(self, "healing")
            )
            return max(0, total_heal)
        if mod == 'resist':
            res_mod = 0
            if ultimate and typ == 'Physical':  # ultimate weapons bypass Physical resistance
                res_mod -= 1
            if typ in self.resistance:
                res_mod = self.resistance[typ]
            resist_effect = self.magic_effects.get(f"Resist {typ}")
            if resist_effect is not None and resist_effect.active:
                try:
                    res_mod += float(resist_effect.extra or 0)
                except (TypeError, ValueError):
                    pass
            if self.flying:
                if typ == 'Wind':
                    res_mod = -0.25
            if typ == "Fire" and self.magic_effects.get("Stone Skin") and self.magic_effects["Stone Skin"].active:
                res_mod += 0.5
            if self.cls.name in ['Warlock', 'Shadowcaster']:
                if self.familiar and self.familiar.spec == 'Mephit' and random.randint(0, 1) and self.familiar.level.pro_level > 1:
                    fam_mod = 0.25 * random.randint(1, max(1, self.stats.charisma // 10))
                    res_mod += fam_mod
            if self.equipment['Pendant'].mod.split("-")[-1] in [typ, "Elemental"] and \
                typ in ["Fire", "Ice", "Electric", "Water", "Earth", "Wind"]:
                if "Immune" in self.equipment['Pendant'].mod:
                    res_mod += 1
                elif "Resist" in self.equipment["Pendant"].mod:
                    res_mod += 0.5
            if self.equipment['OffHand'].name == "Svalinn" and typ == "Fire":
                res_mod += 0.25
            res_mod += armor_resistance_modifier(self.equipment.get("Armor"), typ)
            res_mod += armor_resistance_modifier(self.equipment.get("Helmet"), typ)
            if self.cls.name == "Archbishop" and self.class_effects["Power Up"].active:
                res_mod += 0.25
            if self.cls.name == "Astromancer" and self.class_effects["Power Up"].active and \
                    typ in ["Fire", "Water", "Wind", "Earth"]:
                res_mod += 0.5
            harmony = archdruid.harmony_bonus(self)
            if harmony:
                res_mod += harmony
            if typ == "Fire":
                res_mod += ability_mechanics.primal_ascendance_multiplier(self, "Stone") - 1.0
            res_mod += class_rings.constellation_bonus(self, typ)
            try:
                data = self.class_ring_awakening["data"]["Shadowcaster"]
                if self.cls.name == "Shadowcaster" and typ == "Holy" and int(data.get("eclipse_turns", 0) or 0) > 0:
                    penalty = 0.20 if getattr(getattr(self, "familiar", None), "spec", "") == "Defense" else 0.25
                    res_mod -= penalty
            except Exception:
                pass
            return res_mod
        if mod == 'luck':
            if self.cls.name == "Rogue" and self.power_up:
                luck_factor = max(1, luck_factor // 2)
            lf = max(1, int(luck_factor))
            base = int(self.stats.charisma) + int(self.stats.wisdom)
            return max(0, (base * 2) // lf)
        if mod == "speed":
            speed_mod = self.stats.dex
            speed_mod += self.stat_effects["Speed"].extra * self.stat_effects["Speed"].active
            speed_mod *= paladin.initiative_multiplier(self)
            speed_mod *= 1 + ability_mechanics.melody_inspiration_bonus(self)
            try:
                data = self.class_ring_awakening["data"]["Shadowcaster"]
                if self.cls.name == "Shadowcaster" and int(data.get("eclipse_turns", 0) or 0) > 0:
                    speed_mod *= 1.10
            except Exception:
                pass
            return int(speed_mod)
        return 0

    def special_power(self, game):
            """
            Player attains power up following quest to find the Power Core, used to give Golems life
            Each class has a unique combat ability or passive that is activated upon receiving the Power Core

            Berserker - Blood Rage(passive): attack increases as health decreases; if below 30% health, bonus to defense
            Crusader - Divine Aegis: create shell that absorbs damage and increases healing; if the shield survives
                the full duration, it will explode and deal holy damage to the enemy
            Dragoon - Draconic Onslaught(passive): attack and defense double for each successive hit; a miss resets this buff
            Stalwart Defender - Shield Mastery(passive): increase chance to block melee and spells, with a chance to deflect/reflect
            Wizard - Spell Mastery(passive): automatically triggers when no spells can be cast due to low mana; all spells
                become free for a short time and mana regens based on damage dealt
            Shadowcaster - Veil of Shadows(passive): become one with the darkness, making the player invisible to most enemies
                and making them harder to hit; increases damage of initial attack if first
            Demonologist - Abyssal Covenant: sacrifice health to empower spell damage and fiend contract scaling.
            Knight Enchanter - Arcane Blast: blast the enemy with a powerful attack, draining all remaining mana points; mana
                will regen in full over the next 4 turns (25% per turn)
            Thaumaturgist - Eternal Conduit (passive): The Thaumaturgist's bond with their Xenids shares a portion
                of healing and buffs in either direction.
            Rogue - Stroke of Luck(passive): the Rogue is incredibly lucky, gaining bonuses to all luck-based checks, including
                dodge and critical chance
            Seeker - Eyes of the Unseen(passive): gain increased awareness of battle situations, increasing critical chance as
                well as chance to dodge/parry attacks
            Ninja - Blade of Fatalities: sacrifice percentage of health to imbue blade with the spirit of Muramasa, increasing
                damage dealt and absorbing it into the user
            Arcane Trickster - Trickster's Gambit: stolen-magic momentum improves magic, critical chance, and dodge.
            Hierophant - Sacred Overchannel: open the staff-and-shield channel fully; staff and holy actions build
                Devotion faster, and Consecrated Conduit payoffs strike harder while returning more mana
            Templar - Holy Retribution: a radiant shield envelopes the Templar, reflecting damage back at the attacker; while
                the shield is active, attack damage and chance to dodge/parry increase
            Archbishop - Great Gospel: regens health and mana over time, and restores status; increases magic resistance and
                holy damage for duration
            Master Monk - Dim Mak: unleash a powerful attack that deals heavy damage and can either stun or in some cases
                kill the target; if the target is killed, the user will absorb the enemy's essence and will be regenerated by
                its max health and mana
            Troubadour - Melody of Inspiration (passive): The Troubadour's presence inspires allies and self, granting a small
                bonus to all stats and occasionally removing negative status effects at the start of combat.
            Archdruid - Primal Ascendance: temporarily gain bonuses from Growth, Venom, Storm, and Stone.
            Lycan - Lunar Frenzy(passive): the longer the Lycan is transformed, the further into madness they fall, increasing
                damage and regenerating health on critical hits; if the Lycan stays transformed for longer than 5 turns, they
                will be unable to transform back until after the battle
            Astromancer - Astral Judgment: call the current constellation's judgment, then spin the cycle
            Soulcatcher - Soul Harvest(passive): each enemy killed of a particular type will increase attack damage against
                that enemy type
            Beast Master - Pack Bond (passive): The Beast Master and their animal companion(s) share a deep bond, granting
                increased damage and defense when fighting alongside a companion. Occasionally, the companion will intercept
                attacks or provide a healing effect.
            """

            powerup_dict = {
                    "Berserker": abilities.BloodRage,
                    "Grandmaster of Arms": abilities.ArsenalMastery,
                    "Crusader": abilities.DivineAegis,
                    "Dragoon": abilities.DraconicOnslaught,
                    "Stalwart Defender": abilities.ShieldMastery,
                    "Wizard": abilities.SpellMastery,
                    "Shadowcaster": abilities.VeilShadows,
                    "Demonologist": abilities.AbyssalCovenant,
                    "Knight Enchanter": abilities.ArcaneBlast,
                    "Thaumaturgist": abilities.EternalConduit,
                    "Rogue": abilities.StrokeLuck,
                    "Seeker": abilities.EyesUnseen,
                    "Ninja": abilities.BladeFatalities,
                    "Arcane Trickster": abilities.TrickstersGambit,
                    "Hierophant": abilities.SacredOverchannel,
                    "Templar": abilities.HolyRetribution,
                    "Archbishop": abilities.GreatGospel,
                    "Master Monk": abilities.DimMak,
                    "Troubadour": abilities.MelodyInspiration,
                    "Archdruid": abilities.PrimalAscendance,
                    "Lycan": abilities.LunarFrenzy,
                    "Astromancer": abilities.AstralJudgment,
                    "Soulcatcher": abilities.SoulHarvest,
                    "Beast Master": abilities.PackBond
            }
            game.special_event("Power Up")
            skill = powerup_dict[self.cls.name]()
            self.spellbook['Skills'][skill.name] = skill
            self.power_up = True
            if self.cls.name == "Shadowcaster":
                    self.invisible = True
            return f"You gain the skill {skill.name}.\n"
