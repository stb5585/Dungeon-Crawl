###########################################
""" Town manager """

# Imports
import random
import time
from textwrap import wrap

import items
import classes
import utils


# Functions
def upgrade(game):
    """
    function handles weapon upgrade for Find Chisolm quest
    upgrades non-ultimate weapon to be an ultimate weapon (for damaging the final boss) or further upgrade an existing
      ultimate weapon (increase damage, crit chance, etc.) TODO
    """
    message = ""
    return message


def ultimate(game):
    texts = [
        "Oh my...can it possibly be?...the legendary ore...Unobtainium?",
        "I can\'t believe you have found it!",
        "It has been a lifelong dream of mine to forge a weapon from the mythical metal."
    ]
    ultimate_pad = utils.QuestPopupMenu(game, box_height=len(texts)+2, box_width=len(max(texts, key=len))+4)
    ultimate_pad.draw_popup(texts)
    weapon_list = {'Dagger': items.Carnwennan(),
                   'Sword': items.Excalibur(),
                   'Mace': items.Mjolnir(),
                   'Fist': items.GodsHand(),
                   'Axe': items.Jarnbjorn(),
                   'Polearm': items.Gungnir(),
                   'Staff': [items.PrincessGuard(), items.DragonStaff()],
                   'Hammer': items.Skullcrusher(),
                   'Ninja Blade': items.Ninjato()}
    make_options = []
    i = 0
    for typ, weapon in weapon_list.items():
        if typ == 'Staff':
            if 'Archbishop' == game.player_char.cls.name:
                weapon = weapon[0]
            else:
                weapon = weapon[1]
        if classes.equip_check(weapon, game.player_char.cls, "Weapon"):
            make_options.append(typ)
            i += 1
    make_options.append('Not Yet')
    make_message = "What type of weapon would you like me to make?"
    menu = utils.MainMenu(make_options, top_text=make_message)  # TODO
    ultimatebox = utils.TextBox(game)
    while True:
        make_idx = menu.navigate_menu()
        if make_options[make_idx][0] == 'Not yet':
            ultimatebox.print_text_in_rectangle(
                "I am sorry to hear that...please come back if you change your mind.")
            game.stdscr.getch()
            return
        else:
            weapon = weapon_list[make_options[make_idx]]
            if isinstance(weapon, list):
                if 'Archbishop' == game.player_char.cls.name:
                    weapon = weapon[0]
                else:
                    weapon = weapon[1]
            ultimatebox.print_text_in_rectangle(
                "Give me a moment and I will make you an ultimate weapon...")
            time.sleep(5)
            ultimatebox.print_text_in_rectangle(
                f"I present to you, {game.player_char.name}, the mighty {weapon.name}!")
            time.sleep(2)
            game.player_char.modify_inventory(weapon)
            del game.player_char.inventory['Unobtainium']
            if "He Ain't Heavy" in game.player_char.quest_dict['Side']:
                if game.player_char.quest_dict['Side']["He Ain't Heavy"]['Turned In']:
                    # TODO
                    print("I still have a bit of ore left if you want me to upgrade another weapon or I may even be able to"
                          " improve the one I just made.")


def turn_in_quest(game, quest, typ):
    quest_desc = wrap(game.player_char.quest_dict[typ][quest]['End Text'], 50)
    quest_pad = utils.QuestPopupMenu(game, box_height=len(quest_desc)+2, box_width=len(max(quest_desc, key=len))+4)
    quest_pad.draw_popup(quest_desc)
    quest_pad.clear_popup()
    game.player_char.quest_dict[typ][quest]['Turned In'] = True
    reward = game.player_char.quest_dict[typ][quest]['Reward']
    if len(reward) == 1:
        reward = reward[0]
    else:
        reward_options = [x.name for x in reward]
        popup = utils.SelectionPopupMenu(game, "Choose your reward", reward_options)
        reward_idx = popup.navigate_popup()
        reward = reward[reward_idx]
    exp = game.player_char.quest_dict[typ][quest]['Experience'] * game.player_char.level.pro_level
    if reward == 'Gold':
        game.player_char.gold += game.player_char.quest_dict[typ][quest]['Reward Number']
        reward_message = f"You received {game.player_char.quest_dict[typ][quest]['Reward Number']} gold and {exp} experience.\n"
    elif reward == 'Upgrade':
        reward_message = upgrade(game)
    elif reward == 'Power Up':
        reward_message = game.player_char.special_power(game)
        reward_message += f"You received {exp} experience.\n"
    elif reward == 'Warp Point':
        game.player_char.warp = True
        reward_message = f"You received {exp} experience and gain access to the Warp Point.\n"
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
    turninbox = utils.TextBox(game)
    turninbox.print_text_in_rectangle(reward_message)
    game.stdscr.getch()
    turninbox.clear_rectangle()
    if game.player_char.quest_dict[typ][quest]['Type'] == 'Collect':
        item = game.player_char.quest_dict[typ][quest]['What']
        del game.player_char.special_inventory[item.name]
    if not game.player_char.max_level():
        while game.player_char.level.exp_to_gain <= 0:
            game.player_char.level_up(game)
            if game.player_char.level.exp_to_gain == "MAX":
                break


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

    response_map = {'Barkeep': ["Great, come back to me when it is completed.",
                                "That's a shame, come back if you change your mind."],
                    'Waitress': ["Oh, that's truly wonderful! I'll be waiting to hear from you.",
                                 "I understand, it was stupid of me to even ask..."],
                    'Busboy': ["Good to hear. Now excuse me, I have to get back to work.",
                               "Pfft, why did I even bother?"],
                    'Soldier': ["Excellent, your efforts will not go unnoticed.",
                                "Do not waste my time if you are not dedicated to the cause."],
                    'Drunkard': ["Well fine then, go...wait, oh you said yes...(hic) well thanks! I'll be right here, "
                                 "as always...(hic)",
                                 "Oh I see, your time (hic) is too precious, huh?"],
                    'Hooded Figure': ["Splendid, I will await your return.",
                                      "Pity, you showed so much promise. Be gone then..."],
                    'Griswold': ["Finally someone with some stones! I knew I liked you!",
                                 "Accept or not, at least keep an eye out..."],
                    'Alchemist': ["Our arrangement will be mutually beneficial, you will see.",
                                  "It's a shame you deny me this request."],
                    'Jeweler': ["You will not be disappointed!",
                                "Not sure of your reasoning but fair enough."],
                    'Priest': ["The light of Elysia will guide your efforts.",
                               "Patience is a virtue I hold sacred. I will wait as long as I need."],
                    'Sergeant': ["Outstanding! Return to me when you have completed the quest.",
                                 "You came a long way for nothing..."]
                    }
    quest_key = list(quest)[0]
    who = quest[quest_key]['Who']
    quest_desc = wrap(quest[quest_key]['Start Text'], 50)
    menu = utils.QuestPopupMenu(game, box_height=len(quest_desc)+2, box_width=len(max(quest_desc, key=len))+4)
    accepted = False
    acceptquestbox = utils.TextBox(game)
    menu.draw_popup(quest_desc)
    confirm_str = "Do you accept this quest?"
    confirm = utils.ConfirmPopupMenu(game, confirm_str, box_height=6)
    if confirm.navigate_popup():
        game.player_char.quest_dict[typ][quest_key] = quest[quest_key]
        acceptquestbox.print_text_in_rectangle(response_map[who][0])
        game.stdscr.getch()
        if quest[quest_key]['Type'] == 'Defeat':
            if quest_key in game.player_char.kill_dict:
                game.player_char.quest_dict[typ][quest_key]['Completed'] = True
        accepted = True
    else:
        acceptquestbox.print_text_in_rectangle(response_map[who][1])
        game.stdscr.getch()
    return accepted


