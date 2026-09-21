from settings import *
import settings

T = TypeVar('T')

# --- essential game utilities ---
def clear_input() -> None:
    """Use this to prevent input from carrying over to the next screen."""

    pygame.event.clear()
    pygame.key.get_pressed()
    pygame.mouse.get_pressed()

def kill_sprites(group, exceptions: tuple = (), space: Optional[pymunk.Space] = None) -> None:
    for sprite in group:
        if sprite not in exceptions:
            if space is not None:
                if hasattr(sprite, 'body') and hasattr(sprite, 'shape'):
                    space.remove(sprite.body, sprite.shape)
            sprite.kill()

def close_game() -> None:
    pygame.quit()
    sys.exit()

def save_settings(game: Game) -> None:
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

def save_game(game: Game) -> None:
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

def get_scaled_mouse_pos(game: Game) -> tuple[int, int]:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    scale_x = BASE_RESOLUTION[0] / game.window.get_width()
    scale_y = BASE_RESOLUTION[1] / game.window.get_height()
    return int(mouse_x * scale_x), int(mouse_y * scale_y)

def change_track(game: Game, key: str, fade_out: int = 1, fade_in: int = 1, loop: bool = True) -> None:
    """Switch to another track while preserving base volume."""

    if hasattr(game, 'music_channel') and game.music_channel and game.music_channel.get_busy():
        game.music_channel.fadeout(fade_out)

    track = game.tracks[key]
    game.music_channel = track.play(loops=-1 if loop else 0, fade_ms=fade_in)
    if game.music_channel: game.music_channel.set_volume(game.base_volumes[key])
    game.current_track = key

def fade_to_black(game: Game, duration: float = FADE_TO_BLACK_DURATION, smoothness: int = FADE_TO_BLACK_SMOOTHNESS) -> None:
    """Fade the screen to black over a fixed duration (seconds), with given smoothness."""
    
    bar_width = WINDOW_WIDTH / smoothness
    start_time = perf_counter()

    while True:
        game.clock.tick(FPS)      # keeps dt stable after fade

        elapsed = perf_counter() - start_time
        progress = min(elapsed / duration, 1.0)

        # --- draw progressive black bars ---
        filled = int(progress * smoothness)
        pygame.draw.rect(game.screen, 'black', (0, 0, int(bar_width * filled), WINDOW_HEIGHT))
        present_frame(game)

        if progress >= 1.0:
            break

def present_frame(game: Game) -> None:
    window_w, window_h = game.window.get_size()
    scaled = pygame.transform.smoothscale(game.screen, (window_w, window_h))
    game.window.blit(scaled, (0, 0))
    pygame.display.flip()

def toggle_fullscreen(game: Game) -> None:
    game.fullscreen = not game.fullscreen
    if game.fullscreen:
        game.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        game.window = pygame.display.set_mode(BASE_RESOLUTION)

def set_phase_parameters(game: Game, speeds: tuple[int,int,int,int], rotation_speeds: tuple[int, int, int, int] = (0,0,0,0), spawn_rate_factors: tuple[float, float, float] = (1,1,1), background_speeds: tuple[int, int, int, int] = (0,0,0,0)) -> tuple[int, int, float, list[float]]:
    if game.play_time - game.phase_start < FIRST_OBSTACLE_PHASE_END:
        speed = speeds[0]
        rotation_speed = rotation_speeds[0]
        spawn_rate_factor = 1
        game.background.speed = background_speeds[0]
        weight = RECTANGLE_SUB_PHASE_SPAWN_WEIGHTS[0]
    elif FIRST_OBSTACLE_PHASE_END <= game.play_time - game.phase_start < SECOND_OBSTACLE_PHASE_END:
        speed = speeds[1]
        rotation_speed = rotation_speeds[1]
        spawn_rate_factor = spawn_rate_factors[0]
        game.background.speed = background_speeds[1]
        weight = RECTANGLE_SUB_PHASE_SPAWN_WEIGHTS[1]
    elif SECOND_OBSTACLE_PHASE_END <= game.play_time - game.phase_start < THIRD_OBSTACLE_PHASE_END:
        speed = speeds[2]
        rotation_speed = rotation_speeds[2]
        spawn_rate_factor = spawn_rate_factors[1]
        game.background.speed = background_speeds[2]
        weight = RECTANGLE_SUB_PHASE_SPAWN_WEIGHTS[2]
    elif THIRD_OBSTACLE_PHASE_END <= game.play_time - game.phase_start < FOURTH_OBSTACLE_PHASE_END:
        speed = speeds[3]
        rotation_speed = rotation_speeds[3]
        spawn_rate_factor = spawn_rate_factors[2]
        game.background.speed = background_speeds[3]
        weight = RECTANGLE_SUB_PHASE_SPAWN_WEIGHTS[3]
    return speed, rotation_speed, spawn_rate_factor, weight

