# P4e Class Kit Specs

This document records the completed P4e class-mechanics foundation and the
deferred one-page gates for deeper class-kit work. Balance validation lives in
`PLAYTEST_CHECKLIST.md`.

## Review Baseline

### Diviner/Astromancer Runes

Current shipped rune behavior:

- Rune signs: `Ember`, `Tide`, `Gale`, and `Stone`.
- Rune cap: `3` stored runes per sign.
- Rune source: natural-spell kills by `Diviner` or `Astromancer`.
- Base rune drop chance: `25%`.
- Astromancer active-sign kill bonus: `+25` percentage points when the kill
  matches the active constellation sign.
- Resistance scaling: target resistance lowers the chance multiplicatively;
  target weakness raises it multiplicatively.
- `Runic Boost`: spends one matching rune and empowers the selected spell with a
  `75%` fate floor.
- Awakened, equipped Astromancer Class Ring: raises active-sign `Runic Boost`
  from a `75%` floor to a `100%` floor.
- Progression storage: per-save `astromancer_state`; no account progression,
  rune items, permanent spell mutation, or gear rune modification.

### Shaman/Soulcatcher Nature Totems

Current shipped Totem behavior:

- Totem pulse chance: `35%` at end of player turn.
- Staff pulse bonus: `+15` percentage points.
- Totem pulse potency: `50%` of the selected spell output.
- Staff matching-cast bonus: `+20%` damage or healing when the player casts a
  matching nature spell while the matching Totem is active.
- Water Totem: `+20%` Magic Defense and `25%` hostile spell-damage absorption
  into healing.
- Communion unlocks are represented by learned spells, not separate save flags.
- Soul Drain is a Soulcatcher level-4 spell that deals nonlethal current-HP
  percentage damage.

### Ring-Hooked Legacy Effects

These effects are implemented and visible through existing runtime hooks:

- Stalwart Defender `Resolve` / `Guard Meter`.
- Grand Summoner future summon scaling.
- Soulcatcher harvest tracking and Soul Aspect scaling.
- Beast Master shared recovery.
- Class status text for the legacy class-kit hooks.

## Diviner/Astromancer Rune Scope

The current rune system remains per-save and spell-empowerment based. Future
work must not add rune gear modification, rune inventory items, account history,
meta-progression, or permanent spell alteration unless a new spec explicitly
changes this scope.

### Scope Boundaries

- Keep the four-sign model as shipped: `Ember`, `Tide`, `Gale`, and `Stone`.
- Keep rune generation tied to the currently supported natural-spell elements.
- Do not add additional spell-school aliases to the rune system in this slice.

### UI Acceptance

- Combat must continue to show the current sign and compact four-sign rune grid.
- Curses and pygame views may differ visually, but both must expose the same
  readable state.
- Richer constellation presentation is future polish unless promoted by a
  dedicated UI/readability pass.

### Implementation Requirements

If future rune work changes code, cover the final behavior with focused tests around:

- Rune cap and save/load normalization.
- Rune drop chance for resistance and weakness.
- `Runic Boost` rune consumption and Astromancer sign advancement.
- Awakened equipped ring floor behavior.

## Shaman/Soulcatcher Totem Scope

The current Totem system remains class-local and per-save through spellbook,
Totem, and Class Ring state. Communions are one-time unlocks represented by
learned spells, not new quest flags or account state.

### Communion Locations

Keep these locations locked for the current scope:

- Underground Spring: Water communion, unlocks `Tsunami`.
- Boulder: Earth communion, unlocks `Earthquake`.
- Fire Path: Fire communion, unlocks `Fireball`.
- Floor-3 strange-draft passage: Wind communion, unlocks `Tornado`.

### Soul Drain And Soul Totem

- Preserve `Soul Drain` as nonlethal current-HP percentage damage.
- `Soul Drain` must leave the target at at least `1` HP.
- Soul Totem may pulse `Soul Drain` only when Soul aspect is active and the
  spell is known.
- Soul Totem pulses use the same reduced Totem pulse potency as elemental
  pulses unless a later balance pass explicitly changes all pulse potency rules.

### Implementation Requirements

If future Totem work changes code, cover the final behavior with focused tests around:

- Communion class eligibility, repeat visits, and save/load spell persistence.
- Highest-unlocked matching spell selection for Totem pulses.
- Staff pulse chance and matching-cast amplification.
- Water Totem Magic Defense and spell absorption.
- Soul Drain nonlethal behavior and Soul Totem pulsing.

## Remaining Deep-Kit Specs

