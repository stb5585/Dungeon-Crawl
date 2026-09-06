"""Generate deterministic SVG reference diagrams from runtime ability trees."""

from __future__ import annotations

from html import escape
from pathlib import Path
import re

from .progression import (
    ABILITY_TREES,
    CLASS_DETAILS,
    NodeKind,
    effective_node_level_requirement,
)


OUTPUT_DIRECTORY = Path(__file__).parents[2] / "docs" / "ability_trees"
MANUALLY_AUTHORED_DIAGRAM_CLASSES = frozenset({"Mage"})
STAGE_DIRECTORY_NAMES = {
    1: "base",
    2: "first-promotion",
    3: "second-promotion",
}
STAGE_HEADINGS = {
    1: "Base class",
    2: "First promotions",
    3: "Second promotions",
}
NODE_WIDTH = 188
NODE_HEIGHT = 62
PROMOTION_NODE_HEIGHT = 84
COLUMN_GAP = 34
ROW_GAP = 38
MARGIN_X = 42
HEADER_HEIGHT = 92

KIND_COLORS = {
    NodeKind.ABILITY: ("#133047", "#54b8ed"),
    NodeKind.TALENT: ("#30254a", "#ae84e8"),
    NodeKind.RATING: ("#17383a", "#63d3ca"),
    NodeKind.HEALTH: ("#17383a", "#63d3ca"),
    NodeKind.MANA: ("#17383a", "#63d3ca"),
    NodeKind.PROMOTION: ("#3b2d12", "#f4bf2a"),
}
PASSIVE_COLORS = ("#263b2b", "#72c987")
RESOURCE_COLORS = {
    "Resolve": ("#3d2418", "#ed8a3d"),
    "Oath Conviction": ("#42360f", "#f0d45a"),
}
OTHER_RESOURCE_COLORS = ("#3b213f", "#d27adb")


def _node_resource_type(node) -> str | None:
    """Return a non-mana resource consumed by an ability node."""
    ability_class = node.payload.get("ability_class")
    if ability_class is None:
        return None
    try:
        resource_type = getattr(ability_class(), "resource_type", None)
    except Exception:
        return None
    if not resource_type or resource_type == "Mana":
        return None
    return str(resource_type)


def class_slug(class_name: str) -> str:
    """Return the stable diagram filename stem for a class."""
    return re.sub(r"[^a-z0-9]+", "-", class_name.lower()).strip("-")


def base_class_name(class_name: str) -> str:
    """Return the base-class lineage containing ``class_name``."""
    current = class_name
    while CLASS_DETAILS[current][2] is not None:
        current = str(CLASS_DETAILS[current][2])
    return current


def diagram_relative_path(class_name: str) -> Path:
    """Return a diagram path grouped by base lineage and promotion tier."""
    stage = int(CLASS_DETAILS[class_name][1])
    return (
        Path(class_slug(base_class_name(class_name)))
        / STAGE_DIRECTORY_NAMES[stage]
        / f"{class_slug(class_name)}.svg"
    )


def _node_xy(position: tuple[float, int]) -> tuple[float, float]:
    x, y = position
    return (
        MARGIN_X + x * (NODE_WIDTH + COLUMN_GAP),
        HEADER_HEIGHT + y * (NODE_HEIGHT + ROW_GAP),
    )


def _node_height(node) -> int:
    """Return card height, allowing promotion metadata a second line."""
    return PROMOTION_NODE_HEIGHT if node.kind == NodeKind.PROMOTION else NODE_HEIGHT


