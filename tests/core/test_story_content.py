#!/usr/bin/env python3
"""Coverage for shared story content loaded from core data."""

from src.core import main_story
from src.core.data.data_loader import clear_cache, get_intro_story, get_special_events


def test_new_game_intro_story_content_is_shared_and_spoiler_safe():
    clear_cache()

    pages = get_intro_story()
    intro_text = "\n".join(pages)

    assert len(pages) == 6
    for expected in ("Silvana", "relics", "guardians", "Step below"):
        assert expected in intro_text
    for spoiler in ("Vesperion", "Voluntas", "busboy", "Hooded Figure", "true final"):
        assert spoiler not in intro_text


def test_story_polish_content_keys_are_present_and_spoiler_scoped():
    clear_cache()

    events = get_special_events()
    required_keys = (
        "Triangulus Trial Defeat",
        "Infinitas Trial Defeat",
        "Reflection Prelude Martial",
        "Reflection Prelude Mystic",
        "Reflection Prelude Hybrid",
        "Reflection Victory Martial",
        "Reflection Victory Mystic",
        "Reflection Victory Hybrid",
        "Reflection Defeat Martial",
        "Reflection Defeat Mystic",
        "Reflection Defeat Hybrid",
        "Hooded Figure Angelic Confirmation",
        "Class Voluntas Affirmation",
        "Class Voluntas Dormant Ring",
        "Class Voluntas Awakened Ring",
        "Class Voluntas Reflection Echo",
        "Class Voluntas Archetype Martial",
        "Class Voluntas Archetype Mystic",
        "Class Voluntas Archetype Hybrid",
        "Class Voluntas Archetype Companion",
        "Class Voluntas Archetype Shadow",
        "Class Voluntas Archetype Wanderer",
        "Class Voluntas Followup",
        "Class Voluntas Followup Martial",
        "Class Voluntas Followup Mystic",
        "Class Voluntas Followup Hybrid",
        "Class Voluntas Followup Companion",
        "Class Voluntas Followup Shadow",
        "Class Voluntas Followup Wanderer",
        "Reflection Voluntas Choice Claim",
        "Reflection Voluntas Choice Carry",
        "Reflection Voluntas Choice Choose Again",
        "Reflection Voluntas Retry",
        "Reflection Voluntas Victory Echo",
        "Reflection Path Mirror",
        "Reflection Path Victory Echo",
        "Hooded Figure Witness Farewell",
        "Vesperion Choice Argument",
        "Vesperion Tragedy Reframing",
        "Vesperion True Final Victory",
    )
    for key in required_keys:
        assert events.get(key, {}).get("Text"), key

    for guardian, choices in main_story.GUARDIAN_TRIAL_CHOICES.items():
        assert events.get(f"{guardian} Trial V2 Threshold", {}).get("Text"), guardian
        for choice in choices:
            key = f"{guardian} Trial V2 {choice}"
            assert events.get(key, {}).get("Text"), key
    assert events.get("Liminal Trial V2 Review", {}).get("Text")

    early_tragedy_text = "\n".join(
        line
        for key in ("Dead Body", "Waitress", "Joffrey's Key", "Busboy")
        for line in events[key]["Text"]
    )
    for spoiler in ("Vesperion", "Voluntas", "true final"):
        assert spoiler not in early_tragedy_text
    assert "grief" in early_tragedy_text
    assert "Joffrey" in early_tragedy_text

    endgame_tragedy_text = "\n".join(events["Vesperion Tragedy Reframing"]["Text"])
    assert "Vesperion" in endgame_tragedy_text
    assert "Joffrey" in endgame_tragedy_text
    assert "Waitress" in endgame_tragedy_text
