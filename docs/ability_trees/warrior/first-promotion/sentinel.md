# Sentinel Ability Tree Implementation Reference

Status: `Finished`

Sentinel has 24 nodes across `Assault`, `Wall`, Resolve roots, `Resistance`,
`Support`, and unbound actions. Four level-55 talents provide alternative
Stalwart Defender promotion routes. [Runtime diagram](sentinel.svg).

Resolve generation, passive Shield Riposte and Spell Reflection, persistent
Burst mastery, promotion joins, and ring boundaries are covered by
`tests/core/test_sentinel_stalwart_trees.py` and
`tests/core/test_promotion_class_kits.py`.
