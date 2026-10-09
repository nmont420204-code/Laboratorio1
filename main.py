import pygame
import sys
import math
import random
import json
import os
from wizard import Wizard

pygame.init()
pygame.mixer.init()

pygame.mixer.music.load("sounds/musica.mp3")
pygame.mixer.music.play(-1)

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "difficulty": "Normal",
    "sfx_vol": 0.5,
    "music_vol": 0.5
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

GAME_SETTINGS = load_settings()

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()

scale_ratio = HEIGHT / 1024.0

inicio = pygame.transform.scale(pygame.image.load("interfaz.png").convert_alpha(), (WIDTH, HEIGHT))
pygame.display.set_caption("BLUE KNIGHT")

mapa = pygame.transform.scale(pygame.image.load("MAPA.png").convert_alpha(), (WIDTH, HEIGHT))

floor_left = int(WIDTH * 0.28)
floor_right = int(WIDTH * 0.73) 
floor_top = int(HEIGHT * 0.08)
floor_bottom = int(HEIGHT * 0.86) 

bloque_exterior = pygame.Rect(floor_left, floor_top, floor_right - floor_left, floor_bottom - floor_top)

bloques = [
    pygame.Rect(floor_left, floor_top, floor_right - floor_left, 15),
    pygame.Rect(floor_left, floor_bottom - 15, floor_right - floor_left, 15),
    pygame.Rect(floor_left, floor_top, 15, floor_bottom - floor_top),
    pygame.Rect(floor_right - 15, floor_top, 15, floor_bottom - floor_top),
]
WHITE = (255, 255, 255)
BLACK = (20, 20, 25)
BTN_COLOR = (70, 70, 80)
BTN_HOVER = (120, 120, 130)
HEALTH_RED = (200, 30, 30)
HEALTH_BG = (50, 50, 50)
GOLD = (255, 215, 0)
GREEN = (50, 200, 50)

font_title = pygame.font.SysFont("impact", int(80 * scale_ratio))
font_btn = pygame.font.SysFont("arial", int(40 * scale_ratio), bold=True)
font_hud = pygame.font.SysFont("arial", int(24 * scale_ratio), bold=True)
font_big = pygame.font.SysFont("arial", int(36 * scale_ratio), bold=True)

try:
    snd_attack = pygame.mixer.Sound("sounds/espada_ataque.wav")
    snd_hit = pygame.mixer.Sound("sounds/daño.wav")
    snd_shoot = pygame.mixer.Sound("sounds/bola_fuego.wav")
except:
    snd_attack = snd_hit = snd_shoot = None

def update_volumes():
    if snd_attack: snd_attack.set_volume(GAME_SETTINGS["sfx_vol"])
    if snd_hit: snd_hit.set_volume(GAME_SETTINGS["sfx_vol"])
    if snd_shoot: snd_shoot.set_volume(GAME_SETTINGS["sfx_vol"])
    pygame.mixer.music.set_volume(GAME_SETTINGS["music_vol"])

update_volumes()

