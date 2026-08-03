"""Player text presentation and menu-facing helpers."""

from ..classes import astromancer, bard, class_rings, lycan, promotion_kits, wizard
from ..constants import BASE_CRIT_PER_POINT
from ..items import remove_equipment


class PlayerPresentationMixin:
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
