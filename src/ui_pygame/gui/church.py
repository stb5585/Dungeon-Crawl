"""
Church system for GUI - handles promotion, saving, and quests.
Implements the core church logic from town.py adapted for Pygame presenter.
"""

import os

from src.core import companions
from src.core.abilities import spell_dict, skill_dict
from src.core.classes import classes_dict, apply_promotion_ability_rules, demonologist
from src.core.items import remove_equipment
from .quest_manager import QuestManager
from .confirmation_popup import ConfirmationPopup
from .location_menu import LocationMenuScreen
from .promotion_screen import PromotionScreen
from .town_base import TownScreenBase


class ChurchManager(TownScreenBase):
    """Manages church interactions with pygame presenter."""
    
    def __init__(self, presenter, player_char):
        super().__init__(presenter)
        self.player_char = player_char
    
    def visit_church(self):
        """Visit the Church of Elysia."""
        church_options = ["Promotion", "Save Game", "Quests"]
        if demonologist.is_demonologist(self.player_char):
            church_options.append("Hidden Crypt")
        church_options.append("Leave")
        
        church_screen = LocationMenuScreen(self.presenter, "Church of Elysia")
        
        while True:
            choice_idx = church_screen.navigate(
                church_options,
                reset_cursor=False,
                flush_events=True,
                require_key_release=True,
            )
            
            if choice_idx is None or church_options[choice_idx] == "Leave":
                popup = ConfirmationPopup(self.presenter, "Let the light of Elysia guide you.", show_buttons=False)
                popup.show(**self.popup_show_kwargs())
                break
            
            elif church_options[choice_idx] == "Promotion":
                self.handle_promotion()
            
            elif church_options[choice_idx] == "Save Game":
                self.save_game()
            
            elif church_options[choice_idx] == "Quests":
                qm = QuestManager(
                    self.presenter, 
                    self.player_char, 
                    quest_text_renderer=lambda text: church_screen.display_quest_text(text)
                )
                qm.check_and_offer('Priest')

            elif church_options[choice_idx] == "Hidden Crypt":
                self.visit_hidden_crypt()
    
    def handle_promotion(self):
        """Handle class promotion at level 30."""
        if self.player_char.level.level < 30 or self.player_char.level.pro_level >= 3:
            if self.player_char.level.pro_level == 3:
                popup = ConfirmationPopup(self.presenter, "You are at max promotion level and can no longer be promoted.", show_buttons=False)
            else:
                popup = ConfirmationPopup(self.presenter, "You need to be level 30 before you can promote your character.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
            return

        current_class = self.player_char.cls.name
        pro_level = self.player_char.level.pro_level

        options = []
        option_map = {}

        if pro_level == 1:
            base_entry = None
            for base_name, cls_entry in classes_dict.items():
                try:
                    if cls_entry["class"]().name == current_class:
                        base_entry = cls_entry
                        break
                except Exception:
                    continue
            if base_entry:
                allowed = getattr(getattr(self.player_char, 'race', {}), 'cls_res', {}).get('First', [])
                for pro_name, pro_entry in base_entry.get('pro', {}).items():
                    try:
                        class_name = pro_entry['class']().name
                        if not allowed or pro_name in allowed or class_name in allowed:
                            options.append(class_name)
                            option_map[class_name] = pro_entry['class']
                    except Exception:
                        continue
        elif pro_level == 2:
            for base_name, cls_entry in classes_dict.items():
                for pro_name, pro_entry in cls_entry.get('pro', {}).items():
                    try:
                        if pro_entry['class']().name == current_class:
                            for nested_name, nested_entry in pro_entry.get('pro', {}).items():
                                class_name = nested_entry['class']().name
                                options.append(class_name)
                                option_map[class_name] = nested_entry['class']
                            break
                    except Exception:
                        continue

        if not options:
            popup = ConfirmationPopup(self.presenter, "No promotion options are currently available.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
            return

        promo_screen = PromotionScreen(
            self.presenter,
            self.player_char,
            options,
            option_map,
            current_class=current_class,
            pro_level=pro_level,
        )
        chosen_name = promo_screen.navigate()
        if not chosen_name:
            popup = ConfirmationPopup(self.presenter, "Promotion cancelled.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
            return

        chosen_ctor = option_map.get(chosen_name)
        if not chosen_ctor:
            popup = ConfirmationPopup(self.presenter, "Promotion option unavailable.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
            return

        try:
            self.player_char.cls = chosen_ctor()
            self.player_char.level.pro_level += 1
            self.player_char.level.level = 1

            try:
                self.player_char.level.exp_to_gain = self.player_char.level_exp()
            except Exception:
                pass

            try:
                self.player_char.unequip(promo=True)
                for slot in ["Weapon", "OffHand", "Armor", "Helmet"]:
                    try:
                        self.player_char.equipment[slot] = remove_equipment(slot)
                    except Exception:
                        pass
                core_slots = {"Weapon", "OffHand", "Armor", "Helmet"}
                for slot, item in self.player_char.cls.equipment.items():
                    if slot not in core_slots:
                        continue
                    try:
                        self.player_char.equip(slot, item, check=True)
                    except Exception:
                        self.player_char.equipment[slot] = item
            except Exception:
                pass

            ability_change_msg = apply_promotion_ability_rules(self.player_char, chosen_name)
            if ability_change_msg:
                popup = ConfirmationPopup(self.presenter, ability_change_msg.strip(), show_buttons=False)
                popup.show(**self.popup_show_kwargs())

            # Grant level 1 abilities for the new class
            promo_ability_messages = []
            if str(self.player_char.level.level) in spell_dict.get(chosen_name, {}):
                spell_gain = spell_dict[chosen_name][str(self.player_char.level.level)]()
                if spell_gain.name in self.player_char.spellbook["Spells"]:
                    promo_ability_messages.append(f"{spell_gain.name} goes up a level.")
                else:
                    promo_ability_messages.append(f"You have gained the spell {spell_gain.name}.")
                self.player_char.spellbook["Spells"][spell_gain.name] = spell_gain
            
            if str(self.player_char.level.level) in skill_dict.get(chosen_name, {}):
                skill_gain = skill_dict[chosen_name][str(self.player_char.level.level)]()
                if skill_gain.name in self.player_char.spellbook["Skills"]:
                    promo_ability_messages.append(f"{skill_gain.name} goes up a level.")
                else:
                    promo_ability_messages.append(f"You have gained the skill {skill_gain.name}.")
                self.player_char.spellbook["Skills"][skill_gain.name] = skill_gain
                if skill_gain.name in ["Transform", "Reveal", "Purity of Body"]:
                    skill_gain.use(self.player_char)
            
            if promo_ability_messages:
                popup = ConfirmationPopup(self.presenter, "\n".join(promo_ability_messages), show_buttons=False)
                popup.show(**self.popup_show_kwargs())

            if chosen_name == "Warlock":
                fam_options = ["Homunculus", "Fairy", "Mephit", "Jinkin"]
                fam_map = {
                    "Homunculus": companions.Homunculus,
                    "Fairy": companions.Fairy,
                    "Mephit": companions.Mephit,
                    "Jinkin": companions.Jinkin,
                }

                fam_confirmed = False
                while not fam_confirmed:
                    fam_idx = self.presenter.render_menu("Choose your familiar", fam_options)
                    if fam_idx is None:
                        break

                    fam_class = fam_map[fam_options[fam_idx]]
                    familiar = fam_class()
                    description = familiar.inspect()
                    self.presenter.show_message(description, title=familiar.race)

                    confirm = self.presenter.render_menu(
                        f"Bind with this {familiar.race}?",
                        ["Yes", "No"]
                    )
                    if confirm == 0:
                        default_name = "Buddy"
                        name_confirmed = False
                        while not name_confirmed:
                            fam_name = self.presenter.get_text_input(
                                "What is your familiar's name?", default_text=default_name
                            )
                            if not fam_name:
                                fam_name = default_name
                            fam_name = fam_name.capitalize()
                            confirm_name = self.presenter.render_menu(
                                f"Name your familiar '{fam_name}'?", ["Yes", "No"]
                            )
                            if confirm_name == 0:
                                name_confirmed = True
                                fam_confirmed = True
                                familiar.name = fam_name
                                self.player_char.familiar = familiar
                                popup = ConfirmationPopup(self.presenter, f"Your familiar {familiar.race} joins you as '{familiar.name}'.", show_buttons=False)
                                popup.show(**self.popup_show_kwargs())

            if chosen_name == "Summoner":
                try:
                    pet = companions.Patagon()
                    pet.initialize_stats(self.player_char)
                    self.player_char.summons[pet.name] = pet
                    popup = ConfirmationPopup(self.presenter, "You have learned to summon Patagon.", show_buttons=False)
                    popup.show(**self.popup_show_kwargs())
                except Exception:
                    pass

            if chosen_name == "Demonologist":
                self.player_char.ensure_demonologist_contracts()
                popup = ConfirmationPopup(
                    self.presenter,
                    "As you leave the altar, a priest whispers of a sealed crypt below the church.",
                    show_buttons=False,
                )
                popup.show(**self.popup_show_kwargs())

            popup = ConfirmationPopup(self.presenter, f"Congratulations! You are now a {chosen_name}.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
        except Exception as e:
            popup = ConfirmationPopup(self.presenter, f"Promotion failed: {e}", show_buttons=False)
            popup.show(**self.popup_show_kwargs())

    def visit_hidden_crypt(self):
        """Manage Demonologist contracts and Class Ring awakening."""
        if not demonologist.is_demonologist(self.player_char):
            popup = ConfirmationPopup(self.presenter, "The crypt door is nowhere to be found.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
            return False

        self.player_char.ensure_demonologist_contracts()
        unlocked = self.player_char.refresh_demonologist_contracts()
        state = self.player_char.demonologist_contracts
        options = ["Review Contracts"]
        if unlocked:
            options.append("Bind Patron")
        if demonologist.ring_can_awaken(self.player_char):
            options.append("Awaken Class Ring")
        options.append("Leave")

        while True:
            choice = self.presenter.render_menu("Hidden Church Crypt", options)
            if choice is None or options[choice] == "Leave":
                return True

            if options[choice] == "Review Contracts":
                if unlocked:
                    active = state.get("active_patron") or "None"
                    text = "Unlocked contracts: " + ", ".join(unlocked) + f"\nActive patron: {active}"
                else:
                    text = "No fiend has answered your name. Defeat an eligible fiend, then return."
                popup = ConfirmationPopup(self.presenter, text, show_buttons=False)
                popup.show(**self.popup_show_kwargs())

            elif options[choice] == "Bind Patron":
                bind_idx = self.presenter.render_menu("Bind which patron?", unlocked)
                if bind_idx is not None and 0 <= bind_idx < len(unlocked):
                    patron = unlocked[bind_idx]
                    demonologist.bind_patron(self.player_char, patron)
                    state = self.player_char.demonologist_contracts
                    popup = ConfirmationPopup(self.presenter, f"{patron} is now your active contract.", show_buttons=False)
                    popup.show(**self.popup_show_kwargs())

            elif options[choice] == "Awaken Class Ring":
                success, message = demonologist.awaken_ring(self.player_char)
                popup = ConfirmationPopup(self.presenter, message.strip(), show_buttons=False)
                popup.show(**self.popup_show_kwargs())
                if success:
                    options = [option for option in options if option != "Awaken Class Ring"]
    
    def save_game(self):
        """Save the game at the church."""
        save_dir = "save_files"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Use character name as filename (always overwrites)
        char_name = self.player_char.name.lower().replace(" ", "_")
        filename = f"{char_name}.save"
        filepath = os.path.join(save_dir, filename)
        
        try:
            # Save directly to filepath using the new Player.save signature
            self.player_char.save(filepath=filepath)
            popup = ConfirmationPopup(self.presenter, f"Game saved successfully!", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
        except Exception as e:
            popup = ConfirmationPopup(self.presenter, f"Error saving game:\n\n{str(e)}", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
