#!/usr/bin/env python3
"""
Demo script for Python RPG Labyrinth
Showcases the key features of the game without requiring manual interaction
"""

import sys
import os
import time

# Add the game directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'rpg_game'))

def demo_game_features():
    """
    Demonstrates key game features programmatically
    """
    print("🎮 Python RPG Labyrinth - Feature Demo")
    print("=" * 50)
    print()
    
    # Test imports
    print("📦 Testing game module imports...")
    try:
        from player import Player
        from monsters import MonsterFactory, Monster
        from game_world import GameWorld
        from save_load import SaveLoadManager
        print("✓ All core modules imported successfully")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    print()
    
    # Test player creation
    print("👤 Creating demo player...")
    player = Player("DemoHero")
    print(f"✓ Player created: {player.name}")
    print(f"  Level: {player.level}")
    print(f"  Health: {player.health}/{player.max_health}")
    print(f"  Experience: {player.experience}")
    print()
    
    # Test monster creation
    print("👹 Creating demo monsters...")
    monster_factory = MonsterFactory()
    goblin = monster_factory.create_monster("goblin", 1)
    orc = monster_factory.create_monster("orc", 2)
    print(f"✓ Goblin created: Health {goblin.health}, Attack {goblin.attack}")
    print(f"✓ Orc created: Health {orc.health}, Attack {orc.attack}")
    print()
    
    # Test world generation
    print("🌍 Generating demo world...")
    world = GameWorld()
    # Create some locations around spawn
    locations_created = []
    for x in range(-2, 3):
        for y in range(-2, 3):
            if abs(x) + abs(y) <= 2:  # Diamond pattern around spawn
                location = world.get_or_create_location(x, y)
                locations_created.append(location)
    
    print(f"✓ World created with {len(world.locations)} locations")
    print(f"  Starting area has {len(world.discovered_locations)} discovered locations")
    print()
    
    # Test save system
    print("💾 Testing save system...")
    save_manager = SaveLoadManager()
    # Create a demo save (won't actually save to avoid file clutter)
    print("✓ Save system initialized and ready")
    print()
    
    # Test combat simulation (without actual UI)
    print("⚔️  Simulating combat...")
    print(f"  {player.name} (Level {player.level}) vs {goblin.name}")
    
    # Simple combat simulation
    original_player_health = player.health
    original_goblin_health = goblin.health
    
    # Player attacks (using attack_power instead of strength)
    damage = max(1, player.attack_power - goblin.stats.get("defense", 0))
    goblin.health -= damage
    print(f"  {player.name} attacks for {damage} damage!")
    
    if goblin.health > 0:
        # Goblin attacks back (simplified defense calculation)
        base_defense = 2  # Basic defense value
        damage = max(1, goblin.attack - base_defense)
        player.health -= damage
        print(f"  {goblin.name} attacks back for {damage} damage!")
    
    print(f"  Combat result: Player health {player.health}/{player.max_health}, Goblin health {goblin.health}")
    
    if goblin.health <= 0:
        print("  🏆 Player wins!")
        coins_earned = goblin.coins_reward
        player.collect_coins(coins_earned)
        print(f"  +{coins_earned} coins earned")
    
    print()
    
    # Test level progression
    print("📈 Testing character progression...")
    original_level = player.level
    # Give enough coins to level up (level * 50)
    coins_needed = (player.level * 50) - player.coins
    if coins_needed > 0:
        player.collect_coins(coins_needed)
    
    if player.level > original_level:
        print(f"✓ Level up! {original_level} → {player.level}")
        print(f"  New stats - Attack: {player.attack_power}, Max Health: {player.max_health}")
    else:
        print(f"✓ Coins collected: {player.coins} total")
    
    print()
    
    # Test pygame availability
    print("🎨 Testing graphics system...")
    try:
        import pygame
        pygame.init()
        print(f"✓ Pygame {pygame.version.ver} is available")
        print("✓ Graphics system ready for full game launch")
        pygame.quit()
    except ImportError:
        print("✗ Pygame not available - install with: pip install pygame")
        return False
    
    print()
    print("🎉 Demo completed successfully!")
    print("🚀 Run 'python rpg_game/start_game.py' to play the full game!")
    return True

def quick_game_test():
    """
    Quick test to verify the graphical game can be imported
    """
    print("\n🔧 Quick integration test...")
    try:
        from graphical_game import GraphicalRPGGame
        print("✓ Graphical game engine can be imported")
        print("✓ All dependencies resolved")
        return True
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting Python RPG Labyrinth demonstration...\n")
    
    # Run the demo
    success = demo_game_features()
    
    if success:
        # Quick integration test
        quick_game_test()
        print(f"\n{'='*50}")
        print("🎮 Ready to play! Use one of these commands:")
        print("   python demo.py                    # Run this demo")
        print("   python rpg_game/start_game.py     # Start the full game")
        print("   python rpg_game/graphical_game.py # Direct game launch")
        print(f"{'='*50}")
    else:
        print("\n❌ Demo failed. Please check the error messages above.")
        print("Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)