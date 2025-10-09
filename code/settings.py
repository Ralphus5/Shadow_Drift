from utils import *

# ----- VISUALS -----
# --- display ---
WINDOW_WIDTH: int = 1280 
WINDOW_HEIGHT: int = 720
WINDOW_CENTER = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
BASE_RESOLUTION = (WINDOW_WIDTH, WINDOW_HEIGHT)
FPS: int = 60

# --- font sizes ---
START_SCREEN_FONT_SIZE: int = 140
SCORE_FONT_SIZE: int = 35
GAME_OVER_FONT_SIZE: int = 150

# --- animations ---
FADE_TO_BLACK_DURATION: float = 1.6
FADE_TO_BLACK_SMOOTHNESS: int = 500
BACKGROUND_FRAME_INTERVALL: int = 100
PLAYER_EXPLOSION_SPEED: float = 1.0

# --- colors ---
COLOR = {'ui_text': "#000000",
        'ui_text_shadow': "#FFFFFF",
        'blue_player_glow': "#0066FF81",
        'red_player_glow': "#FF000081",
        'game_over_text': "#C90E0E",
        'start_screen_bg': "#000000",
        'sart_screen_text': "#2D0BEE"}

# ----- AUDIO -----
# --- game music ---
STOP_SCREEN_DIM_FACTOR: float = 0.5
START_TRACK_VOLUME: float = 0.25
GAME_OVER_TRACK_VOLUME: float = 0.3
GAME_TRACK_1_VOLUME: float = 0.6
GAME_TRACK_2_VOLUME: float = 0.5

# --- sound effects ---
DAMAGE_SOUND_VOLUME: float = 0.4
EXPLOSION_SOUND_VOLUME: float = 0.4
GAME_OVER_SOUND_VOLUME: float = 1
RECORD_SOUND_VOLUME: float = 0.8
ABILITY_SOUND_VOLUME: float = 1

# ----- GAMEPLAY -----
STATS = {'score': 0, 'record': 0}
DEFAULT_PLAYER_SPEED: int = 250
OBSTACLE_SPAWN_TIME: float = 0.5 # seconds
PLAYER_ABILITY_COOLDOWN: float = 10.0 # seconds
PLAYER_ABILITY_DURATION: float = 1.0 # seconds
