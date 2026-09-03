# Shipped Regression Checklist

Record class-kit UI/log, meter cadence, preservation, action-economy, and
progression pacing findings in
[`CLASS_KIT_EVIDENCE_NOTES.md`](../CLASS_KIT_EVIDENCE_NOTES.md). Checklist items
remain the prompts; the evidence ledger is the running decision record.

## Found Issues

## Recently Changed

### Roadmap Bugfix Pass
- [ ] Use Smoke Screen from an invalid/non-fleeing state, then enter another battle.
  - Expected: Player Smoke Screen requires and consumes one `Smoke Bomb`; enemies can still use their innate Smoke Screen behavior.
  - Expected: No stale smoke fade, hidden enemy, or flee transition carries over.
- [x] Open the Character screen in Town, a normal dungeon, Realm of Cambion, and Liminal Gap.
  - Expected: Location text is fully readable and does not collide with nearby details.
- [x] Check Records/Statistics on promoted characters.
  - Expected: Highest Level Reached uses cumulative promoted level.
- [x] Visit pygame potion/alchemist/secret consumable shops.
  - Expected: Status items such as Antidote, Eye Drop, Echo Screen, Bandage, and Phoenix Down are available.
- [x] Accept multiple available bounties in one Tavern visit.
  - Expected: The Accept Bounty screen remains open until Back/Cancel or no new bounties remain.
  - Expected: If no new bounties are available, the notice popup keeps the
    Bounty Board menu visible behind it instead of returning to the main
    Tavern menu frame.
- [x] Complete or abandon all board bounties, then revisit the Tavern before and after making progress.
  - Expected: The board does not refill immediately, then restocks after enough dungeon steps, enemy defeats, or a level gain.
- [x] Fight enemies that stun, sleep, or otherwise incapacitate the active actor.
  - Expected: Incapacitated actors do not display an active turn token.
- [x] Compare flying and grounded enemies in combat.
  - Expected: Flying enemies render slightly higher without leaving the combat frame.
  - Expected: Flying enemies are not inherently immune to Earth elemental
    damage. Ground-contact Earth spells such as `Tremor`, `Mudslide`, and
    `Earthquake` do not damage flying targets, while non-grounded Earth effects
    such as `Sandstorm` can.
- [x] Check minimap adjacent markers around walls, closed doors, and undiscovered Fake Walls.
  - Expected: Only enterable visible directions are shown, undiscovered Fake Walls are not revealed, and discovered non-Fake blocking walls appear on later map review.
- [x] Fight a Shapeshift-capable enemy.
  - Expected: The enemy can Shapeshift once, refresh its sprite/name, then take one normal same-turn action.
- [x] Browse weapon/offhand shop item details as a dual-wield-capable character.
  - Expected: Main Hand and OffHand comparisons are separate and unusable slots are called out.

### Remaining Improvements Pass
- [x] Select/click an equipment slot in the modern Character Menu and open the
  replacement picker.
  - Expected: The filtered replacement list appears without a one-frame flash
    of the full equipment-slot list.
- [ ] Die in normal PyGame dungeon combat after level 10, then repeat in Funhouse and Realm of Cambion.
  - Expected: Normal death uses resurrection gold/stat messaging and returns to town; special exits keep their route-specific defeat behavior.
- [ ] Pick up the Rookie Mistake body, die before town, return to the death tile, and pick it up again.
  - Expected: The body is removed from inventory on death, visible where dropped, recoverable, and only turned in after returning to town with it.
- [ ] Promote a character while wearing one legal and one illegal core-slot item.
  - Expected: Legal gear stays equipped, illegal gear moves to inventory, empty illegal slots become `No*` gear, and no promoted-class default gear is granted.
- [ ] Move between town/church/inn/barracks/storage menus and transient confirmation/select-one screens.
  - Expected: Hub menus retain cursor position within the same visit; transient screens reset.
- [ ] Browse load-game saves with valid, corrupt, and missing-asset portrait data.
  - Expected: Valid saves show a portrait preview; corrupt or missing portrait cases fall back cleanly.
- [ ] Search Joffrey's body after turning in Bad Dream and before defeating the Waitress.
  - Expected: The Mad Waitress cue uses the existing sprite, plays the waitress wail if available, then starts combat.
- [ ] Approach the Minotaur room on level 1.
  - Expected: The existing bone pile tile appears on the approach path without changing the boss room.

### Class Ring Activations
- [ ] Inspect Class Ring wording across absent, inventory-only, stored, equipped dormant, and equipped awakened states.
  - Expected: Item/status/story text distinguishes town-visible rings from inventory-only rings, and distinguishes dormant/awakened state from equipped active effects.
- [ ] Inspect special Class Ring descriptions for Grandmaster of Arms, Demonologist, and Archdruid.
  - Expected: Grandmaster names Secret Master binding and equipped-only bound bonuses; Demonologist separates basic contracts from empowered contracts and echo identity; Archdruid separates Fourfold/Grove progress from equipped Harmony Bonus.
- [ ] Visit the Barracks as a Berserker with a dormant Class Ring equipped.
  - Expected: The Barracks menu includes `No Healing Duel`.
  - Expected: Winning the duel awakens the ring and changes its equipped mod to `Bloodied Crits`.
- [ ] Visit the Barracks as a Berserker with a dormant Class Ring only in inventory.
  - Expected: The Barracks menu does not show `No Healing Duel`.
- [ ] Store the dormant Berserker Class Ring in the Barracks storage locker, then revisit the Barracks.
  - Expected: The Barracks menu shows `No Healing Duel` even if the ring is not equipped.
- [ ] Restore HP during the Berserker No Healing Duel through a potion, spell, or regeneration effect.
  - Expected: The duel immediately fails with no normal death penalty.
  - Expected: Any consumable used before the failure remains spent.
- [ ] Lose or flee from the Berserker No Healing Duel.
  - Expected: The ring remains dormant and the player is not sent through the normal death/resurrection flow.
- [ ] Visit the Barracks as a Dragoon with a dormant Class Ring equipped or stored.
  - Expected: The Barracks menu includes `Guard The Fall`.
  - Expected: Winning the trial awakens the ring and changes its equipped mod to `+1 Jump Mod`.
- [ ] Visit the Barracks as a Stalwart Defender with a dormant Class Ring equipped or stored.
  - Expected: The Barracks menu includes `Siege Trial`.
  - Expected: Winning the trial awakens the ring and changes its equipped mod to `Guard Meter`.
- [ ] Lose or flee from `Guard The Fall` or `Siege Trial`.
  - Expected: The ring remains dormant and the player is not sent through the normal death/resurrection flow.
- [ ] Visit the Church as a Wizard, Shadowcaster, or Knight Enchanter with a dormant Class Ring equipped or stored.
  - Expected: The Church menu includes the matching rite: `Four Formulae`, `Debt Cap Trial`, or `Arcane Duel`.
  - Expected: Completing the rite awakens the ring and applies the expected equipped mod.
- [ ] Visit the Church as a Thaumaturgist with a dormant Class Ring equipped or stored.
  - Expected: The Church menu includes `Conduit Ritual`.
  - Expected: Completing the rite awakens the ring, applies `+30% Xenids`, and permanently sacrifices 5% max HP.
- [ ] Visit the Church as a Templar, Hierophant, Master Monk, Archbishop, Troubadour, Lycan, Astromancer, Soulcatcher, or Beast Master with a dormant Class Ring equipped or stored.
  - Expected: The Church menu includes the matching rite: `Relic Defense`, `Purity Rite`, `Miracle Vigil`, `Lost Ballad`, `Control Rite`, `Star Chart`, `Ancestral Totem Rite`, or `Pack Trial`.
  - Expected: Completing the rite awakens the ring and applies the expected equipped mod.
- [ ] Promote a Warrior-line character to Paladin in pygame and curses.
  - Expected: Promotion requires choosing one permanent vow: `Redemption`, `Conquest`, `Protection`, or `Retribution`.
  - Expected: The pygame vow picker uses the styled selection popup and updates
    signature skill, aura, mark, and broad playstyle details while each vow is
    highlighted over the existing progression background, without revealing
    percentage or duration tuning.
  - Expected: Selecting a vow opens an explicit `Swear the Vow` confirmation;
    declining it returns without committing the promotion.
  - Expected: Canceling the vow choice cancels promotion.
  - Expected: Completing promotion grants the matching vow skill: `Redeem`, `Challenge`, `Interpose`, or `Judgment Riposte`.
- [ ] Load or create a legacy Paladin/Crusader save with no vow, then visit the Church.
  - Expected: The Church menu includes `Swear Paladin Vow`.
  - Expected: Choosing a vow persists it and grants the matching vow skill.
- [ ] Visit the Church as a Crusader with a dormant Class Ring equipped or stored and a sworn vow.
  - Expected: The Church menu includes `Vow Trial`.
  - Expected: Completing the trial awakens the ring, stores the chosen vow, and changes the equipped mod to `Vow Affirmation`.
- [ ] Visit the Church as a Crusader with a dormant Class Ring but no sworn vow.
  - Expected: `Vow Trial` does not appear until a vow is sworn.
- [ ] Test `Redeem` against a wounded non-boss enemy and against a boss/Class Ring trial enemy.
  - Expected: Eligible mercy victories grant XP and gold, but no item loot, kill credit, bounty credit, or quest progress.
  - Expected: Boss and Class Ring trial enemies refuse mercy.
- [ ] Test `Challenge`, `Interpose`, and `Judgment Riposte` in combat.
  - Expected: Challenge marks one enemy for 3 turns and Conquest Aura can stack after defeating the challenged or bounty target.
  - Expected: Interpose lasts 2 turns, strengthens the next block, and successful blocks stack Protection Aura.
  - Expected: Judgment Riposte counters the next enemy attack, and a killing counter doubles Retribution Aura duration.
- [ ] Compare Paladin vow aura/mark values before and after equipping an affirmed Crusader Class Ring.
  - Expected: Aura benefits are 50% stronger.
  - Expected: Mark penalties/durations are reduced by 50%, and Mark of Mercy lethal threshold drops from 10% HP to 5% HP.
- [ ] As a Lancer or Dragoon, unlock and equip the `Recover` Jump modification, then use Jump against the Red Dragon at high HP.
  - Expected: The encounter resolves without a low-health requirement.
  - Expected: Messaging says Recover restored Kaelenon's lost transformation ability rather than healing the Red Dragon's HP.
  - Expected: `Dracarys` and standard Red Dragon progression remain completable, including `Dragon's Fury` Jump unlock.
- [ ] Try the Red Dragon route as a non-Lancer/Dragoon, without active `Recover`, and against a non-Red-Dragon target.
  - Expected: Kaelenon restoration does not trigger in any ineligible case.
- [ ] After restoring Kaelenon, interact with the Realm of Cambion anti-magic terminal.
  - Expected: The terminal grants `Kaelenon's Portal Key` once without requiring the anti-magic override code.
- [ ] Return to the Realm of Cambion terminal with `Kaelenon's Portal Key`.
  - Expected: Kaelenon returns home, `Draconite` is granted once, and later terminal interactions do not duplicate the reward.
- [ ] Visit the Jeweler with `Draconite`.
  - Expected: The Jeweler offers `Craft Draconite Pendant`.
  - Expected: Crafting consumes `Draconite`, grants `Draconite Pendant`, and removes the craft option.
- [ ] Equip `Draconite Pendant` and use Jump with `Recover`.
  - Expected: Recover restores more HP and MP than the baseline Recover Jump.
- [ ] Visit the Church for a Mage-branch rite with the Class Ring only in inventory.
  - Expected: The class-specific rite does not appear until the ring is equipped or stored.

### Voluntas Class Identity Bridge
- [ ] After Voluntas is revealed, use the Liminal guide with a visible Class Ring to run `Affirm Class Path`, `Revisit Class Path`, `Bridge Class Identity`, and then enter the Reflection path mirror.
  - Expected: The bridge appears only after affirmation and revisit, plays one generic Voluntas beat plus one recorded-class beat, then disappears after being seen.
  - Expected: The bridge uses the class recorded at affirmation even if the current class, equipment, or ring state changes later.
  - Expected: HP, MP, XP, loot, Class Ring mechanics, true-final gates, Reflection mechanics, and route rewards do not change from viewing the bridge.

### Story And Endgame Route
- [ ] Enter the final chamber before true-final unlock and trigger the Vesperion false-final route.
  - Expected: Vesperion uses the Vesperion identity and `Choose Fate` framing, not Devil/Balor copy.
  - Expected: The scripted transition sends the player to the Liminal Gap without normal town resurrection, XP, loot, quest turn-in, or boss-room victory handling.
- [ ] In the Liminal Gap, interact with the Hooded Figure guide before and after completing Guardian trials.
  - Expected: The guide reveal stays distinct from Vesperion, guide save access works only from approved Liminal surfaces, and clue review never completes missing trials.
  - Expected: Incomplete Guardian trials play threshold/choice vignettes once, while completed older-save trials can recall unseen vignettes without re-awarding consequences.
- [ ] Complete all six Guardian clues, then visit the Seventh Seat, Acolyte, and Reflection gates in order.
  - Expected: Six clues open the Seventh Seat; Voluntas reveal does not unlock the true final by itself.
  - Expected: The Acolyte scene is non-combat, repeat-safe, and presents a failed-hero mirror rather than a boss.
  - Expected: Reflection remains locked until Voluntas is remembered and the Acolyte warning has been faced.
- [ ] Lose to the Reflection/Psychopomp, then retry and win.
  - Expected: Defeat returns to the Liminal hub at the route-specific recovery state without town death flow, XP, loot, or boss-tile victory routing.
  - Expected: Attempts/failures save and reload correctly, retry copy remains readable, and victory sets `reflection_defeated` plus `true_final_unlocked`.
- [ ] Enter the true-final Vesperion battle after Reflection victory.
  - Expected: The true-final choice argument and tragedy reframing play once, acknowledge the busboy disguise and Waitress/Joffrey grief, and do not change Vesperion tuning or route gates.
  - Expected: Completed Guardian trials blunt or cancel their matching `Choose Fate` and phase-pressure consequences with clear combat-log text.
