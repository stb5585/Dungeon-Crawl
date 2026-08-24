from types import SimpleNamespace

from src.core import abilities, enemies, items
from src.core.classes import bard, class_rings, demonologist, promotion_kits
from src.core.save_system import PlayerDataSerializer
from tests.test_framework import TestGameState


def _player(class_name, **kwargs):
    return TestGameState.create_player(class_name=class_name, race_name="Human", level=30, **kwargs)


def test_promotion_kit_state_normalizes_and_round_trips():
    player = _player("Seeker")
    player.promotion_kit_state = {
        "summon_bonds": {"Patagon": 150, "Unknown": 99},
        "case_journal": {"Fiend": 250, "": 20},
        "bard_repertoire": {"Battle Hymn": {"known": True, "practice_xp": 99, "clean_finishes": 4}},
        "lycan_control": {"rank": "Tethered", "stress_events": 3, "dragon_essence": True},
        "favored_enemy": {"type": "Animal", "practice": 1000, "switches": 2},
    }

    state = player.ensure_promotion_kit_state()

    assert state["summon_bonds"]["Patagon"] == 100
    assert "Unknown" not in state["summon_bonds"]
    assert state["case_journal"] == {"Fiend": 100}
    assert state["bard_repertoire"]["Battle Hymn"]["known"] is True
    assert state["lycan_control"]["rank"] == "Tethered"
    assert state["favored_enemy"] == {"type": "Animal", "practice": 999, "switches": 2}

    restored = PlayerDataSerializer.deserialize(PlayerDataSerializer.serialize(player), skip_tiles=True)
    assert restored.promotion_kit_state["case_journal"]["Fiend"] == 100
    assert restored.promotion_kit_state["favored_enemy"]["type"] == "Animal"
    assert promotion_kits.combat_state(restored)["foresight_threads"] == 0


def test_threaded_cast_and_shadowcaster_shade_of_ahool():
    astro = _player("Astromancer", mana=(100, 100))
    assert "requires" in abilities.ThreadedCast().use(astro)
    assert "gains 1 Foresight" in promotion_kits.gain_meter(astro, "foresight_threads", 1, "test")
    assert "prepares Threaded Cast" in abilities.ThreadedCast().use(astro)

    shadow = _player("Shadowcaster", health=(200, 200))
    holy_before = shadow.check_mod("resist", typ="Holy")
    class_rings.ensure_state(shadow)["data"]["Shadowcaster"]["debt"] = 25
    assert "becomes the Shade of Ahool" in abilities.ShadeOfAhool().use(shadow)
    assert shadow.shade_of_ahool_turns == 3
    assert shadow.flying
    assert class_rings.ensure_state(shadow)["data"]["Shadowcaster"]["debt"] == 5
    assert shadow.check_mod("resist", typ="Holy") == holy_before - 0.25


def test_demonologist_corruption_and_mood_gate_intents():
    demo = _player("Demonologist")
    demo.gold = 10000
    demo.demonologist_contracts = demonologist.default_state()
    demo.demonologist_contracts["unlocked_contracts"] = ["Imp"]
    demo.demonologist_contracts["active_patron"] = "Imp"
    demo.ensure_demonologist_contracts()

    assert "Protect" not in demonologist.available_intents(demo, "Imp")
    demo.demonologist_contracts["patron_moods"]["Imp"] = 25
    assert "Protect" in demonologist.available_intents(demo, "Imp")

    target = enemies.Goblin()
    message = demonologist.resolve_contract(demo, target, "Protect", rng=SimpleNamespace(random=lambda: 1.0))

    assert "Bargain taint rises" in message
    assert demo.demonologist_contracts["corruption"] > 0
    assert demo.demonologist_contracts["patron_moods"]["Imp"] > 25


