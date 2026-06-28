# Story And Endgame Design

Status: `Initial Spec, Vesperion Boss Concept, False-Final, Liminal Hub Shell, Six Lightweight Guardian Trials, Liminal Clue Review, Trial Consequences, Endgame Story Route, Reflection Combat Shell, Reflection Path Mirroring, Reflection Retry Tracking, Vesperion Guardian Counters, True-Final Victory, Ending Sequence, Tavern Epilogue, New Game Intro, Story Polish Epic, Class Ring Voluntas Tie-In, Story Polish Bundle V2, Liminal Trials V2, And Narrative Systems Bundle V3 Implemented`

This is the durable story and endgame design reference for **The Forsaken
Tenet** after the Six Relics arc. It records shipped story canon, route gates,
implementation interfaces, regression targets, and optional polish that should
stay aligned with the roadmap.

The current canon replaces the old Devil-centered final reveal with Vesperion,
the fallen Guardian of `Voluntas`.

## Story And Endgame Gate Ownership

This document owns the Story and Endgame Gates. The Vesperion/Voluntas route is
implemented and remains the compatibility baseline: future work should polish,
deepen, or stage the route rather than replace it. Presentation mechanics for
story cards and screen polish remain owned by
`PRESENTATION_ASSET_DESIGN_GATES.md`.

The New Game intro copy expansion has shipped through shared content data and
both frontends. It adds setting, premise, tone, and early stakes while avoiding
major endgame spoilers: do not reveal Vesperion, Voluntas, the busboy twist,
the Hooded Figure truth, or true-final route mechanics in the intro.

Class identity and Class Ring ties to Voluntas have a shipped V2: after
Voluntas is revealed, a visible Class Ring can receive an optional Liminal guide
affirmation, an archetype scene, a follow-up, per-class bridge prose, and
Reflection echoes. Deeper class-specific quests, bonuses, route gates, and ring
mechanics remain deferred.

## Deferred Story Gates

Each gate below needs a promoted story-content decision block before
implementation unless it is pure copy polish inside an already-approved surface.

### New Game Intro Story

Shipped. Future intro edits should remain in shared content data, preserve
pygame story-card presentation, preserve curses parity, and keep late-game
identities and true-final route mechanics hidden.

### Class Identity And Class Ring Tie-Ins

V2 has shipped as optional story-state-only route polish. The Hooded Figure can
affirm the player's visible Class Ring after Voluntas is revealed, records the
current class, dormant/awakened ring state, and class archetype, and lets the
Reflection echo that chosen class path. The affirmation must never gate
true-final access or change Class Ring power, combat balance, rewards, or
curses parity.

Narrative Systems Bundle V3 adds a one-time `Revisit Class Path` follow-up from
the Hooded Figure guide after affirmation. It remains story-state-only and uses
the recorded class/archetype/ring snapshot. The per-class Voluntas bridge adds
one more optional Hooded Figure beat after that follow-up, using the recorded
affirmed class snapshot rather than the current class or equipment. Deeper
per-class Voluntas quests, special rewards, and new Class Ring mechanics remain
deferred behind a future promoted spec.

### Guardian Trial Deepening

Hybrid V1 has shipped without new map rooms: Triangulus and Infinitas use
retry-safe Liminal combat echoes, Quadrata and Polaris remain lightweight
puzzle/interpretation trials, and Hexagonum and Luna remain choice/consequence
trials. Liminal Trials V2 has also shipped as story-state-only Guardian gate
vignettes: incomplete trials play deeper threshold and choice prose, completed
older trials can recall unseen deeper prose without re-awards, and the Hooded
Figure can review witnessed trial depths.

Larger bespoke rooms, mini-bosses, stronger trial consequences, new rewards,
and final-battle tuning remain deferred behind per-trial specs.

### Reflection/Psychopomp Polish

Profile-aware Reflection presentation has shipped for martial, mystic, and
hybrid paths without numeric tuning. V2 adds a one-time Voluntas answer choice,
retry copy, and victory echo without mechanical effect. V3 adds a one-time path
mirror that summarizes the recorded class, Guardian, and Reflection answers
before combat, plus a victory echo. Deeper self-copy mechanics, retry tuning,
and combat balance remain deferred. Every legitimate player build should remain
narratively valid; Reflection victory proves chosen selfhood rather than a
single correct build.

