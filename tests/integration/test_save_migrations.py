"""Compatibility tests for versioned save migration and recovery."""

from __future__ import annotations

import json
from pathlib import Path

from src.core.progression import cumulative_experience_for_level
from src.core.save_system import (
    CURRENT_SAVE_VERSION,
    SaveManager,
    migrate_save_data,
)
from tests.test_framework import TestGameState

FIXTURE_PATH = Path(__file__).parents[1] / "fixtures" / "saves" / "master-v3-sorcerer.save"


def _configure_directories(monkeypatch, tmp_path: Path) -> Path:
    save_directory = tmp_path / "saves"
    monkeypatch.setattr(SaveManager, "SAVE_DIR", str(save_directory))
    monkeypatch.setattr(SaveManager, "TMP_DIR", str(tmp_path / "temporary"))
    SaveManager.ensure_dirs()
    return save_directory


def _legacy_fixture_text() -> str:
    return FIXTURE_PATH.read_text(encoding="utf-8")


def test_master_version_3_payload_maps_to_flat_progression():
    legacy = json.loads(_legacy_fixture_text())

    migration = migrate_save_data(legacy)

    assert migration.migrated is True
    assert migration.source_version == 3
    assert migration.data["version"] == CURRENT_SAVE_VERSION
    assert migration.data["progression"] == {
        "level": 37,
        "total_xp": cumulative_experience_for_level(37),
        "unspent_points": 19,
        "unspent_attribute_points": 0,
        "purchased_node_ids": ["mage.promotion.sorcerer"],
        "trained_attributes": {},
        "ability_ranks": {},
        "completed_trees": ["Mage"],
        "chosen_promotions": {"Mage": "Sorcerer"},
    }
    assert legacy["version"] == 3
    assert "progression" not in legacy


def test_loading_version_3_creates_backup_and_persists_current_save(monkeypatch, tmp_path):
    save_directory = _configure_directories(monkeypatch, tmp_path)
    save_path = save_directory / "legacy.save"
    original_text = _legacy_fixture_text()
    save_path.write_text(original_text, encoding="utf-8")

    result = SaveManager.load_player_result("legacy.save", skip_tiles=True)

    assert result.error is None
    assert result.player is not None
    assert result.player.name == "Legacy Sorcerer"
    assert result.player.cls.name == "Sorcerer"
    assert result.player.progression.level == 37
    assert result.migrated_from_version == 3
    assert result.backup_path == f"{save_path}.v3.bak"
    assert Path(result.backup_path).read_text(encoding="utf-8") == original_text
    assert json.loads(save_path.read_text(encoding="utf-8"))["version"] == CURRENT_SAVE_VERSION


def test_invalid_legacy_data_is_rejected_without_rewriting(monkeypatch, tmp_path):
    save_directory = _configure_directories(monkeypatch, tmp_path)
    save_path = save_directory / "invalid.save"
    payload = json.loads(_legacy_fixture_text())
    payload["class_name"] = "Missing Class"
    original_text = json.dumps(payload)
    save_path.write_text(original_text, encoding="utf-8")

    result = SaveManager.load_player_result("invalid.save", skip_tiles=True)

    assert result.player is None
    assert "Unknown legacy class" in result.error
    assert save_path.read_text(encoding="utf-8") == original_text
    assert not Path(f"{save_path}.v3.bak").exists()


def test_interrupted_migration_write_preserves_original_and_backup(
    monkeypatch,
    tmp_path,
):
    save_directory = _configure_directories(monkeypatch, tmp_path)
    save_path = save_directory / "interrupted.save"
    original_text = _legacy_fixture_text()
    save_path.write_text(original_text, encoding="utf-8")

    def fail_replace(_source, _destination):
        raise OSError("simulated interruption")

    monkeypatch.setattr("src.core.save_system.manager.os.replace", fail_replace)

    result = SaveManager.load_player_result("interrupted.save", skip_tiles=True)

    assert result.player is not None
    assert result.migrated_from_version == 3
    assert result.backup_path == f"{save_path}.v3.bak"
    assert "could not be written" in result.warning
    assert save_path.read_text(encoding="utf-8") == original_text
    assert Path(f"{save_path}.v3.bak").read_text(encoding="utf-8") == original_text
    assert not Path(f"{save_path}.tmp").exists()


def test_version_4_error_describes_repository_history(monkeypatch, tmp_path):
    save_directory = _configure_directories(monkeypatch, tmp_path)
    save_path = save_directory / "version-4.save"
    save_path.write_text('{"version": 4}', encoding="utf-8")

    result = SaveManager.load_player_result("version-4.save", skip_tiles=True)

    assert result.player is None
    assert result.unsupported_version is True
    assert "never produced by a committed save serializer" in result.error


def test_current_version_file_round_trip_does_not_create_backup(monkeypatch, tmp_path):
    save_directory = _configure_directories(monkeypatch, tmp_path)
    player = TestGameState.create_player(
        name="Current",
        class_name="Warrior",
        race_name="Human",
        level=12,
    )

    assert SaveManager.save_player(player, "current.save") is True
    result = SaveManager.load_player_result("current.save", skip_tiles=True)

    assert result.player is not None
    assert result.player.name == "Current"
    assert result.migrated_from_version is None
    assert result.backup_path is None
    assert not Path(f"{save_directory / 'current.save'}.v5.bak").exists()
