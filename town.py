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
    return player_char.level.level + (30 * (player_char.level.pro_level - 1))


def upgrade(player_char):
    """
    function handles weapon upgrade for Find Chisolm quest
    upgrades non-ultimate weapon to be an ultimate weapon (for damaging the final boss) or further upgrade an existing
      ultimate weapon (increase damage, crit chance, etc.) TODO
    """
    return player_char


def power_up(player_char):
    """
    function handles power up for Power Core quest
    adds feature to either item or player TODO
    """

    def test():
        print("hello world!")

    setattr(player_char, 'test', test)


def turn_in_quest(quest, player_char, typ):
    """

    """

    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{player_char.quest_dict[typ][quest]['Who']}")
    storyline.slow_type(player_char.quest_dict[typ][quest]['End Text'] + '\n', typing_speed=125)
    time.sleep(1)
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
    if reward == 'Gold':
        player_char.gold += player_char.quest_dict[typ][quest]['Reward Number']
        print(f"You received {player_char.quest_dict[typ][quest]['Reward Number']} gold and {exp} experience.")
    elif reward == 'Upgrade':
        upgrade(player_char)
    elif reward == 'Power Up':
        power_up(player_char)
    elif reward == 'Warp Point':
        player_char.warp = True
        print(f"You received {exp} experience and gain access to the Warp Point.")
    else:
        num = player_char.quest_dict[typ][quest]['Reward Number']
        player_char.modify_inventory(reward, num=num)
        if num == 1:
            print(f"You received {reward().name} and {exp} experience.")
        else:
            print(f"You received {reward().name} x{num} and {exp} experience.")
    player_char.level.exp += exp
    while player_char.level.exp >= player_char.level.exp_to_gain and not player_char.max_level():
        player_char.level_up()
    if player_char.quest_dict[typ][quest]['Type'] == 'Collect':
        item = player_char.quest_dict[typ][quest]['What']
        del player_char.special_inventory[item().name]
    input("Press enter to continue")


def accept_quest(quest, player_char, typ):
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
      Side: Level 60, locate Chisolm, rewards item upgrade and 400000 exp
    Armorer
      Main: Level 45, collect 1 Power Core, rewards Power Up and
      Side: Level 15, collect 8 Leathers, rewards 2500 gold and 250 exp
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
            Level 20, defeat Barghest, rewards Accuracy Ring and 500 exp
      Side: Level 3, locate Timmy, rewards 5 Health Potions and 150 exp
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
                               "Patience is a virtue I hold sacred. I will wait as long as I need."],
                    'Sergeant': ["Outstanding! Return to me when you have completed the quest.",
                                 "You came a long way for nothing..."]
                    }
    key = list(quest)[0]
    who = quest[key]['Who']
    print(f"{who}")
    storyline.slow_type(quest[key]['Start Text'] + '\n', typing_speed=125)
    print("Do you accept this quest?")
    main_input = storyline.get_response(["Yes", "No"])
    accepted = False
    if not main_input:
        player_char.quest_dict[typ][key] = quest[key]
        print(response_map[who][0])
        if quest[key]['Type'] == 'Defeat':
            if key in player_char.kill_dict:
                player_char.quest_dict[typ][key]['Completed'] = True
        accepted = True
    else:
        print(response_map[who][1])
    input("Press enter to continue")
    return accepted


def check_quests(quest_dict, player_char):
    """

    """

    p_level = player_level(player_char)
    player_mains = list(player_char.quest_dict['Main'])
    player_sides = list(player_char.quest_dict['Side'])
    mains = quest_dict['Main']
    main_quests = [mains[x] for x in mains if p_level >= x]
    sides = quest_dict['Side']
    side_quests = [sides[x] for x in sides if p_level >= x]
    quest = False
    if len(main_quests) > 0:
        for main_quest in main_quests:
            key = list(main_quest)[0]
            if key in player_mains:
                if player_char.quest_dict['Main'][key]['Completed'] and \
                        not player_char.quest_dict['Main'][key]['Turned In']:
                    turn_in_quest(key, player_char, "Main")
                    quest = True
            else:
                quest = accept_quest(main_quest, player_char, "Main")
            if quest:
                break
    if len(side_quests) > 0:
        for side_quest in side_quests:
            key = list(side_quest)[0]
            if key in player_sides:
                if player_char.quest_dict['Side'][key]['Completed'] and \
                        not player_char.quest_dict['Side'][key]['Turned In']:
                    turn_in_quest(key, player_char, "Side")
                    quest = True
            else:
                quest = accept_quest(side_quest, player_char, "Side")
            if quest:
                break
    return quest


