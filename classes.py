###########################################
""" class manager """

# Imports
import time
from textwrap import wrap

import items
import utils


# Functions
def equip_check(item, cls, equip_slot):
    """
    Checks if the class allows the item type to be equipped
    """

    item = item if type(item) != type else item()
    if equip_slot in ["Ring", "Pendant"]:
        if item.subtyp == equip_slot:
            return True
        return False
    if item.subtyp in cls.restrictions[equip_slot]:
        if item.restriction:
            if cls.name not in item.restriction:
                return False
        return True
    return False


def choose_familiar(game):
    import companions
    fam_name = ''
    choose_dict = {"Homunculus": companions.Homunculus,
                   "Fairy": companions.Fairy,
                   "Mephit": companions.Mephit,
                   "Jinkin": companions.Jinkin}
    choose_list = list(choose_dict)
    promo_popup = utils.PromotionPopupMenu(game, "Select Familiar", "Mage", familiar=True)
    promo_popup.update_options(choose_list, choose_dict)
    fam_idx = promo_popup.navigate_popup()
    while fam_name == '':
        fam_name = utils.player_input(game, "What is your familiar's name?").capitalize()
        confirm_str = f"You have chosen to name your familiar {fam_name}. Is this correct? "
        confirm = utils.ConfirmPopupMenu(game, confirm_str, box_height=8)
        if not confirm.navigate_popup():
            fam_name = ''
    familiar = choose_dict[choose_list[fam_idx]]()
    familiar.name = fam_name
    return familiar


