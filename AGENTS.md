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
