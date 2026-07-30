"""Player save-loading helpers."""

import os

from ..save_system import SaveManager


def load_char(char=None, filename=None, is_tmp=False):
    """
    Initializes the character based on the save file using the data-driven save system.

    Args:
        char: Optional character instance; if provided, loads from tmp_files/<name>.save
        filename: Explicit filename to load (e.g., "myhero.save")
        is_tmp: Whether to load from tmp_files instead of save_files
    """
    target_filename = filename
    target_tmp = is_tmp

    if char and not filename:
        target_filename = f"{str(char.name).lower()}.save"
        target_tmp = True

    if not target_filename:
        return None

    # Skip tiles when loading for transform (only need character stats)
    player = SaveManager.load_player(target_filename, is_tmp=target_tmp, skip_tiles=True)
    if player and target_tmp:
        try:
            os.remove(f"tmp_files/{target_filename}")
        except FileNotFoundError:
            pass
    return player
