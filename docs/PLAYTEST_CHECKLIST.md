# Playtest Documentation Index

Broad manual playtesting is active against the completed foundational baseline.
This file is an index, not a second implementation backlog.

- [`playtest/CURRENT.md`](playtest/CURRENT.md) owns the current post-refactor
  manual queue and its exit criteria.
- [`CLASS_KIT_EVIDENCE_NOTES.md`](CLASS_KIT_EVIDENCE_NOTES.md) stores class-kit
  evidence and the required capture format.
- [`history/playtest/SHIPPED_REGRESSIONS.md`](history/playtest/SHIPPED_REGRESSIONS.md)
  contains detailed historical and manual regression prompts for shipped systems.
- [`playtest/DEFERRED_SPEC.md`](playtest/DEFERRED_SPEC.md) lists features that
  need an approved design contract before implementation or expanded testing.
- [`FOUNDATIONAL_REFACTOR_PLAN.md`](FOUNDATIONAL_REFACTOR_PLAN.md) records the
  completed contract and baseline that the comprehensive queue now tests.

## Foundational Refactor Record

The following focused-validation rules applied while the foundational milestone
was in progress and remain useful for later targeted changes:

1. Run focused automated regressions for every changed rule and compatibility
   boundary.
2. Perform only the manual checks needed to verify that slice's UI, input,
   targeting, or timing behavior.
3. Record reproducible failures with build, character, route, actions, expected
   behavior, and observed behavior.
4. Do not collect balance or pacing evidence against behavior already scheduled
   to change.

## Current Broad Playtesting

[`playtest/CURRENT.md`](playtest/CURRENT.md) is rebased onto the completed
rules. Promote only the smallest decision-relevant subset of the shipped
regression prompts into that current queue.
