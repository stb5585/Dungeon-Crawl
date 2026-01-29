"""
Inn/Tavern system for GUI - handles rest, patron dialogue, and bounty board.
Implements the core tavern logic from town.py adapted for Pygame presenter.
"""

import random
import textwrap

from .level_up import LevelUpScreen
from .confirmation_popup import ConfirmationPopup
from .location_menu import LocationMenuScreen
from .town_base import TownScreenBase


# Patron dialogue keyed by minimum total level (base + promotions)
PATRON_DIALOGUES = {
    "Barkeep": {
        1: [
            "If you want to access the character menu, you can do so by hitting the (c) button.",
            "Make sure to stop by from time to time. You never know who might show up.",
            "Equipment vendors will show you how an item can improve or hurt your fighting ability. If an item type doesn't show any change, your class can't use it.",
            "Heavier armor provides better protection but lowers your mobility in combat. Choose carefully.",
        ],
        5: [
            "How did you like that stat bonus at level 4? You get another every 4th level, so plan your promotions accordingly.",
            "If you get a quest from someone, come back and talk with them after it is completed and they will likely reward you for your efforts.",
        ],
        10: [
            "Locked chests contain more powerful items compared with unlocked ones, however you need a key or a lockpick to get to the treasure.",
            "Boss enemies have true sight, so that Invisibility Pendant is useless against them.",
            "Some status effects last until the end of combat or until healed. Make sure to stock up on potions!",
        ],
    },
    "Waitress": {
        1: [
            "Entering the town will replenish your health and mana. Seems like you could take advantage of that.",
            "Sorry, I can't talk now! I am getting married and need to make as much money as I can.",
        ],
        5: [
            "Some spells can be cast outside of battle. You can do so in the Character Menu after inspecting the spell.",
        ],
        10: [
            "(sobbing) I can't believe it...a week before our wedding and my husband to be decides to join the fight against the prime evil...I want to be mad but he says he can't stand by when I am in danger. My hero...",
        ],
        25: [
            "Joffrey returned yesterday bloodied but resolute. He has gained much experience and hopes to have found the source of our suffering by month's end. I gave him my lucky pendant to return to me when his mission is complete.",
        ],
    },
    "Soldier": {
        10: [
            "You may find locked doors along your path while exploring the dungeon. You can't open these with just any old key, you need an actual Old Key.",
            "Watch your carry weight in the Character Menu. If you try to carry more than you can manage, you will become encumbered, which affects your speed in combat.",
            "Check the shops periodically, you may notice new items available to buy.",
        ],
        25: [
            "I just finished my shift guarding the old warehouse behind the barracks. They won't tell us what's in there but I have seen several scientists come and go.",
        ],
        65: [
            "The Devil is immune to normal weapons but legend says there is a material that will do the job.",
        ],
    },
    "Drunkard": {
        8: ["(hic)...I am not as think as you drunk I am...(hic)"],
        25: ["Do you see (hic) that person in the corner? What's their deal, TAKE THE HOOD OFF ALREADY!...ah whatever..."],
        30: ["(hic)...I heard tell there were secret passages...(hic) in the dungeon."],
        65: [
            "We are all praying for your success and survival!",
            "Rutger used to talk about a so-called Master key, that could open any lock. I wonder how much truth was in that.",
        ],
    },
    "Busboy": {
        1: [
            "The waitress left crying some time ago...sounds like her fiance was killed in the dungeons.",
            "Entering the town will replenish your health and mana. Seems like you could take advantage of that.",
            "Some spells can be cast outside of battle. You can do so in the Character Menu after inspecting the spell.",
            "The guy in the corner gives me the creeps...tips well though.",
        ],
    },
    "Hooded Figure": {
        25: ["..."],
        35: ["Hmm...interesting..."],
        50: ["Your power has grown...I am impressed."],
        60: ["Have you defeated the Red Dragon yet?"],
    },
}

# General tavern flavor comments used when no quests are available/active
TAVERN_FLAVOR_DIALOGUES = [
    "I heard there are powerful artifacts deep in the dungeon...",
    "Many adventurers have entered the dungeon, but few return.",
    "They say the evil grows stronger with each passing day.",
    "Be careful down there, adventurer. The monsters are cunning.",
    "I lost my brother to the dungeon. Please, be safe.",
    "The blacksmith Griswold is the best in the kingdom!",
    "If you need potions, visit the alchemist. They saved my life once.",
    "I've heard rumors of a secret shop somewhere in the depths...",
    "The barracks offers bounties for hunting dangerous creatures.",
    "Some say there's treasure beyond imagination in the depths."
]