def test_representative_active_spends_and_status_text():
    cleric = _player("Cleric", mana=(100, 100))
    promotion_kits.gain_meter(cleric, "devotion", 2, "test")
    assert "Sanctuary Ward" in abilities.SanctuaryWard().use(cleric)

    priest = _player("Priest", mana=(100, 100), health=(120, 40))
    promotion_kits.gain_meter(priest, "prayer", 4, "test")
    mana_before = priest.mana.current
    assert abilities.Supplication().cost == 0
    assert "spends 4 Prayer" in abilities.Supplication().use(priest, priest)
    assert priest.mana.current == mana_before
    assert priest.health.current > 40

    monk = _player("Master Monk", mana=(100, 100))
    target = enemies.Goblin()
    promotion_kits.gain_meter(monk, "ki", promotion_kits.cap_for(monk, "ki"), "test")
    assert "Dim Mak" in abilities.DimMak().use(monk, target)

    assert "Ki:" in monk._class_kit_status_str()


def test_held_devotion_reduces_incoming_damage_until_spent():
    cleric = _player("Cleric", mana=(100, 100))
    attacker = enemies.Goblin()

    hit, message, damage = cleric.damage_reduction(100, attacker, typ="Physical")
    assert hit is True
    assert damage == 100
    assert "Devotion guard" not in message

    promotion_kits.gain_meter(cleric, "devotion", 3, "test")
    hit, message, damage = cleric.damage_reduction(100, attacker, typ="Physical")
    assert hit is True
    assert damage == 91
    assert "Devotion guard reduces damage by 9" in message

    assert "spends 3 Devotion" in abilities.SanctuaryWard().use(cleric)
    hit, message, damage = cleric.damage_reduction(100, attacker, typ="Physical")
    assert hit is True
    assert damage == 100
    assert "Devotion guard" not in message

    templar = _player("Templar", mana=(100, 100))
    promotion_kits.gain_meter(templar, "devotion", 5, "test")
    _hit, message, damage = templar.damage_reduction(100, attacker, typ="Physical")
    assert damage == 85
    assert "Devotion guard reduces damage by 15" in message


def test_deferred_devotion_only_applies_when_defender_survives_action():
    cleric = _player("Cleric")
    target = enemies.Goblin()

    promotion_kits.begin_action(cleric, defer_devotion=True)
    promotion_kits.record_damage_event(
        cleric,
        target,
        12,
        "Holy",
        metadata={"attack_source": "weapon", "weapon_type": "Club"},
    )
    assert promotion_kits.combat_state(cleric)["devotion"] == 0
    assert promotion_kits.finish_action(cleric, defender_survived=False) == ""
    assert promotion_kits.combat_state(cleric)["devotion"] == 0

    promotion_kits.begin_action(cleric, defer_devotion=True)
    promotion_kits.record_damage_event(
        cleric,
        target,
        12,
        "Holy",
        metadata={"attack_source": "weapon", "weapon_type": "Club"},
    )
    message = promotion_kits.finish_action(cleric, defender_survived=True)

    assert "gains 1 Devotion" in message
    assert promotion_kits.combat_state(cleric)["devotion"] == 1


def test_hierophant_devotion_and_consecrated_conduit_payoff():
    hierophant = _player("Hierophant", mana=(100, 100), health=(100, 100))
    hierophant.equipment["Weapon"] = items.Quarterstaff()
    hierophant.spellbook["Skills"]["Staff Conduit"] = abilities.StaffConduit()
    target = enemies.Goblin()

    promotion_kits.begin_action(hierophant)
    promotion_kits.record_healing_done(hierophant, 20)
    promotion_kits.record_damage_event(
        hierophant,
        target,
        12,
        "Physical",
        metadata={"attack_source": "weapon", "weapon_slot": "Weapon", "weapon_type": "Staff"},
    )
    assert promotion_kits.combat_state(hierophant)["devotion"] == 1

    promotion_kits.begin_action(hierophant)
    promotion_kits.record_damage_event(
        hierophant,
        target,
        12,
        "Physical",
        metadata={"attack_source": "weapon", "weapon_slot": "Weapon", "weapon_type": "Staff"},
    )
    assert promotion_kits.combat_state(hierophant)["devotion"] == 2

    message = abilities.ConsecratedConduit().use(hierophant)
    assert "spends 2 Devotion" in message
    before_hp = target.health.current
    promotion_kits.record_damage_event(
        hierophant,
        target,
        20,
        "Physical",
        metadata={"attack_source": "weapon", "weapon_slot": "Weapon", "weapon_type": "Staff"},
    )
    assert target.health.current < before_hp
    assert promotion_kits.combat_state(hierophant)["consecrated_conduit"] is None
    assert hierophant.magic_effects["Nature Shield"].active is True


