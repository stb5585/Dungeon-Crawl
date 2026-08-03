"""Data-driven Jump skill and modification behavior."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from src.core.character import Character
    from src.core.effects.base import Effect

from src.core.abilities import Skill


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

    _DEFAULT_UNLOCK_REQUIREMENTS: dict[str, dict[str, Any]] = {
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
        unlock_requirements: dict[str, dict[str, Any]] | None = None,
        modifications_defaults: dict[str, bool] | None = None,
        unlocked_defaults: dict[str, bool] | None = None,
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
        self.unlock_requirements: dict[str, dict[str, Any]] = dict(
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

    def get_max_active_modifications(
        self, user: Character | None = None
    ) -> int:
        """Return the global-level active-mod capacity, capped at five."""
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

        user_level = int(base_level)
        max_mods = min(1 + user_level // 15, 5)
        return max_mods

    def unlock_modification(self, mod_name: str) -> bool:
        if mod_name in self.unlocked_modifications:
            self.unlocked_modifications[mod_name] = True
            return True
        return False

    def check_and_unlock_level_modifications(
        self, user_level: Any, user_class: Any | None = None
    ) -> list[str]:
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

    def get_unlocked_modifications(self) -> list[str]:
        return [m for m, u in self.unlocked_modifications.items() if u]

    def get_active_count(self) -> int:
        return sum(1 for a in self.modifications.values() if a)

    def enforce_modification_limit(self, user: Character | None = None) -> list[str]:
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
        self, mod_name: str, active: bool, user: Character | None = None
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

    def get_active_modifications(self) -> list[str]:
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
    # Execute phase - delegates to composed effects
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
        target: Character | None = None,
        cover: bool = False,
        special: bool = False,
        **kwargs: Any,
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