- [ ] Defeat true-final Vesperion and view the complete ending sequence.
  - Expected: Victory grants no normal XP, loot, quest completion, death-cost routing, or boss-tile reward.
  - Expected: `Vesperion True Final Victory`, `The Forsaken Tenet Ending`, and `The Thirsty Dog Epilogue` play in a coherent order with usable continue/skip input.
  - Expected: The ending preserves Voluntas as free choice and does not imply that grief, Joffrey's death, or the Acolyte's loss were erased.
- [ ] Save/load after `main_story_complete`, then re-enter the final chamber and visit town/tavern surfaces.
  - Expected: `vesperion_true_final_defeated` and `main_story_complete` persist.
  - Expected: The final room shows a reminder instead of restarting Vesperion or duplicating ending rewards.
  - Expected: Any postgame town dialogue is local, repeat-safe, and does not mutate quests, shops, bounties, church, inn, barracks, storage, or NPC availability.
- [ ] Run the Red Dragon route as a Lancer/Dragoon with `Recover`, as a Thaumaturgist choosing a Dragon Xenid, and as another class.
  - Expected: Copy distinguishes Red Dragon boss defeat, Kaelenon restoration, and Zahhak binding without declaring ordinary victories invalid.
  - Expected: Red Dragon floor gates, boss-room state, `Dragon's Fury`, summon unlock behavior, class rewards, and old-save compatibility remain unchanged.

### Weapon Discipline And School Affinity
- [ ] Promote a Warrior to Weapon Master.
  - Expected: The pygame promotion preview shows `Warrior -> Weapon Master`
    and highlights promotion stat deltas with a compact `Weapon Discipline`
    Character Menu note in the class details.
  - Expected: Weapon Master promotion stat deltas include `+2 STR`, `+1 INT`, and `+2 DEX`.
  - Expected: Confirming promotion applies the class change and stat bonuses,
    increases current HP/MP by the same amount as max HP/MP bonuses, and shows
    one concise summary popup with learned abilities, gear removals, and
    `Weapon Discipline` guidance when applicable.
- [ ] Promote a Warrior to Paladin, Lancer, and Sentinel.
  - Expected: The pygame promotion preview embeds compact Character Menu notes,
    and the post-confirmation summary names the matching post-promotion tab:
    `Oath Conviction` for Paladin, `Aerial Tempo` for Lancer, and `Resolve` for
    Sentinel.
  - Expected: Paladin's final vow confirmation repeats only the vow question;
    detailed vow descriptions stay in the selection popup.
  - Expected: `Oath Conviction` shows the sworn vow, signature skill, aura,
    mark, and Conviction rhythm without repeating the class name.
  - Expected: Lancer/Dragoon Jump Mods are selected and toggled directly inside
    the `Aerial Tempo` tab instead of appearing as a bottom action-menu option
    or separate popup.
  - Expected: Sentinel `Resolve` shows a large centered red bar with the
    `current/cap` value inside it and Sentinel-owned Resolve-spending ability
    boxes in the class mechanic tab.
  - Expected: Sentinel/Stalwart `Resolve` appears in Combat Focus as a red
    charge bar with the `current/cap` value centered inside it.
  - Expected: Stalwart Defender keeps the inherited Sentinel Resolve actions
    while adding a `Resolve Surges` section with locked/unlocked full-bar
    payoffs.
- [ ] Promote a Pathfinder to Diviner, Shaman, and Ranger.
  - Expected: Post-confirmation help popups name the matching post-promotion
    class mechanic tab: `Runes` for Diviner, `Totems` for Shaman, and
    `Companion & Hunt` for Ranger.
- [ ] Promote through the Mage tree in pygame.
  - Expected: Post-confirmation help popups show the matching post-promotion
    class mechanic tab: `School Affinity` for Sorcerer/Wizard, `Familiar` for
    Warlock, `Contracts` for Demonologist, and `Summons` for
    Thaumaturgist.
  - Expected: Shadowcaster, Spellblade, and Knight Enchanter receive no
    Character Menu tab help popup; Umbral Debt, Blade Charge, Foundation, and
    Accent remain readable through combat HUD/status/log/action surfaces.
- [ ] Promote through the Footpad tree in pygame.
  - Expected: Post-confirmation help popups show the matching post-promotion
    class mechanic tab: `Case Journal` for Inquisitor/Seeker.
  - Expected: Thief/Rogue and Assassin/Ninja receive no Character Menu tab help
    popup; Fortune/Misfortune and Death Mark remain readable through combat
    HUD/status/log/action surfaces.
  - Expected: Spell Stealer/Arcane Trickster receive no Character Menu tab
    help popup because Stolen Charge is combat/HUD status only; class-mechanic
    guidance belongs in Thieves Guild backroom content after membership.
- [ ] Promote through the Healer tree in pygame.
  - Expected: Post-confirmation help popups show the matching post-promotion
    class mechanic tab for `Crescendo` on Bard/Troubadour.
  - Expected: Monk/Master Monk and Priest/Archbishop receive no Character Menu
    tab help popup; Ki and Prayer remain readable through combat
    HUD/status/log/action surfaces.
  - Expected: Newly learned level-1 promotion spells and skills are announced
    after promotion, including Cleric's `Sanctuary Ward`.
  - Expected: Cleric/Templar/Hierophant Devotion does not require a Character
    Menu mechanic tab; it should remain legible through combat logs, status
    rows, and skill text.
- [ ] Review the class mechanic tab triage in `docs/CLASS_KIT_DESIGN_GATES.md`
  against the pygame Character Menu.
  - Expected: Required tabs with bespoke implementations remain usable:
    `Weapon Discipline`, `Oath Conviction`, `Aerial Tempo`, `Resolve`,
    `Summons`, `Companion & Hunt`, and `Familiar`.
  - Expected: Required tabs that are still mostly generic are tracked as
    implementation follow-up: `School Affinity`, `Contracts`, `Runes`,
    `Totems`, `Case Journal`, `Crescendo`, `Forms`, and `Aspects`.
  - Expected: Devotion and Stolen Charge continue to avoid Character Menu
    tabs, using HUD/status/log/action surfaces instead.
  - Expected: Umbral Debt, Blade Charge, Foundation, Accent, Fortune,
    Death Mark, Ki, and Prayer do not appear as Character Menu tabs; their
    readiness remains readable through HUD/status/log/action surfaces.
- [ ] Fight as a Weapon Master with each supported weapon type equipped.
  - Expected: Successful main-hand/offhand hits grant Weapon Discipline XP to the matching weapon type.
  - Expected: Combat logs show per-hit Weapon Discipline XP without parenthesized progress, and the victory completion text shows the bonus Weapon Discipline XP for weapon types used in the fight.
  - Expected: Starter enemies with `pro_level = 0` grant no Weapon Discipline XP, `pro_level = 1` enemies grant half the baseline insight chance, `pro_level = 2` enemies grant baseline chance, and higher promotion levels scale upward.
  - Expected: The Character Menu shows a full-width `Weapon Discipline` tab with weapon icons, rank/XP progress bars, and visual equipped highlighting instead of a generic Class tab, description rail, or redundant summary rows.
  - Expected: Classes without a class-usage mechanic hide the middle mechanic tab and show only Character and Equipment.
  - Expected: Crossing a Weapon Discipline rank threshold reports the rank increase in combat text and names the rank-1 art unlock.
  - Expected: Rank 1 requires `24` Weapon Discipline XP, so a one-hit kill against a baseline `pro_level = 2` enemy worth `+1` hit XP and `+3` victory XP no longer reaches rank 1 after only two kills.
  - Expected: Rank 1 unlocks the matching art: `Iron Palm`, `Hemorrhage`, `Riposte Line`, `Low Sweep`, `Guard Cleaver`, `Reaver's Mark`, `Brace`, or `Anvil Strike`.
- [ ] Try each Weapon Art with a matching and nonmatching weapon equipped.
  - Expected: Matching weapons allow the art when MP is sufficient.
  - Expected: Nonmatching weapons fail clearly without spending MP or applying effects.
- [ ] Raise one Weapon Discipline to rank 5 and rank 10, then use its art.
  - Expected: Rank 5 and rank 10 add the documented improved/mastered behavior without changing the save key shape.
- [ ] Promote a Weapon Master with discipline progress into Berserker.
  - Expected: Weapon Discipline ranks and unlocked arts carry forward and remain usable.
- [ ] Promote a Weapon Master into Grandmaster of Arms.
  - Expected: Grandmaster of Arms promotion stat deltas include `+2 STR`, `+1 INT`, and `+2 DEX`.
- [ ] Awaken and equip a Grandmaster of Arms Class Ring, bind it to a weapon, then use the matching rank-10 art.
  - Expected: Bound discipline bonuses double while equipped.
  - Expected: Perfect Bound Art adds the conservative bound-weapon mastered bonus only for the bound weapon type.
- [ ] Cast Fire/Ice/Water/Electric/Earth/Wind spells as Sorcerer.
  - Expected: The matching school rises from 0, the opposite school drops, and other schools drift down without going below 0.
  - Expected: Sorcerer affinity caps at 50, permits tier-2 spell purchases at 30, and improves matching rider support at 50.
- [ ] Master Ice affinity as Sorcerer or Wizard with `Frozen Armor` learned, then take incoming damage.
  - Expected: Before Ice mastery, `Frozen Armor` has no damage-reduction effect.
  - Expected: At Ice mastery, incoming damage is modestly reduced and combat text reports the frost ward absorption.
- [ ] Cast Fire/Ice/Water/Electric/Earth/Wind spells as Wizard before and after awakening the Wizard Class Ring.
  - Expected: Wizard affinity caps at 100, unlocks tier-3 spell upgrades at 80, and applies matching damage bonuses per full 10 affinity.
  - Expected: With the awakened ring equipped, matching casts gain +3 affinity instead of +2 and final mastery enables 3-stack school buffs.
- [ ] Load a legacy Sorcerer/Wizard save with old 50-centered affinity values.
  - Expected: Values migrate to the new 0-based model, clamp to the active class cap, and remain readable in character/ring status text.

Audit correction (2026-09-02): Pathfinder promotion checks in this file mix
working regressions with pending acceptance targets. The rune foundation,
elemental Totems, Archdruid persistent Fourfold/Grove system, and Ranger/Beast
Master companion loop are substantially implemented. `Learn Spell`, Threaded
Cast payoff, Druid persistent forms, Lycan control/Dragon Essence routing,
combat Aspect Harmony riders, and Soulcatcher harvest/Aspect Evolution payoffs
are not shipped. Treat checks for those behaviors as implementation acceptance,
not regression evidence.

### Diviner And Astromancer Runes
- [ ] Win combat as a Diviner with Fire, Water, Wind, and Earth natural spells across enemies with neutral resistance, resistance, and weakness to the killing spell's element.
  - Expected: Matching sign runes can drop from natural-spell kills, cap at 3 per sign, and weakness/resistance visibly changes the drop cadence over repeated attempts.
- [ ] Use `Runic Boost` as a Diviner with available and unavailable matching runes.
  - Expected: The combat menu includes `Runic Boost` only when at least one boostable natural spell has a matching rune and enough MP.
  - Expected: The selection menu lists only currently boostable natural spells, consumes one matching rune, and casts the selected spell with the fate floor.
- [ ] Repeat `Runic Boost` as an Astromancer while casting normal natural spells between uses.
  - Expected: Every natural spell cast, including Runic Boost, advances the visible constellation cycle.
  - Expected: Pygame and curses combat views show the current sign and four compact rune rows.
- [ ] Awaken and equip the Astromancer Class Ring, then use `Runic Boost` with a spell matching the active sign.
  - Expected: Active-sign Runic Boost uses the 100% fate floor only while the awakened Class Ring is equipped.
  - Expected: Unequipping the ring leaves rune drops and the cycle available but returns Runic Boost to the baseline 75% floor.
- [ ] Gain the Astromancer Power Core skill and use `Astral Judgment` on each active sign.
- [ ] Gain the Hierophant Power Core skill and use `Sacred Overchannel` before staff, Holy, and `Consecrated Conduit` payoffs.
  - Expected: `Astral Judgment` resolves the current sign, applies the matching first-pass rider, and then randomly spins to a new sign.
  - Expected: Kills from `Astral Judgment` do not award runes.
- [ ] Play through several Diviner combats before Astromancer promotion while spending runes normally.
  - Expected: Rune drops are frequent enough to make `Runic Boost` visible, but not so frequent that the player sits capped at 3 runes per sign after ordinary play.
- [ ] Repeat Astromancer natural-spell casts and `Runic Boost` across a long combat.
  - Expected: The active sign and four-row rune grid remain readable, and sign cycling is understandable without opening a separate help view.
- [ ] Use the awakened Astromancer Class Ring across active-sign and off-sign rune spends.
  - Expected: Active-sign boosts feel meaningfully stronger without making off-sign rune spending irrelevant.
- [ ] Build `Foresight Threads` as Astromancer through time/divination actions, `Runic Boost`, and `Astral Judgment`.
  - Expected: Astromancer caps at 3 Threads, Diviner does not build Threads in V1, and Threads clear on combat end, flee, save/load, death, or class change.
  - Expected: `Rewind` restores snapshot-safe Thread state and cannot be looped to farm unlimited Threads.
- [ ] Use `Threaded Cast` with a spell and with `Runic Boost`.
  - Expected: The skill requires MP and at least 1 Thread, marks the next eligible spell or `Runic Boost`, spends all Threads before resolution, and improves reliability/rider output only on a valid result.
  - Expected: Misses or fully negated results consume Threads but do not apply a payoff.
- [ ] Use `Twist Fate` and `Threaded Cast` in the same combat.
  - Expected: The effects stack safely without creating guaranteed infinite success loops or bypassing boss, immunity, or Class Ring trial boundaries.
