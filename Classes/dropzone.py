import pygame

class Dropzone(pygame.sprite.Sprite):
    def __init__(self, pos, size=(128, 64), groups=None, accepted_types=None):
        super().__init__(groups)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=pos)
        self.accepted_types = accepted_types