#!/usr/bin/env python3
"""Validate canonical ability metadata and the shrinking legacy allowlist."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.data.ability_schema import validate_ability_directory


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Reject every definition that still relies on the migration allowlist.",
    )
    args = parser.parse_args()
    report = validate_ability_directory(require_complete=args.require_complete)
    for issue in report.issues:
        print(f"{issue.ability_id}: {issue.code}: {issue.message}")
    print(
        f"Validated {len(report.definitions)} typed abilities; "
        f"{len(report.legacy_ability_ids)} legacy abilities remain."
    )
    return 0 if report.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
