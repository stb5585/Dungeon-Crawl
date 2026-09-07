"""Save-file persistence manager."""

import json
import os
from dataclasses import dataclass

from .migrations import (
    UnsupportedSaveVersionError,
    migrate_save_data,
)
from .player import PlayerDataSerializer


@dataclass(frozen=True)
class SaveLoadResult:
    """Explicit save-load outcome for UI error reporting."""

    player: object | None
    error: str | None = None
    unsupported_version: bool = False
    migrated_from_version: int | None = None
    backup_path: str | None = None
    warning: str | None = None


class SaveManager:
    """High-level save/load management."""

    SAVE_DIR = "save_files"
    TMP_DIR = "tmp_files"
    last_load_result = SaveLoadResult(None)

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
    def _write_json_atomic(filepath: str, data: dict[str, object]) -> None:
        """Replace one JSON file only after a complete, durable temporary write."""
        tmp_filepath = f"{filepath}.tmp"
        try:
            with open(tmp_filepath, "w", encoding="utf-8") as file_obj:
                json.dump(data, file_obj, indent=2, default=str)
                file_obj.flush()
                os.fsync(file_obj.fileno())
            os.replace(tmp_filepath, filepath)
        except (OSError, TypeError, ValueError):
            try:
                os.remove(tmp_filepath)
            except FileNotFoundError:
                pass
            raise

    @staticmethod
    def _persist_migration(
        filepath: str,
        original_text: str,
        migrated_data: dict[str, object],
        source_version: int,
    ) -> str:
        """Back up a legacy save and atomically replace it with migrated JSON."""
        backup_path = f"{filepath}.v{source_version}.bak"
        try:
            with open(backup_path, "x", encoding="utf-8") as backup_file:
                backup_file.write(original_text)
                backup_file.flush()
                os.fsync(backup_file.fileno())
        except FileExistsError:
            pass
        SaveManager._write_json_atomic(filepath, migrated_data)
        return backup_path

    @staticmethod
    def save_player(player, filename: str, is_tmp: bool = False) -> bool:
        """Save player to file."""
        SaveManager.ensure_dirs()

        try:
            filepath = SaveManager._resolve_save_path(filename, is_tmp=is_tmp)
            data = PlayerDataSerializer.serialize(player)
            SaveManager._write_json_atomic(filepath, data)
            return True
        except (OSError, TypeError, ValueError) as e:
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
        result = SaveManager.load_player_result(
            filename,
            is_tmp=is_tmp,
            skip_tiles=skip_tiles,
        )
        return result.player

    @staticmethod
    def load_player_result(
        filename: str,
        is_tmp: bool = False,
        skip_tiles: bool = False,
    ) -> SaveLoadResult:
        """Load a player and retain a clear unsupported-version outcome."""
        try:
            filepath = SaveManager._resolve_save_path(filename, is_tmp=is_tmp)

            if not os.path.isfile(filepath):
                result = SaveLoadResult(None, "Save file not found.")
                SaveManager.last_load_result = result
                return result

            with open(filepath, "r", encoding="utf-8") as file_obj:
                original_text = file_obj.read()
            data = json.loads(original_text)
            migration = migrate_save_data(data)
            player = PlayerDataSerializer.deserialize(
                migration.data,
                skip_tiles=skip_tiles,
            )
            backup_path = None
            warning = None
            if migration.migrated:
                try:
                    backup_path = SaveManager._persist_migration(
                        filepath,
                        original_text,
                        migration.data,
                        migration.source_version,
                    )
                except OSError as error:
                    candidate_backup = f"{filepath}.v{migration.source_version}.bak"
                    if os.path.isfile(candidate_backup):
                        backup_path = candidate_backup
                    warning = (
                        "Save loaded after in-memory migration, but the migrated file "
                        f"could not be written: {error}"
                    )
            result = SaveLoadResult(
                player,
                migrated_from_version=(
                    migration.source_version if migration.migrated else None
                ),
                backup_path=backup_path,
                warning=warning,
            )
            SaveManager.last_load_result = result
            return result
        except UnsupportedSaveVersionError as error:
            result = SaveLoadResult(None, str(error), unsupported_version=True)
            SaveManager.last_load_result = result
            return result
        except (
            AttributeError,
            IndexError,
            KeyError,
            OSError,
            TypeError,
            ValueError,
        ) as e:
            print(f"Error loading player: {e}")
            result = SaveLoadResult(None, f"Unable to load save: {e}")
            SaveManager.last_load_result = result
            return result

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
