import pygame
import sys
import math
from wizard import Wizard


pygame.init()
screen = pygame.display.set_mode((1536, 1024))


WIDTH, HEIGHT = screen.get_size()
inicio= pygame.transform.scale( pygame.image.load("interfaz.png").convert_alpha(), (WIDTH, HEIGHT))
pygame.display.set_caption("BLUE KNIGHT")
mapa = pygame.transform.scale( pygame.image.load("MAPA.png").convert_alpha(), (HEIGHT, HEIGHT))

mapa11 = (WIDTH - HEIGHT) // 2
bloque_exterior = pygame.Rect(mapa11 + 105, 150, 908 - 105, 768 - 150)

def mapa_bloque(x1, y1, x2, y2):
    return pygame.Rect(mapa11 + x1, y1, x2 - x1, y2 - y1)

bloques = [
    mapa_bloque(300, 270, 346, 697),   
    mapa_bloque(677, 270, 720, 697),   
    mapa_bloque(300, 270, 720, 341),   
    mapa_bloque(300, 625, 475, 697),   
    mapa_bloque(548, 625, 720, 697),   
]

WHITE = (255, 255, 255)
BLACK = (20, 20, 25)
BTN_COLOR = (70, 70, 80)
BTN_HOVER = (120, 120, 130)
GRASS_COLOR = (30, 80, 40)
HEALTH_RED = (200, 30, 30)
HEALTH_BG = (50, 50, 50)

font_title = pygame.font.SysFont("impact", 80)
font_btn = pygame.font.SysFont("arial", 40, bold=True)
font_hud = pygame.font.SysFont("arial", 24, bold=True)

