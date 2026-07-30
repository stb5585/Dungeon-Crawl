"""Helpers behavior for the combat manager package."""


def _battle_log_slug(value: object) -> str:
    """Return a filesystem-friendly token for debug battle-log filenames."""
    text = str(value or "unknown").strip().lower()
    slug = "".join(char if char.isalnum() else "-" for char in text)
    return "-".join(part for part in slug.split("-") if part) or "unknown"


def _player_facing_victory_line(line: str, *, debug_mode: bool) -> str:
    """Return a less diagnostic victory-popup line outside debug mode."""
    if debug_mode:
        return line
    if " bond grows by " in line and " from " in line:
        name = line.split(" bond grows by ", 1)[0].strip()
        return f"{name}'s bond grows stronger."
    return line
