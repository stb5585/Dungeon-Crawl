###########################################
""" Town manager (Curses UI version) """

import random
import time
from textwrap import wrap

from src.core import classes, items
from src.core.town import quest_dict, PATRON_DIALOGUES, RESPONSE_MAP
from . import menus


# Functions
def upgrade(game):
    """
    function handles special attack upgrade for Find Chisolm quest

    
    """
    message = ""
    return message


def ultimate(game):
    texts = [
        "Oh my...can it possibly be?...the legendary ore...Unobtainium?",
        "I can\'t believe you have found it!",
        "It has been a lifelong dream of mine to forge a weapon from the mythical metal."
    ]
    ultimate_pad = menus.QuestPopupMenu(game, box_height=len(texts)+2, box_width=len(max(texts, key=len))+4)
    ultimate_pad.draw_popup(texts)
    make_options = []
    weapon_list = []
    i = 0
    for typ, weapon in items.ultimate_weapons.items():
        if typ == 'Staff':
            if 'Archbishop' == game.player_char.cls.name:
                weapon = weapon[0]
            else:
                weapon = weapon[1]
        if game.player_char.cls.equip_check(weapon, "Weapon"):
            make_options.append(typ)
            weapon_list.append(weapon)
            i += 1
    make_options.append('Not Yet')
    make_message = "What type of weapon would you like me to make?"
    menu = menus.SelectionPopupMenu(game=game,
                                    header_message=make_message,
                                    stat_options=make_options,
                                    box_height=len(make_options)+5,
                                    rewards=weapon_list,
                                    confirm=False)
    ultimatebox = menus.TextBox(game)
    while True:
        make_idx = menu.navigate_popup()
        if make_options[make_idx] == 'Not Yet':
            ultimatebox.print_text_in_rectangle(
                "I am sorry to hear that...please come back if you change your mind.")
            game.stdscr.getch()
            ultimatebox.clear_rectangle()
            return
        else:
            weapon = weapon_list[make_idx]()
            ultimatebox.print_text_in_rectangle(
                "Give me a moment and I will make you an ultimate weapon...")
            time.sleep(5)
            ultimatebox.clear_rectangle()
            ultimatebox.print_text_in_rectangle(
                f"I present to you, {game.player_char.name}, the mighty {weapon.name}!")
            game.stdscr.getch()
            ultimatebox.clear_rectangle()
            game.player_char.modify_inventory(weapon)
            del game.player_char.special_inventory['Unobtainium']
            break


def turn_in_quest(game, quest, typ):
    quest_desc = wrap(game.player_char.quest_dict[typ][quest]['End Text'], 50, break_on_hyphens=False)
    quest_pad = menus.QuestPopupMenu(game, box_height=len(quest_desc)+2, box_width=len(max(quest_desc, key=len))+4)
    quest_pad.draw_popup(quest_desc)
    quest_pad.clear_popup()
    game.player_char.quest_dict[typ][quest]['Turned In'] = True
    reward = game.player_char.quest_dict[typ][quest]['Reward']
    if len(reward) == 1:
        reward = reward[0] if isinstance(reward[0], str) else reward[0]()
    elif "Izulu" in reward:
        reward = reward[0] if "Summoner" in game.player_char.cls.name else reward[1]()
        if "Summoner" not in game.player_char.cls.name:
            game.special_event("Remedy")
    else:
        reward_options = [x().name for x in reward]
        popup = menus.SelectionPopupMenu(
            game, f"Choose your reward{' ':10}(press i for info)",
            reward_options, box_height=6+len(reward), rewards=reward, confirm=True)
        reward_idx = popup.navigate_popup()
        reward = reward[reward_idx]()
    exp = game.player_char.quest_dict[typ][quest]['Experience'] * game.player_char.level.pro_level
    if reward == 'Gold':
        game.player_char.gold += game.player_char.quest_dict[typ][quest]['Reward Number']
        reward_message = f"You received {game.player_char.quest_dict[typ][quest]['Reward Number']} gold and {exp} experience.\n"
    elif reward == 'Upgrade':
        reward_message = upgrade(game)
    elif reward == "Power Up":
        reward_message = game.player_char.special_power(game)
        reward_message += f"You received {exp} experience.\n"
    elif reward == 'Warp Point':
        game.player_char.warp_point = True
        reward_message = f"You received {exp} experience and gain access to the Warp Point.\n"
    elif reward == "Izulu":
        game.special_event("Izulu")
        from ..core.companions import Izulu
        summon = Izulu()
        summon.initialize_stats(game.player_char)
        game.player_char.summons[summon.name] = summon
        reward_message = f"You received {exp} experience and have gained the summon Izulu.\n"
    else:
        num = game.player_char.quest_dict[typ][quest]['Reward Number']
        game.player_char.modify_inventory(reward, num=num)
        if num == 1:
            reward_message = f"You received {reward.name} and {exp} experience.\n"
        else:
            reward_message = f"You received {reward.name} x{num} and {exp} experience.\n"
    game.player_char.level.exp += exp
    if not game.player_char.max_level():
        game.player_char.level.exp_to_gain -= exp
    turninbox = menus.TextBox(game)
    turninbox.print_text_in_rectangle(reward_message)
    game.stdscr.getch()
    turninbox.clear_rectangle()
    if game.player_char.quest_dict[typ][quest]['Type'] == 'Collect':
        item = game.player_char.quest_dict[typ][quest]['What']
        del game.player_char.special_inventory[item().name]
    if not game.player_char.max_level():
        while game.player_char.level.exp_to_gain <= 0:
            textbox = menus.TextBox(game)
            stat_menu = menus.SelectionPopupMenu(game, 
                                                 "Pick the stat you would like to increase.",
                                                 [f'Strength - {game.player_char.stats.strength}',
                                                  f'Intelligence - {game.player_char.stats.intel}',
                                                  f'Wisdom - {game.player_char.stats.wisdom}',
                                                  f'Constitution - {game.player_char.stats.con}',
                                                  f'Charisma - {game.player_char.stats.charisma}',
                                                  f'Dexterity - {game.player_char.stats.dex}'],
                                                 box_height=12, confirm=False)
            game.player_char.level_up(game, textbox=textbox, menu=stat_menu)
            if game.player_char.level.exp_to_gain == "MAX":
                break
    if game.debug_mode and quest == "Debug":
        del game.player_char.quest_dict[typ][quest]
    if quest == "A Bad Dream":
        game.special_event("Busboy")
        if "Where's the Beef?" in game.player_char.quest_dict["Side"]:
            if not game.player_char.quest_dict["Side"]["Where's the Beef?"]["Turned In"]:
                turninbox.print_text_in_rectangle(("I know the waitress asked you to get her some meat for her wedding.\n"
                                                   "She obviously doesn't need them anymore, so I can take them if you get them.\n"))
                game.stdscr.getch()
                turninbox.clear_rectangle()
                game.player_char.quest_dict["Side"]["Where's the Beef?"]["Who"] = "Busboy"
                end_text = "Thanks, this will help feed a lot of people. Here's something for your time."
                game.player_char.quest_dict["Side"]["Where's the Beef?"]["End Text"] = end_text
                help_text = "You can get meat from pretty much any animal. Not really a time to be picky..."
                game.player_char.quest_dict["Side"]["Where's the Beef?"]["Help Text"] = help_text
                


