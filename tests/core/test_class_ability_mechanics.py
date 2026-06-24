from types import SimpleNamespace

from src.core import abilities, enemies, items, map_tiles
from src.core.combat.battle_engine import BattleEngine
from src.core.save_system import PlayerDataSerializer
from tests.test_framework import TestGameState


class _Tile:
    enemy = None

    def available_actions(self, player):
        return player.additional_actions(["Attack", "Cast Spell", "Use Skill", "Use Item", "Flee"])

    def __str__(self):
        return "TestTile"


def test_monkey_grip_keeps_two_handed_weapon_and_offhand_weapon():
    player = TestGameState.create_player(class_name="Berserker", level=1)
    player.equipment["Weapon"] = items.Parashu()
    player.equipment["OffHand"] = items.Changdao()
    player.modify_inventory(items.Greataxe())

    assert player.equip("Weapon", items.Greataxe()) is True
    assert player.equipment["Weapon"].name == "Greataxe"
    assert player.equipment["OffHand"].name == "Changdao"

    base_main = player.check_mod("weapon")
    base_offhand = player.check_mod("offhand")
    player.spellbook["Skills"]["Monkey Grip"] = abilities.MonkeyGrip()
    assert player.check_mod("weapon") > base_main
    assert player.check_mod("offhand") > base_offhand

    stabilized_main = player.check_mod("weapon")
    stabilized_offhand = player.check_mod("offhand")
    player.spellbook["Skills"]["Monkey Grip 2"] = abilities.MonkeyGrip2()
    assert player.check_mod("weapon") == stabilized_main
    assert player.check_mod("offhand") > stabilized_offhand
    assert player.check_mod("offhand") < player.equipment["OffHand"].damage + player.combat.attack


def test_polearm_one_hand_progression_penalty_and_bonus():
    player = TestGameState.create_player(class_name="Lancer", level=1)
    player.equipment["Weapon"] = items.Halberd()
    player.equipment["OffHand"] = items.Glagwa()

    unrestricted = player.check_mod("weapon")
    player.spellbook["Skills"]["Polearm Proficiency"] = abilities.PolearmProficiency()
    penalized = player.check_mod("weapon")

    player.spellbook["Skills"].pop("Polearm Proficiency")
    player.spellbook["Skills"]["Polearm Excellence"] = abilities.PolearmExcellence()
    neutral = player.check_mod("weapon")

    player.spellbook["Skills"].pop("Polearm Excellence")
    player.spellbook["Skills"]["Polearm Mastery"] = abilities.PolearmMastery()
    mastered = player.check_mod("weapon")

    assert penalized < unrestricted
    assert neutral == unrestricted
    assert mastered > neutral


def test_tame_is_animal_only_and_round_trips_save(monkeypatch):
    player = TestGameState.create_player(class_name="Ranger", level=10, stats={"charisma": 40})
    rat = enemies.GiantRat()
    rat.health.current = 1

    monkeypatch.setattr("src.core.classes.ability_mechanics.random.random", lambda: 0.0)
    message = abilities.Tame().use(player, rat)

    assert "tames" in message
    assert player.tamed_companion["enemy_class"] == "GiantRat"
    assert player.familiar is not None

    restored = PlayerDataSerializer.deserialize(PlayerDataSerializer.serialize(player), skip_tiles=True)
    assert restored.tamed_companion["enemy_class"] == "GiantRat"
    assert restored.familiar.name == "Giant Rat"
    assert "cannot be tamed" in abilities.Tame().use(player, enemies.Owlbear())