- [ ] Awaken Astromancer `Constellation Cycle`, then use active-sign and off-sign `Threaded Cast`.
  - Expected: Active-sign `Threaded Cast` gains the documented ring reliability/output support only while the awakened ring is equipped.
  - Expected: The ring does not raise the Thread cap or allow manual constellation control.

### Shaman And Soulcatcher Nature Totems
- [ ] Visit Underground Spring, Boulder, Fire Path, and the floor-3 strange-draft passage as Shaman or Soulcatcher.
  - Expected: The player learns `Tsunami`, `Earthquake`, `Fireball`, and `Tornado` respectively, with repeat visits reporting the communion as already bound.
  - Expected: Non-Shaman/Soulcatcher classes receive flavor or navigation text but do not learn the spells.
- [ ] Activate Earth, Water, Fire, and Wind Totems after their matching communions.
  - Expected: End-of-player-turn Totem pulses can cast the highest unlocked matching spell at reduced potency without spending extra mana.
  - Expected: Elemental Totem pulses can defeat enemies.
  - Expected: Pulse cadence feels readable and useful without replacing ordinary spell choices.
- [ ] Equip a Staff, activate a matching elemental Totem, and cast matching nature spells.
  - Expected: Staff increases Totem pulse frequency and strengthens player-cast matching nature spell damage/healing.
  - Expected: Nonmatching active Totems do not strengthen the spell.
  - Expected: Staff support makes Totem builds attractive without feeling mandatory for Shaman/Soulcatcher.
- [ ] Use `Elemental Strike` with each active elemental Totem.
  - Expected: `Elemental Strike` uses the active Totem's element instead of a random element.
- [ ] Activate Water Totem and receive hostile spell damage.
  - Expected: Water Totem increases Magic Defense, absorbs part of incoming spell damage, and heals for the absorbed amount.
  - Expected: Water Totem helps in spell-heavy fights without replacing healing and defensive decisions.
- [ ] Learn `Soul Drain` as Soulcatcher and use it directly and through Soul Totem.
  - Expected: `Soul Drain` deals current-HP percentage damage, cannot kill, and Soul Totem pulses it at reduced potency when Soul aspect is active.
  - Expected: Soul Drain provides useful pressure without trivializing bosses or long fights.
- [ ] Open Totem aspect selection and inspect active Totem HUD/status presentation in pygame combat.
  - Expected: Current aspect, active benefits, and selection state are readable without relying on combat-log memory.
- [ ] Try to find all four elemental communion locations without reading the map data.
  - Expected: The locations are discoverable enough for exploration without becoming quest-log objectives.
- [ ] Visit the Thieves Guild backroom as a member Rogue, Seeker, Ninja, or Arcane Trickster with a dormant Class Ring equipped or stored.
  - Expected: The Gray Broker offers the matching job: `Loaded Game`, `Cartographer's Proof`, `No-Trace Contract`, or `Impossible Theft`.
  - Expected: Completing the job awakens the ring and applies the expected equipped mod.
- [ ] Visit the Thieves Guild backroom for a Footpad-branch job with the Class Ring only in inventory.
  - Expected: The job is available because stored dormant rings are visible to the guild.
- [ ] Visit `Shops` before level 10.
  - Expected: `Thieves Guild` is listed with the other shop destinations, but Mara Vale's counter is closed until level 10.
- [ ] Visit `Shops -> Thieves Guild` as a level 10+ non-Footpad-line character and as a base Footpad.
  - Expected: The public shop is available, but Mara says only: "The wares are for all but the backroom is for a select few."
  - Expected: Keys, Blank Scrolls, Lockpick Kits, Smoke Bombs, and future tool items appear together under one tools tab; spell scrolls and the Oculus do not appear in the Thieves Guild shop.
- [ ] Visit `Shops -> Magic Shop`.
  - Expected: Seraphine Voss appears as the shopkeeper; design notes frame her as a failed academy lecturer turned practical hedge-magus.
  - Expected: Spell scrolls, staves, tomes, rods, musical instruments, and the expensive Oculus appear there; Blank Scrolls do not appear in the spell-scroll tab.
- [ ] Visit `Shops -> Alchemist`.
  - Expected: Health potions, mana potions, and status items are separated into their own tabs.
- [ ] Start Thieves Guild initiation as each promoted Footpad-line branch.
  - Expected: The Gray Broker assigns the correct branch trial and gives an allusive level 2 / north-approach clue without exact coordinates; the fake wall at `15,1,2` and level 2 trial boss at `15,2,2` stay inert and Oculus-hidden before the promoted Footpad-line candidate talks to the Gray Broker.
  - Expected: Winning the matching upgraded Bandit-style boss grants the `Thieves Guild Signet`, which can be turned in for membership.
  - Expected: Members receive 2 Keys, 2 Blank Scrolls, a 25% guild-shop discount, class-specific guidance, and Spell Stealer guidance explains stolen-scroll casting from the combat `Spells` picker.
- [ ] Unlock Warp Point after the Thieves Guild has opened.
  - Expected: The town menu still includes `Warp Point` and `Shops`; the Thieves Guild remains inside `Shops`, and `Old Warehouse` no longer remains solely for guild or Footpad Class Ring access.

### Combat Architecture And Balance
- [x] Dry-run the remaining-improvement balance baseline wrapper.
  - Command: `./.venv/bin/python tools/run_remaining_balance_baseline.py --dry-run`
  - Expected: Timestamped text/JSON summaries list the base, first, second, and race-delta commands plus Footpad, ordinary drop, multi-strike accuracy, and Enfeeble measurement targets.
- [ ] Run and review the full remaining-improvement balance baseline before numeric tuning.
  - Command: `./.venv/bin/python tools/run_remaining_balance_baseline.py`
  - Expected: Reports are written under `reports/balance_baselines/`, local report outputs remain ignored by git, and no balance constants are changed by the report run.
- [ ] Run the base-tier canonical balance report.
  - Command: `./.venv/bin/python tools/run_balance_suite.py --tier base --level 10 --iters 30 --seed 1337`
  - Expected: The report completes, prints class/enemy win-rate rows, and highlights no command/runtime failure unrelated to combat balance.
- [ ] Run the first-promotion canonical balance report.
  - Command: `./.venv/bin/python tools/run_balance_suite.py --tier first --level 20 --iters 30 --seed 1337`
  - Expected: The report completes with invalid race/class and invalid level pairings skipped clearly rather than crashing.
- [ ] Run the second-promotion canonical balance report.
  - Command: `./.venv/bin/python tools/run_balance_suite.py --tier second --level 30 --iters 30 --seed 1337`
  - Expected: The report completes and provides enough signal to identify extreme win rates, stalls, stomps, or repeated draws.
- [ ] Run the race delta balance pass.
  - Command: `./.venv/bin/python tools/run_balance_suite.py --tier all --level 20 --iters 30 --seed 1337 --races Human Elf "Half Elf" "Half Giant" Gnome Dwarf "Half Orc" --delta --baseline-race Human`
  - Expected: Human is used as the baseline, invalid race/class pairings are skipped, and per-race class deltas are readable.
- [ ] Generate a compact combat simulator summary payload.
  - Expected: The payload includes totals, win rates, top abilities, top status effects, and outliers without raw per-battle results.
- [ ] Export a combat simulator balance report to JSON.
  - Expected: The file includes total battles, win rates, ability usage, status frequency, outliers, and raw results.
- [ ] Run a focused combat simulator test after analytics changes.
  - Expected: The quick balance helper returns a report object even when no simulations are configured.
- [ ] Validate enemy item usage after stealing or otherwise removing a combat consumable.
  - Expected: The enemy no longer selects the missing item and falls back to another valid action without crashing or duplicating the item.
- [ ] Inspect start-of-turn status tick defeats.
  - Expected: Poison, DOT, Bleed, or Doom can defeat the active actor before their action, matching the current combat-balance design baseline.
- [ ] Apply Silence to a character with spells, skills, and summons available.
  - Expected: Silence suppresses spells, skills, summons, and ability-like actions according to the current `abilities_suppressed()` behavior.
- [ ] Review the known balance-suite help issue before relying on `--help`.
  - Expected: The argparse `%` help-string failure is treated as a tooling cleanup item, not as a balance-rule failure.

### Class-Kit Balance Thresholds
- [ ] Run focused meter-cadence checks for at least one martial meter, one caster/support meter, and one persistent-progress-backed meter.
  - Expected: Each meter can produce a payoff within three ordinary eligible combats, does not sit capped for most of a fight without spending pressure, and does not rebuild/spend repeatedly without a meaningful action, MP, risk, target, or opportunity-cost tradeoff.
  - Watch: Record matchup, level, gear/loadout, ring state, battle length, status text, combat-log notes, and simulator `class_kit_events` if the meter starves, caps constantly, or loops too freely.
- [ ] Test awakened-ring preservation for at least two tracks with miss, immunity, negated payoff, or target-loss pressure.
  - Expected: Preservation feels like once-per-combat smoothing, not a required baseline engine or a way to erase failed-payoff costs.
  - Watch: Record evidence if preservation feels mandatory, routinely cancels failure costs, or enables same-turn/every-turn payoff loops.
- [ ] Exercise high-action-economy class-kit loops: Totem pulse/`Totem Surge`, song coda/`Encore`, summon or companion actions, Doublecast-adjacent divine support, and route/economy codas where available.
  - Expected: Bonus or autonomous output supports the player's direct action without regularly exceeding it or creating low-interaction wins.
  - Watch: Record simulator `action_economy_events`, combat-log evidence, and manual notes if the player can mostly defend, wait, or repeat one setup action while the loop wins representative encounters.
- [ ] Review compact simulator payloads after class-kit threshold checks.
  - Expected: `class_kit_events` and `action_economy_events` are treated as evidence for investigation, not as automatic tuning failures.
  - Expected: Numeric changes remain blocked until a one-page balance spec promotes the issue from `Watch` or `Tuning Gate`.

### Class-Kit Progression Pacing
- [ ] Master one Troubadour advanced song through clean completions.
  - Expected: Combat-only mastery takes about 3 clean full 3-turn performances, or exploration mastery takes about 3 clean full exploration performances. Composition XP may buffer progress, but 3 clean finishes are still required.
  - Record: song, performance count, combat or exploration route, interruptions, ring state, and whether cadence felt `Pass`, `Watch`, or `Tuning Gate`.
- [ ] Raise a Beast Master companion to at least `Trusted` bond while it remains active.
  - Expected: A new tame starts with a small fresh bond; active living victories create inverse-scaled bond opportunities, so early bond rises visibly while higher bond slows into smaller or less frequent gains. Favored Enemy wins can add an extra smaller opportunity without guaranteeing a flat bump.
  - Record: companion name/species, evolution form, special ability, combat count, companion actions, Favored Enemy state, ring state, roster swaps/tame interruptions, and cadence band.
- [ ] Raise one Thaumaturgist Xenid bond to at least `50` without switching Xenids.
  - Expected: The Xenid is eligible from its first victory. Conduit gain is chance-based from enemy XP divided by a global-player-level span; low-XP fights often give no conduit, while meaningful fights can grant scaled `+1` to `+5`.
  - Record: Xenid name, global level, enemy XP, combat count, successful conduit rolls, no-gain victories, recall/death interruptions, ring state, and cadence band.
- [ ] Raise one Inquisitor or Seeker Case Journal enemy type to at least `Known Tells`.
  - Expected: `Inspect` plus visible-detail victory gives about `+7/combat`, reaching `Known Tells` near 4 focused combats. Rich evidence loops can be faster; victory-only visible-detail progress can be slower.
  - Record: enemy type, combat count, evidence actions, visible-detail state, ring state, spread across other enemy types, and cadence band.
- [ ] Advance one Lycan control gate through the correct stress behavior.
  - Expected: The current gate advances after 3 matching successful stress records. Class Ring state and Dragon Essence should not advance control rank by themselves.
  - Record: starting rank, required behavior, eligible opportunity count, successful records, moon/ring/Dragon Essence state, failures, and cadence band.

### P6 Content And Ability Mechanics
- [ ] Encounter `Giant` and `Owlbear` on dungeon levels 3 and 4.
  - Expected: Giant reads as a Humanoid bruiser with `Stomp` and `Charge`.
  - Expected: Owlbear reads as a Monster with physical pressure, `Shock`, `Wind Speed`, and below-half `Regen` preference.
- [ ] Equip `Tarnhelm` and `Helm of Rostam` in separate medium-helmet tests.
  - Expected: Tarnhelm still grants and removes invisibility on equip/unequip.
  - Expected: Helm of Rostam does not grant invisibility and blocks Berserk/Stun while equipped.
- [ ] Collect and use `Acorn`, `Vine Seed`, `Fungus Spore`, and `Hemlock Root`.
  - Expected: Reagents appear as visible inventory items from their themed drop sources.
  - Expected: `Plant Seeds` offers eligible reagent choices and applies the matching seed effect.
  - Expected: `Vile Potion` consumes Hemlock Root and Fungus Spore, costs user HP, and deals poison pressure.
- [ ] Use Growth-mastery `Tree of Life`.
  - Expected: The user transforms into an oak form for 3 turns, cannot attack, gains defense/status protection, and heals each turn.
- [ ] Exercise P6 passive hooks in ordinary combat.
  - Expected: Zephyrstrike, Retaliate, Defensive Regen, Posturing, Third Eye, Pious Bounty, Final Assault, Last Stand, and polearm/Monkey Grip penalties or bonuses match their class descriptions.
- [ ] Use Footpad stealth skills against valid and invalid targets.
  - Expected: Kidney Punch costs exactly 18 MP and never leaves the caster below 0 MP.
  - Expected: Backstab is hidden from the skill list unless the target is incapacitated.
