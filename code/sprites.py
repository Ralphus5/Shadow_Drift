from utils import *

# --- player related ---
class Player(pygame.sprite.Sprite):
    def __init__(self, game: Game, groups: Iterable[pygame.sprite.GroupSingle|pygame.sprite.LayeredUpdates]) -> None:
        # --- parameters ---
        self.game = game
        self._layer = self.game.LAYERS['player']
        super().__init__(groups)
        
        # --- gameplay attributes ---
        self.is_alive = True
        self.facing_right = False if self.game.current_phase in ('arrow', 'saw_blade') else True
        self.health = 2
        self.extra_life = 0
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
        self.want_ability = False
        self.can_collide = True
        self.ability_ready = True
        self.ability_start_time = 0.0
        self.ability_cooldown = PLAYER_ABILITY_COOLDOWN
        self.ability_duration = PLAYER_ABILITY_DURATION

        # s--- dash system ---
        self.want_dash = False
        self.dashing = False
        self.dash_ready = True
        self.dash_start_time = 0.0
        self.dash_cooldown = DASH_COOLDOWN
        self.dash_duration = DASH_DURATION

        # --- rendering ---
        self.image: pygame.Surface = self.game.player_sprite_variants[self.health]
        self.mask: pygame.Mask = pygame.mask.from_surface(self.image)
        self.rect: pygame.FRect = self.image.get_frect(center=WINDOW_CENTER)

        # --- glow sprite ---
        self.glow_sprite = PlayerGlow(self.game,
                   (self.game.all_sprites, self.game.player_effect_sprites))
        
        # --- fire outline ---
        self.fire_outline_sprite = PlayerFireOutline(self.game,
                                                     (self.game.all_sprites, self.game.player_effect_sprites))

        # --- motion setup ---
        self.direction = pygame.Vector2(0,0)
        self.dash_direction = pygame.Vector2(0,0)

    def activate_iframes(self) -> None:
        if self.can_collide:
            self.iframes = True
            self.iframe_start = self.game.play_time

    def dash(self) -> None:
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
            self.dash_direction = pygame.Vector2(self.direction.normalize())

    def activate_ability(self) -> None:
        self.game.ability_sound.play()
        self.ability_start_time = self.game.play_time
        self.ability_ready = False
        self.can_collide = False

    def shoot_fireball(self, shoot_direction: pygame.Vector2) -> None:
        self.fireball_ready = False
        self.last_fireball = self.game.play_time
        Fireball(self.game,
                 self.game.LAYERS['player_fireballs'],
                (self.game.all_sprites, self.game.player_fireball_sprites),
                self.game.fireball_image,
                shoot_direction,
                origin=self.rect.center)

    def get_input(self) -> None:
        keys = pygame.key.get_pressed()
        recent_keys = pygame.key.get_just_pressed()

        # --- movement ---
        self.direction.x = int(keys[KEY_BINDINGS["move_right"]]) - int(keys[KEY_BINDINGS["move_left"]])
        self.direction.y = int(keys[KEY_BINDINGS["move_down"]]) - int(keys[KEY_BINDINGS["move_up"]])

        # --- dash and ability---
        if recent_keys[KEY_BINDINGS["dash"]]:
            self.want_dash = True
        if recent_keys[KEY_BINDINGS["ability"]]:
            self.want_ability = True

        # --- shoot fireball ---
        self.shoot_dir = pygame.Vector2()
        if recent_keys[KEY_BINDINGS['shoot_up']]:
            self.shoot_dir = pygame.Vector2(0,-1)
        elif recent_keys[KEY_BINDINGS['shoot_down']]:
            self.shoot_dir = pygame.Vector2(0,1)
        elif recent_keys[KEY_BINDINGS['shoot_right']]:
            self.shoot_dir = pygame.Vector2(1,0)
        elif recent_keys[KEY_BINDINGS['shoot_left']]:
            self.shoot_dir = pygame.Vector2(-1,0)

    # ---------- CONTROLLER INPUT (NEW) ----------
        pad = getattr(self.game, "controller", None)
        if pad is not None:
            # left stick movement
            lx = pad.get_axis(PAD_AXIS_MOVE_X)
            ly = pad.get_axis(PAD_AXIS_MOVE_Y)

            if abs(lx) > CONTROLLER_DEADZONE or abs(ly) > CONTROLLER_DEADZONE:
                # override keyboard if stick is moved
                self.direction.x = lx
                self.direction.y = ly

            # right stick shooting direction (auto-fire style)
            rx = pad.get_axis(PAD_AXIS_SHOOT_X)
            ry = pad.get_axis(PAD_AXIS_SHOOT_Y)

            if abs(rx) > CONTROLLER_DEADZONE or abs(ry) > CONTROLLER_DEADZONE:
                self.shoot_dir = pygame.Vector2(rx, ry)

    def update_banana_boost(self) -> None:
        if self.banana_boosted and self.game.play_time - self.banana_boost_start > BANANA_BOOST_DURATION:
            self.banana_boosted = False
            self.game.buff_end_sound.play()

        if self.banana_boosted:
            self.speed = DEFAULT_PLAYER_SPEED + BANANA_SPEED_BOOST if self.health > 1 else ONE_LIFE_PLAYER_SPEED + BANANA_SPEED_BOOST
        else: 
            self.speed = DEFAULT_PLAYER_SPEED if self.health > 1 else ONE_LIFE_PLAYER_SPEED

    def update_fire_power(self) -> None:
        if not self.fire_power:
            return
        
        if self.game.play_time - self.fire_power_start > FIRE_POWER_DURATION:
            self.fire_power = False
            self.game.buff_end_sound.play()
            return

        if self.game.play_time - self.last_fireball > FIREBALL_SHOOT_COOLDOWN:
            self.fireball_ready = True

        if self.fireball_ready and self.shoot_dir.length_squared() != 0:
            self.shoot_fireball(self.shoot_dir)

    def update_dash(self) -> None:
        if not self.dash_ready and self.game.play_time - self.dash_start_time > self.dash_cooldown:
            self.dash_ready = True  

        if self.dash_ready and self.want_dash and self.direction.length_squared() != 0:
            self.dash()
        self.want_dash = False

        if self.dashing and self.game.play_time - self.dash_start_time > self.dash_duration:
            self.dashing = False

    def update_ability(self) -> None:
        if not self.ability_ready and self.game.play_time - self.ability_start_time > self.ability_cooldown:
            self.ability_ready = True

        if self.ability_ready and self.want_ability:
            self.activate_ability()
        self.want_ability = False

        if not self.can_collide and self.game.play_time - self.ability_start_time > self.ability_duration:
            self.can_collide = True

    def update_iframes(self) -> None:
        if self.iframes and self.game.play_time - self.iframe_start > PLAYER_IFRAMES_DURATION:
            self.iframes = False

    def apply_movement(self, dt: float) -> None:
        if self.dashing:
            self.rect.center += dt * DASH_SPEED * self.dash_direction
            return
        
        if self.direction.length_squared() != 0:
            self.direction = self.direction.normalize()
        self.rect.center += dt * self.speed * self.direction

    def update_appearance(self) -> None:
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
        if self.banana_boosted and self.direction.length_squared() > 0:
            PlayerBananaTrail(
                self.game,
                (self.game.all_sprites, self.game.player_effect_sprites),
                self.rect.center,
            )


        # --- ability and iframes ---
        if not self.can_collide or (self.game.play_time - self.dash_start_time < self.dash_duration and self.game.play_time > 1):
            progress = (self.game.play_time - self.ability_start_time) / self.ability_duration
            progress = max(0.0, min(progress, 1.0))
            darkness = 255 - int(255 * min(progress * PLAYER_BLACK_FADE_SPEED, 1))
            overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            overlay.fill((darkness, darkness, darkness))
            self.image.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        elif self.iframes:
            flicker = 100 + int(105 * abs(sin(self.game.play_time * 20)))
            self.image.set_alpha(flicker)
        else:
            self.image.set_alpha(255)

    def update(self, dt: float) -> None:
        self.get_input()
        self.update_banana_boost()
        self.update_fire_power()
        self.update_dash()
        self.update_ability()
        self.update_iframes()
        self.apply_movement(dt)
        self.update_appearance()
        self.rect.clamp_ip(pygame.Rect(-10, -7, WINDOW_WIDTH + 19, WINDOW_HEIGHT + 14))

