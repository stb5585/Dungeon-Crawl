# Enemy Render Mapping Report

This report was generated from `src/core/enemies.py` by instantiating no-argument enemy classes and assigning each discovered enemy display name to a broad render archetype.

Enemy renders are presentation assets only. Existing map sprites and combat positioning sprites remain separate systems.

The current atlas uses dark-fantasy broad-archetype artwork generated from individual source PNGs in `src/ui_pygame/assets/enemy_renders/`. Rebuild `enemy_render_atlas.png`, `enemy_render_atlas.json`, and `enemy_render_review_sheet.png` with `./.venv/bin/python tools/build_enemy_render_atlas.py` after replacing any source render, while keeping the archetype keys stable. Compact enemy tokens are generated from these same renders with `EnemyTokenManager` and crop overrides in `enemy_token_crop.json`; see `docs/ENEMY_VISUAL_SYSTEM.md` for layer usage.

| Enemy Name | Enemy Class | Enemy Category | Suggested Archetype |
| --- | --- | --- | --- |
| Aboleth | Aboleth | Slime | `ooze` |
| Alligator | Alligator | Animal | `bear` |
| Ankheg | Ankheg | Monster | `insect` |
| Antlion | Antlion | Animal | `insect` |
| Archvile | Archvile | Fiend | `greater_demon` |
| Bandit | Bandit | Humanoid | `bandit` |
| Bandit | Bandit2 | Humanoid | `bandit` |
| Barghest | Barghest | Fiend | `greater_demon` |
| Basilisk | Basilisk | Monster | `dragon` |
| Battle Toad | BattleToad | Animal | `boar` |
| Behemoth | Behemoth | Aberration | `boss` |
| Beholder | Beholder | Aberration | `boss` |
| Black Slime | BlackSlime | Slime | `ooze` |
| Brain Gorger | BrainGorger | Aberration | `greater_demon` |
| Brown Slime | BrownSlime | Slime | `ooze` |
| Cambion Acolyte | CambionAcolyte | Fiend | `demon` |
| Cerberus | Cerberus | Fiend | `greater_demon` |
| Chimera | Chimera | Monster | `boss` |
| Circe | Circe | Humanoid | `cultist` |
| Clannfear | Clannfear | Fiend | `demon` |
| Cockatrice | Cockatrice | Monster | `harpy` |
| Conjurer | Conjurer | Humanoid | `cultist` |
| Copycat | Copycat | Humanoid | `bandit` |
| Cyborg | Cyborg | Construct | `dark_knight` |
| Dark Knight | DarkKnight | Fiend | `dark_knight` |
| Direbear | Direbear | Animal | `bear` |
| Direbear | Direbear2 | Animal | `bear` |
| Direwolf | Direwolf | Animal | `dire_wolf` |
| Direwolf | Direwolf2 | Animal | `dire_wolf` |
| Disciple | Disciple | Humanoid | `cultist` |
| Displacer Beast | DisplacerBeast | Fey | `wolf` |
| Domingo | Domingo | Aberration | `boss` |
| Dragonkin | Dragonkin | Dragon | `dragon` |
| Drow Assassin | DrowAssassin | Humanoid | `bandit` |
| Earth Myrmidon | EarthMyrmidon | Elemental | `earth_elemental` |
| Electric Bat | ElectricBat | Animal | `bat` |
| Evil Crusader | EvilCrusader | Humanoid | `skeleton_warrior` |
| Fire Myrmidon | FireMyrmidon | Elemental | `fire_elemental` |
| Fuath | Fuath | Monster | `water_elemental` |
| Gargoyle | Gargoyle | Elemental | `gargoyle` |
| Ghoul | Ghoul | Undead | `zombie` |
| Giant Centipede | GiantCentipede | Animal | `insect` |
| Giant Hornet | GiantHornet | Animal | `insect` |
| Giant Owl | GiantOwl | Animal | `harpy` |
| Giant Rat | GiantRat | Animal | `giant_rat` |
| Giant Scorpion | GiantScorpion | Animal | `scorpion` |
| Giant Snake | GiantSnake | Animal | `wyrm` |
| Giant Spider | GiantSpider | Animal | `giant_spider` |
| Gnoll | Gnoll | Humanoid | `orc` |
| Goblin | Goblin | Humanoid | `goblin` |
| Goblin | Goblin2 | Humanoid | `goblin` |
| Golden Eagle | GoldenEagle | Animal | `harpy` |
| Golem | Golem | Construct | `earth_elemental` |
| Green Slime | GreenSlime | Slime | `slime` |
| Griffin | Griffin | Monster | `harpy` |
| Harlequin | Harlequin | Humanoid | `bandit` |
| Harpy | Harpy | Monster | `harpy` |
| Hydra | Hydra | Monster | `dragon` |
| Ice Myrmidon | IceMyrmidon | Elemental | `water_elemental` |
| Imp | Imp | Fiend | `demon` |
| Incubus | Incubus | Fiend | `greater_demon` |
| Invisible Stalker | InvisibleStalker | Elemental | `air_elemental` |
| Iron Golem | IronGolem | Construct | `earth_elemental` |
| Jester | Jester | Humanoid | `boss` |
| Lich | Lich | Undead | `lich` |
| Mad Waitress | NightHag2 | Fey | `wraith` |
| Merzhin | Merzhin | Humanoid | `boss` |
| Mind Flayer | MindFlayer | Aberration | `cultist` |
| Minotaur | Minotaur | Monster | `boss` |
| Myrmidon | Myrmidon | Elemental | `earth_elemental` |
| Naga | Naga | Monster | `wyrm` |
| Night Hag | NightHag | Fey | `wraith` |
| Nightmare | Nightmare | Fiend | `greater_demon` |
| Ogre | Ogre | Monster | `orc` |
| Orc | Orc | Humanoid | `orc` |
| Panther | Panther | Animal | `wolf` |
| Panther | Panther2 | Animal | `wolf` |
| Pit Viper | PitViper | Animal | `wyrm` |
| Pseudodragon | Pseudodragon | Dragon | `dragon` |
| Puppet | Puppet | Humanoid | `bandit` |
| Quasit | Quasit | Fiend | `demon` |
| Red Dragon | RedDragon | Dragon | `dragon` |
| Red Dragon | RedDragon2 | Dragon | `dragon` |
| Red Slime | RedSlime | Slime | `slime` |
| Sandworm | Sandworm | Monster | `wyrm` |
| Satyr | Satyr | Fey | `bandit` |
| Scarecrow | Scarecrow | Construct | `zombie` |
| Shadow Serpent | ShadowSerpent | Elemental | `shadow_elemental` |
| Skeleton | Skeleton | Undead | `skeleton` |
| Steel Predator | SteelPredator | Construct | `dark_knight` |
| Storm Myrmidon | StormMyrmidon | Elemental | `air_elemental` |
| Test | Test | Misc | `generic_enemy` |
| The Devil | Devil | Fiend | `greater_demon` |
| Treant | Treant | Fey | `earth_elemental` |
| Trickster | Trickster | Humanoid | `bandit` |
| Troll | Troll | Humanoid | `orc` |
| Twisted Dwarf | TwistedDwarf | Humanoid | `bandit` |
| Vampire | Vampire | Undead | `wraith` |
| Vampire Bat | VampireBat | Animal | `bat` |
| Warforged | Warforged | Construct | `dark_knight` |
| Warrior | Warrior | Humanoid | `bandit` |
| Water Myrmidon | WaterMyrmidon | Elemental | `water_elemental` |
| Wendigo | Wendigo | Fey | `wraith` |
| Wererat | Wererat | Monster | `giant_rat` |
| Werewolf | Werewolf | Monster | `dire_wolf` |
| Werewolf | Werewolf2 | Monster | `dire_wolf` |
| Wind Myrmidon | WindMyrmidon | Elemental | `air_elemental` |
| Wyrm | Wyrm | Dragon | `wyrm` |
| Wyvern | Wyvern | Dragon | `dragon` |
| Xorn | Xorn | Elemental | `earth_elemental` |
| Zombie | Zombie | Undead | `zombie` |
