"""Regression coverage for generated game-catalog spreadsheets."""

from src.core.spreadsheet_exports import OUTPUT_DIRECTORY, render_all, write_all


def test_generated_spreadsheets_match_runtime_catalogs():
    expected = render_all()
    actual = {path.relative_to(OUTPUT_DIRECTORY) for path in OUTPUT_DIRECTORY.rglob("*.csv")}

    assert actual == set(expected)
    for relative_path, content in expected.items():
        assert (OUTPUT_DIRECTORY / relative_path).read_text(
            encoding="utf-8",
        ) == content


def test_spreadsheet_exports_cover_current_catalogs():
    exports = render_all()
    spells = exports[next(path for path in exports if path.as_posix() == "specials/spells.csv")]
    floor_four = exports[next(path for path in exports if path.as_posix() == "enemies/floor-4.csv")]
    classes = exports[next(path for path in exports if path.as_posix() == "characters/classes.csv")]

    assert len(exports) >= 70
    assert "Volcano" in spells
    assert "Necromancer" in floor_four
    assert "Astromancer" in classes


def test_write_all_removes_obsolete_managed_csv(tmp_path):
    obsolete_path = tmp_path / "characters" / "retired-class.csv"
    obsolete_path.parent.mkdir(parents=True)
    obsolete_path.write_text("stale\n", encoding="utf-8")
    unmanaged_path = tmp_path / "notes.csv"
    unmanaged_path.write_text("preserved\n", encoding="utf-8")

    write_all(tmp_path)

    assert not obsolete_path.exists()
    assert unmanaged_path.read_text(encoding="utf-8") == "preserved\n"
