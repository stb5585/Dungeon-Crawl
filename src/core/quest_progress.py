"""Shared quest progression helpers for staged story quests."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

UNCERTAIN_REPORTS = "Uncertain Reports"
HOLY_RELICS = "The Holy Relics"
RELIC_NAMES = (
    "Triangulus",
    "Quadrata",
    "Hexagonum",
    "Luna",
    "Polaris",
    "Infinitas",
)


def ensure_quest_categories(player) -> dict[str, dict]:
    """Return a normalized quest dictionary with core categories present."""
    quest_dict = getattr(player, "quest_dict", None)
    if not isinstance(quest_dict, dict):
        quest_dict = {}
        player.quest_dict = quest_dict
    for category in ("Main", "Side", "Bounty"):
        if not isinstance(quest_dict.get(category), dict):
            quest_dict[category] = {}
    return quest_dict


def _complete_matching_side_quests(player, quest_type: str, predicate) -> str:
    """Complete active side quests of ``quest_type`` accepted by ``player``."""
    completed: list[str] = []
    for quest_name, quest_data in ensure_quest_categories(player)["Side"].items():
        if (
            isinstance(quest_data, dict)
            and quest_data.get("Type") == quest_type
            and not quest_data.get("Completed")
            and not quest_data.get("Turned In")
            and predicate(quest_data)
        ):
            quest_data["Completed"] = True
            completed.append(quest_name)
    return "".join(f"You have completed the quest {name}.\n" for name in completed)


def record_location(player, position: tuple[int, int, int]) -> str:
    """Record arrival at a location for active data-driven locate quests."""
    normalized_position = tuple(position)

    def matches(quest_data: dict[str, Any]) -> bool:
        target = quest_data.get("Target Position")
        return isinstance(target, (list, tuple)) and tuple(target) == normalized_position

    return _complete_matching_side_quests(player, "Locate", matches)


def record_conversation(player, npc_name: str) -> str:
    """Record a conversation for active data-driven town dialogue quests."""
    return _complete_matching_side_quests(
        player,
        "Talk",
        lambda quest_data: quest_data.get("What") == npc_name,
    )


def relic_count(player) -> int:
    """Return how many of the six major relics the player currently carries."""
    inventory = getattr(player, "special_inventory", {}) or {}
    return sum(1 for relic_name in RELIC_NAMES if relic_name in inventory)


def has_all_relics(player) -> bool:
    """Return whether the player currently carries all six major relics."""
    if relic_count(player) == len(RELIC_NAMES):
        return True
    has_relics = getattr(player, "has_relics", None)
    if callable(has_relics):
        try:
            return bool(has_relics())
        except Exception:
            return False
    return False


def _sergeant_main_template(quest_name: str) -> dict[str, Any] | None:
    from src.core.data.data_loader import get_quests

    sergeant_mains = get_quests().get("Sergeant", {}).get("Main", {})
    for quests_at_level in sergeant_mains.values():
        if quest_name in quests_at_level:
            return deepcopy(quests_at_level[quest_name])
    return None


def _stage_help(quest_data: dict[str, Any]) -> str | None:
    stage = quest_data.get("Stage")
    stages = quest_data.get("Stages", {})
    if isinstance(stages, dict) and stage in stages:
        help_text = stages[stage].get("Help Text")
        if isinstance(help_text, str) and help_text.strip():
            return help_text
    return None


def _holy_relics_help(count: int) -> str:
    if count <= 0:
        return (
            "The first relic report proved there may be related sealed chambers. "
            "Recover each relic you find and bring proof back to the Sergeant."
        )
    if count < len(RELIC_NAMES):
        return (
            f"Recovered {count}/{len(RELIC_NAMES)} relics. The Sergeant is comparing their markings "
            "against old patrol reports while you search the remaining sealed chambers."
        )
    return (
        "All six relics have been recovered. Return to the Sergeant before pressing toward "
        "the final threshold."
    )


def _copy_template_or_minimal(quest_name: str) -> dict[str, Any]:
    template = _sergeant_main_template(quest_name)
    if template is not None:
        return template
    if quest_name == UNCERTAIN_REPORTS:
        return {
            "Who": "Sergeant",
            "Type": "Story",
            "What": "First Relic Report",
            "Total": 1,
            "Stage": "investigate",
            "Stages": {},
            "Start Text": "",
            "End Text": "",
            "Help Text": "",
            "Reward": [],
            "Reward Number": 1,
            "Experience": 0,
            "Completed": False,
            "Turned In": False,
        }
    return {
        "Who": "Sergeant",
        "Type": "Collect",
        "What": "Relics",
        "Total": len(RELIC_NAMES),
        "Stage": "collecting",
        "Stages": {},
        "Start Text": "",
        "End Text": "",
        "Help Text": _holy_relics_help(0),
        "Reward": [],
        "Reward Number": 1,
        "Experience": 0,
        "Completed": False,
        "Turned In": False,
    }


def update_staged_help_text(quest_data: dict[str, Any]) -> None:
    """Copy the current staged objective help into the standard Help Text slot."""
    help_text = _stage_help(quest_data)
    if help_text:
        quest_data["Help Text"] = help_text


def ensure_holy_relics_quest(
    player, *, completed: bool | None = None, turned_in: bool = False
) -> dict[str, Any]:
    """Ensure the staged Holy Relics quest exists in the player's main log."""
    quest_dict = ensure_quest_categories(player)
    main_quests = quest_dict["Main"]
    quest_data = main_quests.get(HOLY_RELICS)
    if not isinstance(quest_data, dict):
        quest_data = _copy_template_or_minimal(HOLY_RELICS)
        main_quests[HOLY_RELICS] = quest_data

    quest_data.setdefault("Stage", "collecting")
    quest_data.setdefault("Total", len(RELIC_NAMES))
    quest_data["Help Text"] = _holy_relics_help(relic_count(player))

    if completed is None:
        completed = has_all_relics(player)
    quest_data["Completed"] = bool(completed)
    if turned_in:
        quest_data["Turned In"] = True
        quest_data["Completed"] = True
    else:
        quest_data.setdefault("Turned In", False)
    return quest_data