class PlayerGlow(pygame.sprite.Sprite):
    def __init__(self, game: Game, groups: Iterable[pygame.sprite.AbstractGroup]) -> None:
        self.game = game
        self._layer = self.game.LAYERS['player_glow']
        super().__init__(groups)

        self.variations = {"blue": pygame.Surface((80, 80), pygame.SRCALPHA),
                    "red": pygame.Surface((80, 80), pygame.SRCALPHA)}
        pygame.draw.circle(self.variations["blue"], COLOR["blue_player_glow"], (40, 40), 40, width=5)
        pygame.draw.circle(self.variations["red"], COLOR["red_player_glow"], (40, 40), 40, width=5)
        self.glow = self.variations['blue']

        self.image = pygame.Surface((1,1), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

    def update(self, dt: float) -> None:
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
    def __init__(self, game: Game, groups: Iterable[pygame.sprite.AbstractGroup]) -> None:
        self.game = game
        self._layer = self.game.LAYERS['player_fire_outline']
        super().__init__(groups)

        self.image: pygame.Surface = pygame.Surface((1,1), pygame.SRCALPHA)
        self.rect: pygame.Rect = self.image.get_rect()

    def update(self, dt: float) -> None:
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

class PlayerDeathAnimation(pygame.sprite.Sprite):
    def __init__(self, game: Game, groups: Iterable[pygame.sprite.AbstractGroup]) -> None:
        self.game = game
        self._layer = self.game.LAYERS['player_death_animation']
        super().__init__(groups)
        self.frame_index = 0
        self.image = self.game.player_death_animation_frames[0]
        self.rect = self.image.get_frect(center=self.game.player.rect.center)

    def update(self, dt: float) -> None:
        if self.frame_index <= len(self.game.player_death_animation_frames):
            self.image = self.game.player_death_animation_frames[int(self.frame_index)]
            if not self.game.player.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
            self.frame_index += PLAYER_EXPLOSION_SPEED 
        else:
            self.game.requested_state = 'game_over'
            self.kill()

class PlayerBananaTrail(pygame.sprite.Sprite):
    BLUE_SURF = None
    RED_SURF = None

    def __init__(self, game: Game, groups: Iterable[pygame.sprite.AbstractGroup], pos: tuple[float, float], lifetime: float = BANANA_TRAIL_LIFETIME) -> None:
        self.game = game
        self._layer = self.game.LAYERS['player_banana_trail']
        super().__init__(groups)

        self._spawn = perf_counter()
        self._lifetime = lifetime
        self.is_trail = True

        # --- build cached gradient surfaces once ---
        radius = 35

        if PlayerBananaTrail.BLUE_SURF is None:
            PlayerBananaTrail.BLUE_SURF = self._build_radial_glow(
                radius, COLOR['blue_banana_trail']
            )
        if PlayerBananaTrail.RED_SURF is None:
            PlayerBananaTrail.RED_SURF = self._build_radial_glow(
                radius, COLOR['red_banana_trail']
            )

        base = (
            PlayerBananaTrail.RED_SURF
            if self.game.player.health == 1
            else PlayerBananaTrail.BLUE_SURF
        )

        self.base_image = base
        self.image = base.copy()
        self.rect = self.image.get_rect(center=pos)

    def _build_radial_glow(self, radius: int, color_hex: str) -> pygame.Surface:
        size = radius * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx = cy = radius

        base_col = pygame.Color(color_hex)
        r0, g0, b0 = base_col.r, base_col.g, base_col.b

        # brightest inside, darker outside (like jellyfish glow)
        for r in range(radius, 0, -1):
            t = r / radius          # 1 at edge → 0 at center
            alpha = int(220 * (1 - t) ** 1.9)
            col = (r0, g0, b0, alpha)
            pygame.draw.circle(surf, col, (cx, cy), r)

        return surf

    def update(self, dt: float) -> None:
        # normalized lifetime 0 → 1
        t = (perf_counter() - self._spawn) / max(self._lifetime, 1e-6)
        t = max(0.0, min(1.0, t))

        # fade out smoothly (quadratic)
        alpha = int(255 * (1.0 - t) ** 2)
        img = self.base_image.copy()
        img.set_alpha(alpha)

        # optional very slight growth over lifetime
        scale = 1.0 + 0.1 * t
        w, h = img.get_size()
        img = pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))

        center = self.rect.center
        self.image = img
        self.rect: pygame.Rect = self.image.get_rect(center=center)

        if t >= 1.0:
            self.kill()

class Fireball(pygame.sprite.Sprite):
    def __init__(self, game: Game, layer: float, groups: Iterable[pygame.sprite.AbstractGroup], image: pygame.Surface, direction: pygame.Vector2, origin: Optional[tuple[int,int]|tuple[float,float]|pygame.Vector2] = None, spawn_offset: int = 40) -> None:
        self.game = game
        self._layer = layer
        super().__init__(*groups)
        self.game.shoot_sound.play()
        self.speed = FIRE_BALL_SPEED

        # --- direction ---
        if direction.length_squared() == 0:
            direction = pygame.Vector2(1, 0)
        self.direction = direction.normalize()

        # --- base image and rotation ---
        base_img = image
        angle_deg = degrees(atan2(-self.direction.y, self.direction.x))
        self.image = pygame.transform.rotozoom(base_img, angle_deg, 1.0)

        # --- spawn position ---
        if origin is None:
            origin = pygame.Vector2(self.game.player.rect.center)
        else:
            origin = pygame.Vector2(origin)

        center = origin + self.direction * spawn_offset
        self.rect: pygame.FRect = self.image.get_frect(center=center)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt: float) -> None:
        self.rect.center += self.direction * self.speed * dt
        if (self.rect.right < 0 or self.rect.left > WINDOW_WIDTH or
            self.rect.bottom < 0 or self.rect.top > WINDOW_HEIGHT):
            self.kill()

# --- background and decoration related ---
class AnimatedBackground(pygame.sprite.Sprite):
    def __init__(self, game: Game, groups: Iterable[pygame.sprite.Group|pygame.sprite.LayeredUpdates], frames: list[pygame.Surface], scroll: Optional[str], interval: float = BACKGROUND_FRAME_INTERVALL) -> None:
        self.game = game
        self._layer = self.game.LAYERS['backgrounds']
        super().__init__(groups)
        self.frames = frames
        self.scroll = scroll
        self.index = 0
        self.timer = 0
        self.interval = interval
        self.image: pygame.Surface = self.frames[self.index]
        self.rect: pygame.Rect = self.image.get_rect(topleft=(-WINDOW_WIDTH,0) if self.scroll == 'right' else (0, 0))
        self.speed = 0

    def update(self, dt: float) -> None:
        self.timer += dt * 1000
        if self.timer >= self.interval:
            self.timer = 0
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]

        if self.scroll == 'right':
            self.rect.centerx += dt * self.speed * -1
            if self.rect.centerx <= 0:
                self.rect.topleft = (0,0)
        elif self.scroll == 'left':
            self.rect.centerx += dt * self.speed
            if self.rect.centerx >= WINDOW_WIDTH:
                self.rect.topright = (WINDOW_WIDTH,0)

