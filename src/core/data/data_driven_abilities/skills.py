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
      - ``target_status_damage_multiplier`` → conditional weapon damage
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
        target_status_damage_multiplier: dict[str, Any] | None = None,
        use_offhand: bool = False,
        repeat_until_miss: bool = False,
        accuracy_penalty_per_strike: float = 0.0,
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
        self._target_status_damage_multiplier = target_status_damage_multiplier
        self._use_offhand = use_offhand
        self._repeat_until_miss = repeat_until_miss
        self._accuracy_penalty_per_strike = max(0.0, accuracy_penalty_per_strike)

    def use(
        self,
        user: Character,
        target: Character = None,
        cover: bool = False,
        special: bool = False,
        **kwargs: Any,
    ) -> str | CombatResult:
        from src.core.classes import promotion_kits

        result = self._reset_result(actor=user, target=target)
        try:
            from src.core.classes import promotion_kits

            if self.name in promotion_kits.DEATH_MARK_SETUP_ABILITIES:
                user._death_mark_toxin_status = False
        except Exception:
            pass
        if (
            self.name == "Health/Mana Drain"
            and target is not None
            and "Top Off" in getattr(user, "spellbook", {}).get("Skills", {})
        ):
            try:
                from src.core.classes import class_rings

                debt_data = class_rings.ensure_state(user)["data"]["Shadowcaster"]
                debt = max(0, int(debt_data.get("debt", 0) or 0))
                if debt > 0:
                    debt_data["debt"] = 0
                    if "Death" in getattr(target, "status_immunity", ()):
                        health_drain = min(
                            target.health.current,
                            max(1, int(target.health.max * 0.27)),
                        )
                        mana_drain = min(
                            target.mana.current,
                            max(1, int(target.mana.max * 0.27)),
                        )
                    else:
                        health_drain = min(
                            target.health.current,
                            max(0, user.health.max - user.health.current),
                        )
                        mana_drain = min(
                            target.mana.current,
                            max(0, user.mana.max - user.mana.current),
                        )
                    target.health.current -= health_drain
                    target.mana.current -= mana_drain
                    user.health.current = min(user.health.max, user.health.current + health_drain)
                    user.mana.current = min(user.mana.max, user.mana.current + mana_drain)
                    result.hit = True
                    result.damage = health_drain
                    result.message = (
                        f"Top Off consumes {debt} Umbral Debt, draining {health_drain} health "
                        f"and {mana_drain} mana from {target.name}.\n"
                    )
                    return result
            except (AttributeError, KeyError, TypeError, ValueError):
                pass
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

        fortune_bonus = 0.0
        smash_and_grab = False
        if self.name in promotion_kits.RISKY_LUCK_ACTIONS:
            try:
                from src.core.classes import promotion_kits

                fortune_bonus, fortune_msg = (
                    promotion_kits.consume_fortune_for_risky_action(user, self.name)
                )
                msg += fortune_msg
            except Exception:
                fortune_bonus = 0.0
        result.extra["fortune_bonus"] = fortune_bonus

        if self.weapon:
            damage_mod = self.dmg_mod
            smash_and_grab = bool(
                self.name == "Mug"
                and "Smash and Grab" in getattr(user, "spellbook", {}).get("Skills", {})
            )
            strike_count = 3 if smash_and_grab else self._strikes
            if smash_and_grab:
                damage_mod = 0.60
            status_bonus = self._target_status_damage_multiplier or {}
            status_name = str(status_bonus.get("status", ""))
            target_status = getattr(target, "status_effects", {}).get(status_name)
            if status_name and getattr(target_status, "active", False):
                damage_mod *= float(status_bonus.get("multiplier", 1.0))

            # Build weapon_damage kwargs
            wd_kwargs: dict[str, Any] = {
                "cover": cover,
                "dmg_mod": damage_mod,
                "use_offhand": self._use_offhand,
                "accuracy_modifier": fortune_bonus,
            }
            try:
                from src.core.classes import promotion_kits

                accuracy_bonus = promotion_kits.ki_accuracy_bonus(user, self.name)
                if accuracy_bonus:
                    wd_kwargs["accuracy_modifier"] += accuracy_bonus
            except Exception:
                pass
            if self._ignore_armor:
                wd_kwargs["ignore"] = True
            if self._guaranteed_hit:
                wd_kwargs["hit"] = True
            if self._crit_override is not None:
                wd_kwargs["crit"] = self._crit_override
            if self._intel_dmg_mod:
                wd_kwargs["dmg_mod"] = max(self.dmg_mod, user.stats.intel / 15)
                if self.name == "Imbue Weapon":
                    try:
                        from src.core.classes import mage_mechanics

                        potency = mage_mechanics.arcane_potency_multiplier(user)
                        wd_kwargs["dmg_mod"] = 1 + (
                            (wd_kwargs["dmg_mod"] - 1) * potency
                        )
                    except Exception:
                        pass

            hit = False
            hit_count = 0
            crit = 1
            total_damage = 0
            damage_instances = []
            quick_recharge_started = False
            try:
                from src.core.classes import promotion_kits

                quick_recharge_started = promotion_kits.begin_multi_hit_weave(
                    user,
                    strike_count,
                )
            except Exception:
                quick_recharge_started = False
            try:
                for strike_index in range(strike_count):
                    if self._repeat_until_miss:
                        wd_kwargs["accuracy_modifier"] = -(
                            strike_index * self._accuracy_penalty_per_strike
                        )
                    elif smash_and_grab:
                        wd_kwargs["accuracy_modifier"] = -(0.10 * strike_index)
                    hp_before = target.health.current if target is not None else 0
                    user._last_weapon_primary_damage = None
                    user._last_weapon_primary_damage_instances = []
                    use_str, h, c = user.weapon_damage(target, **wd_kwargs)
                    if not h:
                        try:
                            from src.core.classes import class_rings

                            if class_rings.loaded_dice_succeeds(user):
                                use_str += "Loaded Dice turns the failed risky attack.\n"
                                retry_str, h, c = user.weapon_damage(target, **wd_kwargs)
                                use_str += retry_str
                        except Exception:
                            pass
                    msg += use_str
                    if h:
                        hit = True
                        hit_count += 1
                        crit = max(crit, c)
                        if target is not None:
                            primary_damage = getattr(
                                user,
                                "_last_weapon_primary_damage",
                                None,
                            )
                            if primary_damage is None:
                                primary_damage = max(
                                    0,
                                    hp_before - target.health.current,
                                )
                            total_damage += max(0, int(primary_damage))
                            strike_instances = list(
                                getattr(
                                    user,
                                    "_last_weapon_primary_damage_instances",
                                    (),
                                )
                                or ()
                            )
                            if strike_instances:
                                for value in strike_instances:
                                    instance_damage = max(0, int(value))
                                    if instance_damage > 0:
                                        damage_instances.append(instance_damage)
                            elif primary_damage > 0:
                                damage_instances.append(int(primary_damage))
                    if self._repeat_until_miss and not h:
                        break
                    if target is not None and not target.is_alive():
                        break
            finally:
                if quick_recharge_started:
                    promotion_kits.end_multi_hit_weave(user)

            result.hit = hit
            result.crit = crit if crit > 1 else None
            result.damage = total_damage
            result.extra["damage_instances"] = damage_instances
            result.extra["hit_count"] = hit_count
        else:
            hit = True
            crit = 1

        # Execute composed effects
        if hit:
            result.extra["last_damage"] = result.damage
            result.extra["last_crit"] = crit
            result.extra["dmg_mod"] = (
                wd_kwargs["dmg_mod"] if self.weapon else self.dmg_mod
            )
            effect_target = user if self._self_target else target
            for effect in self._effects:
                try:
                    effect.apply(user, effect_target, result)
                except Exception:
                    continue
            if (
                smash_and_grab
                and result.extra.get("hit_count", 0) >= 2
                and target.is_alive()
            ):
                import random

                if "Stun" not in getattr(target, "status_immunity", ()) and random.random() < 0.25:
                    if target.apply_stun(2, source="Smash and Grab", applier=user):
                        result.effects_applied["Status"].append("Stun")
                        result.extra.setdefault("messages", []).append(
                            f"{target.name} is knocked unconscious by Smash and Grab.\n"
                        )
            if self.weapon and target is not None:
                try:
                    from src.core.classes import pathfinder

                    pathfinder.enhance_melee_bleed(user, target)
                except Exception:
                    pass

            # Collect messages generated by effects
            for emsg in result.extra.get("messages", []):
                msg += emsg
            if (
                self.name == "Life Tap"
                and result.extra.get("gained_amount", 0)
                and "Mystical Vitality" in getattr(user, "spellbook", {}).get("Skills", {})
            ):
                # Status durations tick at the start of a turn, so three stored
                # ticks provide the next two complete player turns.
                user.mystical_vitality_turns = 3
                msg += "Mystical Vitality reduces spell costs for 2 turns.\n"

            if self.name.startswith("Mortal Strike"):
                try:
                    from src.core.classes import paladin

                    msg += paladin.trigger_penalization(user)
                except (AttributeError, KeyError, TypeError, ValueError):
                    pass
            if (
                self.name == "Backstab"
                and crit > 1
                and target is not None
                and target.is_alive()
                and "Cutthroat" in user.spellbook.get("Skills", {})
                and "Death" not in getattr(target, "status_immunity", ())
            ):
                import random

                if random.random() < 0.25:
                    target.health.current = 0
                    msg += f"Cutthroat instantly kills {target.name}.\n"

        try:
            from src.core.classes import promotion_kits

            if self.name == "Shield Slam" and hit:
                msg += promotion_kits.tower_offense_after_shield_slam(
                    user,
                    result.damage,
                )
            if self.name == "Battle Cry" and hit:
                msg += promotion_kits.battle_determination_after_cry(user)
            if self.name in promotion_kits.DEATH_MARK_SETUP_ABILITIES and target is not None:
                status_applied = bool(getattr(user, "_death_mark_toxin_status", False))
                status_applied = status_applied or any(result.effects_applied.values())
                msg += promotion_kits.resolve_death_mark_setup(
                    user,
                    target,
                    self.name,
                    hit=bool(result.hit),
                    status_applied=status_applied,
                )
            if self.name == "Inspect" and target is not None and result.hit:
                msg += promotion_kits.record_inspect(user, target)
            if self.name == "Exploit Weakness" and target is not None and result.hit:
                msg += promotion_kits.add_revelation(user, target, 1, "Exploit Weakness")
                msg += promotion_kits.gain_case_progress(
                    user,
                    getattr(target, "enemy_typ", None),
                    2,
                    "Exploit Weakness",
                )
            if self.name in promotion_kits.RISKY_LUCK_ACTIONS:
                if self.name in promotion_kits.STATUS_LUCK_ACTIONS:
                    luck_success = any(result.effects_applied.values())
                else:
                    luck_success = bool(result.extra.get("luck_success", hit))
                msg += promotion_kits.finish_fortune_payoff(user, luck_success)
                if luck_success:
                    msg += promotion_kits.resolve_misfortune_payoff(
                        user,
                        target,
                        result.damage,
                        self.name,
                        result=result,
                    )
                msg += promotion_kits.record_luck_roll(
                    user,
                    luck_success,
                    self.name,
                )
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
        required_item: str | None = None,
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
        self._required_item = required_item

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

        from src.core.classes import class_rings, promotion_kits

        if self._required_item:
            from ...items import use_reusable_tool

            used, item_message = use_reusable_tool(user, self._required_item)
            if not used:
                return item_message
        else:
            item_message = ""

        if not fam:
            user.mana.current -= self.cost

        # If no status is being applied (e.g. SmokeScreen), just pay cost
        if self._status_name is None:
            return item_message

        fmt = {"user": user.name, "target": target.name if target else ""}

        # Action message (always shown, e.g. "X howls at the moon.")
        prefix = ""
        if self._action_message:
            prefix = self._action_message.format(**fmt)

        # Ice Block / tunnel check
        if any([target.magic_effects["Ice Block"].active,
                getattr(target, "tunnel", False)]):
            return item_message + prefix + "It has no effect.\n"

        # Flying check (physical effects like Prone)
        if self._check_flying and getattr(target, "flying", False):
            return item_message + prefix + self._messages.get("immune", "").format(**fmt)

        # Disarmable check
        if self._check_disarmable:
            if not hasattr(target, "can_be_disarmed") or not target.can_be_disarmed():
                return item_message + prefix + self._messages.get("immune", "").format(**fmt)

        effects_dict = (target.physical_effects if self._physical
                        else target.status_effects)

        # Immunity check (for status_effects only)
        if not self._physical:
            if target.has_status_protection(self._status_name):
                return item_message + prefix + self._messages.get("immune", "").format(**fmt)

        # Already active check — either skip or extend
        if effects_dict[self._status_name].active:
            if self._extend_if_active > 0:
                effects_dict[self._status_name].duration += self._extend_if_active
                return item_message + prefix + self._messages.get("success", "").format(**fmt)
            if self._skip_if_active:
                return item_message + prefix + self._messages.get("already", "").format(**fmt)

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
        elif (
            not self._physical
            and self._status_name
            in {"Stun", "Sleep", "Silence", "Blind", "Stupefy", "Stone"}
        ):
            # Make WIS/CHA matter broadly for resisting control effects even if
            # the YAML entry didn't explicitly opt into luck-based resistance.
            # (Luck is derived from WIS/CHA via Character.check_mod("luck").)
            target_val += target.check_mod("luck", enemy=user, luck_factor=20)
        if (
            self._status_name == "Blind"
            and "Blind Fighting" in target.spellbook.get("Skills", {})
        ):
            target_val += max(3, int(getattr(target.stats, "wisdom", 10)) // 2)
        if bool(getattr(target, "mage_refueling", False)):
            target_val //= 2

        fortune_bonus = 0.0
        fortune_message = ""
        if self.name in promotion_kits.RISKY_LUCK_ACTIONS:
            fortune_bonus, fortune_message = (
                promotion_kits.consume_fortune_for_risky_action(user, self.name)
            )
            actor_val += max(1, int(max(1, actor_val) * fortune_bonus)) if fortune_bonus else 0

        contest_success = actor_val > target_val
        if (self._status_name == "Stun") and (not self._physical):
            contest_success = target.stun_contest_success(user, actor_val, target_val)
        if (
            not contest_success
            and self.name in promotion_kits.RISKY_LUCK_ACTIONS
            and class_rings.loaded_dice_succeeds(user, rng=_rng)
        ):
            contest_success = True
            fortune_message += "Loaded Dice turns the failed status attempt.\n"

        if not contest_success:
            payoff_message = promotion_kits.finish_fortune_payoff(user, False)
            if self.name in promotion_kits.RISKY_LUCK_ACTIONS:
                payoff_message += promotion_kits.record_luck_roll(
                    user,
                    False,
                    self.name,
                )
            return (
                item_message
                + prefix
                + fortune_message
                + self._messages.get("fail", "").format(**fmt)
                + payoff_message
            )

        if self._duration_stat:
            stat_val = getattr(user.stats, self._duration_stat, 10)
            dur = max(self._duration_min, stat_val // self._duration_divisor)
        else:
            dur = self._duration
        if self.name in promotion_kits.RISKY_LUCK_ACTIONS:
            dur += int(promotion_kits.combat_state(user).get("misfortune", 0) or 0)

        if (self._status_name == "Stun") and (not self._physical):
            contest_success = target.apply_stun(dur, source=self.name, applier=user)
        else:
            effects_dict[self._status_name].active = True
            if dur < 0:
                effects_dict[self._status_name].duration = dur
            else:
                effects_dict[self._status_name].duration = max(
                    dur,
                    effects_dict[self._status_name].duration,
                )
            try:
                user._emit_status_event(
                    target,
                    self._status_name,
                    applied=True,
                    duration=effects_dict[self._status_name].duration,
                    source=self.name,
                )
            except Exception:
                pass

        if not contest_success:
            promotion_kits.finish_fortune_payoff(user, False)
            return (
                item_message
                + prefix
                + fortune_message
                + self._messages.get("fail", "").format(**fmt)
            )

        message = prefix + self._messages.get("success", "").format(**fmt)
        if self.name == "Goad":
            message += promotion_kits.build_resolve(user, 5, "Goad")
        if self.name == "Disarm" and "For Good Measure" in user.spellbook.get("Skills", {}):
            offhand = getattr(user, "equipment", {}).get("OffHand")
            if getattr(offhand, "typ", None) == "Weapon" and target.is_alive():
                follow_up, _hit, _crit = user.weapon_damage(
                    target,
                    attack_slots=("OffHand",),
                )
                message += "For Good Measure follows through with the off hand.\n"
                message += follow_up

        payoff_message = promotion_kits.finish_fortune_payoff(user, True)
        if self.name in promotion_kits.RISKY_LUCK_ACTIONS:
            payoff_message += promotion_kits.resolve_misfortune_payoff(
                user,
                target,
                0,
                self.name,
            )
            payoff_message += promotion_kits.record_luck_roll(
                user,
                True,
                self.name,
            )
        return item_message + fortune_message + message + payoff_message
