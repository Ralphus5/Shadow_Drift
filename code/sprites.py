from utils import *

# --- player related ---
class Player(pygame.sprite.Sprite):
    """Player sprite: handles movement, abilities, and player presisentation."""

    def __init__(self, game, groups):
        # --- parameters ---
        self.game = game
        self._layer = self.game.LAYERS['player']
        super().__init__(groups)
        
        # --- gameplay attributes ---
        self.is_alive = True
        self.facing_right = True
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
        self.image = self.game.player_sprite_variants[self.health]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_frect(center=WINDOW_CENTER)

        # --- glow sprite ---
        self.glow_sprite = PlayerGlow(self.game,
                   (self.game.all_sprites, self.game.player_abilities))
        
        # --- fire outline ---
        self.fire_outline_sprite = PlayerFireOutline(self.game,
                                                     (self.game.all_sprites, self.game.player_abilities))

        # --- motion setup ---
        self.direction = pygame.Vector2()
        self.dash_direction = pygame.Vector2()

    def activate_iframes(self):
        if self.can_collide:
            self.iframes = True
            self.iframe_start = self.game.play_time

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
            self.dash_direction = pygame.Vector2(self.direction.normalize())

    def activate_ability(self):
        self.game.ability_sound.play()
        self.ability_start_time = self.game.play_time
        self.ability_ready = False
        self.can_collide = False

    def shoot_fireball(self, shoot_direction):
        self.fireball_ready = False
        self.last_fireball = self.game.play_time
        Fireball(self.game,
                (self.game.all_sprites, self.game.fireball_sprites),
                shoot_direction,
                origin=self.rect.center)

    def get_input(self):
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

    def update_banana_boost(self):
        if self.banana_boosted and self.game.play_time - self.banana_boost_start > BANANA_BOOST_DURATION:
            self.banana_boosted = False

        if self.banana_boosted:
            self.speed = DEFAULT_PLAYER_SPEED + BANANA_SPEED_BOOST if self.health > 1 else ONE_LIFE_PLAYER_SPEED + BANANA_SPEED_BOOST
        else: 
            self.speed = DEFAULT_PLAYER_SPEED if self.health > 1 else ONE_LIFE_PLAYER_SPEED

    def update_fire_power(self):
        if not self.fire_power:
            return
        
        if self.game.play_time - self.fire_power_start > FIRE_POWER_DURATION:
            self.fire_power = False
            return

        if self.game.play_time - self.last_fireball > FIREBALL_SHOOT_COOLDOWN:
            self.fireball_ready = True

        if self.fireball_ready and self.shoot_dir.length_squared() != 0:
            self.shoot_fireball(self.shoot_dir)

    def update_dash(self, dt):
        if not self.dash_ready and self.game.play_time - self.dash_start_time > self.dash_cooldown:
            self.dash_ready = True  

        if self.dash_ready and self.want_dash and self.direction.length_squared() != 0:
            self.want_dash = False
            self.dash()

        if self.dashing and self.game.play_time - self.dash_start_time > self.dash_duration:
            self.dashing = False

    def update_ability(self):
        if not self.ability_ready and self.game.play_time - self.ability_start_time > self.ability_cooldown:
            self.ability_ready = True

        if self.ability_ready and self.want_ability:
            self.want_ability = False
            self.activate_ability()

        if not self.can_collide and self.game.play_time - self.ability_start_time > self.ability_duration:
            self.can_collide = True

    def update_iframes(self):
        if self.iframes and self.game.play_time - self.iframe_start > PLAYER_IFRAMES_DURATION:
            self.iframes = False

    def apply_movement(self, dt):
        if self.dashing:
            self.rect.center += dt * DASH_SPEED * self.dash_direction
            return
        
        if self.direction.length_squared() != 0:
                self.direction = self.direction.normalize()
        self.rect.center += dt * self.speed * self.direction

    def update_appearance(self):
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
            w, h = self.image.get_size()
            shadow = pygame.Surface((w-25, h-25), pygame.SRCALPHA)
            pygame.draw.rect(shadow, COLOR['blue_banana_trail' if self.health > 1 else 'red_banana_trail'], shadow.get_rect(), border_radius=18)
            shadow.set_alpha(100)
            PlayerBananaTrail(self.game, (self.game.all_sprites, self.game.player_abilities), shadow, self.rect.center)

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

    def update(self, dt):
        self.get_input()
        self.update_banana_boost()
        self.update_fire_power()
        self.update_dash(dt)
        self.update_ability()
        self.update_iframes()
        self.apply_movement(dt)
        self.update_appearance()
        self.rect.clamp_ip(pygame.Rect(-10, -7, WINDOW_WIDTH + 19, WINDOW_HEIGHT + 14))

