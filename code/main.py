"""Main game loop and logic control."""

import settings
from settings import *
from sprites import *


class Game:
    """Encapsulates the main game logic, event handling, and rendering loop."""

# --- Define Lifecycle ---

    def __init__(self):
        # --- initialization and preloading ---
        self.init_paths()
        self.init_pygame()
        self.init_window()
        self.load_graphics()
        self.load_sounds()
        self.set_all_volumes()
        self.init_game_state()
        self.init_sprites()
        self.create_custom_events()
        self.load_save()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            self.modify_game_music()

            if self.state == 'start':
                self.start_screen()

            elif self.state == 'play':
                self.game_loop(dt)

            elif self.state == 'stop':
                self.pause_menu()

            elif self.state == 'game over':
                self.game_over_screen()
                self.save_game()
                self.close_game()

            self.present_frame()

    def start_screen(self):
            self.screen.fill('lightblue')

    def game_loop(self, dt):
        # update dt
        # handle events
        # change music track accordingly
        self.update_play_time()
        self.update_background(dt)
        self.all_sprites.update(dt, self.play_time)
        self.check_collisions()
        self.check_record()
        self.update_death_animation()
        self.render_score_text()
        self.draw()
        self.check_game_end()
        # present frame

    def pause_menu(self):
        pass

    def game_over_screen(self):

        self.game_over_sound.play()
        self.fade_to_black()
        self.tracks['game_over_track'].play(-1)

        # --- draw "Game Over" message ---
        game_over_msg = self.font2.render("Game Over!", True, COLOR['game_over_text'])
        msg_rect = game_over_msg.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.screen.blit(game_over_msg, msg_rect)

        # --- game over time ---
        end_time = perf_counter() + 3
        while perf_counter() < end_time:
            self.handle_events()     # allows ESC quit, etc.
            self.present_frame()     # keeps window responsive
            self.clock.tick(FPS)

# --- Initialization steps ---

    def init_paths(self):
        # --- detect running mode ---
        if getattr(sys, "frozen", False):
            base_dir = sys._MEIPASS
            user_dir = os.path.expanduser(join("~", "Documents", "ShadowDrift"))
        else:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            user_dir = join(base_dir, "data")

        # --- create save directory if needed ---
        os.makedirs(user_dir, exist_ok=True)

        # --- asset file paths ---
        self.BASE_DIR = base_dir
        self.USER_DIR = user_dir
        self.IMG_DIR   = join(base_dir, "images")
        self.AUDIO_DIR = join(base_dir, "audio")
        self.DATA_DIR  = join(base_dir, "data")
        self.FONT_DIR = join(base_dir, "fonts")
        self.SAVE_FILE = join(user_dir, "save.json")

    def init_pygame(self):
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.init()
        pygame.mixer.set_num_channels(128)
        self.clock = pygame.time.Clock()

    def init_window(self):
        # --- open window ---
        self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen = pygame.Surface(BASE_RESOLUTION).convert_alpha()
        # --- set caption ---
        pygame.display.set_caption('Shadow Drift')
        # --- set icon ---
        icon = pygame.image.load(join(self.IMG_DIR, 'icon.png')).convert_alpha()
        pygame.display.set_icon(icon)

    def load_graphics(self):
        # --- fonts ---
        self.font1 = pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), 35)
        self.font2 = pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), 150)

        # --- images ---
        self.backgrounds: dict = {
            'bg1': [pygame.image.load(join(self.IMG_DIR, 'background1', f'bg1_{i}.png')).convert_alpha() for i in range(11)],
            'bg2': [pygame.image.load(join(self.IMG_DIR, 'background2', f'bg2_{i}.png')).convert_alpha() for i in range(11)],
            'bg3': [pygame.image.load(join(self.IMG_DIR, 'background3', f'bg3_{i}.png')).convert_alpha() for i in range(11)],}

        self.explosion_frames: list = [pygame.image.load(join(self.IMG_DIR, 'death_animation', f'explosion{i}.png')).convert_alpha() for i in range(16)]

        self.player_sprite_variants = {
            (1, 'right'): pygame.image.load(join(self.IMG_DIR, 'player1-right.png')).convert_alpha(),
            (1, 'left'):  pygame.image.load(join(self.IMG_DIR, 'player1-left.png')).convert_alpha(),
            (2, 'right'): pygame.image.load(join(self.IMG_DIR, 'player2-right.png')).convert_alpha(),
            (2, 'left'):  pygame.image.load(join(self.IMG_DIR, 'player2-left.png')).convert_alpha(),
        }

        self.obstacle_sprite_variants: dict = {width: pygame.image.load(join(self.IMG_DIR, f"obstacle_{width}.png")).convert_alpha() for width in (150, 200, 250, 300)}

    def load_sounds(self):
        # --- game music ---
        self.tracks: dict = {'start_track': pygame.mixer.Sound(join(self.AUDIO_DIR, 'start_track.ogg')),
                             'game_over_track': pygame.mixer.Sound(join(self.AUDIO_DIR, 'game_over_track.ogg')),
                             'game_track_1': pygame.mixer.Sound(join(self.AUDIO_DIR, 'game_track_1.ogg')),
                             'game_track_2': pygame.mixer.Sound(join(self.AUDIO_DIR, 'game_track_2.ogg')),}

        # --- sound effects ---
        self.damage_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'damage_sound.ogg'))
        self.explosion_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'explosion_sound.ogg'))
        self.game_over_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'game_over_sound.ogg'))
        self.record_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'new_record_sound.ogg'))
        self.ability_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'ability_sound.ogg'))

    def set_all_volumes(self):
        # --- game music ---
        self.tracks['start_track'].set_volume(START_TRACK_VOLUME)
        self.tracks['game_over_track'].set_volume(GAME_OVER_TRACK_VOLUME)
        self.tracks['game_track_1'].set_volume(GAME_TRACK_1_VOLUME)
        self.tracks['game_track_2'].set_volume(GAME_TRACK_2_VOLUME)

        # set base volumes to restore after dimming by pause menu
        self.base_volumes = {}
        for name, track in self.tracks.items():
            self.base_volumes[name] = track.get_volume()

        # --- sound effects ---
        self.damage_sound.set_volume(DAMAGE_SOUND_VOLUME)
        self.explosion_sound.set_volume(EXPLOSION_SOUND_VOLUME)
        self.game_over_sound.set_volume(GAME_OVER_SOUND_VOLUME)
        self.record_sound.set_volume(RECORD_SOUND_VOLUME)
        self.ability_sound.set_volume(ABILITY_SOUND_VOLUME)

    def init_game_state(self):
        # --- Game starting conditions ---
        self.fullscreen = True
        self.state = 'start'
        self.record_checked = False

        # --- timing system ---
        self.start_time = perf_counter() # session runtime anchor
        self.play_time = 0.0         # gamplay time
        self.play_start = None
        self.pause_start = 0.0
        self.total_paused = 0.0
        self.is_paused = False

        # --- score text rendering setup ---
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
        # --- sprite groups ---
        self.all_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()

        # --- instantiate player sprite ---
        self.player = Player(self.all_sprites, self.player_sprite_variants, self.ability_sound)

    def create_custom_events(self):
        # --- obstacle spawning ---
        self.obstacle_event = pygame.event.custom_type()
        pygame.time.set_timer(self.obstacle_event, int(OBSTACLE_SPAWN_TIME * 1000))

    def load_save(self):
        try:
            with open(self.SAVE_FILE) as f:
                save_data = json.load(f)
                STATS['record'] = save_data.get('record',0)
                self.previous_runtime = save_data.get('total_runtime', 0.0)
        except:
            self.previous_runtime = 0.0

