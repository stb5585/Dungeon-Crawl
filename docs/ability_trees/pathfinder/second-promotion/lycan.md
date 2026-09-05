# Lycan Ability Tree Implementation Reference

Status: `Finished`

Tier: terminal. Breadth: 28 development nodes costing 30 points across Frenzy,
Moon Hunt, Dragon Essence, and Control. [Current diagram](lycan.svg). The 20
terminal-tier points buy 66.7% of the graph.

## Progression Shape

Each discipline contains seven nodes. Frenzy carries Werewolf, Charge, and
Battle Cry; Moon Hunt carries Mortal Strike and Lunar Rend; Dragon Essence
carries Winged Pounce and Dragon Fang; Control carries Dispel, Center the Beast,
and defensive choices. Frenzied Force raises
the live Frenzy damage bonus from 20% to 30%, while Measured Breath reduces
Frenzy trigger odds by 15%. The Frenzy and Moon Hunt capstones cost two points.

Lunar Rend is a Werewolf-only 140% strike that applies Bleed. Dragon Fang
requires both Werewolf form and canonical Dragon Essence, combining weapon and
Fire damage. Center the Beast grants two turns of defense and halves exactly
the next Frenzy check without awarding control credit.

The tree deliberately offers no purchasable control ranks. Feral, Muzzled,
Restive, Tethered, and Tame still advance only from the existing survive,
dismiss, resist, and safe-dismiss behavior records. Dragon Essence and Winged
Pounce retain their canonical unlock and form requirements.

## Boundaries And Acceptance

- Werewolf remains the only Lycan form; Red Dragon is not restored as a form.
- Moon phase, Frenzy Lock, control progress, Dragon Essence, form overlay, and
  exact dismissal restoration retain their existing persistence rules.
- No talent grants stress credit, control rank, or a second form.
