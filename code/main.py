import settings
from sprites import *

# --- variables from settings not to be prefixed with 'settings.' ---
from settings import (WINDOW_WIDTH, WINDOW_HEIGHT, BASE_RESOLUTION, FPS, IMG_DIR, AUDIO_DIR, FONT_DIR, SAVE_FILE, STATS)


class Game:
    def __init__(self):
        # --- initialization and window ---
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.init()
        self.running = True
        self.clock = pygame.time.Clock()

        self.display_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen = pygame.Surface(BASE_RESOLUTION).convert_alpha()


        pygame.display.set_caption('Shadow Drift')
        icon = pygame.image.load(join(IMG_DIR, 'icon.png')).convert_alpha()
        pygame.display.set_icon(icon)
        self.fullscreen = False

        # --- fonts ---
        self.font1 = pygame.font.Font(join(FONT_DIR, 'slkscr.ttf'), 35)
        self.font2 = pygame.font.Font(join(FONT_DIR, 'slkscr.ttf'), 150)

        # --- stats text rendering optimization ---
        self.prev_stats = None
        self.stats_text = None
        self.stats_text_shadow = None

        # --- background animation setup ---
        self.bg_index = 0
        self.bg_timer = 0
        self.bg_interval = 100

        # --- player death animation setup ---
        self.explosion_index = 0
        self.explosion_finished = False
        self.explosion_speed = 1.2

        # --- images ---
        self.backgrounds: dict = {
            'bg1': [pygame.image.load(join(IMG_DIR, 'background1', f'bg1_{i}.png')).convert_alpha()
                    for i in range(11)],
            'bg2': [pygame.image.load(join(IMG_DIR, 'background2', f'bg2_{i}.png')).convert_alpha()
                    for i in range(11)],
            'bg3': [pygame.image.load(join(IMG_DIR, 'background3', f'bg3_{i}.png')).convert_alpha()
                    for i in range(11)],
        }

        self.explosion_frames: list = [
            pygame.image.load(join(IMG_DIR, 'death_animation', f'explosion{i}.png')).convert_alpha()
            for i in range(16)
        ]

        # --- sounds ---
        pygame.mixer.music.load(join(AUDIO_DIR, '8-Bit-Indigestion.ogg'))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.damage_sound = pygame.mixer.Sound(join(AUDIO_DIR, 'damage.ogg'))
        self.damage_sound.set_volume(0.3)
        self.explosion_sound = pygame.mixer.Sound(join(AUDIO_DIR, 'explosion.wav'))
        self.explosion_sound.set_volume(0.5)
        self.game_over_sound = pygame.mixer.Sound(join(AUDIO_DIR, 'game-over.ogg'))
        self.record_sound = pygame.mixer.Sound(join(AUDIO_DIR, 'new_record.ogg'))
        self.ability_sound = pygame.mixer.Sound(join(AUDIO_DIR, 'ability.ogg'))

        # --- sprite groups ---
        self.all_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.player = Player(self.all_sprites, self.ability_sound)

        # --- custom events ---
        self.obstacle_event = pygame.event.custom_type()
        pygame.time.set_timer(self.obstacle_event, 500)
        
        # --- load save ---
        try:
            with open(SAVE_FILE) as f:
                data = json.load(f)
                STATS['record'] = data.get('record', 0)
        except FileNotFoundError:
            pass

    def save(self):
        if STATS['score'] > STATS['record']:
            STATS['record'] = STATS['score']
        save_data = {'record': STATS['record']}
        with open(SAVE_FILE, 'w') as f:
            json.dump(save_data, f, indent=2)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.display_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    # --- game over sequence ---
    def game_over(self):
        self.game_over_sound.play()
        pygame.mixer.music.fadeout(3000)

        # fade to black animation (scaled for fullscreen)
        window_w, window_h = self.display_surface.get_size()
        steps = 10
        bar_width = WINDOW_WIDTH // steps

        for i in range(1, steps + 1):
            pygame.draw.rect(
                self.screen,
                'black',
                ((0, 0), (bar_width * i, WINDOW_HEIGHT))
            )
            # scale and show
            scaled = pygame.transform.smoothscale(self.screen, (window_w, window_h))
            self.display_surface.blit(scaled, (0, 0))
            pygame.display.flip()
            sleep(0.25)

        # draw final "Game Over!" message on base surface
        game_over_msg = self.font2.render("Game Over!", True, "red")
        rect = game_over_msg.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.screen.blit(game_over_msg, rect)

        # scale and display
        scaled = pygame.transform.smoothscale(self.screen, (window_w, window_h))
        self.display_surface.blit(scaled, (0, 0))
        pygame.display.flip()

        sleep(3)
        pygame.quit()
        sys.exit()


    def collision(self):
        return pygame.sprite.spritecollide(self.player, self.obstacle_sprites, True, pygame.sprite.collide_mask)

    # --- main loop ---
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            settings.update_time()

            # --- events ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                elif event.type == self.obstacle_event:
                    if settings.game_time < 20000:
                        Obstacle((self.all_sprites, self.obstacle_sprites), 250, self.record_sound)
                    elif 20000 <= settings.game_time < 40000:
                        Obstacle((self.all_sprites, self.obstacle_sprites), 350, self.record_sound)
                    else:
                        Obstacle((self.all_sprites, self.obstacle_sprites), 450, self.record_sound)

            self.all_sprites.update(dt)

            # --- collisions ---
            if self.collision() and self.player.can_collide:
                self.player.health -= 1
                if self.player.health >= 1:
                    self.damage_sound.play()
                    pygame.draw.circle(self.player.glow, (255, 0, 0, 100), (40, 40), 40, width=5)
                    self.player.speed += 100
                else:
                    self.explosion_sound.play()
                    self.player.kill()

            # --- background animation ---
            if settings.game_time < 20000:
                bg_frames = self.backgrounds['bg1']
            elif 20000 <= settings.game_time < 40000:
                bg_frames = self.backgrounds['bg2']
            else:
                bg_frames = self.backgrounds['bg3']

            self.bg_timer += dt * 1000
            if self.bg_timer >= self.bg_interval:
                self.bg_timer = 0
                self.bg_index = (self.bg_index + 1) % len(bg_frames)


            # --- drawing on base surface (1280x720) ---
            self.screen.blit(bg_frames[self.bg_index], (0, 0))
            self.all_sprites.draw(self.screen)

            # draw explosion on top of all sprites
            if self.player.health <= 0 and not self.explosion_finished:
                if self.explosion_index < len(self.explosion_frames):
                    frame = self.explosion_frames[int(self.explosion_index)]
                    self.screen.blit(frame, frame.get_rect(center=self.player.rect.center))
                    self.explosion_index += self.explosion_speed
                else:
                    self.explosion_finished = True
                    self.running = False


            # text and glow
            self.current_stats = (self.player.health, STATS['score'], STATS['record'])
            if self.current_stats != self.prev_stats:
                text = f"Lives: {self.player.health}  Score: {STATS['score']}  Record: {STATS['record']}"
                self.stats_text = self.font1.render(text, True, (0, 0, 0))
                self.stats_text_shadow = self.font1.render(text, True, (255, 255, 255))
                self.prev_stats = self.current_stats
            self.screen.blit(self.stats_text_shadow, (22, 22))
            self.screen.blit(self.stats_text, (20, 20))
            if self.player.ability_ready and self.player.health:
                self.screen.blit(self.player.glow, self.player.rect.move(-5, -5))

            # --- scale 1280x720 -> fullscreen resolution ---
            window_w, window_h = self.display_surface.get_size()
            scaled = pygame.transform.smoothscale(self.screen, (window_w, window_h))
            self.display_surface.blit(scaled, (0, 0))
            pygame.display.flip()

        self.save()
        self.game_over()
        

if __name__ == '__main__':
    game = Game()
    game.run()