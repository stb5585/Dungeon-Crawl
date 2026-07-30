"""Gameplay statistic normalization and ability-upgrade helpers."""

GAMEPLAY_STATS_DEFAULTS = {
    "steps_taken": 0,
    "stairs_used": 0,
    "enemies_defeated": 0,
    "deaths": 0,
    "flees": 0,
    "highest_level_reached": 1,
    "highest_damage_dealt": 0,
    "highest_damage_taken": 0,
}


def _upgrade_source_name(ability_cls) -> str | None:
    """Return the inherited ability name for upgrade detection, if available."""
    try:
        explicit = getattr(ability_cls, "replaces", None)
        if explicit:
            return explicit
        bases = getattr(ability_cls, "__mro__", ())
        if len(bases) < 2:
            return None
        parent_instance = bases[1]()
        return getattr(parent_instance, "name", None)
    except Exception:
        return None


def normalize_gameplay_stats(gameplay_stats=None, *, current_level=1):
    """Return a backward-compatible gameplay statistics dictionary."""
    normalized = dict(GAMEPLAY_STATS_DEFAULTS)
    if isinstance(gameplay_stats, dict):
        normalized.update(gameplay_stats)

    for key in GAMEPLAY_STATS_DEFAULTS:
        try:
            normalized[key] = max(
                0,
                int(normalized.get(key, GAMEPLAY_STATS_DEFAULTS[key])),
            )
        except (TypeError, ValueError):
            normalized[key] = GAMEPLAY_STATS_DEFAULTS[key]

    normalized["highest_level_reached"] = max(
        1,
        int(current_level or 1),
        normalized["highest_level_reached"],
    )
    return normalized


def summarize_gameplay_stats(gameplay_stats=None, *, current_level=1) -> dict[str, int]:
    """Return normalized gameplay statistics with derived display counters."""
    summary = normalize_gameplay_stats(gameplay_stats, current_level=current_level)
    summary["encounters_survived"] = max(
        0,
        summary["enemies_defeated"] + summary["flees"] - summary["deaths"],
    )
    summary["combat_outcomes"] = (
        summary["enemies_defeated"] + summary["flees"] + summary["deaths"]
    )
    summary["exploration_actions"] = summary["steps_taken"] + summary["stairs_used"]
    summary["total_activity"] = (
        summary["exploration_actions"]
        + summary["combat_outcomes"]
    )
    summary["combat_survival_rate_percent"] = (
        0
        if summary["combat_outcomes"] <= 0
        else (summary["encounters_survived"] * 100) // summary["combat_outcomes"]
    )
    return summary


def summarize_gameplay_stat_groups(gameplay_stats=None, *, current_level=1) -> dict[str, dict[str, int]]:
    """Return gameplay statistics organized for grouped UI displays."""
    summary = summarize_gameplay_stats(gameplay_stats, current_level=current_level)
    return {
        "exploration": {
            "steps_taken": summary["steps_taken"],
            "stairs_used": summary["stairs_used"],
            "exploration_actions": summary["exploration_actions"],
        },
        "combat": {
            "enemies_defeated": summary["enemies_defeated"],
            "deaths": summary["deaths"],
            "flees": summary["flees"],
            "encounters_survived": summary["encounters_survived"],
            "combat_outcomes": summary["combat_outcomes"],
            "combat_survival_rate_percent": summary["combat_survival_rate_percent"],
        },
        "records": {
            "highest_level_reached": summary["highest_level_reached"],
            "highest_damage_dealt": summary["highest_damage_dealt"],
            "highest_damage_taken": summary["highest_damage_taken"],
            "total_activity": summary["total_activity"],
        },
    }
