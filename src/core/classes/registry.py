"""Class promotion registry."""

from __future__ import annotations

from .warrior import Warrior
from .weapon_master import WeaponMaster
from .grandmaster import GrandmasterOfArms
from .berserker import Berserker
from .paladin import Paladin
from .crusader import Crusader
from .lancer import Lancer
from .dragoon import Dragoon
from .sentinel import Sentinel
from .stalwart_defender import StalwartDefender
from .mage import Mage
from .sorcerer import Sorcerer
from .wizard import Wizard
from .warlock import Warlock
from .shadowcaster import Shadowcaster
from .demonologist import Demonologist
from .spellblade import Spellblade
from .knight_enchanter import KnightEnchanter
from .conjurer import Conjurer
from .thaumaturgist import Thaumaturgist
from .footpad import Footpad
from .thief import Thief
from .rogue import Rogue
from .inquisitor import Inquisitor
from .seeker import Seeker
from .assassin import Assassin
from .ninja import Ninja
from .spell_stealer import SpellStealer
from .arcane_trickster import ArcaneTrickster
from .healer import Healer
from .cleric import Cleric
from .templar import Templar
from .hierophant import Hierophant
from .priest import Priest
from .archbishop import Archbishop
from .monk import Monk
from .master_monk import MasterMonk
from .bard import Bard
from .troubadour import Troubadour
from .pathfinder import Pathfinder
from .druid import Druid
from .lycan import Lycan
from .archdruid import Archdruid
from .diviner import Diviner
from .astromancer import Astromancer
from .shaman import Shaman
from .soulcatcher import Soulcatcher
from .ranger import Ranger
from .beast_master import BeastMaster


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
            "Paladin": {
                "class": Paladin,
                "pro": {"Crusader": {"class": Crusader}}
                },
            "Lancer": {
                "class": Lancer,
                "pro": {"Dragoon": {"class": Dragoon}}
                },
            "Sentinel": {
                "class": Sentinel,
                "pro": {"Stalwart Defender": {"class": StalwartDefender}},
            },
        },
    },
    "Mage": {
        "class": Mage,
        "pro": {
            "Sorcerer": {
                "class": Sorcerer,
                "pro": {"Wizard": {"class": Wizard}}
            },
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
            "Thief": {
                "class": Thief,
                "pro": {"Rogue": {"class": Rogue}}
                },
            "Inquisitor": {
                "class": Inquisitor,
                "pro": {"Seeker": {"class": Seeker}}
                },
            "Assassin": {
                "class": Assassin,
                "pro": {"Ninja": {"class": Ninja}}
                },
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
                }
            },
            "Monk": {
                "class": Monk,
                "pro": {"Master Monk": {"class": MasterMonk}}
            },
            "Priest": {
                "class": Priest,
                "pro": {"Archbishop": {"class": Archbishop}}
            },
            "Bard": {
                "class": Bard,
                "pro": {"Troubadour": {"class": Troubadour}}
            },
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
