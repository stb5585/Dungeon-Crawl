"""Item and ability serialization."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import abilities, items

if TYPE_CHECKING:
    from typing import Any


class ItemSerializer:
    """Serializes items to IDs and names."""

    @staticmethod
    def serialize(item) -> dict[str, Any]:
        """Convert item object to data dict."""
        if item is None or not hasattr(item, 'name'):
            return {'name': 'None', 'typ': 'None', 'subtyp': 'None'}

        data = {
            'name': item.name,
            'typ': getattr(item, 'typ', 'Unknown'),
            'subtyp': getattr(item, 'subtyp', 'None'),
            'class': item.__class__.__name__,
        }
        if item.__class__.__name__ == "InscribedSpellScroll":
            data["spell_class_name"] = getattr(item, "spell_class_name", "MagicMissile")
            data["charges"] = int(getattr(item, "charges", 1) or 1)
        elif (
            item.__class__.__name__ in {"LockpickKit", "WaterBladder", "ThrowingDaggers"}
            or getattr(item, "subtyp", None) == "Crossbow Bolts"
        ):
            default_charges = 10 if item.__class__.__name__ in {
                "WaterBladder", "ThrowingDaggers"
            } else 3
            data["charges"] = int(getattr(item, "charges", default_charges))
        return data

    @staticmethod
    def deserialize(data: dict[str, Any]):
        """Reconstruct item from data dict."""
        # Normalize typ for Accessory items (Ring/Pendant)
        typ = data.get('typ', 'Weapon')
        if typ == 'Accessory':
            # Determine if Ring or Pendant from class name
            class_name = data.get('class', '')
            if 'Ring' in class_name:
                typ = 'Ring'
            elif 'Pendant' in class_name:
                typ = 'Pendant'
            else:
                typ = 'Ring'  # Default to Ring

        if data.get('name') == 'None' or data.get('subtyp') == 'None':
            return items.remove_equipment(typ)

        # Try to find and instantiate the item class
        item_class_name = data.get('class')
        if item_class_name and hasattr(items, item_class_name):
            try:
                item_class = getattr(items, item_class_name)
                # Don't try to instantiate abstract base classes
                if item_class_name not in ['Item', 'Weapon', 'OffHand', 'Armor', 'Helmet', 'Accessory']:
                    if item_class_name == "InscribedSpellScroll":
                        return item_class(
                            data.get("spell_class_name", "MagicMissile"),
                            charges=data.get("charges"),
                        )
                    if (
                        item_class_name in {"LockpickKit", "WaterBladder", "ThrowingDaggers"}
                        or data.get("subtyp") == "Crossbow Bolts"
                    ):
                        default_charges = 10 if item_class_name in {
                            "WaterBladder", "ThrowingDaggers"
                        } else 3
                        return item_class(charges=data.get("charges", default_charges))
                    return item_class()
            except Exception:
                pass

        # Fallback: create empty equipment
        return items.remove_equipment(typ)


class AbilitySerializer:
    """Serializes abilities by class name to avoid ambiguity with variants."""

    @staticmethod
    def serialize(ability) -> str:
        """Convert ability to class name (e.g. 'Heal2' instead of 'Heal').

        Uses class name instead of display name to distinguish variants
        like Heal, Heal2, Heal3 which all have name='Heal'.
        """
        if ability is None:
            return ""
        # Support YAML-migrated abilities that carry their original class name
        if hasattr(ability, '_class_name'):
            return ability._class_name
        # Use class name for unambiguous serialization
        return ability.__class__.__name__

    @staticmethod
    def deserialize(name: str):
        """Reconstruct ability from class name or display name.

        Supports:
        - Class names: 'Heal', 'Heal2', 'Heal3' (unambiguous)
        - Display names: 'Heal' (ambiguous, returns first match)

        Prefers class name lookup for reliability.
        """
        if not name:
            return None

        # First try direct class name lookup (most reliable)
        if hasattr(abilities, name):
            try:
                attr = getattr(abilities, name)
                if hasattr(attr, '__call__'):
                    return attr()
            except Exception:
                pass

        # Fallback to display name lookup (may be ambiguous)
        for attr_name in dir(abilities):
            attr = getattr(abilities, attr_name)
            if hasattr(attr, '__call__'):
                try:
                    instance = attr()
                    if hasattr(instance, 'name') and instance.name == name:
                        return instance
                except Exception:
                    pass

        return None
