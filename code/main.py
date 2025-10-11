from settings import *
from utils import *
from sprites import *


class Game:
    """Encapsulates the main game logic, event handling, and rendering loop."""

# --- Define game modes ---
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
        self.load_save()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            self.handle_input()
            self.set_game_mode()
            if self.state == 'start':
                self.start_screen(dt)
            elif self.state == 'play':
                self.play_loop(dt)
            elif self.state == 'stop':
                self.pause_menu(dt)
            elif self.state == 'game_over':
                self.game_over_screen(dt)
            self.present_frame()

    def handle_input(self):
        '''Check for user input respecting game mode.'''

        for event in pygame.event.get():
            # --- General events ---
            if event.type == pygame.QUIT:
                self.close_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                        self.toggle_fullscreen()

            # --- start state ---
            if self.state == 'start':
                if (not self.title_clicked) and (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered):
                    self.title_flash_sound.play()
                    self.title_clicked = True
                    self.flash_start = perf_counter()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.save_game()
                        self.close_game()

            # --- play state ---
            elif self.state == 'play':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.requested_state = 'stop'

            # --- pause state ---
            elif self.state == 'stop':
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                        self.requested_state = 'play'

            # --- game over state ---
            elif self.state == 'game_over':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.requested_state = 'start'
                    elif event.key == pygame.K_ESCAPE:
                        self.save_game()
                        self.close_game()

    def set_game_mode(self):
        '''Switches game mode and handles necessary changes.'''
        # check for state change request
        if not self.requested_state or self.requested_state == self.state:
            return
        old, new = self.state, self.requested_state
        self.requested_state = None

        # --- switch ---
        self.state = new

        # --- enter actions ---
        if new == 'start':
            self.save_game()
            self.change_track('start_track', 1)
            if old == 'game_over':
                self.reset_to_start()

        elif new == 'play':
            if old == 'start':
                self.play_start = perf_counter()
                self.fade_to_black()
                self.change_track('game_track_1')
            elif old == 'stop':
                self.music_channel.set_volume(self.base_volumes[self.current_track])
                self.resume_play_time()

        elif new == 'stop':
            self.pause_play_time()
            if self.music_channel and self.music_channel.get_busy() and self.current_track:
                self.music_channel.set_volume(self.base_volumes[self.current_track] * STOP_SCREEN_DIM_FACTOR)
            
        elif new == 'game_over':
            if self.music_channel: self.music_channel.stop()
            self.game_over_sound.play()
            self.fade_to_black(duration=GAME_OVER_SCROLL_SPEED)
            self.change_track('game_over_track')

    def start_screen(self, dt):
        self.screen.fill(COLOR['start_screen_bg'])

        # --- get scaled mouse pos ---
        scaled_pos = get_scaled_mouse_pos(self.window, BASE_RESOLUTION)

        # --- hover detection ---
        if self.text_positions['title'].collidepoint(scaled_pos):
            if not self.hovered:
                self.hovered = True
                self.hover_sound_played = False
            if not self.hover_sound_played:
                self.menu_hover_sound.play()
                self.hover_sound_played = True
        else:
            self.hovered = False
            self.hover_sound_played = False

        # --- flicker alpha ---
        if not self.title_clicked:
            flicker = MAX_FLICKER_INT + (MAX_FLICKER_INT - MIN_FLICKER_INT) * sin(perf_counter() * TITLE_FLICKER_SPEED)
        else:
            flicker = 255 * abs(sin((perf_counter() - self.flash_start) * 25))
            if perf_counter() - self.flash_start > 0.4:
                self.play_start = perf_counter()
                self.requested_state = 'play'

        # --- draw title ---
        base_surface = self.text_messages['title']
        scaled = pygame.transform.rotozoom(base_surface, 0, 1.1) if self.hovered else base_surface
        scaled.set_alpha(flicker)
        rect = scaled.get_rect(center=self.text_positions['title'].center)
        self.screen.blit(scaled, rect)

    def play_loop(self, dt):
        # update dt
        # handle_events
        # set_game_mode
        self.spawn_obstacle()
        self.spawn_fruit(dt)
        self.change_background()
        self.update_play_time()
        self.all_sprites.update(dt, self.play_time)
        self.check_collisions()
        self.check_record()
        self.update_death_animation()
        self.render_score_text()
        self.draw_order()
        if not self.player.is_alive and self.explosion_finished:
            self.requested_state = 'game_over'
        # present_frame

    def pause_menu(self, dt):
        self.screen.fill(COLOR['stop_screen_bg'])
        self.render_score_text(True, COLOR['ui_text_stop'], COLOR['ui_text_shadow_stop'])
        self.draw_score_text()
        self.render_score_text(True) # !!!

        mouse_pos = get_scaled_mouse_pos(self.window, BASE_RESOLUTION)
        mouse_click = pygame.mouse.get_pressed()[0]

        for btn in self.ui_buttons:
            btn.update(mouse_pos, mouse_click)
            if btn.hover_changed and btn.hovered:
                self.menu_hover_sound.play()
            btn.draw(self.screen)

            if btn.clicked:
                if btn is self.ui_buttons[0]:
                    self.requested_state = 'play'
                elif btn is self.ui_buttons[1]:
                    self.fade_to_black()
                    self.close_game()

    def game_over_screen(self, dt):
        self.screen.fill('black')
        self.screen.blit(self.text_messages['game_over'], self.text_positions['game_over'])

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
        self.IMG_DIR = join(base_dir, "images")
        self.AUDIO_DIR = join(base_dir, "audio")
        self.DATA_DIR = join(base_dir, "data")
        self.FONT_DIR = join(base_dir, "fonts")
        self.SAVE_FILE = join(user_dir, "save.json")

    def init_pygame(self):
        try:
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=256)
        except:
            print("Audio preinit failed, using defaults.")
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
        self.start_screen_font = pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), TITLE_FONT_SIZE)
        self.score_font = pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), SCORE_FONT_SIZE)
        self.game_over_font = pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), GAME_OVER_FONT_SIZE)

        # --- pre-render static texts ---
        self.text_messages: dict = {
            'title': self.start_screen_font.render('Shadow Drift', True, COLOR['title_text']),
            'game_over': self.game_over_font.render("Game Over!", True, COLOR['game_over_text']),
        }

        self.text_positions: dict = {
            'title': self.text_messages['title'].get_rect(center=WINDOW_CENTER),
            'game_over': self.text_messages['game_over'].get_rect(center=WINDOW_CENTER),
        }

        # --- draws ---
        self.player_glows: dict = {
        "blue": pygame.Surface((80, 80), pygame.SRCALPHA),
        "red": pygame.Surface((80, 80), pygame.SRCALPHA)
        }
        pygame.draw.circle(self.player_glows["blue"], COLOR["blue_player_glow"], (40, 40), 40, width=5)
        pygame.draw.circle(self.player_glows["red"], COLOR["red_player_glow"], (40, 40), 40, width=5)

        # --- images ---

        self.ui_buttons: list = [UIButton(pygame.image.load(join(self.IMG_DIR, "resume_button.png")).convert_alpha(),(WINDOW_WIDTH - 170, 60)),
                                 UIButton(pygame.image.load(join(self.IMG_DIR, "quit_button.png")).convert_alpha(),(WINDOW_WIDTH - 70, 60))]
        self.ui_buttons[0].base_image = pygame.transform.scale(self.ui_buttons[0].base_image, (60,60)) # scale resume button

        self.backgrounds: dict = {
            'bg_1': [pygame.image.load(join(self.IMG_DIR, 'background_1', f'bg1_{i}.png')).convert_alpha() for i in range(11)],
            'bg_2': [pygame.image.load(join(self.IMG_DIR, 'background_2', f'bg2_{i}.png')).convert_alpha() for i in range(11)],
            'bg_3': [pygame.image.load(join(self.IMG_DIR, 'background_3', f'bg3_{i}.png')).convert_alpha() for i in range(11)],}

        self.explosion_frames: list = [pygame.image.load(join(self.IMG_DIR, 'death_animation', f'explosion{i}.png')).convert_alpha() for i in range(16)]

        self.player_sprite_variants: dict = {
            1: pygame.image.load(join(self.IMG_DIR, 'player_1.png')).convert_alpha(),
            2: pygame.image.load(join(self.IMG_DIR, 'player_2.png')).convert_alpha(),
        }

        self.obstacle_sprite_variants: dict = {width: pygame.image.load(join(self.IMG_DIR, f"obstacle_{width}.png")).convert_alpha() for width in (150, 200, 250, 300)}

        self.apple_sprite = pygame.image.load(join(self.IMG_DIR, 'apple.png')).convert_alpha()
        self.apple_sprite = pygame.transform.scale_by(self.apple_sprite, 1.5)
        
    def load_sounds(self):
        # --- game music ---
        self.tracks: dict = {'start_track': pygame.mixer.Sound(join(self.AUDIO_DIR, 'start_track.ogg')),
                             'game_over_track': pygame.mixer.Sound(join(self.AUDIO_DIR, 'game_over_track.ogg')),
                             'game_track_1': pygame.mixer.Sound(join(self.AUDIO_DIR, 'game_track_1.ogg')),
                             'game_track_2': pygame.mixer.Sound(join(self.AUDIO_DIR, 'game_track_2.ogg')),}

        # --- sound effects ---
        self.menu_hover_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'menu_hover_sound.wav'))
        self.menu_select_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'menu_select_sound.wav'))
        self.title_flash_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'title_flash_sound.wav'))
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
        self.menu_hover_sound.set_volume(MENU_HOVER_SOUND_VOLUME)
        self.menu_select_sound.set_volume(MENU_SELECT_SOUND_VOLUME)
        self.title_flash_sound.set_volume(TITLE_FLASH_SOUND_VOLUME)
        self.damage_sound.set_volume(DAMAGE_SOUND_VOLUME)
        self.explosion_sound.set_volume(EXPLOSION_SOUND_VOLUME)
        self.game_over_sound.set_volume(GAME_OVER_SOUND_VOLUME)
        self.record_sound.set_volume(RECORD_SOUND_VOLUME)
        self.ability_sound.set_volume(ABILITY_SOUND_VOLUME)

    def init_game_state(self):
        # --- Game starting conditions ---
        self.fullscreen = True
        self.state = None
        self.requested_state = 'start'

        # --- timing system ---
        self.start_time = perf_counter() # session runtime anchor
        self.play_time = 0.0         # gamplay time
        self.play_start = None
        self.pause_start = 0.0
        self.total_paused = 0.0
        self.is_paused = False

        # --- animation/UI state
        # buttons
        self.title_clicked = False
        self.hovered = False
        self.hover_sound_played = False
        # score text
        self.prev_stats = None
        self.stats_text = None
        self.stats_text_shadow = None
        self.record_checked = False
        # player death animation
        self.explosion_index = 0
        self.explosion_finished = False
        self.explosion_speed = PLAYER_EXPLOSION_SPEED

        # --- music system ---
        self.music_channel = None
        self.current_track = None

    def init_sprites(self):
        # --- sprite groups and layers ---
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.obstacle_sprites = pygame.sprite.Group()
        self.fruit_sprites = pygame.sprite.Group()

        self.LAYERS = {'background': 0,
                       'player': 1, 
                       'fruits': 2,
                       'obstacles': 3,}

        # --- instantiate background ---
        self.background = AnimatedBackground(self.all_sprites,
                                             self.LAYERS['background'],
                                             self.backgrounds['bg_1'],)

        # --- instantiate player sprite ---
        self.player = Player(self.all_sprites,
                             self.LAYERS['player'],
                             self.player_sprite_variants,
                             self.player_glows,
                             self.ability_sound)

    def load_save(self):
        try:
            with open(self.SAVE_FILE) as f:
                save_data = json.load(f)
                STATS['record'] = save_data.get('record',0)
                self.previous_runtime = save_data.get('total_runtime[s]', 0.0)
        except:
            self.previous_runtime = 0.0

