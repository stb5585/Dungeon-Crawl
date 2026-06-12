# Item Art Classification Report

This report defines the first-pass item artwork plan before generating any new
assets. The goal is a collectible dark-fantasy item gallery, not recolored
archetype icons.

## Art Direction

- Style: dark fantasy, realistic, painterly, high detail, dramatic lighting.
- Format: individual PNG files under `src/ui_pygame/assets/item_art/`.
- Do not derive Tier 1 art from the current archetype atlas.
- Do not use recolor-only, tint-only, or copy-paste silhouette variants.
- Atlas generation is deferred until after individual artwork is reviewed.
- Tier 1 items should read as fantasy illustrations of specific objects.

## Review Sheet Items

The first quality-control sheet should include:

- Excalibur
- Mjolnir
- Necronomicon
- Pendant of Vision
- Golden Chalice
- Dragon Staff

Review criteria:

- Each item is visually distinct at inspection scale.
- No item is a recolor-only variant.
- No legendary item shares the same silhouette as a generic weapon.
- Detail quality matches the existing portrait and enemy artwork direction.
- The image reads as an object illustration, not a small UI icon.

## Generation Status

Tier 1 unique-art first pass: `Done`.

Completed and approved:

- Batch 1: Excalibur, Mjolnir, Necronomicon, Pendant of Vision, Golden Chalice,
  Dragon Staff.
- Batch 2: Gungnir, Codex of Eternity, Ultima Scroll, Svalinn, Medusa Shield,
  Ribbon Pendant.
- Batch 3: Jarnbjorn, Carnwennan, God's Hand, Indra's Fist, Skullcrusher,
  Princess Guard.
- Batch 4: Vulcan's Hammer, Flamberge, Earth Hammer, Magus, Compendium of the
  Ancients, Dragon Rouge, Rainbow Rod, Ultima Scepter, Scepter of Ifrit, Gaia's
  Branch, Zephyruswand, Death Scroll, Sanctuary Scroll.
- Batch 5: Genji Armor, Robes of Merlin, Tarnkappe, Mithril Coat, Dragon Hide,
  Maximilian, Klivanion, Ariadne's Diadem, Cohuleen Druith, Tarnhelm, Somen,
  Demon Cowl.
- Batch 6: Blacksmith's Hammer, Jester Token, Ticket Piece, Lucky Locket,
  Joker, Chalice Map, Joffrey's Letter, Empty Vial, Spring Water, Dragon's Tear,
  Chiryu Koma, Excaliper.
- Batch 7: Magic Pendant, Invisibility Pendant, Levitation Pendant, Gorgon
  Pendant, Garfunkel Pendant, Dharma Pendant, Elemental Amulet, Elemental Chain,
  Class Ring, Force Ring.

Generated for review:

- None.

Batch 5 corrections completed:

- Cohuleen Druith must be a cloth cap, not a metal helm.
- Klivanion must read as Byzantine lamellar armor, not samurai armor.
- Maximilian, Genji Armor, and Klivanion should be armor-only torso pieces
  without helmets, greaves, or boots.
- Somen should be only a face covering, not a complete helmet.

Current production standards:

- Final item artwork is stored as individual transparent PNGs.
- Final item artwork is resized to a maximum footprint of roughly `512x768`.
- Review sheets use checkerboard backgrounds so alpha quality is visible.
- New generations should use flat chroma-key backgrounds, followed by local
  alpha extraction, resizing, and visual review.

Next production focus:

- Tier 2 family art, starting with weapon and equipment families that still rely
  on broad archetype or compact icon presentation.
- Integration work can map these individual Tier 1 files into selected-item
  presentation contexts before atlas generation.

## Tier 1: Unique Art Items

These items should receive fully bespoke illustrations and individual prompts.

### Legendary Weapons

- `excalibur.png` - Legendary holy sword with ornate crossguard, ancient runes,
  silver blade, gold accents, and a glowing edge.
- `mjolnir.png` - Massive dwarven thunder hammer with engraved runes, cracked
  stone-metal head, lightning energy, and weathered handle.
