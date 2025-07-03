import pygame
from pytmx.util_pygame import load_pygame

class Tile(pygame.sprite.Sprite):
    """
    A single tile in the map, with its image, position and collision.
    """
    def __init__(self, pos, surf, groups, is_collision=False):
        super().__init__(groups)
        # 2D array of pixels for corresponding tile
        self.image = surf
        # Holds' coordinates for tile position on the map
        self.rect = self.image.get_rect(topleft=pos)
        # Flag to check if tile can be passed through
        self.is_collision = is_collision

class Map:
    """
    Complete map consistent of tiles from tmx data.
    """
    def __init__(self, tmx_path, all_sprites_group, render_layer_group, pickup_locations, delivery_zones):
        # Load TMX map
        self.tmx_data = load_pygame(tmx_path)
        self.tile_width = self.tmx_data.tilewidth
        self.tile_height = self.tmx_data.tileheight
        self.width = self.tmx_data.width
        self.height = self.tmx_data.height

        # Master draw/update group containing all layers and sprites
        self.all_sprites_group = all_sprites_group
        # Holds ONLY the map tile sprites (background layer)
        self.render_layer_group = render_layer_group

        # 2D array to act as a map indicating which tiles are passable and which aren't
        self.collision_map = [
            [False for _ in range(self.height)] for _ in range(self.width)
        ]

        # Store pickup points (single tile per item type)
        self.pickup_locations = pickup_locations  # e.g. {"ItemA": (x, y)}
        # Store delivery zones as rectangles per item type
        self.delivery_zones = delivery_zones  # e.g. {"ItemA": {"x1": x, "y1": y, "x2": x2, "y2": y2}}

        # Load walls/obstacles from TMX layers
        self.load_tiles()

    def load_tiles(self):
        """
        Loads tile layers from TMX, builds a collision map, and adds Tile sprites
        to the sprite groups for rendering.
        """

        # Define which TMX layers count as walls/obstacles
        collision_layers = {
            "Walls"
        }

        for layer in self.tmx_data.visible_layers:
            is_collision = layer.name in collision_layers

            for x, y, surf in layer.tiles():
                # Place tile sprite at pixel position
                pos = (x * self.tile_width, y * self.tile_height)

                # Add Tile to both groups:
                # - all_sprites_group ensures it's updated/drawn with everything
                # - render_layer_group allows drawing the map background separately
                groups = (self.all_sprites_group, self.render_layer_group)
                Tile(pos=pos, surf=surf, groups=groups, is_collision=is_collision)

                # Mark collision in logic grid
                if is_collision:
                    self.collision_map[x][y] = True

    # ====== RL Environment Logic API ======

    def is_within_bounds(self, x, y):
        """
        True if (x,y) is inside the map grid.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def is_blocked(self, x, y):
        """
        True if (x,y) is out of bounds or blocked by wall.
        """
        if not self.is_within_bounds(x, y):
            return True
        return self.collision_map[x][y]

    def get_pickup_location(self, item_type):
        """
        Returns single (x, y) pickup location for item type.
        Used to spawn Items in Environment.
        """
        return self.pickup_locations.get(item_type)

    def get_delivery_zone(self, item_type):
        """
        Returns delivery zone rectangle for item type.
        Format: {"x1": x, "y1": y, "x2": x2, "y2": y2}
        """
        return self.delivery_zones.get(item_type)

    def is_in_delivery_zone(self, item_type, x, y):
        """
        Returns True if (x,y) is inside delivery rectangle for item type.
        """
        zone = self.get_delivery_zone(item_type)
        if not zone:
            return False
        return zone.contains(x, y)

    def draw_grid_debug(self, surface):
        """
        Draws grid lines for debugging.
        """
        for x in range(0, self.width * self.tile_width, self.tile_width):
            pygame.draw.line(surface, (100, 100, 100), (x, 0), (x, self.height * self.tile_height))
        for y in range(0, self.height * self.tile_height, self.tile_height):
            pygame.draw.line(surface, (100, 100, 100), (0, y), (self.width * self.tile_width, y))