def tavern_patrons(player_char):
    """
    Various patrons/employees that frequent the tavern
    3 possible conversations: Talk (tip or hint), Main Quest (directly related to game completion), or Side Quest
    Barkeep: level 1
    Waitress: level 1
    Drunkard: level 8
    Soldier: level 10
    Hooded Figure: level 25
    """
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        p_level = player_level(player_char)
        patrons = {'Barkeep': {'Talk': {1: ["If you want to access the character menu, you can do so by hitting the (c)"
                                            " button.",
                                            "Make sure to stop by from time to time. You never know who might show up.",
                                            "Equipment vendors will only show you what you can equip. If you can't find"
                                            " an item type, your class probably can't use it."],
                                        5: ["How did you like that stat bonus at level 4? You get another every 4th "
                                            "level, so plan your promotions accordingly.",
                                            "If you get a quest from someone, come back and talk with them after it is "
                                            "completed and they will likely reward you for your efforts."],
                                        10: ["You have to be level 20 to get a promotion but you can gain more "
                                             "experience if you wait until level 30.",
                                             "Locked chests contain more powerful items compared with unlocked ones, "
                                             "however you need a key or a lockpick to get to the treasure."]
                                        },
                               'Main': {10: {'The Butcher': {'Who': 'Barkeep',
                                                             'Type': 'Defeat',
                                                             'What': 'Minotaur',
                                                             'Total': 1,
                                                             'Start Text':
                                                                 "There is a monster guarding the steps to the first "
                                                                 "floor, the Minotaur, that is responsible for lots of "
                                                                 "carnage. If you defeat it, I will give you something "
                                                                 "to help you explore the dungeon.",
                                                             'End Text':
                                                                 "I'm glad to hear you took that butcher out. Here's an"
                                                                 " item that should help you in any future quests.",
                                                             'Reward': [items.OldKey],
                                                             'Reward Number': 1,
                                                             'Experience': 200,
                                                             'Completed': False,
                                                             'Turned In': False}
                                             },
                                        },
                               'Side': {1: {'Rat Trap': {'Who': 'Barkeep',
                                                         'Type': 'Collect',
                                                         'What': items.RatTail,
                                                         'Total': 6,
                                                         'Start Text':
                                                             "Darn pesky rats keep getting into my food supply and I'd "
                                                             "bet anything they come up from that dungeon. Help my out "
                                                             "by killing as many as you need to collect 6 tails and "
                                                             "I'll pay you 600 gold.",
                                                         'End Text':
                                                             "Good riddance to the bastards, hopefully this will keep "
                                                             "my food supplies in good order. Here's the gold I "
                                                             "promised you.",
                                                         'Reward': ['Gold'],
                                                         'Reward Number': 600,
                                                         'Experience': 100,
                                                         'Completed': False,
                                                         'Turned In': False}
                                            }
                                        }
                               },
                   'Waitress': {'Talk': {1: ["Entering the town will replenish your health and mana. Seems like you "
                                             "could take advantage of that.",
                                             "Sorry, I can't talk now! I am getting married and need to make as much "
                                             "money as I can."],
                                         10: ["(sobbing) I can't believe it...a week before our wedding and my husband "
                                              "to be decides to join the fight against the prime evil...I want to be "
                                              "mad but he says he can't stand by when I am in danger. My hero..."],
                                         25: ["Joffrey returned yesterday bloodied but resolute. He has gained much "
                                              "experience and hopes to have found the source of our suffering by "
                                              "month's end. I gave him my lucky pendant to return to me when his "
                                              "mission is complete."],
                                         },
                                'Main': {35: {"A Bad Dream": {'Who': 'Waitress',
                                                              'Type': 'Locate',
                                                              'What': "Joffrey",
                                                              'Total': 1,
                                                              'Start Text':
                                                                  "This morning I woke in a sweat...I dreamed I was "
                                                                  "standing in a square room and to my horror a great "
                                                                  "flaming horse struck down my betrothed...please find"
                                                                  " my Joffrey before my dream truly becomes a "
                                                                  "nightmare...",
                                                              'End Text':
                                                                  "My pendant...Elysia take me...he left me these keys "
                                                                  "last I saw of him...please avenge my love...(the "
                                                                  "waitress runs out sobbing...)",
                                                              'Reward': [items.OldKey],
                                                              'Reward Number': 2,
                                                              'Experience': 4500,
                                                              'Completed': False,
                                                              'Turned In': False}
                                              }
                                         },
                                'Side': {5: {"Where's the Beef?": {'Who': 'Waitress',
                                                                   'Type': 'Collect',
                                                                   'What': items.MysteryMeat,
                                                                   'Total': 12,
                                                                   'Start Text':
                                                                       "My wedding day is fast approaching and we are "
                                                                       "trying to save a few gold, so I am cooking the "
                                                                       "meal for the guests. If you could bring me back"
                                                                       " 12 pieces of mystery meat, I can reward you "
                                                                       "with this potion I received as a tip once.",
                                                                   'End Text':
                                                                       "Thank you, thank you, thank you! You have made "
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
                   'Soldier': {'Talk': {10: ["You may find locked doors along your path while exploring the dungeon. "
                                             "You can't open these with just any old key, you need an actual Old Key."],
                                        25: ["I just finished my shift guarding the old warehouse behind the barracks. "
                                             "They won't tell us what's in there but I have seen several scientists "
                                             "come and go."],
                                        65: ["The Devil is immune to normal weapons but legend says there is a "
                                             "material that will do the job."]
                                        },
                               'Main': {55: {'No Laughing Matter': {'Who': 'Soldier',
                                                                    'Type': 'Defeat',
                                                                    'What': 'Jester',
                                                                    'Total': 1,
                                                                    'Start Text':
                                                                        "During my first week of training, a senior "
                                                                        "officer told us a story about a former recruit"
                                                                        " who went mad. He was a bit of an outcast and "
                                                                        "many of the other soldiers bullied him for his"
                                                                        " weirdness, as it was told. He had a fondness "
                                                                        "for card tricks and claimed he was an 'Agent "
                                                                        "of Chaos', whatever that means...anyway, he "
                                                                        "finally cracked one day and disappeared, never"
                                                                        " to be heard from again...that is until we "
                                                                        "started receiving the body parts...the freak "
                                                                        "has been sending back parts of adventurers "
                                                                        "with notes talking about revenge and signed by"
                                                                        " the Jester. Someone needs to take this sick "
                                                                        "bastard out before anyone else gets hurt. Be "
                                                                        "careful, you never truly know what you may get"
                                                                        " with this guy.",
                                                                    'End Text':
                                                                        "Excellent work! Hopefully the souls of those "
                                                                        "tortured by the Jester will be able to rest "
                                                                        "now. This magical ring was shipped back with "
                                                                        "one of the body parts, it increases your "
                                                                        "chance to evade attacks in combat. I'm sure "
                                                                        "the Jester thought he was being clever, since "
                                                                        "it took so long for someone to finally catch "
                                                                        "him. It's fitting that you would wear it now.",
                                                                    'Reward': [items.EvasionRing],
                                                                    'Reward Number': 1,
                                                                    'Experience': 300000,
                                                                    'Completed': False,
                                                                    'Turned In': False}}},
                               'Side': {25: {'Metalingus': {'Who': 'Soldier',
                                                            'Type': 'Collect',
                                                            'What': items.ScrapMetal,
                                                            'Total': 8,
                                                            'Start Text':
                                                                "The city guard are in desperate need of new equipment "
                                                                "but we unfortunately are running short on the required"
                                                                " materials. If you can bring back 8 pieces of scrap "
                                                                "metal, I can use my connections with the alchemist "
                                                                "shop and get you a really nice potion for your "
                                                                "troubles.",
                                                            'End Text':
                                                                "You are a life saver, literally. This metal will help "
                                                                "to fortify the town against the scum that patrols the "
                                                                "dungeon. Here is a token of my appreciation.",
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
                                         25: ["Do you see (hic) that person in the corner? What's their deal, TAKE THE "
                                              "HOOD OFF ALREADY!...ah whatever..."],
                                         30: ["(hic)...I heard tell there were secret passages...(hic) in the dungeon."]
                                         },
                                'Main': {35: {"Lapidation": {'Who': 'Drunkard',
                                                             'Type': 'Defeat',
                                                             'What': 'Cockatrice',
                                                             'Total': 1,
                                                             'Start Text':
                                                                 "Let me tell you a quick story...back in the day I "
                                                                 "used to be an adventurer. My friend and I had delved "
                                                                 "too deep into the dungeon below and were trapped with"
                                                                 " no escape. A giant bird-looking monstrosity had us "
                                                                 "pinned...we made a run for it...but we weren't fast "
                                                                 "enough. I still remember the look on Rutger's face as"
                                                                 " he turned to stone in front of me...this necklace is"
                                                                 " the only reason I am still here. If you come across "
                                                                 "the beast, make sure it's dead before you are. "
                                                                 "(hic)...hmmm...what was I sayin'?",
                                                             'End Text':
                                                                 "Rutger can now be at peace...I can finally let go of "
                                                                 "the past (hic). Here, take this necklace, I don't "
                                                                 "need it anymore...",
                                                             'Reward': [items.GorgonPendant],
                                                             'Reward Number': 1,
                                                             'Experience': 5000,
                                                             'Completed': False,
                                                             'Turned In': False}
                                              }
                                         },
                                'Side': {18: {"I'm Molting!": {'Who': 'Drunkard',
                                                               'Type': 'Collect',
                                                               'What': items.SnakeSkin,
                                                               'Total': 8,
                                                               'Start Text':
                                                                   "SNAKES! Oh my I hate those things...(hic)..."
                                                                   "slithering about. It's unnatural...I think...(hic)"
                                                                   "...what was I saying?...Oh yeah, bring me some "
                                                                   "snake skins and I'll give you these poison curing "
                                                                   "thingies I found...(hic)",
                                                               'End Text':
                                                                   "WHY WOULD YOU BRING...oh yeah I asked you to..."
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
                   'Busboy': {
                       'Talk': {1: ["The waitress left crying some time ago...sounds like her fiance was killed in the "
                                    "dungeons."],
                                },
                       'Main': {},
                       'Side': {}
                       },
                   'Hooded Figure': {'Talk': {25: ["..."],
                                              35: ["Hmm...interesting..."],
                                              50: ["Your power has grown...I am impressed."],
                                              60: ["Have you defeated the Red Dragon yet?"],
                                              },
                                     'Main': {30: {'Payback': {'Who': 'Hooded Figure',
                                                               'Type': 'Defeat',
                                                               'What': 'Pseudodragon',
                                                               'Total': 1,
                                                               'Start Text':
                                                                   "My rival, a wizard known for unimaginable cruelty, "
                                                                   "is looking to increase her power by upgrading her "
                                                                   "familiar. She has her eyes set on a particular "
                                                                   "creature, a Pseudodragon, that dwells in the "
                                                                   "dungeon below. Destroy this creature before she can"
                                                                   " corrupt it and I will reward you.",
                                                               'End Text':
                                                                   "You have done well in taking care of this threat. "
                                                                   "Take this reward and use it wisely.",
                                                               'Reward': [items.Megalixir],
                                                               'Reward Number': 1,
                                                               'Experience': 3000,
                                                               'Completed': False,
                                                               'Turned In': False}
                                                   },
                                              60: {'Dracarys': {'Who': 'Hooded Figure',
                                                                'Type': 'Defeat',
                                                                'What': 'Red Dragon',
                                                                'Total': 1,
                                                                'Start Text':
                                                                    "The depths are home to a powerful Red Dragon. She "
                                                                    "is not to be taken lightly, however if you are "
                                                                    "able to defeat her, the path to glory will be "
                                                                    "yours.",
                                                                'End Text':
                                                                    "You have proven yourself worthy for the ultimate "
                                                                    "challenge...me. Take this as a reminder of the "
                                                                    "futility of being a hero...there will always be "
                                                                    "another evil to deal with and that evil will "
                                                                    "always pale in comparison to my wrath. Pursue me "
                                                                    "at your own peril.",
                                                                'Reward': [items.ClassRing],
                                                                'Reward Number': 1,
                                                                'Experience': 500000,
                                                                'Completed': False,
                                                                'Turned In': False}
                                                   }
                                              },
                                     'Side': {}
                                     }
                   }
        options = ["Barkeep"]
        if 'A Bad Dream' in player_char.quest_dict['Main']:
            if not player_char.quest_dict['Main']['A Bad Dream']['Turned In']:
                options.append("Waitress")
            else:
                options.append('Busboy')
        else:
            options.append('Waitress')
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
        options.append('Go Back')
        print("Who would you like to talk with?")
        option_input = storyline.get_response(options)
        if options[option_input] == 'Go Back':
            return
        quest = check_quests(patrons[options[option_input]], player_char)
        if not quest:
            talks = patrons[options[option_input]]['Talk']
            level_talks = [talks[x] for x in talks if p_level >= x]
            print(random.choice(random.choice(level_talks)))
            input("Press enter to continue")


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
        if isinstance(weapon, list):
            if 'Archbishop' == player_char.cls:
                weapon = weapon[0]
            else:
                weapon = weapon[1]
        print("Give me a moment and I will make you an ultimate weapon...")
        time.sleep(5)
        print(f"I present to you, {player_char.name}, the mighty {weapon().name}!")
        player_char.modify_inventory(weapon, num=1)
        del player_char.inventory['Unobtainium']
        if "He Ain't Heavy" in player_char.quest_dict['Side']:
            if player_char.quest_dict['Side']["He Ain't Heavy"]['Turned In']:
                print("I still have a bit of ore left if you want me to upgrade another weapon or I may even be able to"
                      " improve the one I just made.")
    time.sleep(2)


def barracks(player_char):
    """
    Base location for the player; get quests and direction from the Sergeant
    """

    quests = {'Main': {1: {'The Holy Relics': {'Who': 'Sergeant',
                                               'Type': 'Locate',
                                               'What': 'Relics',
                                               'Total': 6,
                                               'Start Text':
                                                   "So you think you have what it takes, huh? Some of my best men have "
                                                   "died in that dungeon and here you are, barely old enough to wipe "
                                                   "your own ass...very well, it's your funeral. Maybe you have "
                                                   "something those men didn't have. We don't have all the details but "
                                                   "we believe the key to vanquishing the prime evil is to collect all "
                                                   "6 of the holy relics. Do that and you might just stand a chance. "
                                                   "Don't blame me for not holding my breath...",
                                               'End Text':
                                                   "Well I'll be, you crazy son of a bitch, you did it!...I shouldn't "
                                                   "get to excited, there's still work to be done. But this is huge! "
                                                   "Hopefully one of these will help in your quest to destroy what "
                                                   "plagues this town.",
                                               'Reward': [items.MedusaShield, items.Magus, items.AardBeing],
                                               'Reward Number': 1,
                                               'Experience': 1000000,
                                               'Completed': False,
                                               'Turned In': False}
                           },
                       20: {'Cry Havoc!': {'Who': 'Sergeant',
                                           'Type': 'Defeat',
                                           'What': 'Barghest',
                                           'Total': 1,
                                           'Start Text':
                                               "We believe we've identified where the first relic is but it's guarded "
                                               "by a nasty, dog-like beast, a Barghest. This thing can shapeshift and "
                                               "can be fairly nasty if you are not prepared. Destroy it and find the "
                                               "first of the 6 relics. I'll have something for you when you return.",
                                           'End Text':
                                               "Glad to hear you took care of that beast, soldier. Take this ring, it "
                                               "will make you more accurate in combat, which can be useful against "
                                               "flying and invisible creatures.",
                                           'Reward': [items.AccuracyRing],
                                           'Reward Number': 1,
                                           'Experience': 500,
                                           'Completed': False,
                                           'Turned In': False}
                            },
                       50: {'Immovable Object': {'Who': 'Sergeant',
                                                 'Type': 'Defeat',
                                                 'What': 'Iron Golem',
                                                 'Total': 1,
                                                 'Start Text':
                                                     "Only a powerful wizard is capable of creating a golem and a truly"
                                                     " powerful wizard must have created the Iron Golem. While we do "
                                                     "not know who created this monstrosity, the fact is you will not "
                                                     "be able to get to the 5th floor without taking it out.",
                                                 'End Text':
                                                     "I shouldn't be surprised at this point but again you've done what"
                                                     " was thought impossible. Choose your reward and good luck going "
                                                     "forward, although it doesn't seem that you need much luck...",
                                                 'Reward': [items.DiamondAmulet, items.PlatinumPendant],
                                                 'Reward Number': 1,
                                                 'Experience': 200000,
                                                 'Completed': False,
                                                 'Turned In': False}
                            },
                       60: {'In the Day of Our Lord': {'Who': 'Sergeant',
                                                       'Type': 'Defeat',
                                                       'What': 'Domingo',
                                                       'Total': 1,
                                                       'Start Text':
                                                           "Many years ago, an explorer returned with a magical egg "
                                                           "that was said to contain a powerful creature. Our "
                                                           "scientists made many attempts to hatch the creature but "
                                                           "were unsuccessful until recently when they had a "
                                                           "breakthrough when they simple placed it in our chicken "
                                                           "incubator. We had hoped to use this creature to protect the"
                                                           " city from the monsters below but found out quickly that we"
                                                           " could not hope to control it and had locked it away. "
                                                           "However, someone inexplicably let the creature out. It "
                                                           "killed 6 of my men before it disappeared into the dungeon. "
                                                           "Find the creature and destroy it.",
                                                       'End Text':
                                                           "It's a shame we had to kill it but there is no point trying"
                                                           " to control the uncontrollable. The head scientist sends "
                                                           "his thanks and as a reward, they have finished construction"
                                                           " of a warp point that will allow you to teleport directly "
                                                           "to the 5th dungeon level.",
                                                       'Reward': ["Warp Point"],
                                                       'Reward Number': 1,
                                                       'Experience': 500000,
                                                       'Completed': False,
                                                       'Turned In': False}
                            },
                       },
              'Side': {3: {'Bring Him Home': {'Who': 'Sergeant',
                                              'Type': 'Locate',
                                              'What': 'Timmy',
                                              'Total': 1,
                                              'Start Text':
                                                  "We received a report about a small child named Timmy who somehow "
                                                  "made it past my guards and into the dungeon. While my men have been "
                                                  "punished accordingly, we still need to find the boy before something"
                                                  " bad happens to him. Locate him (he shouldn't have gone far) and "
                                                  "bring him home to his family.",
                                              'End Text':
                                                  "You've found the boy, that's excellent news! I'm sure the family is "
                                                  "very relieved. Here are some health potions to keep you alive as you"
                                                  " explore.",
                                              'Reward': [items.HealthPotion],
                                              'Reward Number': 5,
                                              'Experience': 150,
                                              'Completed': False,
                                              'Turned In': False}
                           }
                       }
              }
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Step inside, soldier. This is your new home.")
        options = ["Quests", "Storage", "Leave"]
        response = storyline.get_response(options)
        if options[response] == "Leave":
            print("Take care, soldier.")
            time.sleep(1)
            return
        if options[response] == 'Storage':
            os.system('cls' if os.name == 'nt' else 'clear')
            print("What would you like to do?")
            store_options = ['Store', 'Go Back']
            if len(player_char.storage) > 0:
                store_options.insert(1, 'Retrieve')
            store_response = storyline.get_response(store_options)
            choice = store_options[store_response]
            if choice == 'Store':
                while True:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("What would you like to add to your storage for safe keeping?")
                    p_items = list(player_char.inventory)
                    if len(p_items) == 0:
                        print("You do not have anything to store at the moment.")
                        time.sleep(2)
                        break
                    p_items.append('Go Back')
                    p_choice = storyline.get_response(p_items)
                    if p_items[p_choice] == 'Go Back':
                        break
                    itm, total = player_char.inventory[p_items[p_choice]]
                    if total == 1:
                        if itm().name not in player_char.storage:
                            player_char.storage[p_items[p_choice]] = [itm, 1]
                        else:
                            player_char.storage[p_items[p_choice]][1] += 1
                        player_char.modify_inventory(itm, num=1, subtract=True)
                    else:
                        while True:
                            try:
                                print(f"You have {total} {p_items[p_choice]}s in your inventory.")
                                num = int(input("How many would you like to store? "))
                                if num < 0:
                                    print("Please enter a valid quantity.")
                                elif num <= total:
                                    if itm().name not in player_char.storage:
                                        player_char.storage[p_items[p_choice]] = [itm, num]
                                    else:
                                        player_char.storage[p_items[p_choice]][1] += num
                                    player_char.modify_inventory(itm, num=num, subtract=True)
                                    break
                                print("You do not have that many, please enter a correct value.")
                            except ValueError:
                                print("Please enter a valid number.")
                                input()
                        time.sleep(1)
                        if len(player_char.inventory) == 0:
                            break
            elif choice == 'Retrieve':
                while True:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("What would you like to retrieve?")
                    retrieve_items = []
                    for key, item in player_char.storage.items():
                        retrieve_items.append(key + ": " + str(item[1]))
                    retrieve_items.append('Go Back')
                    retrieve_response = storyline.get_response(retrieve_items)
                    retrieve_item = retrieve_items[retrieve_response]
                    if retrieve_item == 'Go Back':
                        break
                    retrieve_item = retrieve_item.split(': ')[0]
                    if player_char.storage[retrieve_item][1] > 1:
                        total = player_char.storage[retrieve_item][1]
                        while True:
                            try:
                                print(f"You have {total} {retrieve_item}s in storage.")
                                num = int(input("How many would you like to retrieve? "))
                                if num < 0:
                                    print("Please enter a valid quantity.")
                                elif num <= total:
                                    player_char.modify_inventory(player_char.storage[retrieve_item][0], num)
                                    player_char.storage[retrieve_item][1] -= num
                                    if player_char.storage[retrieve_item][1] == 0:
                                        del player_char.storage[retrieve_item]
                                    break
                                print("You do not have that many, please enter a valid quantity.")
                            except ValueError:
                                print("Please enter a valid number.")
                                input()
                    else:
                        player_char.modify_inventory(player_char.storage[retrieve_item][0], 1)
                        del player_char.storage[retrieve_item]
                    time.sleep(1)
                if len(player_char.storage) == 0:
                    break
        else:
            valid = check_quests(quests, player_char)
            if not valid:
                # add helpful comments for each quest if not completed TODO
                responses = ["There are no quests available at this time. Check back in regularly and I might have "
                             "something for you."]
                print(responses[0])
            time.sleep(2)


def blacksmith(player_char):
    """
    Griswold's shop - sells weapons and offhand items
    At level 60 (level 30 first promotion or level 1 second promotion), you will receive a quest to find Griswold's
      brother, Chisolm; completing this quest, along with finding the unobtainium, will allow Griswold to either upgrade
      another weapon to ultimate status (for dual wielding) or improve an existing one further
    Once Unobtainium is found, Griswold will craft an ultimate weapon
    """

    quests = {'Main': {},
              'Side': {60: {"He Ain't Heavy": {'Who': 'Griswold',
                                               'Type': 'Locate',
                                               'Total': 1,
                                               'Start Text':
                                                   "I am so glad you stopped in, I really need your help. My baby "
                                                   "brother, Chisolm, has been missing for far too long. He regularly "
                                                   "goes into the dungeon but never for this long. Please help me find "
                                                   "him and I will forever be indebted to you.",
                                               'End Text':
                                                   "By the light of Elysia, you have found him! I must admit I had "
                                                   "given up hope. It comes at no surprise that he chose to stay in the"
                                                   " depths to help those in need, perhaps he will choose to come home "
                                                   "once the primal evil has been vanquished.",
                                               'Reward': ["Upgrade"],  # still need to handle the reward TODO
                                               'Reward Number': 1,
                                               'Experience': 400000,
                                               'Completed': False,
                                               'Turned In': False
                                               }
                            }
                       }
              }
    if player_char.world_dict[(9, 1, 6)].visited and \
            "He Ain't Heavy" not in player_char.quest_dict['Side']:
        player_char.quest_dict['Side']["He Ain't Heavy"] = quests['Side'][60]["He Ain't Heavy"]
        player_char.quest_dict['Side']["He Ain't Heavy"]['Completed'] = True
    check_quests(quests, player_char)
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        if 'Unobtainium' in player_char.special_inventory:
            ultimate(player_char)
        print("Welcome to Griswold's! What can I do you for?")
        time.sleep(0.5)
        buy_list = ['Weapon', 'Go Back']
        if player_char.cls not in ['Footpad', 'Weapon Master', 'Thief', 'Assassin', 'Monk', 'Berserker', 'Rogue',
                                   'Ninja', 'Master Monk']:
            buy_list.insert(1, 'OffHand')
        print(f"You have {player_char.gold} gold.")
        print("Did you want to buy or sell?")
        option_list = ['Buy', 'Sell', 'Leave']
        opt_index = storyline.get_response(option_list)
        if option_list[opt_index] == 'Leave':
            print("We're sorry to see you go. Come back anytime!")
            time.sleep(1)
            return
        if option_list[opt_index] == 'Buy':
            buy(player_char, buy_list)
        elif option_list[opt_index] == 'Sell':
            os.system('cls' if os.name == 'nt' else 'clear')
            done = False
            while not done:
                done = sell(player_char)
                time.sleep(0.5)
                os.system('cls' if os.name == 'nt' else 'clear')
        else:
            print("Something went wrong.")
            return


def armory(player_char):
    """
    Armorer - sells all types of armor
    At level 15, gives quest to collect 8 Leathers, rewards 2500 gold and 250 exp
    At level 45, gives quest to collect 1 Power Core from Golem, rewards Power Up and 100000 exp
    """

    quests = {'Main': {},
              'Side': {15: {'Eight Is Enough': {'Who': 'Armorer',
                                                'Type': 'Collect',
                                                'What': items.Leather,
                                                'Total': 8,
                                                'Start Text':
                                                    "The thieves guild has placed an order for several sets of leather "
                                                    "armor but my supply of materials is getting short at the moment. "
                                                    "Say, you look capable enough, do you think you could retrieve "
                                                    "some for me? I'll pay top dollar for them.",
                                                'End Text':
                                                    "I knew it when I first saw you that you were the person for the "
                                                    "job. As promised here's some gold for your efforts.",
                                                'Reward': ['Gold'],
                                                'Reward Number': 2500,
                                                'Experience': 250,
                                                'Completed': False,
                                                'Turned In': False}
                            },
                       45: {"This Thing's Nuclear": {'Who': 'Armorer',
                                                     'Type': 'Collect',
                                                     'What': items.PowerCore,
                                                     'Total': 1,
                                                     'Start Text':
                                                         "",
                                                     'End Text':
                                                         "",
                                                     'Reward': ['Power Up'],
                                                     'Reward Number': 1,
                                                     'Experience': 100000,
                                                     'Completed': False,
                                                     'Turned In': False}
                            }
                       }
              }
    check_quests(quests, player_char)
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("I have the finest armors for sale. Come in and look around.")
        time.sleep(0.5)
        buy_list = ['Armor', 'Go Back']
        print(f"You have {player_char.gold} gold.")
        print("Did you want to buy or sell?")
        option_list = ['Buy', 'Sell', 'Leave']
        opt_index = storyline.get_response(option_list)
        if option_list[opt_index] == 'Leave':
            print("We're sorry to see you go. Come back anytime!")
            time.sleep(1)
            return
        if option_list[opt_index] == 'Buy':
            buy(player_char, buy_list)
        elif option_list[opt_index] == 'Sell':
            os.system('cls' if os.name == 'nt' else 'clear')
            done = False
            while not done:
                done = sell(player_char)
                time.sleep(0.5)
                os.system('cls' if os.name == 'nt' else 'clear')
        else:
            print("Something went wrong.")
            return


def alchemist(player_char):
    """
    Alchemist - sells potions and other miscellaneous items (scrolls, keys, etc.)
    At level 20, gives quest for collecting 12 Feathers
    """

    quests = {'Main': {},
              'Side': {20: {'Put A Feather In It': {'Who': 'Alchemist',
                                                    'Type': 'Collect',
                                                    'What': items.Feather,
                                                    'Total': 12,
                                                    'Start Text':
                                                        "As you may or may not know, all of my tinctures are created "
                                                        "here in my lab. I need some more ingredients to make more "
                                                        "Phoenix Down potions, so any Feathers that you find I will pay"
                                                        " you for them.",
                                                    'End Text':
                                                        "Excellent! Here's the gold I promised, spend it wisely.",
                                                    'Reward': ['Gold'],
                                                    'Reward Number': 4000,
                                                    'Experience': 500,
                                                    'Completed': False,
                                                    'Turned In': False}
                            }
                       }
              }
    check_quests(quests, player_char)
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Welcome to Ye Olde Item Shoppe.")
        time.sleep(0.5)
        buy_list = ['Potion', 'Misc', 'Go Back']
        print(f"You have {player_char.gold} gold.")
        print("Did you want to buy or sell?")
        option_list = ['Buy', 'Sell', 'Leave']
        opt_index = storyline.get_response(option_list)
        if option_list[opt_index] == 'Leave':
            print("We're sorry to see you go. Come back anytime!")
            time.sleep(1)
            return
        if option_list[opt_index] == 'Buy':
            buy(player_char, buy_list)
        elif option_list[opt_index] == 'Sell':
            os.system('cls' if os.name == 'nt' else 'clear')
            done = False
            while not done:
                done = sell(player_char)
                time.sleep(0.5)
                os.system('cls' if os.name == 'nt' else 'clear')
        else:
            print("Something went wrong.")
            return


def jeweler(player_char):
    """
    Jewelry shop - sells Pendants and Rings
    At level 55, gives quest to collect 6 elemental motes, rewards Elemental Amulet
    """

    quests = {'Main': {},
              'Side': {55: {'Earth, Wind, and Fire...and Water and...': {'Who': 'Jeweler',
                                                                         'Type': 'Collect',
                                                                         'What': items.ElementalMote,
                                                                         'Total': 6,
                                                                         'Start Text':
                                                                             "Long before I owned this shop, I was "
                                                                             "apprentice to a master craftsman. He "
                                                                             "taught me how to make a very powerful "
                                                                             "item called an Elemental Amulet, which "
                                                                             "requires the core of 6 elementals. "
                                                                             "However I have never been able to make "
                                                                             "this item since I was never able to "
                                                                             "obtain the components. Bring me the 6 "
                                                                             "Elemental Motes and the pendant will be "
                                                                             "yours.",
                                                                         'End Text':
                                                                             "Absolutely amazing, I doubted if I would "
                                                                             "ever be able to put this skill to the "
                                                                             "test. Please wait a moment while I place "
                                                                             "these motes into the amulet...here you "
                                                                             "go, I hope it serves you well!",
                                                                         'Reward': [items.ElementalAmulet],
                                                                         'Reward Number': 1,
                                                                         'Experience': 120000,
                                                                         'Completed': False,
                                                                         'Turned In': False}
                            }
                       }
              }
    check_quests(quests, player_char)
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Jeweler: Come glimpse the finest jewelry in the land.")
        time.sleep(0.5)
        buy_list = ['Accessory', 'Go Back']
        print(f"You have {player_char.gold} gold.")
        print("Did you want to buy or sell?")
        option_list = ['Buy', 'Sell', 'Leave']
        opt_index = storyline.get_response(option_list)
        if option_list[opt_index] == 'Leave':
            print("We're sorry to see you go. Come back anytime!")
            time.sleep(1)
            return
        if option_list[opt_index] == 'Buy':
            buy(player_char, buy_list)
        elif option_list[opt_index] == 'Sell':
            os.system('cls' if os.name == 'nt' else 'clear')
            done = False
            while not done:
                done = sell(player_char)
                time.sleep(0.5)
                os.system('cls' if os.name == 'nt' else 'clear')
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
            bounty_list = []
            level = str(min(6, p_level // 10))
            while len(bounty_list) + num_quests < 3:
                enemy = enemies.random_enemy(level)
                num = random.randint(3, 8)
                if enemy.name not in player_char.quest_dict['Bounty'] and \
                        enemy.name not in [x[0].name for x in bounty_list]:
                    bounty_list.append([enemy, num])
            bounty_options = [x[0].name for x in bounty_list]
            if num_quests > 0:
                bounty_options.append("Abandon Bounty")
            bounty_options.append("Leave")
            bounty_choice = storyline.get_response(bounty_options)
            if bounty_options[bounty_choice] == "Leave":
                continue
            if bounty_options[bounty_choice] == "Abandon Bounty":
                abandon_list = list(player_char.quest_dict['Bounty'])
                abandon_choice = storyline.get_response(abandon_list)
                print(f"Are you sure you want to abandon the {abandon_list[abandon_choice]} bounty? ")
                resp = storyline.get_response(["Yes", "No"])
                if not resp:
                    del player_char.quest_dict['Bounty'][abandon_list[abandon_choice]]
            else:
                selection = bounty_list[bounty_choice]
                print(f"We would like you to defeat {selection[1]} {selection[0].name}s. Do you accept this bounty?")
                resp = storyline.get_response(["Yes", "No"])
                if not resp:
                    player_char.quest_dict['Bounty'][selection[0].name] = [selection[1], 0, False, selection[0]]
                    print("Return here when the job is done and you will be rewarded.")
                else:
                    print("Fair enough. Come back later if you change your mind.")
        elif options[choice] == "Turn In Bounty":
            turn_in_list = [x for x, y in player_char.quest_dict['Bounty'].items() if y[2]]
            turn_in_choice = storyline.get_response(turn_in_list)
            turn_in = turn_in_list[turn_in_choice]
            num = player_char.quest_dict['Bounty'][turn_in][0]
            del player_char.quest_dict['Bounty'][turn_in]
            gold = random.randint(25*num, 50*num) * p_level * player_char.level.pro_level
            player_char.gold += gold
            exp = (random.randint(5*num, 10*num) ** player_char.level.pro_level) * player_char.level.level
            player_char.level.exp += exp
            print(f"You gain {gold} gold and {exp} experience for completing the bounty.")
            while player_char.level.exp >= player_char.level.exp_to_gain and not player_char.max_level():
                player_char.level_up()
            if random.randint(0, player_char.check_mod('luck', luck_factor=10)):
                reward = items.random_item(player_char.level.pro_level + random.randint(0, player_char.level.pro_level))
                player_char.modify_inventory(reward, num=1)
                print(f"And you have been rewarded with a {reward().name}.")
            input("Press enter to continue")
        elif options[choice] == "Go Back":
            break
        else:
            raise AssertionError("You shouldn't reach here.")


def church(player_char):
    """

    """

    quests = {'Main': {40: {'The Power of Elysia Compels You!': {'Who': 'Priest',
                                                                 'Type': 'Defeat',
                                                                 'What': 'Wendigo',
                                                                 'Total': 1,
                                                                 'Start Text':
                                                                     "While the depths of the dungeon are home to many "
                                                                     "a horrible creature, the Wendigo is a curse to "
                                                                     "our very soul. Vanquish this monstrosity and "
                                                                     "Elysia will reward you with a boon.",
                                                                 'End Text':
                                                                     "Some order has been restored, although more work "
                                                                     "is to be done. Take this gift and use it to "
                                                                     "continue the good fight.",
                                                                 'Reward': [items.AardBeing],
                                                                 'Reward Number': 1,
                                                                 'Experience': 6000,
                                                                 'Completed': False,
                                                                 'Turned In': False}
                            }
                       },
              'Side': {}
              }
    check_quests(quests, player_char)
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Come in my child. You are always welcome in the arms of Elysia.")
        time.sleep(0.5)
        print("How can we be of service?")
        church_options = ['Promotion', 'Save', 'Quit Game', 'Leave']
        church_index = storyline.get_response(church_options)
        if church_options[church_index] == 'Promotion':
            if player_char.level.level // 20 > 0 and player_char.level.pro_level < 3:
                storyline.slow_type("You have qualified for a promotion.\n", typing_speed=125)
                classes.promotion(player_char)
                print("Let the light of Elysia guide you on your new path.")
            elif player_char.level.pro_level == 3:
                print("You are at max promotion level and can no longer be promoted.\n")
            else:
                print("You need to be at least level 20 before you can promote your character.\n")
            time.sleep(1)
        elif church_options[church_index] == 'Save':
            player_char.save()  # Can only save at church in town
        elif church_options[church_index] == 'Quit Game':
            q = player_char.game_quit()
            if q:
                return
        elif church_options[church_index] == 'Leave':
            print("Let the light of Elysia guide you.")
            time.sleep(1)
            break
        else:
            raise AssertionError("You shouldn't reach here.")


def secret_shop(player_char):
    """

    """

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("You have found me in this god forsaken place. Since you're here, you might as well buy some supplies.")
        time.sleep(0.5)
        buy_list = ['Weapon', 'OffHand', 'Armor', 'Accessory', 'Potion', 'Misc']
        print(f"You have {player_char.gold} gold.")
        print("Did you want to buy or sell?")
        option_list = ['Buy', 'Sell', 'Leave']
        opt_index = storyline.get_response(option_list)
        if option_list[opt_index] == 'Leave':
            print("We're sorry to see you go. Come back anytime!")
            time.sleep(1)
            player_char.move_south()
        else:
            if option_list[opt_index] == 'Buy':
                buy(player_char, buy_list, in_town=False)
            elif option_list[opt_index] == 'Sell':
                os.system('cls' if os.name == 'nt' else 'clear')
                done = False
                while not done:
                    done = sell(player_char)
                    time.sleep(0.5)
                    os.system('cls' if os.name == 'nt' else 'clear')
            else:
                print("Something went wrong.")
                time.sleep(1)
                player_char.move_south()


def ultimate_armor_repo(player_char):
    """

    """

    if "He Ain't Heavy" in player_char.quest_dict['Side']:
        player_char.quest_dict['Side']["He Ain't Heavy"]['Completed'] = True
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
        print(f"You have chosen for me to make you an immaculate {type_list[armor_typ].lower()} armor. Is this "
              f"correct?")
        confirm = storyline.get_response(["Yes", "No"])
        if not confirm:
            chosen = armor_list[armor_typ]
            print("Please wait while I craft your armor, it will only take a few moments.")
            time.sleep(3)
            print(f"I present to you the legendary armor, {chosen().name}!")
            player_char.modify_inventory(chosen, 1)
            looted = True
            time.sleep(2)
            print(f"Now that I have fulfilled my goal, I will leave this place. Goodbye, {player_char.name}!")
        else:
            print("You need time to consider you choice, I respect that. Come back when you have made your choice.")
        break
    time.sleep(1)
    player_char.move_south()
    os.system('cls' if os.name == 'nt' else 'clear')
    return looted


def buy(player_char, buy_list, in_town=True):
    """

    """

    print("Great! What would you like to buy?")
    time.sleep(0.5)
    if len(buy_list) > 2:
        buy_index = storyline.get_response(buy_list)
        if buy_list[buy_index] == "Go Back":
            return
    else:
        buy_index = 0
    cat_list = []
    for cat in items.items_dict[buy_list[buy_index]]:
        try:
            if cat in player_char.cls.restrictions[buy_list[buy_index]]:
                cat_list.append(cat)
        except KeyError:
            if (in_town and cat != 'Elixir') or not in_town:
                cat_list.append(cat)
    cat_list.append('Go Back')
    if len(cat_list) > 2:
        cat_index = storyline.get_response(cat_list)
        if cat_list[cat_index] == 'Go Back':
            return
    else:
        cat_index = 0
    while True:
        item_list = []
        item_options = []
        for item in items.items_dict[buy_list[buy_index]][cat_list[cat_index]]:
            diffs = []
            if item().restriction and player_char.cls not in item().restriction:
                continue
            if buy_list[buy_index] == 'Weapon':
                diff = str(item().damage - player_char.equipment[buy_list[buy_index]]().damage)
                if '-' not in diff:
                    diff = "+" + diff
                diffs.append(diff)
                if player_char.equipment['OffHand']().typ == 'Weapon':
                    diff_off = str(item().damage - player_char.equipment["OffHand"]().damage)
                    if '-' not in diff_off:
                        diff_off = "+" + diff_off
                    diffs.append(diff_off)
            elif buy_list[buy_index] == 'Armor':
                diff = str(item().armor - player_char.equipment[buy_list[buy_index]]().armor)
                if '-' not in diff:
                    diff = "+" + diff
                diffs.append(diff)
            elif buy_list[buy_index] == 'OffHand':
                if item().subtyp == 'Shield':
                    if player_char.equipment[buy_list[buy_index]]().subtyp == 'Shield':
                        diff = str(int((item().mod - player_char.equipment[buy_list[buy_index]]().mod) * 100)) + "%"
                    else:
                        diff = str(int(item().mod * 100)) + "%"
                    if '-' not in diff:
                        diff = "+" + diff
                    diffs.append(diff)
                elif item().subtyp == 'Tome':
                    if player_char.equipment[buy_list[buy_index]]().subtyp == 'Tome':
                        diff = str(item().mod - player_char.equipment[buy_list[buy_index]]().mod)
                    else:
                        diff = str(item().mod)
                    if '-' not in diff:
                        diff = "+" + diff
                    diffs.append(diff)
                else:
                    diffs.append(False)
            else:
                diffs.append(False)
            try:
                diff_str = "/".join(diffs)
            except TypeError:
                diff_str = ""
            adj_cost = max(1, int(item().value - player_char.stats.charisma * 2))
            if in_town:
                if item().rarity >= 0.25:
                    if diff_str:
                        item_options.append(item().name + '  ' + diff_str + '  ' + str(adj_cost))
                    else:
                        item_options.append(item().name + '  ' + str(adj_cost))
                    item_list.append(item)
            else:
                if 0.1 <= item().rarity < 0.25:
                    if diff_str:
                        item_options.append(item().name + '  ' + diff_str + '  ' + str(adj_cost))
                    else:
                        item_options.append(item().name + '  ' + str(adj_cost))
                    item_list.append(item)
        item_options.append('Go Back')
        item_index = storyline.get_response(item_options)
        if item_options[item_index] == 'Go Back':
            break
        buy_item = item_list[item_index]
        buy_price = max(1, int(buy_item().value - (player_char.stats.charisma * 2)))
        if player_char.gold < buy_price:
            print("You do not have enough gold.")
            time.sleep(0.25)
        else:
            print(str(buy_item()))
            print(f"You have {player_char.gold} gold coins.")
            while True:
                try:
                    num = int(input(f"How many {buy_item().name}s would you like to buy? "))
                    if num * buy_price > player_char.gold:
                        print("You do not have enough money for that purchase.")
                    elif num == 0:
                        pass
                    elif not player_char.add_weight((buy_item, num)):
                        print("You cannot carry that much weight.")
                    else:
                        buy_price *= num
                        print(f"That will cost {buy_price} gold coins.")
                        print(f"Do you still want to buy {num} {buy_item().name}? ")
                        confirm = storyline.get_response(["Yes", "No"])
                        if not confirm:
                            player_char.gold -= buy_price
                            player_char.modify_inventory(buy_item, num=num, subtract=False)
                            print(f"{num} {buy_item().name} will be added to your inventory.")
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

    print("We could always use more product. What do you have to sell?")
    time.sleep(0.5)
    sell_list = []
    for key in player_char.inventory:
        if player_char.inventory[key][0]().rarity > 0:
            sell_list.append(key)
    if len(sell_list) == 0:
        print("You don't have anything to sell.")
        time.sleep(1)
        return True
    sell_list.append('Go Back')
    typ_index = storyline.get_response(sell_list)
    if sell_list[typ_index] == 'Go Back':
        return True
    sell_item = player_char.inventory[sell_list[typ_index]][0]
    sell_amt = player_char.inventory[sell_list[typ_index]][1]
    if sell_item().rarity < 0.25:
        print("Wow, that's something you don't see everyday!")
    print(f"You have {sell_amt} {sell_item().name} to sell.")
    while True:
        try:
            num = int(input("How many would you like to sell? "))
            if num <= sell_amt and num != 0:
                sale_price = int(0.5 * num * sell_item().value + (player_char.stats.charisma * 2))
                print(f"I'll give you {sale_price} gold coins for that.")
                print("Do you still want to sell? ")
                confirm = storyline.get_response(["Yes", "No"])
                if not confirm:
                    player_char.modify_inventory(player_char.inventory[sell_list[typ_index]][0], num=num,
                                                 subtract=True)
                    player_char.gold += sale_price
                    print(f"You sold {num} {sell_item().name} for {sale_price} gold.")
                else:
                    print("I am sorry to hear that. Come back when you have something you wish to "
                          "sell.")
            elif num == 0:
                pass
            else:
                print("You cannot sell more than you have.")
            input("Press enter to continue.")
            return False
        except ValueError:
            print("Please enter a valid number.")
            time.sleep(1)


def town(player_char):
    """

    """

    os.system('cls' if os.name == 'nt' else 'clear')
    locations = [barracks, tavern, church]
    town_options = ['Barracks', 'Tavern', 'Church', 'Shops', 'Dungeon', 'Character Menu']
    if player_char.warp_point:
        town_options.insert(5, 'Warp Point')
    storyline.slow_type("Welcome to the town of Silvana!\n")
    time.sleep(0.5)
    while True:
        if player_char.quit:
            break
        player_char.health.current = player_char.health.max
        player_char.mana.current = player_char.mana.max
        print("Where would you like to go?")
        town_index = storyline.get_response(town_options)
        if town_options[town_index] == 'Dungeon':
            print("You descend into the dungeon.")
            time.sleep(1)
            player_char.change_location(5, 10, 1)
            break
        if town_options[town_index] == 'Character Menu':
            os.system('cls' if os.name == 'nt' else 'clear')
            player_char.character_menu()
        elif town_options[town_index] == 'Shops':
            shops = ['Blacksmith', 'Armory', 'Alchemist', 'Jeweler', 'Go Back']
            shop_index = storyline.get_response(shops)
            if shops[shop_index] != 'Go Back':
                shop_locs = [blacksmith, armory, alchemist, jeweler]
                shop_locs[shop_index](player_char)
        elif town_options[town_index] == 'Warp Point':
            print(f"Hello, {player_char.name}. Do you want to warp down to level 5?")
            confirm = storyline.get_response(["Yes", "No"])
            if not confirm:
                if not player_char.world_dict[(3, 0, 5)].visited:
                    player_char.world_dict[(3, 0, 5)].visited = True
                    player_char.world_dict[(2, 0, 5)].near = True
                    player_char.world_dict[(4, 0, 5)].near = True
                    player_char.world_dict[(3, 1, 5)].near = True
                print("You step into the warp point, taking you deep into the dungeon.")
                player_char.world_dict[(3, 0, 5)].warped = True
                player_char.change_location(3, 0, 5)
            else:
                print("Not a problem, come back when you change your mind.")
            time.sleep(1)
            break
        else:
            locations[town_index](player_char)

        os.system('cls' if os.name == 'nt' else 'clear')