def test_hierophant_conduit_gates_and_ring_preserves_after_payoff():
    cleric = _player("Cleric", mana=(100, 100))
    assert "requires Hierophant" in abilities.ConsecratedConduit().use(cleric)

    hierophant = _player("Hierophant", mana=(100, 100))
    assert "requires a staff" in abilities.ConsecratedConduit().use(hierophant)

    hierophant.equipment["Weapon"] = items.Quarterstaff()
    assert "requires Devotion" in abilities.ConsecratedConduit().use(hierophant)

    _awaken_ring(hierophant, "Hierophant")
    promotion_kits.gain_meter(hierophant, "devotion", 3, "test")
    assert "spends 3 Devotion" in abilities.ConsecratedConduit().use(hierophant)
    target = enemies.Goblin()
    promotion_kits.record_damage_event(
        hierophant,
        target,
        24,
        "Physical",
        metadata={"attack_source": "weapon", "weapon_slot": "Weapon", "weapon_type": "Staff"},
    )
    assert promotion_kits.combat_state(hierophant)["devotion"] == 1
    assert "Sacred Conduit preserves 1 spent devotion" in promotion_kits.pop_messages(hierophant)


def test_sacred_overchannel_boosts_hierophant_devotion_and_payoff():
    hierophant = _player("Hierophant", mana=(100, 80))
    hierophant.equipment["Weapon"] = items.Quarterstaff()
    hierophant.spellbook["Skills"]["Sacred Overchannel"] = abilities.SacredOverchannel()
    hierophant.power_up = True
    hierophant.class_effects["Power Up"].active = True
    hierophant.class_effects["Power Up"].duration = 5
    target = enemies.Goblin()

    promotion_kits.begin_action(hierophant)
    promotion_kits.record_damage_event(
        hierophant,
        target,
        12,
        "Physical",
        metadata={"attack_source": "weapon", "weapon_slot": "Weapon", "weapon_type": "Staff"},
    )
    assert promotion_kits.combat_state(hierophant)["devotion"] == 2

    before_mana = hierophant.mana.current
    assert "spends 2 Devotion" in abilities.ConsecratedConduit().use(hierophant)
    after_cost_mana = hierophant.mana.current
    assert after_cost_mana == before_mana - 10
    promotion_kits.record_damage_event(
        hierophant,
        target,
        20,
        "Physical",
        metadata={"attack_source": "weapon", "weapon_slot": "Weapon", "weapon_type": "Staff"},
    )
    assert hierophant.mana.current == after_cost_mana + 2


def test_ui_log_polish_status_matrix_surfaces():
    astro = _player("Astromancer", mana=(100, 100))
    _awaken_ring(astro, "Astromancer")
    promotion_kits.gain_meter(astro, "foresight_threads", 1, "test")
    abilities.ThreadedCast().use(astro)
    astro_status = astro._class_kit_status_str()
    assert "Threads:" in astro_status
    assert "Threaded ready" in astro_status
    assert "Threaded:" in astro_status
    assert "Pending next spell" in astro_status
    assert "Ring Ready:" in astro_status

    soulcatcher = _player("Soulcatcher")
    _awaken_ring(soulcatcher, "Soulcatcher")
    soulcatcher.magic_effects["Totem"].active = True
    soulcatcher.magic_effects["Totem"].extra = {"aspect": "Fire", "resonance": 2}
    soul_status = soulcatcher._class_kit_status_str()
    assert "Totem:" in soul_status
    assert "Fire 2/4" in soul_status

    seeker = _player("Seeker")
    target = enemies.Goblin()
    promotion_kits.gain_case_progress(seeker, target.enemy_typ, 75, "test")
    promotion_kits.add_revelation(seeker, target, 2, "test")
    seeker_status = seeker._class_kit_status_str()
    assert "Case:" in seeker_status
    assert "Pattern Lock" in seeker_status
    assert "Revelation:" in seeker_status

    beast = _player("Beast Master")
    beast.tamed_companion = {"active": True, "name": "Wolf", "bond": 50}
    beast.familiar = SimpleNamespace(name="Wolf", spec="Tamed", is_alive=lambda: True)
    beast.spellbook["Skills"]["Pack Strike"] = abilities.PackStrike()
    abilities.PackStrike().use(beast)
    beast_status = beast._class_kit_status_str()
    assert "Companion:" in beast_status
    assert "Battle-Trained" in beast_status
    assert "Command:" in beast_status

    lycan = _player("Lycan")
    promotion_kits.unlock_dragon_essence(lycan)
    lycan_status = lycan._class_kit_status_str()
    assert "Control:" in lycan_status
    assert "Dragon Essence:" in lycan_status