Major class-kit implementation remains deferred until the relevant one-page spec
below is promoted from deferred planning. Each spec must define triggers,
storage, UI text/surfaces, save migration needs, tests, and balance assumptions
before code work begins.

Narrative identity beats should tie class progression back to `Voluntas` as
chosen selfhood. Do not implement those beats until their quest/content spec
defines timing, text, flags, and whether the beat is optional or required.

### Demonologist Corruption And Bargain Presentation

- Trigger: deferred; likely Church Crypt or fiend-contract milestones.
- Storage: define whether corruption is derived from contracts, stored directly,
  or purely presentational.
- UI text/surfaces: Crypt dialogue, class status, contract menus, and any combat
  status lines.
- Save migration: required only if new persistent corruption/bargain state is
  added.
- Tests: contract state normalization, dialogue gating, and any combat modifiers.
- Balance assumptions: avoid weakening the existing contract loop unless the
  spec adds compensating power or narrative reward.

### Shadowcaster Overlap

- Trigger: deferred; likely Class Ring awakening, stolen-light narrative beats,
  or late-game shadow encounters.
- Storage: define whether overlap uses existing class-ring state or new
  shadow-specific state.
- UI text/surfaces: combat action descriptions, class status, and activation
  dialogue.
- Save migration: required if overlap adds persistent counters, marks, or
  unlocked states.
- Tests: overlap gating, combat effect boundaries, and no conflict with
  Spell Stealer/Arcane Trickster spell theft.
- Balance assumptions: keep Shadowcaster distinct from Demonologist contracts
  and Wizard affinity.

### Spellblade/Knight Enchanter

- Trigger: deferred; likely enchanted-weapon use, Church rite follow-up, or
  arcane duel milestones.
- Storage: define whether enchantment state lives on the character, equipment,
  Class Ring data, or temporary combat effects.
- UI text/surfaces: equipment previews, combat action text, class status, and
  promotion/rite dialogue.
- Save migration: required if any enchantment persists beyond combat.
- Tests: weapon/spell interaction, equipment replacement behavior, save/load,
  and combat-result reporting.
- Balance assumptions: support hybrid play without making pure weapon or pure
  spell paths obsolete.

### Summoner/Grand Summoner

- Trigger: deferred; likely summon use, Conduit Ritual follow-up, or sacrifice
  milestones.
- Storage: define summon scaling, sacrifice, and companion/summon state
  boundaries.
- UI text/surfaces: combat HUD, class status, summon action descriptions, and
  Church ritual text.
- Save migration: required for any new persistent summon or sacrifice counters.
- Tests: summon stat scaling, HP sacrifice interactions, save/load, and
  no-normal-reward trial behavior if used.
- Balance assumptions: preserve current Grand Summoner ring scaling until a new
  summon economy is specified.

### Druid/Lycan

- Trigger: deferred; likely moon-cycle milestones, nature rites, or wilderness
  content.
- Storage: define whether deeper Druid/Lycan state extends existing Moon Cycle
  and Frenzy Lock data or adds new nature-form state.
- UI text/surfaces: class status, combat HUD, transformation text, and Church or
  nature-site dialogue.
- Save migration: required if new persistent form, cycle, or rite data is added.
- Tests: moon phase transitions, Frenzy Lock, healing modifiers, and any new
  transformation effects.
- Balance assumptions: avoid stacking uncontrolled damage bonuses that make
  Frenzy Lock irrelevant.

### Ranger/Beast Master

- Trigger: deferred; likely companion bond milestones, Pack Trial follow-up, or
  beast encounter content.
- Storage: define companion identity, bond rank, recovery echo, and any shared
  defense/offense state.
- UI text/surfaces: combat HUD, class status, companion presentation, and Pack
  Trial text.
- Save migration: required if companion identity or bond rank persists.
- Tests: shared recovery, companion state restoration, healing echo routing, and
  combat presentation.
- Balance assumptions: keep Beast Master support useful without requiring a full
  multi-actor combat redesign.

### Deeper Shaman/Soulcatcher Expansion

- Trigger: deferred; likely all four communions, awakened Soulcatcher ring, or
  late-game spirit content.
- Storage: define whether expansion uses spellbook/Totem state, Class Ring
  harvest data, or new spirit progress.
- UI text/surfaces: Totem aspect menu, combat HUD, class status, and communion
  or spirit dialogue.
- Save migration: required only if expansion adds new persistent spirit state.
- Tests: Totem pulse rules, Soul Aspect scaling, communion gating, and save/load.
- Balance assumptions: preserve current elemental Totem and Soul Drain contracts
  unless the tuning spec explicitly changes them first.
