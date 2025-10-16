from sprites import *


class Game:
    """Encapsulates the main game logic, event handling, and rendering loop."""

# --- Define game modes ---
    def __init__(self):
        # --- initialization and preloading ---
        self.init_paths()
        self.init_pygame()
        self.init_window()
        self.load_sounds()
        self.set_all_volumes()
        self.load_graphics()
        self.init_game_state()
        self.init_sprites()
        self.load_save()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            self.handle_input()
            self.set_game_mode()
            #print_game_time(self.play_time,self.total_paused,self.runtime) # DEBUGGING
            #print("Track:", self.current_track,"Sound volume:", self.tracks[self.current_track].get_volume(),"Channel volume:", self.music_channel.get_volume()) # DEBUGGING
            if self.state == 'start':
                self.start_screen(dt)
            elif self.state == 'play':
                self.play_loop(dt)
            elif self.state == 'stop':
                self.pause_menu(dt)
            elif self.state == 'game_over':
                self.game_over_screen(dt)
            elif self.state == 'settings':
                self.settings_menu(dt)
            self.present_frame()

    def handle_input(self):
        '''Check for user input regarding non-gameplay actions.'''

        for event in pygame.event.get():
            # --- General events ---
            if event.type == pygame.QUIT:
                self.close_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                        self.toggle_fullscreen()

            # --- start state ---
            if self.state == 'start':
                if (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered):
                    self.start_flash()
                    self.play_start = perf_counter()
                    self.fade_to_black()
                    self.requested_state = 'play'
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.save_game()
                        self.close_game()
                    elif event.key == pygame.K_1:
                        if getattr(self, 'show_start_player', False):
                            delattr(self, 'show_start_player')
                        else: self.show_start_player = True
                    else:
                        self.show_start_hint = True

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
                        self.save_game()
                        self.requested_state = 'start'
                    elif event.key == pygame.K_ESCAPE:
                        self.save_game()
                        self.close_game()
                    elif event.key == pygame.K_1:
                        if getattr(self, 'show_dead_player', False):
                            delattr(self, 'show_dead_player')
                        else: self.show_dead_player = True
                    elif event.key == pygame.K_2:
                        self.show_apple = True
                    else:
                        self.show_game_over_hint = True

            # --- settings state ---
            elif self.state == 'settings':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # if inside a submenu, go back to main settings menu
                        if getattr(self, "active_settings_tab", None):
                            self.active_settings_tab = None
                        else:
                            self.requested_state = self.prev_state

    def set_game_mode(self):
        '''Switches game mode and handles necessary changes.'''
        # check for state change request
        if not self.requested_state or self.requested_state == self.state:
            return
        old, new = self.state, self.requested_state
        self.requested_state = None

        # --- switch ---
        self.state = new

        # --- reset input ---
        pygame.event.clear()
        pygame.key.get_pressed()
        pygame.mouse.get_pressed()

        # --- enter actions ---
        if new == 'start':
            if old == 'game_over':
                self.all_sprites.empty()
                self.init_game_state()
                self.init_sprites()
            self.change_track('start_track', 1)

        elif new == 'play':
            if old == 'start':
                self.play_start = perf_counter()
                self.change_track('game_track_1', fade_ms=1)
                pygame.key.get_pressed()   # resets held keys
            if old == 'stop':
                    self.resume_play_time()
                    if self.music_channel and self.current_track:
                        base = self.base_volumes[self.current_track]
                        self.tracks[self.current_track].set_volume(base)
                        self.music_channel.set_volume(1.0)
                        self.music_dimmed = False

        elif new == 'stop':
            if old != 'settings':
                self.pause_play_time()
                if self.music_channel and self.music_channel.get_busy() and self.current_track:
                    if not getattr(self, 'music_dimmed', False):
                        self.paused_volume = self.base_volumes[self.current_track] * STOP_SCREEN_DIM_FACTOR
                        self.music_channel.set_volume(self.paused_volume)
                        self.music_dimmed = True
            
        elif new == 'game_over':
            self.all_sprites.empty()
            if self.music_channel: self.music_channel.stop()
            self.game_over_sound.play()
            self.fade_to_black(duration=GAME_OVER_SCROLL_SPEED)
            self.change_track('game_over_track')

        elif new == 'settings':
            self.prev_state = old

    def start_screen(self, dt):
        self.screen.fill(COLOR['start_screen_bg'])
        scaled_pos = self.get_scaled_mouse_pos()

        # --- hover sound ---
        hovered_now = self.text_rects['title'].collidepoint(scaled_pos)
        if hovered_now and not self.hover_sound_played:
            self.menu_hover_sound.play()
            self.hover_sound_played = True
        elif not hovered_now:
            self.hover_sound_played = False
        self.hovered = hovered_now

        # --- regular flicker animation ---
        flicker = MAX_FLICKER_INT + (MAX_FLICKER_INT - MIN_FLICKER_INT) * sin(perf_counter() * TITLE_FLICKER_SPEED)
        base_surface = self.text_surfaces['title']
        scaled = pygame.transform.rotozoom(base_surface, 0, 1.1) if self.hovered else base_surface
        scaled.set_alpha(flicker)
        rect = scaled.get_rect(center=self.text_rects['title'].center)
        self.screen.blit(scaled, rect)
        self.start_secrets(dt)

    def start_flash(self):
        """Play title flash and transition cleanly to play mode."""
        self.title_flash_sound.play()
        start = perf_counter()
        while perf_counter() - start < 0.4:
            flicker = 255 * abs(sin((perf_counter() - start) * 25))
            surf = self.text_surfaces['title'].copy()
            surf.set_alpha(flicker)
            rect = surf.get_rect(center=self.text_rects['title'].center)
            self.screen.fill(COLOR['start_screen_bg'])
            self.screen.blit(surf, rect)
            self.present_frame()
            self.clock.tick(FPS)

    def start_secrets(self, dt):
        if getattr(self, 'show_start_hint', False):
            self.screen.blit(self.text_surfaces['start_hint'], self.text_rects['start_hint'])

        if getattr(self, 'show_start_player', False):
            # --- initialize ---
            if not hasattr(self, 'start_player_pos'):
                self.start_player_pos = pygame.Vector2(random_of_spectrum(100,WINDOW_WIDTH-100),random_of_spectrum(100,WINDOW_HEIGHT-100))
                self.start_player_vel = pygame.Vector2(230, -230)
                self.start_player_facing_right = True

            # --- move ---
            self.start_player_pos += self.start_player_vel * dt

            # --- get rect from current position ---
            w, h = self.player_sprite_variants[2].get_size()
            rect = pygame.Rect(0, 0, w, h)
            rect.center = self.start_player_pos

            # --- bounce and clamp horizontally ---
            if rect.left <= 0 or rect.right >= WINDOW_WIDTH:
                self.start_player_vel.x *= -1
                self.start_player_facing_right = not self.start_player_facing_right
            if rect.top <= 0 or rect.bottom >= WINDOW_HEIGHT:
                self.start_player_vel.y *= -1

            rect.clamp_ip(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

            # --- draw with correct facing ---
            img = self.player_sprite_variants[2]
            if not self.start_player_facing_right:
                img = pygame.transform.flip(img, True, False)
            rect = img.get_rect(center=self.start_player_pos)
            self.screen.blit(img, rect)

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
        self.render_score_text()
        self.draw_order()
        self.handle_player_death()
        # present_frame

    def pause_menu(self, dt):
        self.screen.fill(COLOR['stop_screen_bg'])
        self.render_score_text(True, COLOR['ui_text_stop'], COLOR['ui_text_shadow_stop'])
        self.draw_score_text()
        self.render_score_text(True)

        mouse_pos = self.get_scaled_mouse_pos()
        mouse_click = pygame.mouse.get_pressed()[0]

        for btn in self.clickable_icons:
            btn.update(mouse_pos, mouse_click)
            if btn.hover_changed and btn.hovered:
                self.menu_hover_sound.play()
            btn.draw(self.screen)

            if btn.clicked:
                if btn is self.clickable_icons[0]:
                    self.menu_select_sound.play()
                    self.fade_to_black()
                    self.close_game()
                elif btn is self.clickable_icons[1]:
                    self.menu_select_sound.play()
                    self.requested_state = 'play'
                elif btn is self.clickable_icons[2]:
                    self.menu_select_sound.play()
                    self.requested_state = 'settings'

    def game_over_screen(self, dt):
        self.screen.fill('black')
        self.screen.blit(self.text_surfaces['game_over'], self.text_rects['game_over'])
        self.game_over_secrets(dt)
        
    def game_over_secrets(self, dt):
        if getattr(self, 'show_game_over_hint', False):
            self.screen.blit(self.text_surfaces['game_over_hint'], self.text_rects['game_over_hint'])
        if getattr(self,'show_dead_player', False):  
            self.dead_player_rotated = pygame.transform.rotozoom(self.player.image, sin(self.runtime) * 360, 1)
            self.dead_player_rect = self.dead_player_rotated.get_rect(center=self.player.rect.center)
            self.dead_player_mask = pygame.mask.from_surface(self.dead_player_rotated)
            self.screen.blit(self.dead_player_rotated, self.dead_player_rect)
        if getattr(self, 'show_apple', False):
            if not hasattr(self, 'secret_fruits'):
                self.secret_fruits = pygame.sprite.Group()
            Fruit((self.all_sprites, self.secret_fruits),
            self.LAYERS['fruits'],
            random_of_spectrum(300,700),
            self.apple_sprite)
            self.show_apple = False
            
        if hasattr(self, 'secret_fruits'):
            self.secret_fruits.update(dt, self.play_time)
            self.secret_fruits.draw(self.screen)
            if hasattr(self, 'dead_player_rect') and hasattr(self, 'show_dead_player'):
                for fruit in self.secret_fruits.sprites():
                    offset = (fruit.rect.x - self.dead_player_rect.x, fruit.rect.y - self.dead_player_rect.y)
                    if self.dead_player_mask.overlap(pygame.mask.from_surface(fruit.image), offset):
                        fruit.kill()
                        self.eat_fruit_sound.play()

    def settings_menu(self, dt):
            self.screen.fill(COLOR['stop_screen_bg'])
            mouse_pos = self.get_scaled_mouse_pos()
            mouse_click = pygame.mouse.get_just_pressed()[0]

            # --- if no tab active, show main menu ---
            if not self.active_settings_tab:
                for text_btn in self.ui_text_buttons:
                    text_btn.update(mouse_pos, mouse_click)
                    text_btn.draw(self.screen)

                # check clicks
                if self.ui_text_buttons[0].clicked:
                    self.active_settings_tab = "audio"
                    pygame.event.clear()
                    return
                elif self.ui_text_buttons[1].clicked:
                    self.active_settings_tab = "controls"
                    pygame.event.clear()
                    return
                elif self.ui_text_buttons[2].clicked:
                    self.requested_state = self.prev_state
                    pygame.event.clear()
                    return

            elif self.active_settings_tab:
                # back button at bottom
                back_btn = self.ui_text_buttons[2]
                original_pos = back_btn.pos  # save original position
                back_btn.pos = (WINDOW_CENTER[0], WINDOW_HEIGHT - 100)  # move down
                back_btn.rect.center = back_btn.pos

                back_btn.update(mouse_pos, mouse_click)
                back_btn.draw(self.screen)

                if back_btn.clicked:
                    self.active_settings_tab = None
                    pygame.event.clear()

                # restore original position for when we return to main settings
                back_btn.pos = original_pos
                back_btn.rect.center = back_btn.pos

            # --- controls submenu ---
            if self.active_settings_tab == "controls":
                self.screen.blit(self.text_surfaces['controls'], self.text_rects['controls'])

                for btn in self.control_texts:
                    btn.update(mouse_pos, mouse_click)
                    btn.draw(self.screen)

                    if self.control_texts[0].clicked:
                        self.screen.fill('black')
                        pygame.event.clear()
                    if self.control_texts[1].clicked:
                        self.screen.fill('black')
                        pygame.event.clear()
                    if self.control_texts[2].clicked:
                        self.screen.fill('black')
                        pygame.event.clear()
                    if self.control_texts[3].clicked:
                        self.screen.fill('black')
                        pygame.event.clear()
                    if self.control_texts[4].clicked:
                        self.screen.fill('black')
                        pygame.event.clear()
                    if self.control_texts[5].clicked:
                        self.screen.fill('black')
                        pygame.event.clear()
                    if self.control_texts[6].clicked:
                        self.screen.fill('black')
                        pygame.event.clear()
                    if self.control_texts[7].clicked:
                        self.screen.fill('black')
                        pygame.event.clear()

            # --- audio submenu ---
            elif self.active_settings_tab == "audio":
                self.screen.blit(self.text_surfaces['audio'], self.text_rects['audio'])

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
            print("Audio preinit failed. Using defaults.")
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
        self.eat_fruit_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'eat_fruit_sound.wav'))
        self.damage_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'damage_sound.ogg'))
        self.explosion_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'explosion_sound.ogg'))
        self.game_over_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'game_over_sound.ogg'))
        self.record_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'new_record_sound.ogg'))
        self.ability_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'ability_sound.wav'))
        self.dash_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'dash_sound.wav'))

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
        self.eat_fruit_sound.set_volume(EAT_FRUIT_SOUND_VOLUME)
        self.damage_sound.set_volume(DAMAGE_SOUND_VOLUME)
        self.explosion_sound.set_volume(EXPLOSION_SOUND_VOLUME)
        self.game_over_sound.set_volume(GAME_OVER_SOUND_VOLUME)
        self.record_sound.set_volume(RECORD_SOUND_VOLUME)
        self.ability_sound.set_volume(ABILITY_SOUND_VOLUME)
        self.dash_sound.set_volume(DASH_SOUND_VOLUME)

    def load_graphics(self):
        # --- fonts ---
        self.fonts: dict = {'title': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), TITLE_FONT_SIZE),
                            'stats': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), SCORE_FONT_SIZE),
                            'game_over': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), GAME_OVER_FONT_SIZE),
                            'game_over_hint': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), GAME_OVER_HINT_FONT_SIZE),
                            'start_hint': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), START_HINT_FONT_SITZE),}

        # --- pre-render static texts ---
        self.text_surfaces: dict = {'title': self.fonts['title'].render("Shadow Drift", True, COLOR['title_text']),
                                    'game_over': self.fonts['game_over'].render("Game Over!", True, COLOR['game_over_text']),
                                    'game_over_hint': self.fonts['game_over_hint'].render("Play again: ENTER\nClose game: ESC", True, COLOR['game_over_hint']),
                                    'start_hint': self.fonts['start_hint'].render("Start game: RETURN\nClose game: ESC", True, COLOR['start_hint']),
                                    'controls': self.fonts['stats'].render("Controls", True, COLOR['settings_tab_headers']),
                                    'audio': self.fonts['stats'].render("Audio", True, COLOR['settings_tab_headers'])}

        # --- define text positions ---
        self.text_rects: dict = {'title': self.text_surfaces['title'].get_rect(center=WINDOW_CENTER),
                                 'game_over': self.text_surfaces['game_over'].get_rect(center=WINDOW_CENTER),
                                 'game_over_hint': self.text_surfaces['game_over_hint'].get_rect(bottomleft=(15, WINDOW_HEIGHT- 15)),
                                 'start_hint': self.text_surfaces['start_hint'].get_rect(bottomleft=(15, WINDOW_HEIGHT- 15)),
                                 'controls': self.text_surfaces['controls'].get_rect(center=(WINDOW_CENTER[0], 160)),
                                 'audio': self.text_surfaces['audio'].get_rect(center=(WINDOW_CENTER[0], 160))}

        # --- draws ---
        self.player_glows: dict = {"blue": pygame.Surface((80, 80), pygame.SRCALPHA),
                                   "red": pygame.Surface((80, 80), pygame.SRCALPHA)}
        pygame.draw.circle(self.player_glows["blue"], COLOR["blue_player_glow"], (40, 40), 40, width=5)
        pygame.draw.circle(self.player_glows["red"], COLOR["red_player_glow"], (40, 40), 40, width=5)

        # --- images ---
        self.clickable_icons: list = [ClickableIcon(pygame.image.load(join(self.IMG_DIR, "quit_button.png")).convert_alpha(),(WINDOW_WIDTH - 70, 60)),
                                      ClickableIcon(pygame.image.load(join(self.IMG_DIR, "resume_button.png")).convert_alpha(),(WINDOW_WIDTH - 170, 60)),
                                      ClickableIcon(pygame.image.load(join(self.IMG_DIR, "settings_cog_wheel.png")).convert_alpha(),(WINDOW_WIDTH - 270, 60))]
        self.clickable_icons[1].base_image = pygame.transform.scale(self.clickable_icons[1].base_image, (60,60)) # scale resume button
        self.clickable_icons[2].base_image = pygame.transform.scale(self.clickable_icons[2].base_image, (60,60)) # scale settings button

        self.ui_text_buttons: list = [ClickableText("Audio", self.fonts['stats'], (WINDOW_CENTER[0], 300), COLOR ['settings_text_buttons'], COLOR['settings_text_buttons_hovered'], self.menu_select_sound, self.menu_hover_sound),
                                      ClickableText("Controls", self.fonts['stats'], (WINDOW_CENTER[0], 380), COLOR['settings_text_buttons'], COLOR['settings_text_buttons_hovered'], self.menu_select_sound, self.menu_hover_sound),
                                      ClickableText("Back", self.fonts['stats'], (WINDOW_CENTER[0], 460), COLOR['settings_text_buttons'], COLOR['settings_text_buttons_hovered'], self.menu_select_sound, self.menu_hover_sound),]
        
        # Keybinding clickable texts
        if not hasattr(self, "control_texts"):
            self.control_texts = []
            y = 220
            for action, key in KEY_BINDINGS.items():
                label = f"{action.replace('_', ' ').title()}: {pygame.key.name(key).upper()}"
                btn = ClickableText(
                    label,
                    self.fonts['stats'],
                    (WINDOW_CENTER[0], y),
                    COLOR['settings_text_buttons'],
                    COLOR['settings_text_buttons_hovered'],
                    self.menu_select_sound,
                    self.menu_hover_sound)
                self.control_texts.append(btn)
                y += 40

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
        self.apple_sprite = pygame.transform.scale_by(self.apple_sprite, 1.4)

    def init_game_state(self):
        # --- Game starting conditions ---
        self.fullscreen = True
        self.state = None
        self.requested_state = 'start'
        self.active_settings_tab = None

        # --- time tracking ---
        if not hasattr(self,'absolute_start_time'):
            self.absolute_start_time = perf_counter()
        self.play_time = 0.0
        self.play_start = None
        self.pause_start = 0.0
        self.total_paused = 0.0
        self.is_paused = False

        # hover sound
        self.hover_sound_played = getattr(self,'hover_sound_played',False)

        # --- UI flags ---
        # score
        self.record_checked = False
        self.prev_stats = None
        self.stats_text = None
        self.stats_text_shadow = None
        STATS['score'] = 0

        # player death animation
        self.explosion_index = 0
        self.current_explosion_frame = self.explosion_frames[0]

        # obstacle timing
        self.next_obstacle_spawn_time = OBSTACLE_SPAWN_TIME

        for attr in (# reset start secrets
                     'show_start_hint','show_start_player','start_player_pos','start_player_vel','start_player_facing_right',
                     # reset game over secrets
                     'show_game_over_hint','show_apple','secret_fruits','dead_player_rect','dead_player_mask',):
            if hasattr(self, attr):
                delattr(self, attr)

    def init_sprites(self):
        # --- sprite groups and layers ---
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.player_group = pygame.sprite.GroupSingle()
        self.obstacle_sprites = pygame.sprite.Group()
        self.fruit_sprites = pygame.sprite.Group()

        self.LAYERS = {'background': 0,
                       'fruits': 1,
                       'obstacles': 2,
                       'player': 3,}

        # --- instantiate background ---
        self.background = AnimatedBackground(self.all_sprites,
                                             self.LAYERS['background'],
                                             self.backgrounds['bg_1'],)

        # --- instantiate player sprite ---
        Player((self.all_sprites, self.player_group),
                self.LAYERS['player'],
                self.player_sprite_variants,
                self.player_glows,
                self.ability_sound,
                self.dash_sound)
        self.player = self.player_group.sprite

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
        if STATS['score'] < FIRST_PHASE_END:
            speed = 260
        elif FIRST_PHASE_END <= STATS['score'] < THIRD_PHASE_END:
            speed = 350
        elif THIRD_PHASE_END <= STATS['score']:
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
        speed = random_of_spectrum(50,270,False,bias=0.3)
        if random.random() < FRUIT_SPAWN_PER_MINUTE/60 * dt:
            Fruit((self.all_sprites, self.fruit_sprites),
                  self.LAYERS['fruits'],
                  speed,
                  self.apple_sprite)

    def change_background(self):
        if STATS['score'] == FIRST_PHASE_END:
            self.background.frames = self.backgrounds['bg_1']
        elif STATS['score'] == SECOND_PHASE_END:
            self.background.frames = self.backgrounds['bg_2']
        elif STATS['score'] == THIRD_PHASE_END:
            self.background.frames = self.backgrounds['bg_3']

    def check_collisions(self):
        if not self.player.is_alive:
            return
        
        if not self.player.iframes and self.player.can_collide and not self.player.dashing:
            hit = pygame.sprite.spritecollide(self.player, self.obstacle_sprites, True, pygame.sprite.collide_mask)
            if hit:
                self.player.health -= 1
                if self.player.health >= 1:
                    self.damage_sound.play()
                    self.player.speed += 50
                    self.player.glow = self.player.glows['red']
                    self.player.activate_iframes(self.play_time)
                else:
                    self.explosion_sound.play()
                    self.player.kill()
                    self.player.is_alive = False

        eat = pygame.sprite.spritecollide(self.player, self.fruit_sprites, True, pygame.sprite.collide_mask)
        if eat:
            self.eat_fruit_sound.play()
            STATS['score'] += 10

    def check_record(self):
        if STATS['score'] > STATS['record'] and not self.record_checked:
            self.record_checked = True
            self.record_sound.play()

    def render_score_text(self, paused=False, text_color=COLOR['ui_text'], text_shadow_color=COLOR['ui_text_shadow']):
        '''Render text surfaces only when stats change.'''
        self.current_stats = (self.player.health, STATS['score'], STATS['record'])
        if self.current_stats != self.prev_stats or paused:
            text = f"Lives: {self.player.health}  Score: {STATS['score']}  Record: {STATS['record']}"
            self.stats_text = self.fonts['stats'].render(text, True, text_color)
            self.stats_text_shadow = self.fonts['stats'].render(text, True, text_shadow_color)
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
        if not self.player.is_alive and self.explosion_index < len(self.explosion_frames):
            self.screen.blit(self.current_explosion_frame, self.current_explosion_frame.get_rect(center=self.player.rect.center))

        # player glow
        if self.player.ability_ready and self.player.health:
            self.screen.blit(self.player.glow, self.player.rect.move(-5, -5))

    def draw_score_text(self):
        self.screen.blit(self.stats_text_shadow, (22, 22))
        self.screen.blit(self.stats_text, (20, 20))

    def handle_player_death(self):
        if not self.player.is_alive:
            if self.explosion_index < len(self.explosion_frames):
                self.current_explosion_frame = self.explosion_frames[int(self.explosion_index)]
                self.explosion_index += PLAYER_EXPLOSION_SPEED
            else:
                self.requested_state = 'game_over'

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

            if progress >= 1.0:
                pygame.event.clear()
                pygame.key.get_pressed()
                pygame.mouse.get_pressed()
                break

    def change_track(self, key, fade_ms=1000):
        """Switch to another track while preserving base volume."""

        if hasattr(self, 'music_channel') and self.music_channel and self.music_channel.get_busy():
            self.music_channel.stop()

        track = self.tracks[key]
        self.music_channel = track.play(loops=-1, fade_ms=fade_ms)
        self.music_channel.set_volume(self.base_volumes[key])
        self.current_track = key

    def get_scaled_mouse_pos(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        scale_x = BASE_RESOLUTION[0] / self.window.get_width()
        scale_y = BASE_RESOLUTION[1] / self.window.get_height()
        return int(mouse_x * scale_x), int(mouse_y * scale_y)

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
        return perf_counter() - self.absolute_start_time

# --- Execute Lifecycle ---
def main():
    game = Game()
    atexit.register(lambda: game.save_runtime())
    atexit.register(pygame.display.quit)
    atexit.register(pygame.font.quit)
    atexit.register(pygame.mixer.quit)
    atexit.register(pygame.quit)
    game.run()

if __name__ == '__main__':
    main()