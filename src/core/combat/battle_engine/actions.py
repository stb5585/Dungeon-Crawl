"""Battle action execution helpers."""

from __future__ import annotations

from copy import deepcopy
import inspect
import random
import re
from typing import TYPE_CHECKING

from ... import items
from ...classes import ability_mechanics, astromancer, class_rings, promotion_kits, wizard
from ...constants import SPECIAL_ATTACK_LUCK_FACTOR, SPECIAL_ATTACK_ROLL_MAX
from ...events.event_bus import EventType, create_combat_event
from ..actor_cycle import initiative_rating
from ..combat_result import CombatResult

if TYPE_CHECKING:
    from collections.abc import Callable

    from ...character import Character


STOLEN_SCROLL_CHOICE_PREFIX = "__scroll__:"


class BattleActionMixin:
    def player_has_sight(self) -> bool:
        """Check if the player can see enemy details (Seeker/Inquisitor/Vision)."""
        return any([
            self.player.cls.name in ["Inquisitor", "Seeker"],
            getattr(self.player.equipment.get("Pendant"), "mod", None) == "Vision",
            getattr(self.player, "sight", False),
        ])

    def show_enemy_details(self) -> bool:
        """Return True if enemy details should be visible (has sight + not boss/waitress)."""
        return all([
            self.player_has_sight(),
            not self.boss,
            self.enemy.name != "Waitress",
        ])

    # ── Private action helpers ───────────────────────────────────────

    def _execute_attack(self) -> str:
        """Execute a basic/special attack."""
        self._event_bus.emit(create_combat_event(
            EventType.ATTACK,
            actor=self.attacker,
            target=self.defender,
            is_special=False,
            source="weapon_damage",
            attack_source="weapon",
            weapon_name=getattr(self.attacker.equipment.get("Weapon"), "name", None),
            weapon_slot="Weapon",
            weapon_type=getattr(self.attacker.equipment.get("Weapon"), "subtyp", None),
        ))

        # Roll for special attack
        luck_mod = self.attacker.check_mod("luck", luck_factor=SPECIAL_ATTACK_LUCK_FACTOR)
        roll_max = max(1, SPECIAL_ATTACK_ROLL_MAX - luck_mod)
        if not random.randint(0, roll_max):
            try:
                result = self.attacker.special_attack(target=self.defender)
                self._event_bus.emit(create_combat_event(
                    EventType.ATTACK,
                    actor=self.attacker,
                    target=self.defender,
                    is_special=True,
                    source="special_attack",
                    attack_source="special_attack",
                ))
                return result
            except NotImplementedError:
                pass

        message, hit, damage = self.attacker.weapon_damage(self.defender)
        self._last_combat_result = CombatResult(
            action="Attack",
            actor=self.attacker,
            target=self.defender,
            hit=hit,
            damage=damage,
            message=message,
        )
        return message

    def _execute_flee(self) -> tuple[str, bool]:
        """Attempt to flee. Returns (message, success)."""
        hostile = self._fastest_living_hostile()
        self._event_bus.emit(create_combat_event(
            EventType.FLEE_ATTEMPT,
            actor=self.attacker,
            target=hostile,
        ))
        success, message = self.attacker.flee(hostile)
        return message, success

    def _fastest_living_hostile(self):
        """Return the fastest hostile, resolving equal ratings by authored slot."""
        living = self.encounter.living_members
        if not living:
            return self.encounter.primary_enemy
        return max(
            living,
            key=lambda member: (
                initiative_rating(member.enemy, self.player),
                -member.slot,
            ),
        ).enemy

    def _execute_defend(self) -> str:
        """Enter defensive stance."""
        self._event_bus.emit(create_combat_event(
            EventType.DEFEND,
            actor=self.attacker,
            target=self.defender,
        ))
        message = self.attacker.enter_defensive_stance(duration=1, source="Defend")
        if self.attacker == self.player:
            from ...classes import promotion_kits

            message += promotion_kits.build_resolve(
                self.player,
                10,
                "Defend",
            )
        return message

    def _execute_spell(self, choice: str | None) -> str:
        """Cast a spell. Handles silence check."""
        if self.attacker.abilities_suppressed():
            reason = "the anti-magic field" if getattr(self.attacker, "anti_magic_active", False) else "silence"
            return f"{self.attacker.name} cannot cast spells because of {reason}!\n"

        if choice and choice.startswith(STOLEN_SCROLL_CHOICE_PREFIX):
            return self._execute_stolen_scroll_spell(choice)

        if not choice or choice not in self.attacker.spellbook.get('Spells', {}):
            return f"{self.attacker.name} fumbles the spell.\n"

        spell = self.attacker.spellbook['Spells'][choice]
        if self.attacker.mana.current < spell.cost:
            return f"{self.attacker.name} does not have enough mana to cast {choice}!\n"

        self._event_bus.emit(create_combat_event(
            EventType.SPELL_CAST,
            actor=self.attacker,
            target=self.defender,
            spell_name=choice,
            ability_name=choice,
            source="spell",
        ))

        defender_was_alive = self.defender.is_alive()
        message = f"{self.attacker.name} casts {choice}.\n"
        cast_result = self._cast_spell_with_context(
            spell,
            self.attacker,
            self.defender,
        )
        if isinstance(cast_result, CombatResult):
            self._last_combat_result = deepcopy(cast_result)
        message += str(cast_result)
        if self.attacker == self.player:
            if (
                choice in {"Turn Undead", "TurnUndead", "Turn Undead 2", "TurnUndead2"}
                and defender_was_alive
                and not self.defender.is_alive()
                and "Pious Bounty" in self.player.spellbook.get("Skills", {})
            ):
                self.defender._pious_bounty_gold = True
            message += wizard.process_cast(self.player, spell, self.defender)
            if not self.defender.is_alive():
                message += self._record_player_natural_spell_kill(spell)
            if astromancer.is_astromancer(self.player) and astromancer.sign_for_spell(spell):
                astromancer.advance_constellation(self.player)
        return message

    def _execute_stolen_scroll_spell(self, choice: str) -> str:
        """Cast an inscribed stolen-spell scroll selected from the Spells menu."""
        scroll_name = choice.removeprefix(STOLEN_SCROLL_CHOICE_PREFIX)
        if not scroll_name:
            return f"{self.attacker.name} fumbles the spell.\n"
        if scroll_name not in self.attacker.inventory or not self.attacker.inventory[scroll_name]:
            return f"{self.attacker.name} can't find {scroll_name}.\n"

        scroll = self.attacker.inventory[scroll_name][0]
        if not isinstance(scroll, items.InscribedSpellScroll):
            return f"{scroll_name} is not a stolen spell scroll.\n"

        self._event_bus.emit(create_combat_event(
            EventType.ITEM_USE,
            actor=self.attacker,
            target=self.defender,
            item_name=scroll.name,
            item_type=getattr(scroll, "typ", ""),
            item_subtype=getattr(scroll, "subtyp", ""),
            source="stolen_spell_scroll",
        ))

        message = str(scroll.use(self.attacker, target=self.defender))
        if self.attacker == self.player:
            message += promotion_kits.gain_stolen_charge(self.player, "stolen spell scroll")
        return message

    def _record_player_natural_spell_kill(self, spell: object) -> str:
        if not astromancer.has_rune_system(self.player):
            return ""
        gained, sign, _chance = astromancer.maybe_award_rune(self.player, self.enemy, spell)
        if gained and sign:
            return f"{self.player.name} claims an {sign} rune.\n"
        return ""

    def _cast_spell_with_context(self, spell: object, caster: object, target: object) -> object:
        """Cast a spell, passing this engine only when the spell accepts it."""
        cast = getattr(spell, "cast")
        try:
            signature = inspect.signature(cast)
        except (TypeError, ValueError):
            return cast(caster, target=target)
        accepts_engine = any(
            parameter.kind == inspect.Parameter.VAR_KEYWORD
            or parameter.name == "battle_engine"
            for parameter in signature.parameters.values()
        )
        if accepts_engine:
            return cast(caster, target=target, battle_engine=self)
        return cast(caster, target=target)

    def _execute_runic_boost(self, choice: str | None) -> str:
        """Spend a rune to empower and cast a matching natural spell."""
        if self.attacker.abilities_suppressed():
            reason = "the anti-magic field" if getattr(self.attacker, "anti_magic_active", False) else "silence"
            return f"{self.attacker.name} cannot cast spells because of {reason}!\n"

        if self.attacker != self.player or not astromancer.has_rune_system(self.player):
            return f"{self.attacker.name} cannot shape runes.\n"

        if not choice or choice not in self.player.spellbook.get("Spells", {}):
            return f"{self.player.name} fumbles the rune pattern.\n"

        spell = self.player.spellbook["Spells"][choice]
        sign = astromancer.sign_for_spell(spell)
        if not sign:
            return f"{choice} cannot be empowered by the current rune lore.\n"
        if self.player.mana.current < spell.cost:
            return f"{self.player.name} does not have enough mana to cast {choice}!\n"
        if not astromancer.consume_rune(self.player, sign):
            return f"{self.player.name} has no {sign} runes.\n"

        floor = astromancer.runic_boost_floor(self.player, sign)
        prior_floor = getattr(self.player, "_runic_boost_floor", None)
        self.player._runic_boost_floor = floor
        try:
            message = f"{self.player.name} spends one {sign} rune to boost {choice}.\n"
            message += str(spell.cast(self.player, target=self.defender))
        finally:
            if prior_floor is None:
                try:
                    delattr(self.player, "_runic_boost_floor")
                except AttributeError:
                    pass
            else:
                self.player._runic_boost_floor = prior_floor

        message += wizard.process_cast(self.player, spell, self.defender)
        if not self.defender.is_alive():
            message += self._record_player_natural_spell_kill(spell)
        if astromancer.is_astromancer(self.player):
            astromancer.advance_constellation(self.player)
        return message

    def _execute_steal_as_well(self, choice: str | None) -> str:
        """Cast a selected spell or stolen-spell scroll, then steal if damage lands."""
        if self.attacker != self.player:
            return f"{self.attacker.name} cannot use Steal As Well.\n"
        if self.attacker.abilities_suppressed():
            reason = "the anti-magic field" if getattr(self.attacker, "anti_magic_active", False) else "silence"
            return f"{self.attacker.name} cannot use Steal As Well because of {reason}!\n"
        if not choice:
            return f"{self.attacker.name} fumbles the spell theft.\n"

        from ... import abilities, items

        message = f"{self.attacker.name} weaves theft into {choice}.\n"
        before_hp = self.defender.health.current
        if choice in self.attacker.spellbook.get("Spells", {}):
            spell = self.attacker.spellbook["Spells"][choice]
            if self.attacker.mana.current < getattr(spell, "cost", 0):
                return f"{self.attacker.name} does not have enough mana to cast {choice}!\n"
            message += str(self._cast_spell_with_context(spell, self.attacker, self.defender))
        elif choice in self.attacker.inventory and self.attacker.inventory[choice]:
            scroll = self.attacker.inventory[choice][0]
            if not isinstance(scroll, items.InscribedSpellScroll):
                return f"{choice} is not a stolen spell scroll.\n"
            message += str(scroll.use(self.attacker, target=self.defender))
        else:
            return f"{self.attacker.name} cannot find {choice}.\n"

        if before_hp > self.defender.health.current:
            steal_skill = self.attacker.spellbook.get("Skills", {}).get("Steal") or abilities.Steal()
            message += str(steal_skill.use(self.attacker, target=self.defender))
        else:
            message += "The spell fails to open a path for theft.\n"
        return message

    @staticmethod
    @staticmethod
    def _skill_uses_resolve(skill: object) -> bool:
        if getattr(skill, "resource_type", None) == "Resolve":
            return True
        skill_name = str(getattr(skill, "name", "") or "")
        resolve_names = {entry["name"] for entry in promotion_kits.RESOLVE_SPEND_ABILITIES}
        surge_names = {entry["name"] for entry in promotion_kits.RESOLVE_SURGES}
        return skill_name in resolve_names or skill_name in surge_names

    def _execute_skill(
        self,
        choice: str | None,
        slot_machine_callback: Callable | None = None,
    ) -> str:
        """Use a skill. Handles silence, Jump, Charge, Smoke Screen, etc."""
        if not choice:
            return f"{self.attacker.name} does nothing.\n"

        # Handle "Remove Shield" alias for Mana Shield
        if choice == "Remove Shield":
            choice = "Mana Shield"

        skills = self.attacker.spellbook.get('Skills', {})
        if choice not in skills:
            return f"{self.attacker.name} does not know {choice}.\n"

        skill = skills[choice]
        # Charging skills deduct mana at start, then must be allowed to continue
        # even when the user is at 0 mana or becomes silenced (otherwise the
        # charge can never resolve). Resolve actions spend shield pressure, not
        # voice or spellcasting focus, so silence should not suppress them.
        already_charging = bool(getattr(skill, "charging", False))
        is_resolve_skill = self._skill_uses_resolve(skill)
        is_class_resource_skill = (
            is_resolve_skill
            or getattr(skill, "resource_type", None) == "Oath Conviction"
        )
        if (
            self.attacker.abilities_suppressed()
            and not already_charging
            and not is_class_resource_skill
        ):
            reason = "the anti-magic field" if getattr(self.attacker, "anti_magic_active", False) else "silence"
            return f"{self.attacker.name} cannot use skills because of {reason}!\n"

        if (
            not already_charging
            and not is_class_resource_skill
            and self.attacker.mana.current < skill.cost
        ):
            return f"{self.attacker.name} does not have enough mana to use {choice}!\n"

        self._event_bus.emit(create_combat_event(
            EventType.SKILL_USE,
            actor=self.attacker,
            target=self.defender,
            skill_name=skill.name,
            ability_name=skill.name,
            source="resolve" if is_resolve_skill else "skill",
        ))

        message = f"{self.attacker.name} uses {skill.name}.\n"

        # ── Special skill handling ───────────────────────────────────
        if skill.name == "Smoke Screen":
            if self.attacker is self.player:
                consumed, smoke_message = items.consume_smoke_bomb(self.attacker)
                if not consumed:
                    return smoke_message
                message += smoke_message
            hostile = self._fastest_living_hostile()
            message += skill.use(self.attacker, target=hostile)
            perceived = any(
                getattr(member.enemy, "sight", False)
                and not member.enemy.status_effects["Blind"].active
                for member in self.encounter.living_members
            )
            attempted, flee_str = self.attacker.flee(hostile, smoke=True)
            if not perceived:
                self.flee = True
                if not attempted:
                    flee_str = (
                        f"{self.attacker.name} disappears in a cloud of smoke."
                    )
            else:
                self.flee = False
                flee_str = f"{hostile.name} sees through the smoke."
            message += flee_str
            if self.flee and hasattr(self.player, "record_flee"):
                self.player.record_flee()

        elif skill.name == "Slot Machine":
            if slot_machine_callback:
                message += skill.use(
                    self.attacker,
                    target=self.defender,
                    slot_machine_callback=slot_machine_callback,
                )
            else:
                message += skill.use(self.attacker, target=self.defender)

        elif skill.name in ["Doublecast", "Triplecast"]:
            message += skill.use(self.attacker, self.defender, game=self.game)

        elif "Jump" in skill.name:
            charge_time = skill.get_charge_time() if hasattr(skill, "get_charge_time") else 1
            continuing_charge = already_charging and int(getattr(skill, "charge_turns", 0) or 0) > 1
            if charge_time > 0 and (not already_charging or continuing_charge):
                self.attacker.class_effects["Jump"].active = True
                message = ""
            message += skill.use(self.attacker, target=self.defender)
            self.attacker.class_effects["Jump"].active = bool(getattr(skill, "charging", False))
            owner_id = self._actor_id_for(self.attacker)
            if getattr(skill, "charging", False):
                member = self._member_for_character(self.defender)
                self.pending_actions[owner_id] = {
                    "action": "Use Skill",
                    "choice": choice,
                    "ability": skill,
                    "target_id": member.combatant_id if member else None,
                    "policy": getattr(skill, "target_loss_policy", "locked"),
                }
            else:
                self.pending_actions.pop(owner_id, None)

        elif hasattr(skill, 'get_charge_time') and skill.get_charge_time() > 0:
            # Charging abilities (Charge, Crushing Blow, etc.)
            message += skill.use(self.attacker, target=self.defender)
            if getattr(skill, 'charging', False):
                self.charging_ability = (self.attacker, choice, skill)
                member = self._member_for_character(self.defender)
                owner_id = self._actor_id_for(self.attacker)
                self.pending_actions[owner_id] = {
                    "action": "Use Skill",
                    "choice": choice,
                    "ability": skill,
                    "target_id": member.combatant_id if member else None,
                    "policy": getattr(skill, "target_loss_policy", "locked"),
                }
            else:
                # Charge completed this turn
                self.charging_ability = None
                self.pending_actions.pop(self._actor_id_for(self.attacker), None)

        else:
            message += str(skill.use(self.attacker, target=self.defender))

        return message

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

        self._event_bus.emit(create_combat_event(
            EventType.ITEM_USE,
            actor=self.attacker,
            target=target,
            item_name=itm.name,
            item_type=getattr(itm, "typ", ""),
            item_subtype=getattr(itm, "subtyp", ""),
            source="item",
        ))

        message = str(itm.use(self.attacker, target=target))
        if isinstance(itm, items.Potion):
            message += ability_mechanics.trigger_drunken_brawler(self.attacker)
        return message

    def _execute_summon(self, choice: str | None) -> tuple[str, bool, Character | None]:
        """Summon a companion. Returns (message, success, summon_character)."""
        summoner = self.player
        if summoner.abilities_suppressed():
            reason = "the anti-magic field" if getattr(summoner, "anti_magic_active", False) else "being silenced"
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
        self.summon = summon
        self.summon_active = True
        self.player.active_summon_name = summon.name
        self.attacker = summon
        self.defender = self._focused_enemy()
        self.available_actions = self._available_actions()
        costs = []
        if mana_cost:
            costs.append(f"{mana_cost} MP")
        if gold_cost:
            costs.append(f"{gold_cost} gold")
        cost_text = f" ({', '.join(costs)})" if costs else ""
        message = f"{summoner.name} summons {summon.name} to aid them in combat{cost_text}.\n"
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

        message = f"{self.player.name} recalls {self.summon.name}.\n"
        self.summon_active = False
        self.summon = None
        self.player.active_summon_name = None
        self.attacker = self.player
        self.defender = self._focused_enemy()
        self.available_actions = self._available_actions()
        return message, True

    def _execute_totem(self) -> str:
        """Use the Totem skill."""
        skills = self.attacker.spellbook.get("Skills", {})
        totem_skill = skills.get("Totem")
        if not totem_skill:
            for sk in skills.values():
                if getattr(sk, "name", "") == "Totem":
                    totem_skill = sk
                    break

        if totem_skill:
            return str(totem_skill.use(self.attacker, target=self.defender))
        else:
            return f"{self.attacker.name} does not know how to summon a totem.\n"
