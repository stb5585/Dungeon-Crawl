"""
Save System - Data-based serialization for game objects.

This module provides a data-driven save/load system that saves game state as
dictionaries rather than pickled objects. This allows code changes to be applied
to loaded games automatically.

Architecture:
- Serializers: Convert objects → dictionaries
- Deserializers: Convert dictionaries → fresh objects
- SaveData: Root container for all game state
"""

import os
import json
from dataclasses import dataclass, asdict
from typing import Any

import abilities
import items
from character import Resource, Stats, Combat, Level


@dataclass
class ResourceData:
    """Serializable resource (health/mana)."""
    max: int
    current: int


@dataclass
class StatsData:
    """Serializable character stats."""
    strength: int = 0
    intel: int = 0
    wisdom: int = 0
    con: int = 0
    charisma: int = 0
    dex: int = 0


@dataclass
class CombatData:
    """Serializable combat stats."""
    attack: int = 0
    defense: int = 0
    magic: int = 0
    magic_def: int = 0


@dataclass
class LevelData:
    """Serializable level info."""
    level: int = 1
    pro_level: int = 1
    exp: int = 0
    exp_to_gain: int = 25


@dataclass
class StatusEffectData:
    """Serializable status effect."""
    active: bool = False
    duration: int = 0
    extra: int = 0


class ItemSerializer:
    """Serializes items to IDs and names."""
    
    @staticmethod
    def serialize(item) -> dict[str, Any]:
        """Convert item object to data dict."""
        if item is None or not hasattr(item, 'name'):
            return {'name': 'None', 'typ': 'None', 'subtyp': 'None'}
        
        return {
            'name': item.name,
            'typ': getattr(item, 'typ', 'Unknown'),
            'subtyp': getattr(item, 'subtyp', 'None'),
            'class': item.__class__.__name__,
        }
    
    @staticmethod
    def deserialize(data: dict[str, Any]):
        """Reconstruct item from data dict."""
        # Normalize typ for Accessory items (Ring/Pendant)
        typ = data.get('typ', 'Weapon')
        if typ == 'Accessory':
            # Determine if Ring or Pendant from class name
            class_name = data.get('class', '')
            if 'Ring' in class_name:
                typ = 'Ring'
            elif 'Pendant' in class_name:
                typ = 'Pendant'
            else:
                typ = 'Ring'  # Default to Ring
        
        if data.get('name') == 'None' or data.get('subtyp') == 'None':
            return items.remove_equipment(typ)
        
        # Try to find and instantiate the item class
        item_class_name = data.get('class')
        if item_class_name and hasattr(items, item_class_name):
            try:
                item_class = getattr(items, item_class_name)
                # Don't try to instantiate abstract base classes
                if item_class_name not in ['Item', 'Weapon', 'OffHand', 'Armor', 'Accessory']:
                    return item_class()
            except Exception:
                pass
        
        # Fallback: create empty equipment
        return items.remove_equipment(typ)


class AbilitySerializer:
    """Serializes abilities by class name to avoid ambiguity with variants."""
    
    @staticmethod
    def serialize(ability) -> str:
        """Convert ability to class name (e.g. 'Heal2' instead of 'Heal').
        
        Uses class name instead of display name to distinguish variants
        like Heal, Heal2, Heal3 which all have name='Heal'.
        """
        if ability is None:
            return ""
        # Use class name for unambiguous serialization
        return ability.__class__.__name__
    
    @staticmethod
    def deserialize(name: str):
        """Reconstruct ability from class name or display name.
        
        Supports:
        - Class names: 'Heal', 'Heal2', 'Heal3' (unambiguous)
        - Display names: 'Heal' (ambiguous, returns first match)
        
        Prefers class name lookup for reliability.
        """
        if not name:
            return None
        
        # First try direct class name lookup (most reliable)
        if hasattr(abilities, name):
            try:
                attr = getattr(abilities, name)
                if hasattr(attr, '__call__'):
                    return attr()
            except Exception:
                pass
        
        # Fallback to display name lookup (may be ambiguous)
        for attr_name in dir(abilities):
            attr = getattr(abilities, attr_name)
            if hasattr(attr, '__call__'):
                try:
                    instance = attr()
                    if hasattr(instance, 'name') and instance.name == name:
                        return instance
                except Exception:
                    pass
        
        return None