- `gungnir.png` - Mythic spear with dark ash haft, celestial iron spearhead,
  oath-runes, and a cold divine glint.
- `jarnbjorn.png` - Ancient war axe with brutal Norse profile, blackened steel,
  bite marks, and battle-worn haft.
- `carnwennan.png` - Shadowy legendary dagger with blackened silver blade,
  moonlit edge, and subtle assassin motifs.
- `god_s_hand.png` - Sacred fist weapon or gauntlet with white-gold metal,
  relic-like engravings, and divine radiance.
- `indras_fist.png` - Storm-charged fist weapon with crackling electric arcs,
  brass and blue steel, and thunder-god ornamentation.
- `skullcrusher.png` - Named hammer with heavy skull motifs, dark iron,
  chipped bone inlays, and violent weight.
- `dragon_staff.png` - Dragon-shaped staff with carved serpentine body,
  ember-lit eye, clawed headpiece, and ancient lacquered wood.
- `princess_guard.png` - Elegant royal staff with polished ivory, gold filigree,
  protective gemwork, and ceremonial power.
- `vulcans_hammer.png` - Forgemaster hammer with glowing furnace cracks,
  black steel, and volcanic heat.
- `flamberge.png` - Flame-tongued greatsword with wavy blade, scorched
  crossguard, ember glow, and dramatic heat shimmer.
- `earth_hammer.png` - Earthen warhammer with stone-metal head, rootlike
  handle wrapping, and mineral veins.

### Legendary Tomes, Rods, And Scrolls

- `necronomicon.png` - Forbidden grimoire bound in cracked dark leather,
  bone fittings, occult clasps, and sickly green-black glow.
- `codex_of_eternity.png` - Cosmic tome bound in starlight, silver-blue metal,
  impossible pages, and timeworn celestial symbols.
- `magus.png` - Powerful mage tome with ornate arcane lock, deep violet cover,
  and focused spell energy.
- `compendium_of_the_ancients.png` - Heavy ancient book with layered bookmarks,
  worn brass corners, and scholarly relic detail.
- `dragon_rouge.png` - Red dragon grimoire with scale-like cover, claw marks,
  and smoldering runes.
- `rainbow_rod.png` - Prismatic rod with crystal facets, restrained spectral
  light, and refined magical craftsmanship.
- `ultima_scepter.png` - Supreme scepter with black-gold shaft, radiant crown
  crystal, and ominous final-magic glow.
- `scepter_of_ifrit.png` - Fire scepter with obsidian handle, ruby core, and
  restrained infernal flame.
- `gaias_branch.png` - Living branch focus with moss, gemstone knots, and deep
  earth magic.
- `zephyruswand.png` - Air-aspected wand with pale wood, wind-carved silver,
  and floating featherlike ornaments.
- `ultima_scroll.png` - Ancient ultimate scroll with black wax seals, gold
  glyphwork, and reality-bending magical light.
- `death_scroll.png` - Doom scroll with bone seal, ash-dark parchment, and
  necrotic calligraphy.
- `sanctuary_scroll.png` - Sacred defensive scroll with luminous vellum,
  protective sigils, and serene gold-white light.

### Unique Shields And Armor

- `svalinn.png` - Mythic shield with fire-resistant runes, scorched metal,
  layered Nordic construction, and ember reflection.
- `medusa_shield.png` - Petrifying shield with gorgon relief, green gemstone
  eyes, serpent motifs, and cold stone texture.
- `genji_armor.png` - Legendary samurai-inspired armor with lacquered plates,
  silk cords, and battle-worn elegance.
- `robes_of_merlin.png` - Ancient wizard robe with embroidered constellations,
  heavy folds, and quiet blue-gold magic.
- `tarnkappe.png` - Invisibility cloak with smoke-dark fabric, fading edges,
  and subtle distortion.
- `mithril_coat.png` - Fine mithril armor with bright interlocked rings,
  moonlit sheen, and elven craftsmanship.
- `dragon_hide.png` - Fire-aspected hide armor with red-black scales, claw
  stitching, and scorched leather.