def test_reagent_spells_consume_required_items_and_apply_effects(monkeypatch):
    player = TestGameState.create_player(class_name="Archdruid", level=30)
    target = enemies.Goblin()
    target.health.current = target.health.max = 500
    target.dodge_chance = lambda *_args, **_kwargs: 0.0
    monkeypatch.setattr("src.core.abilities.random.random", lambda: 1.0)
    monkeypatch.setattr("src.core.abilities.random.uniform", lambda _lo, _hi: 1.0)
    player.modify_inventory(items.Acorn())
    player.modify_inventory(items.VineSeed())
    player.modify_inventory(items.FungusSpore())
    player.modify_inventory(items.HemlockRoot())
    player.modify_inventory(items.FungusSpore())

    plant = abilities.PlantSeeds()
    assert "mighty oak" in plant.cast(player, target=target, reagent="Acorn").lower()
    assert "Acorn" not in player.inventory
    assert target.status_effects["Stun"].active is True
    target.status_effects["Stun"].active = False

    assert "vines" in plant.cast(player, target=target, reagent="Vine Seed")
    assert "Vine Seed" not in player.inventory
    assert target.physical_effects["Prone"].active is True

    assert "mushroom" in plant.cast(player, target=target, reagent="Fungus Spore")
    assert target.status_effects["Poison"].active is True

    vile = abilities.VilePotion()
    monkeypatch.setattr("src.core.abilities.random.random", lambda: 0.0)
    assert "poison" in vile.cast(player, target=target).lower()
    assert "Hemlock Root" not in player.inventory
    assert "Fungus Spore" not in player.inventory


def test_tree_of_life_is_growth_mastery_oak_form():
    from src.core.classes import archdruid

    player = TestGameState.create_player(class_name="Archdruid", level=30, health=(300, 100), mana=(200, 200))
    state = archdruid.default_state()
    state["aspects"]["Growth"] = True
    state["attunement"]["Growth"] = archdruid.MASTERY_THRESHOLD
    player.archdruid_attunement = state

    archdruid.apply_mastery_perks(player)

    assert "Tree of Life" in player.spellbook["Spells"]
    before_armor = player.check_mod("armor")
    before_mdef = player.check_mod("magic def")
    assert "giant oak" in abilities.TreeOfLife().cast(player)
    assert player.magic_effects["Tree of Life"].active is True
    assert player.check_mod("armor") > before_armor
    assert player.check_mod("magic def") > before_mdef
    assert player.has_status_protection("Stun") is True

    enemy = enemies.Goblin()
    tile = _Tile()
    tile.enemy = enemy
    engine = BattleEngine(player, enemy, tile)
    engine.attacker = player
    engine.defender = enemy
    assert "cannot attack" in engine.execute_action("Attack").message

    message = player.effects()
    assert "Tree of Life restores" in message
    assert player.health.current == 199


def test_ball_lightning_is_multihit_without_stun(monkeypatch):
    caster = TestGameState.create_player(class_name="Archdruid", level=30, mana=(200, 200))
    target = enemies.Goblin()
    target.health.current = target.health.max = 500
    target.dodge_chance = lambda *_args, **_kwargs: 0.0
    monkeypatch.setattr("src.core.abilities.random.random", lambda: 1.0)
    monkeypatch.setattr("src.core.abilities.random.uniform", lambda _lo, _hi: 1.0)

    message = abilities.BallLightning().cast(caster, target=target)

    assert message.count("damages") == 3
    assert target.status_effects["Stun"].active is False


def test_calming_breeze_blocks_berserk_but_cannot_be_cast_while_berserk():
    player = TestGameState.create_player(class_name="Druid", level=20, mana=(200, 200))
    player.status_effects["Berserk"].active = True
    player.status_effects["Berserk"].duration = 2

    message = abilities.CalmingBreeze().cast(player, player)

    assert "too berserk" in message
    assert player.status_effects["Peaceful"].active is False

    player.status_effects["Berserk"].active = False
    assert "steadies" in abilities.CalmingBreeze().cast(player, player)
    abilities.Berserk().cast(player, target=player)
    assert player.status_effects["Berserk"].active is False


def test_defensive_regen_heals_while_defending():
    player = TestGameState.create_player(class_name="Priest", level=20, health=(100, 50))
    player.spellbook["Skills"]["Defensive Regen"] = abilities.DefensiveRegen()
    player.enter_defensive_stance(duration=2)

    message = player.effects()

    assert "defensive focus restores" in message
    assert player.health.current > 50


def test_foretell_and_rewind_restore_combat_snapshot():
    from src.core.classes import ability_mechanics

    player = TestGameState.create_player(class_name="Astromancer", level=30)
    enemy = enemies.Goblin()
    enemy.action_stack = [{"ability": "Stab", "weight": 100}]
    tile = _Tile()
    tile.enemy = enemy
    engine = BattleEngine(player, enemy, tile)
    engine.attacker = player
    engine.defender = enemy

    assert "next action: Stab" in abilities.Foretell().cast(player, target=enemy, battle_engine=engine)
    ability_mechanics.store_rewind_snapshot(engine)
    player.health.current -= 50
    enemy.health.current = 1

    assert "previous choice point" in abilities.Rewind().cast(player, target=enemy, battle_engine=engine)
    assert player.health.current == player.health.max
    assert enemy.health.current == enemy.health.max


