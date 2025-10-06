import settings
from sprites import *

# --- variables from settings not to be prefixed with 'settings.' ---
from settings import (WINDOW_WIDTH, WINDOW_HEIGHT, BASE_RESOLUTION, FPS, IMG_DIR, AUDIO_DIR, FONT_DIR, SAVE_FILE, STATS, OBSTACLE_SPAWN_TIME)


class Game:
    def __init__(self):
        # --- initialization and window ---
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.init()
        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen = pygame.Surface(BASE_RESOLUTION).convert_alpha()
        pygame.display.set_caption('Shadow Drift')
        icon = pygame.image.load(join(IMG_DIR, 'icon.png')).convert_alpha()
        pygame.display.set_icon(icon)
        self.fullscreen = True
        self.running = True

        self.load_assets()
        self.load_sounds()
        self.init_state()
        self.init_sprites()
        self.create_custom_events()
        self.load_save()

    def load_assets(self):
        # --- fonts ---
        self.font1 = pygame.font.Font(join(FONT_DIR, 'slkscr.ttf'), 35)
        self.font2 = pygame.font.Font(join(FONT_DIR, 'slkscr.ttf'), 150)

        # --- images ---
        self.backgrounds: dict = {
            'bg1': [pygame.image.load(join(IMG_DIR, 'background1', f'bg1_{i}.png')).convert_alpha() for i in range(11)],
            'bg2': [pygame.image.load(join(IMG_DIR, 'background2', f'bg2_{i}.png')).convert_alpha() for i in range(11)],
            'bg3': [pygame.image.load(join(IMG_DIR, 'background3', f'bg3_{i}.png')).convert_alpha() for i in range(11)],}

        self.explosion_frames: list = [pygame.image.load(join(IMG_DIR, 'death_animation', f'explosion{i}.png')).convert_alpha() for i in range(16)]

    def load_sounds(self):
        # --- game music ---
        pygame.mixer.music.load(join(AUDIO_DIR, '8-Bit-Indigestion.ogg'))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        # --- other sounds ---
        self.damage_sound = pygame.mixer.Sound(join(AUDIO_DIR, 'damage.ogg'))
        self.damage_sound.set_volume(0.3)
        self.explosion_sound = pygame.mixer.Sound(join(AUDIO_DIR, 'explosion.wav'))
        self.explosion_sound.set_volume(0.5)
        self.game_over_sound = pygame.mixer.Sound(join(AUDIO_DIR, 'game-over.ogg'))
        self.record_sound = pygame.mixer.Sound(join(AUDIO_DIR, 'new_record.ogg'))
        self.ability_sound = pygame.mixer.Sound(join(AUDIO_DIR, 'ability.ogg'))

    def init_state(self):
        # --- score text rendering optimization ---
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

    def init_sprites(self):
        # --- group sprites ---
        self.all_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()

        # --- instantiate player sprite ---
        self.player = Player(self.all_sprites, self.ability_sound)

    def create_custom_events(self):
        # --- obstacle spawning ---
        self.obstacle_event = pygame.event.custom_type()
        pygame.time.set_timer(self.obstacle_event, OBSTACLE_SPAWN_TIME)

    def load_save(self):
        try:
            with open(SAVE_FILE) as f:
                save_data = json.load(f)
                STATS['record'] = save_data.get('record',0)
        except:
            pass

    def save(self):
        if STATS['score'] > STATS['record']:
            save_data = {'record': STATS['score']}
            with open(SAVE_FILE, 'w') as f:
                json.dump(save_data, f, indent=2)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    def scale_and_flip(self):
        # get current window size
        window_w, window_h = self.window.get_size()
        # scale screen to window size
        scaled = pygame.transform.smoothscale(self.screen, (window_w, window_h))
        # draw rescaled screen on window
        self.window.blit(scaled, (0, 0))
        # update frame
        pygame.display.flip()

    def game_over(self):
        # --- music fade ---
        self.game_over_sound.play()
        pygame.mixer.music.fadeout(3000)

        # --- screen fades to black ---
        steps = 10
        bar_width = WINDOW_WIDTH // steps
        for i in range(1, steps + 1):
            pygame.draw.rect(self.screen, 'black', ((0, 0), (bar_width * i, WINDOW_HEIGHT)))
            self.scale_and_flip()
            sleep(0.25)

        # --- draw "Game Over" message ---
        game_over_msg = self.font2.render("Game Over!", True, "red")
        msg_rect = game_over_msg.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.screen.blit(game_over_msg, msg_rect)

        # --- scale and display ---
        self.scale_and_flip()
        sleep(3)

        # --- exit game ---
        pygame.quit()
        sys.exit()

    def collision(self):
        return pygame.sprite.spritecollide(self.player, self.obstacle_sprites, True, pygame.sprite.collide_mask)

    def run(self):
        while self.running:

            # ------------------------------ START OF GAME LOOP -------------------------------
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

            # draw background
            self.screen.blit(bg_frames[self.bg_index], (0, 0))

            # draw sprites
            self.all_sprites.draw(self.screen)

            # draw explosion if player is dead
            if self.player.health <= 0 and not self.explosion_finished:
                if self.explosion_index < len(self.explosion_frames):
                    frame = self.explosion_frames[int(self.explosion_index)]
                    self.screen.blit(frame, frame.get_rect(center=self.player.rect.center))
                    self.explosion_index += self.explosion_speed
                else:
                    self.explosion_finished = True
                    self.running = False

            # draw text
            self.current_stats = (self.player.health, STATS['score'], STATS['record'])
            if self.current_stats != self.prev_stats:
                text = f"Lives: {self.player.health}  Score: {STATS['score']}  Record: {STATS['record']}"
                self.stats_text = self.font1.render(text, True, (0, 0, 0))
                self.stats_text_shadow = self.font1.render(text, True, (255, 255, 255))
                self.prev_stats = self.current_stats
            self.screen.blit(self.stats_text_shadow, (22, 22))
            self.screen.blit(self.stats_text, (20, 20))

            # draw player glow if alive
            if self.player.ability_ready and self.player.health:
                self.screen.blit(self.player.glow, self.player.rect.move(-5, -5))

            # --- display frame ---
            self.scale_and_flip()
            # ------------------------------ END OF GAME LOOP ------------------------------

        # --- closing sequence ---
        self.save()
        self.game_over()
        

if __name__ == '__main__':
    game = Game()
    game.run()