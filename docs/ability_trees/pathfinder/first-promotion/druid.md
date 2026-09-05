# Druid Ability Tree Implementation Reference

Status: `Finished`

Tier: first promotion. Breadth: 28 development nodes costing 28 points across
four six-node disciplines and a shared Primal Practice column, plus independent
Lycan and Archdruid promotions.
[Current diagram](druid.svg). After reserving three promotion points, the 12
remaining tier points buy 42.9% of the deliberately broad dual-promotion graph.

## Progression Shape

| Discipline | Nodes in order |
| --- | --- |
| Panther Form | Transform; +20 Attack; Feline Grace; Mortal Strike; Razor Ambush; Apex Prowler |
| Direbear Form | Transform II; Thick Hide; +20 Defense; Bearish Might; Rooted Guard; Guardian Beast |
| Venom and Stone | Poison Dart; +20 Magic; Resist Poison; Noxious Mist; Stone Skin; Earthen Toxins |
| Growth and Stars | Regrowth; Restoring Boon; Calming Breeze; +20 Magic Defense; Seasonal Rite; Starfall |
| Primal Practice | Primal Practice; +50 HP; +50 MP; Primal Versatility |

Lycan accepts either completed form discipline. Archdruid accepts either
completed nature discipline. This lets a player cross-train without requiring
the competing identity in full. The four new casts add area Poison pressure,
an exploration-time Poison ward, immediate Regrowth conversion, and a
three-impact area attack.
Primal Practice is an ungated active technique that raises Attack while
transformed or Magic while in natural form for three turns.

## Boundaries And Acceptance

- Panther, Direbear, form dismissal, equipment replacement, and exact HP/MP
  deficit restoration continue to use the serialized transformation overlay.
- Resist Poison lasts 100 exploration steps and contributes 50% Poison
  resistance through the normal resistance calculation.
- Restoring Boon clears the existing Regen effect after converting its
  remaining ticks at 125%; it does not create another healing meter.
- Apex Prowler, Guardian Beast, Earthen Toxins, and Starfall occupy the level-55
  row. Both promotions sit on row 7 and the tree stays inside the eight-row view.
