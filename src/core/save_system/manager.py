"""Save-file persistence manager."""

import json
import os

from .player import PlayerDataSerializer


class SaveManager:
    """High-level save/load management."""

    SAVE_DIR = "save_files"
    TMP_DIR = "tmp_files"

    @staticmethod
    def is_valid_save_filename(filename: object) -> bool:
        """Return True when filename is safe to resolve inside save directories."""
        separators = {os.sep, os.altsep, "/", "\\"}
        return (
            isinstance(filename, str)
            and bool(filename.strip())
            and filename not in {".", ".."}
            and not os.path.isabs(filename)
            and not any(sep and sep in filename for sep in separators)
        )

    @staticmethod
    def _resolve_save_path(filename: str, is_tmp: bool = False) -> str:
        """Return a save path confined to the configured save directory."""
        if not SaveManager.is_valid_save_filename(filename):
            raise ValueError(f"Invalid save filename: {filename!r}")

        directory = SaveManager.TMP_DIR if is_tmp else SaveManager.SAVE_DIR
        return os.path.join(directory, filename)

    @staticmethod
    def ensure_dirs():
        """Ensure save directories exist."""
        for dir_path in [SaveManager.SAVE_DIR, SaveManager.TMP_DIR]:
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path, exist_ok=True)

    @staticmethod
    def save_player(player, filename: str, is_tmp: bool = False) -> bool:
        """Save player to file."""
        SaveManager.ensure_dirs()

        tmp_filepath = None
        try:
            filepath = SaveManager._resolve_save_path(filename, is_tmp=is_tmp)
            tmp_filepath = f"{filepath}.tmp"

            # Serialize player
            data = PlayerDataSerializer.serialize(player)

            # Write atomically so a failed save does not corrupt the prior file.
            with open(tmp_filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            os.replace(tmp_filepath, filepath)

            return True
        except Exception as e:
            if tmp_filepath and os.path.exists(tmp_filepath):
                try:
                    os.remove(tmp_filepath)
                except OSError:
                    pass
            print(f"Error saving player: {e}")
            return False

    @staticmethod
    def load_player(filename: str, is_tmp: bool = False, skip_tiles=False):
        """Load player from file.

        Args:
            filename: Name of save file
            is_tmp: Whether to load from tmp directory
            skip_tiles: If True, skip loading world tiles (for transform feature)
        """
        try:
            filepath = SaveManager._resolve_save_path(filename, is_tmp=is_tmp)

            if not os.path.isfile(filepath):
                return None

            # Load JSON
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Deserialize player
            player = PlayerDataSerializer.deserialize(data, skip_tiles=skip_tiles)
            return player
        except Exception as e:
            print(f"Error loading player: {e}")
            return None

    @staticmethod
    def list_saves() -> list[str]:
        """List all save files."""
        SaveManager.ensure_dirs()
        if not os.path.isdir(SaveManager.SAVE_DIR):
            return []
        saves = []
        for filename in os.listdir(SaveManager.SAVE_DIR):
            filepath = os.path.join(SaveManager.SAVE_DIR, filename)
            if filename.endswith('.save') and os.path.isfile(filepath):
                saves.append(filename)
        return sorted(saves)

    @staticmethod
    def describe_save_file(filename: object, is_tmp: bool = False) -> dict[str, object]:
        """Return filesystem metadata for one save entry without reading its contents."""
        metadata: dict[str, object] = {
            "filename": filename,
            "is_tmp": is_tmp,
            "valid": SaveManager.is_valid_save_filename(filename),
            "expected_extension": ".tmp" if is_tmp else ".save",
            "extension_matches_expected": False,
            "path": None,
            "exists": False,
            "is_file": False,
            "is_dir": False,
            "loadable": False,
            "size": None,
            "empty": False,
        }
        if not metadata["valid"]:
            return metadata

        metadata["extension_matches_expected"] = str(filename).endswith(
            str(metadata["expected_extension"])
        )
        filepath = SaveManager._resolve_save_path(filename, is_tmp=is_tmp)
        metadata["path"] = filepath
        metadata["exists"] = os.path.exists(filepath)
        metadata["is_file"] = os.path.isfile(filepath)
        metadata["is_dir"] = os.path.isdir(filepath)
        metadata["loadable"] = bool(metadata["valid"] and metadata["is_file"])
        if metadata["is_file"]:
            try:
                metadata["size"] = os.path.getsize(filepath)
                metadata["empty"] = metadata["size"] == 0
            except OSError:
                metadata["size"] = None
                metadata["empty"] = False
        return metadata

    @staticmethod
    def list_save_metadata() -> list[dict[str, object]]:
        """Return metadata for player-visible save files in load-menu order."""
        return [
            SaveManager.describe_save_file(filename)
            for filename in SaveManager.list_saves()
        ]

    @staticmethod
    def summarize_save_metadata() -> dict[str, object]:
        """Return compact summary diagnostics for player-visible save files."""
        metadata = SaveManager.list_save_metadata()
        sizes = [entry["size"] for entry in metadata if isinstance(entry.get("size"), int)]
        largest = max(
            metadata,
            key=lambda entry: entry["size"] if isinstance(entry.get("size"), int) else -1,
            default=None,
        )
        return {
            "visible_count": len(metadata),
            "visible_filenames": [entry["filename"] for entry in metadata],
            "loadable_count": sum(1 for entry in metadata if entry.get("loadable")),
            "total_size": sum(sizes),
            "empty_save_count": sum(1 for size in sizes if size == 0),
            "largest_save": None if largest is None else largest["filename"],
            "largest_size": None if largest is None else largest["size"],
        }

    @staticmethod
    def summarize_save_directory() -> dict[str, object]:
        """Return compact diagnostics for visible and hidden save-directory entries."""
        SaveManager.ensure_dirs()
        visible = set(SaveManager.list_saves())
        directory_entry_filenames: list[str] = []
        tmp_leftover_filenames: list[str] = []
        ignored_filenames: list[str] = []

        for filename in os.listdir(SaveManager.SAVE_DIR):
            filepath = os.path.join(SaveManager.SAVE_DIR, filename)
            if filename in visible:
                continue
            if filename.endswith(".tmp"):
                tmp_leftover_filenames.append(filename)
            elif filename.endswith(".save") and os.path.isdir(filepath):
                directory_entry_filenames.append(filename)
            else:
                ignored_filenames.append(filename)

        return {
            "visible_count": len(visible),
            "visible_filenames": sorted(visible),
            "tmp_leftover_count": len(tmp_leftover_filenames),
            "tmp_leftover_filenames": sorted(tmp_leftover_filenames),
            "directory_entry_count": len(directory_entry_filenames),
            "directory_entry_filenames": sorted(directory_entry_filenames),
            "ignored_entry_count": len(ignored_filenames),
            "ignored_filenames": sorted(ignored_filenames),
            "hidden_entry_count": (
                len(tmp_leftover_filenames)
                + len(directory_entry_filenames)
                + len(ignored_filenames)
            ),
        }

    @staticmethod
    def delete_save(filename: str) -> bool:
        """Delete a save file."""
        try:
            filepath = SaveManager._resolve_save_path(filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
                return True
        except Exception:
            pass
        return False
