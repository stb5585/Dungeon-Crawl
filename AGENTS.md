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

## Assets And Generated Content

- Avoid modifying generated or asset-heavy content unless the task requires it.
- If an asset or content directory is already dirty and unrelated, leave it alone.

## Communication

- Be explicit about assumptions when local context is incomplete.
- Include the exact command used for important validation in the final summary when relevant.