- `maximilian.png` - Masterwork full plate with fluted steel, noble silhouette,
  and museum-quality polish.
- `klivanion.png` - Electric-aspected lamellar armor with bronze plates,
  storm-blue highlights, and eastern construction.

### Named Helmets

- `ariadnes_diadem.png` - Mythic diadem with labyrinth motif, delicate gold,
  and subtle threadlike magic.
- `cohuleen_druith.png` - Water-aspected enchanted cap with ancient
  Celtic detail and blue-green glow.
- `tarnhelm.png` - Legendary helm with darkened metal, concealment magic, and
  shadowed eye slit.
- `somen.png` - Distinct samurai face mask with lacquer, intimidating contours,
  and aged metal fittings.
- `demon_cowl.png` - Demonic hood with hornlike ridges, charred cloth, and
  deathly inner glow.

### Quest And Story Items

- `golden_chalice.png` - Sacred golden chalice with holy radiance, ancient
  engraving, and Grail-like importance.
- `blacksmiths_hammer.png` - Cacus summon hammer with forge grime, maker marks,
  worn handle, and hidden supernatural weight.
- `jester_token.png` - Trickster token with warped smile motif, carnival gold,
  and unsettling magical polish.
- `ticket_piece.png` - Torn lottery-ticket scrap with aged paper, strange
  numbers, and uncanny significance.
- `lucky_locket.png` - Sentimental gold locket with tiny portrait hint,
  protective warmth, and personal history.
- `joker.png` - Jester relic card/token with dangerous theatrical flourish and
  summoning energy.
- `chalice_map.png` - Worn map tied to the Chalice quest with faded ink,
  sacred annotations, and dungeon grime.
- `joffreys_letter.png` - Sealed letter with noble wax, creases, and readable
  quest-object identity without relying on text.
- `empty_vial.png` - Important empty vial with clear glass, cork, and spring
  quest readiness.
- `spring_water.png` - Filled vial of sacred water with luminous blue clarity.
- `dragon_tear.png` - Rare magical tear gem with crystalline droplet form and
  dragon-scale reflections.
- `chiryu_koma.png` - Dilong summon token with carved earthen piece, eastern
  ornamentation, and buried-dragon energy.
- `excaliper.png` - Failed Excalibur imitation with awkward warped blade,
  cheap shine, and deliberate counterfeit personality.

### Named Accessories

- `pendant_of_vision.png` - Silver pendant with embedded crystal eye, arcane
  inscriptions, and subtle magical glow.
- `ribbon_pendant.png` - Rare protective pendant with ribbonlike mineral loops,
  polished facets, and warding aura.
- `magic_pendant.png` - Anti-magic pendant with mirrored black gem, silver
  warding geometry, and spell-deflecting light.
- `invisibility_pendant.png` - Pendant with translucent smoky gem and bent-light
  distortion.
- `levitation_pendant.png` - Floating pendant with feather-light metalwork,
  airy crystal, and suspended chain.
- `gorgon_pendant.png` - Serpentine pendant with stone-green eye gem and gorgon
  scale texture.
- `garfunkel_pendant.png` - Silence-themed pendant with dark bell or soundwave
  motif, muted metal, and quiet menace.
- `dharma_pendant.png` - Death-ward pendant with wheel motif, aged gold, and
  solemn protective glow.
- `elemental_amulet.png` - High-tier all-element amulet with many colored gems
  harmonized into one relic.
- `elemental_chain.png` - All-element chain with linked elemental cores and
  shifting light.
- `class_ring.png` - Adaptive ring with segmented design, changeable inset, and
  class-neutral magical identity.
- `force_ring.png` - Heavy offensive ring with compressed kinetic energy and
  dense metalwork.

## Tier 2: Family Art Items

These items can share a family prompt and composition language, but each output
still needs distinct geometry, materials, ornamentation, and silhouette details.

### Sword Family

- Rapier, Jian, Talwar, Shamshir, Khopesh, Falchion.
- Family direction: one-handed blades, culturally distinct hilts, varied blade
  curvature, realistic metal, individual scabbard or guard motifs.