# --- Main loop ---

    def handle_events(self):

        print(f"[time] played = {self.play_time:.3f}s   absolute runtime = {self.runtime}") # DEBUG

        for event in pygame.event.get():
            # --- General events ---
            if event.type == pygame.QUIT:
                self.save_game()
                self.close_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                        self.toggle_fullscreen()

            # --- start state ---
            if self.state == 'start':
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        self.play_start = perf_counter()
                        self.state = 'play'

            # --- play state ---
            elif self.state == 'play':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.pause_play_time()
                        self.state = 'stop'

                if event.type == self.obstacle_event:
                    self.spawn_obstacle()

            # --- pause state ---
            elif self.state == 'stop':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.resume_play_time()
                        self.state = 'play'

            # --- game over state ---
            elif self.state == 'game over':
                if event.type == pygame.KEYDOWN:
                    pass

    def spawn_obstacle(self):
        # --- choose speed of obstacle ---
        if self.play_time < 20000:
            speed = 260
        elif 20000 <= self.play_time < 40000:
            speed = 350
        else:
            speed = 450

        # --- spawn obstacle ---
        Obstacle((self.all_sprites, self.obstacle_sprites), 
                 speed, 
                 self.obstacle_sprite_variants)

    def update_background(self, dt):
        # --- background selection ---
        if self.play_time < 20000:
            self.bg_frames = self.backgrounds['bg1']
        elif self.play_time < 40000:
            self.bg_frames = self.backgrounds['bg2']
        else:
            self.bg_frames = self.backgrounds['bg3']

        # --- background frame selection ---
        self.bg_timer += dt * 1000
        if self.bg_timer >= self.bg_interval:
            self.bg_timer = 0
            self.bg_index = (self.bg_index + 1) % len(self.bg_frames)

    def check_collisions(self):
        hit = pygame.sprite.spritecollide(self.player, self.obstacle_sprites, True, pygame.sprite.collide_mask)
        if hit and self.player.can_collide:
            self.player.health -= 1
            if self.player.health >= 1:
                self.damage_sound.play()
                pygame.draw.circle(self.player.glow, COLOR['red_player_glow'], (40, 40), 40, width=5)
                self.player.speed += 70
            else:
                self.explosion_sound.play()
                self.player.kill()
                self.player.is_alive = False

    def check_record(self):
        if STATS['score'] > STATS['record'] and not self.record_checked:
            self.record_checked = True
            self.record_sound.play()

    def update_death_animation(self):
        if not self.player.is_alive and not self.explosion_finished:
            if self.explosion_index < len(self.explosion_frames):
                self.current_explosion_frame = self.explosion_frames[int(self.explosion_index)]
                self.explosion_index += self.explosion_speed
            else:
                self.explosion_finished = True

    def render_score_text(self):
        '''Render text surfaces only when stats change.'''
        self.current_stats = (self.player.health, STATS['score'], STATS['record'])
        if self.current_stats != self.prev_stats:
            text = f"Lives: {self.player.health}  Score: {STATS['score']}  Record: {STATS['record']}"
            self.stats_text = self.font1.render(text, True, COLOR['ui_text'])
            self.stats_text_shadow = self.font1.render(text, True, COLOR['ui_text_shadow'])
            self.prev_stats = self.current_stats

    def draw(self):
        # --- DRAWING ORDER ---
        # 1. background
        self.screen.blit(self.bg_frames[self.bg_index], (0, 0))

        # 2. gameplay sprites
        self.all_sprites.draw(self.screen)

        # 3. death explosion
        if not self.player.is_alive and not self.explosion_finished:
            self.screen.blit(self.current_explosion_frame, self.current_explosion_frame.get_rect(center=self.player.rect.center))

        # 4. UI elements
        # ability ring
        if self.player.ability_ready and self.player.health:
            self.screen.blit(self.player.glow, self.player.rect.move(-5, -5))

        # score text
        self.screen.blit(self.stats_text_shadow, (22, 22))
        self.screen.blit(self.stats_text, (20, 20))

    def check_game_end(self):
        if not self.player.is_alive and self.explosion_finished:
            self.state = 'game over'

