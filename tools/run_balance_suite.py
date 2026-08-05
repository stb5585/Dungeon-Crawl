#!/usr/bin/env python3
"""
Run a lightweight balance suite using CombatSimulator.

This is intentionally simple and UI-free: it creates a test player for each
class name and simulates fights vs a small set of representative enemies.

Example:
  .venv/bin/python tools/run_balance_suite.py --level 10 --iters 50
  .venv/bin/python tools/run_balance_suite.py --level 30 --iters 25 --classes Warrior Wizard Crusader
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import datetime as _dt
import statistics
from dataclasses import dataclass
from pathlib import Path
import sys

# Allow running as a script from repo root without installing as a package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    # Analytics suite needs access to consumables for "use items under pressure".
    # Keep this import near the top so failures are obvious (instead of silently
    # producing incomplete results).
    from src.core import items as core_items
except Exception:  # pragma: no cover - best effort for analytics script
    core_items = None


@dataclass
class MatchupSummary:
    class_name: str
    enemy_name: str
    win_rate: float
    avg_turns: float


@dataclass(frozen=True)
class MatchupKey:
    race_name: str
    class_name: str
    enemy_name: str


_CLASS_COL_W = 20
# Enemy names can be longer than the original 12-char column (e.g. "Evil Crusader").
# Keep this wide enough to avoid breaking the fixed-width table parser.
_ENEMY_COL_W = 20


def _parse_table_from_stdout(text: str) -> dict[tuple[str, str], MatchupSummary]:
    """
    Parse the suite's fixed-width table output into summaries keyed by (class, enemy).
    """
    out: dict[tuple[str, str], MatchupSummary] = {}
    for line in text.splitlines():
        if not line or line.startswith("Balance Suite") or line.startswith("Class"):
            continue
        cls = line[:_CLASS_COL_W].rstrip()
        enemy = line[_CLASS_COL_W + 1:_CLASS_COL_W + 1 + _ENEMY_COL_W].rstrip()
        try:
            win_start = _CLASS_COL_W + 1 + _ENEMY_COL_W + 1
            win = float(line[win_start:win_start + 8])
            turns = float(line[win_start + 9:].strip())
        except Exception:
            continue
        out[(cls, enemy)] = MatchupSummary(cls, enemy, win, turns)
    return out


def _race_allows_class(race_obj, class_name: str) -> bool:
    """
    Return True if the race can ever be this class (base or promoted).

    races.py encodes allowed classes per race across promotion tiers via
    race.cls_res = {"Base": [...], "First": [...], "Second": [...]}.
    """
    cls_res = getattr(race_obj, "cls_res", None)
    if not isinstance(cls_res, dict):
        return True  # be permissive if missing
    for k in ["Base", "First", "Second"]:
        allowed = cls_res.get(k, [])
        if isinstance(allowed, list) and class_name in allowed:
            return True
    # Some races may encode keys differently; fall back to scanning all lists.
    for allowed in cls_res.values():
        if isinstance(allowed, list) and class_name in allowed:
            return True
    return False


def _run_once(
    *,
    level: int,
    iters: int,
    seed: int,
    race: str,
    classes: list[str] | None,
    profile: str,
    gear: str,
    meta_loadouts: str,
    progression: str,
    tier: str,
) -> str:
    """
    Run the suite in-process for a given configuration and return stdout text.

    This avoids subprocess overhead and keeps the delta mode self-contained.
    """
    import io
    import contextlib

    # Reuse the main() implementation by temporarily spoofing argv.
    argv = [
        "run_balance_suite.py",
        "--level", str(level),
        "--iters", str(iters),
        "--seed", str(seed),
        "--race", race,
        "--profile", profile,
        "--gear", gear,
        "--meta-loadouts", meta_loadouts,
        "--progression", progression,
        "--tier", tier,
    ]
    if classes:
        argv += ["--classes", *classes]

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        # Local import to avoid module-level side effects.
        import sys as _sys
        old = list(_sys.argv)
        try:
            _sys.argv = argv
            main()
        finally:
            _sys.argv = old
    return buf.getvalue()


def _progress(msg: str) -> None:
    """Emit lightweight progress to stderr (kept out of report output)."""
    try:
        print(msg, file=sys.stderr, flush=True)
    except Exception:
        pass


def _primary_stat_for_class(cls_obj) -> str:
    """
    Best-effort stat-up choice for non-interactive progression.

    In-game this choice is manual; for analytics we pick the stat whose class
    bonus is largest to better reflect intended archetypes.
    """
    pluses = {
        "strength": getattr(cls_obj, "str_plus", 0),
        "intel": getattr(cls_obj, "int_plus", 0),
        "wisdom": getattr(cls_obj, "wis_plus", 0),
        "con": getattr(cls_obj, "con_plus", 0),
        "charisma": getattr(cls_obj, "cha_plus", 0),
        "dex": getattr(cls_obj, "dex_plus", 0),
    }
    # Stable tie-breaker order to keep results reproducible.
    order = ["strength", "intel", "wisdom", "con", "dex", "charisma"]
    return max(order, key=lambda k: (pluses.get(k, 0), -order.index(k)))


def _apply_auto_stat_ups(
    player,
    target_level: int,
    *,
    point_build: str = "focus",
) -> None:
    """Spend roughly half of earned progression points on a focus attribute."""
    if not getattr(player, "cls", None):
        return
    stat = (
        "strength"
        if point_build == "one-stat"
        else _primary_stat_for_class(player.cls)
    )
    ups = max(
        0,
        int(target_level) - 1
        if point_build == "one-stat"
        else (int(target_level) - 1) // 2,
    )
    if hasattr(player, "stats") and hasattr(player.stats, stat):
        setattr(player.stats, stat, int(getattr(player.stats, stat)) + ups)


def _apply_expected_combat_scaling(player, target_level: int) -> None:
    """
    Approximate combat stat growth without driving Player.level_up() UI flows.

    The real game uses RNG and player-driven stat-ups. For balance analytics,
    an expectation-based approximation keeps results stable while still scaling
    output damage/defense with level.
    """
    from src.core.constants import LEVELUP_STAT_DIVISOR

    lvl = max(1, int(target_level))
    n = max(0, lvl - 1)
    cls = getattr(player, "cls", None)
    if cls is None:
        return

    def _expected(stat_val: int, cls_plus: int) -> int:
        # level_up() draws randint(0, max_gain), so E[gain] ≈ max_gain/2.
        max_gain = (int(stat_val) // LEVELUP_STAT_DIVISOR) + max(1, int(cls_plus) // 2)
        return int((max_gain * 0.5) * n)

    # Use the player's current combat stats as the baseline, so callers can
    # seed race/class baselines before applying expected growth.
    base_attack = int(getattr(player.combat, "attack", 0) or 0)
    base_def = int(getattr(player.combat, "defense", 0) or 0)
    base_magic = int(getattr(player.combat, "magic", 0) or 0)
    base_mdef = int(getattr(player.combat, "magic_def", 0) or 0)

    player.combat.attack = base_attack + _expected(player.stats.strength, cls.att_plus)
    player.combat.defense = base_def + _expected(player.stats.con, cls.def_plus)
    player.combat.magic = base_magic + _expected(player.stats.intel, cls.int_plus)
    player.combat.magic_def = base_mdef + _expected(player.stats.wisdom, cls.wis_plus)


def _get_class_obj_by_name(class_name: str):
    """Instantiate a class/job by display name (Job.name)."""
    from src.core import classes

    for attr in dir(classes):
        obj = getattr(classes, attr)
        if not callable(obj):
            continue
        try:
            inst = obj()
        except Exception:
            continue
        if getattr(inst, "name", None) == class_name:
            return inst
    raise KeyError(class_name)


def _promotion_lineage(class_name: str) -> list[str]:
    """
    Return [base, first, second] if the class docstring contains a Promotion chain.
    Otherwise return [class_name].
    """
    try:
        cls_obj = _get_class_obj_by_name(class_name)
    except Exception:
        return [class_name]

    doc = (getattr(cls_obj.__class__, "__doc__", None) or "").strip()
    for line in doc.splitlines():
        line = line.strip()
        if not line.startswith("Promotion:"):
            continue
        chain = line.split("Promotion:", 1)[1].strip()
        parts = [p.strip() for p in chain.split("->")]
        parts = [p for p in parts if p]
        if class_name in parts:
            return parts
    return [class_name]


def _max_level_for_pro_level(pro_level: int) -> int:
    """Return the flat player cap; class tier does not change it."""
    del pro_level
    return 100


def _total_player_level_for(class_name: str, class_level: int, *, progression: str) -> int:
    """
    Compute Player.player_level() equivalent without requiring a Player instance.
    """
    del class_name, progression
    return int(class_level)


def _apply_expected_combat_scaling_progression(player, class_name: str, class_level: int) -> None:
    """Apply expected growth over global levels using the active class."""
    del class_name
    _apply_expected_combat_scaling(player, class_level)


def _populate_spellbook_for_level(player, class_name: str, target_level: int) -> None:
    """
    Populate spellbook using abilities.{spell_dict,skill_dict} up to target_level.

    This roughly mirrors Player.level_up() ability grants, without promotions
    or UI interactions.
    """
    from src.core import abilities

    spells = abilities.spell_dict.get(class_name, {})
    skills = abilities.skill_dict.get(class_name, {})

    def _sorted_levels(d: dict) -> list[int]:
        out: list[int] = []
        for k in d.keys():
            try:
                out.append(int(k))
            except Exception:
                continue
        return sorted(out)

    # Spells
    for lv in _sorted_levels(spells):
        if lv > target_level:
            break
        gain_cls = spells.get(str(lv))
        if not gain_cls:
            continue
        try:
            gain = gain_cls()
        except Exception:
            continue
        nm = getattr(gain, "name", None)
        if not isinstance(nm, str) or not nm:
            continue
        try:
            base_nm = gain_cls.mro()[1]().name
        except Exception:
            base_nm = None
        if base_nm and base_nm in player.spellbook["Spells"] and base_nm != nm:
            del player.spellbook["Spells"][base_nm]
        player.spellbook["Spells"][nm] = gain

    # Skills
    for lv in _sorted_levels(skills):
        if lv > target_level:
            break
        gain_cls = skills.get(str(lv))
        if not gain_cls:
            continue
        try:
            gain = gain_cls()
        except Exception:
            continue
        nm = getattr(gain, "name", None)
        if not isinstance(nm, str) or not nm:
            continue
        try:
            base_nm = gain_cls.mro()[1]().name
        except Exception:
            base_nm = None
        if base_nm and base_nm in player.spellbook["Skills"] and base_nm != nm:
            del player.spellbook["Skills"][base_nm]
        player.spellbook["Skills"][nm] = gain


def _populate_spellbook_for_progression(
    player,
    class_name: str,
    class_level: int,
    *,
    point_build: str = "focus",
) -> None:
    """Populate a representative point-bought spellbook across its lineage."""
    from src.core.progression import ABILITY_TREES, NodeKind, _grant_ability

    lineage = _promotion_lineage(class_name)
    if class_name not in lineage:
        lineage = [class_name]
    tier_names = lineage[: lineage.index(class_name) + 1]

    player.spellbook = {"Spells": {}, "Skills": {}}
    ability_budget = (
        1
        if point_build == "one-stat"
        else max(1, (int(class_level) + 1) // 2)
    )
    for tree_name in tier_names:
        tree = ABILITY_TREES.get(tree_name)
        if tree is None:
            continue
        for node in tree.nodes:
            if node.kind != NodeKind.ABILITY or ability_budget <= 0:
                continue
            try:
                _grant_ability(player, node)
            except Exception:
                continue
            ability_budget -= 1


def _apply_meta_progression_loadouts(player, target_level: int) -> None:
    """
    Provide representative loadouts for classes whose real power depends on
    out-of-band progression (quest unlocks, learning systems, companions).

    This intentionally does *not* attempt to perfectly mirror a save file; it
    creates a stable baseline so balance comparisons are meaningful.
    """
    from src.core import abilities
    from src.core import companions

    skills = player.spellbook.get("Skills", {})
    lvl = int(target_level)

    # ── Power Core (class power-up) ──────────────────────────────────
    # In real play this is quest-gated. For analytics we assume it's unlocked
    # for promoted characters (and late-game levels).
    if lvl >= 30 and getattr(player, "cls", None) is not None:
        def ability_ctor(name: str):
            return getattr(abilities, name, None)

        powerup_dict = {
            "Berserker": ability_ctor("BloodRage"),
            "Crusader": ability_ctor("DivineAegis"),
            "Dragoon": ability_ctor("DraconicOnslaught"),
            "Wizard": ability_ctor("SpellMastery"),
            "Shadowcaster": ability_ctor("VeilShadows"),
            "Knight Enchanter": ability_ctor("ArcaneBlast"),
            "Summoner": ability_ctor("EternalConduit"),
            "Rogue": ability_ctor("StrokeLuck"),
            "Seeker": ability_ctor("EyesUnseen"),
            "Ninja": ability_ctor("BladeFatalities"),
            "Templar": ability_ctor("HolyRetribution"),
            "Archbishop": ability_ctor("GreatGospel"),
            "Master Monk": ability_ctor("DimMak"),
            "Troubadour": ability_ctor("SongInspiration"),
            "Lycan": ability_ctor("LunarFrenzy"),
            "Astromancer": ability_ctor("TetraDisaster"),
            "Soulcatcher": ability_ctor("SoulHarvest"),
            "Beast Master": ability_ctor("PackBond"),
        }
        ctor = powerup_dict.get(player.cls.name)
        if ctor is not None:
            try:
                skill = ctor()
                player.spellbook.setdefault("Skills", {})
                player.spellbook["Skills"][skill.name] = skill
                player.power_up = True
            except Exception:
                pass

    # ── Learn Spell (Diviner / Spell Stealer lines) ──────────────────
    if "Learn Spell" in skills:
        # Tiered learned spell set (kept intentionally small and PvE-friendly).
        if lvl >= 50:
            learned = [
                abilities.MagicMissile3,
                abilities.Fireball,
                abilities.Dispel,
                abilities.Regen3,
                abilities.Heal3,
            ]
        elif lvl >= 30:
            learned = [
                abilities.MagicMissile2,
                abilities.Fireball,
                abilities.Dispel,
                abilities.Regen2,
                abilities.Heal2,
            ]
        else:
            learned = [
                abilities.MagicMissile,
                abilities.Firebolt,
                abilities.Dispel,
                abilities.Regen,
                abilities.Heal,
            ]

        for ctor in learned:
            try:
                ab = ctor()
            except Exception:
                continue
            nm = getattr(ab, "name", None)
            if not isinstance(nm, str) or not nm:
                continue
            player.spellbook.setdefault("Spells", {})
            player.spellbook["Spells"][nm] = ab

    # ── Familiar (choice-gated in real play) ─────────────────────────
    if "Familiar" in skills and getattr(player, "familiar", None) is None:
        cls_name = getattr(getattr(player, "cls", None), "name", "") or ""
        if cls_name in {"Healer", "Cleric", "Priest", "Archbishop"}:
            fam = companions.Fairy()
        elif cls_name in {"Warlock", "Shadowcaster"}:
            fam = companions.Homunculus()
        elif cls_name in {"Thief", "Rogue", "Seeker", "Bard", "Troubadour"}:
            fam = companions.Jinkin()
        else:
            fam = companions.Mephit()

        fam.name = f"{player.name}'s Familiar"
        # Basic resource baselines so the familiar can act.
        try:
            fam.health.max = fam.health.current = 50 + (lvl * 2)
            fam.mana.max = fam.mana.current = 30 + (lvl * 3)
        except Exception:
            pass

        # Upgrade familiar tier to match late-game assumptions.
        desired = 1 if lvl < 30 else (2 if lvl < 50 else 3)
        try:
            while getattr(fam.level, "pro_level", 1) < desired:
                fam.level_up()
        except Exception:
            pass
        player.familiar = fam

    # ── Summons (Summoner lines) ─────────────────────────────────────
    if getattr(getattr(player, "cls", None), "name", "") in {"Summoner", "Grand Summoner"}:
        if not getattr(player, "summons", None):
            player.summons = {}
        if not player.summons:
            # Pick a representative summon by tier.
            if lvl >= 50:
                summon = companions.Grigori()
            elif lvl >= 30:
                summon = companions.Cacus()
            else:
                summon = companions.Patagon()
            try:
                summon.initialize_stats(player)
            except Exception:
                pass
            player.summons[summon.name] = summon

    # ── Soulcatcher stacks (kill_dict) ───────────────────────────────
    if getattr(getattr(player, "cls", None), "name", "") == "Soulcatcher" and getattr(player, "power_up", False):
        # Provide a conservative baseline of "souls harvested" so the class
        # doesn't appear artificially weak in a fresh test state.
        baseline = 20 if lvl < 30 else (80 if lvl < 50 else 160)
        for typ in ["Humanoid", "Aberration", "Monster", "Undead", "Animal", "Slime", "Construct", "Insect", "Dragon"]:
            player.kill_dict.setdefault(typ, {})
            player.kill_dict[typ].setdefault("Baseline", baseline)


_AUTO_EQUIP_CACHE: dict[tuple[str, str], object] = {}


def _parse_leading_int(s: object) -> int:
    """Parse a leading integer from strings like '5 Magic Damage'."""
    if not isinstance(s, str) or not s:
        return 0
    tok = s.split(" ", 1)[0].strip()
    try:
        return int(tok)
    except Exception:
        return 0


def _auto_equip_best(player) -> None:
    """
    Equip the best available items (by simple heuristics) within class restrictions.

    This is for analytics only; it produces a stable "reasonably geared" baseline
    without needing the full loot/shop pipelines.
    """
    from src.core import items

    cls = getattr(player, "cls", None)
    if cls is None:
        return

    def _iter_items():
        for attr_name in dir(items):
            attr = getattr(items, attr_name)
            if not callable(attr):
                continue
            try:
                it = attr()
            except Exception:
                continue
            # Skip placeholders / sentinels.
            nm = getattr(it, "name", "") or ""
            if isinstance(nm, str) and nm.startswith("No"):
                continue
            yield it

    def _score(slot: str, it) -> int:
        if slot == "Weapon":
            return int(getattr(it, "damage", 0) or 0)
        if slot == "Armor":
            return int(getattr(it, "armor", 0) or 0)
        if slot == "OffHand":
            # Tomes: mod (magic); Shields: mod (block); weapons: damage.
            return int(getattr(it, "damage", 0) or 0) + int(getattr(it, "mod", 0) or 0) + int(getattr(it, "armor", 0) or 0)
        if slot in ["Ring", "Pendant"]:
            return _parse_leading_int(getattr(it, "mod", "")) * 10
        return 0

    for slot in ["Weapon", "Armor", "OffHand", "Ring", "Pendant"]:
        cache_key = (cls.name, slot)
        cached = _AUTO_EQUIP_CACHE.get(cache_key)
        if cached is not None:
            player.equipment[slot] = cached if type(cached) != type else cached()
            continue

        best = None
        best_score = -1
        for it in _iter_items():
            try:
                if not cls.equip_check(it, slot):
                    continue
            except Exception:
                continue
            sc = _score(slot, it)
            if sc > best_score:
                best, best_score = it, sc

        if best is not None:
            player.equipment[slot] = best
            _AUTO_EQUIP_CACHE[cache_key] = best.__class__


def _equip_tiered_from_items_dict(player, target_level: int) -> None:
    """
    Equip a level-appropriate baseline using items.items_dict ordering.

    items.items_dict is already curated by the game as shop tiers (roughly
    increasing strength). We keep the player's *starting* subtype/category
    (e.g., Sword vs Staff; Light vs Heavy armor) and move "up the list"
    based on level bands.
    """
    from src.core import items

    lvl = max(1, int(target_level))
    tier = min(5, (lvl - 1) // 10)  # 0 @ 1-10, 1 @ 11-20, ... 4 @ 41-50

    def _pick(seq: list[type]) -> object | None:
        if not seq:
            return None
        idx = min(tier, len(seq) - 1)
        try:
            return seq[idx]()
        except Exception:
            return None

    # Weapon: keep current weapon subtype and 1H/2H bucket.
    w = player.equipment.get("Weapon")
    w_sub = getattr(w, "subtyp", None)
    if isinstance(w_sub, str) and w_sub:
        weapon_tables = items.items_dict.get("Weapon", {})
        chosen = None
        for hand_bucket in ["1-Handed", "2-Handed"]:
            bucket = weapon_tables.get(hand_bucket, {})
            if w_sub in bucket:
                chosen = _pick(bucket[w_sub])
                break
        if chosen is not None:
            player.equipment["Weapon"] = chosen

    # Armor: keep current armor category.
    a = player.equipment.get("Armor")
    a_sub = getattr(a, "subtyp", None)
    if isinstance(a_sub, str) and a_sub:
        armor_tables = items.items_dict.get("Armor", {})
        if a_sub in armor_tables:
            chosen = _pick(armor_tables[a_sub])
            if chosen is not None:
                player.equipment["Armor"] = chosen

    # OffHand: keep current offhand type (Shield/Tome/Rod/etc.).
    oh = player.equipment.get("OffHand")
    oh_sub = getattr(oh, "subtyp", None)
    if isinstance(oh_sub, str) and oh_sub:
        off_tables = items.items_dict.get("OffHand", {})
        if oh_sub in off_tables:
            chosen = _pick(off_tables[oh_sub])
            if chosen is not None:
                player.equipment["OffHand"] = chosen

    # Accessories: just tier within each list.
    acc = items.items_dict.get("Accessory", {})
    for slot, key in [("Ring", "Ring"), ("Pendant", "Pendant")]:
        seq = acc.get(key)
        if seq:
            chosen = _pick(seq)
            if chosen is not None:
                player.equipment[slot] = chosen


def _iter_playable_class_names() -> list[str]:
    """
    Best-effort discovery of playable classes by instantiating callables in
    src.core.classes and reading their .name attribute.
    """
    from src.core import classes

    names: set[str] = set()
    for attr_name in dir(classes):
        attr = getattr(classes, attr_name)
        if not callable(attr):
            continue
        try:
            inst = attr()
        except Exception:
            continue
        nm = getattr(inst, "name", None)
        if isinstance(nm, str) and nm:
            names.add(nm)
    return sorted(names)


def main() -> int:
    from src.core.analytics.combat_simulator import CombatSimulator
    from tests.test_framework import TestGameState
    from src.core.enemies import (
        Aboleth,
        Bandit,
        Chimera,
        Clannfear,
        Conjurer,
        DarkKnight,
        DisplacerBeast,
        EvilCrusader,
        Gargoyle,
        GiantSpider,
        Goblin,
        GreenSlime,
        Harpy,
        Imp,
        Mimic,
        Naga,
        NightHag,
        ShadowSerpent,
        SteelPredator,
        Skeleton,
        Troll,
        Vampire,
        Werewolf,
    )
    from src.core import races

    def _get_race_obj(race_name: str):
        """Instantiate a race by display name (Race.name)."""
        for race_attr in dir(races):
            obj = getattr(races, race_attr)
            if not callable(obj):
                continue
            try:
                inst = obj()
            except Exception:
                continue
            if getattr(inst, "name", None) == race_name:
                return inst
        raise SystemExit(f"Unknown race: {race_name!r}")

    ap = argparse.ArgumentParser()
    ap.add_argument("--level", type=int, default=10)
    ap.add_argument("--iters", type=int, default=30)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--classes", nargs="*", default=None)
    ap.add_argument(
        "--encounters",
        nargs="*",
        default=None,
        help=(
            "Run only the named development curated encounters instead of "
            "the singleton baseline catalog."
        ),
    )
    ap.add_argument(
        "--tier",
        choices=["all", "base", "first", "second"],
        default="all",
        help="Filter discovered classes by promotion tier (pro_level): base=1, first=2, second=3.",
    )
    ap.add_argument("--race", type=str, default="Human")
    ap.add_argument(
        "--report-out",
        type=str,
        default=None,
        help="Write the report output to a file (also prints to stdout). If a directory is provided, a timestamped file is created in it.",
    )
    ap.add_argument(
        "--races",
        nargs="*",
        default=None,
        help="Optional list of races. When provided, runs delta reports across races for the same class/enemy set.",
    )
    ap.add_argument(
        "--delta",
        action="store_true",
        help="If set, print delta rows vs --baseline-race (requires --races).",
    )
    ap.add_argument(
        "--baseline-race",
        type=str,
        default="Human",
        help="Baseline race for delta reports (requires --races + --delta).",
    )
    ap.add_argument(
        "--delta-summary",
        choices=["none", "class", "top"],
        default="class",
        help="Delta report summary mode: class=per-class aggregates; top=largest win-rate drops overall; none=raw rows only.",
    )
    ap.add_argument(
        "--delta-score",
        choices=["off", "on"],
        default="on",
        help="If enabled, compute a simple penalty score from win-rate drops weighted by baseline wins (delta mode).",
    )
    ap.add_argument(
        "--enemy-weighting",
        choices=["uniform", "pve_default"],
        default="pve_default",
        help="Penalty-score weighting across enemies: uniform=all equal; pve_default=heavier weight on tougher enemies.",
    )
    ap.add_argument(
        "--enemy-weight",
        action="append",
        default=None,
        help="Override/add an enemy weight in the form Name=Weight (e.g., Mimic=1.5). Repeatable.",
    )
    ap.add_argument(
        "--profile",
        choices=["simple", "leveled"],
        default="leveled",
        help="Player build profile: simple=static stub; leveled=point allocation + expected combat scaling + tree purchases",
    )
    ap.add_argument(
        "--point-build",
        choices=["focus", "one-stat"],
        default="focus",
        help=(
            "Progression allocation: focus splits points between a class focus "
            "and tree abilities; one-stat puts every free point into Strength."
        ),
    )
    ap.add_argument(
        "--gear",
        choices=["class_default", "tiered", "auto_best"],
        default="tiered",
        help="Equipment baseline: class_default uses class starter gear; tiered uses items.items_dict ordering; auto_best stress-tests with best-allowed gear",
    )
    ap.add_argument(
        "--meta-loadouts",
        choices=["off", "on"],
        default="on",
        help="Apply representative loadouts for meta-progression classes (e.g., Learn Spell).",
    )
    ap.add_argument(
        "--progression",
        choices=["off", "on"],
        default="on",
        help="If on, use global levels and representative point-bought lineage abilities.",
    )
    args = ap.parse_args()

    report_fp = None
    if args.report_out:
        p = Path(args.report_out)
        if p.exists() and p.is_dir():
            ts = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
            p = p / f"balance_report_{ts}.txt"
        p.parent.mkdir(parents=True, exist_ok=True)
        report_fp = p.open("w", encoding="utf-8")

        class _Tee:
            def __init__(self, *streams):
                self._streams = streams

            def write(self, s: str) -> int:
                n = 0
                for st in self._streams:
                    try:
                        n = st.write(s)
                    except BrokenPipeError:
                        # Allow piping (head/rg) without crashing the report file write.
                        continue
                return n

            def flush(self) -> None:
                for st in self._streams:
                    try:
                        st.flush()
                    except Exception:
                        continue

        sys.stdout = _Tee(sys.stdout, report_fp)  # type: ignore[assignment]

    class_names = args.classes or _iter_playable_class_names()
    if args.tier != "all":
        want = {"base": 1, "first": 2, "second": 3}[args.tier]
        filtered: list[str] = []
        for nm in class_names:
            try:
                pro = int(_get_class_obj_by_name(nm).pro_level)
            except Exception:
                pro = 1
            if pro == want:
                filtered.append(nm)
        class_names = filtered

    # ── Delta mode: run multiple races and print (race - baseline) ───
    if args.races is not None and args.delta:
        _progress(
            f"# Delta: tier={args.tier} level={args.level} iters={args.iters} "
            f"baseline={args.baseline_race} races={len(args.races)}"
        )
        def _enemy_weights() -> dict[str, float]:
            # Default weights are intentionally simple and tuned for the small
            # representative enemy set in this script.
            if args.enemy_weighting == "uniform":
                weights = {}
            else:
                weights = {
                    "Goblin": 0.5,
                    "Green Slime": 0.75,
                    "Bandit": 0.75,
                    "Skeleton": 0.75,
                    "Giant Spider": 0.9,
                    "Harpy": 1.0,
                    "Naga": 1.1,
                    "Night Hag": 1.25,
                    "Imp": 0.9,
                    "Clannfear": 0.75,
                    "Werewolf": 1.25,
                    "Evil Crusader": 1.0,
                    "Troll": 1.25,
                    "Vampire": 1.25,
                    "Conjurer": 1.25,
                    "Gargoyle": 1.35,
                    "Mimic": 1.5,
                    "Steel Predator": 1.25,
                    "Dark Knight": 1.5,
                    "Displacer Beast": 1.6,
                    "Chimera": 1.75,
                    "Shadow Serpent": 2.0,
                    "Aboleth": 2.5,
                }
            if args.enemy_weight:
                for spec in args.enemy_weight:
                    if not isinstance(spec, str) or "=" not in spec:
                        continue
                    name, raw = spec.split("=", 1)
                    name = name.strip()
                    try:
                        w = float(raw.strip())
                    except Exception:
                        continue
                    if name:
                        weights[name] = w
            return weights

        enemy_weights = _enemy_weights()

        races_list = list(dict.fromkeys(args.races))
        if args.baseline_race not in races_list:
            races_list.insert(0, args.baseline_race)

        baseline_race_obj = _get_race_obj(args.baseline_race)
        baseline_classes = [c for c in class_names if _race_allows_class(baseline_race_obj, c)]
        skipped_baseline = [c for c in class_names if c not in baseline_classes]
        for cls_name in skipped_baseline:
            print(f"# Skipping invalid race/class pairing: {baseline_race_obj.name} cannot be {cls_name}")

        _progress(f"# Running baseline race={args.baseline_race} classes={len(baseline_classes)}")
        baseline_out = _run_once(
            level=args.level,
            iters=args.iters,
            seed=args.seed,
            race=args.baseline_race,
            classes=baseline_classes,
            profile=args.profile,
            gear=args.gear,
            meta_loadouts=args.meta_loadouts,
            progression=args.progression,
            tier=args.tier,
        )
        baseline = _parse_table_from_stdout(baseline_out)

        print(
            f"Balance Suite Delta: level={args.level} iters={args.iters} seed={args.seed} "
            f"baseline_race={args.baseline_race}"
        )
        print(
            f"{'Race':12s} "
            f"{'Class':{_CLASS_COL_W}s} "
            f"{'Enemy':{_ENEMY_COL_W}s} "
            f"{'dWin%':>8s} {'dTurns':>8s} {'BaseWin%':>8s} {'BaseT':>6s}"
        )

        all_rows: list[tuple[str, str, str, float, float, float, float]] = []
        for race in races_list:
            if race == args.baseline_race:
                continue
            _progress(f"# Running race={race} (delta vs {args.baseline_race})")
            race_obj = _get_race_obj(race)
            race_classes = [c for c in class_names if _race_allows_class(race_obj, c)]
            skipped = [c for c in class_names if c not in race_classes]
            for cls_name in skipped:
                print(f"# Skipping invalid race/class pairing: {race_obj.name} cannot be {cls_name}")
            if not race_classes:
                print(f"# Skipping race: {race_obj.name} (no valid requested classes)")
                continue
            out = _run_once(
                level=args.level,
                iters=args.iters,
                seed=args.seed,
                race=race,
                classes=race_classes,
                profile=args.profile,
                gear=args.gear,
                meta_loadouts=args.meta_loadouts,
                progression=args.progression,
                tier=args.tier,
            )
            cur = _parse_table_from_stdout(out)
            for (cls, enemy), base in baseline.items():
                now = cur.get((cls, enemy))
                if now is None:
                    continue
                dwin = now.win_rate - base.win_rate
                dturns = now.avg_turns - base.avg_turns
                all_rows.append(
                    (race, cls, enemy, dwin, dturns, base.win_rate, base.avg_turns)
                )
                print(
                    f"{race:12s} "
                    f"{cls:{_CLASS_COL_W}s} "
                    f"{enemy:{_ENEMY_COL_W}s} "
                    f"{dwin:8.1f} {dturns:8.2f} {base.win_rate:8.1f} {base.avg_turns:6.2f}"
                )

        if args.delta_summary == "class":
            # Aggregate per (race, class) across enemies for quick scanning.
            agg: dict[tuple[str, str], list[tuple[str, float, float]]] = defaultdict(list)
            base_by_class: dict[str, list[float]] = defaultdict(list)
            base_by_class_enemy: dict[tuple[str, str], dict[str, float]] = defaultdict(dict)
            for race, cls, enemy, dwin, dturns, basewin, _baset in all_rows:
                agg[(race, cls)].append((enemy, dwin, dturns))
                base_by_class[cls].append(basewin)
                base_by_class_enemy[(race, cls)][enemy] = basewin

            print()
            print("Delta Summary (Per Class; averaged across suite enemies)")
            header = (
                f"{'Race':12s} "
                f"{'Class':{_CLASS_COL_W}s} "
                f"{'Avg dWin%':>9s} {'Avg dTurns':>10s} "
                f"{'Worst Enemy':{_ENEMY_COL_W}s} {'Worst dWin%':>10s} {'BaseAvgWin%':>11s}"
            )
            if args.delta_score == "on":
                header += f" {'Penalty':>8s}"
            print(header)
            for (race, cls), rows in sorted(agg.items(), key=lambda kv: (kv[0][0], kv[0][1])):
                avg_dwin = sum(r[1] for r in rows) / max(1, len(rows))
                avg_dturns = sum(r[2] for r in rows) / max(1, len(rows))
                worst_enemy, worst_dwin, _ = min(rows, key=lambda r: r[1])
                base_avg = sum(base_by_class.get(cls, [0.0])) / max(1, len(base_by_class.get(cls, [0.0])))
                line = (
                    f"{race:12s} "
                    f"{cls:{_CLASS_COL_W}s} "
                    f"{avg_dwin:9.1f} {avg_dturns:10.2f} "
                    f"{worst_enemy:{_ENEMY_COL_W}s} {worst_dwin:10.1f} {base_avg:11.1f}"
                )
                if args.delta_score == "on":
                    # Penalty score: sum of win% drops weighted by baseline win%.
                    # Intended to answer "how much worse does this race feel in matchups that were otherwise winnable?"
                    penalty = 0.0
                    for enemy, dwin, _dturns in rows:
                        basewin = base_by_class_enemy.get((race, cls), {}).get(enemy, 0.0)
                        w = float(enemy_weights.get(enemy, 1.0))
                        penalty += w * max(0.0, -dwin) * (basewin / 100.0)
                    line += f" {penalty:8.1f}"
                print(line)

        elif args.delta_summary == "top":
            # Largest absolute win-rate drops across all matchups.
            drops = sorted(all_rows, key=lambda r: r[3])[:25]
            print()
            print("Top Win-Rate Drops (Worst dWin%)")
            print(
                f"{'Race':12s} "
                f"{'Class':{_CLASS_COL_W}s} "
                f"{'Enemy':{_ENEMY_COL_W}s} "
                f"{'dWin%':>8s} {'BaseWin%':>8s}"
            )
            for race, cls, enemy, dwin, _dturns, basewin, _baset in drops:
                print(f"{race:12s} {cls:{_CLASS_COL_W}s} {enemy:{_ENEMY_COL_W}s} {dwin:8.1f} {basewin:8.1f}")
        return 0

    if args.races is not None and not args.delta:
        raise SystemExit("--races currently requires --delta (delta report mode).")

    # Race baseline for primary stats / resistances.
    race_obj = _get_race_obj(args.race)

    # Representative enemy set for quick signal (expand as needed).
    enemy_factories = [
        ("Goblin", Goblin),
        ("Green Slime", GreenSlime),
        ("Bandit", Bandit),
        ("Skeleton", Skeleton),
        ("Giant Spider", GiantSpider),
        ("Harpy", Harpy),
        ("Naga", Naga),
        ("Night Hag", NightHag),
        ("Imp", Imp),
        ("Clannfear", Clannfear),
        ("Werewolf", Werewolf),
        ("Evil Crusader", EvilCrusader),
        ("Troll", Troll),
        ("Vampire", Vampire),
        ("Conjurer", Conjurer),
        ("Gargoyle", Gargoyle),
        ("Steel Predator", SteelPredator),
        ("Dark Knight", DarkKnight),
        ("Displacer Beast", DisplacerBeast),
        ("Chimera", Chimera),
        ("Shadow Serpent", ShadowSerpent),
        ("Aboleth", Aboleth),
        ("Mimic", lambda: Mimic(
            z=2,
            player_level=(
                args.level
                if args.progression != "on" else
                args.level
            ),
        )),
    ]
    pair_mode = args.encounters is not None
    pair_keys_by_label: dict[str, str] = {}
    pair_specs_by_label = {}
    if pair_mode:
        from src.core.enemies import (
            build_curated_encounter,
            curated_encounter_spec,
        )

        requested = list(dict.fromkeys(args.encounters or []))
        if not requested:
            raise SystemExit("--encounters requires at least one curated key.")
        enemy_factories = [
            (
                curated_encounter_spec(key).display_name,
                lambda key=key: build_curated_encounter(key),
            )
            for key in requested
        ]
        pair_keys_by_label = {
            curated_encounter_spec(key).display_name: key
            for key in requested
        }
        pair_specs_by_label = {
            curated_encounter_spec(key).display_name: curated_encounter_spec(key)
            for key in requested
        }

    sim = CombatSimulator()
    summaries: list[MatchupSummary] = []
    pair_results_by_key = defaultdict(list)
    pair_actor_ratios_by_key = defaultdict(list)

    _progress(
        f"# Running suite: race={args.race} tier={args.tier} level={args.level} "
        f"classes={len(class_names)} enemies={len(enemy_factories)} iters={args.iters}"
    )
    for idx, cls_name in enumerate(class_names, start=1):
        _progress(f"#   class {idx}/{len(class_names)}: {cls_name}")
        # Respect race/class restrictions (avoid impossible pairings like Half Giant Wizard).
        if not _race_allows_class(race_obj, cls_name):
            print(f"# Skipping invalid race/class pairing: {race_obj.name} cannot be {cls_name}")
            continue
        # Enforce per-tier level caps (prevents misleading reports like base classes at 50).
        try:
            cls_obj = _get_class_obj_by_name(cls_name)
            pro_level = int(getattr(cls_obj, "pro_level", 1) or 1)
        except Exception:
            pro_level = 1
        max_lvl = _max_level_for_pro_level(pro_level)
        if int(args.level) > max_lvl:
            print(f"# Skipping invalid class level: {cls_name} (pro_level={pro_level}) cannot be level {args.level} (max {max_lvl})")
            continue

        def make_player():
            total_lvl = _total_player_level_for(cls_name, args.level, progression=args.progression)
            # Derive HP/MP baselines from race stats so stat dumps have tangible impact.
            hp_max = 100 + (race_obj.con * 10) + (total_lvl * 8)
            mp_max = 50 + (race_obj.intel * 8) + (total_lvl * 4)

            player = TestGameState.create_player(
                name=cls_name,
                class_name=cls_name,
                race_name=race_obj.name,
                level=args.level,
                health=(hp_max, hp_max),
                mana=(mp_max, mp_max),
                stats={
                    "strength": race_obj.strength,
                    "intel": race_obj.intel,
                    "wisdom": race_obj.wisdom,
                    "con": race_obj.con,
                    "charisma": race_obj.charisma,
                    "dex": race_obj.dex,
                },
            )
            # Race baselines (combat stats + resistances).
            player.resistance = dict(getattr(race_obj, "resistance", {}) or player.resistance)
            player.combat.attack = int(getattr(race_obj, "base_attack", 0) or player.combat.attack)
            player.combat.defense = int(getattr(race_obj, "base_defense", 0) or player.combat.defense)
            player.combat.magic = int(getattr(race_obj, "base_magic", 0) or player.combat.magic)
            player.combat.magic_def = int(getattr(race_obj, "base_magic_def", 0) or player.combat.magic_def)

            if args.profile == "leveled":
                _apply_auto_stat_ups(
                    player,
                    total_lvl,
                    point_build=args.point_build,
                )
                if args.progression == "on":
                    _apply_expected_combat_scaling_progression(player, cls_name, args.level)
                    _populate_spellbook_for_progression(
                        player,
                        cls_name,
                        args.level,
                        point_build=args.point_build,
                    )
                else:
                    _apply_expected_combat_scaling(player, args.level)
                    _populate_spellbook_for_level(player, cls_name, args.level)
                if args.meta_loadouts == "on":
                    _apply_meta_progression_loadouts(player, total_lvl)
                if args.gear == "tiered":
                    _equip_tiered_from_items_dict(player, total_lvl)
                elif args.gear == "auto_best":
                    _auto_equip_best(player)

            # Stock a small, consistent set of combat consumables so the simulator
            # can model "use items under pressure" behavior.
            if core_items is None:
                # Avoid silent "no potions present" runs (these dramatically skew results).
                # Print once per invocation.
                if not getattr(make_player, "_warned_no_items", False):
                    print("# WARNING: could not import src.core.items; consumables will not be stocked.")
                    setattr(make_player, "_warned_no_items", True)
            else:
                try:
                    if total_lvl >= 45:
                        hp_item = core_items.SuperHealthPotion()
                        mp_item = core_items.SuperManaPotion()
                    elif total_lvl >= 25:
                        hp_item = core_items.GreatHealthPotion()
                        mp_item = core_items.GreatManaPotion()
                    else:
                        hp_item = core_items.HealthPotion()
                        mp_item = core_items.ManaPotion()
                    player.modify_inventory(hp_item, num=2)
                    player.modify_inventory(mp_item, num=2)
                except Exception:
                    pass
            return player

        for enemy_label, enemy_factory in enemy_factories:
            if pair_mode:
                report = sim.run_simulations(
                    make_player,
                    encounter=enemy_factory,
                    iterations=args.iters,
                    seed=args.seed,
                )
            else:
                report = sim.run_simulations(
                    make_player,
                    enemy_factory,
                    iterations=args.iters,
                    seed=args.seed,
                )
            wins = sum(1 for r in report.results if r.winner == cls_name)
            win_rate = (wins / max(1, len(report.results))) * 100.0
            avg_turns = statistics.mean(r.turns for r in report.results) if report.results else 0.0
            summaries.append(MatchupSummary(cls_name, enemy_label, win_rate, avg_turns))
            if pair_mode and report.results:
                pair_key = pair_keys_by_label[enemy_label]
                pair_results_by_key[pair_key].extend(report.results)
                wins_list = [
                    result
                    for result in report.results
                    if result.winner == cls_name
                ]
                losses = sum(
                    1
                    for result in report.results
                    if result.winner not in {cls_name, "draw"}
                )
                draws = len(report.results) - len(wins_list) - losses
                avg_rounds = statistics.mean(
                    result.rounds for result in report.results
                )
                avg_actor_turns = statistics.mean(
                    result.actor_turns for result in report.results
                )
                singleton_actor_turns = []
                for member_factory in pair_specs_by_label[
                    enemy_label
                ].member_factories:
                    member_report = CombatSimulator().run_simulations(
                        make_player,
                        member_factory,
                        iterations=args.iters,
                        seed=args.seed,
                    )
                    singleton_actor_turns.append(
                        statistics.mean(
                            result.actor_turns
                            for result in member_report.results
                        )
                    )
                harder_singleton_turns = max(singleton_actor_turns)
                actor_turn_ratio = (
                    avg_actor_turns / harder_singleton_turns
                    if harder_singleton_turns
                    else 0.0
                )
                pair_actor_ratios_by_key[pair_key].append(actor_turn_ratio)
                avg_hp = statistics.mean(
                    (
                        result.player_hp_remaining
                        / max(1, result.player_hp_max)
                    )
                    * 100
                    for result in report.results
                )
                winning_hp_median = (
                    statistics.median(
                        (
                            result.player_hp_remaining
                            / max(1, result.player_hp_max)
                        )
                        * 100
                        for result in wins_list
                    )
                    if wins_list
                    else 0.0
                )
                avg_mp = statistics.mean(
                    result.player_mana_remaining
                    for result in report.results
                )
                avg_consumables = statistics.mean(
                    result.consumables_used for result in report.results
                )
                avg_reward_xp = statistics.mean(
                    result.reward_experience for result in report.results
                )
                avg_reward_gold = statistics.mean(
                    result.reward_gold for result in report.results
                )
                damage_totals: dict[str, int] = defaultdict(int)
                resolution_counts: Counter[str] = Counter()
                for result in report.results:
                    for label, damage in result.damage_by_combatant.items():
                        damage_totals[label] += damage
                    resolution_counts.update(
                        resolution or "unresolved"
                        for resolution in result.resolutions
                    )
                damage_summary = ",".join(
                    f"{label}:{damage / len(report.results):.1f}"
                    for label, damage in damage_totals.items()
                ) or "none"
                resolution_summary = ",".join(
                    f"{resolution}:{count}"
                    for resolution, count in sorted(resolution_counts.items())
                ) or "none"
                roster = "/".join(report.results[0].roster)
                invalid_intents = sum(
                    result.invalid_intents for result in report.results
                )
                max_turn_loops = sum(
                    result.max_turns_reached for result in report.results
                )
                repeated_non_progress = sum(
                    result.repeated_non_progress_actions
                    for result in report.results
                )
                print(
                    "# PairMetrics "
                    f"key={pair_key} "
                    f"class={cls_name} encounter={enemy_label!r} "
                    f"roster={roster!r} "
                    f"results={len(wins_list)}W/{losses}L/{draws}D "
                    f"rounds={avg_rounds:.2f} "
                    f"actor_turns={avg_actor_turns:.2f} "
                    f"harder_singleton_actor_turns="
                    f"{harder_singleton_turns:.2f} "
                    f"actor_turn_ratio={actor_turn_ratio:.2f} "
                    f"player_hp_pct={avg_hp:.1f} "
                    f"winning_hp_median_pct={winning_hp_median:.1f} "
                    f"player_mp={avg_mp:.1f} "
                    f"consumables={avg_consumables:.2f} "
                    f"damage={damage_summary!r} "
                    f"resolutions={resolution_summary!r} "
                    f"reward_xp={avg_reward_xp:.1f} "
                    f"reward_gold={avg_reward_gold:.1f} "
                    f"invalid_intents={invalid_intents} "
                    f"max_turn_loops={max_turn_loops} "
                    f"repeated_non_progress={repeated_non_progress}"
                )
                diagnostic = next(
                    (
                        result
                        for result in report.results
                        if result.max_turns_reached
                        or result.invalid_intents
                        or not result.damage_by_combatant
                    ),
                    None,
                )
                if diagnostic is not None:
                    print(
                        "# PairDiagnostic "
                        f"key={pair_key} class={cls_name} "
                        f"max_turns={diagnostic.max_turns_reached} "
                        f"invalid_intents={diagnostic.invalid_intents} "
                        f"damage={diagnostic.damage_by_combatant!r} "
                        f"actions={' > '.join(diagnostic.action_sequence)!r}"
                    )

    if pair_mode:
        player_names = set(class_names)
        for key in requested:
            results = pair_results_by_key[key]
            wins = [
                result
                for result in results
                if result.winner in player_names
            ]
            winning_hp_median = (
                statistics.median(
                    (
                        result.player_hp_remaining
                        / max(1, result.player_hp_max)
                    )
                    * 100
                    for result in wins
                )
                if wins
                else 0.0
            )
            win_rate = (len(wins) / max(1, len(results))) * 100
            mean_actor_turn_ratio = statistics.mean(
                pair_actor_ratios_by_key[key]
            )
            invalid_intents = sum(result.invalid_intents for result in results)
            max_turn_loops = sum(result.max_turns_reached for result in results)
            repeated_non_progress = sum(
                result.repeated_non_progress_actions for result in results
            )
            print(
                "# PairAggregate "
                f"key={key} battles={len(results)} "
                f"wins={len(wins)} win_rate={win_rate:.1f} "
                f"winning_hp_median_pct={winning_hp_median:.1f} "
                f"mean_actor_turn_ratio={mean_actor_turn_ratio:.2f} "
                f"invalid_intents={invalid_intents} "
                f"max_turn_loops={max_turn_loops} "
                f"repeated_non_progress={repeated_non_progress}"
            )

    # Print a simple, grep-friendly table.
    print(f"Balance Suite: level={args.level} iters={args.iters} seed={args.seed}")
    print(f"{'Class':{_CLASS_COL_W}s} {'Enemy':{_ENEMY_COL_W}s} {'WinRate%':>8s} {'AvgTurns':>8s}")
    for s in summaries:
        print(f"{s.class_name:{_CLASS_COL_W}s} {s.enemy_name:{_ENEMY_COL_W}s} {s.win_rate:8.1f} {s.avg_turns:8.2f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