- [ ] Use Ranger `Tame` and `Favored Enemy`.
  - Expected: Tame works only on eligible wounded Animal enemies, saves a compact held roster, starts new species with a small fresh bond, assigns a species-flavored special ability, makes the new tame active while roster space remains, and ends the fight without EXP, gold, loot, kill credit, or extra victory bond.
  - Expected: Retaming an already held species strengthens that bond and switches it active; a full roster blocks new species with release-required messaging instead of silently replacing an older companion.
  - Expected: Successful tame skips enemy attack/death/fade animations, shows combat resolution first, then opens a dungeon-background companion naming screen with a confirmation step. Blank/cancel keeps the original animal name; nicknames display as `Nickname (Enemy Name)`.
  - Expected: Bond growth updates the species-family evolution form and the `Companion & Hunt` tab shows bond, form, special ability, held count, and Favored Enemy without exposing hidden formulas or `Promotion Tier`.
  - Expected: Before the first tame, the `Companion & Hunt` tab shows empty held-companion slots instead of a blank panel.
  - Expected: In the `Companion & Hunt` tab selector, `S` makes the selected tamed companion lead and `R` asks for confirmation before releasing the selected tamed companion.
  - Expected: Favored Enemy is a combat skill that marks the current enemy type as quarry, persists beyond combat, grows with disciplined repeated hunts, gives up most practice when switching to a different quarry, and emits only a general combat-log note when its bonus contributes.
- [ ] Use Beast Master `Companion` combat commands.
  - Expected: Ranger companion actions remain subtle automated log events with bond-scaled frequency, while Beast Master gains a top-level `Companion` action when a living tamed companion is active.
  - Expected: `Companion` opens `Pack Strike`, `Guard Partner`, `Harry Prey`, and `Mend Wounds`; the command consumes the player action, appears as pending in HUD/status, resolves on the companion action, and clears afterward.
  - Expected: Low-bond commands still produce a weaker useful result; higher bond improves damage, guard, debuff, or healing strength without granting extra companion turns.
- [ ] Use `Steal As Well` and `Steal Spell 2`.
  - Expected: Steal As Well lets Spell Stealer cast a damaging spell and then attempts item theft only on damaging results.
  - Expected: Steal Spell 2 can permanently learn an eligible enemy spell without consuming a Blank Scroll.
- [ ] Validate Astromancer time spells and exploration effects.
  - Expected: Foretell reveals the next enemy action, Twist Fate guarantees the next action success, Rewind restores the prior selection-phase snapshot, and Wormhole resolves a delayed spell.
  - Expected: Volitation, Enter Wall, and Invisibility persist through temporary exploration-effect state and expire cleanly.
- [ ] Compose and use advanced Bard/Troubadour sheet music.
  - Expected: Sheet music is one-use, requires the intended instrument/composition condition, and starts the matching combat or exploration song effect.
  - Expected: Battle Hymn berserks combatants, Ode to the Ramparts boosts defenses, exploration debuff songs affect enemies while active, encounter/loot songs apply their route hooks, and Chorus Time can consume enemy turns.
- [ ] Use current second-promotion power-up hooks.
  - Expected: Trickster's Gambit, Primal Ascendance, Abyssal Covenant, Arsenal Mastery, Shield Mastery, Eternal Conduit, Melody of Inspiration, and Pack Bond produce visible gameplay/status changes without stale placeholder messages.

### Class-Kit UI/Log Polish
- [ ] Inspect shared class/status text for one martial meter track, such as Berserker, Dragoon, Stalwart Defender, Ninja, or Master Monk.
  - Expected: Current meter value, cap, pending payoff or stance, and awakened/equipped Class Ring readiness appear without duplicate or stale labels.
- [ ] Inspect shared class/status text for one caster or support meter track, such as Astromancer, Shadowcaster, Templar, Archbishop, Archdruid, or Soulcatcher.
  - Expected: Current meter/resource value, cap or represented state, pending payoff, and ring readiness/preservation state are readable in the same status surface.
- [ ] Inspect a persistent-progress class track, such as Demonologist, Thaumaturgist, Seeker, Troubadour, Lycan, or Beast Master.
  - Expected: Persistent progress rank/value and relevant temporary combat state appear together without implying new progression, rewards, or tuning.
- [ ] Trigger representative class-kit combat messages for gain, cap, spend, miss/negated payoff, expiration/cleanup, and ring preservation.
  - Expected: Pygame and curses combat logs keep the class-kit message visible, wrap long lines cleanly, and do not suppress important failure, immunity, downgrade, or preservation text as generic status noise.
- [ ] Inspect one menu/exploration-adjacent class-kit surface, such as Demonologist contracts, Seeker `Hidden Cache`, Troubadour composition/repertoire, Lycan `Dismiss Form`, Beast Master tame/command, or Soulcatcher Totem aspects.
  - Expected: The surface explains current availability and failure state clearly without changing quest gates, save state, combat rules, or numeric balance.
- [ ] Inspect compact class-kit hints across all promotion tracks in Combat Focus and character status.
  - Expected: Meter rows keep current value/cap visible and add only short readiness hints such as `Ready`, `Building`, `Pending`, `Primed`, `Needs level 2`, or equivalent compact wording.
  - Expected: Pygame coin meters for Fortune/Misfortune still render as coins even when the backing value includes a compact hint.
- [ ] Defeat ordinary loot-bearing enemies as Thief/Rogue after the readability pass.
  - Expected: Existing ordinary eligible drops remain unchanged mechanically, but `Scavenger's Eye` or `Finders Keepers` makes the class loot identity visible in the combat log when such loot appears.
- [ ] Win with an active level-1 summon and then with an active level-2+ summon.
  - Expected: Level-1 victories explain that summon bond needs level 2; level-2+ low-XP/no-roll victories can report that bond held steady; successful gains still report the amount and current bond.

### Legacy Class-Kit Mechanics

Implementation update (2026-09-03): Devotion and Prayer now use authored
action/hostile-action boundaries, and their ward, support, power-up, and ring
payoffs are implemented. The checks below remain manual playtest rows rather
than claims of completed play evidence. See `CLASS_KIT_DESIGN_GATES.md` for the
automated implementation boundary.

- [ ] Build `Devotion` as Cleric through healing, Holy pressure, shield actions, and `Turn Undead`.
  - Expected: Cleric caps at 3 stacks, gains only after the enemy survives the
    action resolution, and clears Devotion on combat end, flee, save/load,
    death, or class change.
  - Expected: Held Devotion provides light incoming-damage reduction, creating a visible hold-versus-spend choice.
  - Expected: `Pious Bounty` remains a modest reward accent, still does not
    appear on Priest, and `Turn Undead` kills can mark bounty gold without
    granting Devotion from the lethal action.
- [ ] Spend Devotion with `Sanctuary Ward` as Cleric, Templar, or Hierophant.
  - Expected: Cleric receives the skill immediately on promotion; it requires MP and at least 1 Devotion, spends all stacks, and applies a stronger barrier/mitigation pulse at higher stacks.
  - Expected: `Sanctuary Ward` is hidden from the combat Skills picker until at
    least 1 Devotion has been built.
  - Expected: The cleanse/Regen rider remains conservative and logs clearly when it triggers.
- [ ] Spend Devotion with `Relic Aegis` as Templar.
- [ ] Spend Devotion with `Consecrated Conduit` as Hierophant, then land a staff, Smite, or Holy payoff.
  - Expected: The skill requires MP, at least 1 Devotion, and a staff.
  - Expected: It spends all stacks to empower the next staff, Smite, or Holy payoff with bonus holy damage, modest warding, and small mana return.
- [ ] Use `Holy Retribution` and awakened `Ordered Blessings` with Devotion.
  - Expected: `Holy Retribution` keeps its holy-fire attack window while improving Devotion gain from holy/shield actions once per round.
  - Expected: `Ordered Blessings` keeps the Regen/Defense/Holy Damage rotation and preserves 1 Devotion once per combat after a clean matching payoff.
- [ ] Build `Prayer` as Priest through meaningful healing, cleansing, divine support, Holy pressure, and anti-magic setup.
  - Expected: Priest caps at 4 stacks, gains at most once per player action, and clears Prayer on combat end, flee, save/load, death, or class change.
  - Expected: Tiny regeneration ticks and passive housekeeping do not self-feed Prayer.
- [ ] Spend Prayer with `Supplication` as Priest or Archbishop.
  - Expected: The skill requires MP and at least 1 Prayer, spends all stacks, and applies a conservative support pulse with healing, protection, and a small cleanse chance.
- [ ] Spend Prayer with `Great Benediction` as Archbishop.
  - Expected: The skill requires higher MP and at least 3 Prayer, spends all stacks, and applies several turns of improved healing, protection, status resistance, and modest MP sustain.
- [ ] Use `Doublecast`, `Great Gospel`, and awakened `Divine Intervention` with Prayer.
  - Expected: `Doublecast` can grant Prayer at most once for the whole action.
  - Expected: `Great Gospel` keeps its cleanse/power-up identity, immediately sets Prayer to at least half cap, and improves Prayer gain from divine support once per round.
  - Expected: `Divine Intervention` keeps its once-per-combat 35% emergency heal and preserves 1 Prayer once per combat after a clean Supplication or Benediction payoff.
- [ ] Win ordinary non-trial combat as a Berserker at 10% HP or lower across repeated attempts.
  - Expected: `Battle Scars` can increase, caps at 20, raises max HP, and appears in character/ring status text.
  - Expected: Below 25% HP, weapon damage increases from scars and stacks with awakened `Bloodied Crits`.

Audit correction (2026-09-03): the Footpad branch entries below are now shipped
acceptance checks. Internal progression and proc formulas remain intentionally
absent from player-facing explanations.

- [ ] Defeat ordinary loot-bearing enemies as Thief with `Scavenger's Eye`.
  - Expected: Enemy loot drop rate and eligible rarity outcomes feel modestly improved without creating quest, special, unique, ultimate, or invalid class/summon-gated drops.
- [ ] Defeat ordinary loot-bearing enemies as Rogue with `Finders Keepers`.
  - Expected: Occasional extra unlisted eligible loot can be found from normal loot tables.
  - Expected: Quest, special, unique, ultimate, invalid class-restricted, and invalid summon-gated items are excluded.
- [ ] Build `Fortune` and `Misfortune` as Thief and Rogue through meaningful combat rolls.
  - Expected: Successful meaningful attacks, defenses, theft/luck skills, crits, and major status attempts can build Fortune.
  - Expected: Failed meaningful rolls, missed risky actions, poor `Slot Machine` outcomes, or failed theft/status attempts can build Misfortune.
  - Expected: Tiny status ticks and passive housekeeping rolls do not change either meter.
- [ ] Spend Fortune and Misfortune with representative risky actions.
  - Expected: Fortune improves odds/reliability for `Steal`, `Mug`, `Sneak Attack`, `Gold Toss`, `Slot Machine`, and major status attempts.
  - Expected: Misfortune does not improve pre-roll odds, but increases severity/scale after a successful risky action.
  - Expected: Both meters clear on combat end, flee, save/load, death, or class change.
- [ ] Use `Slot Machine` with Fortune and Misfortune available.
  - Expected: Fortune can soften or reroll worst failure-style outcomes without forcing jackpots.
  - Expected: Misfortune can scale successful outcomes without upgrading them directly into jackpots.
- [ ] Take fatal damage as Rogue with `Cheat Death` available.
  - Expected: Once per combat, fatal damage triggers a Misfortune-boosted Luck check.
  - Expected: On success, the Rogue survives at 1 HP, spends all Misfortune, and gains a temporary `Jinx`/Misfortune-style debuff.
  - Expected: On failure, fatal damage resolves normally.
- [ ] Awaken Rogue `Loaded Dice`, then spend Fortune or Misfortune with the ring equipped.
  - Expected: `Loaded Dice` still gives failed luck checks a 15% chance to become successes.
  - Expected: Once per combat after a clean Fortune or Misfortune payoff, the ring preserves 1 point of the spent meter.
- [ ] Promote Footpad into Inquisitor after learning stealth skills.
  - Expected: Every learned stealth/toolkit ability remains available; only unpurchased Footpad nodes and competing promotions close.
- [ ] Build `Case Journal` progress as Inquisitor or Seeker against several enemy types.
  - Expected: `Inspect`, successful `Exploit Weakness`, visible telegraph reads, and victory with visible enemy details add progress to the broad enemy type.
  - Expected: Progress clamps from 0 to 100 and reports milestone ranks: `Known Tells`, `Weakness Brief`, `Pattern Lock`, and `Closed Case`.
- [ ] Build and spend `Revelation` in combat.
  - Expected: Inquisitor caps at 2 stacks and Seeker caps at 3 stacks.
  - Expected: `Inspect`, `Exploit Weakness`, visible telegraph reads, and anti-magic/setup actions can add stacks.
  - Expected: `Exploit Weakness`, standard weapon hits, and weapon-tagged precision skills spend stacks for reliability/control pressure; misses consume stacks without applying riders.
- [ ] Test studied-type bonuses at each Case Journal milestone.
  - Expected: Studied targets improve first-Inspect Revelation, `Exploit Weakness` reliability, telegraph prediction, and Seeker movement-tool smoothing at the documented thresholds.
  - Expected: Boss and Class Ring trial restrictions are not bypassed.
- [ ] Awaken Seeker `Hidden Cache`, map a level, and use insight tools with the ring equipped.
  - Expected: Existing one-per-depth cache behavior and `claimed_caches` compatibility remain intact.
  - Expected: The ring adds only small insight smoothing after clean `Inspect` or telegraph reads and slightly improves `Wayfinding`.
- [ ] Apply `Death Mark` as Assassin through valid setup actions.
  - Expected: `Backstab`, `Sneak Attack`, `Momentum`, `Kidney Punch`, `Disembowel`, and `Marked Shuriken` add one mark when at least one hit lands and one additional mark after a successful native status or nonimmune coating reaction.
  - Expected: Assassin caps at 1 mark and marks clear on combat end, flee, save/load, target death, or class change.
- [ ] Spend `Death Mark` as Assassin with eligible finishers.
  - Expected: `Deathblow` requires at least one mark, spends all marks on a validated attempt, and gains damage, accuracy, and critical chance per mark.
