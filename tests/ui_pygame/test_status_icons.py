#!/usr/bin/env python3
"""Focused coverage for shared pygame status-icon helpers."""

from __future__ import annotations

from src.ui_pygame.gui.status_icons import (
    STATUS_ICON_COLORS,
    combine_duplicate_status_icons,
    compact_status_icons,
    fit_status_icon_label,
    is_urgent_status_icon,
    prioritize_status_icons,
    status_icon_color,
    status_icon_priority,
)


def test_status_icon_priority_orders_urgent_debuffs_before_buffs():
    icons = [
        ("ATK", True),
        ("REG", True),
        ("PSN", False),
        ("STN", False),
        ("MSH", True),
        ("PRN", False),
    ]

    assert prioritize_status_icons(icons) == [
        ("STN", False),
        ("PRN", False),
        ("PSN", False),
        ("MSH", True),
        ("REG", True),
        ("ATK", True),
    ]
    assert status_icon_priority("UNK", False) < status_icon_priority("MSH", True)
    assert is_urgent_status_icon("STN", False) is True
    assert is_urgent_status_icon("ATK", True) is False


def test_duplicate_status_icons_collapse_into_counted_priority_pills():
    icons = combine_duplicate_status_icons(
        [
            ("ATK", True),
            ("ATK", True),
            ("REG", True),
            ("PSN", False),
            ("PSN", False),
        ]
    )

    assert icons == [
        ("ATK2", True),
        ("REG", True),
        ("PSN2", False),
    ]
    assert prioritize_status_icons(icons) == [
        ("PSN2", False),
        ("REG", True),
        ("ATK2", True),
    ]


def test_compact_status_icons_and_colors():
    icons = [(f"E{i}", i % 2 == 0) for i in range(6)]

    assert compact_status_icons(icons, per_row=2, max_rows=2) == [
        ("E0", True),
        ("E1", False),
        ("E2", True),
        ("+3", None),
    ]
    assert compact_status_icons(icons, per_row=2, max_rows=None) == icons
    assert status_icon_color(True) == STATUS_ICON_COLORS["positive"]
    assert status_icon_color(False) == STATUS_ICON_COLORS["negative"]
    assert status_icon_color(False, "STN") == STATUS_ICON_COLORS["urgent_negative"]
    assert status_icon_color(False, "PSN2") == STATUS_ICON_COLORS["urgent_negative"]
    assert status_icon_color(None) == STATUS_ICON_COLORS["overflow"]


def test_fit_status_icon_label_keeps_text_inside_icon():
    class Font:
        def size(self, text):
            return (len(text) * 8, 12)

    font = Font()

    assert fit_status_icon_label(font, "STN", 24) == "STN"
    assert fit_status_icon_label(font, "LONGSTATUS", 32).endswith(".")
    assert fit_status_icon_label(font, "+12", 12) == "+"