class PlayerGlow(pygame.sprite.Sprite):
    def __init__(self, game, groups):
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
    def __init__(self, game, groups):
        self.game = game
        self._layer = self.game.LAYERS['player_fire_outline']
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

class PlayerDeathAnimation(pygame.sprite.Sprite):
    def __init__(self, game, groups):
        self.game = game
        self._layer = self.game.LAYERS['player_death_animation']
        super().__init__(groups)
        self.frame_index = 0
        self.image = self.game.death_animation_frames[0]
        self.rect = self.image.get_frect(center=self.game.player.rect.center)

    def update(self, dt):
        if self.frame_index < len(self.game.death_animation_frames):
            self.image = self.game.death_animation_frames[int(self.frame_index)]
            if not self.game.player.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
            self.frame_index += PLAYER_EXPLOSION_SPEED 
        else:
            self.game.requested_state = 'game_over'
            self.kill()

class PlayerBananaTrail(pygame.sprite.Sprite):
    def __init__(self, game, groups, image, pos, lifetime=BANANA_TRAIL_LIFETIME):
        self.game = game
        self._layer = self.game.LAYERS['player_banana_trail']
        super().__init__(groups)
        self.image = image.copy()
        self.rect = self.image.get_rect(center=pos)
        self._spawn = perf_counter()
        self._lifetime = lifetime
        self.is_trail = True

    def update(self, dt):
        t = (perf_counter() - self._spawn) / max(self._lifetime, 1e-6)
        alpha = max(0, int(120 * (1.0 - t**2)))
        self.image.set_alpha(alpha)
        if t >= 1.0:
            self.kill()

class Fireball(pygame.sprite.Sprite):
    def __init__(self, game, groups, direction: pygame.Vector2, origin=None, spawn_offset=40):
        self.game = game
        self._layer = self.game.LAYERS['fireballs']
        super().__init__(*groups)
        self.game.shoot_sound.play()
        self.speed = FIRE_BALL_SPEED

        # --- direction ---
        if direction.length_squared() == 0:
            direction = pygame.Vector2(1, 0)
        self.direction = direction.normalize()

        # --- base image and rotation ---
        base_img = self.game.fireball_image
        angle_deg = degrees(atan2(-self.direction.y, self.direction.x))
        self.image = pygame.transform.rotozoom(base_img, angle_deg, 1.0)

        # --- spawn position ---
        if origin is None:
            origin = pygame.Vector2(self.game.player.rect.center)
        else:
            origin = pygame.Vector2(origin)

        center = origin + self.direction * spawn_offset
        self.rect = self.image.get_frect(center=center)
        self.mask = pygame.mask.from_surface(self.image)


    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if (self.rect.right < 0 or self.rect.left > WINDOW_WIDTH or
            self.rect.bottom < 0 or self.rect.top > WINDOW_HEIGHT):
            self.kill()

# --- background and decoration related ---
class AnimatedBackground(pygame.sprite.Sprite):
    """Animated background sprite cycling through frames."""

    def __init__(self, game, groups, frames, scroll, interval=BACKGROUND_FRAME_INTERVALL):
        self.game = game
        self._layer = self.game.LAYERS['backgrounds']
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

