#!/usr/bin/env python3
"""Run the deferred-improvement balance baseline bundle."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "reports" / "balance_baselines"
DEFAULT_PYTHON = "./.venv/bin/python"


@dataclass(frozen=True)
class BaselineCommand:
    label: str
    args: tuple[str, ...]

    def command(self, python_executable: str = DEFAULT_PYTHON) -> list[str]:
        return [python_executable, *self.args]

    def display(self, python_executable: str = DEFAULT_PYTHON) -> str:
        return " ".join(self.command(python_executable))


CANONICAL_BASELINE_COMMANDS: tuple[BaselineCommand, ...] = (
    BaselineCommand(
        "base_level_10",
        ("tools/run_balance_suite.py", "--tier", "base", "--level", "10", "--iters", "30", "--seed", "1337"),
    ),
    BaselineCommand(
        "first_level_20",
        ("tools/run_balance_suite.py", "--tier", "first", "--level", "20", "--iters", "30", "--seed", "1337"),
    ),
    BaselineCommand(
        "second_level_30",
        ("tools/run_balance_suite.py", "--tier", "second", "--level", "30", "--iters", "30", "--seed", "1337"),
    ),
    BaselineCommand(
        "race_delta_level_20",
        (
            "tools/run_balance_suite.py",
            "--tier",
            "all",
            "--level",
            "20",
            "--iters",
            "30",
            "--seed",
            "1337",
            "--races",
            "Human",
            "Elf",
            "Half Elf",
            "Half Giant",
            "Gnome",
            "Dwarf",
            "Half Orc",
            "--delta",
            "--baseline-race",
            "Human",
        ),
    ),
)


def timestamp_slug(now: datetime | None = None) -> str:
    """Return the timestamp slug used for baseline report bundles."""
    return (now or datetime.now()).strftime("%Y%m%d_%H%M%S")


def remaining_tuning_targets() -> dict[str, object]:
    """Expose deferred tuning targets without touching balance constants."""
    from src.core.analytics.combat_simulator import remaining_improvement_tuning_report

    return remaining_improvement_tuning_report()


def planned_baseline_payload(
    *,
    output_dir: Path,
    timestamp: str,
    python_executable: str = DEFAULT_PYTHON,
) -> dict[str, object]:
    """Return the deterministic summary shape for a baseline bundle."""
    bundle_dir = Path(output_dir) / timestamp
    return {
        "timestamp": timestamp,
        "output_dir": str(bundle_dir),
        "commands": [
            {
                "label": command.label,
                "command": command.display(python_executable),
                "stdout_path": str(bundle_dir / f"{index:02d}_{command.label}.txt"),
                "stderr_path": str(bundle_dir / f"{index:02d}_{command.label}.err"),
            }
            for index, command in enumerate(CANONICAL_BASELINE_COMMANDS, start=1)
        ],
        "remaining_tuning_targets": remaining_tuning_targets(),
    }


def write_baseline_summary(
    *,
    output_dir: Path,
    timestamp: str,
    python_executable: str = DEFAULT_PYTHON,
    results: list[dict[str, object]] | None = None,
) -> tuple[Path, Path]:
    """Write text and JSON summaries for a baseline run."""
    payload = planned_baseline_payload(
        output_dir=output_dir,
        timestamp=timestamp,
        python_executable=python_executable,
    )
    if results is not None:
        payload["results"] = results

    bundle_dir = Path(payload["output_dir"])
    bundle_dir.mkdir(parents=True, exist_ok=True)

    json_path = bundle_dir / "remaining_balance_baseline_summary.json"
    text_path = bundle_dir / "remaining_balance_baseline_summary.txt"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "Remaining Improvement Balance Baseline",
        f"Timestamp: {timestamp}",
        "",
        "Commands:",
    ]
    for command in payload["commands"]:
        lines.append(f"- {command['label']}: {command['command']}")
    lines.extend(["", "Deferred tuning targets:"])
    for key, target in payload["remaining_tuning_targets"].items():
        metrics = ", ".join(target.get("metrics", ())) if isinstance(target, dict) else ""
        lines.append(f"- {key}: {metrics}")
    if results is not None:
        lines.extend(["", "Results:"])
        for result in results:
            lines.append(f"- {result['label']}: returncode={result['returncode']}")
    text_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return text_path, json_path


def run_baseline_bundle(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    timestamp: str | None = None,
    python_executable: str = DEFAULT_PYTHON,
    dry_run: bool = False,
) -> tuple[Path, Path]:
    """Run or dry-run the canonical baseline bundle and write summaries."""
    ts = timestamp or timestamp_slug()
    bundle_dir = Path(output_dir) / ts
    bundle_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, object]] = []
    for index, command in enumerate(CANONICAL_BASELINE_COMMANDS, start=1):
        stdout_path = bundle_dir / f"{index:02d}_{command.label}.txt"
        stderr_path = bundle_dir / f"{index:02d}_{command.label}.err"
        if dry_run:
            stdout_path.write_text(f"DRY RUN: {command.display(python_executable)}\n", encoding="utf-8")
            stderr_path.write_text("", encoding="utf-8")
            returncode = 0
        else:
            completed = subprocess.run(
                command.command(python_executable),
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            stdout_path.write_text(completed.stdout, encoding="utf-8")
            stderr_path.write_text(completed.stderr, encoding="utf-8")
            returncode = completed.returncode
        results.append(
            {
                "label": command.label,
                "returncode": returncode,
                "stdout_path": str(stdout_path),
                "stderr_path": str(stderr_path),
            }
        )

    return write_baseline_summary(
        output_dir=output_dir,
        timestamp=ts,
        python_executable=python_executable,
        results=results,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--timestamp", type=str, default=None)
    parser.add_argument("--python", dest="python_executable", default=DEFAULT_PYTHON)
    parser.add_argument("--dry-run", action="store_true", help="Write the bundle plan without running simulations.")
    args = parser.parse_args()

    text_path, json_path = run_baseline_bundle(
        output_dir=args.output_dir,
        timestamp=args.timestamp,
        python_executable=args.python_executable,
        dry_run=args.dry_run,
    )
    print(f"Wrote {text_path}")
    print(f"Wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
