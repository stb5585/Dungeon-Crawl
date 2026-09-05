# Stalwart Defender Ability Tree Implementation Reference

Status: `Finished`

Stalwart Defender has 25 nodes across `Assault`, `Bulwark`, `Shield Offense`,
`Resistance`, and `Support`. Four persistent mastery tracks unlock distinct
full-Resolve Bursts, while purchased talents modify the Resolve loop.
[Runtime diagram](stalwart-defender.svg).

Mastery persistence, qualifying-use deduplication, Burst discovery, Resolve
spends, shield actions, and ring interaction are covered by
`tests/core/test_sentinel_stalwart_trees.py`.