# --- items ---
class Coin(pygame.sprite.Sprite):
    def __init__(self, game: Game, groups: Iterable[pygame.sprite.Group|pygame.sprite.LayeredUpdates], frames: list[pygame.Surface], spawn: str, speed: int|float, spawn_bias: Optional[float] = None) -> None:
        self.game = game
        self._layer = self.game.LAYERS['coins']
        super().__init__(groups)
        self.frames = frames
        self.speed = speed
        self.index = 0
        self.timer = 0
        self.interval = COIN_FRAME_INTERVALL
        self.image = self.frames[self.index]
        width, height = self.image.get_size()
        COIN_ATTRIBUTES: dict[str, list[tuple[int|float, int|float]]] = {'left': [(-width/2,random_of_spectrum(30,WINDOW_HEIGHT-30,bias=spawn_bias)), (1,0)], 'right': [(WINDOW_WIDTH+width/2,random_of_spectrum(30,WINDOW_HEIGHT-30,bias=spawn_bias)), (-1,0)], 'top': [(random_of_spectrum(30,WINDOW_WIDTH-30,bias=spawn_bias),-height/2), (0,1)], 'bottom': [(random_of_spectrum(30,WINDOW_WIDTH-30,bias=spawn_bias),WINDOW_HEIGHT+height/2), (0,-1)]}
        self.rect: pygame.FRect = self.image.get_frect(center=(COIN_ATTRIBUTES[spawn][0]))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(COIN_ATTRIBUTES[spawn][1])

    def update(self, dt: float) -> None:
        self.rect.center += self.direction * self.speed * dt
        if self.rect.left > WINDOW_WIDTH + 100 or self.rect.right < -100 or self.rect.top > WINDOW_HEIGHT + 100 or self.rect.bottom < -100:
            self.kill()
        self.timer += dt * 1000
        if self.timer >= self.interval:
            self.timer = 0
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]

class Fruit(pygame.sprite.Sprite):
    def __init__(self, game: Game, groups: Iterable[pygame.sprite.Group|pygame.sprite.LayeredUpdates], spawn: str, speed: int|float, spawn_bias: Optional[float] = None, rotate: Optional[bool] = False) -> None:
        self.game = game
        self._layer = self.game.LAYERS['fruits']
        super().__init__(groups)
        self.speed = speed
        self.rotate = rotate
        self.image: pygame.Surface = self.game.fruit_sprite_variants[self.__class__]
        width, height = self.image.get_size()
        FRUIT_ATTRIBUTES: dict[str, list[tuple[int|float, int|float]]] = {'left': [(-width/2,random_of_spectrum(50,WINDOW_HEIGHT-50,bias=spawn_bias)), (1,0)], 'right': [(WINDOW_WIDTH+width/2,random_of_spectrum(50,WINDOW_HEIGHT-50, bias=spawn_bias)), (-1,0)], 'top': [(random_of_spectrum(50,WINDOW_WIDTH-50, bias=spawn_bias),-height/2), (0,1)], 'bottom': [(random_of_spectrum(50,WINDOW_WIDTH-50),WINDOW_HEIGHT+height/2), (0,-1)]}
        self.rect: pygame.FRect = self.image.get_frect(center=(FRUIT_ATTRIBUTES[spawn][0]))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(FRUIT_ATTRIBUTES[spawn][1])
        if self.rotate:
            self.angle = 0
            self.rotation_speed = random_of_spectrum(-150,150)
            self.base_image = self.image

    def destroy(self) -> None:
        if self.rect.left > WINDOW_WIDTH + 100 or self.rect.right < -100 or self.rect.top > WINDOW_HEIGHT + 100 or self.rect.bottom < -100:
            self.kill()

    def display_pickup_message(self, font: pygame.font.Font, messages: dict) -> None:
        key = self.__class__
        if key in messages:
            text, color_key = messages[key]
            EffectText(self.game,
                       (self.game.all_sprites, self.game.UI_text_sprites),
                       text,
                       font,
                       COLOR[color_key],
                       self.rect.center)

    def update(self, dt: float) -> None:
        self.rect.center += self.direction * self.speed * dt
        self.destroy()
        if self.rotate:
            self.angle = (self.angle + self.rotation_speed * dt) % 360
            old_center = self.rect.center
            self.image = pygame.transform.rotozoom(self.base_image, -self.angle, 1)
            self.rect = self.image.get_frect(center=old_center)
            self.mask = pygame.mask.from_surface(self.image)

class Apple(Fruit):
    def apply_effect(self) -> None:
        STATS['score'] += APPLE_POINTS

class Blueberry(Fruit):
    def apply_effect(self) -> None:
        self.game.player.health = 2

class Banana(Fruit):
    def apply_effect(self) -> None:
        self.game.player.banana_boosted = True
        self.game.player.banana_boost_start = self.game.play_time

class Chili(Fruit):
    def apply_effect(self) -> None:
        self.game.player.fire_power = True
        self.game.player.fire_power_start = self.game.play_time

class Grapes(Fruit):
    def apply_effect(self) -> None:
        self.game.player.extra_life = 1

class Pear(Fruit):
    def apply_effect(self) -> None:
        for sprite in self.game.obstacle_sprites:
            if not sprite.rect.bottom < 0 and not sprite.rect.top > WINDOW_HEIGHT and not sprite.rect.left > WINDOW_WIDTH and not sprite.rect.right < 0:
                EffectText(self.game, (self.game.all_sprites, self.game.UI_text_sprites), "+1 point", self.game.fonts['effect_texts'], sprite.effect_text_color, sprite.rect.center)
                self.kill()
                sprite.kill()
                STATS['score'] += 1

# --- obstacles ---
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, game: Game, layer: float, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], image: pygame.Surface, speed: int) -> None:
        self.game = game
        self._layer = layer
        super().__init__(groups)
        self.image: pygame.Surface = image
        self.size: tuple[int, int] = self.image.get_size()
        self.speed = speed
        self.effect_text_color = COLOR[(f'{self.size[0]}_' if self.__class__ == Rectangle else '') + f'{str(self.__class__.__name__).lower()}_shot_effect_text']
        self.rect: pygame.Rect|pygame.FRect
        self.direction: pygame.Vector2
        
    def handle_getting_shot(self) -> None:
        if self not in self.game.boss_obstacle_sprites:
            EffectText(self.game, (self.game.all_sprites, self.game.UI_text_sprites), f"+{POINTS_FOR_OBSTACLE_SHOOT} points", self.game.fonts['effect_texts'], self.effect_text_color, self.rect.center)
            STATS['score'] += POINTS_FOR_OBSTACLE_SHOOT
        self.game.eat_fruit_sound.play()
        self.kill()

    def destroy(self) -> None:
        if self.rect.left > WINDOW_WIDTH + 700 or self.rect.right < -700 or self.rect.top > WINDOW_HEIGHT + 700 or self.rect.bottom < -700:
            self.kill()

    def update(self, dt: float) -> None:
        self.rect.center += self.direction * self.speed * dt
        self.destroy()

