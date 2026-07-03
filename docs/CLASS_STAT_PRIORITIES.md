# Class Stat Priorities

This is a gameplay-facing guide to what each core stat does and which stats
each class cares about most. It is based on the current class definitions in
`src/core/classes/` and shared stat formulas in `src/core/character.py` and
`src/core/player.py`.

Registry check: `src/core/classes/registry.py` currently exposes 48 playable
classes through the promotion tree, including the Pathfinder branches
`Diviner`, `Shaman`, and `Ranger`.

## Global Stat Impact

- `STR`: physical identity. Improves attack growth, strength contests, some
  weapon skills, and shield-block mitigation against weaker attackers.
- `INT`: spell offense. Improves mana growth, magic modifier, spell/status
  contests, and many elemental/status effects.
- `WIS`: healing and resistance. Improves healing, magic defense, luck/save
  checks, and many defensive contests.
- `CON`: durability. Improves HP growth, defense growth, poison/bleed
  resistance, and general survival.
- `CHA`: fortune, gold, and companion/contract utility. Contributes to luck
  checks with WIS, gold outcomes, secondary magic defense, and several
  companion or contract-style mechanics.
- `DEX`: speed, crit, and evasion. Improves speed, critical chance, flee odds,
  parry, Evasive Guard scaling, and rogue-style defense.

## Class Priorities

Stats are ordered from most important to least important for typical play.
Ties mean the class wants both stats about equally.

| Class | Stat Priority |
|---|---|
| Warrior | `STR/CON`, `DEX`, `WIS/CHA/INT` |
| Weapon Master | `STR`, `DEX`, `CON`, `WIS/CHA/INT` |
| Berserker | `STR`, `DEX`, `CON/CHA`, `WIS/INT` |
| Grandmaster of Arms | `DEX`, `STR/CON`, `WIS/CHA/INT` |
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
| Summoner | `CHA/INT/WIS`, `CON/DEX/STR` |
| Grand Summoner | `CHA`, `INT/WIS`, `CON/DEX/STR` |
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