def check_quests(game, quest_giver, check=False):

    player_mains = list(game.player_char.quest_dict['Main'])
    player_sides = list(game.player_char.quest_dict['Side'])
    mains = quest_dict[quest_giver]['Main']
    main_quests = [mains[x] for x in mains if game.player_char.player_level() >= x]
    sides = quest_dict[quest_giver]['Side']
    side_quests = [sides[x] for x in sides if game.player_char.player_level() >= x]
    if check:
        return bool(main_quests or side_quests)
    quest = False
    responses = [["I have no new quests for you at this time."]]
    if len(main_quests) > 0:
        for main_quest in main_quests:
            key = list(main_quest)[0]
            if key in player_mains:
                if game.player_char.quest_dict['Main'][key]['Completed'] and \
                        not game.player_char.quest_dict['Main'][key]['Turned In']:
                    turn_in_quest(game, key, "Main")
                    quest = True
                if not game.player_char.quest_dict['Main'][key]['Turned In']:
                    responses.append([game.player_char.quest_dict['Main'][key]['Help Text']])
            else:
                quest = accept_quest(game, main_quest, "Main")
            if quest:
                break
    if len(side_quests) > 0:
        for side_quest in side_quests:
            key = list(side_quest)[0]
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
                break
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
    patrons = {'Barkeep': {1: ["If you want to access the character menu, you can do so by hitting the (c)"
                                " button.",
                                "Make sure to stop by from time to time. You never know who might show up.",
                                "Equipment vendors will show you how an item can improve or hurt your fighting"
                                " ability. If an item type doesn't show any change, your class can't use it.",
                                "Heavier armor provides better protection but lowers your mobility in combat. "
                                "Choose carefully."],
                           5: ["How did you like that stat bonus at level 4? You get another every 4th "
                               "level, so plan your promotions accordingly.",
                               "If you get a quest from someone, come back and talk with them after it is "
                               "completed and they will likely reward you for your efforts."],
                          10: ["Locked chests contain more powerful items compared with unlocked ones, "
                               "however you need a key or a lockpick to get to the treasure.",
                               "Boss enemies have true sight, so that Invisibility Pendant is useless against "
                               "them.",
                               "Some status effects last until the end of combat or until healed. Make sure to "
                               "stock up on potions!"]
                           },
                'Waitress': {1: ["Entering the town will replenish your health and mana. Seems like you "
                                 "could take advantage of that.",
                                 "Sorry, I can't talk now! I am getting married and need to make as much "
                                 "money as I can."],
                            5:  ["Some spells can be cast outside of battle. You can do so in the Character Menu "
                                 "after inspecting the spell."],
                            10: ["(sobbing) I can't believe it...a week before our wedding and my husband "
                                 "to be decides to join the fight against the prime evil...I want to be "
                                 "mad but he says he can't stand by when I am in danger. My hero..."],
                            25: ["Joffrey returned yesterday bloodied but resolute. He has gained much "
                                 "experience and hopes to have found the source of our suffering by "
                                 "month's end. I gave him my lucky pendant to return to me when his "
                                 "mission is complete."],
                            },
                'Soldier': {10: ["You may find locked doors along your path while exploring the dungeon. "
                                 "You can't open these with just any old key, you need an actual Old Key.",
                                 "Watch your carry weight in the Character Menu. If you try to carry more than"
                                 " you can manage, you will become encumbered, which affects your speed "
                                 "in combat.",
                                 "Check the shops periodically, you may notice new items available to buy."],
                            25: ["I just finished my shift guarding the old warehouse behind the barracks. "
                                 "They won't tell us what's in there but I have seen several scientists "
                                 "come and go."],
                            65: ["The Devil is immune to normal weapons but legend says there is a "
                                 "material that will do the job."]
                            },
                'Drunkard': {8: ["(hic)...I am not as think as you drunk I am...(hic)"],
                            25: ["Do you see (hic) that person in the corner? What's their deal, TAKE THE "
                                 "HOOD OFF ALREADY!...ah whatever..."],
                            30: ["(hic)...I heard tell there were secret passages...(hic) in the dungeon."]
                            },
                # TODO Busboy replaces Waitress after conclusion of Joffrey quest
                'Busboy': {1: ["The waitress left crying some time ago...sounds like her fiance was killed in the "
                               "dungeons.",
                               "Entering the town will replenish your health and mana. Seems like you "
                               "could take advantage of that.",
                               "Some spells can be cast outside of battle. You can do so in the Character Menu "
                               "after inspecting the spell."],
                    },
                'Hooded Figure': {25: ["..."],
                                  35: ["Hmm...interesting..."],
                                  50: ["Your power has grown...I am impressed."],
                                  60: ["Have you defeated the Red Dragon yet?"],
                }
            }

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
    menu = utils.LocationMenu(game, "The Thirsty Dog", patron_options, options_message=patron_message)
    while True:
        patron_idx = menu.navigate_menu()
        if patron_options[patron_idx] == 'Go Back':
            return
        quest, responses = check_quests(game, patron_options[patron_idx])
        if not quest:
            talks = patrons[patron_options[patron_idx]]
            level_talks = [talks[x] for x in talks if game.player_char.player_level() >= x]
            responses += level_talks
            response = random.choice(random.choice(responses))
            textbox = utils.TextBox(game)
            textbox.print_text_in_rectangle(response)
            game.stdscr.getch()
        patron_options = patron_list(game)
        menu.update_options(patron_options, options_message=patron_message, reset_current=False)


