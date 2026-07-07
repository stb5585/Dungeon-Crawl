# Equipment, Items, And Economy Design Gates

This document is the durable reference for equipment, item, and economy design
gates. It maps the roadmap section into implementation slices, runtime rules,
and validation targets. Completed work should move to `CHANGELOG.md`; this file
should keep active, deferred, or decision-gated direction.

## Status

Status: `Spec Map, Shop Polish V1 Shipped`

The first implementation slice shipped for the existing pygame shop purchase
and equip-now flow because it did not require new economy rules, new item state,
or save migration.

Save-heavy systems such as durability, identification, item modification, and
equipment active abilities remain deferred until their serializer, UI, economy,
and balance contracts are explicitly promoted.

## Shop Polish V1

Shop Polish V1 improves clarity around the existing pygame buy-then-equip path
without changing prices, stock, inventory, gold, or equip legality.

The shop should make clear:

- which equip actions are available for the purchased item;
- which slots will be replaced;
- what stat comparison applies to the target slot;
- when dual-wield requires two purchased items;
- that cancelling equip keeps the purchased item in inventory;
- that equip failures keep the item in inventory.

The compatibility baseline remains the existing `ShopManager`, `ShopScreen`,
item metadata helpers, `equipment_slots_for_item`, `Player.equip`, and
`Player.equip_diff`.

Shipped coverage includes pygame prompt copy for replacement slots, stat/no-stat
comparisons, dual-wield copy requirements, cancel behavior, preflight equip
failure, and rollback after partial equip failure. Curses prompt parity remains
a later polish pass unless promoted separately.

## Shop Stock Reveal Pacing

Shop stock reveal pacing remains a future per-character economy polish gate.
This covers slower or staged appearance of newly available shop items without
adding account-wide storage or cross-character stock sharing.

Future work must define:

- which shop families, rarity bands, player levels, or dungeon milestones
  control reveal timing;
- whether basic items remain visible while deeper stock is delayed;
- how unavailable stock is described in pygame and curses;
- how reveal pacing interacts with existing level, rarity, and secret-shop
  filters;
- tests that prove prices, item ownership, inventory, gold, and equip legality
  are unchanged unless explicitly promoted by the spec.

## Account-Wide Found/Sold Stock

Mordor: Depths of Dejenol-style shared shop stock remains a separate deferred
gate. In that model, basic stock may be visible by default while deeper stock
requires finding and selling items so future characters can buy them.

This is a profile/account-storage feature, not a shop-list timing tweak. Future
work must define profile storage, migration rules, cross-character ownership,
duplication prevention, item identity, shop UI, sell/buyback behavior, and
economy balance before implementation.

## Ultimate Helmet Acquisition

Ultimate helmet acquisition remains a future quest/reward gate using existing
special helmets unless a later spec explicitly adds new helmets.

The future spec must define:

- trigger source;
- armor-class eligibility;
- reward selection rules;
- UI text;
- save flags;
- duplicate prevention;
- tests for class restrictions and passive effects.

Existing special helmets and restrictions are the compatibility baseline:
`Ariadne's Diadem`, `Demon Cowl`, `Helm of Rostam`, and `Kabuto`.

## Durability And Repair

Durability, repair, broken-item state, shatter/loss rules, and durability costs
are deferred. This is a save/economy/combat/UI feature, not a local item tweak.

Future work must define:

- max and current durability fields;
- which actions reduce durability;
- repair sources and costs;
- broken-state behavior;
- shatter or permanent-loss rules;
- display in inventory, equipment, shop, loot, and combat UI;
- old-save defaults.

Any durability fields must round-trip for equipped items, inventory, special
inventory, and storage.

## Item Identification

Item identification is deferred. Future work must define:

- unidentified display names;
- intelligence-based unidentified drop chance;
- identify scrolls or shop services;
- inventory grouping;
- loot popup display;
- shop buy/sell behavior;
- save fields and legacy defaults.

