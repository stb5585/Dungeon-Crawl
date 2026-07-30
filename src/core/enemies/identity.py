"""Preserve defeat credit across temporary enemy form changes."""


def _clean_text(value) -> str:
    return str(value or "").strip()


def remember_defeat_identity(enemy) -> None:
    """Snapshot the enemy identity that should receive kill and quest credit."""
    if enemy is None:
        return

    if not _clean_text(getattr(enemy, "_defeat_credit_name", None)):
        name = _clean_text(getattr(enemy, "name", None))
        if name:
            setattr(enemy, "_defeat_credit_name", name)

    if not _clean_text(getattr(enemy, "_defeat_credit_type", None)):
        enemy_type = _clean_text(getattr(enemy, "enemy_typ", None))
        if enemy_type:
            setattr(enemy, "_defeat_credit_type", enemy_type)


def defeat_credit_name(enemy) -> str:
    if enemy is None:
        return ""
    return _clean_text(getattr(enemy, "_defeat_credit_name", None)) or _clean_text(
        getattr(enemy, "name", None)
    )


def defeat_credit_type(enemy) -> str:
    if enemy is None:
        return ""
    return _clean_text(getattr(enemy, "_defeat_credit_type", None)) or _clean_text(
        getattr(enemy, "enemy_typ", None)
    )


def restore_defeat_identity(enemy) -> None:
    """Restore the defeat-credit identity onto the live enemy object."""
    if enemy is None:
        return

    name = defeat_credit_name(enemy)
    if name:
        setattr(enemy, "name", name)

    enemy_type = defeat_credit_type(enemy)
    if enemy_type:
        setattr(enemy, "enemy_typ", enemy_type)