### Final Vesperion Polish

Story/log polish has shipped for phase pressure, Guardian counter messaging,
true-final victory. V3 adds a one-time true-final Vesperion argument and
tragedy reframing before combat, using the recorded Voluntas path as message
log context. Phase tuning, bespoke relic-counter interactions beyond
`Choose Fate` and phase pressure, audio/visual presentation, and final battle
balance require a promoted spec. Numeric combat changes should wait for
simulator or playtest evidence where relevant.

### Town Tragedy Route

Initial shared-content polish has shipped for Waitress, Joffrey, and busboy
adjacent beats. Broader rewrites must preserve the human grief of the tragedy
and the existing true-final reframing. Vesperion may pressure, observe, and
exploit choices around the tragedy, but the pain remains real and should not be
erased by later scenes.

### Hooded Figure Polish

The wounded Liminal guide, Witness of Voluntas reveal, post-Reflection angelic
confirmation, and unnamed witness farewell are the baseline. A personal angelic
name stays deferred.

### Legacy Devil Compatibility

The old Devil class and related tests stay valid until a dedicated
compatibility-retirement cleanup intentionally removes them. Narrative Systems
Bundle V3 audits this boundary only: legacy Devil class, event, ability data,
and tests remain present, while the implemented final route remains Vesperion.
Balor owns the old demonic visual direction.

## Story-Content Decision Block

Future story work should define the content beat, trigger, prerequisites, repeat
behavior, save flags, special-event keys, UI surface, spoiler boundaries,
affected NPCs/tiles/enemies, fallback behavior for old saves, regression tests,
and playtest checklist entry.

## Core Direction

- `Vesperion` is the former Guardian of `Voluntas`, the forgotten seventh
  principle of Choice and Free Will.
- Vesperion is associated with the Evening Star, radiant twilight, control,
  mercy-through-removal-of-choice, and hollowed free will.
- The busboy is Vesperion in disguise. He places himself near the hero to watch
  how grief, blame, love, and choice shape them, and he manipulates the
  Waitress/Joffrey tragedy as part of that observation.
- The Hooded Figure is not Vesperion. The Hooded Figure is a hidden guide or
  witness of Voluntas whose ominous behavior is a misdirect.
- The Acolyte is a former hero who once pursued the relics, failed, and now
  believes Vesperion is right that free will only creates suffering.
- The Acolyte supports Vesperion's argument narratively but does not join the
  final fight mechanically.

## Plot Structure

1. The hero gathers the Six Relics through the existing relic progression,
   believing they are weapons against the final evil.
2. The first confrontation with Vesperion should become a real fight that turns
   at a scripted threshold. Vesperion defeats or kills the hero and sends them
   to The Liminal Gap instead of the normal town resurrection flow.
3. The Liminal Gap reveals that the six relics are powerful safeguards, but
   incomplete without Voluntas.
4. The hero completes the Six Guardian trials, discovers the missing seventh
   principle, defeats the Reflection/Psychopomp through build affirmation, and
   returns to life.
5. The true final battle against Vesperion unlocks after Voluntas is revealed
   and the Reflection is defeated, then resolves the main storyline without
   ordinary combat rewards.

## Endgame Plot Chain

The locked route after the current Guardian trial shells is:

1. Six Guardian clues awaken.
2. The empty Seventh Seat opens.
3. Voluntas is revealed.
4. The Acolyte appears as a tragic mirror.
5. The Reflection/Psychopomp tests the chosen self.
6. The hero returns from The Liminal Gap.
7. The true final confrontation with Vesperion unlocks.
8. Defeating true-final Vesperion completes the main story and plays the
   Voluntas ending.

The six Guardian clues should carry these meanings:

- `Triangulus`: selfhood is chosen, not assigned.
- `Quadrata`: order without consent becomes tyranny.
- `Hexagonum`: instinct begins life, but does not define meaning.
- `Luna`: love without freedom becomes possession or obligation.
- `Polaris`: guidance must invite, not command.
- `Infinitas`: endurance only has meaning when stopping or continuing is a
  choice.

After all six clues are found, the guide directs the hero to the Seventh Seat.
The Seventh Seat is empty because Vesperion was once the Guardian of Voluntas
and erased the principle from history through the Hollowing. The reveal should
make the missing pattern explicit: every known principle becomes hollow without
Voluntas.

