# Class Stat Priorities

This is a gameplay-facing guide to what each core stat does and which stats
each class cares about most. It is based on the current class definitions in
`src/core/classes/` and shared stat formulas in the `src/core/character/` and
the `src/core/player/` package.

Registry check: `src/core/classes/registry.py` currently exposes 49 playable
classes through the promotion tree, including the Pathfinder branches
`Diviner`, `Shaman`, and `Ranger`.

## Global Stat Impact

- `STR`: physical identity. Improves attack growth, strength contests, some
  weapon skills, and shield-block mitigation against weaker attackers.
- `INT`: spell offense and technical mastery. Improves mana growth, magic
  modifier, spell/status contests, many elemental/status effects, and Weapon
  Discipline insight chance for Weapon Master/Berserker/Grandmaster of Arms.
- `WIS`: healing and resistance. Improves healing, magic defense, luck/save
  checks, and many defensive contests.
- `CON`: durability. Improves HP growth, defense growth, poison/bleed
  resistance, and general survival.
- `CHA`: fortune, gold, and companion/contract utility. Contributes to luck
  checks with WIS, gold outcomes, secondary magic defense, and several
  companion or contract-style mechanics.
- `DEX`: speed, crit, and evasion. Improves speed, critical chance, flee odds,
  parry, Evasive Guard scaling, and rogue-style defense.

Future low-stat-benefit mechanics are gated in
`docs/COMBAT_BALANCE_DESIGN_GATES.md`. They should not invalidate this stat
priority guide unless a promoted combat-balance spec explicitly updates both
the mechanic and the affected class priorities.

## Class Priorities

The first two groups in this table are also structured progression data in
`src/core/progression_manifest.py`. Promotion nodes use current permanent
attributes (including class bonuses, training, consumables, and permanent
events; excluding equipment and temporary transformations):

- First promotion: primary `17` for one stat, `14` each for two, or `13` each
  for three or more; secondary `13` for one or `10` each for multiple.
- Second promotion: primary `24` for one stat, `20` each for two, or `18` each
  for three or more; secondary `19` for one or `15` each for multiple.

Authored promotion exceptions balance complete route cost and race
reachability rather than forcing identical gates. Warrior retains its documented
Weapon Master, Sentinel, and Paladin exceptions; Mage, Footpad, Pathfinder,
and all second-promotion targets also declare route-specific values in
`src/core/progression_manifest.py`.

These stat requirements complement the global level 30/60 promotion gates.
Every fourth global level grants one stored attribute point. Attribute points
cost one per permanent `+1`, have no cap, are spent from the Progression tab,
and cannot be respecced. Progression points cannot purchase attributes.

Stats are ordered from most important to least important for typical play.
Ties mean the class wants both stats about equally.