class TileStateSerializer:
    """Serializes/deserializes tile state (mutable attributes)."""
    
    @staticmethod
    def serialize_tile_state(world_dict: dict) -> dict[str, dict]:
        """Convert tile states to data dictionary, keyed by position tuple."""
        tile_states = {}
        
        for pos, tile in world_dict.items():
            # Store mutable state attributes
            state = {
                'visited': getattr(tile, 'visited', False),
                'near': getattr(tile, 'near', False),
                'open': getattr(tile, 'open', False),
                'read': getattr(tile, 'read', False),
                'blocked': getattr(tile, 'blocked', None),
                'warped': getattr(tile, 'warped', False),
            }
            
            # For tiles with enemies and defeated flag
            if hasattr(tile, 'defeated'):
                state['defeated'] = tile.defeated
                if hasattr(tile, 'enemy') and tile.enemy:
                    state['enemy_state'] = EnemyStateSerializer.serialize(tile.enemy)
            
            # For tiles with other special state (drink, nimue, etc.)
            if hasattr(tile, 'drink'):
                state['drink'] = tile.drink
            if hasattr(tile, 'nimue'):
                state['nimue'] = tile.nimue
            
            tile_states[str(pos)] = state
        
        return tile_states
    
    @staticmethod
    def restore_tile_state(world_dict: dict, tile_states: dict) -> None:
        """Restore tile state from serialized data."""
        for pos_str, state in tile_states.items():
            # Parse position string back to tuple
            try:
                pos = eval(pos_str)  # e.g., "(5,10,1)"
            except (ValueError, SyntaxError):
                continue
            
            if pos not in world_dict:
                continue
            
            tile = world_dict[pos]
            
            # Restore basic attributes
            if 'visited' in state:
                tile.visited = state['visited']
            if 'near' in state:
                tile.near = state['near']
            if 'open' in state:
                tile.open = state['open']
            if 'read' in state:
                tile.read = state['read']
            if 'blocked' in state:
                tile.blocked = state['blocked']
            if 'warped' in state:
                tile.warped = state['warped']
            
            # Restore defeated flag
            if 'defeated' in state and hasattr(tile, 'defeated'):
                tile.defeated = state['defeated']
            
            # Restore enemy state if present
            if 'enemy_state' in state and hasattr(tile, 'enemy'):
                tile.enemy = EnemyStateSerializer.deserialize(state['enemy_state'])
            
            # Restore special attributes
            if 'drink' in state and hasattr(tile, 'drink'):
                tile.drink = state['drink']
            if 'nimue' in state and hasattr(tile, 'nimue'):
                tile.nimue = state['nimue']


