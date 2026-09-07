# Generated Game Spreadsheets

These UTF-8 CSV files are reviewable snapshots of the current runtime catalogs.
They are organized as one file per Google Sheets tab:

- `characters/` contains race and class summaries, equipment restrictions,
  companions, and one current ability-tree export per class.
- `specials/` contains spells and skills, including acquisition sources.
- `items/` contains a complete item list and category-specific views.
- `enemies/` contains a complete roster, floor-specific views, special-area
  rosters, and natural equipment.
- `quests/quests.csv` contains every authored quest and its current text and
  rewards.

Do not edit generated CSVs by hand. Update the authoritative game data and run:

```bash
./.venv/bin/python tools/export_game_spreadsheets.py
```

The regression test in `tests/core/test_spreadsheet_exports.py` detects stale,
missing, or extra CSV files. Import each CSV as a separate Google Sheets tab;
formatting, charts, filters, and formulas should remain in Google Sheets rather
than becoming a second source of gameplay data.

Enemy minimum and maximum values are evaluated deterministically from the
runtime constructors by selecting the lower and upper outcomes of authored
random ranges. `Class ID` columns distinguish constructors that intentionally
share the same display name.
