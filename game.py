"""
The main module to run the Dungeon Crawl game.
"""

# Imports
import sys
import random
import time
import glob
import curses
import pickle

import utils
import town
import player
from races import races_dict
from classes import classes_dict
from character import Stats, Resource, Level


# objects
class Game:

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.load_files = glob.glob('save_files/*')
        self.races_dict = races_dict
        self.classes_dict = classes_dict
        self.player_char = None
        self.time = time.time()
        self.bounties = {}
        curses.curs_set(0)  # Hide cursor
        self.main_menu()

    def main_menu(self):
        menu = utils.MainMenu(self)
        menu.clear()
        menu_options = ['New Game', 'Settings', 'Exit']
        if self.load_files:
            menu_options.insert(1, "Load Game")
        menu.update_options(menu_options)
        while True:
            done = False
            while not done:
                selected_idx = menu.navigate_menu()
                if menu_options[selected_idx] == 'New Game':
                    menu.clear()
                    self.player_char = self.new_game()
                    if self.player_char:
                        done = True
                        break
                elif menu_options[selected_idx] == 'Load Game':
                    self.player_char = self.load_game(menu)
                    if self.player_char:
                        done = True
                    menu.update_options(menu_options)
                elif menu_options[selected_idx] == 'Settings':
                    pass
                else:
                    sys.exit(0)  # Exit the game
                menu.update_options(menu_options)
            menu.clear()
            self.run()
            menu.update_options(menu_options)

    def run(self):
        self.update_bounties()
        while not self.player_char.quit:
            self.player_char.encumbered = self.player_char.current_weight() > self.player_char.max_weight()
            if time.time() - self.time > (900 * self.player_char.level.pro_level):
                self.update_bounties()
            if self.player_char.in_town():
                self.player_char.state = 'normal'
                self.player_char.health.current = self.player_char.health.max
                self.player_char.mana.current = self.player_char.mana.max
                town.town(self)
            else:
                self.navigate()

    def new_game(self):
        time.sleep(0.5)
        texts = [
            "A great evil has taken hold in the unlikeliest of places, a small town on the edge of the kingdom.",
            "The town of Silvana has sent out a plea for help, with many coming from far and wide to test their mettle.",
            "You, bright-eyed and bushy-tailed, decided that fame and glory were within reach.",
            "What you didn't know was that all who had attempted this feat have never been heard from again.",
            "Will you be different or just another lost soul?",
        ]
        # TODO uncomment
        # texts_pad = utils.QuestPopupMenu(self, box_height=len(texts)+2, box_width=len(max(texts, key=len))+4)
        # texts_pad.draw_popup(texts)
        # self.stdscr.getch()

        # Select the race of the character
        menu = utils.NewGameMenu(self)
        while True:
            menu.update_options()
            while True:
                race = menu.navigate_menu()
                if not race:
                    return
                else:
                    confirm_str = f"Are you sure you want to play as a {race.name.lower()}?"
                    confirm = utils.ConfirmPopupMenu(self, confirm_str, box_height=7)
                    if confirm.navigate_popup():
                        break
                    menu.page = 1
            
            # Select the class of the character
            menu.update_options()
            while True:
                cls = menu.navigate_menu()
                if not cls:
                    break
                confirm_str = f"Are you sure you want to play as a {cls.name.lower()}?"
                confirm = utils.ConfirmPopupMenu(self, confirm_str, box_height=7)
                if confirm.navigate_popup():
                    break
            if cls:
                break
            if menu.options_list[menu.current_option] == "Go Back":
                return

        enternamebox = utils.TextBox(self)
        while True:
            name_message = "What is your character's name?"
            name = utils.player_input(self, name_message).capitalize()
            if not name:
                enternamebox.print_text_in_rectangle("Name cannot be empty.")
                self.stdscr.getch()
                enternamebox.clear_rectangle()
            else:
                menu.clear()
                confirm_str = f"Are you sure you want to name your character {name}?"
                confirm = utils.ConfirmPopupMenu(self, confirm_str, box_height=7)
                if confirm.navigate_popup():
                    break
        menu.clear()

        created = f"Welcome {name}, the {race.name} {cls.name}.\nReport to the barracks for your orders."
        enternamebox.print_text_in_rectangle(created)
        self.stdscr.getch()
        enternamebox.clear_rectangle()

        # Define the player character
        location_x, location_y, location_z = (5, 10, 0)
        stats = tuple(map(lambda x, y: x + y, (race.strength, race.intel, race.wisdom, race.con, race.charisma, race.dex),
                        (cls.str_plus, cls.int_plus, cls.wis_plus, cls.con_plus, cls.cha_plus, cls.dex_plus)))
        hp = stats[3] * 2  # starting HP equal to constitution x 2
        mp = stats[1] + int(stats[2] * 0.5)  # starting MP equal to intel and wis x 0.5
        gold = stats[4] * 25  # starting gold equal to charisma x 25
        player_char = player.Player(location_x, location_y, location_z, level=Level(),
                            health=Resource(hp, hp), mana=Resource(mp, mp),
                            stats=Stats(stats[0], stats[1], stats[2], stats[3], stats[4], stats[5]),
                            gold=gold, resistance=race.resistance)
        player_char.name = name
        player_char.race = race
        player_char.cls = cls
        player_char.equipment = cls.equipment
        player_char.load_tiles()

        return player_char


    def load_game(self, menu):
        player_char = None
        load_options = []
        for f in self.load_files:
            load_options.append(f.split(".")[0].split("/")[-1].capitalize())
        load_options.append("Go Back")
        menu = utils.LoadGameMenu(self, load_options)
        selected_idx = menu.navigate_menu()
        if load_options[selected_idx] == "Go Back":
            return
        with open(self.load_files[selected_idx], "rb") as save_file:
            player_dict = pickle.load(save_file)
        player_char = player.load_char(player_dict=player_dict)
        # player_char.load_tiles()  # uncomment for testing tile changes

        return player_char

    def navigate(self):
        room = self.player_char.world_dict[
            (self.player_char.location_x, self.player_char.location_y, self.player_char.location_z)
            ]
        try:
            room.special_text(self)
        except AttributeError:
            pass
        room.modify_player(self)
        dmenu = utils.DungeonMenu(self)
        dmenu.draw_all()
        dmenu.refresh_all()
        while True:
            if self.player_char.in_town() or "Shop" in str(room):
                return
            available_actions = room.available_actions(self.player_char)
            if self.player_char.state == "normal":
                room.enemy = None
                action_input = self.stdscr.getch()
                for action in available_actions:
                    available_hotkeys = [x['hotkey'] for x in available_actions]
                    try:
                        if chr(action_input) == action['hotkey']:
                            action['method'](self.player_char, self)
                            if chr(action_input) in available_hotkeys and \
                                ("Move" in action['name'] or "Open" in action['name'] or "stairs" in action['name']):
                                return
                    except TypeError:
                        pass
            else:
                self.battle(room.enemy)
            dmenu.draw_all()
            dmenu.refresh_all()

    def battle(self, enemy):
        """
        Function that controls combat
        """

        def initiative(player_char, enemy):
            """
            Determine who goes char using each character's dexterity plus luck
            """
            if player_char.encumbered:
                return enemy, player_char
            if player_char.invisible:
                if not enemy.sight:
                    if player_char.cls.name == "Shadowcaster" and player_char.power_up:
                        player_char.status_effects['Power Up'].active = True
                        player_char.status_effects['Power Up'].duration = 1
                    return player_char, enemy
            if enemy.invisible:
                if not player_char.sight:
                    return enemy, player_char
            p_chance = player_char.stats.dex + player_char.check_mod('luck', luck_factor=10)
            e_chance = enemy.stats.dex + enemy.check_mod('luck', luck_factor=10)
            total_chance = p_chance + e_chance
            chance_list = [p_chance / total_chance, e_chance / total_chance]
            attacker = random.choices([player_char, enemy], chance_list)[0]
            defender = player_char if attacker == enemy else enemy
            return attacker, defender

        battlebox = utils.TextBox(self)
        while True:
            key = self.stdscr.getch()
            if key == curses.KEY_ENTER or key in [10, 13]:
                break
        flee = False
        first, second = initiative(self.player_char, enemy)
        tile = self.player_char.world_dict[(self.player_char.location_x, self.player_char.location_y, self.player_char.location_z)]
        vision = self.player_char.sight and 'Boss' not in str(tile)
        combat = True
        cmenu = utils.CombatMenu(self)
        popup = utils.CombatPopupMenu(self, "Test")
        while combat:
            available_actions = tile.available_actions(self.player_char)
            cmenu.draw_enemy(enemy, vision=vision)
            cmenu.draw_options(available_actions)
            cmenu.draw_char()
            cmenu.refresh_all()
            if not any([first.status_effects['Prone'].active,
                        first.status_effects['Stun'].active,
                        first.status_effects['Sleep'].active]):
                if first == self.player_char:
                    while True:
                        cmenu.current_option = 0
                        available_actions = tile.available_actions(self.player_char)
                        cmenu.draw_enemy(enemy, vision=vision)
                        cmenu.draw_options(available_actions)
                        cmenu.draw_char()
                        cmenu.refresh_all()
                        action_idx = cmenu.navigate_menu()
                        action = available_actions[action_idx]
                        combat_text = ""
                        valid_entry = False
                        flee = False
                        tile = first.world_dict[(first.location_x, first.location_y, first.location_z)]
                        if action == 'Untransform':
                            combat_text += first.transform(back=True)
                            valid_entry = False
                        elif action == "Transform":
                            combat_text += first.transform()
                            valid_entry = False
                        else:
                            if action == 'Open':
                                first.open_up(self)
                                valid_entry = True
                            elif action == 'Attack':
                                wd_str, _, _ = first.weapon_damage(second)
                                combat_text += wd_str
                                valid_entry = True
                            elif action == 'Use Item':
                                use_str, valid_entry = first.use_item(self, second)
                                combat_text += use_str
                            elif action == 'Flee':
                                flee, flee_str = first.flee(second)
                                combat_text += flee_str
                                valid_entry = True
                            elif action == 'Cast Spell':
                                spell_list = []
                                for entry in first.spellbook['Spells']:
                                    if first.spellbook['Spells'][entry].subtyp == "Movement":
                                        continue
                                    if first.spellbook['Spells'][entry].cost <= first.mana.current:
                                        spell_list.append(str(entry) + '  ' + str(first.spellbook['Spells'][entry].cost))
                                spell_list.append('Go Back')
                                popup.update_options(spell_list, ["Spells"])
                                spell_index = popup.navigate_popup()
                                if spell_list[spell_index] == 'Go Back':
                                    valid = False
                                else:
                                    spell = first.spellbook['Spells'][spell_list[spell_index].split('  ')[0]]
                                    spell_str = f"{first.name} casts {spell.name}.\n"
                                    spell_str += spell.cast(first, target=second)
                                    combat_text += spell_str
                                    valid_entry = True
                            elif action == 'Use Skill':
                                skill_list = []
                                for entry in first.spellbook['Skills']:
                                    if first.spellbook['Skills'][entry].cost <= first.mana.current:
                                        if any([first.spellbook['Skills'][entry].passive,
                                                first.spellbook['Skills'][entry].name == 'Smoke Screen' and 'Boss' in str(tile),
                                                first.spellbook['Skills'][entry].name == 'Lockpick',
                                                first.spellbook['Skills'][entry].name == 'Shield Slam' and \
                                                first.equipment['OffHand'].subtyp != 'Shield',
                                                first.spellbook['Skills'][entry].name == 'Mortal Strike' and \
                                                first.equipment['Weapon'].handed == 1]):
                                            continue
                                        if entry == "Mana Shield" and first.status_effects['Mana Shield'].active:
                                            skill_list.append('Remove Shield  ' + str(first.spellbook['Skills'][entry].cost))
                                        else:
                                            skill_list.append(str(entry) + '  ' + str(first.spellbook['Skills'][entry].cost))
                                skill_list.append('Go Back')
                                popup.update_options(skill_list, ["Skills"])
                                skill_index = popup.navigate_popup()
                                if skill_list[skill_index] == 'Go Back':
                                    valid = False
                                else:
                                    skill_name = skill_list[skill_index].split('  ')[0]
                                    if skill_name == "Remove Shield":
                                        skill_name = "Mana Shield"
                                    valid = True
                                    skill = first.spellbook['Skills'][skill_name]
                                    skill_str = f"{first.name} uses {skill.name}.\n"
                                    if skill.name == 'Smoke Screen':
                                        skill_str += skill.use(first, target=second)
                                        flee, flee_str = first.flee(second, smoke=True)
                                        skill_str += flee_str
                                    # elif skill.name == 'Transform':
                                    #     skill_str += first.transform()
                                    #     valid = False
                                    elif skill.name == "Slot Machine":
                                        skill_str += skill.use(self, first, target=second)
                                    elif skill.name in ["Doublecast", "Triplecast"]:
                                        skill_str += skill.use(first, second, game=self)
                                    else:
                                        skill_str += skill.use(first, target=second)
                                    combat_text += skill_str
                                    valid_entry = valid
                        combat_text += first.special_effects(second)
                        if combat_text:
                            combatbox = utils.TextBox(self)
                            combatbox.print_text_in_rectangle(combat_text)
                            self.stdscr.getch()
                            combatbox.clear_rectangle()
                        if flee:
                            combat = False
                            # Moves first randomly to an adjacent tile
                            available_moves = tile.adjacent_moves(first)
                            r = random.choice(available_moves)
                            r['method'](first, self)
                        if valid_entry:
                            break
                else:
                    action = first.options(action_list=available_actions)
                    _, combat, flee = first.combat_turn(self, second, action, combat)
            else:
                if first.status_effects['Stun'].active:
                    combat_text = "stunned"
                elif first.status_effects['Sleep'].active:
                    combat_text = "asleep"
                else:
                    combat_text = "prone"
                combat_text = f"{first.name} is {combat_text}."
                battlebox.print_text_in_rectangle(combat_text)
                self.stdscr.getch()
                battlebox.clear_rectangle()
            if not combat:
                break

            # Familiar's turn
            if second.is_alive():
                familiar_text = first.familiar_turn(second)
                if familiar_text:
                    battlebox.print_text_in_rectangle(familiar_text)
                    self.stdscr.getch()
                    battlebox.clear_rectangle()

            if not second.is_alive():
                if 'Resurrection' in first.spellbook['Spells'] and \
                        abs(first.health.current) <= first.mana.current:
                    res_text = second.spellbook['Spells']['Resurrection'].cast(second, target=first)
                    battlebox.print_text_in_rectangle(res_text)
                    self.stdscr.getch()
                    battlebox.clear_rectangle()
                    combat = True
                else:
                    combat = False

            if not combat:
                break

            # resolve status effects
            status_text = first.statuses(self)
            if status_text:
                if "damage" in status_text:
                    try:
                        second.health.current -= int(status_text.split(" damage")[0].split(" ")[-1])
                    except ValueError:
                        pass
                battlebox.print_text_in_rectangle(status_text)
                self.stdscr.getch()
                battlebox.clear_rectangle()

            if not first.is_alive():
                break

            if first == self.player_char:
                first = enemy
                second = self.player_char
            else:
                first = self.player_char
                second = enemy

        self.player_char.end_combat(self, enemy, tile, flee=flee)
        if self.player_char.is_alive() and "Boss" in str(tile):
            tile.defeated = True
        # return self.player_char.is_alive()

    def update_bounties(self):
        self.bounties = {}
        bounties = town.BountyBoard()
        bounties.generate_bounties(self)
        for bounty in bounties.bounties:
            self.bounties[bounty["enemy"].name] = bounty

    def delete_bounty(self, bounty):
        del self.bounties[bounty["enemy"].name]

    def special_event(self, name):
        text = special_event_dict[name]["Text"]
        pad = utils.QuestPopupMenu(self, box_height=len(text)+2, box_width=len(max(text, key=len))+4)
        pad.draw_popup(text)
        

