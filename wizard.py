import pygame 
import math 
from proyectil import Proyectil
class Wizard(pygame.sprite.Sprite):
    def __init__(self, x, y, proyectiles):
        super().__init__()
        self.image = pygame.image.load("Tiles/tile_0111.png").convert_alpha()
        self.image = pygame.transform.scale(self.image,(50,50))
        self.rect  = self.image.get_rect(center=(x,y)) 
        self.pos   = pygame.math.Vector2(self.rect.center)
        self.speed = 2
        self.hp    = 60
        self.proyectiles = proyectiles 
        self.cooldown    = 120
        self.timer       = 60
        self.damage      = 20
    def update(self,target):
        direccion = pygame.math.Vector2(target.rect.center)-self.pos
        distancia = direccion.length()
        if distancia > 250:
            self.pos += direccion.normalize()* self.speed
            self.rect.center = self.pos
        self.timer -=1
        if self.timer <=0:
            self.proyectiles.add( Proyectil(self.rect.centerx, self.rect.centery,target.rect.centerx,target.rect.centery))
            self.timer = self.cooldown