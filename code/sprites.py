from utils import *

# --- player related sprites ---
class Player(pygame.sprite.Sprite):
    """Player sprite: handles movement, abilities, and player presisentation."""

    def __init__(self, game, groups, layer):
        # --- parameters ---
        self.game = game
        self._layer = layer
        super().__init__(groups)
        
        # --- gameplay attributes ---
        self.is_alive = True
        self.facing_right = True
        self.health = 2
        self.speed = DEFAULT_PLAYER_SPEED
        self.iframes = False
        self.iframe_start = 0.0
        self.banana_boosted = False
        self.banana_boost_start = 0.0
        self.fire_power = False
        self.fire_power_start = 0.0
        self.fireball_ready = True
        self.last_fireball = 0.0

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
        self.image = self.game.player_sprite_variants[self.health]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_frect(center=WINDOW_CENTER)

        # --- glow sprite ---
        self.glow_sprite = PlayerGlow(self.game,
                   (self.game.all_sprites, self.game.UI_sprites),
                   self.game.LAYERS['player_glow'])
        
        # --- fire outline ---
        self.fire_outline_sprite = PlayerFireOutline(self.game,
                                                     (self.game.all_sprites, self.game.UI_sprites),
                                                     self.game.LAYERS['player_fire_outline'])

        # --- motion setup ---
        self.direction = pygame.Vector2()
        self.dash_direction = pygame.Vector2()

    def activate_iframes(self):
        if self.can_collide:
            self.iframes = True
            self.iframe_start = self.game.play_time

    def activate_ability(self):
        self.game.ability_sound.play()
        self.ability_start_time = self.game.play_time
        self.ability_ready = False
        self.can_collide = False

    def dash(self):
        if self.direction.length_squared() != 0:
            self.game.dash_sound.play()
            self.dashing = True
            self.dash_start_time = self.game.play_time
            self.dash_ready = False

            # restrict to cardinal directions
            if abs(self.direction.x) >= abs(self.direction.y):
                        self.dash_direction = pygame.Vector2(1 if self.direction.x > 0 else -1, 0)
            elif abs(self.direction.y) > abs(self.direction.x):
                self.dash_direction = pygame.Vector2(0, 1 if self.direction.y > 0 else -1)

    def shoot_fireball(self, shoot_direction):
        self.game.shoot_sound.play()
        self.fireball_ready = False
        self.last_fireball = self.game.play_time
        Fireball(self.game,
                 (self.game.all_sprites, self.game.fireball_sprites),
                 self.game.LAYERS['fireballs'],
                 shoot_direction)

    def keep_in_window(self):
        self.rect.clamp_ip(pygame.Rect(-10, -10, WINDOW_WIDTH + 20, WINDOW_HEIGHT + 20))

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        recent_keys = pygame.key.get_just_pressed()

        # --- movement ---
        self.direction.x = int(keys[KEY_BINDINGS["move_right"]]) - int(keys[KEY_BINDINGS["move_left"]])
        self.direction.y = int(keys[KEY_BINDINGS["move_down"]]) - int(keys[KEY_BINDINGS["move_up"]])

        # --- shoot fire ball ---
        if self.fire_power:
            if self.game.play_time - self.fire_power_start > FIRE_POWER_DURATION:
                self.fire_power = False

            if self.game.play_time - self.last_fireball > FIREBALL_SHOOT_COOLDOWN:
                self.fireball_ready = True
        
            if self.fireball_ready:
                if recent_keys[KEY_BINDINGS['shoot_up']]:
                    self.shoot_fireball((0,-1))
                elif recent_keys[KEY_BINDINGS['shoot_down']]:
                    self.shoot_fireball((0,1))
                elif recent_keys[KEY_BINDINGS['shoot_right']]:
                    self.shoot_fireball((1,0))
                elif recent_keys[KEY_BINDINGS['shoot_left']]:
                    self.shoot_fireball((-1,0))

        # --- dash use ---
        # cooldown
        if not self.dash_ready and self.game.play_time - self.dash_start_time > self.dash_cooldown:
            self.dash_ready = True  

        # activate dash
        if self.dash_ready and recent_keys[KEY_BINDINGS["dash"]] and (keys[KEY_BINDINGS["move_left"]] or keys[KEY_BINDINGS["move_right"]] or keys[KEY_BINDINGS["move_up"]] or keys[KEY_BINDINGS["move_down"]]):
            self.dash()

        # end dash
        if self.game.play_time - self.dash_start_time > self.dash_duration:
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
        if not self.ability_ready and self.game.play_time - self.ability_start_time > self.ability_cooldown:
            self.ability_ready = True

        # activate ability
        if self.ability_ready and recent_keys[KEY_BINDINGS["ability"]]:
            self.activate_ability()

        # end ability duration
        if not self.can_collide and self.game.play_time - self.ability_start_time > self.ability_duration:
            self.can_collide = True

    def refresh_appearance(self):
        # --- facing direction ---
        if self.direction.x < 0:
            self.facing_right = False
        elif self.direction.x > 0:
            self.facing_right = True

        # --- base image ---
        base = self.game.player_sprite_variants[max(1, self.health)]
        if not self.facing_right:
            base = pygame.transform.flip(base, True, False)
        self.image = base.copy()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.size = self.image.get_size()

        # --- banana trail ---
        if not hasattr(self, "_last_trail_spawn"):
            self._last_trail_spawn = 0.0

        if not hasattr(self, "_TrailClass"):
            class _TrailSprite(pygame.sprite.Sprite):
                def __init__(self, groups, layer, image, pos, lifetime=BANANA_TRAIL_LIFETIME):
                    self._layer = layer
                    super().__init__(groups)
                    self.image = image.copy()
                    self.rect = self.image.get_rect(center=pos)
                    self._spawn = perf_counter()
                    self._lifetime = lifetime
                    self.is_trail = True

                def update(self, dt):
                    t = (perf_counter() - self._spawn) / max(self._lifetime, 1e-6)
                    alpha = max(0, int(120 * (1.0 - t)))
                    self.image.set_alpha(alpha)
                    if t >= 1.0:
                        self.kill()

            self._TrailClass = _TrailSprite

        # only produce trail while banana boost is active and player is moving
        if self.banana_boosted and self.direction.length_squared() > 0:
            # throttle spawn rate
            if self.game.play_time - self._last_trail_spawn > BANANA_TRAIL_DRAW_INTERVALL:  # shadows per frame
                self._last_trail_spawn = self.game.play_time

                # build a tinted surface
                w, h = self.image.get_size()
                shadow = pygame.Surface((w-25, h-25), pygame.SRCALPHA)
                pygame.draw.rect(shadow, COLOR['blue_banana_trail' if self.health > 1 else 'red_banana_trail'], shadow.get_rect(), border_radius=18)
                shadow.set_alpha(100)

                self._TrailClass((self.game.all_sprites, self.game.UI_sprites), self._layer - 0.1, shadow, self.rect.center)

        # --- ability and iframes ---
        if not self.can_collide or (self.game.play_time - self.dash_start_time < self.dash_duration and self.game.play_time > 1):
            progress = (self.game.play_time - self.ability_start_time) / self.ability_duration
            progress = max(0.0, min(progress, 1.0))
            darkness = 255 - int(255 * min(progress * PLAYER_BLACK_FADE_SPEED, 1))
            overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            overlay.fill((darkness, darkness, darkness))
            self.image.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        elif self.iframes:
            flicker = 150 + int(105 * abs(sin(self.game.play_time * 20)))
            self.image.set_alpha(flicker)
        else:
            self.image.set_alpha(255)

    def update(self, dt):
        # banana cooldown
        if self.banana_boosted and self.game.play_time - self.banana_boost_start > BANANA_BOOST_DURATION:
            self.banana_boosted = False

        if self.banana_boosted:
            self.speed = DEFAULT_PLAYER_SPEED + BANANA_SPEED_BOOST if self.health > 1 else ONE_LIFE_PLAYER_SPEED + BANANA_SPEED_BOOST
        else: 
            self.speed = DEFAULT_PLAYER_SPEED if self.health > 1 else ONE_LIFE_PLAYER_SPEED

        self.handle_input(dt)
        self.keep_in_window()

        if self.iframes and self.game.play_time - self.iframe_start > PLAYER_IFRAMES_DURATION:
            self.iframes = False

        self.refresh_appearance()

