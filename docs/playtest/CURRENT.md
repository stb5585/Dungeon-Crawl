# Deferred Comprehensive Playtest Queue

Status: `Deferred Until Foundational Gameplay Refactors Stabilize`

The automated class-tree and critical class-kit closure passes are complete.
The manual routes below remain valuable, but broad evidence collection is
postponed because combat timing, targeting, multi-enemy scope, ability
organization, and the combat action interface may change.

During the refactor milestone, use focused manual validation only for the slice
being changed. Do not mark the comprehensive items below complete against an
intermediate ruleset.

## Post-Refactor Smoke Coverage

- Create and advance representative base, first-promotion, and
  second-promotion characters through the revised action and progression
  surfaces.
- Verify keyboard, mouse, and controller-supported action selection, target
  selection, cancellation, and unavailable-action feedback.
- Exercise singleton and every supported multi-enemy encounter size.
- Verify invisible, revealed, flying, defeated, transformed, and target-lost
  combatants.
- Verify ordinary, charged, delayed, forced, reaction, companion, summon, Totem,
  item, and flee actions under the revised timing model.
- Verify current-save round trips across every changed gameplay or UI state.

## Class Rings And Kit Evidence

- Review Class Ring wording when absent, inventory-only, stored,
  equipped-dormant, and equipped-awakened.
- Record one martial-meter route in
  [`CLASS_KIT_EVIDENCE_NOTES.md`](../CLASS_KIT_EVIDENCE_NOTES.md).
- Record one caster/support-meter route.
- Record one persistent-progress route.
- Record two awakened-ring preservation cases with different failure modes.
- Recheck meter cadence and action-economy findings after the action interface
  and combat timing are final.

## Progression And Interface

- Verify all five base lineages and representative promotion paths under the
  final progression contract.
- Verify staged spending, permanent closures, promotion previews, retained
  abilities, equipment routing, and current-save ownership.
- Confirm active, passive, reaction, and unavailable abilities appear only on
  their intended final surfaces.
- Confirm class resources remain readable at empty, building, ready, spent,
  preserved, and cleanup states.

## World And Story Regression

- Verify the staged relic route from `Uncertain Reports` through Triangulus
  report-back and creation of `The Holy Relics`.
- Verify normal death, special-route defeat, town return, and postgame town
  dialogue.
- Verify the Vesperion/Voluntas route, Liminal trials, Reflection, true-final
  completion, and ending continuity.

## Exit Criteria

The comprehensive readiness pass is complete when:

1. every item above passes or has a reproducible issue;
2. all promoted issues have focused regression coverage;
3. class-kit and combat evidence is recorded against the final ruleset; and
4. the roadmap identifies the next content, tuning, or release-readiness slice.
