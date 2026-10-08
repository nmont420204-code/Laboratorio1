import pygame 

class Proyectil(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = pygame.image.load("Tiles/bola_fuego (1).png").convert_alpha()
        self.image = pygame.transform.scale(self.image,(30,30))
        self.rect = self.image.get_rect(center=(x,y))

        self.pos = pygame.math.Vector2(self.rect.center)
        direccion= pygame.math.Vector2(target_x - x, target_y -y)
        if direccion.length() == 0:
            direccion = pygame.math.Vector2(1,0)
        self.velocidad = direccion.normalize() * 6 
        self.damage = 30
    def update(self):
        self.pos += self.velocidad
        self.rect.center= self.pos
        pantalla= pygame.display.get_surface().get_rect()
        if not pantalla.colliderect(self.rect):
            self.kill()