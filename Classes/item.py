import pygame

class Item(pygame.sprite.Sprite):
    def __init__(self, grid_pos, tile_size, groups, item_type):
        super().__init__(groups)

        self.grid_x, self.grid_y = grid_pos
        self.tile_size = tile_size
        self.item_type = item_type

        # Load image based on item type
        if item_type == 'B':
            self.image = pygame.image.load('Assets/images/Hospital_Black_Shadow_Singles_32x32_317.png').convert_alpha()
        else:
            self.image = pygame.image.load('Assets/images/Hospital_Black_Shadow_Singles_32x32_318.png').convert_alpha()

        # Position on screen based on grid
        pixel_pos = (self.grid_x * tile_size, self.grid_y * tile_size)
        self.rect = self.image.get_rect(topleft=pixel_pos)

