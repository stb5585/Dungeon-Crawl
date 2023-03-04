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
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        if 'UNOBTAINIUM' in list(player.special_inventory.keys()):
            ultimate(player)
        print("Welcome to Griswold's! What can I do you for?")
        time.sleep(0.5)
        buy_list = ['Weapon', 'OffHand', 'Go Back']
        print("You have {} gold.".format(player.gold))
        print("Did you want to buy or sell?")
        option_list = ['Buy', 'Sell', 'Leave']
        opt_index = storyline.get_response(option_list)
        if option_list[opt_index] == 'Leave':
            print("We're sorry to see you go. Come back anytime!")
            time.sleep(1)
            return
        else:
            if option_list[opt_index] == 'Buy':
                buy(player, buy_list)
            elif option_list[opt_index] == 'Sell':
                sell(player)
            else:
                print("Something went wrong.")
                return


def armory(player):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("I have the finest armors for sale. Come in and look around.")
        time.sleep(0.5)
        buy_list = ['Armor', 'Go Back']
        print("You have {} gold.".format(player.gold))
        print("Did you want to buy or sell?")
        option_list = ['Buy', 'Sell', 'Leave']
        opt_index = storyline.get_response(option_list)
        if option_list[opt_index] == 'Leave':
            print("We're sorry to see you go. Come back anytime!")
            time.sleep(1)
            return
        else:
            if option_list[opt_index] == 'Buy':
                buy(player, buy_list)
            elif option_list[opt_index] == 'Sell':
                sell(player)
            else:
                print("Something went wrong.")
                return


def alchemist(player):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Welcome to Ye Olde Item Shoppe.")
        time.sleep(0.5)
        buy_list = ['Potion', 'Misc', 'Go Back']
        print("You have {} gold.".format(player.gold))
        print("Did you want to buy or sell?")
        option_list = ['Buy', 'Sell', 'Leave']
        opt_index = storyline.get_response(option_list)
        if option_list[opt_index] == 'Leave':
            print("We're sorry to see you go. Come back anytime!")
            time.sleep(1)
            return
        else:
            if option_list[opt_index] == 'Buy':
                buy(player, buy_list)
            elif option_list[opt_index] == 'Sell':
                sell(player)
            else:
                print("Something went wrong.")
                return


def jeweler(player):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Come glimpse the finest jewelry in the land.")
        time.sleep(0.5)
        buy_list = ['Accessory', 'Go Back']
        print("You have {} gold.".format(player.gold))
        print("Did you want to buy or sell?")
        option_list = ['Buy', 'Sell', 'Leave']
        opt_index = storyline.get_response(option_list)
        if option_list[opt_index] == 'Leave':
            print("We're sorry to see you go. Come back anytime!")
            time.sleep(1)
            return
        else:
            if option_list[opt_index] == 'Buy':
                buy(player, buy_list)
            elif option_list[opt_index] == 'Sell':
                sell(player)
            else:
                print("Something went wrong.")
                return


def tavern(player):
    """
    Quests
    """
    storyline.slow_type("Sorry but we are closed for construction. Come back once we are open!")
    time.sleep(1)


def church(player):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Come in my child. You are always welcome in the arms of Elysia.")
        time.sleep(0.5)
        print("How can we be of service?")
        church_options = ['Promotion', 'Save', 'Quit', 'Leave']
        church_index = storyline.get_response(church_options)
        if church_options[church_index] == 'Promotion':
            if player.level // 20 > 0 and player.pro_level < 3:
                storyline.slow_type("You have qualified for a promotion.\n")
                classes.promotion(player)
                print("Let the light of Elysia guide you on your new path.")
            elif player.pro_level == 3:
                print("You are at max promotion level and can no longer be promoted.\n")
            else:
                print("You need to be at least level 20 before you can promote your character.\n")
            time.sleep(1)
        elif church_options[church_index] == 'Save':
            player.save()  # Can only save at church in town
        elif church_options[church_index] == 'Quit':
            player.game_quit()
        elif church_options[church_index] == 'Leave':
            print("Let the light of Elysia guide you.")
            time.sleep(1)
            break