class EnemyStateSerializer:
    """Serializes/deserializes enemy state (for bosses and key enemies)."""
    
    @staticmethod
    def serialize(enemy) -> dict[str, Any]:
        """Convert enemy to data dictionary."""
        if not enemy:
            return None
        
        # Handle case where enemy is a class instead of an instance
        if isinstance(enemy, type):
            # It's a class, not an instance - just return the class name
            return {
                'name': enemy.__name__,
                'class_type': enemy.__name__,
                'is_class': True,
            }
        
        # It's an instance
        return {
            'name': getattr(enemy, 'name', 'Unknown'),
            'class_type': enemy.__class__.__name__,
            'is_class': False,
            'health': {
                'max': getattr(enemy.health, 'max', 100) if hasattr(enemy, 'health') else 100,
                'current': getattr(enemy.health, 'current', 100) if hasattr(enemy, 'health') else 100,
            },
            'mana': {
                'max': getattr(enemy.mana, 'max', 0) if hasattr(enemy, 'mana') else 0,
                'current': getattr(enemy.mana, 'current', 0) if hasattr(enemy, 'mana') else 0,
            },
            'alive': enemy.is_alive() if hasattr(enemy, 'is_alive') else True,
        }
    
    @staticmethod
    def deserialize(enemy_data: dict):
        """Reconstruct enemy from data dictionary."""
        if not enemy_data:
            return None
        
        try:
            import enemies
            enemy_class_name = enemy_data.get('class_type')
            
            # Get the enemy class from enemies module
            enemy_class = getattr(enemies, enemy_class_name, None)
            if not enemy_class:
                return None
            
            # If it was stored as a class, return the class
            if enemy_data.get('is_class'):
                return enemy_class
            
            # Create instance
            enemy = enemy_class()
            
            # Restore health/mana if present
            if 'health' in enemy_data and hasattr(enemy, 'health'):
                enemy.health.max = enemy_data['health']['max']
                enemy.health.current = enemy_data['health']['current']
            
            if 'mana' in enemy_data and hasattr(enemy, 'mana'):
                enemy.mana.max = enemy_data['mana']['max']
                enemy.mana.current = enemy_data['mana']['current']
            
            return enemy
        except Exception as e:
            print(f"Error deserializing enemy: {e}")
            return None


