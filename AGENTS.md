# AGENTS

This file defines repo-specific instructions for Codex agents working in this project.

## Environment

- Always use the repo virtual environment for Python commands.
- Prefer `./.venv/bin/python -m pytest ...` over bare `pytest`.
- Prefer `./.venv/bin/python` for scripts, test runs, and one-off validation commands.
- Do not assume globally installed Python packages are available.

## Testing

- Run focused tests for the files or systems you changed before suggesting broader validation.
- When fixing gameplay rules, add or update a regression test when practical.
- If a test cannot be run, say so clearly and explain why.

## Quality Gates And Reliability

- Keep the Ruff gate source-wide: run `./.venv/bin/python -m ruff check src`.
  Do not suppress a correctness rule globally to absorb existing findings. A
  narrow, documented per-file exemption is acceptable only for intentional
  compatibility exports in package `__init__.py` files.
- When adding or changing annotations that may be inspected at runtime, ensure
  `typing.get_type_hints()` can resolve them. Prefer concrete imports or
  runtime-available protocols over unresolved forward references.
- Do not add broad `except Exception` handlers around combat, progression,
  persistence, or other gameplay rules. Catch only expected exception types;
  if a fallback is intentional, document it and cover it with a regression
  test. Never silently disable a gameplay mechanic.
- Preserve and expand strict mypy coverage over stable contracts. Do not remove
  an existing strict target or use a broad mypy suppression to make a target
  pass; fix the target or add a narrowly scoped, documented exception.
- Keep CI and distribution tooling reproducible. Update the committed
  constraints/lock inputs whenever a dependency or tool version changes, and
  validate the affected command with the project virtual environment.

## Editing

- Preserve existing project structure and code style unless the task specifically calls for a refactor.
- Avoid changing unrelated files while solving a focused bug or feature request.
- Do not revert user changes or untracked work unless explicitly asked.

## Python Style

- Follow the Google Python Style Guide unless a repository-specific rule below
  is more explicit.
- Place imports immediately after the module docstring. Separate them into
  standard-library, third-party, and local/application groups, with one blank
  line between groups. Sort imports within each group and do not use wildcard
  imports.
- Import one module per `import` statement. Use `from ... import ...` only when
  it keeps ownership clear, and use aliases only for established conventions or
  to resolve a real naming conflict.
- Remove unused imports. Imports in an export-only `__init__.py` are considered
  public API declarations and should be listed in `__all__` when appropriate.
- Leave exactly two blank lines between the import block and the first
  top-level definition, and two blank lines between top-level class or function
  definitions.
- End every text file with exactly one newline and no additional blank lines.
- Use four spaces for indentation, never tabs. Keep lines at or below the
  configured 100-character limit whenever practical.
- Use `snake_case` for functions, methods, and variables; `CapWords` for
  classes; and `UPPER_SNAKE_CASE` for constants.
- Add concise module, class, and public-function docstrings that describe
  behavior rather than restating the name. Follow Google-style `Args:`,
  `Returns:`, `Raises:`, and `Yields:` sections when those details need
  documentation.
- Prefer explicit exception types over bare `except`, keep `try` blocks narrow,
  and do not silently discard errors without a documented reason.
- Prefer comprehensions only when they remain readable; avoid mutable default
  arguments and unnecessary global state.

## Gameplay And Content Rules

- Treat map files, tile classes, quests, and item-routing rules as gameplay-critical systems.
- When changing progression or gating logic, verify both the data definition and the runtime behavior.
- Prefer small, explicit rule changes over broad behavioral rewrites.

## Foundational Gameplay Refactor

- Treat `docs/FOUNDATIONAL_REFACTOR_PLAN.md` as the active authority for
  ability identity, actions, targeting, timing, visibility, combat UI, and the
  bounded multi-enemy rollout. Update the relevant owner document in the same
  change when a slice changes one of those contracts.
- Do not add new uses of overloaded ability `type`/`subtype` semantics or
  legacy class-name serialization. New and migrated callers use immutable
  ability slugs and typed taxonomy/action models; compatibility adapters may
  exist only at documented migration boundaries.
- Keep canonical combat intents actor-relative and ID-based. Do not introduce
  player/enemy-named target scopes or frontend-only target legality rules.
- Preserve the seed-1337 characterization and acceptance thresholds when
  replacing contact or timing behavior. Structural refactors must not include
  incidental numeric balance tuning.
- Keep ordinary encounter generation singleton until the post-refactor Pilot
  3 gate passes. Any approved pair rollout remains capped at two hostiles and
  must stay behind its default-on runtime kill switch.
- Preserve the versioned-save boundary. Unmarked pre-foundation saves are
  intentionally rejected rather than guessed or partially migrated.

## Assets And Generated Content

- Avoid modifying generated or asset-heavy content unless the task requires it.
- If an asset or content directory is already dirty and unrelated, leave it alone.

## Communication

- Be explicit about assumptions when local context is incomplete.
- Include the exact command used for important validation in the final summary when relevant.
