"""Regression coverage for the authored Bard and Troubadour trees."""

from src.core import abilities, enemies, items
from src.core.classes import bard, promotion_kits
from src.core.progression import ABILITY_TREES, NodeKind, ProgressionState
from tests.test_framework import TestGameState


def _performer(class_name: str, level: int):
    player = TestGameState.create_player(class_name=class_name, level=level)
    player.progression = ProgressionState(level=level)
    player.equipment["OffHand"] = items.Lute()
    return player


def _grant(player, *talent_keys: str) -> None:
    talents = {
        node.payload["talent_key"]: node
        for tree_name in ("Bard", "Troubadour")
        for node in ABILITY_TREES[tree_name].nodes
        if node.kind == NodeKind.TALENT
    }
    for key in talent_keys:
        player.progression.purchased_node_ids.add(talents[key].id)


def test_bard_tree_has_twenty_six_development_nodes_and_four_promotion_routes():
    tree = ABILITY_TREES["Bard"]
    development = [node for node in tree.nodes if node.kind != NodeKind.PROMOTION]
    promotion = next(node for node in tree.nodes if node.kind == NodeKind.PROMOTION)
    ids = {node.id for node in tree.nodes}

    assert len(development) == 26
    assert tree.branches == ("Performance", "Composition")
    assert {
        "bard.ability.songvalor",
        "bard.ability.songshelter",
        "bard.ability.songrenewal",
        "bard.ability.kaleidoscope",
        "bard.ability.inspiring-verse",
        "bard.ability.dissonant-chord",
        "bard.ability.prismatic-ray",
        "bard.ability.rhythmic-strike",
        "bard.ability.curtain-guard",
    } <= ids
    assert "bard.ability.compose" not in ids
    assert promotion.payload["prerequisite_mode"] == "any"
    assert len(promotion.prerequisites) == 4


def test_bard_rows_follow_first_promotion_level_bands_and_fit_eight_rows():
    tree = ABILITY_TREES["Bard"]
    expected_levels = {1: 35, 2: 40, 3: 45, 4: 50, 5: 55}

    assert max(node.position[1] for node in tree.nodes) == 7
    for node in tree.nodes:
        row = node.position[1]
        if node.kind == NodeKind.PROMOTION:
            assert row == 7
        elif row == 0:
            assert "level_requirement" not in node.payload
        else:
            assert node.payload["level_requirement"] == expected_levels[row]

    battle_arrangement = next(
        node for node in tree.nodes if node.name == "Battle Arrangement"
    )
    assert battle_arrangement.position == (3, 0)


def test_troubadour_tree_has_twenty_seven_authored_terminal_nodes():
    tree = ABILITY_TREES["Troubadour"]

    assert len(tree.nodes) == 27
    assert tree.branches == ("Finale", "Mastery")
    assert not any(node.kind == NodeKind.PROMOTION for node in tree.nodes)
    assert "troubadour.ability.grand-finale" in {node.id for node in tree.nodes}
    assert {
        "Rallying Chorus",
        "Resonant Wave",
        "Prismatic Finale",
        "Syncopated Strike",
        "Countermelody",
    } <= {node.name for node in tree.nodes}
    assert "Cutting Refrain" in {node.name for node in tree.nodes}
    assert "Cutting Encore" not in {node.name for node in tree.nodes}


def test_compose_is_inherent_and_selects_matching_custom_song():
    performer = _performer("Bard", 60)
    message = bard.compose_sheet_music(performer, "Battle Hymn")[1]

    assert abilities.Compose not in abilities.skill_dict["Bard"].values()
    assert not any(node.name == "Compose" for node in ABILITY_TREES["Bard"].nodes)
    assert "composes Battle Hymn" in message
    assert "Sheet Music: Battle Hymn" in performer.inventory


