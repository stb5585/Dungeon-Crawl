# Playtest Documentation Index

Broad manual playtesting is deferred until the foundational gameplay refactors
stabilize. This file is an index, not a second implementation backlog.

- [`playtest/CURRENT.md`](playtest/CURRENT.md) preserves the post-refactor manual
  queue and explains what focused validation is still appropriate during
  refactor work.
- [`CLASS_KIT_EVIDENCE_NOTES.md`](CLASS_KIT_EVIDENCE_NOTES.md) stores class-kit
  evidence and the required capture format.
- [`playtest/SHIPPED_REGRESSIONS.md`](playtest/SHIPPED_REGRESSIONS.md) contains
  detailed historical and manual regression prompts for shipped systems.
- [`playtest/DEFERRED_SPEC.md`](playtest/DEFERRED_SPEC.md) lists features that
  need an approved design contract before implementation or expanded testing.
- [`FOUNDATIONAL_REFACTOR_PLAN.md`](FOUNDATIONAL_REFACTOR_PLAN.md) defines the
  milestone that must stabilize before the comprehensive queue resumes.

## During Foundational Refactors

For each implementation slice:

1. Run focused automated regressions for every changed rule and compatibility
   boundary.
2. Perform only the manual checks needed to verify that slice's UI, input,
   targeting, or timing behavior.
3. Record reproducible failures with build, character, route, actions, expected
   behavior, and observed behavior.
4. Do not collect balance or pacing evidence against behavior already scheduled
   to change.

## Resuming Broad Playtesting

When the foundational milestone is complete, rebase
[`playtest/CURRENT.md`](playtest/CURRENT.md) against the new rules. Promote only
the smallest decision-relevant subset of the shipped regression prompts into
that current queue.
