import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Undead Override")

clock = pygame.time.Clock()

# ===== LOAD ASSETS =====
bg_img = pygame.image.load("assets/bg.png")
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

player_img = pygame.image.load("assets/player.png")
player_img = pygame.transform.scale(player_img, (52,52))

zombie_img = pygame.image.load("assets/zombie.png")
zombie_img = pygame.transform.scale(zombie_img, (46, 46))

bullet_img = pygame.image.load("assets/bullet.png")
bullet_img = pygame.transform.scale(bullet_img, (14, 14))

# ===== SETUP =====
player_pos = [400, 300]
player_speed = 5

bullets = []
zombies = []

player_health = 100
score = 0

shoot_cooldown = 0
damage_cooldown = 0
spawn_timer = 0
game_over = False

font = pygame.font.SysFont(None, 36)

def spawn_zombie():
    side = random.choice(["top", "bottom", "left", "right"])
    
    if side == "top":
        x = random.randint(0, WIDTH)
        y = 0
    elif side == "bottom":
        x = random.randint(0, WIDTH)
        y = HEIGHT
    elif side == "left":
        x = 0
        y = random.randint(0, HEIGHT)
    else:
        x = WIDTH
        y = random.randint(0, HEIGHT)

    zombies.append([x, y])

# ===== GAME LOOP =====
while True:

    # INPUT
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    # SHOOTING
    if not game_over and pygame.mouse.get_pressed()[0] and shoot_cooldown <= 0:
        mx, my = pygame.mouse.get_pos()

        dx = mx - player_pos[0]
        dy = my - player_pos[1]

        distance = (dx**2 + dy**2) ** 0.5
        if distance != 0:
            dx /= distance
            dy /= distance

        bullets.append([player_pos[0], player_pos[1], dx, dy])
        shoot_cooldown = 15

    # UPDATE
    if not game_over:

        if shoot_cooldown > 0:
            shoot_cooldown -= 1

        if damage_cooldown > 0:
            damage_cooldown -= 1

        # PLAYER MOVEMENT
        dx, dy = 0, 0

        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1
        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1

        if dx != 0 or dy != 0:
            length = (dx**2 + dy**2) ** 0.5
            dx /= length
            dy /= length

        player_pos[0] += dx * player_speed
        player_pos[1] += dy * player_speed

        player_pos[0] = max(0, min(player_pos[0], WIDTH))
        player_pos[1] = max(0, min(player_pos[1], HEIGHT))

        # SPAWN
        spawn_timer += 1
        if spawn_timer > 60:
            spawn_zombie()
            spawn_timer = 0

        # ZOMBIES
        for zombie in zombies:
            dx = player_pos[0] - zombie[0]
            dy = player_pos[1] - zombie[1]

            distance = (dx**2 + dy**2) ** 0.5

            if distance != 0:
                dx /= distance
                dy /= distance

            speed = min(1 + score * 0.02, 6)
            zombie[0] += dx * speed
            zombie[1] += dy * speed

            px = player_pos[0] - zombie[0]
            py = player_pos[1] - zombie[1]

            if (px**2 + py**2) < (20**2):
                if damage_cooldown <= 0:
                    player_health -= 5
                    damage_cooldown = 20

        # BULLETS
        for bullet in bullets:
            bullet[0] += bullet[2] * 10
            bullet[1] += bullet[3] * 10

        bullets = [b for b in bullets if 0 <= b[0] <= WIDTH and 0 <= b[1] <= HEIGHT]

        # COLLISION
        for bullet in bullets[:]:
            for zombie in zombies[:]:
                dx = bullet[0] - zombie[0]
                dy = bullet[1] - zombie[1]

                if (dx**2 + dy**2) < (15**2):
                    bullets.remove(bullet)
                    zombies.remove(zombie)
                    score += 1
                    break

        if player_health <= 0:
            game_over = True

    # RENDER
    screen.blit(bg_img, (0, 0))

    screen.blit(player_img, (player_pos[0] - 16, player_pos[1] - 16))

    for bullet in bullets:
        screen.blit(bullet_img, (int(bullet[0]) - 5, int(bullet[1]) - 5))

    for zombie in zombies:
        screen.blit(zombie_img, (int(zombie[0]) - 16, int(zombie[1]) - 16))

    # UI
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    health_text = font.render(f"Health: {player_health}", True, (255, 255, 255))

    screen.blit(score_text, (10, 10))
    screen.blit(health_text, (10, 40))

    if game_over:
        text = font.render("GAME OVER - Press R", True, (255, 0, 0))
        screen.blit(text, (WIDTH//2 - 150, HEIGHT//2))

        if keys[pygame.K_r]:
            player_pos = [400, 300]
            bullets.clear()
            zombies.clear()
            player_health = 100
            score = 0
            spawn_timer = 0
            shoot_cooldown = 0
            damage_cooldown = 0
            game_over = False

    pygame.display.flip()
    clock.tick(60)