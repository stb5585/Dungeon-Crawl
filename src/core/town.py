###########################################
""" Town manager """

import random

from . import enemies, items
from .data.data_loader import get_quests, get_patron_dialogues, get_response_map, get_tavern_flavor_dialogues


# Patron dialogue keyed by minimum total level (base + promotions)
# Loaded from external JSON file
PATRON_DIALOGUES = get_patron_dialogues()

# NPC responses to quest acceptance/rejection
# Loaded from external JSON file
RESPONSE_MAP = get_response_map()

# General tavern flavor comments used when no quests are available/active
# Loaded from external JSON file
TAVERN_FLAVOR_DIALOGUES = get_tavern_flavor_dialogues()


# classes
class BountyBoard:

    def __init__(self):
        self.bounties = []

    def create_bounty(self, game):
        bounty = {"reward": None}
        level = str(min(6, game.player_char.player_level() // 10))
        while True:
            enemy = enemies.random_enemy(level)
            if enemy.name not in game.player_char.quest_dict['Bounty'] and \
                enemy.name not in self.bounty_options():
                break
        bounty["enemy"] = enemy
        bounty["num"] = random.randint(3, 8)
        bounty["exp"] = random.randint(enemy.experience*bounty["num"] // 2, enemy.experience*bounty["num"]) * \
            game.player_char.level.pro_level
        bounty["gold"] = random.randint(25*bounty["num"], 50*bounty["num"]) * game.player_char.player_level()
        if random.randint(0, game.player_char.check_mod('luck', luck_factor=10)):
            item_level = min(8, game.player_char.level.pro_level + random.randint(0, game.player_char.level.pro_level))
            bounty["reward"] = items.random_item(item_level)
        return bounty

    def generate_bounties(self, game):
        num = random.randint(1, 4) - len(game.player_char.quest_dict['Bounty'])
        if num > 0:
            for _ in range(num):
                bounty = self.create_bounty(game)
                self.bounties.append(bounty)

    def bounty_options(self):
        try:
            return [x["name"] for x in self.bounties]
        except KeyError:
            return []

    def accept_quest(self, quest):
        quest_idx = self.bounties.index(quest)
        self.bounties.pop(quest_idx)


# quest dict - loaded from external JSON file
# Using lazy loading to defer resolution of item classes until needed
_quest_dict_cache = None

def get_quest_dict():
    """Lazy load quests from JSON data file."""
    global _quest_dict_cache
    if _quest_dict_cache is None:
        _quest_dict_cache = get_quests()
    return _quest_dict_cache


# For backward compatibility, create module-level variable
quest_dict = get_quest_dict()

# Note: The quest_dict has been moved to src/data/content/quests.json
# This module uses get_quests() from data_loader to load it with resolved item references
