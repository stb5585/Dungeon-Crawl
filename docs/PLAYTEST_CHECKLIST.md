# Playtest Checklist Index

The playtest material is grouped by decision value so the active queue stays
small without discarding historical regression coverage.

- [Current P8 playtest](playtest/CURRENT.md) contains the manual routes that
  can change the next implementation decision.
- [Shipped regressions](playtest/SHIPPED_REGRESSIONS.md) preserves the detailed
  system, content, frontend, save, asset, and audio checklist.
- [Deferred spec gates](playtest/DEFERRED_SPEC.md) lists concepts that need an
  owner-doc decision before implementation or playtest expansion.

Record class-kit findings in
[CLASS_KIT_EVIDENCE_NOTES.md](CLASS_KIT_EVIDENCE_NOTES.md). Completed automated
coverage belongs in tests and the changelog; this index should not become a
second implementation backlog.