- [ ] Apply and spend `Death Mark` as Ninja.
  - Expected: Ninja caps at 3 marks; only `Deathblow`, `Thousand Cuts`, and `Death Sentence` are dedicated finishers, and each spends all marks on the attempt.
  - Expected: `Desoul` remains independent of the Ninja tree but shares Death resistance rules with `Death Sentence`; full resistance and bosses are immune.
- [ ] Awaken Ninja `No-Trace Opener`, then start combat with initiative and the ring equipped.
  - Expected: The first standard Ninja Blade attack applies one mark before its roll, spends all marks, and doubles base damage even though the internal legacy state keys remain compatible.
  - Expected: A miss still spends the marks; a successful payoff against a surviving target preserves one mark once per combat.
- [ ] Visit the Alchemist and scroll loot sources after the `Blank Scroll` addition.
  - Expected: `Blank Scroll` can be acquired as a concrete scroll item and round-trips through save/load.
- [ ] Use `Steal Spell` as a Spell Stealer or Arcane Trickster with and without a `Blank Scroll`.
  - Expected: Without a blank scroll, the skill fails clearly.
  - Expected: On success, one `Blank Scroll` is consumed and a usable `Stolen <Spell> Scroll` appears in inventory.
  - Expected: Class Ring trial enemies cannot have spells stolen.
- [ ] Use a stolen-spell scroll in combat.
  - Expected: It appears in the `Spells` picker with scroll labeling, uses the
    saved stolen spell identity, decrements charges, and persists after
    save/load.
- [ ] Build `Stolen Charge` as Spell Stealer and Arcane Trickster.
  - Expected: Successful `Steal Spell`, successful `Steal Spell 2`, and casting an inscribed stolen-spell scroll each grant 1 Charge, capped at 2 for Spell Stealer and 3 for Arcane Trickster.
  - Expected: Item theft from `Steal As Well` does not independently grant Charge.
- [ ] Spend `Stolen Charge` with representative spell, weapon, and weapon-tagged trickster actions.
  - Expected: The next validated eligible attempt commits all Charge and a successful action adds one aggregate typed Arcane payoff.
  - Expected: Misses or fully negated actions consume the commitment without applying the payoff.
- [ ] End combat, flee, save/load, or change class with `Stolen Charge` active.
  - Expected: Charge clears because it is combat-only and has no persistent save field.
- [ ] Complete `Impossible Theft`, then successfully steal a spell as Arcane Trickster with the awakened ring equipped.
  - Expected: `Arcane Larceny` displays as the awakened identity while legacy `Spell Steal Buff` behavior still grants temporary Magic damage and dodge bonuses for 3 turns.
  - Expected: Once per combat after a clean charged payoff, the equipped awakened ring preserves 1 `Stolen Charge`.
- [ ] Use `Song of Valor`, `Song of Shelter`, and `Song of Renewal` as Bard/Troubadour.
  - Expected: Songs require an equipped musical instrument in `OffHand`.
  - Expected: Only one song is active at a time, lasts 3 turns, and appears in character/ring status text.
  - Expected: Valor increases weapon/magic damage, Shelter reduces incoming damage, and Renewal pulses HP/MP recovery.
- [ ] Awaken Troubadour `Encore`, then let each song expire.
  - Expected: Troubadour song strength is higher than Bard baseline.
  - Expected: Encore adds one final weaker pulse or beat when a song expires.
- [ ] Walk dungeon steps as Lycan.
  - Expected: Moon phase advances every 120 dungeon steps through New, Waxing, Full, and Waning.
  - Expected: Moon phase and Frenzy Lock state appear in character/ring status text.
- [ ] Fight while transformed as Lycan across moon phases.
  - Expected: Kills or low HP can trigger Frenzy Lock, with Full Moon feeling riskiest.
  - Expected: Awakened `Controlled Frenzy` improves healing received while locked.
- [ ] Defeat the Red Dragon as Lycan after the Transform4 retirement.
  - Expected: The Red Dragon no longer grants or auto-casts Red Dragon `Transform`.
  - Expected: The Lycan state records Dragon Essence for the future werewolf enhancement route.
- [ ] Build Archdruid `Aspect Harmony` from Venom, Stone, Growth, and Storm actions.
  - Expected: Poison pressure, physical survival/mitigation, meaningful healing or `Tree of Life`, and Electric/Wind pressure each represent the matching aspect.
  - Expected: Aspect Harmony is combat-only and clears on combat end, flee, save/load, death, or class change.
- [ ] Spend Aspect Harmony with `Fourfold Surge`.
  - Expected: The skill requires MP and at least two represented aspects, spends all represented aspects, and rewards distinct aspect coverage more than repeated single-aspect actions.
  - Expected: Venom/Stone/Growth/Storm riders apply conservatively and downgrade cleanly around immunity, bosses, and Class Ring trials.
- [ ] Use `Primal Ascendance`, `Tree of Life`, and awakened `Harmony Bonus` with Aspect Harmony.
  - Expected: Primal Ascendance improves Harmony gain/riders without replacing its existing power-up identity.
  - Expected: Tree of Life contributes Growth Harmony lightly.
  - Expected: The awakened ring keeps total-attunement Harmony Bonus behavior and preserves one represented aspect once per combat after a clean `Fourfold Surge`.
- [ ] Use Defend and take physical pressure as Stalwart Defender with awakened ring.
  - Expected: Resolve/Guard Meter builds to 100 and appears in status text.
  - Expected: A major incoming hit spends 100 Resolve to reduce damage by 40%.
- [ ] Call Xenids before and after awakening Thaumaturgist `Conduit Ritual`.
  - Expected: Future summons initialize with the awakened +30% HP and attack/magic scaling.
- [ ] Summon Patagon and Kobalos in pygame combat.
  - Expected: Summons spend MP when called; Kobalos also spends gold and refuses
    to appear if the Thaumaturgist lacks the fee.
  - Expected: Active summon action log lines use a distinct color from player
    and enemy log lines.
- [ ] Use `Support` while a summon creature is active.
  - Expected: The Xenid remains the single active actor, but `Support` lets the Thaumaturgist spend the turn on restorative/support items, `Recall`, `Heal Summon`, `Raise Summon`, `Conduit Command`, or unlocked `Invoke <Xenid>` skills.
  - Expected: Direct Thaumaturgist attacks, ordinary offensive spells, ordinary offensive skills, fleeing, and starting another Xenid are not available through `Support`.
- [ ] Let an active Xenid die, then use `Raise Summon` during the same combat.
  - Expected: Death removes 25 conduit. Raise costs 100 MP, returns only that
    just-fallen active Xenid at 25% HP, and restores 10 of the lost conduit.
    Other dead Xenids remain dead, and Raise is unavailable outside combat or
    after another Xenid is called.
- [ ] Cast each Thaumaturgist Miracle with and without a Reality Fragment.
  - Expected: Missing reagent prevents the cast without spending MP. A valid
    cast consumes exactly one fragment. Miracle Blade bypasses protection;
    Miracle Shackles cannot be escaped before its three turns; Miracle Potion
    creates one Master Health and one Master Mana potion; Miracle Crystal does
    not siphon player MP and bursts against every living enemy after four turns.
- [ ] Defeat a boss with an eligible level 2+ active summon alive.
  - Expected: Boss victory guarantees summon bond gain and awards double the
    normal scaled gain, capped by the 100 bond maximum.
- [ ] Fight with Dilong and use `Tunnel`, then `Surface`.
  - Expected: Dilong starts with usable Magic and Magic Defense, `Tremor` can contribute, `Tunnel` hides normal offense, and the tunneled action list only allows surfacing or recalling.
- [ ] Fight as Soulcatcher and defeat distinct enemy types with awakened ring.
  - Expected: Distinct harvested type count increases and appears in status text.
- [ ] Heal a Beast Master with awakened `Shared Recovery` while a familiar/companion is present.
  - Expected: The companion receives a 25% echo of actual healing without recursive extra healing.
- [ ] Fight with a bonded tamed companion at `Trusted Form` or above.
  - Expected: The companion keeps its single automatic action, but its named special ability can add a small readable rider such as `Pounce`, `Guard Hide`, `Wingbeat`, `Primal Spark`, or `Keen Scent`.

### Dungeon Rendering
- [ ] Enter upper, middle, and deep dungeon levels.
  - Expected: Walls, floors, and ceilings use the new painterly dungeon materials and deeper areas feel darker, more broken, or more overgrown.
- [x] Inspect the dungeon HUD location label across ordinary levels, Realm of Cambion, and Liminal Gap.
  - Expected: The HUD shows `Dungeon Level N`, `Realm of Cambion`, or `Liminal Gap` without crowding resource bars, compass, minimap, or combat focus panels.
- [ ] Summon a creature during pygame combat and inspect the right-side HUD.
  - Expected: Combat Focus shows the active summon name, level, XP bar, HP bar, MP bar, and any active summon status icons.
  - Expected: Recalling, losing, or ending the summon removes the summon Combat Focus resource readout without shifting the panel into the action area.
  - Expected: Combat Focus does not show passive `Class`, known `Summons`, or persistent `Summon Bond` rows while class/details screens still show summon bond progress.
- [ ] Enter pygame combat with no active focus mechanics.
  - Expected: Combat Focus shows a no-active-focus message instead of passive class or roster summaries.
- [ ] Step onto a tile with special location text such as a class/aspect presence.
  - Expected: The location text appears in a popup before tile damage/combat effects so it cannot be missed in the scrolling log.
- [ ] Open the Character Menu and press `C`.
  - Expected: `C` does not jump between tabs. Open the Class tab normally, then press `C` to toggle summon row selection; arrows move between summons, `Enter` opens the details popup, and `Esc` leaves row selection before closing the menu.
- [ ] Trigger several pygame random encounters.
  - Expected: The first actionable combat frame appears quickly without the old start delay; ordinary post-turn pauses are shorter while damage, death, popup, and special transition animations remain readable.
- [x] Open the enlarged minimap modal with `M` and by clicking the minimap.
  - Expected: The modal reuses existing discovered/visible tile rules, frames the fully revealed current level instead of only the small HUD viewport, and closes with `M`, `Esc`, or outside click.
- [x] Navigate the pygame dungeon at or below 25% HP.
  - Expected: A persistent red edge cue appears in the dungeon viewport without tinting the right-side HUD or changing movement, encounters, damage, healing, or death behavior.
- [ ] Move near decorative rubble, roots, fungus, crystal clusters, bone piles, and broken gear in a test map or authored fixture.
  - Expected: Decorative props render as floor-bound hooks and remain traversable unless future gameplay explicitly changes them.
- [ ] Revisit a defeated encounter body in the dungeon view.
  - Expected: The body renders floor-bound, lower in the scene, and smaller than large blocking props.
- [ ] Inspect root and fungus floor variants in a dungeon test map.
  - Expected: Roots and fungus look embedded into the floor texture, with no flat sticker edges, chroma artifacts, or obvious rectangular backgrounds.
- [ ] Inspect transparent root/fungus overlay sprites on ordinary dungeon floor tiles.
  - Expected: Overlay sprites have transparent backgrounds, muted colors, and soft contact shadows without visible green/chroma fringes.
- [ ] Face ordinary walls across multiple floors.
  - Expected: Torch/sconce overlays appear occasionally, with cleaner lit fixtures high in the dungeon and more broken/unlit fixtures deeper down.
- [ ] Face undiscovered Fake Walls/Fake Paths across multiple floors.
  - Expected: Wall torch/sconce overlays do not render on fake walls before discovery.
- [x] Enter and walk along funhouse boundaries.
  - Expected: Exterior funhouse boundaries use the funhouse boundary wall material at side depths and remain impassable.
- [ ] Enter a dungeon room with side doors or detected Ore Vault doors.
  - Expected: Door/wall surface-slot states render consistently without stale slot overrides from a previous view.
- [x] Face a blocking center wall while one side corridor or side opening remains visible.
  - Expected: The center wall remains the dominant forward face, while the visible side opening still shows its side wall, door, corridor face, or floor/ceiling lane cue.
- [x] Face an unvisited FakeWall/Fake Path from the dungeon view.
  - Expected: The fake path is not visually revealed and renders like an ordinary wall until discovered; `Keen Eye` or a carried `Oculus` can surface the suspicious-wall text nearby.
- [x] Step through or revisit a discovered FakeWall/Fake Path.
  - Expected: The revealed fake path behaves like an open passage and shows a translucent normal wall panel rather than a tiny wall sprite or unrelated marker.
- [x] Revisit a room after moving through side corridors and backtracking.
  - Expected: Floor, ceiling, and wall textures return to the room's actual tile state instead of showing debug or stale override textures.
- [ ] Run renderer diagnostics after moving through several dungeon views.
  - Expected: Projected-surface cache diagnostics report bounded cache size, remaining capacity, and full/not-full state.
- [ ] Run asset fallback diagnostics with a missing or renamed test asset.
  - Expected: Fallback counts identify the affected asset category without changing dungeon rendering.
  - Expected: Fallback key lists identify the affected texture, special-tile, or enemy asset names by category.
- [ ] Run renderer diagnostics with all shipped dungeon assets present.
  - Expected: Texture, special-tile, and manifest fallback counts remain zero for shipped dungeon-render assets.
- [x] Review active and inactive Warp Point dungeon art.
  - Expected: `src/ui_pygame/assets/dungeon_tiles/special_tiles/warp_point_art_review_sheet.png` shows both approved variants.
  - Expected: Active Warp Points use the active platform plus existing spark overlay; inactive/spent Warp Points use the dim platform; missing approved art falls back to the readable legacy teleporter.
- [ ] Inspect aggregate texture diagnostics after entering and leaving several rooms.
  - Expected: Loaded state, fallback counts/totals, cache size/limit/capacity, and override counts are visible in one diagnostic payload.

### Combat Status Icons
- [x] Use Defend in pygame combat.
  - Expected: The `DEF` status icon is green/positive.
  - Expected: `DEF` falls off after one turn unless Defend is selected again.
