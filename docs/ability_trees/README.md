# Ability Tree Diagrams

These SVGs are generated directly from the runtime progression graphs.
The Mage SVG has manually authored connector routing and is preserved
when diagrams are regenerated; its nodes still track the runtime tree.
Run `./.venv/bin/python tools/generate_ability_tree_diagrams.py` after
changing any tree. The drift test fails when these references are stale.
Diagrams are grouped by base-class lineage and then promotion tier.

## Warrior lineage

### Base class

- [Warrior](warrior/base/warrior.svg)

### First promotions

- [Weapon Master](warrior/first-promotion/weapon-master.svg)
- [Paladin](warrior/first-promotion/paladin.svg)
- [Lancer](warrior/first-promotion/lancer.svg)
- [Sentinel](warrior/first-promotion/sentinel.svg)

### Second promotions

- [Berserker](warrior/second-promotion/berserker.svg)
- [Grandmaster of Arms](warrior/second-promotion/grandmaster-of-arms.svg)
- [Crusader](warrior/second-promotion/crusader.svg)
- [Dragoon](warrior/second-promotion/dragoon.svg)
- [Stalwart Defender](warrior/second-promotion/stalwart-defender.svg)

## Mage lineage

### Base class

- [Mage](mage/base/mage.svg)

### First promotions

- [Sorcerer](mage/first-promotion/sorcerer.svg)
- [Warlock](mage/first-promotion/warlock.svg)
- [Spellblade](mage/first-promotion/spellblade.svg)
- [Conjurer](mage/first-promotion/conjurer.svg)

### Second promotions

- [Wizard](mage/second-promotion/wizard.svg)
- [Shadowcaster](mage/second-promotion/shadowcaster.svg)
- [Demonologist](mage/second-promotion/demonologist.svg)
- [Knight Enchanter](mage/second-promotion/knight-enchanter.svg)
- [Thaumaturgist](mage/second-promotion/thaumaturgist.svg)

## Footpad lineage

### Base class

- [Footpad](footpad/base/footpad.svg)

### First promotions

- [Thief](footpad/first-promotion/thief.svg)
- [Inquisitor](footpad/first-promotion/inquisitor.svg)
- [Assassin](footpad/first-promotion/assassin.svg)
- [Spell Stealer](footpad/first-promotion/spell-stealer.svg)

### Second promotions

- [Rogue](footpad/second-promotion/rogue.svg)
- [Seeker](footpad/second-promotion/seeker.svg)
- [Ninja](footpad/second-promotion/ninja.svg)
- [Arcane Trickster](footpad/second-promotion/arcane-trickster.svg)

## Healer lineage

### Base class

- [Healer](healer/base/healer.svg)

### First promotions

- [Cleric](healer/first-promotion/cleric.svg)
- [Monk](healer/first-promotion/monk.svg)
- [Priest](healer/first-promotion/priest.svg)
- [Bard](healer/first-promotion/bard.svg)

### Second promotions

- [Templar](healer/second-promotion/templar.svg)
- [Hierophant](healer/second-promotion/hierophant.svg)
- [Master Monk](healer/second-promotion/master-monk.svg)
- [Archbishop](healer/second-promotion/archbishop.svg)
- [Troubadour](healer/second-promotion/troubadour.svg)

## Pathfinder lineage

### Base class

- [Pathfinder](pathfinder/base/pathfinder.svg)

### First promotions

- [Druid](pathfinder/first-promotion/druid.svg)
- [Diviner](pathfinder/first-promotion/diviner.svg)
- [Shaman](pathfinder/first-promotion/shaman.svg)
- [Ranger](pathfinder/first-promotion/ranger.svg)

### Second promotions

- [Lycan](pathfinder/second-promotion/lycan.svg)
- [Archdruid](pathfinder/second-promotion/archdruid.svg)
- [Astromancer](pathfinder/second-promotion/astromancer.svg)
- [Soulcatcher](pathfinder/second-promotion/soulcatcher.svg)
- [Beast Master](pathfinder/second-promotion/beast-master.svg)