def test_exploration_spells_affect_fire_path_and_wall_movement():
    player = TestGameState.create_player(class_name="Seeker", level=20)
    game = SimpleNamespace(player_char=player, _random_combat=False)
    player.location_x = 0
    player.location_y = 0
    player.location_z = 0
    player.world_dict = {
        (0, 0, 0): map_tiles.CavePath(0, 0, 0),
        (1, 0, 0): map_tiles.Wall(1, 0, 0),
    }

    assert "rises" in abilities.Volitation().cast_out(player)
    health = player.health.current
    map_tiles.FirePath(0, 0, 0).modify_player(game)
    assert player.health.current == health

    assert "stone" in abilities.EnterWall().cast_out(player)
    assert player.move(1, 0) is True
    assert (player.location_x, player.location_y) == (1, 0)


def test_steal_spell_2_learns_spell_without_scroll(monkeypatch):
    player = TestGameState.create_player(class_name="Arcane Trickster", level=20)
    target = enemies.Goblin()
    target.spellbook["Spells"]["Firebolt"] = abilities.Firebolt()

    monkeypatch.setattr("src.core.abilities.random.random", lambda: 0.0)
    monkeypatch.setattr("src.core.abilities.random.choice", lambda values: values[0])

    message = abilities.StealSpell2().use(player, target)

    assert "permanently learns" in message
    assert "Firebolt" in [getattr(spell, "_class_name", spell.__class__.__name__) for spell in player.spellbook["Spells"].values()]
    assert "Stolen Firebolt Scroll" not in player.inventory


def test_sheet_music_composes_and_performs_one_use_song():
    from src.core.classes import bard

    player = TestGameState.create_player(class_name="Bard", level=20)
    player.equipment["OffHand"] = items.Lute()

    success, message = bard.compose_sheet_music(player, "Battle Hymn")
    assert success is True
    assert "Sheet Music: Battle Hymn" in player.inventory
    sheet = player.inventory["Sheet Music: Battle Hymn"][0]

    use_message = sheet.use(player)

    assert "Song of Battle Hymn" in use_message
    assert "Sheet Music: Battle Hymn" not in player.inventory
    assert player.bard_song["active"] == "Battle Hymn"


def test_composable_song_effects_apply_in_combat_and_exploration(monkeypatch):
    from src.core.classes import bard

    player = TestGameState.create_player(class_name="Troubadour", level=30)
    enemy = enemies.Goblin()
    tile = _Tile()
    tile.enemy = enemy
    engine = BattleEngine(player, enemy, tile)

    battle_hymn = items.BattleHymnSheet()
    player.modify_inventory(battle_hymn)
    assert "battle frenzy" in battle_hymn.use(player, target=enemy)
    assert player.status_effects["Berserk"].active is True
    assert enemy.status_effects["Berserk"].active is True

    player.status_effects["Berserk"].active = False
    ramparts = items.RampartsOdeSheet()
    player.modify_inventory(ramparts)
    message = ramparts.use(player, target=enemy)
    assert "raises" in message
    assert player.stat_effects["Defense"].active is True
    assert player.stat_effects["Magic Defense"].active is True

    symphony = items.DysfunctionSymphonySheet()
    player.modify_inventory(symphony)
    assert symphony.use(player, target=enemy)
    assert bard.active_exploration_effect(player) == "enemy_attack_down"
    engine.start_battle()
    assert enemy.stat_effects["Attack"].active is True
    assert enemy.stat_effects["Magic"].active is True

    player.bard_song = {"active": "Chorus Time", "turns": 3, "encore": None}
    engine.attacker = enemy
    engine.defender = player
    rolls = iter([100, 1])
    monkeypatch.setattr("src.core.combat.battle_engine.random.randint", lambda _lo, _hi: next(rolls))
    pre = engine.pre_turn()
    assert pre.can_act is False
    assert "Chorus Time" in pre.effects_text


