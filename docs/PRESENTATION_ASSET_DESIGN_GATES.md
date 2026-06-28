# Presentation And Asset Design Gates

This document is the durable reference for presentation and asset work. It maps
the roadmap's Presentation and Asset Gates into implementation slices, asset
workflow rules, and follow-up gates. Completed work should move to
`CHANGELOG.md`; this file should keep only active, deferred, or decision-gated
presentation direction.

## Status

Status: `Spec Map, V1 Screen/Cue Implementation`

The first implementation slice prioritizes quick wins that do not require a new
art direction pass:

- Replace the plain Character Created popup with a visual character summary
  screen.
- Replace the New Game intro popup chain with reusable story-card pages.
- Extend the existing combat impact layer with richer cues for reflection,
  hard-control hits, and elemental weapon strikes.

Generated bitmap batches are allowed for later asset-heavy slices, but each
batch must have a review artifact before runtime integration.

## Screen Polish V1

Character creation should end with a presentation screen, not a plain text
popup. The screen shows the selected portrait, name, race, sex, class, HP, and
MP. It has a single clear continue action and accepts keyboard confirm or mouse
click. The screen is presentation-only and must not change character creation,
save fields, starting stats, inventory, or class/race selection behavior.

New Game intro text should use reusable story cards. Story cards show a title,
page counter, wrapped body text, and a clear continue action. They should accept
keyboard confirm or mouse click, and may allow Escape to skip the remaining
story sequence without cancelling character creation.

## Combat Status Art

Status-effect artwork remains opt-in. Missing effect PNGs continue to fall back
to readable initials or compact pills. New status assets belong under
`src/ui_pygame/assets/effects/` and must map through the existing status icon
helpers rather than through one-off UI logic.

Adding status artwork must not change status mechanics, duration, stacking,
priority, save data, or combat result text.

## Ability Visual Batch V1

Combat cues should use the existing `CombatView` impact-effect layer. V1 covers:

- Reflection and Magic Reflect: shield/ripple style flashes on confirmed
  reflected damage.
- Stun and Prone: hard-control hit accents when the confirmed result text
  applies those states with damage.
- Elemental strikes: elemental color rings layered over weapon-hit slashes when
  non-spell damage carries a recognized element.

Effects trigger only after confirmed relevant outcomes. Misses, fully resisted
actions, and non-damaging actions must not play hit/spell particle effects.

## Jump And Charge Visuals

Full Jump and Charge wind-up/impact animation remains deferred until enemy
sprite stance adjustments are planned. Future work may add lightweight hooks for
pre-action wind-up and landing/impact cues, but it must not replace enemy
sprites or require alternate enemy stance art in this slice.

## Warp Point Art Pass

Warp Point artistic renderings are a generated-bitmap batch. Targets are:

- active Warp Point;
- inactive or spent Warp Point;
- optional charged shimmer overlay.

The implementation should prefer transparent PNGs or dungeon special-tile
manifest entries and preserve current fallback behavior. Runtime logic should
continue to render a readable Warp Point when an approved asset is absent.

## Town, NPC, And Venue Art Pass

Town/NPC/Venue renderings are batch-gated until art direction, target list,
dimensions, and review workflow are approved. Candidate targets:

- Sergeant/Barracks;
- inn patrons;
- shop purveyors;
- Church priest;
- Old Warehouse guards;
- staffed Warp Point scientists;
- Bring Him Home family and child scenes.

If a future pass needs shared loading/caching, add a small manager following the
existing asset-manager pattern. Do not introduce one-off path loading in several
screens.

## Enemy Identity Presentation

Enemy identity presentation is a readability layer and must preserve underlying
combat mechanics.

- Invisible enemies: keep identity, art, HP, weaknesses, and resistances gated
  by existing Sight/visibility rules. Any reveal note should explain why the
  player can or cannot inspect the target.
- Special forms: form-change notes should describe the visible state change
  without replacing the canonical enemy name or combat sprite lookup.
- Construct-friendly bleed flavor: wording such as `Oil Leak` may be presented
  for construct enemies, but the underlying effect remains `Bleed` for combat
  logic, saves, tests, and compatibility.

## Website

The public-facing website/project page remains deferred until title and identity
direction are stable. Do not spec or implement website files from this gate
until the roadmap promotes that work out of deferral.

## Generated Bitmap Workflow

Generated bitmap batches require:

- transparent PNGs for runtime sprites and overlays;
- JSON map or manifest entries when the existing loader pattern requires them;
- runtime fallback behavior for missing or failed assets;
- a checked-in review sheet/contact sheet before runtime integration.

The review-sheet requirement follows the enemy combat sprite precedent. Review
sheets should show every generated asset against a neutral game-adjacent
background and make clipping, rectangular backgrounds, scale mismatches, and
silhouette problems visible.

Prefer existing systems:

- status and effect icons through `status_icons.py`;
- enemy combat visuals through `EnemyCombatSpriteManager`;
- dungeon and Warp Point visuals through the dungeon texture manifest;
- town/NPC art through a dedicated manager only if direct path loading would be
  duplicated.

Do not replace combat sprites with portraits, tokens, rectangular cards, or
UI-framed art.

## Validation

Focused tests should cover:

- Character Created screen drawing, keyboard/mouse continue, portrait fallback,
  and text wrapping.
- Story-card page advancement, Escape skip, mouse continue, and page counters.
- Combat cue classification and drawing for reflect, stun/prone, elemental
  strikes, and no-cue no-damage outcomes.
- Asset managers or manifest mappings for missing asset fallback, invalid
  mapping tolerance, cache clearing, and review-sheet builder smoke behavior
  when new generated batches are integrated.
- Enemy identity presentation for invisible reveal text, form-change notes, and
  construct bleed-flavor wording without changing the canonical effect name.