def accept_quest(game, quest, typ):
    """
    Quest givers and information; additional quests to be added and rewards need to be optimized TODO
    - Tavern -
    Barkeep
      Main: Level 10, defeat Minotaur, rewards Old Key and 200 exp
            Level 50, defeat Golem, rewards Diamond Amulet or Platinum Pendant and 200000 exp
      Side: Level 1, collect 6 Rat Tails, rewards 600 gold and 100 exp
    Waitress
      Main: Level 35, defeat Nightmare, rewards 2 Old Keys and 4500 exp
      Side: Level 5, collect 12 Mystery Meat, rewards Super Health Potion and 150 exp
    Soldier
      Main: Level 55, defeat Jester, rewards Evasion ring and 300000 exp
      Side: Level 25, collect 10 Scrap Metal, rewards a stat potion of the player's choice and 750 exp
    Drunkard
      Main: Level 35, defeat Cockatrice, rewards Gorgon Pendant and 5000 exp
      Side: Level 18, collect 8 Snake Skins, rewards 5 antidotes and 400 exp
    Hooded Figure
      Main: Level 30, defeat Pseudodragon, reward Megalixir and 3000 exp
            Level 60, defeat Red Dragon, reward Class Ring and 500000 exp
      Side:

    - Shops -
    Griswold
      Main:
      Side: Level 15, collect 8 Leathers, rewards 2500 gold and 250 exp
            Level 45, collect 1 Power Core, rewards Power Up and
            Level 60, locate Chisolm, rewards item upgrade and 400000 exp
    Alchemist
      Main:
      Side: Level 20, collect 12 Feathers, rewards 4000 gold and 500 exp
    Jeweler
      Main:
      Side: Level 55, collect 6 Elemental Motes, rewards Elemental Amulet and 120000 exp
    Priest
      Main: Level 40, defeat Wendigo, rewards Aard of Being and 6000 exp
      Side:

    - Barracks -
    Sergeant
      Main: Level 1, locate Relics, rewards Medusa Shield, Magus, or Aard of Being and 1000000 exp
            Level 20, defeat Barghest, rewards Power Ring and 500 exp
      Side: Level 3, locate Timmy, rewards 5 Health Potions and 150 exp
    """

    quest_key = list(quest)[0]
    who = quest[quest_key]['Who']
    if who == "Drunkard" and game.player_char.player_level() >= 65:
        RESPONSE_MAP["Drunkard"] = [
            "I knew I could count on you!",
            "I understand your hesitation but I hope you reconsider."
        ]
    quest_desc = wrap(quest[quest_key]['Start Text'], 50, break_on_hyphens=False)
    menu = menus.QuestPopupMenu(game, box_height=len(quest_desc)+2, box_width=len(max(quest_desc, key=len))+4)
    accepted = False
    acceptquestbox = menus.TextBox(game)
    menu.draw_popup(quest_desc)
    confirm_str = "Do you accept this quest?"
    confirm = menus.ConfirmPopupMenu(game, confirm_str, box_height=6)
    if confirm.navigate_popup():
        player_char = game.player_char
        player_char.quest_dict[typ][quest_key] = quest[quest_key].copy()
        message = RESPONSE_MAP[who][0] + "\n"
        if who == "Sergeant" and quest_key == "The Holy Relics":
            message += "Make sure to grab the health potions out of your storage locker if you haven't already.\n"
        if quest_key == "Naivete":
            player_char.modify_inventory(items.EmptyVial(), rare=True)
        acceptquestbox.print_text_in_rectangle(message)
        game.stdscr.getch()
        acceptquestbox.clear_rectangle()
        if quest[quest_key]['Type'] == 'Defeat':
            kill_list = [name for typ_dict in player_char.kill_dict.values() for name in typ_dict]
            if quest[quest_key]["What"] in kill_list:
                player_char.quest_dict[typ][quest_key]['Completed'] = True
        accepted = True
    else:
        acceptquestbox.print_text_in_rectangle(RESPONSE_MAP[who][1])
        game.stdscr.getch()
        acceptquestbox.clear_rectangle()
    confirm.clear_popup()
    menu.clear_popup()
    return accepted


