# Current P8 Playtest Queue

Use a current development save or a purpose-built fixture. Record the build,
class, race, level, gear, ring state, route, and exact UI/log behavior for every
failure. Automated regressions cover the narrow foundations below, but the
2026-09-02 class-kit audit found that the accepted Devotion, Prayer, Ki,
Foresight, form/control, Aspect, and Soul-harvest contracts are not complete.
Do not record a helper-only pass as proof that its production action path is
shipped; implementation gaps belong in the roadmap before balance tuning.

## Devotion

- [ ] Treat this as diagnostic evidence for the pending action-scope and payoff
  fixes, not as final V1 acceptance.
- [ ] Smoke-test Cleric Devotion gain, held-stack mitigation, hidden
  `Sanctuary Ward` at zero Devotion, and the first valid spend.
- [ ] Smoke-test Templar `Relic Aegis` and `Sacred Overchannel`, including
  insufficient-resource feedback.
- [ ] Smoke-test Hierophant `Consecrated Conduit` with staff and shield
  loadouts.

## High-Signal UI And Progression

- [ ] Confirm the longest Dwarf Virtue/Sin copy fits on the Race selection
  screen at the supported window size.
- [ ] Trigger invalid and non-fleeing Smoke Screen outcomes, then verify the
  next battle begins without smoke, hidden-enemy, or flee-transition residue.
- [ ] Promote while wearing mixed legal and illegal gear; verify legal gear
  stays equipped, illegal gear moves to inventory, and no default promoted gear
  is granted.
- [ ] Verify the staged relic route from `Uncertain Reports` through
  Triangulus report-back and creation of `The Holy Relics`.

## Class Rings And Kit Evidence

- [ ] Review Class Ring wording when absent, inventory-only, stored,
  equipped-dormant, and equipped-awakened.
- [ ] Record one martial-meter route in
  [`CLASS_KIT_EVIDENCE_NOTES.md`](../CLASS_KIT_EVIDENCE_NOTES.md).
- [ ] Record one caster/support-meter route.
- [ ] Record one persistent-progress route.
- [ ] Record two awakened-ring preservation cases with different failure
  modes.

## Postgame Tavern

- [ ] After `main_story_complete`, talk repeatedly to the Barkeep, Waitress,
  and Soldier in Pygame; confirm the new fallout copy appears
  naturally and does not alter quests, bounties, shops, or town services.

## Exit Criteria

P8 manual readiness is complete when every item above either passes or has a
reproducible issue recorded with enough context to promote one focused fix.
