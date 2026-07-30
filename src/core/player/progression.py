"""Player leveling, class upgrades, and quest progression."""

import random

from .. import abilities, quest_progress
from ..constants import (
    LEVELUP_ATK_LUCK_FACTOR,
    LEVELUP_DEF_LUCK_FACTOR,
    LEVELUP_LUCK_DIVISOR_BASE,
    LEVELUP_LUCK_FACTOR_HP_MP,
    LEVELUP_MAG_LUCK_FACTOR,
    LEVELUP_MDEF_LUCK_FACTOR,
    LEVELUP_STAT_DIVISOR,
)
from .stats import _upgrade_source_name


class PlayerProgressionMixin:
    def level_up(self, game=None, textbox=None, menu=None):
        """Level up the player character.

        Args:
            game: Game instance (for UI interactions, optional)
            textbox: Optional TextBox UI component
            menu: Optional SelectionPopupMenu UI component
        """
        dv = max(1, LEVELUP_LUCK_DIVISOR_BASE - self.check_mod('luck', luck_factor=LEVELUP_LUCK_FACTOR_HP_MP))
        health_gain = random.randint(self.stats.con // dv, self.stats.con)
        self.health.max += health_gain
        mana_gain = random.randint(self.stats.intel // dv, self.stats.intel)
        self.mana.max += mana_gain
        if self.in_town():
            self.health.current = self.health.max
            self.mana.current = self.mana.max
        self.level.level += 1
        self.refresh_highest_level()
        level_str = (f"You have gained a level.\n"
                     f"You are now level {self.level.level}.\n"
                     f"You have gained {health_gain} health points and {mana_gain} mana points.\n")
        attack_gain = random.randint(0, self.check_mod("luck", luck_factor=LEVELUP_ATK_LUCK_FACTOR) +
                                    (self.stats.strength // LEVELUP_STAT_DIVISOR) + max(1, self.cls.att_plus // 2))
        self.combat.attack += attack_gain
        defense_gain = random.randint(0, self.check_mod("luck", luck_factor=LEVELUP_DEF_LUCK_FACTOR) +
                                    (self.stats.con // LEVELUP_STAT_DIVISOR) + max(1, self.cls.def_plus // 2))
        self.combat.defense += defense_gain
        magic_gain = random.randint(0, self.check_mod("luck", luck_factor=LEVELUP_MAG_LUCK_FACTOR) +
                                    (self.stats.intel // LEVELUP_STAT_DIVISOR) + max(1, self.cls.int_plus // 2))
        self.combat.magic += magic_gain
        magic_def_gain = random.randint(0, self.check_mod("luck", luck_factor=LEVELUP_MDEF_LUCK_FACTOR) +
                                    (self.stats.wisdom // LEVELUP_STAT_DIVISOR) + max(1, self.cls.wis_plus // 2))
        self.combat.magic_def += magic_def_gain
        if attack_gain > 0:
            level_str += f"You have gained {attack_gain} attack.\n"
        if defense_gain > 0:
            level_str += f"You have gained {defense_gain} defense.\n"
        if magic_gain > 0:
            level_str += f"You have gained {magic_gain} magic.\n"
        if magic_def_gain > 0:
            level_str += f"You have gained {magic_def_gain} magic defense.\n"
        for spell in abilities.ability_classes_for_level(abilities.spell_dict, self.cls.name, self.level.level):
            spell_gain = spell()
            spell_name = spell_gain.name
            if spell_name in self.spellbook['Spells']:
                level_str += f"{spell_name} goes up a level.\n"
            else:
                old_name = _upgrade_source_name(spell)
                if old_name and old_name in self.spellbook['Spells']:
                    level_str += f"{old_name} is upgraded to {spell_name}."
                    del self.spellbook['Spells'][old_name]
                else:
                    level_str += f"You have gained the ability to cast {spell_name}.\n"
            self.spellbook['Spells'][spell_name] = spell_gain
        for skill in abilities.ability_classes_for_level(abilities.skill_dict, self.cls.name, self.level.level):
            skill_gain = skill()
            skill_name = skill_gain.name
            if skill_name in self.spellbook['Skills']:
                level_str += f"{skill_name} goes up a level.\n"
            else:
                old_name = _upgrade_source_name(skill)
                if old_name and old_name in self.spellbook['Skills']:
                    level_str += f"{old_name} is upgraded to {skill_name}."
                    del self.spellbook['Skills'][old_name]
                else:
                    level_str += f"You have gained the ability to use {skill_name}.\n"
            self.spellbook['Skills'][skill_name] = skill_gain
            if skill_name == 'Health/Mana Drain':
                for skill in ["Health Drain", "Mana Drain"]:
                    if skill in self.spellbook["Skills"]:
                        del self.spellbook['Skills'][skill]
            elif skill_name == "True Piercing Strike":
                for skill in ["Piercing Strike", "True Strike"]:
                    if skill in self.spellbook["Skills"]:
                        del self.spellbook['Skills'][skill]
            elif skill_name == 'Familiar':
                level_str += self.familiar.level_up()
            elif skill_name in ["Transform", "Purity of Body"]:
                level_str += skill_gain.use(self)
            elif skill_name == 'Totem':
                # Initialize aspect unlocking for new Totem
                newly_unlocked = skill_gain.check_and_unlock_aspects(self.level.level)
                if newly_unlocked:
                    aspects_str = ", ".join(newly_unlocked)
                    level_str += f"Totem aspects unlocked: {aspects_str}.\n"
        # Unlock Jump modifications (Lancer/Dragoon)
        jump_skill = None
        skills = self.spellbook.get("Skills", {})
        if "Jump" in skills:
            jump_skill = skills["Jump"]
        else:
            for sk in skills.values():
                if getattr(sk, "name", "") == "Jump":
                    jump_skill = sk
                    break
        if jump_skill is not None:
            newly_unlocked = []
            if hasattr(jump_skill, "check_and_unlock_level_modifications"):
                newly_unlocked = jump_skill.check_and_unlock_level_modifications(
                    self.level.level, self.cls.name
                )
            elif hasattr(jump_skill, "check_and_unlock_level_modification"):
                newly_unlocked = jump_skill.check_and_unlock_level_modification(
                    self.level.level, self.cls.name
                )
            if newly_unlocked:
                mods_str = ", ".join(newly_unlocked)
                level_str += f"New Jump modifications unlocked: {mods_str}.\n"

        # Unlock Totem aspects (Shaman)
        totem_skill = None
        skills = self.spellbook.get("Skills", {})
        if "Totem" in skills:
            totem_skill = skills["Totem"]
        else:
            for sk in skills.values():
                if getattr(sk, "name", "") == "Totem":
                    totem_skill = sk
                    break
        if totem_skill is not None:
            newly_unlocked = []
            if hasattr(totem_skill, "check_and_unlock_aspects"):
                newly_unlocked = totem_skill.check_and_unlock_aspects(self.level.level)
            if newly_unlocked:
                aspects_str = ", ".join(newly_unlocked)
                level_str += f"New Totem aspects unlocked: {aspects_str}.\n"
        if not self.max_level():
            self.level.exp_to_gain += (self.exp_scale ** self.level.pro_level) * self.level.level
        else:
            self.level.exp_to_gain = "MAX"

        # Only show UI if components are provided
        if textbox and game:
            textbox.print_text_in_rectangle(level_str)
            game.stdscr.getch()
            textbox.clear_rectangle()

        if self.level.level % 4 == 0:
            stat_options = [f'Strength - {self.stats.strength}',
                            f'Intelligence - {self.stats.intel}',
                            f'Wisdom - {self.stats.wisdom}',
                            f'Constitution - {self.stats.con}',
                            f'Charisma - {self.stats.charisma}',
                            f'Dexterity - {self.stats.dex}']
            # Only show stat selection if menu is provided
            if menu and game:
                stat_idx = menu.navigate_popup()
                if 'Strength' in stat_options[stat_idx]:
                    self.stats.strength += 1
                    statup_message = f"You are now at {self.stats.strength} strength."
                if 'Intelligence' in stat_options[stat_idx]:
                    self.stats.intel += 1
                    statup_message = f"You are now at {self.stats.intel} intelligence."
                if 'Wisdom' in stat_options[stat_idx]:
                    self.stats.wisdom += 1
                    statup_message = f"You are now at {self.stats.wisdom} wisdom."
                if 'Constitution' in stat_options[stat_idx]:
                    self.stats.con += 1
                    statup_message = f"You are now at {self.stats.con} constitution."
                if 'Charisma' in stat_options[stat_idx]:
                    self.stats.charisma += 1
                    statup_message = f"You are now at {self.stats.charisma} charisma."
                if 'Dexterity' in stat_options[stat_idx]:
                    self.stats.dex += 1
                    statup_message = f"You are now at {self.stats.dex} dexterity."
                textbox.print_text_in_rectangle(statup_message)
                game.stdscr.getch()
                textbox.clear_rectangle()

    def class_upgrades(self, game, enemy):
        upgrade_str = ""
        if self.cls.name == "Soulcatcher":
            state = getattr(self, 'absorb_essence_state', None)
            if not isinstance(state, dict):
                self.absorb_essence_state = {}
                state = self.absorb_essence_state

            state.setdefault('floor', self.location_z)
            state.setdefault('procs_this_floor', 0)
            state.setdefault('procs_by_enemy', {})
            state.setdefault('stat_gains', {
                'strength': 0,
                'intel': 0,
                'wisdom': 0,
                'con': 0,
                'charisma': 0,
                'dex': 0,
            })
            state.setdefault('health_gains', 0)
            state.setdefault('mana_gains', 0)
            state.setdefault('level_gains', 0)
            state.setdefault('dragon_gold_claimed', False)

            if state['floor'] != self.location_z:
                state['floor'] = self.location_z
                state['procs_this_floor'] = 0
                state['procs_by_enemy'] = {}

            if state['procs_this_floor'] >= self.ABSORB_ESSENCE_MAX_PROCS_PER_FLOOR:
                return upgrade_str

            enemy_proc_count = state['procs_by_enemy'].get(enemy.name, 0)
            if enemy_proc_count >= self.ABSORB_ESSENCE_MAX_PROCS_PER_ENEMY_PER_FLOOR:
                return upgrade_str

            luck_bonus = min(4, self.check_mod('luck', enemy=enemy, luck_factor=20))
            chance = max(12, 19 - luck_bonus)
            if not random.randint(0, chance):
                applied = False

                if enemy.name in ['Behemoth', 'Golem', 'Iron Golem'] and \
                        state['stat_gains']['strength'] < self.ABSORB_ESSENCE_MAX_STAT_GAINS:
                    upgrade_str += "Gain 1 strength.\n"
                    self.stats.strength += 1
                    state['stat_gains']['strength'] += 1
                    applied = True

                if enemy.name in ['Lich', 'Brain Gorger'] and \
                        state['stat_gains']['intel'] < self.ABSORB_ESSENCE_MAX_STAT_GAINS:
                    upgrade_str += "Gain 1 intelligence.\n"
                    self.stats.intel += 1
                    state['stat_gains']['intel'] += 1
                    applied = True

                if enemy.name in ['Aboleth', 'Hydra'] and \
                        state['stat_gains']['wisdom'] < self.ABSORB_ESSENCE_MAX_STAT_GAINS:
                    upgrade_str += "Gain 1 wisdom.\n"
                    self.stats.wisdom += 1
                    state['stat_gains']['wisdom'] += 1
                    applied = True

                if enemy.name in ['Warforged', 'Archvile'] and \
                        state['stat_gains']['con'] < self.ABSORB_ESSENCE_MAX_STAT_GAINS:
                    upgrade_str += "Gain 1 constitution.\n"
                    self.stats.con += 1
                    state['stat_gains']['con'] += 1
                    applied = True

                if enemy.name in ['Beholder', 'Wyrm'] and \
                        state['stat_gains']['charisma'] < self.ABSORB_ESSENCE_MAX_STAT_GAINS:
                    upgrade_str += "Gain 1 charisma.\n"
                    self.stats.charisma += 1
                    state['stat_gains']['charisma'] += 1
                    applied = True

                if enemy.name in ['Shadow Serpent', 'Wyvern'] and \
                        state['stat_gains']['dex'] < self.ABSORB_ESSENCE_MAX_STAT_GAINS:
                    upgrade_str += "Gain 1 dexterity.\n"
                    self.stats.dex += 1
                    state['stat_gains']['dex'] += 1
                    applied = True

                if enemy.name in ['Basilisk', 'Sandworm'] and \
                        state['health_gains'] < self.ABSORB_ESSENCE_MAX_HEALTH_GAINS:
                    hp_gain = min(5, self.ABSORB_ESSENCE_MAX_HEALTH_GAINS - state['health_gains'])
                    if hp_gain > 0:
                        upgrade_str += f"Gain {hp_gain} hit points.\n"
                        self.health.max += hp_gain
                        self.health.current += hp_gain
                        state['health_gains'] += hp_gain
                        applied = True

                if enemy.name == 'Mind Flayer' and state['mana_gains'] < self.ABSORB_ESSENCE_MAX_MANA_GAINS:
                    mana_gain = min(5, self.ABSORB_ESSENCE_MAX_MANA_GAINS - state['mana_gains'])
                    if mana_gain > 0:
                        upgrade_str += f"Gain {mana_gain} mana points.\n"
                        self.mana.max += mana_gain
                        self.mana.current += mana_gain
                        state['mana_gains'] += mana_gain
                        applied = True

                if enemy.name in ['Jester', 'Domingo', 'Cerberus'] and \
                        state['level_gains'] < self.ABSORB_ESSENCE_MAX_LEVEL_GAINS and \
                        not self.max_level():
                    upgrade_str += "Gain enough experience to level.\n"
                    self.level.exp += self.level.exp_to_gain
                    self.level.exp_to_gain = 0
                    self.level_up(game)
                    state['level_gains'] += 1
                    applied = True

                if enemy.name == 'Red Dragon' and not state['dragon_gold_claimed']:
                    upgrade_str += "You find a cache of gold, doubling your current stash.\n"
                    self.gold *= 2
                    state['dragon_gold_claimed'] = True
                    applied = True

                if applied:
                    upgrade_str = f"You absorb part of the {enemy.name}'s soul.\n" + upgrade_str
                    state['procs_this_floor'] += 1
                    state['procs_by_enemy'][enemy.name] = enemy_proc_count + 1
        if self.cls.name == "Lycan" and enemy.name == 'Red Dragon':
            lycan_state = self.ensure_lycan_state()
            if not lycan_state.get("dragon_essence", False):
                lycan_state["dragon_essence"] = True
                upgrade_str += (
                    f"{self.name} has harnessed the Red Dragon's essence. "
                    "It will enhance the werewolf form once Dragon Essence techniques are implemented.\n"
                )
        return upgrade_str

    def quests(self, enemy: object | None = None, item: object | None = None) -> str:
        """Update quest completion state for enemy, item, or relic progress.

        Enemy completions cover bounties plus named Main/Side defeat quests.
        Item completions match either item display names or class names so
        JSON-loaded quest definitions and object-backed definitions both work.
        When no enemy or item is supplied, the Holy Relics aggregate is checked.
        """
        quest_message = ""
        if enemy is not None:
            if enemy.name in self.quest_dict['Bounty']:
                if not self.quest_dict['Bounty'][enemy.name][2]:
                    self.quest_dict['Bounty'][enemy.name][1] += 1
                    if self.quest_dict['Bounty'][enemy.name][1] >= self.quest_dict['Bounty'][enemy.name][0]['num']:
                        self.quest_dict['Bounty'][enemy.name][2] = True
                        quest_message += "You have completed a bounty.\n"
            elif enemy.name == "Waitress":
                self.quest_dict['Side']['Something to Cry About']["Completed"] = True
                quest_message += f"You have completed the quest Something to Cry About.\n"
            else:
                for quest in self.quest_dict['Main']:
                    if self.quest_dict['Main'][quest]['What'] == enemy.name and \
                        not self.quest_dict['Main'][quest]['Completed']:
                        self.quest_dict['Main'][quest]['Completed'] = True
                        quest_message += f"You have completed the quest {quest}.\n"

                for quest in self.quest_dict['Side']:
                    quest_info = self.quest_dict['Side'][quest]
                    if (
                        quest_info.get('Type') == 'Defeat'
                        and quest_info.get('What') == enemy.name
                        and not quest_info.get('Completed')
                    ):
                        quest_info['Completed'] = True
                        quest_message += f"You have completed the quest {quest}.\n"
        elif item is not None:
            for quest in self.quest_dict['Side']:
                try:
                    quest_what = self.quest_dict['Side'][quest]['What']
                    if isinstance(quest_what, str):
                        matches_item = quest_what in [item.name, item.__class__.__name__]
                    else:
                        matches_item = quest_what.name == item.name

                    if matches_item:
                        if item.name in self.special_inventory:
                            if len(self.special_inventory[item.name]) >= self.quest_dict['Side'][quest]['Total'] and \
                                    not self.quest_dict['Side'][quest]['Completed']:
                                self.quest_dict['Side'][quest]['Completed'] = True
                                quest_message += f"You have completed the quest {quest}.\n"
                        break
                except (AttributeError, TypeError):
                    pass
        else:
            quest_message += quest_progress.sync_relic_story_progress(self)
        return quest_message
