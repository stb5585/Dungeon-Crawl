# P4b Realm Of Cambion Audit

Status: `Audited`

## Confirmed Current Flow

- Entry starts from the Underground Spring after the Wizard's Folly path opens; the player's return location and facing are saved before moving into the Realm of Cambion.
- Portal tiles either move the player through configured in-realm portal pairs or return them to the saved spring location when no pair is configured.
- Rotator tiles push the player to an adjacent walkable tile and avoid immediately returning to the previous tile when another option exists.
- The anti-magic terminal starts active for the realm, accepts the current code `2749`, disables the field on success, and starts alarm combat on failure.
- Merzhin victory collapses the realm, exits to the saved return location, clears the boss tile enemy, and marks the dungeon view dirty.
- Merzhin defeat exits the realm without using the normal town death flow.

## Special-Tile Presentation

- Portal, Rotator, active FunhouseTeleporter, and visited FakeWall/Fake Path presentation already have renderer coverage.
- No new map tile class is required before adding the next Realm of Cambion content beats.

## Next Content Targets

- Add post-Merzhin follow-up dialogue or town reactions after quest turn-in hooks are selected.
- Add subtle Realm of Cambion flavor messages around portals, rotators, and anti-magic state only where they do not interrupt movement.
- Defer new special tiles until a concrete content beat requires one.
