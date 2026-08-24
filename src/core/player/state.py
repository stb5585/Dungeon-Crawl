"""Player state normalization, class tracking, and gameplay records."""

from .. import main_story, thieves_guild
from ..classes import (
    ability_mechanics,
    archdruid,
    astromancer,
    bard,
    class_rings,
    demonologist,
    dragoon,
    grandmaster,
    lycan,
    mage_mechanics,
    paladin,
    promotion_kits,
    wizard,
)
from .stats import normalize_gameplay_stats


class PlayerStateMixin:
    def ensure_gameplay_stats(self):
        """Ensure gameplay statistics exist and include all supported counters."""
        self.gameplay_stats = normalize_gameplay_stats(
            getattr(self, "gameplay_stats", None),
            current_level=self.player_level(),
        )
        return self.gameplay_stats

    def ensure_grandmaster_discipline(self):
        """Normalize Grandmaster weapon-discipline state for current and legacy saves."""
        self.grandmaster_discipline = grandmaster.normalize_state(
            getattr(self, "grandmaster_discipline", None)
        )
        if not isinstance(getattr(self, "_grandmaster_battle_hit_types", None), set):
            self._grandmaster_battle_hit_types = set()
        grandmaster.sync_weapon_art_skills(self)
        return self.grandmaster_discipline

    def ensure_demonologist_contracts(self):
        """Normalize Demonologist contract state for current and legacy saves."""
        self.demonologist_contracts = demonologist.normalize_state(
            getattr(self, "demonologist_contracts", None)
        )
        if demonologist.is_demonologist(self):
            self.demonologist_contracts["crypt_unlocked"] = True
        return self.demonologist_contracts

    def ensure_archdruid_attunement(self):
        """Normalize Archdruid attunement state for current and legacy saves."""
        self.archdruid_attunement = archdruid.ensure_state(self)
        return self.archdruid_attunement

    def ensure_class_ring_awakening(self):
        """Normalize legacy Class Ring awakening state for current and legacy saves."""
        self.class_ring_awakening = class_rings.ensure_state(self)
        return self.class_ring_awakening

    def ensure_promotion_kit_state(self):
        """Normalize promotion class-kit progression state for current and legacy saves."""
        self.promotion_kit_state = promotion_kits.ensure_state(self)
        return self.promotion_kit_state

    def ensure_astromancer_state(self):
        """Normalize Diviner/Astromancer rune state for current and legacy saves."""
        self.astromancer_state = astromancer.ensure_state(self)
        return self.astromancer_state

    def ensure_paladin_vow(self):
        """Normalize Paladin vow state for current and legacy saves."""
        self.paladin_vow = paladin.ensure_state(self)
        if paladin.path(self):
            paladin.grant_signature_skill(self)
        return self.paladin_vow

    def ensure_dragoon_dragon_quest(self):
        """Normalize Dragoon dragon quest state for current and legacy saves."""
        self.dragoon_dragon_quest = dragoon.ensure_state(self)
        return self.dragoon_dragon_quest

    def ensure_bard_song(self):
        self.bard_song = bard.ensure_song_state(self)
        return self.bard_song

    def ensure_tamed_companion(self):
        self.tamed_companion = ability_mechanics.normalize_tamed_companion(
            getattr(self, "tamed_companion", None)
        )
        try:
            from .. import companions

            self.familiar = companions.tamed_companion_from_state(self.tamed_companion)
        except Exception:
            pass
        return self.tamed_companion

    def ensure_temporary_exploration_effects(self):
        self.temporary_exploration_effects = ability_mechanics.ensure_exploration_effects(self)
        return self.temporary_exploration_effects

    def ensure_lycan_state(self):
        self.lycan_state = lycan.ensure_state(self)
        return self.lycan_state

    def ensure_wizard_affinity(self):
        self.wizard_affinity = wizard.ensure_affinity(self)
        return self.wizard_affinity

    def ensure_main_story_state(self):
        """Normalize main-story progression state for current and legacy saves."""
        self.main_story = main_story.ensure_state(self)
        return self.main_story

    def ensure_thieves_guild_state(self):
        """Normalize Thieves Guild state for current and legacy saves."""
        self.thieves_guild = thieves_guild.ensure_state(self)
        return self.thieves_guild

    def can_enter_true_final(self):
        """Return whether the main-story route has unlocked Vesperion's true final."""
        return self.ensure_main_story_state().get("true_final_unlocked", False)

    def choose_paladin_vow(self, vow_path):
        """Permanently choose a Paladin vow path."""
        return paladin.choose_vow(self, vow_path)

    def awaken_class_ring(self, class_name=None, **kwargs):
        """Complete the current legacy Class Ring awakening helper."""
        return class_rings.activate(self, class_name, **kwargs)

    def refresh_demonologist_contracts(self) -> list[str]:
        """Unlock fiend contracts from recorded defeated enemies."""
        self.ensure_demonologist_contracts()
        return demonologist.refresh_unlocked_contracts(self)

    def record_grandmaster_weapon_hit(
        self,
        weapon_type: str | None,
        opponent=None,
        *,
        reason: str = "hit",
    ) -> tuple[int, int, int]:
        """Award per-hit discipline XP and remember the weapon type for victory XP."""
        self.ensure_grandmaster_discipline()
        before, after, amount = grandmaster.roll_discipline_xp(
            self,
            weapon_type,
            grandmaster.HIT_XP,
            opponent,
            reason=reason,
        )
        if weapon_type in grandmaster.WEAPON_TYPES:
            self._grandmaster_battle_hit_types.add(weapon_type)
        return before, after, amount

    def record_grandmaster_weapon_art(self, weapon_type: str | None, opponent=None) -> tuple[int, int, int]:
        """Award discipline insight for successfully landing a Weapon Art."""
        self.ensure_grandmaster_discipline()
        return grandmaster.roll_discipline_xp(
            self,
            weapon_type,
            grandmaster.ART_XP,
            opponent,
            reason="art",
        )

    def award_grandmaster_victory_xp(self, opponent=None) -> dict[str, tuple[int, int, int]]:
        """Award victory discipline XP to equipped weapon types used in this battle."""
        self.ensure_grandmaster_discipline()
        results = {}
        for weapon_type in sorted(self._grandmaster_battle_hit_types):
            if weapon_type in grandmaster.WEAPON_TYPES:
                before, after, amount = grandmaster.roll_discipline_xp(
                    self,
                    weapon_type,
                    grandmaster.VICTORY_XP,
                    opponent,
                    reason="victory",
                )
                if amount > 0:
                    results[weapon_type] = (before, after, amount)
        self._grandmaster_battle_hit_types.clear()
        grandmaster.sync_weapon_art_skills(self)
        return results

    def record_archdruid_status_applied(self, target, status_name: str) -> None:
        archdruid.record_status_applied(self, target, status_name)

    def record_archdruid_damage_dealt(self, amount: int, damage_type: str) -> None:
        archdruid.record_damage_dealt(self, amount, damage_type)

    def record_archdruid_damage_taken(self, amount: int, damage_type: str) -> None:
        archdruid.record_damage_taken(self, amount, damage_type)

    def record_archdruid_healing_done(self, amount: int) -> None:
        archdruid.record_healing_done(self, amount)

    def record_archdruid_life_drained(self) -> None:
        archdruid.record_life_drain(self)

    def record_step(self, steps=1):
        stats = self.ensure_gameplay_stats()
        step_count = max(0, int(steps))
        stats["steps_taken"] += step_count
        lycan.record_steps(self, step_count)
        bard.tick_exploration_song(self, step_count)
        ability_mechanics.tick_exploration_effects(self, step_count)
        mage_mechanics.tick_exploration(self, step_count)
        if int(getattr(self, "shadow_dungeon_darkness_steps", 0) or 0) > 0:
            self.shadow_dungeon_darkness_steps = max(
                0,
                int(self.shadow_dungeon_darkness_steps) - step_count,
            )
        from .. import curses

        if curses.has_curse(self, "Polydipsia"):
            self._polydipsia_steps = int(getattr(self, "_polydipsia_steps", 0) or 0) + step_count
            while self._polydipsia_steps >= 10:
                self._polydipsia_steps -= 10
                message = curses.polydipsia_tick(self)
                if message:
                    pending = getattr(self, "_exploration_messages", [])
                    pending.append(message)
                    self._exploration_messages = pending

    def record_stairs_used(self, count=1):
        stats = self.ensure_gameplay_stats()
        stats["stairs_used"] += max(0, int(count))

    def record_enemy_defeat(self, count=1):
        stats = self.ensure_gameplay_stats()
        stats["enemies_defeated"] += max(0, int(count))

    def record_flee(self, count=1):
        stats = self.ensure_gameplay_stats()
        stats["flees"] += max(0, int(count))

    def record_death(self, count=1):
        stats = self.ensure_gameplay_stats()
        stats["deaths"] += max(0, int(count))

    def record_damage_dealt(self, damage):
        if damage is None:
            return
        damage = max(0, int(damage))
        stats = self.ensure_gameplay_stats()
        stats["highest_damage_dealt"] = max(stats["highest_damage_dealt"], damage)

    def record_damage_taken(self, damage):
        if damage is None:
            return
        damage = max(0, int(damage))
        stats = self.ensure_gameplay_stats()
        stats["highest_damage_taken"] = max(stats["highest_damage_taken"], damage)

    def refresh_highest_level(self):
        stats = self.ensure_gameplay_stats()
        stats["highest_level_reached"] = max(
            stats["highest_level_reached"],
            int(self.player_level() or 1),
        )

    def exp_gain_multiplier(self) -> float:
        """Race-based experience gain multiplier (used by combat and quests)."""
        multiplier = 1.0
        try:
            from ..constants import HUMAN_EXP_MULTIPLIER, HALF_GIANT_EXP_MULTIPLIER
            race_name = getattr(getattr(self, "race", None), "name", None)
            if race_name == "Human":
                multiplier *= HUMAN_EXP_MULTIPLIER
            if race_name == "Half Giant":
                multiplier *= HALF_GIANT_EXP_MULTIPLIER
        except Exception:
            pass
        try:
            multiplier *= paladin.redemption_reward_multiplier(self)
        except Exception:
            pass
        return multiplier
