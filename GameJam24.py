import pygame
import sys
import os
import random
import json
from pygame.locals import *
from scripts.entities import PhysicsEntity
from scripts.Tilemap import Tilemap

pygame.init()

SIZE = WIDTH, HEIGHT = (700, 700)
DISPLAY = pygame.display.set_mode(SIZE)
FPS = pygame.time.Clock()
BASE_SPEED = 7
BASE_HEALTH = 200
RED = (225, 0, 0)
GREEN = (0, 225, 0)
BLUE = (0, 0, 225)
OVERLAY = (200, 30, 30)

BG = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'Floor.png')).convert(), (WIDTH, HEIGHT))
WALL1 = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'Room1Wall.png')).convert(), (WIDTH, HEIGHT))
WALL1.set_colorkey((0, 0, 0))
WALL2 = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'Room2Wall.png')).convert(), (WIDTH, HEIGHT))
WALL2.set_colorkey((0, 0, 0))
WALL3 = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'Room3Wall.png')).convert(), (WIDTH, HEIGHT))
WALL3.set_colorkey((0, 0, 0))
GRASS = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'Grass.png')).convert(), (WIDTH, HEIGHT))
GRASS.set_colorkey((0, 0, 0))
SPAWN2 = (20, 150)

class Character(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()

        if type == "Boss":
            self.walk_anim = [
            pygame.transform.scale(pygame.image.load(os.path.join("Assets", type, f"{type}_walk_one.png")).convert_alpha(), (250, 250)),
            pygame.transform.scale(pygame.image.load(os.path.join("Assets", type, f"{type}_walk_two.png")).convert_alpha(), (250, 250)),
            pygame.transform.scale(pygame.image.load(os.path.join("Assets", type, f"{type}_idle.png")).convert_alpha(), (250, 250)),
            pygame.transform.scale(pygame.image.load(os.path.join("Assets", type, f"{type}_walk_four.png")).convert_alpha(), (250, 250)),
            ]
            self.surface = pygame.Surface((250,250))
            self.rect = self.surface.get_rect()
            self.direction = 1
            self.step_count = 0
            self.rect.clamp_ip(pygame.display.get_surface().get_rect())
        else:
            self.walk_anim = [
            pygame.image.load(os.path.join("Assets", type, f"{type}_walk_one.png")).convert_alpha(),
            pygame.image.load(os.path.join("Assets", type, f"{type}_walk_two.png")).convert_alpha(),
            pygame.image.load(os.path.join("Assets", type, f"{type}_walk_three.png")).convert_alpha(),
            pygame.image.load(os.path.join("Assets", type, f"{type}_walk_four.png")).convert_alpha(),
            ]
            self.surface = pygame.Surface((25, 25))
            self.rect = self.surface.get_rect()
            self.direction = 1
            self.step_count = 0
            self.rect.clamp_ip(pygame.display.get_surface().get_rect())


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((15, 15))
        self.image.fill((32, 40, 253))
        self.rect = self.image.get_rect(center=(x,y))
        self.speed = 13
        self.direction = direction

    def update(self):
        if self.direction == 2:
            self.rect.y -= self.speed
        elif self.direction == 3:
            self.rect.y += self.speed
        elif self.direction == 0:
            self.rect.x -= self.speed
        elif self.direction == 1:
            self.rect.x += self.speed

        if (self.rect.x < 0 or self.rect.x > WIDTH or self.rect.y < 0 or self.rect.y > HEIGHT):
            self.kill()
        pass

class Player(Character, PhysicsEntity):
    def __init__(self):
        super().__init__("Player")
        self.rect = self.surface.get_rect(center=(WIDTH/2, HEIGHT/2))
        self.x_speed = BASE_SPEED
        self.y_speed = BASE_SPEED
        self.health = BASE_HEALTH
        self.direction = 3

        self.shoot_cooldown = 0
        self.cooldown_time = 45

    def update(self):
        render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
        self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
        self.player.render(self.display, offset = render_scroll)

    def move(self):
        pressed_keys = pygame.key.get_pressed()
        self.step_count += 1

        move_x = 0
        move_y = 0

        if pressed_keys[K_LEFT]:
            move_x = -1
            self.direction = 0  # Facing left
        if pressed_keys[K_RIGHT]:
            move_x = 1
            self.direction = 1  # Facing right
        if pressed_keys[K_UP]:
            move_y = -1
            self.direction = 2  # Facing up
        if pressed_keys[K_DOWN]:
            move_y = 1
            self.direction = 3  # Facing down

        if move_x != 0 and move_y != 0:
            length = (move_x ** 2 + move_y ** 2) ** 0.4
            move_x /= length
            move_y /= length

        self.rect.move_ip(move_x * self.x_speed, move_y * self.y_speed)

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

        if pressed_keys[K_SPACE] and self.shoot_cooldown == 0:
            self.shoot()
            self.shoot_cooldown = self.cooldown_time

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.step_count >= 59:
            self.step_count = 0

    def shoot(self):
        projectile = Projectile(self.rect.centerx, self.rect.centery, self.direction)
        projectiles.add(projectile)

class Enemy(Character):
    def __init__(self):
        super().__init__("Enemy")
        self.x_speed = 3
        self.y_speed = 3
        self.hit_time = 0
        self.hit_duration = 200
        self.is_dead = False

    def move(self, player):
        if self.is_dead:
            return

        direction_x = player.rect.centerx - self.rect.centerx
        direction_y = player.rect.centery - self.rect.centery

        distance = (direction_x ** 2 + direction_y ** 2) ** 0.5
        if distance > 0:
            direction_x /= distance
            direction_y /= distance

        self.rect.x += direction_x * self.x_speed
        self.rect.y += direction_y * self.y_speed

        if self.step_count >= 59:
            self.step_count = 0

        self.step_count += 1

    def hit(self):
        self.hit_time = pygame.time.get_ticks()
        self.is_dead = True

    def is_hit(self):
        return pygame.time.get_ticks() - self.hit_time < self.hit_duration

    def draw(self, display):
        if self.is_dead:
            return
        
        current_enemy_sprite = self.walk_anime[self.step_count // 15]
        if self.direction == 0:
            current_enemy_sprite = pygame.transform.flip(current_enemy_sprite, True, False)

        if self.is_hit():
            red_tint = pygame.Surface(current_enemy_sprite.get_size())
            red_tint.fill(RED)
            red_tint.set_alpha(128)
            current_enemy_sprite.blit(red_tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        display.blit(current_enemy_sprite, self.rect)

class Boss(Character):
    def __init__(self):
        super().__init__("Boss")
        self.x_speed = 1.5
        self.y_speed = 1.5
        self.bossHp = 15
        self.backUp = 0
        self.is_dead = False
        
        # Update surface size and rect size to match the larger sprite size
        self.surface = pygame.Surface((250, 250))  # Surface size matches the sprite size
        self.rect = self.surface.get_rect()  # Adjust starting position if needed
        self.direction = 1
        self.step_count = 0
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())

        # Charge state management
        self.is_charging = False
        self.charge_start_time = 0
        self.charge_duration = 125
        self.charge_interval = 2500  # Charge every 5 seconds

    def move(self, player):
        direction_x = player.rect.centerx - self.rect.centerx
        direction_y = player.rect.centery - self.rect.centery

        distance = (direction_x ** 2 + direction_y ** 2) ** 0.5
        if distance > 0:
            direction_x /= distance
            direction_y /= distance

        self.rect.x += direction_x * self.x_speed
        self.rect.y += direction_y * self.y_speed

        if self.step_count >= 59:
            self.step_count = 0

        self.step_count += 1

    def charge(self):
        # Start charging only if it's time for it (every 5 seconds)
        if not self.is_charging and pygame.time.get_ticks() - self.charge_start_time >= self.charge_interval:
            self.is_charging = True
            self.x_speed = 7.5
            self.y_speed = 7.5
            self.charge_start_time = pygame.time.get_ticks()  # Record the time when charging starts

    def update(self):
        # Stop charging after 1 second
        if self.is_charging and pygame.time.get_ticks() - self.charge_start_time >= self.charge_duration:
            self.is_charging = False
            self.x_speed = 1.5
            self.y_speed = 1.5

    
            
        

def draw_window(display, background, wall3, player, enemies, boss):
    display.blit(background, (0, 0))
    display.blit(wall3, (0, 0))

    # Draw the enemies
    for enemy in enemies:
        current_enemy_sprite = enemy.walk_anim[enemy.step_count // 15]
        if enemy.direction == 0:
            current_enemy_sprite = pygame.transform.flip(current_enemy_sprite, True, False)
        display.blit(current_enemy_sprite, enemy.rect)

    if not boss.is_dead:
        # Draw the boss
        current_boss_sprite = boss.walk_anim[boss.step_count // 15]
        if boss.direction == 0:
            current_boss_sprite = pygame.transform.flip(current_boss_sprite, True, False)
        display.blit(current_boss_sprite, boss.rect)

    # Check for collisions with player and enemies
    if pygame.sprite.spritecollideany(player, enemies):
        player.health -= 1
        display.fill(OVERLAY, special_flags=pygame.BLEND_MULT)
    if not boss.is_dead:
        if pygame.sprite.collide_rect(player, boss):
            player.health -= 1
            display.fill(OVERLAY, special_flags=pygame.BLEND_MULT)

    # Draw player sprite with rotation based on direction
    current_player_sprite = player.walk_anim[player.step_count // 15]

    if player.direction == 0:
        current_player_sprite = pygame.transform.rotate(current_player_sprite, 90)
    elif player.direction == 1:
        current_player_sprite = pygame.transform.rotate(current_player_sprite, 270)
    elif player.direction == 2:
        current_player_sprite = pygame.transform.rotate(current_player_sprite, 0)
    elif player.direction == 3:
        current_player_sprite = pygame.transform.rotate(current_player_sprite, 180)

    display.blit(current_player_sprite, player.rect)

    # Draw projectiles
    projectiles.draw(display)

    # Draw the player's health bar
    pygame.draw.rect(display, GREEN, (20, 20, player.health, 20))
    pygame.draw.rect(display, RED, (player.health + 20, 20, BASE_HEALTH - player.health, 20))

    # Update the display
    pygame.display.update()


player = Player()
enemies = pygame.sprite.Group()
boss = Boss()  

# Create a couple of enemies
for _ in range(2):
    enemy = Enemy()
    enemy.rect.topleft = (random.randint(0, WIDTH), random.randint(0, HEIGHT))  
    enemies.add(enemy)

# Create a group for projectiles
projectiles = pygame.sprite.Group()

# Custom event to trigger boss charging
BOSS_CHARGE_EVENT = pygame.USEREVENT + 1

# Set a timer for boss charge event every 5 seconds
pygame.time.set_timer(BOSS_CHARGE_EVENT, 2500)

# Main game loop
while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # If the player is dead, quit the game
        if player.health <= 0:
            pygame.quit()
            sys.exit()

        # Handle the boss charge event
        if event.type == BOSS_CHARGE_EVENT:
            boss.charge()
        elif event.type != BOSS_CHARGE_EVENT:
            boss.update()

    # Update the player and enemy positions
    player.move()

    for enemy in enemies:
        enemy.move(player)

    boss.move(player)

    # Update projectiles
    projectiles.update()

    

    # Check for projectile collisions with enemies
    for projectile in projectiles:
        hit_enemies = pygame.sprite.spritecollide(projectile, enemies, False)

        if boss.rect.colliderect(projectile.rect):
            boss.bossHp -= 1
            projectile.kill()
            boss.backUp += 1
            if boss.backUp >= 5:
                boss.backUp = 0
                backUpEnemy = Enemy()
                backUpEnemy.rect.topleft = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
                enemies.add(backUpEnemy)
                


            if boss.bossHp <= 0:
                boss.is_dead = True
                if boss.is_dead:
                    boss.kill()
                
        
        for enemy in hit_enemies:
            enemy.kill()
            projectile.kill()

    for enemy in enemies:
        if enemy.is_dead:
            enemy.kill()

    # Draw the game window
    draw_window(DISPLAY, BG, WALL2, player, enemies, boss)

    # Cap the framerate
    FPS.tick(60)