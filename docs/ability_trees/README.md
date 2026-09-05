# Ability Tree Diagrams

These SVGs are generated directly from the runtime progression graphs.
The Mage SVG has manually authored connector routing and is preserved
when diagrams are regenerated; its nodes still track the runtime tree.
Run `./.venv/bin/python tools/generate_ability_tree_diagrams.py` after
changing any tree. The drift test fails when these references are stale.
Diagrams are grouped by base-class lineage and then promotion tier.
See [Ability Tree Status](ABILITY_TREE_STATUS.md) for completion state,
implementation order, and decision-block policy.

## Warrior lineage

### Base class

- [Warrior](warrior/base/warrior.svg) - [documentation](warrior/base/warrior.md)

### First promotions

- [Weapon Master](warrior/first-promotion/weapon-master.svg) - [documentation](warrior/first-promotion/weapon-master.md)
- [Paladin](warrior/first-promotion/paladin.svg) - [documentation](warrior/first-promotion/paladin.md)
- [Lancer](warrior/first-promotion/lancer.svg) - [documentation](warrior/first-promotion/lancer.md)
- [Sentinel](warrior/first-promotion/sentinel.svg) - [documentation](warrior/first-promotion/sentinel.md)

### Second promotions

- [Berserker](warrior/second-promotion/berserker.svg) - [documentation](warrior/second-promotion/berserker.md)
- [Grandmaster of Arms](warrior/second-promotion/grandmaster-of-arms.svg) - [documentation](warrior/second-promotion/grandmaster-of-arms.md)
- [Crusader](warrior/second-promotion/crusader.svg) - [documentation](warrior/second-promotion/crusader.md)
- [Dragoon](warrior/second-promotion/dragoon.svg) - [documentation](warrior/second-promotion/dragoon.md)
- [Stalwart Defender](warrior/second-promotion/stalwart-defender.svg) - [documentation](warrior/second-promotion/stalwart-defender.md)

## Mage lineage

### Base class

- [Mage](mage/base/mage.svg) - [documentation](mage/base/mage.md)

### First promotions

- [Sorcerer](mage/first-promotion/sorcerer.svg) - [documentation](mage/first-promotion/sorcerer.md)
- [Warlock](mage/first-promotion/warlock.svg) - [documentation](mage/first-promotion/warlock.md)
- [Spellblade](mage/first-promotion/spellblade.svg) - [documentation](mage/first-promotion/spellblade.md)
- [Conjurer](mage/first-promotion/conjurer.svg) - [documentation](mage/first-promotion/conjurer.md)

### Second promotions

- [Wizard](mage/second-promotion/wizard.svg) - [documentation](mage/second-promotion/wizard.md)
- [Shadowcaster](mage/second-promotion/shadowcaster.svg) - [documentation](mage/second-promotion/shadowcaster.md)
- [Demonologist](mage/second-promotion/demonologist.svg) - [documentation](mage/second-promotion/demonologist.md)
- [Knight Enchanter](mage/second-promotion/knight-enchanter.svg) - [documentation](mage/second-promotion/knight-enchanter.md)
- [Thaumaturgist](mage/second-promotion/thaumaturgist.svg) - [documentation](mage/second-promotion/thaumaturgist.md)

## Footpad lineage

### Base class

- [Footpad](footpad/base/footpad.svg) - [documentation](footpad/base/footpad.md)

### First promotions

- [Thief](footpad/first-promotion/thief.svg) - [documentation](footpad/first-promotion/thief.md)
- [Inquisitor](footpad/first-promotion/inquisitor.svg) - [documentation](footpad/first-promotion/inquisitor.md)
- [Assassin](footpad/first-promotion/assassin.svg) - [documentation](footpad/first-promotion/assassin.md)
- [Spell Stealer](footpad/first-promotion/spell-stealer.svg) - [documentation](footpad/first-promotion/spell-stealer.md)

### Second promotions

- [Rogue](footpad/second-promotion/rogue.svg) - [documentation](footpad/second-promotion/rogue.md)
- [Seeker](footpad/second-promotion/seeker.svg) - [documentation](footpad/second-promotion/seeker.md)
- [Ninja](footpad/second-promotion/ninja.svg) - [documentation](footpad/second-promotion/ninja.md)
- [Arcane Trickster](footpad/second-promotion/arcane-trickster.svg) - [documentation](footpad/second-promotion/arcane-trickster.md)

## Healer lineage

### Base class

- [Healer](healer/base/healer.svg) - [documentation](healer/base/healer.md)

### First promotions

- [Cleric](healer/first-promotion/cleric.svg) - [documentation](healer/first-promotion/cleric.md)
- [Monk](healer/first-promotion/monk.svg) - [documentation](healer/first-promotion/monk.md)
- [Priest](healer/first-promotion/priest.svg) - [documentation](healer/first-promotion/priest.md)
- [Bard](healer/first-promotion/bard.svg) - [documentation](healer/first-promotion/bard.md)

### Second promotions

- [Templar](healer/second-promotion/templar.svg) - [documentation](healer/second-promotion/templar.md)
- [Hierophant](healer/second-promotion/hierophant.svg) - [documentation](healer/second-promotion/hierophant.md)
- [Master Monk](healer/second-promotion/master-monk.svg) - [documentation](healer/second-promotion/master-monk.md)
- [Archbishop](healer/second-promotion/archbishop.svg) - [documentation](healer/second-promotion/archbishop.md)
- [Troubadour](healer/second-promotion/troubadour.svg) - [documentation](healer/second-promotion/troubadour.md)

## Pathfinder lineage

### Base class

- [Pathfinder](pathfinder/base/pathfinder.svg) - [documentation](pathfinder/base/pathfinder.md)

### First promotions

- [Druid](pathfinder/first-promotion/druid.svg) - [documentation](pathfinder/first-promotion/druid.md)
- [Diviner](pathfinder/first-promotion/diviner.svg) - [documentation](pathfinder/first-promotion/diviner.md)
- [Shaman](pathfinder/first-promotion/shaman.svg) - [documentation](pathfinder/first-promotion/shaman.md)
- [Ranger](pathfinder/first-promotion/ranger.svg) - [documentation](pathfinder/first-promotion/ranger.md)

### Second promotions

- [Lycan](pathfinder/second-promotion/lycan.svg) - [documentation](pathfinder/second-promotion/lycan.md)
- [Archdruid](pathfinder/second-promotion/archdruid.svg) - [documentation](pathfinder/second-promotion/archdruid.md)
- [Astromancer](pathfinder/second-promotion/astromancer.svg) - [documentation](pathfinder/second-promotion/astromancer.md)
- [Soulcatcher](pathfinder/second-promotion/soulcatcher.svg) - [documentation](pathfinder/second-promotion/soulcatcher.md)
- [Beast Master](pathfinder/second-promotion/beast-master.svg) - [documentation](pathfinder/second-promotion/beast-master.md)
