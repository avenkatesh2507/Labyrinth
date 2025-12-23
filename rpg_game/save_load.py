import csv
import os
from datetime import datetime


class SaveLoadManager:
    """Manages saving and loading game data using CSV files.
    
    This class handles persistent storage of player data, world state,
    and game statistics using CSV format for easy data management.
    Includes error handling and directory management.
    """
    
    def __init__(self, save_directory: str = "game_saves"):
        """Initialize the save/load manager with specified directory.
        
        Args:
            save_directory (str): Directory to store save files
        """
        self.save_directory: str = save_directory
        
        # Dictionary mapping save types to filenames
        self.save_files: dict = {
            "player": "player_data.csv",
            "statistics": "game_statistics.csv", 
            "world": "world_data.csv",
            "locations": "location_data.csv"
        }
        
        # Ensure save directory exists
        self._ensure_save_directory()
    
    def _ensure_save_directory(self) -> None:
        """Create the save directory if it doesn't exist.
        
        Includes error handling with fallback to current directory.
        """
        full_path = self._get_full_path("")
        
        if not os.path.exists(full_path):
            try:
                os.makedirs(full_path)
                print(f"Created save directory: {full_path}")
            except OSError as e:
                print(f"Error creating save directory: {e}")
                # Fall back to current directory
                self.save_directory = "."
    
    def _get_full_path(self, filename: str) -> str:
        if self.save_directory == ".":
            return filename
        return os.path.join(self.save_directory, filename)
    
    def save_player_data(self, player) -> bool:
        """Save player data to CSV file with timestamp and version info.
        
        Args:
            player: Player object to save
            
        Returns:
            bool: True if save successful, False otherwise
        """
        filepath = self._get_full_path(self.save_files["player"])
        
        try:
            # Get player data as dictionary
            player_data = player.get_save_data()
            
            # Add metadata
            player_data["save_timestamp"] = datetime.now().isoformat()
            player_data["game_version"] = "1.0"
            
            # Write to CSV (file writing requirement)
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                # Get all keys for fieldnames
                fieldnames = list(player_data.keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header and data
                writer.writeheader()
                writer.writerow(player_data)
            
            print(f"Player data saved to {filepath}")
            return True
            
        except (IOError, OSError, csv.Error) as e:
            print(f"Error saving player data: {e}")
            return False
    
    def load_player_data(self, player) -> bool:
        filepath = self._get_full_path(self.save_files["player"])
        
        # Check if file exists
        if not os.path.exists(filepath):
            print("No save file found. Starting with default player data.")
            return False
        
        try:
            # Read from CSV file
            with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Get first (and should be only) row
                for row in reader:
                    player.load_save_data(row)
                    print(f"Player data loaded from {filepath}")
                    return True
                
                # If we get here, file was empty
                print("Save file is empty.")
                return False
                
        except (IOError, OSError, csv.Error, ValueError) as e:
            print(f"Error loading player data: {e}")
            return False
    
    def save_game_statistics(self, stats: dict) -> bool:
        filepath = self._get_full_path(self.save_files["statistics"])
        
        try:
            # Add session information
            session_stats = stats.copy()
            session_stats["session_timestamp"] = datetime.now().isoformat()
            
            # Determine if we're appending or creating new file
            file_exists = os.path.exists(filepath)
            mode = 'a' if file_exists else 'w'
            
            with open(filepath, mode, newline='', encoding='utf-8') as csvfile:
                fieldnames = list(session_stats.keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header only if new file
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow(session_stats)
            
            print(f"Statistics saved to {filepath}")
            return True
            
        except (IOError, OSError, csv.Error) as e:
            print(f"Error saving statistics: {e}")
            return False
    
    def load_latest_statistics(self):
        filepath = self._get_full_path(self.save_files["statistics"])
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Read all rows and get the last one (most recent)
                rows = list(reader)
                if rows:
                    return rows[-1]  # Return latest statistics
                
                return None
                
        except (IOError, OSError, csv.Error) as e:
            print(f"Error loading statistics: {e}")
            return None
    
    def save_world_data(self, world) -> bool:
        # Save world statistics
        world_stats_path = self._get_full_path(self.save_files["world"])
        locations_path = self._get_full_path(self.save_files["locations"])
        
        try:
            # Save world statistics
            world_stats = world.get_world_statistics()
            world_stats["save_timestamp"] = datetime.now().isoformat()
            
            with open(world_stats_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = list(world_stats.keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(world_stats)
            
            # Save location data (demonstrates loop with file operations)
            with open(locations_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    "x", "y", "name", "visited_count", "has_coins", "coin_amount",
                    "has_monster", "monster_type", "is_safe", "description",
                    "items", "discovered"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Write each location (loop requirement)
                for coords, location in world.locations.items():
                    x, y = coords
                    
                    row_data = {
                        "x": x,
                        "y": y,
                        "name": location.name,
                        "visited_count": location.properties["visited_count"],
                        "has_coins": location.properties["has_coins"],
                        "coin_amount": location.properties["coin_amount"],
                        "has_monster": location.properties["has_monster"],
                        "monster_type": location.properties["monster_type"] or "",
                        "is_safe": location.properties["is_safe"],
                        "description": location.properties["description"],
                        "items": "|".join(location.items),  # Join list into string
                        "discovered": coords in world.discovered_locations
                    }
                    
                    writer.writerow(row_data)
            
            print(f"World data saved to {world_stats_path} and {locations_path}")
            return True
            
        except (IOError, OSError, csv.Error) as e:
            print(f"Error saving world data: {e}")
            return False
    
    def load_world_data(self, world) -> bool:
        locations_path = self._get_full_path(self.save_files["locations"])
        
        if not os.path.exists(locations_path):
            print("No world save data found.")
            return False
        
        try:
            # Clear existing world data
            world.locations.clear()
            world.discovered_locations.clear()
            
            # Load location data
            with open(locations_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    # Parse coordinate data
                    x = int(row["x"])
                    y = int(row["y"])
                    coords = (x, y)
                    
                    # Create location
                    from game_world import Location  # Import here to avoid circular imports
                    location = Location(x, y, row["name"])
                    
                    # Set location properties (demonstrates type conversion)
                    location.properties["visited_count"] = int(row["visited_count"])
                    location.properties["has_coins"] = row["has_coins"].lower() == "true"
                    location.properties["coin_amount"] = int(row["coin_amount"])
                    location.properties["has_monster"] = row["has_monster"].lower() == "true"
                    location.properties["monster_type"] = row["monster_type"] if row["monster_type"] else None
                    location.properties["is_safe"] = row["is_safe"].lower() == "true"
                    location.properties["description"] = row["description"]
                    
                    # Parse items list
                    if row["items"]:
                        location.items = row["items"].split("|")
                    else:
                        location.items = []
                    
                    # Add to world
                    world.locations[coords] = location
                    
                    # Add to discovered if marked as discovered
                    if row["discovered"].lower() == "true":
                        world.discovered_locations.add(coords)
            
            print(f"World data loaded from {locations_path}")
            return True
            
        except (IOError, OSError, csv.Error, ValueError, KeyError) as e:
            print(f"Error loading world data: {e}")
            return False
    
    def get_all_save_files(self) -> list:
        existing_files = [
            filename for save_type, filename in self.save_files.items()
            if os.path.exists(self._get_full_path(filename))
        ]
        
        return existing_files
    
    def delete_save_data(self, save_type: str = None) -> bool:
        try:
            if save_type is None:
                # Delete all save files
                for filename in self.save_files.values():
                    filepath = self._get_full_path(filename)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        print(f"Deleted {filepath}")
                
                # Try to remove save directory if empty
                try:
                    full_dir = self._get_full_path("")
                    if full_dir != ".":
                        os.rmdir(full_dir)
                        print(f"Deleted save directory: {full_dir}")
                except OSError:
                    pass  # Directory not empty or other issue
                    
                return True
                
            elif save_type in self.save_files:
                # Delete specific save file
                filepath = self._get_full_path(self.save_files[save_type])
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"Deleted {filepath}")
                    return True
                else:
                    print(f"Save file {filepath} does not exist")
                    return False
            else:
                print(f"Unknown save type: {save_type}")
                return False
                
        except (IOError, OSError) as e:
            print(f"Error deleting save data: {e}")
            return False
    
    def backup_save_data(self) -> bool:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            for save_type, filename in self.save_files.items():
                source_path = self._get_full_path(filename)
                
                if os.path.exists(source_path):
                    # Create backup filename
                    name, ext = os.path.splitext(filename)
                    backup_filename = f"{name}_backup_{timestamp}{ext}"
                    backup_path = self._get_full_path(backup_filename)
                    
                    # Copy file content
                    with open(source_path, 'r', encoding='utf-8') as source:
                        with open(backup_path, 'w', encoding='utf-8') as backup:
                            backup.write(source.read())
                    
                    print(f"Backed up {filename} to {backup_filename}")
            
            return True
            
        except (IOError, OSError) as e:
            print(f"Error creating backup: {e}")
            return False
