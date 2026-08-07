"""Generate deterministic SVG reference diagrams from runtime ability trees."""

from __future__ import annotations

from html import escape
from pathlib import Path
import re

from .progression import (
    ABILITY_TREES,
    NodeKind,
    effective_node_level_requirement,
)


OUTPUT_DIRECTORY = Path(__file__).parents[2] / "docs" / "ability_trees"
NODE_WIDTH = 188
NODE_HEIGHT = 62
COLUMN_GAP = 34
ROW_GAP = 38
MARGIN_X = 42
HEADER_HEIGHT = 92

KIND_COLORS = {
    NodeKind.ABILITY: ("#133047", "#54b8ed"),
    NodeKind.TALENT: ("#30254a", "#ae84e8"),
    NodeKind.RATING: ("#3b3218", "#e3bc48"),
    NodeKind.HEALTH: ("#401d25", "#e46b78"),
    NodeKind.MANA: ("#182f45", "#6aa8e8"),
    NodeKind.PROMOTION: ("#3b2d12", "#f4bf2a"),
}


def class_slug(class_name: str) -> str:
    """Return the stable diagram filename stem for a class."""
    return re.sub(r"[^a-z0-9]+", "-", class_name.lower()).strip("-")


def _node_xy(position: tuple[float, int]) -> tuple[float, float]:
    x, y = position
    return (
        MARGIN_X + x * (NODE_WIDTH + COLUMN_GAP),
        HEADER_HEIGHT + y * (NODE_HEIGHT + ROW_GAP),
    )


def render_tree_svg(class_name: str) -> str:
    """Render one runtime ability tree as a standalone SVG document."""
    tree = ABILITY_TREES[class_name]
    max_x = max((node.position[0] for node in tree.nodes), default=0)
    max_y = max((node.position[1] for node in tree.nodes), default=0)
    width = int(
        MARGIN_X * 2 + (max_x + 1) * NODE_WIDTH + max_x * COLUMN_GAP
    )
    height = int(
        HEADER_HEIGHT + (max_y + 1) * NODE_HEIGHT + max_y * ROW_GAP + 42
    )
    centers = {
        node.id: (
            _node_xy(node.position)[0] + NODE_WIDTH / 2,
            _node_xy(node.position)[1] + NODE_HEIGHT / 2,
        )
        for node in tree.nodes
    }
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
        ".edge{fill:none;stroke:#7f8998;stroke-width:2}",
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
        for prerequisite in node.prerequisites:
            if prerequisite not in centers:
                continue
            source_x, source_y = centers[prerequisite]
            middle_y = (source_y + target_y) / 2
            lines.append(
                f'<path class="edge" d="M {source_x:.1f} {source_y:.1f} '
                f'V {middle_y:.1f} H {target_x:.1f} V {target_y:.1f}"/>'
            )
    for node in tree.nodes:
        x, y = _node_xy(node.position)
        fill, stroke = KIND_COLORS[node.kind]
        level = effective_node_level_requirement(node, class_name)
        details = [node.kind.value.title(), f"Cost {node.cost}"]
        if level:
            details.append(f"Level {level}")
        name = node.name
        if len(name) > 25:
            name = f"{name[:22]}..."
        lines.extend((
            (
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{NODE_WIDTH}" '
                f'height="{NODE_HEIGHT}" rx="8" fill="{fill}" '
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
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def render_index() -> str:
    """Render the generated diagram index."""
    lines = [
        "# Ability Tree Diagrams",
        "",
        "These SVGs are generated directly from the runtime progression graphs.",
        "Run `./.venv/bin/python tools/generate_ability_tree_diagrams.py` after",
        "changing any tree. The drift test fails when these references are stale.",
        "",
    ]
    for class_name in ABILITY_TREES:
        lines.append(f"- [{class_name}]({class_slug(class_name)}.svg)")
    return "\n".join(lines) + "\n"


def write_all(output_directory: Path = OUTPUT_DIRECTORY) -> None:
    """Write all class diagrams and their index."""
    output_directory.mkdir(parents=True, exist_ok=True)
    for class_name in ABILITY_TREES:
        path = output_directory / f"{class_slug(class_name)}.svg"
        path.write_text(render_tree_svg(class_name), encoding="utf-8")
    (output_directory / "README.md").write_text(
        render_index(),
        encoding="utf-8",
    )