class RotatingObstacle(Obstacle):
    def __init__(self, game: Game, layer: float, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], image: pygame.Surface, speed: int, angle: int|float, rotation_speed: float) -> None:
        super().__init__(game, layer, groups, image, speed)
        self.angle = angle
        self.rotation_speed = rotation_speed
        self.base_image = image
        self.image = self.base_image

    def update(self, dt: float) -> None:
        super().update(dt)
        self.angle = (self.angle + self.rotation_speed * dt) % 360
        old_center = self.rect.center
        self.image = pygame.transform.rotozoom(self.base_image, self.angle, 1)
        self.rect = self.image.get_frect(center=old_center)
        self.mask = pygame.mask.from_surface(self.image)

class Rectangle(Obstacle):
    def __init__(self, game: Game, layer: float, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], image: pygame.Surface, speed: int) -> None:
        super().__init__(game, layer, groups, image, speed)
        self.rect: pygame.FRect = self.image.get_frect(center=(WINDOW_WIDTH + self.size[0]/2, random_of_spectrum(0, WINDOW_HEIGHT)))
        self.mask: pygame.Mask = pygame.mask.from_surface(self.image)
        self.direction: pygame.Vector2 = pygame.Vector2(-1, 0)

class Arrow(Obstacle):
    def __init__(self, game: Game, layer: float, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], image: pygame.Surface, speed: int, spawn_height) -> None:
        super().__init__(game, layer, groups, image, speed)
        self.rect: pygame.FRect = self.image.get_frect(center=(0 - self.size[0]/2, spawn_height))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(1, 0)

class Icicle(Obstacle):
    def __init__(self, game: Game, layer: float, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], image: pygame.Surface, speed: int) -> None:
        super().__init__(game, layer, groups, image, speed)
        self.rect = self.image.get_frect(center=(random_of_spectrum(0,WINDOW_WIDTH, as_float=True), 0-self.size[1]/2))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(0, 1)

class Rocket(Obstacle):
    def __init__(self, game: Game, layer: float, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], image: pygame.Surface, speed: int) -> None:
        super().__init__(game, layer, groups, image, speed)
        self.rect = self.image.get_frect(center=(random_of_spectrum(0,WINDOW_WIDTH, as_float=True), WINDOW_HEIGHT+self.size[1]/2))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(0, -1)

class Jellyfish(Obstacle):
    def __init__(self, game: Game, layer: float, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], frames: list[pygame.Surface], speed: int) -> None:
        super().__init__(game, layer, groups, frames[0], speed)
        self.creation_time = perf_counter()
        self.rect = self.image.get_frect(center=(random_of_spectrum(0,WINDOW_WIDTH), WINDOW_HEIGHT+self.size[1]))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2((0,-1))
        self.frames = frames
        self.index = 0
        self.timer = 0
        self.interval = JELLYFISH_FRAME_INTERVALL
        self.image = self.frames[self.index]
        ObjectGlow(self.game,
                   (self.game.all_sprites, self.game.obstacle_effect_sprites),
                   self,
                   (100,100,220),
                   JELLYFISH_GLOW_RADIUS,
                   offsety=-60)
        
    def update(self, dt: float) -> None:
        self.timer += dt * 1000
        if self.timer >= self.interval:
            self.timer = 0
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]
        super().update(dt)

class SpikeBlock(Obstacle):
    def __init__(self, game: Game, layer: float, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], image: pygame.Surface, speed: int, spawn: str) -> None:
        super().__init__(game, layer, groups, image, speed)
        self.rect = self.image.get_frect(center=(random_of_spectrum(0,WINDOW_WIDTH), -self.size[1]/2 if spawn == 'top' else WINDOW_HEIGHT+self.size[1]/2))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(0, 1) if spawn == 'top' else pygame.Vector2(0, -1)

class PoisonCloud(Obstacle):
    def __init__(self, game: Game, layer: float, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], image: pygame.Surface, speed: int) -> None:
        super().__init__(game, layer, groups, image, speed)
        self.rect = self.image.get_frect(center=(random_of_spectrum(0,WINDOW_WIDTH, as_float=True), WINDOW_HEIGHT+self.size[1]/2))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(0, -1)
        self.creation_time = self.game.play_time

    def update(self, dt: float) -> None:
        super().update(dt)
        self.rect.centerx += dt * sin((self.game.play_time - self.creation_time) * 2) * 40

class Coconut(Obstacle):
    def __init__(self, game: Game, layer: float, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], image: pygame.Surface, speed: int) -> None:
        super().__init__(game, layer, groups, image, speed)
        self.rect = self.image.get_frect(center=(random_of_spectrum(0,WINDOW_WIDTH, as_float=True), -self.size[1]/2))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(0, 1)

class MusicNote(Obstacle):
    def __init__(self, game: Game, layer: float, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], image: pygame.Surface, speed: int) -> None:
        super().__init__(game, layer, groups, image, speed)
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH + self.size[0]/2, random_of_spectrum(0, WINDOW_HEIGHT)))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(-1, 0)

class SawBlade(RotatingObstacle):
    def __init__(self, game: Game, layer: float, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], image: pygame.Surface, speed: int, angle: float = 0, rotation_speed: int = -180, spawn: str ='left') -> None:
        super().__init__(game, layer, groups, image, speed, angle, rotation_speed)
        if spawn == 'right': self.base_image = pygame.transform.flip(self.game.saw_blade_image, True, False)
        if spawn == 'right': self.rotation_speed = -self.rotation_speed 
        self.image = self.base_image
        self.rect = self.image.get_frect(center=(-self.size[0]/2 if spawn == 'left' else WINDOW_WIDTH+self.size[0]/2, random_of_spectrum(0,WINDOW_HEIGHT)))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(1, 0) if spawn == 'left' else pygame.Vector2(-1, 0)

class Asteroid(RotatingObstacle):
    def __init__(self, game: Game, layer: float, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], image: pygame.Surface, speed: int, angle: float = random_of_spectrum(0,360), rotation_speed: float = random_of_spectrum(-180,180)) -> None:
        ASTEROID_ATTRIBUTES: dict[str, list[tuple[int|float, int|float]]] = {'left': [(-70,random_of_spectrum(0,WINDOW_HEIGHT)), (1,uniform(-0.5,0.5))], 'right': [(WINDOW_WIDTH+70,random_of_spectrum(0,WINDOW_HEIGHT)), (-1,uniform(-0.5,0.5))], 'top': [(random_of_spectrum(0,WINDOW_WIDTH),-70), (uniform(-0.5,0.5),1)], 'bottom': [(random_of_spectrum(0,WINDOW_WIDTH),WINDOW_HEIGHT+70), (uniform(-0.5,0.5),-1)]}
        super().__init__(game, layer, groups, image, speed, angle, rotation_speed)
        self.spawn_border = random_of_selection(list(ASTEROID_ATTRIBUTES.keys()))
        self.rect = self.image.get_frect(center=ASTEROID_ATTRIBUTES[self.spawn_border][0])
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(ASTEROID_ATTRIBUTES[self.spawn_border][1])

class SpikeBall(RotatingObstacle):
    def __init__(self, game: Game, layer: float, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], image: pygame.Surface, speed: int, angle: float, rotation_speed: int, spawn: str) -> None:
        super().__init__(game, layer, groups, image, speed, angle, rotation_speed)
        if spawn == 'right': self.base_image = pygame.transform.flip(self.game.spike_ball_image, True, False)
        if spawn == 'left': self.rotation_speed = -self.rotation_speed 
        self.image = self.base_image
        self.rect = self.image.get_frect(center=(-self.size[0]/2 if spawn == 'left' else WINDOW_WIDTH+self.size[0]/2, random_of_spectrum(0,WINDOW_HEIGHT)))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(1, 0) if spawn == 'left' else pygame.Vector2(-1, 0)