def promotion(game):
    pro_message = "Choose your path"
    pro1_dict = {cls_dict['class']().name: 
                 [pro['class']() for name, pro in cls_dict['pro'].items() 
                  if name in game.player_char.race.cls_res['First']]
                 for cls_dict in classes_dict.values()}
    pro2_dict = {
        sub_pro['class']().name: [nested_pro['class']()]
        for cls_dict in classes_dict.values()
        for sub_pro in cls_dict['pro'].values()
        for nested_pro in sub_pro.get('pro', {}).values()
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
            confirm_str = (f"You have chosen to promote from {current_class} to {new_class.name}. Do you want to "
                           "proceed?")
        else:
            class_options = [pro2_dict[current_class][0].name, "Go Back"]
            popup.update_options(class_options, pro2_dict)
            class_index = popup.navigate_popup()
            if class_options[class_index] == "Go Back":
                promo_str = "If you change your mind, you know where to find us.\n"
                break
            new_class = pro2_dict[current_class][0]
            confirm_str = (f"You have chosen to promote from {current_class} to {new_class.name}. Do you want to "
                           "proceed?")
        confirm = utils.ConfirmPopupMenu(game, confirm_str, box_height=9)
        if confirm.navigate_popup():
            import abilities
            promo_str = (f"Congratulations! {game.player_char.name} has been promoted from a {current_class} to a "
                         f"{new_class.name}!\n")
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
            promoted_player.health.max += (new_class.con_plus * 2)
            promoted_player.mana.max += (new_class.int_plus * 2)
            promoted_player.combat.attack += new_class.att_plus
            promoted_player.combat.defense += new_class.def_plus
            promoted_player.combat.magic += new_class.magic_plus
            promoted_player.combat.magic_def += new_class.magic_def_plus
            promoted_player.equipment['Weapon'] = new_class.equipment['Weapon']
            promoted_player.equipment['Armor'] = new_class.equipment['Armor']
            promoted_player.equipment['OffHand'] = new_class.equipment['OffHand']
            if new_class.name == 'Warlock':
                promoted_player.spellbook['Spells'] = {"Enfeeble": abilities.Enfeeble()}
                promo_str += "You lose all previously learned attack spells.\n"
            elif new_class.name in ['Monk', "Ranger"]:
                promoted_player.spellbook['Spells'] = {}
                promo_str += "You lose all previously learned spells.\n"
            elif new_class.name == 'Weapon Master':
                del promoted_player.spellbook['Skills']['Shield Slam']
                promo_str += "You lose the skill Shield Slam.\n"
            elif new_class.name == 'Inquisitor':
                for skill in ["Backstab", "Smoke Screen", "Pocket Sand", "Kidney Punch", "Steal", "Sleeping Powder"]:
                    if skill in promoted_player.spellbook["Skills"]:
                        del promoted_player.spellbook['Skills'][skill]
                promo_str += "You lose the all stealth skills.\n"
            if str(promoted_player.level.level) in abilities.spell_dict[promoted_player.cls.name]:
                spell_gain = abilities.spell_dict[promoted_player.cls.name][str(promoted_player.level.level)]()
                if spell_gain.name in promoted_player.spellbook['Spells']:
                    promo_str += f"{spell_gain.name} goes up a level.\n"
                else:
                    promo_str += f"You have gained the spell {spell_gain.name}.\n"
                promoted_player.spellbook['Spells'][spell_gain.name] = spell_gain
            if str(promoted_player.level.level) in abilities.skill_dict[promoted_player.cls.name]:
                skill_gain = abilities.skill_dict[promoted_player.cls.name][str(promoted_player.level.level)]()
                if skill_gain.name in promoted_player.spellbook['Skills']:
                    promo_str += f"{skill_gain.name} goes up a level.\n"
                else:
                    promo_str += f"You have gained the skill {skill_gain.name}.\n"
                promoted_player.spellbook['Skills'][skill_gain.name] = skill_gain
                if skill_gain.name in ["Transform", "Reveal", "Purity of Body"]:
                    skill_gain.use(promoted_player)
            if new_class.name == 'Warlock':
                promoted_player.familiar = choose_familiar(game)
                promo_str += (f"{promoted_player.familiar.name} the {promoted_player.familiar.spec} familiar has "
                              "joined your team!\n")
            if new_class.name == "Summoner":
                from companions import Patagon
                summon = Patagon()
                summon.initialize_stats(game.player_char)
                promoted_player.summons["Patagon"] = summon
                promo_str += "You have gained the summon Patagon.\n"
            if new_class.name in ['Seeker', 'Wizard']:
                promoted_player.teleport = (promoted_player.location_x,
                                            promoted_player.location_y,
                                            promoted_player.location_z)
        else:
            promo_str = "If you change your mind, you know where to find us.\n"
        break
    promobox.print_text_in_rectangle(promo_str)
    time.sleep(1)
    game.stdscr.getch()
    promobox.clear_rectangle()


# Classes
class Job:
    """
    Base definition for the class.
    *_plus describe the bonus at first level for each class (5 -> 6 -> 7 gain).
    equipment lists the items the player_char starts out with for the selected class.
    restrictions list the allowable item types the class can equip.
    """
    def __init__(self, name, description, str_plus, int_plus, wis_plus, con_plus, cha_plus, dex_plus,
                 att_plus, def_plus, magic_plus, magic_def_plus, equipment, restrictions, pro_level):
        self.name = name
        self.description = "\n".join(wrap(description, 75, break_on_hyphens=False))
        self.str_plus = str_plus
        self.int_plus = int_plus
        self.wis_plus = wis_plus
        self.con_plus = con_plus
        self.cha_plus = cha_plus
        self.dex_plus = dex_plus
        self.att_plus = att_plus
        self.def_plus = def_plus
        self.magic_plus = magic_plus
        self.magic_def_plus = magic_def_plus
        self.equipment = equipment
        self.restrictions = restrictions
        self.pro_level = pro_level


class Warrior(Job):
    """
    Promotion: Warrior -> Weapon Master -> Berserker
                       |
                       -> Paladin       -> Crusader
                       |
                       -> Lancer        -> Dragoon
                       |
                       -> Sentinel      -> Stalwart Defender
    """

    def __init__(self):
        super().__init__(name="Warrior", description="Warriors are weapon specialists that rely on strength and "
                                                     "defense. While unable to cast spells, they have access to a wide"
                                                     " variety of combat skills that make them deadly in combat. The "
                                                     "most stout of the bass classes, this character is best for "
                                                     "someone who wants to hack and slash their way through the game.",
                         str_plus=2, int_plus=0, wis_plus=0, con_plus=2, cha_plus=0, dex_plus=1,
                         att_plus=3, def_plus=2, magic_plus=0, magic_def_plus=1,
                         equipment={'Weapon': items.Rapier(), 'OffHand': items.Aspis(),
                                    'Armor': items.HideArmor(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Dagger', 'Sword', "Club", 'Longsword', "Battle Axe", 'Hammer'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Light', 'Medium', 'Heavy']},
                         pro_level=1)


class WeaponMaster(Job):
    """
    Promotion: Warrior -> Weapon Master -> Berserker
    Pros: Can dual wield some one handed weapons; higher dexterity gain
    Cons: Cannot use shields or heavy armor; lower constitution gain
    """

    def __init__(self):
        super().__init__(name="Weapon Master", description="Weapon Masters focus on the mastery of weapons and their"
                                                           " skill with them. They can equip many weapons and learn "
                                                           "the ability to dual wield one-handed weapons. Since Weapon"
                                                           " Masters really on dexterity, they lose the ability to "
                                                           "wear heavy armor and shields.",
                         str_plus=3, int_plus=0, wis_plus=0, con_plus=1, cha_plus=0, dex_plus=2,
                         att_plus=4, def_plus=2, magic_plus=0, magic_def_plus=2,
                         equipment={'Weapon': items.DoubleAxe(), 'OffHand': items.NoOffHand(), 
                                    'Armor': items.ScaleMail(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Sword', "Club",
                                                  'Longsword', "Battle Axe", 'Hammer'],
                                       'OffHand': ['Fist', 'Dagger', 'Sword', "Club"],
                                       'Armor': ['Light', 'Medium']},
                         pro_level=2)



class Berserker(Job):
    """
    Promotion: Warrior -> Weapon Master -> Berserker
    Additional Pros: Can dual wield 2-handed weapons; additional charisma gain
    Additional Cons: Can only equip light armor
    """

    def __init__(self):
        super().__init__(name="Berserker", description="Berserkers are combat masters, driven by pure rage and "
                                                       "vengeance. Their strength is so great, they gain the "
                                                       "ability to dual wield two-handed weapons. Their further "
                                                       "reliance on maneuverability limits the type of armor to light "
                                                       "armor.",
                         str_plus=3, int_plus=0, wis_plus=0, con_plus=1, cha_plus=1, dex_plus=2,
                         att_plus=5, def_plus=2, magic_plus=0, magic_def_plus=3,
                         equipment={'Weapon': items.Parashu(), 'OffHand': items.Changdao(),
                                    'Armor': items.StuddedLeather(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Longsword', "Battle Axe", 'Hammer'],
                                       'OffHand': ['Longsword', "Battle Axe", 'Hammer'],
                                       'Armor': ['Light']},
                         pro_level=3)



class Paladin(Job):
    """
    Promotion: Warrior -> Paladin -> Crusader
    Pros: Can cast healing spells; additional wisdom and charisma gain
    Cons: Cannot equip 2-handed weapons except hammers and cannot equip light armor; no dex and lower strength gain
    """

    def __init__(self):
        super().__init__(name="Paladin", description="The Paladin is a holy knight, crusading in the name of good and "
                                                     "order. Gaining some healing and damage spells, paladins become a"
                                                     " more balanced class and are ideal for players who always forget"
                                                     " to restock health potions.",
                         str_plus=1, int_plus=0, wis_plus=2, con_plus=2, cha_plus=1, dex_plus=0,
                         att_plus=2, def_plus=2, magic_plus=2, magic_def_plus=2,
                         equipment={'Weapon': items.WarHammer(), 'OffHand': items.Glagwa(),
                                    'Armor': items.Splint(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Sword', "Club", 'Longsword', 'Hammer'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Medium', 'Heavy']},
                         pro_level=2)



class Crusader(Job):
    """
    Promotion: Warrior -> Paladin -> Crusader
    Additional Pros: additional strength gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(name="Crusader", description="The Crusader is a holy warrior, who values order and justice "
                                                      "above all else. Crusaders continue the path of the paladin, "
                                                      "fully embracing all aspects that carry over.",
                         str_plus=2, int_plus=0, wis_plus=2, con_plus=2, cha_plus=1, dex_plus=0,
                         att_plus=3, def_plus=3, magic_plus=2, magic_def_plus=2,
                         equipment={'Weapon': items.Pernach(), 'OffHand': items.KiteShield(),
                                    'Armor': items.PlateMail(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Sword', "Club", 'Longsword', 'Hammer'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Medium', 'Heavy']},
                         pro_level=3)



class Lancer(Job):
    """
    Promotion: Warrior -> Lancer -> Dragoon
    Pros: Can use polearms as 1-handed weapons; charisma gain
    Cons: Cannot equip other 2-handed weapons or dual wield; loses access to light armor
    Special Mechanic: Jump ability takes 2 turns to complete and is guaranteed to hit; during jump, cannot be target of
      melee attacks and gains dodge bonus against magic attacks
    """

    def __init__(self):
        super().__init__(name="Lancer", description="Lancers are typically more at home on the back of a horse but one"
                                                    " benefit this affords is the skill to wield a two-handed polearm "
                                                    "while also using a shield. They are also adept at leaping high "
                                                    "into the air and driving that polearm into their enemies.",
                         str_plus=2, int_plus=0, wis_plus=0, con_plus=2, cha_plus=1, dex_plus=1,
                         att_plus=3, def_plus=3, magic_plus=0, magic_def_plus=2,
                         equipment={'Weapon': items.Halberd(), 'OffHand': items.Glagwa(),
                                    'Armor': items.Splint(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Sword', 'Polearm'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Medium', 'Heavy']},
                         pro_level=2)



class Dragoon(Job):
    """
    Promotion: Warrior -> Lancer -> Dragoon
    Additional Pros: additional dex gain
    Additional Cons: Lose access to medium armor
    """

    def __init__(self):
        super().__init__(name="Dragoon", description="Masters of spears, lances, and polearms and gifted with "
                                                     "supernatural abilities, Dragoons have become legendary for their"
                                                     " grace and power. Their intense training, said to have been "
                                                     "passed down by the dragon riders of old, allows these warriors to"
                                                     " leap unnaturally high into the air and strike their foes with "
                                                     "deadly force from above.",
                         str_plus=2, int_plus=0, wis_plus=0, con_plus=2, cha_plus=1, dex_plus=2,
                         att_plus=4, def_plus=3, magic_plus=0, magic_def_plus=3,
                         equipment={'Weapon': items.Naginata(), 'OffHand': items.KiteShield(),
                                    'Armor': items.PlateMail(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Sword', 'Polearm'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Heavy']},
                         pro_level=3)



class Sentinel(Job):
    """
    Promotion: Warrior -> Sentinel -> Stalwart Defender
    Pros: increased constitution gain
    Cons: Can only wear heavy armor and cannot equip 2-handed weapons
    """

    def __init__(self):
        super().__init__(name="Sentinel", description="Masters of defensive tactics, Sentinels excels at enduring "
                                                      "heavy assaults. Equipped with impenetrable shields and an array"
                                                      " of defensive skills, this class specializes in mitigating "
                                                      "damage, taunting enemies, and bolstering the their resilience. "
                                                      "Their unique abilities allow them to a reflect enemy strikes, "
                                                      "and maintain a near-impervious stance against even the fiercest"
                                                      " foes.",
                         str_plus=2, int_plus=0, wis_plus=0, con_plus=3, cha_plus=0, dex_plus=1,
                         att_plus=1, def_plus=4, magic_plus=0, magic_def_plus=3,
                         equipment={'Weapon': items.Talwar(), 'OffHand': items.Glagwa(),
                                    'Armor': items.Splint(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Fist', 'Sword', 'Club'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Heavy']},
                         pro_level=2)



class StalwartDefender(Job):
    """
    Promotion: Warrior -> Sentinel -> Stalwart Defender
    Additional Pros: additional constitution gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(name="Stalwart Defender", description="The Stalwart Defender embodies unyielding resilience "
                                                               "and unmatched defensive mastery. These protectors are "
                                                               "immovable bastions, capable of absorbing devastating "
                                                               "blows and locking down enemies at will. With "
                                                               "impenetrable defenses and a commanding presence, "
                                                               "they are the epitome of strength and fortitude.",
                         str_plus=2, int_plus=0, wis_plus=0, con_plus=4, cha_plus=0, dex_plus=1,
                         att_plus=2, def_plus=5, magic_plus=0, magic_def_plus=4,
                         equipment={'Weapon': items.Shamshir(), 'OffHand': items.KiteShield(),
                                    'Armor': items.PlateMail(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Fist', 'Sword', 'Club'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Heavy']},
                         pro_level=3)


class Mage(Job):
    """
    Promotion: Mage -> Sorcerer    -> Wizard
                    |
                    -> Warlock     -> Shadowcaster
                    |
                    -> Spellblade  -> Knight Enchanter
                    |
                    -> Summoner    -> Grand Summoner 
    """

    def __init__(self):
        super().__init__(name="Mage", description="Mages possess exceptional aptitude for spell casting, able to "
                                                  "destroy an enemy with the wave of a finger. Weaker and more "
                                                  "vulnerable than any other class, they more than make up for it "
                                                  "with powerful magics.",
                         str_plus=0, int_plus=3, wis_plus=1, con_plus=0, cha_plus=1, dex_plus=0,
                         att_plus=0, def_plus=1, magic_plus=3, magic_def_plus=2,
                         equipment={'Weapon': items.Quarterstaff(), 'OffHand': items.NoOffHand(),
                                    'Armor': items.Tunic(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Dagger', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth']},
                         pro_level=1)



class Sorcerer(Job):
    """
    Promotion: Mage -> Sorcerer -> Wizard
    Pros: Earlier access to spells and access to higher level spells
    Cons: None
    """

    def __init__(self):
        super().__init__(name="Sorcerer", description="A Sorcerer is someone who practices magic derived from "
                                                      "supernatural, occult, or arcane sources. They spend most of "
                                                      "their life reading massive tomes to expand their "
                                                      "knowledge and the rest of the time applying that knowledge at "
                                                      "the expense of anything in their path.",
                         str_plus=0, int_plus=3, wis_plus=2, con_plus=0, cha_plus=1, dex_plus=0,
                         att_plus=0, def_plus=1, magic_plus=4, magic_def_plus=3,
                         equipment={'Weapon': items.SerpentStaff(), 'OffHand': items.NoOffHand(),
                                    'Armor': items.GoldCloak(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Dagger', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth']},
                         pro_level=2)



class Wizard(Job):
    """
    Promotion: Mage -> Sorcerer -> Wizard
    Additional Pros: Increased dex gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(name="Wizard", description="The Wizard is a master of arcane magic, unparalleled in their "
                                                    "magical ability. Being able to cast the most powerful spells makes"
                                                    " the wizard an ideal class for anyone who prefers to live fast "
                                                    "and die hard if not properly prepared.",
                         str_plus=0, int_plus=3, wis_plus=2, con_plus=0, cha_plus=1, dex_plus=1,
                         att_plus=0, def_plus=1, magic_plus=5, magic_def_plus=4,
                         equipment={'Weapon': items.RuneStaff(), 'OffHand': items.NoOffHand(),
                                    'Armor': items.CloakEnchantment(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Dagger', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth']},
                         pro_level=3)



class Warlock(Job):
    """
    Promotion: Mage -> Warlock -> Shadowcaster
    Pros: Higher charisma and constitution gain; access to additional skills; gains access to shadow spells and familiar
    Cons: Lower intelligence gain and limited access to higher level spells; lose access to learned arcane Mage spells
    Special Mechanic: gains familiar that sometimes acts in or out of combat
    """

    def __init__(self):
        super().__init__(name="Warlock", description="The Warlock specializes in the dark arts, forsaking the arcane "
                                                     "training learned as a Mage. However this focus unlocks powerful "
                                                     "abilities, including the ability to summon a familiar to aid "
                                                     "them.",
                         str_plus=0, int_plus=2, wis_plus=1, con_plus=1, cha_plus=2, dex_plus=0,
                         att_plus=1, def_plus=1, magic_plus=4, magic_def_plus=2,
                         equipment={'Weapon': items.Kris(), 'OffHand': items.BookShadows(),
                                    'Armor': items.GoldCloak(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Dagger', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth']},
                         pro_level=2)



class Shadowcaster(Job):
    """
    Promotion: Mage -> Warlock -> Shadowcaster
    Additional Pros: Increased wisdom gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(name="Shadowcaster", description="The Shadowcaster is highly attuned to the dark arts and can "
                                                          "conjure the most demonic of powers, including the practicing"
                                                          " of forbidden blood magic.",
                         str_plus=0, int_plus=2, wis_plus=2, con_plus=1, cha_plus=2, dex_plus=0,
                         att_plus=1, def_plus=1, magic_plus=5, magic_def_plus=3,
                         equipment={'Weapon': items.Rondel(), 'OffHand': items.DragonRouge(),
                                    'Armor': items.CloakEnchantment(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Dagger', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth']},
                         pro_level=3)



class Spellblade(Job):
    """
    Promotion: Mage -> Spellblade -> Knight Enchanter
    Pros: Adds melee damage based on mana percentage and level; higher strength and constitution gain; can equip swords
      and light armor
    Cons: Lower intelligence and wisdom gain; cannot equip staves; gains spells at a much slower pace
    """

    def __init__(self):
        super().__init__(name="Spellblade", description="The Spellblade combines a magical affinity with a higher level"
                                                        " of martial prowess from the other magical classes. While they"
                                                        " no longer gain many of the same arcane spells, the spellblade"
                                                        " has unlocked the ability to channel the learned magical power"
                                                        " through their blade to devastate enemies.",
                         str_plus=2, int_plus=1, wis_plus=0, con_plus=2, cha_plus=1, dex_plus=0,
                         att_plus=3, def_plus=1, magic_plus=2, magic_def_plus=2,
                         equipment={'Weapon': items.Talwar(), 'OffHand': items.BookShadows(),
                                    'Armor': items.Cuirboulli(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Dagger', 'Sword'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth', 'Light']},
                         pro_level=2)



class KnightEnchanter(Job):
    """
    Promotion: Mage -> Spellblade -> Knight Enchanter
    Additional Pros: adds armor based on intel and mana percentage; additional dex gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(name="Knight Enchanter", description="The Knight Enchanter uses their arcane powers to imbue"
                                                              " weapons and armor with magical enchantments that can "
                                                              "rival the most powerful fighter.",
                         str_plus=2, int_plus=1, wis_plus=0, con_plus=2, cha_plus=1, dex_plus=1,
                         att_plus=4, def_plus=1, magic_plus=2, magic_def_plus=3,
                         equipment={'Weapon': items.Shamshir(), 'OffHand': items.DragonRouge(),
                                    'Armor': items.StuddedLeather(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Dagger', 'Sword'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth', 'Light']},
                         pro_level=3)


class Summoner(Job):
    """
    Promotion: Mage -> Summoner -> Grand Summoner
    Pros: Increased charisma and dominion over powerful allies
    Cons: No longer gains attack spells and lower intelligence
    Special Mechanic: gains spells from Summon creatures when used enough times  TODO
    """

    def __init__(self):
        super().__init__(name="Summoner", description="The Summoner has dominion over distant realms, capable of "
                                                      "calling forth powerful creatures to aid them in battle. These "
                                                      "summoned entities range from ferocious beasts to mystical"
                                                      " elementals, each with unique abilities tailored to specific "
                                                      "combat needs. Summoners form bonds with their creatures, "
                                                      "allowing for synergistic strategies and unparalleled "
                                                      "versatility. Highly charismatic individuals will see the "
                                                      "greatest increase in summoning power.",
                         str_plus=0, int_plus=2, wis_plus=2, con_plus=0, cha_plus=2, dex_plus=0,
                         att_plus=0, def_plus=1, magic_plus=4, magic_def_plus=3,
                         equipment={'Weapon': items.SerpentStaff(), 'OffHand': items.NoOffHand(), 
                                    'Armor': items.GoldCloak(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Dagger', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth']},
                         pro_level=2)



class GrandSummoner(Job):
    """
    Promotion: Mage -> Summoner -> Grand Summoner
    Additional Pros: Summoned creatures have increased power
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(name="Grand Summoner", description="The Grand Summoner represents the pinnacle of summoning "
                                                            "mastery, channeling immense magical power to enhance "
                                                            "their summoned creatures. These legendary conjurers can "
                                                            "summon stronger, larger, and more formidable entities "
                                                            "than ever before, each imbued with enhanced abilities and"
                                                            " resilience. The bond between the Grand Summoner and "
                                                            "their creatures is unbreakable, allowing for precise "
                                                            "control and synergy.",
                         str_plus=0, int_plus=2, wis_plus=2, con_plus=0, cha_plus=3, dex_plus=0, 
                         att_plus=0, def_plus=2, magic_plus=4, magic_def_plus=4,
                         equipment={'Weapon': items.RuneStaff(), 'OffHand': items.NoOffHand(),
                                    'Armor': items.CloakEnchantment(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Dagger', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth']},
                         pro_level=3)


class Footpad(Job):
    """
    Promotion: Footpad -> Thief         -> Rogue
                       |
                       -> Inquisitor    -> Seeker
                       |
                       -> Assassin      -> Ninja
                       |
                       -> Spell Stealer -> Arcane Trickster
    """

    def __init__(self):
        super().__init__(name="Footpad", description="Footpads are agile and perceptive, with an natural ability of "
                                                     "deftness. While more than capable of holding their own in hand-"
                                                     "to-hand combat, they truly excel at subterfuge. Footpads are the"
                                                     " only base class that can dual wield, albeit the offhand weapon "
                                                     "must be a dagger.",
                         str_plus=0, int_plus=0, wis_plus=0, con_plus=1, cha_plus=2, dex_plus=2,
                         att_plus=2, def_plus=1, magic_plus=1, magic_def_plus=2,
                         equipment={'Weapon': items.Dirk(), 'OffHand': items.Dirk(),
                                    'Armor': items.PaddedArmor(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Sword', "Club"],
                                       'OffHand': ['Fist', 'Dagger'],
                                       'Armor': ['Light']},
                         pro_level=1)



class Thief(Job):
    """
    Promotion: Footpad -> Thief-> Rogue
    Pros: Access to stealth abilities earlier than other classes; gains bonus to damage from dex; increased
        intel gain
    Cons: None
    """

    def __init__(self):
        super().__init__(name="Thief", description="Thieves prefer stealth over brute force, although a well-placed "
                                                   "backstab is still highly effective. They gain stealth abilities "
                                                   "more quickly than other classes and are typically more well-"
                                                   "balanced.",
                         str_plus=0, int_plus=1, wis_plus=0, con_plus=1, cha_plus=2, dex_plus=2,
                         att_plus=2, def_plus=2, magic_plus=1, magic_def_plus=3,
                         equipment={'Weapon': items.Talwar(), 'OffHand': items.Kris(),
                                    'Armor': items.Cuirboulli(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Sword', "Club"],
                                       'OffHand': ['Fist', 'Dagger'],
                                       'Armor': ['Light']},
                         pro_level=2)



class Rogue(Job):
    """
    Promotion: Footpad -> Thief -> Rogue
    Additional Pros: Ability to dual wield swords and maces in offhand; increased dex gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(name="Rogue", description="Rogues rely on skill, stealth, and their foes' vulnerabilities to "
                                                   "get the upper hand in any situation. They have a knack for finding "
                                                   "the solution to just about any problem, demonstrating a "
                                                   "resourcefulness and versatility that has no rival. They gain the "
                                                   "ability to dual wield swords, maces, and fist weapons.",
                         str_plus=0, int_plus=1, wis_plus=0, con_plus=1, cha_plus=2, dex_plus=3,
                         att_plus=3, def_plus=2, magic_plus=2, magic_def_plus=3,
                         equipment={'Weapon': items.Shamshir(), 'OffHand': items.Rondel(),
                                    'Armor': items.StuddedLeather(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Sword', "Club"],
                                       'OffHand': ['Fist', 'Dagger', 'Sword', "Club"],
                                       'Armor': ['Light']},
                         pro_level=3)



class Inquisitor(Job):
    """
    Promotion: Footpad -> Inquisitor -> Seeker
    Pros: Increased strength and constitution gain; ability to perceive enemy status and weaknesses; access to medium
          armor, shields, and some spells; increased resistance to shadow damage
    Cons: Lower dexterity and charisma gain; lose ability to dual wield and stealth skills and access to fist weapons
    """

    def __init__(self):
        super().__init__(name="Inquisitor", description="Inquisitors exchange the stealth of the shadows for a pure"
                                                        "distain. They excel at rooting out hidden secrets and "
                                                        "unraveling mysteries. They rely on a sharp eye for detail, "
                                                        "but also on a finely honed ability to read the words and "
                                                        "deeds of other creatures to determine their true intent. "
                                                        "They excel at defeating creatures that hide in the shadows "
                                                        " and their mastery of lore and sharp eye make them "
                                                        "well-equipped to expose and end hidden evils.",
                         str_plus=2, int_plus=0, wis_plus=0, con_plus=2, cha_plus=1, dex_plus=1,
                         att_plus=2, def_plus=2, magic_plus=2, magic_def_plus=2,
                         equipment={'Weapon': items.Talwar(), 'OffHand': items.Glagwa(),
                                    'Armor': items.ScaleMail(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Dagger', 'Sword', "Club"],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Light', 'Medium']},
                         pro_level=2)



class Seeker(Job):
    """
    Promotion: Footpad -> Inquisitor -> Seeker
    Additional Pros: Additional intel gain
    Additional Cons: None
    """
    def __init__(self):
        super().__init__(name="Seeker", description="Seekers are very good at moving through the dungeon, being able to"
                                                    " levitate, locate other characters, and teleport. They can't "
                                                    "directly kill monsters with their magical abilities, but a Seeker "
                                                    "does well with a weapon in hand. They are also the best at "
                                                    "mapping the dungeon and detecting any types of 'anomalies' they "
                                                    "may encounter in the depths.",
                         str_plus=2, int_plus=1, wis_plus=0, con_plus=2, cha_plus=1, dex_plus=1,
                         att_plus=3, def_plus=2, magic_plus=2, magic_def_plus=3,
                         equipment={'Weapon': items.Shamshir(), 'OffHand': items.KiteShield(),
                                    'Armor': items.Breastplate(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Dagger', 'Sword', "Club"],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Light', 'Medium']},
                         pro_level=3)



class Assassin(Job):
    """
    Promotion: Footpad -> Assassin -> Ninja
    Pros: Higher dexterity and wisdom (magic defense); earlier access to skills and more powerful skills; can use fist
      weapons in the offhand slot; gains bonus to damage from dex
    Cons: Lower constitution; can only equip daggers or fist weapons
    """

    def __init__(self):
        super().__init__(name="Assassin", description="You focus your training on the grim art of death. Those who "
                                                      "adhere to this archetype are diverse: hired killers, spies, "
                                                      "bounty hunters, and even specially anointed priests trained to "
                                                      "exterminate  the enemies of their deity. Stealth, poison, and "
                                                      "disguise help you eliminate your foes with deadly efficiency.",
                         str_plus=0, int_plus=0, wis_plus=1, con_plus=0, cha_plus=2, dex_plus=3,
                         att_plus=3, def_plus=1, magic_plus=1, magic_def_plus=3,
                         equipment={'Weapon': items.Kris(), 'OffHand': items.Kris(),
                                    'Armor': items.Cuirboulli(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Fist', 'Dagger'],
                                       'OffHand': ['Fist', 'Dagger'],
                                       'Armor': ['Light']},
                         pro_level=2)



class Ninja(Job):
    """
    Promotion: Footpad -> Assassin -> Ninja
    Additional Pros: Gains access to class only Ninja Blade weapons
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(name="Ninja", description="Since a Ninja desires quickness, they are very specific about the "
                                                   "items they use. Ninjas are not allowed to wear most types of armor "
                                                   "and other items. However, having access to special weapons that "
                                                   "only they can use, Ninjas possess the skills of Critically hitting "
                                                   "and Backstabbing their opponents, along with moderate thieving "
                                                   "skills.",
                         str_plus=0, int_plus=0, wis_plus=2, con_plus=0, cha_plus=2, dex_plus=3,
                         att_plus=4, def_plus=1, magic_plus=1, magic_def_plus=4,
                         equipment={'Weapon': items.Tanto(), 'OffHand': items.Rondel(),
                                    'Armor': items.StuddedLeather(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Ninja Blade'],
                                       'OffHand': ['Fist', 'Dagger', 'Ninja Blade'],
                                       'Armor': ['Light']},
                         pro_level=3)


class SpellStealer(Job):
    """
    Promotion: Footpad -> Spell Stealer -> Arcane Trickster
    Pros: Intel and wisdom gain; can use Tomes in offhand and can wear cloth armor
    Cons: Lower dex and no constitution gain; lose access to fist and club weapons
    Special Mechanic: can steal magic from enemies  TODO
    """

    def __init__(self):
        super().__init__(name="Spell Stealer", description="The Spell Stealer is an elite evolution of the Footpad, "
                                                           "blending agility and cunning with mystical talent. Masters"
                                                           " of magical deception, they can cast a variety of spells "
                                                           "while uniquely able to steal magic from enemies. Spells "
                                                           "directed at them may be absorbed or reflected back at "
                                                           "their casters. Their versatility allows them to adapt to "
                                                           "both offensive and defensive situations, disrupting foes' "
                                                           "strategies while empowering themselves with stolen magic.",
                         str_plus=0, int_plus=2, wis_plus=1, con_plus=0, cha_plus=1, dex_plus=2,
                         att_plus=1, def_plus=1, magic_plus=4, magic_def_plus=2,
                         equipment={'Weapon': items.Kris(), 'OffHand': items.BookShadows(),
                                    'Armor': items.Cuirboulli(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Dagger', "Sword"],
                                       'OffHand': ['Dagger', "Tome"],
                                       'Armor': ["Cloth", 'Light']},
                         pro_level=2)



class ArcaneTrickster(Job):
    """
    Promotion: Footpad -> Spell Stealer -> Arcane Trickster
    Additional Pros: Increased intel gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(name="Arcane Trickster", description="The Arcane Trickster elevates the Spell Stealer's "
                                                              "cunning and arcane mastery to new heights. Adept at "
                                                              "weaving magic and subterfuge, these versatile "
                                                              "spellcasters manipulate the battlefield with illusions,"
                                                              " stealth, and devastating arcane strikes. Their ability"
                                                              " to enhance their physical attacks with magical force "
                                                              "and cast debilitating spells ensures they are as "
                                                              "dangerous in close quarters as from afar.",
                         str_plus=0, int_plus=3, wis_plus=1, con_plus=0, cha_plus=1, dex_plus=2,
                         att_plus=1, def_plus=1, magic_plus=5, magic_def_plus=3,
                         equipment={'Weapon': items.Rondel(), 'OffHand': items.DragonRouge(),
                                    'Armor': items.StuddedLeather(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Dagger', "Sword"],
                                       'OffHand': ['Dagger', "Tome"],
                                       'Armor': ["Cloth", 'Light']},
                         pro_level=3)


class Healer(Job):
    """
    Promotion: Healer -> Cleric -> Templar
                      |
                      -> Priest -> Archbishop
                      |
                      -> Monk   -> Master Monk
                      |
                      -> Bard   -> Troubadour

    """

    def __init__(self):
        super().__init__(name="Healer", description="Healers primary role in battle is to preserve the party with "
                                                    "healing and protective spells. Well, how does that work when "
                                                    "they are alone? Pretty much the same way!",
                         str_plus=0, int_plus=1, wis_plus=2, con_plus=1, cha_plus=1, dex_plus=0,
                         att_plus=1, def_plus=1, magic_plus=2, magic_def_plus=2,
                         equipment={'Weapon': items.Quarterstaff(), 'OffHand': items.NoOffHand(),
                                    'Armor': items.PaddedArmor(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ["Club", 'Staff'],
                                       'OffHand': ['Shield', 'Tome'],
                                       'Armor': ['Cloth', 'Light']},
                         pro_level=1)



class Cleric(Job):
    """
    Promotion: Healer -> Cleric -> Templar
    Pros: Can equip medium armor; gains additional protective abilities including turn undead; increased strength and
        constitution
    Cons: gains fewer healing spells compared to Priest class; no longer gains holy damage spells; lose access to tomes;
        lower intel gain
    """

    def __init__(self):
        super().__init__(name="Cleric", description="Where the paladin is a warrior that can heal, a cleric is a "
                                                    "healer that can hold their own in combat. The biggest difference"
                                                    " is that the cleric cannot equip heavy armor (yet...) but gain "
                                                    "additional protective abilities that paladins do not.",
                         str_plus=1, int_plus=0, wis_plus=2, con_plus=2, cha_plus=1, dex_plus=0,
                         att_plus=2, def_plus=2, magic_plus=2, magic_def_plus=2,
                         equipment={'Weapon': items.WarHammer(), 'OffHand': items.Glagwa(),
                                    'Armor': items.ScaleMail(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ["Club", 'Staff'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Light', 'Medium']},
                         pro_level=2)



class Templar(Job):
    """
    Promotion: Healer -> Cleric -> Templar
    Additional Pros: Can equip heavy armor and hammers; increased strength and dex gain
    Additional Cons: lose access to staff weapons; lower wisdom gain
    """

    def __init__(self):
        super().__init__(name="Templar", description="A templar exemplifies the best of both worlds, able to heal and"
                                                     " protect while also being able to dish out quite a bit of damage"
                                                     " along the way. While a templar is right at home with a mace and"
                                                     " a shield, they have also trained in the art of the 2-handed "
                                                     "hammer.",
                         str_plus=2, int_plus=0, wis_plus=1, con_plus=2, cha_plus=1, dex_plus=1,
                         att_plus=3, def_plus=2, magic_plus=2, magic_def_plus=3,
                         equipment={'Weapon': items.Pernach(), 'OffHand': items.KiteShield(),
                                    'Armor': items.PlateMail(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ["Club", 'Hammer'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Light', 'Medium', 'Heavy']},
                         pro_level=3)



class Priest(Job):
    """
    Promotion: Healer -> Priest -> Archbishop
    Pros: Access to the best healing and holy spells; only class that can equip the holy staff except Archbishop;
        increased intel and wisdom gain
    Cons: Can only equip cloth armor; lose access to shields; lower constitution gain
    """

    def __init__(self):
        super().__init__(name="Priest", description="A priest channels the holy light through prayer, accessing "
                                                    "powerful regenerative and cleansing spells. While they can only "
                                                    "equip cloth armor, they gain the ability to increase their "
                                                    "defense at the expense of mana.",
                         str_plus=0, int_plus=2, wis_plus=3, con_plus=0, cha_plus=1, dex_plus=0,
                         att_plus=0, def_plus=2, magic_plus=3, magic_def_plus=3,
                         equipment={'Weapon': items.SerpentStaff(), 'OffHand': items.NoOffHand(),
                                    'Armor': items.GoldCloak(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ["Club", 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth']},
                         pro_level=2)



class Archbishop(Job):
    """
    Promotion: Healer -> Priest -> Archbishop
    Additional Pros: Only class that can create and equip the Princess Guard; increased intel gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(name="Archbishop", description="An archbishop attunes with the holy light for the most "
                                                        "powerful healing, protective, and holy magics available.",
                         str_plus=0, int_plus=3, wis_plus=3, con_plus=0, cha_plus=1, dex_plus=0,
                         att_plus=1, def_plus=2, magic_plus=4, magic_def_plus=3,
                         equipment={'Weapon': items.HolyStaff(), 'OffHand': items.NoOffHand(),
                                    'Armor': items.CloakEnchantment(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ["Club", 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth']},
                         pro_level=3)



class Monk(Job):
    """
    Promotion: Healer -> Monk -> Master Monk
    Pros: Adds wisdom to damage rolls; gains special skills; increased strength and dex gain
    Cons: Can only wear light armor; loses access to spells; lower intel and wisdom gain
    """

    def __init__(self):
        super().__init__(name="Monk", description="Monks abandon the cloth to focus the mind into the body, harnessing "
                                                  "the inner power of the chi. Monks specialize in hand-to-hand combat,"
                                                  " adding both strength and wisdom to their melee damage.",
                         str_plus=2, int_plus=0, wis_plus=1, con_plus=1, cha_plus=1, dex_plus=1,
                         att_plus=3, def_plus=2, magic_plus=1, magic_def_plus=2,
                         equipment={'Weapon': items.Cestus(), 'OffHand': items.Cestus(),
                                    'Armor': items.Cuirboulli(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Fist', 'Staff'],
                                       'OffHand': ['Fist'],
                                       'Armor': ['Light']},
                         pro_level=2)



class MasterMonk(Job):
    """
    Promotion: Healer -> Monk -> Master Monk
    Additional Pros: increased constitution gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(name="Master Monk", description="A master monk has fully attuned to the power of the chi, "
                                                         "becoming unparalleled at dealing damage with fists or a "
                                                         "staff.",
                         str_plus=2, int_plus=0, wis_plus=1, con_plus=2, cha_plus=1, dex_plus=1,
                         att_plus=4, def_plus=2, magic_plus=1, magic_def_plus=3,
                         equipment={'Weapon': items.BattleGauntlet(), 'OffHand': items.BattleGauntlet(),
                                    'Armor': items.StuddedLeather(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Fist', 'Staff'],
                                       'OffHand': ['Fist'],
                                       'Armor': ['Light']},
                         pro_level=3)



class Bard(Job):
    """
    Promotion: Healer -> Bard -> Troubadour
    Pros: Gain access to musical instruments, can dual wield daggers; gains songs that have affects in and out of
      combat; increased strength and dex gain
    Cons: Lose access to certain priest spells; lower wisdom gain
    Special Mechanic: Plays songs that boost self, hurt foes, or affects actions out of combat  TODO
    """

    def __init__(self):
        super().__init__(name="Bard", description="The Bard is a master of performance and inspiration, blending "
                                                  "healing arts with the power of music and storytelling. They can "
                                                  "weave enchanting melodies to bolster their own strength, restore "
                                                  "health, and demoralize enemies. Bards excel at turning the tide of "
                                                  "battle through clever improvisation, crowd control, and "
                                                  "spellcasting.",
                         str_plus=1, int_plus=1, wis_plus=1, con_plus=1, cha_plus=1, dex_plus=1,
                         att_plus=1, def_plus=1, magic_plus=3, magic_def_plus=3,
                         equipment={'Weapon': items.Kris(), 'OffHand': items.Lute(),
                                    'Armor': items.Cuirboulli(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ["Dagger", "Sword", "Staff"],
                                       'OffHand': ["Dagger", "Musical Instrument"],
                                       'Armor': ["Cloth", 'Light']},
                         pro_level=2)



class Troubadour(Job):
    """
    Promotion: Healer -> Bard -> Troubadour
    Additional Pros: Increased dex gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(name="Troubadour", description="The Troubadour is the pinnacle of the Bard's art, a legendary"
                                                        " performer who wields songs and stories with unmatched "
                                                        "mastery. Their melodies amplify their abilities, granting "
                                                        "powerful buffs and healing over time, while their sharp wit "
                                                        "and magical harmonies sow discord among foes. They are "
                                                        "paragons of charisma, seamlessly blending support, "
                                                        "enchantment, and clever combat tricks to uplift their "
                                                        "companions and ensure victory through the power of "
                                                        "performance.",
                         str_plus=1, int_plus=1, wis_plus=1, con_plus=1, cha_plus=1, dex_plus=2,
                         att_plus=1, def_plus=2, magic_plus=4, magic_def_plus=3,
                         equipment={'Weapon': items.Rondel(), 'OffHand': items.Lyre(),
                                    'Armor': items.StuddedLeather(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ["Dagger", "Sword", "Staff"],
                                       'OffHand': ["Dagger", "Musical Instrument"],
                                       'Armor': ["Cloth", 'Light']},
                         pro_level=3)


class Pathfinder(Job):
    """
    Promotion: Pathfinder -> Druid   -> Lycan
                          |
                          -> Diviner -> Geomancer
                          |
                          -> Shaman  -> Soulcatcher
                          |
                          -> Ranger  -> Beast Master
    """

    def __init__(self):
        super().__init__(name="Pathfinder", description="In philosophy, naturalism is the belief that only natural laws"
                                                        " and forces operate in the universe. A pathfinder embraces "
                                                        "this idea by being attuned to one or more of the various "
                                                        "aspects of nature, mainly the 4 classical elements: Earth, "
                                                        "Wind, Water, and Fire.",
                         str_plus=0, int_plus=1, wis_plus=1, con_plus=1, cha_plus=1, dex_plus=1,
                         att_plus=1, def_plus=1, magic_plus=2, magic_def_plus=2,
                         equipment={'Weapon': items.Dirk(), 'OffHand': items.Buckler(),
                                    'Armor': items.HideArmor(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Dagger', "Club", 'Polearm', 'Hammer', 'Staff'],
                                       'OffHand': ['Shield', 'Tome'],
                                       'Armor': ['Cloth', 'Light', 'Medium']},
                         pro_level=1)



class Druid(Job):
    """
    Promotion: Pathfinder -> Druid -> Lycan
    Pros: gains animal abilities and statistics when shifted; increased strength and dex gain
    Cons: loses ability to wear medium armor and shields; lower intel gain
    """

    def __init__(self):
        super().__init__(name="Druid", description="Druids act as an extension of nature to call upon the elemental"
                                                   " forces, embodying nature's wrath and mystique. This attunement "
                                                   "with nature allows druids to emulate creatures of the animal world,"
                                                   " transforming into them and gaining there specs and abilities. They"
                                                   " lose the ability to wear medium armor and shields but gain "
                                                   "natural weapons and armor when transformed.",
                         str_plus=1, int_plus=0, wis_plus=1, con_plus=1, cha_plus=1, dex_plus=2,
                         att_plus=2, def_plus=2, magic_plus=2, magic_def_plus=2,
                         equipment={'Weapon': items.SerpentStaff(), 'OffHand': items.NoOffHand(),
                                    'Armor': items.Cuirboulli(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Dagger', "Club", 'Polearm', 'Hammer', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth', 'Light']},
                         pro_level=2)



class Lycan(Job):
    """
    Promotion: Pathfinder -> Druid -> Lycan
    Additional Pros: Can learn to transform into Red Dragon; increased constitution gain
    Additional Cons: None
    Special Mechanic: Can shapeshift into alternative forms
    """

    def __init__(self):
        super().__init__(name="Lycan", description="Unlike the lycans of mythology who have little choice in morphing "
                                                   "into their animal form, these lycans have gained mastery over their"
                                                   " powers to become something truly terrifying.",
                         str_plus=1, int_plus=0, wis_plus=1, con_plus=2, cha_plus=1, dex_plus=2,
                         att_plus=3, def_plus=2, magic_plus=2, magic_def_plus=3,
                         equipment={'Weapon': items.Maul(), 'OffHand': items.NoOffHand(),
                                    'Armor': items.StuddedLeather(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Dagger', "Club", 'Polearm', 'Hammer', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth', 'Light']},
                         pro_level=3)



class Diviner(Job):
    """
    Promotion: Pathfinder -> Diviner -> Geomancer
    Pros: can learn rank 1 enemy specials when cast against; increased intel and wisdom gain
    Cons: loses access to shields and some weapon choices; lower dex gain
    """

    def __init__(self):
        super().__init__(name="Diviner", description="A diviner works with nature to balance the four classical "
                                                     "elements of Earth, Wind, Water, and Fire, and can learn certain "
                                                     "spells cast against them within these domains. Diviners are also "
                                                     "hyper aware of their surroundings, limiting the effect of traps "
                                                     "and magic effects.",
                         str_plus=0, int_plus=2, wis_plus=2, con_plus=1, cha_plus=1, dex_plus=0,
                         att_plus=0, def_plus=1, magic_plus=4, magic_def_plus=3,
                         equipment={'Weapon': items.Kris(), 'OffHand': items.BookShadows(),
                                    'Armor': items.GoldCloak(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Dagger', 'Staff'],
                                       'OffHand': ['Tome', 'Rod'],
                                       'Armor': ['Cloth']},
                         pro_level=2)



class Geomancer(Job):
    """
    Promotion: Pathfinder -> Diviner -> Geomancer
    Additional Pros: can learn rank 2 enemy specials when cast against; increased intel gain
    Additional Cons: None
    Special Mechanic: similar to a Blue Mage, gains spells from enemy use
    """

    def __init__(self):
        super().__init__(name="Geomancer", description="Classified as one of the 7 forbidden arts, geomancers have "
                                                       "mastered natural phenomena, granting them access to some of the"
                                                       " most devastating elemental spells. Their adeptness with "
                                                       "magical effects allow geomancers to manipulate special tiles to"
                                                       " their advantage.",
                         str_plus=0, int_plus=3, wis_plus=2, con_plus=1, cha_plus=1, dex_plus=0,
                         att_plus=1, def_plus=1, magic_plus=4, magic_def_plus=4,
                         equipment={'Weapon': items.Rondel(), 'OffHand': items.DragonRouge(),
                                    'Armor': items.CloakEnchantment(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Dagger', 'Staff'],
                                       'OffHand': ['Tome', 'Rod'],
                                       'Armor': ['Cloth']},
                         pro_level=3)



class Shaman(Job):
    """
    Promotion: Pathfinder -> Shaman -> Soulcatcher
    Pros: Can dual wield fist weapons; can imbue weapons with elemental fury; increased strength and dex gain
    Cons: Loses access to cloth armor, tomes, and some weapons; lower intel gain
    """

    def __init__(self):
        super().__init__(name="Shaman", description="The Shaman is a master of the natural elements, channeling the "
                                                    "raw forces of fire, water, earth, and air to devastate their "
                                                    "enemies. By imbuing weapons with elemental fury, they transform "
                                                    "mundane strikes into catastrophic blows. As warriors of nature, "
                                                    "they bring balance to the battlefield, wielding power both "
                                                    "destructive and enhancing.",
                         str_plus=1, int_plus=0, wis_plus=1, con_plus=1, cha_plus=1, dex_plus=2,
                         att_plus=3, def_plus=1, magic_plus=2, magic_def_plus=2,
                         equipment={'Weapon': items.Cestus(), 'OffHand': items.Cestus(),
                                    'Armor': items.ScaleMail(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Fist', 'Dagger', "Club", 'Staff'],
                                       'OffHand': ['Fist', 'Shield'],
                                       'Armor': ['Light', 'Medium']},
                         pro_level=2)



class Soulcatcher(Job):
    """
    Promotion: Pathfinder -> Shaman -> Soulcatcher
    Additional Pros: Chance to gain essence from enemies; increased strength gain
    Additional Cons: None
    Special Mechanic: gains power based on enemies slain
    """

    def __init__(self):
        super().__init__(name="Soulcatcher", description="The Soulcatcher is a mystic who has mastered the art of "
                                                         "binding spirits and harnessing their power. As a promotion "
                                                         "of the Shaman, they wield unparalleled control over "
                                                         "elemental and spiritual energies, weaving them into "
                                                         "devastating attacks or protective barriers. By capturing the"
                                                         " essence of defeated foes, the Soulcatcher can unleash "
                                                         "soul-charged magic upon enemies. Their deep connection to "
                                                         "the spirit world grants them unique insight and power, "
                                                         "making them both revered and feared on the battlefield.",
                         str_plus=2, int_plus=0, wis_plus=1, con_plus=1, cha_plus=1, dex_plus=2,
                         att_plus=3, def_plus=2, magic_plus=2, magic_def_plus=3,
                         equipment={'Weapon': items.BattleGauntlet(), 'OffHand': items.BattleGauntlet(),
                                    'Armor': items.Breastplate(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ['Fist', 'Dagger', "Club", 'Staff'],
                                       'OffHand': ['Fist', 'Shields'],
                                       'Armor': ['Light', 'Medium']},
                         pro_level=3)
        

class Ranger(Job):
    """
    Promotion: Pathfinder -> Ranger -> Beast Master
    Pros: Increased strength and dex gain; gain dual wielding with daggers; can use swords and 2-handed axes
    Cons: Lose access to attack spells, some weapons and armor, shields, and tomes
    Special Mechanic: can tame a beast to aid in and out of combat; companion strength affected by charisma
    """

    def __init__(self):
        super().__init__(name="Ranger", description="Rangers blend their deep wilderness expertise with fierce melee "
                                                    "combat capabilities. Skilled in tracking and survival, they excel"
                                                    " in close-quarters combat using precision and agility. Their true"
                                                    " strength lies in their ability to tame and command powerful "
                                                    "animals, forging bonds with beasts to fight alongside them. "
                                                    "Rangers leverage their primal connection to nature and combat "
                                                    "mastery, creating a formidable duo of human and beast.",
                         str_plus=2, int_plus=0, wis_plus=0, con_plus=1, cha_plus=1, dex_plus=2,
                         att_plus=3, def_plus=2, magic_plus=1, magic_def_plus=2,
                         equipment={'Weapon': items.Talwar(), 'OffHand': items.Kris(),
                                    'Armor': items.ScaleMail(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ["Dagger", "Sword", "Longsword", "Battle Axe", "Polearm"],
                                       'OffHand': ["Dagger"],
                                       'Armor': ['Light', 'Medium']},
                         pro_level=2)



class BeastMaster(Job):
    """
    Promotion: Pathfinder -> Ranger -> Beast Master
    Additional Pros: Increased charisma gain; increased companion strength from charisma
    Additional Cons: Lose access to medium armor
    """

    def __init__(self):
        super().__init__(name="Beast Master", description="The Beast Master is the pinnacle of the Ranger's journey, "
                                                          "embodying an unbreakable bond with the wild. Beast Masters "
                                                          "thrive in harmony with their companion, fighting as one "
                                                          "unified force. With heightened instincts and the ability "
                                                          "to channel primal energy, they inspire and protect their "
                                                          "allies, making them guardians of the natural world and "
                                                          "champions of untamed strength.",
                         str_plus=2, int_plus=0, wis_plus=0, con_plus=1, cha_plus=2, dex_plus=2,
                         att_plus=4, def_plus=2, magic_plus=1, magic_def_plus=3,
                         equipment={'Weapon': items.Shamshir(), 'OffHand': items.Rondel(),
                                    'Armor': items.StuddedLeather(),
                                    'Pendant': items.NoPendant(), 'Ring': items.NoRing()},
                         restrictions={'Weapon': ["Dagger", "Sword", "Longsword", "Battle Axe", "Polearm"],
                                       'OffHand': ["Dagger"],
                                       'Armor': ['Light']},
                         pro_level=3)


# dataclass dictionaries
classes_dict = {'Warrior': 
                {'class': Warrior, 
                 'pro': {'Weapon Master': 
                         {'class': WeaponMaster, 
                          'pro': {'Berserker': 
                                  {'class': Berserker}}},
                         'Paladin': {
                             'class': Paladin,
                              'pro': {'Crusader': 
                                      {'class': Crusader}}},
                         'Lancer': 
                         {'class': Lancer,
                          'pro': {'Dragoon':
                                  {'class': Dragoon}}},
                         'Sentinel':
                         {'class': Sentinel,
                          'pro': {'Stalwart Defender':
                                  {'class': StalwartDefender}}}}},
                'Mage':
                {'class': Mage,
                'pro': {'Sorcerer': 
                        {'class': Sorcerer,
                         'pro': {'Wizard':
                                 {'class': Wizard}}},
                        'Warlock':
                        {'class': Warlock, 
                         'pro': {'Shadowcaster':
                                 {'class': Shadowcaster}}},
                        'Spellblade':
                         {'class': Spellblade,
                          'pro': {'Knight Enchanter': 
                                  {'class': KnightEnchanter}}},
                        'Summoner':
                        {'class': Summoner,
                         'pro' : {'Grand Summoner':
                                  {'class': GrandSummoner}}}}},

                'Footpad': 
                {'class': Footpad,
                 'pro': {'Thief': 
                         {'class': Thief,
                          'pro': {'Rogue':
                                  {'class': Rogue}}},
                        'Inquisitor': 
                        {'class': Inquisitor,
                         'pro': {'Seeker':
                                 {'class': Seeker}}},
                        'Assassin':
                         {'class': Assassin,
                          'pro': {"Ninja":
                                  {'class': Ninja}}},
                        'Spell Stealer':
                        {'class': SpellStealer,
                         'pro': {"Arcane Trickster":
                                 {'class': ArcaneTrickster}}}}},

                'Healer': 
                {'class': Healer,
                 'pro': {'Cleric':
                         {'class': Cleric,
                          'pro': {'Templar':
                                  {'class': Templar}}},
                        'Monk':
                         {'class': Monk,
                          'pro': {'Master Monk':
                                  {'class': MasterMonk}}},
                        'Priest': 
                         {'class': Priest,
                          'pro': {'Archbishop':
                                  {'class': Archbishop}}},
                        'Bard':
                        {'class': Bard,
                         'pro': {"Troubadour":
                                 {'class': Troubadour}}}}},

                'Pathfinder': 
                {'class': Pathfinder,
                 'pro': {'Druid':
                         {'class': Druid,
                          'pro': {'Lycan':
                                  {'class': Lycan}}},
                        'Diviner': 
                        {'class': Diviner,
                         'pro': {'Geomancer':
                                 {'class': Geomancer}}},
                        'Shaman': 
                        {'class': Shaman,
                         'pro': {'Soulcatcher':
                                 {'class': Soulcatcher}}},
                        'Ranger':
                        {'class': Ranger,
                         'pro': {"Beast Master":
                                 {'class': BeastMaster}}}}}
}
