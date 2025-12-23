"""Graphics Engine Module for Python RPG Adventure.

This module handles all visual rendering for the game including:
- Sprite management and animation
- User interface rendering  
- Color definitions and theming
- Combat overlay and effects
- Menu and screen transitions

The graphics system is built on Pygame and provides a clean interface
for the main game loop to render all visual elements.
"""

import pygame
import pygame.freetype
import math
import os
from enum import Enum


class Colors:
    """Centralized color definitions for consistent theming throughout the game."""
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    CYAN = (0, 255, 255)
    PINK = (255, 192, 203)
    BROWN = (139, 69, 19)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (211, 211, 211)
    DARK_GRAY = (64, 64, 64)
    GOLD = (255, 215, 0)
    SILVER = (192, 192, 192)
    LIGHT_BLUE = (173, 216, 230)
    
    # Game-specific colors
    GRASS_GREEN = (34, 139, 34)
    DIRT_BROWN = (160, 82, 45)
    WATER_BLUE = (65, 105, 225)
    
    # Maze specific colors
    WALL = (64, 64, 64)        # Dark gray walls
    FLOOR = (240, 240, 240)    # Light gray floor
    PLAYER_BLUE = (0, 128, 255)     # Blue player
    MONSTER_RED = (255, 64, 64)    # Red monsters
    MONSTER_GREEN = (64, 255, 64)  # Green monsters
    MONSTER_PURPLE = (128, 64, 255) # Purple monsters
    STONE_GRAY = (105, 105, 105)
    FOREST_GREEN = (0, 100, 0)
    MOUNTAIN_BROWN = (139, 90, 43)
    HEALTH_RED = (220, 20, 60)
    MANA_BLUE = (30, 144, 255)
    XP_PURPLE = (138, 43, 226)