- [x] Trigger or simulate Blind Rage in combat.
  - Expected: The status row shows a distinct `BRG` icon.
  - Expected: `BRG` is prioritized with other urgent negative combat states before overflow.
- [ ] Trigger or simulate the newly wired effect artwork in pygame combat.
  - Expected: Astral Shift, Ice Block, Mana Shield, Mirror Image, Speed up/down, and generic/burn/poison/bleed DOT states use PNG icons instead of text-only fallback pills.
  - Expected: Spell Reflect uses the magic reflect icon, while Totem's melee-reflect secondary uses the melee reflect icon.
- [ ] Stack repeated status effects alongside several other combat states.
  - Expected: Counted status icons keep urgent effects visible first and use stable ordering instead of flickering between turns.
- [ ] Build Evasive Guard stacks as a Footpad-line character in pygame combat.
  - Expected: The combat status row shows an `EG#` stack indicator using the approved Evasive Guard PNG.
  - Expected: Evasive Guard stacks reset after a successful dodge.
- [ ] Resize the game window or view a crowded combat overlay.
  - Expected: Status icon labels remain clipped to the icon pill instead of spilling into neighboring UI.
- [ ] Inspect combat status layout diagnostics with many active effects.
  - Expected: Visible, hidden, overflow, urgent-visible, capacity, and row counts match the status row shown on screen.
  - Expected: Overflow state and hidden urgent-status count make it clear whether high-priority effects were hidden.
  - Expected: Positive, negative, and neutral visible/hidden counts match the rendered icon mix.
  - Expected: Visible/hidden label lists identify exactly which status pills were shown or compacted.
  - Expected: Stat-effect icon filtering diagnostics identify active zero-value effects that were suppressed before rendering.

### Combat Visual Polish
- [x] Land a normal weapon hit against an enemy in pygame combat.
  - Expected: The enemy sprite briefly flashes and shows a subdued warm slash/spark impact over the current enemy artwork.
  - Expected: The effect fades quickly and does not cover the enemy HP bar, action menu, or combat log.
- [x] Cast elemental attack spells such as fire, ice, or lightning against an enemy.
  - Expected: Confirmed spell damage produces a soft elemental glow/ray effect using the matching element color family.
  - Expected: The effect appears over the existing dungeon-backed combat scene without replacing enemy sprites or portraits.
  - Expected: The spell selector is no longer covering the enemy when the spell effect plays.
  - Expected: Spell selection uses a bottom combat command panel rather than a centered full-screen combat modal.
- [x] Open spell, skill, item, and totem selections during combat.
  - Expected: Each selection panel stays in the bottom command area and leaves the enemy sprite, HP bar, telegraph banner, and target details visible.
  - Expected: Long lists scroll within the compact panel and keep the selected row visible.
- [x] Use a damaging combat skill against an enemy.
  - Expected: Confirmed skill damage produces a compact ring/burst effect distinct from normal weapon slashes and spell glows.
- [ ] Trigger confirmed reflected damage in pygame combat.
  - Expected: Reflection and Magic Reflect damage use a shield/ripple impact cue instead of an ordinary weapon slash.
  - Expected: The cue appears only when HP changes and does not replace combat log or status icon updates.
- [ ] Trigger a damaging Stun or Prone application in pygame combat.
  - Expected: Confirmed hard-control hits show a compact status accent near the affected combatant.
  - Expected: Missed, resisted, or non-damaging control attempts do not play hit particles.
- [ ] Land a non-spell elemental weapon strike in pygame combat.
  - Expected: Confirmed elemental weapon damage layers the element color over the standard slash effect.
  - Expected: Pure spell damage still uses the existing spell glow/ray effect.
- [x] Take damage from an enemy attack or spell.
  - Expected: The player-side damage flash remains readable while the short impact effect appears near the player/status area.
  - Expected: Combat log scrolling and quit handling remain responsive during the flash.
- [x] Miss, get resisted, or use a non-damaging action in combat.
  - Expected: No hit/spell particle effect plays when HP does not change.
  - Expected: Existing combat messages, telegraph banners, and status icons still update normally.
- [x] Trigger long combat log messages, including telegraphs and multi-clause spell/skill results.
  - Expected: Long messages wrap within the combat log panel instead of running off-screen.
  - Expected: Wrapped continuation lines keep the same message color and indent slightly under the source line.
  - Expected: PgUp/PgDn and mouse-wheel scrolling move through wrapped visible lines predictably.
- [x] Review mixed combat log outcomes such as damage, healing/regeneration, resisted effects, and telegraphs.
  - Expected: Telegraphs remain gold, damage/bleed lines use a restrained red, healing/regeneration lines use green, and misses/resists use muted gray.
- [x] Review combat log readability during a fight with mixed outcomes.
  - Expected: Each source message has a subtle left-edge category tick, and wrapped continuation lines use a muted continuation tick.
- [x] Trigger an enemy telegraph such as Jump, Charge, or Dragon Breath.
  - Expected: The incoming-action banner appears as a compact warning strip near the enemy combat area and does not cover the action panel or combat log.
  - Expected: A charging enemy continues or resolves the charged ability on its next turns instead of taking unrelated attacks.
- [ ] Trigger Dragon Breath against a character with active Mana Shield.
  - Expected: Mana Shield absorbs Dragon Breath damage before elemental reduction or HP loss; absorbed breaths spend mana and report the shield absorption.
- [x] Use Jump, then become stunned before Jump resolves.
  - Expected: Non-Unstoppable Jump is cancelled by stun instead of waiting to resolve after stun ends.
- [x] Use Jump without Quick Dive.
  - Expected: The initial charge turn logs only the charging telegraph, not a separate `uses Jump` line.
- [x] Use player Jump or another player telegraph in combat.
  - Expected: Player telegraphs stay in the log/status row and do not appear as the enemy-area `Incoming` banner.
- [x] Let stun, sleep, or prone expire at the start of an actor turn.
  - Expected: The log shows the recovery message without also printing stale incapacitation text.
- [x] Get stunned by an enemy effect in pygame combat.
  - Expected: The combat log prints a clear stun message if the underlying effect did not already include one.
- [x] Land or receive damage in pygame combat.
  - Expected: The damage result is visible in the combat log before the hit flash/impact animation begins.
  - Expected: Spell damage follows the same result-before-impact timing as melee damage.
  - Expected: Confirmed damage shows compact floating damage text near the target and the enemy briefly recoils on enemy-side hits.
- [x] Receive healing or regeneration during pygame combat.
  - Expected: Confirmed HP recovery shows compact floating healing text near the healed combatant without playing a hit flash.
- [x] Drop the player to low health in pygame combat.
  - Expected: A restrained red danger vignette appears around the combat area at low HP without covering the action menu, combat log, or enemy sprite.
- [x] Take bleed damage at start of turn.
  - Expected: Physical bleed damage is described as the character bleeding, not as generic magic damage.
- [x] Navigate the bottom action panel in combat.
  - Expected: The panel uses the darker stone/parchment treatment with a clearer selected-action border while preserving compact grid behavior.
- [x] Enter combat with more than six available actions, such as debug actions plus item/spell/skill options.
  - Expected: The action menu compacts into the bottom command panel without overflowing below the screen.
  - Expected: Long action labels are truncated inside their cells instead of overlapping neighboring actions.
- [x] Set `DUNGEON_FORCE_ENEMY=Test` before running `launch_gui_debug.sh`, or uncomment the matching line in the script during an ability debug run.
  - Expected: Random encounters use the requested debug enemy only while the environment variable is active, then return to normal catalog selection.
- [x] Trigger random encounters while an active defeat, collection, or bounty quest target exists in the current floor catalog.
  - Expected: The helper can softly prefer matching active quest enemies, ignores completed/turned-in targets, falls back on soft-roll failure, and still lets debug overrides win.
- [ ] Use `src.core.enemies.set_random_enemy_override("Test")` from a Python harness, then call
  `src.core.enemies.clear_random_enemy_override()`.
  - Expected: The explicit helper still forces targeted encounters and takes precedence over the environment variable when both are set.
- [x] Inspect enemy details with Vision, Reveal, Seeker, or Inquisitor sight during a boss fight.
  - Expected: Boss fights suppress enemy detail visibility even when ordinary encounters would reveal HP, type, or resistance details.

### Enemy Combat Sprites
- [x] Enter combat against early enemies such as Giant Rat, Skeleton, Goblin, and Slime.
  - Expected: The center combat enemy is a transparent full-body sprite, not a rectangular portrait or token.
  - Expected: Existing HP bars, menus, targeting, turn order, and combat mechanics are unchanged.
- [x] Enter combat against mid-game enemies such as Gnoll, Satyr, Vampire, Troll, and Dragonkin.
  - Expected: Enemy weapons/body shapes match their current enemy definitions closely enough for combat readability.
  - Expected: Sprites preserve aspect ratio and do not cover the enemy HP bar or action menu.
- [x] Enter combat against late-game or boss enemies such as Beholder, Hydra, Red Dragon, Cerberus, and The Devil.
  - Expected: Large enemies use `enemy_combat_sprite_scale.json` for intentional size differences while remaining centered and readable.
  - Expected: If a sprite is missing or fails to load, combat falls back gracefully without crashing.

### Main Menu
- [ ] Complete pygame New Game character creation.
  - Expected: The Character Created presentation screen shows the chosen portrait, name, race, sex, class, HP, and MP.
  - Expected: Enter, Space, or clicking the continue button advances to gameplay without changing the created character data.
- [ ] Start a new level-1 pygame character and view the intro.
  - Expected: The New Game intro appears as story cards with a title, page counter, wrapped text, and clear continue action.
  - Expected: Enter, Space, or mouse click advances pages, and Escape can skip the remaining intro without cancelling the character.
- [x] Load an existing save from the pygame Load Game screen.
  - Expected: The loading popup progress bar fills smoothly instead of advancing in visibly jumpy chunks.
- [x] Quit from a pygame session after visiting dungeon or popup-heavy screens.
  - Expected: The game exits cleanly without leaving stale popup backgrounds or hanging the window.
- [x] Open several popups after moving between town, dungeon, and combat views.
  - Expected: A stale or unavailable popup background falls back cleanly instead of repeating an old scene.
  - Expected: Popup-background diagnostics expose provider presence and fallback count after stale-provider fallbacks.
- [x] Open a yes/no or message confirmation after a screen transition.
  - Expected: The popup draws over a copied background instead of mutating the live screen surface.
- [x] Level up and open the stat-selection prompt after changing screens.
  - Expected: Level-up overlays use a copied background and do not smear or redraw over the live screen unexpectedly.
  - Expected: Level-up and stat-selection prompts accept the first fresh key once no key is held, even without a KEYUP event.
- [ ] Open choice, reward, quantity, and code-entry popups after changing screens.
  - Expected: Each popup draws over the current copied view instead of reusing a live or empty background surface.
  - Expected: Confirmation, reward, quantity, and code-entry popups all wait for the same buffered-key release rule before accepting input.
  - Expected: If no keys are currently held, the next fresh key press is accepted even if no synthetic KEYUP event arrives first.
- [x] Enter combat or a character/shop selector after a previous key-driven transition.
  - Expected: The first fresh action key is accepted once no key is physically held, even if the loop never receives a KEYUP event.
  - Expected: Combat action-grid navigation accepts the first fresh movement/confirm key after turn start once pygame key state has been pumped.
- [x] Move through main, town, load-game, shop-selection, race, class, naming, and location menus after a prior key press.
  - Expected: Guarded navigation still blocks buffered held keys but accepts the next fresh key without waiting for a KEYUP event that may never arrive.
- [x] Navigate selector-style pygame screens with the mouse.
  - Expected: Hovering updates the highlighted row where rows are selectable.
  - Expected: Left-clicking main menu, town menu, shop selection, location, race, class, Character Menu action, tab, and equipment-slot targets selects the same option the keyboard would select.
  - Expected: Shop screens support hover and left-click selection for main options, item rows, and buy-list subtype tabs; item-list mouse-wheel movement preserves keyboard behavior.
  - Expected: NPC conversation and quest text boxes advance with left click using the same skip/continue behavior as keyboard confirm.
  - Expected: Accept Bounty and Active Bounties content lists support row hover, left-click selection, and mouse-wheel movement without changing bounty state.
  - Expected: Reusable popup menus support row hover, left-click selection, ignored header-row clicks, and mouse-wheel movement while preserving keyboard behavior.
- [x] Open the in-dungeon popup menu after a key-driven transition.
  - Expected: The menu ignores a still-held buffered key but accepts the first fresh selection key once no key is physically held.
- [x] Open inventory, equipment, or quest popups after a key-driven transition.
  - Expected: Popup menus ignore still-held buffered keys but accept the first fresh selection key without requiring a KEYUP event.
  - Expected: Holding Up or Down quick-scrolls long popup lists with a short repeat pause and without skipping selectable rows.
  - Expected: Long item descriptions wrap inside the details panel instead of running off-screen.
  - Expected: Attempting to equip a non-equippable inventory item shows a styled popup over the inventory menu background.

### Character Menu
- [ ] Resize the pygame window or test smaller supported resolutions with the modern menu enabled.
  - Expected: Panels remain aligned, text stays readable, and no UI elements overlap incoherently.
  - Expected: Equipment and effect text clips cleanly instead of spilling into neighboring panels.
- [x] Save and load after creating characters with different sex choices.
  - Expected: The load-game save summary shows Sex alongside Level, Race, and Class.
  - Expected: Inventory, equipment management, and character progression remain unchanged.
- [ ] Create several new characters and browse portrait variants on the naming screen.
  - Expected: The standalone sex-selection page no longer appears in the creation flow.
  - Expected: Male/Female buttons below the portrait switch between the selected race's five-portrait sex-specific sets.
  - Expected: The initial portrait varies across attempts, left/right arrows or portrait buttons cycle through five atlas variants, and the chosen sex/portrait persists into the Character Menu and player token.
