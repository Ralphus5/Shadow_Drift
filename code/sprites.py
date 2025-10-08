"""Sprite classes for player and obstacles."""

import settings
from settings import *


class Player(pygame.sprite.Sprite):
    """Player sprite: handles movement, abilities, and player presisentation."""

    def __init__(self, groups, sprite_variants, ability_sound):
        super().__init__(groups)

        # --- parameters ---
        self.sprite_variants = sprite_variants
        self.ability_sound = ability_sound
        
        # --- gameplay attributes ---
        self.is_alive = True
        self.health = 2
        self.speed = DEFAULT_PLAYER_SPEED

        # --- ability system ---
        self.can_collide = True
        self.ability_ready = True
        self.ability_start_time = ABILITY_UNUSED
        self.ability_cooldown = PLAYER_ABILITY_COOLDOWN
        self.ability_duration = PLAYER_ABILITY_DURATION

        # --- rendering ---
        self.facing = 'right'
        self.image = self.sprite_variants[(self.health, self.facing)]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.glow = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(self.glow, COLOR['blue_player_glow'], (40, 40), 40, width=5)

        # --- motion setup ---
        self.direction = pygame.Vector2()

    def activate_ability(self):
        self.ability_sound.play()
        self.ability_start_time = pygame.time.get_ticks()
        self.ability_ready = False
        self.can_collide = False

    def keep_in_window(self):
        self.rect.clamp_ip(pygame.Rect(-10, -10, WINDOW_WIDTH + 20, WINDOW_HEIGHT + 20))

    def handle_input(self, dt):
        # --- check user input ---
        keys = pygame.key.get_pressed()
        recent_keys = pygame.key.get_just_pressed()

        # --- movement ---
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += dt * self.speed * self.direction

        # --- ability use ---
        # check cooldown
        if settings.game_time - self.ability_start_time >= self.ability_cooldown:
            self.ability_ready = True

        # activate ability
        if self.ability_ready and recent_keys[pygame.K_SPACE]:
            self.activate_ability()

        # end ability duration
        if settings.game_time - self.ability_start_time >= self.ability_duration:
            self.can_collide = True

    def refresh_appearance(self):
        # --- adjust facing ---
        if self.direction.x > 0:
            self.facing = 'right'
        elif self.direction.x < 0:
            self.facing = 'left'
        select = (self.health, self.facing)
        self.image = self.sprite_variants[select]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.size = self.image.get_size()

        # --- blur if ability active ---
        self.image.set_alpha(100 if not self.can_collide else 255)

    def update(self, dt):
    # --- control flow of player sprite ---

        self.handle_input(dt)

        self.keep_in_window()
        
        self.refresh_appearance()


class Obstacle(pygame.sprite.Sprite):
    """Obstacle sprite: moves across the screen and updates score on exit."""

    def __init__(self, groups, speed, sprite_variants):
        super().__init__(groups)

        # --- parameters ---
        self.speed = speed

        # --- visual setup ---
        self.width = settings.random_of_selection((150, 200, 250, 300))
        self.image = sprite_variants[self.width]
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH + self.width, settings.random_of_spectrum(0, WINDOW_HEIGHT)))
        self.mask = pygame.mask.from_surface(self.image)

        # --- motion setup ---
        self.direction = pygame.Vector2(-1, 0)
        
    def update(self, dt):
        global STATS

        # --- move ---
        self.rect.centerx -= self.speed * dt

        # --- update stats when killed ---
        if self.rect.right < 0:
            self.kill()
            STATS['score'] += 1
