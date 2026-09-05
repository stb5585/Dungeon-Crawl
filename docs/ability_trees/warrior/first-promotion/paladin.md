# Paladin Ability Tree Implementation Reference

Status: `Finished`

Paladin has 22 nodes across `Zeal`, `Grace`, and `Sanctity`. Independent Oath's
Judgment and Oath's Shelter roots feed attack, Holy, healing, and protection
routes before joining the centered Crusader promotion.
[Runtime diagram](paladin.svg).

Permanent vows, combat-only Conviction, signature spends, route geometry,
promotion gates, and retained abilities are covered by
`tests/core/test_paladin_vows.py` and
`tests/core/test_paladin_crusader_trees.py`.