def render_tree_svg(class_name: str) -> str:
    """Render one runtime ability tree as a standalone SVG document."""
    tree = ABILITY_TREES[class_name]
    max_x = max((node.position[0] for node in tree.nodes), default=0)
    width = int(
        MARGIN_X * 2 + (max_x + 1) * NODE_WIDTH + max_x * COLUMN_GAP
    )
    max_bottom = max(
        (
            _node_xy(node.position)[1] + _node_height(node)
            for node in tree.nodes
        ),
        default=HEADER_HEIGHT,
    )
    height = int(max_bottom + 42)
    centers = {
        node.id: (
            _node_xy(node.position)[0] + NODE_WIDTH / 2,
            _node_xy(node.position)[1] + _node_height(node) / 2,
        )
        for node in tree.nodes
    }
    promotion_targets_by_source: dict[str, list[tuple[str, float]]] = {}
    for target_node in tree.nodes:
        if target_node.kind != NodeKind.PROMOTION:
            continue
        target_x = centers[target_node.id][0]
        for prerequisite in target_node.prerequisites:
            promotion_targets_by_source.setdefault(prerequisite, []).append(
                (target_node.id, target_x)
            )
    promotion_source_anchors: dict[tuple[str, str], float] = {}
    for source_id, targets in promotion_targets_by_source.items():
        if source_id not in centers:
            continue
        source_x = centers[source_id][0]
        source_left = source_x - NODE_WIDTH / 2
        ordered_targets = sorted(targets, key=lambda entry: entry[1])
        for edge_index, (target_id, _target_x) in enumerate(ordered_targets):
            promotion_source_anchors[(source_id, target_id)] = (
                source_left
                + NODE_WIDTH * (edge_index + 1) / (len(ordered_targets) + 1)
            )
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">'
        ),
        "<style>",
        "text{font-family:DejaVu Sans,Arial,sans-serif}",
        ".title{fill:#f4bf2a;font-size:24px;font-weight:700}",
        ".meta{fill:#aab2bf;font-size:12px}",
        ".name{fill:#f4f6fa;font-size:13px;font-weight:700}",
        ".detail{fill:#c5ccd6;font-size:11px}",
        ".resource{fill:#e6bfdc;font-size:9px;font-weight:700}",
        ".edge{fill:none;stroke:#7f8998;stroke-width:2}",
        ".promotion-edge{fill:none;stroke:#c59d3d;stroke-width:3}",
        "</style>",
        f'<rect width="{width}" height="{height}" fill="#10131a"/>',
        (
            f'<text class="title" x="{MARGIN_X}" y="38">'
            f"{escape(class_name)} Ability Tree</text>"
        ),
        (
            f'<text class="meta" x="{MARGIN_X}" y="62">'
            f"Tier {tree.stage} · {len(tree.nodes)} nodes · "
            f"{escape(' · '.join(tree.branches))}</text>"
        ),
    ]
    for node in tree.nodes:
        target_x, target_y = centers[node.id]
        if node.kind == NodeKind.PROMOTION:
            prerequisite_centers = sorted(
                (
                    (
                        prerequisite,
                        centers[prerequisite][0],
                        centers[prerequisite][1],
                    )
                    for prerequisite in node.prerequisites
                    if prerequisite in centers
                ),
                key=lambda entry: entry[1],
            )
            target_left = target_x - NODE_WIDTH / 2
            target_top = target_y - PROMOTION_NODE_HEIGHT / 2
            edge_count = len(prerequisite_centers)
            prerequisite_mode = node.payload.get("prerequisite_mode", "all")
            grouped_requirements = node.payload.get("prerequisite_groups")
            merge_paths = (
                prerequisite_mode != "any"
                and not grouped_requirements
                and edge_count > 1
            )
            source_rows = {
                prerequisite: next(
                    source.position[1]
                    for source in tree.nodes
                    if source.id == prerequisite
                )
                for prerequisite, _source_x, _source_y in prerequisite_centers
            }
            buffer_join_y = (
                _node_xy((0, node.position[1] - 1))[1] + NODE_HEIGHT / 2
            )
            has_buffer_row = (
                bool(source_rows)
                and node.position[1] - max(source_rows.values()) >= 2
            )
            join_y = buffer_join_y if has_buffer_row else target_top - 12
            for edge_index, (source_id, source_x, source_y) in enumerate(
                prerequisite_centers
            ):
                source_anchor_x = promotion_source_anchors.get(
                    (source_id, node.id),
                    source_x,
                )
                enters_left_side = (
                    not merge_paths and edge_count > 1 and edge_index == 0
                )
                enters_right_side = (
                    not merge_paths
                    and edge_count > 1
                    and edge_index == edge_count - 1
                )
                enters_side = enters_left_side or enters_right_side
                if merge_paths:
                    destination_x = target_x
                elif edge_count == 1:
                    destination_x = target_x
                elif enters_left_side:
                    destination_x = target_left
                elif enters_right_side:
                    destination_x = target_left + NODE_WIDTH
                else:
                    destination_x = (
                        target_left
                        + NODE_WIDTH * edge_index / (edge_count - 1)
                    )
                source_bottom = source_y + NODE_HEIGHT / 2
                destination_y = target_y if enters_side else join_y
                source_is_penultimate = (
                    has_buffer_row
                    and source_rows[source_id] == node.position[1] - 2
                )
                if source_is_penultimate or (
                    not enters_side
                    and target_top - source_bottom <= NODE_HEIGHT + ROW_GAP
                ):
                    path = (
                        f'M {source_anchor_x:.1f} {source_bottom:.1f} '
                        f'V {destination_y:.1f} H {destination_x:.1f}'
                    )
                else:
                    branch_y = source_bottom + 8
                    column_step = NODE_WIDTH + COLUMN_GAP
                    if source_x < target_x:
                        channel_x = source_x + column_step / 2
                    elif source_x > target_x:
                        channel_x = source_x - column_step / 2
                    else:
                        channel_x = source_x
                    path = (
                        f'M {source_anchor_x:.1f} {source_bottom:.1f} '
                        f'V {branch_y:.1f} H {channel_x:.1f} '
                        f'V {destination_y:.1f} '
                        f'H {destination_x:.1f}'
                    )
                lines.append(
                    f'<path class="promotion-edge" d="{path}"/>'
                )
                if not merge_paths and not enters_side:
                    lines.append(
                        f'<path class="promotion-edge" d="M {destination_x:.1f} '
                        f'{join_y:.1f} V {target_top:.1f}"/>'
                    )
            if merge_paths:
                lines.append(
                    f'<path class="promotion-edge" d="M {target_x:.1f} '
                    f'{join_y:.1f} V {target_top:.1f}"/>'
                )
            continue
        for prerequisite in node.prerequisites:
            if prerequisite not in centers:
                continue
            source_x, source_y = centers[prerequisite]
            channel_column = node.payload.get(
                "connector_channel_columns",
                {},
            ).get(prerequisite)
            if node.payload.get("connector_enter_from_top"):
                source_is_left = source_x < target_x
                source_side_x = source_x + (
                    NODE_WIDTH / 2 if source_is_left else -NODE_WIDTH / 2
                )
                channel_x = (
                    target_x
                    if channel_column is None
                    else _node_xy((channel_column, 0))[0] + NODE_WIDTH / 2
                )
                target_top = target_y - NODE_HEIGHT / 2
                lines.append(
                    f'<path class="edge" d="M {source_side_x:.1f} '
                    f'{source_y:.1f} H {channel_x:.1f} V {target_top:.1f} '
                    f'H {target_x:.1f}"/>'
                )
                continue
            if channel_column is not None:
                channel_x = _node_xy((channel_column, 0))[0] + NODE_WIDTH / 2
                source_is_left = source_x <= target_x
                source_side_x = source_x + (
                    NODE_WIDTH / 2 if source_is_left else -NODE_WIDTH / 2
                )
                if source_x == target_x:
                    target_side_x = target_x + (
                        NODE_WIDTH / 2
                        if channel_x >= target_x
                        else -NODE_WIDTH / 2
                    )
                else:
                    target_side_x = target_x + (
                        -NODE_WIDTH / 2 if source_is_left else NODE_WIDTH / 2
                    )
                lines.append(
                    f'<path class="edge" d="M {source_side_x:.1f} '
                    f'{source_y:.1f} H {channel_x:.1f} V {target_y:.1f} '
                    f'H {target_side_x:.1f}"/>'
                )
                continue
            middle_y = (
                target_y
                if node.payload.get("connector_join_at_target_row")
                else (source_y + target_y) / 2
            )
            lines.append(
                f'<path class="edge" d="M {source_x:.1f} {source_y:.1f} '
                f'V {middle_y:.1f} H {target_x:.1f} V {target_y:.1f}"/>'
            )
    for node in tree.nodes:
        x, y = _node_xy(node.position)
        node_height = _node_height(node)
        resource_type = _node_resource_type(node)
        if resource_type:
            fill, stroke = RESOURCE_COLORS.get(resource_type, OTHER_RESOURCE_COLORS)
        elif node.icon_key == "skill_passive":
            fill, stroke = PASSIVE_COLORS
        else:
            fill, stroke = KIND_COLORS[node.kind]
        level = effective_node_level_requirement(node, class_name)
        details = [node.kind.value.title(), f"Cost {node.cost}"]
        if level:
            details.append(f"Level {level}")
        promotion_detail = ""
        if node.kind == NodeKind.PROMOTION and node.prerequisites:
            groups = node.payload.get("prerequisite_groups")
            if groups:
                promotion_detail = f"Requires ALL {len(groups)} groups"
            else:
                prerequisite_mode = node.payload.get("prerequisite_mode", "all")
                path_noun = "path" if len(node.prerequisites) == 1 else "paths"
                if prerequisite_mode == "any":
                    promotion_detail = (
                        f"Requires 1 of {len(node.prerequisites)} {path_noun}"
                    )
                else:
                    promotion_detail = (
                        f"Requires ALL {len(node.prerequisites)} {path_noun}"
                    )
        # These diagrams are developer references, so quest-hidden nodes use
        # their authored names even while the player-facing tree says Unknown.
        name = str(node.payload.get("revealed_name", node.name))
        if len(name) > 20:
            name = f"{name[:17]}..."
        lines.extend((
            (
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{NODE_WIDTH}" '
                f'height="{node_height}" rx="8" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="2"/>'
            ),
            (
                f'<text class="name" x="{x + 10:.1f}" y="{y + 24:.1f}">'
                f"{escape(name)}</text>"
            ),
            (
                f'<text class="detail" x="{x + 10:.1f}" y="{y + 45:.1f}">'
                f"{escape(' · '.join(details))}</text>"
            ),
        ))
        if promotion_detail:
            lines.append(
                f'<text class="detail" x="{x + 10:.1f}" y="{y + 66:.1f}">'
                f"{escape(promotion_detail)}</text>"
            )
        elif resource_type:
            lines.append(
                f'<text class="resource" x="{x + 10:.1f}" y="{y + 57:.1f}">'
                f"Uses {escape(resource_type)}</text>"
            )
    lines.append("</svg>")
    return "\n".join(lines).rstrip() + "\n"