def test_kaleidoscope_emerald_mist_restores_health_and_vivid_mana():
    performer = _performer("Bard", 60)
    performer.health.current = max(1, performer.health.max // 2)
    performer.mana.current = max(20, performer.mana.max // 2)
    _grant(performer, "bard.vivid-palette")

    class EmeraldRng:
        @staticmethod
        def choice(_values):
            return "Emerald"

    before_hp = performer.health.current
    before_mp = performer.mana.current
    message = abilities.Kaleidoscope().cast(
        performer,
        enemies.Goblin(),
        rng=EmeraldRng(),
    )

    assert "blooms Emerald" in message
    assert performer.health.current > before_hp
    assert performer.mana.current > before_mp - 12


def test_bard_performance_talents_extend_song_and_preserve_transition_meter():
    performer = _performer("Bard", 60)
    _grant(
        performer,
        "bard.sustained-performance",
        "bard.seamless-transition",
        "bard.crescendo-reserve",
    )

    bard.start_song(performer, "Valor")
    promotion_kits.combat_state(performer)["crescendo"] = 3
    _success, message = bard.start_song(performer, "Shelter")

    assert bard.ensure_song_state(performer)["turns"] == 4
    assert promotion_kits.combat_state(performer)["crescendo"] == 1
    assert "Seamless Transition" in message
    assert promotion_kits.cap_for(performer, "crescendo") == 4


def test_grand_finale_spends_crescendo_now_and_decisive_ending_reduces_cost():
    performer = _performer("Troubadour", 90)
    _grant(performer, "troubadour.decisive-ending")
    bard.start_song(performer, "Valor")
    promotion_kits.combat_state(performer)["crescendo"] = 3
    before_mp = performer.mana.current

    message = abilities.GrandFinale().use(performer)

    assert "ends Song of Valor with Grand Finale" in message
    assert "spends 3 Crescendo" in message
    assert bard.active_song(performer) is None
    assert performer.mana.current == before_mp - 6


def test_troubadour_mastery_talents_accelerate_practice_without_skipping_finishes():
    performer = _performer("Troubadour", 90)
    _grant(
        performer,
        "troubadour.composers-memory",
        "troubadour.practiced-ear",
        "troubadour.flawless-form",
    )

    _success, message = bard.compose_sheet_music(performer, "Battle Hymn")
    bard.start_song(performer, "Battle Hymn")
    for _ in range(3):
        message += bard.tick_song(performer)
    entry = promotion_kits.ensure_state(performer)["bard_repertoire"]["Battle Hymn"]

    assert "2 practice XP from composition" in message
    assert entry["practice_xp"] == 13
    assert entry["clean_finishes"] == 1
    assert entry["known"] is False


def test_bard_support_attack_and_defense_actions_preserve_active_song(monkeypatch):
    performer = _performer("Bard", 60)
    bard.start_song(performer, "Valor")
    target = enemies.Goblin()

    support = abilities.InspiringVerse().cast(performer)
    guard = abilities.CurtainGuard().use(performer)

    def weapon_hit(enemy, **_kwargs):
        enemy.health.current -= 9
        return "Rhythmic hit.\n", True, 1

    monkeypatch.setattr(performer, "weapon_damage", weapon_hit)
    strike = abilities.RhythmicStrike().use(performer, target)

    assert support.hit is True
    assert performer.stat_effects["Attack"].active is True
    assert guard.hit is True
    assert performer.stat_effects["Defense"].active is True
    assert strike.damage == 9
    assert bard.active_song(performer) == "Valor"
    assert promotion_kits.combat_state(performer)["crescendo"] == 3


def test_prismatic_finale_spends_crescendo_for_elemental_damage(monkeypatch):
    performer = _performer("Troubadour", 90)
    target = enemies.Goblin()
    promotion_kits.combat_state(performer)["crescendo"] = 3

    def spell_hit(_user, enemy, *, dmg_mod, typ):
        damage = int(10 * dmg_mod)
        enemy.health.current -= damage
        return f"{typ} hits.\n", damage

    monkeypatch.setattr("src.core.abilities.bard._simple_spell_damage", spell_hit)

    class FireRng:
        @staticmethod
        def choice(_values):
            return "Fire"

    result = abilities.PrismaticFinale().cast(performer, target, rng=FireRng())

    assert result.damage == 15
    assert result.extra == {"cost": 18, "type": "Spell", "subtype": "Elemental", "element": "Fire", "crescendo_spent": 3}
    assert promotion_kits.combat_state(performer)["crescendo"] == 0


def test_troubadour_support_untyped_and_defense_actions(monkeypatch):
    performer = _performer("Troubadour", 90)
    performer.health.current -= 20
    target = enemies.Goblin()

    chorus = abilities.RallyingChorus().cast(performer)
    promotion_kits.combat_state(performer)["crescendo"] = 2
    ward = abilities.Countermelody().use(performer)

    def spell_hit(_user, enemy, *, dmg_mod, typ):
        del dmg_mod
        enemy.health.current -= 12
        return f"{typ} hits.\n", 12

    monkeypatch.setattr("src.core.abilities.bard._simple_spell_damage", spell_hit)
    wave = abilities.ResonantWave().cast(performer, target)

    assert chorus.healing > 0
    assert ward.hit is True
    assert performer.magic_effects["Nature Shield"].active is True
    assert wave.damage == 12
    assert target.stat_effects["Attack"].active is True
    assert target.stat_effects["Magic"].active is True
