# Beast Master Ability Tree Implementation Reference

Status: `Finished`

Tier: terminal. Breadth: 22 development nodes across `Pack Tactics` and
`Commands`. [Current diagram](beast-master.svg).

## Decision

All four original commands, Zephyrstrike, Cover, and Bonded Bulwark retain
their stable IDs. Pack Tactics specializes coordinated offense, quarry
pressure, and automatic companion traits. Commands specializes Guard Partner,
Harry Prey, Mend Wounds, condition recovery, and bond-scaled protection. The
tree adds two commands but never adds another companion action.

## Authored Tracks

| Identity | Track | Nodes in order |
| --- | --- | --- |
| Pack Tactics | Pack Assault | Pack Strike; Heavy Hunter; Coordinated Assault; Alpha Instinct; Unleash Instinct; Apex Pack |
| Pack Tactics | Quarry Control | Zephyrstrike; Harry Prey; Trail Guard; Crippling Harrier; Cornered Prey |
| Commands | Guardian | Cover; Guard Partner; Bonded Bulwark; Mend Wounds; Field Dressing; Guardian Pack |
| Commands | Command Mastery | Rally Partner; Commander's Voice; Adaptive Orders; Perfect Coordination; True Bond |

Heavy Hunter grants 15% two-handed damage against the favored enemy. Trail
Guard reduces damage from that enemy type by 10%. Coordinated Assault rewards
fighting beside a living companion, while Cornered Prey and Apex Pack improve
companion damage without creating another turn.

Unleash Instinct spends the pending companion action on its species trait.
Rally Partner spends that action healing the Beast Master and clearing one
harmful condition. Commander's Voice strengthens command values, Adaptive
Orders extends commands used against the quarry, and Perfect Coordination lets
a missed Pack Strike still deliver its species trait. Guardian Pack improves
Guard Partner and splits Mend Wounds treatment across both partners. True Bond
adds another ten percentage points to bond-derived combat scaling.

## Boundaries And Acceptance

- Reuse roster, active companion, bond, pending command, special trait, and
  Shared Recovery state. Node ownership is the only new persistence.
- Preserve one active companion and one companion action boundary.
- Use the Companion & Hunt tab, command picker, HUD, detail view, and logs.
- Exclude stables, multi-companion combat, collection rewards, summon death
  penalties, and broad species rebalance.
- Focused regression coverage verifies the 22-node graph and legacy IDs,
  restored Ranger talents, both new commands, offensive and guardian capstones,
  quarry interaction, bond scaling, condition recovery, and action cleanup.
- Remaining evidence is balance-only: measure high-bond automatic action
  frequency, command strength with an awakened Shared Recovery ring, and
  low-health Cornered Prey pacing in representative terminal encounters.