def sync_relic_story_progress(player) -> str:
    """Synchronize staged relic quest state and return any completion message."""
    quest_dict = ensure_quest_categories(player)
    main_quests = quest_dict["Main"]
    count = relic_count(player)
    message = ""

    uncertain = main_quests.get(UNCERTAIN_REPORTS)
    if isinstance(uncertain, dict):
        update_staged_help_text(uncertain)
        if count >= 1 and not uncertain.get("Turned In"):
            uncertain["Stage"] = "report_first_relic"
            update_staged_help_text(uncertain)
            if not uncertain.get("Completed"):
                uncertain["Completed"] = True
                message += f"You have completed the quest {UNCERTAIN_REPORTS}.\n"

    holy = main_quests.get(HOLY_RELICS)
    if isinstance(holy, dict):
        was_completed = bool(holy.get("Completed"))
        ensure_holy_relics_quest(
            player, completed=has_all_relics(player), turned_in=bool(holy.get("Turned In"))
        )
        if has_all_relics(player) and not was_completed:
            message += f"You have completed the quest {HOLY_RELICS}!\n"

    return message


def handle_quest_turn_in(player, quest_name: str) -> None:
    """Apply story quest side effects after a quest is turned in."""
    if quest_name == UNCERTAIN_REPORTS:
        ensure_holy_relics_quest(player)


def migrate_relic_story_quests(player) -> None:
    """Replace old immediate Holy Relics quest state with the staged chain."""
    quest_dict = ensure_quest_categories(player)
    main_quests = quest_dict["Main"]
    holy = main_quests.get(HOLY_RELICS)
    if isinstance(holy, dict) and "Stage" not in holy:
        old_turned_in = bool(holy.get("Turned In"))
        old_completed = bool(holy.get("Completed"))
        main_quests.pop(HOLY_RELICS, None)
        count = relic_count(player)
        if old_turned_in:
            ensure_holy_relics_quest(player, completed=True, turned_in=True)
        elif count <= 0:
            uncertain = _copy_template_or_minimal(UNCERTAIN_REPORTS)
            uncertain["Completed"] = old_completed
            main_quests[UNCERTAIN_REPORTS] = uncertain
            sync_relic_story_progress(player)
        else:
            ensure_holy_relics_quest(player, completed=count == len(RELIC_NAMES))
        return

    sync_relic_story_progress(player)
