from random import randint
import pygame
def get_non_overlapping_spawn(existing_robots, base_x, base_y, x_offset, y_offset, size, max_attempts=100):
    for _ in range(max_attempts):
        x = base_x + randint(-x_offset, x_offset)
        y = base_y + randint(-y_offset, y_offset)
        new_rect = pygame.Rect(x, y, size, size)

        # Check collision with already-spawned robots
        if not any(r.rect.colliderect(new_rect) for r in existing_robots):
            return x, y

    raise Exception("Could not find a non-overlapping spawn location.")