def test_ui_log_polish_persistent_and_preservation_status_lines():
    demo = _player("Demonologist")
    demo.demonologist_contracts = demonologist.default_state()
    demo.demonologist_contracts["unlocked_contracts"] = ["Imp"]
    demo.demonologist_contracts["active_patron"] = "Imp"
    demo.demonologist_contracts["corruption"] = 30
    demo.demonologist_contracts["patron_moods"]["Imp"] = 25
    demo.demonologist_contracts["imprisoned_familiar"] = {
        "name": "Ash",
        "race": "Mephit",
        "spec": "Arcane",
    }
    demo_status = demo._class_kit_status_str()
    assert "Corruption:" in demo_status
    assert "Patron:" in demo_status
    assert "Echo:" in demo_status

    templar = _player("Templar", mana=(100, 100))
    _awaken_ring(templar, "Templar")
    promotion_kits.gain_meter(templar, "devotion", 2, "test")
    ready_status = templar._class_kit_status_str()
    assert "Ring Ready:" in ready_status
    assert "Ring Preserve:" in ready_status
    assert "Ready" in ready_status

    message = abilities.SanctuaryWard().use(templar)
    used_status = templar._class_kit_status_str()
    assert "Ordered Blessings preserves 1 spent devotion" in message
    assert "Ring Preserve:" in used_status
    assert "Used" in used_status


def test_status_summary_rows_are_clean_label_value_pairs():
    dragoon = _player("Dragoon")
    promotion_kits.combat_state(dragoon)["aerial_tempo"] = 2
    assert ("Aerial Tempo", "2/3 Follow-up") in promotion_kits.status_summary_rows(dragoon)
    assert "Aerial Tempo:" in dragoon._class_kit_status_str()

    archbishop = _player("Archbishop", mana=(100, 100))
    _awaken_ring(archbishop, "Archbishop")
    promotion_kits.gain_meter(archbishop, "prayer", 2, "test")
    archbishop_rows = promotion_kits.status_summary_rows(archbishop)
    assert ("Prayer", "2/7 Supplication ready") in archbishop_rows
    assert ("Ring Ready", "Divine Intervention") in archbishop_rows
    assert ("Ring Preserve", "Ready") in archbishop_rows

    demo = _player("Demonologist")
    demo.demonologist_contracts = demonologist.default_state()
    demo.demonologist_contracts["unlocked_contracts"] = ["Imp"]
    demo.demonologist_contracts["active_patron"] = "Imp"
    demo.demonologist_contracts["corruption"] = 40
    demo.demonologist_contracts["patron_moods"]["Imp"] = 12
    demo.demonologist_contracts["imprisoned_familiar"] = {"name": "Ash", "spec": "Arcane"}
    demo_rows = promotion_kits.status_summary_rows(demo)
    assert ("Corruption", "40/100") in demo_rows
    assert ("Patron", "Imp (12)") in demo_rows
    assert ("Echo", "Ash") in demo_rows


