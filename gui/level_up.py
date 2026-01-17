"""
Level Up GUI for Pygame.
Displays level up bonuses and allows stat selection.
"""
import pygame
import random


class LevelUpScreen:
    """Display level up information and handle stat selection."""
    
    def __init__(self, screen, presenter):
        self.screen = screen
        self.presenter = presenter
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Colors
        self.bg_color = (20, 20, 30)
        self.panel_color = (40, 40, 50)
        self.border_color = (100, 100, 150)
        self.text_color = (220, 220, 220)
        self.highlight_color = (255, 215, 0)
        self.gain_color = (100, 255, 100)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 56)
        self.header_font = pygame.font.Font(None, 36)
        self.stat_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
    
    def show_level_up(self, player_char, game):
        """
        Display level up screen and process level up bonuses.
        
        Args:
            player_char: The player character
            game: Game object (for compatibility, might not be needed)
        
        Returns:
            dict: Information about the level up (gains, new abilities, etc.)
        """
        # Calculate gains
        level_info = self._calculate_level_up(player_char)
        
        # Show level up information
        self._display_level_up_info(player_char, level_info)
        
        # Wait for player to acknowledge
        self._wait_for_continue()
        
        # Handle stat selection every 4 levels
        if player_char.level.level % 4 == 0:
            self._select_stat_increase(player_char)
        
        return level_info
    
    def _calculate_level_up(self, player_char):
        """Calculate all level up bonuses."""
        import abilities
        
        dv = max(1, 5 - player_char.check_mod('luck', luck_factor=8))
        
        # Calculate gains
        health_gain = random.randint(player_char.stats.con // dv, player_char.stats.con)
        mana_gain = random.randint(player_char.stats.intel // dv, player_char.stats.intel)
        
        attack_gain = random.randint(0, player_char.check_mod("luck", luck_factor=12) +
                                    (player_char.stats.strength // 12) + 
                                    max(1, player_char.cls.att_plus // 2))
        defense_gain = random.randint(0, player_char.check_mod("luck", luck_factor=15) + 
                                    (player_char.stats.con // 12) + 
                                    max(1, player_char.cls.def_plus // 2))
        magic_gain = random.randint(0, player_char.check_mod("luck", luck_factor=12) +
                                    (player_char.stats.intel // 12) + 
                                    max(1, player_char.cls.int_plus // 2))
        magic_def_gain = random.randint(0, player_char.check_mod("luck", luck_factor=15) +
                                    (player_char.stats.wisdom // 12) + 
                                    max(1, player_char.cls.wis_plus // 2))
        
        # Apply gains
        player_char.health.max += health_gain
        player_char.mana.max += mana_gain
        
        if player_char.in_town():
            player_char.health.current = player_char.health.max
            player_char.mana.current = player_char.mana.max
        
        player_char.combat.attack += attack_gain
        player_char.combat.defense += defense_gain
        player_char.combat.magic += magic_gain
        player_char.combat.magic_def += magic_def_gain
        
        player_char.level.level += 1
        
        # Check for new spells/skills
        new_abilities = []
        spell_upgrades = []
        skill_upgrades = []
        
        # Check for new spell
        if str(player_char.level.level) in abilities.spell_dict.get(player_char.cls.name, {}):
            spell = abilities.spell_dict[player_char.cls.name][str(player_char.level.level)]
            spell_gain = spell()
            spell_name = spell_gain.name
            
            if spell_name in player_char.spellbook['Spells']:
                spell_upgrades.append(f"{spell_name} goes up a level")
            else:
                try:
                    if spell.mro()[1]().name in player_char.spellbook['Spells']:
                        old_name = spell.mro()[1]().name
                        spell_upgrades.append(f"{old_name} upgraded to {spell_name}")
                        del player_char.spellbook['Spells'][old_name]
                    else:
                        new_abilities.append(f"Spell: {spell_name}")
                except TypeError:
                    new_abilities.append(f"Spell: {spell_name}")
            
            player_char.spellbook['Spells'][spell_name] = spell_gain
        
        # Check for new skill
        if str(player_char.level.level) in abilities.skill_dict.get(player_char.cls.name, {}):
            skill = abilities.skill_dict[player_char.cls.name][str(player_char.level.level)]
            skill_gain = skill()
            skill_name = skill_gain.name
            
            if skill_name in player_char.spellbook['Skills']:
                skill_upgrades.append(f"{skill_name} goes up a level")
            else:
                try:
                    if skill.mro()[1]().name in player_char.spellbook['Skills']:
                        old_name = skill.mro()[1]().name
                        skill_upgrades.append(f"{old_name} upgraded to {skill_name}")
                        del player_char.spellbook['Skills'][old_name]
                    else:
                        new_abilities.append(f"Skill: {skill_name}")
                except TypeError:
                    new_abilities.append(f"Skill: {skill_name}")
            
            player_char.spellbook['Skills'][skill_name] = skill_gain
            
            # Handle special skill effects
            if skill_name == 'Health/Mana Drain':
                for old_skill in ["Health Drain", "Mana Drain"]:
                    if old_skill in player_char.spellbook["Skills"]:
                        del player_char.spellbook['Skills'][old_skill]
            elif skill_name == "True Piercing Strike":
                for old_skill in ["Piercing Strike", "True Strike"]:
                    if old_skill in player_char.spellbook["Skills"]:
                        del player_char.spellbook['Skills'][old_skill]
            elif skill_name == 'Familiar' and hasattr(player_char, 'familiar'):
                familiar_msg = player_char.familiar.level_up()
                new_abilities.append(f"Familiar: {familiar_msg}")
            elif skill_name in ["Transform", "Purity of Body"]:
                effect_msg = skill_gain.use(player_char)
                new_abilities.append(effect_msg)
        
        # Update exp requirement
        if not player_char.max_level():
            player_char.level.exp_to_gain += (player_char.exp_scale ** player_char.level.pro_level) * player_char.level.level
        else:
            player_char.level.exp_to_gain = "MAX"
        
        return {
            'new_level': player_char.level.level,
            'health_gain': health_gain,
            'mana_gain': mana_gain,
            'attack_gain': attack_gain,
            'defense_gain': defense_gain,
            'magic_gain': magic_gain,
            'magic_def_gain': magic_def_gain,
            'new_abilities': new_abilities,
            'spell_upgrades': spell_upgrades,
            'skill_upgrades': skill_upgrades
        }
    
    def _display_level_up_info(self, player_char, level_info):
        """Display the level up information screen."""
        self.screen.fill(self.bg_color)
        
        y = 50
        
        # Title
        title = self.title_font.render("LEVEL UP!", True, self.highlight_color)
        title_rect = title.get_rect(center=(self.width // 2, y))
        self.screen.blit(title, title_rect)
        y += 80
        
        # New level
        level_text = self.header_font.render(
            f"You are now level {level_info['new_level']}!",
            True, self.text_color
        )
        level_rect = level_text.get_rect(center=(self.width // 2, y))
        self.screen.blit(level_text, level_rect)
        y += 60
        
        # Stats gained
        stats_header = self.header_font.render("Stats Gained:", True, self.text_color)
        self.screen.blit(stats_header, (100, y))
        y += 50
        
        gains = [
            f"Health: +{level_info['health_gain']}",
            f"Mana: +{level_info['mana_gain']}",
        ]
        
        if level_info['attack_gain'] > 0:
            gains.append(f"Attack: +{level_info['attack_gain']}")
        if level_info['defense_gain'] > 0:
            gains.append(f"Defense: +{level_info['defense_gain']}")
        if level_info['magic_gain'] > 0:
            gains.append(f"Magic: +{level_info['magic_gain']}")
        if level_info['magic_def_gain'] > 0:
            gains.append(f"Magic Defense: +{level_info['magic_def_gain']}")
        
        for gain in gains:
            text = self.stat_font.render(gain, True, self.gain_color)
            self.screen.blit(text, (120, y))
            y += 35
        
        # New abilities
        if level_info['new_abilities']:
            y += 20
            abilities_header = self.header_font.render("New Abilities:", True, self.text_color)
            self.screen.blit(abilities_header, (100, y))
            y += 50
            
            for ability in level_info['new_abilities']:
                text = self.stat_font.render(ability, True, self.highlight_color)
                self.screen.blit(text, (120, y))
                y += 35
        
        # Upgrades
        all_upgrades = level_info['spell_upgrades'] + level_info['skill_upgrades']
        if all_upgrades:
            y += 20
            upgrades_header = self.header_font.render("Upgrades:", True, self.text_color)
            self.screen.blit(upgrades_header, (100, y))
            y += 50
            
            for upgrade in all_upgrades:
                text = self.stat_font.render(upgrade, True, self.highlight_color)
                self.screen.blit(text, (120, y))
                y += 35
        
        # Footer
        footer = self.small_font.render("Press any key to continue...", True, self.text_color)
        footer_rect = footer.get_rect(center=(self.width // 2, self.height - 40))
        self.screen.blit(footer, footer_rect)
        
        pygame.display.flip()
    
    def _select_stat_increase(self, player_char):
        """Allow player to select a stat to increase (every 4 levels)."""
        stat_options = [
            ('Strength', player_char.stats.strength),
            ('Intelligence', player_char.stats.intel),
            ('Wisdom', player_char.stats.wisdom),
            ('Constitution', player_char.stats.con),
            ('Charisma', player_char.stats.charisma),
            ('Dexterity', player_char.stats.dex)
        ]
        
        selected = 0
        choosing = True
        
        while choosing:
            # Render selection screen
            self.screen.fill(self.bg_color)
            
            y = 80
            title = self.title_font.render("Choose Stat to Increase", True, self.highlight_color)
            title_rect = title.get_rect(center=(self.width // 2, y))
            self.screen.blit(title, title_rect)
            y += 100
            
            # Display stat options
            for i, (stat_name, stat_value) in enumerate(stat_options):
                if i == selected:
                    # Highlight selected
                    rect = pygame.Rect(self.width // 2 - 200, y - 5, 400, 40)
                    pygame.draw.rect(self.screen, self.border_color, rect)
                    pygame.draw.rect(self.screen, self.highlight_color, rect, 3)
                
                text = self.header_font.render(
                    f"{stat_name}: {stat_value} -> {stat_value + 1}",
                    True, self.text_color
                )
                text_rect = text.get_rect(center=(self.width // 2, y + 15))
                self.screen.blit(text, text_rect)
                y += 60
            
            # Footer
            footer = self.small_font.render(
                "Arrow Keys: Navigate | Enter: Select",
                True, self.text_color
            )
            footer_rect = footer.get_rect(center=(self.width // 2, self.height - 40))
            self.screen.blit(footer, footer_rect)
            
            pygame.display.flip()
            
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(stat_options)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(stat_options)
                    elif event.key == pygame.K_RETURN:
                        # Apply stat increase
                        stat_name = stat_options[selected][0]
                        if stat_name == 'Strength':
                            player_char.stats.strength += 1
                        elif stat_name == 'Intelligence':
                            player_char.stats.intel += 1
                        elif stat_name == 'Wisdom':
                            player_char.stats.wisdom += 1
                        elif stat_name == 'Constitution':
                            player_char.stats.con += 1
                        elif stat_name == 'Charisma':
                            player_char.stats.charisma += 1
                        elif stat_name == 'Dexterity':
                            player_char.stats.dex += 1
                        
                        # Show confirmation
                        self._show_stat_confirmation(stat_name, stat_options[selected][1] + 1)
                        choosing = False
    
    def _show_stat_confirmation(self, stat_name, new_value):
        """Show confirmation of stat increase."""
        self.screen.fill(self.bg_color)
        
        message = self.header_font.render(
            f"{stat_name} increased to {new_value}!",
            True, self.gain_color
        )
        message_rect = message.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(message, message_rect)
        
        footer = self.small_font.render("Press any key to continue...", True, self.text_color)
        footer_rect = footer.get_rect(center=(self.width // 2, self.height - 40))
        self.screen.blit(footer, footer_rect)
        
        pygame.display.flip()
        self._wait_for_continue()
    
    def _wait_for_continue(self):
        """Wait for player to press a key."""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    waiting = False
