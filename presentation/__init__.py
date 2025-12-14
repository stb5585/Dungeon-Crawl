"""
Presentation Module for Dungeon Crawl

Provides abstract interfaces and implementations for different UI technologies.
"""

from presentation.interface import (
    GamePresenter,
    NullPresenter,
    EventDrivenPresenter,
    ConsolePresenter,
)

__all__ = [
    'GamePresenter',
    'NullPresenter',
    'EventDrivenPresenter',
    'ConsolePresenter',
]