# --- randomizers ---
def random_of_spectrum(start: int, end: int, as_float: bool = False, bias: Optional[float] = None) -> int|float:
    """Return random number from [start, end].
    - as_float: True → return float, False → return integer
    - bias: if given (0.0–1.0), biases result toward one end
      e.g. bias=0.2 favors start, bias=0.8 favors end"""
    
    if bias is not None:
        value = triangular(start, end, start + (end - start) * bias)
        return value if as_float else int(value)
    return uniform(start, end) if as_float else randint(start, end)

def random_of_selection(selection: Sequence[T], weights: Optional[Sequence[float]] = None, unique: bool = False) -> T:
    """Return random element from a collection.
    - weights: optional list of probabilities (must match len(selection))
    - unique: if True, convert to set before choice (removes duplicates)"""

    seq = list(set(selection)) if unique else list(selection)
    if weights:
        return choices(seq, weights=weights, k=1)[0]
    return choice(seq)

# --- one time uses ---
def save_runtime(game: Game) -> None:
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

def title_flash(game: Game) -> None:
    
    game.title_flash_sound.play()
    start = perf_counter()
    while perf_counter() - start < 0.4:
        flicker = int(255 * abs(sin((perf_counter() - start) * 25)))
        surf = game.text_surfaces['title'].copy()
        surf.set_alpha(flicker)
        rect = surf.get_rect(center=game.text_rects['title'].center)
        game.screen.fill(COLOR['start_screen_bg'])
        game.screen.blit(surf, rect)
        present_frame(game)
        game.clock.tick(FPS)

# --- time system ---
def update_play_time(game: Game) -> None:
    if not game.is_paused and game.play_start is not None:
        game.play_time = perf_counter() - game.play_start - game.total_paused

def pause_play_time(game: Game) -> None:
    if not game.is_paused:
        game.pause_start = perf_counter()
        game.is_paused = True

def resume_play_time(game: Game) -> None:
    if game.is_paused:
        game.total_paused += perf_counter() - game.pause_start
        game.is_paused = False

# --- UI elements ---
class ClickableIcon:
    """Clickable image button used in the pause menu."""

    def __init__(self, image: pygame.Surface, pos: tuple[int, int], anchor: str = "center", hover_scale_factor: float = 1.1) -> None:
        self.base_image = image
        self.rect: pygame.Rect = image.get_rect()
        setattr(self.rect, anchor, pos)
        self.scale_factor = hover_scale_factor

        self.controller_hovered = False
        self.controller_clicked = False
        self.hovered = False
        self.hover_changed = False
        self.clicked = False

    def update(self, mouse_pos: tuple[float, float], mouse_click: bool) -> None:
        prev_hover = self.hovered
        self.hovered = any((self.rect.collidepoint(mouse_pos), self.controller_hovered))
        self.controller_hovered = False if self.rect.collidepoint(mouse_pos) else self.controller_hovered
        self.hover_changed = (self.hovered != prev_hover)
        self.clicked = mouse_click and not self.controller_hovered and self.hovered

    def draw(self, screen: pygame.Surface) -> None:
        scale = self.scale_factor if self.hovered else 1.0
        surf = pygame.transform.rotozoom(self.base_image, 0, scale)
        rect = surf.get_rect(center=self.rect.center)
        screen.blit(surf, rect)

