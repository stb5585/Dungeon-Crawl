###########################################
""" Town manager """

# Imports
import os
import random
import time

import enemies
import items
import storyline
import classes


# Functions
def player_level(player_char):
    return player_char.level + (30 * (player_char.pro_level - 1))


def turn_in_quest(quest, player_char, typ):
    """

    """

    os.system('cls' if os.name == 'nt' else 'clear')
    print('{}: '.format(player_char.quest_dict[typ][quest]['Who']) + player_char.quest_dict[typ][quest]['End Text'])
    player_char.quest_dict[typ][quest]['Turned In'] = True
    reward = player_char.quest_dict[typ][quest]['Reward']
    if len(reward) == 1:
        reward = reward[0]
    else:
        print("Choose your reward")
        rewards = [x().name for x in reward]
        choice = storyline.get_response(rewards)
        reward = reward[choice]
    exp = player_char.quest_dict[typ][quest]['Experience']
    if player_char.quest_dict[typ][quest]['Reward'][0] == 'Gold':
        player_char.gold += player_char.quest_dict[typ][quest]['Reward Number']
        print("You received {} gold and {} experience.".format(
            player_char.quest_dict[typ][quest]['Reward Number'], exp))
    else:
        num = player_char.quest_dict[typ][quest]['Reward Number']
        player_char.modify_inventory(reward, num=num)
        if num == 1:
            print("You received {} and {} experience.".format(reward().name, exp))
        else:
            print("You received {} x{} and {} experience.".format(reward().name, num, exp))
    player_char.experience += exp
    while player_char.experience >= player_char.exp_to_gain:
        player_char.level_up()
    if player_char.quest_dict[typ][quest]['Type'] == 'Collect':
        item = player_char.inventory[quest][0]
        player_char.modify_inventory(item, num=player_char.quest_dict[typ][quest]['Total'], subtract=True)
    input("Press enter to continue")


def accept_quest(quest, player_char, typ):
    """

    """

    os.system('cls' if os.name == 'nt' else 'clear')
    response_map = {'Barkeep': ["Great, come back to me when it is completed.",
                                "That's a shame, come back if you change your mind."],
                    'Waitress': ["Oh, that's truly wonderful! I'll be waiting to hear from you.",
                                 "I understand, it was stupid of me to even ask..."],
                    'Soldier': ["Excellent, your efforts will not go unnoticed.",
                                "Do not waste my time if you are not dedicated to the cause."],
                    'Drunkard': ["Well fine then, go...wait, oh you said yes...(hic) well thanks! I'll be right here, "
                                 "as always...(hic)",
                                 "Oh I see, your time (hic) is too precious, huh?"],
                    'Hooded Figure': ["Splendid, I will await your return.",
                                      "Pity, you showed so much promise. Be gone then..."],
                    'Griswold': ["Please hurry, I do not know how long he has left...",
                                 "Accept or not, at least keep an eye out..."],
                    'Armorer': ["Finally someone with some stones! I knew I liked you!",
                                "Too bad..."],
                    'Alchemist': ["Our arrangement will be mutually beneficial, you will see.",
                                  "It's a shame you deny me this request."],
                    'Jeweler': ["You will not be disappointed!",
                                "Not sure of your reasoning but fair enough."],
                    'Priest': ["The light of Elysia will guide your efforts.",
                               "Patience is a virtue I hold sacred. I will wait as long as I need."]
                    }
    yes_no = ['Yes', 'No']
    key = list(quest.keys())[0]
    who = quest[key]['Who']
    print("{}: ".format(who) + quest[key]['Start Text'])
    print("Do you accept this quest?")
    main_input = storyline.get_response(yes_no)
    if yes_no[main_input] == 'Yes':
        player_char.quest_dict[typ][key] = quest[key]
        print(response_map[who][0])
        if quest[key]['Type'] == 'Defeat':
            if key in list(player_char.kill_dict.keys()):
                player_char.quest_dict[typ][key]['Completed'] = True
        elif quest[key]['Type'] == 'Collect':
            if key in list(player_char.inventory.keys()):
                if player_char.inventory[key][1] >= player_char.quest_dict[typ][key]['Total']:
                    player_char.quest_dict[typ][key]['Completed'] = True
        else:
            print("You shouldn't be here.")
            raise BaseException
        return True
    else:
        print(response_map[who][1])
    input("Press enter to continue")
    return False


