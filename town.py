###########################################
""" Town manager """

# Imports
import time

import items
import storyline


def blacksmith(player):
    print("Welcome to Griswold's! What can I do you for?")
    weapon_options = [('Weapon', 0), ('OffHand', 1)]
    weapon_index = storyline.get_response(weapon_options)
    shop_inventory = items.items_dict[weapon_options[weapon_index][0]][0]
    shop(shop_inventory, player)


def armory(player):
    print("I have the finest armors for sale. Come in and look around.")
    shop_inventory = items.items_dict['Armor'][0]
    shop(shop_inventory, player)


def alchemist(player):
    print("Welcome to Ye Olde Item Shoppe.")
    shop_inventory = items.items_dict['Potion'][0]
    shop(shop_inventory, player)


def church(player):
    print("Come in my child. Let the light of Elysia guide you.")
    print("How can we be of service?")
    church_options = [('Save', 0), ('Quit', 1)]
    church_index = storyline.get_response(church_options)
    if church_options[church_index][1] == 0:
        player.save()
    elif church_options[church_index][1] == 1:
        player.game_quit()


def shop(shop_inventory, player):
    time.sleep(0.25)
    while True:
        print("Did you want to buy or sell?")
        option_list = [('Buy', 0), ('Sell', 1), ('Leave', 2)]
        opt_index = storyline.get_response(option_list)
        if option_list[opt_index][0] == 'Leave':
            print("We're sorry to see you go. Come back anytime!")
            break
        elif option_list[opt_index][0] == 'Buy':
            print("Great! What would you like to buy?")
            buy_list = []
            i = 0
            for item in shop_inventory:
                buy_list.append((item().name, i))
                i += 1
            buy_index = storyline.get_response(buy_list)
            buy_item = shop_inventory[buy_index]
            print(buy_item())
            input()
            # print("%s costs %s gold coins." % (buy_item().name, buy_item().value))
            if player.gold < buy_item().value:
                print("You do not have enough gold.")
                time.sleep(0.25)
            else:
                print("You have %s gold coins." % player.gold)
                while True:
                    try:
                        num = int(input("How many would you like to buy? "))
                        if num * buy_item().value > player.gold:
                            print("You do not have enough money for that purchase.")
                        elif num == 0:
                            break
                        else:
                            buy_price = num * buy_item().value
                            print("That will cost %s gold coins." % buy_price)
                            confirm = input("Do you still want to buy? ").lower()
                            if confirm == 'y':
                                player.gold -= num * buy_item().value
                                player.modify_inventory(buy_item, num=num, sell=False)
                                print("%s %s will be added to your inventory." % (num, buy_item().name))
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
                print(sell_item())
                input()
                print("You have %s %s to sell." %
                      (sell_amt, sell_item().name))
                while True:
                    try:
                        num = int(input("How many would you like to sell? "))
                        if num <= sell_amt:
                            sale_price = int(0.5 * num * sell_item().value)
                            print("I'll give you %s gold coins for that." % sale_price)
                            confirm = input("Do you still want to sell? ").lower()
                            if confirm == 'y':
                                player.modify_inventory(player.inventory[sell_list[typ_index][0]][0], num=num,
                                                        sell=True)
                                player.gold += sale_price
                                print("You sold %s %s for %s gold." % (num, sell_item().name, sale_price))
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


def town(player):
    print("Welcome to the town of Silvana!")
    time.sleep(0.25)
    locations = [blacksmith, armory, alchemist, church]
    town_options = [('Blacksmith', 0), ('Armory', 1), ('Alchemist', 2), ('Church', 3), ('Dungeon', 4)]
    while True:
        town_index = storyline.get_response(town_options)
        if town_options[town_index][1] == 4:
            player.location_x, player.location_y, player.location_z = (5, 10, 1)
            break
        else:
            locations[town_index](player)
