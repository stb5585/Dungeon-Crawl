"""Player text presentation and menu-facing helpers."""

from ..classes import astromancer, bard, class_rings, lycan, promotion_kits, wizard
from ..constants import BASE_CRIT_PER_POINT
from ..items import remove_equipment


class PlayerPresentationMixin:
    def character_menu(self, game=None, menu=None, textbox=None, actions_dict=None, ui_factory=None):
        """
        Lists character options. UI logic must be provided by the frontend.
        Args:
            game: Game instance (optional, for UI context)
            menu: Optional menu UI component
            textbox: Optional TextBox UI component
            actions_dict: Optional dict of action callbacks
            ui_factory: Optional dict of UI component factory functions/classes
        Returns True if quit, else None.
        """
        if not (menu and actions_dict):
            return
        jump_skill = None
        skills = getattr(self, "spellbook", {}).get("Skills", {})
        if "Jump" in skills:
            jump_skill = skills["Jump"]
        else:
            for skill in skills.values():
                if getattr(skill, "name", "") == "Jump":
                    jump_skill = skill
                    break

        has_jump_mods = bool(jump_skill and hasattr(jump_skill, "modifications"))

        totem_skill = None
        skills = getattr(self, "spellbook", {}).get("Skills", {})
        if "Totem" in skills:
            totem_skill = skills["Totem"]
        else:
            for skill in skills.values():
                if getattr(skill, "name", "") == "Totem":
                    totem_skill = skill
                    break
        has_totem_aspects = bool(totem_skill and hasattr(totem_skill, "get_unlocked_aspects"))

        character_options = [
            actions_dict.get('ViewInventory'),
            actions_dict.get("ViewKeyItems"),
            actions_dict.get("Equipment"),
            actions_dict.get('Specials'),
            actions_dict.get('ViewQuests'),
        ]
        options = ["Inventory", "Key Items", "Equipment", "Specials", "Quests"]

        if has_jump_mods:
            character_options.append(actions_dict.get("JumpMods"))
            options.append("Jump Mods")

        if has_totem_aspects:
            character_options.append(actions_dict.get("TotemAspects"))
            options.append("Totem Aspects")

        character_options.extend(["Exit Menu", actions_dict.get('Quit')])
        options.extend(["Exit Menu", "Quit Game"])
        menu.set_options(options)
        menu.draw_all()
        while True:
            character_idx = menu.navigate_menu()
            action = character_options[character_idx]
            if action == "Exit Menu":
                break
            if action is None and textbox:
                textbox.print_text_in_rectangle("Your class does not have a special menu.\n")
            elif isinstance(action, dict) and 'method' in action:
                # Use UI factory to create components if provided
                if ui_factory:
                    if action['name'] == 'Inventory':
                        inv_popup = ui_factory['InventoryPopup'](game, "Inventory")
                        confirm_popup = ui_factory['ConfirmPopup']
                        useitembox = ui_factory['TextBox'](game)
                        action['method'](self, game, inv_popup=inv_popup, confirm_popup=confirm_popup, useitembox=useitembox)
                    elif action['name'] == 'Key Items':
                        inv_popup = ui_factory['InventoryPopup'](game, "Key Items")
                        action['method'](self, game, inv_popup=inv_popup)
                    elif action['name'] == 'Equipment':
                        popup = ui_factory['EquipmentPopup'](game, action['name'], 25)
                        action['method'](self, game, popup=popup)
                    elif action['name'] == 'Specials':
                        popup = ui_factory['SpecialsPopup'](game, action['name'])
                        action['method'](self, game, popup=popup)
                    elif action['name'] == 'Quests':
                        popup = ui_factory['QuestsPopup'](game, action['name'])
                        action['method'](self, game, popup=popup)
                    elif action['name'] == 'Jump Mods':
                        popup = ui_factory['JumpModsPopup'](game, action['name'])
                        action['method'](self, game, jump_popup=popup)
                    elif action['name'] == 'Totem Aspects':
                        popup = ui_factory['TotemAspectsPopup'](game, action['name'])
                        action['method'](self, game, totem_popup=popup)
                    elif action['name'] == 'Quit':
                        confirm_popup = ui_factory['ConfirmPopup']
                        quit_textbox = ui_factory['TextBox'](game)
                        action['method'](self, game, confirm_popup=confirm_popup, textbox=quit_textbox)
                    else:
                        # For other actions (like Summons, Quit), call with game only
                        action['method'](self, game)
                else:
                    # Fallback: call without UI components (may raise error)
                    action['method'](self, game)
                if self.quit:
                    return True
            menu.draw_all()
            menu.refresh_all()

    def status_str(self):
        """
        Returns a string with the status of the player
        """
        status_message = (f"{'Hit Points:':13}{' ':1}{self.health.current:3}/{self.health.max:>3}\n"
                          f"{'Mana Points:':13}{' ':1}{self.mana.current:3}/{self.mana.max:>3}\n"
                          f"{'Strength:':13}{' ':1}{self.stats.strength:>7}\n"
                          f"{'Intelligence:':13}{' ':1}{self.stats.intel:>7}\n"
                          f"{'Wisdom:':13}{' ':1}{self.stats.wisdom:>7}\n"
                          f"{'Constitution:':13}{' ':1}{self.stats.con:>7}\n"
                          f"{'Charisma:':13}{' ':1}{self.stats.charisma:>7}\n"
                          f"{'Dexterity:':13}{' ':1}{self.stats.dex:>7}\n")
        try:
            virtue = getattr(getattr(self, "race", None), "virtue", None)
            sin = getattr(getattr(self, "race", None), "sin", None)
            if virtue and getattr(virtue, "name", ""):
                status_message += f"{'Virtue:':13} {virtue.name}\n"
            if sin and getattr(sin, "name", ""):
                status_message += f"{'Sin:':13} {sin.name}\n"
        except Exception:
            pass
        status_message += self._class_kit_status_str()
        return status_message

    def _class_kit_status_str(self):
        lines = []
        cls_name = getattr(getattr(self, "cls", None), "name", "")
        if cls_name == "Berserker":
            scars = class_rings.ensure_state(self)["data"]["Berserker"].get("battle_scars", 0)
            lines.append(f"{'Battle Scars:':13} {int(scars)}/20")
        if cls_name in {"Bard", "Troubadour"}:
            song = bard.ensure_song_state(self)
            active = song.get("active") or "None"
            lines.append(f"{'Song:':13} {active} ({int(song.get('turns', 0) or 0)} turns)")
        if cls_name in {"Sorcerer", "Wizard"}:
            affinity = wizard.ensure_affinity(self)
            cap = int(wizard.cap_for(self))
            values = " ".join(f"{school[:3]}:{affinity[school]:.1f}" for school in wizard.AFFINITY_SCHOOLS)
            lines.append(f"{'Affinity:':13} {values} /{cap}")
        if cls_name == "Lycan":
            state = lycan.ensure_state(self)
            lines.append(f"{'Moon:':13} {state['moon_phase']} ({state['moon_steps']}/{lycan.STEPS_PER_PHASE})")
            if state["frenzy_turns"]:
                lines.append(f"{'Frenzy Lock:':13} {state['frenzy_turns']} turns")
        if cls_name in {"Diviner", "Astromancer"}:
            self.ensure_astromancer_state()
            lines.append(f"{'Runes:':13} {astromancer.rune_status_summary(self)}")
        if cls_name == "Astromancer":
            lines.append(f"{'Constellation:':13} {astromancer.active_constellation(self)}")
        if cls_name == "Soulcatcher":
            harvested = class_rings.ensure_state(self)["data"]["Soulcatcher"].get("harvested_types", [])
            lines.append(f"{'Soul Types:':13} {len(harvested)}")
        lines.extend(promotion_kits.status_summary(self))
        return "".join(f"{line}\n" for line in lines)

    def combat_str(self):
        combat_message = ""
        main_dmg = self.check_mod('weapon')
        main_crit = int((self.equipment['Weapon'].crit + (BASE_CRIT_PER_POINT * self.check_mod("speed"))) * 100)
        if self.equipment['OffHand'].typ == 'Weapon':
            off_dmg = self.check_mod('offhand')
            off_crit = int((self.equipment['OffHand'].crit + (BASE_CRIT_PER_POINT * self.check_mod("speed"))) * 100)
            combat_message += f"{'Attack:':16}{' ':2}{str(main_dmg):>3}/{str(off_dmg):>3}\n"
            combat_message += f"{'Critical Chance:':16}{' ':2}{str(main_crit):2}%/{str(off_crit):>2}%\n"
        else:
            combat_message += f"{'Attack:':16}{' ':2}{str(main_dmg):>7}\n"
            combat_message += f"{'Critical Chance:':16}{' ':2}{str(main_crit):>6}%\n"
        combat_message += f"{'Defense:':16}{' ':2}{self.check_mod('armor'):>7}\n"
        combat_message += f"{'Block Chance:':16}{' ':2}{self.check_mod('shield'):>6}%\n"
        combat_message += f"{'Spell Defense:':16}{' ':2}{str(self.check_mod('magic def')):>7}\n"
        spell_mod = self.check_mod('magic')
        heal_mod = self.check_mod('heal')
        combat_message += f"{'Spell Modifier:':16}{' ':2}{str(spell_mod):>7}\n"
        combat_message += f"{'Heal Modifier:':16}{' ':2}{str(heal_mod):>7}\n"
        return combat_message

    def equipment_str(self):
        """
        Returns a string containing the current equipment of the player
        """

        buff_str = self.buff_str()
        # Format OffHand with buff info
        offhand_item = self.equipment['OffHand']
        if offhand_item.subtyp == 'Shield':
            offhand_str = f"{offhand_item.name} ({int(offhand_item.mod * 100)}% Block)"
        elif offhand_item.subtyp in ['Tome', 'Rod']:
            offhand_str = f"{offhand_item.name} (+{int(offhand_item.mod)} Magic)"
        elif offhand_item.subtyp == 'Musical Instrument':
            offhand_str = f"{offhand_item.name} (+{int(offhand_item.mod)} Heal)"
        elif offhand_item.typ == 'Weapon':
            offhand_str = offhand_item.name
        else:
            offhand_str = offhand_item.name

        return (f"{'Weapon'}:    {self.equipment['Weapon'].name:<30}\n"
                f"{'Armor'}:     {self.equipment['Armor'].name:<30}\n"
                f"{'Helmet'}:    {self.equipment.get('Helmet', remove_equipment('Helmet')).name:<30}\n"
                f"{'Ring'}:      {self.equipment['Ring'].name:<30}\n"
                f"{'OffHand'}:   {offhand_str:<30}\n"
                f"{'Pendant'}:   {self.equipment['Pendant'].name:<30}\n"
                f"{'Buffs'}:     {buff_str:<30}\n")

    def resist_str(self):
        """
        Returns a string containing the current resistances of the player
        """

        rest_dict = {}
        for typ in self.resistance:
            rest_dict[typ] = self.check_mod("resist", typ=typ)
        return (f"{'Fire:'}     {rest_dict['Fire']:>5}       "
                f"{'Electric:'} {rest_dict['Electric']:>5}       "
                f"{'Earth:'}    {rest_dict['Earth']:>5}       "
                f"{'Shadow:'}   {rest_dict['Shadow']:>5}       "
                f"{'Poison:'}   {rest_dict['Poison']:>5}       \n"
                f"{'Ice:'}      {rest_dict['Ice']:>5}       "
                f"{'Water:'}    {rest_dict['Water']:>5}       "
                f"{'Wind:'}     {rest_dict['Wind']:>5}       "
                f"{'Holy:'}     {rest_dict['Holy']:>5}       "
                f"{'Physical:'} {rest_dict['Physical']:>5}       ")

    def inventory_screen(self, game, inv_popup=None, confirm_popup=None, useitembox=None):
        """Inventory screen logic, now UI-agnostic. UI components must be provided by the frontend."""
        if inv_popup is None:
            raise ValueError("UI component 'inv_popup' must be provided by the frontend.")
        while True:
            item = inv_popup.navigate_popup()
            if item == "Go Back":
                return
            if self.usable_item(item):
                if confirm_popup is None:
                    raise ValueError("UI component 'confirm_popup' must be provided by the frontend.")
                popup = confirm_popup(game, f"Do you want to use the {item.name}", box_height=7)
                if popup.navigate_popup():
                    use_str = item.use(self)
                    if use_str:
                        if useitembox is None:
                            raise ValueError("UI component 'useitembox' must be provided by the frontend.")
                        useitembox.print_text_in_rectangle(use_str)
                        useitembox.clear_rectangle()
                    if "Sanctuary" in item.name:
                        return

    def key_item_screen(self, game, inv_popup=None):
        """Key item screen logic, now UI-agnostic. UI component must be provided by the frontend."""
        if inv_popup is None:
            raise ValueError("UI component 'inv_popup' must be provided by the frontend.")
        while True:
            item = inv_popup.navigate_popup()
            if item == "Go Back":
                return

    def equipment_screen(self, game, popup):
        """Equipment screen logic, now UI-agnostic. UI component must be provided by the frontend."""
        popup.navigate_popup()

    def abilities_screen(self, game, popup):
        """Abilities screen logic, now UI-agnostic. UI component must be provided by the frontend."""
        popup.navigate_popup()

    def jump_mods_menu(self, game, jump_popup=None):
        """Jump modifications menu logic, now UI-agnostic. UI component must be provided by the frontend."""
        if jump_popup is None:
            raise ValueError("UI component 'jump_popup' must be provided by the frontend.")
        jump_popup.navigate_popup()

    def totem_aspects_menu(self, game, totem_popup=None):
        """Totem aspects menu logic, now UI-agnostic. UI component must be provided by the frontend."""
        if totem_popup is None:
            raise ValueError("UI component 'totem_popup' must be provided by the frontend.")
        totem_popup.navigate_popup()

    def quests_screen(self, game, popup):
        """Quests screen logic, now UI-agnostic. UI component must be provided by the frontend."""
        popup.navigate_popup()

    def summon_menu(self, game, summonpopup=None, summonbox=None):
        """Summon menu logic, now UI-agnostic. UI components must be provided by the frontend."""
        if summonpopup is None or summonbox is None:
            raise ValueError("UI components 'summonpopup' and 'summonbox' must be provided by the frontend.")
        summon_names = list(self.summons)
        summon_idx = summonpopup.navigate_popup()
        summon = self.summons[summon_names[summon_idx]]
        summonbox.print_text_in_rectangle(summon.inspect())
        summonbox.clear_rectangle()