def tavern_patrons(player_char):
    """
    Various patrons/employees that frequent the tavern
    3 possible conversations: Talk (tip or hint), Main Quest (directly related to game completion), or Side Quest
    Barkeep (level 1)
      Talk:
      Main: defeat Minotaur, level 10, rewards Old Key
      Side: return 6 Rat Tails, level 1, rewards 600 gold and 100 exp
    Waitress (level 1)
      Talk:
      Main:
      Side: return 12 Mystery Meat, level 5, rewards Super Health Potion and 150 exp
    Soldier (level 15)
      Talk:
      Main:
      Side: return 10 Scrap Metal, level 25, rewards a stat potion of the player' choice
    Drunkard (level 30)
      Talk:
      Main:
      Side: return 8 Snake Skins, level 18, rewards 5 antidotes
    Hooded Figure (level 40)
      Talk:
      Main: defeat Red Dragon, level 60, reward Class Ring and 15000 exp
      Side:
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    p_level = player_level(player_char)
    player_mains = list(player_char.quest_dict['Main'].keys())
    player_sides = list(player_char.quest_dict['Side'].keys())
    patrons = {'Barkeep': {'Talk': {1: ["If you want to access the character menu, you can do so by hitting the (c) "
                                        "button.",
                                        "Make sure to stop by from time to time. You never know who might show up."],
                                    10: ["You have to be level 20 to get a promotion but you can gain more experience"
                                         " if you wait until level 30.",
                                         "Locked chests contain more powerful items compared with unlocked ones, "
                                         "however you need a key or a lockpick to get to the treasure."]
                                    },
                           'Main': {10: {'Minotaur': {'Who': 'Barkeep',
                                                      'Type': 'Defeat',
                                                      'Total': 1,
                                                      'Start Text': "There is a monster guarding the steps to the first"
                                                                    " floor, the Minotaur, that is responsible for lots"
                                                                    " of carnage. If you defeat it, I will give you "
                                                                    "something to help you explore the dungeon.",
                                                      'End Text': "I'm glad to hear you took that butcher out. Here's "
                                                                  "an item that should help you in your quest.",
                                                      'Reward': [items.OldKey],
                                                      'Reward Number': 1,
                                                      'Experience': 200,
                                                      'Completed': False,
                                                      'Turned In': False}
                                         }
                                    },
                           'Side': {1: {'Rat Tail': {'Who': 'Barkeep',
                                                     'Type': 'Collect',
                                                     'Total': 6,
                                                     'Start Text': "Darn pesky rats keep getting into my food supply "
                                                                   "and I'd bet anything they come up from that "
                                                                   "dungeon. Help my out by killing as many as you need"
                                                                   " to collect 6 tails and I'll pay you 600 gold.",
                                                     'End Text': "Good riddance to the bastards, hopefully this will "
                                                                 "keep my food supplies in good order. Here's the gold "
                                                                 "I promised you.",
                                                     'Reward': ['Gold'],
                                                     'Reward Number': 600,
                                                     'Experience': 100,
                                                     'Completed': False,
                                                     'Turned In': False}
                                        }
                                    }
                           },
               'Waitress': {'Talk': {1: ["Entering the town will replenish your health and mana. Seems like you could "
                                         "take advantage of that."]
                                     },
                            'Main': {},
                            'Side': {5: {'Mystery Meat': {'Who': 'Waitress',
                                                          'Type': 'Collect',
                                                          'Total': 12,
                                                          'Start Text': "I am getting married and we are trying to save"
                                                                        " a few gold, so I am cooking the meal for the "
                                                                        "guests. If you could bring me back 12 pieces "
                                                                        "of mystery meat, I can reward you with this "
                                                                        "potion I received as a tip once.",
                                                          'End Text': "Thank you, thank you, thank you! You have made "
                                                                      "my special day that much easier. Please take "
                                                                      "this as a token of my appreciation.",
                                                          'Reward': [items.SuperHealthPotion],
                                                          'Reward Number': 1,
                                                          'Experience': 150,
                                                          'Completed': False,
                                                          'Turned In': False}
                                         }
                                     }
                            },
               'Soldier': {'Talk': {10: ["You may find locked doors along your path while exploring the dungeon. You "
                                         "can't open these with just any old key, you need an actual Old Key."],
                                    65: ["The Devil is immune to normal weapons but legend says there is a "
                                         "material that will do the job."]
                                    },
                           'Main': {},
                           'Side': {25: {'Scrap Metal': {'Who': 'Soldier',
                                                         'Type': 'Collect',
                                                         'Total': 10,
                                                         'Start Text': "The city guard are in desperate need of new "
                                                                       "equipment but we unfortunately are running "
                                                                       "short on the required materials. If you can "
                                                                       "bring back 10 pieces of scrap metal, I can use "
                                                                       "my connections with the alchemist shop and get "
                                                                       "you a really nice potion for your troubles.",
                                                         'End Text': "You are a life saver, literally. This metal will "
                                                                     "help to fortify the town against the scum that "
                                                                     "patrols the dungeon. Here is a token of my "
                                                                     "appreciation.",
                                                         'Reward': [items.StrengthPotion, items.IntelPotion,
                                                                    items.WisdomPotion, items.ConPotion,
                                                                    items.CharismaPotion, items.DexterityPotion],
                                                         'Reward Number': 1,
                                                         'Experience': 750,
                                                         'Completed': False,
                                                         'Turned In': False}
                                         }
                                    }
                           },
               'Drunkard': {'Talk': {8: ["(hic)...I am not as think as you drunk I am...(hic)"],
                                     30: ["(hic)...I heard tell there were secret passages...(hic) in the dungeon."]
                                     },
                            'Main': {},
                            'Side': {18: {'Snake Skin': {'Who': 'Drunkard',
                                                         'Type': 'Collect',
                                                         'Total': 8,
                                                         'Start Text': "SNAKES! Oh my I hate those things...(hic)... "
                                                                       "slithering about. It's unnatural...I think..."
                                                                       "(hic)...what was I saying?...Oh yeah, bring me "
                                                                       "some snake skins and I'll give you these "
                                                                       "poison curing thingies I found...(hic)",
                                                         'End Text': "WHY WOULD YOU BRING...oh yeah I asked you to..."
                                                                     "(hic)..thanks I guess. Here's those things..."
                                                                     "ANTIDOTES, that's what they're called. BARKEEP, "
                                                                     "another beer please...(hic).",
                                                         'Reward': [items.Antidote],
                                                         'Reward Number': 5,
                                                         'Experience': 400,
                                                         'Completed': False,
                                                         'Turned In': False}
                                          }
                                     }
                            },
               'Hooded Figure': {'Talk': {25: ["..."],
                                          50: ["Your power has grown...I am impressed."],
                                          60: ["Have you defeated the Red Dragon yet?"],
                                          },
                                 'Main': {60: {'Red Dragon': {'Who': 'Hooded Figure',
                                                              'Type': 'Defeat',
                                                              'Total': 1,
                                                              'Start Text': "The depths are home to a powerful Red "
                                                                            "Dragon. She is not to be taken lightly, "
                                                                            "however if you are able to defeat her, "
                                                                            "the path to glory will be yours.",
                                                              'End Text': "You have proven yourself worthy for the "
                                                                          "ultimate challenge...me. Take this as a "
                                                                          "reminder of the futility of being a hero..."
                                                                          "there will always be another evil to deal "
                                                                          "with and that evil will always pale in "
                                                                          "comparison to my wrath. Pursue me at your "
                                                                          "own peril.",
                                                              'Reward': items.ClassRing,
                                                              'Reward Number': 1,
                                                              'Experience': 15000,
                                                              'Completed': False,
                                                              'Turned In': False}
                                               }
                                          },
                                 'Side': {}}
               }
    options = ["Barkeep", "Waitress"]
    if p_level >= 8:
        options.append("Drunkard")
        if p_level >= 10:
            options.append("Soldier")
            if p_level >= 25:
                if 'Red Dragon' in player_char.quest_dict['Main']:
                    if not player_char.quest_dict['Main']['Red Dragon']['Turned In']:
                        options.append("Hooded Figure")
                else:
                    options.append("Hooded Figure")
    print("Who would you like to talk with?")
    option_input = storyline.get_response(options)
    mains = patrons[options[option_input]]['Main']
    main_quests = [mains[x] for x in mains if p_level >= x]
    sides = patrons[options[option_input]]['Side']
    side_quests = [sides[x] for x in sides if p_level >= x]
    quest = False
    if len(main_quests) > 0:
        for main_quest in main_quests:
            key = list(main_quest.keys())[0]
            if key in player_mains:
                if player_char.quest_dict['Main'][key]['Completed'] and \
                        not player_char.quest_dict['Main'][key]['Turned In']:
                    turn_in_quest(key, player_char, "Main")
                    quest = True
            else:
                quest = accept_quest(main_quest, player_char, "Main")
            if quest:
                break
    elif len(side_quests) > 0:
        for side_quest in side_quests:
            key = list(side_quest.keys())[0]
            if key in player_sides:
                if player_char.quest_dict['Side'][key]['Completed'] and \
                        not player_char.quest_dict['Side'][key]['Turned In']:
                    turn_in_quest(key, player_char, "Side")
                    quest = True
            else:
                quest = accept_quest(side_quest, player_char, "Side")
            if quest:
                break
    if not quest:
        talks = patrons[options[option_input]]['Talk']
        level_talks = [talks[x] for x in talks if p_level >= x][0]
        print(random.choice(level_talks))
    time.sleep(1)


def ultimate(player_char):
    texts = [
        "Oh my...can it possibly be?...the legendary ore...Unobtainium?\n",
        "I can\'t believe you have found it!\n",
        "It has been a lifelong dream of mine to forge a weapon from the mythical metal.\n"
    ]
    for text in texts:
        storyline.slow_type(text)
        time.sleep(0.5)
    weapon_list = {'Dagger': items.Carnwennan,
                   'Sword': items.Excalibur,
                   'Mace': items.Mjolnir,
                   'Fist': items.GodsHand,
                   'Axe': items.Jarnbjorn,
                   'Polearm': items.Gungnir,
                   'Staff': [items.PrincessGuard, items.DragonStaff],
                   'Hammer': items.Skullcrusher,
                   'Ninja Blade': items.Ninjato}
    make_list = []
    i = 0
    for typ, weapon in weapon_list.items():
        if typ == 'Staff':
            if 'Archbishop' == player_char.cls:
                weapon = weapon[0]
            else:
                weapon = weapon[1]
        if classes.equip_check(weapon, 'Weapon', player_char.cls):
            make_list.append(typ)
            i += 1
    make_list.append('Not Yet')
    while True:
        print('What type of weapon would you like me to make?')
        weapon_ind = storyline.get_response(make_list)
        break
    if make_list[weapon_ind][0] == 'Not yet':
        print("I am sorry to hear that...please come back if you change your mind.")
    else:
        weapon = weapon_list[make_list[weapon_ind]]
        if type(weapon) == list:
            if 'Archbishop' == player_char.cls:
                weapon = weapon[0]
            else:
                weapon = weapon[1]
        print("Give me a moment and I will make you an ultimate weapon...")
        time.sleep(5)
        print("I present to you, {}, the mighty {}!".format(player_char.name, weapon().name))
        player_char.modify_inventory(weapon, num=1)
        del player_char.inventory['Unobtainium']
        if 'Chisolm' in list(player_char.quest_dict['Side'].keys()):
            if player_char.quest_dict['Side']['Chisolm']['Turned In']:
                print("I still have a bit of ore left if you want me to upgrade another weapon or I may even be able to"
                      " improve the one I just made.")
    time.sleep(2)


def blacksmith(player_char):
    """
    Griswold's shop - sells weapons and offhand items
    At level 60 (level 30 first promotion or level 1 second promotion), you will receive a quest to find Griswold's
      brother, Chisolm; completing this quest, along with finding the unobtainium, will allow Griswold to either upgrade
      another weapon to ultimate status (for dual wielding) or improve an existing one further
    Once Unobtainium is found, Griswold will craft an ultimate weapon
    """

    p_level = player_level(player_char)
    chisolm_quest = {'Chisolm': {'Who': 'Griswold',
                                 'Type': 'Locate',
                                 'Total': 1,
                                 'Start Text': "I am so glad you stopped in, I really need your help. My baby "
                                               "brother, Chisolm, has been missing for far too long. He regularly "
                                               "goes into the dungeon but never for this long. Please help me find "
                                               "him and I will forever be indebted to you.",
                                 'End Text': "By the light of Elysia, you have found him! I must admit I had given "
                                             "up hope. It comes at no surprise that he chose to stay in the depths "
                                             "to help those in need, perhaps he will choose to come home once the "
                                             "primal evil has been vanquished.",
                                 'Reward': "Upgrade",
                                 'Reward Number': 1,
                                 'Experience': 20000,
                                 'Completed': False,
                                 'Turned In': False}
                     }
    if player_char.world_dict[(9, 1, 6)].visited and 'Chisolm' not in list(player_char.quest_dict['Side'].keys()):
        player_char.quest_dict['Side']['Chisolm'] = chisolm_quest['Chisolm']
        player_char.quest_dict['Side']['Chisolm']['Completed'] = True
    if 'Chisolm' in list(player_char.quest_dict['Side'].keys()):
        if player_char.quest_dict['Side']['Chisolm']['Completed'] and \
                not player_char.quest_dict['Side']['Chisolm']['Turned In']:
            turn_in_quest('Chisolm', player_char, 'Side')
    elif p_level >= 60 and not player_char.world_dict[(9, 1, 6)].visited:
        # still need to handle the reward TODO
        accept_quest(chisolm_quest, player_char, 'Side')
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        if 'Unobtainium' in list(player_char.special_inventory.keys()):
            ultimate(player_char)
        print("Welcome to Griswold's! What can I do you for?")
        time.sleep(0.5)
        buy_list = ['Weapon', 'OffHand', 'Go Back']
        print("You have {} gold.".format(player_char.gold))
        print("Did you want to buy or sell?")
        option_list = ['Buy', 'Sell', 'Leave']
        opt_index = storyline.get_response(option_list)
        if option_list[opt_index] == 'Leave':
            print("We're sorry to see you go. Come back anytime!")
            time.sleep(1)
            return
        else:
            if option_list[opt_index] == 'Buy':
                buy(player_char, buy_list)
            elif option_list[opt_index] == 'Sell':
                sell(player_char)
            else:
                print("Something went wrong.")
                return


def armory(player_char):
    """
    Armorer - sells all types of armor
    At level 15, gives quest to collect 12 Leathers
    """

    p_level = player_level(player_char)
    if 'Leather' in list(player_char.quest_dict['Side'].keys()):
        if player_char.quest_dict['Side']['Leather']['Completed'] and \
                not player_char.quest_dict['Side']['Leather']['Turned In']:
            turn_in_quest('Leather', player_char, 'Side')
    elif p_level >= 15:
        pelt_quest = {'Leather': {'Who': 'Armorer',
                                  'Type': 'Collect',
                                  'Total': 8,
                                  'Start Text': "The thieves guild has placed an order for several sets of leather "
                                                "armor but my supply is getting short at the moment. Say, you look "
                                                "capable enough, do you think you could retrieve some for me? I'll pay "
                                                "top dollar for them.",
                                  'End Text': "I knew it when I first saw you that you were the person for the job. "
                                              "As promised here's some gold for your efforts.",
                                  'Reward': ['Gold'],
                                  'Reward Number': 2500,
                                  'Experience': 250,
                                  'Completed': False,
                                  'Turned In': False}
                      }
        accept_quest(pelt_quest, player_char, 'Side')
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("I have the finest armors for sale. Come in and look around.")
        time.sleep(0.5)
        buy_list = ['Armor', 'Go Back']
        print("You have {} gold.".format(player_char.gold))
        print("Did you want to buy or sell?")
        option_list = ['Buy', 'Sell', 'Leave']
        opt_index = storyline.get_response(option_list)
        if option_list[opt_index] == 'Leave':
            print("We're sorry to see you go. Come back anytime!")
            time.sleep(1)
            return
        else:
            if option_list[opt_index] == 'Buy':
                buy(player_char, buy_list)
            elif option_list[opt_index] == 'Sell':
                sell(player_char)
            else:
                print("Something went wrong.")
                return


def alchemist(player_char):
    """
    Alchemist - sells potions and other miscellaneous items (scrolls, keys, etc.)
    At level 20, gives quest for collecting 15 Feathers
    """

    p_level = player_level(player_char)
    if 'Feather' in list(player_char.quest_dict['Side'].keys()):
        if player_char.quest_dict['Side']['Feather']['Completed'] and \
                not player_char.quest_dict['Side']['Feather']['Turned In']:
            turn_in_quest('Feather', player_char, 'Side')
    elif p_level >= 20:
        pelt_quest = {'Feather': {'Who': 'Alchemist',
                                  'Type': 'Collect',
                                  'Total': 12,
                                  'Start Text': "As you may or may not know, all of my tinctures are created here in my"
                                                " lab. I need some more ingredients to make more Phoenix Down potions, "
                                                "so any Feathers that you find I will pay you for them.",
                                  'End Text': "Excellent! Here's the gold I promised, spend it wisely.",
                                  'Reward': ['Gold'],
                                  'Reward Number': 2500,
                                  'Experience': 250,
                                  'Completed': False,
                                  'Turned In': False}
                      }
        accept_quest(pelt_quest, player_char, 'Side')
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Welcome to Ye Olde Item Shoppe.")
        time.sleep(0.5)
        buy_list = ['Potion', 'Misc', 'Go Back']
        print("You have {} gold.".format(player_char.gold))
        print("Did you want to buy or sell?")
        option_list = ['Buy', 'Sell', 'Leave']
        opt_index = storyline.get_response(option_list)
        if option_list[opt_index] == 'Leave':
            print("We're sorry to see you go. Come back anytime!")
            time.sleep(1)
            return
        else:
            if option_list[opt_index] == 'Buy':
                buy(player_char, buy_list)
            elif option_list[opt_index] == 'Sell':
                sell(player_char)
            else:
                print("Something went wrong.")
                return


def jeweler(player_char):
    """
    Jewelry shop - sells Pendants and Rings
    At level 55, gives quest to collect 6 elemental motes, rewards Elemental Amulet
    """

    p_level = player_level(player_char)
    if 'Elemental Mote' in list(player_char.quest_dict['Side'].keys()):
        if player_char.quest_dict['Side']['Elemental Mote']['Completed'] and \
                not player_char.quest_dict['Side']['Elemental Mote']['Turned In']:
            turn_in_quest('Elemental Mote', player_char, 'Side')
    elif p_level >= 55:
        myr_quest = {'Elemental Mote': {'Who': 'Jeweler',
                                        'Type': 'Collect',
                                        'Total': 6,
                                        'Start Text': "Long before I owned this shop, I was apprentice to a master "
                                                      "craftsman. He taught me how to make a very powerful item called "
                                                      "an Elemental Amulet, which requires the core of 6 elementals. "
                                                      "However I have never been able to make this item since I was "
                                                      "never able to obtain the components. Bring me the 6 Elemental "
                                                      "Motes and the pendant will be yours.",
                                        'End Text': "Absolutely amazing, I doubted if I would ever be able to put this "
                                                    "skill to the test. Please wait a moment while I place these motes "
                                                    "into the amulet...here you go, I hope it serves you well!",
                                        'Reward': [items.ElementalAmulet],
                                        'Reward Number': 1,
                                        'Experience': 12000,
                                        'Completed': False,
                                        'Turned In': False}
                     }
        accept_quest(myr_quest, player_char, 'Side')
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Jeweler: Come glimpse the finest jewelry in the land.")
        time.sleep(0.5)
        buy_list = ['Accessory', 'Go Back']
        print("You have {} gold.".format(player_char.gold))
        print("Did you want to buy or sell?")
        option_list = ['Buy', 'Sell', 'Leave']
        opt_index = storyline.get_response(option_list)
        if option_list[opt_index] == 'Leave':
            print("We're sorry to see you go. Come back anytime!")
            time.sleep(1)
            return
        else:
            if option_list[opt_index] == 'Buy':
                buy(player_char, buy_list)
            elif option_list[opt_index] == 'Sell':
                sell(player_char)
            else:
                print("Something went wrong.")
                return


def tavern(player_char):
    """
    Quests and tips/hints
    """

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        p_level = player_level(player_char)
        print("Barkeep: Hey there, make yourself at home. Let me know if you need anything.")
        options = ["Talk with Patrons", "View the Job Board", "Go Back"]
        if any(x[2] for x in player_char.quest_dict['Bounty'].values()):
            options.insert(0, "Turn In Bounty")
        choice = storyline.get_response(options)
        if options[choice] == "Talk with Patrons":
            tavern_patrons(player_char)
        elif options[choice] == "View the Job Board":
            num_quests = len(player_char.quest_dict['Bounty'])
            if random.randint(0, num_quests ** 3) or num_quests > 5:
                print("There are no jobs currently available.")
            else:
                level = str(min(6, p_level // 10))
                while True:
                    enemy = enemies.random_enemy(level)
                    if enemy.name not in list(player_char.quest_dict['Bounty'].keys()):
                        break
                num = random.randint(3, 10)
                print("We would like you to defeat {} {}s. Do you accept this bounty?".format(num, enemy.name))
                yes_no = ["Yes", "No"]
                resp = storyline.get_response(yes_no)
                if yes_no[resp] == "Yes":
                    player_char.quest_dict['Bounty'][enemy.name] = [num, 0, False, enemy]
                    print("Return here when the job is done and you will be rewarded.")
                else:
                    print("Fair enough. Come back later if you change your mind.")
            input("Press enter to continue")
        elif options[choice] == "Turn In Bounty":
            turn_in_list = [x for x, y in player_char.quest_dict['Bounty'].items() if y[2]]
            turn_in_choice = storyline.get_response(turn_in_list)
            turn_in = turn_in_list[turn_in_choice]
            del player_char.quest_dict['Bounty'][turn_in]
            gold = random.randint(100, 200) * p_level
            player_char.gold += gold
            exp = random.randint(10, 20) * p_level
            player_char.experience += exp
            print("You gain {} gold and {} experience for completing the bounty.".format(gold, exp))
            while player_char.experience >= player_char.exp_to_gain:
                player_char.level_up()
            if random.randint(0, player_char.check_mod('luck', luck_factor=10)):
                reward = items.random_item(player_char.pro_level + 2)
                player_char.modify_inventory(reward, num=1)
                print("And you have been rewarded with a {}.".format(reward().name))
            input("Press enter to continue")
        elif options[choice] == "Go Back":
            break
        else:
            print("This shouldn't be reached.")
            raise BaseException


def church(player_char):
    """

    """

    p_level = player_level(player_char)
    if 'Wendigo' in list(player_char.quest_dict['Main'].keys()):
        if player_char.quest_dict['Main']['Wendigo']['Completed']:
            turn_in_quest('Wendigo', player_char, 'Main')
    elif p_level >= 40:
        wendigo_quest = {'Wendigo': {'Who': 'Priest',
                                     'Type': 'Defeat',
                                     'Total': 1,
                                     'Start Text': "While the depths of the dungeon are home to many a horrible "
                                                   "creature, the Wendigo is a curse to our very soul. Vanquish this "
                                                   "monstrosity and Elysia will reward you with a boon.",
                                     'End Text': "Some order has been restored, although more work is to be done. Take "
                                                 "this gift and use it to continue the good fight.",
                                     'Reward': [items.AardBeing],
                                     'Reward Number': 1,
                                     'Experience': 6000,
                                     'Completed': False,
                                     'Turned In': False}
                         }
        accept_quest(wendigo_quest, player_char, 'Main')
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Come in my child. You are always welcome in the arms of Elysia.")
        time.sleep(0.5)
        print("How can we be of service?")
        church_options = ['Promotion', 'Save', 'Quit', 'Leave']
        church_index = storyline.get_response(church_options)
        if church_options[church_index] == 'Promotion':
            if player_char.level // 20 > 0 and player_char.pro_level < 3:
                storyline.slow_type("You have qualified for a promotion.\n")
                classes.promotion(player_char)
                print("Let the light of Elysia guide you on your new path.")
            elif player_char.pro_level == 3:
                print("You are at max promotion level and can no longer be promoted.\n")
            else:
                print("You need to be at least level 20 before you can promote your character.\n")
            time.sleep(1)
        elif church_options[church_index] == 'Save':
            player_char.save()  # Can only save at church in town
        elif church_options[church_index] == 'Quit':
            player_char.game_quit()
        elif church_options[church_index] == 'Leave':
            print("Let the light of Elysia guide you.")
            time.sleep(1)
            break


def secret_shop(player_char):
    """

    """

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("You have found me in this god forsaken place. Since you're here, you might as well buy some supplies.")
        time.sleep(0.5)
        buy_list = ['Weapon', 'OffHand', 'Armor', 'Accessory', 'Potion', 'Misc']
        print("You have {} gold.".format(player_char.gold))
        print("Did you want to buy or sell?")
        option_list = ['Buy', 'Sell', 'Leave']
        opt_index = storyline.get_response(option_list)
        if option_list[opt_index] == 'Leave':
            print("We're sorry to see you go. Come back anytime!")
            time.sleep(1)
            player_char.location_y += 1
        else:
            if option_list[opt_index] == 'Buy':
                buy(player_char, buy_list, in_town=False)
            elif option_list[opt_index] == 'Sell':
                sell(player_char)
            else:
                print("Something went wrong.")
                time.sleep(1)
                player_char.location_y += 1


def ultimate_armor_repo(player_char):
    """

    """

    if 'Chisolm' in list(player_char.quest_dict['Side'].keys()):
        player_char.quest_dict['Side']['Chisolm']['Completed'] = True
        print("Hmmm, I see my big brother sent you to look for me. Tell him do not worry about me and that I will not "
              "return until the ultimate evil has been vanquished.")
        print("You have completed a quest.")
        input("Press enter to continue")
    looted = False
    os.system('cls' if os.name == 'nt' else 'clear')
    texts = [
        "Hello, my name is Chisolm, Griswold's brother.",
        "I tried to defeat the ultimate evil but could not even damage it.",
        "I barely escaped, camping here to lick my wounds.",
        "I decided I would instead use my blacksmith skills to help those who look to do what I could not.",
        "Choose the type of armor you would prefer and I will make you the finest set you could imagine."
    ]
    for text in texts:
        time.sleep(0.1)
        storyline.slow_type(text)
    while True:
        type_list = ['Cloth', 'Light', 'Medium', 'Heavy']
        armor_list = [items.MerlinRobe, items.DragonHide, items.Aegis, items.Genji]
        armor_typ = storyline.get_response(type_list)
        print("You have chosen for me to make you an immaculate {} armor. Is this correct?".format(
            type_list[armor_typ].lower()))
        yes_no = ['Yes', 'No']
        confirm = storyline.get_response(yes_no)
        if yes_no[confirm] == 'Yes':
            chosen = armor_list[armor_typ]
            print("Please wait while I craft your armor, it will only take a few moments.")
            time.sleep(3)
            print("I present to you the legendary armor, {}!".format(chosen().name))
            player_char.modify_inventory(chosen, 1)
            looted = True
            time.sleep(2)
            print("Now that I have fulfilled my goal, I will leave this place. Goodbye, {}!".format(player_char.name))
        else:
            print("You need time to consider you choice, I respect that. Come back when you have made your choice.")
        break
    time.sleep(1)
    player_char.location_y += 1
    os.system('cls' if os.name == 'nt' else 'clear')
    return looted


def buy(player_char, buy_list, in_town=True):
    """

    """

    yes_no = ['Yes', 'No']
    print("Great! What would you like to buy?")
    time.sleep(0.5)
    buy_index = storyline.get_response(buy_list)
    if buy_list[buy_index] == "Go Back":
        return
    cat_list = []
    for cat in items.items_dict[buy_list[buy_index]]:
        cat_list.append(cat)
    cat_list.append('Go Back')
    cat_index = storyline.get_response(cat_list)
    if cat_list[cat_index] == 'Go Back':
        return
    while True:
        item_list = []
        item_options = []
        for item in items.items_dict[buy_list[buy_index]][cat_list[cat_index]]:
            adj_cost = max(1, int(item().value - player_char.charisma * 2))
            if in_town:
                if item().rarity < 35:
                    item_options.append(item().name + '  ' + str(adj_cost))
                    item_list.append(item)
            else:
                if 35 <= item().rarity <= 40:
                    item_options.append(item().name + '  ' + str(adj_cost))
                    item_list.append(item)
        item_options.append('Go Back')
        item_index = storyline.get_response(item_options)
        if item_options[item_index] == 'Go Back':
            break
        buy_item = item_list[item_index]
        buy_price = max(1, int(buy_item().value - (player_char.charisma * 2)))
        if player_char.gold < buy_price:
            print("You do not have enough gold.")
            time.sleep(0.25)
        else:
            print("You have {} gold coins.".format(player_char.gold))
            while True:
                try:
                    num = int(input("How many {}s would you like to buy? ".format(buy_item().name)))
                    if num * buy_price > player_char.gold:
                        print("You do not have enough money for that purchase.")
                    elif num == 0:
                        pass
                    else:
                        buy_price *= num
                        print("That will cost {} gold coins.".format(buy_price))
                        print("Do you still want to buy {} {}? ".format(num, buy_item().name))
                        confirm = storyline.get_response(yes_no)
                        if yes_no[confirm] == 'Yes':
                            player_char.gold -= buy_price
                            player_char.modify_inventory(buy_item, num=num, subtract=False)
                            print("{} {} will be added to your inventory.".format(num, buy_item().name))
                        else:
                            print("Sorry to hear that. Come back when you have something you wish to buy.")
                    input("Press enter to continue.")
                    return
                except ValueError:
                    print("Please enter a valid number.")
                    input()


def sell(player_char):
    """

    """

    yes_no = ['Yes', 'No']
    print("We could always use more product. What do you have to sell?")
    time.sleep(0.5)
    sell_list = []
    for key in player_char.inventory.keys():
        if player_char.inventory[key][0]().rarity < 99:
            sell_list.append(key)
    if len(sell_list) == 0:
        print("You don't have anything to sell.")
        time.sleep(1)
        return
    sell_list.append('Go Back')
    typ_index = storyline.get_response(sell_list)
    if sell_list[typ_index] == 'Go Back':
        return
    else:
        sell_item = player_char.inventory[sell_list[typ_index]][0]
        sell_amt = player_char.inventory[sell_list[typ_index]][1]
        if sell_item().rarity >= 50:
            print("Wow, that's something you don't see everyday!")
        print("You have {} {} to sell.".format(sell_amt, sell_item().name))
        while True:
            try:
                num = int(input("How many would you like to sell? "))
                if num <= sell_amt and num != 0:
                    sale_price = int(0.5 * num * sell_item().value + (player_char.charisma * 2))
                    print("I'll give you {} gold coins for that.".format(sale_price))
                    print("Do you still want to sell? ")
                    confirm = storyline.get_response(yes_no)
                    if yes_no[confirm] == 'Yes':
                        player_char.modify_inventory(player_char.inventory[sell_list[typ_index]][0], num=num,
                                                     subtract=True)
                        player_char.gold += sale_price
                        print("You sold {} {} for {} gold.".format(num, sell_item().name, sale_price))
                    else:
                        print("I am sorry to hear that. Come back when you have something you wish to "
                              "sell.")
                elif num == 0:
                    pass
                else:
                    print("You cannot sell more than you have.")
                input("Press enter to continue.")
                return
            except ValueError:
                print("Please enter a valid number.")
                time.sleep(1)


def town(player_char):
    """

    """

    os.system('cls' if os.name == 'nt' else 'clear')
    locations = [blacksmith, armory, alchemist, jeweler, church, tavern]
    town_options = ['Blacksmith', 'Armory', 'Alchemist', 'Jeweler', 'Church', 'Tavern', 'Dungeon', 'Character Menu']
    storyline.slow_type("Welcome to the town of Silvana!\n")
    time.sleep(0.5)
    while True:
        player_char.health = player_char.health_max
        player_char.mana = player_char.mana_max
        print("Where would you like to go?")
        town_index = storyline.get_response(town_options)
        if town_options[town_index] == 'Dungeon':
            print("You descend into the dungeon.")
            time.sleep(1)
            player_char.location_x, player_char.location_y, player_char.location_z = (5, 10, 1)
            break
        elif town_options[town_index] == 'Character Menu':
            os.system('cls' if os.name == 'nt' else 'clear')
            player_char.character_menu()
        elif town_options[town_index] == 'Church':
            locations[town_index](player_char)
        else:
            locations[town_index](player_char)
        os.system('cls' if os.name == 'nt' else 'clear')
