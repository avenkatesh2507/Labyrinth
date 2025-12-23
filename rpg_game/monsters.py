import random
from abc import ABC, abstractmethod


class Monster(ABC):
    """Abstract base class for all monsters in the game.
    
    This class defines the common interface and behavior for all monsters,
    including health management, attack mechanics, and special abilities.
    Uses abstract methods to enforce implementation in subclasses.
    """
    def __init__(self, name: str, health: int, attack: int, coins_reward: int):
        """Initialize a monster with basic stats.
        
        Args:
            name (str): The monster's display name
            health (int): Starting health points
            attack (int): Base attack damage
            coins_reward (int): Coins dropped when defeated
        """
        self.name: str = name
        self.health: int = health
        self.max_health: int = health
        self.attack: int = attack
        self.coins_reward: int = coins_reward
        self.is_alive: bool = True
        
        # Dictionary for monster stats and resistances
        self.stats: dict = {
            "defense": 0,
            "speed": random.randint(1, 10),
            "magic_resistance": 0
        }
    
    @abstractmethod
    def special_ability(self) -> int:
        """Abstract method for monster special abilities.
        
        Each monster type must implement their own special ability.
        
        Returns:
            int: Additional damage from special ability
        """
        pass
    
    def take_damage(self, damage: int) -> bool:
        """Apply damage to the monster with defense calculation.
        
        Args:
            damage (int): Incoming damage amount
            
        Returns:
            bool: True if monster survives, False if defeated
        """
        # Calculate actual damage with defense
        actual_damage = max(1, damage - self.stats["defense"])
        self.health -= actual_damage
        
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            print(f"{self.name} has been defeated!")
            return False
        else:
            print(f"{self.name} took {actual_damage} damage. Health: {self.health}/{self.max_health}")
            return True
    
    def attack_player(self) -> int:
        base_damage = self.attack
        variation = random.randint(-2, 3)  # Random damage variation
        final_damage = max(1, base_damage + variation)
        
        print(f"{self.name} attacks for {final_damage} damage!")
        return final_damage


class Goblin(Monster):
    def __init__(self):
        super().__init__("Goblin", 30, 5, 15)
        self.stats["speed"] = random.randint(6, 10)  # Goblins are fast
        
    def special_ability(self) -> int:
        if random.random() < 0.3:  # 30% chance
            print(f"{self.name} uses Quick Strike!")
            return self.attack * 2
        return self.attack


class Orc(Monster):
    def __init__(self):
        super().__init__("Orc", 60, 8, 30)
        self.stats["defense"] = 2
        self.stats["speed"] = random.randint(1, 4)  # Orcs are slow
        
    def special_ability(self) -> int:
        if random.random() < 0.25:  # 25% chance
            print(f"{self.name} uses Brutal Slam!")
            return self.attack * 3
        return self.attack


class Dragon(Monster):
    def __init__(self):
        super().__init__("Dragon", 120, 15, 100)
        self.stats["defense"] = 5
        self.stats["magic_resistance"] = 8
        self.stats["speed"] = random.randint(5, 8)
        
    def special_ability(self) -> int:
        if random.random() < 0.4:  # 40% chance
            print(f"{self.name} breathes fire!")
            return self.attack * 2
        return self.attack


class Slime(Monster):
    def __init__(self):
        super().__init__("Slime", 25, 5, 10)
        self.stats["magic_resistance"] = 3
        
    def special_ability(self) -> int:
        if random.random() < 0.2 and self.health < self.max_health:  # 20% chance
            heal_amount = 5
            self.health = min(self.max_health, self.health + heal_amount)
            print(f"💚 {self.name} regenerates {heal_amount} health!")
        return self.attack


class MonsterFactory:
    # Dictionary mapping monster types to classes
    monster_types: dict = {
        "goblin": Goblin,
        "orc": Orc,
        "dragon": Dragon,
        "slime": Slime
    }
    
    # List of monster weights for random encounters
    encounter_weights = [
        ("goblin", 40),  # 40% chance
        ("slime", 30),   # 30% chance
        ("orc", 25),     # 25% chance
        ("dragon", 5)    # 5% chance
    ]
    
    @classmethod
    def create_monster(cls, monster_type: str = None, player_level: int = 1) -> Monster:
        if monster_type is None:
            monster_type = cls.get_random_monster_type(player_level)
        
        monster_type = monster_type.lower()
        
        if monster_type in cls.monster_types:
            return cls.monster_types[monster_type]()
        else:
            print(f"Unknown monster type: {monster_type}")
            return cls.monster_types["goblin"]()  # Default to goblin
    
    @classmethod
    def get_random_monster_type(cls, player_level: int = 1) -> str:
        # Level-based monster spawning
        if player_level <= 2:
            # Early game: only goblins and slimes
            weighted_list = ["goblin"] * 60 + ["slime"] * 40
        elif player_level <= 5:
            # Mid game: goblins, slimes, and some orcs
            weighted_list = ["goblin"] * 40 + ["slime"] * 35 + ["orc"] * 25
        else:
            # Late game: all monsters including dragons
            weighted_list = ["goblin"] * 30 + ["slime"] * 25 + ["orc"] * 35 + ["dragon"] * 10
        
        return random.choice(weighted_list)
    
    @classmethod
    def get_all_monster_types(cls) -> list:
        return list(cls.monster_types.keys())