# --- fruits ---
class Fruit(pygame.sprite.Sprite):
    """Collectable items that give benefits"""

    def __init__(self, game, groups, speed, spawn_bias=None, rotate=False):
        self.game = game
        self._layer = self.game.LAYERS['fruits']
        super().__init__(groups)
        self.speed = speed
        self.rotate = rotate
        self.image = self.game.fruit_sprite_variants[self.__class__]
        self.rect = self.image.get_frect(center=(random_of_spectrum(60,WINDOW_WIDTH-60,bias=spawn_bias),-80))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(0,1)
        if self.rotate:
            self.angle = 0
            self.rotation_speed = random_of_spectrum(-150,150)
            self.base_image = self.image

    def destroy(self):
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

    def display_pickup_message(self, font, messages):
        key = self.__class__
        if key in messages:
            text, color_key = messages[key]
            EffectText(self.game,
                       (self.game.all_sprites, self.game.UI_texts),
                       text,
                       font,
                       COLOR[color_key],
                       self.rect.center)

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        self.destroy()
        if self.rotate:
            self.angle = (self.angle + self.rotation_speed * dt) % 360
            old_center = self.rect.center
            self.image = pygame.transform.rotozoom(self.base_image, -self.angle, 1)
            self.rect = self.image.get_frect(center=old_center)
            self.mask = pygame.mask.from_surface(self.image)

class Apple(Fruit):
    """Apple collectable: gives 10 points."""

    def apply_effect(self):
        STATS['score'] += APPLE_POINTS

class Blueberry(Fruit):
    """Blueberry collectable: restore 2nd life."""

    def apply_effect(self):
        self.game.player.health = 2

class Banana(Fruit):
    """Banana collectable: temporary speed boost."""

    def apply_effect(self):
        self.game.player.banana_boosted = True
        self.game.player.banana_boost_start = self.game.play_time

class Chili(Fruit):
    """Chili collectable: Grants temporary ability to shoot fire balls."""

    def apply_effect(self):
        self.game.player.fire_power = True
        self.game.player.fire_ball_ready = True
        self.game.player.fire_power_start = self.game.play_time

class Grapes(Fruit):
    """Grapes collectable: gain 1 extra life beyond base health."""

    def apply_effect(self):
        self.game.player.extra_life = 1

class Pear(Fruit):
    """Pear collectable: clear all obstacles currently on screen and gain a point for each."""

    def apply_effect(self):
        for sprite in self.game.obstacle_sprites:
            EffectText(self.game, (self.game.all_sprites, self.game.UI_texts), "+1 point", self.game.fonts['effect_texts'], sprite.effect_text_color, sprite.rect.center)
            self.kill()
            sprite.kill()
            STATS['score'] += 1

# --- obstacles ---
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, game, groups, speed):
        self.game = game
        self._layer = self.game.LAYERS['obstacles']
        super().__init__(groups)
        self.speed = speed

    def handle_getting_shot(self):
        if self not in self.game.boss_obstacle_sprites:
            EffectText(self.game, (self.game.all_sprites, self.game.UI_texts), f"+{POINTS_FOR_OBSTACLE_SHOOT} points", self.game.fonts['effect_texts'], self.effect_text_color, self.rect.center)
            STATS['score'] += POINTS_FOR_OBSTACLE_SHOOT
        self.game.eat_fruit_sound.play()
        self.kill()

    def destroy(self):
        if self.rect.left > WINDOW_WIDTH + 1000 or self.rect.right < -1000 or self.rect.top > WINDOW_WIDTH + 1000 or self.rect.bottom < -1000:
            self.kill()

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        self.destroy()

class Rectangle(Obstacle):
    def __init__(self, game, groups, speed, width):
        super().__init__(game, groups, speed)
        self.width = width
        self.image = self.game.rectangle_sprite_variants[self.width]
        self.size = self.image.get_size()
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH+self.width, random_of_spectrum(0, WINDOW_HEIGHT)))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(-1, 0)
        self.effect_text_color = COLOR[f'{self.width}_rectangle_shot_effect_text']

class Icicle(Obstacle):
    def __init__(self, game, groups, speed):
        super().__init__(game, groups, speed)
        self.image = self.game.icicle_image
        self.size = self.image.get_size()
        self.rect = self.image.get_frect(center=(random_of_spectrum(0,WINDOW_WIDTH, as_float=True), 0-self.size[1]))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(0, 1)
        self.effect_text_color = COLOR['icicle_shot_effect_text']

