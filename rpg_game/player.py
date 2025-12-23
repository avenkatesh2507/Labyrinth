import random


class Player:
    """Represents the player character in the RPG.
    
    This class manages player stats, inventory, position, and various game states.
    Demonstrates multiple Python data types including strings, integers, floats,
    dictionaries, lists, tuples, sets, and booleans.
    """
    def __init__(self, name: str = "Hero"):
        """Initialize a new player with default stats and equipment.
        
        Args:
            name (str): The player's chosen name, defaults to "Hero"
        """
        # Variables of different data types
        self.name: str = name  # string
        self.health: int = 100  # integer
        self.max_health: int = 100
        self.coins: int = 0  # integer
        self.level: int = 1  # integer
        self.experience: float = 0.0  # float
        self.attack_power: int = 10
        
        # Dictionary for equipment (requirement: include dictionary)
        self.equipment: dict = {
            "weapon": "Wooden Sword",
            "armor": "Cloth Shirt", 
            "accessory": "None"
        }
        
        # List for inventory (requirement: sequence data type)
        self.inventory: list = ["Health Potion", "Bread"]
        
        # Tuple for position coordinates (requirement: sequence data type)
        self.position = (0, 0)
        
        # Set for visited locations (requirement: sequence data type)
        self.visited_locations: set = {(0, 0)}
        
        # Boolean variables for game states
        self.is_alive: bool = True
        self.in_combat: bool = False
        
        # Coin collection system
        self.coins: int = 0
        
    def move(self, direction: str):
        """Move the player in the specified direction.
        
        Updates player position based on directional input and tracks
        visited locations for exploration mechanics.
        
        Args:
            direction (str): Direction to move (north/n, south/s, east/e, west/w)
        """
        x, y = self.position
        old_position = self.position
        
        # Branching logic (requirement: multiple if statements)
        if direction.lower() == "north" or direction.lower() == "n":
            y += 1
        elif direction.lower() == "south" or direction.lower() == "s":
            y -= 1
        elif direction.lower() == "east" or direction.lower() == "e":
            x += 1
        elif direction.lower() == "west" or direction.lower() == "w":
            x -= 1
        else:
            print("Invalid direction! Use north, south, east, or west.")
            return self.position
            
        # Update position and add to visited locations
        self.position = (x, y)
        self.visited_locations.add(self.position)
        
        print(f"You moved {direction} from {old_position} to {self.position}")
        return self.position
    
    def collect_coins(self, amount: int) -> bool:
        if amount > 0:  # Logical expression
            self.coins += amount  # Arithmetic expression
            print(f"You collected {amount} coins! Total coins: {self.coins}")
            
            # Level up check (expression with operators, variables, constants)
            if self.coins >= (self.level * 50):  # x >= constant expression
                self.level_up()
            return True
        return False
    
    def level_up(self) -> None:
        """Level up the player, increasing stats and resetting experience.
        
        Increases level, max health, attack power, and fully heals the player.
        This provides meaningful character progression throughout the game.
        """
        self.level += 1
        self.max_health += 20
        self.health = self.max_health  # Full heal on level up
        self.attack_power += 5
        self.experience = 0.0
        
        print(f"Level up! You are now level {self.level}!")
        print(f"Health: {self.health}, Attack Power: {self.attack_power}")
    
    def take_damage(self, damage: int) -> bool:
        """Apply damage to the player and check if they survive.
        
        Args:
            damage (int): Amount of damage to take
            
        Returns:
            bool: True if player survives, False if defeated
        """
        self.health -= damage
        
        # Logical expression with comparison
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            print(f"{self.name} has been defeated!")
            return False
        else:
            print(f"You took {damage} damage. Health: {self.health}/{self.max_health}")
            return True
    
    def heal(self, amount: int) -> None:
        """Heal the player by the specified amount, up to max health.
        
        Args:
            amount (int): Amount of health to restore
        """
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        actual_heal = self.health - old_health
        
        if actual_heal > 0:
            print(f"You healed for {actual_heal} HP. Health: {self.health}/{self.max_health}")
        else:
            print("You are already at full health!")
    
    def use_item(self, item_name: str) -> bool:
        """Use an item from the player's inventory.
        
        Args:
            item_name (str): Name of the item to use
            
        Returns:
            bool: True if item was successfully used, False otherwise
        """
        # Check if item exists in inventory (using list method)
        if item_name in self.inventory:
            self.inventory.remove(item_name)  # List method
            
            # Nested branching logic
            if item_name.lower() == "health potion":
                self.heal(30)
                return True
            elif item_name.lower() == "bread":
                self.heal(10)
                return True
            else:
                print(f"You don't know how to use {item_name}")
                self.inventory.append(item_name)  # Put it back
                return False
        else:
            print(f"You don't have {item_name} in your inventory")
            return False
    
    def add_to_inventory(self, item: str) -> None:
        self.inventory.append(item)
        print(f"Added {item} to inventory")
    
    def show_stats(self) -> None:
        print("\n" + "="*30)
        print(f"Player: {self.name}")
        print(f"Level: {self.level}")
        print(f"Health: {self.health}/{self.max_health}")
        print(f"Coins: {self.coins}")
        print(f"Attack Power: {self.attack_power}")
        print(f"Position: {self.position}")
        
        # Access dictionary values by key (requirement)
        print(f"Weapon: {self.equipment['weapon']}")
        print(f"Armor: {self.equipment['armor']}")
        print(f"Accessory: {self.equipment['accessory']}")
        
        print(f"Inventory: {', '.join(self.inventory) if self.inventory else 'Empty'}")
        print(f"Locations visited: {len(self.visited_locations)}")
        print("="*30 + "\n")
    
    def get_save_data(self) -> dict:
        return {
            "name": self.name,
            "health": self.health,
            "max_health": self.max_health,
            "coins": self.coins,
            "level": self.level,
            "experience": self.experience,
            "attack_power": self.attack_power,
            "position_x": self.position[0],
            "position_y": self.position[1],
            "equipment_weapon": self.equipment["weapon"],
            "equipment_armor": self.equipment["armor"],
            "equipment_accessory": self.equipment["accessory"],
            "inventory": "|".join(self.inventory),  # Convert list to string
            "visited_locations": "|".join([f"{x},{y}" for x, y in self.visited_locations])
        }
    
    def load_save_data(self, data: dict) -> None:
        try:
            self.name = data.get("name", "Hero")
            self.health = int(data.get("health", 100))
            self.max_health = int(data.get("max_health", 100))
            self.coins = int(data.get("coins", 0))
            self.level = int(data.get("level", 1))
            self.experience = float(data.get("experience", 0.0))
            self.attack_power = int(data.get("attack_power", 10))
            
            # Reconstruct tuple from saved data
            pos_x = int(data.get("position_x", 0))
            pos_y = int(data.get("position_y", 0))
            self.position = (pos_x, pos_y)
            
            # Reconstruct dictionary
            self.equipment["weapon"] = data.get("equipment_weapon", "Wooden Sword")
            self.equipment["armor"] = data.get("equipment_armor", "Cloth Shirt")
            self.equipment["accessory"] = data.get("equipment_accessory", "None")
            
            # Reconstruct list from string
            inventory_str = data.get("inventory", "Health Potion|Bread")
            self.inventory = inventory_str.split("|") if inventory_str else []
            
            # Reconstruct set from string
            locations_str = data.get("visited_locations", "0,0")
            if locations_str:
                locations = [loc.split(",") for loc in locations_str.split("|")]
                self.visited_locations = {(int(x), int(y)) for x, y in locations}
            
        except (ValueError, KeyError) as e:
            print(f"Error loading save data: {e}")
            print("Using default values...")

