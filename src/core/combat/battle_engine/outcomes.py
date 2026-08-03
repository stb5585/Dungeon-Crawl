"""Battle victory, defeat, reward, and trial resolution."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ... import items, thieves_guild
from ...classes import berserker, class_rings, dragoon, grandmaster, lycan, paladin, promotion_kits
from ...enemies.identity import restore_defeat_identity

if TYPE_CHECKING:
    from ...character import Character


class BattleOutcomeMixin:
    def _process_victory(self) -> str:
        """Handle victory bookkeeping: exp, loot, quests, kill tracking."""
        restore_defeat_identity(self.enemy)
        if getattr(self.enemy, "paladin_repelled", False):
            self.player.state = "normal"
            if (
                hasattr(self.player, "transform_type")
                and self.player.cls != self.player.transform_type
            ):
                self.player.transform(back=True)
            self.player.effects(end=True)
            self.enemy.effects(end=True)
            msg = f"{self.enemy.name} flees from the battle.\n"
            msg += promotion_kits.end_combat(
                self.player,
                victory=False,
                enemy=self.enemy,
            )
            return msg
        if getattr(self.enemy, "tamed_by_player", False) or getattr(self.enemy, "no_victory_rewards", False):
            self.player.state = 'normal'
            if hasattr(self.player, 'transform_type') and self.player.cls != self.player.transform_type:
                self.player.transform(back=True)
            self.player.effects(end=True)
            msg = f"{self.enemy.name} leaves the fight as a companion.\n"
            msg += promotion_kits.end_combat(self.player, victory=False, enemy=self.enemy)
            return msg

        mercy = bool(getattr(self.enemy, "paladin_mercy_victory", False))
        exp_gain = int(self.enemy.experience)
        try:
            exp_gain = max(0, int(exp_gain * float(self.player.exp_gain_multiplier())))
        except Exception:
            pass
        msg = dragoon.red_dragon_victory_text(self.enemy)
        msg += f"{self.player.name} gained {exp_gain} experience.\n"

        # Handle summon experience
        if self.summon:
            try:
                self.player._active_summon_bond_level_span_xp = promotion_kits.summon_level_span_xp(self.summon)
            except Exception:
                pass
            self.summon.effects(end=True)
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
            if self.enemy.enemy_typ not in self.player.kill_dict:
                self.player.kill_dict[self.enemy.enemy_typ] = {}
            if self.enemy.name not in self.player.kill_dict[self.enemy.enemy_typ]:
                self.player.kill_dict[self.enemy.enemy_typ][self.enemy.name] = 0
            self.player.kill_dict[self.enemy.enemy_typ][self.enemy.name] += 1
            if hasattr(self.player, "record_enemy_defeat"):
                self.player.record_enemy_defeat()
            if hasattr(self.player, "refresh_demonologist_contracts"):
                self.player.refresh_demonologist_contracts()

            vow_text = paladin.on_enemy_defeated(
                self.player,
                self.enemy,
                bounty_target=self._enemy_is_active_bounty(),
                mercy=False,
            )
            if vow_text:
                msg += vow_text

            _scar_gained, scar_text = berserker.record_battle_scar(self.player)
            if scar_text:
                msg += scar_text
            class_rings.record_soul_harvest(self.player, getattr(self.enemy, "enemy_typ", None))
            msg += promotion_kits.end_combat(self.player, victory=True, enemy=self.enemy, exp_gain=exp_gain, boss=self.boss)
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
            if getattr(self.enemy, "windswept_ejected", False):
                msg += f"{self.enemy.name} is too far away to loot.\n"
            else:
                loot_msg = self.player.loot(self.enemy, self.tile)
                if loot_msg:
                    msg += loot_msg

            # Quest progress
            quest_msg = self.player.quests(enemy=self.enemy)
            if quest_msg:
                msg += quest_msg

        # Clear effects
        self.player.state = 'normal'
        if hasattr(self.player, 'transform_type') and self.player.cls != self.player.transform_type:
            self.player.transform(back=True)
        self.player.effects(end=True)

        # Experience growth uses permanent post-transformation stats.
        from ...progression import award_experience

        level_result = award_experience(self.player, exp_gain)
        self.player._pending_level_up_result = (
            level_result
            if level_result.new_level > level_result.old_level
            else None
        )
        if hasattr(self.player, "award_grandmaster_victory_xp"):
            msg += self._grandmaster_victory_xp_text()

        return msg

    def _grandmaster_victory_xp_text(self) -> str:
        if not hasattr(self.player, "award_grandmaster_victory_xp"):
            return ""
        text = ""
        for weapon_type, (before, after, amount) in self.player.award_grandmaster_victory_xp(self.enemy).items():
            text += grandmaster.discipline_xp_text(
                self.player,
                weapon_type,
                amount,
                before,
                after,
            )
        return text

    @staticmethod
    @staticmethod
    def _summon_experience_text(summon: Character, exp_gain: int) -> str:
        level = getattr(summon, "level", None)
        if getattr(level, "level", 1) >= 10:
            return f"{summon.name} gained {exp_gain} experience (MAX level).\n"
        return f"{summon.name} gained {exp_gain} experience.\n"

    def _award_mercy_gold(self) -> str:
        gold = max(0, int(getattr(self.enemy, "gold", 0) or 0))
        if not gold:
            return ""
        try:
            gold = max(0, int(gold * paladin.redemption_reward_multiplier(self.player)))
        except Exception:
            pass
        self.player.gold += gold
        return f"{self.enemy.name} offers {gold} gold in restitution.\n"

    def _enemy_is_active_bounty(self) -> bool:
        try:
            bounties = self.player.quest_dict.get("Bounty", {})
            if not isinstance(bounties, dict):
                return False
            return self.enemy.name in bounties or any(
                getattr(data.get("enemy", None), "name", None) == self.enemy.name
                for data in bounties.values()
                if isinstance(data, dict)
            )
        except Exception:
            return False

    def _process_grandmaster_trial_victory(self) -> str:
        """Handle Secret Master trial victory without normal combat rewards."""
        self.player.state = 'normal'
        if hasattr(self.player, 'transform_type') and self.player.cls != self.player.transform_type:
            self.player.transform(back=True)
        self.player.effects(end=True)
        self.enemy.effects(end=True)

        msg = "You complete this Secret Master bout.\n"
        msg += self._grandmaster_victory_xp_text()
        return msg

    def _process_class_ring_trial_victory(self) -> str:
        """Handle legacy Class Ring trial victory without normal combat rewards."""
        self.player.state = 'normal'
        if hasattr(self.player, 'transform_type') and self.player.cls != self.player.transform_type:
            self.player.transform(back=True)
        self.player.effects(end=True)
        self.enemy.effects(end=True)
        return f"You complete the {self._class_ring_trial_name()}.\n"

    def _process_thieves_guild_trial_victory(self) -> str:
        """Handle Thieves Guild initiation victory without normal combat rewards."""
        self.player.state = 'normal'
        if hasattr(self.player, 'transform_type') and self.player.cls != self.player.transform_type:
            self.player.transform(back=True)
        self.player.effects(end=True)
        self.enemy.effects(end=True)
        if not thieves_guild.has_signet(self.player):
            self.player.modify_inventory(items.ThievesGuildSignet(), rare=True)
        return f"You complete the {self._thieves_guild_trial_name()} and recover the Thieves Guild Signet.\n"

    def _process_class_ring_trial_defeat(self) -> None:
        """Handle Class Ring trial defeat without normal death rules."""
        self.player.state = 'normal'
        if hasattr(self.player, 'transform_type') and self.player.cls != self.player.transform_type:
            self.player.transform(back=True)
        self.player.effects(end=True)
        if hasattr(self.player, "_grandmaster_battle_hit_types"):
            self.player._grandmaster_battle_hit_types.clear()
        self.player.health.current = max(1, self.player.health.current)
        self.enemy.effects(end=True)
        self.enemy.health.current = self.enemy.health.max
        self.enemy.mana.current = self.enemy.mana.max

    def _process_defeat(self) -> None:
        """Handle defeat bookkeeping: reset enemy, player death."""
        self.player.state = 'normal'
        if hasattr(self.player, 'transform_type') and self.player.cls != self.player.transform_type:
            self.player.transform(back=True)
        self.player.effects(end=True)
        if hasattr(self.player, "_grandmaster_battle_hit_types"):
            self.player._grandmaster_battle_hit_types.clear()

        # Reset enemy for potential re-fight
        self.enemy.effects(end=True)
        self.enemy.health.current = self.enemy.health.max
        self.enemy.mana.current = self.enemy.mana.max

        self.player.death()