def combat_encounter(player, monster: Monster) -> bool:
    print(f"\nCombat begins! {player.name} vs {monster.name}")
    print(f"Monster Health: {monster.health}")
    print(f"Your Health: {player.health}")
    
    player.in_combat = True
    
    # Main combat loop (requirement: while loop)
    while player.is_alive and monster.is_alive:
        print("\n" + "-"*20)
        print("Choose your action:")
        print("1. Attack")
        print("2. Use Item")
        print("3. Try to Flee")
        
        try:
            choice = input("Enter choice (1-3): ").strip()
        except (EOFError, KeyboardInterrupt):
            choice = "3"  # Default to flee if input fails
        
        # Player action phase
        if choice == "1":
            # Player attacks
            damage = player.attack_power + random.randint(-2, 3)
            print(f"You attack {monster.name} for {damage} damage!")
            monster.take_damage(damage)
            
        elif choice == "2":
            # Use item
            if player.inventory:  # Check if inventory is not empty
                print(f"Inventory: {', '.join(player.inventory)}")
                item = input("Enter item name: ").strip()
                if not player.use_item(item):
                    continue  # Skip monster turn if invalid item
            else:
                print("Your inventory is empty!")
                continue  # Skip monster turn
                
        elif choice == "3":
            # Try to flee
            flee_chance = 0.5  # 50% base flee chance
            if player.position[0] == 0 and player.position[1] == 0:  # At spawn
                flee_chance = 0.8  # Higher chance at spawn
                
            if random.random() < flee_chance:
                print("You successfully fled from combat!")
                player.in_combat = False
                return False  # Combat ended, no winner
            else:
                print("You failed to escape!")
                
        else:
            print("Invalid choice! You lose your turn.")
        
        # Monster action phase (if monster is still alive)
        if monster.is_alive:
            # 50% chance for special ability, otherwise normal attack
            if random.random() < 0.5:
                damage = monster.special_ability()
            else:
                damage = monster.attack_player()
            
            player.take_damage(damage)
    
    player.in_combat = False
    
    # Combat resolution
    if player.is_alive and not monster.is_alive:
        print(f"\nVictory! You defeated the {monster.name}!")
        
        # Reward calculation
        coins_earned = monster.coins_reward
        exp_earned = monster.max_health * 0.5
        
        player.collect_coins(coins_earned)
        player.experience += exp_earned
        
        # Random item drop (30% chance)
        if random.random() < 0.3:
            items = ["Health Potion", "Bread", "Rusty Key", "Magic Crystal"]
            item_found = random.choice(items)
            player.add_to_inventory(item_found)
            print(f"You found a {item_found}!")
        
        return True
    elif not player.is_alive:
        print(f"\nDefeat! You were slain by the {monster.name}...")
        return False
    else:
        return False  # Fled or other outcome


def test_monster_system():
    print("Testing Monster system...")
    
    # Test monster creation
    goblin = MonsterFactory.create_monster("goblin")
    assert goblin.name == "Goblin", "Goblin creation failed"
    assert goblin.health > 0, "Monster health not positive"
    print("✓ Monster creation test passed")
    
    # Test monster factory
    random_monster = MonsterFactory.create_monster()
    assert random_monster.name in ["Goblin", "Orc", "Dragon", "Slime"], "Random monster creation failed"
    print("✓ Monster factory test passed")
    
    # Test monster stats
    all_types = MonsterFactory.get_all_monster_types()
    assert len(all_types) > 0, "No monster types available"
    print("✓ Monster types test passed")
    
    # Test special abilities
    orc = MonsterFactory.create_monster("orc")
    damage = orc.special_ability()
    assert damage >= orc.attack, "Special ability damage too low"
    print("✓ Special abilities test passed")
    
    print("All Monster tests passed! ✅\n")


# Uncomment to run tests
# test_monster_system()