def test_composition_requires_matching_instrument():
    from src.core.classes import bard

    player = TestGameState.create_player(class_name="Bard", level=20)
    player.equipment["OffHand"] = items.Lute()

    success, message = bard.compose_sheet_music(player, "Chorus Time")

    assert success is False
    assert "GrandPiano" in message
    assert "Sheet Music: Chorus Time" not in player.inventory


def test_class_power_ups_have_runtime_effects():
    from src.core.classes import grandmaster

    trickster = TestGameState.create_player(class_name="Arcane Trickster", level=30)
    trickster.spellbook["Skills"]["Trickster's Gambit"] = abilities.TrickstersGambit()
    trickster.class_effects["Power Up"].active = True
    trickster.class_effects["Power Up"].duration = 3
    trickster.power_up = True
    assert trickster.check_mod("magic") > TestGameState.create_player(class_name="Arcane Trickster", level=30).check_mod("magic")
    assert trickster.critical_chance("Weapon") > 0

    archdruid = TestGameState.create_player(class_name="Archdruid", level=30)
    archdruid.spellbook["Skills"]["Primal Ascendance"] = abilities.PrimalAscendance()
    archdruid.class_effects["Power Up"].active = True
    archdruid.class_effects["Power Up"].duration = 3
    archdruid.power_up = True
    base_heal = TestGameState.create_player(class_name="Archdruid", level=30).check_mod("heal")
    assert archdruid.check_mod("heal") > base_heal

    demonologist = TestGameState.create_player(class_name="Demonologist", level=30)
    demonologist.spellbook["Skills"]["Abyssal Covenant"] = abilities.AbyssalCovenant()
    demonologist.class_effects["Power Up"].active = True
    demonologist.class_effects["Power Up"].duration = 3
    demonologist.power_up = True
    assert demonologist.check_mod("magic") > TestGameState.create_player(class_name="Demonologist", level=30).check_mod("magic")

    grandmaster_pc = TestGameState.create_player(class_name="Grandmaster of Arms", level=30)
    grandmaster_pc.spellbook["Skills"]["Arsenal Mastery"] = abilities.ArsenalMastery()
    grandmaster_pc.power_up = True
    grandmaster_pc.class_effects["Power Up"].active = True
    grandmaster_pc.class_effects["Power Up"].duration = 3
    state = grandmaster.default_state()
    state["disciplines"]["Sword"]["xp"] = 500
    state["disciplines"]["Sword"]["rank"] = 10
    grandmaster_pc.grandmaster_discipline = state
    assert grandmaster_pc.check_mod("weapon") > TestGameState.create_player(class_name="Grandmaster of Arms", level=30).check_mod("weapon")


def test_passive_power_ups_support_defender_troubadour_and_beast_master():
    defender = TestGameState.create_player(class_name="Stalwart Defender", level=30)
    defender.spellbook["Skills"]["Shield Mastery"] = abilities.ShieldMastery()
    defender.power_up = True
    assert defender.check_mod("shield") >= 25

    troubadour = TestGameState.create_player(class_name="Troubadour", level=30, stats={"dex": 40})
    troubadour.spellbook["Skills"]["Melody of Inspiration"] = abilities.MelodyInspiration()
    troubadour.power_up = True
    base_speed = TestGameState.create_player(class_name="Troubadour", level=30, stats={"dex": 40}).check_mod("speed")
    assert troubadour.check_mod("speed") > base_speed

    beast = TestGameState.create_player(class_name="Beast Master", level=30)
    beast.spellbook["Skills"]["Pack Bond"] = abilities.PackBond()
    beast.power_up = True
    beast.familiar = SimpleNamespace(is_alive=lambda: True, health=SimpleNamespace(current=10, max=20))
    base_weapon = TestGameState.create_player(class_name="Beast Master", level=30).check_mod("weapon")
    assert beast.check_mod("weapon") > base_weapon


def test_bad_breath_applies_enemy_only_status_package():
    user = enemies.Basilisk()
    target = TestGameState.create_player(class_name="Warrior", level=10)

    message = abilities.BadBreath().use(user, target)

    assert "poison" in message.lower()
    assert target.status_effects["Poison"].active is True
    assert target.status_effects["Blind"].active is True
    assert target.status_effects["Silence"].active is True
