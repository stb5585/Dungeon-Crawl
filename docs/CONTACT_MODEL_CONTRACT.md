# Combat Contact-Model Contract

Status: `Shipped — Preserve Unless A New Combat Spec Replaces It`

Combat resolves exactly one shared contact draw per strike. Weapon contact uses
the fitted weapon axes; spell contact uses the fitted spell axes. Accuracy and
dodge modifiers apply through the approved pipeline in
`src/core/combat/contact.py`; resistance, immunity, Reflect, damage reduction,
and authored contests remain post-contact behavior.

The fitted model is deterministic. Its seed-1337 characterization must remain
within a weighted mean error of three percentage points and an ordinary-cell
maximum error of seven percentage points. Verify the committed fit with:

```bash
./.venv/bin/python tools/fit_contact_model.py --check
```

An always-hit action bypasses contact only; it does not bypass later defenses.
Failure attribution uses the same contact draw and must not introduce a second
roll.

The pre-foundation tables, original characterization command, and retained
comparison reports are browsable history in
[`history/FOUNDATIONAL_CHARACTERIZATION_BASELINE.md`](history/FOUNDATIONAL_CHARACTERIZATION_BASELINE.md).
