"""Player leveling, class upgrades, and quest progression."""

import random

from .. import quest_progress


class PlayerProgressionMixin:
    def level_up(self, game=None, textbox=None, menu=None):
        """Level up the player character.

        Args:
            game: Game instance (for UI interactions, optional)
            textbox: Optional TextBox UI component
            menu: Optional SelectionPopupMenu UI component
        """
        from ..progression import (
            award_experience,
            cumulative_experience_for_level,
            ensure_progression,
            level_up_message,
        )

        progression = ensure_progression(self)
        if progression.level >= 100:
            return None
        required_total = cumulative_experience_for_level(progression.level + 1)
        result = award_experience(
            self,
            max(0, required_total - progression.total_xp),
            rng=random,
        )
        if textbox and game:
            textbox.print_text_in_rectangle(level_up_message(result))
            game.stdscr.getch()
            textbox.clear_rectangle()
        return result

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