Voluntas is not recovered as a relic, item, throne, or external power. It is the
act of choosing itself, present wherever a soul can freely decide.

The Hooded Figure reveal should remain staged:

- Current implemented reveal: wounded Liminal guide.
- Seventh Seat reveal: surviving Witness of Voluntas who preserved the path.
- Post-Reflection reveal: angelic nature may be confirmed later, but this spec
  does not require a personal angelic name.

The Acolyte appears before the Reflection as a warning, not a boss. They are a
former failed hero who accepted Vesperion's mercy-through-control argument and
surrendered meaningful choice. Their testimony should suggest that giving up
choice felt peaceful at first, then empty. They do not fight, redeem themselves,
or join Vesperion mechanically in this route.

The Reflection/Psychopomp represents the hero's possible selves and paths not
taken. It tests affirmation of the player's chosen build, class, promotion,
relic journey, and Guardian answers. Reflection victory proves Voluntas through
affirmation rather than by choosing one correct build; every legitimate player
build must be narratively valid.

After Reflection victory, the Liminal exit opens. The guide sends the hero back
to the final threshold, the true-final re-entry unlocks, and ordinary
victory/death rewards remain bypassed for the Liminal transition.

In the true final, Vesperion should acknowledge the busboy disguise and reframe
the Waitress/Joffrey tragedy as evidence for his thesis that choice creates
suffering. The story must not erase the human grief of that tragedy: Vesperion
pressured and observed the choices around it, but the pain remains real. The
hero's answer is that removing choice also removes love, courage, redemption,
and growth. Victory over Vesperion completes the main story by preserving
Voluntas rather than claiming it as an object or external prize.

## The Liminal Gap

The Liminal Gap should be implemented as a hub-and-six-wings realm:

- Central sanctuary hub with a wounded/disfigured guide.
- Save access only through the guide in the hub and immediately before the
  Reflection/Psychopomp battle.
- Guide review of awakened Guardian clues and current Liminal progress.
- Six trial wings, one for each known Guardian principle.
- A sealed seventh path that opens only after the six trials reveal Voluntas.
- A final Reflection arena.

Failed trials or Reflection attempts return the player to the Liminal hub and
do not use the ordinary town death flow.

## Guardian Trials

- `Triangulus`: selfhood trial tied to class, promotion, and chosen identity.
- `Quadrata`: order trial with rule-bound movement, sequencing, or constraint
  logic.
- `Hexagonum`: nature trial centered on exploration and environmental
  interaction.
- `Luna`: love trial requiring protection, mercy, or sacrifice.
- `Polaris`: guidance trial using memory, direction, and clue interpretation.
- `Infinitas`: endurance trial built around loops, attrition, or endless
  struggle.

The first implementation should use mixed trial structure: two combat-heavy
trials, two exploration/puzzle trials, and two choice/sacrifice trials.

## Vesperion Boss Concept

Vesperion is distinct from the old Devil identity. The old Devil class may
remain for legacy saves/tests, and the old Devil visual direction belongs to
`Balor`, but the main plot routes to `Vesperion`.

Vesperion's palette:

- Evening Star light.
- Radiant twilight.
- Astral pressure.
- Silence and control.
- Reality edits rather than demonic flame.

Vesperion's fight has three phases:

1. **Mercy/control argument**: Vesperion frames choice as the cause of
   suffering.
2. **Voluntas pressure**: Vesperion forces the player to choose between
   consequence types.
3. **Evening Star desperation**: Vesperion tries to overwrite choice entirely.

## Choose Fate Redesign

Vesperion uses a distinct `Choose Fate` implementation instead of the legacy
Devil-coded `choose_fate.yaml`.

The Vesperion version evolves by phase and asks the player to choose between
types of suffering:

- Direct radiant damage.
- Resource loss.
- Control/status pressure.

The mechanic should never frame Vesperion as bored or randomly cruel. His thesis
is that if choice is sacred, the hero must bear the consequences of choosing.

## Relics In The Final Battle

The six relics should act as phase counters after their Guardian trials are
complete:

- `Triangulus` counters identity overwrite.
- `Quadrata` counters forced-order/control effects.
- `Hexagonum` counters environmental or attrition pressure.
- `Luna` counters sacrifice/mercy manipulation.
- `Polaris` counters misdirection or targeting confusion.
- `Infinitas` counters loop/endurance escalation.

These counters should make the Liminal Gap trials feel mechanically relevant
without turning the relics into passive stat sticks.

Current implementation uses two counter layers:

- `Choose Fate` options are linked to Guardian principles; if the matching
  Guardian trial is complete, direct/resource consequences are blunted and
  control/overwrite consequences can be resisted.
- Vesperion applies once-per-phase battlefield pressure during enemy turns.
  Phase 1 tests `Hexagonum` and `Luna`, phase 2 tests `Quadrata` and
  `Polaris`, and phase 3 tests `Triangulus` and `Infinitas`.

Broader relic-counter hooks for future bespoke Vesperion mechanics remain final
battle polish.

## Implementation State

Implemented in the initial slice:

- Added a distinct `Vesperion` enemy concept.
- Added Vesperion-specific `Choose Fate` YAML/effect wiring.
- Removed `Choose Fate` from Balor's kit and action stack.
- Routed the current pygame/core final boss entry points to `Vesperion`.
- Replaced the current final-boss event text with Vesperion-facing prose.

Implemented in the false-final stub slice:

- Added normalized `main_story` save state for Vesperion/Liminal progression.
- Added Vesperion's first-confrontation scripted transition at 70% HP, after
  three Vesperion turns, or on player death before the threshold.
- Added the first Liminal Gap recovery path and final-room re-entry blocker.

Implemented in the Liminal Gap hub shell slice:

- Added a real navigable Liminal Gap hub map.
- Routed the Vesperion false-final transition into the hub.
- Revealed the Hooded Figure as the wounded Liminal guide, while reserving
  their fuller angelic identity for later.
- Added guide-only save access, a no-exit blocker, and six named sealed
  Guardian gates for future trials.
- Added `main_story` state for guide reveal/save and Guardian trial completion.

Implemented in the Guardian trial story slice:

- Activated all six Guardian gates as lightweight non-combat trials:
  `Triangulus`, `Quadrata`, `Hexagonum`, `Luna`, `Polaris`, and `Infinitas`.
- Each trial records whether it was started, the player's selected answer,
  completion, and a Guardian-specific Voluntas clue placeholder.
- The Hooded Figure can now review awakened Guardian clues and summarize the
  recovered Voluntas pattern.
- Guardian trials now apply small one-time principle consequences, such as
  resource recovery, clearing misdirection, or setting a defensive order.
- The trials remain story-first shells, but their clues now feed the Seventh
  Seat route and their completion powers Vesperion counter mechanics.

Implemented in the endgame story route slice:

- Locked the post-trial route as six Guardian clues, empty Seventh Seat,
  Voluntas reveal, Acolyte tragic mirror, Reflection/Psychopomp, return from
  The Liminal Gap, and true Vesperion final.
- Added the Seventh Seat, Acolyte, and Reflection/Psychopomp story tiles to the
  Liminal Gap hub.
- Added all planned endgame route flags to `main_story` and save normalization.
- Implemented clue aggregation: six completed Guardian clues open the Seventh
  Seat reveal.
- Implemented Voluntas reveal, Hooded Figure Witness reveal, non-combat Acolyte
  tragic mirror scene, Reflection/Psychopomp route gating, true-final unlock,
  return from The Liminal Gap, and true-final Vesperion prelude.

Implemented in the Reflection and relic-counter slice:

- Added a `Reflection Psychopomp` Liminal enemy as a first combat shell for the
  chosen-self test.
- The Reflection now records a compact mirrored path profile from the player
  and shifts between martial, mystic, and hybrid action priorities.
- The Reflection tile now starts a no-normal-reward Liminal combat after the
  Voluntas reveal and Acolyte mirror scene.
- Reflection victory sets `reflection_defeated` and unlocks true-final re-entry
  when the other route gates are satisfied.
- Reflection defeat returns the player to the Liminal hub at 50% HP/MP without
  town resurrection, death costs, XP, loot, or boss-tile victory handling.
- Reflection attempts and failures are tracked in `main_story` for retry-safe
  presentation and future tuning.
- Vesperion `Choose Fate` options now map to Guardian counters, making completed
  Guardian trials mitigate or cancel matching consequences during the final
  battle.