def check_quests(game, quest_giver):

    player_mains = list(game.player_char.quest_dict['Main'])
    player_sides = list(game.player_char.quest_dict['Side'])
    mains = quest_dict[quest_giver]['Main']
    sides = quest_dict[quest_giver]['Side']
    main_quests = [mains[x] for x in mains if game.player_char.player_level() >= int(x)]
    side_quests = [sides[x] for x in sides if game.player_char.player_level() >= int(x)]
    quest = False
    responses = [["I have no new quests for you at this time."]]
    if len(main_quests) > 0:
        for main_quest in main_quests:
            key = list(main_quest)[0]
            if key in player_mains:
                # Ensure collection quests like Relics reflect current progress even if accepted late
                try:
                    q = game.player_char.quest_dict['Main'][key]
                    if q.get('Type') == 'Collect' and q.get('What') == 'Relics' and not q.get('Completed'):
                        if game.player_char.has_relics():
                            q['Completed'] = True
                except Exception:
                    pass
                if game.player_char.quest_dict['Main'][key]['Completed'] and \
                        not game.player_char.quest_dict['Main'][key]['Turned In']:
                    turn_in_quest(game, key, "Main")
                    quest = True
                if not game.player_char.quest_dict['Main'][key]['Turned In']:
                    responses.append([game.player_char.quest_dict['Main'][key]['Help Text']])
            else:
                quest = accept_quest(game, main_quest, "Main")
            if quest:
                return quest, responses
    if len(side_quests) > 0:
        for side_quest in side_quests:
            key = list(side_quest)[0]
            # Skip Debug quest entirely (never show in production)
            if key == "Debug":
                continue
            if key in player_sides:
                if game.player_char.quest_dict['Side'][key]['Completed'] and \
                        not game.player_char.quest_dict['Side'][key]['Turned In']:
                    turn_in_quest(game, key, "Side")
                    quest = True
                if not game.player_char.quest_dict['Side'][key]['Turned In']:
                    responses.append([game.player_char.quest_dict['Side'][key]['Help Text']])
            else:
                if key == "Pandora's Box" and "Ultima" not in game.player_char.spellbook["Spells"]:
                    continue
                quest = accept_quest(game, side_quest, "Side")
            if quest:
                return quest, responses
    return quest, responses


def tavern_patrons(game):
    """
    Various patrons/employees that frequent the tavern
    3 possible conversations: Talk (tip or hint), Main Quest (directly related to game completion), or Side Quest
    Barkeep: level 1
    Waitress: level 1
    Drunkard: level 8
    Soldier: level 10
    Hooded Figure: level 25
    """

    def patron_list(game):
        patron_options = ["Barkeep"]
        if 'A Bad Dream' in game.player_char.quest_dict['Main']:
            if not game.player_char.quest_dict['Main']['A Bad Dream']['Turned In']:
                patron_options.append("Waitress")
            else:
                patron_options.append('Busboy')
        else:
            patron_options.append('Waitress')
        if game.player_char.player_level() >= 8:
            patron_options.append("Drunkard")
            if game.player_char.player_level() >= 10:
                patron_options.append("Soldier")
                if game.player_char.player_level() >= 25:
                    if 'Red Dragon' in game.player_char.quest_dict['Main']:
                        if not game.player_char.quest_dict['Main']['Red Dragon']['Turned In']:
                            patron_options.append("Hooded Figure")
                    else:
                        patron_options.append("Hooded Figure")
        patron_options.append('Go Back')
        return patron_options

    patron_options = patron_list(game)
    patron_message = "Who would you like to talk with?"
    menu = menus.LocationMenu(game, "The Thirsty Dog", patron_options, options_message=patron_message)
    while True:
        patron_idx = menu.navigate_menu()
        if patron_options[patron_idx] == 'Go Back':
            return
        quest, _ = check_quests(game, patron_options[patron_idx])
        if not quest:
            talks = PATRON_DIALOGUES[patron_options[patron_idx]]
            level_talks = [talks[x] for x in talks if game.player_char.player_level() >= int(x)]
            if patron_options[patron_idx] == "Drunkard" and game.player_char.player_level() >= 65:
                level_talks = [talks[65]]
            response = random.choice(random.choice(level_talks))
            textbox = menus.TextBox(game)
            textbox.print_text_in_rectangle(response)
            game.stdscr.getch()
            textbox.clear_rectangle()
        patron_options = patron_list(game)
        menu.update_options(patron_options, options_message=patron_message, reset_current=False)


