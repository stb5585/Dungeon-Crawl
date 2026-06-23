"""Main storyline progression state helpers."""

from __future__ import annotations

from copy import deepcopy


GUARDIAN_TRIALS = (
    "Triangulus",
    "Quadrata",
    "Hexagonum",
    "Luna",
    "Polaris",
    "Infinitas",
)

GUARDIAN_TRIAL_CHOICES = {
    "Triangulus": ("Name", "Body", "Memory"),
    "Quadrata": ("Obey", "Resist", "Rewrite"),
    "Hexagonum": ("Root", "Fang", "River"),
    "Luna": ("Protect", "Release", "Share"),
    "Polaris": ("Trust", "Question", "Remember"),
    "Infinitas": ("Endure", "Break", "Rest"),
}

GUARDIAN_CLUE_MEANINGS = {
    "Triangulus": "selfhood is chosen, not assigned",
    "Quadrata": "order without consent becomes tyranny",
    "Hexagonum": "instinct begins life, but does not define meaning",
    "Luna": "love without freedom becomes possession or obligation",
    "Polaris": "guidance must invite, not command",
    "Infinitas": "endurance only has meaning when stopping or continuing is a choice",
}

DEFAULT_MAIN_STORY_STATE = {
    "vesperion_false_final_triggered": False,
    "pending_liminal_gap_entry": False,
    "liminal_gap_entered": False,
    "liminal_gap_guide_revealed": False,
    "liminal_gap_guide_save_used": False,
    "liminal_gap_clues_reviewed": False,
    "guardian_trials_started": {
        guardian: False
        for guardian in GUARDIAN_TRIALS
    },
    "guardian_trials_completed": {
        guardian: False
        for guardian in GUARDIAN_TRIALS
    },
    "guardian_trial_choices": {
        guardian: None
        for guardian in GUARDIAN_TRIALS
    },
    "voluntas_clues_found": {
        guardian: False
        for guardian in GUARDIAN_TRIALS
    },
    "voluntas_revealed": False,
    "seventh_seat_revealed": False,
    "acolyte_liminal_seen": False,
    "reflection_attempts": 0,
    "reflection_failures": 0,
    "reflection_defeated": False,
    "returned_from_liminal_gap": False,
    "hooded_figure_witness_revealed": False,
    "true_final_unlocked": False,
    "vesperion_true_final_defeated": False,
    "main_story_complete": False,
}


def default_state() -> dict[str, object]:
    """Return a fresh main-story state dictionary."""
    return deepcopy(DEFAULT_MAIN_STORY_STATE)


def normalize_state(state: object = None) -> dict[str, object]:
    """Return a backward-compatible main-story progression dictionary."""
    normalized = default_state()
    if isinstance(state, dict):
        for key in DEFAULT_MAIN_STORY_STATE:
            if key in {"guardian_trials_started", "guardian_trials_completed", "voluntas_clues_found"}:
                saved_trials = state.get(key, {})
                if isinstance(saved_trials, dict):
                    normalized[key] = {
                        guardian: bool(saved_trials.get(guardian, False))
                        for guardian in GUARDIAN_TRIALS
                    }
                continue
            if key == "guardian_trial_choices":
                saved_choices = state.get(key, {})
                if isinstance(saved_choices, dict):
                    normalized[key] = {
                        guardian: saved_choices.get(guardian)
                        if saved_choices.get(guardian) in GUARDIAN_TRIAL_CHOICES[guardian]
                        else None
                        for guardian in GUARDIAN_TRIALS
                    }
                continue
            if key in {"reflection_attempts", "reflection_failures"}:
                try:
                    normalized[key] = max(0, int(state.get(key, normalized[key])))
                except (TypeError, ValueError):
                    normalized[key] = 0
                continue
            normalized[key] = bool(state.get(key, normalized[key]))
    return normalized


def ensure_state(player) -> dict[str, object]:
    """Attach normalized main-story state to a player and return it."""
    player.main_story = normalize_state(getattr(player, "main_story", None))
    return player.main_story


def all_guardian_trials_completed(story_state: dict[str, object]) -> bool:
    """Return whether every Guardian trial has been completed."""
    completed = story_state.get("guardian_trials_completed", {})
    return isinstance(completed, dict) and all(completed.get(guardian) for guardian in GUARDIAN_TRIALS)


def all_voluntas_clues_found(story_state: dict[str, object]) -> bool:
    """Return whether every Guardian Voluntas clue has been found."""
    clues = story_state.get("voluntas_clues_found", {})
    return isinstance(clues, dict) and all(clues.get(guardian) for guardian in GUARDIAN_TRIALS)


def completed_guardian_count(story_state: dict[str, object]) -> int:
    """Return how many Guardian trials have been completed."""
    completed = story_state.get("guardian_trials_completed", {})
    if not isinstance(completed, dict):
        return 0
    return sum(1 for guardian in GUARDIAN_TRIALS if completed.get(guardian))


def guardian_clue_summary(story_state: dict[str, object]) -> list[str]:
    """Return readable summaries for each awakened Guardian clue."""
    clues = story_state.get("voluntas_clues_found", {})
    choices = story_state.get("guardian_trial_choices", {})
    if not isinstance(clues, dict):
        clues = {}
    if not isinstance(choices, dict):
        choices = {}

    summaries: list[str] = []
    for guardian in GUARDIAN_TRIALS:
        if not clues.get(guardian):
            continue
        choice = choices.get(guardian)
        choice_text = f" ({choice})" if choice else ""
        summaries.append(f"{guardian}{choice_text}: {GUARDIAN_CLUE_MEANINGS[guardian]}.")
    return summaries


def can_reveal_voluntas(story_state: dict[str, object]) -> bool:
    """Return whether the Seventh Seat can reveal Voluntas."""
    return all_guardian_trials_completed(story_state) and all_voluntas_clues_found(story_state)


def can_unlock_true_final(story_state: dict[str, object]) -> bool:
    """Return whether the true final path has all narrative prerequisites."""
    return bool(story_state.get("voluntas_revealed") and story_state.get("reflection_defeated"))
