"""
Presentation Module for The Forsaken Tenet

Provides abstract interfaces and implementations for different UI technologies.
"""

from .interface import (
    ConsolePresenter,
    EventDrivenPresenter,
    GamePresenter,
    NullPresenter,
)

__all__ = [
    "GamePresenter",
    "NullPresenter",
    "EventDrivenPresenter",
    "ConsolePresenter",
]