def tavern(game):
    while True:
        tavern_options = ["Talk with Patrons", "View the Job Board", "Leave"]
        if any(x[2] for x in game.player_char.quest_dict['Bounty'].values()):
            tavern_options.insert(1, "Turn In Bounty")
        menu = menus.LocationMenu(game, "The Thirsty Dog", tavern_options)
        tavernbox = menus.TextBox(game)
        while True:
            menu.update_options(tavern_options)
            tavern_idx = menu.navigate_menu()
            if tavern_options[tavern_idx] == "Talk with Patrons":
                tavern_patrons(game)
            elif tavern_options[tavern_idx] == "View the Job Board":
                bounty_list = list(game.bounties.values())
                bounty_options = list(game.bounties.keys())
                if len(game.player_char.quest_dict['Bounty']) > 0:
                    bounty_options.append("Abandon Bounty")
                bounty_options.append("Go Back")
                menu.update_options(bounty_options, options_message="Bounty Board")
                while True:
                    bounty_idx = menu.navigate_menu()
                    if bounty_options[bounty_idx] == "Go Back":
                        break
                    if bounty_options[bounty_idx] == "Abandon Bounty":
                        abandon_options = list(game.player_char.quest_dict['Bounty'])
                        abandon_options.append("Go Back")
                        menu.update_options(abandon_options, options_message="Bounty Board")
                        while True:
                            if len(abandon_options) == 1:
                                break
                            abandon_idx = menu.navigate_menu()
                            abandon_choice = abandon_options[abandon_idx]
                            if abandon_choice == "Go Back":
                                break
                            abandon_message = f"Are you sure you want to abandon the {abandon_choice} bounty?"
                            confirm = menus.ConfirmPopupMenu(game, abandon_message, box_height=8)
                            if confirm.navigate_popup():
                                del game.player_char.quest_dict['Bounty'][abandon_choice]
                                abandon_options.pop(abandon_options.index(abandon_choice))
                        if len(abandon_options) == 1:
                            bounty_options.pop(bounty_options.index("Abandon Bounty"))
                        if not any(x[2] for x in game.player_char.quest_dict['Bounty'].values()) and \
                            "Turn In Bounty" in  tavern_options:
                            tavern_options.pop(1)
                    else:
                        selection = bounty_list[bounty_idx]
                        select_message = f"We would like you to defeat {selection['num']} {selection['enemy'].name}s."
                        confirm = menus.ConfirmPopupMenu(game, select_message, box_height=7)
                        if confirm.navigate_popup():
                            game.player_char.quest_dict['Bounty'][selection["enemy"].name] = [selection, 0, False]
                            tavernbox.print_text_in_rectangle(
                                "Return here when the job is done and you will be rewarded.")
                            game.stdscr.getch()
                            tavernbox.clear_rectangle()
                            game.delete_bounty(selection)
                            bounty_idx = bounty_options.index(selection["enemy"].name)
                            bounty_list.pop(bounty_idx)
                            bounty_options.pop(bounty_idx)
                            if "Abandon Bounty" not in bounty_options:
                                bounty_options.insert(-1, "Abandon Bounty")
                    menu.update_options(bounty_options, options_message="Bounty Board")
            elif tavern_options[tavern_idx] == "Turn In Bounty":
                turn_in_options = [x for x, y in game.player_char.quest_dict['Bounty'].items() if y[2]]
                turn_in_options.append("Go Back")
                menu.update_options(turn_in_options, options_message="Bounty Board")
                turn_in_idx = menu.navigate_menu()
                turn_in_choice = turn_in_options[turn_in_idx]
                if turn_in_choice == "Go Back":
                    break
                bounty = game.player_char.quest_dict['Bounty'][turn_in_choice][0]
                gold = bounty["gold"]
                game.player_char.gold += gold
                exp = bounty["exp"]
                game.player_char.level.exp += exp
                if not game.player_char.max_level():
                    game.player_char.level.exp_to_gain -= exp
                bounty_gain = (f"You have completed a bounty on {turn_in_choice}s.\n"
                                f"You gain {gold} gold and {exp} experience.\n")
                if bounty["reward"]:
                    reward = bounty["reward"]()
                    game.player_char.modify_inventory(reward)
                    bounty_gain += f"And you have been rewarded with a {reward.name}."
                tavernbox.print_text_in_rectangle(bounty_gain)
                game.stdscr.getch()
                tavernbox.clear_rectangle()
                del game.player_char.quest_dict['Bounty'][turn_in_choice]
                if not game.player_char.max_level():
                    while game.player_char.level.exp_to_gain <= 0:
                        textbox = menus.TextBox(game)
                        stat_menu = menus.SelectionPopupMenu(game, 
                                                             "Pick the stat you would like to increase.",
                                                             [f'Strength - {game.player_char.stats.strength}',
                                                              f'Intelligence - {game.player_char.stats.intel}',
                                                              f'Wisdom - {game.player_char.stats.wisdom}',
                                                              f'Constitution - {game.player_char.stats.con}',
                                                              f'Charisma - {game.player_char.stats.charisma}',
                                                              f'Dexterity - {game.player_char.stats.dex}'],
                                                             box_height=12, confirm=False)
                        game.player_char.level_up(game, textbox=textbox, menu=stat_menu)
                        if game.player_char.level.exp_to_gain == "MAX":
                            break
                if not any(x[2] for x in game.player_char.quest_dict['Bounty'].values()) and \
                    "Turn In Bounty" in  tavern_options:
                    tavern_options.pop(1)
            elif tavern_options[tavern_idx] == "Leave":
                tavernbox.print_text_in_rectangle("Come back whenever you'd like.")
                game.stdscr.getch()
                tavernbox.clear_rectangle()
                return
            else:
                raise AssertionError("You shouldn't reach here.")


