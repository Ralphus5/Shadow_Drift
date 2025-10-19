from settings import *


class Player(pygame.sprite.Sprite):
    """Player sprite: handles movement, abilities, and player presisentation."""

    def __init__(self, groups, layer, sprite_variants, ability_sound, dash_sound):
        self._layer = layer
        super().__init__(groups)

        # --- parameters ---
        self.sprite_variants = sprite_variants
        self.ability_sound = ability_sound
        self.dash_sound = dash_sound

        # --- glow effect ---
        self.glows: dict = {"blue": pygame.Surface((80, 80), pygame.SRCALPHA),
                            "red": pygame.Surface((80, 80), pygame.SRCALPHA)}
        pygame.draw.circle(self.glows["blue"], COLOR["blue_player_glow"], (40, 40), 40, width=5)
        pygame.draw.circle(self.glows["red"], COLOR["red_player_glow"], (40, 40), 40, width=5)
        
        # --- gameplay attributes ---
        self.is_alive = True
        self.facing_right = True
        self.health = 2
        self.speed = DEFAULT_PLAYER_SPEED
        self.iframes = False
        self.iframe_start = 0.0

        # --- ability system ---
        self.can_collide = True
        self.ability_ready = True
        self.ability_start_time = 0.0
        self.ability_cooldown = PLAYER_ABILITY_COOLDOWN
        self.ability_duration = PLAYER_ABILITY_DURATION

        # s--- dash system ---
        self.dashing = False
        self.dash_ready = True
        self.dash_start_time = 0.0
        self.dash_cooldown = DASH_COOLDOWN
        self.dash_duration = DASH_DURATION

        # --- rendering ---
        self.image = self.sprite_variants[self.health]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_frect(center=WINDOW_CENTER)
        self.glows
        self.glow = self.glows['blue']

        # --- motion setup ---
        self.direction = pygame.Vector2()
        self.dash_direction = pygame.Vector2()

    def activate_iframes(self, play_time):
        if self.can_collide:
            self.iframes = True
            self.iframe_start = play_time

    def activate_ability(self):
        self.ability_sound.play()
        self.ability_start_time = self.play_time
        self.ability_ready = False
        self.can_collide = False

    def dash(self):
        if self.direction.length_squared() != 0:
            self.dash_sound.play()
            self.dashing = True
            self.dash_start_time = self.play_time
            self.dash_ready = False

            # restrict to cardinal directions
            if abs(self.direction.x) >= abs(self.direction.y):
                        self.dash_direction = pygame.Vector2(1 if self.direction.x > 0 else -1, 0)
            elif abs(self.direction.y) > abs(self.direction.x):
                self.dash_direction = pygame.Vector2(0, 1 if self.direction.y > 0 else -1)

    def keep_in_window(self):
        self.rect.clamp_ip(pygame.Rect(-10, -10, WINDOW_WIDTH + 20, WINDOW_HEIGHT + 20))

    def handle_input(self, dt, play_time):
        self.play_time = play_time
        keys = pygame.key.get_pressed()
        recent_keys = pygame.key.get_just_pressed()

        # --- movement ---
        self.direction.x = int(keys[KEY_BINDINGS["move_right"]]) - int(keys[KEY_BINDINGS["move_left"]])
        self.direction.y = int(keys[KEY_BINDINGS["move_down"]]) - int(keys[KEY_BINDINGS["move_up"]])


        # --- dash use ---
        # cooldown
        if not self.dash_ready and self.play_time - self.dash_start_time > self.dash_cooldown:
            self.dash_ready = True  

        # activate dash
        if self.dash_ready and recent_keys[KEY_BINDINGS["dash"]] and (keys[KEY_BINDINGS["move_left"]] or keys[KEY_BINDINGS["move_right"]] or keys[KEY_BINDINGS["move_up"]] or keys[KEY_BINDINGS["move_down"]]):
            self.dash()

        # end dash
        if self.play_time - self.dash_start_time > self.dash_duration:
            self.dashing = False

        # dash movement
        if self.dashing:
            self.rect.center += dt * DASH_SPEED * self.dash_direction

        # --- regular movement ---
        else:
            if not self.dashing and self.direction.length_squared() > 0:
                self.direction = self.direction.normalize()
            self.rect.center += dt * self.speed * self.direction

        # --- ability use ---
        # check cooldown
        if not self.ability_ready and self.play_time - self.ability_start_time > self.ability_cooldown:
            self.ability_ready = True

        # activate ability
        if self.ability_ready and recent_keys[KEY_BINDINGS["ability"]]:
            self.activate_ability()

        # end ability duration
        if not self.can_collide and self.play_time - self.ability_start_time > self.ability_duration:
            self.can_collide = True

    def refresh_appearance(self, play_time):
        self.play_time = play_time
        # --- facing direction ---
        if self.direction.x < 0:
            self.facing_right = False
        elif self.direction.x > 0:
            self.facing_right = True

        # --- base image ---
        base = self.sprite_variants[max(1, self.health)]
        if not self.facing_right:
            base = pygame.transform.flip(base, True, False)
        self.image = base.copy()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.size = self.image.get_size()

        # --- ability and iframes ---
        if not self.can_collide or (self.play_time - self.dash_start_time < self.dash_duration and self.play_time > 1):
            progress = (self.play_time - self.ability_start_time) / self.ability_duration
            progress = max(0.0, min(progress, 1.0))
            darkness = 255 - int(255 * min(progress * PLAYER_BLACK_FADE_SPEED, 1))
            overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            overlay.fill((darkness, darkness, darkness))
            self.image.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        elif self.iframes:
            flicker = 150 + int(105 * abs(sin(self.play_time * 20)))
            self.image.set_alpha(flicker)
        else:
            self.image.set_alpha(255)

    def update(self, dt, play_time):
        # --- control flow of player sprite ---
        self.play_time = play_time

        self.speed = DEFAULT_PLAYER_SPEED if self.health > 1 else ONE_LIFE_PLAYER_SPEED
        self.glow = self.glows['red'] if self.health == 1 else self.glows['blue']

        self.handle_input(dt, self.play_time)
        self.keep_in_window()

        if self.iframes and self.play_time - self.iframe_start > PLAYER_IFRAMES_DURATION:
            self.iframes = False

        self.refresh_appearance(self.play_time)

