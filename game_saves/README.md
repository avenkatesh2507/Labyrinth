# Python RPG Labyrinth - Game Files

This directory contains save files for the Python RPG Labyrinth game.

## Save File Structure

- `player_data.csv`: Player character information (stats, inventory, progress)
- `world_data.csv`: World state (discovered locations, monster positions)
- `location_data.csv`: Individual location states and properties

## Important Notes

- Save files are automatically created when you save your game
- Do not manually edit these files unless you know what you're doing
- Backup your save files before major game updates
- The game supports multiple save slots (planned feature)

## Save File Format

The save files use CSV format for easy debugging and modification:

### player_data.csv
Contains player character information:
- Character name, level, experience points
- Health, mana, and other stats
- Inventory items
- Current location

### world_data.csv
Contains world state information:
- Generated world layout
- Monster spawn points
- Discovered areas

### location_data.csv
Contains individual location details:
- Room descriptions
- Available exits
- Special features
- Items found