def barracks(game):
    """
    Base location for the player; get quests and direction from the Sergeant
    """

    barracks_message = "Step inside, soldier. This is your new home."
    barracks_options = ["Quests", "Storage", "Leave"]
    menu = menus.LocationMenu(game, barracks_message, barracks_options)
    barracksbox = menus.TextBox(game)
    menu.draw_all()
    menu.refresh_all()
    if "Brass Key" in game.player_char.special_inventory:
        game.special_event("Joffrey's Key")
        game.player_char.modify_inventory(items.BrassKey(), subtract=True, rare=True)
        game.player_char.modify_inventory(items.JoffreysLetter(), rare=True)
        game.player_char.modify_inventory(items.GreatHealthPotion(), num=5)
        barracksbox.print_text_in_rectangle("You gain 5 Great Health Potions and Joffrey's Letter.")
        game.stdscr.getch()
        barracksbox.clear_rectangle()
    while True:
        menu.update_options(barracks_options)
        while True:
            menu.update_options(barracks_options, options_message=barracks_message)
            barrack_idx = menu.navigate_menu()
            if barracks_options[barrack_idx] == "Leave":
                message = "Take care, soldier."
                barracksbox.print_text_in_rectangle(message)
                game.stdscr.getch()
                barracksbox.clear_rectangle()
                return
            if barracks_options[barrack_idx] == 'Storage':
                storage_message = "What would you like to do?"
                storage_options = ['Store', 'Go Back']
                if len(game.player_char.storage) > 0:
                    storage_options.insert(1, 'Retrieve')
                menu.update_options(storage_options, options_message=storage_message)
                while True:
                    menu.update_options(storage_options, options_message=storage_message)
                    storage_idx = menu.navigate_menu()
                    if storage_options[storage_idx] == 'Store':
                        store_message = "What would you like to add to your storage for safe keeping?"
                        store_items = []
                        for itemlist in game.player_char.inventory.values():
                            store_items.append(f"{itemlist[0].name:20}{' ':2}{len(itemlist):>2}")
                        if len(store_items) == 0:
                            barracksbox.print_text_in_rectangle(
                                "You do not have anything to store at the moment.")
                            game.stdscr.getch()
                            barracksbox.clear_rectangle()
                            continue
                        store_items.append('Go Back')
                        menu.update_options(store_items, options_message=store_message)
                        while True:
                            store_idx = menu.navigate_menu()
                            if store_items[store_idx] == 'Go Back':
                                break
                            name = list(filter(None, store_items[store_idx].split('  ')))[0]
                            itemlist = game.player_char.inventory[name]
                            total = len(itemlist)
                            while True:
                                num_message = (f"You have {total} {name}s in your inventory.\n"
                                                f"How many would you like to store?")
                                popup = menus.ShopPopup(game, num_message, box_height=9)
                                num = popup.navigate_popup()
                                if num <= total:
                                    game.player_char.modify_inventory(itemlist[0], num=num, subtract=True, storage=True)
                                    if num == total:
                                        store_items.pop(store_idx)
                                    else:
                                        store_items[store_idx] = f"{name:20}{' ':2}{total-num:>2}"
                                    break
                                else:
                                    barracksbox.print_text_in_rectangle(
                                        "You do not have that many, please enter a correct value.")
                                    game.stdscr.getch()
                                    barracksbox.clear_rectangle()
                            if len(game.player_char.inventory) == 0:
                                break
                            if len(game.player_char.storage) > 0 and "Retrieve" not in storage_options:
                                storage_options.insert(1, 'Retrieve')
                            menu.update_options(store_items, options_message=store_message)
                    elif storage_options[storage_idx] == 'Retrieve':
                        retrieve_message = "What would you like to retrieve?"
                        retrieve_items = []
                        for itemlist in game.player_char.storage.values():
                            retrieve_items.append(f"{itemlist[0].name:20}{' ':2}{len(itemlist):>2}")
                        retrieve_items.append('Go Back')
                        menu.update_options(retrieve_items, options_message=retrieve_message)
                        while True:
                            retrieve_idx = menu.navigate_menu()
                            if retrieve_items[retrieve_idx] == 'Go Back':
                                break
                            name = list(filter(None, retrieve_items[retrieve_idx].split('  ')))[0]
                            itemlist = game.player_char.storage[name]
                            total = len(itemlist)
                            while True:
                                num_message = (f"You have {total} {name}s in storage.\n"
                                               f"How many would you like to retrieve? ")
                                popup = menus.ShopPopup(game, num_message, box_height=9)
                                num = popup.navigate_popup()
                                if num <= total:
                                    game.player_char.modify_inventory(game.player_char.storage[name][0], num, storage=True)
                                    if name not in game.player_char.storage:
                                        retrieve_items.pop(retrieve_idx)
                                    else:
                                        retrieve_items[retrieve_idx] = f"{itemlist[0].name:20}{' ':2}{len(itemlist):>2}"
                                    break
                                else:
                                    barracksbox.print_text_in_rectangle(
                                        "You do not have that many, please enter a valid quantity.")
                                    game.stdscr.getch()
                                    barracksbox.clear_rectangle()
                            menu.update_options(retrieve_items, options_message=retrieve_message)
                            if len(game.player_char.storage) == 0 and "Retrieve" in storage_options:
                                storage_options.pop(1)
                                break
                    else:
                        break
                    menu.update_options(storage_options, options_message=storage_message)
            else:
                quest, responses = check_quests(game, 'Sergeant')
                if not quest:
                    response = random.choice(random.choice(responses))
                    barracksbox.print_text_in_rectangle(response)
                    game.stdscr.getch()
                    barracksbox.clear_rectangle()


def blacksmith(game):
    """
    Griswold's shop - sells weapons and offhand items
    At level 60 (level 30 first promotion or level 1 second promotion), you will receive a quest to find Griswold's
      brother, Chisolm; completing this quest, along with finding the unobtainium, will allow Griswold to either upgrade
      another weapon to ultimate status (for dual wielding) or improve an existing one further
    Once Unobtainium is found, Griswold will craft an ultimate weapon
    """

    if game.player_char.world_dict[(9, 1, 6)].visited and \
            "He Ain't Heavy" not in game.player_char.quest_dict['Side']:
        game.player_char.quest_dict['Side']["He Ain't Heavy"] = quest_dict['Griswold']['Side'][60]["He Ain't Heavy"]
        game.player_char.quest_dict['Side']["He Ain't Heavy"]['Completed'] = True
    if 'Unobtainium' in game.player_char.special_inventory:
        ultimate(game)
    blacksmith_message = "Welcome to Griswold's! What can I do you for?"
    menu = menus.ShopMenu(game, blacksmith_message)
    blacksmithbox = menus.TextBox(game)
    if all(["Summoner" in game.player_char.cls.name,
            "Triangulus" in game.player_char.special_inventory,
            "Quadrata" in game.player_char.special_inventory]):
        game.player_char.modify_inventory(items.VulcansHammer(), rare=True)
        message = ("Ah, I see you have made great progress in collecting the relics.\n"
                   "A while back, I had someone sell me a blacksmith's hammer but it's too nice to use!\n"
                   "I am not sure if it will help you or not but I have an odd feeling you need this...\n"
                   "You gain Vulcan's Hammer.\n")
        blacksmithbox.print_text_in_rectangle(message)
        game.stdscr.getch()
        blacksmithbox.clear_rectangle()
    while True:
        menu.update_itemdict(None)
        blacksmith_choice = menu.navigate_options()
        if blacksmith_choice == 'Leave':
            leave_message = "We're sorry to see you go. Come back anytime!"
            blacksmithbox.print_text_in_rectangle(leave_message)
            game.stdscr.getch()
            blacksmithbox.clear_rectangle()
            return
        done = False
        while not done:
            if blacksmith_choice == 'Buy':
                buy_options = ['Weapon', 'OffHand', 'Armor', 'Go Back']
                menu.update_options(buy_options)
                buy_choice = menu.navigate_options()
                if buy_choice == "Go Back":
                    menu.reset_options(quests=True)
                    break
                if buy_choice == "Weapon":
                    menu.update_options(["1-Handed", "2-Handed"])
                    handed = menu.navigate_options()
                    done = buy(game, menu, buy_choice, handed=handed)
                else:
                    done = buy(game, menu, buy_choice)
            elif blacksmith_choice == 'Sell':
                done = sell(game, menu)
            elif blacksmith_choice == 'Quests':
                quest, responses = check_quests(game, 'Griswold')
                if not quest:
                    response = random.choice(random.choice(responses))
                    blacksmithbox.print_text_in_rectangle(response)
                    game.stdscr.getch()
                    blacksmithbox.clear_rectangle()
                done = True
            else:
                raise Exception("Something went wrong.")