def render_index() -> str:
    """Render the generated diagram index."""
    lines = [
        "# Ability Tree Diagrams",
        "",
        "These SVGs are generated directly from the runtime progression graphs.",
        "The Mage SVG has manually authored connector routing and is preserved",
        "when diagrams are regenerated; its nodes still track the runtime tree.",
        "Run `./.venv/bin/python tools/generate_ability_tree_diagrams.py` after",
        "changing any tree. The drift test fails when these references are stale.",
        "Diagrams are grouped by base-class lineage and then promotion tier.",
        "See [Ability Tree Status](ABILITY_TREE_STATUS.md) for completion state and",
        "future-change policy.",
        "",
    ]
    base_classes = [
        class_name
        for class_name in ABILITY_TREES
        if CLASS_DETAILS[class_name][2] is None
    ]
    for base_class in base_classes:
        lines.extend((f"## {base_class} lineage", ""))
        for stage in STAGE_DIRECTORY_NAMES:
            members = [
                class_name
                for class_name, tree in ABILITY_TREES.items()
                if tree.stage == stage
                and base_class_name(class_name) == base_class
            ]
            if not members:
                continue
            lines.extend((f"### {STAGE_HEADINGS[stage]}", ""))
            for class_name in members:
                path = diagram_relative_path(class_name).as_posix()
                documentation_path = str(Path(path).with_suffix(".md"))
                lines.append(
                    f"- [{class_name}]({path}) - "
                    f"[documentation]({documentation_path})"
                )
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_all(output_directory: Path = OUTPUT_DIRECTORY) -> None:
    """Write all class diagrams and their index."""
    output_directory.mkdir(parents=True, exist_ok=True)
    for class_name in ABILITY_TREES:
        path = output_directory / diagram_relative_path(class_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        legacy_path = output_directory / f"{class_slug(class_name)}.svg"
        if (
            class_name in MANUALLY_AUTHORED_DIAGRAM_CLASSES
            and not path.exists()
            and legacy_path.exists()
        ):
            legacy_path.replace(path)
        if class_name in MANUALLY_AUTHORED_DIAGRAM_CLASSES and path.exists():
            if legacy_path.exists():
                legacy_path.unlink()
            continue
        path.write_text(render_tree_svg(class_name), encoding="utf-8")
        if legacy_path.exists():
            legacy_path.unlink()
    (output_directory / "README.md").write_text(
        render_index(),
        encoding="utf-8",
    )
