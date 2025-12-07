from settings import *
import settings

# --- essential game utilities ---
def clear_input():
    """Use this to prevent input from carrying over to the next screen."""

    pygame.event.clear()
    pygame.key.get_pressed()
    pygame.mouse.get_pressed()

def kill_sprites(group, exceptions: tuple = (), space=None):
    for sprite in group:
        if sprite not in exceptions:
            if hasattr(sprite, 'body') and hasattr(sprite, 'shape'):
                space.remove(sprite.body, sprite.shape)
            sprite.kill()

def close_game():
    pygame.quit()
    sys.exit()

def save_settings(game):
    global MASTER_VOLUME, MUSIC_VOLUME, SFX_VOLUME

    save_data = {}
    try:
        with open(game.SETTINGS_FILE) as f:
            save_data = json.load(f)
    except:
        pass

    # controls
    save_data['key_bindings'] = {action: pygame.key.name(key) for action, key in KEY_BINDINGS.items()}
    # audio
    save_data['audio'] = {'master': settings.MASTER_VOLUME,
                            'music': settings.MUSIC_VOLUME,
                            'sfx': settings.SFX_VOLUME,}

    with open(game.SETTINGS_FILE, "w") as f:
        json.dump(save_data, f, indent=2)

def save_game(game):
    # update record if needed
    if STATS['score'] > STATS['record']:
        STATS['record'] = STATS['score']

    save_data = {}

    try:
        with open(game.SAVE_FILE) as f:
            save_data = json.load(f)
    except:
        pass

    # what to save
    save_data['record'] = STATS['record']

    # dump into file
    with open(game.SAVE_FILE, "w") as f:
        json.dump(save_data, f, indent=2)

def get_scaled_mouse_pos(game):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    scale_x = BASE_RESOLUTION[0] / game.window.get_width()
    scale_y = BASE_RESOLUTION[1] / game.window.get_height()
    return int(mouse_x * scale_x), int(mouse_y * scale_y)

def change_track(game, key, fade_ms=1, loop=True):
    """Switch to another track while preserving base volume."""

    if hasattr(game, 'music_channel') and game.music_channel and game.music_channel.get_busy():
        game.music_channel.stop()

    track = game.tracks[key]
    game.music_channel = track.play(loops=-1 if loop else 0, fade_ms=fade_ms)
    game.music_channel.set_volume(game.base_volumes[key])
    game.current_track = key

def fade_to_black(game, duration=FADE_TO_BLACK_DURATION, smoothness=FADE_TO_BLACK_SMOOTHNESS):
    """Fade the screen to black over a fixed duration (seconds), with given smoothness."""
    
    bar_width = WINDOW_WIDTH / smoothness
    start_time = perf_counter()

    while True:
        now = perf_counter()
        elapsed = now - start_time
        progress = min(elapsed / duration, 1.0)

        # --- draw progressive black bars ---
        filled = int(progress * smoothness)
        pygame.draw.rect(game.screen, 'black', (0, 0, int(bar_width * filled), WINDOW_HEIGHT))
        present_frame(game)

        if progress >= 1.0:
            break

def present_frame(game):
    window_w, window_h = game.window.get_size()
    scaled = pygame.transform.smoothscale(game.screen, (window_w, window_h))
    game.window.blit(scaled, (0, 0))
    pygame.display.flip()

def toggle_fullscreen(game):
    game.fullscreen = not getattr(game, 'fullscreen', True)
    if game.fullscreen:
        game.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        game.window = pygame.display.set_mode(BASE_RESOLUTION)

# --- randomizers ---
def random_of_spectrum(start: int|float, end: int|float, as_float=False, bias: float=None) -> int|float:
    """Return random number from [start, end].
    - as_float: True → return float, False → return integer
    - bias: if given (0.0–1.0), biases result toward one end
      e.g. bias=0.2 favors start, bias=0.8 favors end"""
    
    if bias is not None:
        value = triangular(start, end, start + (end - start) * bias)
        return value if as_float else int(value)
    return uniform(start, end) if as_float else randint(start, end)

def random_of_selection(selection: Sequence, weights: Optional[Sequence[float]] =None, unique: bool=False) -> Sequence[Any]:
    """Return random element from a collection.
    - weights: optional list of probabilities (must match len(selection))
    - unique: if True, convert to set before choice (removes duplicates)"""

    seq = list(set(selection)) if unique else list(selection)
    if weights:
        return choices(seq, weights=weights, k=1)[0]
    return choice(seq)

# --- one time uses ---
def save_runtime(game):
    """Save total runtime of the game. This method gets called every time the program closes."""
    save_data = {}

    try:
        with open(game.SAVE_FILE) as f:
            save_data = json.load(f)
    except: 
        pass

    total_runtime = save_data.get('total_runtime[s]', 0.0) + game.runtime
    save_data['total_runtime[s]'] = round(total_runtime)

    with open(game.SAVE_FILE, 'w') as f:
        json.dump(save_data, f, indent=2)

def apply_audio_settings(game):
    game.set_all_volumes()
    if game.music_channel and game.current_track:
        base = game.base_volumes[game.current_track]
        dimmed = base * STOP_SCREEN_DIM_FACTOR
        game.music_channel.set_volume(dimmed)
        game.paused_volume = dimmed
        game.music_dimmed = True

