from src.core import abilities, enemies
from tests.test_framework import TestGameState


def _make_player():
    return TestGameState.create_player(
        name="ChoiceBearer",
        class_name="Warrior",
        race_name="Human",
        level=40,
        health=(1000, 1000),
        mana=(500, 500),
        stats={"strength": 45, "intel": 35, "wisdom": 35, "con": 40, "charisma": 30, "dex": 30},
    )


def test_balor_does_not_use_choose_fate():
    balor = enemies.Balor()

    assert "Choose Fate" not in balor.spellbook["Skills"]
    assert all(entry["ability"] != "Choose Fate" for entry in balor.action_stack)


def test_vesperion_owns_distinct_choose_fate_and_relic_counters():
    vesperion = enemies.Vesperion()

    assert vesperion.enemy_typ == "Celestial"
    assert "Choose Fate" in vesperion.spellbook["Skills"]
    assert isinstance(vesperion.spellbook["Skills"]["Choose Fate"], abilities.Skill)
    assert vesperion.spellbook["Skills"]["Choose Fate"]._class_name == "VesperionChooseFate"
    assert vesperion.relic_counter_for("Triangulus") == "identity overwrite"
    assert vesperion.relic_counter_for("Infinitas") == "endurance loops"


def test_vesperion_choose_fate_phase_one_damage_choice():
    vesperion = enemies.Vesperion()
    player = _make_player()
    captured = {}

    before = player.health.current
    message = vesperion.spellbook["Skills"]["Choose Fate"].use(
        vesperion,
        player,
        selection_callback=lambda prompt, options: captured.update(prompt=prompt, options=options) or 0,
    )

    assert vesperion.vesperion_phase() == 1
    assert captured["options"] == ["Bear the Wound", "Spend the Breath", "Accept Stillness"]
    assert "Vesperion offers a terrible choice: Bear the Wound." in message
    assert player.health.current < before


def test_vesperion_choose_fate_damage_relic_counter_mitigates_wound():
    vesperion = enemies.Vesperion()
    uncountered = _make_player()
    countered = _make_player()
    countered.main_story["guardian_trials_completed"]["Hexagonum"] = True

    vesperion.spellbook["Skills"]["Choose Fate"].use(
        vesperion,
        uncountered,
        selection_callback=lambda _prompt, _options: 0,
    )
    message = vesperion.spellbook["Skills"]["Choose Fate"].use(
        vesperion,
        countered,
        selection_callback=lambda _prompt, _options: 0,
    )

    uncountered_damage = uncountered.health.max - uncountered.health.current
    countered_damage = countered.health.max - countered.health.current
    assert countered_damage < uncountered_damage
    assert "Hexagonum answers the Evening Star" in message


def test_vesperion_choose_fate_phase_two_resource_choice():
    vesperion = enemies.Vesperion()
    vesperion.health.current = int(vesperion.health.max * 0.5)
    player = _make_player()
    captured = {}

    before = player.mana.current
    message = vesperion.spellbook["Skills"]["Choose Fate"].use(
        vesperion,
        player,
        selection_callback=lambda prompt, options: captured.update(prompt=prompt, options=options) or 1,
    )

    assert vesperion.vesperion_phase() == 2
    assert captured["options"] == ["Carry the Hurt", "Lose the Voice", "Yield the Moment"]
    assert "Vesperion offers a terrible choice: Lose the Voice." in message
    assert player.mana.current < before


def test_vesperion_choose_fate_phase_three_control_choice():
    vesperion = enemies.Vesperion()
    vesperion.health.current = int(vesperion.health.max * 0.2)
    player = _make_player()
    captured = {}

    message = vesperion.spellbook["Skills"]["Choose Fate"].use(
        vesperion,
        player,
        selection_callback=lambda prompt, options: captured.update(prompt=prompt, options=options) or 2,
    )

    assert vesperion.vesperion_phase() == 3
    assert captured["options"] == ["Suffer and Stand", "Empty the Self", "Be Written Over"]
    assert "Vesperion offers a terrible choice: Be Written Over." in message
    assert player.status_effects["Silence"].active is True
    assert player.status_effects["Silence"].duration == 3


def test_vesperion_choose_fate_identity_counter_cancels_overwrite():
    vesperion = enemies.Vesperion()
    vesperion.health.current = int(vesperion.health.max * 0.2)
    player = _make_player()
    player.main_story["guardian_trials_completed"]["Triangulus"] = True

    message = vesperion.spellbook["Skills"]["Choose Fate"].use(
        vesperion,
        player,
        selection_callback=lambda _prompt, _options: 2,
    )

    assert "Triangulus answers the Evening Star" in message
    assert player.status_effects["Silence"].active is False


def test_vesperion_phase_pressure_uses_all_guardian_counter_pairs():
    vesperion = enemies.Vesperion()
    player = _make_player()

    phase_one = vesperion.apply_phase_pressure(player)

    assert "Twilight attrition burns ChoiceBearer for 80 HP." in phase_one
    assert "Mercy without freedom drains 40 MP." in phase_one
    assert player.health.current == 920
    assert player.mana.current == 460
    assert vesperion.apply_phase_pressure(player) == ""

    player.main_story["guardian_trials_completed"]["Quadrata"] = True
    vesperion.health.current = int(vesperion.health.max * 0.5)
    phase_two = vesperion.apply_phase_pressure(player)

    assert "Quadrata breaks the forced order" in phase_two
    assert player.status_effects["Silence"].active is False
    assert player.status_effects["Blind"].active is True

    player.main_story["guardian_trials_completed"]["Triangulus"] = True
    player.main_story["guardian_trials_completed"]["Infinitas"] = True
    player.status_effects["Blind"].active = False
    vesperion.health.current = int(vesperion.health.max * 0.2)
    hp_before = player.health.current
    phase_three = vesperion.apply_phase_pressure(player)

    assert "Triangulus holds the self" in phase_three
    assert "Infinitas turns the endless loop" in phase_three
    assert player.status_effects["Silence"].active is False
    assert player.health.current == hp_before


def test_reflection_psychopomp_is_liminal_no_reward_enemy():
    reflection = enemies.ReflectionPsychopomp()
    player = _make_player()

    reflection.mirror_player(player)

    assert reflection.enemy_typ == "Liminal"
    assert reflection.reflection_psychopomp is True
    assert reflection.experience == 0
    assert reflection.health.max >= 600
    assert "Ruin" in reflection.spellbook["Spells"]


def test_reflection_psychopomp_records_mirrored_path_profile():
    martial = _make_player()
    martial.name = "BladePath"
    martial.cls.name = "Grandmaster of Arms"
    martial.combat.attack = 160
    martial.combat.magic = 10
    reflection = enemies.ReflectionPsychopomp()

    reflection.mirror_player(martial)

    assert reflection.mirrored_path == {
        "class": "Grandmaster of Arms",
        "profile": "martial",
        "level": 40,
    }
    assert reflection.resistance["Physical"] == 0.4
    assert reflection.action_stack[0]["ability"] == "Attack"
    assert reflection.action_stack[0]["priority"] == enemies.ActionPriority.HIGH

    mystic = _make_player()
    mystic.cls.name = "Wizard"
    mystic.combat.attack = 10
    mystic.combat.magic = 180
    mystic_reflection = enemies.ReflectionPsychopomp()

    mystic_reflection.mirror_player(mystic)

    assert mystic_reflection.mirrored_path["profile"] == "mystic"
    assert [entry["ability"] for entry in mystic_reflection.action_stack[:2]] == ["Holy II", "Ruin"]
