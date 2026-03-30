"""
Data-Driven Ability Classes

These classes bridge the effects system into actual combat execution.
DataDrivenSpell replicates the Attack.cast() damage pipeline but delegates
secondary effects to composed Effect objects loaded from YAML.

DataDrivenSkill does the same for weapon-based skills.

Both return CombatResult with a populated .message field, so str(result)
works transparently with the existing battle engine code.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from src.core.abilities import Spell, Skill
from src.core.combat.combat_result import CombatResult
from src.core.constants import (
    ARMOR_SCALING_FACTOR,
    DAMAGE_VARIANCE_HIGH,
    DAMAGE_VARIANCE_LOW,
)

if TYPE_CHECKING:
    from typing import Any

    from src.core.character import Character
    from src.core.effects.base import Effect


# ---------------------------------------------------------------------------
# Lazy imports for base classes that live in abilities.py.  We import them
# at call-time to avoid circular-import issues.
# ---------------------------------------------------------------------------
def _get_heal_spell_class():
    from src.core.abilities import HealSpell
    return HealSpell


def _get_support_spell_class():
    from src.core.abilities import SupportSpell
    return SupportSpell


def _get_status_spell_class():
    from src.core.abilities import StatusSpell
    return StatusSpell


class DataDrivenSpell(Spell):
    """
    A spell whose behavior is defined by composed Effect objects + YAML config.

    Replicates the Attack.cast() pipeline (mana → immunity → dodge → crit →
    base damage → defenses → resistance → variance → CON save → apply damage)
    and then executes the composed effects for secondary outcomes (burn, stun,
    chill damage, etc.).

    The .cast() method returns a CombatResult whose __str__ produces the display
    message, so the battle engine's ``str(spell.cast(...))`` works unchanged.
    """

    def __init__(
        self,
        name: str,
        description: str,
        cost: int,
        dmg_mod: float,
        crit: int,
        subtyp: str,
        effects: list[Effect] | None = None,
        school: str | None = None,
        rank: int | None = None,
        charge_time: int | None = None,
        delay: int | None = None,
        telegraph_message: str | None = None,
        priority: str | None = None,
        notes: str | None = None,
    ):
        super().__init__(name, description, school=school)
        self.cost = cost
        self.dmg_mod = dmg_mod
        self.crit = crit
        self.subtyp = subtyp
        self.turns = None
        self.rank = rank
        self._effects: list[Effect] = effects or []
        self._charge_time = charge_time
        self._delay = delay
        self._telegraph_message = telegraph_message
        self._priority = priority
        self._notes = notes

    # ------------------------------------------------------------------
    # Attack.cast() replica with composed-effects integration
    # ------------------------------------------------------------------
    def cast(
        self,
        caster: Character,
        target: Character = None,
        cover: bool = False,
        special: bool = False,
        fam: bool = False,
    ) -> CombatResult:
        result = self._reset_result(actor=caster, target=target)
        result.extra['cost'] = self.cost
        msg = ""

        # ── 1. Mana cost ────────────────────────────────────────────
        if not (
            special
            or fam
            or (
                caster.cls.name == "Wizard"
                and caster.class_effects["Power Up"].active
            )
        ):
            caster.mana.current -= self.cost

        # ── 2. Immunity checks ──────────────────────────────────────
        if any([target.magic_effects["Ice Block"].active, target.tunnel]):
            result.hit = False
            result.message = "It has no effect.\n"
            return result

        # ── 3. Reflect ──────────────────────────────────────────────
        reflect = target.magic_effects["Reflect"].active

        # ── 4. Dodge / hit rolls ────────────────────────────────────
        spell_mod = caster.check_mod("magic", enemy=target)
        dodge = target.dodge_chance(caster, spell=True)
        hit = caster.hit_chance(target, typ="magic")
        if target.incapacitated():
            dodge = False
            hit = True

        if dodge and not reflect:
            msg += f"{target.name} dodged the {self.name} and was unhurt.\n"
            result.dodge = True
            result.hit = False
            result.message = msg
            return result

        # ── 5. Crit roll ────────────────────────────────────────────
        if reflect:
            target = caster
            msg += f"{self.name} is reflected back at {caster.name}!\n"

        crit = 1
        if not random.randint(0, self.crit):
            crit = 2
        crit_per = random.uniform(1, crit)
        result.crit = crit_per if crit > 1 else None

        # ── 6. Base damage ──────────────────────────────────────────
        damage = int(self.dmg_mod * spell_mod * crit_per)

        # ── 7. Defenses & resistance ────────────────────────────────
        hit, message, damage = target.handle_defenses(
            caster, damage, cover, typ="Magic"
        )
        msg += message
        hit, message, damage = target.damage_reduction(
            damage, caster, typ=self.subtyp
        )
        msg += message

        if hit:
            # ── 8. Class bonuses ────────────────────────────────────
            if (
                caster.cls.name == "Archbishop"
                and caster.class_effects["Power Up"].active
                and self.subtyp == "Holy"
            ):
                damage = int(damage * 1.25)

            if damage < 0:
                # Absorption – target heals
                target.health.current -= damage
                msg += (
                    f"{target.name} absorbs {self.subtyp} and is healed "
                    f"for {abs(damage)} health.\n"
                )
            else:
                # ── 9. Variance ─────────────────────────────────────
                variance = random.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
                damage = int(damage * variance)

                if damage <= 0:
                    msg += "The spell was ineffective and does no damage.\n"
                    damage = 0
                elif random.randint(0, target.stats.con // 2) > random.randint(
                    (caster.stats.intel * crit) // 2,
                    (caster.stats.intel * crit),
                ):
                    # ── 10. CON save → half damage ──────────────────
                    damage //= 2
                    if damage > 0:
                        msg += (
                            f"{target.name} shrugs off the spell and only "
                            f"receives half of the damage.\n"
                        )
                        damage_msg = (
                            f"{caster.name} damages {target.name} "
                            f"for {damage} hit points"
                        )
                        if crit > 1:
                            damage_msg += " (Critical hit!)"
                        msg += damage_msg + ".\n"
                    else:
                        msg += "The spell was ineffective and does no damage.\n"
                else:
                    damage_msg = (
                        f"{caster.name} damages {target.name} "
                        f"for {damage} hit points"
                    )
                    if crit > 1:
                        damage_msg += " (Critical hit!)"
                    msg += damage_msg + ".\n"

                # ── 11. Apply damage ────────────────────────────────
                target.health.current -= damage
                result.damage = damage
                result.hit = True

                # ── 12. Execute composed effects (secondary) ────────
                if target.is_alive() and damage > 0:
                    effect_target = caster if reflect else target
                    msg += self._apply_effects(
                        caster, effect_target, damage, crit, result
                    )

            # ── 13. Counterspell check ──────────────────────────────
            if (
                "Counterspell" in target.spellbook.get("Spells", {})
                and not random.randint(0, 4)
            ):
                from src.core.abilities import Counterspell

                msg += f"{target.name} uses Counterspell.\n"
                msg += Counterspell().use(target, caster)
        else:
            msg += f"The spell misses {target.name}.\n"

        # ── 14. Wizard mana regen on Power Up ───────────────────────
        if (
            caster.cls.name == "Wizard"
            and caster.class_effects["Power Up"].active
            and damage > 0
        ):
            msg += f"{caster.name} regens {damage} mana.\n"
            caster.mana.current += damage
            if caster.mana.current > caster.mana.max:
                caster.mana.current = caster.mana.max

        result.message = msg
        return result

    # ------------------------------------------------------------------
    # Effect execution – replaces the per-subtype special_effect()
    # ------------------------------------------------------------------
    def _apply_effects(
        self,
        caster: Character,
        target: Character,
        damage: int,
        crit: int,
        result: CombatResult,
    ) -> str:
        """
        Execute composed effects and return any messages they generate.

        Effects operate on the CombatResult; any text they produce is
        returned so the caller can append it to the running message.
        """
        msg = ""
        # Store damage/crit context so effects can reference it
        result.extra["last_damage"] = damage
        result.extra["last_crit"] = crit

        for effect in self._effects:
            # Snapshot target HP before effect
            hp_before = target.health.current
            effects_before = dict(result.effects_applied)

            try:
                effect.apply(caster, target, result)
            except Exception:
                # Effects are non-breaking (same philosophy as event bus)
                continue

            # Build messages from observable state changes
            hp_diff = hp_before - target.health.current
            if hp_diff > 0 and hp_diff != damage:
                # Effect dealt additional damage beyond the base spell
                msg += (
                    f"{target.name} takes an extra {hp_diff} damage.\n"
                )

            # Check for newly applied status effects
            for status in result.effects_applied.get("Status", []):
                if status not in effects_before.get("Status", []):
                    msg += f"{target.name} is afflicted with {status}.\n"

            for magic_eff in result.effects_applied.get("Magic", []):
                if magic_eff not in effects_before.get("Magic", []):
                    if "DOT" in magic_eff:
                        msg += f"{target.name} is set ablaze.\n"
                    elif magic_eff == "Regen":
                        msg += f"{target.name} begins to regenerate.\n"

        return msg

    def special_effect(
        self,
        caster: Character,
        target: Character,
        damage: int,
        crit: int,
    ) -> str:
        """
        Compatibility shim — if called directly (e.g. from Attack.cast in
        a mixed-inheritance scenario), delegate to the composed effects.
        """
        result = CombatResult(action=self.name, actor=caster, target=target)
        result.damage = damage
        return self._apply_effects(caster, target, damage, crit, result)


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

        if not special:
            user.mana.current -= self.cost

        if self._requires_incapacitated and target is not None:
            if not target.incapacitated():
                return f"{self.name} is ineffective against {target.name}."

        if self.weapon:
            # Build weapon_damage kwargs
            wd_kwargs: dict[str, Any] = {"cover": cover, "dmg_mod": self.dmg_mod}
            if self._ignore_armor:
                wd_kwargs["ignore"] = True
            if self._guaranteed_hit:
                wd_kwargs["hit"] = True
            if self._crit_override is not None:
                wd_kwargs["crit"] = self._crit_override
            if self._intel_dmg_mod:
                wd_kwargs["dmg_mod"] = max(self.dmg_mod, user.stats.intel / 15)

            hit = False
            crit = 1
            for _ in range(self._strikes):
                use_str, h, c = user.weapon_damage(target, **wd_kwargs)
                msg += use_str
                if h:
                    hit = True
                    crit = max(crit, c)
                if target is not None and not target.is_alive():
                    break

            result.hit = hit
            result.crit = crit if crit > 1 else None
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
# DataDrivenStatusSkill – replaces status-applying Skill subclasses
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
            if any([
                self._status_name in getattr(target, "status_immunity", []),
                f"Status-{self._status_name}" in target.equipment["Pendant"].mod,
                "Status-All" in target.equipment["Pendant"].mod,
            ]):
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


# ======================================================================
# DataDrivenHealSpell – replaces HealSpell subclasses
# ======================================================================

class DataDrivenHealSpell(_get_heal_spell_class()):
    """
    A heal spell loaded from YAML.  Supports instant heal, HoT (Regen),
    and hybrid (Hydration = instant + HoT).  Also provides ``cast_out()``
    for the out-of-combat healing UI.
    """

    def __init__(
        self,
        name: str,
        description: str,
        cost: int,
        heal: float,
        crit: int,
        turns: int = 0,
        effects: list[Effect] | None = None,
        rank: int | None = None,
        instant_heal: bool = False,
    ):
        super().__init__(name, description, cost, heal, crit)
        self.turns = turns
        self.combat = turns > 0
        self.rank = rank
        self._effects: list[Effect] = effects or []
        self._instant_heal = instant_heal

    # -- HoT helper (Regen pattern) ------------------------------------
    def hot(self, target, heal):
        """Apply heal-over-time using the Regen magic effect."""
        target.magic_effects["Regen"].active = True
        target.magic_effects["Regen"].duration = max(
            self.turns, target.magic_effects["Regen"].duration
        )
        target.magic_effects["Regen"].extra = max(
            heal, target.magic_effects["Regen"].extra
        )
        try:
            target._emit_status_event(
                target, "Regen", applied=True,
                duration=target.magic_effects["Regen"].duration,
                source="Heal",
            )
        except Exception:
            pass

    # -- cast override to support Hydration hybrid ---------------------
    def cast(self, caster, target=None, cover=False, special=False, fam=False):
        if self._instant_heal and self.turns > 0:
            return self._cast_hybrid(caster, target, cover, special, fam)
        return super().cast(caster, target, cover, special, fam)

    def _cast_hybrid(self, caster, target, cover, special, fam):
        """Hydration-style: instant heal THEN apply HoT."""
        cast_message = ""
        if not fam:
            target = caster
        if not (special or fam):
            caster.mana.current -= self.cost
        crit = 1
        heal_mod = caster.check_mod("heal")
        heal = int(
            (random.randint(target.health.max // 2, target.health.max) + heal_mod)
            * self.heal
        )
        if not random.randint(0, self.crit):
            cast_message += "Critical Heal!\n"
            crit = 2
        crit_per = random.uniform(1, crit)
        heal = int(heal * crit_per)
        heal = int(heal * target.healing_received_multiplier())
        actual_heal = min(heal, target.health.max - target.health.current)
        target.health.current += actual_heal
        caster._emit_healing_event(actual_heal, source=self.name)
        cast_message += (
            f"{caster.name} heals {target.name} for {actual_heal} hit points.\n"
        )
        if target.health.current >= target.health.max:
            target.health.current = target.health.max
            cast_message += f"{target.name} is at full health.\n"
        self.hot(target, actual_heal)
        return cast_message

    # -- out-of-combat heal --------------------------------------------
    def cast_out(self, actor):
        """UI-agnostic out-of-combat heal."""
        cast_message = f"{actor.name} casts {self.name}.\n"
        if actor.health.current == actor.health.max:
            cast_message += "You are already at full health.\n"
            return cast_message
        actor.mana.current -= self.cost
        crit = 1
        heal_mod = actor.check_mod("heal")
        heal = int(actor.health.max * self.heal + heal_mod)
        if not random.randint(0, self.crit):
            cast_message += "Critical Heal!\n"
            crit = 2
        heal *= crit
        heal = int(heal * actor.healing_received_multiplier())
        actual_heal = min(heal, actor.health.max - actor.health.current)
        actor.health.current += actual_heal
        actor._emit_healing_event(actual_heal, source=self.name)
        cast_message += (
            f"{actor.name} heals themself for {actual_heal} hit points.\n"
        )
        if actor.health.current >= actor.health.max:
            actor.health.current = actor.health.max
            cast_message += f"{actor.name} is at full health.\n"
        return cast_message


# ======================================================================
# DataDrivenSupportSpell – replaces SupportSpell / IllusionSpell subs
# ======================================================================

class DataDrivenSupportSpell(_get_support_spell_class()):
    """
    A self-targeting buff spell loaded from YAML.  The effects list handles
    all buff application (stat buffs, magic effects, cleanse, etc.).
    Messages are collected from ``result.extra["messages"]`` set by effects,
    or from the optional static ``message`` template.
    """

    def __init__(
        self,
        name: str,
        description: str,
        cost: int,
        effects: list[Effect] | None = None,
        school: str | None = None,
        rank: int | None = None,
        target_self: bool = True,
        wizard_free_cast: bool = False,
        message: str | None = None,
        subtype: str = "Support",
    ):
        super().__init__(name, description, cost)
        self._effects: list[Effect] = effects or []
        self.school = school
        self.rank = rank
        self._target_self = target_self
        self._wizard_free_cast = wizard_free_cast
        self._message = message
        self.subtyp = subtype

    def cast(self, caster, target=None, cover=False, special=False, fam=False):
        if self._target_self and not fam:
            target = caster
        elif target is None:
            target = caster

        if not (
            special
            or fam
            or (
                self._wizard_free_cast
                and caster.cls.name == "Wizard"
                and caster.class_effects["Power Up"].active
            )
        ):
            caster.mana.current -= self.cost

        result = CombatResult(action=self.name, actor=caster, target=target)

        for effect in self._effects:
            try:
                effect.apply(caster, target, result)
            except Exception:
                continue

        # Collect messages from effects
        messages = result.extra.get("messages", [])

        # Stat buff messages (from DynamicStatBuffEffect)
        for stat, amount in result.extra.get("buff_amounts", {}).items():
            messages.append(
                f"{target.name}'s {stat.lower()} increases by {amount}."
            )

        # Cleanse message
        if result.effects_applied.get("Cleansed"):
            messages.append(
                f"All negative status effects have been cured for "
                f"{target.name}!"
            )

        # Magic effect messages
        for eff_name in result.effects_applied.get("Magic", []):
            _magic_msgs = {
                "Ice Block": (
                    f"{target.name} encases themself in a block of ice, "
                    "making them invulnerable for a time."
                ),
                "Duplicates": (
                    f"{caster.name} creates duplicates of themself "
                    f"to fool {target.name if target != caster else 'the enemy'}."
                ),
                "Reflect": (
                    f"A magic force field envelopes {target.name}."
                ),
                "Astral Shift": (
                    f"{target.name} shifts partially into the astral plane, "
                    "reducing damage taken by 25%."
                ),
                "Regen": f"{target.name} begins to regenerate.",
            }
            messages.append(
                _magic_msgs.get(eff_name, f"{target.name} gains {eff_name}.")
            )

        # Stat modifier messages for fixed multi_buff (no dynamic amounts)
        for stat_info in result.effects_applied.get("Stat", []):
            if stat_info not in [
                f"{s} Buff" for s in result.extra.get("buff_amounts", {})
            ]:
                stat = stat_info.replace(" Buff", "").replace(" Debuff", "")
                val = getattr(target.stat_effects.get(stat), "extra", "?")
                messages.append(
                    f"{target.name}'s {stat.lower()} "
                    f"{'increases' if 'Buff' in stat_info else 'decreases'} by {val}."
                )

        # Static message template fallback
        if not messages and self._message:
            messages = [
                self._message.format(target=target.name, caster=caster.name)
            ]

        if not messages:
            messages = [f"{self.name} was cast."]

        return "\n".join(messages) + "\n"


# ======================================================================
# DataDrivenStatusSpell – replaces StatusSpell subclasses
# ======================================================================

class DataDrivenStatusSpell(_get_status_spell_class()):
    """
    An enemy-targeting debuff/status spell loaded from YAML.  Handles:
    mana cost → Ice Block/tunnel immunity → effects (stat contests wrapping
    status_apply / debuffs / dispels) → message generation.
    """

    _STATUS_MESSAGES: dict[str, dict[str, str]] = {
        "Blind": {
            "success": "{target} is blinded.",
            "immune": "{target} is immune to blind status.",
            "already": "{target} is already blinded.",
        },
        "Sleep": {
            "success": "{target} is asleep.",
            "immune": "{target} is immune to sleep effect.",
            "already": "{target} is already asleep.",
            "resist": "{caster} fails to put {target} to sleep.",
        },
        "Stun": {
            "success": "{target} is stunned.",
            "immune": "{target} is immune to stun effect.",
            "already": "{target} is already stunned.",
            "resist": "{caster} fails to stun {target}.",
        },
        "Silence": {
            "success": "{target} has been silenced.",
            "immune": "{target} is immune to silence.",
        },
        "Berserk": {
            "success": "{target} is enraged.",
            "immune": "{target} is immune to berserk status.",
            "already": "{target} is already enraged.",
        },
    }

    def __init__(
        self,
        name: str,
        description: str,
        cost: int,
        effects: list[Effect] | None = None,
        rank: int | None = None,
        wizard_free_cast: bool = False,
        messages: dict[str, str] | None = None,
        subtype: str | None = None,
        school: str | None = None,
    ):
        super().__init__(name, description, cost)
        self._effects: list[Effect] = effects or []
        self.rank = rank
        self._wizard_free_cast = wizard_free_cast
        self._messages = messages or {}
        if subtype:
            self.subtyp = subtype
        if school:
            self.school = school

    def cast(self, caster, target=None, cover=False, special=False, fam=False):
        # Mana deduction
        if not (
            special
            or fam
            or (
                self._wizard_free_cast
                and caster.cls.name == "Wizard"
                and caster.class_effects["Power Up"].active
            )
        ):
            caster.mana.current -= self.cost

        # Ice Block / tunnel immunity
        if any([target.magic_effects["Ice Block"].active, target.tunnel]):
            return "It has no effect.\n"

        # Apply effects (stat contest → status_apply / debuff / dispel)
        result = CombatResult(action=self.name, actor=caster, target=target)
        result.extra["last_crit"] = 1

        for effect in self._effects:
            try:
                effect.apply(caster, target, result)
            except Exception:
                continue

        # --- Message generation ---
        fmt = {"target": target.name, "caster": caster.name}

        # Immunity
        immune_status = result.extra.get("status_immune")
        if immune_status:
            msgs = self._STATUS_MESSAGES.get(immune_status, {})
            tmpl = self._messages.get(
                "immune", msgs.get("immune", "{target} is immune.")
            )
            return tmpl.format(**fmt) + "\n"

        # Already active
        already = result.extra.get("status_already_active")
        if already:
            msgs = self._STATUS_MESSAGES.get(already, {})
            tmpl = self._messages.get(
                "already", msgs.get("already", "{target} is already affected.")
            )
            return tmpl.format(**fmt) + "\n"

        # Effect-generated messages (DynamicMultiDebuff, FullDispel)
        effect_msgs = result.extra.get("messages", [])

        # Status applied
        statuses = result.effects_applied.get("Status", [])
        if statuses:
            status = statuses[0]
            msgs = self._STATUS_MESSAGES.get(status, {})
            tmpl = self._messages.get(
                "success",
                msgs.get("success", "{target} is afflicted with " + status.lower() + "."),
            )
            return tmpl.format(**fmt) + "\n"

        # Dispel success
        if result.effects_applied.get("Dispelled") is not None:
            tmpl = self._messages.get(
                "success",
                "All positive status effects removed from {target}.",
            )
            return tmpl.format(**fmt) + "\n"

        # Multi-debuff messages
        if effect_msgs:
            return "\n".join(effect_msgs) + "\n"

        # Contest lost / resist
        if result.extra.get("stat_contest_won") is False:
            # Determine resist message: find first status in effects
            first_status = None
            for eff in self._effects:
                inner = getattr(eff, "effect", None)
                if inner and hasattr(inner, "status_name"):
                    first_status = inner.status_name
                    break
            if first_status:
                msgs = self._STATUS_MESSAGES.get(first_status, {})
                tmpl = self._messages.get(
                    "resist", msgs.get("resist", "The spell is ineffective.")
                )
            else:
                tmpl = self._messages.get(
                    "resist", "{target} resists the spell."
                )
            return tmpl.format(**fmt) + "\n"

        return ""


class DataDrivenWeaponSpell(Spell):
    """
    A spell that first makes a weapon attack, then runs composed effects
    on a successful hit (e.g. Smite's holy damage follow-up).

    Pipeline: mana cost → weapon_damage() → if hit + alive → effects.
    """

    def __init__(
        self,
        name: str,
        description: str,
        cost: int,
        dmg_mod: float = 1.0,
        crit: int = 5,
        subtyp: str = "Holy",
        effects: list | None = None,
        school: str | None = None,
        rank: int | None = None,
    ):
        super().__init__(name, description, school=school)
        self.cost = cost
        self.dmg_mod = dmg_mod
        self.crit = crit
        self.subtyp = subtyp
        self.rank = rank
        self._effects: list = effects or []

    def cast(
        self,
        caster,
        target=None,
        cover: bool = False,
        special: bool = False,
        fam: bool = False,
    ):
        if not (special or fam):
            caster.mana.current -= self.cost

        msg, hit, crit = caster.weapon_damage(
            target, dmg_mod=self.dmg_mod, cover=cover
        )

        if hit and target.is_alive():
            result = CombatResult(action=self.name, actor=caster, target=target)
            result.hit = True
            result.extra["last_crit"] = crit
            result.extra["dmg_mod"] = self.dmg_mod

            for effect in self._effects:
                try:
                    effect.apply(caster, target, result)
                except Exception:
                    continue

            for emsg in result.extra.get("messages", []):
                msg += emsg

        return msg


class DataDrivenCustomSpell(Spell):
    """
    A spell whose entire combat logic resides in its composed effects.

    Pipeline: mana cost → ice block / tunnel check → run effects →
    collect messages.  No dodge / crit / damage pipeline — effects handle
    everything.  Used for abilities like Turn Undead.
    """

    def __init__(
        self,
        name: str,
        description: str,
        cost: int,
        dmg_mod: float = 1.0,
        crit: int = 5,
        subtyp: str = "Holy",
        effects: list | None = None,
        school: str | None = None,
        rank: int | None = None,
    ):
        super().__init__(name, description, school=school)
        self.cost = cost
        self.dmg_mod = dmg_mod
        self.crit = crit
        self.subtyp = subtyp
        self.rank = rank
        self._effects: list = effects or []

    def cast(
        self,
        caster,
        target=None,
        cover: bool = False,
        special: bool = False,
        fam: bool = False,
    ):
        if not (special or fam):
            caster.mana.current -= self.cost

        if any([target.magic_effects["Ice Block"].active, target.tunnel]):
            return "It has no effect.\n"

        result = CombatResult(action=self.name, actor=caster, target=target)
        result.extra["dmg_mod"] = self.dmg_mod
        result.extra["crit_chance"] = self.crit

        for effect in self._effects:
            try:
                effect.apply(caster, target, result)
            except Exception:
                continue

        msg = ""
        for emsg in result.extra.get("messages", []):
            msg += emsg

        return msg if msg else "The spell has no effect.\n"


# ======================================================================
# DataDrivenChargingSkill – multi-turn charging state machine
# ======================================================================

class DataDrivenChargingSkill(Skill):
    """
    A skill with a charging phase before execution.

    Manages: deduct mana → start_charge (if charge_time > 0) →
    continue / cancel (incapacitated) → execute → run effects.

    Used by: Charge, CrushingBlow, ArcaneBlast.

    The execute phase delegates entirely to the composed Effect list,
    which handles weapon damage, stun checks, damage pipelines, etc.
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
        requires_any_mana: bool = False,
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
        self._requires_any_mana = requires_any_mana

        # Mutable charging state (per-instance)
        self.charging: bool = False
        self.charge_turns: int = 0
        self.charge_target: Character | None = None
        self._charge_context: dict | None = None

    # ------------------------------------------------------------------
    # Charging helpers
    # ------------------------------------------------------------------
    def get_charge_time(self) -> int:
        return self._charge_time if self._charge_time else 0

    def start_charge(self, user: Character, target: Character) -> str:
        self.charging = True
        self.charge_turns = self.get_charge_time()
        self.charge_target = target
        self._charge_context = {"mana": user.mana.current}

        if self._telegraph_message:
            return f"{user.name} is {self._telegraph_message}!\n"
        return f"{user.name} begins to charge!\n"

    def cancel_charge(self, user: Character) -> str:
        self.charging = False
        self.charge_turns = 0
        self.charge_target = None
        self._charge_context = None
        return f"{user.name}'s {self.name} was interrupted!\n"

    # ------------------------------------------------------------------
    # Execute phase – delegates to composed effects
    # ------------------------------------------------------------------
    def _execute(self, user: Character, target: Character, cover: bool = False) -> str:
        result = self._reset_result(actor=user, target=target)
        result.extra["cover"] = cover
        result.extra["charge_context"] = self._charge_context or {}
        msg = ""

        for effect in self._effects:
            try:
                effect.apply(user, target, result)
            except Exception:
                continue

        for emsg in result.extra.get("messages", []):
            msg += emsg

        # Reset charging state
        self.charging = False
        self.charge_turns = 0
        self.charge_target = None
        self._charge_context = None
        return msg

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------
    def use(
        self,
        user: Character,
        target: Character = None,
        cover: bool = False,
        special: bool = False,
        **kwargs: Any,
    ) -> str:
        # Pre-execution mana gate (ArcaneBlast needs *some* mana)
        if self._requires_any_mana and user.mana.current == 0:
            return f"Not enough mana to cast {self.name}.\n"

        if self.charging:
            if user.incapacitated():
                return self.cancel_charge(user)

            self.charge_turns -= 1
            if self.charge_turns <= 0:
                return self._execute(
                    user, self.charge_target or target, cover
                )
            turns_left = self.charge_turns
            return (
                f"{user.name} continues charging... "
                f"({turns_left} turn{'s' if turns_left > 1 else ''} remaining)\n"
            )

        # First-time activation
        if not special:
            user.mana.current -= self.cost

        charge_time = self.get_charge_time()
        if charge_time > 0:
            return self.start_charge(user, target)

        # Instant execution (charge_time == 0)
        return self._execute(user, target, cover)


# ======================================================================
# DataDrivenMagicMissileSpell – multi-missile spell pipeline
# ======================================================================

class DataDrivenMagicMissileSpell(Spell):
    """
    A spell that fires multiple missiles, each independently resolving
    dodge / hit / Duplicates / crit / Mana Shield / Crusader / armor /
    variance / CON save / damage.

    Cannot be reflected.  Parameterized by ``missiles`` count.

    Used by: MagicMissile, MagicMissile2, MagicMissile3.
    """

    def __init__(
        self,
        name: str,
        description: str,
        cost: int,
        dmg_mod: float = 1.0,
        crit: int = 8,
        subtyp: str = "Non-elemental",
        missiles: int = 1,
        effects: list[Effect] | None = None,
        school: str | None = None,
        rank: int | None = None,
    ):
        super().__init__(name, description, school=school)
        self.cost = cost
        self.dmg_mod = dmg_mod
        self.crit = crit
        self.subtyp = subtyp
        self.missiles = missiles
        self._effects: list[Effect] = effects or []
        self.rank = rank

    def cast(
        self,
        caster: Character,
        target: Character = None,
        cover: bool = False,
        special: bool = False,
        fam: bool = False,
    ) -> str:
        cast_message = ""

        # ── 1. Mana cost (free with Wizard Power Up) ────────────────
        if not (
            special
            or fam
            or (
                caster.cls.name == "Wizard"
                and caster.class_effects["Power Up"].active
            )
        ):
            caster.mana.current -= self.cost

        # ── 2. Immunity check ───────────────────────────────────────
        if any([target.magic_effects["Ice Block"].active, target.tunnel]):
            return "It has no effect.\n"

        spell_mod = caster.check_mod("magic", enemy=target)
        hits: list[bool] = []

        # ── 3. Per-missile loop ─────────────────────────────────────
        for i in range(self.missiles):
            hits.append(False)
            dodge = target.dodge_chance(caster, spell=True)
            hits[i] = caster.hit_chance(target, typ="magic")
            if target.incapacitated():
                dodge = False
                hits[i] = True

            if dodge:
                cast_message += (
                    f"{target.name} dodged the {self.name} and was unhurt.\n"
                )
            elif cover:
                cast_message += (
                    f"{target.familiar.name} steps in front of the attack, "
                    f"absorbing the damage directed at {target.name}.\n"
                )
            else:
                crit = 1
                if not random.randint(0, self.crit):
                    crit = 2

                # Duplicates (Mirror Image) interception
                if hits[i] and target.magic_effects["Duplicates"].active:
                    chance = (
                        target.magic_effects["Duplicates"].duration
                        - self.check_mod("luck", luck_factor=15)
                    )
                    if random.randint(0, max(0, chance)):
                        hits[i] = False
                        cast_message += (
                            f"{self.name} hits a mirror image of "
                            f"{target.name} and it vanishes from existence.\n"
                        )
                        target.magic_effects["Duplicates"].duration -= 1
                        if not target.magic_effects["Duplicates"].duration:
                            target.magic_effects["Duplicates"].active = False

                if hits[i]:
                    crit_per = random.uniform(1, crit)
                    damage = int(self.dmg_mod * spell_mod * crit_per)

                    # Mana Shield
                    if target.magic_effects["Mana Shield"].active:
                        hits[i], message, damage = target._apply_mana_shield(
                            damage
                        )
                        cast_message += message
                    elif (
                        target.cls.name == "Crusader"
                        and target.power_up
                        and target.class_effects["Power Up"].active
                    ):
                        _, message, damage = target.handle_crusader_shield(
                            damage
                        )
                        cast_message += message

                    # Armor scaling
                    dam_red = target.check_mod("magic def", enemy=caster)
                    damage = int(
                        damage
                        * (1 - (dam_red / (dam_red + ARMOR_SCALING_FACTOR)))
                    )

                    # Variance
                    variance = random.uniform(
                        DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH
                    )
                    damage = int(damage * variance)

                    if damage <= 0:
                        cast_message += (
                            f"{self.name} was ineffective and does no damage.\n"
                        )
                        damage = 0
                    elif random.randint(
                        0, target.stats.con // 2
                    ) > random.randint(
                        caster.stats.intel // 2, caster.stats.intel
                    ):
                        damage //= 2
                        if damage > 0:
                            cast_message += (
                                f"{target.name} shrugs off the {self.name} "
                                f"and only receives half of the damage.\n"
                            )
                            damage_msg = (
                                f"{caster.name} damages {target.name} "
                                f"for {damage} hit points"
                            )
                            if crit > 1:
                                damage_msg += " (Critical hit!)"
                            cast_message += damage_msg + ".\n"
                        else:
                            cast_message += (
                                f"{self.name} was ineffective and does "
                                f"no damage.\n"
                            )
                    else:
                        damage_msg = (
                            f"{caster.name} damages {target.name} "
                            f"for {damage} hit points"
                        )
                        if crit > 1:
                            damage_msg += " (Critical hit!)"
                        cast_message += damage_msg + ".\n"

                    target.health.current -= damage
                    if not target.is_alive():
                        break
                else:
                    cast_message += f"The spell misses {target.name}.\n"

                # Wizard mana regen
                if (
                    caster.cls.name == "Wizard"
                    and caster.class_effects["Power Up"].active
                    and damage > 0
                ):
                    cast_message += f"{caster.name} regens {damage} mana.\n"
                    caster.mana.current += damage
                    if caster.mana.current > caster.mana.max:
                        caster.mana.current = caster.mana.max

        # ── 4. Counterspell check ───────────────────────────────────
        if any(hits):
            if (
                "Counterspell" in target.spellbook.get("Spells", {})
                and not random.randint(0, 4)
            ):
                from src.core.abilities import Counterspell

                cast_message += f"{target.name} uses Counterspell.\n"
                cast_message += Counterspell().use(target, target=caster)

        return cast_message


# ======================================================================
# DataDrivenJumpSkill – Jump with full modification system
# ======================================================================

class DataDrivenJumpSkill(Skill):
    """
    Data-driven Jump skill with its complete modification management
    system, customised charging (Unstoppable, Retribution tracking,
    Defend/Acrobat flags), and execute phase delegated to JumpEffect.

    All modification management helper methods are retained 1-to-1 so
    that UI code, save/load, and game logic can interact with Jump as
    before.

    Used by: Jump.
    """

    # Default modification / unlock state (shared template, copied per
    # instance).
    _DEFAULT_MODIFICATIONS: dict[str, bool] = {
        "Crit": True,
        "Thrust": False,
        "Defend": False,
        "Rend": False,
        "Quake": False,
        "Acrobat": False,
        "Dragon's Fury": False,
        "Soaring Strike": False,
        "Quick Dive": False,
        "Retribution": False,
        "Unstoppable": False,
        "Recover": False,
        "Skyfall": False,
    }

    _DEFAULT_UNLOCKED: dict[str, bool] = {
        "Crit": True,
        "Thrust": False,
        "Defend": False,
        "Rend": False,
        "Quake": False,
        "Acrobat": False,
        "Dragon's Fury": False,
        "Soaring Strike": False,
        "Quick Dive": False,
        "Retribution": False,
        "Unstoppable": False,
        "Recover": False,
        "Skyfall": False,
    }

    _DEFAULT_UNLOCK_REQUIREMENTS: dict[str, dict] = {
        "Crit": {"type": "initial", "requirement": None},
        "Defend": {"type": "lancer_level", "requirement": 5},
        "Quick Dive": {"type": "lancer_level", "requirement": 10},
        "Acrobat": {"type": "lancer_level", "requirement": 15},
        "Thrust": {"type": "lancer_level", "requirement": 20},
        "Rend": {"type": "lancer_level", "requirement": 25},
        "Quake": {"type": "dragoon_level", "requirement": 5},
        "Soaring Strike": {"type": "dragoon_level", "requirement": 10},
        "Retribution": {"type": "dragoon_level", "requirement": 20},
        "Unstoppable": {"type": "dragoon_level", "requirement": 30},
        "Skyfall": {"type": "boss", "requirement": "Merzhin"},
        "Dragon's Fury": {"type": "boss", "requirement": "Red Dragon"},
        "Recover": {"type": "item", "requirement": "Dragon's Tear"},
    }

    def __init__(
        self,
        name: str,
        description: str,
        cost: int = 10,
        weapon: bool = True,
        dmg_mod: float = 2.0,
        effects: list[Effect] | None = None,
        subtyp: str = "Offensive",
        charge_time: int = 1,
        telegraph_message: str | None = None,
        prone_while_charging: bool = True,
        unlock_requirements: dict | None = None,
        modifications_defaults: dict | None = None,
        unlocked_defaults: dict | None = None,
        priority: str | None = None,
        notes: str | None = None,
    ):
        super().__init__(name, description, weapon=weapon)
        self.cost = cost
        self.dmg_mod = dmg_mod
        self.subtyp = subtyp
        self.strikes = 1
        self.crit = 1
        self._effects: list[Effect] = effects or []
        self._charge_time = charge_time
        self._telegraph_message = telegraph_message
        self._prone_while_charging = prone_while_charging
        self._priority = priority
        self._notes = notes

        # ── Modification state ────────────────────────────────────
        self.modifications: dict[str, bool] = dict(
            modifications_defaults or self._DEFAULT_MODIFICATIONS
        )
        self.unlocked_modifications: dict[str, bool] = dict(
            unlocked_defaults or self._DEFAULT_UNLOCKED
        )
        self.unlock_requirements: dict[str, dict] = dict(
            unlock_requirements or self._DEFAULT_UNLOCK_REQUIREMENTS
        )

        # ── Charging state ────────────────────────────────────────
        self.charging: bool = False
        self.charge_turns: int = 0
        self.charge_target: Character | None = None
        self.retribution_damage: int = 0
        self.jump_charge_health: int | None = None

        # Legacy attributes expected by backward-compat / UI code
        self._yaml_charge_time = charge_time
        self._yaml_telegraph_message = telegraph_message
        self._yaml_prone_while_charging = prone_while_charging

    # ==================================================================
    # Modification management (1-to-1 parity with original Jump)
    # ==================================================================

    def get_max_active_modifications(self, user: Character = None) -> int:
        """Max active mods: 1 + (level // 15), cap 5, +1 for ClassRing."""
        if user is None:
            return 5

        if hasattr(user, "level"):
            base_level = (
                user.level.level
                if hasattr(user.level, "level")
                else user.level
            )
        else:
            base_level = 99

        if hasattr(user, "cls") and hasattr(user.cls, "name"):
            if "Dragoon" in user.cls.name:
                user_level = 30 + int(base_level)
            else:
                user_level = int(base_level)
        else:
            user_level = int(base_level)

        max_mods = min(1 + user_level // 15, 5)

        if hasattr(user, "equipment") and "Ring" in user.equipment:
            ring = user.equipment["Ring"]
            if hasattr(ring, "mod") and ring.mod == "+1 Jump Mod":
                max_mods += 1

        return max_mods

    def unlock_modification(self, mod_name: str) -> bool:
        if mod_name in self.unlocked_modifications:
            self.unlocked_modifications[mod_name] = True
            return True
        return False

    def check_and_unlock_level_modifications(
        self, user_level, user_class=None
    ) -> list:
        if hasattr(user_level, "level"):
            user_level = user_level.level
        if hasattr(user_class, "name"):
            user_class = user_class.name
        if not user_class:
            return []
        user_class = str(user_class)

        newly_unlocked: list[str] = []
        for mod_name, req in self.unlock_requirements.items():
            req_type = req["type"]
            req_level = req["requirement"]
            should_unlock = False
            if (
                req_type == "lancer_level"
                and "Lancer" in user_class
                and req_level <= user_level
            ):
                should_unlock = True
            elif (
                req_type == "dragoon_level"
                and "Dragoon" in user_class
                and req_level <= user_level
            ):
                should_unlock = True
            if should_unlock and not self.unlocked_modifications[mod_name]:
                self.unlocked_modifications[mod_name] = True
                newly_unlocked.append(mod_name)
        return newly_unlocked

    def unlock_boss_modification(self, boss_name: str) -> str:
        for mod_name, req in self.unlock_requirements.items():
            if req["type"] == "boss" and req["requirement"] == boss_name:
                if not self.unlocked_modifications[mod_name]:
                    self.unlocked_modifications[mod_name] = True
                    return mod_name
        return ""

    def unlock_item_modification(self, item_name: str) -> str:
        for mod_name, req in self.unlock_requirements.items():
            if req["type"] == "item" and req["requirement"] == item_name:
                if not self.unlocked_modifications[mod_name]:
                    self.unlocked_modifications[mod_name] = True
                    return mod_name
        return ""

    def is_modification_unlocked(self, mod_name: str) -> bool:
        return self.unlocked_modifications.get(mod_name, False)

    def get_unlocked_modifications(self) -> list:
        return [m for m, u in self.unlocked_modifications.items() if u]

    def get_active_count(self) -> int:
        return sum(1 for a in self.modifications.values() if a)

    def enforce_modification_limit(self, user: Character = None) -> list:
        max_allowed = self.get_max_active_modifications(user)
        current_active = self.get_active_count()
        deactivated: list[str] = []
        if current_active > max_allowed:
            excess = current_active - max_allowed
            for mod_name in reversed(list(self.modifications.keys())):
                if excess <= 0:
                    break
                if self.modifications[mod_name]:
                    self.modifications[mod_name] = False
                    deactivated.append(mod_name)
                    excess -= 1
        return deactivated

    def set_modification(
        self, mod_name: str, active: bool, user: Character = None
    ) -> tuple[bool, str]:
        if mod_name not in self.modifications:
            return (False, "Modification doesn't exist")
        if not self.unlocked_modifications.get(mod_name, False):
            return (False, "Modification not unlocked")

        if active and not self.modifications[mod_name]:
            current_active = self.get_active_count()
            max_active = self.get_max_active_modifications(user)
            if current_active >= max_active:
                if user and hasattr(user, "level"):
                    base_level = (
                        user.level.level
                        if hasattr(user.level, "level")
                        else user.level
                    )
                    if (
                        hasattr(user, "cls")
                        and hasattr(user.cls, "name")
                        and "Dragoon" in user.cls.name
                    ):
                        user_level = 30 + int(base_level)
                    else:
                        user_level = int(base_level)
                else:
                    user_level = "?"
                return (
                    False,
                    f"Maximum {max_active} modifications can be active "
                    f"(based on level {user_level})",
                )

        self.modifications[mod_name] = active

        if active:
            if (
                mod_name == "Quick Dive"
                and self.modifications["Soaring Strike"]
            ):
                self.modifications["Soaring Strike"] = False
            elif (
                mod_name == "Soaring Strike"
                and self.modifications["Quick Dive"]
            ):
                self.modifications["Quick Dive"] = False
            elif mod_name == "Crit":
                if self.modifications["Soaring Strike"]:
                    self.modifications["Soaring Strike"] = False
            elif (
                mod_name == "Soaring Strike"
                and self.modifications["Crit"]
            ):
                self.modifications["Crit"] = False

        return (True, "")

    def get_active_modifications(self) -> list:
        return [m for m, a in self.modifications.items() if a]

    # ==================================================================
    # Charging helpers (Jump-specific)
    # ==================================================================

    def get_charge_time(self) -> int:
        if self.modifications["Quick Dive"]:
            return 0
        if self.modifications["Soaring Strike"]:
            return 2
        return self._charge_time if self._charge_time else 1

    def start_charge(self, user: Character, target: Character) -> str:
        charge_time = self.get_charge_time()
        if charge_time == 0:
            return ""

        self.charging = True
        self.charge_turns = charge_time
        self.charge_target = target
        self.retribution_damage = 0
        self.jump_charge_health = user.health.current

        if self._telegraph_message:
            use_str = f"{user.name} is {self._telegraph_message}"
        else:
            use_str = f"{user.name} prepares to leap into the air"
        if self.modifications["Soaring Strike"]:
            use_str += ", gathering power for a devastating strike"
        use_str += "!\n"

        if self.modifications["Defend"]:
            if not hasattr(user, "jump_defend_active"):
                user.jump_defend_active = False
            user.jump_defend_active = True
            use_str += (
                f"{user.name} assumes a defensive stance while preparing.\n"
            )

        if self.modifications["Acrobat"]:
            if not hasattr(user, "jump_acrobat_active"):
                user.jump_acrobat_active = False
            user.jump_acrobat_active = True
            use_str += f"{user.name} moves with enhanced agility.\n"

        return use_str

    def add_retribution_damage(self, damage: int) -> None:
        if self.modifications["Retribution"]:
            self.retribution_damage += damage

    def cancel_charge(self, user: Character) -> str:
        if not self.modifications["Unstoppable"]:
            self.charging = False
            self.charge_turns = 0
            self.charge_target = None
            self.retribution_damage = 0
            self.jump_charge_health = None

            if hasattr(user, "jump_defend_active"):
                user.jump_defend_active = False
            if hasattr(user, "jump_acrobat_active"):
                user.jump_acrobat_active = False
            if hasattr(user, "class_effects") and "Jump" in user.class_effects:
                user.class_effects["Jump"].active = False

            return f"{user.name}'s Jump was interrupted!\n"
        return f"{user.name}'s Jump cannot be stopped!\n"

    # ==================================================================
    # Execute phase – delegates to composed effects
    # ==================================================================

    def _execute(
        self, user: Character, target: Character, cover: bool = False
    ) -> str:
        result = self._reset_result(actor=user, target=target)
        result.extra["cover"] = cover
        result.extra["modifications"] = dict(self.modifications)
        result.extra["retribution_damage"] = self.retribution_damage

        for effect in self._effects:
            try:
                effect.apply(user, target, result)
            except Exception:
                continue

        msg = ""
        for emsg in result.extra.get("messages", []):
            msg += emsg

        # Reset charging state
        self.charging = False
        self.charge_turns = 0
        self.charge_target = None
        self.retribution_damage = 0
        self.jump_charge_health = None

        if hasattr(user, "jump_defend_active"):
            user.jump_defend_active = False
        if hasattr(user, "jump_acrobat_active"):
            user.jump_acrobat_active = False

        return msg

    # ==================================================================
    # Main entry point
    # ==================================================================

    def use(
        self,
        user: Character,
        target: Character = None,
        cover: bool = False,
        special: bool = False,
        **kwargs,
    ) -> str:
        if self.charging:
            # Interrupt if incapacitated (unless Unstoppable)
            if not self.modifications["Unstoppable"] and user.incapacitated():
                return self.cancel_charge(user)

            # Interrupt if hit hard enough during charge
            if (
                not self.modifications["Unstoppable"]
                and self.jump_charge_health is not None
            ):
                damage_taken = max(
                    0, self.jump_charge_health - user.health.current
                )
                # Half Giant racial virtue: perseverance — pain alone doesn't interrupt a charge.
                # Only incapacitation can interrupt.
                is_half_giant = getattr(getattr(user, "race", None), "name", None) == "Half Giant"
                if not is_half_giant:
                    interrupt_threshold = max(1, int(user.health.max * 0.1))
                    if damage_taken >= interrupt_threshold:
                        return self.cancel_charge(user)

                # Retribution tracks max damage taken
                if (
                    self.modifications["Retribution"]
                    and damage_taken > self.retribution_damage
                ):
                    self.retribution_damage = damage_taken

            self.charge_turns -= 1
            if self.charge_turns <= 0:
                return self._execute(
                    user, self.charge_target or target, cover
                )
            turns_left = self.charge_turns
            return (
                f"{user.name} continues to gather power... "
                f"({turns_left} turn{'s' if turns_left > 1 else ''} "
                f"remaining)\n"
            )

        # First-time activation
        if not special:
            user.mana.current -= self.cost

        charge_time = self.get_charge_time()
        if charge_time == 0:
            return self._execute(user, target, cover)

        return self.start_charge(user, target)


# ======================================================================
# DataDrivenMovementSpell – out-of-combat movement abilities
# ======================================================================

def _get_movement_spell_class():
    from src.core.abilities import MovementSpell
    return MovementSpell


class DataDrivenMovementSpell(_get_movement_spell_class()):
    """
    Data-driven out-of-combat movement spell.

    Movement spells define ``cast_out()`` (not ``cast()``) and operate
    on the game/player world-state rather than in the battle pipeline.
    Two movement_types are supported:

    * ``sanctuary`` — deduct mana, full heal, call ``user.to_town()``.
    * ``teleport``  — present Set / Teleport choice via
      ``selection_callback``, then store or restore coordinates.

    Used by: Sanctuary, Teleport.
    """

    def __init__(
        self,
        name: str,
        description: str,
        cost: int,
        movement_type: str = "sanctuary",
        combat: bool = True,
        effects: list | None = None,
        notes: str | None = None,
    ):
        super().__init__(name, description, cost)
        self._movement_type = movement_type
        self.combat = combat
        self._effects = effects or []
        self._notes = notes

    # ------------------------------------------------------------------
    # cast_out – the primary entry point for movement spells
    # ------------------------------------------------------------------
    def cast_out(self, user=None, selection_callback=None, game=None):
        """
        Dispatch to the appropriate movement behaviour.

        **Sanctuary** callers pass ``user`` (the Character).
        **Teleport** callers pass ``selection_callback`` and ``game``.
        The curses UI passes ``(self.game)`` as a single positional arg,
        so we accept that flexibly.
        """
        if self._movement_type == "sanctuary":
            return self._cast_sanctuary(user)
        elif self._movement_type == "teleport":
            return self._cast_teleport(selection_callback, game)
        return f"{self.name} has no effect.\n"

    # ------------------------------------------------------------------
    # Sanctuary behaviour
    # ------------------------------------------------------------------
    def _cast_sanctuary(self, user) -> str:
        user.mana.current -= self.cost
        user.health.current = user.health.max
        user.mana.current = user.mana.max
        user.to_town()
        return (
            f"{user.name} casts Sanctuary and is transported back to "
            f"town.\n"
        )

    # ------------------------------------------------------------------
    # Teleport behaviour
    # ------------------------------------------------------------------
    def _cast_teleport(self, selection_callback=None, game=None) -> str:
        import random as _random

        teleport_message = (
            "Do you want to set your location or teleport to the "
            "previous location?"
        )
        options = ["Set", "Teleport"]

        if selection_callback is not None:
            option_index = selection_callback(teleport_message, options)
        else:
            option_index = _random.randint(0, len(options) - 1)

        if options[option_index] == "Set":
            cast_message = (
                f"This location has been set for teleport by "
                f"{game.player_char.name}.\n"
            )
            game.player_char.teleport = (
                game.player_char.location_x,
                game.player_char.location_y,
                game.player_char.location_z,
            )
        else:
            cast_message = (
                f"{game.player_char.name} teleports to set location.\n"
            )
            game.player_char.mana.current -= self.cost
            (
                game.player_char.location_x,
                game.player_char.location_y,
                game.player_char.location_z,
            ) = game.player_char.teleport

        return cast_message