- [x] Open the pygame Character Menu before and after equipping a stronger weapon.
  - Expected: The Attack stat includes equipped weapon damage and matches the value previewed by equipment changes.
  - Expected: The display falls back to the base combat attack only if weapon-adjusted attack cannot be calculated.
- [x] Open the pygame Character Menu before and after equipping stronger armor.
  - Expected: The Defense stat includes equipped armor and matches the value previewed by equipment changes.
  - Expected: The display falls back to the base combat defense only if armor-adjusted defense cannot be calculated.
- [ ] Equip the special helmets and inspect their persistent effects.
  - Expected: Cohuleen Druith increases Water resistance through combat resistance checks.
  - Expected: Demon Cowl increases Death resistance through combat resistance checks.
  - Expected: Tarnhelm grants invisibility while equipped and removes it when unequipped or replaced.
- [x] Equip a second Indra's Fist on a Soulcatcher through the pygame equipment popup.
  - Expected: The OffHand item list includes eligible fist weapons from inventory.
  - Expected: Equipping the second Indra's Fist keeps the main-hand weapon equipped and sets the offhand to Indra's Fist.
- [ ] Try class-restricted cloth helmets with priest/diviner and non-priest/diviner classes.
  - Expected: Mitre Hat can be equipped by Priest, Archbishop, Diviner, and Astromancer only.
  - Expected: Circlet is blocked for Priest, Archbishop, Diviner, and Astromancer, but remains available to other cloth-helmet users.
- [ ] Equip cloth armor such as Wizard's Robe and inspect Spell Modifier.
  - Expected: Cloth armor contributes a spell modifier bonus while non-cloth armor does not.
  - Expected: Future armor with explicit `spell_mod` uses that value instead of the derived cloth armor bonus.

### Bestiary
- [ ] Open the Character Menu Bestiary before any encounters on a new save.
  - Expected: The Bestiary shows no entries and does not crash.
- [ ] Enter combat with an enemy, flee or leave without defeating it, then open the Bestiary.
  - Expected: The enemy appears as `Seen`, with identity, art, type, and seen count only.
  - Expected: Locations, Possible Drops, resistances, immunities, features, and known abilities remain hidden.
- [ ] Defeat a seen enemy without Vision/detail visibility, then reopen the Bestiary.
  - Expected: Status changes to `Defeated`, defeated count increases, and coarse `Locations` plus `Possible Drops` appear.
  - Expected: Drop info uses broad labels such as `Common`, `Rare`, or `Very Rare`, not exact percentages.
  - Expected: Mechanics remain hidden with the detail-unlock hint.
- [ ] Browse several defeated Bestiary entries repeatedly.
  - Expected: Location and drop hints redraw smoothly from the popup cache while preserving the same visible rows.
- [ ] Use Vision, Reveal, Seeker, or Inquisitor sight during a non-boss fight, observe at least one enemy special action, then open the Bestiary.
  - Expected: Status changes to `Detailed`.
  - Expected: Resistances, known abilities, immunities, and features appear alongside Locations and Possible Drops after defeat.
  - Expected: Repeated combat-frame rendering does not inflate Seen count.
- [ ] Defeat or load a legacy-save defeated enemy with no detailed record.
  - Expected: The entry still appears from `kill_dict`, shows defeated count, and displays defeated-gated practical info.
- [ ] Defeat or load a defeated boss with no detailed Bestiary record.
  - Expected: The entry shows defeated-gated practical info but does not suggest using Vision to reveal boss details.
- [ ] Check fixed and special encounters such as Green Slime, Mimic, Red Dragon, Funhouse enemies, and the Realm of Cambion terminal alarm.
  - Expected: Coarse locations are readable, such as `Early Dungeon`, `Chests`, `Funhouse`, boss-room labels, or realm labels, without exact coordinates.
  - Expected: Quest-only inactive material drops are not shown as normal possible drops.
  - Expected: Ordinary level 5+ chests can become Mimics at a noticeable bounded rate; Funhouse Mimic Chests remain guaranteed Mimics.

### Shops
- [x] Buy from blacksmith categories that now use item-list tabs.
  - Expected: Top-level category selection remains in place for Weapons, Shields, Armor, and Helmets.
  - Expected: Weapon handedness selection remains in place, then weapon subtypes are browsed as tabs inside the buy list.
  - Expected: Armor and Helmet subtypes are browsed as tabs inside the buy list instead of opening another subtype menu.
- [x] Switch pygame shop buy-list tabs with Left and Right.
  - Expected: The active tab changes without leaving the buy list or resetting the top-level shop flow.
  - Expected: The highlighted row resets to a valid visible item on the newly selected tab.
  - Expected: Confirming a purchase refreshes owned counts while preserving the active tab.
- [x] Browse a shop category where some subtypes have no available stock for the current player level or shop rarity rules.
  - Expected: Empty unavailable subtypes are omitted from the tab strip.
  - Expected: Categories with no available stock return cleanly without opening an empty purchase flow.
- [x] Buy from secret-shop grouped categories.
  - Expected: Weapons keep handedness selection, then show subtype tabs for the selected handedness.
  - Expected: Shields/Tomes/Rods, Armor, Helmets, Accessories, and Consumables use tabs for their subgroups.
  - Expected: Secret-shop rarity filtering still applies to each tab.
- [x] Navigate a pygame shop with more than one page of buy or sell items.
  - Expected: PageUp/PageDown move by a visible page while keeping the highlighted item on screen.
  - Expected: Home/End jump to the first and last item without corrupting scroll position.
  - Expected: Long shop lists show the visible item range, and changing buy/sell lists keeps the selected item on a valid visible page.
- [x] Inspect elemental and resistance-bearing equipment in shop description panels.
  - Expected: The item description includes an `Element: ...` line for any item type with elemental metadata.
  - Expected: Fist weapons such as Indra's Fist show their elemental metadata in the secret-shop description panel.
  - Expected: Resistance-bearing shields and accessories show explicit `Resistance: ...` or `Immunity: ...` lines.
- [x] Buy an equipable item from blacksmith, jeweler, and secret-shop equipment categories in pygame.
  - Expected: After the purchase summary, the shop offers to equip class-eligible equipment immediately.
  - Expected: The equip prompt shows available actions, replacement slots, stat changes or `no stat change`, and dual-wield copy requirements.
  - Expected: Choosing equip uses normal equipment rules and leaves failed equip attempts in inventory.
  - Expected: Non-equipment purchases such as potions, keys, scrolls, and quest items do not show equip prompts.
- [ ] Buy an equipable item from blacksmith, jeweler, and secret-shop equipment categories in curses.
  - Expected: Existing curses shop behavior remains usable; prompt-copy parity with pygame is a later polish pass.
- [ ] Buy one weapon that can be equipped in either hand.
  - Expected: The equip prompt offers `Main Hand`, `OffHand`, and `Cancel`.
  - Expected: The equip prompt explains that dual-wield requires buying two copies.
  - Expected: Choosing either slot equips the purchased weapon there and removes one purchased copy from inventory.
- [x] Buy two copies of a dual-wieldable weapon in pygame.
  - Expected: The equip prompt offers `Main Hand`, `OffHand`, `Dual Wield`, and `Cancel`.
  - Expected: `Dual Wield` equips one copy in each hand and leaves any extra purchased copies in inventory.
- [ ] Take hits while wearing each ultimate armor reward.
  - Expected: Robes of Merlin can restore mana after incoming weapon hits.
  - Expected: Dragon Hide can scorch attackers with fire retaliation damage.
  - Expected: Klivanion can shock attackers and may stun them.
  - Expected: Genji Armor can recover a portion of incoming damage after a hit.
- [ ] Equip armor with elemental metadata and inspect matching resistance behavior.
  - Expected: Matching elemental armor contributes resistance through combat resistance checks.
  - Expected: Non-matching elements do not receive the armor resistance bonus.
- [ ] Inspect stat-bearing equipment in the pygame shop item-info flow.
  - Expected: The info panel can show a generated stat-themed display name based on the item's primary metadata.
  - Expected: The generated display name does not replace the canonical item name used by inventory, quests, or saves.
- [ ] Fight an enemy carrying a useful combat consumable while it is injured or low on mana.
  - Expected: The enemy can select `Use Item` and consume a matching potion from class-backed inventory entries.
  - Expected: Consumed enemy inventory items are removed after use instead of remaining available forever.

### Quest Rewards
- [ ] Turn in "The Butcher" quest at the tavern after defeating the Minotaur.
  - Expected: The reward message grants 2 Old Keys.
  - Expected: The inventory shows 2 more Old Keys than before turn-in.
  - Expected: The quest-manager turn-in path records the quest as turned in after granting the keys.
- [ ] Turn in "A Bad Dream" after locating Joffrey.
  - Expected: The reward message grants 3 Old Keys.
  - Expected: The inventory shows 3 more Old Keys than before turn-in.
  - Expected: The Waitress takes the Lucky Locket during turn-in.
  - Expected: The quest-manager turn-in path records the quest as turned in after granting the keys.

## Regression Areas

### Save/Load
- [x] Save after receiving Old Keys, quit, and reload.
  - Expected: The Old Key count persists.
  - Expected: Multi-key quest rewards survive a SaveManager round trip.
- [ ] Open the Load Game menu after a failed or interrupted save attempt.
  - Expected: Only real `.save` files appear; temporary leftovers and directories are hidden.
- [x] Delete a real save file from the pygame Load Game menu.
  - Expected: The delete action asks for confirmation before removing the selected save file.
  - Expected: The deleted save disappears from the list and the next visible save can still be loaded.
- [x] Attempt to delete or load invalid save entries such as blank names or folder-like entries.
  - Expected: The game refuses the invalid entry without loading directories, deleting directories, or creating blank-name saves.
- [ ] Validate save names from a debug/menu path before attempting load or delete.
  - Expected: Normal `.save` names pass; blank, absolute, path-bearing, and non-text entries are rejected.
- [ ] Inspect save-file metadata for a normal save, missing save, directory entry, and temp save.
  - Expected: Validity, file/directory state, existence, size, and tmp-vs-normal location are reported without loading the save.
  - Expected: Expected extension and extension-match state are visible for normal and tmp save paths.
  - Expected: Empty files are flagged directly in individual save metadata.
- [ ] Inspect visible-save metadata from the load-game path.
  - Expected: Metadata appears in the same order as the load menu and excludes temporary leftovers and directories.
  - Expected: Summary diagnostics report visible save count, total size, and largest visible save without opening the save payload.
  - Expected: Loadable entries and visible filename lists match the load menu.
  - Expected: Summary diagnostics include loadable and empty-save counts.
- [ ] Inspect save-directory diagnostics after creating a normal save, a `.tmp` leftover, a `.save` directory, and an unrelated file.
  - Expected: Visible saves, temp leftovers, directory entries, and ignored entries are counted separately.
  - Expected: Hidden-entry filename lists identify temp leftovers, directory-like saves, and ignored files.
  - Expected: Hidden-entry totals match temp leftovers plus directory-like saves plus ignored files.
- [ ] Load an older or partially malformed save with tile-state data.
  - Expected: Valid door/chest/boss room states still restore, while malformed tile-state entries are ignored.
  - Expected: Tile-state diagnostics count valid entries, malformed positions, malformed state payloads, and positions absent from the loaded world.
  - Expected: Tile-state diagnostics identify restorable attribute counts and any unknown legacy/custom attribute keys.
- [x] Attempt to load a corrupted save file.
  - Expected: Loading fails gracefully without deleting or rewriting the corrupted file.

### Quest Log
- [x] Accept and complete a main quest that grants item rewards.
  - Expected: Quest completion and turned-in state are recorded correctly.
- [ ] Inspect quest status summary diagnostics after accepting, completing, and turning in quests.
  - Expected: Main/Side/Bounty category counts distinguish total, completed, turned-in, ready-to-turn-in, and active quests.
  - Expected: Malformed or legacy non-dictionary quest entries are ignored instead of crashing diagnostics.

### Developer Tooling
- [ ] Generate or inspect a `CombatResult` / `CombatResultGroup` diagnostic payload after combat.
  - Expected: Actor and target are represented by names, not full character objects.
  - Expected: Mutating the exported dictionary does not mutate the live combat result's `effects_applied` or `extra` data.
- [ ] Inspect a weapon through equipment/debug output after setting `crit_chance`.
  - Expected: `crit_chance` and legacy `crit` stay in sync.
  - Expected: Character critical-hit chance uses `crit_chance` when it is available.
  - Expected: New weapon definitions can pass `crit_chance=` to the constructor without using ambiguous legacy `crit` values.
- [ ] Run an enemy weighted-action selection diagnostic for an action with telegraph/delay metadata.
  - Expected: The selected action metadata includes ability, priority, delay, telegraph, and `from_action_stack`.
  - Expected: Metadata clears after fallback or non-`action_stack` selection so stale telegraphs are not reported.
- [ ] Run sound/music asset diagnostics for expected combat, town, and menu audio.
  - Expected: Present sound/music files report available paths, while missing placeholder content is reported without crashing or playing audio.
  - Expected: Missing sound/music entries report the checked candidate filenames for supported extensions.
  - Expected: `.wav` music files and staged `sounds/new_sounds/` effects appear in candidate path diagnostics.
  - Expected: The staged `ice_spell.wav` effect appears in default SFX diagnostics when present.
  - Expected: The staged `distorted_scream.wav` effect appears in default SFX diagnostics when present.
  - Expected: The staged `mortal_strike.wav` effect appears in default SFX diagnostics when present.
  - Expected: The staged `shield_block_metal_weapon.wav` effect appears in default SFX diagnostics when present.
  - Expected: The staged `underground_spring.wav` effect appears in default SFX diagnostics when present.
  - Expected: The staged `open_door.wav` effect appears in default SFX diagnostics when present.
  - Expected: The `dungeon` music theme can resolve `eerie_dungeon_background.wav` without changing the runtime theme name.
  - Expected: Default diagnostics include the runtime's main-menu, combat, town, shop, church, inn, dungeon, and final-combat audio names.
  - Expected: Summary counts report available and missing SFX/music assets.
  - Expected: Summary payloads include available and missing SFX/music name lists.
