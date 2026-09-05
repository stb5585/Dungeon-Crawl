# Thaumaturgist Ability Tree Implementation Reference

Status: `Finished`

Thaumaturgist has 29 nodes across Callings, Xenid choices, Xenid ultimates,
Conduit, and Miracles. Seven permanent two-Xenid choices replace Conjurer's
transient results while conduit drives growth and ability tiers.
[Runtime diagram](thaumaturgist.svg).

Fixed roster choices, conduit progression/death loss, Raise Summon, reciprocal
effects, Reality Fragment Miracles, and save/load are covered by
`tests/core/test_thaumaturgist_conduit_payoff.py` and
`tests/core/test_promotion_class_kits.py`.