class PlayerGlow(pygame.sprite.Sprite):
    def __init__(self, game, groups, layer):
        self.game = game
        self._layer = layer
        super().__init__(groups)

        self.variations = {"blue": pygame.Surface((80, 80), pygame.SRCALPHA),
                    "red": pygame.Surface((80, 80), pygame.SRCALPHA)}
        
        pygame.draw.circle(self.variations["blue"], COLOR["blue_player_glow"], (40, 40), 40, width=5)
        pygame.draw.circle(self.variations["red"], COLOR["red_player_glow"], (40, 40), 40, width=5)
        self.glow = self.variations['blue']

        self.image = pygame.Surface((1,1), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

    def update(self, dt):
        if not self.game.player.is_alive:
            self.kill()
            return
        
        surf = self.variations['red'] if self.game.player.health == 1 else self.variations['blue']
        
        if self.game.player.ability_ready:
            self.image = surf
        else:
            self.image = pygame.Surface((1,1), pygame.SRCALPHA)

        self.rect = self.image.get_rect(center=self.game.player.rect.center)

class PlayerFireOutline(pygame.sprite.Sprite):
    def __init__(self, game, groups, layer):
        self.game = game
        self._layer = layer
        super().__init__(groups)

        self.image = pygame.Surface((1,1), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

    def update(self, dt):
        if not self.game.player.is_alive:
            self.kill()
            return
        
        if not self.game.player.fire_power:
            self.image = pygame.Surface((1,1), pygame.SRCALPHA)
            self.rect.center = self.game.player.rect.center
            return
        
        outline = self.game.player.mask.outline()
        if not outline:
            self.image = pygame.Surface((1,1), pygame.SRCALPHA)
            self.rect.center = self.game.player.rect.center
            return
        
        surf = pygame.Surface(self.game.player.image.get_size(), pygame.SRCALPHA)
        t = perf_counter()
        alpha = 180 + int(75 * sin(t * 12))
        alpha = max(0, min(255, alpha))
        color = (255, 120, 0, alpha)

        thickness = 1
        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                if abs(dx) + abs(dy) <= thickness:
                    shifted = [(x + dx, y + dy) for x, y in outline]
                    pygame.draw.polygon(surf, color, shifted, width=1)

        self.image = surf
        self.rect = self.image.get_rect(center=self.game.player.rect.center)

class Fireball(pygame.sprite.Sprite):
    def __init__(self, game, groups, layer, shoot_direction):
        self.game = game
        self._layer = layer
        super().__init__(groups)
        self.image = self.game.fireball_image
        self.speed = FIRE_BALL_SPEED
        self.direction = pygame.Vector2(shoot_direction)
        rotation = {(1,0): 0, (0,-1): 90, (-1,0): 180, (0,1): 270}
        offset_x = {(1,0): 40, (0,-1): 0, (-1,0): -40, (0,1): 0}
        offset_y = {(1,0): 0, (0,-1): -40, (-1,0): 0, (0,1): 40}
        self.image = pygame.transform.rotozoom(self.image, rotation[shoot_direction], 1)
        self.rect = self.image.get_frect(center=(self.game.player.rect.centerx + offset_x[shoot_direction], self.game.player.rect.centery + offset_y[shoot_direction]))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if self.rect.right < 0 or self.rect.left > WINDOW_WIDTH or self.rect.bottom < 0 or self.rect.top > WINDOW_HEIGHT:
            self.kill()

# --- background and decoration related sprites ---
class AnimatedBackground(pygame.sprite.Sprite):
    """Animated background sprite cycling through frames."""

    def __init__(self, groups, layer, frames, scroll, interval=BACKGROUND_FRAME_INTERVALL):
        self._layer = layer
        super().__init__(groups)
        self.frames = frames
        self.index = 0
        self.timer = 0
        self.interval = interval
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.speed = DEFAULT_BACKGROUND_SCROLL_SPEED
        self.scroll = scroll

    def update(self, dt):
        self.timer += dt * 1000
        if self.timer >= self.interval:
            self.timer = 0
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]

        if self.scroll:
            self.rect.centerx += dt * self.speed * -1
            if self.rect.centerx <= 0:
                self.rect.topleft = (0,0)

# --- entities ---
class Fruit(pygame.sprite.Sprite):
    """Collectable items that give benefits"""

    def __init__(self, game, groups, layer, speed):
        self.game = game
        self._layer = layer
        super().__init__(groups)
        self.speed = speed
        self.image = self.game.fruit_sprite_variants[self.__class__]
        self.rect = self.image.get_frect(center=(random_of_spectrum(60,WINDOW_WIDTH-100,bias=0.6),-100))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(0,1)

    def destroy(self):
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

    def display_pickup_message(self, font, messages):
        key = self.__class__
        if key in messages:
            text, color_key = messages[key]
            EffectText((self.game.all_sprites, self.game.UI_sprites),
                       self.game.LAYERS['effect_texts'],
                       text,
                       font,
                       COLOR[color_key],
                       self.rect.center)

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        self.destroy()

class Apple(Fruit):
    """Apple collectable: gives 10 points."""

    def __init__(self, game, groups, layer, speed):
        super().__init__(game, groups, layer, speed)

    def apply_effect(self):
        STATS['score'] += APPLE_POINTS
        self.kill()

class Blueberry(Fruit):
    """Blueberry collectable: restore 2nd life."""

    def __init__(self, game, groups, layer, speed):
        super().__init__(game, groups, layer, speed)

    def apply_effect(self):
        if self.game.player.health < 2:
            self.game.player.health += 1
        self.kill()

class Banana(Fruit):
    """Banana collectable: temporary speed boost."""

    def __init__(self, game, groups, layer, speed):
        super().__init__(game, groups, layer, speed)

    def apply_effect(self):
        self.game.player.banana_boosted = True
        self.game.player.banana_boost_start = self.game.play_time
        self.kill()

class Chili(Fruit):
    """Chili collectable: Grants temporary ability to shoot fire balls."""
    def __int__(self, game, groups, layer, speed):
        super().__init__(game, groups, layer, speed)

    def apply_effect(self):
        self.game.player.fire_power = True
        self.game.player.fire_ball_ready = True
        self.game.player.fire_power_start = self.game.play_time
        self.kill()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, game, groups, layer, kill_condition, speed):
        self.game = game
        self._layer = layer
        super().__init__(groups)
        self.kill_condition = kill_condition
        self.speed = speed

    def handle_getting_shot(self):
        EffectText((self.game.all_sprites, self.game.UI_sprites), self.game.LAYERS['effect_texts'], f"+{POINTS_FOR_OBSTACLE_SHOOT} points", self.game.fonts['effect_texts'], self.effect_text_color, self.rect.center)
        self.kill()
        self.game.eat_fruit_sound.play()
        STATS['score'] += POINTS_FOR_OBSTACLE_SHOOT

    def destroy(self):
        if eval(self.kill_condition):
            self.kill()

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        self.destroy()