- [ ] Trigger location music routing from main menu, town, shops, church, inn, dungeon, and combat contexts.
  - Expected: Main-menu, town, shop-family, church, inn, dungeon, normal-combat, boss-combat, and final-combat contexts map to distinct runtime music theme names.
  - Expected: Unknown locations fall back to the town theme instead of failing.
  - Expected: Entering top-level pygame town, shop, church, inn, barracks, and dungeon flows requests the matching theme without crashing when audio is unavailable.
  - Expected: Returning from dungeon exploration to town requests town music, and returning to the main menu stops the active location track.
  - Expected: Re-entering the same location does not restart the already active track unless forced.
  - Expected: Combat start requests normal, boss, or final combat music from combat event context.
  - Expected: Ending combat restores the previous non-combat location theme when one was active.
- [ ] Trigger an ice or frost spell/skill event.
  - Expected: The staged `ice_spell` SFX is requested instead of the generic ice placeholder.
- [ ] Trigger a scream, howl, or nightmare-style skill-use event.
  - Expected: The staged `distorted_scream` SFX is requested instead of the generic spell-cast sound.
- [ ] Trigger Mortal Strike in combat.
  - Expected: The staged `mortal_strike` SFX is requested instead of the generic spell-cast sound.
- [ ] Trigger a shield block in combat.
  - Expected: The staged `shield_block_metal_weapon` SFX is requested for the block event.
- [ ] Trigger Laser weapon damage in combat.
  - Expected: The weapon-damage event includes Laser weapon/source metadata.
  - Expected: The staged `laser_beam` SFX is requested instead of generic hit/heavy-hit routing.
- [ ] Trigger Screech from a bird/lightning-bird style enemy or summon.
  - Expected: The staged `bird_attack_sound` SFX is requested for Screech.
  - Expected: Howl/nightmare-style skills still use the existing distorted-scream route.
- [ ] Use a scroll, a health/mana potion, and an elixir in combat.
  - Expected: `ITEM_USE` events include item name, type, subtype, and source metadata.
  - Expected: Scrolls request cast audio, while potions and elixirs request the recovery cue.
- [ ] Accept the underground spring interaction prompt.
  - Expected: The staged `underground_spring` SFX is requested once the prompt is accepted.
- [ ] Unlock/open a dungeon door through Master Key, Master Lockpick plus Lockpick Kit, Cryptic Key, or Old Key flow.
  - Expected: The staged `open_door` SFX is requested only when the door actually opens.
  - Expected: Lockpick Kits lose durability and can break after successful picks; Master Lockpick lowers the break chance.
- [ ] Export a battle log JSON file during a debug run or test.
  - Expected: The file is created with metadata, events, and summary sections.
- [ ] Generate a compact battle-log summary during a debug/tooling check.
  - Expected: The payload includes battle metadata, event-type counts, flag counts, actor/target counts, and aggregate summary counts without raw event rows.
  - Expected: Damage-row counts distinguish all numeric damage events from positive-damage events.
  - Expected: Positive damage totals are attributed by actor and by target.
- [ ] Run an event-bus history check with history disabled.
  - Expected: Subscribers still receive events while history remains empty.
- [ ] Inspect compact event-bus history counts during a debug/test run.
  - Expected: Counts reflect only retained history and remain empty when history is disabled.
- [ ] Inspect compact event-bus subscriber counts during a debug/test run.
  - Expected: Duplicate subscriptions are counted once, and unsubscribed callbacks disappear from the counts.
- [ ] Inspect compact event-bus diagnostics during a debug/test run.
  - Expected: Enabled state, history size/limit, retained event counts, and subscriber counts are visible without raw event rows.
  - Expected: Diagnostics also expose whether bounded history is full and the total subscriber count.
  - Expected: Diagnostics expose remaining history capacity plus sorted retained-history and subscriber event-type lists.
- [ ] Emit an event while one subscriber unsubscribes itself.
  - Expected: Other subscribers for the same event still receive the in-flight event.
  - Expected: The unsubscribed callback is not called on later emissions.
- [ ] Run focused action-queue tests after combat scheduling changes.
  - Expected: Negative delays are treated as instant actions and helper-created actions include debug metadata.

### Item Icons
- [x] Open the modern Character Menu equipment tab with weapon, armor, offhand, ring, pendant, and helmet states.
  - Expected: Implemented equipment slots display an archetype icon next to the item name, including `No Helmet`.
  - Expected: Empty equipment slots do not crash and preserve the existing slot text.
- [x] Open Inventory with weapons, armor, accessories, potions, scrolls, quest items, and special/key items.
  - Expected: Each visible inventory row displays an icon.
  - Expected: Repeated tier items intentionally share the same archetype icon.
- [x] Inspect consumables in Inventory.
  - Expected: Health, mana, status/remedy, stat potion, elixir, and scroll-style items use their individual large artwork when selected.
- [x] Inspect quest/key/special items.
  - Expected: Quest items, keys, gems/specials, and crafting-material style items use individual large artwork when selected.
- [ ] Add or simulate an unknown item with no explicit mapping.
  - Expected: The UI logs a warning, infers from item type/subtype when possible, and otherwise displays `generic_item`.
- [x] Navigate inventory actions after icons render.
  - Expected: Equip, use, drop, cancel, sorting, and scrolling behavior still works.
- [x] Save and reload a character after icon rendering.
  - Expected: Save data is unchanged; icons are derived from item names/types at render time.

### Large Item Artwork
- [x] Open Inventory and highlight weapons, armor, accessories, consumables, quest items, and unknown/fallback items.
  - Expected: The selected-item detail panel shows large artwork while compact inventory rows still use small icons.
  - Expected: Long item names and wrapped descriptions do not overlap the artwork.
- [x] Open Equipment and move through weapon, armor, helmet, offhand, ring, and pendant slots.
  - Expected: Equipped item detail views show large artwork where panel width allows it.
  - Expected: The modern Character Menu Equipment tab uses large artwork in its slot cards rather than small icons.
  - Expected: Empty equipment slots do not crash.
- [x] Open a shop buy/sell list and highlight equippable and non-equippable items.
  - Expected: The left option panel shows the selected item artwork while buy/sell items are being browsed.
  - Expected: The selected item description panel remains readable and text-focused.
  - Expected: Price, owned count, and stat comparison panels continue to work.
- [x] Open a chest or reward popup that grants loot.
  - Expected: Loot entries show large artwork beside the item name, description, and stats.
  - Expected: Empty chest and unlock prompts are unchanged.
- [x] Reopen a chest that has already been opened.
  - Expected: The chest reports that it has already been opened and does not regenerate loot, trigger combat, show a loot popup, or mutate inventory.
- [x] Collect a relic from a relic room and interact with the room again.
  - Expected: The first interaction uses the shared relic-specific discovery text in pygame and core/curses flows, grants the relic, sets the room read state, and restores HP/MP; repeat interaction does not duplicate the relic or restoration.
- [ ] Simulate or create an item with no exact render mapping.
  - Expected: The render manager falls back through icon mapping, category/slot, and then the generated fallback surface without blocking gameplay.
- [x] Save and reload after viewing item artwork.
  - Expected: Save data is unchanged; large artwork is resolved from item names/types at render time.

### NPC Story Artwork
- [ ] Review the generated NPC portrait sheet after the story portrait batch.
  - Expected: `src/ui_pygame/assets/npc_art/npc_art_review_sheet.png` shows recurring town NPCs, Seraphine Voss, Mara Vale, The Gray Broker, Old Warehouse Guard, Warp Point Scientist, Acolyte, Reflection, and Vesperion.
  - Expected: Portraits have transparent edges, no rectangular backgrounds, no labels or watermarks, consistent dark fantasy painterly style, and readable silhouettes.
- [ ] Inspect Seraphine Voss, Mara Vale, The Gray Broker, Old Warehouse Guard, and Warp Point Scientist portrait aliases.
  - Expected: Their assets appear in the NPC review sheet and resolve through `NpcArtManager` without appearing in unrelated shop, combat, bounty, or town hover panels.
- [ ] Visit the Old Warehouse after the Thieves Guild has unlocked.
  - Expected: The off-limits warning uses the split dialogue popup with the Old Warehouse Guard portrait instead of a plain text-only popup.
- [ ] Review `src/ui_pygame/assets/npc_art/npc_art_review_sheet.png` after the V3 diversity replacements.
  - Expected: Alchemist, Barkeep, Jeweler, Priest, Soldier, Waitress, and Warp Point Scientist use the approved replacement portraits.
  - Expected: Busboy, Drunkard, Griswold, Old Warehouse Guard, and Sergeant retain their prior approved portraits.
  - Expected: Archived originals and rejected candidates under `npc_art/old_files/` do not appear in live dialogue, shops, town menus, combat, bounty boards, or hover panels.
- [ ] Trigger Acolyte Liminal Waiting/Mirror dialogue.
  - Expected: The Acolyte portrait appears only on named Acolyte dialogue surfaces and does not alter Liminal route state.
- [ ] Trigger Reflection locked/prelude/victory/defeat dialogue.
  - Expected: The Reflection portrait appears on named Reflection dialogue surfaces while combat still uses the Reflection enemy sprite through the combat renderer.
- [ ] Trigger initial and true-final Vesperion story dialogue.
  - Expected: Vesperion narrative dialogue uses the Vesperion portrait, including the initial final-room prelude.
  - Expected: Combat sprites, enemy info panels, combat HUD, ending text, shops, bounties, and town hover panels do not display story portraits unless explicitly mapped.
- [ ] Review the deferred story-scene target map before creating the next story art batch.
  - Expected: `joffrey_body`, `timmy_found`, `timmy_home`, `waitress_grief`, and optional `waitress_mad` are documented as named special-event/dialogue targets, not venue-wide or location-panel art.

### Companion And Summon Artwork
- [x] Review the generated summon companion-art sheet.
  - Expected: the Xenid review sheet shows Patagon, Kobalos, Dilong, Cacus,
    Agloolik, Izulu, Hala, Lamashtu, Seraphim, Bardi, Tiamat, and Zahhak.
  - Expected: Sprites have transparent backgrounds, clean silhouettes, no rectangular cards, no labels, and no clipping.
- [ ] View at least one familiar, one tamed companion, and one summon in pygame companion-art surfaces.
  - Expected: The Class tab companion/summon list is compact, does not show art thumbnails, and uses stacked full-width rows instead of a square grid.
  - Expected: A Thaumaturgist with seven chosen Xenids shows all seven rows without clipping.
  - Expected: Selecting a familiar or summon opens a Character-tab-style details popup with the large companion artwork, identity, core attributes, combat stats, abilities, weaknesses, and resistances.
  - Expected: Selecting a tamed companion opens a Character-tab-style details popup with large artwork, identity, form/special/bond rows, and flavor notes instead of targetable HP/MP/stat-sheet detail.
  - Expected: Familiars and summons resolve through `CompanionArtManager` from `companion_art/`; renamed tamed companions resolve artwork from their original enemy class first, then fall back through enemy combat sprites when no bespoke companion art exists.
  - Expected: Save/load data is unchanged.

### Enemy Sprite Artwork
- [ ] Start combat against an enemy mapped to the boss fallback.
  - Expected: Boss fallback sprite appears when no specific boss sprite exists.
  - Expected: Boss combat, victory, defeat, and flee flows still function.
- [ ] Simulate or create an enemy with no exact mapping, category, or useful name hint.
  - Expected: `generic_enemy` displays without crashing combat.
- [x] Inspect the combat target panel while Sight is active and inactive.
  - Expected: Enemy sprite and name remain visible.
  - Expected: HP, weaknesses, resistances, and status icons appear only when combat visibility rules allow them.
  - Expected: Invisible enemies explain whether details are hidden without Sight or revealed by Sight.
- [x] Apply or simulate Bleed on a construct enemy in pygame combat.
  - Expected: Pygame combat presentation uses `Oil Leak` wording/icon text for the construct while core mechanics, saves, and reports still use canonical `Bleed`.
- [ ] Verify enemy sprite lookup does not affect saves.
  - Expected: Save/load data is unchanged.
- [ ] Start Vesperion combat after the portrait batch.
  - Expected: Center combat uses the full-body `src/ui_pygame/assets/enemy_combat_sprites/vesperion.png`, visually matching the dialogue portrait identity instead of reusing the portrait crop or generic boss sprite.
  - Expected: Vesperion combat mechanics, phase pressure, Liminal transition, true-final victory, rewards, and save state are unchanged.
  - Expected: Combat panels, enemy tokens, and dungeon boss navigation figures use `enemy_combat_sprites/`.
- [ ] Review `docs/ENEMY_VISUAL_SYSTEM.md` before adding new enemy presentation screens.
  - Expected: Combat sprites and enemy tokens are used for their intended visual layers.

### Enemy Combat Sprites
- [x] Review the generated enemy combat sprite sheet.
  - Expected: `src/ui_pygame/assets/enemy_combat_sprites/enemy_combat_sprite_review_sheet.png` shows every sprite on a neutral dungeon background.
  - Expected: Sprites have transparent backgrounds, clean silhouettes, no rectangular cards, no labels, and no clipping.
  - Expected: Quasit is visually distinct from Imp, with green warted skin, spiky horns, barbed tail, and long clawed digits.
- [x] Start combat against Skeleton, Giant Rat, an elemental such as Ice Myrmidon, Dragon, Demon, boss fallback, and generic fallback enemies.
  - Expected: Center combat uses `EnemyCombatSpriteManager` sprites from `enemy_combat_sprites/`.
  - Expected: Enemy portraits, enemy render artwork, and enemy tokens do not appear as the center enemy body.
- [x] Trigger damage and defeat animations.
  - Expected: Damage flash and death fade/scale still apply to the transparent sprite surface.
