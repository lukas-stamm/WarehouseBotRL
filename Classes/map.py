import pygame
from pytmx.util_pygame import load_pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, is_collision=False):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.is_collision = is_collision

class Map:
    def __init__(self, tmx_path, sprite_group):
        self.tmx_data = load_pygame(tmx_path)
        self.sprite_group = sprite_group
        self.collision_group = pygame.sprite.Group()
        self.load_map()

    def load_map(self):
        tile_width = self.tmx_data.tilewidth
        tile_height = self.tmx_data.tileheight

        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                is_collision = layer.name in ['Below Walls', 'Objects Below', 'Objects', 'ObjectsTop', 'Walls']
                for x, y, surf in layer.tiles():
                    pos = (x * tile_width, y * tile_height)
                    Tile(
                            pos=pos,
                            surf=surf,
                            groups=(self.sprite_group, self.collision_group) if is_collision else (self.sprite_group,),
                            is_collision=is_collision
                         )