# --- Utility ---
    def present_frame(self):
        # get current window size
        window_w, window_h = self.window.get_size()
        # scale screen to window size
        scaled = pygame.transform.smoothscale(self.screen, (window_w, window_h))
        # draw rescaled screen on window
        self.window.blit(scaled, (0, 0))
        # update frame
        pygame.display.flip()

    def save_game(self):

        # update total_runtime
        total_runtime = self.previous_runtime + self.runtime

        # update record if needed
        if STATS['score'] > STATS['record']:
            STATS['record'] = STATS['score']

        # what to save
        save_data = {
            "record": STATS['record'],
            "total_runtime": round(total_runtime, 3)
        }

        # dump into file
        with open(self.SAVE_FILE, "w") as f:
            json.dump(save_data, f, indent=2)

    def close_game(self):
        pygame.quit()
        sys.exit()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    def fade_to_black(self, duration=1.6, smoothness=500):
        """Fade the screen to black over a fixed duration (seconds), with given smoothness."""
        bar_width = WINDOW_WIDTH / smoothness
        start_time = perf_counter()

        while True:
            now = perf_counter()
            elapsed = now - start_time
            progress = min(elapsed / duration, 1.0)

            # --- draw progressive black bars ---
            filled = int(progress * smoothness)
            pygame.draw.rect(self.screen, 'black', (0, 0, int(bar_width * filled), WINDOW_HEIGHT))
            self.present_frame()

            # --- handle window events so runtime keeps running ---
            self.handle_events()
            self.clock.tick(FPS)

            if progress >= 1.0:
                break

    def modify_game_music(self):
        """Centralized music behavior controller, based on current game state."""
        if not hasattr(self, "music_channel"):
            self.music_channel = None
            self.current_track = None
            self.prev_state = None

        if self.state != self.prev_state:
            if self.state == "start":
                self.change_track("start_track")

            elif self.state == "play":
                if self.music_channel and self.music_channel.get_busy() and self.current_track:
                    # restore base volume
                    self.music_channel.set_volume(self.base_volumes[self.current_track])
                self.change_track("game_track_1")

            elif self.state == "stop":
                if self.music_channel and self.music_channel.get_busy() and self.current_track:
                    # dim relative to base volume
                    self.music_channel.set_volume(
                        self.base_volumes[self.current_track] * STOP_SCREEN_DIM_FACTOR
                    )

            elif self.state == "game over":
                self.music_channel.stop()

            self.prev_state = self.state

    def change_track(self, key, fade_ms=1000):
        """Switch to another track while preserving base volume."""
        track = self.tracks[key]
        if self.current_track != key:
            if self.music_channel and self.music_channel.get_busy():
                self.music_channel.fadeout(fade_ms)
            self.music_channel = track.play(loops=-1, fade_ms=fade_ms)
            self.music_channel.set_volume(self.base_volumes[key])
            self.current_track = key

# --- time system ---
    def update_play_time(self):
        if not self.is_paused and self.play_start is not None:
            self.play_time = perf_counter() - self.play_start - self.total_paused

    def pause_play_time(self):
        if not self.is_paused:
            self.pause_start = perf_counter()
            self.is_paused = True

    def resume_play_time(self):
        if self.is_paused:
            self.total_paused += perf_counter() - self.pause_start
            self.is_paused = False

    @property
    def runtime(self):
        """Total runtime since the program started (seconds)."""
        return perf_counter() - self.start_time

# --- Execute Lifecycle ---

def main():
    game = Game()
    game.run()

if __name__ == '__main__':
    main()