class AnimatedBackground(pygame.sprite.Sprite):
    """Animated background sprite cycling through frames."""

    def __init__(self, groups, layer, frames, interval=BACKGROUND_FRAME_INTERVALL):
        self._layer = layer
        super().__init__(groups)
        self.frames = frames
        self.index = 0
        self.timer = 0
        self.interval = interval  # ms between frame changes
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(topleft=(0, 0))

    def update(self, dt, *_):
        self.timer += dt * 1000
        if self.timer >= self.interval:
            self.timer = 0
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]

class Fruit(pygame.sprite.Sprite):
    """Collectable items that give benefits"""

    def __init__(self, groups, layer, speed, fruit_sprites):
        self._layer = layer
        super().__init__(groups)
        self.speed = speed
        self.image = fruit_sprites
        self.rect = self.image.get_frect(center=(random_of_spectrum(60,WINDOW_WIDTH-100,bias=0.6),-100))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(0,1)

    def destroy(self):
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

    def update(self, dt, play_time):
        self.rect.center += self.direction * self.speed * dt
        self.destroy()

class Apple(Fruit):
    """Apple collectable: gives 10 points."""

    def __init__(self, groups, layer, speed, fruit_sprites):
        super().__init__(groups, layer, speed, fruit_sprites)

    def apply_effect(self, player):
        STATS['score'] += 10
        self.kill()

class Blueberry(Fruit):
    """Blueberry collectable: restore 2nd life."""

    def __init__(self, groups, layer, speed, fruit_sprites):
        super().__init__(groups, layer, speed, fruit_sprites)

    def apply_effect(self, player):
        if player.health < 2:
            player.health += 1
        self.kill()

class Obstacle(pygame.sprite.Sprite):
    """Obstacle sprite: moves across the screen and updates score on exit."""

    def __init__(self, groups, layer, speed, sprite_variants):
        self._layer = layer
        super().__init__(groups)
        self.speed = speed

        # --- visual setup ---
        self.width = random_of_selection((150, 200, 250, 300))
        self.image = sprite_variants[self.width]
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH + self.width, random_of_spectrum(0, WINDOW_HEIGHT)))
        self.mask = pygame.mask.from_surface(self.image)

        # --- motion setup ---
        self.direction = pygame.Vector2(-1, 0)

    def destroy(self):
        if self.rect.right < 0:
            self.kill()
        # update stats when killed
            STATS['score'] += 1
        
    def update(self, dt, play_time):
        # --- move ---
        self.rect.center += self.direction * self.speed * dt
        self.destroy()
