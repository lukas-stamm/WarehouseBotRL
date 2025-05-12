import pygame

class Item(pygame.sprite.Sprite):
    def __init__(self, pos, groups, type):
        super().__init__(groups)
        self.image = pygame.image.load('Assets/images/Hospital_Black_Shadow_Singles_32x32_317.png') if type == 'b' else pygame.image.load('Assets/images/Hospital_Black_Shadow_Singles_32x32_318.png')
        self.rect = self.image.get_rect(topleft=pos)
        self.type = type