- Vesperion now applies once-per-phase battlefield pressure answered by all six
  Guardian trials across the three true-final phases.

Implemented in the true-final completion slice:

- True-final Vesperion victory resolves outside ordinary combat reward flow:
  no XP, loot, quest completion, boss-tile victory handling, town resurrection,
  or death-cost routing is granted by the ending.
- True-final victory sets `vesperion_true_final_defeated` and
  `main_story_complete` in `main_story`.
- The final room now plays `Vesperion True Final Victory` and
  `The Forsaken Tenet Ending` after the true-final combat is won, followed by
  `The Thirsty Dog Epilogue` to acknowledge the Busboy/Vesperion absence while
  preserving the Waitress/Joffrey grief.
- After `main_story_complete`, re-entering the final room shows the ending
  reminder instead of reopening the final boss.

Optional polish is now tracked under the Deferred Story Gates above so future
work has one owner section for story-content decisions.

Implemented in the story polish epic:

- Moved Guardian trial structure into core definitions with explicit kind,
  prompt, choice, and special-event metadata.
- Deepened Triangulus and Infinitas into retry-safe Liminal combat trials using
  `GuardianTrialEcho`; victory completes the clue, while defeat returns to the
  Liminal hub without normal rewards or death flow.
- Added martial, mystic, and hybrid Reflection presentation copy without
  changing Reflection tuning.
- Added one-time post-Reflection Hooded Figure angelic confirmation.
- Polished Vesperion phase-pressure/final-victory story text without numeric
  combat changes.
- Polished Waitress/Joffrey/busboy-adjacent tragedy copy while preserving the
  true-final reframing.

Implemented in the Class Ring and Voluntas identity tie-in V1:

- Added optional `main_story` state for a Class Ring/Voluntas affirmation:
  `class_voluntas_affirmed`, `class_voluntas_affirmed_class`, and
  `class_voluntas_affirmed_ring_awakened`.
- Added a shared Class Ring identity summary helper for current class, visible
  ring state, awakened state, activation, mod, and description.
- Added a pygame Hooded Figure guide option, `Affirm Class Path`, that appears
  only after Voluntas is revealed and a Class Ring is visible.
- Added dormant and awakened Class Ring prose plus a one-time Reflection echo
  for affirmed class identity, without changing true-final gates, combat
  tuning, rewards, or Class Ring mechanics.

Implemented in Story Polish Bundle V2:

- Added archetype snapshots for Class Ring/Voluntas affirmation using martial,
  mystic, hybrid, companion, shadow, and wanderer story categories.
- Added a one-time Reflection Voluntas answer choice with Claim, Carry, and
  Choose Again answers, plus retry and victory echo prose.
- Added an optional unnamed Hooded Figure witness farewell after Reflection
  victory and before returning from the Liminal Gap.
- Polished Vesperion phase-pressure and Guardian-counter combat log text
  without changing phase thresholds, damage, statuses, AI, rewards, or gates.

Implemented in Liminal Trials V2:

- Added normalized `main_story` state for deeper Guardian trial vignettes:
  `guardian_trial_vignettes_seen` and `liminal_trial_v2_reviewed`.
- Added core helpers to record, count, and summarize seen Guardian trial
  vignettes.
- Extended existing pygame Guardian gate interactions with V2 threshold and
  choice-specific story beats for all six Guardians.
- Completed trials from older saves can recall an unseen deeper trial beat
  using the stored Guardian choice, or the first valid choice as prose fallback,
  without re-awarding consequences or changing route gates.
- The Hooded Figure guide can review witnessed trial depths once at least one
  deeper vignette has been seen.
- The slice remains story-state-only: no new rooms, enemies, rewards, permanent
  stat effects, combat tuning, or true-final prerequisites were added.

Implemented in Narrative Systems Bundle V3:

- Added normalized `main_story` state for one-time class follow-up, Reflection
  path mirror, and true-final Vesperion choice argument scenes.
- Added core helpers for showing/recording those one-time scenes and for
  summarizing the recorded Voluntas path.
- Added a pygame Hooded Figure guide option, `Revisit Class Path`, after class
  affirmation.
- Added one-time Reflection path mirror and victory echo presentation without
  changing Reflection mechanics, rewards, resources, or route gates.
