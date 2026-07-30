"""Character movement, inventory, modifiers, and fallback hooks."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from ..constants import BASE_FLEE_CHANCE, MAX_FLEE_CHANCE
from .models import _class_name, armor_resistance_modifier, armor_spell_modifier

if TYPE_CHECKING:
    from .core import Character


class CharacterUtilityMixin:
    def flee(self, enemy: Character, smoke: bool = False) -> tuple[bool, str]:
        blind = enemy.status_effects["Blind"].active
        success = False
        flee_message = f"{self.name} couldn't escape from the {enemy.name}."
        if smoke:
            if not enemy.sight or self.invisible:
                flee_message = f"{self.name} disappears in a cloud of smoke."
                self.state = 'normal'
                success = True
            else:
                flee_message = f"{enemy.name} is not fooled by cheap parlor tricks."
        else:
            chance = (self.check_mod('luck', enemy=enemy, luck_factor=10) + \
                (self.stat_effects["Speed"].active * self.stat_effects["Speed"].extra))
            chance = (chance / 100) + BASE_FLEE_CHANCE
            speed_factor = (self.check_mod("speed", enemy=enemy) - enemy.check_mod("speed", enemy=enemy)) / \
                (self.check_mod("speed", enemy=enemy) + enemy.check_mod("speed", enemy=enemy) + 1)
            pro_diff = self.level.pro_level / max(enemy.level.pro_level, 1)
            flee_chance = min(MAX_FLEE_CHANCE, chance + speed_factor * pro_diff)
            if random.random() < flee_chance or enemy.incapacitated() or blind:
                flee_message = f"{self.name} flees from the {enemy.name}."
                self.state = 'normal'
                success = True
        return success, flee_message

    def is_alive(self) -> bool:
        return self.health.current > 0

    def modify_inventory(self, item: object, num: int = 1, subtract: bool = False,
                         rare: bool = False, quest: bool = False, storage: bool = False) -> None:
        inventory = self.special_inventory if rare else self.inventory
        if subtract:
            for _ in range(num):
                inventory[item.name].pop(0)
                if storage:
                    if item.name not in self.storage:
                        self.storage[item.name] = []
                    self.storage[item.name].append(item)
            if not len(inventory[item.name]):
                del inventory[item.name]
        else:
            if item.name not in inventory:
                inventory[item.name] = []
            num = min(num, 99 - len(inventory[item.name]))
            for _ in range(num):
                inventory[item.name].append(item)
                if storage:
                    self.storage[item.name].pop(0)
                    if not len(self.storage[item.name]):
                        del self.storage[item.name]
        if quest:
            self.quests(item=item)

        # Update encumbered status for player characters
        if hasattr(self, 'max_weight'):
            self.encumbered = self.current_weight() > self.max_weight()

    def check_mod(self, mod: str, enemy: Character | None = None, typ: str | None = None,
                  luck_factor: int = 1, ultimate: bool = False, ignore: bool = False) -> int | float:
        class_mod = 0
        berserk_per = int(self.status_effects["Berserk"].active) * 0.1  # berserk increases damage by 10%
        disarm_damage_multiplier = 0.5 if self.is_disarmed() else 1.0

        # Totem bonus: +15% attack and defense when active (guard missing key)
        totem = self.magic_effects.get("Totem")
        totem_bonus = 1.15 if (totem and getattr(totem, "active", False)) else 1.0

        if mod == 'weapon':
            weapon_mod = (self.equipment['Weapon'].damage * int(not self.is_disarmed()))
            weapon_mod += self.stat_effects["Attack"].extra * self.stat_effects["Attack"].active
            total_mod = (weapon_mod + class_mod + self.combat.attack) * disarm_damage_multiplier
            return max(0, int(total_mod * (1 + berserk_per) * totem_bonus))
        if mod == 'shield':
            block_mod = 0
            if self.equipment['OffHand'].subtyp == 'Shield':
                block_mod = round(self.equipment['OffHand'].mod * (1 + ('Shield Block' in self.spellbook['Skills'])) * 100)
            if self.equipment['Ring'].mod == "Block":
                block_mod += 25
            return max(0, block_mod)
        if mod == 'offhand':
            try:
                off_mod = self.equipment['OffHand'].damage
                off_mod += self.stat_effects["Attack"].extra * self.stat_effects["Attack"].active
                return max(0, int((off_mod + class_mod + self.combat.attack) * (0.75 + berserk_per)))
            except AttributeError:
                return 0
        if mod == 'armor':
            armor_mod = self.equipment['Armor'].armor
            if self.turtle:
                class_mod += 99
            armor_mod += self.stat_effects["Defense"].extra * self.stat_effects["Defense"].active
            return max(0, int((armor_mod * int(not ignore)) + class_mod + self.combat.defense) * totem_bonus)
        if mod == 'magic':
            magic_mod = int(self.stats.intel // 4) * self.level.pro_level
            if self.equipment['OffHand'].subtyp == 'Tome':
                magic_mod += self.equipment['OffHand'].mod
            if self.equipment['Weapon'].subtyp == 'Staff':
                magic_mod += int(self.equipment['Weapon'].damage * 0.75)
            magic_mod += armor_spell_modifier(self.equipment.get("Armor"))
            magic_mod += self.stat_effects["Magic"].extra * self.stat_effects["Magic"].active
            return max(0, magic_mod + class_mod + self.combat.magic)
        if mod == 'magic def':
            # Wisdom is the primary magic-defense stat; charisma provides a secondary
            # willpower component so "dump CHA/WIS" has a tangible downside.
            m_def_mod = int(self.stats.wisdom) + (int(self.stats.charisma) // 2)
            if self.turtle:
                class_mod += 99
            m_def_mod += self.stat_effects["Magic Defense"].extra * self.stat_effects["Magic Defense"].active
            total_magic_def = m_def_mod + class_mod + self.combat.magic_def
            try:
                from src.core.classes import nature_totems

                if nature_totems.active_totem_aspect(self) == "Water":
                    total_magic_def = int(total_magic_def * (1 + nature_totems.WATER_WARD_MAGIC_DEFENSE_BONUS))
            except Exception:
                pass
            return max(0, total_magic_def)
        if mod == 'heal':
            heal_mod = self.stats.wisdom * self.level.pro_level
            if self.equipment['OffHand'].subtyp == 'Tome':
                heal_mod += self.equipment['OffHand'].mod
            elif self.equipment['Weapon'].subtyp == 'Staff':
                heal_mod += self.equipment['Weapon'].damage
            heal_mod += self.stat_effects["Magic"].extra * self.stat_effects["Magic"].active
            return max(0, heal_mod + class_mod + self.combat.magic)
        if mod == 'resist':
            if ultimate and typ == 'Physical':  # ultimate weapons bypass Physical resistance
                return -0.25
            res_mod = self.resistance.get(typ, 0)
            resist_effect = self.magic_effects.get(f"Resist {typ}")
            if resist_effect is not None and resist_effect.active:
                try:
                    res_mod += float(resist_effect.extra or 0)
                except (TypeError, ValueError):
                    pass
            res_mod += armor_resistance_modifier(self.equipment.get("Armor"), typ)
            res_mod += armor_resistance_modifier(self.equipment.get("Helmet"), typ)
            if self.flying:
                if typ == 'Wind':
                    res_mod = -0.25
            if typ == "Fire" and self.magic_effects.get("Stone Skin") and self.magic_effects["Stone Skin"].active:
                res_mod += 0.5
            try:
                data = self.class_ring_awakening["data"]["Shadowcaster"]
                if _class_name(self) == "Shadowcaster" and typ == "Holy" and int(data.get("eclipse_turns", 0) or 0) > 0:
                    penalty = 0.20 if getattr(getattr(self, "familiar", None), "spec", "") == "Defense" else 0.25
                    res_mod -= penalty
            except Exception:
                pass
            return res_mod
        if mod == 'luck':
            # "Luck" also acts as a general-purpose saving-throw modifier in many effects.
            # Include wisdom so low WIS/CHA builds pay a consistent penalty in combat.
            lf = max(1, int(luck_factor))
            base = int(self.stats.charisma) + int(self.stats.wisdom)
            return max(0, (base * 2) // lf)
        if mod == "speed":
            speed_mod = self.stats.dex
            speed_mod += self.stat_effects["Speed"].extra * self.stat_effects["Speed"].active
            try:
                data = self.class_ring_awakening["data"]["Shadowcaster"]
                if _class_name(self) == "Shadowcaster" and int(data.get("eclipse_turns", 0) or 0) > 0:
                    speed_mod = int(speed_mod * 1.10)
            except Exception:
                pass
            return speed_mod
        return 0

    def buff_str(self) -> str:
        buffs = []
        if self.equipment['Ring'].mod in ["Accuracy", "Dodge"]:
            buffs.append(self.equipment['Ring'].mod)
        if self.equipment['Pendant'].mod in \
            ["Vision", "Flying", "Invisible",
             "Magic Dodge",
             "Status-Poison", "Status-Berserk", "Status-Stone", "Status-Silence", "Status-Death", "Status-All"]:
            buffs.append(self.equipment['Pendant'].mod)
        if self.flying and "Flying" not in buffs:
            buffs.append("Flying")
        if self.invisible and "Invisible" not in buffs:
            buffs.append("Invisible")
        if self.sight and "Vision" not in buffs:
            buffs.append("Vision")
        if not buffs:
            buffs.append("None")
        return ", ".join(buffs)

    def level_up(self) -> None:
        raise NotImplementedError

    def special_attack(self, target: Character) -> str:
        raise NotImplementedError
