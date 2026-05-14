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
    "BRG": 5,
    "DSA": 6,
    "DOM": 7,
    "PSN": 8,
    "RND": 9,
}

IMPORTANT_POSITIVE_STATUS_LABELS = {
    "MSH": 0,
    "RFL": 1,
    "ICE": 2,
    "REG": 3,
    "ATK": 4,
    "DEF": 5,
}


def stat_effect_status_icon(label: str, effect) -> StatusIcon | None:
    """Return a stat-effect icon, skipping active no-op stat changes."""
    try:
        extra = effect.extra
    except AttributeError:
        return None
    if not getattr(effect, "active", False) or extra == 0:
        return None
    return (label, extra > 0)


def describe_stat_effect_icon_filtering(stat_effects, labeler=None) -> dict[str, object]:
    """Return diagnostics for stat effects hidden before icon layout."""
    if labeler is None:
        labeler = lambda name: str(name)[:3].upper()

    active_labels: list[str] = []
    emitted_labels: list[str] = []
    skipped_zero_labels: list[str] = []

    for name, effect in stat_effects.items():
        label = labeler(name)
        if not getattr(effect, "active", False):
            continue
        active_labels.append(label)
        icon = stat_effect_status_icon(label, effect)
        if icon is None:
            skipped_zero_labels.append(label)
        else:
            emitted_labels.append(icon[0])

    return {
        "active_stat_effect_count": len(active_labels),
        "emitted_stat_icon_count": len(emitted_labels),
        "skipped_zero_stat_icon_count": len(skipped_zero_labels),
        "active_stat_effect_labels": tuple(active_labels),
        "emitted_stat_icon_labels": tuple(emitted_labels),
        "skipped_zero_stat_icon_labels": tuple(skipped_zero_labels),
    }


def _split_counted_label(label: str) -> tuple[str, int]:
    stripped = label.rstrip("0123456789")
    if not stripped:
        return label, 1
    suffix = label[len(stripped):]
    count = int(suffix) if suffix else 1
    return stripped, count


def _priority_label(label: str) -> str:
    stripped, _count = _split_counted_label(label)
    if stripped in URGENT_NEGATIVE_STATUS_LABELS or stripped in IMPORTANT_POSITIVE_STATUS_LABELS:
        return stripped
    return label


def status_icon_priority(label: str, is_positive: bool | None) -> tuple[int, int, int, str]:
    """Return a stable sort key that keeps urgent combat states visible."""
    priority_label = _priority_label(label)
    sort_label, count = _split_counted_label(label)
    if is_positive is None:
        return (2, 50, -count, sort_label)
    if not is_positive:
        return (0, URGENT_NEGATIVE_STATUS_LABELS.get(priority_label, 50), -count, sort_label)
    return (1, IMPORTANT_POSITIVE_STATUS_LABELS.get(priority_label, 50), -count, sort_label)


def is_urgent_status_icon(label: str, is_positive: bool | None) -> bool:
    """Return whether an icon should receive high-alert presentation."""
    return is_positive is False and _priority_label(label) in URGENT_NEGATIVE_STATUS_LABELS


def prioritize_status_icons(icons) -> list[StatusIcon]:
    indexed_icons = list(enumerate(icons))
    indexed_icons.sort(key=lambda item: (*status_icon_priority(*item[1]), item[0]))
    return [icon for _index, icon in indexed_icons]


def combine_duplicate_status_icons(icons) -> list[StatusIcon]:
    """Collapse repeated same-label status icons into one compact counted pill."""
    counts: dict[StatusIcon, int] = {}
    order: list[StatusIcon] = []
    for icon in icons:
        if icon not in counts:
            counts[icon] = 0
            order.append(icon)
        counts[icon] += 1

    combined: list[StatusIcon] = []
    for label, is_positive in order:
        count = counts[(label, is_positive)]
        combined_label = f"{label}{count}" if count > 1 else label
        combined.append((combined_label, is_positive))
    return combined


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


def describe_status_icon_layout(icons, per_row: int, max_rows: int | None) -> dict[str, object]:
    """Return compact layout diagnostics for a status-icon row."""
    icon_list = list(icons)
    visible_icons = compact_status_icons(icon_list, per_row, max_rows)
    normalized_per_row = max(1, per_row)
    capacity = None if max_rows is None or max_rows <= 0 else max(1, normalized_per_row * max_rows)
    overflow_label = None
    if visible_icons and visible_icons[-1][1] is None and visible_icons[-1][0].startswith("+"):
        overflow_label = visible_icons[-1][0]
    visible_real_count = len([icon for icon in visible_icons if icon[1] is not None])
    hidden_icons = icon_list[visible_real_count:]
    hidden_count = max(0, len(hidden_icons))
    visible_positive_count = sum(1 for _label, is_positive in visible_icons if is_positive is True)
    visible_negative_count = sum(1 for _label, is_positive in visible_icons if is_positive is False)
    visible_neutral_count = sum(1 for _label, is_positive in visible_icons if is_positive is None)
    hidden_positive_count = sum(1 for _label, is_positive in hidden_icons if is_positive is True)
    hidden_negative_count = sum(1 for _label, is_positive in hidden_icons if is_positive is False)
    hidden_neutral_count = sum(1 for _label, is_positive in hidden_icons if is_positive is None)
    visible_urgent_labels = tuple(
        label for label, is_positive in visible_icons if is_urgent_status_icon(label, is_positive)
    )
    hidden_urgent_labels = tuple(
        label for label, is_positive in hidden_icons if is_urgent_status_icon(label, is_positive)
    )
    return {
        "input_count": len(icon_list),
        "visible_count": len(visible_icons),
        "hidden_count": hidden_count,
        "visible_labels": tuple(label for label, _is_positive in visible_icons),
        "hidden_labels": tuple(label for label, _is_positive in hidden_icons),
        "visible_positive_count": visible_positive_count,
        "visible_negative_count": visible_negative_count,
        "visible_neutral_count": visible_neutral_count,
        "hidden_positive_count": hidden_positive_count,
        "hidden_negative_count": hidden_negative_count,
        "hidden_neutral_count": hidden_neutral_count,
        "urgent_visible_count": len(visible_urgent_labels),
        "urgent_hidden_count": len(hidden_urgent_labels),
        "urgent_visible_labels": visible_urgent_labels,
        "urgent_hidden_labels": hidden_urgent_labels,
        "has_overflow": overflow_label is not None,
        "capacity": capacity,
        "row_count": (len(visible_icons) + normalized_per_row - 1) // normalized_per_row,
        "per_row": per_row,
        "max_rows": max_rows,
        "overflow_label": overflow_label,
    }


def fit_status_icon_label(font, label: str, max_width: int) -> str:
    """Shorten an icon label so it stays inside the icon pill."""
    def measured_width(value: str) -> int:
        if hasattr(font, "size"):
            return font.size(value)[0]
        return len(value) * 8

    if max_width <= 0:
        return "+" if label.startswith("+") else "."
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
