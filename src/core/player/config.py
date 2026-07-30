"""Player navigation, location, and Bestiary constants."""

DIRECTIONS = {
    "north": {
        "move": (0, -1),
        "char": "\u2191"
        },
    "south": {
        "move": (0, 1),
        "char": "\u2193"
        },
    "east": {
        "move": (1, 0),
        "char": "\u2192"
        },
    "west": {"move": (-1, 0),
             "char": "\u2190"
             }
    }


REALM_OF_CAMBION_LEVEL = 8
LIMINAL_GAP_LEVEL = 9
LIMINAL_GAP_ENTRY_POS = (5, 7, LIMINAL_GAP_LEVEL)
LIMINAL_GAP_ENTRY_FACING = "north"
RESISTANCE_DISPLAY_ORDER = ("Fire", "Electric", "Earth", "Shadow", "Poison", "Ice", "Water", "Wind", "Holy", "Physical")
BASIC_BESTIARY_ACTIONS = {None, "", "Attack", "Defend", "Nothing", "Use Item", "Pickup Weapon"}