# --- shadow guardian related ---
class ShadowGuardian(pygame.sprite.Sprite):
    STATE_DURATIONS = SHADOW_GUARDIAN_STATE_DURATIONS

    def __init__(self, game: Game, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group]) -> None:
        self.game = game
        self._layer = self.game.LAYERS['bosses']
        super().__init__(groups)
        self.max_health: int = SHADOW_GUARDIAN_HEALTH
        self.current_health: int = self.max_health
        self.target_health: int = self.max_health
        self.health_ratio: float = self.max_health / BOSS_HEALTH_BAR_LENGTH
        self.speed: int = SHADOW_GUARDIAN_SPEED
        self.speed_during_summon: int = SHADOW_GUARDIAN_SPEED_DURING_SUMMON
        self.image: pygame.Surface = self.game.shadow_guardian_image
        self.rect: pygame.FRect = self.image.get_frect(center=(WINDOW_CENTER[0], -500))
        self.mask = pygame.mask.from_surface(self.image)
        self.distance_to_player = pygame.Vector2(self.game.player.rect.center) - pygame.Vector2(self.rect.center)
        self.direction = self.distance_to_player
        self.direction.normalize()
        self.hurting: bool = False
        self.hurting_start: float = 0.0
        self.current_state: str = 'follow_player'
        self.select_next_state: bool = False
        self.state_start: float = self.game.play_time
        self.game.shadow_guardian_growl_sound.play()

    def track_player(self) -> None:
        self.distance_to_player = pygame.Vector2(self.game.player.rect.center) - pygame.Vector2(self.rect.center)
        self.direction = self.distance_to_player
        if self.direction.length_squared() != 0:
            self.direction = self.direction.normalize()

    def take_damage(self) -> None:
        self.game.shadow_guardian_hurt_sound.play()
        self.target_health -= SHADOW_GUARDIAN_DAMAGE_PER_SHOT
        if self.target_health > 0:
            self.hurting = True
            self.hurting_start = self.game.play_time
        else: self.game.shadow_guardian_death_sound.play(); ShadowGuardianDeathAnimation(self.game, (self.game.all_sprites, self.game.boss_effect_sprites)); self.kill()

    def update_appearance(self) -> None:
        # adjust facing
        base = self.game.shadow_guardian_image
        if self.distance_to_player[0] < 0:
            base = pygame.transform.flip(base, True, False)
        self.image = base.copy()
        self.mask = pygame.mask.from_surface(self.image)

        # flash red after taking damage
        if self.game.play_time - self.hurting_start > 0.5:
            self.hurting = False
        if self.hurting:
            duration = 0.5
            t = (self.game.play_time - self.hurting_start) / duration
            t = max(0.0, min(t, 1.0))

            # strong at start, then fades out
            intensity = int(255 * (1.0 - t) ** 2)
            if intensity <= 0:
                return

            # refresh mask for current frame (image may be flipped)
            self.mask = pygame.mask.from_surface(self.image)

            # build a surface in the exact shape of the boss
            flash_surf = self.mask.to_surface(
                setcolor=(255, 80, 80, 0),   
                unsetcolor=(0, 0, 0, 0)
            ).convert_alpha()

            flash_surf.set_alpha(intensity)

            # additively brighten only the masked area
            self.image.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def update(self, dt: float) -> None:
        self.track_player()
        self.set_state(dt)
        self.update_appearance()

    # states/phases
    def set_state(self, dt: float) -> None:
        if self.game.play_time - self.state_start >= self.STATE_DURATIONS[self.current_state]: self.select_next_state = True
        if self.select_next_state:
            if self.current_state == 'transition':
                while self.prev_state is self.current_state or self.current_state == 'transition':
                    self.current_state = random_of_selection(list(self.STATE_DURATIONS.keys()))
            else: 
                self.prev_state = self.current_state
                self.current_state = 'transition'
                self.game.shadow_guardian_growl_sound.play()
            self.state_start = self.game.play_time
            self.select_next_state = False

        match(self.current_state):
            case 'follow_player':
                self.follow_player(dt)
            case 'summon_saw_blades':
                self.summon_saw_blades(dt)
            case 'summon_asteroids':
                self.summon_asteroids(dt)
            case 'shoot_energy_ball':
                self.shoot_energy_ball()

    def follow_player(self, dt: float) -> None:
        if self.distance_to_player.length_squared() > 5:
            self.rect.center += dt * self.speed * self.direction

    def summon_saw_blades(self, dt: float) -> None:
        if self.game.play_time - getattr(self, 'last_saw_blade_summon', 0.0) >= SHADOW_GUARDIAN_SAW_BLADE_SPAWN_DURATION:
            SawBlade(self.game, self.game.LAYERS['obstacles'], (self.game.all_sprites, self.game.enemy_sprites, self.game.obstacle_sprites, self.game.boss_obstacle_sprites), self.game.saw_blade_image, SHADOW_GUARDIAN_SAW_BLADE_SPEED, spawn=(random_of_selection(('left', 'right'))))
            self.last_saw_blade_summon = self.game.play_time
        if self.distance_to_player.length_squared() > 5:
            self.rect.center += dt * self.speed_during_summon * self.direction

    def summon_asteroids(self, dt: float) -> None:
        if self.game.play_time - getattr(self, 'last_asteroid_summon', 0.0) >= SHADOW_GUARDIAN_ASTEROID_SPAWN_DURATION:
            Asteroid(self.game, self.game.LAYERS['obstacles'], (self.game.all_sprites, self.game.enemy_sprites, self.game.obstacle_sprites, self.game.boss_obstacle_sprites), self.game.asteroid_image, SHADOW_GUARDIAN_ASTEROID_SPEED, rotation_speed=0)
            self.last_asteroid_summon = self.game.play_time
        if self.distance_to_player.length_squared() > 5:
            self.rect.center += dt * self.speed_during_summon * self.direction

    def shoot_energy_ball(self) -> None:
        if not getattr(self, 'energy_ball', None):
            self.energy_ball: DarkEnergyBall|None = DarkEnergyBall(self.game, self.game.LAYERS['boss_projectiles'], (self.game.all_sprites, self.game.enemy_sprites, self.game.obstacle_sprites, self.game.boss_obstacle_sprites, self.game.energy_ball_sprites), self.rect.center)

class DarkEnergyBall(pygame.sprite.Sprite):
    def __init__(self, game: Game, layer: float, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], pos: tuple[float, float]) -> None:
        self.game = game
        self._layer = layer
        super().__init__(groups)
        self.creation_time = self.game.play_time
        self.health = 2
        self.speed = DARK_ENERGY_BALL_SPEED
        self.image = self.game.dark_energy_ball_image
        self.rect: pygame.FRect = self.image.get_frect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.distance_to_player = pygame.Vector2(self.game.player.rect.center) - pygame.Vector2(self.rect.center)
        self.direction = self.distance_to_player
        self.direction.normalize()
        ObjectGlow(self.game,
                   (self.game.all_sprites, self.game.obstacle_effect_sprites),
                   self,
                   (210,210,210),
                   DARK_ENERGY_BALL_GLOW_RADIUS,
                   pulse=False)
    
    def handle_getting_shot(self) -> None:
        self.game.energy_ball_shot_sound.play()
        self.health -= 1
        if self.health <= 0:
            self.game.shadow_guardian.energy_ball = None
            self.kill()

    def home_in_on_player(self, dt: float) -> None:
        self.distance_to_player = pygame.Vector2(self.game.player.rect.center) - pygame.Vector2(self.rect.center)
        self.direction = self.distance_to_player
        if self.direction.length_squared() != 0:
            self.direction = self.direction.normalize()
        self.rect.center += dt * self.speed * self.direction

    def destroy(self) -> None:
        if self.game.play_time - self.creation_time > DART_ENERGY_BALL_LIFE_TIME:
            self.game.shadow_guardian.energy_ball = None
            self.game.energy_ball_shot_sound.play()
            self.kill()

    def update(self, dt: float) -> None:
        self.home_in_on_player(dt)
        self.destroy()

