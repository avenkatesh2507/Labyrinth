import random
from monsters import MonsterFactory, Monster


class Location:
    def __init__(self, x: int, y: int, name: str = None):
        self.coordinates = (x, y)
        self.name: str = name or f"Location ({x}, {y})"
        
        # Dictionary for location properties
        self.properties: dict = {
            "has_coins": False,
            "coin_amount": 0,
            "has_monster": False,
            "monster_type": None,
            "is_safe": False,
            "description": "A mysterious location...",
            "visited_count": 0
        } 
        
        # List of items that can be found here
        self.items: list = []
        
        # Generate random location features
        self._generate_location_features()
    
    def _generate_location_features(self):
        x, y = self.coordinates
        
        # Special locations (using logical and/or operators)
        if x == 0 and y == 0:  # Spawn point
            self.name = "Village Center"
            self.properties["is_safe"] = True
            self.properties["description"] = "A peaceful village where your journey begins."
            
        elif abs(x) >= 5 or abs(y) >= 5:  # Far locations
            self.name = "Dangerous Wilderness"
            self.properties["has_monster"] = True
            self.properties["monster_type"] = "dragon" if random.random() < 0.3 else "orc"
            self.properties["description"] = "A dangerous area filled with powerful monsters."
            
        elif abs(x) + abs(y) == 1:  # Adjacent to spawn
            self.name = "Village Outskirts" 
            self.properties["has_coins"] = random.random() < 0.7 
            self.properties["coin_amount"] = random.randint(5, 15)
            self.properties["description"] = "The quiet outskirts of the village."
            
        else:  # Normal locations
            # Coin generation 
            if random.random() < 0.3:
                self.properties["has_coins"] = True
                self.properties["coin_amount"] = random.randint(10, 25)
            
            # Monster generation (40% chance, but not if coins present)
            if not self.properties["has_coins"] and random.random() < 0.4:
                self.properties["has_monster"] = True
                
            # Item generation 
            if random.random() < 0.2:
                possible_items = ["Health Potion", "Bread", "Rusty Key", "Map Fragment", "Magic Crystal"]
                self.items.append(random.choice(possible_items))
        
        # Generate location name based on coordinates
        if not hasattr(self, 'name') or "Location" in self.name:
            self._generate_location_name()
    
    def _generate_location_name(self):
        x, y = self.coordinates
        
        # Lists for name generation (demonstrates list usage)
        prefixes = ["Ancient", "Forgotten", "Mystic", "Dark", "Sunny", "Frozen", "Burning"]
        places = ["Forest", "Cave", "Ruins", "Temple", "Meadow", "Mountain", "Valley"]
        
        # Use coordinate-based selection for consistency
        prefix_index = abs(x + y) % len(prefixes)
        place_index = abs(x * y + 1) % len(places)
        
        self.name = f"{prefixes[prefix_index]} {places[place_index]}"
    
    def visit(self) -> dict:
        self.properties["visited_count"] += 1
        
        visit_result = {
            "coins_found": 0,
            "items_found": [],
            "monster_encountered": None,
            "messages": []
        }
        
        visit_result["messages"].append(f"You arrive at {self.name}")
        visit_result["messages"].append(self.properties["description"])
        
        # Handle coin collection
        if self.properties["has_coins"]:
            visit_result["coins_found"] = self.properties["coin_amount"]
            visit_result["messages"].append(f"You found {self.properties['coin_amount']} coins!")
            
            # Remove coins after collection
            self.properties["has_coins"] = False
            self.properties["coin_amount"] = 0
        
        # Handle item collection
        if self.items:
            for item in self.items[:]:  # Copy list to avoid modification during iteration
                visit_result["items_found"].append(item)
                visit_result["messages"].append(f"You found a {item}!")
                self.items.remove(item)
        
        # Handle monster encounter
        if self.properties["has_monster"]:
            monster_type = self.properties["monster_type"]
            if monster_type:
                visit_result["monster_encountered"] = MonsterFactory.create_monster(monster_type)
            else:
                visit_result["monster_encountered"] = MonsterFactory.create_monster()
            
            visit_result["messages"].append(f"A {visit_result['monster_encountered'].name} appears!")
        
        return visit_result


