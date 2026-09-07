"""Battle victory, defeat, reward, and trial resolution."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ... import items, thieves_guild
from ...classes import (
    berserker,
    class_rings,
    dragoon,
    grandmaster,
    lycan,
    mage_mechanics,
    paladin,
    promotion_kits,
)
from ...enemies.identity import restore_defeat_identity
from ..encounter import EnemyResolution
from .models import EnemySettlement, LootAward

if TYPE_CHECKING:
    from ...character import Character


class BattleOutcomeMixin:
    def _warlock_soul_reward(self, enemy) -> str:
        """Award Soul Gems and temporary undead for marked death effects."""
        skills = self.player.spellbook.get("Skills", {})
        marked = isinstance(getattr(enemy, "soul_siphon", None), dict)
        doomed = bool(getattr(enemy.status_effects.get("Doom"), "active", False)) or (
            getattr(enemy, "_killed_by_ability", "") == "Doom"
        )
        messages = ""
        desouled = getattr(enemy, "_killed_by_ability", "") == "Desoul"
        if marked or (desouled and "Soul Asylum" in skills):
            self.player.modify_inventory(items.SoulGem())
            messages += f"{self.player.name} captures {enemy.name}'s soul in a Soul Gem.\n"
        if doomed and "Dance of the Dead" in skills:
            allies = getattr(self.player, "temporary_undead_allies", [])
            allies.append(
                {
                    "name": enemy.name,
                    "turns": 3,
                    "damage": max(1, int(getattr(enemy.combat, "attack", 1) * 0.5)),
                }
            )
            self.player.temporary_undead_allies = allies
            messages += f"{enemy.name} rises as a temporary undead ally.\n"
        return messages

    @staticmethod
    def _inventory_counts(player) -> dict[tuple[str, str], int]:
        """Snapshot acquired item counts by inventory destination and name."""
        counts = {}
        for destination, attribute in (
            ("normal", "inventory"),
            ("special", "special_inventory"),
        ):
            inventory = getattr(player, attribute, {}) or {}
            for item_name, stack in inventory.items():
                counts[(destination, str(item_name))] = len(stack)
        return counts

    @staticmethod
    def _inventory_awards(before, after) -> tuple[LootAward, ...]:
        """Return positive inventory changes in stable destination/name order."""
        return tuple(
            LootAward(
                item_name=name, quantity=after[key] - before.get(key, 0), destination=destination
            )
            for key in sorted(after, key=lambda value: (value[0], value[1]))
            for destination, name in (key,)
            if after[key] > before.get(key, 0)
        )

    def _process_victory(self) -> str:
        """Handle victory bookkeeping: exp, loot, quests, kill tracking."""
        enemy = self.encounter.primary_enemy
        restore_defeat_identity(enemy)
        if getattr(enemy, "paladin_repelled", False):
            self.player.state = "normal"
            self.player.effects(end=True)
            enemy.effects(end=True)
            msg = f"{enemy.name} flees from the battle.\n"
            msg += promotion_kits.end_combat(
                self.player,
                victory=False,
                enemy=enemy,
            )
            return msg
        if getattr(enemy, "tamed_by_player", False) or getattr(enemy, "no_victory_rewards", False):
            self.player.state = "normal"
            self.player.effects(end=True)
            msg = f"{enemy.name} leaves the fight as a companion.\n"
            msg += promotion_kits.end_combat(self.player, victory=False, enemy=enemy)
            return msg

        mercy = bool(getattr(enemy, "paladin_mercy_victory", False))
        exp_gain = int(enemy.experience)
        try:
            exp_gain = max(0, int(exp_gain * float(self.player.exp_gain_multiplier())))
        except Exception:
            pass
        if bool(getattr(enemy, "_surprise_bonus_experience", False)):
            exp_gain = int(exp_gain * 1.5)
        msg = dragoon.red_dragon_victory_text(enemy)
        msg += f"{self.player.name} gained {exp_gain} experience.\n"

        familiar = getattr(self.player, "familiar", None)
        if familiar is not None and getattr(self.player, "_familiar_acted", False):
            gain = getattr(familiar, "gain_action_experience", None)
            if callable(gain):
                msg += gain(exp_gain)

        # Handle summon experience
        if self.summon:
            self.summon.effects(end=True)
            if getattr(getattr(self.player, "cls", None), "name", "") == "Thaumaturgist":
                msg += f"{self.summon.name}'s growth is driven by its conduit, " "not experience.\n"
            else:
                self.summon.level.exp += exp_gain
                if self.summon.level.level < 10:
                    self.summon.level.exp_to_gain -= exp_gain
                    while self.summon.level.exp_to_gain <= 0:
                        msg += self.summon.level_up(self.player)
                        if self.summon.level.level == 10:
                            break
                msg += self._summon_experience_text(self.summon, exp_gain)

        if mercy:
            msg += self._award_mercy_gold()
        else:
            # Kill tracking
            if enemy.enemy_typ not in self.player.kill_dict:
                self.player.kill_dict[enemy.enemy_typ] = {}
            if enemy.name not in self.player.kill_dict[enemy.enemy_typ]:
                self.player.kill_dict[enemy.enemy_typ][enemy.name] = 0
            self.player.kill_dict[enemy.enemy_typ][enemy.name] += 1
            if hasattr(self.player, "record_enemy_defeat"):
                self.player.record_enemy_defeat()
            mage_mechanics.record_last_enemy(self.player, enemy, boss=self.boss)
            if hasattr(self.player, "refresh_demonologist_contracts"):
                self.player.refresh_demonologist_contracts()
            msg += self._warlock_soul_reward(enemy)

            vow_text = paladin.on_enemy_defeated(
                self.player,
                enemy,
                bounty_target=self._enemy_is_active_bounty(),
                mercy=False,
            )
            if vow_text:
                msg += vow_text

            _scar_gained, scar_text = berserker.record_battle_scar(self.player)
            if scar_text:
                msg += scar_text
            class_rings.record_soul_harvest(self.player, getattr(enemy, "enemy_typ", None))
            msg += promotion_kits.end_combat(
                self.player, victory=True, enemy=enemy, exp_gain=exp_gain, boss=self.boss
            )
            try:
                from ...classes import demonologist

                if self.player.cls.name == "Demonologist":
                    msg += demonologist.cool_corruption(self.player, 2, "combat victory")
            except Exception:
                pass
            frenzy_triggered, frenzy_text = lycan.maybe_trigger_frenzy(self.player, reason="kill")
            if frenzy_triggered:
                msg += frenzy_text

            # Loot
            if getattr(enemy, "windswept_ejected", False):
                msg += f"{enemy.name} is too far away to loot.\n"
            else:
                loot_msg = self.player.loot(enemy, self.tile)
                if loot_msg:
                    msg += loot_msg
            bullion_gold = max(0, int(getattr(self.player, "bullionaire_bonus_gold", 0) or 0))
            if bullion_gold:
                self.player.gold += bullion_gold
                self.player.bullionaire_bonus_gold = 0
                msg += f"Bullionaire adds {bullion_gold} gold to the combat reward.\n"

            # Quest progress
            quest_msg = self.player.quests(enemy=enemy)
            if quest_msg:
                msg += quest_msg

        # Clear effects
        self.player.state = "normal"
        self.player.effects(end=True)

        # Experience growth uses permanent post-transformation stats.
        from ...progression import award_experience

        level_result = award_experience(self.player, exp_gain)
        self.player._pending_level_up_result = (
            level_result if level_result.new_level > level_result.old_level else None
        )
        if hasattr(self.player, "award_grandmaster_victory_xp"):
            msg += self._grandmaster_victory_xp_text()

        return msg

    def _grandmaster_victory_xp_text(self) -> str:
        return self._grandmaster_victory_xp_text_for(self.encounter.primary_enemy)

    @staticmethod
    @staticmethod
    def _summon_experience_text(summon: Character, exp_gain: int) -> str:
        level = getattr(summon, "level", None)
        if getattr(level, "level", 1) >= 10:
            return f"{summon.name} gained {exp_gain} experience (MAX level).\n"
        return f"{summon.name} gained {exp_gain} experience.\n"

    def _award_mercy_gold(self) -> str:
        enemy = self.encounter.primary_enemy
        gold = max(0, int(getattr(enemy, "gold", 0) or 0))
        if not gold:
            return ""
        try:
            gold = max(0, int(gold * paladin.redemption_reward_multiplier(self.player)))
        except Exception:
            pass
        self.player.gold += gold
        return f"{enemy.name} offers {gold} gold in restitution.\n"

    def _enemy_is_active_bounty(self) -> bool:
        return self._enemy_is_active_bounty_for(self.encounter.primary_enemy)

    def _enemy_is_active_bounty_for(self, enemy) -> bool:
        """Return whether one encounter member matches an active bounty."""
        try:
            bounties = self.player.quest_dict.get("Bounty", {})
            if not isinstance(bounties, dict):
                return False
            return enemy.name in bounties or any(
                getattr(data.get("enemy", None), "name", None) == enemy.name
                for data in bounties.values()
                if isinstance(data, dict)
            )
        except Exception:
            return False

    def _process_multi_victory(
        self,
    ) -> tuple[
        str,
        tuple[EnemySettlement, ...],
        int,
        bool,
        tuple[str, ...],
    ]:
        """Settle a completed multi-enemy ledger exactly once."""
        settlements = []
        total_exp = 0
        defeated_members = []
        multiplier = 1.0
        try:
            multiplier = float(self.player.exp_gain_multiplier())
        except Exception:
            pass

        for member in self.encounter.members:
            enemy = member.enemy
            resolution = member.resolution or EnemyResolution.ESCAPED
            restore_defeat_identity(enemy)
            exp_factor = {
                EnemyResolution.DEFEATED: 1.0,
                EnemyResolution.MERCY: 1.0,
                EnemyResolution.EJECTED: 0.5,
            }.get(resolution, 0.0)
            exp_gain = max(
                0,
                int(int(getattr(enemy, "experience", 0) or 0) * exp_factor * multiplier),
            )
            total_exp += exp_gain
            gold_before = int(getattr(self.player, "gold", 0) or 0)
            inventory_before = self._inventory_counts(self.player)
            member_message = ""
            loot_eligible = resolution == EnemyResolution.DEFEATED
            kill_credit = loot_eligible
            quest_credit = loot_eligible
            bounty_credit = loot_eligible and self._enemy_is_active_bounty_for(enemy)
            bestiary_credit = loot_eligible

            if resolution == EnemyResolution.DEFEATED:
                defeated_members.append(member)
                member_message += dragoon.red_dragon_victory_text(enemy)
                enemy_type = getattr(enemy, "enemy_typ", None)
                if enemy_type not in self.player.kill_dict:
                    self.player.kill_dict[enemy_type] = {}
                self.player.kill_dict[enemy_type][enemy.name] = (
                    self.player.kill_dict[enemy_type].get(enemy.name, 0) + 1
                )
                if hasattr(self.player, "record_enemy_defeat"):
                    self.player.record_enemy_defeat()
                mage_mechanics.record_last_enemy(
                    self.player,
                    enemy,
                    boss=bool(self.boss),
                )
                if hasattr(self.player, "refresh_demonologist_contracts"):
                    self.player.refresh_demonologist_contracts()
                member_message += self._warlock_soul_reward(enemy)
                vow_text = paladin.on_enemy_defeated(
                    self.player,
                    enemy,
                    bounty_target=bounty_credit,
                    mercy=False,
                )
                member_message += vow_text or ""
                class_rings.record_soul_harvest(
                    self.player,
                    enemy_type,
                )
                frenzy_triggered, frenzy_text = lycan.maybe_trigger_frenzy(
                    self.player,
                    reason="kill",
                )
                if frenzy_triggered:
                    member_message += frenzy_text
                loot_text = self.player.loot(enemy, self.tile)
                member_message += loot_text or ""
                quest_text = self.player.quests(enemy=enemy)
                member_message += quest_text or ""
            elif resolution == EnemyResolution.MERCY:
                gold = max(0, int(getattr(enemy, "gold", 0) or 0))
                try:
                    gold = max(
                        0,
                        int(gold * paladin.redemption_reward_multiplier(self.player)),
                    )
                except Exception:
                    pass
                self.player.gold += gold
                member_message += (
                    f"{member.display_label} offers {gold} gold in restitution.\n"
                    if gold
                    else f"{member.display_label} yields to mercy.\n"
                )
            elif resolution == EnemyResolution.TAMED:
                member_message += f"{member.display_label} leaves as a companion.\n"
            elif resolution == EnemyResolution.EJECTED:
                member_message += (
                    f"{member.display_label} was ejected and grants half experience only.\n"
                )
            else:
                member_message += f"{member.display_label} escaped the encounter.\n"

            if exp_gain:
                member_message = (
                    f"{member.display_label}: {exp_gain} experience.\n" + member_message
                )
            settlements.append(
                EnemySettlement(
                    combatant_id=member.combatant_id,
                    display_label=member.display_label,
                    resolution=resolution,
                    experience=exp_gain,
                    gold=max(0, int(self.player.gold) - gold_before),
                    loot_eligible=loot_eligible,
                    kill_credit=kill_credit,
                    bestiary_credit=bestiary_credit,
                    quest_credit=quest_credit,
                    bounty_credit=bounty_credit,
                    loot_awards=self._inventory_awards(
                        inventory_before,
                        self._inventory_counts(self.player),
                    ),
                    message=member_message,
                )
            )

        message = "".join(settlement.message for settlement in settlements)

        if self.summon:
            self.summon.effects(end=True)
            if getattr(getattr(self.player, "cls", None), "name", "") == "Thaumaturgist":
                message += (
                    f"{self.summon.name}'s growth is driven by its conduit, " "not experience.\n"
                )
            else:
                self.summon.level.exp += total_exp
                if self.summon.level.level < 10:
                    self.summon.level.exp_to_gain -= total_exp
                    while self.summon.level.exp_to_gain <= 0:
                        message += self.summon.level_up(self.player)
                        if self.summon.level.level == 10:
                            break
                message += self._summon_experience_text(self.summon, total_exp)

        if defeated_members:
            _scar_gained, scar_text = berserker.record_battle_scar(self.player)
            message += scar_text or ""
            representative = max(
                defeated_members,
                key=lambda member: (
                    int(getattr(getattr(member.enemy, "level", None), "pro_level", 0) or 0),
                    -member.slot,
                ),
            ).enemy
            for member in defeated_members:
                if member.enemy is representative or not self.show_enemy_details(member.enemy):
                    continue
                message += promotion_kits.gain_case_progress(
                    self.player,
                    getattr(member.enemy, "enemy_typ", None),
                    4,
                    "victory",
                )
            message += promotion_kits.end_combat(
                self.player,
                victory=True,
                enemy=representative,
                exp_gain=total_exp,
                boss=False,
            )
            try:
                from ...classes import demonologist

                if self.player.cls.name == "Demonologist":
                    message += demonologist.cool_corruption(
                        self.player,
                        2,
                        "combat victory",
                    )
            except Exception:
                pass
            message += self._grandmaster_victory_xp_text_for(representative)
        else:
            message += promotion_kits.end_combat(
                self.player,
                victory=False,
                enemy=self.encounter.primary_enemy,
            )

        self.player.state = "normal"
        self.player.effects(end=True)
        for member in self.encounter.members:
            member.enemy.effects(end=True)

        from ...progression import award_experience

        level_result = award_experience(self.player, total_exp)
        self.player._pending_level_up_result = (
            level_result if level_result.new_level > level_result.old_level else None
        )
        message += f"Encounter total: {total_exp} experience.\n"
        reward_fragments = (
            " experience.",
            " dropped ",
            " offers ",
            " yields to mercy",
            " leaves as a companion",
            " was ejected ",
            " escaped the encounter",
            "Encounter total:",
        )
        notices = tuple(
            line
            for line in message.splitlines()
            if line and not any(fragment in line for fragment in reward_fragments)
        )
        return (
            message,
            tuple(settlements),
            total_exp,
            level_result.new_level > level_result.old_level,
            notices,
        )

    def _grandmaster_victory_xp_text_for(self, enemy) -> str:
        """Award one Grandmaster victory roll using a representative enemy."""
        if not hasattr(self.player, "award_grandmaster_victory_xp"):
            return ""
        text = ""
        for weapon_type, (before, after, amount) in self.player.award_grandmaster_victory_xp(
            enemy
        ).items():
            text += grandmaster.discipline_xp_text(
                self.player,
                weapon_type,
                amount,
                before,
                after,
            )
        return text

    def _process_grandmaster_trial_victory(self) -> str:
        """Handle Secret Master trial victory without normal combat rewards."""
        self.player.state = "normal"
        self.player.effects(end=True)
        self.encounter.primary_enemy.effects(end=True)

        msg = "You complete this Secret Master bout.\n"
        msg += self._grandmaster_victory_xp_text()
        return msg

    def _process_class_ring_trial_victory(self) -> str:
        """Handle legacy Class Ring trial victory without normal combat rewards."""
        self.player.state = "normal"
        self.player.effects(end=True)
        self.encounter.primary_enemy.effects(end=True)
        return f"You complete the {self._class_ring_trial_name()}.\n"

    def _process_thieves_guild_trial_victory(self) -> str:
        """Handle Thieves Guild initiation victory without normal combat rewards."""
        self.player.state = "normal"
        self.player.effects(end=True)
        self.encounter.primary_enemy.effects(end=True)
        if not thieves_guild.has_signet(self.player):
            self.player.modify_inventory(items.ThievesGuildSignet(), rare=True)
        return f"You complete the {self._thieves_guild_trial_name()} and recover the Thieves Guild Signet.\n"

    def _process_class_ring_trial_defeat(self) -> None:
        """Handle Class Ring trial defeat without normal death rules."""
        self.player.state = "normal"
        self.player.effects(end=True)
        if hasattr(self.player, "_grandmaster_battle_hit_types"):
            self.player._grandmaster_battle_hit_types.clear()
        self.player.health.current = max(1, self.player.health.current)
        enemy = self.encounter.primary_enemy
        enemy.effects(end=True)
        enemy.health.current = enemy.health.max
        enemy.mana.current = enemy.mana.max

    def _process_defeat(self) -> None:
        """Handle defeat bookkeeping: reset enemy, player death."""
        from ... import curses

        curses.cure_curses(self.player)
        self.player.state = "normal"
        self.player.effects(end=True)
        if hasattr(self.player, "_grandmaster_battle_hit_types"):
            self.player._grandmaster_battle_hit_types.clear()

        # Reset enemy for potential re-fight
        enemy = self.encounter.primary_enemy
        enemy.effects(end=True)
        enemy.health.current = enemy.health.max
        enemy.mana.current = enemy.mana.max

        self.player.death()
