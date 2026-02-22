"""
Dungeon Navigation Manager
Handles dungeon exploration logic, movement, and interactions.
"""

import os
import random
import sys
import traceback

import pygame

from src.core import items, enemies, companions
from src.core.data.data_loader import get_special_events
from src.core.player import DIRECTIONS
from .character_screen import CharacterScreen
from .combat_manager import GUICombatManager
from .dungeon_hud import DungeonHUD
from .enhanced_dungeon_renderer import EnhancedDungeonRenderer
from .loot_popup import LootPopup


class DungeonManager:
    """
    Manages dungeon exploration in first-person view.
    Handles movement, interactions, and ties together rendering and game logic.
    """

    def __init__(self, presenter, player_char, game_instance):
        self.presenter = presenter
        self.player_char = player_char
        self.game = game_instance

        # Cache for dungeon background (used for loading screen & character menu)
        self._dungeon_background = None
        self._dungeon_background_loaded = False

        # Initialize renderer and HUD
        self.renderer = EnhancedDungeonRenderer(presenter)
        self.hud = DungeonHUD(presenter)

        # Initialize combat manager
        self.combat_manager = GUICombatManager(presenter, self.hud, game_instance)
        # Give combat manager access to dungeon renderer for in-place combat
        self.combat_manager.dungeon_renderer = self.renderer

        # Initialize character screen (shared with town UI)
        self.character_screen = CharacterScreen(presenter)

        # Initialize loot popup
        self.loot_popup = LootPopup(presenter.screen, presenter)

        # Import shop manager (lazy import to avoid circular dependencies)
        from .shops import ShopManager
        self.shop_manager = ShopManager(presenter, player_char)

        # Import ultimate armor shop
        from .ultimate_armor import UltimateArmorShop
        self.ultimate_armor_shop = UltimateArmorShop(presenter)

        # Message log
        self.messages = []
        self.max_messages = 50

        # Control state
        self.running = True

        # --- Render throttling / caching ---
        # The 3D view is expensive; only redraw it when something actually changes.
        self.view_dirty = True
        self.ui_dirty = True
        self._render_error_logged = False
        self._cached_view = None  # pygame.Surface
        self._cached_frame = None  # pygame.Surface
        self._next_anim_tick = 0
        self._anim_interval_ms = 120  # torch flicker / subtle view effects

        # Apply dungeon background to character menu in-dungeon
        dungeon_bg = self._load_dungeon_background()
        if dungeon_bg:
            self.character_screen.background = dungeon_bg

        if hasattr(self.presenter, "set_background_provider"):
            self.presenter.set_background_provider(self._get_popup_background)

    def _get_popup_background(self):
        if self._cached_frame is not None:
            return self._cached_frame
        if self._cached_view is not None:
            return self._cached_view
        return self.presenter.screen.copy()

    def add_message(self, message: str):
        """Add a message to the message log."""
        # Split long messages into multiple lines if needed
        max_length = 60
        if len(message) > max_length:
            words = message.split()
            lines = []
            current_line = ""
            for word in words:
                if len(current_line) + len(word) + 1 <= max_length:
                    current_line += (word + " ")
                else:
                    if current_line:
                        lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())
            for line in lines:
                self.messages.append(line)
        else:
            self.messages.append(message)

        # Keep only last max_messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

        # Messages affect the UI overlay.
        self.ui_dirty = True

    def get_current_tile(self):
        """Return the tile the player is currently standing on."""
        return self.player_char.world_dict.get(
            (self.player_char.location_x, self.player_char.location_y, self.player_char.location_z)
        )
    
    def _check_random_cry(self):
        """
        Check if player should hear random cries on floor 2 during "Something to Cry About" quest.
        Cries get louder as player gets closer to the dead body location.
        """
        # Only trigger on floor 2 (location_z == 2)
        if self.player_char.location_z != 2:
            return
        
        # Check if quest "Something to Cry About" is active and not completed
        if 'Something to Cry About' not in self.player_char.quest_dict.get('Side', {}):
            return
        
        if self.player_char.quest_dict['Side']['Something to Cry About'].get('Completed'):
            return
        
        # Dead body is at approximately (18, 12, 2) - you can adjust these coords if needed
        dead_body_x, dead_body_y = 18, 12
        player_x = self.player_char.location_x
        player_y = self.player_char.location_y
        
        # Calculate distance to dead body
        distance = ((player_x - dead_body_x) ** 2 + (player_y - dead_body_y) ** 2) ** 0.5
        
        # Only trigger if within 30 tiles of dead body
        if distance > 30:
            return
        
        # Random chance increases as player gets closer
        # At 5 tiles: 60% chance, at 10 tiles: 40% chance, at 20 tiles: 20% chance
        base_chance = max(0.1, (30 - distance) / 50)  # Scales from 10% to 60%
        
        if random.random() > base_chance:
            return
        
        # Generate cry message based on distance
        cries = [
            "*Heart-wrenching sobs echo through the dungeon...*",
            "*A mournful wail reverberates in the distance...*",
            "*The anguished cry of a broken soul pierces the air...*",
            "*You hear desperate weeping somewhere nearby...*",
            "*A wail of grief and despair fills the dungeon...*",
            "*Anguished sobbing echoes through the corridors...*",
        ]
        
        cry = random.choice(cries)
        self.add_message(cry)

    def _load_dungeon_background(self):
        """Load and scale the dungeon background once."""
        if self._dungeon_background_loaded:
            return self._dungeon_background

        self._dungeon_background_loaded = True
        # Assets are now in src/ui_pygame/assets/
        bg_path = os.path.join(os.path.dirname(__file__), "..", "assets", "backgrounds", "dungeon.png")
        bg_path = os.path.abspath(bg_path)

        if os.path.exists(bg_path):
            try:
                bg_image = pygame.image.load(bg_path).convert()
                bg_width, bg_height = bg_image.get_size()
                scale_x = self.presenter.width / bg_width
                scale_y = self.presenter.height / bg_height
                scale = max(scale_x, scale_y)

                new_width = int(bg_width * scale)
                new_height = int(bg_height * scale)
                self._dungeon_background = pygame.transform.scale(bg_image, (new_width, new_height))
            except Exception as exc:
                print(f"Warning: Could not load dungeon background: {exc}")
                self._dungeon_background = None
        else:
            print(f"Warning: Dungeon background not found at {bg_path}")
            self._dungeon_background = None

        return self._dungeon_background

    def _show_dungeon_loading_screen(self, message: str, duration: float = 1.25):
        """Display a short fake-loading screen with progress bar."""
        bg = self._load_dungeon_background()
        screen = self.presenter.screen
        clock = pygame.time.Clock()

        start_ms = pygame.time.get_ticks()
        end_ms = start_ms + int(duration * 1000)

        while True:
            now = pygame.time.get_ticks()
            progress = min(1.0, (now - start_ms) / max(1, end_ms - start_ms))

            # Draw background + dim overlay
            if bg:
                bg_rect = bg.get_rect(center=(self.presenter.width // 2, self.presenter.height // 2))
                screen.blit(bg, bg_rect)
            else:
                screen.fill((0, 0, 0))

            overlay = pygame.Surface((self.presenter.width, self.presenter.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            screen.blit(overlay, (0, 0))

            # Title text
            text = self.presenter.title_font.render(message, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.presenter.width // 2, self.presenter.height // 2 - 40))
            screen.blit(text, text_rect)

            # Progress bar
            bar_width = self.presenter.width // 2
            bar_height = 24
            bar_x = (self.presenter.width - bar_width) // 2
            bar_y = self.presenter.height // 2 + 10

            border_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
            fill_rect = pygame.Rect(bar_x + 3, bar_y + 3, int((bar_width - 6) * progress), bar_height - 6)

            pygame.draw.rect(screen, (220, 220, 220), border_rect, 2)
            pygame.draw.rect(screen, (218, 165, 32), fill_rect)

            # Percent text
            percent_text = self.presenter.small_font.render(f"{int(progress * 100)}%", True, (255, 255, 255))
            percent_rect = percent_text.get_rect(center=(self.presenter.width // 2, bar_y + bar_height + 16))
            screen.blit(percent_text, percent_rect)

            pygame.display.flip()

            # Keep window responsive
            for event in pygame.event.get(pygame.QUIT):
                pygame.quit()
                sys.exit()

            if progress >= 1.0:
                break

            clock.tick(60)

    def _mark_view_dirty(self):
        """Mark the 3D view and UI overlays to redraw next frame."""
        self.view_dirty = True
        self.ui_dirty = True

    def _refresh_cached_frame(self):
        """Ensure cached background reflects the current tile before popups/combat."""
        if self.view_dirty or self.ui_dirty or self._cached_view is None:
            self._render()

    def move_forward(self):
        """Move one tile forward if the path is clear."""
        dx, dy = DIRECTIONS[self.player_char.facing]["move"]
        ahead_pos = (
            self.player_char.location_x + dx,
            self.player_char.location_y + dy,
            self.player_char.location_z,
        )

        tile_ahead = self.player_char.world_dict.get(ahead_pos)
        if tile_ahead is None:
            self.add_message("You can't move that way.")
            return False

        tile_type = type(tile_ahead).__name__

        # Impassable tiles (walls, undetected hidden doors, etc.)
        if not getattr(tile_ahead, "enter", True):
            if tile_type == "OreVaultDoor" and getattr(tile_ahead, "locked", False):
                self.add_message("A solid wall blocks your path.")
            else:
                self.add_message("You can't move that way.")
            return False

        # Closed or locked doors block movement
        if 'Door' in tile_type:
            if hasattr(tile_ahead, "open") and tile_ahead.open:
                pass
            elif getattr(tile_ahead, "locked", False):
                self.add_message("A locked door blocks your path. (Press O to unlock)")
                return False
            elif hasattr(tile_ahead, "open") and not tile_ahead.open:
                self.add_message("A closed door blocks your path. (Press O to open)")
                return False

        # Final blocker requires relics
        if 'FinalBlocker' in tile_type and not self.player_char.has_relics():
            blocked_dir = getattr(tile_ahead, 'blocked', None)
            if blocked_dir and blocked_dir.lower() == self.player_char.facing:
                self.add_message("An invisible force prevents you from moving forward!")
                return False

        # Record previous position for tiles that inspect it (doors, blockers, etc.)
        self.player_char.previous_location = (
            self.player_char.location_x,
            self.player_char.location_y,
            self.player_char.location_z,
        )

        # Move the player
        self.player_char.location_x += dx
        self.player_char.location_y += dy

        # The view definitely changed.
        self._mark_view_dirty()

        # Update tile visited status
        new_tile = self.get_current_tile()
        if new_tile:
            new_tile.visited = True
            new_tile.adjacent_visited(self.player_char)

        # Add movement confirmation
        self.add_message(f"Moved to ({self.player_char.location_x}, {self.player_char.location_y})")

        # Debug: log tile type and FirePath state on each step
        try:
            x = self.player_char.location_x
            y = self.player_char.location_y
            z = self.player_char.location_z
            tname = type(new_tile).__name__ if new_tile else "None"
            if new_tile and ('FirePath' in tname):
                resist = self.player_char.check_mod('resist', typ='Fire')
        except Exception as e:
            pass

        # Get tile intro text
        intro_messages = self._get_tile_intro()
        if intro_messages:
            for message in intro_messages:
                self.add_message(message)

        # Check for random encounters or tile effects
        self._check_tile_effects()

        return True

    def turn_left(self):
        """Turn player 90 degrees counterclockwise."""
        directions = ["north", "east", "south", "west"]
        current_idx = directions.index(self.player_char.facing)
        self.player_char.facing = directions[(current_idx - 1) % 4]
        self.add_message(f"You turn to face {self.player_char.facing}.")
        self._mark_view_dirty()
        # Emit any context intro messages for the new facing (e.g., hidden door detection)
        intro_messages = self._get_tile_intro()
        if intro_messages:
            for message in intro_messages:
                self.add_message(message)

    def turn_right(self):
        """Turn player 90 degrees clockwise."""
        directions = ["north", "east", "south", "west"]
        current_idx = directions.index(self.player_char.facing)
        self.player_char.facing = directions[(current_idx + 1) % 4]
        self.add_message(f"You turn to face {self.player_char.facing}.")
        self._mark_view_dirty()
        # Emit any context intro messages for the new facing (e.g., hidden door detection)
        intro_messages = self._get_tile_intro()
        if intro_messages:
            for message in intro_messages:
                self.add_message(message)

    def turn_around(self):
        """Turn player 180 degrees."""
        directions = ["north", "east", "south", "west"]
        current_idx = directions.index(self.player_char.facing)
        self.player_char.facing = directions[(current_idx + 2) % 4]
        self.add_message(f"You turn around to face {self.player_char.facing}.")
        self._mark_view_dirty()
        # Emit any context intro messages for the new facing (e.g., hidden door detection)
        intro_messages = self._get_tile_intro()
        if intro_messages:
            for message in intro_messages:
                self.add_message(message)

    def use_stairs_up(self):
        """Use stairs to go up a level."""
        current_tile = self.get_current_tile()
        tile_type = type(current_tile).__name__

        if 'StairsUp' not in tile_type and 'LadderUp' not in tile_type:
            self.add_message("There are no stairs here!")
            return False

        target_level = self.player_char.location_z - 1
        loading_text = "Returning to town..." if target_level <= 0 else f"Ascending to level {target_level}..."
        self._show_dungeon_loading_screen(loading_text)

        self.player_char.location_z = target_level
        self._mark_view_dirty()
        self.add_message(f"You climb the stairs upward...")

        # Check if returned to town
        if self.player_char.in_town():
            self.add_message("You emerge back in town!")
            self.running = False  # Exit dungeon mode
            return True
        else:
            self.add_message(f"Now on dungeon level {self.player_char.location_z}")

        return True

    def use_stairs_down(self):
        """Use stairs to go down a level."""
        current_tile = self.get_current_tile()
        tile_type = type(current_tile).__name__

        if 'StairsDown' not in tile_type and 'LadderDown' not in tile_type:
            self.add_message("There are no stairs here!")
            return False

        target_level = self.player_char.location_z + 1
        self._show_dungeon_loading_screen(f"Descending to level {target_level}...")

        self.player_char.location_z = target_level
        self._mark_view_dirty()
        self.add_message(f"You descend the stairs deeper into the dungeon...")
        self.add_message(f"Now on dungeon level {self.player_char.location_z}")

        return True

    def interact(self):
        """Interact with the tile ahead (or current tile for some types)."""
        # For interactive objects like chests/doors/relics, check tile ahead
        # For things you stand on (stairs, shops), check current tile

        self._mark_view_dirty()

        # First check tile ahead
        direction = self.player_char.facing
        dx, dy = DIRECTIONS[direction]['move']
        ahead_x = self.player_char.location_x + dx
        ahead_y = self.player_char.location_y + dy
        ahead_z = self.player_char.location_z

        ahead_tile = self.player_char.world_dict.get((ahead_x, ahead_y, ahead_z))

        if ahead_tile:
            tile_type = type(ahead_tile).__name__

            # Interact with tile ahead for these types
            if 'Chest' in tile_type:
                self._interact_chest(ahead_tile, tile_type)
                return
            elif 'Door' in tile_type:
                # Special check for OreVaultDoor - only allow interaction if detected or open
                if tile_type == 'OreVaultDoor':
                    has_cryptic_key = "Cryptic Key" in self.player_char.inventory
                    has_keen_eye = 'Keen Eye' in self.player_char.spellbook.get('Skills', [])
                    is_open = getattr(ahead_tile, 'open', False)
                    if not (has_cryptic_key or has_keen_eye or is_open):
                        # Door not detected - treat like a wall
                        self.add_message("There's nothing to interact with here.")
                        return
                self._interact_door(ahead_tile)
                return
            elif 'Relic' in tile_type:
                self._interact_relic(ahead_tile)
                return
            elif 'Boulder' in tile_type:
                self._interact_boulder(ahead_tile)
                return
            elif 'UnobtainiumRoom' in tile_type:
                self._interact_unobtainium_room(ahead_tile)
                return

        # Check current tile for things you stand on
        current_tile = self.get_current_tile()
        if not current_tile:
            self.add_message("There's nothing to interact with here.")
            return

        tile_type = type(current_tile).__name__

        if 'SecretShop' in tile_type:
            # Show special message on first discovery
            if not hasattr(current_tile, 'read') or not current_tile.read:
                self.presenter.show_message(
                    "You've discovered a secret shop!\n\n"
                    "A mysterious merchant appears from the shadows...\n\n"
                    "\"Welcome, traveler. I have rare goods for sale.\""
                )
                current_tile.read = True

            self.add_message("Entering secret shop...")
            self.shop_manager.visit_secret_shop()
        elif 'UltimateArmorShop' in tile_type:
            self.add_message("Approaching the forge...")
            self.ultimate_armor_shop.visit_shop(self.player_char, current_tile)
        elif 'WarpPoint' in tile_type:
            self._handle_warp_point(current_tile)
        elif 'UndergroundSpring' in tile_type:
            self._interact_underground_spring(current_tile)
        elif 'UnobtainiumRoom' in tile_type:
            self._interact_unobtainium_room(current_tile)
        elif 'DeadBody' in tile_type:
            self._interact_dead_body(current_tile)
        elif 'FinalRoom' in tile_type:
            self._interact_final_room(current_tile)
        else:
            self.add_message("There's nothing to interact with here.")

    def _interact_chest(self, chest_tile, tile_type):
        """Handle chest interaction."""
        # Check if already opened
        if hasattr(chest_tile, 'open') and chest_tile.open:
            self.add_message("This chest has already been opened.")
            return

        # Check if locked
        if hasattr(chest_tile, 'locked') and chest_tile.locked:
            # Try to unlock
            if "Master Key" in self.player_char.special_inventory:
                chest_tile.locked = False
                self.add_message("You unlock the chest with the Master Key!")
            elif "Lockpick" in self.player_char.spellbook.get("Skills", []):
                chest_tile.locked = False
                self.add_message("You skillfully pick the lock!")
            elif "Key" in self.player_char.inventory:
                # Ask if they want to use a key with visual popup
                use_key = self.loot_popup.show_unlock_prompt("chest")
                if use_key:
                    chest_tile.locked = False
                    self.player_char.modify_inventory(
                        self.player_char.inventory["Key"][0],
                        subtract=True
                    )
                    self.add_message("You unlock the chest with a Key!")
                else:
                    self.add_message("The chest remains locked.")
                    return
            else:
                self.add_message("The chest is locked! You need a Key or Lockpick skill.")
                return

        # Check for Mimic (FunhouseMimicChest always spawns one; other chests have random chance)
        locked = int('Locked' in tile_type)
        plus = int('ChestRoom2' in tile_type)
        is_funhouse_mimic = 'FunhouseMimicChest' in tile_type
        if is_funhouse_mimic or (not random.randint(0, 9 + self.player_char.check_mod('luck', luck_factor=3)) and self.player_char.level.level >= 10):
            print("[DEBUG] Mimic encounter triggered in chest interaction.")
            from src.core import enemies
            # For funhouse mimic chest, spawn level 4 mimic; for other chests use normal scaling
            mimic_level = 4 if is_funhouse_mimic else (self.player_char.location_z + locked + plus)
            enemy = enemies.Mimic(mimic_level)
            chest_tile.enemy = enemy
            self.add_message("There is a Mimic in the chest!")
            # Start combat with the Mimic
            self.player_char.state = 'fight'
            self._refresh_cached_frame()
            victory = self.combat_manager.start_combat(self.player_char, enemy, chest_tile)
            if not getattr(enemy, "is_alive", lambda: True)():
                chest_tile.enemy = None
            if not victory or not self.player_char.is_alive():
                return  # Player fled or died, don't open chest

        # Open the chest
        chest_tile.open = True

        # Generate loot if not already generated
        if not hasattr(chest_tile, 'loot') or chest_tile.loot is None:
            chest_tile.generate_loot()

        # Show loot with visual popup
        if chest_tile.loot:
            loot_item = chest_tile.loot()
            # Show the loot popup first
            chest_name = "Locked Chest" if "Locked" in tile_type else "Chest"
            self.loot_popup.show_loot(loot_item, chest_name)
            # Then add to inventory
            self.player_char.modify_inventory(loot_item)
            self.add_message(f"Obtained {loot_item.name}!")
            
            # Funhouse Mimic Chest also drops a Jester Token
            if is_funhouse_mimic:
                from src.core import items as items_module
                token = items_module.JesterToken()
                self.player_char.modify_inventory(token)
                self.add_message(f"A shimmering {token.name} manifests as the Mimic dissolves!")
        else:
            self.loot_popup.show_loot([], "Empty Chest")

    def _interact_door(self, door_tile):
        """Handle door interaction."""
        if not hasattr(door_tile, 'locked'):
            self.add_message("This door cannot be interacted with.")
            return

        if not door_tile.locked:
            self.add_message("The door is already unlocked.")
            return

        # Special handling for OreVaultDoor
        door_type = type(door_tile).__name__
        if door_type == 'OreVaultDoor':
            # Try to unlock with Cryptic Key first
            if "Cryptic Key" in self.player_char.inventory:
                door_tile.locked = False
                door_tile.open = True
                door_tile.enter = True
                door_tile.detected = True
                self.player_char.modify_inventory(
                    self.player_char.inventory['Cryptic Key'][0],
                    subtract=True
                )
                self.add_message("The Cryptic Key turns smoothly in the hidden lock.")
                self.add_message("The door swings open, revealing the vault beyond!")
                self._mark_view_dirty()
                return
            # Master Key works if player has Keen Eye
            elif "Master Key" in self.player_char.special_inventory:
                if 'Keen Eye' in self.player_char.spellbook.get('Skills', []):
                    door_tile.locked = False
                    door_tile.open = True
                    door_tile.enter = True
                    door_tile.detected = True
                    self.add_message("You unlock and open the hidden door with the Master Key!")
                    self._mark_view_dirty()
                    return
            # Master Lockpick works if player has Keen Eye
            elif 'Master Lockpick' in self.player_char.spellbook.get('Skills', []):
                if 'Keen Eye' in self.player_char.spellbook.get('Skills', []):
                    door_tile.locked = False
                    door_tile.open = True
                    door_tile.enter = True
                    door_tile.detected = True
                    self.add_message("You skillfully pick the hidden door's lock!")
                    self._mark_view_dirty()
                    return
            # If we get here, they can't unlock it
            self.add_message("You sense something is hidden here, but you lack the means to open it.")
            return

        # Regular door handling
        # Try to unlock
        if "Master Key" in self.player_char.special_inventory:
            door_tile.locked = False
            door_tile.open = True
            door_tile.blocked = None
            self.add_message("You unlock and open the door with the Master Key!")
        elif "Master Lockpick" in self.player_char.spellbook.get("Skills", []):
            door_tile.locked = False
            door_tile.open = True
            door_tile.blocked = None
            self.add_message("You skillfully pick the lock and open the door!")
        elif "Old Key" in self.player_char.inventory:
            use_key = self.loot_popup.show_unlock_prompt("door")
            if use_key:
                door_tile.locked = False
                door_tile.open = True
                door_tile.blocked = None
                self.player_char.modify_inventory(
                    self.player_char.inventory["Old Key"][0],
                    subtract=True
                )
                self.add_message("You unlock and open the door with an Old Key!")
            else:
                self.add_message("The door remains locked.")
        else:
            self.add_message("The door is locked! You need an Old Key or Master Lockpick skill.")

    def _interact_relic(self, relic_tile):
        """Handle relic room interaction."""
        if hasattr(relic_tile, 'read') and relic_tile.read:
            self.add_message("You already collected the relic from this room.")
            return

        # Get the appropriate relic for this level
        z = self.player_char.location_z
        relics = [
            items.Relic1(), items.Relic2(), items.Relic3(),
            items.Relic4(), items.Relic5(), items.Relic6()
        ]

        if 1 <= z <= 6:
            try:
                if self.game is not None:
                    self.game.special_event("Relic Room")
            except Exception:
                pass
            relic = relics[z - 1]
            self.add_message(f"You found a relic: {relic.name}!")
            self.player_char.modify_inventory(relic, rare=True, quest=True)
            relic_tile.read = True

            # Restore HP and MP
            self.player_char.health.current = self.player_char.health.max
            self.player_char.mana.current = self.player_char.mana.max
            self.add_message("Your health and mana have been fully restored!")
        else:
            self.add_message("The pedestal is empty.")

    def _handle_warp_point(self, warp_tile):
        """Handle warp point interaction - return to town."""
        choice = self.presenter.render_menu(
            "You've found a warp point!\n\nDo you want to return to town?",
            ["Yes", "No"]
        )

        if choice == 0:  # Yes
            self.add_message("Warping to town...")

            # Move player to town using proper method
            self.player_char.to_town()

            # Exit dungeon exploration - return to town menu
            self.running = False
        else:
            self.add_message("You remain in the dungeon.")
            warp_tile.warped = False

    def _interact_boulder(self, boulder_tile):
        """Handle boulder interaction - can find Excaliper sword."""
        if hasattr(boulder_tile, 'read') and boulder_tile.read:
            self.add_message("Just a broken boulder where you found that sword.")
            return

        # Check if player has drunk from the spring
        spring_tile = self.player_char.world_dict.get((4, 9, 3))
        if spring_tile and hasattr(spring_tile, 'drink') and spring_tile.drink:
            self.add_message("You find a magnificent sword embedded in the boulder!")
            self.add_message("You obtained: Excaliper!")
            self.player_char.modify_inventory(items.Excaliper(), rare=True)
            boulder_tile.read = True
        else:
            self.add_message("An oddly placed boulder. Nothing seems special about it.")

    def _interact_underground_spring(self, spring_tile):
        """Handle underground spring interaction."""
        from .confirmation_popup import ConfirmationPopup
        popup = ConfirmationPopup(
            self.presenter,
            "You see a refreshing underground spring.\n\nDo you want to drink from it?",
            show_buttons=True,
        )
        if not popup.show():
            return

        # Check for Naivete quest
        if "Naivete" in self.player_char.quest_dict.get("Side", {}):
            if not self.player_char.quest_dict["Side"]["Naivete"]["Completed"]:
                self.add_message("You fill the vial with spring water.")
                self.player_char.modify_inventory(items.EmptyVial(), subtract=True, rare=True)
                self.player_char.modify_inventory(items.SpringWater(), rare=True)
                self.player_char.quest_dict["Side"]["Naivete"]["Completed"] = True
                self.add_message("Quest completed: Naivete")
                from .confirmation_popup import ConfirmationPopup
                popup = ConfirmationPopup(
                    self.presenter,
                    "You fill the empty vial with Spring Water.\n\nItem received: Spring Water",
                    show_buttons=False,
                )
                popup.show()

        # Random encounter with Fuath
        if self.player_char.level.pro_level > 1 and not random.randint(0, 1):
            if not hasattr(spring_tile, 'defeated') or not spring_tile.defeated:
                self.add_message("A Fuath emerges from the spring!")

                enemy = enemies.Fuath()

                # Start combat
                self._refresh_cached_frame()
                combat_won = self.combat_manager.start_combat(
                    self.player_char,
                    enemy,
                    spring_tile
                )

                if combat_won and "Summoner" in self.player_char.cls.name:
                    if "Fuath" not in self.player_char.summons:
                        self.add_message("The Fuath pledges loyalty to you!")
                        summon = companions.Fuath()
                        summon.initialize_stats(self.player_char)
                        self.player_char.summons[summon.name] = summon

                spring_tile.defeated = True

        # Drink from spring
        if not hasattr(spring_tile, 'drink'):
            spring_tile.drink = False

        if not spring_tile.drink:
            self.add_message("You drink from the spring... nothing seems to have changed.")
            spring_tile.drink = True

        # Check for Excaliper quest
        if not hasattr(spring_tile, 'nimue'):
            spring_tile.nimue = False

        if not spring_tile.nimue and "Excaliper" in self.player_char.special_inventory:
            self.add_message("A beautiful woman rises from the spring!")
            self.add_message("She takes the Excaliper and vanishes...")
            self.player_char.modify_inventory(items.Excaliper(), subtract=True, rare=True)
            spring_tile.nimue = True

        # Check for Excalibur upgrade
        if spring_tile.nimue:
            if "Excalibur" in self.player_char.inventory:
                self.add_message("The Lady of the Lake appears and upgrades your Excalibur!")
                self.player_char.modify_inventory(items.Excalibur2())
                self.player_char.modify_inventory(items.Excalibur(), subtract=True)
            elif "Excalibur" == self.player_char.equipment.get('Weapon', items.Stick()).name:
                self.add_message("The Lady of the Lake appears and upgrades your Excalibur!")
                self.player_char.equipment['Weapon'] = items.Excalibur2()

    def _interact_unobtainium_room(self, unobtainium_tile):
        """Handle Unobtainium room interaction."""
        if hasattr(unobtainium_tile, 'visited') and unobtainium_tile.visited:
            self.add_message("The ground here is already cleared.")
            return

        self.add_message("You spot Unobtainium on the ground and pick it up!")
        self.player_char.modify_inventory(items.Unobtainium(), rare=True, quest=True)
        unobtainium_tile.visited = True

    def _interact_dead_body(self, body_tile):
        """Handle dead body interaction."""
        # Check for quest item pickup
        if "A Bad Dream" in self.player_char.quest_dict.get("Main", {}):
            if not hasattr(body_tile, 'read') or not body_tile.read:
                self.game.special_event("Dead Body")
                self.add_message("You found a Lucky Locket on the body!")
                self.player_char.modify_inventory(items.LuckyLocket(), rare=True, quest=True)
                self.player_char.quest_dict["Main"]["A Bad Dream"]["Completed"] = True
                body_tile.read = True
                self.add_message("Quest completed: A Bad Dream")
                return
        
        # Trigger Waitress encounter if "A Bad Dream" has been turned in
        if "A Bad Dream" in self.player_char.quest_dict.get("Main", {}):
            if self.player_char.quest_dict["Main"]["A Bad Dream"].get("Turned In"):
                if not self.player_char.quest_dict["Main"]["A Bad Dream"].get("Waitress Defeated", False):
                    self.game.special_event("Waitress")
                    self.add_message("The Waitress appears, overcome with grief and rage!")
                    
                    enemy = enemies.NightHag2()
                    
                    # Start combat
                    self._refresh_cached_frame()
                    combat_won = self.combat_manager.start_combat(
                        self.player_char,
                        enemy,
                        body_tile
                    )
                    
                    if combat_won:
                        # Mark the encounter as complete
                        self.player_char.quest_dict["Main"]["A Bad Dream"]["Waitress Defeated"] = True
                    return

        # Check for Something to Cry About quest
        if "Something to Cry About" in self.player_char.quest_dict.get("Side", {}):
            if not self.player_char.quest_dict["Side"]["Something to Cry About"]["Completed"]:
                self.add_message("A Night Hag appears to protect the body!")

                enemy = enemies.NightHag2()

                # Start combat
                self._refresh_cached_frame()
                combat_won = self.combat_manager.start_combat(
                    self.player_char,
                    enemy,
                    body_tile
                )

    def _interact_final_room(self, final_room_tile):
        """Handle final room interaction - ask if player wants to fight final boss."""
        choice = self.presenter.render_menu(
            "You stand before the final chamber.\n\n"
            "The Devil awaits within.\n\n"
            "Do you wish to enter and face your destiny?",
            ["Yes, I'm ready", "No, not yet"]
        )

        if choice == 0:  # Yes
            self.add_message("You step forward into the final chamber...")
            # Move player north into the final boss room (2 tiles north)
            self.player_char.location_y -= 2
            self._mark_view_dirty()
            
            # Reveal the surrounding room tiles
            final_room_tile.adjacent_visited(self.player_char)
            
            # Show the Devil's dialogue
            special_event_dict = get_special_events()
            if "Final Boss" in special_event_dict:
                dialog_lines = special_event_dict["Final Boss"]["Text"]
                dialog_text = " ".join(line.strip() for line in dialog_lines if line is not None).strip()
                self.presenter.show_message(dialog_text, "The Devil")
            
            # Clear event queue to remove any lingering keypresses from dialogs
            pygame.event.clear()
            
            # Spawn and initiate combat with Devil
            devil = enemies.Devil()
            self.player_char.state = 'fight'
            
            # Update combat manager with current world state
            self.combat_manager.player_world_dict = self.player_char.world_dict
            
            # Start combat
            self._refresh_cached_frame()
            combat_won = self.combat_manager.start_combat(
                self.player_char,
                devil,
                final_room_tile
            )
            
            if combat_won:
                self.add_message("You have defeated the Devil! The dungeon fades away...")
                self.player_char.quit = True
                self.running = False
            elif not self.player_char.is_alive():
                self.add_message("You were defeated... The world fades to black.")
                try:
                    self.player_char.to_town()
                except Exception:
                    self.player_char.location_x, self.player_char.location_y, self.player_char.location_z = (5, 10, 0)
                self.player_char.state = 'normal'
                self.running = False
            else:
                self.add_message("You escaped from combat.")
        else:
            # Move player back south (1 tile)
            self.add_message("You step back to prepare yourself...")
            self.player_char.location_y += 1
            self._mark_view_dirty()

    def _get_tile_intro(self):
        """Get intro text for current tile and tile ahead."""
        messages = []

        # Check current tile (for stairs, shops, enemies you're standing on)
        current_tile = self.get_current_tile()
        if current_tile:
            intro_text = current_tile.intro_text(self.game).strip('\n')
            tile_type = type(current_tile).__name__

            if 'StairsUp' in tile_type:
                messages.append("You see stairs leading upward.")
            elif 'LadderUp' in tile_type:
                messages.append("A sturdy ladder leads upward.")
            elif 'StairsDown' in tile_type:
                messages.append("You see stairs descending into darkness.")
            elif 'LadderDown' in tile_type:
                messages.append("A sturdy ladder descends into darkness.")
            elif 'SecretShop' in tile_type:
                messages.append("You've found a secret shop! (Press O to enter)")
            elif 'UltimateArmorShop' in tile_type:
                messages.append("You've found a mysterious forge! (Press O to enter)")
            elif 'WarpPoint' in tile_type:
                messages.append("A warp point shimmers before you! (Press O to use)")
            elif 'UndergroundSpring' in tile_type:
                messages.append("An underground spring bubbles nearby. (Press O to interact)")
            elif 'UnobtainiumRoom' in tile_type:
                if not (hasattr(current_tile, 'looted') and not current_tile.looted):
                    messages.append("You happen upon a strange metal! (Press O to take)")
            elif 'DeadBody' in tile_type:
                messages.append("The body of a fallen soldier lies here.")
            elif 'FinalBlocker' in tile_type:
                if not self.player_char.has_relics():
                    messages.append("An invisible force blocks your path northward.")
                else:
                    messages.append("The way to the final chamber has opened!")
            elif 'FinalRoom' in tile_type:
                messages.append("The final chamber awaits. (Press O to proceed)")
            elif 'Boss' in tile_type:
                if hasattr(current_tile, 'enemy') and current_tile.enemy:
                    messages.append("You sense a powerful presence nearby...")
                else:
                    if intro_text:
                        messages.append(intro_text)
            elif hasattr(current_tile, 'enemy') and current_tile.enemy:
                messages.append(f"A {current_tile.enemy.name} blocks your path!")

        # Check tile ahead (for interactive objects like chests, doors, relics)
        direction = self.player_char.facing
        dx, dy = DIRECTIONS[direction]['move']
        ahead_x = self.player_char.location_x + dx
        ahead_y = self.player_char.location_y + dy
        ahead_z = self.player_char.location_z

        ahead_tile = self.player_char.world_dict.get((ahead_x, ahead_y, ahead_z))
        if ahead_tile:
            tile_type = type(ahead_tile).__name__

            if 'Chest' in tile_type:
                if hasattr(ahead_tile, 'open') and ahead_tile.open:
                    messages.append("There's an open chest ahead.")
                elif hasattr(ahead_tile, 'locked') and ahead_tile.locked:
                    messages.append("There's a locked chest ahead! (Press O to unlock)")
                else:
                    messages.append("There's a chest ahead! (Press O to open)")
            elif tile_type == 'OreVaultDoor':
                # Hidden door: appears as wall unless detected or open
                # Show identification message once when the player has means to detect it
                is_open = getattr(ahead_tile, 'open', False)
                is_detected = getattr(ahead_tile, 'detected', False)
                has_cryptic_key = "Cryptic Key" in self.player_char.inventory
                has_keen_eye = 'Keen Eye' in self.player_char.spellbook.get('Skills', [])

                if is_open:
                    messages.append("The secret vault door stands open ahead.")
                elif not is_detected and (has_cryptic_key or has_keen_eye):
                    # Mark as detected and inform the player
                    ahead_tile.detected = True
                    if has_cryptic_key:
                        messages.append("The Cryptic Key begins to glow; faint seams reveal a hidden door ahead!")
                    else:
                        messages.append(f"{self.player_char.name}'s keen eye spots a hidden door ahead!")
                    # View changed (door will render as detected)
                    self._mark_view_dirty()
            elif 'Door' in tile_type:
                if hasattr(ahead_tile, 'open') and ahead_tile.open:
                    messages.append("An open doorway ahead.")
                elif hasattr(ahead_tile, 'locked') and ahead_tile.locked:
                    messages.append("A locked door blocks your path. (Press O to unlock)")
                else:
                    messages.append("An open doorway ahead.")
            elif 'Relic' in tile_type:
                if hasattr(ahead_tile, 'read') and ahead_tile.read:
                    messages.append("An empty altar stands ahead.")
                else:
                    messages.append("A glowing relic rests on a altar ahead! (Press O to collect)")
            elif 'Boulder' in tile_type:
                if hasattr(ahead_tile, 'read') and ahead_tile.read:
                    messages.append("A broken boulder ahead.")
                else:
                    messages.append("An oddly placed boulder ahead. (Press O to examine)")
            elif 'UnobtainiumRoom' in tile_type:
                is_looted = bool(getattr(ahead_tile, 'visited', False))
                if is_looted:
                    messages.append("The ground ahead is already cleared.")
                else:
                    messages.append("You see Unobtainium on the ground ahead! (Press O to take)")

        return messages if messages else None

    def _check_tile_effects(self):
        """Check for tile effects like encounters, traps, etc."""
        current_tile = self.get_current_tile()
        if not current_tile:
            return

        # Check for stairs - automatically use them when stepping on them
        tile_type = type(current_tile).__name__
        if 'StairsUp' in tile_type:
            self.use_stairs_up()
            return  # Don't check for other effects when using stairs
        elif 'StairsDown' in tile_type:
            self.use_stairs_down()
            return  # Don't check for other effects when using stairs
        elif 'FinalRoom' in tile_type:
            # Automatically trigger final room conversation when stepping on the tile
            self._interact_final_room(current_tile)
            return  # Don't check for other effects after final room interaction

        # Display special event text BEFORE tile effects and combat
        if hasattr(current_tile, 'special_text'):
            try:
                special = current_tile.special_text(self.game)
                if special:
                    self.add_message(special)
            except:
                pass

        # Apply tile-defined effects (original game behavior)
        # This enables effects like FirePath damage on entry.
        hp_before = getattr(self.player_char.health, 'current', None)
        try:
            if 'UndergroundSpring' not in tile_type:
                from .confirmation_popup import ConfirmationPopup
                try:
                    current_tile.modify_player(self.game, popup_class=ConfirmationPopup)
                except TypeError:
                    current_tile.modify_player(self.game)
        except AttributeError:
            pass
        except Exception as e:
            pass
        else:
            hp_after = getattr(self.player_char.health, 'current', None)
            if ('FirePath' in tile_type and hp_before is not None and hp_after is not None
                    and hp_after < hp_before):
                damage = hp_before - hp_after
                self.add_message(f"The heat sears you for {damage} damage!")
                # Brief red flash when the floor burns the player
                if hasattr(self.renderer, 'trigger_damage_flash'):
                    self.renderer.trigger_damage_flash()
                self.ui_dirty = True
                self.view_dirty = True
        
        # Check if tile effect teleported player to town (e.g., "Bring Him Home" quest)
        if self.player_char.in_town():
            self.add_message("You've been teleported back to town!")
            try:
                from .confirmation_popup import ConfirmationPopup
                popup = ConfirmationPopup(
                    self.presenter,
                    "You've been teleported back to town!",
                    show_buttons=False
                )
                popup.show(
                    flush_events=True,
                    require_key_release=True,
                    min_display_ms=300
                )
            except Exception:
                pass
            self.running = False  # Exit dungeon mode
            return

        # Check for enemy encounter after enter_combat has had a chance to spawn one
        if hasattr(current_tile, 'enemy') and current_tile.enemy:
            enemy = current_tile.enemy
            # If enemy is still a class (not instantiated), instantiate it
            if callable(enemy) and not hasattr(enemy, 'name'):
                enemy = enemy()
                current_tile.enemy = enemy  # Update tile's enemy to the instance

            if hasattr(enemy, "is_alive") and not enemy.is_alive():
                current_tile.enemy = None
                return
            if hasattr(enemy, "health") and getattr(enemy.health, "current", 1) <= 0:
                current_tile.enemy = None
                return
            
            self.add_message(f"You've encountered a {enemy.name}!")

            # Set player state to fight BEFORE calling start_combat
            # This ensures available_actions returns combat actions
            self.player_char.state = 'fight'

            # Update combat manager with current world state for rendering
            self.combat_manager.player_world_dict = self.player_char.world_dict

            # Initiate combat
            self._refresh_cached_frame()
            combat_won = self.combat_manager.start_combat(
                self.player_char,
                enemy,
                current_tile
            )

            if combat_won:
                # Enemy defeated - clear from tile
                current_tile.enemy = None
                self.add_message("You emerge victorious!")
            elif not self.player_char.is_alive():
                # Player died - return to town or exit funhouse
                if self.player_char.location_z == 7:
                    # In funhouse - exit instead of going to town
                    self.add_message("You were defeated... The funhouse spits you back out.")
                    self.player_char.exit_funhouse()
                else:
                    self.add_message("You were defeated... You awaken safely back in town.")
                    self.player_char.to_town()
                self.player_char.state = 'normal'
                # End dungeon exploration loop (return control to town menu)
                self.running = False
            else:
                # Player fled - enemy moves away/disappears
                current_tile.enemy = None
                self.add_message("You escaped from combat.")

        # Check for warning tiles (difficulty increase)
        if 'WarningTile' in tile_type and not hasattr(current_tile, '_warning_shown'):
            self.add_message("*** WARNING: Enemies beyond this point increase in difficulty. Plan accordingly. ***")
            current_tile._warning_shown = True

    def explore_dungeon(self):
        """
        Main dungeon exploration loop.
        Returns when player exits dungeon (returns to town, quits, etc.)
        """
        # Always show a loading screen on entry. If we're in town coordinates, use a descending message.
        if hasattr(self.player_char, "in_town") and callable(self.player_char.in_town):
            msg = "Descending further into the dungeon..." if self.player_char.in_town() else "Entering the dungeon..."
        else:
            msg = "Entering the dungeon..."
        self._show_dungeon_loading_screen(msg, duration=1.25)

        # Initial message
        current_tile = self.get_current_tile()
        if current_tile:
            current_tile.visited = True
            current_tile.adjacent_visited(self.player_char)

        self.add_message("You enter the dungeon...")
        self.add_message(f"Facing: {self.player_char.facing}")

        # Show controls
        if getattr(self.game, "debug_mode", False):
            self.add_message("Controls: Arrows/WASD=Move/Turn, O=Interact, U=Stairs Up, J=Stairs Down, ESC=Menu, L=Debug Level Up")
        else:
            self.add_message("Controls: Arrows/WASD=Move/Turn, O=Interact, U=Stairs Up, J=Stairs Down, ESC=Menu")

        clock = pygame.time.Clock()
        self.running = True

        # Initialize animation timer (torch flicker, subtle post-effects, etc.)
        self._next_anim_tick = pygame.time.get_ticks() + self._anim_interval_ms
        
        # Initialize cry timer for floor 2 quest
        self._last_cry_time = 0
        self._cry_interval = 8000  # Check every 8 seconds

        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.player_char.quit = True

                elif event.type == pygame.KEYDOWN:
                    self._handle_keypress(event.key)

            # Periodic animation refresh (even if the player doesn't move)
            now = pygame.time.get_ticks()
            if now >= self._next_anim_tick:
                self._mark_view_dirty()
                self._next_anim_tick = now + self._anim_interval_ms
            
            # Check for random cries on floor 2 during "Something to Cry About" quest
            if now >= self._last_cry_time + self._cry_interval:
                self._check_random_cry()
                self._last_cry_time = now

            # Keep UI refreshing while a damage flash is active so the fade animates
            if getattr(self.renderer, '_damage_flash_active', False):
                self.ui_dirty = True

            # Only redraw when something changed.
            if self.view_dirty or self.ui_dirty or self._cached_view is None:
                self._render()
                pygame.display.flip()

            # Keep event loop responsive; redraws are conditional.
            clock.tick(60)

        return not self.player_char.quit  # Return True if player didn't quit game

    def _handle_keypress(self, key):
        """Handle keyboard input for dungeon navigation."""
        # Movement and turning
        if key in (pygame.K_w, pygame.K_UP):
            self.move_forward()

        elif key in (pygame.K_a, pygame.K_LEFT):
            self.turn_left()

        elif key in (pygame.K_d, pygame.K_RIGHT):
            self.turn_right()

        elif key in (pygame.K_s, pygame.K_DOWN):
            self.turn_around()

        # Stairs
        elif key == pygame.K_u:
            self.use_stairs_up()

        elif key == pygame.K_j:
            self.use_stairs_down()

        # Interact
        elif key == pygame.K_o:
            self.interact()

        # Character menu
        elif key == pygame.K_c:
            # Open character screen (same as town)
            while True:
                choice = self.character_screen.navigate(self.player_char)
                if choice == "Exit Menu" or choice is None:
                    break
                elif choice == "Quit Game":
                    self.game.running = False
                    self.running = False
                    break
                else:
                    # Placeholder until inventory/equipment/etc screens exist
                    self.presenter.show_message("This menu is not yet implemented in the dungeon.")

        # Debug level-up shortcut
        elif key == pygame.K_l and getattr(self.game, "debug_mode", False):
            self.game.debug_level_up()

        # Escape menu
        elif key == pygame.K_ESCAPE:
            self._show_menu()

    def _show_menu(self):
        """Show in-dungeon menu."""
        menu_options = [
            "Resume Exploration",
            "Character Menu",
        ]
        if getattr(self.game, "debug_mode", False):
            menu_options.append("Save Game")
        menu_options.append("Quit Game (No Save)")

        choice = self._popup_menu("Dungeon Menu", menu_options)

        # Handle None (menu closed without selection)
        if choice is None or choice == 0:  # Resume
            self.add_message("Resuming exploration...")
            return

        elif choice == 1:  # Character Menu
            while True:
                char_choice = self.character_screen.navigate(self.player_char)
                if char_choice == "Exit Menu" or char_choice is None:
                    break
                elif char_choice == "Quit Game":
                    self.game.running = False
                    self.running = False
                    return
                else:
                    self.presenter.show_message("This menu is not yet implemented in the dungeon.")

        elif menu_options[choice] == "Save Game":
            from .confirmation_popup import ConfirmationPopup
            popup = ConfirmationPopup(self.presenter, "Save your progress?")
            if popup.show():
                self.game.save_game()
                self.add_message("Game saved!")

        elif menu_options[choice] == "Quit Game (No Save)":
            from .confirmation_popup import ConfirmationPopup
            popup = ConfirmationPopup(self.presenter, "Quit without saving? Progress will be lost.")
            if popup.show():
                self.add_message("Exiting game...")
                self.running = False
                self.player_char.quit = True

    def _popup_menu(self, title: str, options: list[str]):
        """Lightweight modal popup menu drawn over the current view.

        Returns the selected index or None if canceled.
        """
        selected = 0
        clock = self.presenter.clock
        screen = self.presenter.screen

        # Snapshot current frame as background
        background = screen.copy()

        # Layout
        panel_width = self.presenter.width // 2
        panel_height = self.presenter.height // 2
        panel_x = (self.presenter.width - panel_width) // 2
        panel_y = (self.presenter.height - panel_height) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        def draw():
            # Draw background dimmed
            screen.blit(background, (0, 0))
            overlay = pygame.Surface((self.presenter.width, self.presenter.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            # Panel
            pygame.draw.rect(screen, (20, 20, 30), panel_rect)
            pygame.draw.rect(screen, (200, 200, 200), panel_rect, 3)

            # Title
            title_surf = self.presenter.title_font.render(title, True, (218, 165, 32))
            title_rect = title_surf.get_rect(center=(panel_rect.centerx, panel_rect.top + 40))
            screen.blit(title_surf, title_rect)

            # Options
            y = title_rect.bottom + 20
            for idx, opt in enumerate(options):
                color = (218, 165, 32) if idx == selected else (255, 255, 255)
                surf = self.presenter.large_font.render(opt, True, color)
                rect = surf.get_rect(center=(panel_rect.centerx, y))
                screen.blit(surf, rect)
                y += 40

            # Instructions
            instr = "UP/DOWN: Navigate  ENTER: Select  ESC: Cancel"
            instr_surf = self.presenter.small_font.render(instr, True, (180, 180, 180))
            instr_rect = instr_surf.get_rect(center=(panel_rect.centerx, panel_rect.bottom - 30))
            screen.blit(instr_surf, instr_rect)

            pygame.display.flip()

        while True:
            draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        selected = (selected - 1) % len(options)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        selected = (selected + 1) % len(options)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        return selected
                    elif event.key == pygame.K_ESCAPE:
                        return None
            clock.tick(30)

    def _render(self):
        """Render the complete dungeon view."""
        # Ensure we have a cached view surface for the current resolution.
        screen = self.presenter.screen
        if self._cached_view is None or self._cached_view.get_size() != screen.get_size():
            self._cached_view = pygame.Surface(screen.get_size()).convert()
            self._mark_view_dirty()

        # --- 3D view (expensive) ---
        if self.view_dirty:
            screen.fill((0, 0, 0))
            try:
                self.renderer.render_dungeon_view(self.player_char, self.player_char.world_dict)

                # Cache the freshly-rendered 3D view *before* overlay UI is drawn.
                self._cached_view.blit(screen, (0, 0))
                self._render_error_logged = False
            except Exception as e:
                # Do not spam tracebacks every frame.
                if not self._render_error_logged:
                    print(f"Render error: {e}")
                    traceback.print_exc()
                    self._render_error_logged = True

                # Fall back to the last known-good view if available.
                screen.blit(self._cached_view, (0, 0))
        else:
            # Re-use the cached 3D view.
            screen.blit(self._cached_view, (0, 0))

        # --- UI overlays (cheap) ---
        try:
            self.renderer.render_message_area(self.messages)
        except Exception as e:
            print(f"Message render error: {e}")

        try:
            self.hud.render_hud(self.player_char)
        except Exception as e:
            if not self._render_error_logged:
                print(f"HUD render error: {e}")
                traceback.print_exc()
                self._render_error_logged = True

        try:
            self.renderer.render_damage_flash()
        except Exception as e:
            if not self._render_error_logged:
                print(f"Damage flash render error: {e}")
                traceback.print_exc()
                self._render_error_logged = True

        self._cached_frame = screen.copy()

        # Clear dirty flags after a frame attempt.
        self.view_dirty = False
        self.ui_dirty = False
