"""Regenerate CSV snapshots for Google Sheets and repository review."""

from src.core.spreadsheet_exports import write_all


if __name__ == "__main__":
    write_all()