- Added one-time true-final Vesperion choice argument and tragedy reframing
  before combat without changing Vesperion tuning, `Choose Fate`, rewards, or
  true-final prerequisites.
- Added a legacy Devil compatibility audit test/docs boundary without removing
  or renaming legacy Devil classes, assets, events, ability data, or tests.

Implemented in the Voluntas/Class-Identity Bridge slice:

- Added normalized `main_story` state for a one-time per-class Voluntas bridge:
  `class_voluntas_bridge_seen`.
- Added a pygame Hooded Figure guide option, `Bridge Class Identity`, after
  class affirmation and `Revisit Class Path`.
- Added one short bridge event for every fully playable Class Ring awakening
  class, plus a `Wanderer` fallback for old saves or unknown class names.
- The slice remains story-state-only: it uses the recorded affirmed class
  snapshot and does not change current class state, equipment, Class Ring
  mechanics, rewards, resources, combat tuning, or true-final prerequisites.

## Implementation Interfaces

The endgame route now uses these explicit route flags:

- `seventh_seat_revealed`
- `acolyte_liminal_seen`
- `returned_from_liminal_gap`
- `hooded_figure_witness_revealed`
- `hooded_figure_angelic_confirmed`
- `class_voluntas_affirmed`
- `class_voluntas_affirmed_class`
- `class_voluntas_affirmed_ring_awakened`
- `class_voluntas_affirmed_archetype`
- `reflection_voluntas_answer`
- `hooded_figure_witness_farewell_seen`
- `guardian_trial_vignettes_seen`
- `liminal_trial_v2_reviewed`
- `class_voluntas_followup_seen`
- `class_voluntas_bridge_seen`
- `reflection_path_mirror_seen`
- `vesperion_choice_argument_seen`
- `vesperion_true_final_defeated`
- `main_story_complete`

The existing `voluntas_revealed`, `reflection_defeated`, and
`true_final_unlocked` flags remain the core true-final gates. True-final unlock
should require all six Guardian trials complete, Voluntas revealed, and the
Reflection defeated. The existing final-room false-final blocker should remain
active until `true_final_unlocked=True`.

Implemented special-event keys include:

- `Voluntas Pattern Complete`
- `Seventh Seat Sealed`
- `Seventh Seat Reveal`
- `Acolyte Liminal Waiting`
- `Acolyte Liminal Mirror`
- `Reflection Locked`
- `Reflection Prelude`
- `Reflection Victory`
- `Reflection Defeat`
- `Reflection Prelude Martial`
- `Reflection Prelude Mystic`
- `Reflection Prelude Hybrid`
- `Reflection Victory Martial`
- `Reflection Victory Mystic`
- `Reflection Victory Hybrid`
- `Reflection Defeat Martial`
- `Reflection Defeat Mystic`
- `Reflection Defeat Hybrid`
- `Hooded Figure Witness Reveal`
- `Hooded Figure Angelic Confirmation`
- `Class Voluntas Affirmation`
- `Class Voluntas Dormant Ring`
- `Class Voluntas Awakened Ring`
- `Class Voluntas Archetype Martial`
- `Class Voluntas Archetype Mystic`
- `Class Voluntas Archetype Hybrid`
- `Class Voluntas Archetype Companion`
- `Class Voluntas Archetype Shadow`
- `Class Voluntas Archetype Wanderer`
- `Class Voluntas Followup`
- `Class Voluntas Followup Martial`
- `Class Voluntas Followup Mystic`
- `Class Voluntas Followup Hybrid`
- `Class Voluntas Followup Companion`
- `Class Voluntas Followup Shadow`
- `Class Voluntas Followup Wanderer`
- `Class Voluntas Bridge`
- `Class Voluntas Bridge <Class Name>`
- `Class Voluntas Bridge Wanderer`
- `Class Voluntas Reflection Echo`
- `Reflection Voluntas Choice Claim`
- `Reflection Voluntas Choice Carry`
- `Reflection Voluntas Choice Choose Again`
- `Reflection Voluntas Retry`
- `Reflection Voluntas Victory Echo`
- `Reflection Path Mirror`
- `Reflection Path Victory Echo`
- `Hooded Figure Witness Farewell`
- `{Guardian} Trial V2 Threshold`
- `{Guardian} Trial V2 {Choice}`
- `Liminal Trial V2 Review`
- `Return From Liminal Gap`
- `True Final Prelude`
- `Vesperion Choice Argument`
- `Vesperion Tragedy Reframing`
- `Vesperion True Final Victory`
- `The Forsaken Tenet Ending`
- `The Thirsty Dog Epilogue`
- `Liminal Clue Review`

