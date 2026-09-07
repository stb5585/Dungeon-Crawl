# Stabilization Checklist

This record separates completed promotion-readiness work from known follow-up
work. It describes stabilization of the `improvements` branch, not new gameplay
scope.

## Completed

- [x] Confirm save-version history: committed serializers produced version 3,
  followed by a direct transition to version 5; no committed version 4 writer
  exists.
- [x] Migrate validated version 3 saves to version 5 with recoverable backups,
  atomic replacement, structured warnings, and regression fixtures.
- [x] Reject unknown versions and version 4 with accurate diagnostics.
- [x] Centralize checkout/frozen resource paths and platform user-data paths.
- [x] Package runtime maps and Pygame assets in a PyInstaller onedir build.
- [x] Add a noninteractive frozen startup and resource-discovery smoke mode.
- [x] Make fatal startup failures nonzero and register signal handlers only in
  executable startup.
- [x] Retain structured event-dispatch failures while allowing healthy
  subscribers to continue.
- [x] Separate generated review sheets from runtime assets.
- [x] Add the MIT `LICENSE` and an asset provenance inventory.
- [x] Apply Black and isort in isolated mechanical commits.
- [x] Replace automatic push artifacts with manual/release-only artifact builds.

## Enforced Quality Baseline

Ordinary CI runs the full test suite with `src` coverage reporting, compiles
`src`, checks Black and isort across tracked source/test/tool directories, and
applies Ruff correctness rules to the stabilization-critical files. Ruff
ignores `F401` only in `__init__.py` files because those imports intentionally
define public and compatibility APIs.

The strict mypy baseline is deliberately incremental:

```bash
./.venv/bin/mypy --strict --follow-imports=skip \
  src/paths.py \
  src/core/save_system/migrations.py \
  tools/build_distribution.py
```

`--follow-imports=skip` prevents the three strict modules from inheriting the
unrelated legacy annotation backlog through imports. New stabilized packages
should be added to this list only after they pass strictly.

## Remaining Blockers And Owner Decisions

- **Audio attribution:** the exact source pages and license terms for existing
  audio are unknown. The owner must supply them before public distribution can
  claim complete asset attribution. See `ASSET_PROVENANCE.md`.
- **Platform artifacts:** the Linux onedir artifact is verified. Native Windows
  and macOS builds still require builds and smoke tests on those platforms.
- **Version 3 partial experience:** old saves do not contain enough reliable
  information to reconstruct progress within a level. Migration intentionally
  places the player at the reconstructed level threshold. Changing that policy
  requires an owner decision or new historical evidence.
- **Version 4 saves:** none can be migrated without a real version 4 fixture or
  serializer contract. If an owner-held version 4 save exists, preserve it and
  derive a migration from the actual payload rather than relabeling it.

## Deferred Cleanup

- Convert large WAV runtime files only after provenance is resolved and
  source-quality originals have an agreed archival home; verify the chosen
  format through Pygame and the frozen artifact.
- Consider Git LFS for large binary history in a separately coordinated task.
  Do not rewrite shared history as routine stabilization.
- Expand Ruff and strict mypy coverage package by package. The current legacy
  backlog is not a reason to disable useful rules globally.
- Audit transitional package re-exports, publish replacement imports and a
  deprecation window, then remove them only in a planned breaking release.
- Perform the foundational combat refactor after design approval: introduce
  typed combat context/result models and ordered modifier pipelines for large
  damage and status-resolution methods.
- Commit significant manual playtest time after the planned gameplay refactors
  stabilize; the current playtest queue remains intentionally deferred.
