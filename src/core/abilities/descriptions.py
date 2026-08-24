"""Build player-facing ability details with learned modifiers."""

from __future__ import annotations

from copy import copy
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AbilityModification:
    """One learned modifier presented on an affected ability card."""

    name: str
    description: str


def is_embedded_modifier(ability: Any) -> bool:
    """Return whether an ability belongs inside another ability's description."""
    return bool(
        getattr(ability, "presentation_modifier", False)
        or getattr(ability, "modifies", ())
        or getattr(ability, "modifies_abilities", ())
        or getattr(ability, "modifies_school", None)
        or getattr(ability, "modifies_schools", ())
    )


def _modifier_applies(modifier: Any, ability: Any) -> bool:
    names = getattr(modifier, "modifies", ()) or getattr(
        modifier,
        "modifies_abilities",
        (),
    )
    if isinstance(names, str):
        names = (names,)
    if str(getattr(ability, "name", "")) in names:
        return True
    schools = getattr(modifier, "modifies_schools", ()) or ()
    school = str(getattr(modifier, "modifies_school", "") or "")
    if school:
        schools = (*schools, school)
    if not schools:
        return False
    ability_schools = {
        str(getattr(ability, "school", "") or ""),
        str(getattr(ability, "subtyp", "") or ""),
    }
    try:
        from src.core.classes import mage_mechanics

        resolved_school = mage_mechanics.school_from_ability(ability)
        if resolved_school:
            ability_schools.add(resolved_school)
    except Exception:
        pass
    return bool(set(str(value) for value in schools) & ability_schools)


def ability_modifications(character: Any, ability: Any) -> tuple[AbilityModification, ...]:
    """Return every learned modifier that affects an ability."""
    modifiers: list[AbilityModification] = []
    seen: set[str] = set()
    for book in getattr(character, "spellbook", {}).values():
        for candidate in getattr(book, "values", lambda: ())():
            name = str(getattr(candidate, "name", "") or "")
            if (
                name not in seen
                and is_embedded_modifier(candidate)
                and _modifier_applies(candidate, ability)
            ):
                modifiers.append(
                    AbilityModification(
                        name=name,
                        description=str(getattr(candidate, "description", "") or ""),
                    )
                )
                seen.add(name)
    if str(getattr(ability, "name", "")) in {
        "Magic Missile",
        "Magic Missile II",
        "Magic Missile III",
    }:
        try:
            from src.core.progression import has_talent

            if has_talent(character, "mage.arcane-fundamentals"):
                modifiers.insert(
                    0,
                    AbilityModification(
                        name="Guidance Upgrade",
                        description=(
                            "Magic Missile projectiles deal 20% more critical-strike "
                            "bonus damage."
                        ),
                    ),
                )
        except Exception:
            pass
    return tuple(modifiers)


def composed_description(character: Any, ability: Any) -> str:
    """Return an ability's base description without folding modifiers into it."""
    del character
    return str(getattr(ability, "description", "") or "")


def described_selection_text(character: Any, ability: Any) -> str:
    """Return compact ability details for combat selection overlays."""
    description = composed_description(character, ability)
    modifiers = ability_modifications(character, ability)
    if not modifiers:
        return description
    modification_lines = "\n".join(
        f"{modifier.name}: {modifier.description}" for modifier in modifiers
    )
    return f"{description}\n\nModifications\n{modification_lines}"


def presented_abilities(character: Any, bucket: str) -> list[Any]:
    """Return display copies with standalone modifiers attached to targets."""
    abilities = getattr(character, "spellbook", {}).get(bucket, {}) or {}
    presented = []
    for ability in abilities.values():
        if is_embedded_modifier(ability) or getattr(ability, "specials_hidden", False):
            continue
        display = copy(ability)
        display.description = composed_description(character, ability)
        display.presentation_modifications = ability_modifications(character, ability)
        presented.append(display)
    return presented
