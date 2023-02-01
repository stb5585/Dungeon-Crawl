###########################################
""" Town manager """

# Imports
import os
import time

import items
import storyline
import classes


# Functions
def shop_inventory():
    pass


def ultimate(player):
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
                   'Ninja Blades': items.Ninjato}
    make_list = []
    i = 0
    for typ, weapon in weapon_list.items():
        if typ == 'Staff':
            if 'Archbishop' == player.cls:
                weapon = weapon[0]
            else:
                weapon = weapon[1]
        if classes.equip_check(weapon, 'Weapon', player.cls):
            make_list.append((typ, i))
            i += 1
    make_list.append(('Not yet', i))
    while True:
        print('What type of weapon would you like me to make?')
        weapon_ind = storyline.get_response(make_list)
        break
    if make_list[weapon_ind][0] == 'Not yet':
        print("I am sorry to hear that...please come back if you change your mind.")
    else:
        weapon = weapon_list[make_list[weapon_ind][0]]
        if type(weapon) == list:
            if 'Archbishop' == player.cls:
                weapon = weapon[0]
            else:
                weapon = weapon[1]
        print("Give me a moment and I will make you an ultimate weapon...")
        time.sleep(5)
        print("I present to you, {}, the mighty {}!".format(player.name, weapon().name))
        player.modify_inventory(weapon, num=1)
        del player.inventory['UNOBTAINIUM']
    time.sleep(2)


def blacksmith(player):
    os.system('cls' if os.name == 'nt' else 'clear')
    shop_text = "Welcome to Griswold's! What can I do you for?"
    if 'UNOBTAINIUM' in list(player.inventory.keys()) and player.pro_level == 3:
        ultimate(player)
    buy_list = [('Weapon', 0), ('OffHand', 1)]
    shop(player, buy_list, shop_text)


def armory(player):
    os.system('cls' if os.name == 'nt' else 'clear')
    shop_text = "I have the finest armors for sale. Come in and look around."
    buy_list = [('Armor', 0)]
    shop(player, buy_list, shop_text)


def alchemist(player):
    os.system('cls' if os.name == 'nt' else 'clear')
    shop_text = "Welcome to Ye Olde Item Shoppe."
    buy_list = [('Potion', 0), ('Misc', 1)]
    shop(player, buy_list, shop_text)


def jeweler(player):
    os.system('cls' if os.name == 'nt' else 'clear')
    shop_text = "Come glimpse the finest jewelry in the land."
    buy_list = [('Accessory', 0)]
    shop(player, buy_list, shop_text)


def tavern(player):
    """
    Quests
    """
    print("Sorry but we are closed for construction. Come back once we are open!")
    time.sleep(1)


def church(player, wmap):
    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        print("Come in my child. You are always welcome in the arms of Elysia.")
        print("How can we be of service?")
        church_options = [('Promotion', 0), ('Save', 1), ('Quit', 2), ('Leave', 3)]
        church_index = storyline.get_response(church_options)
        if church_options[church_index][1] == 0:
            if player.level // 20 > 0 and player.pro_level < 3:
                print("You have qualified for a promotion. Which path would you like to follow?")
                classes.promotion(player)
                print("Let the light of Elysia guide you on your new path.")
            elif player.pro_level == 3:
                print("You are at max promotion level and can no longer be promoted.")
            else:
                print("You need to be at least level 20 before you can promote your character.")
            time.sleep(1)
        elif church_options[church_index][1] == 1:
            player.save(wmap)  # Can only save at church in town
        elif church_options[church_index][1] == 2:
            player.game_quit()
        elif church_options[church_index][1] == 3:
            print("Let the light of Elysia guide you.")
            time.sleep(1)
            break
        os.system('cls' if os.name == 'nt' else 'clear')


def secret_shop(player):
    os.system('cls' if os.name == 'nt' else 'clear')
    shop_text = "You have found me in this god forsaken place. Since you're here, you might as well buy some supplies."
    buy_list = [('Weapon', 0), ('OffHand', 1), ('Armor', 2), ('Accessory', 3), ('Potion', 4)]
    shop(player, buy_list, shop_text, in_town=False)
    player.location_y += 1


