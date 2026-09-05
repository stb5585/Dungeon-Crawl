# Dragoon Ability Tree Implementation Reference

Status: `Finished`

Dragoon has 33 nodes and retains Lancer's Jump and polearm graph while adding
Dragonheart, advanced landings, Polearm Mastery, and Dragon Dive. Its seven
branches remain aligned with the Lancer layout. [Runtime diagram](dragoon.svg).

Aerial Tempo, modifier prerequisites, retained node ownership, Dragon Essence
separation, landing effects, and row bounds are covered by
`tests/core/test_lancer_dragoon_trees.py` and
`tests/core/test_dragoon_dragon_quest.py`.
