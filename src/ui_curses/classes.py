"""
Curses UI-specific class selection and promotion logic.
Moved from core/classes.py to keep UI dependencies separate from core logic.
"""
import time


def choose_familiar(game):
    from src.ui_curses import menus as utils
    from src.core import companions

    fam_name = ""
    choose_dict = {
        "Homunculus": companions.Homunculus,
        "Fairy": companions.Fairy,
        "Mephit": companions.Mephit,
        "Jinkin": companions.Jinkin,
    }
    choose_list = list(choose_dict)
    promo_popup = utils.PromotionPopupMenu(
        game, "Select Familiar", "Mage", familiar=True
    )
    promo_popup.update_options(choose_list, choose_dict)
    fam_idx = promo_popup.navigate_popup()
    while fam_name == "":
        fam_name = utils.player_input(
            game, "What is your familiar's name?"
        ).capitalize()
        confirm_str = (
            f"You have chosen to name your familiar {fam_name}. Is this correct? "
        )
        confirm = utils.ConfirmPopupMenu(game, confirm_str, box_height=8)
        if not confirm.navigate_popup():
            fam_name = ""
    familiar = choose_dict[choose_list[fam_idx]]()
    familiar.name = fam_name
    return familiar


def promotion(game):
    from src.ui_curses import menus as utils
    from src.core.abilities import spell_dict, skill_dict
    from src.core.classes import apply_promotion_ability_rules, classes_dict
    from src.core import companions

    pro_message = "Choose your path"
    pro1_dict = {
        cls_dict["class"]().name: [
            pro["class"]()
            for name, pro in cls_dict["pro"].items()
            if name in game.player_char.race.cls_res["First"]
        ]
        for cls_dict in classes_dict.values()
    }
    pro2_dict = {
        sub_pro["class"]().name: [nested_pro["class"]()]
        for cls_dict in classes_dict.values()
        for sub_pro in cls_dict["pro"].values()
        for nested_pro in sub_pro.get("pro", {}).values()
    }
    current_class = game.player_char.cls.name
    class_options = []
    popup = utils.PromotionPopupMenu(game, pro_message, current_class)
    promobox = utils.TextBox(game)
    while True:
        if game.player_char.level.pro_level == 1:
            for cls in pro1_dict[current_class]:
                class_options.append(cls.name)
            class_options.append("Go Back")
            popup.update_options(class_options, pro1_dict)
            class_index = popup.navigate_popup()
            if class_options[class_index] == "Go Back":
                promo_str = "If you change your mind, you know where to find us.\n"
                break
            new_class = pro1_dict[current_class][class_index]
            confirm_str = (
                f"You have chosen to promote from {current_class} to {new_class.name}. Do you want to "
                "proceed?"
            )
        else:
            class_options = [pro2_dict[current_class][0].name, "Go Back"]
            popup.update_options(class_options, pro2_dict)
            class_index = popup.navigate_popup()
            if class_options[class_index] == "Go Back":
                promo_str = "If you change your mind, you know where to find us.\n"
                break
            new_class = pro2_dict[current_class][0]
            confirm_str = (
                f"You have chosen to promote from {current_class} to {new_class.name}. Do you want to "
                "proceed?"
            )
        confirm = utils.ConfirmPopupMenu(game, confirm_str, box_height=9)
        if confirm.navigate_popup():
            promo_str = (
                f"Congratulations! {game.player_char.name} has been promoted from a {current_class} to a "
                f"{new_class.name}!\n"
            )
            game.player_char.unequip(promo=True)
            promoted_player = game.player_char
            promoted_player.cls = new_class
            promoted_player.level.pro_level = new_class.pro_level
            promoted_player.level.level = 1
            promoted_player.level.exp_to_gain = game.player_char.level_exp()
            promoted_player.stats.strength += new_class.str_plus
            promoted_player.stats.intel += new_class.int_plus
            promoted_player.stats.wisdom += new_class.wis_plus
            promoted_player.stats.con += new_class.con_plus
            promoted_player.stats.charisma += new_class.cha_plus
            promoted_player.stats.dex += new_class.dex_plus
            promoted_player.health.max += new_class.con_plus * 2
            promoted_player.mana.max += new_class.int_plus * 2
            promoted_player.combat.attack += new_class.att_plus
            promoted_player.combat.defense += new_class.def_plus
            promoted_player.combat.magic += new_class.magic_plus
            promoted_player.combat.magic_def += new_class.magic_def_plus
            promoted_player.equipment["Weapon"] = new_class.equipment["Weapon"]
            promoted_player.equipment["Armor"] = new_class.equipment["Armor"]
            promoted_player.equipment["OffHand"] = new_class.equipment["OffHand"]
            # Apply ability transition rules for this promotion
            ability_change_msg = apply_promotion_ability_rules(promoted_player, new_class.name)
            promo_str += ability_change_msg
            if (
                str(promoted_player.level.level)
                in spell_dict[promoted_player.cls.name]
            ):
                spell_gain = spell_dict[promoted_player.cls.name][
                    str(promoted_player.level.level)
                ]()
                if spell_gain.name in promoted_player.spellbook["Spells"]:
                    promo_str += f"{spell_gain.name} goes up a level.\n"
                else:
                    promo_str += f"You have gained the spell {spell_gain.name}.\n"
                promoted_player.spellbook["Spells"][spell_gain.name] = spell_gain
            if (
                str(promoted_player.level.level)
                in skill_dict[promoted_player.cls.name]
            ):
                skill_gain = skill_dict[promoted_player.cls.name][
                    str(promoted_player.level.level)
                ]()
                if skill_gain.name in promoted_player.spellbook["Skills"]:
                    promo_str += f"{skill_gain.name} goes up a level.\n"
                else:
                    promo_str += f"You have gained the skill {skill_gain.name}.\n"
                promoted_player.spellbook["Skills"][skill_gain.name] = skill_gain
                if skill_gain.name in ["Transform", "Reveal", "Purity of Body"]:
                    skill_gain.use(promoted_player)
            if new_class.name == "Warlock":
                promoted_player.familiar = choose_familiar(game)
                promo_str += (
                    f"{promoted_player.familiar.name} the {promoted_player.familiar.spec} familiar has "
                    "joined your team!\n"
                )
            if new_class.name == "Summoner":
                summon = companions.Patagon()
                summon.initialize_stats(game.player_char)
                promoted_player.summons["Patagon"] = summon
                promo_str += "You have gained the summon Patagon.\n"
            if new_class.name in ["Seeker", "Wizard"]:
                promoted_player.teleport = (
                    promoted_player.location_x,
                    promoted_player.location_y,
                    promoted_player.location_z,
                )
        else:
            promo_str = "If you change your mind, you know where to find us.\n"
        break
    promobox.print_text_in_rectangle(promo_str)
    time.sleep(1)
    game.stdscr.getch()
    promobox.clear_rectangle()