class Knight(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()  
        size = int(60 * scale_ratio)
        self.sprites = {
            "up": pygame.transform.scale(pygame.image.load("Tiles/tile_0087_espalda.png").convert_alpha(), (size, size)),
            "down": pygame.transform.scale(pygame.image.load("Tiles/tile_0087.png").convert_alpha(), (size, size)),
            "left": pygame.transform.scale(pygame.image.load("Tiles/tile_0087_izquierda.png").convert_alpha(), (size, size)),
            "right": pygame.transform.scale(pygame.image.load("Tiles/tile_0087_derecha.png").convert_alpha(), (size, size))
        }
        self.direction = "right"
        self.image = self.sprites[self.direction]
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5 * scale_ratio
        self.max_hp = 100
        self.hp = 100
        self.hit_cooldown = 0
        self.damage = 30 
        
        atk_size = int(120 * scale_ratio)
        self.attack_frames = [
            pygame.transform.scale(pygame.image.load("Tiles/ataque1.png").convert_alpha(), (atk_size, atk_size)),
            pygame.transform.scale(pygame.image.load("Tiles/ataque2.png").convert_alpha(), (atk_size, atk_size)),
            pygame.transform.scale(pygame.image.load("Tiles/ataque3.png").convert_alpha(), (atk_size, atk_size)),
            pygame.transform.scale(pygame.image.load("Tiles/ataque4.png").convert_alpha(), (atk_size, atk_size))
        ]
        
        self.is_attacking = False
        self.current_frame = 0
        self.animation_speed = 0.25
        self.attack_angle = 0
        self.attack_rect = None
        self.damage_dealt = False
        self.attack_cooldown = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if self.hit_cooldown > 0: self.hit_cooldown -= 1
        if self.attack_cooldown > 0: self.attack_cooldown -= 1 
        
        if not self.is_attacking:
            margen = int(-26 * scale_ratio)
            
            y_antes = self.rect.y
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.rect.y -= self.speed
                self.direction = "up"
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.rect.y += self.speed
                self.direction = "down"

            if self.rect.inflate(margen, margen).collidelist(bloques) != -1:
                self.rect.y = y_antes
            
            x_antes = self.rect.x
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.rect.x -= self.speed
                self.direction = "left"
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.rect.x += self.speed
                self.direction = "right"

            if self.rect.inflate(margen, margen).collidelist(bloques) != -1:
                self.rect.x = x_antes
                
            self.image = self.sprites[self.direction]
                
        self.rect.clamp_ip(bloque_exterior)

        if self.is_attacking:
            self.current_frame += self.animation_speed
            
            offset_dist = 50 * scale_ratio
            offset_x = math.cos(math.radians(self.attack_angle)) * offset_dist
            offset_y = -math.sin(math.radians(self.attack_angle)) * offset_dist
            
            atk_box = int(80 * scale_ratio)
            self.attack_rect = pygame.Rect(0, 0, atk_box, atk_box)
            self.attack_rect.center = (self.rect.centerx + offset_x, self.rect.centery + offset_y)
            
            if self.current_frame >= len(self.attack_frames):
                self.is_attacking = False
                self.current_frame = 0
                self.attack_rect = None
        if self.is_attacking:
            self.current_frame += self.animation_speed
            
            offset_dist = 50 * scale_ratio
            offset_x = math.cos(math.radians(self.attack_angle)) * offset_dist
            offset_y = -math.sin(math.radians(self.attack_angle)) * offset_dist
            
            atk_box = int(80 * scale_ratio)
            self.attack_rect = pygame.Rect(0, 0, atk_box, atk_box)
            self.attack_rect.center = (self.rect.centerx + offset_x, self.rect.centery + offset_y)
            
            if self.current_frame >= len(self.attack_frames):
                self.is_attacking = False
                self.current_frame = 0
                self.attack_rect = None
    def attack(self):
        if not self.is_attacking and self.attack_cooldown == 0:
            self.is_attacking = True
            self.current_frame = 0
            self.damage_dealt = False
            self.attack_cooldown = 25
            
            if snd_attack: snd_attack.play()
            
            if self.direction == "right": self.attack_angle = 0
            elif self.direction == "left": self.attack_angle = 180
            elif self.direction == "up": self.attack_angle = 90
            elif self.direction == "down": self.attack_angle = 270

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
        size = int(40 * scale_ratio)
        self.image = pygame.image.load("Tiles/tile_0108.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2 * scale_ratio
        self.damage = 10
        self.hp = 30

    def update(self, target, enemies_group):
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            dx /= dist; dy /= dist
            
            y_antes = self.rect.y
            self.rect.y += dy * self.speed
            idx_y = self.rect.collidelist(bloques)
            col_y = idx_y != -1
            if col_y: 
                self.rect.y = y_antes
                
            x_antes = self.rect.x
            self.rect.x += dx * self.speed
            idx_x = self.rect.collidelist(bloques)
            col_x = idx_x != -1
            if col_x: 
                self.rect.x = x_antes
            
            if col_x and not col_y:
                move_y = dy
                if abs(dy) < 0.1:
                    move_y = -1 if self.rect.centery < bloques[idx_x].centery else 1
                self.rect.y += (1 if move_y > 0 else -1) * (self.speed * 0.8)
            elif col_y and not col_x:
                move_x = dx
                if abs(dx) < 0.1:
                    move_x = -1 if self.rect.centerx < bloques[idx_y].centerx else 1
                self.rect.x += (1 if move_x > 0 else -1) * (self.speed * 0.8)

            for other in enemies_group:
                if other != self and self.rect.colliderect(other.rect):
                    ox = self.rect.centerx - other.rect.centerx
                    oy = self.rect.centery - other.rect.centery
                    if ox == 0 and oy == 0:
                        ox, oy = random.choice([-1, 1]), random.choice([-1, 1])
                    odist = math.hypot(ox, oy)
                    if odist > 0:
                        self.rect.x += (ox / odist) * (self.speed * 1.2)
                        self.rect.y += (oy / odist) * (self.speed * 1.2)
class Cyclops(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        size = int(60 * scale_ratio)
        try:
            self.image = pygame.image.load("Tiles/tile_0109.png").convert_alpha()
        except:
            self.image = pygame.image.load("Tiles/tile_0108.png").convert_alpha() 
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 1.2 * scale_ratio
        self.damage = 20
        self.hp = 70

    def update(self, target, enemies_group):
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx /= dist; dy /= dist
            
            y_antes = self.rect.y
            self.rect.y += dy * self.speed
            idx_y = self.rect.collidelist(bloques)
            col_y = idx_y != -1
            if col_y: 
                self.rect.y = y_antes

            x_antes = self.rect.x
            self.rect.x += dx * self.speed
            idx_x = self.rect.collidelist(bloques)
            col_x = idx_x != -1
            if col_x: 
                self.rect.x = x_antes
            
            if col_x and not col_y:
                move_y = dy
                if abs(dy) < 0.1:
                    move_y = -1 if self.rect.centery < bloques[idx_x].centery else 1
                self.rect.y += (1 if move_y > 0 else -1) * (self.speed * 0.8)
            elif col_y and not col_x:
                move_x = dx
                if abs(dx) < 0.1:
                    move_x = -1 if self.rect.centerx < bloques[idx_y].centerx else 1
                self.rect.x += (1 if move_x > 0 else -1) * (self.speed * 0.8)

            for other in enemies_group:
                if other != self and self.rect.colliderect(other.rect):
                    ox = self.rect.centerx - other.rect.centerx
                    oy = self.rect.centery - other.rect.centery
                    if ox == 0 and oy == 0:
                        ox, oy = random.choice([-1, 1]), random.choice([-1, 1])
                    odist = math.hypot(ox, oy)
                    if odist > 0:
                        self.rect.x += (ox / odist) * (self.speed * 1.2)
                        self.rect.y += (oy / odist) * (self.speed * 1.2)

            self.rect.clamp_ip(bloque_exterior)
class DropItem(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        super().__init__()
        self.type = item_type
        size = int(50 * scale_ratio) # Aumentado de 30 a 50 para que se vean más grandes
        img_path = "Tiles/tile_0115.png" if item_type == "potion" else "Tiles/tile_0106.png"
        try:
            self.image = pygame.image.load(img_path).convert_alpha()
        except:
            self.image = pygame.Surface((size, size))
            self.image.fill(HEALTH_RED if item_type == "potion" else GOLD)
            
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect(center=(x, y))
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 10000 

    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > self.duration:
            self.kill()

def draw_hud(surface, x, y, player, score, level, round_num):
    bar_width = int(200 * scale_ratio)
    bar_height = int(22 * scale_ratio)
    fill = max(0, (player.hp / player.max_hp) * bar_width)
    
    outline_rect = pygame.Rect(x, y, bar_width, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    
    pygame.draw.rect(surface, HEALTH_BG, outline_rect, border_radius=4)
    pygame.draw.rect(surface, HEALTH_RED, fill_rect, border_radius=4)
    pygame.draw.rect(surface, WHITE, outline_rect, 2, border_radius=4)
    
    hp_text = font_hud.render(f"HP: {int(player.hp)}/{player.max_hp}", True, WHITE)
    surface.blit(hp_text, (x + 10, y - 2))
    
    score_text = font_hud.render(f"Score: {score}", True, WHITE)
    dmg_text = font_hud.render(f"Daño: {player.damage}", True, GOLD)
    surface.blit(score_text, (x, y + int(30 * scale_ratio)))
    surface.blit(dmg_text, (x, y + int(60 * scale_ratio)))

    level_text = font_big.render(f"Nivel: {level} - Ronda: {round_num}/4", True, WHITE)
    surface.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, int(20 * scale_ratio)))

def random_valid_pos(size_w, size_h):
    while True:
        x = random.randint(bloque_exterior.left, bloque_exterior.right)
        y = random.randint(bloque_exterior.top, bloque_exterior.bottom)
        temp_rect = pygame.Rect(x - size_w//2, y - size_h//2, size_w, size_h)
        if temp_rect.collidelist(bloques) == -1:
            return x, y

def spawn_wave(level, round_num, enemies_group, all_sprites, proyectiles, items_group):
    mult = {"Fácil": 0.5, "Normal": 1.0, "Difícil": 1.5}[GAME_SETTINGS["difficulty"]]
    
    num_slimes = int((level * 2 + round_num) * mult)
    num_cyclops = int((level + (round_num // 2)) * mult)
    num_wizards = 1 if round_num == 4 else 0 
    
    if num_slimes == 0 and num_cyclops == 0: num_slimes = 1

    for _ in range(num_slimes):
        x, y = random_valid_pos(int(40*scale_ratio), int(40*scale_ratio))
        s = Slime(x, y)
        enemies_group.add(s); all_sprites.add(s)

    for _ in range(num_cyclops):
        x, y = random_valid_pos(int(60*scale_ratio), int(60*scale_ratio))
        c = Cyclops(x, y)
        enemies_group.add(c); all_sprites.add(c)

    for _ in range(num_wizards):
        x, y = random_valid_pos(int(50*scale_ratio), int(50*scale_ratio))
        w = Wizard(x, y, proyectiles, bloques)
        enemies_group.add(w); all_sprites.add(w)

    px, py = random_valid_pos(int(30*scale_ratio), int(30*scale_ratio))
    potion = DropItem(px, py, "potion")
    items_group.add(potion); all_sprites.add(potion)

    sx, sy = random_valid_pos(int(30*scale_ratio), int(30*scale_ratio))
    sword = DropItem(sx, sy, "sword")
    items_group.add(sword); all_sprites.add(sword)

def blur_surface(surface):
    small = pygame.transform.smoothscale(surface, (WIDTH // 10, HEIGHT // 10))
    blur = pygame.transform.smoothscale(small, (WIDTH, HEIGHT))
    dark_overlay = pygame.Surface((WIDTH, HEIGHT))
    dark_overlay.fill((0, 0, 0))
    dark_overlay.set_alpha(150)
    blur.blit(dark_overlay, (0,0))
    return blur

def end_screen(bg_surface, score, level, round_num, is_victory):
    clock = pygame.time.Clock()
    running = True
    while running:
        screen.blit(bg_surface, (0, 0))
        
        main_text = "¡VICTORIA!" if is_victory else "HAS PERDIDO"
        color = GREEN if is_victory else HEALTH_RED
        
        title = font_title.render(main_text, True, color)
        score_lbl = font_btn.render(f"Puntuación final: {score}", True, WHITE)
        level_lbl = font_btn.render(f"Llegaste al Nivel {level} - Ronda {round_num}", True, WHITE)
        cont_lbl = font_hud.render("Haz clic o presiona ESCAPE para salir", True, GOLD)

        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - int(150 * scale_ratio)))
        screen.blit(score_lbl, (WIDTH//2 - score_lbl.get_width()//2, HEIGHT//2 - int(20 * scale_ratio)))
        screen.blit(level_lbl, (WIDTH//2 - level_lbl.get_width()//2, HEIGHT//2 + int(40 * scale_ratio)))
        screen.blit(cont_lbl, (WIDTH//2 - cont_lbl.get_width()//2, HEIGHT//2 + int(150 * scale_ratio)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                running = False

        pygame.display.flip()
        clock.tick(60)

def run_game():
    clock = pygame.time.Clock()
    player = Knight(WIDTH // 2, HEIGHT // 2)
    score = 0
    
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    proyectiles = pygame.sprite.Group()
    items = pygame.sprite.Group()
    all_sprites.add(player)
    
    level = 1
    round_num = 1
    max_levels = 5
    
    spawn_wave(level, round_num, enemies, all_sprites, proyectiles, items)
    prev_proj_count = 0 
    running = True
    won = False
    
    while running:
        screen.fill(BLACK)
        screen.blit(mapa, (0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings(GAME_SETTINGS)
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    bg_snap = screen.copy()
                    blurred_bg = blur_surface(bg_snap)
                    settings_menu(blurred_bg)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                player.attack()
                    
        if len(enemies) == 0:
            round_num += 1
            if round_num > 4:
                round_num = 1
                level += 1
                if level > max_levels:
                    won = True
                    running = False 
            if running:
                spawn_wave(level, round_num, enemies, all_sprites, proyectiles, items)

        player.update()
        enemies.update(player, enemies)
        proyectiles.update()
        items.update()

        current_proj_count = len(proyectiles)
        if current_proj_count > prev_proj_count and snd_shoot:
            snd_shoot.play()
        prev_proj_count = current_proj_count

        for p in proyectiles:
            if p.rect.collidelist(bloques) != -1: p.kill()
            
        for p in proyectiles:
            if p.rect.colliderect(player.rect):
                player.hp -= p.damage 
                player.hit_cooldown = 40
                if snd_hit: snd_hit.play() 
                if player.hp <= 0: running = False 
                p.kill()
        
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect) and player.hit_cooldown == 0:
                player.hp -= getattr(enemy, "damage", 10)
                player.hit_cooldown = 45
                if snd_hit: snd_hit.play() 
                if player.hp <= 0: running = False
        
        hits_items = pygame.sprite.spritecollide(player, items, True)
        for drop in hits_items:
            if drop.type == "potion":
                player.hp = min(player.hp + 30, player.max_hp)
            elif drop.type == "sword":
                player.damage += 10 
        
        if player.is_attacking and not player.damage_dealt and player.attack_rect:
            for enemy in enemies:
                if player.attack_rect.colliderect(enemy.rect):
                    enemy.hp -= player.damage 
                    if enemy.hp <= 0:
                        enemy.kill()
                        score += 100
            player.damage_dealt = True
            
        all_sprites.draw(screen)
        proyectiles.draw(screen)
        player.draw_attack(screen)
        
        draw_hud(screen, int(30 * scale_ratio), int(30 * scale_ratio), player, score, level, round_num)
        
        pygame.display.flip()
        clock.tick(60)

    bg_snap = screen.copy()
    blurred_bg = blur_surface(bg_snap)
    end_screen(blurred_bg, score, level, round_num, won)

def settings_menu(bg_surface):
    clock = pygame.time.Clock()
    
    btn_w, btn_h = int(50 * scale_ratio), int(50 * scale_ratio)
    btn_sfx_menos = pygame.Rect(WIDTH//2 - int(150 * scale_ratio), HEIGHT//2 - int(100 * scale_ratio), btn_w, btn_h)
    btn_sfx_mas   = pygame.Rect(WIDTH//2 + int(100 * scale_ratio), HEIGHT//2 - int(100 * scale_ratio), btn_w, btn_h)
    
    btn_mus_menos = pygame.Rect(WIDTH//2 - int(150 * scale_ratio), HEIGHT//2, btn_w, btn_h)
    btn_mus_mas   = pygame.Rect(WIDTH//2 + int(100 * scale_ratio), HEIGHT//2, btn_w, btn_h)
    
    btn_diff = pygame.Rect(WIDTH//2 - int(100 * scale_ratio), HEIGHT//2 + int(100 * scale_ratio), int(200 * scale_ratio), btn_h)
    btn_back = pygame.Rect(WIDTH//2 - int(100 * scale_ratio), HEIGHT//2 + int(250 * scale_ratio), int(200 * scale_ratio), btn_h)

    dificultades = ["Fácil", "Normal", "Difícil"]
    idx_diff = dificultades.index(GAME_SETTINGS["difficulty"])

    running = True
    while running:
        screen.blit(bg_surface, (0, 0))
        
        title = font_title.render("AJUSTES", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - int(250 * scale_ratio)))
        
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings(GAME_SETTINGS)
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                save_settings(GAME_SETTINGS)
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_sfx_menos.collidepoint(mouse_pos):
                    GAME_SETTINGS["sfx_vol"] = max(0.0, GAME_SETTINGS["sfx_vol"] - 0.1)
                    update_volumes()
                if btn_sfx_mas.collidepoint(mouse_pos):
                    GAME_SETTINGS["sfx_vol"] = min(1.0, GAME_SETTINGS["sfx_vol"] + 0.1)
                    update_volumes()
                    
                if btn_mus_menos.collidepoint(mouse_pos):
                    GAME_SETTINGS["music_vol"] = max(0.0, GAME_SETTINGS["music_vol"] - 0.1)
                    update_volumes()
                if btn_mus_mas.collidepoint(mouse_pos):
                    GAME_SETTINGS["music_vol"] = min(1.0, GAME_SETTINGS["music_vol"] + 0.1)
                    update_volumes()
                    
                if btn_diff.collidepoint(mouse_pos):
                    idx_diff = (idx_diff + 1) % len(dificultades)
                    GAME_SETTINGS["difficulty"] = dificultades[idx_diff]
                    
                if btn_back.collidepoint(mouse_pos):
                    save_settings(GAME_SETTINGS) 
                    running = False

        def draw_option(text, rect_less, rect_more, val_text, y):
            label = font_btn.render(text, True, WHITE)
            screen.blit(label, (WIDTH//2 - int(350 * scale_ratio), y))
            pygame.draw.rect(screen, BTN_COLOR, rect_less)
            pygame.draw.rect(screen, BTN_COLOR, rect_more)
            screen.blit(font_btn.render("-", True, WHITE), (rect_less.x + (rect_less.w//2 - 10), rect_less.y))
            screen.blit(font_btn.render("+", True, WHITE), (rect_more.x + (rect_more.w//2 - 10), rect_more.y))
            val_lbl = font_btn.render(val_text, True, GOLD)
            screen.blit(val_lbl, (WIDTH//2 - val_lbl.get_width()//2, y))

        draw_option("Efectos:", btn_sfx_menos, btn_sfx_mas, f"{int(GAME_SETTINGS['sfx_vol']*100)}%", HEIGHT//2 - int(100 * scale_ratio))
        draw_option("Música:", btn_mus_menos, btn_mus_mas, f"{int(GAME_SETTINGS['music_vol']*100)}%", HEIGHT//2)
        
        pygame.draw.rect(screen, BTN_COLOR, btn_diff)
        diff_text = font_btn.render(GAME_SETTINGS["difficulty"], True, GOLD)
        screen.blit(diff_text, (btn_diff.x + btn_diff.w//2 - diff_text.get_width()//2, btn_diff.y))
        
        pygame.draw.rect(screen, HEALTH_RED, btn_back)
        back_text = font_btn.render("Volver", True, WHITE)
        screen.blit(back_text, (btn_back.x + btn_back.w//2 - back_text.get_width()//2, btn_back.y))
        
        pygame.display.flip()
        clock.tick(60)

def main_menu():
    pb_w, pb_h = int(380 * scale_ratio), int(75 * scale_ratio)
    play_btn     = pygame.Rect(WIDTH//2 - pb_w//2, HEIGHT//2, pb_w, pb_h)
    settings_btn = pygame.Rect(WIDTH//2 - pb_w//2, HEIGHT//2 + int(115 * scale_ratio), pb_w, pb_h)
    stats_btn    = pygame.Rect(WIDTH//2 - pb_w//2, HEIGHT//2 + int(225 * scale_ratio), pb_w, pb_h)
    quit_btn     = pygame.Rect(WIDTH//2 - pb_w//2, HEIGHT//2 + int(330 * scale_ratio), pb_w, pb_h)

    clock = pygame.time.Clock()

    while True:
        screen.blit(inicio, (0,0))
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_btn.collidepoint(mouse_pos):
                    run_game() 
                elif settings_btn.collidepoint(mouse_pos):
                    bg_snap = screen.copy()
                    blurred_bg = blur_surface(bg_snap)
                    settings_menu(blurred_bg)
                elif stats_btn.collidepoint(mouse_pos):
                    pass
                elif quit_btn.collidepoint(mouse_pos):
                    pygame.quit(); sys.exit()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main_menu()