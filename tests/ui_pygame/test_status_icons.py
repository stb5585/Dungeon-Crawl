#!/usr/bin/env python3
"""Focused coverage for shared pygame status-icon helpers."""

from __future__ import annotations

from types import SimpleNamespace

from src.ui_pygame.gui.status_icons import (
    STATUS_ICON_COLORS,
    combine_duplicate_status_icons,
    compact_status_icons,
    describe_stat_effect_icon_filtering,
    describe_status_icon_layout,
    fit_status_icon_label,
    is_urgent_status_icon,
    prioritize_status_icons,
    stat_effect_status_icon,
    status_icon_asset_path,
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
        ("BRG", False),
    ]

    assert prioritize_status_icons(icons) == [
        ("STN", False),
        ("PRN", False),
        ("BRG", False),
        ("PSN", False),
        ("MSH", True),
        ("REG", True),
        ("ATK", True),
    ]
    assert status_icon_priority("UNK", False) < status_icon_priority("MSH", True)
    assert is_urgent_status_icon("STN", False) is True
    assert is_urgent_status_icon("BRG", False) is True
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
    assert status_icon_color(False, "BRG") == STATUS_ICON_COLORS["urgent_negative"]
    assert status_icon_color(False, "PSN2") == STATUS_ICON_COLORS["urgent_negative"]
    assert status_icon_color(None) == STATUS_ICON_COLORS["overflow"]


def test_stat_effect_status_icon_skips_inactive_and_zero_value_changes():
    assert stat_effect_status_icon("ATK", SimpleNamespace(active=False, extra=4)) is None
    assert stat_effect_status_icon("ATK", SimpleNamespace(active=True, extra=0)) is None
    assert stat_effect_status_icon("ATK", SimpleNamespace(active=True, extra=3)) == ("ATK", True)
    assert stat_effect_status_icon("DEF", SimpleNamespace(active=True, extra=-2)) == ("DEF", False)
    assert stat_effect_status_icon("MYS", SimpleNamespace(active=True)) is None


def test_describe_stat_effect_icon_filtering_reports_skipped_zero_changes():
    stat_effects = {
        "Attack": SimpleNamespace(active=True, extra=0),
        "Defense": SimpleNamespace(active=True, extra=-2),
        "Magic": SimpleNamespace(active=True, extra=3),
        "Speed": SimpleNamespace(active=False, extra=4),
    }

    assert describe_stat_effect_icon_filtering(stat_effects) == {
        "active_stat_effect_count": 3,
        "emitted_stat_icon_count": 2,
        "skipped_zero_stat_icon_count": 1,
        "active_stat_effect_labels": ("ATT", "DEF", "MAG"),
        "emitted_stat_icon_labels": ("DEF", "MAG"),
        "skipped_zero_stat_icon_labels": ("ATT",),
    }


def test_describe_status_icon_layout_reports_overflow_and_urgent_visibility():
    icons = prioritize_status_icons(
        [
            ("ATK", True),
            ("STN", False),
            ("PSN", False),
            ("REG", True),
            ("BLD", False),
        ]
    )

    assert describe_status_icon_layout(icons, per_row=2, max_rows=2) == {
        "input_count": 5,
        "visible_count": 4,
        "hidden_count": 2,
        "visible_labels": ("STN", "BLD", "PSN", "+2"),
        "hidden_labels": ("REG", "ATK"),
        "visible_positive_count": 0,
        "visible_negative_count": 3,
        "visible_neutral_count": 1,
        "hidden_positive_count": 2,
        "hidden_negative_count": 0,
        "hidden_neutral_count": 0,
        "urgent_visible_count": 3,
        "urgent_hidden_count": 0,
        "urgent_visible_labels": ("STN", "BLD", "PSN"),
        "urgent_hidden_labels": (),
        "has_overflow": True,
        "capacity": 4,
        "row_count": 2,
        "per_row": 2,
        "max_rows": 2,
        "overflow_label": "+2",
    }
    assert describe_status_icon_layout(icons[:2], per_row=2, max_rows=None) == {
        "input_count": 2,
        "visible_count": 2,
        "hidden_count": 0,
        "visible_labels": ("STN", "BLD"),
        "hidden_labels": (),
        "visible_positive_count": 0,
        "visible_negative_count": 2,
        "visible_neutral_count": 0,
        "hidden_positive_count": 0,
        "hidden_negative_count": 0,
        "hidden_neutral_count": 0,
        "urgent_visible_count": 2,
        "urgent_hidden_count": 0,
        "urgent_visible_labels": ("STN", "BLD"),
        "urgent_hidden_labels": (),
        "has_overflow": False,
        "capacity": None,
        "row_count": 1,
        "per_row": 2,
        "max_rows": None,
        "overflow_label": None,
    }
    assert describe_status_icon_layout(icons[:3], per_row=0, max_rows=1)["row_count"] == 1

    unprioritized_icons = [
        ("ATK", True),
        ("REG", True),
        ("STN", False),
        ("PSN", False),
    ]
    assert describe_status_icon_layout(unprioritized_icons, per_row=2, max_rows=1)[
        "urgent_hidden_count"
    ] == 2
    assert describe_status_icon_layout(unprioritized_icons, per_row=2, max_rows=1)[
        "urgent_hidden_labels"
    ] == ("STN", "PSN")


def test_fit_status_icon_label_keeps_text_inside_icon():
    class Font:
        def size(self, text):
            return (len(text) * 8, 12)

    font = Font()

    assert fit_status_icon_label(font, "STN", 24) == "STN"
    assert fit_status_icon_label(font, "LONGSTATUS", 32).endswith(".")
    assert fit_status_icon_label(font, "+12", 12) == "+"


def test_status_icon_asset_path_uses_existing_effect_art_with_text_fallback():
    assert status_icon_asset_path("STN").name == "stun.png"
    assert status_icon_asset_path("STN2").name == "stun.png"
    assert status_icon_asset_path("PRN").name == "prone.png"
    assert status_icon_asset_path("RND").name == "bleed.png"
    assert status_icon_asset_path("BLD").name == "blind.png"
    assert status_icon_asset_path("PSN").name == "poison.png"
