# Class-Kit Evidence Notes

Canonical ledger for class-kit UI/log readability, meter cadence, ring
preservation, action-economy pressure, and progression pacing evidence. Use this
file to turn `PLAYTEST_CHECKLIST.md` prompts into concrete decision fuel before
promoting any tuning, content, or expansion slice.

## Evidence Rules

- Do not invent subjective manual findings. If nobody played the route, the
  result remains `Pending Manual`.
- Automated evidence may record command results, tested behavior, and simulator
  payload presence. It can support regression confidence, but it does not prove
  a mechanic feels good in play.
- `Design Baseline` rows capture documented formulas or expected cadence. They
  are not manual passes.
- `Watch` or `Tuning Gate` notes must include build/class/race/enemy, level,
  gear/loadout, ring state, battle length, status/log notes, and simulator
  payload when available.
- Numeric tuning remains blocked until the issue is promoted through a separate
  one-page tuning spec.

## Current Evidence Summary

- Overall state: `Evidence Collection Started`.
- Automated regression evidence exists for class-kit shared status lines,
  representative combat-log messages, pygame log filtering/wrapping, class-ring
  readiness/status behavior, and simulator payload aggregation/export.
- A presentation-only all-track UI/log readability batch is active for compact
  status hints, class-kit log preservation, Thief/Rogue loot visibility, and
  Summoner bond eligibility/no-bond messaging.
- Manual readability, cadence, preservation feel, action-economy pressure, and
  pacing feel remain pending until focused playtest notes are recorded below.

## Seeded Objective Evidence

| Area | Track/class | Evidence source | Command or playtest route | Result band | Notes | Follow-up decision |
| --- | --- | --- | --- | --- | --- | --- |
| UI/log readability | Representative V1 class-kit surfaces | Automated regression | `./.venv/bin/python -m pytest tests/core/test_promotion_class_kits.py tests/ui_pygame/test_combat_view.py tests/core/test_class_ring_awakening.py` | `Pass` | 67 tests passed on 2026-06-28. Coverage includes shared status matrix surfaces, persistent/preservation status lines, representative class-kit messages, pygame class-kit log filtering, combat-log wrapping/cache behavior, and class-ring awakening/status coverage. | Keep as regression baseline; still requires manual readability inspection across real panels and logs. |
| Ring preservation | Representative awakened class-ring tracks | Automated regression | `./.venv/bin/python -m pytest tests/core/test_promotion_class_kits.py tests/core/test_class_ring_awakening.py` | `Pass` | Tests cover existing preservation/readiness paths such as Devotion/Prayer smoothing, Troubadour Encore preservation, and class-ring activation/status behavior. | Use manual preservation rows to judge whether smoothing feels mandatory or erases failure costs. |
| Analytics payloads | Combat simulator class-kit and action-economy reporting | Automated regression | `./.venv/bin/python -m pytest tests/core/test_combat_simulator.py tests/core/test_combat_simulator_advanced.py` | `Pass` | 25 tests passed on 2026-06-28. Coverage includes aggregate/export payload behavior and smoke coverage for `class_kit_events` and `action_economy_events`. | Use payloads as investigation support, not automatic tuning failures. |
| Progression pacing | Troubadour, Beast Master, Summoner/Grand Summoner, Seeker/Inquisitor, Lycan | Design baseline | `docs/CLASS_KIT_DESIGN_GATES.md` progression pacing tables | `Design Baseline` | Tables document expected formulas and watch gates: Troubadour clean completions, Beast Master bond milestones, Summoner bond milestones, Seeker Case Journal milestones, and Lycan stress-record gates. | Manual pacing rows must confirm actual combat counts, interruptions, ring state, and feel before any tuning spec. |
| UI/log readability | Thief level 13 Fortune/Misfortune and loot visibility | Manual playtest | Player-reported Thief route, level 13 | `Watch` | Fortune gain was visible, but spend/use eligibility was not obvious; Misfortune was not encountered clearly from ordinary misses; `Scavenger's Eye` felt too subtle because loot text did not make the class identity visible. | Improve compact meter eligibility/status hints and ordinary-loot visibility first; keep broader lower-impact ordinary-combat Fortune/Misfortune expansion behind a future design gate. |
| Progression pacing | Summoner level 5 Patagon bond | Manual playtest | Player-reported Summoner route, Patagon reached level 2 and gained bond | `Tuning Gate Candidate` | Patagon reached level 2 and bond gains were visible but rare; the level-2 eligibility gate was not memorable enough. Concrete route counts, enemy XP context, recall/death interruptions, and final bond value are still needed before changing numbers. | Add level-2 eligibility and no-bond outcome messaging now; promote numeric bond pacing only after route-count evidence is recorded. |