def secret_shop(player):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("You have found me in this god forsaken place. Since you're here, you might as well buy some supplies.")
        time.sleep(0.5)
        buy_list = ['Weapon', 'OffHand', 'Armor', 'Accessory', 'Potion', 'Misc']
        print("You have {} gold.".format(player.gold))
        print("Did you want to buy or sell?")
        option_list = ['Buy', 'Sell', 'Leave']
        opt_index = storyline.get_response(option_list)
        if option_list[opt_index] == 'Leave':
            print("We're sorry to see you go. Come back anytime!")
            time.sleep(1)
            player.location_y += 1
        else:
            if option_list[opt_index] == 'Buy':
                buy(player, buy_list, in_town=False)
            elif option_list[opt_index] == 'Sell':
                sell(player)
            else:
                print("Something went wrong.")
                time.sleep(1)
                player.location_y += 1


def ultimate_armor_repo(player):
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
            player.modify_inventory(chosen, 1)
            looted = True
            time.sleep(2)
            print("Now that I have fulfilled my goal, I will leave this place. Goodbye, {}!".format(player.name))
        else:
            print("You need time to consider you choice, I respect that. Come back when you have made your choice.")
        break
    time.sleep(1)
    player.location_y += 1
    os.system('cls' if os.name == 'nt' else 'clear')
    return looted


def buy(player, buy_list, in_town=True):
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
        print(cat_list[cat_index])
        for item in items.items_dict[buy_list[buy_index]][cat_list[cat_index]]:
            adj_cost = max(1, int(item().value - player.charisma * 2))
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
                        pass
                    else:
                        buy_price *= num
                        print("That will cost {} gold coins.".format(buy_price))
                        print("Do you still want to buy {} {}s? ".format(num, buy_item().name))
                        confirm = storyline.get_response(yes_no)
                        if yes_no[confirm] == 'Yes':
                            player.gold -= buy_price
                            player.modify_inventory(buy_item, num=num, sell=False)
                            print("{} {} will be added to your inventory.".format(num, buy_item().name))
                        else:
                            print("Sorry to hear that. Come back when you have something you wish to buy.")
                    input("Press enter to continue.")
                    return
                except ValueError:
                    print("Please enter a valid number.")
                    input()


def sell(player):
    yes_no = ['Yes', 'No']
    print("We could always use more product. What do you have to sell?")
    time.sleep(0.5)
    sell_list = []
    for key in player.inventory.keys():
        if player.inventory[key][0]().rarity < 99:
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
        sell_item = player.inventory[sell_list[typ_index]][0]
        sell_amt = player.inventory[sell_list[typ_index]][1]
        if sell_item().rarity >= 50:
            print("Wow, that's something you don't see everyday!")
        print("You have {} {} to sell.".format(sell_amt, sell_item().name))
        while True:
            try:
                num = int(input("How many would you like to sell? "))
                if num <= sell_amt and num != 0:
                    sale_price = int(0.5 * num * sell_item().value + (player.charisma * 2))
                    print("I'll give you {} gold coins for that.".format(sale_price))
                    print("Do you still want to sell? ")
                    confirm = storyline.get_response(yes_no)
                    if yes_no[confirm] == 'Yes':
                        player.modify_inventory(player.inventory[sell_list[typ_index]][0], num=num,
                                                sell=True)
                        player.gold += sale_price
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


def town(player):
    os.system('cls' if os.name == 'nt' else 'clear')
    locations = [blacksmith, armory, alchemist, jeweler, church, tavern]
    town_options = ['Blacksmith', 'Armory', 'Alchemist', 'Jeweler', 'Church', 'Tavern', 'Dungeon', 'Character Menu']
    storyline.slow_type("Welcome to the town of Silvana!\n")
    time.sleep(0.5)
    while True:
        print("Where would you like to go?")
        town_index = storyline.get_response(town_options)
        if town_options[town_index] == 'Dungeon':
            print("You descend into the dungeon.")
            time.sleep(1)
            player.location_x, player.location_y, player.location_z = (5, 10, 1)
            break
        elif town_options[town_index] == 'Character Menu':
            os.system('cls' if os.name == 'nt' else 'clear')
            player.character_menu()
        elif town_options[town_index] == 'Church':
            locations[town_index](player)
        else:
            locations[town_index](player)
        os.system('cls' if os.name == 'nt' else 'clear')