class Rectangle(Obstacle):
    def __init__(self, game, groups, layer, kill_condition, speed, width):
        super().__init__(game, groups, layer, kill_condition, speed)
        self.width = width
        self.image = self.game.rectangle_sprite_variants[self.width]
        self.size = self.image.get_size()
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH+self.width, random_of_spectrum(0, WINDOW_HEIGHT)))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(-1, 0)
        self.effect_text_color = COLOR[f'{self.width}_rectangle_shot_effect_text']

class Icicle(Obstacle):
    def __init__(self, game, groups, layer, kill_condition, speed):
        super().__init__(game, groups, layer, kill_condition, speed)
        self.image = self.game.icicle_image
        self.size = self.image.get_size()
        self.rect = self.image.get_frect(center=(random_of_spectrum(self.size[0]/2,WINDOW_WIDTH-self.size[0]/2, as_float=True), 0-self.size[1]))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(0, 1)
        self.effect_text_color = COLOR['icicle_shot_effect_text']

# --- effects ---
class EffectText(pygame.sprite.Sprite):
    """Text that pops up after collecting a fruit, indicating the its effect"""

    def __init__(self, groups, layer, text, font, color, pos, lifetime=EFFECT_TEXT_DURATION, rise=EFFECT_TEXT_RISE_SPEED):
        self._layer = layer
        super().__init__(groups)
        base = font.render(text, True, color)
        shadow = font.render(text, True, (COLOR['effect_text_shadow']))
        self.image = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        self.image.blit(shadow, (2, 2))
        self.image.blit(base, (0, 0))
        self.rect = self.image.get_rect(center=pos)
        self.spawn = perf_counter()
        self.lifetime = lifetime
        self.rise = rise
        self.is_effect_text = True

    def update(self, dt):
        self.rect.y -= int(self.rise * dt)
        t = (perf_counter() - self.spawn) / max(self.lifetime, 1e-6)
        fade_start = 0.7          # 0s–0.7s: fully visible, 0.7s–1.0s: fade
        if t < fade_start:
            alpha = 255
        else:
            u = (t - fade_start) / (1 - fade_start) 

            # fast fade: power > 1 makes it drop quickly near the end
            alpha = int(255 * (1 - u)**2)

        self.image.set_alpha(max(0, min(255, alpha)))
        if t >= 1.0:
            self.kill()