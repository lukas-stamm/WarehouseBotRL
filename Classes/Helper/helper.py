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


def get_frame(sprite, frame_index, width, height, rh):
    """
    Extract one frame from the sprite_sheet attribute of `sprite`.
    """
    frame = pygame.Surface((width, height), pygame.SRCALPHA)
    frame.blit(sprite.sprite_sheet, (0, 0), (frame_index * width, rh, width, height))
    return frame




def reset_event_flags(self):
    """Call at the start of each RL step to clear last-step’s events."""
    self.collided_with_wall = False
    self.collided_with_robot = False
    self.just_picked_up = False
    self.just_tried_wrong_pickup = False
    self.just_delivered = False
    self.just_tried_wrong_drop = False