class ShadowGuardianDeathAnimation(pygame.sprite.Sprite):
    def __init__(self, game: Game, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group]) -> None:
        self.game = game
        self._layer = self.game.LAYERS['boss_death_animation']
        super().__init__(groups)
        self.frame_index = 0
        self.image = self.game.shadow_guardian_death_animation_frames[0]
        self.rect = self.image.get_frect(center=self.game.shadow_guardian.rect.center)

    def update(self, dt: float) -> None:
        if self.frame_index <= len(self.game.shadow_guardian_death_animation_frames):
            self.image = self.game.shadow_guardian_death_animation_frames[int(self.frame_index)]
            if self.game.shadow_guardian.distance_to_player[0] < 0:
                self.image = pygame.transform.flip(self.image, True, False)
            self.frame_index += SHADOW_GUARDIAN_EXPLOSION_SPEED
        else:
            self.game.shadow_guardian_defeated = True
            self.kill()

# --- rotten shadow related ---
class RottenShadow(pygame.sprite.Sprite):
    STATE_DURATIONS = ROTTEN_SHADOW_STATE_DURATIONS

    def __init__(self, game: Game, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group]) -> None:
        self.game = game
        self._layer = self.game.LAYERS['bosses']
        super().__init__(groups)
        self.max_health = ROTTEN_SHADOW_HEALTH
        self.current_health = self.max_health
        self.target_health = self.max_health
        self.health_ratio = self.max_health / BOSS_HEALTH_BAR_LENGTH
        self.speed = ROTTEN_SHADOW_SPEED
        self.speed_during_action = ROTTEN_SHADOW_SPEED_DURING_ACTION
        self.image = self.game.rotten_shadow_image
        self.rect: pygame.FRect = self.image.get_frect(center=(WINDOW_WIDTH + 100, WINDOW_CENTER[1]))
        self.mask = pygame.mask.from_surface(self.image)
        self.distance_to_player = pygame.Vector2(self.game.player.rect.center) - pygame.Vector2(self.rect.center)
        self.direction = self.distance_to_player
        self.direction.normalize()
        self.hurting = False
        self.hurting_start = 0.0
        self.current_state = 'follow_player'
        self.select_next_state = False
        self.state_start = self.game.play_time
        self.next_fireball_time = 0.0
        self.dashing = False
        self.dash_start_time = 0.0
        self.dash_direction = pygame.Vector2()
        self.next_dash_allowed = 0.0
        self.laser_charging = False
        self.laser_firing = False
        self.laser_start_time = 0.0
        self.laser_direction = pygame.Vector2()
        self.next_laser_allowed = 0.0
        self.last_laser_damage_time = 0.0
        self.laser_beam = None
        self.enraged = False
        self.game.rotten_shadow_growl_sound.play()

    def track_player(self) -> None:
        self.distance_to_player = pygame.Vector2(self.game.player.rect.center) - pygame.Vector2(self.rect.center)
        self.direction = self.distance_to_player
        if self.direction.length_squared() != 0:
            self.direction = self.direction.normalize()

    def take_damage(self) -> None:
        self.game.rotten_shadow_hurt_sound.play()
        self.target_health -= ROTTEN_SHADOW_DAMAGE_PER_SHOT
        if self.target_health > 0:
            self.hurting = True
            self.hurting_start = self.game.play_time
        else: self.game.rotten_shadow_death_sound.play(); RottenShadowDeathAnimation(self.game, (self.game.all_sprites, self.game.boss_effect_sprites)); self.kill()

    def enrage(self) -> None:
        if self.enraged:
            return

        if self.target_health <= self.max_health * 0.5:
            self.enraged = True

            self.speed *= SECOND_PHASE_SPEED_MULTIPLIER
            self.speed_during_action *= SECOND_PHASE_SPEED_MULTIPLIER

    def update_appearance(self) -> None:
        # --- base sprite ---
        base = self.game.rotten_shadow_image

        if self.distance_to_player.x < 0:
            base = pygame.transform.flip(base, True, False)

        self.image = base.copy()

        # --- dash darkening ---
        if self.dashing:
            overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0))
            self.image.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # --- damage flash ---
        if self.hurting:
            duration = 0.5
            t = (self.game.play_time - self.hurting_start) / duration
            t = max(0.0, min(t, 1.0))
            intensity = int(255 * (1.0 - t) ** 2)

            if intensity > 0:
                mask = pygame.mask.from_surface(self.image)
                flash = mask.to_surface(
                    setcolor=(255, 80, 80, 0),
                    unsetcolor=(0, 0, 0, 0)
                ).convert_alpha()
                flash.set_alpha(intensity)
                self.image.blit(flash, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            else:
                self.hurting = False

        # --- laser visuals ---
        if self.laser_charging:
            pulse = 0.5 + 0.5 * sin(self.game.play_time * 8)
            glow = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            glow.fill((0, 120, 0, int(120 * pulse)))
            self.image.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


        self.mask = pygame.mask.from_surface(self.image)

    def try_dash(self) -> None:
        if self.dashing:
            return

        if self.game.play_time < self.next_dash_allowed:
            return

        # let him dash only by chance and if he is far enough from the player
        if random.random() < (ROTTEN_SHADOW_DASH_CHANCE_PER_FRAME_1 if self.current_health > self.max_health/2 else 
        ROTTEN_SHADOW_DASH_CHANCE_PER_FRAME_2) and self.distance_to_player.length_squared() > DASH_DISTANCE_THRESHOLD:
            if self.distance_to_player.length_squared() == 0:
                return

            self.dashing = True
            self.dash_start_time = self.game.play_time
            self.dash_direction = self.distance_to_player.normalize()
            self.next_dash_allowed = (self.game.play_time + ROTTEN_SHADOW_DASH_DURATION * 2.5)
            self.game.dash_sound.play()

    def fire_laser(self) -> None:
        origin = pygame.Vector2(self.rect.center)
        direction = self.laser_direction

        length = max(WINDOW_WIDTH, WINDOW_HEIGHT)

        # laser rect (simple but effective)
        laser_rect = pygame.Rect(0, 0, length, ROTTEN_SHADOW_LASER_WIDTH)
        laser_rect.center = origin + direction * (length // 2)
        laser_rect = laser_rect.copy()

    def update(self, dt: float) -> None:
        self.enrage()
        self.track_player()
        self.set_state(dt)

        if self.dashing:
            self.rect.center += self.dash_direction * ROTTEN_SHADOW_DASH_SPEED * dt
            if self.game.play_time - self.dash_start_time >= ROTTEN_SHADOW_DASH_DURATION:
                self.dashing = False

        self.update_appearance()

    # states/phases
    def set_state(self, dt: float) -> None:
        if self.game.play_time - self.state_start >= self.STATE_DURATIONS[str(self.current_state)]: self.select_next_state = True
        if self.select_next_state:
            if self.current_state == 'laser':
                self.laser_charging = False
                self.laser_firing = False
                if self.laser_beam:
                    self.laser_beam.kill()
                    self.laser_beam = None
            if self.current_state == 'transition':
                while self.prev_state is self.current_state or self.current_state == 'transition':
                    self.current_state = random_of_selection(list(self.STATE_DURATIONS.keys()))
            else: 
                self.prev_state = self.current_state
                self.current_state = 'transition'
                self.game.rotten_shadow_growl_sound.play()
            self.state_start = self.game.play_time
            self.select_next_state = False

        match(self.current_state):
            case 'follow_player':
                self.follow_player(dt)
            case 'shoot_fireballs':
                self.shoot_fireballs(dt)
            case 'shoot_radial_fireballs':
                self.shoot_radial_fireballs()
            case 'laser':
                self.laser_attack()

    def follow_player(self, dt: float) -> None:
        self.try_dash()
        if self.distance_to_player.length_squared() > 5:
            self.rect.center += dt * self.speed * self.direction

    def shoot_fireballs(self, dt: float) -> None:
        if self.game.play_time >= self.next_fireball_time:
            self.game.shoot_sound.play()
            self.next_fireball_time = self.game.play_time + (ROTTEN_SHADOW_FIREBALL_INTERVAL_1 if self.current_health > self.max_health/2 else ROTTEN_SHADOW_FIREBALL_INTERVAL_2)
            self.fire_ball = Fireball(self.game, self.game.LAYERS['boss_projectiles'], (self.game.all_sprites, self.game.enemy_sprites, self.game.obstacle_sprites, self.game.boss_obstacle_sprites, self.game.rotten_shadow_fireball_sprites), self.game.blue_fireball_image, self.direction, self.rect.center)
        if self.distance_to_player.length_squared() > 5:
            self.rect.center += dt * self.speed_during_action * self.direction

    def shoot_radial_fireballs(self) -> None:
        if self.game.play_time >= self.next_fireball_time:
            self.game.shoot_sound.play()
            self.next_fireball_time = self.game.play_time + ROTTEN_SHADOW_RADIAL_FIREBALL_INTERVAL
            angles = [i * (360 / (ROTTEN_SHADOW_RADIAL_FIREBALL_COUNT_1 if self.current_health > self.max_health/2 else ROTTEN_SHADOW_RADIAL_FIREBALL_COUNT_2)) for i in range(ROTTEN_SHADOW_RADIAL_FIREBALL_COUNT_1 if self.current_health > self.max_health/2 else ROTTEN_SHADOW_RADIAL_FIREBALL_COUNT_2)]
            angle_modifier = random_of_spectrum(0, 360)
            for angle in angles:
                direction = pygame.Vector2(1, 0).rotate(angle + angle_modifier)
                self.game.shoot_sound.play()
                self.fire_ball = Fireball(self.game, self.game.LAYERS['boss_projectiles'], (self.game.all_sprites, self.game.enemy_sprites, self.game.obstacle_sprites, self.game.boss_obstacle_sprites, self.game.rotten_shadow_fireball_sprites), self.game.blue_fireball_image, direction, self.rect.center)

    def laser_attack(self) -> None:
        now = self.game.play_time

        # start charging
        if not self.laser_charging and not self.laser_firing:
            self.laser_charging = True
            self.game.laser_charge_sound.play()
            self.laser_start_time = now
            self.laser_direction = self.distance_to_player.normalize()

        # charging phase
        if self.laser_charging:
            if now - self.laser_start_time >= (ROTTEN_SHADOW_LASER_CHARGE_TIME_1 if self.current_health > self.max_health/2 else ROTTEN_SHADOW_LASER_CHARGE_TIME_2):
                self.laser_charging = False
                self.laser_firing = True
                self.laser_start_time = now

                # spawn laser beam sprite
                duration = (ROTTEN_SHADOW_LASER_DURATION_1 if self.current_health > self.max_health / 2
                            else ROTTEN_SHADOW_LASER_DURATION_2)
                self.laser_beam = LaserBeam(
                    self.game,
                    (
                        self.game.all_sprites,
                        self.game.enemy_sprites,
                        self.game.boss_obstacle_sprites,
                    ),
                    origin=self.rect.center,
                    direction=self.laser_direction,
                    duration=duration,
                )
            return

        # firing phase
        if self.laser_firing:
            # keep laser attached to boss
            if self.laser_beam:
                self.laser_beam.origin = pygame.Vector2(self.rect.center)

            if now - self.laser_start_time >= (ROTTEN_SHADOW_LASER_DURATION_1 if self.current_health > self.max_health/2 else ROTTEN_SHADOW_LASER_DURATION_2):
                self.laser_firing = False
                self.next_laser_allowed = now

                if self.laser_beam:
                    self.laser_beam.kill()
                    self.laser_beam = None

class LaserBeam(pygame.sprite.Sprite):
    def __init__(self, game: Game, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], origin: tuple[float, float], direction: pygame.Vector2, duration: float) -> None:
        self.game = game
        self._layer = self.game.LAYERS['laser_beam']
        super().__init__(groups)

        self.origin = pygame.Vector2(origin)
        self.direction = direction.normalize()
        self.duration = duration

        self.spawn_time = self.game.play_time

        self.length = int(max(WINDOW_WIDTH, WINDOW_HEIGHT))
        self.width = int(ROTTEN_SHADOW_LASER_WIDTH)

        # Use a PNG beam if available; fall back to a colored rectangle.
        base_img = getattr(self.game, "laser_beam_image", None)
        if base_img is not None:
            # Expected to be horizontal, pointing to the right.
            beam_surf = pygame.transform.scale(base_img, (self.length, self.width))
        else:
            beam_surf = pygame.Surface((self.length, self.width), pygame.SRCALPHA)
            beam_surf.fill((COLOR['rotten_shadow_laser']))

        # Rotate to match direction.
        angle = degrees(atan2(-self.direction.y, self.direction.x))
        self.image = pygame.transform.rotate(beam_surf, angle)

        # Position so that the beam starts at origin and extends forward.
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.center = self.origin + self.direction * (self.length // 2)

        self.mask = pygame.mask.from_surface(self.image)

        self.game.laser_shoot_sound.play()

    def update(self, dt: float) -> None:
        # Follow boss origin every frame.
        self.rect.center = self.origin + self.direction * (self.length // 2)

        # Auto-destroy after its configured duration (and if boss is gone).
        if self.game.play_time - self.spawn_time >= self.duration:
            self.kill()
            return

        boss = getattr(self.game, "rotten_shadow", None)
        if boss is None or not boss.alive():
            self.kill()

class RottenShadowDeathAnimation(pygame.sprite.Sprite):
    def __init__(self, game: Game, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group]) -> None:
        self.game = game
        self._layer = self.game.LAYERS['boss_death_animation']
        super().__init__(groups)
        self.frame_index = 0
        self.image = self.game.rotten_shadow_death_animation_frames[0]
        self.rect: pygame.FRect = self.image.get_frect(center=self.game.rotten_shadow.rect.center)

    def update(self, dt: float) -> None:
        if self.frame_index <= len(self.game.rotten_shadow_death_animation_frames):
            self.image = self.game.rotten_shadow_death_animation_frames[int(self.frame_index)]
            if self.game.rotten_shadow.distance_to_player[0] < 0:
                self.image = pygame.transform.flip(self.image, True, False)
            self.frame_index += ROTTEN_SHADOW_EXPLOSION_SPEED
        else:
            self.game.rotten_shadow_defeated = True
            self.kill()

# --- effects ---
class EffectText(pygame.sprite.Sprite):

    def __init__(self, game: Game, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], text: str, font: pygame.font.Font, color: str, pos: tuple[float, float], lifetime: float = EFFECT_TEXT_DURATION, rise: float = EFFECT_TEXT_RISE_SPEED) -> None:
        self.game = game
        self._layer = self.game.LAYERS['ui_texts']
        super().__init__(groups)
        base = font.render(text, True, color)
        shadow = font.render(text, True, (COLOR['effect_text_shadow']))
        self.image: pygame.Surface = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        self.image.blit(shadow, (2, 2))
        self.image.blit(base, (0, 0))
        self.rect: pygame.Rect = self.image.get_rect(center=pos)
        self.spawn = perf_counter()
        self.lifetime = lifetime
        self.rise = rise
        self.is_effect_text = True

    def update(self, dt: float) -> None:
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

class ObjectGlow(pygame.sprite.Sprite):
    CACHE = {}

    def __init__(self, game: Game, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], object: Obstacle|DarkEnergyBall, glow_color: tuple[int, int, int], glow_radius: int,offsetx: int = 0, offsety: int = 0, pulse: bool = True) -> None:
        self.game = game
        self.object = object
        self._layer = self.game.LAYERS['object_effects'] 
        super().__init__(groups)

        self.pulse = pulse
        self.offsetx = offsetx
        self.offsety = offsety

        key = (glow_color[0], glow_color[1], glow_color[2], glow_radius)

        if key not in ObjectGlow.CACHE:
            radius = glow_radius
            size = radius * 2
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            cx = cy = radius

            for r in range(radius, 0, -1):
                t = r / radius
                alpha = int(255 * (1 - t) ** 2)
                pygame.draw.circle(surf, (*glow_color, alpha), (cx, cy), r)

            ObjectGlow.CACHE[key] = surf

        self.base_glow = ObjectGlow.CACHE[key]
        self.image = self.base_glow.copy()
        self.rect: pygame.Rect = self.image.get_rect(center=(object.rect.centerx + self.offsetx, object.rect.centery + self.offsety))

    def update(self, dt: float) -> None:
        if not self.object.alive():
            self.kill()
            return

        if self.pulse:
            t = self.game.runtime
            pulse = 0.65 + 0.35 * abs(sin(t * JELLYFISH_GLOW_FREQUENCY))
            self.image = self.base_glow.copy()
            self.image.set_alpha(int(255 * pulse))
        else:
            self.image = self.base_glow

        self.rect.center = (self.object.rect.centerx + self.offsetx, self.object.rect.centery + self.offsety,)

