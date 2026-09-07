"""Item, summon, recall, and totem actions for the battle engine."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ... import items
from ...classes import (
    ability_mechanics,
    promotion_kits,
)
from ...events.event_bus import EventType, create_combat_event

if TYPE_CHECKING:
    from ...character import Character


class InventoryActionMixin:
    """Resolve consumables and deployable companion actions."""

    def _execute_item(self, choice: str | None) -> str:
        """Use an inventory item."""
        if not choice:
            return f"{self.attacker.name} fumbles with their items.\n"

        item_key = re.split(r"\s{2,}", choice)[0]
        if item_key not in self.attacker.inventory or not self.attacker.inventory[item_key]:
            return f"{self.attacker.name} can't find {item_key}.\n"

        itm = self.attacker.inventory[item_key][0]
        if isinstance(itm, type):
            itm = itm()
        target = self.attacker
        if itm.subtyp == "Scroll" and hasattr(itm, "spell"):
            if itm.spell.subtyp != "Support":
                target = self.defender

        self._event_bus.emit(
            create_combat_event(
                EventType.ITEM_USE,
                actor=self.attacker,
                target=target,
                item_name=itm.name,
                item_type=getattr(itm, "typ", ""),
                item_subtype=getattr(itm, "subtyp", ""),
                source="item",
            )
        )

        message = str(itm.use(self.attacker, target=target))
        if isinstance(itm, items.Potion):
            message += ability_mechanics.trigger_drunken_brawler(self.attacker)
        return message

    def _execute_summon(self, choice: str | None) -> tuple[str, bool, Character | None]:
        """Summon a companion. Returns (message, success, summon_character)."""
        summoner = self.player
        if summoner.abilities_suppressed():
            reason = (
                "the anti-magic field"
                if getattr(summoner, "anti_magic_active", False)
                else "being silenced"
            )
            return f"{summoner.name} cannot summon because of {reason}!\n", False, None

        summons = getattr(summoner, "summons", {}) or {}
        if not choice or choice not in summons:
            return f"{summoner.name} has nothing to summon.\n", False, None

        summon = summons[choice]
        mana_cost = self._summon_mana_cost(summon)
        gold_cost = self._summon_gold_cost(summon)
        if mana_cost and getattr(summoner.mana, "current", 0) < mana_cost:
            return f"{summoner.name} needs {mana_cost} MP to summon {summon.name}.\n", False, None
        if gold_cost and getattr(summoner, "gold", 0) < gold_cost:
            return f"{summoner.name} needs {gold_cost} gold to summon {summon.name}.\n", False, None
        if mana_cost:
            summoner.mana.current = max(0, summoner.mana.current - mana_cost)
        if gold_cost:
            summoner.gold = max(0, int(getattr(summoner, "gold", 0) or 0) - gold_cost)
        command_expiry = promotion_kits.clear_conduit_command(
            summoner,
            "is replaced",
        )
        self.summon = summon
        self.summon_active = True
        self.player.active_summon_name = summon.name
        combat = promotion_kits.combat_state(summoner)
        combat["fallen_xenid"] = None
        combat["fallen_xenid_conduit_loss"] = 0
        self.attacker = summon
        self.defender = self._focused_enemy()
        self.available_actions = self._available_actions()
        costs = []
        if mana_cost:
            costs.append(f"{mana_cost} MP")
        if gold_cost:
            costs.append(f"{gold_cost} gold")
        cost_text = f" ({', '.join(costs)})" if costs else ""
        message = command_expiry
        message += f"{summoner.name} summons {summon.name} to aid them in combat{cost_text}.\n"
        return message, True, summon

    @staticmethod
    @staticmethod
    def _summon_mana_cost(summon: Character) -> int:
        explicit = getattr(summon, "summon_mana_cost", None)
        if explicit is not None:
            try:
                return max(0, int(explicit))
            except (TypeError, ValueError):
                return 0
        if not hasattr(summon, "start_stats"):
            return 0
        try:
            pro_level = max(1, int(getattr(getattr(summon, "level", None), "pro_level", 1) or 1))
        except (TypeError, ValueError):
            pro_level = 1
        return pro_level * 8

    @staticmethod
    @staticmethod
    def _summon_gold_cost(summon: Character) -> int:
        try:
            return max(0, int(getattr(summon, "summon_gold_cost", 0) or 0))
        except (TypeError, ValueError):
            return 0

    def _execute_recall(self) -> tuple[str, bool]:
        """Recall a summoned companion. Returns (message, success)."""
        if not self.summon:
            return "No summon to recall.\n", False

        message = promotion_kits.clear_conduit_command(self.player, "is recalled")
        message += f"{self.player.name} recalls {self.summon.name}.\n"
        self.summon_active = False
        self.summon = None
        self.player.active_summon_name = None
        self.attacker = self.player
        self.defender = self._focused_enemy()
        self.available_actions = self._available_actions()
        return message, True

    def _execute_totem(self, aspect: str | None = None) -> str:
        """Use the Totem skill."""
        skills = self.attacker.spellbook.get("Skills", {})
        totem_skill = skills.get("Totem")
        if not totem_skill:
            for sk in skills.values():
                if getattr(sk, "name", "") == "Totem":
                    totem_skill = sk
                    break

        if totem_skill:
            return str(
                totem_skill.use(
                    self.attacker,
                    target=self.defender,
                    active_aspect=aspect or "Earth",
                )
            )
        else:
            return f"{self.attacker.name} does not know how to summon a totem.\n"
