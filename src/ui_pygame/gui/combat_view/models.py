"""Models behavior for the combat view package."""

from dataclasses import dataclass
from pathlib import Path


ASSETS_BASE_DIR=Path(__file__).resolve().parents[2]/"assets"


@dataclass
class CombatImpactEffect:
    """Brief procedural combat polish drawn over the current battlefield."""

    target: str
    kind: str
    color: tuple[int, int, int]
    start_ms: int
    duration_ms: int = 420
    critical: bool = False


@dataclass
class FloatingCombatText:
    """Small transient combat result text anchored near a target."""

    target: str
    text: str
    color: tuple[int, int, int]
    start_ms: int
    duration_ms: int = 760


@dataclass(frozen=True)
class CombatLogLine:
    """A render-ready combat log fragment with source-message styling."""

    text: str
    color: tuple[int, int, int]
    marker_color: tuple[int, int, int]
    continuation: bool = False