def tavern(game):
    while True:
        tavern_options = ["Talk with Patrons", "View the Job Board", "Leave"]
        if any(x[2] for x in game.player_char.quest_dict['Bounty'].values()):
            tavern_options.insert(1, "Turn In Bounty")
        menu = utils.LocationMenu(game, "The Thirsty Dog", tavern_options)
        tavernbox = utils.TextBox(game)
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
                            confirm = utils.ConfirmPopupMenu(game, abandon_message, box_height=8)
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
                        confirm = utils.ConfirmPopupMenu(game, select_message, box_height=7)
                        if confirm.navigate_popup():
                            game.player_char.quest_dict['Bounty'][selection["enemy"].name] = [selection, 0, False]
                            tavernbox.print_text_in_rectangle(
                                "Return here when the job is done and you will be rewarded.")
                            game.stdscr.getch()
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
                    reward = bounty["reward"]
                    game.player_char.modify_inventory(reward)
                    bounty_gain += f"And you have been rewarded with a {reward.name}."
                tavernbox.print_text_in_rectangle(bounty_gain)
                game.stdscr.getch()
                del game.player_char.quest_dict['Bounty'][turn_in_choice]
                if not game.player_char.max_level():
                    while game.player_char.level.exp_to_gain <= 0:
                        game.player_char.level_up(game)
                        if game.player_char.level.exp_to_gain == "MAX":
                            break
                if not any(x[2] for x in game.player_char.quest_dict['Bounty'].values()) and \
                    "Turn In Bounty" in  tavern_options:
                    tavern_options.pop(1)
            elif tavern_options[tavern_idx] == "Leave":
                tavernbox.print_text_in_rectangle("Come back whenever you'd like.")
                game.stdscr.getch()
                return
            else:
                raise AssertionError("You shouldn't reach here.")


def barracks(game):
    """
    Base location for the player; get quests and direction from the Sergeant
    """

    barracks_message = "Step inside, soldier. This is your new home."
    barracks_options = ["Quests", "Storage", "Leave"]
    menu = utils.LocationMenu(game, barracks_message, barracks_options)
    barracksbox = utils.TextBox(game)
    menu.draw_all()
    menu.refresh_all()
    if "Ornate Key" in game.player_char.special_inventory:
        game.special_event("Joffrey's Key")
        game.player_char.modify_inventory(items.OrnateKey(), subtract=True, rare=True)
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
                            break
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
                                popup = utils.ShopPopup(game, num_message, box_height=9)
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
                                popup = utils.ShopPopup(game, num_message, box_height=9)
                                num = popup.navigate_popup()
                                if num <= total:
                                    game.player_char.modify_inventory(game.player_char.storage[name][0], num, storage=True)
                                    if name not in game.player_char.storage:
                                        retrieve_items.pop(retrieve_idx)
                                    break
                                else:
                                    barracksbox.print_text_in_rectangle(
                                        "You do not have that many, please enter a valid quantity.")
                                    game.stdscr.getch()
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
    menu = utils.ShopMenu(game, blacksmith_message)
    blacksmithbox = utils.TextBox(game)
    while True:
        menu.update_itemdict(None)
        blacksmith_choice = menu.navigate_options()
        if blacksmith_choice == 'Leave':
            leave_message = "We're sorry to see you go. Come back anytime!"
            blacksmithbox.print_text_in_rectangle(leave_message)
            game.stdscr.getch()
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
    menu = utils.ShopMenu(game, alchemist_message)
    alchemistbox = utils.TextBox(game)
    while True:
        menu.update_itemdict(None)
        alchemist_choice = menu.navigate_options()
        if alchemist_choice == 'Leave':
            leave_message = "We're sorry to see you go. Come back anytime!"
            alchemistbox.print_text_in_rectangle(leave_message)
            game.stdscr.getch()
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
    menu = utils.ShopMenu(game, jeweler_message)
    jewelerbox = utils.TextBox(game)
    while True:
        menu.update_itemdict(None)
        jeweler_choice = menu.navigate_options()
        if jeweler_choice == 'Leave':
            leave_message = "We're sorry to see you go. Come back anytime!"
            jewelerbox.print_text_in_rectangle(leave_message)
            game.stdscr.getch()
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
    menu = utils.LocationMenu(game, church_message, church_options)
    churchbox = utils.TextBox(game)
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
        elif church_options[church_idx] == 'Save':
            game.player_char.save(game=game)  # Can only save at church in town
        elif church_options[church_idx] == 'Quests':
            quest, responses = check_quests(game, 'Priest')
            if not quest:
                response = random.choice(random.choice(responses))
                churchbox.print_text_in_rectangle(response)
                game.stdscr.getch()
                churchbox.clear_rectangle()
        elif church_options[church_idx] == 'Quit Game':
            if game.player_char.game_quit(game):
                return
        elif church_options[church_idx] == 'Leave':
            churchbox.print_text_in_rectangle("Let the light of Elysia guide you.")
            game.stdscr.getch()
            return
        else:
            raise AssertionError("You shouldn't reach here.")
        menu.update_options(church_options, reset_current=False)


def secret_shop(game):

    ss_message = "Since you're here, you might as well buy some supplies."
    menu = utils.ShopMenu(game, ss_message)
    secret_options = ['Buy', 'Sell', 'Leave']
    menu.update_options(secret_options)
    secretshopbox = utils.TextBox(game)
    while True:
        menu.reset_options()
        menu.update_itemdict(None)
        secret_choice = menu.navigate_options()
        if secret_choice == 'Leave':
            secretshopbox.print_text_in_rectangle("We're sorry to see you go. Come back anytime!")
            game.stdscr.getch()
            game.player_char.move_south(game)
            return
        done = False
        while not done:
            if secret_choice == 'Buy':
                done = buy(game, menu, "Secret")
            elif secret_choice == 'Sell':
                done = sell(game, menu)
            else:
                raise Exception("Something went wrong.")