### Greatsword Family

- Bastard Sword, Claymore, Zweihander, Changdao, Katana, Executioner's Blade.
- Family direction: large two-handed blades, stronger silhouette variation,
  distinctive guards, grips, and blade profiles.

### Dagger Family

- Dirk, Baselard, Kris, Rondel, Kukri, Khanjar.
- Family direction: compact blades with strongly different profiles, ritual
  ornament, practical wear, and readable scale.

### Axe Family

- Mattock, Broadaxe, Double Axe, Parashu, Greataxe, Tabarzin.
- Family direction: varied axe heads and pole lengths, forged steel, wood grain,
  chips, bindings, and regional decoration.

### Hammer And Club Family

- Mace, War Hammer, Pernach, Morgenstern, Shishpar, Sledgehammer, Spike Maul,
  Great Maul, Streithammer.
- Family direction: impact weapons with different head construction, spikes,
  flanges, stone or iron mass, and worn grips.

### Polearm Family

- Framea, Partisan, Halberd, Naginata, Trident, Ranseur.
- Family direction: full-length weapon studies with unique spearheads, tassels,
  socket details, and cultural ornament.

### Staff Family

- Quarterstaff, Baston, Ironshod Staff, Serpent Staff, Holy Staff, Rune Staff,
  Mithrilshod Staff, Khatvanga.
- Family direction: distinct staff heads and materials; magical staves should
  read as individual ritual tools, not recolored poles.

### Fist Weapon Family

- Brass Knuckles, Cestus, Battle Gauntlet, Bagh Nahk.
- Family direction: hand-worn weapons with different materials, straps, claw
  geometry, and scale.

### Ninja Blade Family

- Tanto, Wakizashi, Ninjato.
- Family direction: Japanese blade family with distinct lengths, wrappings,
  fittings, and stealth-focused dark fantasy mood.

### Shield Family

- Buckler, Aspis, Targe, Glagwa, Kite Shield, Pavise.
- Family direction: different shield shapes, boss placement, surface wear,
  heraldic hints, and construction materials.

### Tome Family

- Book, Tome of Knowledge, Infernal Grimoire, Elemental Primer, Treatise of
  Balance, Vedas.
- Family direction: individual cover designs, clasps, bookmarks, page aging,
  and restrained magic cues.

### Rod Family

- Dowsing Rod, Scepter of Ifrit, Gaia's Branch, Zephyruswand, Rainbow Rod,
  Ultima Scepter.
- Family direction: hand-held magical focuses with distinct headpieces,
  gemstones, elemental material language, and dramatic lighting.

### Instrument Family

- Lute, Lyre.
- Family direction: detailed bardic instruments with carved wood, string detail,
  magical resonance, and worn performance surfaces.

### Ring Family

- Iron Ring, Power Ring, Barrier Ring, Steel Ring, Might Ring, Accuracy Ring,
  Evasion Ring, Titanium Ring.
- Family direction: rings can share framing, but each should vary gem, band
  shape, engraving, and implied stat function.

### Pendant And Necklace Family

- Ruby Locket, Silver Necklace, Antidote Pendant, Calming Pendant, Fire Chain,
  Ice Chain, Electric Chain, Water Chain, Earth Chain, Wind Chain, Sapphire
  Locket, Gold Necklace, Diamond Locket, Platinum Necklace.
- Family direction: jewelry object studies with clear gem/material differences,
  chain designs, and status or element motifs.

### Armor Families

- Cloth: Tunic, Cloth Cloak, Silver Cloak, Gold Cloak, Cloak of Enchantment,
  Wizard's Robe.
- Light: Padded Armor, Leather Armor, Cuirboulli, Studded Leather, Studded
  Cuirboulli.
- Medium: Hide Armor, Chain Shirt, Scale Mail, Breastplate, Half Plate, Kusari.
- Heavy: Ring Mail, Chain Mail, Splint Mail, Plate Mail, Full Plate.
- Natural: Animal Hide, Carapace, Stone Armor, Snake Scales, Demon Armor, Metal
  Plating, Dragon Scales, Cerberus Hide, Devil Skin.