def test_ui_log_polish_representative_messages():
    monk = _player("Master Monk")
    cap = promotion_kits.cap_for(monk, "ki")
    assert "gains" in promotion_kits.gain_meter(monk, "ki", cap, "test")
    assert "capped" in promotion_kits.gain_meter(monk, "ki", 1, "test")

    troubadour = _player("Troubadour")
    promotion_kits.gain_meter(troubadour, "crescendo", 1, "song")
    assert "Crescendo clears from interruption" in promotion_kits.clear_crescendo(
        troubadour,
        "interruption",
    )

    shaman = _player("Shaman")
    shaman.magic_effects["Totem"].active = True
    shaman.magic_effects["Totem"].extra = {"aspect": "Fire", "resonance": 3}
    assert "Totem Resonance is capped" in promotion_kits.gain_totem_resonance(
        shaman,
        "pulse",
    )


def test_resolve_aerial_aspect_totem_and_beast_commands():
    sentinel = _player("Sentinel")
    sentinel.equipment["OffHand"] = items.Glagwa()
    assert "Resolve" in promotion_kits.build_resolve(sentinel, 50, "test")
    assert class_rings.ensure_state(sentinel)["data"]["Stalwart Defender"]["guard_meter"] == 50
    assert "Bulwark Guard" in abilities.BulwarkGuard().use(sentinel)

    defender = _player("Stalwart Defender")
    defender.equipment["OffHand"] = items.Glagwa()
    assert "Resolve" in promotion_kits.build_resolve(defender, 100, "test")
    assert promotion_kits.resolve_surge_unlocked(defender, "Citadel Aegis")
    assert promotion_kits.resolve_surge_unlocked(defender, "Ironwall Revenge")
    assert promotion_kits.resolve_surge_unlocked(defender, "Last Bastion")
    assert promotion_kits.resolve_surge_unlocked(defender, "Stronghold")
    assert "Citadel Aegis" in abilities.CitadelAegis().use(defender)
    assert class_rings.ensure_state(defender)["data"]["Stalwart Defender"]["guard_meter"] == 0
    promotion_kits.gain_resolve_mastery(defender, 4, "shield tactics")
    assert promotion_kits.resolve_surge_unlocked(defender, "Ironwall Revenge")

    restored = PlayerDataSerializer.deserialize(PlayerDataSerializer.serialize(defender), skip_tiles=True)
    assert promotion_kits.resolve_surge_unlocked(restored, "Ironwall Revenge")

    dragoon = _player("Dragoon")
    promotion_kits.combat_state(dragoon)["aerial_tempo"] = 2
    assert "Aerial Tempo:" in dragoon._class_kit_status_str()

    archdruid = _player("Archdruid", mana=(100, 100), health=(150, 100))
    target = enemies.Goblin()
    assert "Venom" in promotion_kits.add_aspect(archdruid, "Venom")
    assert "Growth" in promotion_kits.add_aspect(archdruid, "Growth")
    assert "Fourfold Surge" in abilities.FourfoldSurge().use(archdruid, target)

    shaman = _player("Shaman", mana=(100, 100))
    shaman.magic_effects["Totem"].active = True
    shaman.magic_effects["Totem"].extra = {"aspect": "Fire", "resonance": 1}
    shaman.spellbook["Spells"]["Fireball"] = abilities.Fireball()
    assert "force Fireball" in abilities.TotemSurge().use(shaman, target)

    beast = _player("Beast Master")
    beast.tamed_companion = {"active": True, "name": "Companion", "bond": 50}
    beast.familiar = SimpleNamespace(name="Companion", spec="Tamed", is_alive=lambda: True)
    assert "Pack Strike" in abilities.PackStrike().use(beast)


def test_case_revelation_death_mark_stolen_charge_and_summon_bond():
    seeker = _player("Seeker")
    target = enemies.Goblin()
    assert "Revelation" in promotion_kits.add_revelation(seeker, target, 1, "test")
    assert "Case Journal" in promotion_kits.gain_case_progress(seeker, target.enemy_typ, 50, "test")

    ninja = _player("Ninja")
    assert "Death Mark" in promotion_kits.apply_death_mark(ninja, target, "test")

    trickster = _player("Arcane Trickster")
    assert "Stolen Charge" in promotion_kits.gain_stolen_charge(trickster, "test")

    summoner = _player("Thaumaturgist", mana=(100, 100))
    assert "Patagon's conduit" in promotion_kits.gain_summon_bond(summoner, "Patagon", 50, "test")
    assert ("Xenid Conduit", "Patagon 50/100 Invoke ready") in promotion_kits.status_summary_rows(summoner)
    assert "invokes Patagon" in abilities.InvokePatagon().use(summoner, target)


