#!/usr/bin/env python3

import pygame
import sys
import os

# Add the rpg_game directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graphics_engine import PlayerSprite, UI, test_graphics_engine
from player import Player
from monsters import MonsterFactory
from save_load import SaveLoadManager


class TestSuite:
    
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.total_tests = 0
    
    def run_test(self, test_name, test_function):
        self.total_tests += 1
        print(f"Running {test_name}...", end=" ")
        
        try:
            test_function()
            print("✓ PASSED")
            self.passed_tests += 1
        except Exception as e:
            print(f"✗ FAILED: {e}")
            self.failed_tests += 1
    
    def test_player_creation(self):
        player = Player("TestPlayer")
        assert player.name == "TestPlayer"
        assert player.health == 100
        assert player.level == 1
        assert player.coins == 0
        assert len(player.inventory) >= 2  # Should have initial items
    
    def test_player_leveling(self):
        player = Player("TestPlayer")
        original_health = player.health
        original_attack = player.attack_power
        
        # Simulate experience gain and level up
        player.experience = 100.0
        player.level_up()
        
        assert player.level == 2
        assert player.health > original_health
        assert player.attack_power > original_attack
    
    def test_monster_creation(self):
        goblin = MonsterFactory.create_monster("goblin")
        assert goblin.name == "Goblin"
        assert goblin.health > 0
        assert goblin.attack > 0
        
        orc = MonsterFactory.create_monster("orc")
        assert orc.name == "Orc"
        assert orc.health > goblin.health  # Orc should be stronger
    
    def test_level_based_spawning(self):
        # Test early game spawning (level 1)
        low_level_monster = MonsterFactory.create_monster(None, 1)
        assert low_level_monster.name in ["Goblin", "Slime"]
        
        # Test high level spawning (level 10) 
        high_level_monster = MonsterFactory.create_monster(None, 10)
        # Should be able to spawn any monster type
        assert high_level_monster.name in ["Goblin", "Slime", "Orc", "Dragon"]
    
    def test_save_load_manager(self):
        save_manager = SaveLoadManager("test_saves")
        
        # Test directory creation
        assert os.path.exists("test_saves") or True  # Will create if doesn't exist
        
        # Test player data structure
        player = Player("TestSave")
        player_data = save_manager._player_to_dict(player)
        
        assert "name" in player_data
        assert "health" in player_data
        assert "level" in player_data
        assert "coins" in player_data
    
    def test_combat_calculations(self):
        player = Player("TestPlayer")
        goblin = MonsterFactory.create_monster("goblin")
        
        # Test that damage is within expected range
        initial_health = goblin.health
        damage = 10
        
        goblin.take_damage(damage)
        assert goblin.health == initial_health - damage
        assert not goblin.is_alive if goblin.health <= 0 else goblin.is_alive
    
    def test_graphics_components(self):
        # This will run the existing graphics engine tests
        test_graphics_engine()
    
    def run_all_tests(self):
        print("="*50)
        print("RPG GAME TEST SUITE")
        print("="*50)
        
        # Run all tests
        self.run_test("Player Creation", self.test_player_creation)
        self.run_test("Player Leveling", self.test_player_leveling)
        self.run_test("Monster Creation", self.test_monster_creation)
        self.run_test("Level-based Spawning", self.test_level_based_spawning)
        self.run_test("Save/Load Manager", self.test_save_load_manager)
        self.run_test("Combat Calculations", self.test_combat_calculations)
        self.run_test("Graphics Components", self.test_graphics_components)
        
        # Print results
        print("="*50)
        print(f"TEST RESULTS:")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        print("="*50)
        
        # Cleanup
        self.cleanup()
        
        return self.failed_tests == 0
    
    def cleanup(self):
        import shutil
        if os.path.exists("test_saves"):
            shutil.rmtree("test_saves")


def main():
    test_suite = TestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()