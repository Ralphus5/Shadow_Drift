from sprites import *
import settings

class Game:

# --- Define game modes ---
    def __init__(self):
        self.init_paths()
        self.init_pygame()
        self.init_menu_physics()
        self.load_settings()
        self.init_window()
        self.load_sounds()
        self.set_all_volumes()
        self.load_graphics()
        self.create_custome_events()
        self.init_game_state()
        self.init_sprites()
        self.load_save()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events_and_input()
            self.set_game_mode()
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
            #print_game_time(self) # DEBUGGING
            #print_track_volume(self) # DEBUGGING
            #print(self.player.speed) # DEBUGGING
            #print_sprite_counts(self) # DEBUGGING
            #show_rects(self.all_sprites, self.screen) # DEBUGGING
            present_frame(self)

    def handle_events_and_input(self):
        '''Check for user input regarding non-gameplay actions and handling timed events.'''

        for event in pygame.event.get():
            # --- General events ---
            if event.type == pygame.QUIT:
                close_game()

            if event.type == pygame.KEYDOWN:
                if event.key == KEY_BINDINGS['fullscreen'] and not self.waiting_for_key:
                        toggle_fullscreen(self)

            # --- start state ---
            if self.state == 'start':
                if (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered):
                    title_flash(self)
                    fade_to_black(self)
                    self.requested_state = 'play'
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        save_game(self)
                        close_game()
                    elif event.key == pygame.K_1:
                        if getattr(self, 'show_start_player', False):
                            delattr(self, 'show_start_player')
                        else: self.show_start_player = True
                    elif event.key == pygame.K_2:
                        if not self.start_ability and getattr(self, 'show_start_player', False):
                            self.ability_sound.play()
                            self.start_ability = True
                            self.start_ability_time = perf_counter()
                    elif event.key == pygame.K_3:
                        self.show_blueberry = True
                    elif event.key == pygame.K_4:
                        self.show_icicle = True
                    elif event.key == pygame.K_5:
                        kill_sprites(self.secret_fruits, space=self.menu_space)
                    elif event.key == pygame.K_6:
                        kill_sprites(self.secret_obstacles, space=self.menu_space)
                    else:
                        if event.key != KEY_BINDINGS['fullscreen']:
                            self.show_start_hint = True
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button in (PAD_START_BUTTON, PAD_SELECT_BUTTON):
                        title_flash(self)
                        fade_to_black(self)
                        self.requested_state = 'play'
                    elif event.button == PAD_HOME_BUTTON:
                        save_game(self)
                        close_game()
                    else: self.show_start_hint = True

            # --- play state ---
            elif self.state == 'play':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.player.is_alive and self.requested_state != 'game_over':
                        self.requested_state = 'stop'

            # controller buttons
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == PAD_B_BUTTON:
                        self.player.want_dash = True
                    elif event.button == PAD_A_BUTTON:
                        self.player.want_ability = True
                    elif event.button in (PAD_START_BUTTON, PAD_SELECT_BUTTON, PAD_HOME_BUTTON) and self.player.is_alive and self.requested_state != 'game_over':
                        self.requested_state = 'stop'

                elif event.type == self.score_event:
                    STATS['score'] += 1

            # --- pause state ---
            elif self.state == 'stop':
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                        if getattr(self, 'show_credits',False): 
                            self.show_credits = False
                            self.credits_title_rect.center = WINDOW_CENTER
                            for attr in ('header_counter', 'credits_instances', 'last_created'):
                                if hasattr(self, attr): delattr(self, attr)
                        elif getattr(self, 'quit_prompt', False): self.quit_prompt = False
                        else: self.requested_state = 'play'

                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button in (PAD_START_BUTTON, PAD_SELECT_BUTTON, PAD_HOME_BUTTON):
                        self.requested_state = 'play'
                    
                if event.type == self.credits_event and getattr(self, 'show_credits', False):
                    if not getattr(self, 'header_counter', False): self.header_counter = 1
                    else: self.header_counter += 1
                    if self.header_counter <= len(self.credits_texts):
                        self.credits_instances.append(CreditsText(self.credits_texts[self.header_counter-1],
                                    self.fonts['credits_header'],
                                    (WINDOW_CENTER[0], WINDOW_HEIGHT),
                                    COLOR['credits_header'],))
                        self.credits_instances.append(CreditsText("Raphael Glueck",
                                    self.fonts['credits_name'],
                                    (WINDOW_CENTER[0], WINDOW_HEIGHT + 50),
                                    COLOR['credits_name'],))
                    else: 
                        if not getattr(self, 'last_created', False): 
                            self.credits_instances.append(CreditsText("Thanks for playing!",
                                        self.fonts['credits_header'],
                                        (WINDOW_CENTER[0], WINDOW_HEIGHT),
                                        COLOR['title_text'],))
                            self.last_created = True

            # --- game over state ---
            elif self.state == 'game_over':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        save_game(self)
                        self.requested_state = 'start'
                    elif event.key == pygame.K_ESCAPE:
                        save_game(self)
                        close_game()
                    elif event.key == pygame.K_1:
                        if getattr(self, 'show_dead_player', False):
                            self.show_dead_player = False
                        else: self.show_dead_player = True
                    elif event.key == pygame.K_2:
                        if getattr(self, 'show_dead_player', False):
                            self.show_fireball = True 
                    elif event.key == pygame.K_3:
                        self.show_apple = True
                    elif event.key == pygame.K_4:
                        self.show_chili = True
                    elif event.key == pygame.K_5:
                        self.show_rectangle = True
                    elif event.key == pygame.K_6:
                        kill_sprites(self.secret_fruits, space=self.menu_space)
                    else:
                        if event.key != KEY_BINDINGS['fullscreen']:
                            self.show_game_over_hint = True
                
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button in (PAD_START_BUTTON, PAD_SELECT_BUTTON):
                        save_game(self)
                        self.requested_state = 'start'
                    elif event.button == PAD_HOME_BUTTON:
                        save_game(self)
                        close_game()
                    else: self.show_game_over_hint = True

            # --- settings state ---
            elif self.state == 'settings':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and not self.waiting_for_key:
                        if self.active_settings_tab:
                            self.active_settings_tab = None
                        else:
                            self.requested_state = self.prev_state
                            save_settings(self)

                    if self.waiting_for_key:
                        # assign new key to the selected action
                        if event.key != pygame.K_ESCAPE:
                            KEY_BINDINGS[self.waiting_for_key] = event.key
                        self.waiting_for_key = None
                        pygame.event.clear()
                        # rebuild control texts
                        self.control_texts.clear()

                        # re-add reset button first
                        self.control_texts.append(ClickableText("Reset to Defaults",
                                                                self.fonts["settings_texts"],
                                                                (WINDOW_CENTER[0], 110),
                                                                COLOR['clickable_text_buttons'],
                                                                COLOR['clickable_text_buttons_hovered'],
                                                                self.menu_select_sound,
                                                                self.menu_hover_sound))

                        # rebuild keybind buttons below it
                        y = 180
                        for action, key in KEY_BINDINGS.items():
                            label = f"{action.replace('_', ' ').title()}: {pygame.key.name(key).upper()}"
                            self.control_texts.append(ClickableText(label,
                                                                    self.fonts['settings_texts'],
                                                                    (WINDOW_CENTER[0], y),
                                                                    COLOR['clickable_text_buttons'],
                                                                    COLOR['clickable_text_buttons_hovered'],
                                                                    self.menu_select_sound,
                                                                    self.menu_hover_sound))
                            y += 40

    def set_game_mode(self):
        '''Switches game mode and handles necessary changes.'''
        # check for state change request
        if not self.requested_state or self.requested_state == self.state:
            if getattr(self, 'show_credits', False) and self.current_track != 'credits_track':
                self.pre_credits_track = self.current_track
                change_track(self, 'credits_track', fade_ms=0, loop=False)
            elif not getattr(self, 'show_credits', False) and self.current_track == 'credits_track':
                change_track(self, self.pre_credits_track, fade_ms=0)
                self.music_channel.set_volume(self.base_volumes[self.current_track] * STOP_SCREEN_DIM_FACTOR)
            return
        
        old, new = self.state, self.requested_state
        self.requested_state = None
        self.state = new

        # --- enter actions ---
        if new == 'start':
            if old == 'game_over':
                kill_sprites(self.all_sprites, space=self.menu_space)
                self.init_game_state()
                self.init_sprites()
            change_track(self, 'start_track')

        elif new == 'play':
            if old == 'start':
                kill_sprites(self.all_sprites, exceptions=[self.player, self.player.glow_sprite, self.player.fire_outline_sprite, self.background], space=self.menu_space)
                self.play_start = perf_counter()
                change_track(self, 'game_track_1')
                pygame.key.get_pressed()
                clear_input()
            if old == 'stop':
                    resume_play_time(self)
                    if self.music_channel and self.current_track:
                        base = self.base_volumes[self.current_track]
                        self.tracks[self.current_track].set_volume(base)
                        self.music_channel.set_volume(1.0)
                        self.music_dimmed = False

        elif new == 'stop':
            if old != 'settings':
                pause_play_time(self)
                if self.music_channel and self.music_channel.get_busy() and self.current_track:
                    if not getattr(self, 'music_dimmed', False):
                        self.paused_volume = self.base_volumes[self.current_track] * STOP_SCREEN_DIM_FACTOR
                        self.music_channel.set_volume(self.paused_volume)
                        self.music_dimmed = True
            
        elif new == 'game_over':
            kill_sprites(self.all_sprites)
            if self.music_channel: self.music_channel.stop()
            self.game_over_sound.play()
            fade_to_black(self, duration=GAME_OVER_FADE_DURATION)
            clear_input()
            change_track(self, 'game_over_track')
            self.text_surfaces['game_over_score'] = self.fonts['game_over_score'].render(f"Score: {STATS['score']}", True, COLOR['game_over_text'])
            self.text_rects['game_over_score'] = self.text_surfaces['game_over_score'].get_rect(topleft=(10, 10))
            
        elif new == 'settings':
            self.prev_state = old

    def start_screen(self, dt):
        self.menu_space.step(dt)
        self.screen.fill(COLOR['start_screen_bg'])
        scaled_pos = get_scaled_mouse_pos(self)

        # --- hover sound ---
        hovered_now = self.text_rects['title'].collidepoint(scaled_pos)
        if hovered_now and not getattr(self, 'hover_sound_played', False):
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
            self.start_player_pos = pygame.Vector2(rect.center)

            # --- adjust facing ---
            img = self.player_sprite_variants[2].copy()
            if not self.start_player_facing_right:
                img = pygame.transform.flip(img, True, False)

            # --- use ability ---
            if self.start_ability:
                progress = (perf_counter() - self.start_ability_time) / self.start_ability_duration
                progress = max(0.0, min(progress, 1.0))
                darkness = 255 - int(255 * min(progress * PLAYER_BLACK_FADE_SPEED, 1))
                overlay = pygame.Surface(self.player_sprite_variants[2].get_size(), pygame.SRCALPHA)
                overlay.fill((darkness, darkness, darkness))
                img.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                if perf_counter() - self.start_ability_time > self.start_ability_duration:
                    self.start_ability = False

            # --- draw ---
            rect = img.get_rect(center=self.start_player_pos)
            self.screen.blit(img, rect)

        if getattr(self, 'show_blueberry', False):
            StartBlueberry(self,
                          (self.all_sprites, self.secret_fruits),
                          self.menu_space,
                          pos=(random_of_spectrum(30,1250), -25))
            self.show_blueberry = False

        if getattr(self, 'show_icicle', False):
            StartIcicle(self,
                   self.LAYERS['obstacles'],
                   (self.all_sprites, self.secret_obstacles),
                   self.icicle_image,
                   self.menu_space,
                   (random_of_spectrum(50,1230), -60))
            self.show_icicle = False

        if getattr(self, 'secret_fruits', False):
            self.secret_fruits.update(dt)
            self.secret_fruits.draw(self.screen)
            if getattr(self, 'show_start_player', False):
                for fruit in self.secret_fruits.sprites():
                    offset = (fruit.rect.x - rect.x, fruit.rect.y - rect.y)
                    if pygame.mask.from_surface(img).overlap(pygame.mask.from_surface(fruit.image), offset):
                        self.menu_space.remove(fruit.body, fruit.shape)
                        fruit.kill()
                        self.eat_fruit_sound.play()

        if getattr(self, 'secret_obstacles', False):
            self.secret_obstacles.update(dt)
            self.secret_obstacles.draw(self.screen)
            if getattr(self, 'show_start_player', False) and not self.start_ability:
                for obstacle in self.secret_obstacles.sprites():
                    offset = (obstacle.rect.x - rect.x, obstacle.rect.y - rect.y)
                    if pygame.mask.from_surface(img).overlap(pygame.mask.from_surface(obstacle.image), offset):
                        self.menu_space.remove(obstacle.body, obstacle.shape)
                        obstacle.kill()
                        self.damage_sound.play()

    def play_loop(self, dt):
        # update dt
        # handle_events
        # set_game_mode
        update_play_time(self)
        self.set_phase(dt)
        self.all_sprites.update(dt)
        self.collisions()
        self.check_record()
        self.all_sprites.draw(self.screen)
        self.draw_boss_health_bar()
        self.draw_hearts()
        self.draw_score_text(COLOR[f'score_{self.current_phase}_phase'], COLOR[f'score_shadow_{self.current_phase}_phase'])
        # present_frame

    def pause_menu(self, dt):
        if not getattr(self, 'show_credits', False):
            mouse_pos = get_scaled_mouse_pos(self)
            mouse_click = pygame.mouse.get_pressed()[0]
            self.all_sprites.draw(self.screen)
            self.draw_boss_health_bar()

            # --- dim effect ---
            dim = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)).convert_alpha()
            dim.fill((0, 0, 0, 140))
            self.screen.blit(dim, (0, 0))

            if not getattr(self, 'quit_prompt', False):
                # --- display main pause menu ---
                self.draw_hearts()
                self.draw_score_text(COLOR[f'score_{self.current_phase}_phase'], COLOR[f'score_shadow_{self.current_phase}_phase'])
                self.credits_btn.update(mouse_pos, mouse_click)
                self.credits_btn.draw(self.screen)
                if self.credits_btn.clicked:
                    self.show_credits = True
                    pygame.time.set_timer(self.credits_event, 5000)
                for btn in self.clickable_icons:
                    btn.update(mouse_pos, mouse_click)
                    if btn.hovered:
                        if btn is self.clickable_icons[0]:
                            self.screen.blit(self.text_surfaces['quit_icon_text'], self.text_rects['quit_icon_text'])
                        elif btn is self.clickable_icons[1]:
                            self.screen.blit(self.text_surfaces['play_icon_text'], self.text_rects['play_icon_text'])
                        elif btn is self.clickable_icons[2]:
                            self.screen.blit(self.text_surfaces['settings_icon_text'], self.text_rects['settings_icon_text'])
                        if btn.hover_changed:
                            self.menu_hover_sound.play()
                    btn.draw(self.screen)

                    if btn.clicked:
                        if btn is self.clickable_icons[0]:
                            self.menu_select_sound.play()
                            self.quit_prompt = True
                        elif btn is self.clickable_icons[1]:
                            self.menu_select_sound.play()
                            self.requested_state = 'play'
                        elif btn is self.clickable_icons[2]:
                            self.menu_select_sound.play()
                            self.requested_state = 'settings'
            else:
                # --- display quit prompt ---
                self.screen.blit(self.quit_prompt_surface, self.quit_prompt_rect)
                self.quit_prompt_surface.blit(self.text_surfaces['quit_prompt_heading'], self.text_rects['quit_prompt_heading'])

                for btn in (self.yes_btn, self.no_btn):
                    btn.update(mouse_pos, mouse_click)
                    btn.draw(self.screen)

                if self.yes_btn.clicked:   
                    fade_to_black(self)
                    close_game()
                elif self.no_btn.clicked:
                    self.quit_prompt = False
        
        else:
            # --- display credits ---
            if not hasattr(self, 'credits_instances'): self.credits_instances = []
            self.screen.fill(COLOR['credits_bg'])
            if self.credits_title_rect.bottom > 0:
                self.screen.blit(self.credits_title_surf, self.credits_title_rect)
                self.credits_title_rect.bottom -= 60 * dt

            for instance in self.credits_instances:
                if instance.rect.bottom > 0:
                    if instance.text == "Thanks for playing!" and instance.rect.centery <= WINDOW_CENTER[1]:
                        instance.rect.center = WINDOW_CENTER
                        self.screen.blit(self.text_surfaces['credits_hint'], self.text_rects['credits_hint'])
                    else:
                        instance.update(dt)
                    instance.draw(self.screen)

    def game_over_screen(self, dt):
        self.menu_space.step(dt)
        self.screen.fill('black')
        self.screen.blit(self.text_surfaces['game_over'], self.text_rects['game_over'])
        self.game_over_secrets(dt)
        
    def game_over_secrets(self, dt):
        if getattr(self, 'show_game_over_hint', False):
            self.screen.blit(self.text_surfaces['game_over_hint'], self.text_rects['game_over_hint']) 
            self.screen.blit(self.text_surfaces['game_over_score'], self.text_rects['game_over_score'])

        if getattr(self, 'show_dead_player', False):
            self.dead_angle_deg = sin(self.runtime) * 360
            self.dead_player_rotated = pygame.transform.rotozoom(self.player.image, self.dead_angle_deg, 1)
            self.dead_player_rect = self.dead_player_rotated.get_rect(center=self.player.rect.center)
            self.dead_player_mask = pygame.mask.from_surface(self.dead_player_rotated)
            self.screen.blit(self.dead_player_rotated, self.dead_player_rect)

        if getattr(self, 'show_fireball', False):
            angle_deg = getattr(self, 'dead_angle_deg', 0.0)
            angle_rad = radians(angle_deg)
            Fireball(self,
                     (self.all_sprites, self.secret_fireballs),
                     pygame.Vector2(cos(angle_rad), -sin(angle_rad)) * (-1 if not self.player.facing_right else 1),
                     origin=self.dead_player_rect.center)
            self.show_fireball = False
            
        if getattr(self, 'show_apple', False):
            GameOverApple(self,
                          (self.all_sprites, self.secret_fruits),
                          self.menu_space,
                          (random_of_spectrum(20,1260), -25))
            self.show_apple = False

        if getattr(self, 'show_chili', False):
            GameOverChili(self,
                          (self.all_sprites, self.secret_fruits),
                          self.menu_space,
                          (random_of_spectrum(30, 1250), -25))
            self.show_chili = False

        if hasattr(self, 'secret_fireballs') and self.secret_fireballs:
            self.secret_fireballs.update(dt)
            self.secret_fireballs.draw(self.screen)

        if hasattr(self, 'secret_fruits') and self.secret_fruits:
            self.secret_fruits.update(dt)
            self.secret_fruits.draw(self.screen)
            if hasattr(self, 'dead_player_rect') and getattr(self, 'show_dead_player', False):
                for fruit in self.secret_fruits.sprites():
                    offset = (fruit.rect.x - self.dead_player_rect.x, fruit.rect.y - self.dead_player_rect.y)
                    if self.dead_player_mask.overlap(pygame.mask.from_surface(fruit.image), offset):
                        self.menu_space.remove(fruit.body, fruit.shape)
                        fruit.kill()
                        self.eat_fruit_sound.play()

        if getattr(self, 'show_rectangle', False):
            Rectangle(self,
                      self.LAYERS['obstacles'],
                      (self.all_sprites, self.secret_obstacles),
                      self.rectangle_sprite_variants[3],
                      random_of_spectrum(300, 500))
            self.show_rectangle = False

        if getattr(self, 'secret_obstacles', False):
            self.secret_obstacles.update(dt)
            self.secret_obstacles.draw(self.screen)
            if hasattr(self, 'dead_player_rect') and getattr(self, 'show_dead_player', False):
                for obstacle in self.secret_obstacles.sprites():
                    offset = (obstacle.rect.x - self.dead_player_rect.x, obstacle.rect.y - self.dead_player_rect.y)
                    if self.dead_player_mask.overlap(pygame.mask.from_surface(obstacle.image), offset):
                        obstacle.kill()
                        self.damage_sound.play()
            if getattr(self, 'secret_fireballs', False):
                for obstacle in self.secret_obstacles.sprites():
                    if pygame.sprite.groupcollide(self.secret_obstacles, self.secret_fireballs, True, True, pygame.sprite.collide_mask):
                        self.eat_fruit_sound.play()

    def settings_menu(self, dt):
            self.screen.fill(COLOR['settings_bg'])
            mouse_pos = get_scaled_mouse_pos(self)
            mouse_click = pygame.mouse.get_just_pressed()[0]

            # --- if no tab active, show main menu ---
            if not self.active_settings_tab:
                self.screen.blit(self.text_surfaces['settings'], self.text_rects['settings'])
                for text_btn in self.main_settings_buttons:
                    text_btn.update(mouse_pos, mouse_click)
                    text_btn.draw(self.screen)

                # check clicks
                if self.main_settings_buttons[0].clicked:
                    self.active_settings_tab = "audio"
                    pygame.event.clear()
                    return
                elif self.main_settings_buttons[1].clicked:
                    self.active_settings_tab = "controls"
                    pygame.event.clear()
                    return
                elif self.main_settings_buttons[2].clicked:
                    save_settings(self)
                    self.requested_state = self.prev_state
                    pygame.event.clear()
                    return

            elif self.active_settings_tab:
                # back button at bottom
                back_btn = self.main_settings_buttons[2]

                # only draw back button if not waiting for key
                if not self.waiting_for_key:
                    back_btn.update(mouse_pos, mouse_click)
                    back_btn.draw(self.screen)

                # check back button click
                if back_btn.clicked:
                    self.active_settings_tab = None
                    pygame.event.clear()

            # --- controls submenu ---
            if self.active_settings_tab == "controls":
                self.screen.blit(self.text_surfaces['controls'], self.text_rects['controls'])

                for btn in self.control_texts:
                    btn.update(mouse_pos, mouse_click)
                    btn.draw(self.screen)

                    # handle clicks
                    if btn.clicked and self.waiting_for_key is None:
                        if btn.text == "Reset to Defaults":
                            # restore defaults
                            KEY_BINDINGS.clear()
                            KEY_BINDINGS.update({'move_left': pygame.K_a,
                                                 'move_right': pygame.K_d,
                                                 'move_up': pygame.K_w,
                                                 'move_down': pygame.K_s,
                                                 'ability': pygame.K_SPACE,
                                                 'dash': pygame.K_RETURN,
                                                 'shoot_up': pygame.K_UP,
                                                 'shoot_down': pygame.K_DOWN,
                                                 'shoot_right': pygame.K_RIGHT,
                                                 'shoot_left': pygame.K_LEFT,
                                                 'fullscreen': pygame.K_F11,})

                            # rebuild control texts
                            self.control_texts.clear()
                            self.control_texts.append(ClickableText("Reset to Defaults",
                                                      self.fonts["settings_texts"],
                                                      (WINDOW_CENTER[0], 110),
                                                      COLOR["clickable_text_buttons"],
                                                      COLOR["clickable_text_buttons_hovered"],
                                                      self.menu_select_sound,
                                                      self.menu_hover_sound))
                            y = 180
                            for action, key in KEY_BINDINGS.items():
                                label = f"{action.replace('_', ' ').title()}: {pygame.key.name(key).upper()}"
                                self.control_texts.append(ClickableText(label,
                                                          self.fonts["settings_texts"],
                                                          (WINDOW_CENTER[0], y),
                                                          COLOR["clickable_text_buttons"],
                                                          COLOR["clickable_text_buttons_hovered"],
                                                          self.menu_select_sound,
                                                          self.menu_hover_sound))
                                y += 40
                            pygame.event.clear()
                        else:
                            # clicked a keybinding line
                            for action, key in KEY_BINDINGS.items():
                                label = f"{action.replace('_', ' ').title()}: {pygame.key.name(key).upper()}"
                                if btn.text == label:
                                    self.waiting_for_key = action
                                    pygame.event.clear()

                if self.waiting_for_key:
                    # highlight selected button
                    for btn in self.control_texts:
                        if btn.text.startswith(self.waiting_for_key.replace('_', ' ').title()):
                            btn.color = COLOR['key_binding_prompt']; btn.hover_color = COLOR['key_binding_prompt']; btn.hovered = True
                    prompt = self.fonts['settings_texts'].render("Press new key...", True, COLOR['key_binding_prompt'])
                    rect = prompt.get_rect(center=(WINDOW_CENTER[0], WINDOW_HEIGHT - 60))
                    self.screen.blit(prompt, rect)

            # --- audio submenu ---
            elif self.active_settings_tab == "audio":
                    self.screen.blit(self.text_surfaces["audio"], self.text_rects["audio"])
                    mouse_pos = get_scaled_mouse_pos(self)
                    mouse_click = pygame.mouse.get_just_pressed()[0]

                    volumes = {"Master": settings.MASTER_VOLUME, "Music": settings.MUSIC_VOLUME, "SFX": settings.SFX_VOLUME}

                    for entry in self.audio_texts:
                        label = entry["label"]

                        # draw label
                        self.screen.blit(entry["text"], entry["rect"])

                        # draw percentage text
                        percent = int(volumes[label] * 100)
                        percent_surface = self.fonts['settings_texts'].render(f"{percent}%", True, COLOR['clickable_text_buttons'])
                        percent_rect = percent_surface.get_rect(center=(WINDOW_CENTER[0], entry["rect"].centery))
                        self.screen.blit(percent_surface, percent_rect)

                        # update and draw buttons
                        entry["minus"].update(mouse_pos, mouse_click)
                        entry["plus"].update(mouse_pos, mouse_click)
                        entry["minus"].draw(self.screen)
                        entry["plus"].draw(self.screen)

                        if entry["minus"].clicked:
                            volumes[label] = round(max(0.0, volumes[label] - 0.05), 2)
                            settings.MASTER_VOLUME, settings.MUSIC_VOLUME, settings.SFX_VOLUME = volumes["Master"], volumes["Music"], volumes["SFX"]
                            apply_audio_settings(self)
                            save_settings(self)
                        elif entry["plus"].clicked:
                            volumes[label] = round(min(1.0, volumes[label] + 0.05), 2)
                            settings.MASTER_VOLUME, settings.MUSIC_VOLUME, settings.SFX_VOLUME = volumes["Master"], volumes["Music"], volumes["SFX"]
                            apply_audio_settings(self)
                            save_settings(self)

                    # reassign updated globals
                    settings.MASTER_VOLUME, settings.MUSIC_VOLUME, settings.SFX_VOLUME = volumes["Master"], volumes["Music"], volumes["SFX"]

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
        self.SETTINGS_FILE = join(user_dir, "settings.json")

    def init_pygame(self):
        try:
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=256)
        except:
            print("Audio preinit failed. Using defaults.")
        pygame.init()
        pygame.mixer.set_num_channels(128)
        self.clock = pygame.time.Clock()

        # --- initialize controller ---
        pygame.joystick.init()
        self.controller = None
        if pygame.joystick.get_count() > 0:
            self.controller = pygame.joystick.Joystick(0)
            print(f"Using {self.controller.get_name()}")

    def init_menu_physics(self):
        self.menu_space = pymunk.Space()
        self.menu_space.gravity = (0, MENU_GRAVITY)
        
        # --- menu floor ---
        floor_y = WINDOW_HEIGHT + 10
        self.menu_floor = pymunk.Segment(
            self.menu_space.static_body,
            (0, floor_y),
            (WINDOW_WIDTH, floor_y),
            10)   # thickness of the collision edge
        
        # --- walls ---
        left_wall  = pymunk.Segment(self.menu_space.static_body, (0, 0), (0, WINDOW_HEIGHT), 1)
        right_wall = pymunk.Segment(self.menu_space.static_body, (WINDOW_WIDTH, 0), (WINDOW_WIDTH, WINDOW_HEIGHT), 1)

        self.menu_floor.elasticity = left_wall.elasticity = right_wall.elasticity = 0.3
        self.menu_floor.friction = left_wall.friction = right_wall.friction = 0.7
        self.menu_space.add(self.menu_floor, left_wall, right_wall)

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
                             'credits_track': pygame.mixer.Sound(join(self.AUDIO_DIR, 'credits_track.ogg')),
                             'game_track_1': pygame.mixer.Sound(join(self.AUDIO_DIR, 'game_track_1.ogg')),
                             'boss_track': pygame.mixer.Sound(join(self.AUDIO_DIR, 'boss_track.ogg')),}

        # --- sound effects ---
        self.menu_hover_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'menu_hover_sound.wav'))
        self.menu_select_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'menu_select_sound.wav'))
        self.title_flash_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'title_flash_sound.wav'))
        self.eat_fruit_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'eat_fruit_sound.wav'))
        self.damage_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'damage_sound.wav'))
        self.death_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'death_sound.wav'))
        self.game_over_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'game_over_sound.ogg'))
        self.record_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'new_record_sound.ogg'))
        self.ability_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'ability_sound.wav'))
        self.dash_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'dash_sound.wav'))
        self.phase_switch_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'phase_switch_sound.wav'))
        self.shoot_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'shoot_sound.wav'))
        self.boss_growl_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'boss_growl_sound.wav'))
        self.boss_hurt_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'boss_hurt_sound.wav'))
        self.energy_ball_shot_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'energy_ball_shot_sound.wav'))
        self.buff_end_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'buff_end_sound.wav'))
        self.boss_death_sound = pygame.mixer.Sound(join(self.AUDIO_DIR, 'boss_death_sound.wav'))

    def set_all_volumes(self):
        # --- game music ---
        self.tracks['start_track'].set_volume(START_TRACK_VOLUME * settings.MUSIC_VOLUME * settings.MASTER_VOLUME)
        self.tracks['game_over_track'].set_volume(GAME_OVER_TRACK_VOLUME * settings.MUSIC_VOLUME * settings.MASTER_VOLUME)
        self.tracks['credits_track'].set_volume(CREDITS_TRACK_VOLUME * settings.MUSIC_VOLUME * settings.MASTER_VOLUME)
        self.tracks['game_track_1'].set_volume(GAME_TRACK_1_VOLUME * settings.MUSIC_VOLUME * settings.MASTER_VOLUME) 
        self.tracks['boss_track'].set_volume(BOSS_TRACK_VOLUME * settings.MUSIC_VOLUME * settings.MASTER_VOLUME)

        # --- store base volumes ---
        self.base_volumes = {name: track.get_volume() for name, track in self.tracks.items()}

        # --- sound effects ---
        self.menu_hover_sound.set_volume(MENU_HOVER_SOUND_VOLUME * settings.SFX_VOLUME * settings.MASTER_VOLUME)
        self.menu_select_sound.set_volume(MENU_SELECT_SOUND_VOLUME * settings.SFX_VOLUME * settings.MASTER_VOLUME)
        self.title_flash_sound.set_volume(TITLE_FLASH_SOUND_VOLUME * settings.SFX_VOLUME * settings.MASTER_VOLUME)
        self.eat_fruit_sound.set_volume(EAT_FRUIT_SOUND_VOLUME * settings.SFX_VOLUME * settings.MASTER_VOLUME)
        self.damage_sound.set_volume(DAMAGE_SOUND_VOLUME * settings.SFX_VOLUME * settings.MASTER_VOLUME)
        self.death_sound.set_volume(DEATH_SOUND_VOLUME * settings.SFX_VOLUME * settings.MASTER_VOLUME)
        self.game_over_sound.set_volume(GAME_OVER_SOUND_VOLUME * settings.SFX_VOLUME * settings.MASTER_VOLUME)
        self.record_sound.set_volume(RECORD_SOUND_VOLUME * settings.SFX_VOLUME * settings.MASTER_VOLUME)
        self.ability_sound.set_volume(ABILITY_SOUND_VOLUME * settings.SFX_VOLUME * settings.MASTER_VOLUME)
        self.dash_sound.set_volume(DASH_SOUND_VOLUME * settings.SFX_VOLUME * settings.MASTER_VOLUME)
        self.phase_switch_sound.set_volume(PHASE_SWITCH_SOUND_VOLUME * settings.SFX_VOLUME * settings.MASTER_VOLUME)
        self.shoot_sound.set_volume(SHOOT_SOUND_VOLUME * settings.SFX_VOLUME * settings.MASTER_VOLUME)
        self.boss_growl_sound.set_volume(BOSS_GROWL_SOUND_VOLUME * settings.SFX_VOLUME * settings.MASTER_VOLUME)
        self.boss_hurt_sound.set_volume(BOSS_HURT_SOUND_VOLUME * settings.SFX_VOLUME * settings.MASTER_VOLUME)
        self.energy_ball_shot_sound.set_volume(ENERGY_BALL_SHOT_SOUND_VOLUME * settings.SFX_VOLUME * settings.MASTER_VOLUME)
        self.buff_end_sound.set_volume(BUFF_END_SOUND_VOLUME * settings.SFX_VOLUME * settings.MASTER_VOLUME)
        self.boss_death_sound.set_volume(BOSS_DEATH_SOUND_VOLUME * settings.SFX_VOLUME * settings.MASTER_VOLUME)

    def load_graphics(self):
        # --- fonts ---
        self.fonts: dict = {'title': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), TITLE_FONT_SIZE),
                            'stats': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), SCORE_FONT_SIZE),
                            'game_over': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), GAME_OVER_FONT_SIZE),
                            'game_over_score': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), GAME_OVER_SCORE_FONT_SIZE),
                            'game_over_hint': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), GAME_OVER_HINT_FONT_SIZE),
                            'start_hint': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), START_HINT_FONT_SITZE),
                            'credits_hint': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), CREDITS_HINT_FONT_SITZE),
                            'settings_headers': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), SETTINGS_HEADERS_FONT_SIZE),
                            'settings_texts': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), SETTINGS_TEXTS_FONT_SIZE),
                            'quit_prompt_heading': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), QUIT_PROMPT_HEADING_FONT_SIZE),
                            'quit_prompt_options': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), QUIT_PROMPT_OPTIONS_FONT_SIZE),
                            'credits_button': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), CREDITS_BUTTON_FONT_SIZE),
                            'effect_texts': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), FRUIT_PICKUP_MESSAGES_FONT_SIZE),
                            'credits_header': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), CREDITS_HEADER_FONT_SIZE),
                            'credits_name': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), CREDITS_NAME_FONT_SIZE),
                            'quit_icon_text': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), ICON_TEXTS_FONT_SIZE),
                            'play_icon_text': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), ICON_TEXTS_FONT_SIZE),
                            'settings_icon_text': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), ICON_TEXTS_FONT_SIZE),
                            'boss_name': pygame.font.Font(join(self.FONT_DIR, 'slkscr.ttf'), BOSS_NAME_FONT_SIZE)}

        # --- pre-render non-clickable static texts ---
        self.text_surfaces: dict = {'title': self.fonts['title'].render("Shadow Drift", True, COLOR['title_text']),
                                    'game_over': self.fonts['game_over'].render("Game Over!", True, COLOR['game_over_text']),
                                    'game_over_hint': self.fonts['game_over_hint'].render("Play again: " + ("START" if self.controller else "ENTER") + "\nClose game: " + ("HOME" if self.controller else "ESC"), True, COLOR['game_over_text']),
                                    'start_hint': self.fonts['start_hint'].render("Start game: " + ("START" if self.controller else "RETURN") + "\nClose game: " + ("HOME" if self.controller else "ESC"), True, COLOR['start_hint']),
                                    'credits_hint': self.fonts['credits_hint'].render("Press ESC or RETURN", True, COLOR['credits_hint']),
                                    'settings': self.fonts['settings_headers'].render("Settings", True, COLOR['settings_headers']),
                                    'controls': self.fonts['settings_headers'].render("Controls", True, COLOR['settings_headers']),
                                    'audio': self.fonts['settings_headers'].render("Audio", True, COLOR['settings_headers']),
                                    'quit_prompt_heading': self.fonts['quit_prompt_heading'].render("Close the game without saving?", True, COLOR['quit_prompt_heading']),
                                    'quit_icon_text': self.fonts['quit_icon_text'].render("Quit", True, COLOR['quit_icon_text']),
                                    'play_icon_text': self.fonts['quit_icon_text'].render("Continue", True, COLOR['play_icon_text']),
                                    'settings_icon_text': self.fonts['quit_icon_text'].render("Settings", True, COLOR['settings_icon_text']),
                                    'boss_name': self.fonts['boss_name'].render("Shadow Guardian", True, COLOR['boss_name']),
                                    'boss_name_shadow': self.fonts['boss_name'].render("Shadow Guardian", True, COLOR['boss_name_shadow'])}
        
        # credits title
        self.credits_title_surf = self.text_surfaces['title'].copy()


        # --- define non-clickable texts positions ---
        self.text_rects: dict = {'title': self.text_surfaces['title'].get_rect(center=WINDOW_CENTER),
                                 'game_over': self.text_surfaces['game_over'].get_rect(center=WINDOW_CENTER),
                                 'game_over_hint': self.text_surfaces['game_over_hint'].get_rect(bottomleft=(15, WINDOW_HEIGHT- 15)),
                                 'start_hint': self.text_surfaces['start_hint'].get_rect(bottomleft=(15, WINDOW_HEIGHT- 15)),
                                 'credits_hint': self.text_surfaces['credits_hint'].get_rect(bottomleft=(15, WINDOW_HEIGHT- 15)),
                                 'settings': self.text_surfaces['settings'].get_rect(center=(WINDOW_CENTER[0], 50)),
                                 'controls': self.text_surfaces['controls'].get_rect(center=(WINDOW_CENTER[0], 50)),
                                 'audio': self.text_surfaces['audio'].get_rect(center=(WINDOW_CENTER[0], 50)),
                                 'quit_prompt_heading': self.text_surfaces['quit_prompt_heading'].get_rect(center=(QUIT_RECT_WIDTH/2, QUIT_RECT_HEIGHT/8)),
                                 'quit_icon_text': self.text_surfaces['quit_icon_text'].get_rect(center=(WINDOW_WIDTH - 70, 130)),
                                 'play_icon_text': self.text_surfaces['play_icon_text'].get_rect(center=(WINDOW_WIDTH - 170, 130)),
                                 'settings_icon_text': self.text_surfaces['settings_icon_text'].get_rect(center=(WINDOW_WIDTH - 270, 130)),
                                 'boss_name': self.text_surfaces['boss_name'].get_rect(center=(WINDOW_CENTER[0], WINDOW_HEIGHT - 52 - BOSS_HEALTH_BAR_HEIGHT)),
                                 'boss_name_shadow': self.text_surfaces['boss_name_shadow'].get_rect(center=(WINDOW_CENTER[0], WINDOW_HEIGHT- 50 - BOSS_HEALTH_BAR_HEIGHT))}
        
        # credits title
        self.credits_title_rect = self.text_rects['title'].copy()
        
        # --- define fruit-collect messages ---
        self.FRUIT_PICKUP_TEXTS: dict = {Apple: (f"+{APPLE_POINTS} points", 'apple_effect_text'),
                                         Banana: ("+speed", 'banana_effect_text'),
                                         Blueberry: ("health restored", 'blueberry_effect_text'),
                                         Chili: ("fire power", 'chili_effect_text'),
                                         Grapes: ("extra life", 'grapes_effect_text'),
                                         Pear: ("clear obstacles", 'pear_effect_text')}
        
        # --- define credits texts ---
        self.credits_texts: list = ("Director",
                              "Producer",
                              "Designer",
                              "Pixel Artist",
                              "Concept Artist",
                              "Music Supervisor",
                              "Music Composer",
                              "SFX Artist",
                              "Programmer",
                              "2D Animator",
                              "Project Manager",
                              "Production Coordinator",
                              "Creative Director",
                              "Writer",
                              "Editor",
                              "Playtester")
        
        # --- images ---
        self.clickable_icons: list = [ClickableIcon(pygame.image.load(join(self.IMG_DIR, "quit_button.png")).convert_alpha(),(WINDOW_WIDTH - 70, 70)),
                                      ClickableIcon(pygame.image.load(join(self.IMG_DIR, "resume_button.png")).convert_alpha(),(WINDOW_WIDTH - 170, 70)),
                                      ClickableIcon(pygame.image.load(join(self.IMG_DIR, "cog_wheel.png")).convert_alpha(),(WINDOW_WIDTH - 270, 70))]

        self.main_settings_buttons: list = [ClickableText("Audio", self.fonts['settings_texts'], (WINDOW_CENTER[0], 300), COLOR ['clickable_text_buttons'], COLOR['clickable_text_buttons_hovered'], self.menu_select_sound, self.menu_hover_sound),
                                      ClickableText("Controls", self.fonts['settings_texts'], (WINDOW_CENTER[0], 380), COLOR['clickable_text_buttons'], COLOR['clickable_text_buttons_hovered'], self.menu_select_sound, self.menu_hover_sound),
                                      ClickableText("Back", self.fonts['settings_texts'], (WINDOW_CENTER[0], WINDOW_HEIGHT - 60), COLOR['clickable_text_buttons'], COLOR['clickable_text_buttons_hovered'], self.menu_select_sound, self.menu_hover_sound),]
        
        # --- quit prompt ---
        # surface
        self.quit_prompt_surface = pygame.Surface((QUIT_RECT_WIDTH + 2*QUIT_RECT_OUTLINE_THICKNESS, QUIT_RECT_HEIGHT + 2*QUIT_RECT_OUTLINE_THICKNESS), pygame.SRCALPHA)
        # rect outline
        pygame.draw.rect(self.quit_prompt_surface, COLOR['quit_prompt_rect_outline'], pygame.Rect(0,0,QUIT_RECT_WIDTH + 2*QUIT_RECT_OUTLINE_THICKNESS,QUIT_RECT_HEIGHT + 2*QUIT_RECT_OUTLINE_THICKNESS), border_radius=QUIT_RECT_ROUNDING + QUIT_RECT_OUTLINE_THICKNESS)
        # rect
        pygame.draw.rect(self.quit_prompt_surface, COLOR['quit_prompt_rect'], pygame.Rect(QUIT_RECT_OUTLINE_THICKNESS,QUIT_RECT_OUTLINE_THICKNESS,QUIT_RECT_WIDTH,QUIT_RECT_HEIGHT),border_radius=QUIT_RECT_ROUNDING)
        self.quit_prompt_rect = self.quit_prompt_surface.get_rect(center=WINDOW_CENTER)
        # clickable texts (yes/no)
        cx, cy = self.quit_prompt_rect.center
        y = cy + 15
        self.yes_btn = ClickableText("Yes", 
                                     self.fonts['quit_prompt_options'],
                                     (cx - 120, y),
                                     COLOR['clickable_text_buttons'], COLOR['clickable_text_buttons_hovered'],
                                     self.menu_select_sound, self.menu_hover_sound)
        self.no_btn = ClickableText("No", self.fonts["quit_prompt_options"],
                                    (cx + 120, y),
                                    COLOR['clickable_text_buttons'], COLOR['clickable_text_buttons_hovered'],
                                    self.menu_select_sound, self.menu_hover_sound)
        
        # --- credits clickable text ---
        self.credits_btn = ClickableText("Credits", 
                                         self.fonts['credits_button'],
                                         (80, WINDOW_HEIGHT - 30),
                                         COLOR['clickable_text_buttons'], COLOR['clickable_text_buttons_hovered'],
                                         self.menu_select_sound, self.menu_hover_sound)
        
        # --- keybinding clickable texts ---
        if not hasattr(self, "control_texts"):
            self.control_texts = [ClickableText('Reset to Defaults', self.fonts['settings_texts'], (WINDOW_CENTER[0], 110), COLOR['clickable_text_buttons'], COLOR['clickable_text_buttons_hovered'], self.menu_select_sound, self.menu_hover_sound)]
            y = 180
            for action, key in KEY_BINDINGS.items():
                label = f"{action.replace('_', ' ').title()}: {pygame.key.name(key).upper()}"
                btn = ClickableText(
                    label,
                    self.fonts['settings_texts'],
                    (WINDOW_CENTER[0], y),
                    COLOR['clickable_text_buttons'],
                    COLOR['clickable_text_buttons_hovered'],
                    self.menu_select_sound,
                    self.menu_hover_sound)
                self.control_texts.append(btn)
                y += 40

        # --- audio clickable texts ---
        self.audio_texts = []
        labels = [("Master", 300), ("Music", 360), ("SFX", 420)]
        for label, y in labels:
            text_surface = self.fonts["settings_texts"].render(label, True, COLOR['clickable_text_buttons'])
            text_rect = text_surface.get_rect(midleft=(WINDOW_CENTER[0] - 250, y))

            minus_btn = ClickableText("-", self.fonts["settings_texts"],
                                    (WINDOW_CENTER[0] + 90, y),
                                    COLOR['clickable_text_buttons'], COLOR['clickable_text_buttons_hovered'],
                                    self.menu_select_sound, self.menu_hover_sound)
            plus_btn = ClickableText("+", self.fonts["settings_texts"],
                                    (WINDOW_CENTER[0] + 140, y),
                                    COLOR['clickable_text_buttons'], COLOR['clickable_text_buttons_hovered'],
                                    self.menu_select_sound, self.menu_hover_sound)

            self.audio_texts.append({"label": label, "text": text_surface, "rect": text_rect,
                                        "minus": minus_btn, "plus": plus_btn})

        # --- animated backgrounds ---
        self.backgrounds: dict = {
            'rectangle': [pygame.image.load(join(self.IMG_DIR, 'bg_rectangle_phase', f'bg_rectangle_phase_{i}.png')).convert_alpha() for i in range(11)],
            'arrow': [pygame.image.load(join(self.IMG_DIR, 'bg_arrow_phase', 'bg_arrow_phase.png')).convert_alpha()],
            'icicle': [pygame.image.load(join(self.IMG_DIR, 'bg_icicle_phase', 'bg_icicle_phase.png')).convert_alpha()],
            'saw_blade': [pygame.image.load(join(self.IMG_DIR, 'bg_saw_blade_phase', 'bg_saw_blade_phase.png')).convert_alpha()],
            'rocket': [pygame.image.load(join(self.IMG_DIR, 'bg_rocket_phase', 'bg_rocket_phase.png')).convert_alpha()],
            'asteroid': [pygame.image.load(join(self.IMG_DIR, 'bg_asteroid_phase', 'bg_asteroid_phase.png')).convert_alpha()],
            'spike_ball': [pygame.image.load(join(self.IMG_DIR, 'bg_spike_ball_phase', 'bg_spike_ball_phase.png')).convert_alpha()],
            'boss': [pygame.image.load(join(self.IMG_DIR, 'bg_boss_phase', 'bg_boss_phase.png')).convert_alpha()]}
        
        # --- heart images ---
        self.empty_heart = pygame.image.load(join(self.IMG_DIR, 'empty_heart.png')).convert_alpha()
        self.red_heart = pygame.image.load(join(self.IMG_DIR, 'red_heart.png')).convert_alpha()
        self.blue_heart = pygame.image.load(join(self.IMG_DIR, 'blue_heart.png')).convert_alpha()
        self.purple_heart = pygame.image.load(join(self.IMG_DIR, 'purple_heart.png')).convert_alpha()

        # --- player images ---
        self.player_sprite_variants: dict = {1: pygame.image.load(join(self.IMG_DIR, 'player_1.png')).convert_alpha(),
                                             2: pygame.image.load(join(self.IMG_DIR, 'player_2.png')).convert_alpha(),}
        
        self.player_death_animation_frames: list = [pygame.image.load(join(self.IMG_DIR, 'player_death_animation', f'explosion{i}.png')).convert_alpha() for i in range(17)]

        # --- fireball ---
        self.fireball_image = pygame.image.load(join(self.IMG_DIR, 'fireball.png')).convert_alpha()

        # --- other entities ---
        self.rectangle_sprite_variants: list = [pygame.image.load(join(self.IMG_DIR, f"obstacle_{width}.png")).convert_alpha() for width in (250, 300, 350, 400)]

        self.arrow_image = pygame.image.load(join(self.IMG_DIR, 'arrow.png')).convert_alpha()

        self.icicle_image = pygame.image.load(join(self.IMG_DIR, 'icicle.png')).convert_alpha()

        self.saw_blade_image = pygame.image.load(join(self.IMG_DIR, 'saw_blade.png')).convert_alpha()

        self.rocket_image = pygame.image.load(join(self.IMG_DIR, 'rocket.png')).convert_alpha()

        self.asteroid_image = pygame.image.load(join(self.IMG_DIR, 'asteroid.png')).convert_alpha()

        self.spike_ball_image = pygame.image.load(join(self.IMG_DIR, 'spike_ball.png')).convert_alpha()

        self.fruit_sprite_variants = {Apple: pygame.image.load(join(self.IMG_DIR, 'apple.png')).convert_alpha(),
                                      Blueberry: pygame.image.load(join(self.IMG_DIR, 'blueberry.png')).convert_alpha(),
                                      Banana: pygame.image.load(join(self.IMG_DIR, 'banana.png')).convert_alpha(),
                                      Chili: pygame.image.load(join(self.IMG_DIR, 'chili.png')).convert_alpha(),
                                      Grapes: pygame.image.load(join(self.IMG_DIR, 'grapes.png')).convert_alpha(),
                                      Pear: pygame.image.load(join(self.IMG_DIR, 'pear.png')).convert_alpha()}
        self.fruit_sprite_variants[StartBlueberry] = self.fruit_sprite_variants[Blueberry]
        self.fruit_sprite_variants[GameOverApple] = self.fruit_sprite_variants[Apple]
        self.fruit_sprite_variants[GameOverChili] = self.fruit_sprite_variants[Chili]
        
        self.boss_image = pygame.image.load(join(self.IMG_DIR, 'boss.png')).convert_alpha()

        self.boss_death_animation_frames: list = [pygame.image.load(join(self.IMG_DIR, 'boss_death_animation', f'boss_death_frame{i}.png')).convert_alpha() for i in range(23)]

        self.dark_energy_ball_image = pygame.image.load(join(self.IMG_DIR, 'dark_energy_ball.png')).convert_alpha()

    def init_game_state(self):
        # --- Game starting conditions ---
        STATS['score'] = 0
        self.state = None
        self.requested_state = 'start'
        self.active_settings_tab = None
        self.waiting_for_key = None
        self.score_event = pygame.event.custom_type()
        pygame.time.set_timer(self.score_event, SCORE_UPDATE_TIME)

        # --- starting phase ---
        self.current_phase = 'rectangle'
        self.prev_phase = self.current_phase

        # --- spawn timers ---
        self.next_rectangle_spawn_time = RECTANGLE_SPAWN_TIME
        self.next_arrow_spawn_time = ARROW_COLUMN_SPAWN_TIME
        self.next_icicle_spawn_time = ICICLE_SPAWN_TIME
        self.next_saw_blade_spawn_time = SAW_BLADE_SPAWN_TIME
        self.next_rocket_spawn_time = ROCKET_SPAWN_TIME
        self.next_asteroid_spawn_time = ASTEROID_SPAWN_TIME
        self.next_spike_ball_spawn_time = SPIKE_BALL_SPAWN_TIME

        # --- time tracking ---
        if not hasattr(self,'absolute_start_time'):
            self.absolute_start_time = perf_counter()
        self.play_time = 0.0
        self.phase_start = 0.0
        self.play_start = None
        self.pause_start = 0.0
        self.total_paused = 0.0
        self.is_paused = False

        # start player
        self.start_ability_time = 0.0
        self.start_ability_duration = PLAYER_ABILITY_DURATION
        self.start_ability = False

        for attr in (# reset start secrets
                     'show_start_hint', 'show_icicle', 'show_blueberry', 'show_start_player','start_player_pos','start_player_vel','start_player_facing_right',
                     # reset game over secrets
                     'show_game_over_hint', 'show_rectangle', 'show_chili', 'show_apple','secret_fruits','dead_player_rect','dead_player_mask',
                     # other flags
                     'quit_prompt', 'stats_text', 'stats_text_shadow','prev_stats', 'record_checked', 'phase_ended', 'had_boss', 'boss', 'boss_phase_end_start', 'last_chili_drop'):
            if hasattr(self, attr):
                delattr(self, attr)

    def init_sprites(self):
        # --- sprite groups and layers ---
        self.all_sprites = pygame.sprite.LayeredUpdates()
        # actual entities
        self.player_group = pygame.sprite.GroupSingle()
        self.fireball_sprites = pygame.sprite.Group()
        self.fruit_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.rectangle_sprites = pygame.sprite.Group()
        self.arrow_sprites = pygame.sprite.Group()
        self.icicle_sprites = pygame.sprite.Group()
        self.saw_blade_sprites = pygame.sprite.Group()
        self.rocket_sprites = pygame.sprite.Group()
        self.asteroid_sprites = pygame.sprite.Group()
        self.spike_ball_sprites = pygame.sprite.Group()
        self.boss_sprites = pygame.sprite.Group()
        self.energy_ball_sprites = pygame.sprite.Group()
        self.boss_obstacle_sprites = pygame.sprite.Group()
        # animations and UI
        self.player_effect_sprites = pygame.sprite.Group()
        self.boss_effect_sprites = pygame.sprite.Group()
        self.UI_text_sprites = pygame.sprite.Group()
        self.background_sprites = pygame.sprite.Group()
        self.secret_fireballs = pygame.sprite.Group()
        self.secret_fruits = pygame.sprite.Group()
        self.secret_obstacles = pygame.sprite.Group()

        self.LAYERS = {'backgrounds': 1,
                       'bosses': 2, 'boss_death_animation': 2.1,
                       'player_banana_trail': 3, 'player': 3.1, 'player_fire_outline': 3.2, 'player_glow': 3.3, 'player_death_animation': 3.4,
                       'fruits': 4,
                       'fireballs': 5,
                       'obstacles': 6,
                       'boss_projectiles': 7,
                       'ui_texts': 8}

        # --- instantiate background ---
        self.background = AnimatedBackground(self,
                                             (self.all_sprites, self.background_sprites),
                                             self.backgrounds[self.current_phase],
                                             BACKGROUND_SCROLLABILITIES[self.current_phase])

        # --- instantiate player sprite ---
        Player(self, (self.all_sprites, self.player_group))
        self.player = self.player_group.sprite

    def load_save(self):
        try:
            with open(self.SAVE_FILE) as f:
                save_data = json.load(f)
                STATS['record'] = save_data.get('record',0)
                self.previous_runtime = save_data.get('total_runtime[s]', 0.0)
        except:
            self.previous_runtime = 0.0

    def load_settings(self):
        try:
            with open(self.SETTINGS_FILE) as f:
                settings_data = json.load(f)

                # controls
                loaded_bindings: dict = settings_data.get('key_bindings', {}) 
                for action, key_name in loaded_bindings.items():
                    try:
                        KEY_BINDINGS[action] = pygame.key.key_code(key_name)
                    except:
                        pass

                # audio volumes
                audio = settings_data.get("audio", {})
                settings.MASTER_VOLUME = audio.get("master", 1.0)
                settings.MUSIC_VOLUME = audio.get("music", 1.0)
                settings.SFX_VOLUME = audio.get("sfx", 1.0)
        except:
            pass

    def create_custome_events(self):
        # --- credits text spawn rate ---
        self.credits_event = pygame.event.custom_type()
        pygame.time.set_timer(self.credits_event, 5000)

        # --- increase score with time ---
        self.score_event = pygame.event.custom_type()
        pygame.time.set_timer(self.score_event, SCORE_UPDATE_TIME)

    @property
    def runtime(self):
        """Total runtime since the program started (seconds)."""
        return perf_counter() - self.absolute_start_time

