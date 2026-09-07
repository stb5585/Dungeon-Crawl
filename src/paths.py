"""Stable read-only resources and writable per-user application paths."""

from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Mapping


APPLICATION_DIRECTORY_NAME = "the-forsaken-tenet"
SOURCE_ROOT = Path(__file__).resolve().parent


def resource_root() -> Path:
    """Return the checkout or frozen-bundle root containing runtime resources."""
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        return Path(frozen_root).resolve()
    return SOURCE_ROOT.parent


def default_user_data_dir(
    *,
    environment: Mapping[str, str] | None = None,
    platform: str | None = None,
    home: Path | None = None,
) -> Path:
    """Return the platform-appropriate writable application-data directory."""
    env = os.environ if environment is None else environment
    override = env.get("FORSAKEN_TENET_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()

    platform_name = sys.platform if platform is None else platform
    home_directory = Path.home() if home is None else home
    if platform_name == "win32":
        base = Path(env.get("LOCALAPPDATA", home_directory / "AppData" / "Local"))
        return base / "The Forsaken Tenet"
    if platform_name == "darwin":
        return home_directory / "Library" / "Application Support" / "The Forsaken Tenet"
    base = Path(env.get("XDG_DATA_HOME", home_directory / ".local" / "share"))
    return base / APPLICATION_DIRECTORY_NAME


RESOURCE_ROOT = resource_root()
PROJECT_ROOT = RESOURCE_ROOT
CORE_DATA_DIR = RESOURCE_ROOT / "src" / "core" / "data"
MAP_FILES_DIR = CORE_DATA_DIR / "maps"
PYGAME_ASSETS_DIR = RESOURCE_ROOT / "src" / "ui_pygame" / "assets"

USER_DATA_DIR = default_user_data_dir()
USER_SAVE_DIR = USER_DATA_DIR / "saves"
USER_TEMP_DIR = USER_DATA_DIR / "temporary"
USER_CONFIG_DIR = USER_DATA_DIR / "config"
DEBUG_LOGS_DIR = USER_DATA_DIR / "logs"
