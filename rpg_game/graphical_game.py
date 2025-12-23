import pygame
import pygame.freetype
import sys
import math
import random


# Import our existing game modules
from player import Player
from monsters import Monster, MonsterFactory, combat_encounter
from game_world import GameWorld, Location
from save_load import SaveLoadManager
from graphics_engine import (
    UI, Colors, PlayerSprite, MonsterSprite, LocationSprite, WallSprite,
    GameSprite, create_simple_sprites, test_graphics_engine
)


class GraphicalRPGGame:
    
    def __init__(self):
      
        # Pygame initialization
        pygame.init()
        pygame.freetype.init()
        
        # Initialize messages early so they can be used anywhere
        self.game_messages = []
        
        # Screen setup
        self.screen_width = 1024
        self.screen_height = 768
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Python RPG Adventure - Graphical Edition")
        
        # Game timing
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Game state variables
        self.running = True
        self.game_state = "character_creation"  # character_creation, menu, playing, combat, paused, game_over
        self.last_update = pygame.time.get_ticks()
        
        # Character creation
        self.character_name = ""
        self.character_name_input_active = True
        
        # Initialize game systems (will be created after character creation)
        self.player = None
        self.world = GameWorld()
        self.save_manager = SaveLoadManager()
        self.ui = UI(self.screen_width, self.screen_height)
        
        # Graphics and sprites
        self.all_sprites = pygame.sprite.Group()
        self.location_sprites = pygame.sprite.Group()
        self.monster_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()
        self.wall_sprites = pygame.sprite.Group()
        
        # Player sprite (will be created after character creation)
        self.player_sprite = None
        
        # Movement controls and timing
        self.movement_keys = {
            pygame.K_w: "north", pygame.K_UP: "north",
            pygame.K_s: "south", pygame.K_DOWN: "south", 
            pygame.K_a: "west", pygame.K_LEFT: "west",
            pygame.K_d: "east", pygame.K_RIGHT: "east"
        }
        
        # Input handling
        self.last_move_time = 0
        self.move_delay = 150  # Reduced delay for smoother movement
        
        # Camera settings
        self.camera_speed = 5  # Initialize early so methods can use it
        self.camera_x = 0
        self.camera_y = 0
        
        # Maze data
        self.maze = {}  # Dict to store wall positions
        self.coins = {}  # Dict to store coin positions
        self.monsters = {}  # Dict to store monster positions
        self.exit_door = (14, -8)  # Exit door position (top right area)
        self.total_monsters = 0  # Track total monsters for completion
        self.monsters_defeated = 0  # Track defeated monsters
        
        # Maze boundaries (based on the pattern)
        self.maze_min_x = -16
        self.maze_max_x = 15
        self.maze_min_y = -9
        self.maze_max_y = 9
        
        # Load simple sprites
        self.simple_sprites = create_simple_sprites()
        
        self._generate_simple_maze()
        self._place_coins_and_monsters()
    
    def _place_coins_and_monsters(self):
        import random
        
        # Get all reachable positions using flood fill from spawn point (0,0)
        reachable = self._get_reachable_positions((0, 0))
        
        # Filter out positions too close to spawn and exit door
        safe_positions = []
        for pos in reachable:
            x, y = pos
            # Keep away from spawn point and exit door
            if (abs(x) + abs(y) > 2 and  # Not too close to spawn
                pos != self.exit_door and  # Not on exit door
                abs(x - self.exit_door[0]) + abs(y - self.exit_door[1]) > 2):  # Not too close to exit
                safe_positions.append(pos)
        
        # Place coins only in safe reachable positions (25% of safe spaces)
        coin_count = len(safe_positions) // 4
        coin_positions = random.sample(safe_positions, min(coin_count, len(safe_positions)))
        for pos in coin_positions:
            self.coins[pos] = 10
        
        # Place monsters in remaining safe positions
        available = [pos for pos in safe_positions if pos not in self.coins]
        monster_count = min(6, len(available) // 12)  # Reduced monster count for better spacing
        monster_positions = random.sample(available, monster_count)
        
        monster_types = ["goblin", "orc", "slime", "dragon"]
        for i, pos in enumerate(monster_positions):
            self.monsters[pos] = monster_types[i % 4]
        
        self.total_monsters = len(monster_positions)
        self.monsters_defeated = 0
    
    def _get_reachable_positions(self, start):
        visited = set()
        stack = [start]
        
        while stack:
            x, y = stack.pop()
            if (x, y) in visited or (x, y) in self.maze:
                continue
            # Use actual maze boundaries
            if x < self.maze_min_x or x > self.maze_max_x or y < self.maze_min_y or y > self.maze_max_y:
                continue
                
            visited.add((x, y))
            # Add adjacent positions
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                stack.append((x+dx, y+dy))
        
        return list(visited)
    
    def _collect_coin_at_position(self, x, y):
        if (x, y) in self.coins:
            coin_value = self.coins.pop((x, y))
            self.player.coins += coin_value
            # Only add message if game_messages exists (after initialization)
            if hasattr(self, 'game_messages'):
                self.add_message(f"💰 Collected {coin_value} coins! Total: {self.player.coins}")
    
    def _check_for_monster_encounter(self, x, y):
        if (x, y) in self.monsters and self.game_state != "combat":
            monster_type = self.monsters.pop((x, y))
            from monsters import MonsterFactory
            monster = MonsterFactory.create_monster(monster_type, self.player.level)
            self.current_monster = monster
            self.game_state = "combat"
            if hasattr(self, 'game_messages'):
                self.add_message(f"⚔️ {monster.name} appears!")
    
    def _check_for_exit_door(self, x, y):
        if (x, y) == self.exit_door:
            if self.monsters_defeated >= self.total_monsters:
                self.game_state = "victory"
                if hasattr(self, 'game_messages'):
                    self.add_message("🚪 You found the exit! Congratulations!")
            else:
                remaining = self.total_monsters - self.monsters_defeated
                if hasattr(self, 'game_messages'):
                    self.add_message(f"🔒 Exit locked! Defeat {remaining} more monsters first!")
        
    def _generate_simple_maze(self):
        self.maze.clear()
        
        # Compact maze pattern with exit door area
        pattern = [
            "################################",
            "#..............##.............E#",
            "#.####.#######.##.#######.####.#",
            "#..............................#",
            "#.####.##.############.##.####.#",
            "#......##......##......##......#",
            "######.#######.##.#######.######",
            "     #.##..............##.#     ",
            "     #.##.###    ###.##.#     ",
            "######.##.#        #.##.######",
            "......##..#        #..##......",
            "######.##.#        #.##.######",
            "     #.##.##########.##.#     ",
            "     #.##..............##.#     ",
            "######.##.############.##.######",
            "#..............##.............#",
            "#.####.#######.##.#######.####.#",
            "#..............................#",
            "################################"
        ]
        
        # Convert pattern to walls (E marks exit door location)
        for y, row in enumerate(pattern):
            for x, cell in enumerate(row):
                if cell == '#':
                    self.maze[(x-16, y-9)] = True
                elif cell == 'E':
                    self.exit_door = (x-16, y-9)
    
    def _create_wall_sprites(self):
       
        self.wall_sprites.empty()
        
        # Create wall sprites for visible area around player
        if self.player:
            px, py = self.player.position
            view_range = 15  # Show walls within this range
            
            for x in range(px - view_range, px + view_range + 1):
                for y in range(py - view_range, py + view_range + 1):
                    if (x, y) in self.maze:
                        # Convert world coordinates to screen coordinates
                        screen_x = (x - px) * 32 + self.screen_width // 2 - 16
                        screen_y = (y - py) * 32 + self.screen_height // 2 - 16
                        
                        wall_sprite = WallSprite(screen_x, screen_y)
                        self.wall_sprites.add(wall_sprite)
                        self.all_sprites.add(wall_sprite)
        
    def _create_world_sprites(self):
      
        if not self.player:
            return
            
        # Create sprites for discovered locations
        grid_size = 64
        
        for coords, location in self.world.locations.items():
            x, y = coords
            
            # Determine location type based on properties
            if location.properties["is_safe"]:
                location_type = "village"
            elif abs(x) + abs(y) > 3:
                location_type = "mountain"
            elif location.name and "forest" in location.name.lower():
                location_type = "forest"
            elif location.name and "cave" in location.name.lower():
                location_type = "cave"
            else:
                location_type = "plains"
                
            location_sprite = LocationSprite(x * grid_size, y * grid_size, location_type)
            location_sprite.world_x = x
            location_sprite.world_y = y
            
            self.location_sprites.add(location_sprite)
            self.all_sprites.add(location_sprite)
    
    def _try_load_saved_game(self):
        if self.player and self.save_manager.load_player_data(self.player):
            self.save_manager.load_world_data(self.world)
            # Recalculate monster count based on current monster positions
            # (in case save/load messed up the tracking)
            current_monsters = len(self.monsters)
            if current_monsters != self.total_monsters:
                self.monsters_defeated = max(0, self.total_monsters - current_monsters)
                self.add_message(f"Monster tracking updated: {self.monsters_defeated}/{self.total_monsters}")
            self.add_message(f"Welcome back, {self.player.name}!")
            self._create_world_sprites()  # Recreate sprites with loaded data
        elif self.player:
            self.add_message(f"Welcome to the adventure, {self.player.name}!")
    
    def add_message(self, message: str):
      
        self.game_messages.append(message)
        if len(self.game_messages) > 20:  # Keep only last 20 messages
            self.game_messages.pop(0)
        
        # Show as notification too
        self.ui.show_notification(message)
    
    def run(self):

        while self.running:
            # Handle events
            self._handle_events()
            
            # Update game state
            self._update()
            
            # Render everything
            self._render()
            
            # Control frame rate
            self.clock.tick(self.fps)
        
        # Cleanup
        self._cleanup()
    
    def _handle_events(self):
       # Handle all Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
                
            elif event.type == pygame.KEYUP:
                self._handle_keyup(event)
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(event)
    
    def _handle_keydown(self, event):
        if self.game_state == "character_creation":
            if event.key == pygame.K_RETURN:
                if len(self.character_name.strip()) > 0:
                    self._finish_character_creation()
                else:
                    self.add_message("Please enter a character name!")
            elif event.key == pygame.K_BACKSPACE:
                self.character_name = self.character_name[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.unicode.isprintable() and len(self.character_name) < 20:
                self.character_name += event.unicode
                
        elif self.game_state == "menu":
            if event.key == pygame.K_RETURN:
                self.game_state = "playing"
                self.add_message("Game started! Use WASD or arrow keys to move.")
            elif event.key == pygame.K_ESCAPE:
                self.running = False
                
        elif self.game_state == "playing":
            # Movement handled in update loop for smooth movement
            if event.key == pygame.K_ESCAPE:
                self.game_state = "paused"
            elif event.key == pygame.K_i:
                self._show_inventory()
            elif event.key == pygame.K_m:
                self._show_map()
            elif event.key == pygame.K_h:
                self._show_help()
            elif event.key == pygame.K_SPACE:
                self._interact_with_location()
            elif event.key >= pygame.K_1 and event.key <= pygame.K_9:
                item_index = event.key - pygame.K_1
                self._use_inventory_item(item_index)
                
        elif self.game_state == "combat":
            if event.key == pygame.K_1:
                self._combat_attack()
            elif event.key == pygame.K_2:
                self._combat_use_item()
            elif event.key == pygame.K_ESCAPE:
                # Quick exit from combat
                self.game_state = "playing"
                self.current_monster = None
                
        elif self.game_state == "paused":
            if event.key == pygame.K_ESCAPE:
                self.game_state = "playing"
            elif event.key == pygame.K_s:
                self._save_game()
            elif event.key == pygame.K_q:
                self.running = False
                
        elif self.game_state == "victory":
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.running = False
            elif event.key == pygame.K_r:
                # Restart game
                self.__init__()
                
        elif self.game_state == "victory":
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.running = False
            elif event.key == pygame.K_r:
                # Restart game
                self.__init__()
    
    def _finish_character_creation(self):
        # Complete character creation and start the game
        # Create player with chosen name
        self.player = Player(self.character_name.strip())
        
        # Create player sprite
        self.player_sprite = PlayerSprite(0, 0)
        self.all_sprites.add(self.player_sprite)
        
        # Initialize world sprites
        self._create_world_sprites()
        self._create_wall_sprites()
        
        # Try to load saved game
        self._try_load_saved_game()
        
        # Move to menu state
        self.game_state = "menu"
        self.add_message(f"Welcome to the maze adventure, {self.player.name}!")
    
    def _handle_keyup(self, event):
       
        pass  # No longer needed with direct key checking
    
    def _handle_mouse_click(self, event):
        # Handle mouse click events
        if self.game_state == "playing":
            # Convert mouse position to world coordinates
            mouse_x, mouse_y = event.pos
            
            # Adjust for game area (account for sidebar)
            if mouse_x < self.ui.game_area_width:
                world_x = (mouse_x - self.ui.game_area_width // 2 + self.camera_x) // 64
                world_y = (mouse_y - self.ui.game_area_height // 2 + self.camera_y) // 64
                
                # Move player towards clicked location
                self._move_towards(world_x, world_y)
    
    def _update(self):
        current_time = pygame.time.get_ticks()
        
        if self.game_state == "playing" and self.player:
            # Handle continuous movement
            self._handle_movement(current_time)
            
            # Update sprites
            self.all_sprites.update()
            
            # Update camera to follow player
            self._update_camera()
            
            # Check for location events
            self._check_location_events()
            
        elif self.game_state == "combat" and self.current_monster:
            # Update combat animations
            pass
        
        # Update UI animations
        self.ui.update_animations()
        
        self.last_update = current_time
    
    def _handle_movement(self, current_time):
        if current_time - self.last_move_time < self.move_delay:
            return
            
        moved = False
        
        # Get current key states
        keys = pygame.key.get_pressed()
        
        # Check WASD and arrow keys directly
        direction = None
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction = "north"
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction = "south"
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction = "west"
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction = "east"
        
        if direction:
            old_pos = self.player.position
            
            # Calculate target position
            target_x, target_y = old_pos
            if direction == "north":
                target_y -= 1
            elif direction == "south":
                target_y += 1
            elif direction == "east":
                target_x += 1
            elif direction == "west":
                target_x -= 1
            
            # Check for wall collision and boundaries
            if ((target_x, target_y) not in self.maze and 
                self.maze_min_x <= target_x <= self.maze_max_x and 
                self.maze_min_y <= target_y <= self.maze_max_y):
                # Move is valid, update player position
                self.player.position = (target_x, target_y)
                
                # Collect coin if there's one at this position
                self._collect_coin_at_position(target_x, target_y)
                
                # Update player sprite animation and position
                if self.player_sprite:
                    self.player_sprite.set_direction(direction)
                    self.player_sprite._update_sprite_image()
                    # Update sprite position to match player's logical position
                    self.player_sprite.world_x = target_x
                    self.player_sprite.world_y = target_y
                
                moved = True
                self.last_move_time = current_time
                
                # Only show important messages, not every movement
                
                # Check for monster encounters
                self._check_for_monster_encounter(target_x, target_y)
                self._check_for_exit_door(target_x, target_y)
            else:
                # Hit a wall - just change sprite direction, no message spam
                if self.player_sprite:
                    self.player_sprite.set_direction(direction)
        
        # Stop walking animation if no movement
        if not moved and self.player_sprite:
            self.player_sprite.stop_walking()
    
    def _update_camera(self):
        target_x, target_y = self.player.position[0] * 64, self.player.position[1] * 64
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1
    
    def _check_location_events(self):
        px, py = self.player.position
        location = self.world.get_or_create_location(px, py)
        
        if hasattr(location, '_last_visit') and location._last_visit == (px, py):
            return
            
        location._last_visit = (px, py)
        visit_result = location.visit()
        
        if visit_result["coins_found"] > 0:
            self.player.collect_coins(visit_result["coins_found"])
            self.add_message(f"Found {visit_result['coins_found']} coins!")
        
        for item in visit_result["items_found"]:
            self.player.add_to_inventory(item)
            self.add_message(f"Found {item}!")
    
    def _interact_with_location(self):
        px, py = self.player.position
        location = self.world.get_or_create_location(px, py)
        self.add_message(f"You examine {location.name}:")
        self.add_message(location.properties["description"])
    
    def _show_inventory(self):
        items = ", ".join(self.player.inventory) if self.player.inventory else "empty"
        self.add_message(f"Inventory: {items}")
    
    def _show_map(self):
        px, py = self.player.position
        self.add_message(f"Position: ({px}, {py}), Discovered: {len(self.world.discovered_locations)}")
    
    def _show_help(self):
        help_msg = "WASD: Move | Space: Examine | I: Inventory | M: Map | H: Help | 1-9: Use item | ESC: Pause"
        self.add_message(help_msg)
    
    def _use_inventory_item(self, index: int):
        if 0 <= index < len(self.player.inventory):
            item = self.player.inventory[index]
            if self.player.use_item(item):
                self.add_message(f"Used {item}")
            else:
                self.add_message(f"Cannot use {item}")
        else:
            self.add_message("Invalid item number")
    
    def _combat_attack(self):
        if not self.current_monster:
            return
        
        # Balanced damage calculation - base damage plus small random variation
        base_damage = min(15, max(8, self.player.level // 2 + 5))  # Scale with level but cap it
        damage = base_damage + random.randint(-3, 3)
        damage = max(1, damage)  # Ensure at least 1 damage
        
        self.current_monster.take_damage(damage)
        self.add_message(f"You attack for {damage} damage!")
        
        if not self.current_monster.is_alive:
            self.monsters_defeated += 1
            self.add_message(f"💀 {self.current_monster.name} has been defeated!")
            self.add_message(f"Monsters defeated: {self.monsters_defeated}/{self.total_monsters}")
            self.player.collect_coins(self.current_monster.coins_reward)
            self.current_monster = None
            self.game_state = "playing"  # Exit combat immediately
            return
        
        # Monster attacks back
        monster_damage = self.current_monster.attack_player()
        self.player.take_damage(monster_damage)
        
        if not self.player.is_alive:
            self.game_state = "game_over"
    
    def _combat_use_item(self):
     
        if self.player.inventory:
            # Use first healing item found
            for item in self.player.inventory:
                if "potion" in item.lower() or "bread" in item.lower():
                    if self.player.use_item(item):
                        self.add_message(f"Used {item} in combat!")
                        return
            self.add_message("No usable items in inventory!")
        else:
            self.add_message("No items in inventory!")
    
    def _save_game(self):
        
        if self.save_manager.save_player_data(self.player):
            self.save_manager.save_world_data(self.world)
            self.add_message("Game saved successfully!")
        else:
            self.add_message("Failed to save game!")
    
    def _render(self):
        # Clear screen
        self.screen.fill(Colors.BLACK)
        
        if self.game_state == "character_creation":
            self._render_character_creation()
        elif self.game_state == "menu":
            self._render_menu()
        elif self.game_state == "playing":
            self._render_game()
        elif self.game_state == "combat":
            self._render_combat()
        elif self.game_state == "paused":
            self._render_pause_menu()
        elif self.game_state == "victory":
            self._render_victory()
        elif self.game_state == "game_over":
            self._render_game_over()
        
        # Always render notifications
        self.ui.draw_notifications(self.screen)
        
        # Update display
        pygame.display.flip()
    
    def _render_character_creation(self):
        title_font = pygame.freetype.Font(None, 48)
        input_font = pygame.freetype.Font(None, 28)
        
        self.screen.fill((30, 30, 50))
        
        # Title and input
        title_surface, title_rect = title_font.render("🧙 Character Creation 🧙", Colors.GOLD)
        title_rect.center = (self.screen_width // 2, 150)
        self.screen.blit(title_surface, title_rect)
        
        # Name input
        input_rect = pygame.Rect((self.screen_width - 400) // 2, 280, 400, 50)
        pygame.draw.rect(self.screen, Colors.WHITE, input_rect)
        pygame.draw.rect(self.screen, Colors.BLUE, input_rect, 3)
        
        display_name = self.character_name + ("|") if (pygame.time.get_ticks() // 500) % 2 and self.character_name_input_active else self.character_name
        name_surface, name_rect = input_font.render(display_name, Colors.BLACK)
        name_rect.left = input_rect.x + 10
        name_rect.centery = input_rect.centery
        self.screen.blit(name_surface, name_rect)
        
        # Instructions
        instruction = "Type your name and press ENTER to start, ESC to quit"
        text_surface, text_rect = input_font.render(instruction, Colors.WHITE)
        text_rect.center = (self.screen_width // 2, 400)
        self.screen.blit(text_surface, text_rect)
    
    def _render_menu(self):
        title_font = pygame.freetype.Font(None, 48)
        menu_font = pygame.freetype.Font(None, 24)
        
        self.screen.fill(Colors.BLACK)
        
        title_surface, title_rect = title_font.render("🎮 Python RPG Adventure 🎮", Colors.GOLD)
        title_rect.center = (self.screen_width // 2, 200)
        self.screen.blit(title_surface, title_rect)
        
        instructions = "ENTER: Play | ESC: Quit | WASD: Move | Space: Interact"
        text_surface, text_rect = menu_font.render(instructions, Colors.WHITE)
        text_rect.center = (self.screen_width // 2, 350)
        self.screen.blit(text_surface, text_rect)
    
    def _render_game(self):
        # Fill game area with dark background like Pacman
        game_surface = pygame.Surface((self.ui.game_area_width, self.ui.game_area_height))
        game_surface.fill(Colors.BLACK)
        
        # Always position player in center of screen
        player_screen_x = self.ui.game_area_width // 2 - 16
        player_screen_y = self.ui.game_area_height // 2 - 16
        
        # Calculate world offset based on player position
        if self.player:
            px, py = self.player.position
            world_offset_x = player_screen_x - px * 32
            world_offset_y = player_screen_y - py * 32
        else:
            world_offset_x = world_offset_y = 0
            px, py = 0, 0
        
        # Draw maze walls
        tile_size = 32
        for (wx, wy) in self.maze:
            screen_x = wx * tile_size + world_offset_x
            screen_y = wy * tile_size + world_offset_y
            
            # Only draw walls that are visible
            if (-tile_size <= screen_x <= self.ui.game_area_width and 
                -tile_size <= screen_y <= self.ui.game_area_height):
                # Draw wall as blue rectangle (Pacman style)
                wall_rect = pygame.Rect(screen_x, screen_y, tile_size, tile_size)
                pygame.draw.rect(game_surface, Colors.BLUE, wall_rect)
                pygame.draw.rect(game_surface, Colors.LIGHT_BLUE, wall_rect, 2)
        
        # Draw dots and coins on empty spaces
        view_range = 15
        for x in range(px - view_range, px + view_range + 1):
            for y in range(py - view_range, py + view_range + 1):
                if (x, y) not in self.maze:  # Empty space
                    screen_x = x * tile_size + world_offset_x + tile_size//2
                    screen_y = y * tile_size + world_offset_y + tile_size//2
                    
                    if (0 <= screen_x <= self.ui.game_area_width and 
                        0 <= screen_y <= self.ui.game_area_height):
                        
                        # Draw coin if there's one here
                        if (x, y) in self.coins:
                            pygame.draw.circle(game_surface, Colors.GOLD, 
                                             (int(screen_x), int(screen_y)), 4)
                            pygame.draw.circle(game_surface, Colors.YELLOW, 
                                             (int(screen_x), int(screen_y)), 2)
                        else:
                            # Draw small pellet dot
                            pygame.draw.circle(game_surface, Colors.YELLOW, 
                                             (int(screen_x), int(screen_y)), 1)
        
        # Draw exit door
        if self.exit_door:
            ex, ey = self.exit_door
            door_screen_x = ex * tile_size + world_offset_x
            door_screen_y = ey * tile_size + world_offset_y
            if (-tile_size <= door_screen_x <= self.ui.game_area_width and 
                -tile_size <= door_screen_y <= self.ui.game_area_height):
                # Check if door is unlocked (all monsters defeated)
                door_unlocked = self.monsters_defeated >= self.total_monsters
                
                if door_unlocked:
                    # Draw exit door as green glowing rectangle (unlocked)
                    door_rect = pygame.Rect(door_screen_x, door_screen_y, tile_size, tile_size)
                    pygame.draw.rect(game_surface, (0, 255, 0), door_rect)
                    pygame.draw.rect(game_surface, (0, 200, 0), door_rect, 3)
                else:
                    # Draw exit door as red locked rectangle
                    door_rect = pygame.Rect(door_screen_x, door_screen_y, tile_size, tile_size)
                    pygame.draw.rect(game_surface, (200, 0, 0), door_rect)
                    pygame.draw.rect(game_surface, (150, 0, 0), door_rect, 3)
                
                # Add door symbol
                center_x = door_screen_x + tile_size // 2
                center_y = door_screen_y + tile_size // 2
                pygame.draw.rect(game_surface, (255, 255, 255), 
                               (center_x - 8, center_y - 10, 16, 20))
                pygame.draw.circle(game_surface, (0, 0, 0), (center_x + 5, center_y), 2)
                
                # Add lock symbol if locked
                if not door_unlocked:
                    pygame.draw.rect(game_surface, (255, 255, 0), 
                                   (center_x - 4, center_y - 6, 8, 8))
                    pygame.draw.rect(game_surface, (255, 215, 0), 
                                   (center_x - 4, center_y - 6, 8, 8), 2)
        
        # Draw monsters
        for (mx, my), monster_type in self.monsters.items():
            monster_screen_x = mx * tile_size + world_offset_x
            monster_screen_y = my * tile_size + world_offset_y
            
            if (-tile_size <= monster_screen_x <= self.ui.game_area_width and 
                -tile_size <= monster_screen_y <= self.ui.game_area_height):
                
                # Create temporary monster sprite to display
                temp_sprite = MonsterSprite(monster_screen_x, monster_screen_y, monster_type)
                game_surface.blit(temp_sprite.image, (monster_screen_x, monster_screen_y))
                
                # Add bright outline around monster
                pygame.draw.rect(game_surface, Colors.RED, 
                               (monster_screen_x-1, monster_screen_y-1, 34, 34), 2)
        
        # Draw player sprite in center (always visible)
        if self.player_sprite:
            game_surface.blit(self.player_sprite.image, (player_screen_x, player_screen_y))
            
            # Add a bright outline around player to make it more visible
            pygame.draw.rect(game_surface, Colors.WHITE, 
                           (player_screen_x-1, player_screen_y-1, 34, 34), 2)
        
        self.screen.blit(game_surface, (0, 0))
        
        # Render sidebar
        sidebar_surface = self.ui.draw_sidebar(self.player)
        self.screen.blit(sidebar_surface, (self.ui.game_area_width, 0))
        
        # Render bottom panel with player position and coin count
        current_location_name = f"🏰 Warrior at ({px}, {py}) | 💰 Coins: {self.player.coins}"
        bottom_surface = self.ui.draw_bottom_panel(self.game_messages, current_location_name)
        self.screen.blit(bottom_surface, (0, self.ui.game_area_height))
    
    def _render_combat(self):
        # Render game background
        self._render_game()
        
        # Render combat overlay
        if self.current_monster:
            self.ui.draw_combat_overlay(self.screen, self.player, self.current_monster)
    
    def _render_pause_menu(self):
        # Render game background (dimmed)
        self._render_game()
        
        # Overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Pause menu
        font = pygame.freetype.Font(None, 36)
        
        title_surface, title_rect = font.render("PAUSED", Colors.YELLOW)
        title_rect.center = (self.screen_width // 2, 300)
        self.screen.blit(title_surface, title_rect)
        
        instructions = [
            "ESC - Resume game",
            "S - Save game",
            "Q - Quit to desktop"
        ]
        
        y_offset = 350
        for instruction in instructions:
            text_surface, text_rect = font.render(instruction, Colors.WHITE)
            text_rect.center = (self.screen_width // 2, y_offset)
            self.screen.blit(text_surface, text_rect)
            y_offset += 40
    
    def _render_victory(self):
        self.screen.fill((0, 20, 0))  # Dark green background
        
        font_large = pygame.freetype.Font(None, 64)
        font_medium = pygame.freetype.Font(None, 32)
        font_small = pygame.freetype.Font(None, 24)
        
        # Victory title with animation
        title_color = (255, 255, 100) if (pygame.time.get_ticks() // 300) % 2 else (255, 215, 0)
        title_surface, title_rect = font_large.render("🎉 VICTORY! 🎉", title_color)
        title_rect.center = (self.screen_width // 2, 150)
        self.screen.blit(title_surface, title_rect)
        
        # Congratulatory message
        msg_surface, msg_rect = font_medium.render("You escaped the labyrinth!", Colors.WHITE)
        msg_rect.center = (self.screen_width // 2, 220)
        self.screen.blit(msg_surface, msg_rect)
        
        # Final statistics
        if self.player:
            stats = [
                f"Hero: {self.player.name}",
                f"Final Level: {self.player.level}",
                f"Coins Collected: {self.player.coins}",
                f"Locations Explored: {len(self.player.visited_locations)}",
                "",
                "🏆 Achievement Unlocked: Maze Master! 🏆",
                "",
                "SPACE/ENTER: Exit Game",
                "R: Restart Adventure"
            ]
        else:
            stats = ["Game completed!", "", "SPACE/ENTER: Exit Game"]
        
        y_offset = 300
        for stat in stats:
            if stat:
                color = Colors.GOLD if "Achievement" in stat else Colors.WHITE
                text_surface, text_rect = font_small.render(stat, color)
                text_rect.center = (self.screen_width // 2, y_offset)
                self.screen.blit(text_surface, text_rect)
            y_offset += 30
    
    def _render_game_over(self):
        self.screen.fill(Colors.BLACK)
        
        font_large = pygame.freetype.Font(None, 48)
        font_medium = pygame.freetype.Font(None, 24)
        
        # Game Over title
        title_surface, title_rect = font_large.render("💀 GAME OVER 💀", Colors.RED)
        title_rect.center = (self.screen_width // 2, 200)
        self.screen.blit(title_surface, title_rect)
        
        # Statistics
        stats = [
            f"Character: {self.player.name}",
            f"Level Reached: {self.player.level}",
            f"Coins Collected: {self.player.coins}",
            f"Locations Visited: {len(self.player.visited_locations)}",
            "",
            "Press ESC to quit"
        ]
        
        y_offset = 300
        for stat in stats:
            if stat:  # Skip empty lines
                text_surface, text_rect = font_medium.render(stat, Colors.WHITE)
                text_rect.center = (self.screen_width // 2, y_offset)
                self.screen.blit(text_surface, text_rect)
            y_offset += 30
    
    def _cleanup(self):
        # Auto-save before quitting
        if self.player.is_alive and self.game_state != "game_over":
            self._save_game()
        
        pygame.quit()


def main():
    try:
        # Test graphics engine first
        print("Initializing graphics system...")
        test_graphics_engine()
        
        # Create and run the game
        print("Starting graphical RPG game...")
        game = GraphicalRPGGame()
        game.run()
        
    except pygame.error as e:
        print(f"Pygame error: {e}")
        print("Make sure Pygame is properly installed: pip install pygame")
    except Exception as e:
        print(f"Game error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure Pygame shuts down cleanly
        if pygame.get_init():
            pygame.quit()


def quick_demo():
    print("🎮 Pygame RPG Demo 🎮")
    print("=" * 30)
    
    try:
        pygame.init()
        print("✓ Pygame initialized successfully")
        
        screen = pygame.display.set_mode((800, 600))
        print("✓ Display surface created")
        
        player_sprite = PlayerSprite(100, 100)
        print("✓ Player sprite created")
        
        ui = UI(800, 600)
        print("✓ UI system initialized")
        
        pygame.quit()
        print("✓ Pygame shutdown cleanly")
        
        print("\nAll graphics systems working! 🎉")
        print("Run the main game with: python graphical_game.py")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            quick_demo()
        elif sys.argv[1] == "test":
            test_graphics_engine()
        else:
            print("Usage:")
            print("  python graphical_game.py       - Run the game")
            print("  python graphical_game.py demo  - Run quick demo")
            print("  python graphical_game.py test  - Run graphics tests")
    else:
        main()