import pygame
import settings
from settings import *
from settings import IMG_DIR


class Player(pygame.sprite.Sprite):
    def __init__(self, groups, ability_sound):
        super().__init__(groups)
        self.ability_sound = ability_sound

        # --- image loading using IMG_DIR ---
        self.images = {
            (1, 'right'): pygame.image.load(os.path.join(IMG_DIR, 'player1-right.png')).convert_alpha(),
            (1, 'left'):  pygame.image.load(os.path.join(IMG_DIR, 'player1-left.png')).convert_alpha(),
            (2, 'right'): pygame.image.load(os.path.join(IMG_DIR, 'player2-right.png')).convert_alpha(),
            (2, 'left'):  pygame.image.load(os.path.join(IMG_DIR, 'player2-left.png')).convert_alpha(),
        }

        self.image = pygame.image.load(os.path.join(IMG_DIR, 'player2-right.png')).convert_alpha()
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2()
        self.facing = 'right'
        self.speed = 250
        self.can_collide = True
        self.cooldown = 10000
        self.activation_time = -10000
        self.glow = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(self.glow, (0, 100, 255, 100), (40, 40), 40, width=5)

    def update_sprite(self):
        key = (STATS['health'], self.facing)
        self.image = self.images[key]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.size = self.image.get_size()

    def activate_ability(self):
        self.ability_sound.play()
        self.activation_time = pygame.time.get_ticks()
        STATS['ability'] = False
        self.can_collide = False

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += dt * self.speed * self.direction

        recent_keys = pygame.key.get_just_pressed()
        if settings.game_time - self.activation_time >= self.cooldown:
            STATS['ability'] = True
            if recent_keys[pygame.K_SPACE]:
                self.activate_ability()
        if settings.game_time - self.activation_time >= 1000:
            self.can_collide = True

        # blur while invincible
        self.image.set_alpha(100) if not self.can_collide else self.image.set_alpha(255)

        # facing direction
        if self.direction.x > 0:
            self.facing = 'right'
        elif self.direction.x < 0:
            self.facing = 'left'

        self.update_sprite()

        # keep inside window
        self.rect.clamp_ip(pygame.Rect(-10, -10, WINDOW_WIDTH + 20, WINDOW_HEIGHT + 20))


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, groups, speed, record_sound):
        super().__init__(groups)
        self.record_sound = record_sound
        self.width = choice((150, 200, 250, 300))
        filename = f"obstacle_{self.width}.png"

        # --- load using IMG_DIR ---
        self.image = pygame.image.load(os.path.join(IMG_DIR, filename)).convert_alpha()
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH + self.width, randint(0, WINDOW_HEIGHT)))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(-1, 0)
        self.speed = speed

    def update(self, dt):
        global STATS
        self.rect.centerx -= self.speed * dt
        if self.rect.right < 0:
            STATS['score'] += 1
            if STATS['score'] == STATS['record'] + 1:
                self.record_sound.play()
            self.kill()
