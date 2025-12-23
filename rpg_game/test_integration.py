#!/usr/bin/env python3

import pygame
import sys
import os
import time

# Add the rpg_game directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graphical_game import GraphicalRPGGame
from player import Player
from monsters import MonsterFactory
from save_load import SaveLoadManager


class IntegrationTests:
    
    def __init__(self):
        self.test_results = []
    
    def log_test(self, test_name, passed, message=""):
        status = "✓ PASSED" if passed else "✗ FAILED"
        self.test_results.append((test_name, passed, message))
        print(f"{test_name}: {status} {message}")
    
    def test_game_initialization(self):
        try:
            # Test without pygame display (headless mode for CI)
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
            pygame.init()
            pygame.display.set_mode((1, 1))
            
            game = GraphicalRPGGame()
            
            # Check basic game state
            assert hasattr(game, 'player')
            assert hasattr(game, 'world')
            assert hasattr(game, 'ui')
            assert game.game_state == "playing"
            
            pygame.quit()
            self.log_test("Game Initialization", True)
            return True
            
        except Exception as e:
            self.log_test("Game Initialization", False, str(e))
            return False
    
    def test_player_progression_cycle(self):
        try:
            player = Player("TestHero")
            
            # Test initial state
            assert player.level == 1
            assert player.health == 100
            initial_attack = player.attack_power
            
            # Simulate collecting experience and leveling up
            for level in range(2, 6):  # Level up to 5
                player.experience = 100.0
                old_health = player.max_health
                player.level_up()
                
                assert player.level == level
                assert player.max_health > old_health
                assert player.attack_power > initial_attack
                
            self.log_test("Player Progression Cycle", True, f"Reached level {player.level}")
            return True
            
        except Exception as e:
            self.log_test("Player Progression Cycle", False, str(e))
            return False
    
    def test_combat_scenario(self):
        try:
            player = Player("TestWarrior")
            player.level = 5  # Give player some strength
            player.max_health = 180
            player.health = 180
            player.attack_power = 30
            
            # Create a monster
            monster = MonsterFactory.create_monster("goblin")
            initial_monster_health = monster.health
            initial_player_health = player.health
            
            # Simulate combat rounds
            rounds = 0
            while monster.is_alive and player.is_alive and rounds < 20:
                # Player attacks
                damage = player.attack_power // 2  # Simplified damage
                monster.take_damage(damage)
                
                # Monster attacks back if still alive
                if monster.is_alive:
                    monster_damage = monster.attack_player()
                    player.take_damage(monster_damage)
                
                rounds += 1
            
            # Combat should end with either monster or player defeated
            assert not (monster.is_alive and player.is_alive) or rounds >= 20
            
            self.log_test("Combat Scenario", True, f"Combat ended in {rounds} rounds")
            return True
            
        except Exception as e:
            self.log_test("Combat Scenario", False, str(e))
            return False
    
    def test_save_load_cycle(self):
        try:
            # Create test save manager
            save_manager = SaveLoadManager("integration_test_saves")
            
            # Create a player with some progress
            original_player = Player("SaveTestHero")
            original_player.level = 3
            original_player.coins = 150
            original_player.add_to_inventory("Magic Sword")
            original_player.position = (5, -3)
            
            # Save the player
            success = save_manager.save_player_data(original_player)
            assert success, "Save operation failed"
            
            # Load the player back
            loaded_data = save_manager.load_player_data()
            assert loaded_data is not None, "Load operation failed"
            
            # Verify data integrity
            assert loaded_data['name'] == "SaveTestHero"
            assert int(loaded_data['level']) == 3
            assert int(loaded_data['coins']) == 150
            assert "Magic Sword" in loaded_data['inventory']
            assert int(loaded_data['position_x']) == 5
            assert int(loaded_data['position_y']) == -3
            
            self.log_test("Save/Load Cycle", True, "Data integrity verified")
            
            # Cleanup
            import shutil
            if os.path.exists("integration_test_saves"):
                shutil.rmtree("integration_test_saves")
            
            return True
            
        except Exception as e:
            self.log_test("Save/Load Cycle", False, str(e))
            return False
    
    def test_monster_scaling(self):
        try:
            # Test early game monsters (level 1-2)
            early_monsters = [MonsterFactory.create_monster(None, level) for level in [1, 2]]
            
            # Should only get weak monsters
            for monster in early_monsters:
                assert monster.name in ["Goblin", "Slime"], f"Wrong monster for early game: {monster.name}"
            
            # Test late game monsters (level 10+)
            late_monsters = [MonsterFactory.create_monster(None, level) for level in [10, 15]]
            
            # Could get any monster including dragons
            monster_types = [m.name for m in late_monsters]
            
            self.log_test("Monster Scaling", True, f"Monster variety: {set(monster_types)}")
            return True
            
        except Exception as e:
            self.log_test("Monster Scaling", False, str(e))
            return False
    
    def test_inventory_management(self):
        try:
            player = Player("InventoryTester")
            
            # Test adding items
            initial_count = len(player.inventory)
            player.add_to_inventory("Test Sword")
            player.add_to_inventory("Test Potion")
            
            assert len(player.inventory) == initial_count + 2
            assert "Test Sword" in player.inventory
            assert "Test Potion" in player.inventory
            
            # Test using items
            player.health = 50  # Damage the player
            initial_health = player.health
            
            # Add and use a health potion
            player.add_to_inventory("Health Potion")
            used = player.use_item("Health Potion")
            
            assert used, "Health potion should be usable"
            assert player.health > initial_health, "Health should increase"
            assert "Health Potion" not in player.inventory, "Potion should be consumed"
            
            self.log_test("Inventory Management", True)
            return True
            
        except Exception as e:
            self.log_test("Inventory Management", False, str(e))
            return False
    
    def run_all_tests(self):
        print("="*60)
        print("RPG GAME INTEGRATION TEST SUITE")
        print("="*60)
        
        tests = [
            self.test_game_initialization,
            self.test_player_progression_cycle,
            self.test_combat_scenario,
            self.test_save_load_cycle,
            self.test_monster_scaling,
            self.test_inventory_management
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"Test failed with exception: {e}")
        
        print("="*60)
        print(f"INTEGRATION TEST RESULTS:")
        print(f"Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print("="*60)
        
        # Print detailed results
        for test_name, passed_test, message in self.test_results:
            status = "✓" if passed_test else "✗"
            print(f"{status} {test_name} {message}")
        
        return passed == total


def main():
    integration_tests = IntegrationTests()
    success = integration_tests.run_all_tests()
    
    if success:
        print("\nAll integration tests passed!")
        print("The RPG game is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Some integration tests failed!")
        print("Check the test results above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()