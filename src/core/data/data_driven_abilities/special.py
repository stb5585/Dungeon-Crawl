"""Data-driven weapon, custom, and charging ability implementations."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from src.core.character import Character
    from src.core.effects.base import Effect

from src.core.abilities import Skill, Spell
from src.core.combat.combat_result import CombatResult


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
        effects: list[Effect] | None = None,
        school: str | None = None,
        rank: int | None = None,
        enemy_type_damage_modifiers: dict[str, float] | None = None,
    ):
        super().__init__(name, description, school=school)
        self.cost = cost
        self.dmg_mod = dmg_mod
        self.crit = crit
        self.subtyp = subtyp
        self.rank = rank
        self._effects: list[Effect] = effects or []
        self._enemy_type_damage_modifiers = enemy_type_damage_modifiers or {}

    def cast(
        self,
        caster: Character,
        target: Character,
        cover: bool = False,
        special: bool = False,
        fam: bool = False,
        **_kwargs: Any,
    ) -> str:
        if not (special or fam):
            caster.mana.current -= self.cost

        enemy_type = str(getattr(target, "enemy_typ", ""))
        type_modifier = float(self._enemy_type_damage_modifiers.get(enemy_type, 1.0))
        msg, hit, crit = caster.weapon_damage(
            target,
            dmg_mod=self.dmg_mod * type_modifier,
            cover=cover,
            use_offhand=False,
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
        effects: list[Effect] | None = None,
        school: str | None = None,
        rank: int | None = None,
    ):
        super().__init__(name, description, school=school)
        self.cost = cost
        self.dmg_mod = dmg_mod
        self.crit = crit
        self.subtyp = subtyp
        self.rank = rank
        self._effects: list[Effect] = effects or []

    def cast(
        self,
        caster: Character,
        target: Character,
        cover: bool = False,
        special: bool = False,
        fam: bool = False,
        **_kwargs: Any,
    ) -> str:
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
        self._charge_context: dict[str, Any] | None = None

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
    # Execute phase - delegates to composed effects
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
        target: Character | None = None,
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
