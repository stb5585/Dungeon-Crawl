"""Shared-service pygame progression tree and attribute screen."""

from __future__ import annotations

import math
import re

import pygame

from src.core import companions
from src.core.progression import (
    ABILITY_TREES,
    PRIMARY_ATTRIBUTES,
    TREE_NODES,
    NodeKind,
    NodeState,
    apply_progression_plan,
    available_nodes,
    effective_node_level_requirement,
    permanent_closures_for_plan,
    progression_class_name,
)
from src.ui_pygame.assets.ability_icon_manager import (
    get_ability_icon_manager,
)

from .church import PaladinVowSelectionPopup
from .character_naming import CompanionNamingScreen
from .confirmation_popup import ConfirmationPopup
from .familiar_selection_popup import FamiliarSelectionPopup
from .mouse_helpers import hit_index, is_left_click, mouse_position
from .popup_menus import SelectionPopup
from .promotion_screen import PromotionScreen
from .town_base import TownScreenBase, wrap_text_to_pixel_width


class ProgressionScreen(TownScreenBase):
    """Keyboard-and-mouse progression screen backed only by core services."""

    STAT_DISPLAY_NAMES = {
        "strength": "Strength",
        "intel": "Intelligence",
        "wisdom": "Wisdom",
        "con": "Constitution",
        "charisma": "Charisma",
        "dex": "Dexterity",
    }
    CONNECTOR_COLOR = (72, 78, 88)
    NODE_BACKING_COLOR = (12, 14, 20)
    LABEL_BACKING_COLOR = (8, 10, 14)
    PROMOTION_WARNING_COLOR = (205, 95, 95)
    TREE_WARNING_HEIGHT = 38
    TREE_WARNING_TEXT = (
        "Permanent choice: Buying promotion nodes may prevent the player "
        "from buying learning certain abilities. Choose carefully."
    )
    LANCER_PROMOTION_TEXT = (
        "Promoting to Dragoon retains all unpurchased Lancer nodes in the "
        "Dragoon tree."
    )

    STATE_COLORS = {
        NodeState.OWNED: (90, 190, 110),
        NodeState.AVAILABLE: (218, 165, 32),
        NodeState.BLOCKED: (130, 130, 130),
        NodeState.CLOSED: (120, 60, 60),
    }

    def __init__(self, presenter, player_char):
        super().__init__(presenter)
        self.player_char = player_char
        self.focus = "nodes"
        self.current_node = 0
        self.current_attribute = 0
        self.tree_index = 0
        self.node_rects: list[pygame.Rect] = []
        self.node_icon_rects: list[pygame.Rect] = []
        self.attribute_rects: list[pygame.Rect] = []
        self.attribute_minus_rects: list[pygame.Rect] = []
        self.attribute_plus_rects: list[pygame.Rect] = []
        self.reset_button_rect = pygame.Rect(0, 0, 0, 0)
        self.spend_button_rect = pygame.Rect(0, 0, 0, 0)
        self.pending_node_ids: list[str] = []
        self.pending_attributes: dict[str, int] = {}
        self.background_draw_func = None
        self.show_embedded_navigation_helper = False
        self.embedded_navigation_active = False
        self.tree_scroll_row = 0
        self._tree_viewport: pygame.Rect | None = None
        self.icon_manager = get_ability_icon_manager()

    def _popup_background(self):
        if callable(self.background_draw_func):
            self.background_draw_func()
        else:
            self.draw_all(do_flip=False)

    def _statuses(self):
        self._ensure_staging()
        return available_nodes(
            self.player_char,
            self._selected_tree_id(),
            planned_node_ids=self.pending_node_ids,
            planned_attributes=self.pending_attributes,
        )

    def _ensure_staging(self):
        if not hasattr(self, "pending_node_ids"):
            self.pending_node_ids = []
        if not hasattr(self, "pending_attributes"):
            self.pending_attributes = {}
        if not hasattr(self, "attribute_minus_rects"):
            self.attribute_minus_rects = []
        if not hasattr(self, "attribute_plus_rects"):
            self.attribute_plus_rects = []
        if not hasattr(self, "spend_button_rect"):
            self.spend_button_rect = pygame.Rect(0, 0, 0, 0)
        if not hasattr(self, "reset_button_rect"):
            self.reset_button_rect = pygame.Rect(0, 0, 0, 0)

    def _pending_node_cost(self) -> int:
        self._ensure_staging()
        return sum(
            TREE_NODES[node_id].cost
            for node_id in self.pending_node_ids
        )

    def _pending_attribute_cost(self) -> int:
        self._ensure_staging()
        return sum(self.pending_attributes.values())

    def _remaining_points(self) -> int:
        return (
            self.player_char.progression.unspent_points
            - self._pending_node_cost()
        )

    def _remaining_attribute_points(self) -> int:
        return (
            self.player_char.progression.unspent_attribute_points
            - self._pending_attribute_cost()
        )

    def has_pending_changes(self) -> bool:
        """Return whether the screen has an uncommitted distribution."""
        return self._pending_node_cost() + self._pending_attribute_cost() > 0

    def _clear_pending(self) -> None:
        self._ensure_staging()
        self.pending_node_ids.clear()
        self.pending_attributes.clear()

    def _tree_ids(self):
        current = progression_class_name(self.player_char)
        completed = sorted(self.player_char.progression.completed_trees)
        return [current, *(tree for tree in completed if tree != current)]

    def _selected_tree_id(self):
        tree_ids = self._tree_ids()
        self.tree_index %= len(tree_ids)
        return tree_ids[self.tree_index]

    def _selected_status(self):
        statuses = self._statuses()
        return statuses[self.current_node] if statuses else None

    @staticmethod
    def _node_frame_rect(icon_rect: pygame.Rect) -> pygame.Rect:
        """Return the shared node frame and selection-highlight bounds."""
        return icon_rect.inflate(4, 4)

    def _layout_node_rects(self, rect, statuses, branches):
        """Lay icon nodes at explicit manifest columns and rows."""
        if not statuses:
            self.node_icon_rects = []
            return []
        explicit_column_count = math.ceil(
            max(status.node.position[0] for status in statuses) + 1
        )
        column_count = max(1, len(branches), explicit_column_count)
        lane_width = (rect.width - 24) // column_count
        self._tree_column_origin = rect.left + 12 + lane_width // 2
        self._tree_lane_width = lane_width
        graph_top = rect.top + 42
        graph_bottom = rect.bottom - self.TREE_WARNING_HEIGHT
        cell_height = 50
        max_row = max(status.node.position[1] for status in statuses)
        available_height = graph_bottom - graph_top
        row_step = 58
        if max_row:
            row_step = min(
                row_step,
                max(52, (available_height - cell_height) // max_row),
            )
        visible_rows = max(
            1,
            (available_height - cell_height) // row_step + 1,
        )
        selected_row = statuses[self.current_node].node.position[1]
        if selected_row < self.tree_scroll_row:
            self.tree_scroll_row = selected_row
        elif selected_row >= self.tree_scroll_row + visible_rows:
            self.tree_scroll_row = selected_row - visible_rows + 1
        self.tree_scroll_row = max(
            0,
            min(self.tree_scroll_row, max(0, max_row - visible_rows + 1)),
        )
        self._tree_viewport = pygame.Rect(
            rect.left + 4,
            graph_top,
            rect.width - 8,
            graph_bottom - graph_top,
        )
        result: list[pygame.Rect] = []
        icon_rects: list[pygame.Rect] = []
        for status in statuses:
            column, row = status.node.position
            center_x = int(
                rect.left + 12 + column * lane_width + lane_width // 2
            )
            y = graph_top + (row - self.tree_scroll_row) * row_step
            cell_width = max(64, min(144, lane_width - 8))
            cell = pygame.Rect(
                center_x - cell_width // 2,
                y,
                cell_width,
                cell_height,
            )
            result.append(cell)
            icon_rects.append(pygame.Rect(center_x - 16, y, 32, 32))
        self.node_icon_rects = icon_rects
        return result

    def _draw_connectors(self, statuses):
        """Draw orthogonal prerequisite connectors behind talent nodes."""
        index_by_id = {
            status.node.id: index
            for index, status in enumerate(statuses)
        }
        for index, status in enumerate(statuses):
            target_rect = self.node_icon_rects[index]
            if not self._tree_viewport or not self._tree_viewport.colliderect(target_rect):
                continue
            for prerequisite in status.node.prerequisites:
                source_index = index_by_id.get(prerequisite)
                if source_index is None:
                    continue
                source_rect = self.node_icon_rects[source_index]
                if not self._tree_viewport.colliderect(source_rect):
                    continue
                if status.node.payload.get("connector_enter_from_top"):
                    source_is_left = source_rect.centerx < target_rect.centerx
                    source_side = (
                        source_rect.midright
                        if source_is_left
                        else source_rect.midleft
                    )
                    channel_column = status.node.payload.get(
                        "connector_channel_columns",
                        {},
                    ).get(prerequisite)
                    channel_x = (
                        target_rect.centerx
                        if channel_column is None
                        else int(
                            self._tree_column_origin
                            + channel_column * self._tree_lane_width
                        )
                    )
                    pygame.draw.lines(
                        self.screen,
                        self.CONNECTOR_COLOR,
                        False,
                        (
                            source_side,
                            (channel_x, source_side[1]),
                            (channel_x, target_rect.top),
                            target_rect.midtop,
                        ),
                        1,
                    )
                    continue
                if status.node.payload.get("connector_join_at_target_row"):
                    source_is_left = source_rect.centerx < target_rect.centerx
                    end = (
                        target_rect.midleft
                        if source_is_left
                        else target_rect.midright
                    )
                    pygame.draw.lines(
                        self.screen,
                        self.CONNECTOR_COLOR,
                        False,
                        (
                            source_rect.midbottom,
                            (source_rect.centerx, end[1]),
                            end,
                        ),
                        1,
                    )
                    continue
                end = target_rect.midtop
                color = self.CONNECTOR_COLOR
                if source_rect.centerx == target_rect.centerx:
                    pygame.draw.line(
                        self.screen,
                        color,
                        source_rect.midbottom,
                        end,
                        1,
                    )
                    continue
                source_is_left = source_rect.centerx < target_rect.centerx
                source_side = (
                    source_rect.midright
                    if source_is_left
                    else source_rect.midleft
                )
                end = (
                    target_rect.midleft
                    if source_is_left
                    else target_rect.midright
                )
                channel_column = status.node.payload.get(
                    "connector_channel_columns",
                    {},
                ).get(prerequisite)
                if channel_column is None:
                    channel_x = (source_side[0] + end[0]) // 2
                else:
                    channel_x = int(
                        self._tree_column_origin
                        + channel_column * self._tree_lane_width
                    )
                pygame.draw.lines(
                    self.screen,
                    color,
                    False,
                    (
                        source_side,
                        (channel_x, source_side[1]),
                        (channel_x, end[1]),
                        end,
                    ),
                    1,
                )

    def _draw_header(self):
        title = self.large_font.render("Progression", True, self.colors.GOLD)
        self.screen.blit(title, (32, 24))
        state = self.player_char.progression
        summary = (
            f"Global Level {state.level}  |  Class Tier "
            f"{self.player_char.level.pro_level}  |  Progression Points "
            f"{state.unspent_points}  |  Attribute Points "
            f"{state.unspent_attribute_points}"
        )
        self.screen.blit(
            self.normal_font.render(summary, True, self.colors.WHITE),
            (32, 62),
        )

    def _draw_tree(self, rect):
        self.draw_semi_transparent_panel(rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, rect, 2)
        points_text = (
            "Available Progression Points: "
            f"{self._remaining_points()}"
        )
        points_surface = self.normal_font.render(
            points_text,
            True,
            self.colors.GOLD,
        )
        self.screen.blit(
            points_surface,
            (rect.left + 16, rect.top + 12),
        )
        if getattr(self, "show_embedded_navigation_helper", False):
            helper = (
                "Arrows: Navigate  Enter: Select  P/Esc: Back"
                if getattr(self, "embedded_navigation_active", False)
                else "P: Navigate tree"
            )
            helper_surface = self.small_font.render(
                helper,
                True,
                self.colors.GRAY,
            )
            self.screen.blit(
                helper_surface,
                (
                    rect.right - helper_surface.get_width() - 16,
                    rect.top + 15,
                ),
            )
        statuses = self._statuses()
        tree = ABILITY_TREES[self._selected_tree_id()]
        self.node_rects = self._layout_node_rects(
            rect,
            statuses,
            tree.branches,
        )
        self._draw_connectors(statuses)

        for index, status in enumerate(statuses):
            node_rect = self.node_rects[index]
            icon_rect = self.node_icon_rects[index]
            if not self._tree_viewport.colliderect(icon_rect):
                continue
            selected = self.focus == "nodes" and index == self.current_node
            is_pending = status.node.id in self.pending_node_ids
            frame_rect = self._node_frame_rect(icon_rect)
            pygame.draw.rect(
                self.screen,
                (
                    self.colors.HIGHLIGHT_BG
                    if selected
                    else self.NODE_BACKING_COLOR
                ),
                frame_rect,
            )
            icon_manager = getattr(self, "icon_manager", None)
            if icon_manager is None:
                icon_manager = get_ability_icon_manager()
                self.icon_manager = icon_manager
            icon = icon_manager.get_icon(status.node.icon_key).copy()
            if status.state == NodeState.BLOCKED:
                icon.fill((145, 145, 145, 190), special_flags=pygame.BLEND_RGBA_MULT)
            elif status.state == NodeState.CLOSED:
                icon.fill((150, 70, 70, 175), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(icon, icon_rect)
            state_color = (
                (90, 175, 220)
                if is_pending
                else self.STATE_COLORS[status.state]
            )
            pygame.draw.rect(
                self.screen,
                state_color,
                frame_rect,
                2 if selected else 1,
            )
            label = status.node.name
            while len(label) > 5 and self.small_font.size(label)[0] > node_rect.width:
                label = f"{label[:-4]}..."
            label_surface = self.small_font.render(
                label,
                True,
                state_color,
            )
            label_rect = label_surface.get_rect(
                centerx=icon_rect.centerx,
                top=icon_rect.bottom + 2,
            )
            pygame.draw.rect(
                self.screen,
                self.LABEL_BACKING_COLOR,
                label_rect.inflate(4, 0),
            )
            self.screen.blit(
                label_surface,
                label_rect,
            )
        self._draw_tree_warning(rect)

    def _has_pending_promotion(self) -> bool:
        """Return whether the current distribution contains a promotion."""
        self._ensure_staging()
        return any(
            node_id in TREE_NODES
            and TREE_NODES[node_id].kind == NodeKind.PROMOTION
            for node_id in self.pending_node_ids
        )

    def _draw_tree_warning(self, rect) -> None:
        """Draw the permanent promotion warning at the tree's bottom edge."""
        try:
            selected_tree = self._selected_tree_id()
        except (AttributeError, ZeroDivisionError):
            selected_tree = ""
        warning_text = (
            self.LANCER_PROMOTION_TEXT
            if selected_tree == "Lancer"
            else self.TREE_WARNING_TEXT
        )
        lines = wrap_text_to_pixel_width(
            warning_text,
            self.small_font,
            rect.width - 32,
        )
        line_height = self.small_font.get_height() + 2
        warning_height = len(lines) * line_height
        warning_y = rect.bottom - warning_height - 8
        backing_rect = pygame.Rect(
            rect.left + 8,
            warning_y - 2,
            rect.width - 16,
            warning_height + 4,
        )
        pygame.draw.rect(
            self.screen,
            self.LABEL_BACKING_COLOR,
            backing_rect,
        )
        color = (
            self.PROMOTION_WARNING_COLOR
            if self._has_pending_promotion()
            else self.colors.GRAY
        )
        for index, line in enumerate(lines):
            self.screen.blit(
                self.small_font.render(line, True, color),
                (rect.left + 16, warning_y + index * line_height),
            )

    def _draw_attributes(self, rect):
        self._ensure_staging()
        self.draw_semi_transparent_panel(rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, rect, 2)
        self.screen.blit(
            self.normal_font.render(
                "Primary Attributes",
                True,
                self.colors.GOLD,
            ),
            (rect.left + 16, rect.top + 12),
        )
        self.attribute_rects = []
        self.attribute_minus_rects = []
        self.attribute_plus_rects = []
        for index, stat_name in enumerate(PRIMARY_ATTRIBUTES):
            row = pygame.Rect(
                rect.left + 12,
                rect.top + 48 + index * 38,
                rect.width - 24,
                32,
            )
            self.attribute_rects.append(row)
            minus_rect = pygame.Rect(row.left + 4, row.top + 4, 24, 24)
            plus_rect = pygame.Rect(row.right - 28, row.top + 4, 24, 24)
            self.attribute_minus_rects.append(minus_rect)
            self.attribute_plus_rects.append(plus_rect)
            selected = self.focus == "attributes" and index == self.current_attribute
            if selected:
                pygame.draw.rect(self.screen, self.colors.HIGHLIGHT_BG, row)
            pygame.draw.rect(
                self.screen,
                self.colors.GOLD if selected else self.colors.BORDER_COLOR,
                row,
                1,
            )
            pending = self.pending_attributes.get(stat_name, 0)
            value = getattr(self.player_char.stats, stat_name) + pending
            label = self.STAT_DISPLAY_NAMES[stat_name]
            text = f"{label}: {value} (+{pending})"
            text_surface = self.small_font.render(
                text,
                True,
                self.colors.WHITE,
            )
            self.screen.blit(
                text_surface,
                (row.left + 34, row.top + 7),
            )
            minus_color = (
                self.colors.GOLD
                if pending > 0
                else self.colors.GRAY
            )
            plus_color = (
                self.colors.GOLD
                if self._remaining_attribute_points() > 0
                else self.colors.GRAY
            )
            pygame.draw.rect(self.screen, minus_color, minus_rect, 1)
            pygame.draw.rect(self.screen, plus_color, plus_rect, 1)
            self.screen.blit(
                self.small_font.render("-", True, minus_color),
                (
                    minus_rect.centerx - 3,
                    minus_rect.centery - self.small_font.get_height() // 2,
                ),
            )
            self.screen.blit(
                self.small_font.render("+", True, plus_color),
                (
                    plus_rect.centerx - 3,
                    plus_rect.centery - self.small_font.get_height() // 2,
                ),
            )
        available_text = (
            "Available Attribute Points: "
            f"{self._remaining_attribute_points()}"
        )
        self.screen.blit(
            self.small_font.render(
                available_text,
                True,
                self.colors.GOLD,
            ),
            (rect.left + 16, rect.bottom - 26),
        )

    def _draw_details(self, rect):
        self.draw_semi_transparent_panel(rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, rect, 2)
        status = self._selected_status()
        if status is None:
            return
        point_label = "Point" if status.node.cost == 1 else "Points"
        lines = [
            status.node.name,
            f"{status.node.cost} {point_label}",
        ]
        warning_lines = set()
        content_width = rect.width - 28
        displayed_class = (
            self._selected_tree_id()
            if hasattr(self, "player_char")
            else status.node.tree_id
        )
        required_level = effective_node_level_requirement(
            status.node,
            displayed_class,
        )
        description = status.node.payload.get("description", "")
        if description:
            lines.extend(
                wrap_text_to_pixel_width(
                    description,
                    self.small_font,
                    content_width,
                )
            )
        if status.node.kind == NodeKind.PROMOTION:
            requirements = status.node.payload["requirements"]
            lines.extend(wrap_text_to_pixel_width(
                (
                    "Required level: "
                    f"{status.node.payload['level_requirement']}"
                ),
                self.small_font,
                content_width,
            ))
            lines.extend(wrap_text_to_pixel_width(
                (
                    "Required Stats: "
                    + ", ".join(
                        f"{self.STAT_DISPLAY_NAMES.get(name, name.title())} "
                        f"{value}"
                        for name, value in requirements.items()
                    )
                ),
                self.small_font,
                content_width,
            ))
        elif required_level:
            lines.append(
                "Required level: "
                f"{required_level}"
            )
        specialization = status.node.payload.get("weapon_specialization")
        if specialization:
            weapon_type, rank = specialization
            lines.extend(wrap_text_to_pixel_width(
                f"Required {weapon_type} specialization level: {rank}",
                self.small_font,
                content_width,
            ))
        implied_prerequisites = {
            f"Requires {TREE_NODES[node_id].name}."
            for node_id in status.node.prerequisites
        }
        point_noun = "point" if status.node.cost == 1 else "points"
        implied_cost_reasons = {
            f"Requires {status.node.cost} {point_noun}.",
            f"Requires {status.node.cost} progression {point_noun}.",
        }
        for reason in status.reasons:
            if not (
                reason not in implied_prerequisites
                and reason not in implied_cost_reasons
                and not (
                    required_level
                    and (
                        reason.startswith("Requires global level ")
                        or reason.startswith("Requires level ")
                    )
                )
                and not (
                    specialization
                    and reason.startswith(
                        f"Requires {specialization[0]} specialization level "
                    )
                )
                and not (
                    status.node.kind == NodeKind.PROMOTION
                    and any(
                        any(
                            reason.startswith(f"Requires {display_name} ")
                            for display_name in {
                                self.STAT_DISPLAY_NAMES.get(
                                    stat_name,
                                    stat_name.title(),
                                ),
                                stat_name.replace(
                                    "intel",
                                    "intelligence",
                                ).title(),
                            }
                        )
                        for stat_name in status.node.payload["requirements"]
                    )
                )
            ):
                continue
            cleaned_reason = re.sub(r" \(current [^)]+\)", "", reason)
            wrapped_reason = wrap_text_to_pixel_width(
                cleaned_reason,
                self.small_font,
                content_width,
            )
            lines.extend(wrapped_reason)
            if reason.startswith("Another promotion is already distributed"):
                warning_lines.update(wrapped_reason)
        line_height = self.small_font.get_height() + 2
        max_lines = max(1, (rect.height - 20) // line_height)
        for index, line in enumerate(lines[:max_lines]):
            if index == 0:
                color = self.colors.GOLD
            elif line in warning_lines:
                color = self.PROMOTION_WARNING_COLOR
            else:
                color = self.colors.WHITE
            self.screen.blit(
                self.small_font.render(line, True, color),
                (rect.left + 14, rect.top + 10 + index * line_height),
            )

    def _draw_spend_button(self, rect):
        self._ensure_staging()
        enabled = self.has_pending_changes()
        gap = 8
        reset_width = max(72, (rect.width - gap) // 3)
        self.reset_button_rect = pygame.Rect(
            rect.left,
            rect.top,
            reset_width,
            rect.height,
        )
        self.spend_button_rect = pygame.Rect(
            self.reset_button_rect.right + gap,
            rect.top,
            rect.right - self.reset_button_rect.right - gap,
            rect.height,
        )

        self._draw_action_button(
            self.reset_button_rect,
            "Reset",
            enabled,
            getattr(self, "focus", "nodes") == "reset",
        )
        label = "Spend Distribution"
        self._draw_action_button(
            self.spend_button_rect,
            label,
            enabled,
            getattr(self, "focus", "nodes") == "spend",
        )

    def _draw_action_button(self, rect, label, enabled, selected):
        if selected:
            pygame.draw.rect(self.screen, self.colors.HIGHLIGHT_BG, rect)
        color = self.colors.GOLD if enabled else self.colors.GRAY
        pygame.draw.rect(self.screen, color, rect, 2 if selected else 1)
        surface = self.normal_font.render(label, True, color)
        self.screen.blit(
            surface,
            (
                rect.centerx - surface.get_width() // 2,
                rect.centery - surface.get_height() // 2,
            ),
        )

    def draw_all(self, do_flip=True):
        self.draw_background()
        self._draw_header()
        tree_rect = pygame.Rect(24, 100, int(self.width * 0.69), self.height - 280)
        attr_rect = pygame.Rect(
            tree_rect.right + 12,
            100,
            self.width - tree_rect.right - 36,
            320,
        )
        detail_rect = pygame.Rect(24, self.height - 165, self.width - 48, 125)
        self._draw_tree(tree_rect)
        self._draw_attributes(attr_rect)
        self._draw_details(detail_rect)
        hint = (
            "Q/E: Current/Completed Trees  TAB: Tree/Attributes  "
            "ARROWS: Select  ENTER/CLICK: Purchase  ESC: Back"
        )
        self.screen.blit(
            self.small_font.render(hint, True, self.colors.GRAY),
            (24, self.height - 28),
        )
        if do_flip:
            pygame.display.flip()

    def _promotion_choices(self, target_class: str):
        if target_class == "Paladin":
            vow = PaladinVowSelectionPopup(self.presenter).show(
                flush_events=True,
                require_key_release=True,
                background_draw_func=self._popup_background,
            )
            if vow is None:
                return None
            confirm = ConfirmationPopup(
                self.presenter,
                f"Swear the Vow of {vow}?",
                show_buttons=True,
            )
            if not confirm.show(
                flush_events=True,
                require_key_release=True,
                background_draw_func=self._popup_background,
            ):
                return None
            return {"vow": vow}
        if target_class == "Warlock":
            familiar_types = [
                companions.Homunculus,
                companions.Fairy,
                companions.Mephit,
                companions.Jinkin,
            ]
            familiar = FamiliarSelectionPopup(
                self.presenter,
                self,
                familiar_types,
            ).show(
                self.player_char,
                flush_events=True,
                require_key_release=True,
            )
            if familiar is None:
                return None
            familiar.name = familiar.race
            naming = CompanionNamingScreen(
                self.presenter,
                familiar.race,
                species=familiar.race,
                form=familiar.spec,
                special=", ".join(
                    [
                        *familiar.spellbook.get("Skills", {}),
                        *familiar.spellbook.get("Spells", {}),
                    ]
                ),
            )
            nickname = naming.navigate(
                default=familiar.race,
                flush_events=True,
                require_key_release=True,
                background_surface=self.screen.copy(),
            )
            if nickname is None:
                return None
            familiar.name = str(nickname).strip() or familiar.race
            return {"familiar": familiar}
        return {}

    def _toggle_selected_node(self):
        self._ensure_staging()
        status = self._selected_status()
        if status is None:
            return
        node = status.node
        if node.id in self.pending_node_ids:
            removed = {node.id}
            changed = True
            while changed:
                changed = False
                for pending_id in self.pending_node_ids:
                    if pending_id in removed:
                        continue
                    pending_node = TREE_NODES[pending_id]
                    remaining = (
                        set(self.pending_node_ids)
                        | self.player_char.progression.purchased_node_ids
                    ) - removed
                    loses_requirement = (
                        not any(
                            prerequisite in remaining
                            for prerequisite in pending_node.prerequisites
                        )
                        if pending_node.payload.get("prerequisite_mode") == "any"
                        else any(
                            prerequisite in removed
                            for prerequisite in pending_node.prerequisites
                        )
                    )
                    if loses_requirement:
                        removed.add(pending_id)
                        changed = True
            self.pending_node_ids = [
                node_id
                for node_id in self.pending_node_ids
                if node_id not in removed
            ]
        elif status.state == NodeState.AVAILABLE:
            self.pending_node_ids.append(node.id)

    def _adjust_selected_attribute(self, amount: int):
        self._ensure_staging()
        stat_name = PRIMARY_ATTRIBUTES[self.current_attribute]
        current = self.pending_attributes.get(stat_name, 0)
        if amount > 0:
            if self._remaining_attribute_points() < amount:
                return
            self.pending_attributes[stat_name] = current + amount
            return
        if current <= 0:
            return
        new_value = max(0, current + amount)
        if new_value:
            self.pending_attributes[stat_name] = new_value
        else:
            self.pending_attributes.pop(stat_name, None)
        self._revalidate_pending_nodes()

    def _revalidate_pending_nodes(self):
        changed = True
        while changed:
            changed = False
            for node_id in reversed(self.pending_node_ids):
                other_nodes = [
                    candidate
                    for candidate in self.pending_node_ids
                    if candidate != node_id
                ]
                statuses = available_nodes(
                    self.player_char,
                    self._selected_tree_id(),
                    planned_node_ids=other_nodes,
                    planned_attributes=self.pending_attributes,
                )
                status = next(
                    candidate
                    for candidate in statuses
                    if candidate.node.id == node_id
                )
                if status.state != NodeState.AVAILABLE:
                    self.pending_node_ids.remove(node_id)
                    changed = True
                    break

    def _reset_pending(self):
        self._clear_pending()

    def _confirm_staged_promotion(self, node) -> bool:
        target_name = node.payload["target_class"]
        target_ctor = node.payload["target_class_ctor"]
        target_tier = max(1, int(target_ctor().pro_level) - 1)
        promotion_screen = PromotionScreen(
            self.presenter,
            self.player_char,
            [target_name],
            {target_name: target_ctor},
            current_class=node.tree_id,
            pro_level=target_tier,
        )
        return promotion_screen.navigate() == target_name

    def _spend_pending(self):
        if not self.has_pending_changes():
            return
        closures = ()
        if (
            getattr(self.player_char, "cls", None) is not None
            and getattr(self.player_char, "progression", None) is not None
        ):
            closures = permanent_closures_for_plan(
                self.player_char,
                self._selected_tree_id(),
                self.pending_node_ids,
            )
        if closures:
            names = "\n".join(f"- {name}" for name in closures)
            confirmed = ConfirmationPopup(
                self.presenter,
                (
                    "Confirm Permanent Choice?\n\n"
                    "Spending this distribution will permanently close:\n"
                    f"{names}\n\nThese abilities cannot be learned later."
                ),
                show_buttons=True,
            ).show(background_draw_func=self._popup_background)
            if not confirmed:
                return
        promotion_choices_by_node: dict[str, dict] = {}
        node_choices: dict[str, dict] = {}
        for node_id in self.pending_node_ids:
            node = TREE_NODES[node_id]
            category = node.payload.get("xenid_category")
            if category:
                options = list(node.payload.get(
                    "xenid_options",
                    companions.XENID_PAIRS.get(str(category), ()),
                ))
                result = SelectionPopup(
                    self.presenter,
                    self,
                    title=f"Choose {category} Xenid",
                    header_message=(
                        "This choice is permanent. Select the Xenid that will "
                        "answer this Calling."
                    ),
                    options=options,
                ).show(self.player_char)
                if not result or result[0] != "selection":
                    return
                selected = result[1]
                confirmed = ConfirmationPopup(
                    self.presenter,
                    (
                        f"Permanently bind {selected} to the {category} "
                        "Calling?"
                    ),
                    show_buttons=True,
                ).show(background_draw_func=self._popup_background)
                if not confirmed:
                    return
                node_choices[node_id] = {"xenid": selected}
            if node.kind != NodeKind.PROMOTION:
                continue
            if not self._confirm_staged_promotion(node):
                return
            promotion_choices = self._promotion_choices(
                node.payload["target_class"],
            )
            if promotion_choices is None:
                return
            promotion_choices_by_node[node_id] = promotion_choices
        result = apply_progression_plan(
            self.player_char,
            self.pending_node_ids,
            self.pending_attributes,
            promotion_choices=promotion_choices_by_node,
            node_choices=node_choices,
        )
        if result.success:
            self._clear_pending()
            self.current_node = 0
            self.tree_index = 0
            self.tree_scroll_row = 0
            if self.background_draw_func is not None:
                self.background_draw_func()
            return
        ConfirmationPopup(
            self.presenter,
            result.message,
            show_buttons=False,
        ).show(background_draw_func=self._popup_background)

    def confirm_discard_pending(self) -> bool:
        """Confirm leaving when distributed points have not been committed."""
        if not self.has_pending_changes():
            return True
        popup = ConfirmationPopup(
            self.presenter,
            "Leave Progression?\n\nDistributed points will not be spent.",
            show_buttons=True,
        )
        if not popup.show(background_draw_func=self._popup_background):
            return False
        self._clear_pending()
        return True

    def draw_embedded(self, player_char, rect):
        """Draw progression as a Character Menu tab without flipping."""
        self.player_char = player_char
        tree_width = int(rect.width * 0.74)
        tree_rect = pygame.Rect(
            rect.left,
            rect.top,
            tree_width,
            rect.height,
        )
        attr_rect = pygame.Rect(
            tree_rect.right + 10,
            rect.top,
            rect.right - tree_rect.right - 10,
            min(320, rect.height),
        )
        detail_top = attr_rect.bottom + 10
        detail_rect = pygame.Rect(
            attr_rect.left,
            detail_top,
            attr_rect.width,
            max(1, rect.bottom - detail_top - 48),
        )
        spend_rect = pygame.Rect(
            attr_rect.left,
            rect.bottom - 38,
            attr_rect.width,
            38,
        )
        self._draw_tree(tree_rect)
        self._draw_attributes(attr_rect)
        self._draw_details(detail_rect)
        self._draw_spend_button(spend_rect)

    def handle_event(self, event) -> bool:
        """Handle an event while embedded in the Character Menu."""
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
                delta = -1 if event.button == 4 else 1
                self.current_node = (
                    self.current_node + delta
                ) % max(1, len(self._statuses()))
                return True
            node_index = hit_index(self.node_rects, mouse_position(event))
            attribute_index = hit_index(self.attribute_rects, mouse_position(event))
            minus_index = hit_index(
                self.attribute_minus_rects,
                mouse_position(event),
            )
            plus_index = hit_index(
                self.attribute_plus_rects,
                mouse_position(event),
            )
            if self.reset_button_rect.collidepoint(mouse_position(event)):
                self.focus = "reset"
                if is_left_click(event):
                    self._reset_pending()
                return True
            if self.spend_button_rect.collidepoint(mouse_position(event)):
                self.focus = "spend"
                if is_left_click(event):
                    self._spend_pending()
                return True
            if node_index is not None:
                self.focus = "nodes"
                self.current_node = node_index
                if is_left_click(event):
                    self._toggle_selected_node()
                return True
            if attribute_index is not None:
                self.focus = "attributes"
                self.current_attribute = attribute_index
                if is_left_click(event):
                    if minus_index is not None:
                        self._adjust_selected_attribute(-1)
                    elif plus_index is not None:
                        self._adjust_selected_attribute(1)
                return True
            return False
        if event.type != pygame.KEYDOWN:
            return False
        if event.key in (pygame.K_q, pygame.K_e):
            direction = -1 if event.key == pygame.K_q else 1
            self.tree_index = (self.tree_index + direction) % len(self._tree_ids())
            self.current_node = 0
            self.tree_scroll_row = 0
            return True
        if event.key == pygame.K_a:
            self.focus = "attributes" if self.focus == "nodes" else "nodes"
            return True
        if event.key == pygame.K_UP:
            if self.focus == "nodes":
                self.current_node = (self.current_node - 1) % len(self._statuses())
            else:
                self.current_attribute = (
                    self.current_attribute - 1
                ) % len(PRIMARY_ATTRIBUTES)
            return True
        if event.key == pygame.K_LEFT:
            if self.focus == "nodes":
                self.current_node = (self.current_node - 1) % len(self._statuses())
            else:
                self.current_attribute = (
                    self.current_attribute - 1
                ) % len(PRIMARY_ATTRIBUTES)
            return True
        if event.key == pygame.K_DOWN:
            if self.focus == "nodes":
                self.current_node = (self.current_node + 1) % len(self._statuses())
            else:
                self.current_attribute = (
                    self.current_attribute + 1
                ) % len(PRIMARY_ATTRIBUTES)
            return True
        if event.key == pygame.K_RIGHT:
            if self.focus == "nodes":
                self.current_node = (self.current_node + 1) % len(self._statuses())
            else:
                self.current_attribute = (
                    self.current_attribute + 1
                ) % len(PRIMARY_ATTRIBUTES)
            return True
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.focus == "nodes":
                self._toggle_selected_node()
            elif self.focus == "attributes":
                self._adjust_selected_attribute(1)
            elif self.focus == "reset":
                self._reset_pending()
            elif self.focus == "spend":
                self._spend_pending()
            return True
        if event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            if self.focus == "attributes":
                self._adjust_selected_attribute(-1)
                return True
        if event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
            if self.focus == "attributes":
                self._adjust_selected_attribute(1)
                return True
        if event.key == pygame.K_s:
            self.focus = "spend"
            self._spend_pending()
            return True
        if event.key == pygame.K_r:
            self.focus = "reset"
            self._reset_pending()
            return True
        return False

    def navigate(self):
        """Run the modal screen until the player returns."""
        while True:
            self.draw_all()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.confirm_discard_pending():
                            return
                    if event.key in (pygame.K_q, pygame.K_e):
                        direction = -1 if event.key == pygame.K_q else 1
                        self.tree_index = (
                            self.tree_index + direction
                        ) % len(self._tree_ids())
                        self.current_node = 0
                    if event.key == pygame.K_TAB:
                        self.focus = "attributes" if self.focus == "nodes" else "nodes"
                    elif event.key in (pygame.K_UP, pygame.K_LEFT):
                        if self.focus == "nodes":
                            self.current_node = (self.current_node - 1) % len(self._statuses())
                        else:
                            self.current_attribute = (self.current_attribute - 1) % len(PRIMARY_ATTRIBUTES)
                    elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
                        if self.focus == "nodes":
                            self.current_node = (self.current_node + 1) % len(self._statuses())
                        else:
                            self.current_attribute = (self.current_attribute + 1) % len(PRIMARY_ATTRIBUTES)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.focus == "nodes":
                            self._toggle_selected_node()
                        else:
                            self._adjust_selected_attribute(1)
                elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    node_index = hit_index(self.node_rects, mouse_position(event))
                    attribute_index = hit_index(self.attribute_rects, mouse_position(event))
                    if node_index is not None:
                        self.focus = "nodes"
                        self.current_node = node_index
                        if is_left_click(event):
                            self._toggle_selected_node()
                    elif attribute_index is not None:
                        self.focus = "attributes"
                        self.current_attribute = attribute_index
                        if is_left_click(event):
                            minus_index = hit_index(
                                self.attribute_minus_rects,
                                mouse_position(event),
                            )
                            plus_index = hit_index(
                                self.attribute_plus_rects,
                                mouse_position(event),
                            )
                            if minus_index is not None:
                                self._adjust_selected_attribute(-1)
                            elif plus_index is not None:
                                self._adjust_selected_attribute(1)
            self.presenter.clock.tick(30)