def ultimate_armor_repo(game):
    if "He Ain't Heavy" in game.player_char.quest_dict['Side']:
        if not game.player_char.quest_dict['Side']["He Ain't Heavy"]['Completed']:
            game.player_char.quest_dict['Side']["He Ain't Heavy"]['Completed'] = True
            quest_texts = ["Hmmm, I see my big brother sent you to look for me.", 
                    "Tell him do not worry about me and that I will not return until the ultimate evil has been vanquished."]
            ultimate_pad = utils.QuestPopupMenu(game, box_height=len(quest_texts)+2, box_width=len(max(quest_texts, key=len))+4)
            ultimate_pad.draw_popup(quest_texts)
    loc = (game.player_char.location_x, game.player_char.location_y, game.player_char.location_z)
    tile = game.player_char.world_dict[loc]
    texts = [
        "Hello, my name is Chisolm, Griswold's brother.",
        "I tried to defeat the ultimate evil but could not even damage it.",
        "I barely escaped, camping here to lick my wounds.",
        "I decided I would instead use my blacksmith skills to help those who look to do what I could not.",
        "Choose the type of armor you would prefer and I will make you the finest set you could imagine."
    ]
    if not tile.looted:
        ultimate_pad = utils.QuestPopupMenu(game, box_height=len(texts)+2, box_width=len(max(texts, key=len))+4)
        ultimate_pad.draw_popup(texts)
        ultimatebox = utils.TextBox(game)
        ultimate_message = "Which type of armor do you choose?"
        ultimate_options = ['Cloth', 'Light', 'Medium', 'Heavy', "Leave"]
        no_message = "You need time to consider you choice, I respect that. Come back when you have made your choice."
        armor_list = [items.MerlinRobe(), items.DragonHide(), items.Aegis(), items.Genji()]
        popup = utils.SelectionPopupMenu(game, ultimate_message, ultimate_options)
        ultimate_idx = popup.navigate_popup()
        if ultimate_options[ultimate_idx] == "Leave":
            ultimatebox.print_text_in_rectangle(no_message)
            game.stdscr.getch()
        else:
            ultimatebox.print_text_in_rectangle(armor_list[ultimate_idx].description)
            game.stdscr.getch()
            confirm_str = f"You have chosen an immaculate {ultimate_options[ultimate_idx].lower()} armor. Is this correct?"
            confirm = utils.ConfirmPopupMenu(game, confirm_str, box_height=8)
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
            else:
                ultimatebox.print_text_in_rectangle(no_message)
                game.stdscr.getch()
    game.player_char.move_south(game)


def buy(game, menu, buy_choice, handed=None):

    if buy_choice == "Weapon":
        item_dict = items.items_dict[buy_choice][handed]
    elif buy_choice == "Alchemist":
        item_dict = {}
        alc_dict = items.items_dict["Potion"].copy()
        alc_dict.update(items.items_dict["Misc"])
        for key, value in alc_dict.items():
            item_dict[key] = value
    elif buy_choice == "Jeweler":
        item_dict = {}
        je_dict = {"Ring": items.items_dict["Accessory"]["Ring"],
                   "Pendant": items.items_dict["Accessory"]["Pendant"]}
        for key, value in je_dict.items():
            item_dict[key] = value
    elif buy_choice == "Secret":
        item_dict = {}
        for typ, typ_dict in items.items_dict.items():
            if typ == "Weapon":
                for handed in ["1-Handed", "2-Handed"]:
                    item_dict.update(items.items_dict[typ][handed])
            elif typ == "Accessory":
                for acc in ["Ring", "Pendant"]:
                    item_dict[acc] = items.items_dict[typ][acc]
            else:
                for key, value in typ_dict.items():
                    item_dict[key] = value
    else:
        item_dict = items.items_dict[buy_choice]
    while True:
        menu.update_itemdict(item_dict, reset_current=False)
        item_str = menu.navigate_items()
        if item_str == "Go Back":
            menu.update_itemdict(None)
            return False if buy_choice not in ["Alchemist", "Jeweler", "Secret"] else True
        buybox = utils.TextBox(game)
        typ, name, adj_cost, _ = [x.strip() for x in list(filter(None, item_str.split('  ')))]
        if int(adj_cost) > game.player_char.gold:
            buybox.print_text_in_rectangle("You do not have enough gold to purchase this item.")
            game.stdscr.getch()
            buybox.clear_rectangle()
        else:
            popup = utils.ShopPopup(game, f"How many {name} do you want to buy?", box_height=7)
            num = popup.navigate_popup()
            total_cost = int(adj_cost) * num
            if int(total_cost) > game.player_char.gold:
                buybox.print_text_in_rectangle("You do not have enough gold to purchase this item.")
                game.stdscr.getch()
                buybox.clear_rectangle()
            elif num > 0:
                item = [x for x in item_dict[typ] if x().name == name][0]()
                buy_popup = utils.ConfirmPopupMenu(
                    game, f"Are you sure you want to buy {num} {name} for {total_cost} gold?", box_height=8)
                if buy_popup.navigate_popup():
                    game.player_char.gold -= int(total_cost)
                    game.player_char.modify_inventory(item, num=num)


def sell(game, menu):

    sellbox = utils.TextBox(game)
    if len(game.player_char.inventory) == 0:
        sellbox.print_text_in_rectangle("You don't have anything to sell.")
        game.stdscr.getch()
        return True
    while True:
        sell_dict = {}
        for name, item in game.player_char.inventory.items():
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
        popup = utils.ShopPopup(game, f"How many {name} do you want to sell?", max=total, box_height=8)
        num = popup.navigate_popup()
        if num > 0:
            adj_cost = int((0.025 * game.player_char.stats.charisma) * num * item.value)
            sell_popup = utils.ConfirmPopupMenu(
                game, f"Do you want to sell {num} {name} for {adj_cost} gold?", box_height=8)
            if sell_popup.navigate_popup():
                game.player_char.gold += int(adj_cost)
                game.player_char.modify_inventory(item, num=num, subtract=True)


def warp_point(game):
    warpbox = utils.TextBox(game)
    warp_message = f"Hello, {game.player_char.name}. Do you want to warp down to level 5?"
    warp_popup = utils.ConfirmPopupMenu(game, warp_message, box_height=8)
    if warp_popup.navigate_popup():
        if not game.player_char.world_dict[(3, 0, 5)].visited:
            game.player_char.world_dict[(3, 0, 5)].visited = True
            game.player_char.world_dict[(2, 0, 5)].near = True
            game.player_char.world_dict[(4, 0, 5)].near = True
            game.player_char.world_dict[(3, 1, 5)].near = True
        message = "You step into the warp point, taking you deep into the dungeon."
        warpbox.print_text_in_rectangle(message)
        game.stdscr.getch()
        game.player_char.world_dict[(3, 0, 5)].warped = True
        game.player_char.change_location(3, 0, 5)
        return True
    message = "Not a problem, come back when you change your mind."
    warpbox.print_text_in_rectangle(message)
    game.stdscr.getch()


def town(game):

    locations = [barracks, tavern, church, blacksmith, alchemist, jeweler]
    town_options = ['Barracks', 'Tavern', 'Church',
                    'Blacksmith', 'Alchemist', 'Jeweler',
                    'Dungeon', 'Character Menu', "Old Warehouse"]
    if game.player_char.warp_point:
        town_options.pop(-1)
        town_options.append("Warp Point")
    game.player_char.health.current = game.player_char.health.max
    game.player_char.mana.current = game.player_char.mana.max
    menu = utils.TownMenu(game, town_options)
    townbox = utils.TextBox(game)
    while True:
        game.player_char.encumbered = game.player_char.current_weight() > game.player_char.max_weight()
        town_idx = menu.navigate_menu()
        if town_options[town_idx] == 'Dungeon':
            townbox.print_text_in_rectangle("You descend into the dungeon.")
            game.player_char.change_location(5, 10, 1)
            game.stdscr.getch()
            break
        if town_options[town_idx] == 'Character Menu':
            game.player_char.character_menu(game)
        elif town_options[town_idx] == 'Old Warehouse':
            townbox.print_text_in_rectangle("Authorized personnel only. Please leave.")
            game.stdscr.getch()
        elif town_options[town_idx] == 'Warp Point':
            if warp_point(game):
                return
        else:
            locations[town_idx](game)
        if game.player_char.quit:
            break