class InnManager(TownScreenBase):
    """Manages inn/tavern interactions with pygame presenter."""
    
    def __init__(self, presenter, player_char):
        super().__init__(presenter)
        self.player_char = player_char
        self.level_up_screen = LevelUpScreen(presenter.screen, presenter)
    
    def visit_inn(self):
        """Visit the inn/tavern - integrates with The Thirsty Dog tavern."""
        inn_options = ["Talk to Patrons", "Bounty Board", "Leave"]
        
        inn_screen = LocationMenuScreen(self.presenter, "The Thirsty Dog Tavern")
        
        while True:
            choice_idx = inn_screen.navigate(inn_options)
            
            if choice_idx is None or choice_idx == 2:  # Leave
                popup = ConfirmationPopup(self.presenter, "Come back whenever you'd like.", show_buttons=False)
                popup.show(background_draw_func=lambda: self.draw_background())
                break
            
            elif choice_idx == 0:  # Talk to patrons
                self.talk_to_patrons()
            
            elif choice_idx == 1:  # Bounty Board
                self.show_bounty_board()

    def _random_patron_comment(self, patron: str) -> str | None:
        # Gather patron-specific dialogues eligible for the player's level
        combined_pool: list[str] = []
        dialogues = PATRON_DIALOGUES.get(patron)
        player_level = self.player_char.player_level()
        if dialogues:
            eligible_levels = [lvl for lvl in dialogues if player_level >= lvl]
            if dialogues and eligible_levels:
                # Drunkard uses only the high-tier messages once level 65 is reached
                if patron == "Drunkard" and player_level >= 65:
                    eligible_levels = [lvl for lvl in eligible_levels if lvl == 65]
                chosen_level = random.choice(eligible_levels)
                combined_pool.extend(dialogues[chosen_level])

        # Always include general tavern flavor comments in the random pool
        combined_pool.extend(TAVERN_FLAVOR_DIALOGUES)

        return random.choice(combined_pool) if combined_pool else None
    
    def talk_to_patrons(self):
        """Talk to tavern patrons and access their quests."""
        # Build patron list similar to town.patron_list
        options = ["Barkeep"]
        if 'A Bad Dream' in self.player_char.quest_dict.get('Main', {}):
            if not self.player_char.quest_dict['Main']['A Bad Dream'].get('Turned In'):
                options.append("Waitress")
            else:
                options.append('Busboy')
        else:
            options.append('Waitress')
        if self.player_char.player_level() >= 8:
            options.append("Drunkard")
            if self.player_char.player_level() >= 10:
                options.append("Soldier")
                if self.player_char.player_level() >= 25:
                    if 'Red Dragon' in self.player_char.quest_dict.get('Main', {}):
                        if not self.player_char.quest_dict['Main']['Red Dragon'].get('Turned In'):
                            options.append("Hooded Figure")
                    else:
                        options.append("Hooded Figure")
        options.append('Back')

        patrons_screen = LocationMenuScreen(self.presenter, "The Thirsty Dog - Patrons")
        
        while True:
            choice = patrons_screen.navigate(options, reset_cursor=False)
            if choice is None or (choice is not None and options[choice] == 'Back'):
                return

            patron = options[choice]
            # Route to quest manager for applicable quest givers
            if patron in ("Barkeep", "Waitress", "Soldier", "Busboy", "Hooded Figure", "Drunkard"):
                from .quest_manager import QuestManager
                qm = QuestManager(
                    self.presenter, 
                    self.player_char, 
                    background_draw_func=lambda: self.draw_background(),
                    quest_text_renderer=lambda text: patrons_screen.display_quest_text(text)
                )
                did_action, showed_message = qm.check_and_offer(patron, show_help=False, suppress_no_quests_message=True)
                if not did_action and not showed_message:
                    # Mix a random patron comment with a random quest help hint
                    pool = []
                    hint = qm.get_random_help_hint(patron)
                    if hint:
                        pool.append(hint)
                    comment = self._random_patron_comment(patron)
                    if comment:
                        pool.append(comment)
                    if pool:
                        selection = random.choice(pool)
                        wrapped_selection = "\n".join(textwrap.wrap(selection, width=52))
                        qm.quest_text_renderer(wrapped_selection)
            else:
                # This branch is not used since all patrons are handled above,
                # but keep a fallback to show a general tavern flavor comment.
                patron_dialogue = random.choice(TAVERN_FLAVOR_DIALOGUES)
                popup = ConfirmationPopup(self.presenter, patron_dialogue, show_buttons=False)
                popup.show(background_draw_func=lambda: self.draw_background())
    
    def show_bounty_board(self):
        """Show and manage bounty quests from the tavern."""
        # Check for completable bounties
        bounty_dict = self.player_char.quest_dict.get('Bounty', {})
        
        bounty_screen = LocationMenuScreen(self.presenter, "Bounty Board")
        
        while True:
            bounty_options = ["Accept Bounty", "View Active Bounties", "Leave"]
            
            # Check if any bounties are complete
            completable = [name for name, data in bounty_dict.items() if data[2]]
            if completable:
                bounty_options.insert(1, "Turn In Bounty")
            
            choice_idx = bounty_screen.navigate(bounty_options)
            
            if choice_idx is None or bounty_options[choice_idx] == "Leave":
                break
            
            if bounty_options[choice_idx] == "Accept Bounty":
                self.accept_bounty()
            
            elif bounty_options[choice_idx] == "Turn In Bounty":
                self.turn_in_bounty(completable)
            
            elif bounty_options[choice_idx] == "View Active Bounties":
                self.view_active_bounties()
    
    def accept_bounty(self):
        """Accept a bounty from the board."""
        bounty_dict = self.player_char.quest_dict.get('Bounty', {})
        
        # Get available bounties
        bounties_available = []
        if hasattr(self.presenter, 'game') and hasattr(self.presenter.game, 'bounties'):
            game_bounties = self.presenter.game.bounties
            # Only offer bounties the player doesn't already have
            for bounty_name in game_bounties.keys():
                if bounty_name not in bounty_dict:
                    bounties_available.append(bounty_name)
        
        if not bounties_available:
            popup = ConfirmationPopup(self.presenter, "No new bounties available at this time.", show_buttons=False)
            popup.show(background_draw_func=lambda: self.draw_background())
            return
        
        bounty_screen = LocationMenuScreen(self.presenter, "Accept Bounty")
        
        # Build display list
        bounty_display = [(name, 0) for name in bounties_available]
        bounty_display.append(("Back", 0))
        
        choice = bounty_screen.navigate_with_content(bounty_display)
        
        if choice is None or bounty_display[choice][0] == "Back":
            return
        
        bounty_name = bounty_display[choice][0]
        bounty_data = self.presenter.game.bounties[bounty_name]
        enemy_obj = bounty_data.get("enemy")
        enemy_name = getattr(enemy_obj, "name", bounty_data.get("enemy_name", "Unknown"))
        
        # Add bounty to player's quest dict
        self.player_char.quest_dict['Bounty'][bounty_name] = [bounty_data, 0, False]
        
        # Show bounty info
        info_msg = (
            f"Bounty Accepted: {bounty_name}\n"
            f"Target: {enemy_name}\n"
            f"Enemies to defeat: {bounty_data.get('num', 1)}\n"
            f"Reward: {bounty_data.get('gold', 0)} Gold, {bounty_data.get('exp', 0)} Experience"
        )
        popup = ConfirmationPopup(self.presenter, info_msg, show_buttons=False)
        popup.show(background_draw_func=lambda: self.draw_background())
    
    def turn_in_bounty(self, completable):
        """Turn in completed bounties using the inn UI."""
        if not completable:
            popup = ConfirmationPopup(self.presenter, "No bounties to turn in.", show_buttons=False)
            popup.show(background_draw_func=lambda: self.draw_background())
            return

        bounty_screen = LocationMenuScreen(self.presenter, "Turn In Bounty")
        bounty_options = list(completable) + ["Back"]

        choice_idx = bounty_screen.navigate(bounty_options)

        if choice_idx is None or bounty_options[choice_idx] == "Back":
            return

        bounty_name = bounty_options[choice_idx]
        bounty_data = self.player_char.quest_dict['Bounty'].get(bounty_name)
        if not bounty_data:
            popup = ConfirmationPopup(self.presenter, "That bounty is no longer available.", show_buttons=False)
            popup.show(background_draw_func=lambda: self.draw_background())
            return

        bounty = bounty_data[0]

        # Award rewards
        gold = bounty.get("gold", 0)
        exp = bounty.get("exp", 0)
        self.player_char.gold += gold
        self.player_char.level.exp += exp

        if not self.player_char.max_level():
            self.player_char.level.exp_to_gain -= exp

        reward_lines = [
            f"Bounty Complete: {bounty_name}",
            "",
            "Rewards:",
            f"• {gold} Gold",
            f"• {exp} Experience",
        ]

        if bounty.get("reward"):
            reward_item = bounty["reward"]()
            self.player_char.modify_inventory(reward_item)
            reward_lines.append(f"• {reward_item.name}")

        reward_msg = "\n".join(reward_lines)
        popup = ConfirmationPopup(self.presenter, reward_msg, show_buttons=False)
        popup.show(background_draw_func=lambda: self.draw_background())

        # Remove completed bounty
        del self.player_char.quest_dict['Bounty'][bounty_name]

        # Check for level up
        if not self.player_char.max_level():
            while self.player_char.level.exp_to_gain <= 0:
                self.level_up()
                if self.player_char.level.exp_to_gain == "MAX":
                    break
    
    def view_active_bounties(self):
        """View all active bounty quests."""
        bounty_dict = self.player_char.quest_dict.get('Bounty', {})
        
        if not bounty_dict:
            popup = ConfirmationPopup(self.presenter, "No active bounties.\n\nCheck back later for new opportunities!", show_buttons=False)
            popup.show(background_draw_func=lambda: self.draw_background())
            return
        
        bounty_screen = LocationMenuScreen(self.presenter, "Active Bounties")
        
        # Build display list
        bounty_display = []
        for name, data in bounty_dict.items():
            bounty = data[0]
            killed = data[1]
            complete = data[2]
            status = "✓ Complete" if complete else f"{killed}/{bounty['num']} killed"
            display_text = f"{name} - {status}"
            bounty_display.append((display_text, 0))
        
        bounty_display.append(("Back", 0))
        
        choice = bounty_screen.navigate_with_content(bounty_display)
        
        if choice is None or bounty_display[choice][0] == "Back":
            return
    
    def level_up(self):
        """Handle level up with GUI interface."""
        # show_level_up already displays all level-up information
        self.level_up_screen.show_level_up(self.player_char, None)
