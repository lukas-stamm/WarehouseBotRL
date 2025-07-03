import pygame
from Classes.Helper.helper import get_frame

class Robot(pygame.sprite.Sprite):

    ACTIONS = {
        0: (-1, 0), # move left
        1: (1, 0), # move right
        2: (0, -1), # move up
        3:  (0, 1), # move down
    }

    def __init__(self, bot_id, grid_pos, groups, grid_size, tile_size):
        super().__init__(groups)

        # Store grid position and grid size for logic
        self.grid_x, self.grid_y = grid_pos
        self.grid_size = grid_size
        self.tile_size = tile_size

        # Load sprite sheet & animations
        self.sprite_sheet = pygame.image.load('Assets/images/Drone_2_Flying_32x32.png').convert_alpha()
        self.fly_frames = [get_frame(self, i, width=32, height=44, rh=0) for i in range(20, 23)]
        self.grab_frames = [get_frame(self, i, width=32, height=44, rh=228) for i in range(12)]
        self.frame_index = 0
        self.animation_speed = 0.15
        self.is_grabbing = False
        self.grab_timer = 0
        self.grab_duration = 500  # milliseconds

        # Initial sprite image and hitbox
        self.image = self.fly_frames[self.frame_index]
        pixel_pos = (self.grid_x * self.tile_size, self.grid_y * self.tile_size)
        self.hitbox = pygame.Rect(pixel_pos[0], pixel_pos[1], 32, 32)
        self.rect = self.image.get_rect(center=self.hitbox.topleft)

        # Unique identifier for each bot on the map
        self.bot_id = bot_id
        # Movement speed of bot
        self.speed = self.tile_size
        # Represents inventory; None = empty, "A" = ItemA, "B" = ItemB
        self.held_item_type = None

    def propose_move(self, action):
        """
        Propose move without enforcing walls or collisions.
        """
        dx, dy = Robot.ACTIONS[action]
        proposed_x = self.grid_x + dx
        proposed_y = self.grid_y + dy
        return proposed_x, proposed_y

    def set_position(self, x, y):
        """
        Set grid position ONLY if the environment approves it.
        """
        self.grid_x = x
        self.grid_y = y
        # Update pixel position for rendering
        self.hitbox.topleft = (self.grid_x * self.tile_size, self.grid_y * self.tile_size)

    def pickup_item(self, item):
        """
        Sets the inventory flag for the picked-up item to True if empty.
        """
        if self.held_item_type is None:
            self.held_item_type = item.item_type
            print(f"({self.bot_id})Picked up item {item.item_type}.")

            # Trigger grab animation
            self.is_grabbing = True
            self.grab_timer = pygame.time.get_ticks()
            self.frame_index = 0
        else:
            print(f"({self.bot_id})Already holding item {self.held_item_type}.")

    def deliver_item(self, dropzone):

        print("delivering item works")

        if self.held_item_type is None:
            print(f"({self.bot_id})No item to deliver.")
            return False

        if self.held_item_type == dropzone.accepted_type:
            print(f"({self.bot_id})Delivered item {self.held_item_type}.")
            self.held_item_type = None

            # Trigger grab animation
            self.is_grabbing = True
            self.grab_timer = pygame.time.get_ticks()
            self.frame_index = 0
            return True
        else:
            print(f"({self.bot_id})Wrong item for this dropzone.")
            return False

    def animate(self):
        """
        Handles flying loop and grab overlay.
        """
        current_time = pygame.time.get_ticks()

        # Base fly animation
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.fly_frames):
            self.frame_index = 0
        base_frame = self.fly_frames[int(self.frame_index)]

        # If grabbing, composite bottom claw
        if self.is_grabbing:
            elapsed = current_time - self.grab_timer
            grab_frame_index = min(int((elapsed / self.grab_duration) * len(self.grab_frames)), len(self.grab_frames) - 1)
            grab_frame = self.grab_frames[grab_frame_index]
            # Create a full composite image
            full_frame = pygame.Surface((32, 72), pygame.SRCALPHA)
            # Only copy top 20 px from fly frame
            full_frame.blit(base_frame, (0, 0), (0, 0, 32, 34))
            # Then copy full grab claw (32x12) at y = 20
            full_frame.blit(grab_frame, (0, 34))

            self.image = full_frame

            if elapsed >= self.grab_duration:
                self.is_grabbing = False
                self.frame_index = 0
            return

        # Not grabbing → fly frame only
        self.image = base_frame

    def update(self):
        self.animate()