class Knight(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()  
        
        self.sprites = {
            "up": pygame.transform.scale(pygame.image.load("Tiles/tile_0087_espalda.png").convert_alpha(), (60, 60)),
            "down": pygame.transform.scale(pygame.image.load("Tiles/tile_0087.png").convert_alpha(), (60, 60)),
            "left": pygame.transform.scale(pygame.image.load("Tiles/tile_0087_izquierda.png").convert_alpha(), (60, 60)),
            "right": pygame.transform.scale(pygame.image.load("Tiles/tile_0087_derecha.png").convert_alpha(), (60, 60))
        }
        
        self.direction = "right"
        self.image = self.sprites[self.direction]
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
        self.max_hp = 100
        self.hp = 100
        self.hit_cooldown = 0
        
        self.attack_frames = [
            pygame.transform.scale(pygame.image.load("Tiles/ataque1.png").convert_alpha(), (120, 120)),
            pygame.transform.scale(pygame.image.load("Tiles/ataque2.png").convert_alpha(), (120, 120)),
            pygame.transform.scale(pygame.image.load("Tiles/ataque3.png").convert_alpha(), (120, 120)),
            pygame.transform.scale(pygame.image.load("Tiles/ataque4.png").convert_alpha(), (120, 120))
        ]
        
        self.is_attacking = False
        self.current_frame = 0
        self.animation_speed = 0.25
        self.attack_angle = 0
        self.attack_rect = None
        self.damage_dealt = False

    def update(self):
        keys = pygame.key.get_pressed()
        
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        
        if not self.is_attacking:
            y2 = self.rect.y
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.rect.y -= self.speed
                self.direction = "up"
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.rect.y += self.speed
                self.direction = "down"

            if self.rect.collidelist(bloques) != -1:
                self.rect.y = y2
            x2 = self.rect.x
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.rect.x -= self.speed
                self.direction = "left"
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.rect.x += self.speed
                self.direction = "right"

            if self.rect.collidelist(bloques) != -1:
                self.rect.x = x2
                
            self.image = self.sprites[self.direction]
                
        self.rect.clamp_ip(bloque_exterior)

        if self.is_attacking:
            self.current_frame += self.animation_speed
            
            offset_x = math.cos(math.radians(self.attack_angle)) * 50
            offset_y = -math.sin(math.radians(self.attack_angle)) * 50
            self.attack_rect = pygame.Rect(0, 0, 80, 80)
            self.attack_rect.center = (self.rect.centerx + offset_x, self.rect.centery + offset_y)
            
            if self.current_frame >= len(self.attack_frames):
                self.is_attacking = False
                self.current_frame = 0
                self.attack_rect = None

    def attack(self):
        if not self.is_attacking:
            self.is_attacking = True
            self.current_frame = 0
            self.damage_dealt = False
            
            if self.direction == "right":
                self.attack_angle = 0
            elif self.direction == "left":
                self.attack_angle = 180
            elif self.direction == "up":
                self.attack_angle = 90
            elif self.direction == "down":
                self.attack_angle = 270

    def draw_attack(self, surface):
        if self.is_attacking:
            frame_image = self.attack_frames[int(self.current_frame)]
            rotated_image = pygame.transform.rotate(frame_image, self.attack_angle)
            
            if self.attack_rect:
                rotated_rect = rotated_image.get_rect(center=self.attack_rect.center)
                surface.blit(rotated_image, rotated_rect)

class Slime(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("Tiles/tile_0108.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2
        self.damage = 10
        self.hp = 30

    def update(self, target):
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            dx /= dist
            dy /= dist
            y_antes = self.rect.y
            self.rect.y += dy * self.speed
            if self.rect.collidelist(bloques) != -1:
                self.rect.y = y_antes

            x_antes = self.rect.x
            self.rect.x += dx * self.speed
            if self.rect.collidelist(bloques) != -1:
                self.rect.x = x_antes

            self.rect.clamp_ip(bloque_exterior)

def draw_hud(surface, x, y, hp, max_hp, score):
    bar_width = 200
    bar_height = 22
    fill = max(0, (hp / max_hp) * bar_width)
    
    outline_rect = pygame.Rect(x, y, bar_width, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    
    pygame.draw.rect(surface, HEALTH_BG, outline_rect, border_radius=4)
    pygame.draw.rect(surface, HEALTH_RED, fill_rect, border_radius=4)
    pygame.draw.rect(surface, WHITE, outline_rect, 2, border_radius=4)
    
    hp_text = font_hud.render(f"HP: {int(hp)}/{max_hp}", True, WHITE)
    surface.blit(hp_text, (x + 10, y - 2))
    
    score_text = font_hud.render(f"Score: {score}", True, WHITE)
    surface.blit(score_text, (x, y + 30))

def run_game():
    clock = pygame.time.Clock()
    player = Knight(WIDTH // 2, HEIGHT // 2)
    score = 0
    
    enemies = pygame.sprite.Group()
    slime1 = Slime(mapa11 + 150, 200)
    slime2 = Slime(mapa11 + 850, 700)
    
    
    proyectiles = pygame.sprite.Group()
    wizard = Wizard(mapa11 + 760, 200, proyectiles, bloques)
    
    enemies.add(slime1, slime2, wizard)  
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player, slime1, slime2, wizard)
    
    running = True
    while running:
        screen.fill(BLACK)
        screen.blit(mapa, (mapa11, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False 
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player.attack()
                    
        player.update()
        enemies.update(player)

        proyectiles.update()
        for p in proyectiles:
            if p.rect.collidelist(bloques) != -1:
                p.kill()
        for p in proyectiles:
            if p.rect.colliderect(player.rect):
                player.hp -= p.damage 
                player.hit_cooldown = 40
                if player.hp <= 0:
                    running = False 
                p.kill()
        
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect) and player.hit_cooldown == 0:
                player.hp -= 10
                player.hit_cooldown = 45
                if player.hp <= 0:
                    running = False
        
        if player.is_attacking and not player.damage_dealt and player.attack_rect:
            for enemy in enemies:
                if player.attack_rect.colliderect(enemy.rect):
                    enemy.hp -= 30
                    if enemy.hp <= 0:
                        enemy.kill()
                        score += 100
            player.damage_dealt = True
            
        all_sprites.draw(screen)
        proyectiles.draw(screen)
        player.draw_attack(screen)
        
        draw_hud(screen, 30, 30, player.hp, player.max_hp, score)
        
        pygame.display.flip()
        clock.tick(60)




def main_menu():
    play_btn     = pygame.Rect(575, 536, 380, 75)
    settings_btn = pygame.Rect(579, 653, 370, 64)
    stats_btn    = pygame.Rect(575, 761, 375, 62)
    quit_btn     = pygame.Rect(576, 867, 370, 71)

    clock = pygame.time.Clock()

    while True:
        screen.blit(inicio, (0,0))
        mouse_pos = pygame.mouse.get_pos()

        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_btn.collidepoint(mouse_pos):
                    run_game() 
                elif settings_btn.collidepoint(mouse_pos):
                    pass
                elif stats_btn.collidepoint(mouse_pos):
                    pass
                elif quit_btn.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main_menu()