# --- Main loop ---

    def spawn_obstacle(self):
        # --- choose speed of obstacle ---
        if self.play_time < 25000:
            speed = 260
        elif 25000 <= self.play_time < 45000:
            speed = 350
        else:
            speed = 450

        # --- spawn obstacle ---
        if not hasattr(self, 'next_obstacle_spawn_time'):
            self.next_obstacle_spawn_time = OBSTACLE_SPAWN_TIME
        if self.play_time >= self.next_obstacle_spawn_time:
            Obstacle((self.all_sprites, self.obstacle_sprites),
                    self.LAYERS['obstacles'], 
                    speed, 
                    self.obstacle_sprite_variants)
            self.next_obstacle_spawn_time = self.play_time + OBSTACLE_SPAWN_TIME

    def spawn_fruit(self, dt):
        speed = random_of_spectrum(50,250,False,bias=0.3)
        if random.random() < FRUIT_SPAWN_PER_MINUTE/60 * dt:
            Fruit((self.all_sprites, self.fruit_sprites),
                  self.LAYERS['fruits'],
                  speed,
                  self.apple_sprite)

    def change_background(self):
        if self.play_time < 20000:
            self.background.frames = self.backgrounds['bg_1']
        elif self.play_time < 40000:
            self.background.frames = self.backgrounds['bg_2']
        else:
            self.background.frames = self.backgrounds['bg_3']

    def check_collisions(self):
        if not self.player.is_alive:
            return
        
        hit = pygame.sprite.spritecollide(self.player, self.obstacle_sprites, True, pygame.sprite.collide_mask)
        if hit: 
            STATS['score'] += 1
            if self.player.can_collide:
                self.player.health -= 1
                if self.player.health >= 1:
                    self.damage_sound.play()
                    self.player.speed += 50
                    self.player.glow = self.player.glows['red']
                else:
                    self.explosion_sound.play()
                    self.player.kill()
                    self.player.is_alive = False

        eat = pygame.sprite.spritecollide(self.player, self.fruit_sprites, True, pygame.sprite.collide_mask)
        if eat:
            STATS['score'] += 10

    def check_record(self):
        if STATS['score'] > STATS['record'] and not self.record_checked:
            self.record_checked = True
            self.record_sound.play()

    def update_death_animation(self):
        if not self.player.is_alive and not self.explosion_finished:
            if self.explosion_index < len(self.explosion_frames):
                self.current_explosion_frame = self.explosion_frames[int(self.explosion_index)]
                self.explosion_index += PLAYER_EXPLOSION_SPEED
            else:
                self.explosion_finished = True

    def render_score_text(self, paused=False, main_color=COLOR['ui_text'], text_shadow_color=COLOR['ui_text_shadow']):
        '''Render text surfaces only when stats change.'''
        self.current_stats = (self.player.health, STATS['score'], STATS['record'])
        if self.current_stats != self.prev_stats or paused:
            text = f"Lives: {self.player.health}  Score: {STATS['score']}  Record: {STATS['record']}"
            self.stats_text = self.score_font.render(text, True, main_color)
            self.stats_text_shadow = self.score_font.render(text, True, text_shadow_color)
            self.prev_stats = self.current_stats

    def draw_order(self):
        # --- DRAWING ORDER ---
        self.draw_sprites()
        self.draw_effects()
        self.draw_score_text()

    def draw_sprites(self):
        self.all_sprites.draw(self.screen)

    def draw_effects(self):
        # player death explosion
        if not self.player.is_alive and not self.explosion_finished:
            self.screen.blit(self.current_explosion_frame, self.current_explosion_frame.get_rect(center=self.player.rect.center))

        # player glow
        if self.player.ability_ready and self.player.health:
            self.screen.blit(self.player.glow, self.player.rect.move(-5, -5))

    def draw_score_text(self):
        self.screen.blit(self.stats_text_shadow, (22, 22))
        self.screen.blit(self.stats_text, (20, 20))