# --- Play loop ---

    def set_phase(self, dt):
        if getattr(self, 'phase_ended', False) and self.player.is_alive:
            self.phase_ended = False
            self.phase_switch_sound.play()
            fade_to_black(self)
            clear_input()
            kill_sprites(self.background_sprites)
            kill_sprites(self.enemy_sprites)
            kill_sprites(self.obstacle_sprites)
            kill_sprites(self.boss_sprites)
            kill_sprites(self.fruit_sprites)
            kill_sprites(self.fireball_sprites)
            if STATS['score'] >= BOSS_PHASE_START_POINTS and not getattr(self, 'had_boss', False):
                self.current_phase = 'boss'
                change_track(self, 'boss_track', fade_ms=2000, loop=True)
            else:
                self.prev_phase = self.current_phase
                while self.current_phase == self.prev_phase:
                    self.current_phase = random_of_selection(PHASE_PROBABILITIES.keys(), PHASE_PROBABILITIES.values())
            self.background = AnimatedBackground(self,
                                                 (self.all_sprites, self.background_sprites),
                                                 self.backgrounds[self.current_phase],
                                                 BACKGROUND_SCROLLABILITIES[self.current_phase])
            self.change_score_color = True
            self.phase_start = self.play_time
            if self.current_phase in ('arrow', 'saw_blade'):
                self.player.rect.center = (WINDOW_CENTER[0] + 400,WINDOW_CENTER[1])
                self.player.facing_right = False
            elif self.current_phase == 'rocket':
                self.player.rect.center = (WINDOW_CENTER[0],WINDOW_CENTER[1] - 200)
            elif self.current_phase in ('boss', 'icicle'):
                self.player.rect.center = (WINDOW_CENTER[0],WINDOW_CENTER[1] + 200)
            else:
                self.player.rect.center = WINDOW_CENTER
            
        match(self.current_phase):
            case 'rectangle':
                self.rectangle_phase()       
                self.spawn_fruit(dt)
            case 'arrow':
                self.arrow_phase()
                self.spawn_fruit(dt, spawn_tendency=0.6)
            case 'icicle':
                self.icicle_phase()
                self.spawn_fruit(dt, spawn_tendency=0.5)
            case 'saw_blade':
                self.saw_blade_phase()
                self.spawn_fruit(dt, spawn_tendency=0.65)
            case 'rocket':
                self.rocket_phase()
                self.spawn_fruit(dt, speed_tendency=0.25, rotation=True)
            case 'asteroid':
                self.asteroid_phase()
                self.spawn_fruit(dt, speed_tendency=0.25, rotation=True)
            case 'spike_ball':
                self.spike_ball_phase()
                self.spawn_fruit(dt)
            case 'boss':
                self.boss_phase()
                self.spawn_fruit(dt, speed_tendency=0.3, fruits=(Blueberry, Banana, Grapes))

    def rectangle_phase(self):
        # --- choose speed and spawn rate of rectangle ---
        if self.play_time - self.phase_start < FIRST_OBSTACLE_PHASE_END:
            speed = 250
            weight = (1, 0.8, 0.6, 0.4)
            spawn_rate_factor = 1
        elif FIRST_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < SECOND_OBSTACLE_PHASE_END:
            speed = 350
            weight = (0.8, 0.7, 0.7, 0.6)
            spawn_rate_factor = SECOND_RECTANGEL_PHASE_SPAWN_FACTOR
            self.background.speed = 84
        elif SECOND_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < THIRD_OBSTACLE_PHASE_END:
            speed = 450
            weight = (0.6, 0.6, 0.8, 0.8)
            spawn_rate_factor = THIRD_RECTANGEL_PHASE_SPAWN_FACTOR
            self.background.speed = 108
        elif THIRD_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < FOURTH_OBSTACLE_PHASE_END:
            speed = 550
            weight = (0.4, 0.5, 0.9, 1)
            spawn_rate_factor = FOURTH_RECTANGLE_PHASE_SPAWN_FACTOR
            self.background.speed = 132
        elif self.play_time - self.phase_start >= FOURTH_OBSTACLE_PHASE_END:
            self.phase_ended = True
            STATS['score'] += RECTANGLE_PHASE_END_POINTS
            return

        # --- spawn rectangle ---
        if self.play_time >= self.next_rectangle_spawn_time:
            Rectangle(self,
                      self.LAYERS['obstacles'],
                      (self.all_sprites, self.enemy_sprites, self.obstacle_sprites, self.rectangle_sprites),
                      random_of_selection(self.rectangle_sprite_variants, weights=weight),
                      speed)
            self.next_rectangle_spawn_time = self.play_time + RECTANGLE_SPAWN_TIME / spawn_rate_factor

    def arrow_phase(self):
        if self.play_time - getattr(self, 'arrow_sub_phase_start', -ARROW_SUB_PHASE_DURATION) >= ARROW_SUB_PHASE_DURATION:
            self.prev_arrow_sub_phase = getattr(self, 'arrow_sub_phase', None)
            while self.prev_arrow_sub_phase == getattr(self, 'arrow_sub_phase', None):
                self.arrow_sub_phase = random_of_selection(('columns', 'singles'))
            self.arrow_sub_phase_start = self.play_time

        if self.play_time - self.phase_start < FIRST_OBSTACLE_PHASE_END:
            speed = 280
            spawn_rate_factor = 1
        elif FIRST_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < SECOND_OBSTACLE_PHASE_END:
            speed = 300
            spawn_rate_factor = SECOND_ARROW_PHASE_SPAWN_FACTOR
            self.background.speed = 95
        elif SECOND_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < THIRD_OBSTACLE_PHASE_END:
            speed = 320
            spawn_rate_factor = THIRD_ARROW_PHASE_SPAWN_FACTOR
            self.background.speed = 115
        elif THIRD_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < FOURTH_OBSTACLE_PHASE_END:
            speed = 370
            spawn_rate_factor = FOURTH_ARROW_PHASE_SPAWN_FACTOR
            self.background.speed = 125
        elif self.play_time - self.phase_start >= FOURTH_OBSTACLE_PHASE_END:
            self.phase_ended = True
            STATS['score'] += ARROW_PHASE_END_POINTS
            return

        if self.play_time >= self.next_arrow_spawn_time:
            match(self.arrow_sub_phase):
                    case 'columns':
                        height = random_of_selection(ARROW_COLUMN_SPAWN_HEIGHTS)
                        for i in range(0, 480, 40):
                            Arrow(self,
                                  self.LAYERS['obstacles'],
                                  (self.all_sprites, self.enemy_sprites, self.obstacle_sprites, self.arrow_sprites),
                                  self.arrow_image,
                                  speed,
                                  i + height)
                        self.next_arrow_spawn_time = self.play_time + ARROW_COLUMN_SPAWN_TIME / spawn_rate_factor

                    case 'singles':
                        Arrow(self,
                              self.LAYERS['obstacles'],
                              (self.all_sprites, self.enemy_sprites, self.obstacle_sprites, self.arrow_sprites),
                              self.arrow_image,
                              speed,
                              random_of_spectrum(0,WINDOW_HEIGHT))
                        self.next_arrow_spawn_time = self.play_time + ARROW_SINGLES_SPAWN_TIME / spawn_rate_factor

    def icicle_phase(self):
        # --- choose speed and spawn rate of icicle ---
        if self.play_time - self.phase_start < FIRST_OBSTACLE_PHASE_END:
            speed = 200
            spawn_rate_factor = 1
        elif FIRST_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < SECOND_OBSTACLE_PHASE_END:
            speed = 250
            spawn_rate_factor = SECOND_ICICLE_PHASE_SPAWN_FACTOR
        elif SECOND_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < THIRD_OBSTACLE_PHASE_END:
            speed = 300
            spawn_rate_factor = THIRD_ICICLE_PHASE_SPAWN_FACTOR
        elif THIRD_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < FOURTH_OBSTACLE_PHASE_END:
            speed = 350
            spawn_rate_factor = FOURTH_ICICLE_PHASE_SPAWN_FACTOR
        elif self.play_time - self.phase_start >= FOURTH_OBSTACLE_PHASE_END:
            self.phase_ended = True
            STATS['score'] += ICICLE_PHASE_END_POINTS
            return

        # --- spawn icicle ---
        if self.play_time >= self.next_icicle_spawn_time:
            Icicle(self,
                   self.LAYERS['obstacles'],
                   (self.all_sprites, self.enemy_sprites, self.obstacle_sprites, self.icicle_sprites),
                   self.icicle_image,
                   speed)
            self.next_icicle_spawn_time = self.play_time + ICICLE_SPAWN_TIME / spawn_rate_factor

    def saw_blade_phase(self):
        # --- choose speed and spawn rate of saw blade ---
        if self.play_time - self.phase_start < FIRST_OBSTACLE_PHASE_END:
            speed = 360
            rotation_speed = -180
            spawn_rate_factor = 1
        elif FIRST_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < SECOND_OBSTACLE_PHASE_END:
            speed = 460
            rotation_speed = -220
            spawn_rate_factor = SECOND_SAW_BLADE_PHASE_SPAWN_FACTOR
        elif SECOND_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < THIRD_OBSTACLE_PHASE_END:
            speed = 560
            rotation_speed = -270
            spawn_rate_factor = THIRD_SAW_BLADE_PHASE_SPAWN_FACTOR
        elif THIRD_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < FOURTH_OBSTACLE_PHASE_END:
            speed = 660
            rotation_speed = -320
            spawn_rate_factor = FOURTH_SAW_BLADE_PHASE_SPAWN_FACTOR
        elif self.play_time - self.phase_start >= FOURTH_OBSTACLE_PHASE_END:
            self.phase_ended = True
            STATS['score'] += SAW_BLADE_PHASE_END_POINTS
            return

        # --- spawn saw blade ---
        if self.play_time >= self.next_saw_blade_spawn_time and self.play_time - self.phase_start > 2:
            SawBlade(self,
                     self.LAYERS['obstacles'],
                     (self.all_sprites, self.enemy_sprites, self.obstacle_sprites, self.saw_blade_sprites),
                     self.saw_blade_image,
                     speed,
                     rotation_speed=rotation_speed)
            self.next_saw_blade_spawn_time = self.play_time + SAW_BLADE_SPAWN_TIME / spawn_rate_factor

    def rocket_phase(self):
        # --- choose speed and spawn rate of rocket ---
        if self.play_time - self.phase_start < FIRST_OBSTACLE_PHASE_END:
            speed = 600
            spawn_rate_factor = 1
        elif FIRST_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < SECOND_OBSTACLE_PHASE_END:
            speed = 700
            spawn_rate_factor = SECOND_ROCKET_PHASE_SPAWN_FACTOR
        elif SECOND_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < THIRD_OBSTACLE_PHASE_END:
            speed = 800
            spawn_rate_factor = THIRD_ROCKET_PHASE_SPAWN_FACTOR
        elif THIRD_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < FOURTH_OBSTACLE_PHASE_END:
            speed = 900
            spawn_rate_factor = FOURTH_ROCKET_PHASE_SPAWN_FACTOR
        elif self.play_time - self.phase_start >= FOURTH_OBSTACLE_PHASE_END:
            self.phase_ended = True
            STATS['score'] += ROCKET_PHASE_END_POINTS
            return

        # --- spawn rocket ---
        if self.play_time >= self.next_rocket_spawn_time and self.play_time - self.phase_start > 2.0:
            Rocket(self,
                   self.LAYERS['obstacles'],
                   (self.all_sprites, self.enemy_sprites, self.obstacle_sprites, self.rocket_sprites),
                   self.rocket_image,
                   speed)
            self.next_rocket_spawn_time = self.play_time + ROCKET_SPAWN_TIME / spawn_rate_factor

    def asteroid_phase(self):
        # --- choose speed and spawn rate of asteroid ---
        if self.play_time - self.phase_start < FIRST_OBSTACLE_PHASE_END:
            speed = 200
        elif FIRST_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < SECOND_OBSTACLE_PHASE_END:
            speed = 230
        elif SECOND_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < THIRD_OBSTACLE_PHASE_END:
            speed = 260
        elif THIRD_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < FOURTH_OBSTACLE_PHASE_END:
            speed = 290
        elif self.play_time - self.phase_start >= FOURTH_OBSTACLE_PHASE_END:
            self.phase_ended = True
            STATS['score'] += ASTEROID_PHASE_END_POINTS
            return

        # --- spawn rocket ---
        if self.play_time >= self.next_asteroid_spawn_time and self.play_time - self.phase_start > 1.0:
            Asteroid(self,
                     self.LAYERS['obstacles'],
                    (self.all_sprites, self.enemy_sprites, self.obstacle_sprites, self.asteroid_sprites),
                    self.asteroid_image,
                    speed)
            self.next_asteroid_spawn_time = self.play_time + ASTEROID_SPAWN_TIME

    def spike_ball_phase(self):
        # --- choose speed and spawn rate of spike ball ---
        if self.play_time - self.phase_start < FIRST_OBSTACLE_PHASE_END:
            speed = 250
        elif FIRST_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < SECOND_OBSTACLE_PHASE_END:
            speed = 300
        elif SECOND_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < THIRD_OBSTACLE_PHASE_END:
            speed = 350
        elif THIRD_OBSTACLE_PHASE_END <= self.play_time - self.phase_start < FOURTH_OBSTACLE_PHASE_END:
            speed = 400
        elif self.play_time - self.phase_start >= FOURTH_OBSTACLE_PHASE_END:
            self.phase_ended = True
            STATS['score'] += SPIKE_BALL_PHASE_END_POINTS
            return

        # --- spawn spike ball ---
        if self.play_time >= self.next_spike_ball_spawn_time and self.play_time - self.phase_start > 2:
            SpikeBall(self,
                      self.LAYERS['obstacles'],
                     (self.all_sprites, self.enemy_sprites, self.obstacle_sprites, self.spike_ball_sprites),
                     self.spike_ball_image,
                     speed,
                     0,
                     230,
                     random_of_selection(('right', 'left')))
            self.next_spike_ball_spawn_time = self.play_time + SPIKE_BALL_SPAWN_TIME

    def boss_phase(self):
        if getattr(self, 'init_boss_phase_end', False):
            if self.play_time - self.boss_phase_end_start > BOSS_PHASE_END_DURATION:
                self.init_boss_phase_end = False
                self.phase_ended = True
                change_track(self, 'game_track_1', fade_ms=3000, loop=True)
            return
        if self.play_time - getattr(self, 'last_chili_drop', -10) > 10:
            Chili(self, (self.all_sprites, self.fruit_sprites), random_of_spectrum(100,200))
            self.last_chili_drop = self.play_time
        if not getattr(self, 'boss', False):
            self.boss = ShadowGuardian(self, (self.all_sprites, self.enemy_sprites, self.boss_sprites))
            
        if getattr(self, 'boss_defeated', False):
            self.boss_defeated = False
            self.had_boss = True
            self.music_channel.stop()
            STATS['score'] += BOSS_KILL_POINTS
            self.init_boss_phase_end = True
            self.boss_phase_end_start = self.play_time
            kill_sprites(self.boss_obstacle_sprites)
            kill_sprites(self.obstacle_sprites)
            return

    def spawn_fruit(self, dt, spawns_per_min=FRUIT_SPAWNS_PER_MINUTE, spawn_tendency=None, speed_tendency=None, rotation=False, fruits=(Apple,Blueberry,Banana,Chili,Grapes,Pear)):
        if random.random() < spawns_per_min/60 * dt:
            new_fruit = random_of_selection(fruits, (FRUITS_SPAWN_PROBABILITIES[str(fruit.__name__).lower()] for fruit in fruits))
            new_fruit(self,
                    (self.all_sprites, self.fruit_sprites),
                    speed=random_of_spectrum(80,260,bias=speed_tendency),
                    spawn_bias=spawn_tendency,
                    rotate=rotation)

    def collisions(self):
        # --- fireball collisions ---
        shot_obstacles = pygame.sprite.groupcollide(self.obstacle_sprites, self.fireball_sprites, False, True, pygame.sprite.collide_mask)
        if shot_obstacles:
            for obstacle in shot_obstacles:
                obstacle.handle_getting_shot()

        shot_bosses = pygame.sprite.groupcollide(self.boss_sprites, self.fireball_sprites, False, True, pygame.sprite.collide_mask)
        if shot_bosses:
            for boss in shot_bosses:
                boss.take_damage()

        if not self.player.is_alive:
            return
        # --- enemy collisions ---
        if not self.player.iframes and self.player.can_collide and not self.player.dashing:
            hit_enemy = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask)
            if hit_enemy:
                for enemy in hit_enemy: 
                    if enemy in self.energy_ball_sprites:
                        self.boss.energy_ball = None
                    if enemy in self.obstacle_sprites:
                        enemy.kill()
                if self.player.extra_life:
                    self.player.extra_life -= 1
                else:
                    self.player.health -= 1
                if self.player.health >= 1:
                    self.damage_sound.play()
                    self.player.activate_iframes()
                else:
                    self.player.is_alive = False
                    self.death_sound.play()
                    PlayerDeathAnimation(self, (self.all_sprites, self.player_effect_sprites))
                    self.player.kill()

                    for sprite in list(self.all_sprites):
                        if getattr(sprite, "is_trail", False) or getattr(sprite, "is_effect_text", False):
                            sprite.kill()

        # --- fruit collisions ---
        eaten_fruits = pygame.sprite.spritecollide(self.player, self.fruit_sprites, True, pygame.sprite.collide_mask)
        if eaten_fruits:
            for fruit in eaten_fruits:
                last_stats = [STATS['score'], self.player.health, self.player.banana_boost_start, self.player.fire_power_start, self.player.extra_life]
                fruit.apply_effect()
                new_stats = [STATS['score'], self.player.health, self.player.banana_boost_start, self.player.fire_power_start, self.player.extra_life]
                if new_stats != last_stats:
                    fruit.display_pickup_message(self.fonts['effect_texts'], self.FRUIT_PICKUP_TEXTS)
                self.eat_fruit_sound.play()

    def check_record(self):
        if STATS['score'] > STATS['record'] and not getattr(self, 'record_checked', False):
            self.record_checked = True
            self.record_sound.play()

    def draw_boss_health_bar(self):
        if self.current_phase != 'boss':
            return

        # --- animate display health ---
        if self.boss.current_health > self.boss.target_health:
            self.boss.current_health = max(self.boss.target_health,
                self.boss.current_health - BOSS_HEALTH_CHANGE_SPEED)
                
        # shorthand
        current = self.boss.current_health
        target  = self.boss.target_health
        ratio   = self.boss.health_ratio

        current_width = current / ratio
        target_width  = target / ratio

        bar_x = WINDOW_CENTER[0] - BOSS_HEALTH_BAR_LENGTH / 2
        bar_y = WINDOW_HEIGHT - 50

        # --- create surface for the whole bar ---
        bar_surface = pygame.Surface((BOSS_HEALTH_BAR_LENGTH, BOSS_HEALTH_BAR_HEIGHT),
            pygame.SRCALPHA)

        # --- base bar: REAL health ---
        health_bar_rect = pygame.Rect(
            0,
            0,
            target_width,
            BOSS_HEALTH_BAR_HEIGHT)
            
        pygame.draw.rect(
            bar_surface,
            COLOR['boss_health_bar'],
            health_bar_rect,
            border_radius=2)

        # --- damage/transition bar ---
        if current_width > target_width:
            transition_width = current_width - target_width
            transition_rect = pygame.Rect(
                target_width,
                0,
                transition_width,
                BOSS_HEALTH_BAR_HEIGHT)
            
            pygame.draw.rect(
                bar_surface,
                COLOR['boss_health_bar_damage'],
                transition_rect,
                border_radius=2)

        # --- bar border ---
        border_rect = pygame.Rect(
            0,
            0,
            BOSS_HEALTH_BAR_LENGTH,
            BOSS_HEALTH_BAR_HEIGHT)
        
        pygame.draw.rect(
            bar_surface,
            COLOR['boss_health_bar_border'],
            border_rect,
            width=4,
            border_radius=2)

        # --- adjust transparency ---
        bar_world_rect = pygame.Rect(
            bar_x,
            bar_y,
            BOSS_HEALTH_BAR_LENGTH,
            BOSS_HEALTH_BAR_HEIGHT)
        
        # boss name
        boss_name_shadow_surf = self.text_surfaces['boss_name_shadow'].copy()
        boss_name_surf = self.text_surfaces['boss_name'].copy()

        if self.player.rect.colliderect(bar_world_rect):
            bar_surface.set_alpha(100) 
        else: bar_surface.set_alpha(255)
        if self.player.rect.colliderect(self.text_rects['boss_name']):
            boss_name_shadow_surf.set_alpha(100)
            boss_name_surf.set_alpha(100)
        else: boss_name_shadow_surf.set_alpha(255); boss_name_surf.set_alpha(255)

        # --- draw bar surface and name ---
        self.screen.blit(bar_surface, (bar_x, bar_y))
        self.screen.blit(boss_name_shadow_surf, self.text_rects['boss_name_shadow'])
        self.screen.blit(boss_name_surf, self.text_rects['boss_name'])

    def draw_hearts(self):
        alpha = 100 if self.player.rect.top < 55 and self.player.rect.left < 200 and self.state == 'play' else 255
        self.empty_heart.set_alpha(alpha)
        self.red_heart.set_alpha(alpha)
        self.blue_heart.set_alpha(alpha)
        self.purple_heart.set_alpha(alpha)

        self.screen.blit(self.red_heart if self.player.health > 0 else self.empty_heart, (25, 16))
        self.screen.blit(self.blue_heart if self.player.health > 1 else self.empty_heart, (75, 16))
        self.screen.blit(self.purple_heart if self.player.extra_life else self.empty_heart, (125, 16))

    def draw_score_text(self, text_color, text_shadow_color):
        '''Render text surfaces only when stats change.'''

        #render
        self.current_stats = (STATS['score'], STATS['record'])
        if self.current_stats != getattr(self, 'prev_stats', None) or getattr(self, 'change_score_color', False):
            self.change_score_color = False
            text = f"Score: {STATS['score']}  Record: {STATS['record']}"
            self.stats_text = self.fonts['stats'].render(text, True, text_color)
            self.stats_text_shadow = self.fonts['stats'].render(text, True, text_shadow_color)
            self.prev_stats = self.current_stats

        # change opacity if player is behind score text
        if self.player.rect.top < self.stats_text.get_height() + 20 and self.player.rect.left < self.stats_text.get_width() + 190 and self.player.rect.right > 190 and self.state == 'play':
            self.stats_text.set_alpha(100)
            self.stats_text_shadow.set_alpha(0)
        else:
            self.stats_text.set_alpha(255)
            self.stats_text_shadow.set_alpha(255)

        # draw
        self.screen.blit(self.stats_text_shadow, (190, 22))
        self.screen.blit(self.stats_text, (190, 20))

# --- Execute Lifecycle ---
def main():
    game = Game()
    atexit.register(lambda: save_runtime(game))
    atexit.register(pygame.display.quit)
    atexit.register(pygame.font.quit)
    atexit.register(pygame.mixer.quit)
    atexit.register(pygame.quit)
    game.run()

if __name__ == '__main__':
    main()