## Regression Targets

- Balor never has `Choose Fate` in its skill list or action stack.
- Vesperion owns the Vesperion-specific `Choose Fate` ability.
- Vesperion's `Choose Fate` presents phase-specific options.
- Phase 1 can apply direct damage.
- Phase 2 can apply resource loss.
- Phase 3 can apply control/status pressure.
- Completed Guardian trials mitigate or cancel matching Vesperion `Choose Fate`
  consequences.
- Vesperion phase pressure fires once per phase and each Guardian trial counters
  its matching pressure.
- Existing legacy Devil tests remain valid until that compatibility class is
  intentionally retired.
- Guardian trials can be completed only after the Hooded Figure guide reveal.
- Completing each Guardian trial records the selected answer and a Voluntas clue
  without unlocking the true final by itself.
- The Hooded Figure can review awakened clues without completing missing trials.
- Guardian trial consequences apply once and completed gates do not re-award
  their benefits.
- Incomplete Guardian trials play V2 threshold and choice-specific vignette
  prose before ordinary completion, and combat-heavy trials do not mark V2
  prose seen on defeat.
- Completed Guardian trials with unseen V2 prose can recall the deeper trial
  without re-awarding consequences, completing new route gates, or changing the
  stored Guardian answer.
- The Hooded Figure can review witnessed trial depths only after at least one
  vignette is seen, and the review does not alter Voluntas, true-final flags,
  resources, XP, loot, or Guardian completion.
- Six completed Guardian clues trigger the Seventh Seat path.
- Voluntas reveal sets `voluntas_revealed` without unlocking the true final by
  itself.
- The Acolyte Liminal scene is non-combat and repeat-safe.
- Reflection victory sets `reflection_defeated` and `true_final_unlocked`
  without normal combat rewards.
- Reflection defeat returns the player to the Liminal hub without the ordinary
  town death flow.
- Reflection attempts and failures are tracked and round-trip through saves.
- Class Ring/Voluntas affirmation is optional, records class identity once, and
  never gates true-final access or changes Class Ring mechanics.
- Class Ring/Voluntas archetype scenes play from the recorded class snapshot
  and remain story-only.
- `Revisit Class Path` appears only after class affirmation, records once, and
  remains story-only.
- `Bridge Class Identity` appears only after class affirmation and `Revisit
  Class Path`, records once, uses the recorded affirmed class snapshot, and
  remains story-only.
- The Class Ring Reflection echo plays once on the first affirmed Reflection
  attempt and does not change HP, MP, XP, loot, or route flags.
- Reflection Voluntas answers record once, reject invalid old-save values, and
  never change Reflection stats, AI, rewards, or true-final gates.
- Reflection path mirror plays once before combat and does not alter Reflection
  stats, AI, HP, MP, XP, loot, rewards, failures, or true-final gates.
- Hooded Figure witness farewell appears only after Reflection victory, before
  returning from the Liminal Gap, and disappears after being seen.
- The Reflection records a martial, mystic, or hybrid path profile from the
  player and adjusts action priorities accordingly.
- Returning from The Liminal Gap places the player at the final threshold
  without normal death/victory rewards.
- The final-room blocker prevents Vesperion combat before true-final unlock and
  allows true-final combat after unlock.
- True-final Vesperion choice argument/tragedy reframing plays once before
  combat and does not change Vesperion mechanics, rewards, or unlock rules.
- True-final Vesperion victory completes the story without normal combat
  rewards or death/victory bookkeeping.
- True-final completion plays the tavern epilogue after the Voluntas ending.
- `vesperion_true_final_defeated` and `main_story_complete` round-trip through
  saves.
- Re-entering the final room after `main_story_complete` shows the ending
  reminder and does not restart combat.
- Legacy saves normalize any new main-story flags safely.
- Legacy Devil compatibility surfaces remain present until a dedicated
  compatibility-retirement cleanup intentionally removes them.
