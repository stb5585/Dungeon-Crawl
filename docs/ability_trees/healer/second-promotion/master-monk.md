# Master Monk Ability Tree Implementation Reference

Status: `Finished`

Tier: terminal. Four seven-node disciplines contain 28 nodes costing 30
points. [Runtime diagram](master-monk.svg). The 20 terminal-tier points buy
66.7% of development cost.

## Implemented Decision

`Perfected Flurry` improves multi-hit accuracy, control, Chi Heal, and purity.
`Final Art` develops Hadouken and Suplex into the full-Ki Dim Mak finisher.
`Diamond Body` covers unarmed mitigation, reaction recovery, reflection, and
the bounded Dim Mak refund. `Rope-a-Dope` adds the requested active challenge:
it enters an escalating dodge stance, breaks when hit, and releases a four-hit
combination after three consecutive dodges.

The Rope-a-Dope branch can improve its challenge chance, base and escalating
dodge, counter damage, and post-combination recovery. Dim Mak keeps Death and
boss immunity, its independent Stun contest, ordinary-staff penalty/disarm,
Ruyi Jingu Bang exception, and once-per-combat refund boundary.

## Validation Contract

- Rows follow ungated, 65, 70, 75, 80, 85, and 90.
- Ki capacity remains five and no talent creates unconditional execution.
- Rope-a-Dope tracks only combat state and clears with normal combat cleanup.
- Focused tests cover its escalating dodge and four hits, Dim Mak adjustments,
  unarmed defense, Ki economy, point coverage, and diagram parity.
