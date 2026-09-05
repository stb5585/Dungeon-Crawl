# Conjurer Ability Tree Implementation Reference

Status: `Finished`

Conjurer has 21 nodes across `Constructs`, `Binding`, `Illusion / Movement`, and
`Calling`. Six location-aware Callings and Conjure Animal create transient
companions and feed alternative routes to Thaumaturgist.
[Runtime diagram](conjurer.svg).

Transient-slot rules, duration, location selection, Calling ownership,
promotion joins, and the separation from permanent Xenids are covered by
`tests/core/test_class_ability_mechanics.py` and
`tests/core/test_promotion_class_kits.py`.
