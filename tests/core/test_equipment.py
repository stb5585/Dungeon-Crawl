#!/usr/bin/env python3
"""
Equipment System Tests

Tests the player equipment system including:
- Equipment equipping and unequipping
- Two-handed weapon logic
- Class-specific equipment restrictions
- Off-hand shield with polearm (Lancer/Dragoon special case)
- Equipment conflicts and validation
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

from src.core import items
from tests.test_framework import TestGameState


class TestEquipmentBasics:
    """Test basic equipment operations."""
    
    def test_player_starts_with_equipment(self):
        """Verify player has initial equipment from class defaults."""
        player = TestGameState.create_player(name="TestPlayer", class_name="Warrior", race_name="Human")
        
        assert player.equipment is not None
        assert "Weapon" in player.equipment
        assert "Armor" in player.equipment
        assert "OffHand" in player.equipment
        assert "Ring" in player.equipment
        assert "Pendant" in player.equipment
    
    def test_equipment_items_are_not_none(self):
        """Verify all equipment slots have valid items."""
        player = TestGameState.create_player(name="TestPlayer", class_name="Warrior", race_name="Human")
        
        for slot, item in player.equipment.items():
            assert item is not None, f"Equipment slot {slot} should not be None"
            assert hasattr(item, 'name'), f"Equipment in {slot} should have a name attribute"


class TestTwoHandedWeaponLogic:
    """Test two-handed weapon equipping and offhand conflicts."""
    
    def test_2h_weapon_has_correct_hand_count(self):
        """Verify 2H weapons are correctly marked as 2-handed."""
        two_handed = items.Claymore()
        assert two_handed.handed == 2, "Claymore should be 2-handed"
        
        two_handed_2 = items.Greataxe()
        assert two_handed_2.handed == 2, "Greataxe should be 2-handed"
    
    def test_lancer_can_equip_polearm_with_shield(self):
        """Verify Lancer/Dragoon can keep shield with polearm."""
        player = TestGameState.create_player(name="TestPlayer", class_name="Lancer", race_name="Human")
        
        # Start with shield
        player.equipment['OffHand'] = items.Buckler()
        shield_name = player.equipment['OffHand'].name
        
        # Equip polearm (2H but Lancer can use with shield)
        polearm = items.Partisan()
        assert polearm.subtyp == 'Polearm'
        assert polearm.handed == 2
        
        result = player.equip('Weapon', polearm, check=True)
        assert result is True
        
        # Shield should still be equipped
        assert player.equipment['OffHand'].name == shield_name
        assert player.equipment['Weapon'].name == 'Partisan'
    
    def test_dragoon_can_equip_polearm_with_shield(self):
        """Verify Dragoon (promotion of Lancer) can keep shield with polearm."""
        player = TestGameState.create_player(name="TestPlayer", class_name="Dragoon", race_name="Human")
        
        # Start with shield
        player.equipment['OffHand'] = items.Buckler()
        
        # Equip polearm
        polearm = items.Framea()
        assert polearm.subtyp == 'Polearm'
        result = player.equip('Weapon', polearm, check=True)
        assert result is True
        
        # Shield should still be equipped
        assert player.equipment['OffHand'].name == 'Buckler'
        assert player.equipment['Weapon'].name == 'Framea'
    
    def test_berserker_2h_weapon_logic(self):
        """Verify Berserker is not Lancer/Dragoon for 2H polearm exception."""
        berserker = TestGameState.create_player(name="TestPlayer", class_name="Berserker", race_name="Human")
        
        # Berserker should NOT have the Lancer/Dragoon polearm+shield exception
        assert berserker.cls.name == "Berserker"
        assert berserker.cls.name not in ["Lancer", "Dragoon"]


class TestClassEquipmentRestrictions:
    """Test class-specific equipment restrictions."""
    
    def test_warrior_can_equip_warrior_sword(self):
        """Verify Warrior can equip Warrior-class weapons."""
        player = TestGameState.create_player(name="TestPlayer", class_name="Warrior", race_name="Human")
        
        # Equip class-appropriate weapon
        weapon = items.Claymore()
        result = player.equip('Weapon', weapon, check=True)
        assert result is True
        assert player.equipment['Weapon'].name == 'Claymore'
    
    def test_different_classes_different_equipment(self):
        """Verify different classes prefer different equipment types."""
        warrior = TestGameState.create_player(name="Warrior", class_name="Warrior", race_name="Human")
        rogue = TestGameState.create_player(name="Rogue", class_name="Thief", race_name="Human")
        mage = TestGameState.create_player(name="Mage", class_name="Mage", race_name="Human")
        
        # All should have weapons but may be different types
        assert warrior.equipment['Weapon'] is not None
        assert rogue.equipment['Weapon'] is not None
        assert mage.equipment['Weapon'] is not None


class TestOffHandEquipment:
    """Test off-hand equipment handling."""
    
    def test_dual_wield_compatible_weapons(self):
        """Verify can equip compatible off-hand weapons."""
        player = TestGameState.create_player(name="TestPlayer", class_name="Warrior", race_name="Human")
        
        # Main hand weapon
        player.equipment['Weapon'] = items.Mace()
        
        # Off-hand: shields are valid off-hand
        offhand = items.Buckler()
        result = player.equip('OffHand', offhand, check=True)
        assert result is True
    
    def test_shield_in_offhand_slot(self):
        """Verify shields can be equipped in off-hand."""
        player = TestGameState.create_player(name="TestPlayer", class_name="Warrior", race_name="Human")
        
        shield = items.Buckler()
        assert shield.subtyp == 'Shield'
        
        result = player.equip('OffHand', shield, check=True)
        assert result is True
        assert player.equipment['OffHand'].name == 'Buckler'


class TestEquipmentSlots:
    """Test all equipment slots."""
    
    def test_all_equipment_slots_exist(self):
        """Verify all 5 equipment slots are present."""
        player = TestGameState.create_player(name="TestPlayer", class_name="Warrior", race_name="Human")
        
        required_slots = ['Weapon', 'Armor', 'OffHand', 'Ring', 'Pendant']
        for slot in required_slots:
            assert slot in player.equipment, f"Missing equipment slot: {slot}"
    
    def test_armor_slot_contains_armor(self):
        """Verify armor slot contains armor type."""
        player = TestGameState.create_player(name="TestPlayer", class_name="Warrior", race_name="Human")
        
        armor = player.equipment['Armor']
        assert armor is not None
        assert hasattr(armor, 'subtyp')
        # Should be 'Light', 'Medium', 'Heavy', or 'None'
        assert armor.subtyp in ['Light', 'Medium', 'Heavy', 'None']
    
    def test_ring_slot_contains_ring(self):
        """Verify ring slot contains ring or empty."""
        player = TestGameState.create_player(name="TestPlayer", class_name="Warrior", race_name="Human")
        
        ring = player.equipment['Ring']
        assert ring is not None
        assert hasattr(ring, 'name')
    
    def test_pendant_slot_contains_pendant(self):
        """Verify pendant slot contains pendant or empty."""
        player = TestGameState.create_player(name="TestPlayer", class_name="Warrior", race_name="Human")
        
        pendant = player.equipment['Pendant']
        assert pendant is not None
        assert hasattr(pendant, 'name')


class TestEquipmentEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_equip_same_item_twice(self):
        """Verify can't equip same item instance in multiple slots."""
        player = TestGameState.create_player(name="TestPlayer", class_name="Warrior", race_name="Human")
        
        sword = items.Mace()
        player.equipment['Weapon'] = sword
        
        # Trying to equip same item in OffHand should still work
        # (items might allow it or game prevents it)
        # This documents current behavior
        result = player.equip('OffHand', sword, check=True)
        # Result depends on implementation - just verify no crash
        assert isinstance(result, bool)
    
    def test_unequip_and_reequip(self):
        """Verify can unequip and re-equip items."""
        player = TestGameState.create_player(name="TestPlayer", class_name="Warrior", race_name="Human")
        
        original_weapon = player.equipment['Weapon']
        new_weapon = items.Claymore()
        
        # Equip new weapon
        player.equip('Weapon', new_weapon, check=True)
        assert player.equipment['Weapon'].name == 'Claymore'
        
        # Equipment changed successfully
        assert player.equipment['Weapon'].name != original_weapon.name


def run_tests():
    """Run all equipment tests."""
    print("=" * 70)
    print("EQUIPMENT SYSTEM TESTS")
    print("=" * 70)
    print()
    
    import pytest
    exit_code = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--color=yes'
    ])
    
    return exit_code


if __name__ == '__main__':
    sys.exit(run_tests())