# classes
class BountyBoard:
    def __init__(self):
        self.bounties = []

    def create_bounty(self, game):
        bounty = {"reward": None}
        level = str(min(6, game.player_char.player_level() // 10))
        while True:
            from enemies import random_enemy
            enemy = random_enemy(level)
            if enemy.name not in game.player_char.quest_dict['Bounty'] and \
                enemy.name not in self.bounty_options():
                break
        bounty["enemy"] = enemy
        bounty["num"] = random.randint(3, 8)
        bounty["exp"] = random.randint(enemy.experience*bounty["num"] // 2, enemy.experience*bounty["num"]) * \
            game.player_char.level.pro_level
        bounty["gold"] = random.randint(25*bounty["num"], 50*bounty["num"]) * game.player_char.player_level()
        if random.randint(0, game.player_char.check_mod('luck', luck_factor=10)):
            bounty["reward"] = items.random_item(
                game.player_char.level.pro_level + random.randint(0, game.player_char.level.pro_level))
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


# quest dict
quest_dict = {
    "Barkeep": {
        'Main': {10: 
                 {'The Butcher': 
                   {'Who': 'Barkeep',
                    'Type': 'Defeat',
                    'What': 'Minotaur',
                    'Total': 1,
                    'Start Text':
                        "There is a monster guarding the steps to the first floor, the Minotaur, that is responsible "
                        "for lots of carnage. If you defeat it, I will give you something to help you explore the "
                        "dungeon.",
                    'End Text':
                        "I'm glad to hear you took that butcher out. Here's an item that should help you in any "
                        "future quests.",
                    "Help Text":
                        "If you are having trouble finding the Minotaur, he is located north of the entrance to the "
                        "town.",
                    'Reward': [items.OldKey()],
                    'Reward Number': 1,
                    'Experience': 200,
                    'Completed': False,
                    'Turned In': False}
                    },
                },
        'Side': {1: 
                 {'Rat Trap': 
                   {'Who': 'Barkeep',
                    'Type': 'Collect',
                    'What': items.RatTail(),
                    'Total': 6,
                    'Start Text':
                        "Darn pesky rats keep getting into my food supply and I'd bet anything they come up from that "
                        "dungeon. Help my out by killing as many as you need to collect 6 tails and I'll pay you 600 "
                        "gold.",
                    'End Text':
                        "Good riddance to the bastards, hopefully this will keep my food supplies in good order. "
                        "Here's the gold I promised you.",
                    "Help Text":
                        "Search the area around town on the first floor of the dungeon for those pesky little rat "
                        "vermin.",
                    'Reward': ['Gold'],
                    'Reward Number': 600,
                    'Experience': 100,
                    'Completed': False,
                    'Turned In': False}
                    },
                 40:
                 {'Knock Back a Couple Brewskis': 
                   {'Who': 'Barkeep',
                    'Type': 'Collect',
                    'What': items.CursedHops(),
                    'Total': 3,
                    'Start Text':
                        "My stock of beer is running low and my supplier says the reason is a shortage of the hops"
                        " used to make it. The previous owner of the tavern once told me about a form of hops that"
                        " could be found within the depths. He claimed it makes the most delicious drink you've ever"
                        " tasted. If you could get me a few of them, I'll make sure you are the first to try it "
                        "once it's done brewing. I'll also throw in some gold for your troubles.",
                    'End Text':
                        "I don't believe it, I was sure the old coot was out of his mind with that tale but you "
                        "found them! Come back later and I'll save you a glass. Also here's some gold for your "
                        "troubles.",
                    "Help Text":
                        "Hops can be found growing on certain types of flowering plants. I am not sure how many "
                        "plants you'll find down there...",
                    'Reward': ['Gold'],
                    'Reward Number': 10000,
                    'Experience': 3000,
                    'Completed': False,
                    'Turned In': False}
                    }
                }
    },
    "Waitress": {
        'Main': {35: 
                 {"A Bad Dream": 
                   {'Who': 'Waitress',
                    'Type': 'Locate',
                    'What': "Joffrey",
                    'Total': 1,
                    'Start Text':
                        "This morning I woke in a sweat...I dreamed I was standing in a small room and to my horror a "
                        "great flaming horse struck down my betrothed...please find my Joffrey before my dream truly "
                        "becomes a nightmare...",
                    'End Text':
                        "My pendant...Elysia take me...he left me these keys last I saw of him...please avenge my "
                        "love...(the waitress runs out sobbing...)",
                    "Help Text":
                        "Joffrey was last spotted entering a locked door in the northeast corner on the second floor "
                        "of the dungeon.",
                    'Reward': [items.OldKey()],
                    'Reward Number': 2,
                    'Experience': 3500,
                    'Completed': False,
                    'Turned In': False}
                    }
                },
        'Side': {5: 
                 {"Where's the Beef?": 
                   {'Who': 'Waitress',
                    'Type': 'Collect',
                    'What': items.MysteryMeat(),
                    'Total': 12,
                    'Start Text':
                        "My wedding day is fast approaching and we are trying to save a few gold, so I am cooking "
                        "the meal for the guests. If you could bring me back 12 pieces of mystery meat, I can "
                        "reward you with this potion I received as a tip once.",
                    'End Text':
                        "Thank you, thank you, thank you! You have made my special day that much easier. Please "
                        "take this as a token of my appreciation.",
                    "Help Text":
                        "The wedding guests aren't picky when it comes to the food, so any animal meat will do.",
                    'Reward': [items.GreatHealthPotion()],
                    'Reward Number': 1,
                    'Experience': 150,
                    'Completed': False,
                    'Turned In': False}
                    }
                }

    },
    "Soldier": {
        'Main': {65: 
                 {'No Laughing Matter': 
                   {'Who': 'Soldier',
                    'Type': 'Defeat',
                    'What': 'Jester',
                    'Total': 1,
                    'Start Text':
                        "During my first week of training, a senior officer told us a story about a former recruit"
                        " who went mad. He was a bit of an outcast and many of the other soldiers bullied him for "
                        "his weirdness, as it was told. He had a fondness for card tricks and claimed he was an "
                        "'Agent of Chaos', whatever that means...anyway, he finally cracked one day and "
                        "disappeared, never to be heard from again...that is until we started receiving the body "
                        "parts...the freak has been sending back parts of adventurers with notes talking about "
                        "revenge and signed by the Jester. Someone needs to take this sick bastard out before "
                        "anyone else gets hurt. Be careful, you never truly know what you may get with this guy.",
                    'End Text':
                        "Excellent work! Hopefully the souls of those tortured by the Jester will be able to rest "
                        "now. This magical ring was shipped back with one of the body parts, it increases your "
                        "chance to evade attacks in combat. I'm sure the Jester thought he was being clever, since"
                        " it took so long for someone to finally catch him. It's fitting that you would wear it "
                        "now.",
                    "Help Text":
                        "The Jester has a bag full of tricks. Word is he even has the ability to change his "
                        "resistances each round to keep you on your toes.",
                    'Reward': [items.EvasionRing()],
                    'Reward Number': 1,
                    'Experience': 15000,
                    'Completed': False,
                    'Turned In': False}
                    }
                },
        'Side': {25: 
                 {'Metalingus': 
                   {'Who': 'Soldier',
                    'Type': 'Collect',
                    'What': items.ScrapMetal(),
                    'Total': 8,
                    'Start Text':
                        "The city guard are in desperate need of new equipment but we unfortunately are running short "
                        "on the required materials. If you can bring back 8 pieces of scrap metal, I can use my "
                        "connections with the alchemist shop and get you a really nice potion for your troubles.",
                    'End Text':
                        "You are a life saver, literally. This metal will help to fortify the town against the scum "
                        "that patrols the dungeon. Take one of these potions as a token of my appreciation.",
                    "Help Text":
                        "There are a few sources of metal that would be usable, including broken equipment, metal "
                        "constructs, and enemies that consume items.",
                    'Reward': [items.StrengthPotion(),
                                items.IntelPotion(),
                                items.WisdomPotion(),
                                items.ConPotion(),
                                items.CharismaPotion(),
                                items.DexterityPotion()],
                    'Reward Number': 1,
                    'Experience': 750,
                    'Completed': False,
                    'Turned In': False}
                    }
                }
    },
    "Drunkard": {
        'Main': {35:
                 {"Lapidation": 
                   {'Who': 'Drunkard',
                    'Type': 'Defeat',
                    'What': 'Cockatrice',
                    'Total': 1,
                    'Start Text':
                        "Let me tell you a quick story...back in the day I used to be an adventurer. My friend and I "
                        "had delved too deep into the dungeon below and were trapped with no escape. A giant bird-"
                        "looking monstrosity had us pinned...we made a run for it...but we weren't fast enough. I "
                        "still remember the look on Rutger's face as he turned to stone in front of me...this necklace"
                        " is the only reason I am still here. If you come across the beast, make sure it's dead before"
                        " you are. (hic)...hmmm...what was I sayin'?",
                    'End Text':
                        "Rutger can now be at peace...I can finally let go of the past (hic). Here, take this "
                        "necklace, I don't need it anymore...",
                    "Help Text":
                        "Rutger and I were on the 3rd floor of the dungeon when we encountered the Cockatrice. Make "
                        "sure you prepare for the powerful enemies on your way.",
                    'Reward': [items.GorgonPendant()],
                    'Reward Number': 1,
                    'Experience': 3000,
                    'Completed': False,
                    'Turned In': False}
                    }
                },
        'Side': {18: 
                 {"I'm Molting!": 
                   {'Who': 'Drunkard',
                    'Type': 'Collect',
                    'What': items.SnakeSkin(),
                    'Total': 8,
                    'Start Text':
                        "SNAKES! Oh my I hate those things... (hic) ...slithering about. It's unnatural...I think... "
                        "(hic)...what was I saying?...Oh yeah, bring me some snake skins and I'll give you these "
                        "poison curing thingies I found... (hic)",
                    'End Text':
                        "WHY WOULD YOU BRING...oh yeah I asked you to... (hic) ..thanks I guess. Here's those "
                        "things...ANTIDOTES, that's what they're called. BARKEEP, another beer please... (hic).",
                    "Help Text":
                        "Watch out for the snake's venom, as it can drain your health quickly.",
                    'Reward': [items.Antidote()],
                    'Reward Number': 5,
                    'Experience': 400,
                    'Completed': False,
                    'Turned In': False}
                    }
                }
    },
    "Hooded Figure": {
        'Main': {30:
                 {'Payback': 
                   {'Who': 'Hooded Figure',
                    'Type': 'Defeat',
                    'What': 'Pseudodragon',
                    'Total': 1,
                    'Start Text':
                        "My rival, a wizard known for unimaginable cruelty, is looking to increase her power by "
                        "upgrading her familiar. She has her eyes set on a particular creature, a Pseudodragon, that "
                        "dwells in the dungeon below. Destroy this creature before she can corrupt it and I will "
                        "reward you.",
                    'End Text':
                        "You have done well in taking care of this threat. Take this reward and use it wisely.",
                    "Help Text":
                        "Do not mistake the Pseudodragon's miniature size, for its power is very potent. Beware of the"
                        " deadly Fireball spell, as it can be devastating.",
                    'Reward': [items.Elixir()],
                    'Reward Number': 1,
                    'Experience': 2000,
                    'Completed': False,
                    'Turned In': False}
                    },
                 60:
                 {'Dracarys': 
                   {'Who': 'Hooded Figure',
                    'Type': 'Defeat',
                    'What': 'Red Dragon',
                    'Total': 1,
                    'Start Text':
                        "The depths are home to a powerful Red Dragon. She is not to be taken lightly. If you are "
                        "able to defeat her, the path to glory will be yours.",
                    'End Text':
                        "You have proven yourself worthy for the ultimate challenge...me. Take this as a reminder of "
                        "the futility of being a hero...there will always be another evil to deal with and that evil "
                        "will always pale in comparison to my wrath. Pursue me at your own peril.",
                    "Help Text":
                        "The Red Dragon is your toughest test yet, having access to some of the strongest abilities.",
                    'Reward': [items.ClassRing()],
                    'Reward Number': 1,
                    'Experience': 25000,
                    'Completed': False,
                    'Turned In': False}
                    }
                },
        'Side':{1:
                 {"Pandora's Box":
                   {'Who': "Hooded Figure",
                    'Type': "Collect",
                    'What': items.Phylactery(),
                    'Total': 1,
                    'Start Text':
                        "Oh impressive, you have obtained the powerful Ultima spell. Interested in making it more "
                        "powerful? Of course you are, who wouldn't? Bring me the soul of a Lich and I will create an "
                        "item on a scale hitherto undreamt of.",
                    'End Text':
                        "What a wonderful specimen you have brought me, this will do well in the ritual...oh right, "
                        "here's that item I promised you.",
                    "Help Text":
                        "A Lich is a powerful foe, do not underestimate them!",
                    'Reward': [items.UltimaScepter()],
                    'Reward Number': 1,
                    'Experience': 30000,
                    'Completed': False,
                    'Turned In': False}
                    }
                }
    },
    "Griswold": {
        'Main': {},
        'Side': {15:
                 {'Eight Is Enough': 
                   {'Who': 'Griswold',
                    'Type': 'Collect',
                    'What': items.Leather(),
                    'Total': 8,
                    'Start Text':
                        "The thieves guild has placed an order for several sets of leather armor but my supply of "
                        "materials is getting short at the moment. Say, you look capable enough, do you think you "
                        "could retrieve some for me? I'll pay top dollar for them.",
                    'End Text':
                        "I knew it when I first saw you that you were the person for the job. As promised here's some "
                        "gold for your efforts.",
                    "Help Text":
                        "I am able to fashion leather armor out of either fresh animal hides or by using scraps from "
                        "old armor pieces.",
                    'Reward': ['Gold'],
                    'Reward Number': 2500,
                    'Experience': 250,
                    'Completed': False,
                    'Turned In': False}
                    },
                 60: 
                 {"This Thing's Nuclear": 
                   {'Who': 'Griswold',
                    'Type': 'Collect',
                    'What': items.PowerCore(),
                    'Total': 1,
                    'Start Text':
                        "I came across an old dusty tome while cleaning out the belongings of my mentor. Most of it "
                        "contained random armor designs but there was a loose piece of parchment that contained a "
                        "blueprint for a way to increase a person's defensive prowess, however it requires some hard "
                        "to find items. The hardest to come by is a nuclear power core, which sounds fake and may "
                        "actually be, who knows? If by some miracle you find one, bring it to me and you will reap the"
                        " benefit.",
                    'End Text':
                        "So a power core is the secret to creating golems? This bit of information may prove to be "
                        "more valuable than any thing I could give you. I do have an idea though. There may be a way "
                        "to harness the power into you. If you're up for it of course. Step into the back and we will "
                        "start the process.",
                    "Help Text":
                        "I met an old wizard at the tavern who mentioned that power cores do indeed exist. I don't "
                        "know how he knows this but he seems pretty credible. Maybe they are used to power something "
                        "of incredible size?",
                    'Reward': ['Power Up'],
                    'Reward Number': 1,
                    'Experience': 5000,
                    'Completed': False,
                    'Turned In': False}
                    },
                 70:
                 {"He Ain't Heavy": 
                   {'Who': 'Griswold',
                    'Type': 'Locate',
                    'Total': 1,
                    'Start Text':
                        "I am so glad you stopped in, I really need your help. My baby brother, Chisolm, has been "
                        "missing for far too long. He regularly goes into the dungeon but never for this long. Please "
                        "help me find him and I will forever be indebted to you.",
                    'End Text':
                        "By the light of Elysia, you have found him! I must admit I had given up hope. It comes at no "
                        "surprise that he chose to stay in the depths to help those in need, perhaps he will choose to"
                        " come home once the primal evil has been vanquished.",
                    "Help Text":
                        "I haven't the faintest idea where Chisolm may be but he is a strong warrior and I have no "
                        "doubt he is still alive. I have heard rumors of secret passageways in the depths but they "
                        "have never been confirmed.",
                    'Reward': ["Upgrade"],
                    'Reward Number': 1,
                    'Experience': 20000,
                    'Completed': False,
                    'Turned In': False}
                    }
                }
    },
    "Alchemist": {
        'Main': {},
        'Side': {20:
                 {'Put A Feather In It':
                   {'Who': 'Alchemist',
                    'Type': 'Collect',
                    'What': items.Feather(),
                    'Total': 12,
                    'Start Text':
                        "As you may or may not know, all of my tinctures are created here in my lab. I need some more "
                        "ingredients to make more Phoenix Down potions, so any Feathers that you find I will pay you "
                        "for them.",
                    'End Text':
                        "Excellent! Here's the gold I promised, spend it wisely.",
                    "Help Text":
                        "Birds have feathers, so try killing some birds. You may also find them on other enemies, as "
                        "bird is a favorite dish to eat.",
                    'Reward': ['Gold'],
                    'Reward Number': 4000,
                    'Experience': 500,
                    'Completed': False,
                    'Turned In': False}
                    }
                }
    },
    "Jeweler": {
        'Main': {},
        'Side': {50:
                 {'Earth, Wind, and Fire...and Water and...': 
                   {'Who': 'Jeweler',
                    'Type': 'Collect',
                    'What': items.ElementalMote(),
                    'Total': 6,
                    'Start Text':
                        "Long before I owned this shop, I was apprentice to a master craftsman. He taught me how to "
                        "make a very powerful item called an Elemental Amulet, which requires the core of 6 "
                        "elementals. However I have never been able to make this item since I was never able to "
                        "obtain the components. Bring me the 6 Elemental Motes and the pendant will be yours.",
                    'End Text':
                        "Absolutely amazing, I doubted if I would ever be able to put this skill to the test. Please "
                        "wait a moment while I place these motes into the amulet...here you go, I hope it serves you "
                        "well!",
                    "Help Text":
                        "The elemental beasts known as Myrmidons come in many variations. Unfortunately the only way "
                        "to know what type you are fighting is to see what elements work or don't work against them.",
                    'Reward': [items.ElementalAmulet()],
                    'Reward Number': 1,
                    'Experience': 6000,
                    'Completed': False,
                    'Turned In': False}
                    }
                }
    },
    "Priest": {
        'Main': {45:
                 {'The Power of Elysia Compels You!': 
                   {'Who': 'Priest',
                    'Type': 'Defeat',
                    'What': 'Wendigo',
                    'Total': 1,
                    'Start Text':
                        "While the depths of the dungeon are home to many a horrible creature, the Wendigo is a curse "
                        "to our very soul. Vanquish this monstrosity and Elysia will reward you with a boon.",
                    'End Text':
                        "Some order has been restored, although more work is to be done. Take this gift and use it to "
                        "continue the good fight.",
                    "Help Text":
                        "As with many creatures of the night, your best option for cleansing the world of the Wendigo "
                        "is Fire. Stay away from using Ice magic.",
                    'Reward': [items.AardBeing()],
                    'Reward Number': 1,
                    'Experience': 6000,
                    'Completed': False,
                    'Turned In': False}
                    }
                },
        'Side': {}
    },
    "Sergeant": {
        'Main': {1:
                 {'The Holy Relics': 
                   {'Who': 'Sergeant',
                    'Type': 'Collect',
                    'What': 'Relics',
                    'Total': 6,
                    'Start Text':
                        "So you think you have what it takes, huh? Some of my best men have died in that dungeon and "
                        "here you are, barely old enough to wipe your own ass...very well, it's your funeral. Maybe "
                        "you have something those men didn't have. We don't have all the details but we believe the "
                        "key to vanquishing the prime evil is to collect all 6 of the holy relics. Do that and you "
                        "might just stand a chance. Don't blame me for not holding my breath...",
                    'End Text':
                        "Well I'll be, you crazy son of a bitch, you did it!...I shouldn't get to excited, there's "
                        "still work to be done. But this is huge! Hopefully one of these will help in your quest to "
                        "destroy what plagues this town.",
                    "Help Text":
                        "Each relic is protected by a powerful creature. Only the most determined champions will "
                        "succeed in this quest.",
                    'Reward': [items.MedusaShield(), items.Magus(), items.RainbowRod(), items.AardBeing()],
                    'Reward Number': 1,
                    'Experience': 500000,
                    'Completed': False,
                    'Turned In': False}
                    },
                 20: 
                 {'Cry Havoc!':
                   {'Who': 'Sergeant',
                    'Type': 'Defeat',
                    'What': 'Barghest',
                    'Total': 1,
                    'Start Text':
                        "We believe we've identified where the first relic is but it's guarded by a nasty, dog-like "
                        "beast, a Barghest. This thing can shapeshift and can be fairly nasty if you are not prepared."
                        " Destroy it and find the first of the 6 relics. I'll have something for you when you return.",
                    'End Text':
                        "Glad to hear you took care of that beast, soldier. Take this ring, it will make your physical"
                        " attacks more powerful.",
                    "Help Text":
                        "The Barghest has 3 forms: a Goblin, a Direwolf, and its natural hybrid form.",
                    'Reward': [items.PowerRing()],
                    'Reward Number': 1,
                    'Experience': 500,
                    'Completed': False,
                    'Turned In': False}
                    },
                 50:
                 {'Immovable Object':
                   {'Who': 'Sergeant',
                    'Type': 'Defeat',
                    'What': 'Iron Golem',
                    'Total': 1,
                    'Start Text':
                        "Only a powerful wizard is capable of creating a golem and a truly powerful wizard must have "
                        "created the Iron Golem. While we do not know who created this monstrosity, the fact is you "
                        "will not be able to get to the 5th floor without taking it out.",
                    'End Text':
                        "I shouldn't be surprised at this point but again you've done what was thought impossible. "
                        "Choose your reward and good luck going forward, although it doesn't seem that you need much "
                        "luck...",
                    "Help Text":
                        "Do not let the Iron Golem get its hands on you, as it will literally crush you to oblivion.",
                    'Reward': [items.DiamondAmulet(), items.PlatinumPendant()],
                    'Reward Number': 1,
                    'Experience': 20000,
                    'Completed': False,
                    'Turned In': False}
                    },
                 60: 
                 {'In the Day of Our Lord': 
                   {'Who': 'Sergeant',
                    'Type': 'Defeat',
                    'What': 'Domingo',
                    'Total': 1,
                    'Start Text':
                        "Many years ago, an explorer returned with a magical egg that was said to contain a powerful "
                        "creature. Our scientists made many attempts to hatch the creature but were unsuccessful until"
                        " recently when they had a breakthrough when they simple placed it in our chicken incubator. "
                        "We had hoped to use this creature to protect the city from the monsters below but found out "
                        "quickly that we could not hope to control it and had locked it away. However, someone "
                        "inexplicably let the creature out. It killed 6 of my men before it disappeared into the "
                        "dungeon. Find the creature and destroy it.",
                    'End Text':
                        "It's a shame we had to kill it but there is no point trying to control the uncontrollable. "
                        "The head scientist sends his thanks and as a reward, they have finished construction of a "
                        "warp point that will allow you to teleport directly to the 5th dungeon level.",
                    "Help Text":
                        "The magical creature excels at, you guessed it, magic. Look out for the powerful Ultima spell"
                        " that it will undoubtably spam each turn.",
                    'Reward': ["Warp Point"],
                    'Reward Number': 1,
                    'Experience': 50000,
                    'Completed': False,
                    'Turned In': False}
                    },
                },
        'Side': {3: 
                 {'Bring Him Home': 
                   {'Who': 'Sergeant',
                    'Type': 'Locate',
                    'What': 'Timmy',
                    'Total': 1,
                    'Start Text':
                        "We received a report about a small child named Timmy who somehow made it past my guards and "
                        "into the dungeon. While my men have been punished accordingly, we still need to find the boy "
                        "before something bad happens to him. Locate him (he shouldn't have gone far) and bring him "
                        "home to his family.",
                    'End Text':
                        "You've found the boy, that's excellent news! I'm sure the family is very relieved. Here are "
                        "some health potions to keep you alive as you explore.",
                    "Help Text":
                        "That kid must be an expert at hide-and-seek. I have sent several sentries to find him and "
                        "haven't seen a trace. I guess there is an alternate outcome...let's not think that way.",
                    'Reward': [items.HealthPotion()],
                    'Reward Number': 5,
                    'Experience': 150,
                    'Completed': False,
                    'Turned In': False}
                    }
                }
    },
    "Busboy": {
        "Main": {},
        "Side": {1: 
                 {'Something to Cry About':
                   {'Who': 'Busboy',
                    'Type': 'Locate',
                    'What': 'Waitress',
                    'Total': 1,
                    'Start Text':
                        "Oh man, I am so screwed...do you think you can help me? I let the waitress borrow my key to "
                        "the tavern and the boss is gonna kill me if I don't get it back. Could you try and track her "
                        "down for me and get the key back? This may be a long shot but I am desperate. People are "
                        "saying she went crazy after her fiance died and she took off into the dungeon and hasn't been"
                        " seen since. I know this sounds a bit heartless after what she's been through but she made "
                        "her choice and now I have to pay for it. I don't have much but I can give you this potion my "
                        "mom keeps on her mantle. She claims it makes her live longer but who knows whether that's "
                        "true or not.",
                    'End Text':
                        "So she really did go crazy. It's sad what grief will do to a person...thanks for tracking"
                        " her down but it turns out she left the tavern key in my locker before she left. Whatever"
                        " this key is, it's not mine. You can keep it, maybe it'll unlock something useful. Here's "
                        "that potion I promised you.",
                    "Help Text":
                        "Adventurers have told stories of hearing wailing on the second floor of the dungeon that"
                        " sounds like a woman crying.",
                    'Reward': [items.HPPotion()],
                    'Reward Number': 1,
                    'Experience': 5000,
                    'Completed': False,
                    'Turned In': False}
                    }
                }
    }
}