class RainDrop(pygame.sprite.Sprite):
    def __init__(self, game: Game, layer: float, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], image: pygame.Surface, speed: int) -> None:
        self.game = game
        self._layer = layer
        super().__init__(groups)
        self.image = image
        self.rect: pygame.FRect = self.image.get_frect(center=(random_of_spectrum(0, WINDOW_WIDTH), -self.image.get_height()/2))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = speed
        self.direction = pygame.Vector2(random_of_selection((-0.05, 0.0, 0.05)), 1)

    def update(self, dt: float) -> None:
        self.rect.center += dt * self.speed * self.direction
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

# --- physics objects ---
class StartBlueberry(Blueberry):
    def __init__(self, game: Game, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], spawn: str, space: pymunk.Space, pos: tuple[float, float]) -> None:
        super().__init__(game, groups, spawn, speed=0, spawn_bias=None, rotate=False)
        self.rect.center = pos

        # ---- Pymunk body/shape ----     
        mass = 1.0
        moment = pymunk.moment_for_circle(mass, 0, 20)
        self.body = pymunk.Body(mass, moment)
        self.body.position = pos

        self.shape = pymunk.Circle(self.body, 20)
        self.shape.elasticity = 0.9
        self.shape.friction = 0.4
        self.shape.sprite_ref = self   # so handlers can find the sprite
        space.add(self.body, self.shape)

    def update(self, dt: float) -> None:
        self.rect.center = self.body.position
    