## Manual Evidence Queue

Use these rows for focused evidence collection. Replace `Pending Manual` only
after the route has been played or measured.

| Area | Track/class | Evidence source | Command or playtest route | Result band | Notes | Follow-up decision |
| --- | --- | --- | --- | --- | --- | --- |
| UI/log readability | Martial meter: Berserker, Dragoon, Stalwart Defender, Ninja, or Master Monk | Manual playtest | Inspect character/status panel during setup, active combat, payoff-ready state, and post-payoff cleanup. | `Pending Manual` | Record build/class/race/enemy, level, gear/loadout, ring state, battle length, meter value/cap, pending payoff or stance, duplicate/stale labels, and combat-log visibility. | Mark `Watch` if meter readiness or payoff state is unclear, duplicated, or hidden during ordinary play. |
| UI/log readability | Caster/support meter: Astromancer, Shadowcaster, Templar, Archbishop, Archdruid, or Soulcatcher | Manual playtest | Inspect status text before gain, at cap/readiness, after spend, and after cleanup. | `Pending Manual` | Record resource value/cap, pending payoff, preservation/readiness line, miss/negated payoff text, and whether the current panel has enough room. | Mark `Watch` if the player cannot tell when to spend or why a payoff failed. |
| UI/log readability | Persistent-progress track: Demonologist, Grand Summoner, Seeker, Troubadour, Lycan, or Beast Master | Manual playtest | Inspect persistent rank/value plus temporary combat state in status and any menu/exploration surface. | `Pending Manual` | Record rank/value, temporary meter/form/song/totem/companion state, ring state, menu availability, and failure text. | Mark `Watch` if persistent progress looks like a new reward gate, tuning promise, or stale combat state. |
| UI/menu readability | Character Menu mechanic tab triage | Manual review | Compare `Required`, `Not Needed`, and `Too General` rows in `CLASS_KIT_DESIGN_GATES.md` against pygame tab content. | `Pending Manual` | Record which tabs are bespoke, which are generic summaries, which combat-only meters rely on HUD/status/log/action surfaces, and whether the tab explains persistent progression, configuration, or roster detail better than other surfaces. | Promote bespoke tab work for required generic tabs first; keep combat-only meter clarity on HUD/status/log/action surfaces unless a future spec adds persistent progression, configuration, or roster/detail needs. |
| UI/log readability | Combat-log gain/spend/failure/preservation messages | Manual playtest | Trigger gain, cap, spend, miss or negated payoff, expiration/cleanup, and ring preservation. | `Pending Manual` | Record exact messages, frontend, wrapping behavior, filters, and whether important failure/immunity/preservation text stays visible. | Mark `Watch` if required class-kit messages are hidden as generic status noise or wrap into unreadable fragments. |
| UI/log readability | Menu/exploration surface: Demonologist, Seeker, Troubadour, Lycan, Beast Master, or Soulcatcher | Manual playtest | Inspect one class-kit menu, exploration, town, or command surface. | `Pending Manual` | Record availability, failure state, current progress, ring state, and whether text implies mechanics that do not exist. | Mark `Watch` if availability or failure state is unclear without external documentation. |
| Meter cadence | Martial meter | Manual playtest plus optional simulator payload | Run at least three ordinary eligible combats with one martial meter. | `Pending Manual` | Record payoff count, capped turns, rebuild/spend loops, action tradeoffs, battle length, and `class_kit_events` if available. | Mark `Watch` if payoff usually cannot occur within three combats, sits capped without pressure, or loops without meaningful tradeoff. |
| Meter cadence | Caster/support meter | Manual playtest plus optional simulator payload | Run at least three ordinary eligible combats with one caster/support meter. | `Pending Manual` | Record gain triggers, cap state, payoff timing, MP/risk/target costs, miss/negated payoff text, and `class_kit_events` if available. | Mark `Watch` if starvation, constant cap, or repeated low-cost payoff loops appear. |
| Meter cadence | Persistent-progress-backed meter | Manual playtest plus optional simulator payload | Run focused combats for one persistent-progress track. | `Pending Manual` | Record persistent progress, temporary meter state, payoff timing, interruptions, ring state, and simulator payload if available. | Mark `Watch` if persistent progress overwhelms ordinary action decisions or fails to produce visible payoff. |
| Ring preservation | Awakened ring track A | Manual playtest | Trigger a miss, immunity, negated payoff, or target-loss case with ring ready. | `Pending Manual` | Record class, ring state, preserved resource, failure cost, same-turn follow-up, battle length, and log text. | Mark `Watch` if preservation feels mandatory or routinely erases failure costs. |
| Ring preservation | Awakened ring track B | Manual playtest | Repeat preservation test on a second track with a different failure mode. | `Pending Manual` | Record class, ring state, preserved resource, failure cost, same-turn follow-up, battle length, and log text. | Mark `Tuning Gate` only if preservation creates a repeatable same-turn or every-turn payoff loop across evidence sources. |
| Action economy | Totems, songs, summons/companions, divine support, or route/economy codas | Manual playtest plus simulator payload | Exercise one high-action-economy loop for representative encounters. | `Pending Manual` | Record player direct actions, bonus/autonomous outputs, passive damage/healing, battle length, defend/wait turns, and `action_economy_events`. | Mark `Watch` if bonus output regularly exceeds direct player impact or creates low-interaction wins. |
| Progression pacing | Troubadour advanced song mastery | Manual playtest | Master one advanced song through clean completions. | `Pending Manual` | Record song, performance count, combat or exploration route, interruptions, ring state, clean finishes, composition XP, and cadence feel. | Mark `Watch` if clean completions do not approach documented mastery cadence or feel overly brittle. |
| Progression pacing | Beast Master companion to `Trusted` | Manual playtest | Raise one active companion to at least bond 25. | `Pending Manual` | Record companion name/species/nickname, combat count, actions, victories, Favored Enemy state/log trigger, ring state, replacement/tame interruptions, release confirmations, and cadence feel. | Mark `Watch` if `Trusted` is not near 5-6 ordinary active wins, if high-bond growth feels automatic, if naming/release UI interrupts control flow, or if command output dominates direct turns. |
| Progression pacing | Summoner or Grand Summoner bond to `50` | Manual playtest | Raise one summon bond to at least 50 without switching summons. | `Pending Manual` | Record summon name, combat count, summon action count, victories, recall/death interruptions, ring state, and cadence feel. | Mark `Watch` if focused bond progress misses expected cadence or switching pressure feels unclear. |
| Progression pacing | Seeker or Inquisitor `Known Tells` | Manual playtest | Raise one Case Journal enemy type to at least 25. | `Pending Manual` | Record enemy type, combat count, Inspect/Exploit/telegraph evidence, visible-detail state, ring state, spread across other enemy types, and cadence feel. | Mark `Watch` if focused evidence does not reach `Known Tells` near the documented route cadence. |
| Progression pacing | Lycan control gate | Manual playtest | Advance one control gate through the correct stress behavior. | `Pending Manual` | Record starting rank, required behavior, eligible opportunities, successful records, moon state, ring state, Dragon Essence state, failures, and cadence feel. | Mark `Watch` if a gate does not reasonably progress after 6-8 eligible opportunities or if ring/Dragon Essence appears to advance rank. |

## Evidence Capture Template

Copy this shape into a row note when a manual route produces `Watch` or
`Tuning Gate` evidence:

```text
Build/class/race:
Enemy or route:
Level:
Gear/loadout:
Ring state:
Battle length or opportunity count:
Actions taken:
Status text notes:
Combat-log notes:
Simulator payload, if available:
Result band:
Follow-up decision:
```