# --- Game functionality ---
    def present_frame(self):
        # get current window size
        window_w, window_h = self.window.get_size()
        # scale screen to window size
        scaled = pygame.transform.smoothscale(self.screen, (window_w, window_h))
        # draw rescaled screen on window
        self.window.blit(scaled, (0, 0))
        # update frame
        pygame.display.flip()

    def save_runtime(self):

        save_data = {}

        try:
            with open(self.SAVE_FILE) as f:
                save_data = json.load(f)
        except:
            pass
    
        total_runtime = save_data.get('total_runtime[s]', 0.0) + self.runtime
        save_data['total_runtime[s]'] = round(total_runtime)

        with open(self.SAVE_FILE, 'w') as f:
            json.dump(save_data, f, indent=2)

    def save_game(self):
        # update record if needed
        if STATS['score'] > STATS['record']:
            STATS['record'] = STATS['score']

        save_data = {}

        try:
            with open(self.SAVE_FILE) as f:
                save_data = json.load(f)
        except:
            pass

        # what to save
        save_data['record'] = STATS['record']

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
            self.window = pygame.display.set_mode(BASE_RESOLUTION)

    def fade_to_black(self, duration=FADE_TO_BLACK_DURATION, smoothness=FADE_TO_BLACK_SMOOTHNESS):
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
            self.clock.tick(FPS)
            if progress >= 1.0:
                break

    def change_track(self, key, fade_ms=1000):
        """Switch to another track while preserving base volume."""
        track = self.tracks[key]
        if self.current_track != key:
            if self.music_channel and self.music_channel.get_busy():
                self.music_channel.fadeout(fade_ms)
            self.music_channel = track.play(loops=-1, fade_ms=fade_ms)
            self.music_channel.set_volume(self.base_volumes[key])
            self.current_track = key

    def reset_to_start(self):
        # scores and flags
        STATS['score'] = 0
        self.record_checked = False
        self.title_clicked = False
        self.hovered = False
        self.hover_sound_played = False
        del self.next_obstacle_spawn_time

        # time + pause state
        self.play_time = 0.0
        self.play_start = None
        self.total_paused = 0.0
        self.is_paused = False

        # sprites
        self.obstacle_sprites.empty()
        self.all_sprites.empty()
        self.background = AnimatedBackground(self.all_sprites, self.LAYERS['background'], self.backgrounds['bg_1'])
        self.player = Player(self.all_sprites, self.LAYERS['player'],
                            self.player_sprite_variants, self.player_glows, self.ability_sound)

        # death anim
        self.explosion_index = 0
        self.explosion_finished = False

# --- Time system ---
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
    atexit.register(lambda: game.save_runtime())
    atexit.register(pygame.quit)
    game.run()

if __name__ == '__main__':
    main()