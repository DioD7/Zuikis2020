#######
##Entity classes for visualization in window
#######
import pygame
from pygame.locals import *


class Zuikis(pygame.sprite.Sprite):
    picture = 'pics/—Pngtree—rabbit_2622880.png'

    def __init__(self, field):
        pygame.sprite.Sprite.__init__(self)
        self.field = field

        self.image = pygame.image.load(self.picture).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.field.square, self.field.square))
        self.rect = self.image.get_rect()

    def update(self):
        pass


class Vilkas(pygame.sprite.Sprite):
    picture = 'pics/Wolf.png'

    def __init__(self, field):
        pygame.sprite.Sprite.__init__(self)
        self.field = field

        self.image = pygame.image.load(self.picture).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.field.square, self.field.square))
        self.rect = self.image.get_rect()

    def update(self):
        pass


class Morka(pygame.sprite.Sprite):
    picture = 'pics/carrot.png'

    def __init__(self, field):
        pygame.sprite.Sprite.__init__(self)
        self.field = field

        self.image = pygame.image.load(self.picture).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.field.square, self.field.square))
        self.rect = self.image.get_rect()

    def update(self):
        pass