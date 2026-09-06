# Master Monk Ability Tree Implementation Reference

Status: `Finished`

Tier: terminal. Five disciplines contain 27 nodes costing 28 points.
[Runtime diagram](master-monk.svg). The 20 terminal-tier points buy 71.4% of
development cost.

## Implemented Decision

`Perfected Flurry` improves multi-hit accuracy, control, Chi Heal, and purity.
`Final Art` develops Hadouken directly into Suplex. `Diamond Body` covers
unarmed mitigation, reaction recovery, and reflection. `Rope-a-Dope` adds the
requested active challenge: it enters an escalating dodge stance, breaks when
hit, and releases a four-hit combination after three consecutive dodges.
`Dim Mak Mastery` contains six optional terminal modifiers for the Power Core
quest reward; Dim Mak itself is not purchasable from the tree.

The Rope-a-Dope branch can improve its challenge chance, base and escalating
dodge, counter damage, and post-combination recovery. Dim Mak keeps Death and
boss immunity, its independent Stun contest, ordinary-staff penalty/disarm,
Ruyi Jingu Bang exception, and once-per-combat refund boundary.

## Validation Contract

- Rows follow ungated, 65, 70, 75, 80, 85, and 90.
- Every Dim Mak modifier is a leaf and cannot block ordinary class progress.
- Ki capacity remains five and no talent creates unconditional execution.
- Rope-a-Dope tracks only combat state and clears with normal combat cleanup.
- Focused tests cover its escalating dodge and four hits, Dim Mak adjustments,
  unarmed defense, Ki economy, point coverage, and diagram parity.
