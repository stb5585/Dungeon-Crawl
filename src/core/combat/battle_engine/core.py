"""Concrete UI-agnostic battle engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..battle_logger import BattleLogger
from ..initiative import determine_initiative
from ...classes import ability_mechanics, astromancer, bard, paladin, promotion_kits
from ...enemies.identity import remember_defeat_identity
from ...events.event_bus import EventType, create_combat_event, get_event_bus
from .actions import BattleActionMixin
from .models import ActionResult
from .outcomes import BattleOutcomeMixin
from .turns import BattleTurnMixin

if TYPE_CHECKING:
    from typing import Any, Callable

    from ...character import Character
    from ...player import Player


class BattleEngine(BattleTurnMixin, BattleActionMixin, BattleOutcomeMixin):
    """
    UI-agnostic combat engine.

    Holds all combat state and provides methods for each phase of a turn.
    UI layers drive the loop and call these methods; the engine never
    renders or reads input itself.
    """

    def __init__(
        self,
        player: Player,
        enemy: Character,
        tile: Any,
        game: Any | None = None,
        logger: BattleLogger | None = None,
    ):
        self.player: Player = player
        self.enemy: Character = enemy
        self.tile: Any = tile
        self.game: Any = game
        self.logger: BattleLogger = logger if logger else BattleLogger()
        remember_defeat_identity(self.enemy)

        self.flee: bool = False
        self.boss: bool = "Boss" in str(tile)

        self.summon_active: bool = False
        self.summon: Character | None = None
        self.player.active_summon_name = None

        self.attacker: Character | None = None
        self.defender: Character | None = None

        # Track charging abilities across turns
        self.charging_ability: tuple[Character, str, Any] | None = None  # (owner, name, skill_obj)
        self.delayed_spells: list[dict[str, Any]] = []

        # Available actions refreshed each turn
        self.available_actions: list = self._available_actions()

        self._event_bus = get_event_bus()

    def _is_class_ring_trial_enemy(self) -> bool:
        """Return whether this fight should use Class Ring trial bookkeeping."""
        return bool(
            getattr(self.enemy, "grandmaster_trial_enemy", False)
            or getattr(self.enemy, "class_ring_trial_enemy", False)
        )

    def _is_thieves_guild_trial_enemy(self) -> bool:
        """Return whether this fight is a Thieves Guild initiation trial."""
        return bool(getattr(self.enemy, "thieves_guild_trial_enemy", False))

    def _class_ring_trial_name(self) -> str:
        return str(getattr(self.enemy, "class_ring_trial_name", "Class Ring trial"))

    def _thieves_guild_trial_name(self) -> str:
        return str(getattr(self.enemy, "thieves_guild_trial_name", getattr(self.enemy, "name", "initiation trial")))

    def _no_healing_duel_active(self) -> bool:
        return bool(getattr(self.enemy, "class_ring_no_healing_duel", False))

    def _available_actions(self) -> list:
        if self.summon_active and self.attacker == self.summon and self.summon:
            options = getattr(self.summon, "options", None)
            if callable(options):
                return options()
            return ["Attack", "Recall"]
        actions = list(self.tile.available_actions(self.player))
        if astromancer.boostable_spells(self.player) and "Runic Boost" not in actions:
            insert_at = actions.index("Cast Spell") + 1 if "Cast Spell" in actions else len(actions)
            actions.insert(insert_at, "Runic Boost")
        if (
            self.attacker == self.player
            and "Tame" in getattr(self.player, "spellbook", {}).get("Skills", {})
            and not ability_mechanics.has_living_tamed_companion(self.player)
            and not self.player.abilities_suppressed()
            and "Tame" not in actions
        ):
            insert_at = actions.index("Attack") + 1 if "Attack" in actions else len(actions)
            actions.insert(insert_at, "Tame")
        if (
            self.attacker == self.player
            and ability_mechanics.available_beast_companion_commands(self.player)
            and not self.player.abilities_suppressed()
            and "Companion" not in actions
        ):
            insert_at = actions.index("Attack") + 1 if "Attack" in actions else len(actions)
            actions.insert(insert_at, "Companion")
        return actions

    def summoner_support_actions(self) -> list[str]:
        """Return limited owner actions available while a summon takes point."""
        if not self.summon_active or not self.summon:
            return []
        actions = []
        if getattr(self.player, "inventory", None):
            actions.append("Use Item")
        actions.append("Recall")
        skills = getattr(self.player, "spellbook", {}).get("Skills", {})
        for name in skills:
            if name in {"Heal Summon", "Raise Summon", "Conduit Command"} or name.startswith("Invoke "):
                actions.append("Use Skill")
                break
        return actions

    def summoner_support_skill_names(self) -> list[str]:
        """Return owner skill names valid through the active-summon Support menu."""
        skills = getattr(self.player, "spellbook", {}).get("Skills", {})
        return [
            name for name, skill in skills.items()
            if (
                name in {"Heal Summon", "Raise Summon", "Conduit Command"}
                or name.startswith("Invoke ")
            )
            and not getattr(skill, "passive", False)
        ]

    def execute_summoner_support_action(
        self,
        action: str,
        choice: str | None = None,
        slot_machine_callback: Callable | None = None,
    ) -> ActionResult:
        """Execute a constrained Summoner intervention during an active summon turn."""
        if not self.summon_active or not self.summon:
            result = ActionResult()
            result.message = "No active summon can be supported.\n"
            return result

        original_attacker = self.attacker
        original_defender = self.defender
        self.attacker = self.player
        self.defender = self.enemy
        try:
            result = self.execute_action(action, choice, slot_machine_callback)
        finally:
            if self.summon_active and self.summon:
                self.attacker = self.summon
                self.defender = self.enemy
            else:
                self.attacker = self.player
                self.defender = self.enemy
            self.available_actions = self._available_actions()
            if not self.summon_active and original_attacker is self.enemy:
                self.attacker = original_attacker
                self.defender = original_defender
        return result

    def _fail_no_healing_duel_if_healed(self, hp_before: int) -> str:
        """Fail the Berserker duel when the player restores HP during the bout."""
        if not self._no_healing_duel_active():
            return ""
        if self.player.health.current <= hp_before:
            return ""
        self.player.health.current = 0
        return "The No Healing Duel rejects restored life. You yield the bout.\n"

    # ── Lifecycle ────────────────────────────────────────────────────

    def start_battle(self) -> tuple[Character, Character]:
        """
        Initialise the battle: determine initiative, emit events, start logging.

        Returns:
            (first_actor, second_actor) — the initiative order.
        """
        self._clear_stale_charging_actions(self.player)
        self._clear_stale_charging_actions(self.enemy)
        self.player._final_assault_used = False
        self.player._last_stand_used = False
        self.player._foretell_snapshot = None
        self.player._rewind_snapshot = None
        promotion_kits.start_combat(self.player)
        self.attacker, self.defender = determine_initiative(self.player, self.enemy)
        self.available_actions = self._available_actions()

        self._event_bus.emit(create_combat_event(
            EventType.COMBAT_START,
            actor=self.player,
            target=self.enemy,
            initiative=self.attacker == self.player,
            boss=self.boss,
        ))

        self.logger.start_battle(
            self.player,
            self.enemy,
            initiative=self.attacker == self.player,
            boss=self.boss,
        )

        if hasattr(self.player, "record_bestiary_encounter"):
            self.player.record_bestiary_encounter(self.enemy, getattr(self.enemy, "enemy_typ", None))

        paladin.advance_encounter(self.player)
        paladin.clear_transient_marks(self.player)
        debuff_text = bard.apply_enemy_opening_debuffs(self.player, self.enemy)
        if debuff_text:
            self.logger.log_event("Bard Song", self.player, target=self.enemy, outcome=debuff_text)
        return self.attacker, self.defender

    def battle_continues(self) -> bool:
        """Return True while both combatants are alive and nobody fled."""
        return self.player.is_alive() and self.enemy.is_alive() and not self.flee
