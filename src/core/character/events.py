"""Character combat-event emission behavior."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import Character


class CharacterEventsMixin:
    def abilities_suppressed(self) -> bool:
        return bool(self.status_effects["Silence"].active or getattr(self, "anti_magic_active", False))

    def _emit_damage_event(
        self,
        target: Character,
        damage: int,
        damage_type: str = "Physical",
        is_critical: bool = False,
        *,
        source: str = "Unknown",
        attack_source: str | None = None,
        weapon_name: str | None = None,
        weapon_slot: str | None = None,
        weapon_type: str | None = None,
        ability_name: str | None = None,
        item_name: str | None = None,
    ) -> None:
        """Helper to emit damage dealt events."""
        if damage and damage > 0:
            try:
                from ..classes import class_rings

                reduced_damage = class_rings.reduce_major_hit(target, damage)
                if reduced_damage < damage:
                    target.health.current = min(target.health.max, target.health.current + (damage - reduced_damage))
                    damage = reduced_damage
            except Exception:
                pass
            if hasattr(self, "record_damage_dealt"):
                self.record_damage_dealt(damage)
            if hasattr(target, "record_damage_taken"):
                target.record_damage_taken(damage)
            if hasattr(self, "record_archdruid_damage_dealt"):
                self.record_archdruid_damage_dealt(damage, damage_type)
            if hasattr(target, "record_archdruid_damage_taken"):
                target.record_archdruid_damage_taken(damage, damage_type)
            try:
                from ..classes import class_rings, promotion_kits

                class_rings.record_damage_dealt(self, damage, damage_type)
                class_rings.build_guard_meter(target, damage)
                class_rings.trigger_umbral_debt(self)
                class_rings.divine_intervention(target)
                promotion_kits.record_damage_event(
                    self,
                    target,
                    damage,
                    damage_type,
                    metadata={
                        "source": source,
                        "attack_source": attack_source,
                        "weapon_name": weapon_name,
                        "weapon_slot": weapon_slot,
                        "weapon_type": weapon_type,
                        "ability_name": ability_name,
                        "item_name": item_name,
                        "is_critical": is_critical,
                        "crit": is_critical,
                    },
                )
                promotion_kits.record_damage_taken(target, damage, damage_type)
            except Exception:
                pass
        try:
            from ..events.event_bus import get_event_bus, create_combat_event, EventType
            event_bus = get_event_bus()
            event_data = {
                "damage": damage,
                "damage_type": damage_type,
                "is_critical": is_critical,
                "crit": is_critical,
                "source": source,
            }
            optional_payload = {
                "attack_source": attack_source,
                "weapon_name": weapon_name,
                "weapon_slot": weapon_slot,
                "weapon_type": weapon_type,
                "ability_name": ability_name,
                "item_name": item_name,
            }
            event_data.update({key: value for key, value in optional_payload.items() if value})
            event_bus.emit(create_combat_event(
                EventType.DAMAGE_DEALT if damage > 0 else EventType.MISS,
                actor=self,
                target=target,
                **event_data,
            ))
        except Exception:
            pass

    def _emit_healing_event(self, amount: int, source: str = "Unknown") -> None:
        """Helper to emit healing events."""
        if amount and amount > 0 and hasattr(self, "record_archdruid_healing_done"):
            self.record_archdruid_healing_done(amount)
        if amount and amount > 0:
            try:
                from ..classes import class_rings

                echo = class_rings.shared_recovery_amount(self, amount)
                familiar = getattr(self, "familiar", None)
                if echo and familiar is not None and familiar.is_alive():
                    familiar.health.current = min(familiar.health.max, familiar.health.current + echo)
            except Exception:
                pass
            try:
                if getattr(self, "power_up", False) and "Eternal Conduit" in getattr(self, "spellbook", {}).get("Skills", {}):
                    echo = max(1, int(amount * 0.25))
                    for summon in getattr(self, "summons", {}).values():
                        if summon.is_alive():
                            summon.health.current = min(summon.health.max, summon.health.current + echo)
                    familiar = getattr(self, "familiar", None)
                    if familiar is not None and familiar.is_alive():
                        familiar.health.current = min(familiar.health.max, familiar.health.current + echo)
            except Exception:
                pass
        try:
            from ..events.event_bus import get_event_bus, create_combat_event, EventType
            event_bus = get_event_bus()
            event_bus.emit(create_combat_event(
                EventType.HEALING_DONE,
                actor=self,
                target=self,
                amount=amount,
                source=source
            ))
        except Exception:
            pass

    def _emit_status_event(self, target: Character, status_name: str, applied: bool, duration: int = 0, source: str = "Unknown") -> None:
        """Helper to emit status effect events."""
        if applied:
            try:
                from ..classes import archdruid
                archdruid.record_status_applied(self, target, status_name)
            except Exception:
                pass
        try:
            from ..events.event_bus import get_event_bus, create_combat_event, EventType
            event_bus = get_event_bus()
            event_bus.emit(create_combat_event(
                EventType.STATUS_APPLIED if applied else EventType.STATUS_REMOVED,
                actor=self,
                target=target,
                status_name=status_name,
                duration=duration,
                source=source
            ))
        except Exception:
            pass

    def _emit_status_tick_event(
        self,
        target: Character,
        status_name: str,
        amount: int,
        kind: str,
        source: str = "Unknown",
    ) -> None:
        """Emit a status tick (damage/heal) event for analytics/tests."""
        if kind == "damage" and amount and amount > 0 and hasattr(target, "record_damage_taken"):
            target.record_damage_taken(amount)
        if kind == "damage" and amount and amount > 0 and hasattr(target, "record_archdruid_damage_taken"):
            damage_type = "Poison" if status_name == "Poison" else status_name
            target.record_archdruid_damage_taken(amount, damage_type)
        if kind == "healing" and amount and amount > 0 and hasattr(self, "record_archdruid_healing_done"):
            self.record_archdruid_healing_done(amount)
        try:
            from ..events.event_bus import get_event_bus, create_combat_event, EventType
            event_bus = get_event_bus()
            event_bus.emit(create_combat_event(
                EventType.STATUS_TICK,
                actor=self,
                target=target,
                status_name=status_name,
                amount=amount,
                kind=kind,
                source=source,
            ))
        except Exception:
            pass