def test_stolen_charge_payoff_has_meaningful_damage_floor():
    trickster = _player("Arcane Trickster")
    target = enemies.Goblin()
    target.health.current = 100
    state = promotion_kits.combat_state(trickster)
    state["stolen_charge"] = 3

    promotion_kits.record_damage_event(
        trickster,
        target,
        6,
        "Physical",
        metadata={"attack_source": "weapon"},
    )

    assert target.health.current == 85
    assert state["stolen_charge"] == 0


def test_summon_conduit_gain_uses_global_level_scaled_roll(monkeypatch):
    from src.core import companions

    summoner = _player("Thaumaturgist")
    summon = companions.Patagon()
    summon.level.level = 2
    summon.level.pro_level = 1
    summon.exp_scale = 250
    summoner.summons = {"Patagon": summon}
    summoner.active_summon_name = "Patagon"
    monkeypatch.setattr("src.core.classes.promotion_kits.random.random", lambda: 0.01)

    assert promotion_kits.summon_bond_gain_for_victory(summoner, 50) > 0


def test_summon_conduit_gain_allows_new_xenids_and_can_fail_roll(monkeypatch):
    from src.core import companions

    summoner = _player("Thaumaturgist")
    summon = companions.Patagon()
    summoner.summons = {"Patagon": summon}
    summoner.active_summon_name = "Patagon"

    assert promotion_kits.summon_bond_gain_for_victory(
        summoner,
        9999,
        guaranteed=True,
    ) > 0
    monkeypatch.setattr("src.core.classes.promotion_kits.random.random", lambda: 0.99)
    assert promotion_kits.summon_bond_gain_for_victory(summoner, 50) == 0
    message = promotion_kits.gain_summon_bond_for_active(summoner, 0, "victory")
    assert "Xenid Conduit: Patagon conduit holds steady" in message


def test_summon_defaults_and_dilong_starting_stats(monkeypatch):
    from src.core import companions

    player = _player("Thaumaturgist")
    dilong = companions.Dilong()
    monkeypatch.setattr("src.core.companions.random.randint", lambda _low, _high: 15)
    dilong.initialize_stats(player)

    assert dilong.exp_scale == 1000
    assert dilong.level.exp_to_gain == 2000
    assert dilong.combat.magic > 0
    assert dilong.combat.magic_def > 0
    assert "Surface" in dilong.spellbook["Skills"]


def test_lycan_control_and_dragon_essence():
    lycan = _player("Lycan")
    assert "rank Feral" in promotion_kits.record_lycan_stress(lycan, "survive")
    assert "Dragon Essence" in promotion_kits.unlock_dragon_essence(lycan)
    target = enemies.Goblin()
    assert "Winged Pounce" in abilities.WingedPounce().use(lycan, target)


def _awaken_ring(player, class_name):
    player.equipment["Ring"] = items.ClassRing()
    class_rings.ensure_state(player)["awakened"][class_name] = True
    player.equipment["Ring"].class_mod(player)


def test_ring_smoothing_preserves_devotion_prayer_and_rogue_luck(monkeypatch):
    templar = _player("Templar", mana=(100, 100))
    _awaken_ring(templar, "Templar")
    promotion_kits.gain_meter(templar, "devotion", 3, "test")
    message = abilities.SanctuaryWard().use(templar)
    assert "Ordered Blessings preserves 1 spent devotion" in message
    assert promotion_kits.combat_state(templar)["devotion"] == 1

    archbishop = _player("Archbishop", mana=(100, 100), health=(100, 40))
    _awaken_ring(archbishop, "Archbishop")
    promotion_kits.gain_meter(archbishop, "prayer", 3, "test")
    message = abilities.Supplication().use(archbishop, archbishop)
    assert "Divine Intervention preserves 1 spent prayer" in message
    assert promotion_kits.combat_state(archbishop)["prayer"] == 1

    rogue = _player("Rogue")
    _awaken_ring(rogue, "Rogue")
    promotion_kits.gain_meter(rogue, "fortune", 2, "test")
    monkeypatch.setattr("random.random", lambda: 0.0)
    forced, message = promotion_kits.consume_fortune_for_risky_action(rogue, "Steal")
    assert forced is True
    assert "Loaded Dice preserves 1 spent fortune" in message
    assert promotion_kits.combat_state(rogue)["fortune"] == 1

    target = enemies.Goblin()
    promotion_kits.gain_meter(rogue, "misfortune", 3, "test")
    before = target.health.current
    message = promotion_kits.resolve_misfortune_payoff(rogue, target, 50, "Mug")
    assert "Loaded Dice preserves 1 spent misfortune" in message
    assert target.health.current < before
    assert promotion_kits.combat_state(rogue)["misfortune"] == 1


