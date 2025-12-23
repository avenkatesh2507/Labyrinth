#!/usr/bin/env python3
"""Game launcher for Python RPG Adventure.

This is the main entry point for the game. It handles:
- Python path configuration
- Pygame dependency checking
- Error handling for common startup issues
- Clean game initialization

Run this file to start the game: python3 start_game.py
"""

import sys
import os

# Add the game directory to Python path
sys.path.insert(0, '/Users/aparnavenkatesh/Desktop/Labyrinth/rpg_game')

def main():
    """Main entry point - initialize and start the game."""
    try:
        from graphical_game import main as run_game
        print("Starting Python RPG Adventure...")
        run_game()
    except ImportError as e:
        print(f"Error importing game: {e}")
        print("Make sure Pygame is installed: pip install pygame")
    except Exception as e:
        print(f"Error starting game: {e}")

if __name__ == "__main__":
    main()