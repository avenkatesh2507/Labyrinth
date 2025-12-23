# Python RPG Adventure - Labyrinth

A graphical RPG adventure game built with Python and Pygame. Navigate through a maze-like world, battle monsters, collect items, and level up your character!

## Features

- **Graphical Interface**: Beautiful 2D graphics with sprite-based rendering
- **Character Progression**: Level up, gain experience, and improve stats
- **Combat System**: Turn-based combat with various monsters
- **World Exploration**: Navigate through interconnected locations
- **Save/Load System**: Save your progress and continue later
- **Multiple Game Modes**: Both graphical and text-based interfaces

## Screenshots

![Game Screenshot](docs/screenshot.png)

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/python-rpg-labyrinth.git
cd python-rpg-labyrinth
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## How to Play

### Quick Start (Graphical Mode)
```bash
python rpg_game/start_game.py
```

### Alternative (Direct Launch)
```bash
cd rpg_game
python graphical_game.py
```

### Game Controls
- **WASD or Arrow Keys**: Move your character
- **Mouse**: Navigate menus and interact with UI
- **Enter**: Confirm selections
- **Esc**: Pause game or return to previous menu

## Game Mechanics

### Character Creation
- Enter your character's name
- Start with basic stats that improve as you level up

### Combat
- Turn-based combat system
- Choose between Attack, Defend, or Use Item
- Gain experience points for defeating monsters
- Level up to increase your stats

### Exploration
- Navigate through interconnected rooms
- Discover new areas and hidden passages
- Find items and treasures
- Encounter various monsters

### Save System
- Automatic saving after significant events
- Manual save/load through the game menu
- Multiple save slots available

## Project Structure

```
python-rpg-labyrinth/
├── rpg_game/                 # Main game directory
│   ├── graphical_game.py     # Main graphical game engine
│   ├── start_game.py         # Game launcher
│   ├── player.py             # Player class and mechanics
│   ├── monsters.py           # Monster classes and combat
│   ├── game_world.py         # World generation and locations
│   ├── graphics_engine.py    # Graphics rendering engine
│   ├── save_load.py          # Save/load system
│   ├── game.py              # Text-based game version
│   └── game_saves/          # Save game files
├── game_saves/              # Global save directory
├── docs/                    # Documentation and screenshots
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Development

### Running Tests
```bash
# Run the test suite
python rpg_game/test_suite.py

# Run integration tests
python rpg_game/test_integration.py

# Test graphics engine
python rpg_game/test_animations.py
```

### Game Architecture

The game is built with a modular architecture:

- **GraphicalRPGGame**: Main game loop and state management
- **Player**: Character stats, inventory, and progression
- **Monster/MonsterFactory**: Enemy generation and AI
- **GameWorld/Location**: World generation and navigation
- **GraphicsEngine**: Sprite rendering and UI management
- **SaveLoadManager**: Game persistence

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Pygame](https://www.pygame.org/)
- Inspired by classic RPG games
- Thanks to the Python gaming community

## Troubleshooting

### Common Issues

**Game won't start**
- Make sure Pygame is installed: `pip install pygame`
- Check Python version: `python --version` (requires 3.7+)

**Graphics issues**
- Ensure you have a compatible graphics driver
- Try running in windowed mode

**Save/Load problems**
- Check file permissions in the game_saves directory
- Ensure the game has write access to the project directory

---

*Happy adventuring! 🗡️🛡️*