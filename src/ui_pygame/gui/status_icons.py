"""Shared helpers for compact pygame status-effect icon rendering."""

from __future__ import annotations

StatusIcon = tuple[str, bool | None]

STATUS_ICON_COLORS = {
    "positive": (70, 170, 90),
    "negative": (190, 70, 70),
    "urgent_negative": (225, 85, 65),
    "overflow": (95, 95, 110),
}

URGENT_NEGATIVE_STATUS_LABELS = {
    "STN": 0,
    "SLP": 1,
    "SIL": 2,
    "PRN": 3,
    "BLD": 4,
    "DSA": 5,
    "DOM": 6,
    "PSN": 7,
    "RND": 8,
}

IMPORTANT_POSITIVE_STATUS_LABELS = {
    "MSH": 0,
    "RFL": 1,
    "ICE": 2,
    "REG": 3,
    "ATK": 4,
    "DEF": 5,
}


def status_icon_priority(label: str, is_positive: bool | None) -> tuple[int, int, str]:
    """Return a stable sort key that keeps urgent combat states visible."""
    if is_positive is None:
        return (2, 50, label)
    if not is_positive:
        return (0, URGENT_NEGATIVE_STATUS_LABELS.get(label, 50), label)
    return (1, IMPORTANT_POSITIVE_STATUS_LABELS.get(label, 50), label)


def is_urgent_status_icon(label: str, is_positive: bool | None) -> bool:
    """Return whether an icon should receive high-alert presentation."""
    return is_positive is False and label in URGENT_NEGATIVE_STATUS_LABELS


def prioritize_status_icons(icons) -> list[StatusIcon]:
    indexed_icons = list(enumerate(icons))
    indexed_icons.sort(key=lambda item: (*status_icon_priority(*item[1]), item[0]))
    return [icon for _index, icon in indexed_icons]


def compact_status_icons(icons, per_row: int, max_rows: int | None) -> list[StatusIcon]:
    icon_list = list(icons)
    if max_rows is None or max_rows <= 0:
        return icon_list

    capacity = max(1, per_row * max_rows)
    if len(icon_list) <= capacity:
        return icon_list

    visible_count = max(0, capacity - 1)
    hidden_count = len(icon_list) - visible_count
    return icon_list[:visible_count] + [(f"+{hidden_count}", None)]


def fit_status_icon_label(font, label: str, max_width: int) -> str:
    """Shorten an icon label so it stays inside the icon pill."""
    def measured_width(value: str) -> int:
        if hasattr(font, "size"):
            return font.size(value)[0]
        return len(value) * 8

    if max_width <= 0:
        return label
    if measured_width(label) <= max_width:
        return label
    if label.startswith("+"):
        return "+"

    ellipsis = "."
    clipped = label
    while clipped and measured_width(f"{clipped}{ellipsis}") > max_width:
        clipped = clipped[:-1]
    return f"{clipped}{ellipsis}" if clipped else ellipsis


def status_icon_color(is_positive: bool | None, label: str = "") -> tuple[int, int, int]:
    if is_positive is None:
        return STATUS_ICON_COLORS["overflow"]
    if is_urgent_status_icon(label, is_positive):
        return STATUS_ICON_COLORS["urgent_negative"]
    return STATUS_ICON_COLORS["positive" if is_positive else "negative"]