class GameWorld:
    def __init__(self):
        # Dictionary of all locations (nested dictionary structure)
        self.locations: dict = {}
        
        # Set of discovered locations
        self.discovered_locations = set()
        
        # Dictionary for world statistics
        self.world_stats: dict = {
            "total_locations_created": 0,
            "total_coins_generated": 0,
            "total_monsters_spawned": 0,
            "total_items_placed": 0
        }
        
        # List of special events
        self.special_events: list = []
        
        # Initialize spawn location
        self._create_spawn_area()
    
    def _create_spawn_area(self):
        spawn_coords = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]
        
        # Loop to create spawn area
        for x, y in spawn_coords:
            self.get_or_create_location(x, y)
            self.discovered_locations.add((x, y))
    
    def get_or_create_location(self, x: int, y: int) -> Location:
        coords = (x, y)
        
        if coords not in self.locations:
            #new location
            location = Location(x, y)
            self.locations[coords] = location
            
            # Updated statistics
            self.world_stats["total_locations_created"] += 1
            
            if location.properties["has_coins"]:
                self.world_stats["total_coins_generated"] += location.properties["coin_amount"]
            
            if location.properties["has_monster"]:
                self.world_stats["total_monsters_spawned"] += 1
                
            if location.items:
                self.world_stats["total_items_placed"] += len(location.items)
        
        return self.locations[coords]
    
    def get_location_info(self, x: int, y: int) -> str:
        location = self.get_or_create_location(x, y)
        coords = (x, y)
        
        info_lines = [
            f" {location.name} at ({x}, {y})",
            f"   {location.properties['description']}"
        ]
        
        # Add status information
        if coords in self.discovered_locations:
            info_lines.append("   (Discovered)")
            info_lines.append(f"   Visited: {location.properties['visited_count']} times")
        else:
            info_lines.append("    (Unknown)")
        
        # Add feature hints (without spoiling exact details)
        if location.properties["is_safe"]:
            info_lines.append("    Safe location")
        elif location.properties["has_monster"]:
            info_lines.append("    Dangerous area")
        elif location.properties["has_coins"]:
            info_lines.append("   Something valuable here...")
        
        return "\n".join(info_lines)
    
    def get_surrounding_locations(self, x: int, y: int, radius: int = 1):

        surrounding = []
        
        # Nested loop to check all positions in radius
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0:  # Skip current position
                    continue
                
                new_x, new_y = x + dx, y + dy
                surrounding.append((new_x, new_y))
        
        return surrounding
    
    def discover_location(self, x: int, y: int) -> None:
        coords = (x, y)
        if coords not in self.discovered_locations:
            self.discovered_locations.add(coords)
            location = self.get_or_create_location(x, y)
            print(f"Discovered: {location.name}")
    
    def get_world_map(self, player_x: int, player_y: int, view_radius: int = 3) -> str:
        map_lines = []
        
        map_lines.append("World Map")
        map_lines.append("=" * 20)
        
        # Generate map grid (nested loop)
        for y in range(player_y + view_radius, player_y - view_radius - 1, -1):
            line = ""
            for x in range(player_x - view_radius, player_x + view_radius + 1):
                coords = (x, y)
                
                if x == player_x and y == player_y:
                    line += "P"  # Player position
                elif coords in self.discovered_locations:
                    location = self.locations.get(coords)
                    if location:
                        if location.properties["is_safe"]:
                            line += "H"
                        elif location.properties["has_monster"]:
                            line += "M"
                        elif location.properties["has_coins"]:
                            line += "T"
                        else:
                            line += "E"
                    else:
                        line += "?"
                else:
                    line += "."  # Unknown/undiscovered
            
            map_lines.append(line)
        
        # Add legend
        map_lines.append("\nLegend:")
        map_lines.append("P=You  H=Safe  M=Danger  T=Treasure  E=Explored  ?=Unknown")
        
        return "\n".join(map_lines)
    
    def generate_random_event(self, player):
      
        #chance for random event
        if random.random() > 0.1:
            return None
        
        events = [
            {
                "type": "treasure_chest",
                "message": "You stumble upon a hidden treasure chest!",
                "coins": random.randint(20, 50),
                "items": ["Rare Gem"]
            },
            {
                "type": "wandering_merchant",
                "message": "A wandering merchant offers you a deal!",
                "coins": 0,
                "items": ["Health Potion", "Magic Bread"]
            },
            {
                "type": "mysterious_shrine",
                "message": "You find a mysterious shrine that fully heals you!",
                "healing": player.max_health
            }
        ]
        
        event = random.choice(events).copy()
        self.special_events.append(event)
        
        return event
    
    def get_world_statistics(self) -> dict:
        stats = self.world_stats.copy()
        
        # Add calculated statistics
        stats["locations_discovered"] = len(self.discovered_locations)
        stats["total_locations"] = len(self.locations)
        stats["discovery_percentage"] = (len(self.discovered_locations) / 
                                       max(1, len(self.locations))) * 100
        
        # Count current monsters and coins in world
        current_monsters = sum(1 for loc in self.locations.values() 
                             if loc.properties["has_monster"])
        current_coins = sum(loc.properties["coin_amount"] for loc in self.locations.values() 
                           if loc.properties["has_coins"])
        
        stats["current_monsters"] = current_monsters
        stats["current_coins"] = current_coins
        stats["special_events_triggered"] = len(self.special_events)
        
        return stats