| Class | Stat Priority |
|---|---|
| Warrior | `STR/CON`, `DEX`, `WIS/CHA/INT` |
| Weapon Master | `STR`, `DEX/INT`, `CON`, `WIS/CHA` |
| Berserker | `STR`, `DEX/CON`, `INT/CHA`, `WIS` |
| Grandmaster of Arms | `DEX`, `STR/INT`, `CON`, `WIS/CHA` |
| Paladin | `CON/WIS`, `STR/CHA`, `DEX/INT` |
| Crusader | `STR/CON/WIS`, `CHA`, `DEX/INT` |
| Lancer | `STR/CON`, `DEX/CHA`, `WIS/INT` |
| Dragoon | `STR/CON/DEX`, `CHA`, `WIS/INT` |
| Sentinel | `CON`, `STR`, `DEX`, `WIS/CHA/INT` |
| Stalwart Defender | `CON`, `STR`, `DEX`, `WIS/CHA/INT` |
| Mage | `INT`, `WIS/CHA`, `CON/DEX/STR` |
| Sorcerer | `INT`, `WIS`, `CHA`, `CON/DEX/STR` |
| Wizard | `INT`, `WIS`, `DEX/CHA`, `CON/STR` |
| Warlock | `INT/CHA`, `WIS/CON`, `DEX/STR` |
| Shadowcaster | `INT`, `WIS`, `DEX/CON`, `CHA/STR` |
| Demonologist | `CHA/INT/WIS`, `CON`, `DEX/STR` |
| Spellblade | `STR/CON`, `INT/CHA`, `DEX/WIS` |
| Knight Enchanter | `STR/CON`, `INT/DEX/CHA`, `WIS` |
| Conjurer | `CHA/INT/WIS`, `CON/DEX` |
| Thaumaturgist | `CHA`, `INT/WIS`, `CON/DEX` |
| Footpad | `DEX/CHA`, `CON`, `INT/WIS/STR` |
| Thief | `DEX/CHA`, `CON/INT`, `WIS/STR` |
| Rogue | `DEX`, `CHA`, `CON/INT`, `WIS/STR` |
| Inquisitor | `STR/CON`, `DEX/CHA`, `WIS/INT` |
| Seeker | `STR/CON`, `DEX/CHA/INT`, `WIS` |
| Assassin | `DEX`, `CHA`, `WIS`, `CON/INT/STR` |
| Ninja | `DEX`, `CHA/WIS`, `CON/INT/STR` |
| Spell Stealer | `INT/DEX`, `WIS/CHA`, `CON/STR` |
| Arcane Trickster | `INT`, `DEX`, `WIS/CHA`, `CON/STR` |
| Healer | `WIS`, `INT/CON/CHA`, `DEX/STR` |
| Cleric | `WIS/CON`, `STR/CHA`, `DEX/INT` |
| Templar | `STR/CON`, `WIS/DEX/CHA`, `INT` |
| Hierophant | `WIS/INT`, `CON/CHA`, `STR/DEX` |
| Monk | `STR`, `WIS/CON/DEX/CHA`, `INT` |
| Master Monk | `STR/CON`, `WIS/DEX/CHA`, `INT` |
| Priest | `WIS`, `INT`, `CHA`, `CON/DEX/STR` |
| Archbishop | `WIS/INT`, `CHA`, `CON/DEX/STR` |
| Bard | balanced, slight lean `CHA/WIS/INT/DEX`, then `CON/STR` |
| Troubadour | `DEX`, then balanced `CHA/WIS/INT/CON/STR` |
| Pathfinder | balanced utility: `DEX/WIS/INT/CON/CHA`, `STR` last |
| Druid | balanced; no true dump stat |
| Lycan | `CON/DEX`, `STR/WIS/CHA`, `INT` |
| Archdruid | `INT`, `WIS`, `CON/DEX`, `CHA/STR` |
| Diviner | `INT/WIS`, `CON/CHA`, `DEX/STR` |
| Astromancer | `INT`, `WIS`, `CON/CHA`, `DEX/STR` |
| Shaman | `DEX`, `STR/WIS/CON/CHA`, `INT` |
| Soulcatcher | `STR/DEX`, `WIS/CON/CHA`, `INT` |
| Ranger | `STR/DEX`, `CON/CHA`, `WIS/INT` |
| Beast Master | `STR/DEX/CHA`, `CON`, `WIS/INT` |

Weapon Discipline class bonuses now include Intelligence as technical mastery:
Weapon Master uses `+2 STR / +1 INT / +2 DEX`, and Grandmaster of Arms uses
`+2 STR / +1 INT / +2 DEX`. This keeps the branch martial while making INT a
visible promotion reward rather than only a hidden insight chance.
Weapon Master's Brutish Strength further rewards matching Weapon Discipline:
it increases only the bonus portion of critical damage by `5%` per rank.
Two-Handed Weapon Proficiency independently grants `+10%` accuracy and damage
while a two-handed weapon is used.
Grandmaster Perfect Form converts each equipped discipline rank into `+1%`
weapon damage and `+0.5%` hit chance. Adaptive Arsenal converts each rank into
`+0.5%` parry chance and `+1%` counterattack critical chance.

## Elemental Spell Secondary Effects

- Fire attack spells: secondary burn/DOT pressure.
- Ice attack spells: secondary bonus damage.
- Electric attack spells: secondary stun chance.
- Water attack spells: Water Jet/Aqualung/Tsunami can reduce Attack. Some
  special Water abilities, such as Maelstrom Vortex, have bespoke status
  effects.
- Wind attack spells: Gust/Hurricane/Tornado can reduce Speed.
  `Windswept` is a special ejection spell rather than the baseline Wind attack
  family effect.
- Earth attack spells: Tremor/Mudslide/Earthquake can knock targets Prone.
  `Sandstorm` is a named exception with Blind.