class ClickableText:
    """Clickable text button that changes color when hovered."""

    def __init__(self, text: str, font: pygame.Font, pos: tuple[float, float], color: str, hover_color: str, click_sound: Optional[pygame.Sound] = None, hover_sound: Optional[pygame.Sound] = None, anchor: str = "center") -> None:
        self.font = font
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.pos = pos
        self.anchor = anchor
        self.click_sound = click_sound
        self.hover_sound = hover_sound

        self.surface: pygame.Surface = self.font.render(self.text, True, self.color)
        self.rect: pygame.Rect = self.surface.get_rect()
        setattr(self.rect, self.anchor, self.pos)

        self.controller_hovered = False
        self.controller_clicked = False
        self.hovered = False
        self.hover_changed = False
        self.clicked = False

    def update(self, mouse_pos: tuple[float, float], mouse_click: bool) -> None:
        prev_hover = self.hovered
        self.hovered = any((self.rect.collidepoint(mouse_pos), self.controller_hovered))
        self.controller_hovered = False if self.rect.collidepoint(mouse_pos) else self.controller_hovered
        self.hover_changed = (self.hovered != prev_hover)

        if self.hover_changed and self.hovered and self.hover_sound:
            self.hover_sound.play()

        color = self.hover_color if self.hovered else self.color
        self.surface = self.font.render(self.text, True, color)

        self.clicked = mouse_click and not self.controller_hovered and self.hovered
        if self.clicked and self.click_sound:
            self.click_sound.play()

    def draw(self, screen: pygame.Surface):
        screen.blit(self.surface, self.rect)

class CreditsText:
    """Texts that appear on the credits screen and move upwards."""

    def __init__(self, text: str, font: pygame.Font, pos: tuple[float, float], color: str) -> None:
        self.text = text
        self.font = font
        self.pos = pos
        self.color = color

        self.surface = self.font.render(self.text, True, self.color)
        self.rect: pygame.Rect = self.surface.get_rect()
        setattr(self.rect, 'center', self.pos)

    def update(self, dt: float) -> None:
        self.rect.bottom -= 60 * dt
        self.surface = self.font.render(self.text, True, self.color)

    def draw(self, screen: pygame.Surface) -> None:
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

def print_game_time(game: Game) -> None:
    '''DEBUGGING TOOL: Use this at top of the event handler function to measure times.'''

    print(f"[time] played = {game.play_time:.3f}s   stopped = {game.total_paused:.3f}s   absolute runtime = {game.runtime}")

def print_track_volume(game: Game) -> None:
    """DEBUGGING TOOL: Show current track, its base volume, and the current channel volume."""
    if game.music_channel:
        print("Track:", game.current_track,"| Default Volume:", game.tracks[game.current_track].get_volume(), "| Total Volume:", game.tracks[game.current_track].get_volume()*game.music_channel.get_volume())

def print_sprite_counts(game: Game) -> None:
    """DEBUGGING TOOL: Show count of sprites for every sprite group."""
    print(f"Total Sprites: {len(game.all_sprites)} | Coin Sprites: {len(game.coin_sprites)} | Fruit Sprites: {len(game.fruit_sprites)} | Obstacle Sprites: {len(game.obstacle_sprites)} | Fireball Sprites: {len(game.player_fireball_sprites)} | UI Texts: {len(game.UI_text_sprites)} | Background: {len(game.background_sprites)} | Player Sprite: {len(game.player_group)}")

def show_rects(sprites: list[pygame.sprite.Sprite], surf: pygame.Surface) -> None:
    """DEBUGGING TOOL: Show rectangles of sprites."""

    for sprite in sprites:
        if sprite.rect:
            pygame.draw.rect(surf, (255,0,0), sprite.rect, 1)
