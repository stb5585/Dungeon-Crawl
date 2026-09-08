# Ability Taxonomy Baseline

Status: `Complete — 197/197 Definitions Validated`

The foundational migration assigns every YAML ability an immutable filename
slug, legacy class-token and display-name aliases, closed taxonomy, registered
traits, and an actor-relative targeting policy. The exact legacy allowlist is
empty. CI runs:

```bash
./.venv/bin/python tools/validate_ability_taxonomy.py --require-complete
```

## Inventory

| Axis | Counts |
|---|---|
| Origin | martial 56; innate 34; natural 30; arcane 29; divine 27; extraplanar 11; spiritual 6; alchemical 4 |
| Primary intent | damage 112; protection 29; control 25; restoration 12; utility 9; mobility 7; information 2; summoning 1 |
| Activation | active 192; passive 3; reaction 2 |

The migration is deterministic and reviewable in
`tools/migrate_ability_taxonomy.py`. Explicit family sets resolve semantic
cases that cannot be inferred safely from the overloaded legacy `type` and
`subtype` fields. Notable decisions include:

- Arcane Blast and Astral Judgment are damage actions despite legacy
  `Power Up` subtype values.
- Great Gospel is primarily restoration, with its protection behavior
  remaining in declarative effects.
- Consume Item is a direct alchemical consumption action; it is not a player
  inventory action and therefore does not use the `item_action` form.
- Counterspell and Resurrection are reactions. Purity of Body, its upgrade,
  and Reveal are passive.
- Shared display-name aliases are allowed only when every owner actually has
  that display name. Non-display alias collisions remain validation errors.

This baseline classifies behavior but does not tune damage, accuracy, costs,
progression, or encounter composition. Legacy execution selectors remain only
until specialized Python behavior has moved behind the validated definition
contract.