def test_rogue_cheat_death_spends_misfortune_and_applies_jinx(monkeypatch):
    rogue = _player("Rogue", health=(100, 0))
    _awaken_ring(rogue, "Rogue")
    promotion_kits.gain_meter(rogue, "misfortune", 3, "test")
    monkeypatch.setattr("random.random", lambda: 0.0)

    message = promotion_kits.cheat_death(rogue)

    assert "Cheat Death spends 3 Misfortune" in message
    assert rogue.health.current == 1
    assert promotion_kits.combat_state(rogue)["jinx_turns"] == 2
    assert "Jinx:" in rogue._class_kit_status_str()
    rogue.effects()
    rogue.effects()
    assert promotion_kits.combat_state(rogue)["jinx_turns"] == 0


def test_thief_rogue_fortune_only_grows_on_critical_damage():
    thief = _player("Thief")
    target = enemies.Goblin()

    promotion_kits.record_damage_event(
        thief,
        target,
        10,
        "Physical",
        metadata={"attack_source": "weapon", "is_critical": False},
    )
    assert promotion_kits.combat_state(thief)["fortune"] == 0

    promotion_kits.record_damage_event(
        thief,
        target,
        10,
        "Physical",
        metadata={"attack_source": "weapon", "is_critical": True},
    )
    assert promotion_kits.combat_state(thief)["fortune"] == 1


def test_risky_thief_ability_miss_adds_misfortune_without_noncrit_fortune(monkeypatch):
    thief = _player("Thief", mana=(100, 100))
    target = enemies.Goblin()

    monkeypatch.setattr(thief, "weapon_damage", lambda *_args, **_kwargs: ("misses.\n", False, 1))
    abilities.Mug().use(thief, target)
    state = promotion_kits.combat_state(thief)
    assert state["fortune"] == 0
    assert state["misfortune"] == 1

    state["misfortune"] = 0

    def noncritical_hit(target, **_kwargs):
        target.health.current -= 5
        return "hits.\n", True, 1

    monkeypatch.setattr(thief, "weapon_damage", noncritical_hit)
    abilities.Mug().use(thief, target)
    assert state["fortune"] == 0
    assert state["misfortune"] == 0


def test_troubadour_crescendo_coda_practice_and_encore_preservation():
    troubadour = _player("Troubadour", mana=(100, 100))
    troubadour.equipment["OffHand"] = items.Lute()
    _awaken_ring(troubadour, "Troubadour")

    ok, message = bard.start_song(troubadour, "Battle Hymn", target=enemies.Goblin())
    assert ok is True
    for _ in range(3):
        message += bard.tick_song(troubadour)

    state = promotion_kits.combat_state(troubadour)
    repertoire = promotion_kits.ensure_state(troubadour)["bard_repertoire"]["Battle Hymn"]
    assert "spends 3 Crescendo" in message
    assert "Encore preserves 1 spent crescendo" in message
    assert state["crescendo"] == 1
    assert repertoire["practice_xp"] == 6
    assert repertoire["clean_finishes"] == 1


def test_shared_recovery_scales_with_companion_bond():
    beast = _player("Beast Master")
    _awaken_ring(beast, "Beast Master")
    beast.tamed_companion = {"active": True, "bond": 100}

    assert class_rings.shared_recovery_amount(beast, 100) == 35
