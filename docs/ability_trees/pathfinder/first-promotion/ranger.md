# Ranger Ability Tree Implementation Reference

Status: `Finished`

Tier: first promotion. Breadth: 24 development nodes across `Hunt`,
`Companion Bond`, `Duelist / Ranged`, `Two-Handed Fighting`, and `Defense`, plus
the Beast Master promotion. [Current diagram](ranger.svg).

## Decision

Favored Enemy retains its stable ID as an ungated Hunt root. The two promotion
routes join at `Pack Tactics`: creature care reaches it through `Kindred
Instinct`, while quarry specialization crosses in from `Quarry's Bane`.
`Companion Bond` sits at level 55 beneath that join, and Beast Master requires
the shared capstone without requiring a full roster or awakened ring.

## Authored Paths

| Path | Nodes in order |
| --- | --- |
| Hunt | Favored Enemy; Wild Sense; Relentless Tracker; Quarry's Bane; Aggressive Pursuit; Apex Hunter |
| Companion Bond | Detect Animal; Creature Comforts; Kindred Instinct; Pack Tactics; Companion Bond |
| Duelist / Ranged | Duelist; Crossbow Training; Vision; Uncanny Volley; Quick Reload |
| Two-Handed Fighting | Two-Handed Weapon Proficiency; Quarry Cleave; True Strike; Braced Grip |
| Defense | Parry; Combo Breaker; Hunter's Snare; Companion Cover |

`Detect Animal`, `Creature Comforts`, `Duelist`, `Vision`, `Two-Handed Weapon
Proficiency`, `True Strike`, and `Parry` recognize prior ownership. Duelist may
use a Ranger-trained crossbow off hand; a two-handed main-hand weapon still
excludes the crossbow naturally through equipment rules.

Wild Sense reveals vitality immediately, combat ratings at 10 Tracking
Mastery, resistances at 20, and known techniques at 30. Uncanny Volley spends
one selected bolt per living enemy, suppresses repeated Napalm splash, and
deals 25% more damage to Slimes, Monsters, Undead, and Aberrations. Combo
Quarry Cleave is a committed two-handed strike that grows from 25% to 50%
bonus damage against the favored enemy type. Hunter's Snare applies a Speed
penalty whose strength and duration increase against the current quarry. Combo
Breaker reduces successive damage instances within one enemy action by 8%
each, capped at 32%, and resets between enemy actions.

## Boundaries And Acceptance

- Reuse the six-slot roster, one active companion, bond/evolution, quarry
  practice, and selected bolt state.
- Preserve one companion turn, inverse-scaled bond growth, and Tame validation.
- Use the Companion & Hunt tab, combat Tame surface, HUD, logs, and item text.
- Exclude a town stable, multi-companion combat, collection rewards, and new
  species balance tiers.
- Covered by focused regression tests: both Pack Tactics joins, the Beast
  Master gate, ungated Favored Enemy, Wild Sense disclosure, Uncanny Volley's
  one-bolt targeting and unnatural bonus, Combo Breaker reset/scaling, existing
  ammunition behavior, companion rules, and global manifest validation.
- Remaining evidence is balance-only: capture Trusted-rank companion pacing,
  ammo economy across multi-enemy encounters, and defensive stacking under
  representative multi-hit enemy actions.