special_event_dict = {
    "Timmy": {
        "Text": [
            "'Hello...who's there?'",
            "You see a small child peak out from behind some rubble.",
            "'This place is scary...I want to go home.'",
            "You have found the little boy, Timmy, and escort him home."
            ]
    },
    "Unobtainium": {
        "Text": [
            "A brilliant column of light highlights the small piece of ore on a pedestal at the center of the room.",
            "You approach it with caution but find no traps or tricks.",
            "This must be the legendary ore you have heard so much about...",
            "You reach for it, half expecting to be obliterated...but all you feel is warmth throughout your body.",
            "You have obtained the Unobtainium!"
            ]
    },
    "Dead Body": {
        "Text" : [
            "Before you lies the body of a warrior, battered, bloody, and broken...",
            "This must be the body of Joffrey, the one betrothed to the waitress at the tavern.",
            "You move the body for a proper burial and notice a crushed gold locket lying on the ground.",
            "You should return this to its rightful owner..."
            ]
    },
    "Waitress": {
        "Text" : [
            "(cry)...why, why did you have to leave me, Joffrey...",
            "Who...who's there..leave me, I do not wish to be disturbed...",
            "WAIT, IT'S YOU! YOU FAILED MY BELOVED JOFFREY!",
            "WHY DIDN'T YOU SAVE HIM?! YOU WILL MEET THE SAME FATE!!"
            ]
    },
    "Joffrey's Key": {
        "Text" : [
            "That key that you have...that's one of our storage locker keys.",
            "You say you got this from the waitress at the tavern?",
            "She attacked you?! Well, I guess she lost her mind after Joffrey's death.",
            "Maybe this key is to his locker. Let me see...yes it is.",
            "All that's left inside are some potions and this letter.",
            "'My love, I know you have questions but the answers will not be to your liking...",
            "forgive me but I could not resist his will. If you are reading this, it means I am dead...",
            "please remember that above all, I love you.' -Joffrey",
            "Not sure what he is referring to when he said he could not resist his will. Something doesn't seem right...",
            "Keep you wits about you, there's evil afoot.", 
            "Since there is no one left to claim his things, you can have what's left. Put them to good use."
        ]
    },
    "Power Up": {
        "Text" : [
            "You enter into the back of the blacksmith shop and see what looks like a metal coffin glowing green.",
            "'Climb on in, we have some work to do.' You enter the machine against your better judgment.",
            "Griswold stands behind a panel and after a few button presses, you see the green glow around you grow.",
            "You are suddenly overwhelmed with a pain you've never felt. You stifle a scream but it is becoming unbearable.",
            "Just as you think you can't take more, the whir of the machine begins to wane.",
            "Your whole body hurts but strangely you feel a power inside of you that you have never experienced.",
            "'How do you feel? Any different?' You exit the chamber more powerful than you entered it."
        ]
    },
    "Final Blocker": {
        "Text": [
            "The invisible force that once blocked you path is now gone.",
            "What lies ahead is unknown.",
            "Proceed at your own peril..."
            ]
    },
    "Final Boss": {
        "Text": [
            "You enter a massive room. A great beast greets you.",
            "\"Hello again. You have done well to reach me, many have tried and failed.",
            "The bones of those that came before you litter this sanctum. Will your bones join them?",
            "It would seem our meeting was inevitable but it still doesn't lessen the sorrow I feel,",
            "knowing that one of us will not leave here alive.",
            "I give you but one chance to reconsider, after which I will not go easy on you.\""
            ]
    },
    "Relic Room": {
        "Text": [
            "A bright column of light highlights a pedestal at the center of the room.",
            "You instantly realize the significance of the finding, sure that this is one of the six relics you seek.",
            "You eagerly take the relic and instantly feel rejuvenated.",
            "You have obtained a relic!"
            ]
    },
    "Secret Shop": {
        "Text": [
            "Who's there?! Oh, you're not a monster...",
            "You are one of the first travelers I have seen in some time.",
            "I have built up a cache of items that I can sell you if you're interested..."
        ]
    },
    "Boss": {
        "Text": [
            "Ready yourself for combat, I will not yield easily!",
        ]
    }
}


if __name__ == "__main__":
    curses.wrapper(Game)