class SawBlade(Obstacle):
    def __init__(self, game, groups, speed, spawn):
        super().__init__(game, groups, speed)
        self.spawn = spawn
        self.base_image = self.game.saw_blade_image if self.spawn == 'left' else pygame.transform.flip(self.game.saw_blade_image, True, False)
        self.angle = 0
        self.rotation_speed = 180
        self.image = self.base_image
        self.size = self.image.get_size()
        self.rect = self.image.get_frect(center=(-self.size[0]/2 if self.spawn == 'left' else WINDOW_WIDTH+self.size[0]/2, random_of_spectrum(0,WINDOW_HEIGHT)))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(1, 0) if self.spawn == 'left' else pygame.Vector2(-1, 0)
        self.effect_text_color = COLOR['saw_blade_shot_effect_text']

    def update(self, dt):
        super().update(dt)
        self.angle = (self.angle + self.rotation_speed * dt) % 360
        old_center = self.rect.center
        self.image = pygame.transform.rotozoom(self.base_image, -self.angle if self.spawn == 'left' else self.angle, 1)
        self.rect = self.image.get_frect(center=old_center)
        self.mask = pygame.mask.from_surface(self.image)

class Rocket(Obstacle):
    def __init__(self, game, groups, speed):
        super().__init__(game, groups, speed)
        self.image = self.game.rocket_image
        self.size = self.image.get_size()
        self.rect = self.image.get_frect(center=(random_of_spectrum(0,WINDOW_WIDTH, as_float=True), WINDOW_HEIGHT+self.size[1]/2))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(0, -1)
        self.effect_text_color = COLOR['rocket_shot_effect_text']

class Asteroid(Obstacle):
    def __init__(self, game, groups, speed, rotation_speed=random_of_spectrum(-180,180)):
        ASTEROID_ATTRIBUTES: dict = {'left': [(-70,random_of_spectrum(0,WINDOW_HEIGHT)), (1,uniform(-0.5,0.5))], 'right': [(WINDOW_WIDTH+70,random_of_spectrum(0,WINDOW_HEIGHT)), (-1,uniform(-0.5,0.5))], 'top': [(random_of_spectrum(0,WINDOW_WIDTH),-70), (uniform(-0.5,0.5),1)], 'bottom': [(random_of_spectrum(0,WINDOW_WIDTH),WINDOW_HEIGHT+70), (uniform(-0.5,0.5),-1)]}
        super().__init__(game, groups, speed)
        self.rotation_speed = rotation_speed
        self.effect_text_color = COLOR['asteroid_shot_effect_text']
        self.base_image = self.game.asteroid_image
        self.image = self.base_image
        self.size = self.image.get_size()
        self.angle = random_of_spectrum(0,360)
        self.spawn_border = random_of_selection(ASTEROID_ATTRIBUTES.keys())
        self.rect = self.image.get_frect(center=ASTEROID_ATTRIBUTES[self.spawn_border][0])
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(ASTEROID_ATTRIBUTES[self.spawn_border][1])

    def update(self, dt):
        super().update(dt)
        self.angle = (self.angle + self.rotation_speed * dt) % 360
        old_center = self.rect.center
        self.image = pygame.transform.rotozoom(self.base_image, -self.angle, 1)
        self.rect = self.image.get_frect(center=old_center)
        self.mask = pygame.mask.from_surface(self.image)