Identification must not obscure quest-critical items, relics, class rings, or
other special inventory that the player needs to route progression.

## Usable Equipment Actives

Active abilities granted by equipped weapons, accessories, armor, helmets, and
offhands are deferred.

Future work must define:

- action-menu placement;
- combat-only versus exploration use;
- MP/HP/item/durability costs;
- cooldown or charge state;
- save fields;
- UI text and failure states.

Equipped items do not currently add active-use actions in this gate.

## Armor Mobility

Armor speed and mobility penalties remain deferred. Current weight and
encumbrance behavior is unchanged.

Future armor mobility work needs a separate balance pass covering armor subtype,
class exceptions, dungeon movement, combat turn effects, previews, and tests.

## Rarity Semantics

Future economy work should split rarity language into separate concepts:

- acquisition rarity for drops;
- shop availability;
- generated item quality;
- economic value.

The current rarity buckets and item values remain the compatibility baseline
until a later economy pass promotes a new model.

## Ordinary Drop-Rate Tuning

Ordinary item drop rates remain an evidence-gated economy question. Lowering
baseline drops may improve the value of `Steal`, luck passives, Bestiary hints,
and class-kit loot riders, but it can also starve early consumables and quest
routes.

Future tuning must use `tools/run_remaining_balance_baseline.py` and the
`ordinary_drops` section of `remaining_improvement_tuning_report()` before
changing drop rates, rarity nudges, gold values, or eligible item pools.

The tuning spec must preserve these boundaries:

- quest, special, boss-guaranteed, summon-gated, class-ring, and ultimate item
  sources are not ordinary-drop knobs;
- Steal and luck bonuses should feel useful without becoming mandatory;
- early consumable access should remain playable;
- Bestiary possible-drop hints must continue to describe possible outcomes
  without promising exact odds.

## Dungeon Refreshers

Random healing or mana refresher spots remain deferred until dungeon
interaction rules are promoted from the Dungeon, World, and Encounter gate.

They should not be implemented as ordinary item drops without a dungeon-state
and refresh-rule spec.

## Tome Special Effects

Tome special effects remain a future item-balance pass. The goal is to give
Tomes caster-offhand identity that can compete with Staves without replacing
the current Tome magic bonus.

Future work should define effect themes, trigger timing, class restrictions,
stacking rules, and combat log text.

## Elemental Armor And Item Modification

Elemental armor options and item modification remain deferred until
identification and durability rules exist.

Future modification work must define:

- source materials;
- allowed item types;
- element or resistance behavior;
- UI copy;
- save fields;
- rollback and failure behavior;
- tests for combat resistance, metadata, and serialization.

## P6-Adjacent Item Content

Additional P6-adjacent item content requires a one-page decision block per item
before implementation.

Each block must cover:

- catalog placement;
- rarity;
- shop, drop, crafting, or quest source;
- subtype;
- icon/render mapping;
- save compatibility;
- tests;
- whether the item is inert reagent-only or actively usable.

## Validation

Focused tests should cover:

- Shop Polish V1: purchase cancel, quantity purchase, equip-now cancel,
  main-hand/offhand/dual-wield equip, replacement inventory behavior,
  restricted equip failure, and stat-comparison display.
- Ultimate helmets: quest trigger, eligible reward by armor class, existing
  special helmet restrictions, save flag persistence, and duplicate prevention.
- Durability/repair: serializer defaults, durability loss triggers, repair
  pricing, broken behavior, shatter/loss rules, and UI display.
- Identification: unidentified loot display, identify services/items, inventory
  grouping, shop sell/buy behavior, old saves, and identified round trip.
- Tome/equipment actives/modification: action availability, costs/cooldowns,
  combat results, item state changes, and save/load.
- Economy content: rarity bucket placement, shop availability, drop eligibility,
  icon/render lookup, and no invalid restricted, ultimate, or generated drops.