### Helmet Families

- Cloth: Cloth Cap, Jaapi, Turban, Witch Hat, Enchanted Hood, Mitre Hat,
  Circlet.
- Light: Leather Cap, Pith Helmet, War Mask, Arming Cap, Katapu.
- Medium: Scale Helm, Chain Coif, Kulah Khud, Cervelliere, Visored Sallet,
  Tolga.
- Heavy: Iron Helm, Kettle Helm, Barbute, Great Helm, Full Plate Helm, Close
  Helm, Kabuto.

### Potion Families

- Health Potion, Great Health Potion, Super Health Potion, Master Health Potion.
- Mana Potion, Great Mana Potion, Super Mana Potion, Master Mana Potion.
- Elixir, Megalixir.
- HP Potion, MP Potion, Strength Potion, Intelligence Potion, Wisdom Potion,
  Constitution Potion, Charisma Potion, Dexterity Potion, Aard of Being.
- Family direction: bottle silhouettes, labels, liquid behavior, stoppers, and
  magical contents should differ by item and potency.

### Scroll Families

- Bless Scroll, Sleep Scroll, Fire Scroll, Ice Scroll, Electric Scroll, Water
  Scroll, Earth Scroll, Wind Scroll, Shadow Scroll, Holy Scroll, Cleanse Scroll,
  Boost Scroll, Shell Scroll, Silence Scroll, Dispel Scroll.
- Family direction: shared parchment language is acceptable, but seals, ribbon
  color, glyph style, burn/frost/water damage, and presentation should vary.

### Crafting And Quest Material Families

- Rat Tail, Mystery Meat, Leather, Feather, Snake Skin, Scrap Metal, Cursed
  Hops, Bird Fat, Elemental Mote, Power Core, Phylactery.
- Family direction: still-life object illustrations, not icons; props should
  be concrete and tactile.

### Relic Gem Family

- Triangulus, Quadrata, Hexagonum, Luna, Polaris, Infinitas.
- Family direction: sacred geometric gems with distinct shapes, internal light,
  and ancient relic presentation.

## Tier 3: Generic Or Deferred Items

These can keep archetype renders initially or receive lower-priority family art.

- Unequipped placeholders: Bare Hands, No Armor, No Helmet, No OffHand, No Ring,
  No Pendant.
- Simple keys: Key, Old Key, Master Key, Cryptic Key, Brass Key.
- Basic status cures: Antidote, Eye Drop, Echo Screen, Bandage, Phoenix Down,
  Remedy.
- Common low-tier gear where family art is enough at first: Iron Ring, Steel
  Ring, Leather Armor, Chain Mail, Cloth Cap, Iron Helm, Buckler, Book.
- Natural enemy/body weapons: Bite, Claw, Bear Claw, Stinger, Pincers, Demon
  Claw, Snake Fang, Alligator Tail, Lion Paw, Laser, Gaze, Dragon Claw, Dragon
  Tail, Nightmare Hoof, Elemental Blade, Tentacle, Invisible Blade, attacks,
  bites, claws, touches.
- Summon or enemy-only equipment can remain deferred unless it appears in player
  inspection flows: Giant's Club, Kobold Dagger, Scythe, Force Field.

## Historical First Generation Batch

This initial Tier 1 batch has been generated, reviewed, and approved:

1. Excalibur
2. Mjolnir
3. Necronomicon
4. Pendant of Vision
5. Golden Chalice
6. Dragon Staff

Completed outputs:

- `src/ui_pygame/assets/item_art/excalibur.png`
- `src/ui_pygame/assets/item_art/mjolnir.png`
- `src/ui_pygame/assets/item_art/necronomicon.png`
- `src/ui_pygame/assets/item_art/pendant_of_vision.png`
- `src/ui_pygame/assets/item_art/golden_chalice.png`
- `src/ui_pygame/assets/item_art/dragon_staff.png`
- `src/ui_pygame/assets/item_art/review_sheet_tier1_batch1.png`