class QuestDataSerializer:
    """Serializes/deserializes quest data with proper item handling."""
    
    @staticmethod
    def serialize_quest_dict(quest_dict: dict) -> dict:
        """Convert quest_dict with item objects to serializable format."""
        serialized = {}
        
        for quest_type, quests_by_category in quest_dict.items():
            serialized[quest_type] = {}
            
            if quest_type == 'Bounty':
                # Bounty format: {enemy_name: [bounty_data, count, completed]}
                for quest_name, quest_info in quests_by_category.items():
                    if isinstance(quest_info, list) and len(quest_info) >= 3:
                        bounty_data, count, completed = quest_info[0], quest_info[1], quest_info[2]
                        # Serialize bounty data if it contains items
                        serialized_bounty = dict(bounty_data)
                        if 'reward' in serialized_bounty and serialized_bounty['reward']:
                            serialized_bounty['reward'] = ItemSerializer.serialize(serialized_bounty['reward']())
                        serialized[quest_type][quest_name] = [serialized_bounty, count, completed]
                    else:
                        serialized[quest_type][quest_name] = quest_info
            else:
                # Main/Side quests: {quest_name: quest_data}
                for quest_name, quest_data in quests_by_category.items():
                    if isinstance(quest_data, dict):
                        serialized_quest = dict(quest_data)
                        
                        # Serialize item class in 'What' field for Collect quests FIRST
                        # (before other processing to ensure it's properly handled)
                        if 'What' in serialized_quest and serialized_quest.get('Type') == 'Collect':
                            what = serialized_quest['What']
                            if isinstance(what, type):
                                try:
                                    instance = what()
                                    serialized_quest['What'] = ItemSerializer.serialize(instance)
                                except:
                                    serialized_quest['What'] = what.__name__
                            elif isinstance(what, str):
                                # Already a string, leave it
                                pass
                            elif hasattr(what, 'name'):
                                # It's an instance, serialize it
                                serialized_quest['What'] = ItemSerializer.serialize(what)
                        
                        # Serialize item classes in 'Reward' field
                        if 'Reward' in serialized_quest:
                            reward = serialized_quest['Reward']
                            if isinstance(reward, list):
                                # Convert item classes to serialized form
                                serialized_rewards = []
                                for r in reward:
                                    if isinstance(r, str):
                                        serialized_rewards.append(r)  # Keep string keywords like 'Gold'
                                    elif isinstance(r, type):
                                        # It's a class, serialize by instantiating
                                        try:
                                            instance = r()
                                            serialized_rewards.append(ItemSerializer.serialize(instance))
                                        except:
                                            serialized_rewards.append(r.__name__)
                                    else:
                                        # It's an instance or something else
                                        serialized_rewards.append(ItemSerializer.serialize(r))
                                serialized_quest['Reward'] = serialized_rewards
                            elif reward == 'Gold':
                                pass  # Leave as-is
                            elif isinstance(reward, type):
                                serialized_quest['Reward'] = ItemSerializer.serialize(reward())
                        
                        serialized[quest_type][quest_name] = serialized_quest
                    else:
                        serialized[quest_type][quest_name] = quest_data
        
        return serialized
    
    @staticmethod
    def deserialize_quest_dict(serialized: dict) -> dict:
        """Reconstruct quest_dict with proper item objects from serialized format."""
        quest_dict = {}
        
        for quest_type, quests_by_category in serialized.items():
            quest_dict[quest_type] = {}
            
            if quest_type == 'Bounty':
                # Bounty format: {enemy_name: [bounty_data, count, completed]}
                for quest_name, quest_info in quests_by_category.items():
                    if isinstance(quest_info, list) and len(quest_info) >= 3:
                        bounty_data, count, completed = quest_info[0], quest_info[1], quest_info[2]
                        # Deserialize bounty data if it contains items
                        deserialized_bounty = dict(bounty_data)
                        if 'reward' in deserialized_bounty and deserialized_bounty['reward']:
                            if isinstance(deserialized_bounty['reward'], dict):
                                # It's serialized, deserialize it
                                deserialized_bounty['reward'] = ItemSerializer.deserialize(deserialized_bounty['reward'])
                            else:
                                # It's already an item or callable
                                deserialized_bounty['reward'] = deserialized_bounty['reward']
                        quest_dict[quest_type][quest_name] = [deserialized_bounty, count, completed]
                    else:
                        quest_dict[quest_type][quest_name] = quest_info
            else:
                # Main/Side quests: {quest_name: quest_data}
                for quest_name, quest_data in quests_by_category.items():
                    if isinstance(quest_data, dict):
                        deserialized_quest = dict(quest_data)
                        
                        # Deserialize item classes in 'Reward' field
                        if 'Reward' in deserialized_quest:
                            reward = deserialized_quest['Reward']
                            if isinstance(reward, list):
                                deserialized_rewards = []
                                for r in reward:
                                    if isinstance(r, str):
                                        deserialized_rewards.append(r)  # Keep string keywords
                                    elif isinstance(r, dict):
                                        # It's serialized, deserialize it
                                        deserialized_rewards.append(ItemSerializer.deserialize(r))
                                    else:
                                        deserialized_rewards.append(r)
                                deserialized_quest['Reward'] = deserialized_rewards
                        
                        # Deserialize item class in 'What' field for Collect quests
                        if 'What' in deserialized_quest and deserialized_quest.get('Type') == 'Collect':
                            what = deserialized_quest['What']
                            if isinstance(what, dict):
                                deserialized_quest['What'] = ItemSerializer.deserialize(what)
                            elif isinstance(what, str):
                                # Handle legacy string data - try to find the item class
                                # For now, leave as string (will be handled by GUI)
                                # TODO: Could add item name -> class mapping here
                                pass
                        
                        quest_dict[quest_type][quest_name] = deserialized_quest
                    else:
                        quest_dict[quest_type][quest_name] = quest_data
        
        return quest_dict