class GameSprite(pygame.sprite.Sprite):
    """Base sprite class for all game objects.
    
    Provides common functionality for position management, rendering,
    and sprite group integration. All game sprites inherit from this class.
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, color):
        """Initialize a basic game sprite.
        
        Args:
            x, y (int): Screen position coordinates
            width, height (int): Sprite dimensions
            color: RGB color tuple for sprite fill
        """
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Animation properties
        self.animation_frame = 0.0
        self.animation_speed = 0.15
        self.last_update = pygame.time.get_ticks()
        self.frame_count = 4  # Number of animation frames
        
        # Movement properties for smooth animation
        self.target_x = x
        self.target_y = y
        self.move_speed = 8.0
        self.is_moving = False
        
        # Game properties
        self.world_x = x
        self.world_y = y
    
    def update(self):
        now = pygame.time.get_ticks()
        dt = now - self.last_update
        
        if dt > 16:  # Update at ~60 FPS (16ms per frame)
            # Update animation frame
            self.animation_frame += self.animation_speed
            if self.animation_frame >= self.frame_count:
                self.animation_frame = 0.0
            
            # Smooth movement towards target
            if self.is_moving:
                dx = self.target_x - self.rect.x
                dy = self.target_y - self.rect.y
                distance = (dx * dx + dy * dy) ** 0.5
                
                if distance > 2:  # Still moving
                    move_amount = min(self.move_speed, distance)
                    if distance > 0:
                        self.rect.x += int((dx / distance) * move_amount)
                        self.rect.y += int((dy / distance) * move_amount)
                else:
                    # Snap to target and stop moving
                    self.rect.x = self.target_x
                    self.rect.y = self.target_y
                    self.is_moving = False
            
            self.last_update = now
    
    def draw_text_on_sprite(self, text: str, font, color):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.image.blit(text_surface, (text_rect.x - self.rect.x, text_rect.y - self.rect.y))


class PlayerSprite(GameSprite):
    
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 32, 32, Colors.BLACK)
        
        # Animation properties
        self.direction = "down"
        self.walking = False
        self.animation_frames = {}
        self._create_animation_frames()
        self._update_sprite_image()
   
    def _create_animation_frames(self):
        # Create frames for each direction and animation state
        for direction in ["up", "down", "left", "right"]:
            self.animation_frames[direction] = []
            for frame in range(4):  # 4 animation frames
                frame_surface = pygame.Surface((32, 32))
                frame_surface.set_colorkey(Colors.BLACK)  # Transparent background
                
                # Create detailed warrior character
                center_x, center_y = 16, 16
                
                # Base body position with walking animation
                body_offset = 0
                if self.walking:
                    body_offset = (frame % 2) * 1 - 0.5  # Subtle bobbing
                
                # Draw character based on direction
                if direction == "down":  # Facing player
                    # Head (flesh color)
                    pygame.draw.circle(frame_surface, (255, 220, 177), (center_x, 8), 6)
                    # Hair (brown)
                    pygame.draw.arc(frame_surface, (139, 69, 19), (10, 2, 12, 8), 0, 3.14159, 2)
                    # Eyes
                    pygame.draw.circle(frame_surface, Colors.BLACK, (13, 7), 1)
                    pygame.draw.circle(frame_surface, Colors.BLACK, (19, 7), 1)
                    
                    # Body (blue tunic)
                    body_y = 15 + int(body_offset)
                    pygame.draw.rect(frame_surface, (0, 100, 200), (12, body_y, 8, 12))
                    # Armor chest plate (silver)
                    pygame.draw.rect(frame_surface, Colors.SILVER, (13, body_y, 6, 8))
                    
                    # Arms
                    arm_y = 17 + int(body_offset)
                    pygame.draw.rect(frame_surface, (255, 220, 177), (9, arm_y, 3, 8))   # Left arm
                    pygame.draw.rect(frame_surface, (255, 220, 177), (20, arm_y, 3, 8))  # Right arm
                    
                    # Legs with walking animation
                    leg_y = 27 + int(body_offset)
                    if self.walking:
                        leg_offset = (frame % 2) * 2 - 1
                        pygame.draw.rect(frame_surface, (139, 69, 19), (13, leg_y + leg_offset, 2, 5))  # Left leg
                        pygame.draw.rect(frame_surface, (139, 69, 19), (17, leg_y - leg_offset, 2, 5))  # Right leg
                    else:
                        pygame.draw.rect(frame_surface, (139, 69, 19), (13, leg_y, 2, 5))  # Left leg
                        pygame.draw.rect(frame_surface, (139, 69, 19), (17, leg_y, 2, 5))  # Right leg
                    
                    # Sword (held in right hand)
                    pygame.draw.rect(frame_surface, Colors.GRAY, (21, arm_y - 2, 2, 10))
                    pygame.draw.rect(frame_surface, Colors.GOLD, (20, arm_y - 3, 4, 2))  # Hilt
                    
                elif direction == "up":  # Back view
                    # Head (flesh color)
                    pygame.draw.circle(frame_surface, (255, 220, 177), (center_x, 8), 6)
                    # Hair (brown) - back of head
                    pygame.draw.circle(frame_surface, (139, 69, 19), (center_x, 7), 7, 2)
                    
                    # Body (blue tunic)
                    body_y = 15 + int(body_offset)
                    pygame.draw.rect(frame_surface, (0, 100, 200), (12, body_y, 8, 12))
                    # Back armor
                    pygame.draw.rect(frame_surface, Colors.DARK_GRAY, (13, body_y, 6, 8))
                    
                    # Arms (showing back)
                    arm_y = 17 + int(body_offset)
                    pygame.draw.rect(frame_surface, (255, 220, 177), (9, arm_y, 3, 8))   # Left arm
                    pygame.draw.rect(frame_surface, (255, 220, 177), (20, arm_y, 3, 8))  # Right arm
                    
                    # Legs
                    leg_y = 27 + int(body_offset)
                    if self.walking:
                        leg_offset = (frame % 2) * 2 - 1
                        pygame.draw.rect(frame_surface, (139, 69, 19), (13, leg_y - leg_offset, 2, 5))
                        pygame.draw.rect(frame_surface, (139, 69, 19), (17, leg_y + leg_offset, 2, 5))
                    else:
                        pygame.draw.rect(frame_surface, (139, 69, 19), (13, leg_y, 2, 5))
                        pygame.draw.rect(frame_surface, (139, 69, 19), (17, leg_y, 2, 5))
                    
                    # Shield on back
                    pygame.draw.ellipse(frame_surface, Colors.BROWN, (7, body_y + 2, 4, 6))
                    
                elif direction == "left":  # Side view facing left
                    # Head profile
                    pygame.draw.circle(frame_surface, (255, 220, 177), (center_x, 8), 6)
                    # Hair
                    pygame.draw.arc(frame_surface, (139, 69, 19), (10, 2, 12, 8), 0, 3.14159, 2)
                    # Eye
                    pygame.draw.circle(frame_surface, Colors.BLACK, (13, 7), 1)
                    
                    # Body side view
                    body_y = 15 + int(body_offset)
                    pygame.draw.rect(frame_surface, (0, 100, 200), (12, body_y, 8, 12))
                    pygame.draw.rect(frame_surface, Colors.SILVER, (11, body_y, 4, 8))  # Side armor
                    
                    # Arms (left side showing)
                    arm_y = 17 + int(body_offset)
                    pygame.draw.rect(frame_surface, (255, 220, 177), (8, arm_y, 6, 4))  # Visible arm
                    
                    # Legs side view with walking
                    leg_y = 27 + int(body_offset)
                    if self.walking:
                        leg_offset = (frame % 2) * 3 - 1
                        pygame.draw.rect(frame_surface, (139, 69, 19), (12 + leg_offset, leg_y, 3, 5))  # Front leg
                        pygame.draw.rect(frame_surface, (139, 69, 19), (15 - leg_offset, leg_y, 3, 5))  # Back leg
                    else:
                        pygame.draw.rect(frame_surface, (139, 69, 19), (12, leg_y, 3, 5))
                        pygame.draw.rect(frame_surface, (139, 69, 19), (15, leg_y, 3, 5))
                    
                    # Sword pointing forward
                    pygame.draw.rect(frame_surface, Colors.GRAY, (4, arm_y, 8, 2))
                    pygame.draw.rect(frame_surface, Colors.GOLD, (3, arm_y - 1, 2, 4))  # Hilt
                    
                else:  # right
                    # Head profile (facing right)
                    pygame.draw.circle(frame_surface, (255, 220, 177), (center_x, 8), 6)
                    # Hair
                    pygame.draw.arc(frame_surface, (139, 69, 19), (10, 2, 12, 8), 0, 3.14159, 2)
                    # Eye
                    pygame.draw.circle(frame_surface, Colors.BLACK, (19, 7), 1)
                    
                    # Body side view
                    body_y = 15 + int(body_offset)
                    pygame.draw.rect(frame_surface, (0, 100, 200), (12, body_y, 8, 12))
                    pygame.draw.rect(frame_surface, Colors.SILVER, (17, body_y, 4, 8))  # Side armor
                    
                    # Arms (right side showing)
                    arm_y = 17 + int(body_offset)
                    pygame.draw.rect(frame_surface, (255, 220, 177), (18, arm_y, 6, 4))  # Visible arm
                    
                    # Legs side view with walking
                    leg_y = 27 + int(body_offset)
                    if self.walking:
                        leg_offset = (frame % 2) * 3 - 1
                        pygame.draw.rect(frame_surface, (139, 69, 19), (14 - leg_offset, leg_y, 3, 5))  # Front leg
                        pygame.draw.rect(frame_surface, (139, 69, 19), (17 + leg_offset, leg_y, 3, 5))  # Back leg
                    else:
                        pygame.draw.rect(frame_surface, (139, 69, 19), (14, leg_y, 3, 5))
                        pygame.draw.rect(frame_surface, (139, 69, 19), (17, leg_y, 3, 5))
                    
                    # Sword pointing forward
                    pygame.draw.rect(frame_surface, Colors.GRAY, (20, arm_y, 8, 2))
                    pygame.draw.rect(frame_surface, Colors.GOLD, (27, arm_y - 1, 2, 4))  # Hilt
                
                self.animation_frames[direction].append(frame_surface)
    
    def _update_sprite_image(self):
        frame_index = int(self.animation_frame) % len(self.animation_frames[self.direction])
        self.image = self.animation_frames[self.direction][frame_index].copy()
    
    def update_position(self, world_x: int, world_y: int):
        self.world_x = world_x
        self.world_y = world_y
    
    def set_direction(self, direction: str):
        # Map movement directions to sprite directions
        # W=up, A=left, S=down, D=right
        direction_mapping = {
            "north": "up",      # W key -> up sprite
            "south": "down",    # S key -> down sprite  
            "east": "right",    # D key -> right sprite
            "west": "left",     # A key -> left sprite
            "up": "up",
            "down": "down",
            "left": "left",
            "right": "right"
        }
        
        sprite_direction = direction_mapping.get(direction.lower(), "down")
        self.direction = sprite_direction
        self.walking = True
        self._create_animation_frames()  # Recreate frames with walking animation
    
    def stop_walking(self):
        self.walking = False
        self._create_animation_frames()  # Recreate frames without walking animation
    
    def update(self):
        super().update()
        self._update_sprite_image()
        
        # Stop walking animation when not moving
        if not self.is_moving:
            self.stop_walking()
    
    def smooth_move_to(self, target_x: int, target_y: int, direction: str):
        self.target_x = target_x
        self.target_y = target_y
        self.is_moving = True
        self.set_direction(direction)
        self.move_speed = 4.0  # Smooth movement speed


class WallSprite(GameSprite):
    
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 32, 32, Colors.WALL)
        self._create_wall_sprite()
    
    def _create_wall_sprite(self):
        self.image = pygame.Surface((32, 32))
        
        # Draw solid wall
        self.image.fill(Colors.WALL)
        # Add some texture with lighter gray lines
        for i in range(0, 32, 8):
            pygame.draw.line(self.image, Colors.GRAY, (i, 0), (i, 32), 1)
            pygame.draw.line(self.image, Colors.GRAY, (0, i), (32, i), 1)

class MonsterSprite(GameSprite):
    
    def __init__(self, x: int, y: int, monster_type: str):
        super().__init__(x, y, 32, 32, Colors.RED)
        self.monster_type = monster_type.lower()
        self.animation_frame = 0
        self._create_monster_sprite()
    
    def _create_monster_sprite(self):
        self.image = pygame.Surface((32, 32))
        self.image.set_colorkey(Colors.BLACK)  # Transparent background
        
        center_x, center_y = 16, 16
        
        if self.monster_type == "goblin":
            # Green goblin - small and wiry
            # Head
            pygame.draw.circle(self.image, (0, 150, 0), (center_x, 10), 8)
            # Large pointed ears
            pygame.draw.polygon(self.image, (0, 150, 0), [(8, 8), (6, 4), (10, 6)])
            pygame.draw.polygon(self.image, (0, 150, 0), [(22, 8), (26, 4), (24, 6)])
            # Evil red eyes
            pygame.draw.circle(self.image, Colors.RED, (12, 9), 2)
            pygame.draw.circle(self.image, Colors.RED, (20, 9), 2)
            # Body (dark green)
            pygame.draw.rect(self.image, (0, 100, 0), (12, 18, 8, 10))
            # Arms with claws
            pygame.draw.rect(self.image, (0, 150, 0), (8, 20, 4, 6))
            pygame.draw.rect(self.image, (0, 150, 0), (20, 20, 4, 6))
            # Legs
            pygame.draw.rect(self.image, (0, 100, 0), (13, 28, 2, 4))
            pygame.draw.rect(self.image, (0, 100, 0), (17, 28, 2, 4))
            
        elif self.monster_type == "orc":
            # Red orc - large and muscular
            # Large head
            pygame.draw.circle(self.image, (150, 0, 0), (center_x, 12), 10)
            # Tusks
            pygame.draw.polygon(self.image, Colors.WHITE, [(12, 15), (10, 18), (14, 17)])
            pygame.draw.polygon(self.image, Colors.WHITE, [(20, 15), (18, 17), (22, 18)])
            # Angry yellow eyes
            pygame.draw.circle(self.image, Colors.YELLOW, (11, 10), 2)
            pygame.draw.circle(self.image, Colors.YELLOW, (21, 10), 2)
            pygame.draw.circle(self.image, Colors.RED, (11, 10), 1)
            pygame.draw.circle(self.image, Colors.RED, (21, 10), 1)
            # Muscular body
            pygame.draw.rect(self.image, (120, 0, 0), (10, 22, 12, 8))
            # Large arms
            pygame.draw.rect(self.image, (150, 0, 0), (6, 24, 4, 8))
            pygame.draw.rect(self.image, (150, 0, 0), (22, 24, 4, 8))
            # Thick legs
            pygame.draw.rect(self.image, (120, 0, 0), (12, 30, 3, 4))
            pygame.draw.rect(self.image, (120, 0, 0), (17, 30, 3, 4))
            
        elif self.monster_type == "dragon":
            # Purple dragon - serpentine
            # Dragon head (elongated)
            pygame.draw.ellipse(self.image, (128, 0, 128), (8, 6, 16, 12))
            # Dragon snout
            pygame.draw.ellipse(self.image, (128, 0, 128), (20, 10, 8, 6))
            # Fierce orange eyes
            pygame.draw.circle(self.image, Colors.ORANGE, (12, 11), 2)
            pygame.draw.circle(self.image, Colors.ORANGE, (20, 11), 2)
            pygame.draw.circle(self.image, Colors.RED, (12, 11), 1)
            pygame.draw.circle(self.image, Colors.RED, (20, 11), 1)
            # Body (coiled)
            pygame.draw.ellipse(self.image, (100, 0, 100), (6, 18, 20, 8))
            # Wings
            pygame.draw.polygon(self.image, (80, 0, 80), [(4, 20), (2, 16), (8, 18)])
            pygame.draw.polygon(self.image, (80, 0, 80), [(28, 20), (30, 16), (24, 18)])
            # Tail
            pygame.draw.ellipse(self.image, (128, 0, 128), (12, 26, 8, 6))
            
        elif self.monster_type == "slime":
            # Cyan slime - blob-like
            # Main blob body
            pygame.draw.ellipse(self.image, (0, 255, 255), (6, 12, 20, 16))
            # Glossy highlights
            pygame.draw.ellipse(self.image, (150, 255, 255), (8, 14, 8, 6))
            # Simple dot eyes
            pygame.draw.circle(self.image, Colors.BLACK, (12, 18), 2)
            pygame.draw.circle(self.image, Colors.BLACK, (20, 18), 2)
            # Small bubbles around it
            pygame.draw.circle(self.image, (200, 255, 255), (26, 16), 1)
            pygame.draw.circle(self.image, (200, 255, 255), (6, 20), 1)
            pygame.draw.circle(self.image, (200, 255, 255), (24, 26), 1)
            
        else:
            # Default monster - mysterious shadow
            pygame.draw.ellipse(self.image, (64, 0, 64), (8, 8, 16, 20))
            pygame.draw.circle(self.image, Colors.YELLOW, (12, 14), 2)
            pygame.draw.circle(self.image, Colors.YELLOW, (20, 14), 2)
    
    def update(self):
        self.animation_frame += 0.1
        # Simple floating animation for some monsters
        if self.monster_type in ["dragon", "slime"]:
            offset = int(1 * math.sin(self.animation_frame))
            original_y = getattr(self, 'original_y', self.rect.y)
            if not hasattr(self, 'original_y'):
                self.original_y = self.rect.y
            self.rect.y = self.original_y + offset


class LocationSprite(GameSprite):
    
    def __init__(self, x: int, y: int, location_type: str):
        # Different base colors for different location types
        color_map = {
            "village": Colors.LIGHT_GRAY,
            "forest": Colors.FOREST_GREEN,
            "mountain": Colors.MOUNTAIN_BROWN,
            "cave": Colors.DARK_GRAY,
            "water": Colors.WATER_BLUE,
            "desert": Colors.YELLOW,
            "plains": Colors.GRASS_GREEN
        }
        
        base_color = color_map.get(location_type, Colors.GRASS_GREEN)
        super().__init__(x, y, 64, 64, base_color)
        
        self.location_type = location_type
        self._draw_location_details()
    
    def _draw_location_details(self):
        if self.location_type == "village":
            # Draw simple buildings
            pygame.draw.rect(self.image, Colors.BROWN, (10, 30, 20, 20))
            pygame.draw.polygon(self.image, Colors.RED, [(10, 30), (20, 20), (30, 30)])
            pygame.draw.rect(self.image, Colors.BROWN, (35, 35, 15, 15))
            
        elif self.location_type == "forest":
            # Draw trees
            for i in range(3):
                x = 15 + i * 15
                y = 20 + (i % 2) * 20
                pygame.draw.rect(self.image, Colors.BROWN, (x, y + 15, 4, 10))
                pygame.draw.circle(self.image, Colors.GREEN, (x + 2, y + 10), 8)
                
        elif self.location_type == "mountain":
            # Draw mountain peaks
            pygame.draw.polygon(self.image, Colors.GRAY, [(32, 10), (10, 50), (54, 50)])
            pygame.draw.polygon(self.image, Colors.WHITE, [(32, 10), (25, 25), (39, 25)])
            
        elif self.location_type == "cave":
            # Draw cave entrance
            pygame.draw.ellipse(self.image, Colors.BLACK, (15, 20, 30, 25))
            pygame.draw.arc(self.image, Colors.GRAY, (15, 20, 30, 25), 0, 3.14, 3)


class UI:
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Initialize fonts
        pygame.freetype.init()
        self.font_large = pygame.freetype.Font(None, 24)
        self.font_medium = pygame.freetype.Font(None, 18)
        self.font_small = pygame.freetype.Font(None, 14)
        
        # UI panel dimensions
        self.sidebar_width = 250
        self.bottom_panel_height = 150
        self.game_area_width = screen_width - self.sidebar_width
        self.game_area_height = screen_height - self.bottom_panel_height
        
        # UI surfaces
        self.sidebar_surface = pygame.Surface((self.sidebar_width, screen_height))
        self.bottom_panel_surface = pygame.Surface((self.game_area_width, self.bottom_panel_height))
        self.game_surface = pygame.Surface((self.game_area_width, self.game_area_height))
        
        # Animation variables
        self.blink_timer = 0
        self.notification_timer = 0
        self.current_notification = ""
        
    def draw_sidebar(self, player) -> pygame.Surface:
        self.sidebar_surface.fill(Colors.DARK_GRAY)
        
        y_offset = 10
        
        # Title
        self.font_large.render_to(self.sidebar_surface, (10, y_offset), 
                                 "CHARACTER", Colors.GOLD)
        y_offset += 40
        
        # Player name
        self.font_medium.render_to(self.sidebar_surface, (10, y_offset), 
                                  f"Name: {player.name}", Colors.WHITE)
        y_offset += 25
        
        # Level
        self.font_medium.render_to(self.sidebar_surface, (10, y_offset), 
                                  f"Level: {player.level}", Colors.CYAN)
        y_offset += 25
        
        # Health bar
        self.font_small.render_to(self.sidebar_surface, (10, y_offset), 
                                 "Health:", Colors.WHITE)
        y_offset += 20
        self._draw_progress_bar(self.sidebar_surface, 10, y_offset, 200, 15, 
                               player.health, player.max_health, Colors.HEALTH_RED)
        self.font_small.render_to(self.sidebar_surface, (10, y_offset + 20), 
                                 f"{player.health}/{player.max_health}", Colors.WHITE)
        y_offset += 45
        
        # Coins
        self.font_medium.render_to(self.sidebar_surface, (10, y_offset), 
                                  f"Coins: {player.coins}", Colors.GOLD)
        y_offset += 25
        
        # Attack Power
        self.font_medium.render_to(self.sidebar_surface, (10, y_offset), 
                                  f"Attack: {player.attack_power}", Colors.RED)
        y_offset += 25
        
        # Position
        self.font_medium.render_to(self.sidebar_surface, (10, y_offset), 
                                  f" Position: {player.position}", Colors.YELLOW)
        y_offset += 35
        
        # Equipment section
        self.font_large.render_to(self.sidebar_surface, (10, y_offset), 
                                 "EQUIPMENT", Colors.GOLD)
        y_offset += 30
        
        equipment_items = [
            f"Weapon: {player.equipment['weapon']}",
            f"Armor: {player.equipment['armor']}",
            f"Accessory: {player.equipment['accessory']}"
        ]
        
        for item in equipment_items:
            self.font_small.render_to(self.sidebar_surface, (10, y_offset), 
                                     item, Colors.LIGHT_GRAY)
            y_offset += 18
        
        y_offset += 20
        
        # Inventory section
        self.font_large.render_to(self.sidebar_surface, (10, y_offset), 
                                 "INVENTORY", Colors.GOLD)
        y_offset += 30
        
        if player.inventory:
            for i, item in enumerate(player.inventory[:8]):  # Show max 8 items
                self.font_small.render_to(self.sidebar_surface, (10, y_offset), 
                                         f"{i+1}. {item}", Colors.LIGHT_GRAY)
                y_offset += 18
        else:
            self.font_small.render_to(self.sidebar_surface, (10, y_offset), 
                                     "Empty", Colors.GRAY)
        
        return self.sidebar_surface
    
    def draw_bottom_panel(self, messages: list, current_location: str) -> pygame.Surface:
        self.bottom_panel_surface.fill(Colors.BLACK)
        
        # Draw border
        pygame.draw.rect(self.bottom_panel_surface, Colors.WHITE, 
                        (0, 0, self.game_area_width, self.bottom_panel_height), 2)
        
        # Location info
        self.font_medium.render_to(self.bottom_panel_surface, (10, 10), 
                                  f"Current Location: {current_location}", Colors.CYAN)
        
        # Messages
        self.font_small.render_to(self.bottom_panel_surface, (10, 40), 
                                 "Recent Events:", Colors.YELLOW)
        
        # Show last 6 messages
        y_offset = 60
        for message in messages[-6:]:
            if y_offset < self.bottom_panel_height - 15:
                self.font_small.render_to(self.bottom_panel_surface, (10, y_offset), 
                                         message[:80], Colors.WHITE)  # Truncate long messages
                y_offset += 15
        
        return self.bottom_panel_surface
    
    def draw_game_area(self, camera_x: int, camera_y: int, 
                      world_sprites: pygame.sprite.Group, 
                      player_sprite: PlayerSprite) -> pygame.Surface:
        self.game_surface.fill(Colors.GRASS_GREEN)
        
        # Draw grid
        grid_size = 64
        for x in range(0, self.game_area_width, grid_size):
            pygame.draw.line(self.game_surface, Colors.DARK_GRAY, 
                           (x, 0), (x, self.game_area_height))
        for y in range(0, self.game_area_height, grid_size):
            pygame.draw.line(self.game_surface, Colors.DARK_GRAY, 
                           (0, y), (self.game_area_width, y))
        
        # Calculate camera offset
        center_x = self.game_area_width // 2
        center_y = self.game_area_height // 2
        
        # Draw world sprites
        for sprite in world_sprites:
            screen_x = sprite.world_x * grid_size - camera_x + center_x
            screen_y = sprite.world_y * grid_size - camera_y + center_y
            
            # Only draw if on screen
            if (-grid_size <= screen_x <= self.game_area_width and 
                -grid_size <= screen_y <= self.game_area_height):
                sprite.rect.x = screen_x
                sprite.rect.y = screen_y
                self.game_surface.blit(sprite.image, sprite.rect)
        
        # Draw player in center
        player_sprite.rect.x = center_x - 16  # Center the 32x32 player sprite
        player_sprite.rect.y = center_y - 16
        self.game_surface.blit(player_sprite.image, player_sprite.rect)
        
        # Draw compass
        self._draw_compass(center_x + self.game_area_width//2 - 80, 20)
        
        return self.game_surface
    
    def _draw_progress_bar(self, surface: pygame.Surface, x: int, y: int, 
                          width: int, height: int, current: int, maximum: int, 
                          color):
        # Background
        pygame.draw.rect(surface, Colors.DARK_GRAY, (x, y, width, height))
        
        # Border
        pygame.draw.rect(surface, Colors.WHITE, (x, y, width, height), 1)
        
        # Fill
        if maximum > 0:
            fill_width = int((current / maximum) * (width - 2))
            pygame.draw.rect(surface, color, (x + 1, y + 1, fill_width, height - 2))
    
    def _draw_compass(self, x: int, y: int):
        radius = 25
        center = (x + radius, y + radius)
        
        # Background circle
        pygame.draw.circle(self.game_surface, Colors.WHITE, center, radius)
        pygame.draw.circle(self.game_surface, Colors.BLACK, center, radius, 2)
        
        # North arrow
        pygame.draw.polygon(self.game_surface, Colors.RED, [
            (center[0], center[1] - radius + 5),
            (center[0] - 5, center[1] - 5),
            (center[0] + 5, center[1] - 5)
        ])
        
        # Labels
        self.font_small.render_to(self.game_surface, (center[0] - 3, center[1] - radius - 15), 
                                 "N", Colors.BLACK)
    
    def show_notification(self, message: str, duration: int = 3000):
        self.current_notification = message
        self.notification_timer = pygame.time.get_ticks() + duration
    
    def draw_notifications(self, surface: pygame.Surface):
        if self.current_notification and pygame.time.get_ticks() < self.notification_timer:
            # Create semi-transparent background
            notification_surface = pygame.Surface((400, 50))
            notification_surface.set_alpha(180)
            notification_surface.fill(Colors.BLACK)
            
            # Draw notification text
            text_surface, _ = self.font_medium.render(self.current_notification, Colors.WHITE)
            text_rect = text_surface.get_rect(center=(200, 25))
            notification_surface.blit(text_surface, text_rect)
            
            # Position at top center of screen
            x = (surface.get_width() - 400) // 2
            surface.blit(notification_surface, (x, 50))
    
    def draw_combat_overlay(self, surface: pygame.Surface, player, monster):
        # Semi-transparent background
        overlay = pygame.Surface((surface.get_width(), surface.get_height()))
        overlay.set_alpha(128)
        overlay.fill(Colors.BLACK)
        surface.blit(overlay, (0, 0))
        
        # Combat panel
        panel_width = 500
        panel_height = 300
        panel_x = (surface.get_width() - panel_width) // 2
        panel_y = (surface.get_height() - panel_height) // 2
        
        combat_panel = pygame.Surface((panel_width, panel_height))
        combat_panel.fill(Colors.DARK_GRAY)
        pygame.draw.rect(combat_panel, Colors.WHITE, (0, 0, panel_width, panel_height), 3)
        
        # Title
        self.font_large.render_to(combat_panel, (20, 20), "COMBAT", Colors.RED)
        
        # Player stats
        y_offset = 60
        self.font_medium.render_to(combat_panel, (20, y_offset), 
                                  f"{player.name}", Colors.CYAN)
        y_offset += 25
        self.font_small.render_to(combat_panel, (20, y_offset), 
                                 f"Health: {player.health}/{player.max_health}", Colors.WHITE)
        
        # Player health bar
        y_offset += 20
        self._draw_progress_bar(combat_panel, 20, y_offset, 200, 15, 
                               player.health, player.max_health, Colors.HEALTH_RED)
        
        # Monster stats  
        y_offset = 60
        self.font_medium.render_to(combat_panel, (280, y_offset), 
                                  f"{monster.name}", Colors.RED)
        y_offset += 25
        self.font_small.render_to(combat_panel, (280, y_offset), 
                                 f"Health: {monster.health}/{monster.max_health}", Colors.WHITE)
        
        # Monster health bar
        y_offset += 20
        self._draw_progress_bar(combat_panel, 280, y_offset, 200, 15, 
                               monster.health, monster.max_health, Colors.HEALTH_RED)
        
        # Combat options
        y_offset = 180
        options = ["1. Attack", "2. Use Item"]
        for option in options:
            self.font_medium.render_to(combat_panel, (20, y_offset), option, Colors.YELLOW)
            y_offset += 30
        
        surface.blit(combat_panel, (panel_x, panel_y))
    
    def update_animations(self):
        self.blink_timer += 1
        if self.blink_timer > 60:  # Reset every second at 60 FPS
            self.blink_timer = 0


def test_graphics_engine():
    print("Testing Graphics Engine...")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Graphics Engine Test")
    
    # Test UI creation
    ui = UI(800, 600)
    assert ui.sidebar_width == 250, "UI sidebar width incorrect"
    print("✓ UI initialization test passed")
    
    # Test sprite creation
    player_sprite = PlayerSprite(100, 100)
    assert player_sprite.rect.width == 32, "Player sprite size incorrect"
    print("✓ Player sprite test passed")
    
    # Test monster sprite creation
    goblin_sprite = MonsterSprite(200, 200, "goblin")
    assert goblin_sprite.monster_type == "goblin", "Monster type incorrect"
    print("✓ Monster sprite test passed")
    
    pygame.quit()
    print("All Graphics Engine tests passed\n")


def create_simple_sprites():
    sprites = {}
    
    # Create coin sprite
    coin_sprite = pygame.Surface((16, 16))
    coin_sprite.fill(Colors.GOLD)
    pygame.draw.circle(coin_sprite, Colors.YELLOW, (8, 8), 7)
    pygame.draw.circle(coin_sprite, Colors.GOLD, (8, 8), 7, 2)
    sprites['coin'] = coin_sprite
    
    # Create treasure chest sprite
    chest_sprite = pygame.Surface((24, 20))
    chest_sprite.fill(Colors.BROWN)
    pygame.draw.rect(chest_sprite, Colors.GOLD, (2, 2, 20, 6))
    pygame.draw.rect(chest_sprite, Colors.BROWN, (0, 8, 24, 12))
    sprites['chest'] = chest_sprite
    
    # Create tree sprite
    tree_sprite = pygame.Surface((32, 48))
    tree_sprite.set_colorkey(Colors.BLACK)  # Make black transparent
    pygame.draw.rect(tree_sprite, Colors.BROWN, (14, 32, 4, 16))  # Trunk
    pygame.draw.circle(tree_sprite, Colors.GREEN, (16, 20), 12)   # Leaves
    sprites['tree'] = tree_sprite
    
    return sprites