# --- boss related ---
class Boss(pygame.sprite.Sprite):
    STATE_DURATIONS = BOSS_STATE_DURATIONS

    def __init__(self, game, groups):
        self.game = game
        self._layer = self.game.LAYERS['bosses']
        super().__init__(groups)
        self.health = BOSS_HEALTH
        self.speed = BOSS_SPEED
        self.is_defeated = False
        self.image = self.game.boss_image
        self.rect = self.image.get_frect(center=(WINDOW_CENTER[0], -500))
        self.mask = pygame.mask.from_surface(self.image)
        self.distance_to_player = pygame.Vector2(self.game.player.rect.center) - pygame.Vector2(self.rect.center)
        self.direction = self.distance_to_player
        self.direction.normalize()
        self.hurting = False
        self.hurting_start = 0.0
        self.current_state = 'follow_player'
        self.select_next_state = False
        self.state_start = 0.0
        self.game.boss_growl_sound.play()

    def track_player(self):
        self.distance_to_player = pygame.Vector2(self.game.player.rect.center) - pygame.Vector2(self.rect.center)
        self.direction = self.distance_to_player
        if self.direction.length_squared() != 0:
            self.direction = self.direction.normalize()

    # states/phases
    def set_state(self, dt):
        if self.game.play_time - self.state_start >= self.STATE_DURATIONS[self.current_state]: self.select_next_state = True
        if self.select_next_state:
            self.game.boss_growl_sound.play()
            prev_state = self.current_state
            while prev_state is self.current_state:
                self.current_state = random_of_selection(self.STATE_DURATIONS.keys())
            self.state_start = self.game.play_time
            self.select_next_state = False

        match(self.current_state):
            case 'follow_player':
                self.follow_player(dt)
            case 'summon_saw_blades':
                self.summon_saw_blades()
            case 'summon_asteroids':
                self.summon_asteroids()
            case 'shoot_energy_ball':
                self.shoot_energy_ball()

    def follow_player(self, dt):
        if self.distance_to_player.length_squared() > 5:
            self.rect.center += dt * self.speed * self.direction

    def summon_saw_blades(self):
        if self.game.play_time - getattr(self, 'last_saw_blade_summon', 0.0) >= BOSS_SAW_BLADE_SPAWN_DURATION:
            SawBlade(self.game, (self.game.all_sprites, self.game.enemy_sprites, self.game.obstacle_sprites, self.game.boss_obstacle_sprites), BOSS_SAW_BLADE_SPEED, (random_of_selection(('left', 'right'))))
            self.last_saw_blade_summon = self.game.play_time

    def summon_asteroids(self):
        if self.game.play_time - getattr(self, 'last_asteroid_summon', 0.0) >= BOSS_ASTEROID_SPAWN_DURATION:
            Asteroid(self.game, (self.game.all_sprites, self.game.enemy_sprites, self.game.obstacle_sprites, self.game.boss_obstacle_sprites), BOSS_ASTEROID_SPEED, rotation_speed=0)
            self.last_asteroid_summon = self.game.play_time

    def shoot_energy_ball(self):
        if not getattr(self, 'energy_ball', None):
            self.energy_ball = DarkEnergyBall(self.game, (self.game.all_sprites, self.game.enemy_sprites, self.game.obstacle_sprites, self.game.boss_obstacle_sprites), self.rect.center)

    def take_damage(self):
        self.game.boss_hurt_sound.play()
        self.health -= BOSS_DAMAGE_PER_SHOT
        self.hurting = True
        self.hurting_start = self.game.play_time

    def update_appearance(self):
        # adjust facing
        base = self.game.boss_image
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

    def handle_death(self):
        if self.health <= 0:
            self.is_defeated = True

    def update(self, dt):
        self.track_player()
        self.set_state(dt)
        self.update_appearance()
        self.handle_death()

class DarkEnergyBall(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos):
        self.game = game
        self._layer = self.game.LAYERS['boss_projectiles']
        super().__init__(groups)
        self.creation_time = self.game.play_time
        self.health = 2
        self.speed = DARK_ENERGY_BALL_SPEED
        self.image = self.game.dark_energy_ball_image
        self.rect = self.image.get_frect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.distance_to_player = pygame.Vector2(self.game.player.rect.center) - pygame.Vector2(self.rect.center)
        self.direction = self.distance_to_player
        self.direction.normalize()
    
    def handle_getting_shot(self):
        self.game.energy_ball_shot_sound.play()
        self.health -= 1
        if self.health <= 0:
            self.game.boss.energy_ball = None
            self.kill()

    def home_in_on_player(self, dt):
        self.distance_to_player = pygame.Vector2(self.game.player.rect.center) - pygame.Vector2(self.rect.center)
        self.direction = self.distance_to_player
        if self.direction.length_squared() != 0:
            self.direction = self.direction.normalize()
        self.rect.center += dt * self.speed * self.direction

    def destroy(self):
        if self.game.play_time - self.creation_time > 8:
            self.game.boss.energy_ball = None
            self.game.energy_ball_shot_sound.play()
            self.kill()

    def update(self, dt):
        self.home_in_on_player(dt)
        self.destroy()

# --- effects ---
class EffectText(pygame.sprite.Sprite):
    """Text that pops up after collecting a fruit, indicating the its effect"""

    def __init__(self, game, groups, text, font, color, pos, lifetime=EFFECT_TEXT_DURATION, rise=EFFECT_TEXT_RISE_SPEED):
        self.game = game
        self._layer = self.game.LAYERS['ui_texts']
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