class StartIcicle(Icicle):
    def __init__(self, game: Game, layer: float, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], image: pygame.Surface, space: pymunk.Space, pos: tuple[float, float]) -> None:
        self.__class__.__name__ = 'Icicle'
        super().__init__(game, layer, groups, image, speed=0)
        self.rect.center = pos
        self.base_image = image
        mass = 6.0
        moment = pymunk.moment_for_poly(mass, [(-33, -60), (33, -60), (0, 70)])

        self.body = pymunk.Body(mass, moment)
        self.body.position = pos

        self.shape = pymunk.Poly(self.body, [(-33, -60), (33, -60), (0, 70)])
        self.shape.elasticity = 0.1
        self.shape.friction = 0.6
        self.shape.sprite_ref = self
        space.add(self.body, self.shape)

    def update(self, dt: float) -> None:
        pos = self.body.position
        angle_deg = -degrees(self.body.angle)
        rotated = pygame.transform.rotozoom(self.base_image, angle_deg, 1.0)

        self.image = rotated
        self.rect = self.image.get_frect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

class GameOverApple(Apple):
    def __init__(self, game: Game, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], spawn: str, space: pymunk.Space, pos: tuple[float, float]) -> None:
        super().__init__(game, groups, spawn, speed=0, spawn_bias=None, rotate=False)
        self.rect.center = pos
        self.base_image = self.image

        # ---- Pymunk body/shape ----     
        mass = 2.0
        moment = pymunk.moment_for_circle(mass, 0, 17)
        self.body = pymunk.Body(mass, moment)
        self.body.position = pos

        self.shape = pymunk.Circle(self.body, 17)
        self.shape.elasticity = 0.6
        self.shape.friction = 0.4
        self.shape.sprite_ref = self   # so handlers can find the sprite
        space.add(self.body, self.shape)

    def update(self, dt: float) -> None:
        angle_deg = -degrees(self.body.angle)  # minus to match screen rotation
        rotated = pygame.transform.rotozoom(self.base_image, angle_deg, 1.0)

        self.image = rotated
        self.rect: pygame.FRect = self.image.get_frect(center=self.body.position)
        self.mask = pygame.mask.from_surface(self.image)

class GameOverChili(Chili):
    def __init__(self, game: Game, groups: Iterable[pygame.sprite.LayeredUpdates|pygame.sprite.Group], spawn: str, space: pymunk.Space, pos: tuple[float, float]) -> None:
        super().__init__(game, groups, spawn, speed=0, spawn_bias=None, rotate=False)
        self.rect.center = pos
        self.base_image = self.image

        # ---- Pymunk body/shape ----     
        mass = 0.5
        moment = pymunk.moment_for_poly(mass, [
    (17, -29),   # top stem
    (15, -25),
    (14, -10),
    (10,  10),
    (-3, 15),
    (-22, 25),
    (3, 24),
    (14, 10),
    (17, -10),
    (19, -25)
])
        self.body = pymunk.Body(mass, moment)
        self.body.position = pos

        self.shape = pymunk.Poly(self.body,[
    (17, -29),   # top stem
    (15, -25),
    (14, -10),
    (10,  10),
    (-3, 15),
    (-22, 25),
    (3, 24),
    (14, 10),
    (17, -10),
    (19, -25)
])
        self.shape.elasticity = 0.6
        self.shape.friction = 0.4
        self.shape.sprite_ref = self   # so handlers can find the sprite
        space.add(self.body, self.shape)

    def update(self, dt: float) -> None:
        pos = self.body.position
        angle_deg = -degrees(self.body.angle)  # minus to match screen rotation
        rotated = pygame.transform.rotozoom(self.base_image, angle_deg, 1.0)

        self.image = rotated
        self.rect = self.image.get_frect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