class PlayerDataSerializer:
    """Serializes/deserializes player character."""
    
    @staticmethod
    def serialize(player) -> dict[str, Any]:
        """Convert player object to data dictionary."""
        
        # Basic attributes
        data = {
            'version': 2,
            'name': player.name,
            'location': (player.location_x, player.location_y, player.location_z),
            'facing': player.facing,
            'health': asdict(ResourceData(player.health.max, player.health.current)),
            'mana': asdict(ResourceData(player.mana.max, player.mana.current)),
            'stats': asdict(StatsData(
                player.stats.strength, player.stats.intel, player.stats.wisdom,
                player.stats.con, player.stats.charisma, player.stats.dex
            )),
            'combat': asdict(CombatData(
                player.combat.attack, player.combat.defense,
                player.combat.magic, player.combat.magic_def
            )),
            'level': asdict(LevelData(
                player.level.level, player.level.pro_level,
                player.level.exp, player.level.exp_to_gain
            )),
            'gold': player.gold,
            'resistance': dict(player.resistance),
            
            # Equipment
            'equipment': {
                slot: ItemSerializer.serialize(item)
                for slot, item in player.equipment.items()
            },
            
            # Inventory
            'inventory': {
                item_name: [ItemSerializer.serialize(item) for item in item_list]
                for item_name, item_list in player.inventory.items()
            },
            'special_inventory': {
                item_name: [ItemSerializer.serialize(item) for item in item_list]
                for item_name, item_list in player.special_inventory.items()
            },
            'storage': {
                item_name: [ItemSerializer.serialize(item) for item in item_list]
                for item_name, item_list in player.storage.items()
            },
            
            # Spellbook
            'spellbook': {
                'Spells': {
                    name: AbilitySerializer.serialize(spell)
                    for name, spell in player.spellbook['Spells'].items()
                },
                'Skills': {
                    name: AbilitySerializer.serialize(skill)
                    for name, skill in player.spellbook['Skills'].items()
                },
            },
            
            # Character attributes
            'class_name': player.cls.name if player.cls else None,
            'race_name': player.race.name if player.race else None,
            'invisible': player.invisible,
            'flying': player.flying,
            'sight': player.sight,
            'power_up': player.power_up,
            'encumbered': player.encumbered,
            'state': player.state,
            'warp_point': player.warp_point,
            'intro_shown': getattr(player, 'intro_shown', False),
            
            # Derived data - serialize quest_dict properly
            'quest_dict': QuestDataSerializer.serialize_quest_dict(player.quest_dict),
            'kill_dict': player.kill_dict,
            
            # World state (tile visited flags, defeated enemies, open doors, etc.)
            'world_state': TileStateSerializer.serialize_tile_state(player.world_dict) if player.world_dict else {},
        }
        
        return data
    
    @staticmethod
    def deserialize(data: dict[str, Any]):
        """Reconstruct player from data dictionary."""
        from player import Player
        import races
        import classes
        
        # Create fresh character
        health = Resource(data['health']['max'], data['health']['current'])
        mana = Resource(data['mana']['max'], data['mana']['current'])
        
        stats_d = data['stats']
        stats = Stats(
            strength=stats_d['strength'], intel=stats_d['intel'],
            wisdom=stats_d['wisdom'], con=stats_d['con'],
            charisma=stats_d['charisma'], dex=stats_d['dex']
        )
        
        combat_d = data['combat']
        combat = Combat(
            attack=combat_d['attack'], defense=combat_d['defense'],
            magic=combat_d['magic'], magic_def=combat_d['magic_def']
        )
        
        level_d = data['level']
        level = Level(
            level=level_d['level'], pro_level=level_d['pro_level'],
            exp=level_d['exp'], exp_to_gain=level_d['exp_to_gain']
        )
        
        # Create player
        player = Player(
            data['location'][0], data['location'][1], data['location'][2],
            level, health, mana, stats, combat, data['gold'], data['resistance']
        )
        
        # Restore basic attributes
        player.name = data['name']
        player.invisible = data['invisible']
        player.flying = data['flying']
        player.sight = data['sight']
        player.power_up = data['power_up']
        player.state = data['state']
        player.warp_point = data['warp_point']
        player.facing = data['facing']
        
        # Restore class and race
        if data.get('class_name'):
            for cls_attr in dir(classes):
                cls_obj = getattr(classes, cls_attr)
                if hasattr(cls_obj, '__call__'):
                    try:
                        instance = cls_obj()
                        if hasattr(instance, 'name') and instance.name == data['class_name']:
                            player.cls = instance
                            break
                    except Exception:
                        pass
        
        if data.get('race_name'):
            for race_attr in dir(races):
                race_obj = getattr(races, race_attr)
                if hasattr(race_obj, '__call__'):
                    try:
                        instance = race_obj()
                        if hasattr(instance, 'name') and instance.name == data['race_name']:
                            player.race = instance
                            break
                    except Exception:
                        pass
        
        # Restore equipment
        for slot, item_data in data['equipment'].items():
            player.equipment[slot] = ItemSerializer.deserialize(item_data)
        
        # Restore inventory
        for item_name, item_list in data['inventory'].items():
            player.inventory[item_name] = [ItemSerializer.deserialize(item_data) for item_data in item_list]
        
        for item_name, item_list in data['special_inventory'].items():
            player.special_inventory[item_name] = [ItemSerializer.deserialize(item_data) for item_data in item_list]
        
        for item_name, item_list in data['storage'].items():
            player.storage[item_name] = [ItemSerializer.deserialize(item_data) for item_data in item_list]
        
        # Restore spellbook
        player.spellbook['Spells'] = {
            name: AbilitySerializer.deserialize(ability_name)
            for name, ability_name in data['spellbook']['Spells'].items()
        }
        player.spellbook['Skills'] = {
            name: AbilitySerializer.deserialize(ability_name)
            for name, ability_name in data['spellbook']['Skills'].items()
        }
        
        # Restore quest/kill dicts
        player.quest_dict = QuestDataSerializer.deserialize_quest_dict(data.get('quest_dict', {'Bounty': {}, 'Main': {}, 'Side': {}}))
        player.kill_dict = data.get('kill_dict', {})
        player.intro_shown = data.get('intro_shown', False)
        
        # Load world tiles and restore saved world state
        player.load_tiles()
        if 'world_state' in data:
            TileStateSerializer.restore_tile_state(player.world_dict, data['world_state'])
        
        return player


