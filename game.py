"""
The main module to run the Dungeon Crawl game.
"""

import curses
import glob
import random
import sys
import time

import dill

import player
import town
import utils
from character import Combat, Level, Resource, Stats
from classes import classes_dict
from races import races_dict


# objects
class Game:
    """
    Game object that contains all of the necessary details
    """

    def __init__(self, stdscr, debug_mode=False):
        self.stdscr = stdscr
        self.debug_mode = debug_mode
        self.load_files = glob.glob('save_files/*')
        self.races_dict = races_dict
        self.classes_dict = classes_dict
        self.player_char = None
        self.debug_mode = debug_mode
        self.random_combat = True
        self.time = time.time()
        self.bounties = {}
        curses.curs_set(0)  # Hide cursor
        self.main_menu()

    def main_menu(self):
        menu = utils.MainMenu(self)
        menu.erase()
        if self.debug_mode:
            confirm_str = "You are in debug mode. Do you want to turn off random encounters?"
            confirm = utils.ConfirmPopupMenu(self, confirm_str, box_height=8)
            if confirm.navigate_popup():
                self.random_combat = False
        menu_options = ['New Game', 'Settings', 'Exit']
        if self.load_files:
            menu_options.insert(1, "Load Game")
        menu.update_options(menu_options)
        while True:
            while True:
                selected_idx = menu.navigate_menu()
                menu.erase()
                if menu_options[selected_idx] == 'New Game':
                    self.player_char = self.new_game()
                elif menu_options[selected_idx] == 'Load Game':
                    self.player_char = self.load_game(menu)
                elif menu_options[selected_idx] == 'Settings':
                    """
                    Settings to include
                    - special text print speed
                    - difficulty level
                    - hardcore mode (perma-death)
                    - 
                    """
                    pass
                else:
                    sys.exit(0)  # Exit the game
                if self.player_char:
                    break
            self.run()
            self.update_loadfiles()
            if self.load_files and "Load Game" not in menu_options:
                menu_options.insert(1, "Load Game")
            menu.update_options(menu_options)

    def update_loadfiles(self):
        self.load_files = glob.glob('save_files/*')

    def run(self):
        self.update_bounties()
        while not self.player_char.quit:
            self.player_char.encumbered = self.player_char.current_weight() > self.player_char.max_weight()
            if time.time() - self.time > (900 * self.player_char.level.pro_level):
                self.update_bounties()
            if self.player_char.in_town():
                self.player_char.town_heal()
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
        if not self.debug_mode:
            texts_pad = utils.QuestPopupMenu(self, box_height=len(texts)+2, box_width=len(max(texts, key=len))+4)
            texts_pad.draw_popup(texts)
            self.stdscr.getch()

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
                if not self.debug_mode:
                    enternamebox.print_text_in_rectangle("Name cannot be empty.")
                    self.stdscr.getch()
                    enternamebox.clear_rectangle()
                else:
                    name = "Test"
                    break
            else:
                menu.erase()
                confirm_str = f"Are you sure you want to name your character {name}?"
                confirm = utils.ConfirmPopupMenu(self, confirm_str, box_height=7)
                if confirm.navigate_popup():
                    break
        menu.erase()

        created = f"Welcome {name}, the {race.name} {cls.name}.\nReport to the barracks for your orders."
        enternamebox.print_text_in_rectangle(created)
        self.stdscr.getch()
        enternamebox.clear_rectangle()

        # Define the player character
        import abilities
        import items
        location_x, location_y, location_z = (5, 10, 0)
        stats = tuple(map(lambda x, y: x + y, (race.strength, race.intel, race.wisdom, race.con, race.charisma, race.dex),
                        (cls.str_plus, cls.int_plus, cls.wis_plus, cls.con_plus, cls.cha_plus, cls.dex_plus)))
        hp = stats[3] * 2  # starting HP equal to constitution x 2
        mp = stats[1] * 2  # starting MP equal to intel x 2
        attack = race.base_attack + cls.att_plus
        defense = race.base_defense + cls.def_plus
        magic = race.base_magic + cls.magic_plus
        magic_def = race.base_magic_def + cls.magic_def_plus
        gold = stats[4] * 25  # starting gold equal to charisma x 25
        player_char = player.Player(location_x, location_y, location_z, level=Level(),
                            health=Resource(hp, hp), mana=Resource(mp, mp),
                            stats=Stats(stats[0], stats[1], stats[2], stats[3], stats[4], stats[5]),
                            combat=Combat(attack=attack, defense=defense, magic=magic, magic_def=magic_def),
                            gold=gold, resistance=race.resistance)
        player_char.name = name
        player_char.race = race
        player_char.cls = cls
        player_char.equipment = cls.equipment
        if "1" in abilities.spell_dict[cls.name]:
            spell_gain = abilities.spell_dict[cls.name]["1"]()
            player_char.spellbook['Spells'][spell_gain.name] = spell_gain
        player_char.storage["Health Potion"] = [items.HealthPotion() for _ in range(5)]  # care package
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
        utils.save_file_popup(self, load=True)
        with open(self.load_files[selected_idx], "rb") as save_file:
            player_dict = dill.load(save_file)
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
        if self.player_char.in_town() or "Shop" in str(room):
            return
        dmenu = utils.DungeonMenu(self)
        dmenu.draw_all()
        dmenu.refresh_all()
        while True:
            if self.player_char.in_town() or self.player_char.quit:
                return
            available_actions = room.available_actions(self.player_char)
            if self.player_char.state == "normal":
                room.enemy = None
                action_input = self.stdscr.getch()
                for action in available_actions:
                    available_hotkeys = [x['hotkey'] for x in available_actions]
                    try:
                        if chr(action_input).lower() == action['hotkey']:
                            action['method'](self.player_char, self)
                            if chr(action_input).lower() in available_hotkeys and \
                                ("Move" in action['name'] or "Open" in action['name'] or "stairs" in action['name']):
                                return
                    except TypeError:
                        pass
            else:
                flee = self.battle(room.enemy)
                if flee:
                    return
            dmenu.draw_all()
            dmenu.refresh_all()

    def battle(self, enemy, pause=True):
        """
        Function that controls combat
        TODO needs to be optimized
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
                        player_char.class_effects["Power Up"].active = True
                        player_char.class_effects["Power Up"].duration = 1
                    return player_char, enemy
            if enemy.invisible:
                if not player_char.sight:
                    return enemy, player_char
            p_chance = player_char.check_mod("speed", enemy=enemy) + \
                player_char.check_mod('luck', enemy=enemy, luck_factor=10)
            e_chance = enemy.check_mod("speed", enemy=player_char) + \
                enemy.check_mod('luck', enemy=player_char, luck_factor=10)
            total_chance = p_chance + e_chance
            chance_list = [p_chance / total_chance, e_chance / total_chance]
            attacker = random.choices([player_char, enemy], chance_list)[0]
            defender = player_char if attacker == enemy else enemy
            return attacker, defender

        battlebox = utils.TextBox(self)
        if pause:
            while True:
                key = self.stdscr.getch()
                if key == curses.KEY_ENTER or key in [10, 13]:
                    break
        flee = False
        first, second = initiative(self.player_char, enemy)
        other = None
        tile = self.player_char.world_dict[(self.player_char.location_x,
                                            self.player_char.location_y,
                                            self.player_char.location_z)]
        vision = self.player_char.sight and 'Boss' not in str(tile) and enemy.name != "Waitress"
        combat = True
        cmenu = utils.CombatMenu(self)
        popup = utils.CombatPopupMenu(self, "Test")
        available_actions = tile.available_actions(self.player_char)
        while combat:
            cmenu.draw_enemy(enemy, vision=vision)
            cmenu.draw_options(available_actions)
            if other:
                cmenu.draw_char(char=other)
            else:
                cmenu.draw_char()
            cmenu.refresh_all()

            # resolve status effects
            status_text = first.effects()
            if first == other:
                status_text += self.player_char.effects()
            if status_text:
                if "damage" in status_text:
                    # handles exploding shield for Crusader
                    try:
                        second.health.current -= int(status_text.split(" damage")[0].split(" ")[-1])
                    except ValueError:
                        pass
                battlebox.print_text_in_rectangle(status_text)
                self.stdscr.getch()
                battlebox.clear_rectangle()

            if any([not self.player_char.is_alive(),
                    not enemy.is_alive()]):
                break

            if not first.incapacitated():
                
                if first == self.player_char:
                    while True:
                        if first.magic_effects["Ice Block"].active:
                            combat_text = f"{first.name} is encased in ice and does nothing.\n"
                            valid_entry = True
                        elif first.status_effects["Berserk"].active:
                            wd_str, _, _ = first.weapon_damage(second)
                            combat_text = wd_str
                            valid_entry = True
                        elif first.class_effects["Jump"].active:
                            jump_name = [x for x in first.spellbook['Skills'] if "Jump" in x][0]
                            combat_text = first.spellbook['Skills'][jump_name].use(first, target=second)
                            first.class_effects["Jump"].active = False
                        else:
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
                            tile = self.player_char.world_dict[
                                (self.player_char.location_x, self.player_char.location_y, self.player_char.location_z)
                                ]
                            if action == 'Untransform':
                                combat_text += first.transform(back=True)
                                valid_entry = False
                            elif action == "Transform":
                                combat_text += first.transform()
                                valid_entry = False
                            elif action == "Pickup Weapon":
                                combat_text += f"{first.name} picks up their weapon.\n"
                                first.physical_effects["Disarm"].active = False
                                valid_entry = True
                            elif action == "Totem":  # TODO
                                valid_entry = True
                            else:
                                if action == 'Open':
                                    first.open_up(self)
                                    valid_entry = True
                                elif action == "Attack":
                                    special_str = ""
                                    if not random.randint(0, 9 - self.check_mod("luck", luck_factor=20)):
                                        special_str = self.special_attack(target=second)
                                    if not special_str:
                                        wd_str, _, _ = first.weapon_damage(second)
                                        combat_text += wd_str
                                    else:
                                        combat_text += special_str
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
                                                    first.spellbook['Skills'][entry].name == 'Smoke Screen' and \
                                                        'Boss' in str(tile),
                                                    first.spellbook['Skills'][entry].name == 'Lockpick',
                                                    first.spellbook['Skills'][entry].name == 'Shield Slam' and \
                                                        first.equipment['OffHand'].subtyp != 'Shield',
                                                    first.spellbook['Skills'][entry].name == 'Mortal Strike' and \
                                                        first.equipment['Weapon'].handed == 1,
                                                    first.spellbook['Skills'][entry].name == "Backstab" and \
                                                        not second.incapacitated(),
                                                    first.spellbook["Skills"][entry].weapon and \
                                                        first.physical_effects["Disarm"].active]):
                                                continue
                                            if entry == "Mana Shield" and first.magic_effects["Mana Shield"].active:
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
                                        elif skill.name == "Slot Machine":
                                            skill_str += skill.use(self, first, target=second)
                                        elif skill.name in ["Doublecast", "Triplecast"]:
                                            skill_str += skill.use(first, second, game=self)
                                        elif "Jump" in skill.name:
                                            first.class_effects["Jump"].active = True
                                            combat_text += f"{first.name} prepares to leap into the air.\n"
                                        else:
                                            skill_str += skill.use(first, target=second)
                                        combat_text += skill_str
                                        valid_entry = valid
                                elif action == "Summon":
                                    summon_names = list(self.player_char.summons)
                                    popup.update_options(summon_names, ["Summons"])
                                    skill_index = popup.navigate_popup()
                                    other = first.summons[summon_names[skill_index]]
                                    first = first.summons[summon_names[skill_index]]
                                    combat_text += f"{self.player_char.name} summons {other.name} to aid them in combat.\n"
                                    valid_entry = True
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
                elif first == enemy:
                    action = first.options(second, action_list=available_actions)
                    _, combat, flee = first.combat_turn(self, second, action, combat)
                else:
                    cmenu.current_option = 0
                    available_actions = first.options()
                    cmenu.draw_enemy(enemy, vision=vision)
                    cmenu.draw_options(available_actions)
                    cmenu.draw_char(char=first)
                    cmenu.refresh_all()
                    action_idx = cmenu.navigate_menu()
                    action = available_actions[action_idx]
                    combat_text = ""
                    valid_entry = False
                    if first.magic_effects["Ice Block"].active:
                        combat_text += f"{first.name} is encased in ice and does nothing.\n"
                        valid_entry = True
                    if action == "Recall":
                        combat_text += f"{self.player_char.name} recalls {first.name}.\n"
                        other = None
                        first = self.player_char
                        valid_entry = True
                    elif action == "Attack":
                        special_str = ""
                        if not random.randint(0, 9 - self.check_mod("luck", luck_factor=20)):
                            special_str = self.special_attack(target=second)
                        if not special_str:
                            wd_str, _, _ = first.weapon_damage(second)
                            combat_text += wd_str
                        else:
                            combat_text += special_str
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
                                        first.spellbook["Skills"][entry].weapon and \
                                            first.physical_effects["Disarm"].active]):
                                    continue
                                if entry == "Mana Shield" and first.magic_effects["Mana Shield"].active:
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
                            elif skill.name == "Slot Machine":
                                skill_str += skill.use(self, first, target=second)
                            elif skill.name in ["Doublecast", "Triplecast"]:
                                skill_str += skill.use(first, second, game=self)
                            else:
                                skill_str += skill.use(first, target=second)
                            combat_text += skill_str
                            valid_entry = valid

                    if combat_text:
                        combatbox = utils.TextBox(self)
                        combatbox.print_text_in_rectangle(combat_text)
                        self.stdscr.getch()
                        combatbox.clear_rectangle()
            else:
                if first.incapacitated():
                    combat_text = f"{first.name} is incapacitated."
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
                if second == other:
                    battlebox.print_text_in_rectangle(f"{other.name} is killed.")
                    self.stdscr.getch()
                    battlebox.clear_rectangle()
                    second = self.player_char
                    other = None
                elif 'Resurrection' in second.spellbook['Spells'] and \
                        abs(second.health.current) <= second.mana.current:
                    res_text = second.spellbook['Spells']['Resurrection'].cast(second)
                    battlebox.print_text_in_rectangle(res_text)
                    self.stdscr.getch()
                    battlebox.clear_rectangle()
                else:
                    if second.name == "Behemoth":
                        final_text = second.special_effects(first)
                        battlebox.print_text_in_rectangle(final_text)
                        self.stdscr.getch()
                        battlebox.clear_rectangle()
                    combat = False

            if not combat:
                break

            if not first.is_alive() or not self.player_char.is_alive():
                break

            if first == self.player_char:
                first = enemy
                second = self.player_char
            elif first == enemy:
                if second == other:
                    first = other
                    second = enemy
                else:
                    first = self.player_char
                    second = enemy
            else:
                first = enemy
                second = other

        self.player_char.end_combat(self, enemy, tile, flee=flee, summon=other)
        if self.player_char.is_alive() and "Boss" in str(tile):
            tile.defeated = True
        return flee

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
        pad.clear_popup()
        

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
    "Busboy": {
        "Text": [
            "The door to the tavern swings shut and you can no longer hear the waitress fleeing",
            "Just then you hear the bartender from behind the bar. 'Hey, where are you going?!'",
            "'Damn, now whose gonna get this food and drink out to my patrons?!'",
            "You shrug your shoulders, not wanting to get caught up in all of the chaos.",
            "'BUSBOY! Get out here, you've gotta take over these tables.'"
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
            "What did he mean by he couldn't resist his will? Something doesn't seem right...",
            "Keep you wits about you, there's evil afoot.", 
            "Since there is no one left to claim his things, you can have what's left. Put them to good use."
        ]
    },
    "Power Up": {
        "Text" : [
            "You enter into the back of the blacksmith shop and see what looks like a metal coffin glowing green.",
            "'Climb on in, we have some work to do.' You enter the machine against your better judgment.",
            "Griswold stands behind a panel and after a few button presses, you see the green glow around you grow.",
            "You are suddenly overwhelmed by an searing pain. You stifle a scream but it is becoming unbearable.",
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
            "You enter a massive room. A booming voice greets you.",
            "'Hello again. You have done well to reach me, many have tried and failed.'",
            "The voice talks to you as if you should recognize them...it must the be hooded figure from the tavern.",
            "'It would seem our meeting was inevitable but it still doesn't lessen the sorrow I feel,",
            "knowing that one of us will not leave here alive.'",
            "You know this is what you were working toward but the threat of death has left you wavering.",
            "'I give you but one chance to reconsider, after which I will not go easy on you.'"
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
    "Ultimate Armor":{
        "Text": [
            "Hello, my name is Chisolm, Griswold's brother.",
            "I tried to defeat the ultimate evil but could not even damage it.",
            "I barely escaped, camping here to lick my wounds.",
            "I decided I would instead use my blacksmith skills to help those who look to do what I could not.",
            "Choose the type of armor you would prefer and I will make you the finest set you could imagine."
        ]
    },
    "Boulder": {
        "Text": [
            "Before you sits a decent sized boulder, although you are not sure what it is doing in the dungeon.",
            "You look closer and notice the hilt of a sword sticking out from behind it.",
            "You grab the sword and try to dislodge it but it seems pretty stuck.",
            "With one final yank, the sword comes free...or part of it at least.",
            "You gain the not-so-legendary Excaliper...whomp whomp..."
        ]
    },
    "Nimue": {
        "Text": [
            "Before your eyes appears the most beautiful creature you have ever seen.",
            "'Greeting, my name is Nimue. I am the Maid of this spring.'",
            "You notice a faint aura resonating from your bag, as if you carry something of value to her.",
            "'Finally, a worthy champion...you have brought me the sword of legend. May I see it?'",
            "Sword of legend?...you are uncertain what she could be referring to...perhaps the broken sword?",
            "You take out what's left of Excaliper and hand it over. Her joyous expression quickly changes.",
            "'Oh pity, this is not but a cheap knock-off...and it's broken...curses.'",
            "'Whoever forged this weapon was not much of a blacksmith, yet possessed the magical acumen to trick me.'",
            "'I'd bet anything Merzhin was involved. Ever since I spurred his advances, he has been a very naughty boy.'",
            "The remains of Excaliper vanish from her hands. 'Oh well, you can still be of use to me.'",
            "Her words are somewhat unsettling as you ponder what she means. You thoughts are quickly disturbed.",
            "'I see you seek to end the blight of this land, perhaps we can be of assistance to each other.'",
            "'Merzhin is a powerful wizard and he has become a thorn in my side. I would like you to deal with him.'",
            "'His domain is not of this plane, residing in the Realm of Cambion. Luckily I can teleport you there.'",
            "You are uncertain if you want to get involved. 'I can make it worth your time. Think on it for a bit.'",
            "'If you wish to summon me, just drink from the spring and I will appear. Until then...'. She disappears.",
        ]
    },
    "Minotaur": {
        "Text": [
            "As you enter the corridor, you are met with a horrific scene.",
            "The carnage is almost as unbelievable as the monster you are confronted with.",
            "You first notice the glint of a battle-worn axe, stained with the blood of countless foes.",
            "The beast's fiery eyes lock onto you, letting out a deafening roar.",
            "There is no mistaking the towering Minotaur, known to many as 'The Butcher'.",
            "Chains and bone fragments litter the floor—a grim testament to those who dared to challenge him.",
            "The Butcher snarls, 'You are next, little one!'",
        ]
    },
    "Barghest": {
        "Text": [
            "The sacred chamber hums with an ominous energy as you step forward, the air growing cold with each breath.",
            "A deep growl reverberates through the hall, and from the shadows emerges a large wolf-like beast.",
            "This must be the Barghest, a tricky shapeshifter that is also the guardian of the first Holy Relic.",
            "Its spectral eyes burn with a ghostly light, and its jagged fangs gleam with menace.",
            "Its black fur bristles like shadowy flames and its claws carve furrows into the stone floor as it prowls.",
            "With a chilling snarl, it lunges, its voice echoing, “None shall desecrate the relics!”"
        ]
    },
    "Pseudodragon": {
        "Text": [
            "The dungeon narrows as you round the corner and you are met by a faint, red light.",
            "A warmth meets your body and the sweet smell of jasmine permeates around you.",
            "'Oh please, enter my chamber without permission.' You see nothing but a lavish lair and a crackling fireplace.",
            "You step forward in defiance, spotting the creature perched upon the hearth, no larger than a house cat.",
            "'So, you thought you would make a name for yourself by slaying a mighty dragon? Sorry to disappoint...'",
            "It is true, you did expect something more. However, your experience tells you not to take it lightly.",
            "'Oh, still a bit frisky, are we? Well, I should warn you that short doesn't always mean sweet.'",
            "'But that is enough foreplay, let us proceed to the main course!' The beast takes flight and attacks!"
        ]
    },
    "Nightmare": {
        "Text": [
            "You travel a great hall, expecting something monstrous to attack. What you find is much worse.",
            "The hair on the back of your neck stands at attention and suddenly feel fear grab ahold of you.",
            "Your will is steadfast but you know that will only last for so long as the sight you feared emerges.",
            "A massive stallion with a mane and tail of flames, the rest as black as the deepest depths.",
            "It says no words but has no need, for silence is much more frightening.",
            "You catch a glimpse of a relic perched atop a glowing pedestal but the Nightmare stands in your way.",
            "With a flare of its nostrils, the beast charges right at you, filled with malice aforethought."
        ]
    },
    "Cockatrice": {
        "Text": [
            "As you step into the dimly lit cavern, the air grows thick and heavy.",
            "A low, menacing hiss reverberates off the stone walls, sending shivers down your spine.",
            "A monstrosity emerges from the shadows, its leathery wings unfurling, and its beady eyes locked onto you.",
            "With every movement, its claws scrape against the floor, and its serpentine tail lashes out.",
            "The beast lets out a bone-chilling screech, its petrifying aura threatening to halt your advance."
        ]
    },
    "Wendigo": {
        "Text": [
            "The stagnant isolation of the dungeon is suddenly disturbed, replaced by a bone-chilling cold.",
            "The icy winds howl as you approach the sacred grounds of the third relic.",
            "Emerging from the darkness, a beast towers above, its gaunt frame shrouded in frost and shadows.",
            "Its hollow eyes burn with a ravenous hunger, and its clawed hands twitch with restless energy.",
            "The air grows colder, biting at your skin, as the creature lets out an unearthly wail.",
            "The guardian of the relic stands ready, an embodiment of hunger and despair, the Wendigo."
        ]
    },
    "Golem": {
        "Text": [
            "The ground trembles as a towering figure of stone and metal lumbers into view.",
            "Its massive frame glints in the dim light, its eyes dead and lifeless.",
            "You stand still waiting for something to happen and notice a low hum build as the construct comes online.",
            "The golem's glowing eyes fixate on you, while the hum of ancient magic reverberates through the air.",
            "Cracks in its surface reveal faint pulsations of energy, hinting at the immense power contained within.",
            "The guardian moves with deliberate purpose, its heavy footsteps echoing like a drumbeat of inevitability.",
            "Another trial stands before you, as implacable as the earth itself."
        ]
    },
    "Iron Golem": {
        "Text": [
            "The Iron Golem stands motionless at the threshold, its massive form forged from enchanted steel.",
            "Etched with ancient runes of power, the massive statue is a formidable sight.",
            "Sparks crackle from its joints as it animates, each movement deliberate and heavy with menace.",
            "Its glowing core pulses like a molten heart, radiating an oppressive heat that fills the chamber.",
            "The ground shudders under its iron steps, and its piercing gaze locks onto you, assessing your worth.",
            "The path forward lies in proving yourself against this unyielding sentinel of the dungeon depths."
        ]
    },
    "Jester": {
        "Text": [
            "You pass through the open door into a small chamber and you are met with a horrifying sight.",
            "A disfigured man is shackled against the wall, upside down and covered with blood.",
            "The man struggles to breathe but manages to muster a weak 'Help me!'.",
            "The Jester steps into view with an unsettling gait, his face painted in a macabre grin.",
            "His ragged outfit jingles with the sound of bells, each step punctuated by a spine-chilling laugh.",
            "His eyes glint with wild, unrestrained madness as he deftly twirls a knife between his fingers.",
            "Without looking away from you, he steps towards the chained man and thrusts the knife deep into his chest.",
            "You hear nothing but a meager gasp, his body slumping down. 'We were playing a game. He lost...hehe.'",
            "The Jester turns and walks towards a table in the corner of the room, covered with the tools of his trade.",
            "'Care to play?' he asks, his voice dripping with mockery.",
            "'The stakes? Oh, just your sanity—or maybe your life. Let's see where the chips fall!'"
        ]
    },
    "Domingo": {
        "Text": [
            "Your search for another one of the mystical relics leads you down a dark flight of stairs.",
            "As you descend into the dungeon, you notice the air grow heavy, and a gurgling sound echoing from beyond.",
            "A cartoonish creature emerges, its writhing tentacles glowing faintly with an unearthly, pulsating light.",
            "Its bulbous body quivers, and its eyes...far too many eyes...unnervingly fixate on you.",
            "'You dare face the perfection of creation?' a voice reverberates in your mind. How?!",
            "The creature's tentacles twitch, ready to unleash its magical fury. 'Prepare to witness true power!'"
        ]
    },
    "Red Dragon": {
        "Text": [
            "After several minutes exploring an empty corridor, you exit into a massive sanctum riddled with fissures.",
            "The cavern trembles as the ground beneath you grows unbearably hot.",
            "A deafening roar erupts from the shadows, and the Red Dragon steps forward.",
            "Its scales gleam like molten metal and its eyes burn with a primal fury.",
            "'You've come this far,' it growls, its voice reverberating like thunder.",
            "'But you will go no further. Prove your worth... or be reduced to ashes where you stand.'",
            "Its wings spread wide, blocking your path as your next trial begins."
        ]
    },
    "Cerberus": {
        "Text": [
            "You step out from the hidden passage and expect a moment to gather yourself. You were mistaken.",
            "The ground quakes, and an ominous growl fills the air as the three-headed Cerberus emerges before you.",
            "Each head snarls and gnashes in unison, its glowing eyes locking onto you with predatory intent.",
            "'You dare to disturb the sanctity of the final relic?' the voices echo, a guttural chorus of menace.",
            "'No one passes. No one escapes.' The beast's claws dig into the ground, its teeth gleaming in the faint light.",
            "This is your pentultimate test-face the guardian or perish in its jaws."
        ]
    },
    "Devil": {
        "Text": [
            "You feel your body lifted in the air, riding an invisible path toward the far side of the sanctum.",
            "The ride comes to an immediate end, leaving you reeling from the abrupt stop.",
            "The bones of those who have faced the prime evil surround you. Will you join them?",
            "Your thoughts are interrupted by the shaking of the ground as an incomprehesible sight approaches you.",
            "Before you stands the Devil—a towering figure of malice, wreathed in flame and shadow.",
            "Its horns scrape the heavens, and its crimson eyes burn with the fury of eons.",
            "'You may not recognize me in my current form. Let me refresh your memory.'",
            "From the shadows appears the hooded figure from the town tavern.",
            "'You probably expected my appearance but the surprises are just beginning.'",
            "You were certain of their duplicity but your suspicion was only partially correct.",
            "The Devil begins to transform, replacing the monstrosity with a familiar sight-the busboy!",
            "'Not who you expected? I guess you weren't actually paying attention then.'",
            "Your mind races, combing over everything that has happened, certain you have missed some clue.",
            "'I have been lurking, with my trusted acolyte by my side. I knew eventually a worthy opponent would appear.'",
            "A fury rises within you at the thought of all the lives ruined. You clench as he continues to speak.",
            "'I stayed away at first but your success piqued my curiosity. You have earned a mighty reward.'",
            "Reward?! This must be a joke, surely there is nothing left but a battle to the death.",
            "'Join my army and I will make you one of my chosen. You will lead droves of my minions into battle.'",
            "You cry out for silence, insulted by the implication. You would never join him!",
            "'I thought it was a fair offer but so be it. Instead your soul will be used for my amusement.'",
            "The Devil transforms back into his real form and a battle for the ages commences."
        ]
    },
    "Dilong": {
        "Text": [
            "The ground feels different here, almost like sand.",
            "Suddenly your whole body starts to shake and the ground starts to open underneath you.",
            "You stumble back just in time and out of the floor a massive earthworm-like creature appears.",
            "'Who dares disturb my home! Give me one reason I shouldn't swallow you right up?'",
            "The game piece you found begins to glows and levitates up into the air.",
            "'Oh look, that will complete my set. Maybe instead of violence, we could help each other out.'",
            "'Give it to me and I will lend you my services when needed.'",
            "You have gained the summon Dilong."
        ]
    },
    "Agloolik": {
        "Text": [
            "The wails of anguish have settled and the Wendigo lays at your feet.",
            "After a long fight, you take a moment to catch your breath and feel an icy chill creep over you.",
            "A mist has fallen upon the room with an icy film caked over every surface, including you.",
            "A massive shiver runs through your bones and you buckle at your knees in pain.",
            "'I expected more from the one who defeated this beast. Hahaha...pathetic.'",
            "You regain your composure and return to your feet, defiant in the face of the unseen.",
            "An entity forms in front of you with a crooked smile, 'Maybe you are worth something. We shall see...'",
            "You have gained the summon Agloolik."
        ]
    },
    "Cacus": {
        "Text": [
            "The searing pain continues as you traverse the blazing hallway, unsure if the reward is worth the pain.",
            "You encounter what appears to be a dead end but notice a pool of lava, bubbling and spitting molten rock.",
            "This must be the place...perhaps there is a way to awaken what dwells here.",
            "You cast the blacksmith's hammer into the lava...and nothing...for a time.",
            "Suddenly a large figure emerges, a man over nine feet tall, engulfed in fire and brimstone.",
            "'I have slumbered for too long. What is this that returns me to the realm of the living?'",
            "'A summoner? Of course, I should have known...the downfalls of my curse. Shall we leave?'"
            "You have gained the summon Cacus."
        ]
    },
    "Fuath1": {
        "Text": [
            "You drank water from the underground spring...nothing seems to have changed...at first.",
            "Suddenly an eddy forms and out from the vortex emerges a blond-haired maiden in a green silk dress.",
            "A haunting voice echoes around you, even though her mouth does not move.",
            "You start to feel a strange calm, as if you are being lulled to sleep. Is this some kind of trick?",
            "Your question is immediately answered, when the figure changes into something out of the horrors.",
            "An ugly creature, with giant teeth and webbed hands and feet, let's out a shriek and falls to all fours.",
            "As if by some godly power, the creature crawls along the top of the water, heading right toward you.",
            "You are overcome with an almost mystical level of fear, frozen in place even against your will.",
            "Giant claws reach out for you, no doubt to pull you under. Your resolve finally returns.",
            "You prepare for combat, sure of a fight to ensue."
        ]
    },
    "Fuath2": {
        "Text": [
            "The Fuath relents slumping to the ground. The creature returns to its original form.",
            "After a moment, you hear a raspy voice coming from inside your head.",
            "'It's been some time since anyone could hold their own against me. Many have tried but none have succeeded.'",
            "Exhaustion is replaced by an expression of hatred. 'I will not submit to your will!'",
            "The Fuath tries to slip back into the waters but is held back by an invisible force.",
            "'NO, I WON'T GO WITH THEM!!!', as if pleading with the universe. The struggle ends quickly.",
            "'CURSES!...I must fulfill the covenant and aid you in your quest...'",
            "You have gained the summon Fuath."
        ]
    },
    "Izulu": {
        "Text": [
            "You follow the priest down a dark alley, passing several homeless people before arriving at a tent.",
            "'Go inside and tell her I sent you.' The priest turns around and heads back toward the church.",
            "You enter the tent and are instantly hit by a strange odor, not bad but also not good.",
            "A figure emerges from behind a bookshelf. 'Come in, I've been expecting you.'",
            "A masked figure stands before you, minimally clothed in rags and adorned in shells and bones.",
            "'The priest told me you helped the church out immensely. I owe him my life.'",
            "'Perhaps I can help you. You possess the power to summon creatures, a gift not many have mastered.'",
            "From a back room, you hear a bird shriek, followed by a bright flash and the crack of thunder.",
            "'Right on cue, come out Izulu.' To your surprise, a young man emerges from the darkness.",
            "'This is Izulu, my familiar. Don't let this form fool you, my pet is a powerful force.'",
            "At the snap of a finger, the young man transforms into a giant bird. Electricity crackles around him.",
            "'I grant you permission to summon him and do your bidding, until the day the evil is purged.'",
            "You have gained the summon Izulu."
        ]
    },
    "Hala": {
        "Text": [
            "You have gained the summon Hala."
        ]
    },
    "Grigori": {
        "Text": [
            "You have gained the summon Grigori."
        ]
    },
    "Bardi": {
        "Text": [
            "You have gained the summon Bardi."
        ]
    },
    "Kobalos": {
        "Text": [
            "You have gained the summon Kobalos."
        ]
    },
    "Zahhak": {
        "Text": [
            "You have gained the summon Zahhak."
        ]
    },
    "Rookie": {
        "Text": [
            "You come to the end of a long corridor and realize the dungeon smells just a little worse than normal.",
            "You spot a mass against the wall and quickly identify the insignia of the town guard.",
            "The body is partially eaten but you believe this must be the recruit the Sergeant told you about.",
            "You retrieve the body that even though is missing parts, still weighs quite a bit.",
            "As you turn to leave you come face to face with an enemy and it attacks!"
        ]
    },
    "Remedy": {
        "Text": [
            "You follow the priest down a dark alley, passing several homeless people before arriving at a tent.",
            "'Go inside and tell her I sent you.' The priest turns around and heads back toward the church.",
            "You enter the tent and are instantly hit by a strange odor, not bad but also not good.",
            "A figure emerges from behind a bookshelf. 'Come in, I've been expecting you.'",
            "A masked figure stands before you, minimally clothed in rags and adorned in shells and bones.",
            "'The priest told me you helped the church out immensely. I owe him my life.'",
            "'As you likely have guessed, I am a shaman. Some would call me a witch doctor...'",
            "'I believe I can help you in your quest to purge this land of evil. Wait here...'",
            "The shaman exits the room through a flap in the back. You wait for some time...",
            "Suddenly a flash of light and a series of bangs exit the back room, followed by a trail of smoke.",
            "The shaman reemerges. 'Here, take these potions. They will cure all status effects.'",
            "'Good luck. I will do what I can from the shadows to help you.'"
        ]
    }
}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "debug":
            curses.wrapper(Game, **{'debug_mode': True})
    curses.wrapper(Game)
