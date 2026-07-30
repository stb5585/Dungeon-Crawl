"""Data-driven weapon and status skill implementations."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from src.core.character import Character
    from src.core.effects.base import Effect

from src.core.abilities import Skill
from src.core.combat.combat_result import CombatResult


class DataDrivenSkill(Skill):
    """
    A skill whose behavior is defined by composed Effect objects + YAML config.

    For weapon-based skills, delegates to user.weapon_damage() for the primary
    hit, then executes composed effects for secondary outcomes.

    Batch 3 extensions:
      - ``ignore_armor``/``guaranteed_hit``/``crit_override`` → weapon_damage kwargs
      - ``strikes`` → multi-hit loop
      - ``requires_incapacitated`` → SneakAttack-style check
      - ``intel_dmg_mod`` → ImbueWeapon: dmg_mod = max(self.dmg_mod, intel/15)
      - ``ice_block_check`` → pre-execution immunity check
      - ``self_target`` → effects apply to user (BattleCry)
      - ``use_out_enabled`` → supports out-of-combat use
    """

    def __init__(
        self,
        name: str,
        description: str,
        cost: int = 0,
        weapon: bool = False,
        dmg_mod: float = 1.0,
        effects: list[Effect] | None = None,
        subtyp: str = "Offensive",
        charge_time: int | None = None,
        delay: int | None = None,
        telegraph_message: str | None = None,
        priority: str | None = None,
        notes: str | None = None,
        ignore_armor: bool = False,
        guaranteed_hit: bool = False,
        crit_override: int | None = None,
        strikes: int = 1,
        requires_incapacitated: bool = False,
        intel_dmg_mod: bool = False,
        ice_block_check: bool = False,
        self_target: bool = False,
        use_out_enabled: bool = False,
    ):
        super().__init__(name, description, weapon=weapon)
        self.cost = cost
        self.dmg_mod = dmg_mod
        self.subtyp = subtyp
        self._effects: list[Effect] = effects or []
        self._charge_time = charge_time
        self._delay = delay
        self._telegraph_message = telegraph_message
        self._priority = priority
        self._notes = notes
        self._ignore_armor = ignore_armor
        self._guaranteed_hit = guaranteed_hit
        self._crit_override = crit_override
        self._strikes = strikes
        self._requires_incapacitated = requires_incapacitated
        self._intel_dmg_mod = intel_dmg_mod
        self._ice_block_check = ice_block_check
        self._self_target = self_target
        self._use_out_enabled = use_out_enabled

    def use(
        self,
        user: Character,
        target: Character = None,
        cover: bool = False,
        special: bool = False,
        **kwargs: Any,
    ) -> str | CombatResult:
        result = self._reset_result(actor=user, target=target)
        result.extra['cost'] = self.cost
        result.extra['cover'] = cover
        result.extra['use_kwargs'] = kwargs
        msg = ""

        # Pre-execution checks
        if self._ice_block_check and target is not None:
            if any([target.magic_effects["Ice Block"].active,
                    getattr(target, "tunnel", False)]):
                return "It has no effect.\n"

        if self.weapon and hasattr(user, "is_disarmed") and user.is_disarmed():
            return f"{self.name} requires a weapon."

        if self._requires_incapacitated and target is not None:
            if not target.incapacitated():
                return f"{self.name} is ineffective against {target.name}."

        if not special:
            user.mana.current -= self.cost

        fortune_force_hit = False
        if self.name in {"Steal", "Mug", "Gold Toss", "Slot Machine", "Sneak Attack"}:
            try:
                from src.core.classes import promotion_kits

                fortune_force_hit, fortune_msg = promotion_kits.consume_fortune_for_risky_action(user, self.name)
                msg += fortune_msg
            except Exception:
                fortune_force_hit = False

        if self.weapon:
            # Build weapon_damage kwargs
            wd_kwargs: dict[str, Any] = {"cover": cover, "dmg_mod": self.dmg_mod}
            if self._ignore_armor:
                wd_kwargs["ignore"] = True
            if self._guaranteed_hit or fortune_force_hit:
                wd_kwargs["hit"] = True
            if self._crit_override is not None:
                wd_kwargs["crit"] = self._crit_override
            if self._intel_dmg_mod:
                wd_kwargs["dmg_mod"] = max(self.dmg_mod, user.stats.intel / 15)

            hit = False
            crit = 1
            total_damage = 0
            for _ in range(self._strikes):
                hp_before = target.health.current if target is not None else 0
                use_str, h, c = user.weapon_damage(target, **wd_kwargs)
                msg += use_str
                if h:
                    hit = True
                    crit = max(crit, c)
                    if target is not None:
                        total_damage += max(0, hp_before - target.health.current)
                if target is not None and not target.is_alive():
                    break

            result.hit = hit
            result.crit = crit if crit > 1 else None
            result.damage = total_damage
        else:
            hit = True
            crit = 1

        # Execute composed effects
        if hit:
            result.extra["last_damage"] = result.damage
            result.extra["last_crit"] = crit
            result.extra["dmg_mod"] = self.dmg_mod
            effect_target = user if self._self_target else target
            for effect in self._effects:
                try:
                    effect.apply(user, effect_target, result)
                except Exception:
                    continue

            # Collect messages generated by effects
            for emsg in result.extra.get("messages", []):
                msg += emsg

        try:
            from src.core.classes import promotion_kits

            if self.name in {"Sneak Attack", "Poison Strike"} and hit and target is not None:
                msg += promotion_kits.apply_death_mark(user, target, self.name)
            if self.name == "Inspect" and target is not None:
                msg += promotion_kits.add_revelation(user, target, 1, "Inspect")
                msg += promotion_kits.gain_case_progress(user, getattr(target, "enemy_typ", None), 3, "Inspect")
            if self.name == "Exploit Weakness" and target is not None and hit:
                msg += promotion_kits.add_revelation(user, target, 1, "Exploit Weakness")
                msg += promotion_kits.gain_case_progress(user, getattr(target, "enemy_typ", None), 2, "Exploit Weakness")
            if self.name in {"Steal", "Mug", "Gold Toss", "Slot Machine", "Sneak Attack"}:
                if hit:
                    msg += promotion_kits.resolve_misfortune_payoff(user, target, result.damage, self.name)
                if not hit or crit > 1:
                    msg += promotion_kits.add_fortune(user, bool(hit and crit > 1), self.name)
            msg += promotion_kits.pop_messages(user)
            if target is not None:
                msg += promotion_kits.pop_messages(target)
        except Exception:
            pass

        result.message = msg
        return msg if not self.weapon else result

    def use_out(self, game) -> str:
        """Out-of-combat usage (LifeTap, ManaTap, etc.)."""
        if not self._use_out_enabled:
            return f"{self.name} can only be used in combat.\n"
        result = self._reset_result(actor=game.player_char, target=game.player_char)
        user = game.player_char
        for effect in self._effects:
            try:
                effect.apply(user, user, result)
            except Exception:
                continue
        msg = ""
        for emsg in result.extra.get("messages", []):
            msg += emsg
        return msg if msg else f"{self.name} has no effect.\n"


# ======================================================================
# DataDrivenStatusSkill - replaces status-applying Skill subclasses
# ======================================================================

class DataDrivenStatusSkill(Skill):
    """
    A skill that applies a status/physical effect to the target via an
    immunity check + stat contest, without dealing weapon damage.

    Used by: Disarm, Goad, Howl, PocketSand, SleepingPowder, SmokeScreen,
             Trip, Web.
    Pattern: mana cost → ice block/tunnel check → immunity check →
             already-active check → stat contest → apply status/physical.

    Batch 4 extensions:
      - ``check_flying`` → blocks application on flying targets (Trip, Web)
      - ``actor_stat_alt`` → uses max(actor_stat, actor_stat_alt) for contest
      - ``extend_if_active`` → adds N turns to existing duration instead of
        skipping (Web)
      - ``action_message`` → always-displayed message before result (Howl)
    """

    # Default message templates keyed by status/effect name.
    _STATUS_MSG_DEFAULTS: dict[str, dict[str, str]] = {
        "Berserk": {
            "success": "{target} is enraged.\n",
            "immune": "{target} is immune to berserk status.\n",
            "already": "{target} is already enraged.\n",
            "fail": "{target} is not so easily provoked.\n",
        },
        "Blind": {
            "success": "{target} is blinded.\n",
            "immune": "{target} is immune to blind status.\n",
            "already": "{target} is already blinded.\n",
            "fail": "{user} fails to blind {target}.\n",
        },
        "Sleep": {
            "success": "{target} is asleep.\n",
            "immune": "{target} is immune to sleep effect.\n",
            "already": "{target} is already asleep.\n",
            "fail": "{user} fails to put {target} to sleep.\n",
        },
        "Stun": {
            "success": "{user} stunned {target}.\n",
            "immune": "{target} is immune to stun effect.\n",
            "already": "{target} is already stunned.\n",
            "fail": "{target}'s resolve is steadfast.\n",
        },
        "Prone": {
            "success": "{target} is knocked prone.\n",
            "immune": "{target} cannot be knocked prone.\n",
            "already": "{target} is already prone.\n",
            "fail": "{user} fails to knock {target} prone.\n",
        },
        "Disarm": {
            "success": "{target} is disarmed.\n",
            "immune": "{target} cannot be disarmed.\n",
            "already": "{target} is already disarmed.\n",
            "fail": "{user} fails to disarm the {target}.\n",
        },
    }

    def __init__(
        self,
        name: str,
        description: str,
        cost: int = 0,
        effects: list[Effect] | None = None,
        subtyp: str = "Defensive",
        status_name: str | None = None,
        physical: bool = False,
        actor_stat: str = "strength",
        actor_lo_divisor: int = 2,
        actor_hi_divisor: int = 1,
        actor_use_check_mod: str | None = None,
        actor_stat_alt: str | None = None,
        target_stat: str = "wisdom",
        target_lo_divisor: int = 2,
        target_hi_divisor: int = 1,
        target_use_check_mod: str | None = None,
        duration: int = 3,
        duration_stat: str | None = None,
        duration_divisor: int = 5,
        duration_min: int = 3,
        skip_if_active: bool = True,
        extend_if_active: int = 0,
        check_disarmable: bool = False,
        check_flying: bool = False,
        use_crit_multiplier: bool = False,
        messages: dict[str, str] | None = None,
        add_luck_chance: bool = False,
        action_message: str | None = None,
    ):
        super().__init__(name, description)
        self.cost = cost
        self.subtyp = subtyp
        self._effects: list[Effect] = effects or []
        self._status_name = status_name
        self._physical = physical
        self._actor_stat = actor_stat
        self._actor_lo_divisor = actor_lo_divisor
        self._actor_hi_divisor = actor_hi_divisor
        self._actor_use_check_mod = actor_use_check_mod
        self._actor_stat_alt = actor_stat_alt
        self._target_stat = target_stat
        self._target_lo_divisor = target_lo_divisor
        self._target_hi_divisor = target_hi_divisor
        self._target_use_check_mod = target_use_check_mod
        self._duration = duration
        self._duration_stat = duration_stat
        self._duration_divisor = duration_divisor
        self._duration_min = duration_min
        self._skip_if_active = skip_if_active
        self._extend_if_active = extend_if_active
        self._check_disarmable = check_disarmable
        self._check_flying = check_flying
        self._use_crit_multiplier = use_crit_multiplier
        self._add_luck_chance = add_luck_chance
        self._action_message = action_message

        # Merge custom messages over defaults
        defaults = self._STATUS_MSG_DEFAULTS.get(status_name or "", {})
        self._messages = {**defaults, **(messages or {})}

    def use(
        self,
        user: Character,
        target: Character = None,
        cover: bool = False,
        fam: bool = False,
        **kwargs: Any,
    ) -> str:
        import random as _rng

        if not fam:
            user.mana.current -= self.cost

        # If no status is being applied (e.g. SmokeScreen), just pay cost
        if self._status_name is None:
            return ""

        fmt = {"user": user.name, "target": target.name if target else ""}

        # Action message (always shown, e.g. "X howls at the moon.")
        prefix = ""
        if self._action_message:
            prefix = self._action_message.format(**fmt)

        # Ice Block / tunnel check
        if any([target.magic_effects["Ice Block"].active,
                getattr(target, "tunnel", False)]):
            return prefix + "It has no effect.\n"

        # Flying check (physical effects like Prone)
        if self._check_flying and getattr(target, "flying", False):
            return prefix + self._messages.get("immune", "").format(**fmt)

        # Disarmable check
        if self._check_disarmable:
            if not hasattr(target, "can_be_disarmed") or not target.can_be_disarmed():
                return prefix + self._messages.get("immune", "").format(**fmt)

        effects_dict = (target.physical_effects if self._physical
                        else target.status_effects)

        # Immunity check (for status_effects only)
        if not self._physical:
            if target.has_status_protection(self._status_name):
                return prefix + self._messages.get("immune", "").format(**fmt)

        # Already active check — either skip or extend
        if effects_dict[self._status_name].active:
            if self._extend_if_active > 0:
                effects_dict[self._status_name].duration += self._extend_if_active
                return prefix + self._messages.get("success", "").format(**fmt)
            if self._skip_if_active:
                return prefix + self._messages.get("already", "").format(**fmt)

        # Stat contest
        if self._actor_use_check_mod:
            actor_val = user.check_mod(self._actor_use_check_mod, enemy=user)
        else:
            a_stat = getattr(user.stats, self._actor_stat, 10)
            # Batch 4: use max of primary and alt stat if provided
            if self._actor_stat_alt:
                a_stat_alt = getattr(user.stats, self._actor_stat_alt, 0)
                a_stat = max(a_stat, a_stat_alt)
            actor_lo = 0 if self._actor_lo_divisor == 0 else a_stat // self._actor_lo_divisor
            actor_hi = a_stat // max(1, self._actor_hi_divisor)
            actor_val = _rng.randint(actor_lo, max(actor_lo, actor_hi))

        if self._target_use_check_mod:
            target_val = target.check_mod(self._target_use_check_mod, enemy=user)
            target_val = _rng.randint(0, max(0, target_val))
        else:
            t_stat = getattr(target.stats, self._target_stat, 10)
            target_lo = 0 if self._target_lo_divisor == 0 else t_stat // self._target_lo_divisor
            target_hi = t_stat // max(1, self._target_hi_divisor)
            target_val = _rng.randint(target_lo, max(target_lo, target_hi))

        if self._add_luck_chance:
            luck_bonus = target.check_mod("luck", enemy=user, luck_factor=10)
            target_val += luck_bonus
        elif (not self._physical) and (self._status_name in {"Stun", "Sleep", "Silence", "Blind", "Stupefy", "Stone"}):
            # Make WIS/CHA matter broadly for resisting control effects even if
            # the YAML entry didn't explicitly opt into luck-based resistance.
            # (Luck is derived from WIS/CHA via Character.check_mod("luck").)
            target_val += target.check_mod("luck", enemy=user, luck_factor=20)

        contest_success = actor_val > target_val
        if (self._status_name == "Stun") and (not self._physical):
            contest_success = target.stun_contest_success(user, actor_val, target_val)

        if contest_success:
            # Calculate duration
            if self._duration_stat:
                stat_val = getattr(user.stats, self._duration_stat, 10)
                dur = max(self._duration_min, stat_val // self._duration_divisor)
            else:
                dur = self._duration

            # Stun uses centralized application (handles post-stun immunity).
            if (self._status_name == "Stun") and (not self._physical):
                if not target.apply_stun(dur, source=self.name, applier=user):
                    return prefix + self._messages.get("fail", "").format(**fmt)
                return prefix + self._messages.get("success", "").format(**fmt)

            effects_dict[self._status_name].active = True
            # Negative duration = permanent (e.g. Disarm = -1)
            if dur < 0:
                effects_dict[self._status_name].duration = dur
            else:
                effects_dict[self._status_name].duration = max(
                    dur, effects_dict[self._status_name].duration
                )

            try:
                user._emit_status_event(
                    target, self._status_name, applied=True,
                    duration=effects_dict[self._status_name].duration,
                    source=self.name,
                )
            except Exception:
                pass

            return prefix + self._messages.get("success", "").format(**fmt)

        return prefix + self._messages.get("fail", "").format(**fmt)
