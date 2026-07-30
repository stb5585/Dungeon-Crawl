"""Stable filesystem locations for project data and runtime assets."""

from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = SOURCE_ROOT.parent
CORE_DATA_DIR = SOURCE_ROOT / "core" / "data"
MAP_FILES_DIR = PROJECT_ROOT / "map_files"
PYGAME_ASSETS_DIR = SOURCE_ROOT / "ui_pygame" / "assets"
DEBUG_LOGS_DIR = PROJECT_ROOT / "debug_logs"
