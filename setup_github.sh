#!/bin/bash

# GitHub Repository Creation Helper Script
# This script helps you create a GitHub repository and push your RPG game

echo "🎮 Python RPG Labyrinth - GitHub Repository Setup"
echo "=================================================="
echo

# Check if we're in the right directory
if [[ ! -f "demo.py" || ! -d "rpg_game" ]]; then
    echo "❌ Error: Please run this script from the Labyrinth project directory"
    exit 1
fi

echo "📋 Pre-flight checks:"

# Check git status
if git status &>/dev/null; then
    echo "✓ Git repository initialized"
else
    echo "❌ Git repository not found"
    exit 1
fi

# Check if commits exist
if git log --oneline &>/dev/null; then
    echo "✓ Git commits found"
    echo "  Latest commit: $(git log -1 --oneline)"
else
    echo "❌ No commits found"
    exit 1
fi

echo

echo "🚀 To create your GitHub repository, follow these steps:"
echo

echo "1. Go to https://github.com/new"
echo "2. Repository name: python-rpg-labyrinth"
echo "3. Description: A graphical RPG adventure game built with Python and Pygame"
echo "4. Set as Public repository"
echo "5. Do NOT initialize with README, .gitignore, or license (we already have these)"
echo "6. Click 'Create repository'"
echo

echo "7. After creating the repository, run these commands:"
echo
echo "   git remote add origin https://github.com/YOUR_USERNAME/python-rpg-labyrinth.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo

echo "Replace 'YOUR_USERNAME' with your actual GitHub username."
echo

echo "📊 Repository contents that will be uploaded:"
git ls-files | head -20
total_files=$(git ls-files | wc -l)
echo "   ... and $((total_files - 20)) more files"
echo

echo "🎯 After pushing to GitHub, your repository will include:"
echo "   ✓ Complete RPG game with graphics"
echo "   ✓ Working demo script (python demo.py)"
echo "   ✓ Installation instructions"
echo "   ✓ Comprehensive documentation"
echo "   ✓ License and contribution guidelines"
echo

echo "💡 To showcase your working model:"
echo "   1. Run the demo: python demo.py"
echo "   2. Start the game: python rpg_game/start_game.py"
echo "   3. Add screenshots to docs/screenshot.png"
echo

echo "Press Enter to continue with manual setup, or Ctrl+C to exit"
read -r

echo "Opening GitHub in your default browser..."
open "https://github.com/new" 2>/dev/null || echo "Please manually navigate to: https://github.com/new"

echo
echo "✨ Repository setup helper completed!"
echo "Follow the steps above to create and upload your repository."