def alchemist(game):
    """
    Alchemist - sells potions and other miscellaneous items (scrolls, keys, etc.)
    At level 20, gives quest for collecting 12 Feathers
    """

    alchemist_message = "Welcome to Ye Olde Item Shoppe."
    menu = menus.ShopMenu(game, alchemist_message)
    alchemistbox = menus.TextBox(game)
    while True:
        menu.update_itemdict(None)
        alchemist_choice = menu.navigate_options()
        if alchemist_choice == 'Leave':
            leave_message = "We're sorry to see you go. Come back anytime!"
            alchemistbox.print_text_in_rectangle(leave_message)
            game.stdscr.getch()
            alchemistbox.clear_rectangle()
            return
        done = False
        while not done:
            if alchemist_choice == 'Buy':
                done = buy(game, menu, "Alchemist")
            elif alchemist_choice == 'Sell':
                done = sell(game, menu)
            elif alchemist_choice == 'Quests':
                quest, responses = check_quests(game, 'Alchemist')
                if not quest:
                    response = random.choice(random.choice(responses))
                    alchemistbox.print_text_in_rectangle(response)
                    game.stdscr.getch()
                    alchemistbox.clear_rectangle()
                done = True
            else:
                raise Exception("Something went wrong.")


def jeweler(game):
    """
    Jewelry shop - sells Pendants and Rings
    At level 55, gives quest to collect 6 elemental motes, rewards Elemental Amulet
    """

    jeweler_message = "Come glimpse the finest jewelry in the land."
    menu = menus.ShopMenu(game, jeweler_message)
    jewelerbox = menus.TextBox(game)
    while True:
        menu.update_itemdict(None)
        jeweler_choice = menu.navigate_options()
        if jeweler_choice == 'Leave':
            leave_message = "We're sorry to see you go. Come back anytime!"
            jewelerbox.print_text_in_rectangle(leave_message)
            game.stdscr.getch()
            jewelerbox.clear_rectangle()
            return
        done = False
        while not done:
            if jeweler_choice == 'Buy':
                done = buy(game, menu, "Jeweler")
            elif jeweler_choice == 'Sell':
                done = sell(game, menu)
            elif jeweler_choice == 'Quests':
                quest, responses = check_quests(game, 'Jeweler')
                if not quest:
                    response = random.choice(random.choice(responses))
                    jewelerbox.print_text_in_rectangle(response)
                    game.stdscr.getch()
                    jewelerbox.clear_rectangle()
                done = True
            else:
                raise Exception("Something went wrong.")


def church(game):
    church_message = "Come in my child. You are always welcome in the arms of Elysia. How can we be of service?"
    church_options = ['Promotion', 'Save', 'Quests', 'Quit Game', 'Leave']
    menu = menus.LocationMenu(game, church_message, church_options)
    churchbox = menus.TextBox(game)
    while True:
        church_idx = menu.navigate_menu()
        if church_options[church_idx] == 'Promotion':
            if game.player_char.level.level == 30 and game.player_char.level.pro_level < 3:
                classes.promotion(game)
            else:
                if game.player_char.level.pro_level == 3:
                    churchbox.print_text_in_rectangle(
                        "You are at max promotion level and can no longer be promoted.\n")
                else:
                    churchbox.print_text_in_rectangle(
                        "You need to be level 30 before you can promote your character.\n")
                game.stdscr.getch()
                churchbox.clear_rectangle()
        elif church_options[church_idx] == 'Save':
            confirm = menus.ConfirmPopupMenu(game, "A save file under this name already exists. Are you sure you want to overwrite it?", box_height=8)
            game.player_char.save(game=game, confirm_popup=confirm, save_popup=menus.save_file_popup)
        elif church_options[church_idx] == 'Quests':
            quest, responses = check_quests(game, 'Priest')
            if not quest:
                response = random.choice(random.choice(responses))
                churchbox.print_text_in_rectangle(response)
                game.stdscr.getch()
                churchbox.clear_rectangle()
        elif church_options[church_idx] == 'Quit Game':
            quit_confirm = menus.ConfirmPopupMenu(game, "Are you sure you want to quit? Any unsaved progress will be lost.", box_height=8)
            if quit_confirm.navigate_popup():
                game.player_char.quit = True
                return
        elif church_options[church_idx] == 'Leave':
            churchbox.print_text_in_rectangle("Let the light of Elysia guide you.")
            game.stdscr.getch()
            churchbox.clear_rectangle()
            return
        else:
            raise AssertionError("You shouldn't reach here.")
        menu.update_options(church_options, reset_current=False)