def title_flash(game):
    """Play title flash and transition to play mode."""
    
    game.title_flash_sound.play()
    start = perf_counter()
    while perf_counter() - start < 0.4:
        flicker = 255 * abs(sin((perf_counter() - start) * 25))
        surf = game.text_surfaces['title'].copy()
        surf.set_alpha(flicker)
        rect = surf.get_rect(center=game.text_rects['title'].center)
        game.screen.fill(COLOR['start_screen_bg'])
        game.screen.blit(surf, rect)
        present_frame(game)
        game.clock.tick(FPS)

# --- time system ---
def update_play_time(game):
    if not game.is_paused and game.play_start is not None:
        game.play_time = perf_counter() - game.play_start - game.total_paused

def pause_play_time(game):
    if not game.is_paused:
        game.pause_start = perf_counter()
        game.is_paused = True

def resume_play_time(game):
    if game.is_paused:
        game.total_paused += perf_counter() - game.pause_start
        game.is_paused = False

# --- UI elements ---
class ClickableIcon:
    """Clickable image button used in the pause menu."""

    def __init__(self, image, pos: tuple, anchor: str = "center", hover_scale_factor: float = 1.1):
        self.base_image = image
        self.rect = image.get_rect()
        setattr(self.rect, anchor, pos)
        self.scale_factor = hover_scale_factor

        self.hovered = False
        self.hover_changed = False
        self.clicked = False

    def update(self, mouse_pos: tuple[float, float], mouse_click: bool):
        prev_hover = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.hover_changed = (self.hovered != prev_hover)
        self.clicked = mouse_click and self.hovered

    def draw(self, screen):
        scale = self.scale_factor if self.hovered else 1.0
        surf = pygame.transform.rotozoom(self.base_image, 0, scale)
        rect = surf.get_rect(center=self.rect.center)
        screen.blit(surf, rect)

class ClickableText:
    """Clickable text button that changes color when hovered."""

    def __init__(self, text, font, pos, color, hover_color, click_sound=None, hover_sound=None, anchor="center"):
        self.font = font
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.pos = pos
        self.anchor = anchor
        self.click_sound = click_sound
        self.hover_sound = hover_sound

        self.surface = self.font.render(self.text, True, self.color)
        self.rect = self.surface.get_rect()
        setattr(self.rect, self.anchor, self.pos)

        self.hovered = False
        self.hover_changed = False
        self.clicked = False

    def update(self, mouse_pos, mouse_click):
        prev_hover = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.hover_changed = (self.hovered != prev_hover)

        if self.hover_changed and self.hovered and self.hover_sound:
            self.hover_sound.play()

        color = self.hover_color if self.hovered else self.color
        self.surface = self.font.render(self.text, True, color)

        self.clicked = mouse_click and self.hovered
        if self.clicked and self.click_sound:
            self.click_sound.play()

    def draw(self, screen):
        screen.blit(self.surface, self.rect)

class CreditsText:
    """Texts that appear on the credits screen and move upwards."""

    def __init__(self, text, font, pos, color):
        self.text = text
        self.font = font
        self.pos = pos
        self.color = color

        self.surface = self.font.render(self.text, True, self.color)
        self.rect = self.surface.get_rect()
        setattr(self.rect, 'center', self.pos)

    def update(self, dt):
        self.rect.bottom -= 60 * dt
        self.surface = self.font.render(self.text, True, self.color)

    def draw(self, screen):
        screen.blit(self.surface, self.rect)

# --- debugging and performance check ---
def get_func_time(func: Callable) -> Callable:
    '''DEBUGGING TOOL: Check how long a function took to execute.'''

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time: float = perf_counter()
        result: Any = func(*args, **kwargs)
        end_time: float = perf_counter()

        print(f'"{func.__name__}()" took {end_time - start_time:.3f} seconds to execute')
        return result

    return wrapper

def print_game_time(game):
    '''DEBUGGING TOOL: Use this at top of the event handler function to measure times.'''

    print(f"[time] played = {game.play_time:.3f}s   stopped = {game.total_paused:.3f}s   absolute runtime = {game.runtime}")

def print_track_volume(game):
    """DEBUGGING TOOL: Show current track, its base volume, and the current channel volume."""

    print("Track:", game.current_track,"| Default Volume:", game.tracks[game.current_track].get_volume(),"| Dim Factor:", game.music_channel.get_volume(), "| Total Volume:", game.tracks[game.current_track].get_volume()*game.music_channel.get_volume())

def print_sprite_counts(game):
    """DEBUGGING TOOL: Show count of sprites for every sprite group."""

    print(f"Total Sprites: {len(game.all_sprites)} | Fruit Sprites: {len(game.fruit_sprites)} | Obstacle Sprites: {len(game.obstacle_sprites)} | Fireball Sprites: {len(game.fireball_sprites)} | UI Texts: {len(game.UI_text_sprites)} | Player Abilities: {len(game.player_effect_sprites)} | Background: {len(game.background_sprites)} | Player Sprite: {len(game.player_group)}")

def show_rects(sprites, surf):
    """DEBUGGING TOOL: Show rectangles of sprites."""

    for sprite in sprites:
        pygame.draw.rect(surf, (255,0,0), sprite.rect, 1)
