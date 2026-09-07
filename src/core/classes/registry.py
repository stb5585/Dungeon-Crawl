"""Class promotion registry."""

from __future__ import annotations

from .arcane_trickster import ArcaneTrickster
from .archbishop import Archbishop
from .archdruid import Archdruid
from .assassin import Assassin
from .astromancer import Astromancer
from .bard import Bard
from .beast_master import BeastMaster
from .berserker import Berserker
from .cleric import Cleric
from .conjurer import Conjurer
from .crusader import Crusader
from .demonologist import Demonologist
from .diviner import Diviner
from .dragoon import Dragoon
from .druid import Druid
from .footpad import Footpad
from .grandmaster import GrandmasterOfArms
from .healer import Healer
from .hierophant import Hierophant
from .inquisitor import Inquisitor
from .knight_enchanter import KnightEnchanter
from .lancer import Lancer
from .lycan import Lycan
from .mage import Mage
from .master_monk import MasterMonk
from .monk import Monk
from .ninja import Ninja
from .paladin import Paladin
from .pathfinder import Pathfinder
from .priest import Priest
from .ranger import Ranger
from .rogue import Rogue
from .seeker import Seeker
from .sentinel import Sentinel
from .shadowcaster import Shadowcaster
from .shaman import Shaman
from .sorcerer import Sorcerer
from .soulcatcher import Soulcatcher
from .spell_stealer import SpellStealer
from .spellblade import Spellblade
from .stalwart_defender import StalwartDefender
from .templar import Templar
from .thaumaturgist import Thaumaturgist
from .thief import Thief
from .troubadour import Troubadour
from .warlock import Warlock
from .warrior import Warrior
from .weapon_master import WeaponMaster
from .wizard import Wizard

classes_dict = {
    "Warrior": {
        "class": Warrior,
        "pro": {
            "Weapon Master": {
                "class": WeaponMaster,
                "pro": {
                    "Berserker": {"class": Berserker},
                    "Grandmaster of Arms": {"class": GrandmasterOfArms},
                },
            },
            "Paladin": {"class": Paladin, "pro": {"Crusader": {"class": Crusader}}},
            "Lancer": {"class": Lancer, "pro": {"Dragoon": {"class": Dragoon}}},
            "Sentinel": {
                "class": Sentinel,
                "pro": {"Stalwart Defender": {"class": StalwartDefender}},
            },
        },
    },
    "Mage": {
        "class": Mage,
        "pro": {
            "Sorcerer": {"class": Sorcerer, "pro": {"Wizard": {"class": Wizard}}},
            "Warlock": {
                "class": Warlock,
                "pro": {
                    "Shadowcaster": {"class": Shadowcaster},
                    "Demonologist": {"class": Demonologist},
                },
            },
            "Spellblade": {
                "class": Spellblade,
                "pro": {"Knight Enchanter": {"class": KnightEnchanter}},
            },
            "Conjurer": {
                "class": Conjurer,
                "pro": {"Thaumaturgist": {"class": Thaumaturgist}},
            },
        },
    },
    "Footpad": {
        "class": Footpad,
        "pro": {
            "Thief": {"class": Thief, "pro": {"Rogue": {"class": Rogue}}},
            "Inquisitor": {"class": Inquisitor, "pro": {"Seeker": {"class": Seeker}}},
            "Assassin": {"class": Assassin, "pro": {"Ninja": {"class": Ninja}}},
            "Spell Stealer": {
                "class": SpellStealer,
                "pro": {"Arcane Trickster": {"class": ArcaneTrickster}},
            },
        },
    },
    "Healer": {
        "class": Healer,
        "pro": {
            "Cleric": {
                "class": Cleric,
                "pro": {
                    "Templar": {"class": Templar},
                    "Hierophant": {"class": Hierophant},
                },
            },
            "Monk": {"class": Monk, "pro": {"Master Monk": {"class": MasterMonk}}},
            "Priest": {"class": Priest, "pro": {"Archbishop": {"class": Archbishop}}},
            "Bard": {"class": Bard, "pro": {"Troubadour": {"class": Troubadour}}},
        },
    },
    "Pathfinder": {
        "class": Pathfinder,
        "pro": {
            "Druid": {
                "class": Druid,
                "pro": {
                    "Lycan": {"class": Lycan},
                    "Archdruid": {"class": Archdruid},
                },
            },
            "Diviner": {
                "class": Diviner,
                "pro": {"Astromancer": {"class": Astromancer}},
            },
            "Shaman": {
                "class": Shaman,
                "pro": {"Soulcatcher": {"class": Soulcatcher}},
            },
            "Ranger": {
                "class": Ranger,
                "pro": {"Beast Master": {"class": BeastMaster}},
            },
        },
    },
}