def shop(player, buy_list, shop_text, in_town=True):
    items_dict = items.items_dict
    while True:
        print(shop_text)
        print("You have {} gold.".format(player.gold))
        print("Did you want to buy or sell?")
        option_list = [('Buy', 0), ('Sell', 1), ('Leave', 2)]
        opt_index = storyline.get_response(option_list)
        if option_list[opt_index][0] == 'Leave':
            print("We're sorry to see you go. Come back anytime!")
            time.sleep(1)
            break
        elif option_list[opt_index][0] == 'Buy':
            print("Great! What would you like to buy?")
            if len(buy_list) > 1:
                buy_index = storyline.get_response(buy_list)
            else:
                buy_index = 0
            cat_list = []
            i = 0
            for cat in items_dict[buy_list[buy_index][0]]:
                cat_list.append((cat, i))
                i += 1
            cat_list.append(('Go back', i))
            cat_index = storyline.get_response(cat_list)
            if cat_list[cat_index][0] == 'Go back':
                continue
            item_list = []
            item_options = []
            i = 0
            for item in items_dict[buy_list[buy_index][0]][cat_list[cat_index][0]]:
                adj_cost = max(1, int(item().value - player.charisma * 2))
                if in_town:
                    if item().rarity < 35:
                        item_options.append((item().name + '  ' + str(adj_cost), i))
                        item_list.append(item)
                        i += 1
                else:
                    if 35 <= item().rarity <= 40:
                        item_options.append((item().name + '  ' + str(adj_cost), i))
                        item_list.append(item)
                        i += 1
            item_options.append(('Go back', i))
            item_index = storyline.get_response(item_options)
            if item_options[item_index][0] == 'Go back':
                continue
            buy_item = item_list[item_index]
            buy_price = max(1, int(buy_item().value - (player.charisma * 2)))
            if player.gold < buy_price:
                print("You do not have enough gold.")
                time.sleep(0.25)
            else:
                print("You have {} gold coins.".format(player.gold))
                while True:
                    try:
                        num = int(input("How many {}s would you like to buy? ".format(buy_item().name)))
                        if num * buy_price > player.gold:
                            print("You do not have enough money for that purchase.")
                        elif num == 0:
                            break
                        else:
                            buy_price *= num
                            print("That will cost {} gold coins.".format(buy_price))
                            confirm = input("Do you still want to buy {} {}s? ".format(num, buy_item().name)).lower()
                            if confirm == 'y':
                                player.gold -= buy_price
                                player.modify_inventory(buy_item, num=num, sell=False)
                                print("{} {} will be added to your inventory.".format(num, buy_item().name))
                            else:
                                print("Sorry to hear that. Come back when you have something you wish to buy.")
                            break
                    except ValueError:
                        print("Please enter a valid number.")
                        input()
        elif option_list[opt_index][0] == 'Sell':
            print("We could always use more product. What do you have to sell?")
            sell_list = []
            i = 0
            for key in player.inventory.keys():
                if player.inventory[key][0]().rarity < 99:
                    sell_list.append((key, i))
                    i += 1
            if len(sell_list) == 0:
                print("You don't have anything to sell.")
                break
            sell_list.append(('Exit', i))
            typ_index = storyline.get_response(sell_list)
            if sell_list[typ_index][0] == 'Exit':
                break
            else:
                sell_item = player.inventory[sell_list[typ_index][0]][0]
                sell_amt = player.inventory[sell_list[typ_index][0]][1]
                if sell_item().rarity >= 50:
                    print("Wow, that's something you don't see everyday!")
                print("You have {} {} to sell.".format(sell_amt, sell_item().name))
                while True:
                    try:
                        num = int(input("How many would you like to sell? "))
                        if num <= sell_amt and num != 0:
                            sale_price = int(0.5 * num * sell_item().value + (player.charisma * 2))
                            print("I'll give you {} gold coins for that.".format(sale_price))
                            confirm = input("Do you still want to sell? ").lower()
                            if confirm == 'y':
                                player.modify_inventory(player.inventory[sell_list[typ_index][0]][0], num=num,
                                                        sell=True)
                                player.gold += sale_price
                                print("You sold {} {} for {} gold.".format(num, sell_item().name, sale_price))
                            else:
                                print("I am sorry to hear that. Come back when you have something you wish to sell.")
                            break
                        elif num == 0:
                            break
                        else:
                            print("You cannot sell more than you have.")
                    except ValueError:
                        print("Please enter a valid number.")
                        input()
        else:
            print("Please enter a valid option.")
        time.sleep(1)
        os.system('cls' if os.name == 'nt' else 'clear')


def town(player, wmap):
    os.system('cls' if os.name == 'nt' else 'clear')
    locations = [blacksmith, armory, alchemist, jeweler, church, tavern]
    town_options = [('Blacksmith', 0), ('Armory', 1), ('Alchemist', 2), ('Jeweler', 3), ('Church', 4), ('Tavern', 5),
                    ('Dungeon', 6), ('Status', 7)]
    while True:
        print("Welcome to the town of Silvana!")
        print("Where would you like to go?")
        town_index = storyline.get_response(town_options)
        if town_options[town_index][0] == 'Dungeon':
            print("You descend into the dungeon.")
            time.sleep(1)
            player.location_x, player.location_y, player.location_z = (5, 10, 1)
            break
        elif town_options[town_index][0] == 'Status':
            player.status()
        elif town_options[town_index][0] == 'Church':
            locations[town_index](player, wmap)
        else:
            locations[town_index](player)
        os.system('cls' if os.name == 'nt' else 'clear')
