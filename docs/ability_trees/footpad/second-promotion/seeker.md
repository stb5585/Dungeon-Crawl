# Seeker Ability Tree Implementation Reference

Status: `Finished`

Tier: terminal. The tree contains 28 development nodes costing 30 points
across four seven-node disciplines. [Runtime diagram](seeker.svg). The 20
terminal-tier points buy 66.7% of its development cost.

## Implemented Decision

- `Wayfinding` turns Cartography into route economy through Early Bearings,
  Wayfinding, Surveyor's Step, Teleport, Efficient Passage, and Enter Wall.
- `Safe Passage` combines Volitation, the new defensive Safe Passage cast,
  Sanctuary, Resist All, and mapped-floor defensive mastery.
- `Revelation` carries Inspect forward and adds Deductive Strike plus Foregone
  Conclusion, with talents improving evidence pace and committed debuffs.
- `Judgment` develops Third Eye, Weaken Mind, Triple Strike, and True Piercing
  Strike while improving Revelation accuracy, miss conservation, and exposed
  Defense pressure.

No additional meter or persistent record was introduced. Surveyor's Step and
Safe Passage consume current mapped-floor information; Deductive Strike and
Foregone Conclusion consume the existing Case Journal and Revelation states.
Hidden Cache remains an awakened-ring reward rather than a tree loot loop.

## Validation Contract

- Rows follow ungated, 65, 70, 75, 80, 85, and 90 without scrolling.
- Every talent changes an existing runtime calculation or one of the four new
  active techniques; none is a generic rating placeholder.
- Focused coverage verifies the 28-node/30-point budget, mapping thresholds and
  discounts, Inspect progress, Revelation accuracy/refunds/debuffs, and the
  new active techniques.
- Preserve movement failure handling, combat cleanup, Case rank concealment,
  and current-save defaults.