class SaveManager:
    """High-level save/load management."""
    
    SAVE_DIR = "save_files"
    TMP_DIR = "tmp_files"
    
    @staticmethod
    def ensure_dirs():
        """Ensure save directories exist."""
        for dir_path in [SaveManager.SAVE_DIR, SaveManager.TMP_DIR]:
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path, exist_ok=True)
    
    @staticmethod
    def save_player(player, filename: str, is_tmp: bool = False) -> bool:
        """Save player to file."""
        SaveManager.ensure_dirs()
        
        try:
            directory = SaveManager.TMP_DIR if is_tmp else SaveManager.SAVE_DIR
            filepath = os.path.join(directory, filename)
            
            # Serialize player
            data = PlayerDataSerializer.serialize(player)
            
            # Save as JSON
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"Error saving player: {e}")
            return False
    
    @staticmethod
    def load_player(filename: str, is_tmp: bool = False):
        """Load player from file."""
        try:
            directory = SaveManager.TMP_DIR if is_tmp else SaveManager.SAVE_DIR
            filepath = os.path.join(directory, filename)
            
            if not os.path.exists(filepath):
                return None
            
            # Load JSON
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Deserialize player
            player = PlayerDataSerializer.deserialize(data)
            return player
        except Exception as e:
            print(f"Error loading player: {e}")
            return None
    
    @staticmethod
    def list_saves() -> list[str]:
        """List all save files."""
        SaveManager.ensure_dirs()
        if not os.path.isdir(SaveManager.SAVE_DIR):
            return []
        return [f for f in os.listdir(SaveManager.SAVE_DIR) if f.endswith('.save')]
    
    @staticmethod
    def delete_save(filename: str) -> bool:
        """Delete a save file."""
        filepath = os.path.join(SaveManager.SAVE_DIR, filename)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception:
            pass
        return False