def secret_shop(game):

    ss_message = "Since you're here, you might as well buy some supplies."
    menu = menus.ShopMenu(game, ss_message)
    secret_options = ['Buy', 'Sell', 'Leave']
    menu.update_options(secret_options)
    secretshopbox = menus.TextBox(game)
    while True:
        menu.reset_options()
        menu.update_itemdict(None)
        secret_choice = menu.navigate_options()
        if secret_choice == 'Leave':
            secretshopbox.print_text_in_rectangle("We're sorry to see you go. Come back anytime!")
            game.stdscr.getch()
            secretshopbox.clear_rectangle()
            game.player_char.move_south(game)
            return
        done = False
        while not done:
            if secret_choice == "Buy":
                buy_options = ["Weapon", "OffHand", "Armor", "Accessories", "Miscellaneous", "Go Back"]
                menu.update_options(buy_options)
                buy_choice = menu.navigate_options()
                if buy_choice == "Go Back":
                    menu.reset_options(quests=True)
                    break
                if buy_choice == "Weapon":
                    menu.update_options(["1-Handed", "2-Handed"])
                    handed = menu.navigate_options()
                    done = buy(game, menu, buy_choice, handed=handed)
                else:
                    done = buy(game, menu, buy_choice)
            elif secret_choice == "Sell":
                done = sell(game, menu)
            else:
                raise Exception("Something went wrong.")


def ultimate_armor_repo(game):
    if "He Ain't Heavy" in game.player_char.quest_dict['Side']:
        if not game.player_char.quest_dict['Side']["He Ain't Heavy"]['Completed']:
            game.player_char.quest_dict['Side']["He Ain't Heavy"]['Completed'] = True
            quest_texts = ["Hmmm, I see my big brother sent you to look for me.", 
                           "Tell him do not worry about me and that I will not return",
                           " until the ultimate evil has been vanquished."]
            ultimate_pad = menus.QuestPopupMenu(game, box_height=len(quest_texts)+2, box_width=len(max(quest_texts, key=len))+4)
            ultimate_pad.draw_popup(quest_texts)
    loc = (game.player_char.location_x, game.player_char.location_y, game.player_char.location_z)
    tile = game.player_char.world_dict[loc]
    ultimatebox = menus.TextBox(game)
    if not tile.looted:
        ultimate_message = f"Which type of armor do you choose?"
        ultimate_options = ['Cloth', 'Light', 'Medium', 'Heavy', "Leave"]
        no_message = "You need time to consider you choice, I respect that. Come back when you have made your choice."
        armor_list = [items.MerlinRobe(), items.DragonHide(), items.Aegis(), items.Genji()]
        popup = menus.SelectionPopupMenu(game, ultimate_message, ultimate_options, confirm=True)
        ultimate_idx = popup.navigate_popup()
        if ultimate_options[ultimate_idx] == "Leave":
            ultimatebox.print_text_in_rectangle(no_message)
            game.stdscr.getch()
            ultimatebox.clear_rectangle()
        else:
            ultimatebox.print_text_in_rectangle(armor_list[ultimate_idx].description)
            game.stdscr.getch()
            ultimatebox.clear_rectangle()
            confirm_str = f"You have chosen an immaculate {ultimate_options[ultimate_idx].lower()} armor. Is this correct?"
            confirm = menus.ConfirmPopupMenu(game, confirm_str, box_height=8)
            if confirm.navigate_popup():
                chosen = armor_list[ultimate_idx]
                ultimatebox.print_text_in_rectangle(
                    "Please wait while I craft your armor, it will only take a few moments.")
                time.sleep(3)
                ultimatebox.clear_rectangle()
                ultimatebox.print_text_in_rectangle(f"I present to you the legendary armor, {chosen.name}!")
                game.player_char.modify_inventory(chosen, 1)
                tile.looted = True
                game.stdscr.getch()
                ultimatebox.clear_rectangle()
            else:
                ultimatebox.print_text_in_rectangle(no_message)
                game.stdscr.getch()
                ultimatebox.clear_rectangle()
    else:
        ultimatebox.print_text_in_rectangle("Please, defeat him before it's too late...do not worry about me.")
        game.stdscr.getch()
        ultimatebox.clear_rectangle()
    game.player_char.move_south(game)


def buy(game, menu, buy_choice, handed=None):

    if buy_choice == "Weapon":
        item_dict = items.items_dict[buy_choice][handed]
    elif buy_choice in ["Alchemist", "Miscellaneous"]:
        item_dict = {}
        alc_dict = items.items_dict["Potion"].copy()
        alc_dict.update(items.items_dict["Misc"])
        for key, value in alc_dict.items():
            item_dict[key] = value
    elif buy_choice in ["Jeweler", "Accessories"]:
        item_dict = {}
        je_dict = {"Ring": items.items_dict["Accessory"]["Ring"],
                   "Pendant": items.items_dict["Accessory"]["Pendant"]}
        for key, value in je_dict.items():
            item_dict[key] = value
    else:
        item_dict = items.items_dict[buy_choice]
    while True:
        menu.update_itemdict(item_dict, reset_current=False)
        item_str = menu.navigate_items()
        if item_str == "Go Back":
            menu.update_itemdict(None)
            return False if buy_choice not in ["Alchemist", "Jeweler", "Secret"] else True
        buybox = menus.TextBox(game)
        typ, name, adj_cost, _ = [x.strip() for x in list(filter(None, item_str.split('  ')))]
        if int(adj_cost) > game.player_char.gold:
            buybox.print_text_in_rectangle("You do not have enough gold to purchase this item.")
            game.stdscr.getch()
            buybox.clear_rectangle()
        else:
            popup = menus.ShopPopup(game, f"How many {name} do you want to buy?", box_height=7)
            num = popup.navigate_popup()
            total_cost = int(adj_cost) * num
            if int(total_cost) > game.player_char.gold:
                buybox.print_text_in_rectangle("You do not have enough gold to purchase this item.")
                game.stdscr.getch()
                buybox.clear_rectangle()
            elif num > 0:
                item = [x for x in item_dict[typ] if x().name == name][0]()
                buy_popup = menus.ConfirmPopupMenu(
                    game, f"Are you sure you want to buy {num} {name} for {total_cost} gold?", box_height=8)
                if buy_popup.navigate_popup():
                    game.player_char.gold -= int(total_cost)
                    game.player_char.modify_inventory(item, num=num)


