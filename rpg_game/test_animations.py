#!/usr/bin/env python3

import pygame
import time
from graphics_engine import PlayerSprite, UI, MonsterSprite


def test_animations():
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Animation & Performance Test")
    clock = pygame.time.Clock()
    
    # Create UI for reference
    ui = UI(800, 600)
    
    # Create test sprites
    player_sprite = PlayerSprite(400, 300)
    goblin_sprite = MonsterSprite(200, 200, "goblin")
    orc_sprite = MonsterSprite(600, 200, "orc")
    
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player_sprite, goblin_sprite, orc_sprite)
    
    # Performance tracking
    frame_count = 0
    start_time = time.time()
    fps_samples = []
    
    print("Animation Test Controls:")
    print("WASD/Arrow Keys: Move player and test animations")
    print("SPACE: Toggle animation speed")
    print("ESC: Quit test")
    print("F: Toggle FPS display")
    print("\nTesting animations at 60 FPS...")
    
    show_fps = True
    animation_speed = 1.0
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        current_fps = clock.get_fps()
        
        # Track FPS for performance analysis
        if current_fps > 0:
            fps_samples.append(current_fps)
            if len(fps_samples) > 300:  # Keep last 5 seconds at 60 FPS
                fps_samples.pop(0)
        
        frame_count += 1
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_f:
                    show_fps = not show_fps
                elif event.key == pygame.K_SPACE:
                    animation_speed = 2.0 if animation_speed == 1.0 else 1.0
                    print(f"Animation speed: {animation_speed}x")
        
        # Handle continuous key presses for movement
        keys = pygame.key.get_pressed()
        move_speed = 120 * dt * animation_speed  # pixels per second
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_sprite.rect.x -= move_speed
            player_sprite.update_animation("moving")
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_sprite.rect.x += move_speed
            player_sprite.update_animation("moving")
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            player_sprite.rect.y -= move_speed
            player_sprite.update_animation("moving")
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player_sprite.rect.y += move_speed
            player_sprite.update_animation("moving")
        else:
            player_sprite.update_animation("idle")
        
        # Keep player on screen
        player_sprite.rect.clamp_ip(pygame.Rect(0, 0, 800, 600))
        
        # Update all sprites
        all_sprites.update()
        
        # Draw everything
        screen.fill((30, 30, 30))  # Dark gray background
        
        # Draw grid for reference
        for x in range(0, 800, 32):
            pygame.draw.line(screen, (60, 60, 60), (x, 0), (x, 600), 1)
        for y in range(0, 600, 32):
            pygame.draw.line(screen, (60, 60, 60), (0, y), (800, y), 1)
        
        # Draw sprites
        all_sprites.draw(screen)
        
        # Draw performance info
        if show_fps:
            font = pygame.font.Font(None, 36)
            
            # Current FPS
            fps_text = font.render(f"FPS: {current_fps:.1f}", True, (255, 255, 0))
            screen.blit(fps_text, (10, 10))
            
            # Average FPS
            if fps_samples:
                avg_fps = sum(fps_samples) / len(fps_samples)
                avg_text = font.render(f"Avg FPS: {avg_fps:.1f}", True, (255, 255, 0))
                screen.blit(avg_text, (10, 50))
            
            # Frame count and elapsed time
            elapsed = time.time() - start_time
            frame_text = font.render(f"Frames: {frame_count}", True, (255, 255, 0))
            time_text = font.render(f"Time: {elapsed:.1f}s", True, (255, 255, 0))
            screen.blit(frame_text, (10, 90))
            screen.blit(time_text, (10, 130))
            
            # Animation speed
            speed_text = font.render(f"Speed: {animation_speed}x", True, (255, 255, 0))
            screen.blit(speed_text, (10, 170))
        
        # Performance warning
        if current_fps < 50 and frame_count > 60:  # After first second
            warning_font = pygame.font.Font(None, 24)
            warning = warning_font.render("Performance Warning: FPS below 50", True, (255, 100, 100))
            screen.blit(warning, (10, 550))
        
        pygame.display.flip()
    
    # Final performance report
    total_time = time.time() - start_time
    avg_fps = sum(fps_samples) / len(fps_samples) if fps_samples else 0
    
    print(f"\nPerformance Report:")
    print(f"Total frames: {frame_count}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average FPS: {avg_fps:.1f}")
    print(f"Target FPS: 60")
    print(f"Performance: {'GOOD' if avg_fps >= 55 else 'NEEDS OPTIMIZATION'}")
    
    pygame.quit()
    return avg_fps >= 55


def test_sprite_loading():
    print("Testing sprite loading performance...")
    
    pygame.init()
    screen = pygame.display.set_mode((100, 100))  # Minimal window
    
    start_time = time.time()
    
    # Test creating many sprites
    sprites = []
    for i in range(100):
        player = PlayerSprite(i, i)
        goblin = MonsterSprite(i, i, "goblin")
        sprites.extend([player, goblin])
    
    loading_time = time.time() - start_time
    
    print(f"Created {len(sprites)} sprites in {loading_time:.3f} seconds")
    print(f"Average time per sprite: {(loading_time/len(sprites)*1000):.2f} ms")
    
    pygame.quit()
    
    return loading_time < 1.0  # Should create 200 sprites in under 1 second


def main():
    print("="*50)
    print("ANIMATION & PERFORMANCE TEST SUITE")
    print("="*50)
    
    # Test sprite loading first
    loading_ok = test_sprite_loading()
    print(f"Sprite loading: {'✓ PASSED' if loading_ok else '✗ FAILED'}")
    
    print("\nStarting animation test...")
    print("Close the window or press ESC when done testing")
    
    # Test animations
    animation_ok = test_animations()
    print(f"Animation performance: {'✓ PASSED' if animation_ok else '✗ FAILED'}")
    
    if loading_ok and animation_ok:
        print("\nAll animation tests passed!")
    else:
        print("\nSome performance issues detected")


if __name__ == "__main__":
    main()