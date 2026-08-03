"""Combat behavior for the menus package."""

import curses
import random
from textwrap import wrap
import time

from src.core.classes import grandmaster, paladin, promotion_kits
import src.ui_curses.menus as menus
from .foundation import PopupMenu


class PromotionPopupMenu(PopupMenu):

    def __init__(self, game, header_message, current_class, familiar=False, box_height=30, box_width=120):
        super().__init__(game, header_message, box_height, box_width)
        self.current_class = current_class
        self.options_list = []
        self.cls_dict = {}
        self.familiar = familiar

    def draw_popup(self):
        self.popup_win.erase()
        if self.options_list[self.current_option] != "Go Back":
            if self.familiar:
                # self.popup_win.addstr(1, (self.box_width // 2) - 5, "Promotion", curses.A_BOLD)
                fam = self.cls_dict[self.options_list[self.current_option]]()
                self.popup_win.addstr(7, (2 * self.box_width // 5) - (len(fam.race) // 2), fam.race, curses.A_BOLD)
                lines = wrap(fam.inspect(), 75, break_on_hyphens=False)
                for i, line in enumerate(lines):
                    self.popup_win.addstr(i + 9, 14, line)
                self.popup_win.addstr(16, (2 * self.box_width // 5) - 5, "Abilities", curses.A_BOLD)
                spells = list(fam.spellbook["Spells"].keys())
                if not spells:
                    spells = ["None"]
                spell_str = "Spells: " + ", ".join(spells)
                self.popup_win.addstr(18, (2 * self.box_width // 5) - (len(spell_str) // 2), spell_str)
                skills = list(fam.spellbook["Skills"].keys())
                if not skills:
                    skills = ["None"]
                skill_str = "Skills: " + ", ".join(skills)
                self.popup_win.addstr(19, (2 * self.box_width // 5) - (len(skill_str) // 2), skill_str)
            else:
                self.popup_win.addstr(1, (self.box_width // 2) - 5, "Promotion", curses.A_BOLD)
                cls = self.cls_dict[self.current_class][self.current_option]
                self.popup_win.addstr(3, (2 * self.box_width // 5) - (len(cls.name) // 2), cls.name, curses.A_BOLD)
                # class description
                lines = cls.description.splitlines()
                for i, line in enumerate(lines):
                    self.popup_win.addstr(i + 5, 14, line)
                # promo stats
                self.popup_win.addstr(13, (self.box_width // 5) - 7, "Promotion Stats", curses.A_BOLD)
                stat_plus_str = ["{:14}{:>3}({:>2})  {:14}{:>4}({:>2})".format(
                                    "Strength:", f"{self.game.player_char.stats.strength+cls.str_plus}", f"+{cls.str_plus}",
                                    "Health:", f"{self.game.player_char.health.max+(cls.con_plus*2)}", f"+{cls.con_plus*2}"),
                                 "{:14}{:>3}({:>2})  {:14}{:>4}({:>2})".format(
                                    "Intelligence:", f"{self.game.player_char.stats.intel+cls.int_plus}", f"+{cls.int_plus}",
                                    "Mana:", f"{self.game.player_char.mana.max+(cls.int_plus*2)}", f"+{cls.int_plus*2}"),
                                 "{:14}{:>3}({:>2})  {:14}{:>4}({:>2})".format(
                                    "Wisdom:", f"{self.game.player_char.stats.wisdom+cls.wis_plus}", f"+{cls.wis_plus}",
                                    "Attack:", f"{self.game.player_char.combat.attack+cls.att_plus}", f"+{cls.att_plus}"),
                                 "{:14}{:>3}({:>2})  {:14}{:>4}({:>2})".format(
                                    "Constitution:",  f"{self.game.player_char.stats.con+cls.con_plus}", f"+{cls.con_plus}",
                                    "Defense:", f"{self.game.player_char.combat.defense+cls.def_plus}", f"+{cls.def_plus}"),
                                 "{:14}{:>3}({:>2})  {:14}{:>4}({:>2})".format(
                                    "Charisma:", f"{self.game.player_char.stats.charisma+cls.cha_plus}", f"+{cls.cha_plus}",
                                    "Magic:", f"{self.game.player_char.combat.magic+cls.magic_plus}", f"+{cls.magic_plus}"),
                                 "{:14}{:>3}({:>2})  {:14}{:>4}({:>2})".format(
                                    "Dexterity:", f"{self.game.player_char.stats.dex+cls.dex_plus}", f"+{cls.dex_plus}",
                                    "Magic Defense:", f"{self.game.player_char.combat.magic_def+cls.magic_def_plus}",
                                    f"+{cls.magic_def_plus}")]
                for j, line in enumerate(stat_plus_str):
                    self.popup_win.addstr(j + 14, (self.box_width // 5) - (len(line) // 2), line)
                # new equipment
                self.popup_win.addstr(13, (3 * self.box_width // 5) - 6, "New Equipment", curses.A_BOLD)
                self.popup_win.addstr(14, (3 * self.box_width // 5) - 15, f"{'Weapon:':8} {cls.equipment['Weapon'].name:>20}")
                # Format OffHand with buff info
                offhand_item = cls.equipment['OffHand']
                if offhand_item.subtyp == 'Shield':
                    offhand_display = f"{offhand_item.name} ({int(offhand_item.mod * 100)}%)"
                elif offhand_item.subtyp in ['Tome', 'Rod']:
                    offhand_display = f"{offhand_item.name} (+{int(offhand_item.mod)})"
                else:
                    offhand_display = offhand_item.name
                self.popup_win.addstr(16, (3 * self.box_width // 5) - 15, f"{'OffHand:':8} {offhand_display:>20}")
                self.popup_win.addstr(18, (3 * self.box_width // 5) - 15, f"{'Armor:':8} {cls.equipment['Armor'].name:>20}")
                # equipment restrictions
                self.popup_win.addstr(j + 17, (2 * self.box_width // 5) - 11, "Equipment Restrictions", curses.A_BOLD)
                for k, (typ, lst) in enumerate(cls.restrictions.items()):
                    line = f"{typ}: " + ", ".join(lst)
                    self.popup_win.addstr(j + k + 19, (2 * self.box_width // 5) - (len(line) // 2), line)
        # header message and options
        if not isinstance(self.header_message, list):
            self.header_message = [self.header_message]
        for i, line in enumerate(self.header_message):
            self.popup_win.addstr((self.box_height // 2) - (len(self.options_list) // 2) + i - 3,
                                  (7 * self.box_width // 8) - (len(line) // 2), line, curses.A_BOLD)
        for idx, option in enumerate(self.options_list):
            if idx == self.current_option:
                self.popup_win.attron(curses.A_REVERSE)
            self.popup_win.addstr((self.box_height // 2) - (len(self.options_list) // 2) + idx + i,
                                  (7 * self.box_width // 8) - (len(option) // 2), option)
            if idx == self.current_option:
                self.popup_win.attroff(curses.A_REVERSE)
        self.popup_win.box()

    def update_options(self, options_list, cls_dict):
        self.current_option = 0
        self.options_list = options_list
        self.cls_dict = cls_dict


class CombatPopupMenu(PopupMenu):
    def __init__(self, game, header_message=None):
        super().__init__(game, header_message)

    def update_options(self, action, tile=None, options=None):
        self.current_option = 0
        self.options_list = []
        if options:
            self.options_list = options
        if action == "Cast Spell":
            for entry in self.game.player_char.spellbook['Spells']:
                spell = self.game.player_char.spellbook['Spells'][entry]
                if getattr(spell, "exploration_cast", False):
                    continue
                if spell.subtyp == "Movement" and entry not in {"Volitation"}:
                    continue
                if spell.cost <= self.game.player_char.mana.current:
                    self.options_list.append(
                        f"{str(entry)}  {str(spell.cost)}"
                        )
        elif action in {'Use Skill', 'Resolve'}:
            resolve_only = action == 'Resolve'
            for entry in self.game.player_char.spellbook['Skills']:
                skill = self.game.player_char.spellbook['Skills'][entry]
                is_resolve = getattr(skill, "resource_type", None) == "Resolve"
                if is_resolve != resolve_only:
                    continue
                can_pay = (
                    is_resolve
                    or skill.cost <= self.game.player_char.mana.current
                )
                if can_pay:
                    if any([self.game.player_char.spellbook['Skills'][entry].passive,
                            not promotion_kits.combat_skill_visible(
                                self.game.player_char,
                                self.game.player_char.spellbook['Skills'][entry],
                            ),
                            self.game.player_char.spellbook['Skills'][entry].name == 'Smoke Screen' and \
                                'Boss' in str(tile),
                            self.game.player_char.spellbook['Skills'][entry].name == 'Lockpick',
                            self.game.player_char.spellbook['Skills'][entry].name == 'Shield Slam' and \
                                self.game.player_char.equipment['OffHand'].subtyp != 'Shield',
                            self.game.player_char.spellbook['Skills'][entry].name == 'Mortal Strike' and \
                                self.game.player_char.equipment['Weapon'].handed == 1,
                            self.game.player_char.spellbook['Skills'][entry].name == "Backstab" and \
                                not tile.enemy.incapacitated(),
                            self.game.player_char.spellbook["Skills"][entry].weapon and \
                                self.game.player_char.physical_effects["Disarm"].active,
                            self.game.player_char.spellbook["Skills"][entry].name in grandmaster.ART_WEAPON_TYPES and \
                                not grandmaster.matching_weapon_for_art_equipped(
                                    self.game.player_char,
                                    self.game.player_char.spellbook["Skills"][entry].name,
                                )]):
                        continue
                    if entry == "Mana Shield" and self.game.player_char.magic_effects["Mana Shield"].active:
                        self.options_list.append(
                            f"Remove Shield  {str(self.game.player_char.spellbook['Skills'][entry].cost)}"
                            )
                    elif is_resolve:
                        display_name = getattr(skill, "name", entry)
                        cost = getattr(skill, "resolve_cost", skill.cost)
                        cost_label = (
                            "Full Resolve"
                            if str(cost).lower() == "full"
                            else f"{cost} Resolve"
                        )
                        current = promotion_kits.current_resolve(
                            self.game.player_char
                        )
                        ready = "Ready"
                        if str(cost).lower() != "full" and current < int(cost):
                            ready = f"Need {int(cost) - current}"
                        self.options_list.append(
                            f"{display_name}  {cost_label}; {ready}"
                        )
                    else:
                        if getattr(skill, "resource_type", None) == "Oath Conviction":
                            vow = paladin.path(self.game.player_char) or "No vow"
                            conviction = int(
                                promotion_kits.combat_state(
                                    self.game.player_char
                                ).get("oath_conviction", 0)
                                or 0
                            )
                            self.options_list.append(
                                f"{entry}  {vow}; all {conviction} Conviction"
                            )
                            continue
                        self.options_list.append(
                            f"{str(entry)}  {str(skill.cost)}"
                            )
        elif action == "Use Item":
            cat_options = ['Health', 'Mana', 'Elixir', 'Status', 'Scroll']
            for itm in self.game.player_char.inventory:
                if str(self.game.player_char.inventory[itm][0].subtyp) in cat_options:
                    item_list = self.game.player_char.inventory[itm]
                    self.options_list.append(
                        f"{str(item_list[0].name)}  {str(len(item_list))}"
                        )
        elif action == "Steal As Well":
            from src.core import items as core_items

            for entry, spell in self.game.player_char.spellbook["Spells"].items():
                if spell.subtyp not in {"Support", "Movement"} and spell.cost <= self.game.player_char.mana.current:
                    self.options_list.append(f"{entry}  {spell.cost}")
            for item_name, item_list in self.game.player_char.inventory.items():
                if item_list and isinstance(item_list[0], core_items.InscribedSpellScroll):
                    self.options_list.append(f"{item_name}  {len(item_list)}")
        self.options_list.append('Go Back')
        self.header_message = action

    def navigate_popup(self):
        self.draw_popup()
        while True:
            self.draw_popup()
            self.popup_win.refresh()
            key = self.game.stdscr.getch()

            # Navigate the item list
            if key == curses.KEY_UP:
                self.current_option -= 1
                if self.current_option < 0:
                    self.current_option = len(self.options_list) - 1
            elif key == curses.KEY_DOWN:
                self.current_option += 1
                if self.current_option > len(self.options_list) - 1:
                    self.current_option = 0
            elif key == curses.KEY_ENTER or key in [10, 13]:
                return self.options_list[self.current_option]


class SlotMachinePopupMenu(PopupMenu):
    def __init__(self, game, header_message, box_height=5, box_width=7):
        super().__init__(game, header_message, box_height, box_width)
        self.result = ['*', '*', '*']

    def draw_popup(self):
        self.popup_win.erase()
        self.popup_win.box()
        self.popup_win.addstr(2, 2, "".join(self.result))
        for i, _ in enumerate(self.result):
            for _ in range(50):
                self.result[i] = str(random.randint(0, 9))
                self.popup_win.addstr(2, 2, "".join(self.result))
                self.popup_win.refresh()
                time.sleep(0.01)
        self.game.stdscr.getch()

    def results(self):
        self.draw_popup()
        return "".join(self.result)

    def navigate_popup(self):
        raise NotImplementedError


class BlackjackPopupMenu(PopupMenu):

    def __init__(self, game, header_message, box_height=10, box_width=30):
        super().__init__(game, header_message, box_height, box_width)
        self.numbers = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.suits = ["♠️", "♥️", "♣️", "♦️"]
        self.deck = [f"{suit} {number}" for suit in self.suits for number in self.numbers]
        self.user_hand = []
        self.user_stay = False
        self.target_hand = []
        self.target_stay = False

    def draw_popup(self):
        user_name, target_name = self.header_message[0].split('  ')
        self.popup_win.erase()
        self.popup_win.addstr(1, 2, user_name)
        self.popup_win.addstr(1, 27 - len(target_name), target_name)
        for i, card in enumerate(self.user_hand):
            self.popup_win.addstr(3 + i, 5, card)
        for i, card in enumerate(self.target_hand):
            self.popup_win.addstr(3 + i, 18, card)
        self.popup_win.box()

    def deal(self):
        def draw_card(cards):
            card = random.choice(cards)
            return cards.pop(cards.index(card))

        def score(hand):
            total = 0
            for card in hand:
                try:
                    total += int(card.split()[1])
                except ValueError:
                    if card.split()[1] in ['J', 'Q', 'K']:
                        total += 10
                    else:
                        total += 11
                        if total > 21:
                            total -= 10
            return total

        if not self.target_stay:
            self.target_hand.append(draw_card(self.deck))
            target_score = score(self.target_hand)
            if target_score > 21:
                return "Target Break"
            if target_score >= 17:
                self.target_stay = True
        if not self.user_stay:
            self.user_hand.append(draw_card(self.deck))
            user_score = score(self.user_hand)
            if user_score > 21:
                return "User Break"
            if user_score >= 17:
                self.user_stay = True
        if all([self.target_stay, self.user_stay]):
            target_score = score(self.target_hand)
            user_score = score(self.user_hand)
            if target_score > user_score:
                return "Target Win"
            if user_score > target_score:
                return "User Win"
            return "Push"

    def navigate_popup(self):
        self.draw_popup()
        result = None
        while True:
            if result:
                self.draw_popup()
                self.popup_win.refresh()
                self.game.stdscr.getch()
                return result
            self.draw_popup()
            self.popup_win.refresh()
            result = self.deal()
            self.game.stdscr.getch()


class SelectionPopupMenu(PopupMenu):

    def __init__(self, game, header_message, stat_options, box_height=10, rewards=None, confirm=True):
        super().__init__(game, header_message, box_height=box_height)
        self.options_list = stat_options
        self.rewards = rewards
        self.confirm = confirm

    def navigate_popup(self):
        self.draw_popup()
        while True:
            self.draw_popup()
            self.popup_win.refresh()
            key = self.game.stdscr.getch()

            # Navigate the item list
            if key == curses.KEY_UP:
                self.current_option -= 1
                if self.current_option < 0:
                    self.current_option = len(self.options_list) - 1
            elif key == curses.KEY_DOWN:
                self.current_option += 1
                if self.current_option > len(self.options_list) - 1:
                    self.current_option = 0
            elif key == ord("i") or key == ord("I") and self.rewards:
                try:
                    self.inspect_item(self.rewards[self.current_option])
                except TypeError:
                    pass
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if self.confirm:
                    choice_str = self.options_list[self.current_option]
                    confirm_str = f"Are you sure you want to choose: {choice_str}?"
                    confirm_popup = menus.ConfirmPopupMenu(self.game, confirm_str, box_height=7)
                    if confirm_popup.navigate_popup():
                        return self.current_option
                else:
                    return self.current_option

    def inspect_item(self, item):
        itembox = menus.TextBox(self.game)
        itembox.print_text_in_rectangle(str(item()))
        itembox.clear_rectangle()


class ShopPopup(PopupMenu):

    def __init__(self, game, header_message, max="01", box_height=20, box_width=30):
        super().__init__(game, header_message, box_height, box_width)
        self.current_option = 1
        self.max = max.zfill(2)
        self.tens = self.max[0]
        self.ones = self.max[1]

    def draw_popup(self):
        self.popup_win.erase()
        for i, line in enumerate(self.header_message):
            self.popup_win.addstr(1 + i, (self.box_width // 2) - (len(line) // 2), line, curses.A_BOLD)
        for idx, option in enumerate([self.tens, self.ones]):
            if idx == self.current_option:
                self.popup_win.attron(curses.A_REVERSE)
            self.popup_win.addstr(3 + i, self.box_width // 2 + idx - 1, option)
            if idx == self.current_option:
                self.popup_win.attroff(curses.A_REVERSE)
        self.popup_win.box()

    def navigate_popup(self):
        self.draw_popup()
        while True:
            self.draw_popup()
            self.popup_win.refresh()
            key = self.game.stdscr.getch()

            # Navigate the item list
            if key == curses.KEY_LEFT:
                self.current_option -= 1
                if self.current_option < 0:
                    self.current_option = 1
            elif key == curses.KEY_RIGHT:
                self.current_option += 1
                if self.current_option > 1:
                    self.current_option = 0
            elif key == curses.KEY_UP:
                if self.current_option == 1:
                    self.ones = str(int(self.ones) + 1)
                    if int(self.ones) > 9:
                        self.ones = "0"
                else:
                    self.tens = str(int(self.tens) + 1)
                    if int(self.tens) > 9:
                        self.tens = "0"
            elif key == curses.KEY_DOWN:
                if self.current_option == 1:
                    self.ones = str(int(self.ones) - 1)
                    if int(self.ones) < 0:
                        self.ones = "9"
                else:
                    self.tens = str(int(self.tens) - 1)
                    if int(self.tens) < 0:
                        self.tens = "9"
            elif key == curses.KEY_ENTER or key in [10, 13]:
                return int(self.tens+self.ones)