def sell(game, menu):

    sellbox = menus.TextBox(game)
    if len(game.player_char.inventory) == 0:
        sellbox.print_text_in_rectangle("You don't have anything to sell.")
        game.stdscr.getch()
        sellbox.clear_rectangle()
        return True
    while True:
        sell_dict = {}
        for name, item in game.player_char.inventory.items():
            if not item[0].ultimate:
                sell_dict[name] = item
        if len(sell_dict) == 0:
            return True
        menu.update_itemdict(sell_dict, reset_current=False)
        item_str = menu.navigate_items()
        if item_str == "Go Back":
            menu.update_itemdict(None)
            return True
        typ_name, total = [x.strip() for x in list(filter(None, item_str.split(" x")))]
        _, name = [x.strip() for x in list(filter(None, typ_name.split('  ')))]
        item = sell_dict[name][0]
        popup = menus.ShopPopup(game, f"How many {name} do you want to sell?", max=total, box_height=8)
        num = popup.navigate_popup()
        if num > 0:
            adj_cost = int((0.025 * game.player_char.stats.charisma) * num * item.value)
            sell_popup = menus.ConfirmPopupMenu(
                game, f"Do you want to sell {num} {name} for {adj_cost} gold?", box_height=8)
            if sell_popup.navigate_popup():
                game.player_char.gold += int(adj_cost)
                game.player_char.modify_inventory(item, num=num, subtract=True)


def warp_point(game):
    warpbox = menus.TextBox(game)
    warp_message = f"Hello, {game.player_char.name}. Do you want to warp down to level 5?"
    warp_popup = menus.ConfirmPopupMenu(game, warp_message, box_height=8)
    if warp_popup.navigate_popup():
        if not game.player_char.world_dict[(3, 0, 5)].visited:
            game.player_char.world_dict[(3, 0, 5)].visited = True
            game.player_char.world_dict[(2, 0, 5)].near = True
            game.player_char.world_dict[(4, 0, 5)].near = True
            game.player_char.world_dict[(3, 1, 5)].near = True
        message = "You step into the warp point, taking you deep into the dungeon."
        warpbox.print_text_in_rectangle(message)
        game.stdscr.getch()
        warpbox.clear_rectangle()
        game.player_char.world_dict[(3, 0, 5)].warped = True
        game.player_char.change_location(3, 0, 5)
        return True
    message = "Not a problem, come back when you change your mind."
    warpbox.print_text_in_rectangle(message)
    game.stdscr.getch()
    warpbox.clear_rectangle()


def town_options(game):
    town_options = ['Barracks', 'Tavern', 'Church',
                    'Blacksmith', 'Alchemist', 'Jeweler',
                    'Dungeon', 'Character Menu', "Old Warehouse"]
    if game.player_char.warp_point:
        town_options.pop(-1)
        town_options.append("Warp Point")
    return town_options


def town(game):

    locations = [barracks, tavern, church, blacksmith, alchemist, jeweler]
    options = town_options(game)
    game.player_char.health.current = game.player_char.health.max
    game.player_char.mana.current = game.player_char.mana.max
    menu = menus.TownMenu(game, options)
    townbox = menus.TextBox(game)
    if "Dead Body" in game.player_char.special_inventory and \
        not game.player_char.quest_dict['Side']['Rookie Mistake']['Completed']:
        game.player_char.quest_dict['Side']['Rookie Mistake']['Completed'] = True
        game.player_char.modify_inventory(items.DeadBody(), subtract=True, rare=True)
        townbox.print_text_in_rectangle("You have completed the quest Rookie Mistake.")
        game.stdscr.getch()
        townbox.clear_rectangle()
    while True:
        game.player_char.encumbered = game.player_char.current_weight() > game.player_char.max_weight()
        town_idx = menu.navigate_menu()
        if options[town_idx] == 'Dungeon':
            townbox.print_text_in_rectangle("You descend into the dungeon.")
            game.stdscr.getch()
            townbox.clear_rectangle()
            game.player_char.change_location(5, 10, 1)
            break
        if options[town_idx] == 'Character Menu':
            game.player_char.character_menu(game)
        elif options[town_idx] == 'Old Warehouse':
            townbox.print_text_in_rectangle("Authorized personnel only. Please leave.")
            game.stdscr.getch()
            townbox.clear_rectangle()
        elif options[town_idx] == 'Warp Point':
            if warp_point(game):
                return
        else:
            if game.player_char.player_level() < 5 and options[town_idx] == "Blacksmith":
                townbox.print_text_in_rectangle("Sorry but the blacksmith is currently closed. Try again later.")
                game.stdscr.getch()
                townbox.clear_rectangle()
            elif game.player_char.player_level() < 10 and options[town_idx] == "Jeweler":
                townbox.print_text_in_rectangle("Sorry but the jeweler is currently closed.    Try again later.")
                game.stdscr.getch()
                townbox.clear_rectangle()
            else:
                locations[town_idx](game)
        if game.player_char.quit:
            break
        options = town_options(game)
        menu.options_list = options


# quest dictionary can be imported from core/town.py
