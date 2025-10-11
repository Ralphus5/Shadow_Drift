from utils import *

# ----- VISUALS -----
# --- display ---
WINDOW_WIDTH: int = 1280 
WINDOW_HEIGHT: int = 720
WINDOW_CENTER = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
BASE_RESOLUTION = (WINDOW_WIDTH, WINDOW_HEIGHT)
FPS: Annotated[int, [25-120]] = 60

# --- font sizes ---
TITLE_FONT_SIZE: int = 140
SCORE_FONT_SIZE: int = 35
GAME_OVER_FONT_SIZE: int = 150

# --- animations ---
TITLE_FLICKER_SPEED: Annotated[float, 1-6] = 5
MAX_FLICKER_INT: Annotated[int, 188-255] = 255
MIN_FLICKER_INT: Annotated[int, 60-160] = 100
FADE_TO_BLACK_SMOOTHNESS: int = 600
FADE_TO_BLACK_DURATION: float = 0.6
GAME_OVER_SCROLL_SPEED: float = 1.6
BACKGROUND_FRAME_INTERVALL: int = 100
PLAYER_EXPLOSION_SPEED: float = 1.0

# --- colors ---
COLOR = {'ui_text': "#000000",
        'ui_text_shadow': "#FFFFFF",
        'ui_text_stop': "#0015FF",
        'ui_text_shadow_stop': "#000000",
        'blue_player_glow': "#0066FF81",
        'red_player_glow': "#FF000081",
        'game_over_text': "#C90E0E",
        'start_screen_bg': "#11121F",
        'stop_screen_bg': "#11121F",
        'title_text': "#2D0BEE"}

# ----- AUDIO -----
# --- game music ---
STOP_SCREEN_DIM_FACTOR: Annotated[float, [0-1]] = 0.2
START_TRACK_VOLUME: Annotated[float, [0-1]] = 0.3
GAME_OVER_TRACK_VOLUME: Annotated[float, [0-1]] = 0.25
GAME_TRACK_1_VOLUME: Annotated[float, [0-1]] = 0.6
GAME_TRACK_2_VOLUME: Annotated[float, [0-1]] = 0.6

# --- sound effects ---
# menu sound volumes
MENU_HOVER_SOUND_VOLUME: Annotated[float, [0-1]] = 0.8
MENU_SELECT_SOUND_VOLUME: Annotated[float, [0-1]] = 1
TITLE_FLASH_SOUND_VOLUME: Annotated[float, [0-1]] = 0.8

# gameplay sound volumes
DAMAGE_SOUND_VOLUME: Annotated[float, [0-1]] = 0.4
EXPLOSION_SOUND_VOLUME: Annotated[float, [0-1]] = 0.4
GAME_OVER_SOUND_VOLUME: Annotated[float, [0-1]] = 1
RECORD_SOUND_VOLUME: Annotated[float, [0-1]] = 0.8
ABILITY_SOUND_VOLUME: Annotated[float, [0-1]] = 1

# ----- GAMEPLAY -----
STATS = {'score': 0, 'record': 0}
DEFAULT_PLAYER_SPEED: int = 250
OBSTACLE_SPAWN_TIME: float = 0.5 # seconds
FRUIT_SPAWN_PER_MINUTE: float = 4
PLAYER_ABILITY_COOLDOWN: float = 10.0 # seconds
PLAYER_ABILITY_DURATION: float = 1.0 # seconds
