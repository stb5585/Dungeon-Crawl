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

# ── Dodge / defensive caps ──────────────────────────────────────────
MAX_DODGE_CHANCE: float = 0.75          # hard cap on dodge probability
MAX_DEFENSIVE_REDUCTION: float = 0.75   # hard cap on damage reduction from stance

# ── Hit-chance modifiers (weapon attacks) ───────────────────────────
ACCURACY_RING_BONUS: float = 0.25       # Accuracy ring: +25% hit
BLIND_ACCURACY_PENALTY: float = 0.5     # Blind: −50% hit
FLYING_ACCURACY_PENALTY: float = 0.1    # Flying target: −10% hit
DISARM_HIT_PENALTY: float = 0.25        # Disarmed: −25% hit
BERSERK_HIT_PENALTY: float = 0.15       # Berserk: −15% hit
INVISIBLE_ACCURACY_PENALTY: float = 1 / 3  # Invisible: −33.3% hit
ENCUMBERED_HIT_MULTIPLIER: float = 0.75    # Encumbered: ×0.75 hit
PRO_LEVEL_HIT_MODIFIER: float = 0.05       # Per-promotion-level difference

# ── Critical hit ────────────────────────────────────────────────────
BASE_CRIT_PER_POINT: float = 0.005      # crit chance per speed+luck point
SEEKER_CRIT_BONUS: float = 0.1          # Seeker power-up crit per stack
MAELSTROM_CRIT_PER_HIT: float = 0.05    # Maelstrom Weapon crit per consecutive hit

# ── Misc combat modifiers ──────────────────────────────────────────
ASTRAL_SHIFT_REDUCTION: float = 0.25    # Astral Shift damage reduction
REFLECT_DAMAGE_FRACTION: float = 0.25   # Templar/Totem reflect %
DISARM_DAMAGE_MULTIPLIER: float = 0.5   # Disarmed damage multiplier
BERSERK_DAMAGE_BONUS: float = 0.1       # Berserk damage bonus
OFFHAND_DAMAGE_MULTIPLIER: float = 0.75 # Base off-hand damage multiplier

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
