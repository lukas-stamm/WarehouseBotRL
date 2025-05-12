import pygame
from Classes.item import Item

class Robot(pygame.sprite.Sprite):
    def __init__(self, id, pos, groups, collision_group):
        super().__init__(groups)
        self.id = id
        self.collision_group = collision_group
        self.speed = 2
        self.inventory = []
        self.last_delivery_time = 0
        self.delivery_cooldown = 1500

        # Load sprite sheet
        self.sprite_sheet = pygame.image.load('Assets/images/Drone_2_Flying_32x32.png').convert_alpha()

        # Fly loop frames (first row, indices 20–22)
        self.fly_frames = [self.get_frame(i, row=0) for i in range(20, 23)]

        # Grab claw frames (only bottom 12px, row 1)
        self.grab_frames = [self.get_grab_frame(i) for i in range(12)]

        # Animation state
        self.frame_index = 0
        self.animation_speed = 0.15
        self.is_grabbing = False
        self.grab_timer = 0
        self.grab_duration = 500  # milliseconds

        # Initial sprite image and hitbox
        self.image = self.fly_frames[self.frame_index]
        self.hitbox = pygame.Rect(pos[0], pos[1], 32, 32)
        self.rect = self.image.get_rect(center=self.hitbox.topleft)

    def get_frame(self, frame_index, row=0, width=32, height=44):
        """Extract a 32x32 frame from the sprite sheet."""
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        frame.blit(self.sprite_sheet, (0, 0), (frame_index * width, row * height, width, height))
        return frame

    def get_grab_frame(self, frame_index, width=32, height=28):
        """Extract a 32x12 grab claw frame from the second row."""
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        frame.blit(self.sprite_sheet, (0, 0), (frame_index * width, 228, width, height))  # Y=52
        return frame

    def animate(self):
        """Handles flying loop and grab overlay."""
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
            # Create full composite image
            full_frame = pygame.Surface((32, 72), pygame.SRCALPHA)
            # Only copy top 20px from fly frame
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

    def input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_RIGHT]:
            dx = self.speed
        if keys[pygame.K_UP]:
            dy = -self.speed
        if keys[pygame.K_DOWN]:
            dy = self.speed
        return dx, dy

    def update_pos(self):
        dx, dy = self.input()

        # Move hitbox
        self.hitbox.x += dx
        if pygame.sprite.spritecollide(self, self.collision_group, False,
                                       collided=lambda x, y: x.hitbox.colliderect(y.rect)):
            self.hitbox.x -= dx

        self.hitbox.y += dy
        if pygame.sprite.spritecollide(self, self.collision_group, False,
                                       collided=lambda x, y: x.hitbox.colliderect(y.rect)):
            self.hitbox.y -= dy

        # Align sprite rect to hitbox
        self.rect.center = self.hitbox.center

    def pickup_item(self, item):
        if not self.inventory:
            self.inventory.append(item)
            print(f"({self.id})Item picked up.")
            item.kill()

            # Trigger grab animation
            self.is_grabbing = True
            self.grab_timer = pygame.time.get_ticks()
            self.frame_index = 0

    def deliver_item(self, item):
        if not self.inventory:
            print(f"({self.id})No item to deliver. Inventory empty.")
            return

        if item.accepted_types == self.inventory[0].type:
            self.inventory.pop(0)
            # Trigger grab animation
            self.is_grabbing = True
            self.grab_timer = pygame.time.get_ticks()
            self.frame_index = 0

            print(f"({self.id})Item delivered.")
        else:
            print(f"({self.id})Wrong item for this zone.")

    def update(self):
        self.update_pos()
        self.animate()