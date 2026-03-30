"""
Shared game-balance constants used across core, combat, and UI modules.

Centralising these values makes it easy to tune game balance without
hunting through multiple files.
"""

# ── Damage variance ──────────────────────────────────────────────────
DAMAGE_VARIANCE_LOW: float = 0.85
DAMAGE_VARIANCE_HIGH: float = 1.15

# ── Armor / damage reduction ────────────────────────────────────────
ARMOR_SCALING_FACTOR: int = 50          # dam_red / (dam_red + ARMOR_SCALING_FACTOR)
MAGIC_DEF_SCALING_FACTOR: int = 60      # m_def / (m_def + MAGIC_DEF_SCALING_FACTOR)

# ── Dodge / defensive caps ──────────────────────────────────────────
MAX_DODGE_CHANCE: float = 0.75          # hard cap on dodge probability
MAX_DEFENSIVE_REDUCTION: float = 0.75   # hard cap on damage reduction from stance

# ── Hit-chance modifiers (weapon attacks) ───────────────────────────
ACCURACY_RING_BONUS: float = 0.25       # Accuracy ring: +25% hit
BLIND_ACCURACY_PENALTY: float = 0.5     # Blind: −50% hit
FLYING_ACCURACY_PENALTY: float = 0.1    # Flying target: −10% hit
DISARM_HIT_PENALTY: float = 0.25        # Disarmed: −25% hit
BERSERK_HIT_PENALTY: float = 0.15       # Berserk: −15% hit
BLIND_RAGE_HIT_PENALTY: float = 0.25    # Blind Rage: −25% hit (retains control)
INVISIBLE_ACCURACY_PENALTY: float = 1 / 3  # Invisible: −33.3% hit
ENCUMBERED_HIT_MULTIPLIER: float = 0.75    # Encumbered: ×0.75 hit
PRO_LEVEL_HIT_MODIFIER: float = 0.05       # Per-promotion-level difference
TENTACLE_TRIP_PROC_CHANCE: float = 0.70    # chance Tentacle attempts to apply Trip on hit

# ── Critical hit ────────────────────────────────────────────────────
BASE_CRIT_PER_POINT: float = 0.005      # crit chance per speed+luck point
SEEKER_CRIT_BONUS: float = 0.1          # Seeker power-up crit per stack
MAELSTROM_CRIT_PER_HIT: float = 0.05    # Maelstrom Weapon crit per consecutive hit
WEAPON_CRIT_WEIGHT: float = 0.5         # weight applied to weapon crit contributions
MAX_CRIT_CHANCE: float = 0.60           # hard cap on overall crit probability

# ── Misc combat modifiers ──────────────────────────────────────────
ASTRAL_SHIFT_REDUCTION: float = 0.25    # Astral Shift damage reduction
REFLECT_DAMAGE_FRACTION: float = 0.25   # Templar/Totem reflect %
DISARM_DAMAGE_MULTIPLIER: float = 0.5   # Disarmed damage multiplier
BERSERK_DAMAGE_BONUS: float = 0.1       # Berserk damage bonus
OFFHAND_DAMAGE_MULTIPLIER: float = 0.75 # Base off-hand damage multiplier

# ── Racial tuning (7 sins / 7 virtues) ──────────────────────────────
HUMAN_EXP_MULTIPLIER: float = 1.10
HUMAN_STATUS_RESIST_MULTIPLIER: float = 0.90  # affects resisted-status contest scores (lower = worse resist)

ELF_INVISIBLE_PENALTY_MULTIPLIER: float = 0.50  # reduces the impact of INVISIBLE_ACCURACY_PENALTY
ELF_BLIND_PENALTY_MULTIPLIER: float = 0.80      # reduces the impact of BLIND_ACCURACY_PENALTY
ELF_HEALING_RECEIVED_MULTIPLIER: float = 0.95

HALF_ELF_HEALING_RECEIVED_MULTIPLIER: float = 1.05
# Half Elf sin should trim extreme crit spikes without nuking burst identities.
HALF_ELF_CRIT_SPIKE_MULTIPLIER: float = 0.93  # scales crit bonus above 1.0

HALF_GIANT_EXP_MULTIPLIER: float = 0.85

GNOME_GOLD_CHARISMA_MULTIPLIER: float = 1.25   # treat CHA as higher for gold/shop outcomes
GNOME_ENCUMBERED_HIT_MULTIPLIER: float = 0.85  # extra hit penalty while encumbered (stacks w/ ENCUMBERED_HIT_MULTIPLIER)
GNOME_ENCUMBERED_DODGE_MULTIPLIER: float = 0.75  # extra dodge penalty while encumbered

DWARF_COMBAT_CONSUMABLE_MULTIPLIER: float = 1.10
DWARF_HANGOVER_STEPS_PER_USE: int = 6
DWARF_HANGOVER_MAX_STEPS: int = 30
DWARF_HANGOVER_COMBAT_DURATION: int = 3
DWARF_HANGOVER_DODGE_MULTIPLIER: float = 0.75

HALF_ORC_CRIT_DAMAGE_TAKEN_MULTIPLIER: float = 0.85  # take 15% less damage from weapon crits
HALF_ORC_BLIND_RAGE_CHANCE: float = 0.0075           # 0.75% chance on taking weapon damage
HALF_ORC_BLIND_RAGE_DURATION: int = 2                # turns

# ── Flee mechanics ──────────────────────────────────────────────────
BASE_FLEE_CHANCE: float = 0.2           # base flee probability
MAX_FLEE_CHANCE: float = 0.95           # cap on flee probability

# ── Enemy AI thresholds ─────────────────────────────────────────────
ENEMY_LOW_HEALTH_THRESHOLD: float = 0.25  # AI uses defensive / flee at 25% HP

# ── Special attack chance (shared by both UIs) ──────────────────────
SPECIAL_ATTACK_ROLL_MAX: int = 9        # randint(0, ROLL_MAX - luck_mod)
SPECIAL_ATTACK_LUCK_FACTOR: int = 20    # luck_factor used in the roll

# ── Level-up scaling ────────────────────────────────────────────────
LEVELUP_LUCK_DIVISOR_BASE: int = 5      # divisor in max(1, BASE - luck_mod)
LEVELUP_LUCK_FACTOR_HP_MP: int = 8      # luck factor for HP/MP roll divisor
LEVELUP_STAT_DIVISOR: int = 12          # stat // DIVISOR in combat gain formulas
LEVELUP_ATK_LUCK_FACTOR: int = 12       # luck factor for attack gain
LEVELUP_DEF_LUCK_FACTOR: int = 15       # luck factor for defense gain
LEVELUP_MAG_LUCK_FACTOR: int = 12       # luck factor for magic gain
LEVELUP_MDEF_LUCK_FACTOR: int = 15      # luck factor for magic defense gain

# ── Town / map ──────────────────────────────────────────────────────
TOWN_LOCATION: tuple[int, int, int] = (5, 10, 0)

# ── EXP scaling ─────────────────────────────────────────────────────
EXP_SCALE_BASE: int = 25
