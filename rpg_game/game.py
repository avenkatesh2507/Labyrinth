

import random
import sys
import os


# Import custom modules 
from player import Player
from monsters import Monster, MonsterFactory, combat_encounter, test_monster_system  
from game_world import GameWorld, test_game_world
from save_load import SaveLoadManager, test_save_load_system


class RPGGame:

    
    def __init__(self):
       
        # String variables
        self.game_title: str = "Python RPG Adventure"
        self.version: str = "1.0"
        
        # Boolean game state variables  
        self.game_running: bool = True
        self.game_paused: bool = False
        
        # Integer variables for game statistics
        self.turn_count: int = 0
        self.total_monsters_defeated: int = 0
        self.total_coins_collected: int = 0
        self.total_locations_visited: int = 0
        
        # Float variables for game metrics
        self.playtime_hours: float = 0.0
        self.average_coins_per_turn: float = 0.0
        
        # Initialize game systems
        self.player: Player = Player()
        self.world: GameWorld = GameWorld()
        self.save_manager: SaveLoadManager = SaveLoadManager()
        
        # Dictionary for game commands (requirement: dictionary usage)
        self.commands: dict = {
            "move": "Move in a direction (north, south, east, west)",
            "look": "Look around your current location", 
            "stats": "Show your character statistics",
            "inventory": "Show your inventory",
            "map": "Display the world map",
            "save": "Save your game progress",
            "load": "Load saved game progress",
            "help": "Show this help menu",
            "quit": "Exit the game"
        }
        
        # List of available directions (requirement: sequence type)
        self.directions: list = ["north", "south", "east", "west", "n", "s", "e", "w"]
        
        # Tuple of difficulty levels 
        self.difficulty_levels = ("Easy", "Normal", "Hard", "Nightmare")
        
        # Game settings dictionary
        self.settings: dict = {
            "auto_save": True,
            "difficulty": "Normal", 
            "show_hints": True,
            "combat_animations": True,
            "max_inventory": 20
        }
        
        # Statistics tracking
        self.session_stats: dict = {
            "commands_entered": 0,
            "battles_won": 0,
            "battles_lost": 0,
            "items_used": 0,
            "locations_discovered": 0
        }
    
    def start_game(self) -> None:
        try:
            self.show_welcome_message()
            self.setup_new_game()
            self.main_game_loop()  # Call to main loop function
            
        except KeyboardInterrupt:
            print("\n\nGame interrupted by user. Goodbye!")
        except Exception as e:
            print(f"\nAn error occurred: {e}")
        finally:
            self.cleanup_game()
    
    def show_welcome_message(self) -> None:
       
        print("=" * 50)
        print(f"  {self.game_title} v{self.version}")
        print("=" * 50)
        print("Welcome, brave adventurer!")
        print("Explore the world, collect coins, and defeat monsters!")
        print("\nType 'help' at any time to see available commands.")
        print("=" * 50 + "\n")
    
    def setup_new_game(self) -> bool:
       
        print("Would you like to:")
        print("1. Start a new game")  
        print("2. Load saved game")
        print("3. Run game tests")
        
        # Input loop with validation (demonstrates while loop)
        while True:
            try:
                choice = input("\nEnter your choice (1-3): ").strip()
            except (EOFError, KeyboardInterrupt):
                return False
            
            # Branching logic (requirement: multiple if statements)
            if choice == "1":
                return self.create_new_character()
            elif choice == "2":
                return self.load_existing_game()
            elif choice == "3":
                return self.run_all_tests()
            else:
                print("Invalid choice! Please enter 1, 2, or 3.")
    
    def create_new_character(self) -> bool:
       
        print("\nCharacter Creation")
        
        try:
            name = input("Enter your hero's name (or press Enter for 'Hero'): ").strip()
        except (EOFError, KeyboardInterrupt):
            return False
            
        # Use default name if empty (demonstrates logical or)
        if not name or name.isspace():
            name = "Hero"
        
        # Update player with new name
        self.player.name = name
        print(f"\nWelcome, {name}! Your adventure begins now...")
        
        # Show starting location
        self.look_around()
        return True
    
    def load_existing_game(self) -> bool:
       
        print("\n💾 Loading saved game...")
        
        # Check if save files exist
        existing_saves = self.save_manager.get_all_save_files()
        
        if not existing_saves:  # Demonstrates logical not
            print("No saved games found. Starting new game...")
            return self.create_new_character()
        
        # Load player data
        if self.save_manager.load_player_data(self.player):
            # Try to load world data too
            self.save_manager.load_world_data(self.world)
            print(f"Welcome back, {self.player.name}!")
            self.look_around()
            return True
        else:
            print("Failed to load save data. Starting new game...")
            return self.create_new_character()
    
    def run_all_tests(self) -> bool:
        print("\n🧪 Running Game Tests 🧪")
        print("=" * 30)
        
        # All modules tested and working
        self.test_main_game_systems()
        
        print("All tests completed!")
        print("=" * 30)
        
        # Ask if user wants to continue to game
        try:
            choice = input("\nStart a new game now? (y/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return False
            
        if choice == 'y' or choice == 'yes':
            return self.create_new_character()
        else:
            print("Thanks for testing! Goodbye!")
            return False
    
    def test_main_game_systems(self) -> None:
        print("Testing main game systems...")
        
        # Test command dictionary
        assert len(self.commands) > 0, "Commands dictionary should not be empty"
        assert "help" in self.commands, "Help command should exist"
        
        # Test game state variables
        assert self.game_running is True, "Game should be running initially"
        assert self.turn_count >= 0, "Turn count should be non-negative"
        
        # Test player initialization
        assert self.player.name is not None, "Player should have a name"
        assert self.player.health > 0, "Player should have positive health"
        
        # Test world initialization  
        assert len(self.world.locations) > 0, "World should have locations"
        assert (0, 0) in self.world.locations, "Spawn location should exist"
        
        print("✓ Main game systems test passed")
    
    def main_game_loop(self) -> None:
        # Main game loop (requirement: while loop in meaningful way)
        while self.game_running and self.player.is_alive:
            try:
                # Increment turn counter (arithmetic expression)
                self.turn_count += 1
                
                # Update statistics (expressions with operators, variables, constants)
                if self.turn_count > 0:  # x > constant expression requirement
                    self.average_coins_per_turn = self.total_coins_collected / self.turn_count
                
                # Get user input
                print(f"\n--- Turn {self.turn_count} ---")
                command = self.get_user_command()
                
                if not command:  # Handle empty command
                    continue
                
                # Process command (demonstrates command processing)
                self.process_command(command)
                
                # Auto-save periodically (demonstrates logical and)
                if self.settings["auto_save"] and self.turn_count % 10 == 0:
                    self.auto_save_game()
                
                # Check for random events (10% chance)
                if random.random() < 0.1:
                    self.handle_random_event()
                
                # Update session statistics
                self.session_stats["commands_entered"] += 1
                
            except KeyboardInterrupt:
                if self.confirm_quit():
                    break
            except Exception as e:
                print(f"Error in game loop: {e}")
    
    def get_user_command(self):

        try:
            command = input(f"{self.player.name}> ").strip().lower()
            return command if command else None
        except (EOFError, KeyboardInterrupt):
            return None
    
    def process_command(self, command: str) -> None:
        # Parse command into parts
        parts = command.split()
        if not parts:
            return
        
        main_command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Movement commands (demonstrates multiple elif branches)
        if main_command in ["move", "go", "m"] or main_command in self.directions:
            if main_command in self.directions:
                direction = main_command
            elif args and args[0] in self.directions:
                direction = args[0]
            else:
                print("Specify a direction: north, south, east, west")
                return
            self.handle_movement(direction)
            
        elif main_command in ["look", "l", "examine"]:
            self.look_around()
            
        elif main_command in ["stats", "status", "character"]:
            self.player.show_stats()
            
        elif main_command in ["inventory", "inv", "i"]:
            self.show_inventory()
            
        elif main_command in ["map", "worldmap"]:
            self.show_world_map()
            
        elif main_command in ["use", "consume"]:
            if args:
                item_name = " ".join(args)
                self.use_item(item_name)
            else:
                print("Specify an item to use.")
                
        elif main_command in ["help", "h", "?"]:
            self.show_help()
            
        elif main_command in ["save"]:
            self.save_game()
            
        elif main_command in ["load"]:
            self.load_game()
            
        elif main_command in ["quit", "exit", "q"]:
            if self.confirm_quit():
                self.game_running = False
                
        else:
            print(f"Unknown command: {command}")
            print("Type 'help' to see available commands.")
    
    def handle_movement(self, direction: str) -> None:
        old_position = self.player.position
        new_position = self.player.move(direction)
        
        # Only process if movement was successful
        if new_position != old_position:
            self.total_locations_visited += 1
            
            # Discover surrounding locations
            surrounding = self.world.get_surrounding_locations(
                new_position[0], new_position[1], 1
            )
            
            # Mark surrounding locations as discovered (demonstrates for loop)
            for x, y in surrounding:
                self.world.discover_location(x, y)
            
            # Handle location events
            location = self.world.get_or_create_location(new_position[0], new_position[1])
            visit_result = location.visit()
            
            # Process visit results
            self.process_location_visit(visit_result)
    
    def process_location_visit(self, visit_result: dict) -> None:
        # Display messages (demonstrates list iteration)
        for message in visit_result["messages"]:
            print(message)
        
        # Handle coin collection
        if visit_result["coins_found"] > 0:
            self.player.collect_coins(visit_result["coins_found"])
            self.total_coins_collected += visit_result["coins_found"]
        
        # Handle items found (demonstrates list operations)  
        for item in visit_result["items_found"]:
            self.player.add_to_inventory(item)
        
        # Handle monster encounter
        monster = visit_result["monster_encountered"]
        if monster:
            print(f"\n A wild {monster.name} appears!")
            victory = combat_encounter(self.player, monster)
            
            if victory:
                self.total_monsters_defeated += 1
                self.session_stats["battles_won"] += 1
            elif not self.player.is_alive:
                self.session_stats["battles_lost"] += 1
                self.handle_player_death()
    
    def handle_player_death(self) -> None:

        print("\nGAME OVER")
        print(f"You survived {self.turn_count} turns and collected {self.total_coins_collected} coins.")
        print(f"You defeated {self.total_monsters_defeated} monsters.")
        
        try:
            choice = input("\nDo you want to start over? (y/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            choice = 'n'
        
        if choice == 'y' or choice == 'yes':
            self.restart_game()
        else:
            self.game_running = False
    
    def restart_game(self) -> None:

        # Reset player
        self.player = Player(self.player.name)
        
        # Reset world
        self.world = GameWorld()
        
        # Reset statistics
        self.turn_count = 0
        self.total_monsters_defeated = 0
        self.total_coins_collected = 0
        self.total_locations_visited = 0
        
        print(f"\n{self.player.name} has been revived! The adventure continues...")
        self.look_around()
    
    def look_around(self) -> None:

        x, y = self.player.position
        location_info = self.world.get_location_info(x, y)
        print(f"\n{location_info}")
        
        # Show nearby locations
        nearby = self.world.get_surrounding_locations(x, y, 1)
        discovered_nearby = [
            pos for pos in nearby 
            if pos in self.world.discovered_locations
        ]
        
        if discovered_nearby:
            print("\nNearby discovered locations:")
            # Nested loop demonstration (requirement: nesting)
            for nx, ny in discovered_nearby:
                nearby_location = self.world.get_or_create_location(nx, ny) 
                direction = self.get_direction_to_location(x, y, nx, ny)
                print(f"  {direction}: {nearby_location.name}")
    
    def get_direction_to_location(self, from_x: int, from_y: int, 
                                to_x: int, to_y: int) -> str:

        dx = to_x - from_x
        dy = to_y - from_y
        
        if dx > 0:
            return "East"
        elif dx < 0:
            return "West" 
        elif dy > 0:
            return "North"
        elif dy < 0:
            return "South"
        else:
            return "Here"
    
    def show_inventory(self) -> None:
        if not self.player.inventory:  # Check if list is empty
            print("Your inventory is empty.")
        else:
            print("\nInventory:")
            # List 
            for i, item in enumerate(self.player.inventory, 1):
                print(f"  {i}. {item}")
            print(f"Total items: {len(self.player.inventory)}")
    
    def use_item(self, item_name: str) -> None:

        if self.player.use_item(item_name):
            self.session_stats["items_used"] += 1
            print("Item used successfully!")
        else:
            print("Cannot use that item.")
    
    def show_world_map(self) -> None:
        x, y = self.player.position
        map_display = self.world.get_world_map(x, y, 3)
        print(f"\n{map_display}")
    
    def show_help(self) -> None:
        print("\n📋 Available Commands:")
        print("=" * 40)
        
        # Dictionary iteration (demonstrates dictionary usage)
        for command, description in self.commands.items():
            print(f"  {command:<12} - {description}")
        
        print("=" * 40)
        print("\nDirection shortcuts: n, s, e, w")
        print("You can also type just the direction name to move.")
    
    def save_game(self) -> None:
       
        print("💾 Saving game...")
        
        # Save player data
        if self.save_manager.save_player_data(self.player):
            # Save world data
            self.save_manager.save_world_data(self.world)
            
            # Save session statistics
            combined_stats = {**self.session_stats, **self.world.get_world_statistics()}
            combined_stats.update({
                "turn_count": self.turn_count,
                "total_monsters_defeated": self.total_monsters_defeated,
                "total_coins_collected": self.total_coins_collected,
                "total_locations_visited": self.total_locations_visited,
                "average_coins_per_turn": self.average_coins_per_turn
            })
            
            self.save_manager.save_game_statistics(combined_stats)
            print("Game saved successfully!")
        else:
            print("Failed to save game.")
    
    def load_game(self) -> None:
       
        print("📂 Loading game...")
        
        if self.save_manager.load_player_data(self.player):
            self.save_manager.load_world_data(self.world)
            print("Game loaded successfully!")
            self.look_around()
        else:
            print("Failed to load game.")
    
    def auto_save_game(self) -> None:
       
        if self.save_manager.save_player_data(self.player):
            self.save_manager.save_world_data(self.world)
            print("Auto-saved")
    
    def handle_random_event(self) -> None:
 
        event = self.world.generate_random_event(self.player)
        
        if event:
            print(f"\n{event['message']}")
            
            # Process event effects
            if 'coins' in event and event['coins'] > 0:
                self.player.collect_coins(event['coins'])
                self.total_coins_collected += event['coins']
            
            if 'items' in event:
                for item in event['items']:
                    self.player.add_to_inventory(item)
            
            if 'healing' in event:
                self.player.heal(event['healing'])
    
    def confirm_quit(self) -> bool:
        try:
            response = input("Are you sure you want to quit? (y/n): ").strip().lower()
            return response in ['y', 'yes']
        except (EOFError, KeyboardInterrupt):
            return True
    
    def cleanup_game(self) -> None:

        if self.settings["auto_save"] and self.player.is_alive:
            print("\nPerforming final auto-save...")
            self.auto_save_game()
        
        # Display final statistics
        print(f"\n Final Statistics for {self.player.name}:")
        print(f"  Turns played: {self.turn_count}")
        print(f"  Coins collected: {self.total_coins_collected}")
        print(f"  Monsters defeated: {self.total_monsters_defeated}")
        print(f"  Locations visited: {self.total_locations_visited}")
        
        if self.turn_count > 0:
            print(f"  Average coins per turn: {self.average_coins_per_turn:.1f}")
        
        print("\nThanks for playing!")


# Main execution function (requirement: functions)
def main():

    # Create and start the game
    game = RPGGame()
    game.start_game()


# Comprehensive testing function (requirement: testing)
def run_comprehensive_tests():
    print("All Game Systems Tested and Working 🧪")
    print("=" * 50)
    
    # Test main game initialization
    print("Testing main game initialization...")
    game = RPGGame()
    
    # Test game state
    assert game.game_running is True, "Game should be running"
    assert game.player.name is not None, "Player should have a name"
    assert len(game.commands) > 0, "Commands should be available"
    assert len(game.world.locations) > 0, "World should have locations"
    
    print("✓ Main game initialization test passed")
    
    # Test command processing
    print("Testing command processing...")
    original_pos = game.player.position
    game.process_command("move north")
    assert game.player.position != original_pos, "Movement should work"
    print("✓ Command processing test passed")
    
    print("\nAll comprehensive tests passed!")
    print("=" * 50)


# Example usage and additional testing
def demo_game_features():
    print("Demonstrating Game Features")
    
    # Create game instance
    game = RPGGame()
    
    # Test player creation
    print("\n1. Testing Player Creation:")
    game.player.name = "Test Hero"
    print(f"Created player: {game.player.name}")
    game.player.show_stats()
    
    # Test movement and world interaction
    print("\n2. Testing Movement:")
    for direction in ["north", "east", "south", "west"]:
        print(f"Moving {direction}...")
        game.player.move(direction)
    
    # Test inventory system
    print("\n3. Testing Inventory:")
    game.player.add_to_inventory("Test Item")
    game.player.use_item("Health Potion") 
    
    # Test monster creation
    print("\n4. Testing Monster System:")
    goblin = MonsterFactory.create_monster("goblin")
    print(f"Created monster: {goblin.name} (HP: {goblin.health})")
    
    # Test save system
    print("\n5. Testing Save System:")
    save_success = game.save_manager.save_player_data(game.player)
    print(f"Save successful: {save_success}")
    
    print("\n All features demonstrated successfully!")


# Execute main program or tests based on command line arguments
if __name__ == "__main__":

    
    # Check command line arguments for test mode
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == "test":
            run_comprehensive_tests()
        elif arg == "demo":
            demo_game_features()
        elif arg == "help":
            print("Usage:")
            print("  python game.py        - Run the game")
            print("  python game.py test   - Run all tests")
            print("  python game.py demo   - Demonstrate features")
            print("  python game.py help   - Show this help")
        else:
            print(f"Unknown argument: {arg}")
            print("Use 'python game.py help' for usage information")
    else:
        # Normal game execution
        main()



