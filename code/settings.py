from utils import *


# --- VISUALS ---
# display
WINDOW_WIDTH: int = 1280 
WINDOW_HEIGHT: int = 720
WINDOW_CENTER = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
BASE_RESOLUTION = (WINDOW_WIDTH, WINDOW_HEIGHT)
FPS: Annotated[int, (25-120)] = 60

# colors
COLOR = {'ui_text': "#000000",
         'ui_text_shadow': "#FFFFFF",
         'ui_text_stop': "#70C1FF",
         'ui_text_shadow_stop': "#000000",
         'blue_player_glow': "#0066FF81",
         'red_player_glow': "#FF000081",
         'game_over_text': "#C90E0E",
         'game_over_hint': "#C90E0E",
         'start_screen_bg': "#11121F",
         'stop_screen_bg': "#11121F",
         'title_text': "#2D0BEE",
         'start_hint': '#2D0BEE',
         'settings_text_buttons': "#FFFFFF",
         'settings_text_buttons_hovered': '#2D0BEE',
         'settings_headers': "#70C1FF",
         'key_binding_prompt': "#BB08DB",}

# font sizes
TITLE_FONT_SIZE: int = 140
SCORE_FONT_SIZE: int = 35
GAME_OVER_FONT_SIZE: int = 150
GAME_OVER_HINT_FONT_SIZE: int = 23
START_HINT_FONT_SITZE: int = 23
SETTINGS_HEADERS_FONT_SIZE: int = 50
SETTINGS_TEXTS_FONT_SIZE: int = 35


# animations
TITLE_FLICKER_SPEED: Annotated[float, (1-6)] = 5
MAX_FLICKER_INT: Annotated[int, (188-255)] = 255
MIN_FLICKER_INT: Annotated[int, (60-160)] = 100
FADE_TO_BLACK_SMOOTHNESS: int = 600
FADE_TO_BLACK_DURATION: float = 0.6
GAME_OVER_SCROLL_SPEED: float = 1.6
BACKGROUND_FRAME_INTERVALL: int = 100
PLAYER_EXPLOSION_SPEED: float = 0.9
PLAYER_BLACK_FADE_SPEED: Annotated[float, (0-10)] = 7.5


# ----- AUDIO -----
# user volume settings
MASTER_VOLUME: Annotated[float, (0-1)] = 1
MUSIC_VOLUME: Annotated[float, (0-1)] = 1
SFX_VOLUME: Annotated[float, (0-1)] = 1

# game music volumes
STOP_SCREEN_DIM_FACTOR: Annotated[float, (0-1)] = 0.4
START_TRACK_VOLUME: Annotated[float, (0-1)] = 0.3
GAME_OVER_TRACK_VOLUME: Annotated[float, (0-1)] = 0.25
GAME_TRACK_1_VOLUME: Annotated[float, (0-1)] = 0.4
GAME_TRACK_2_VOLUME: Annotated[float, (0-1)] = 0.4

# menu sound volumes
MENU_HOVER_SOUND_VOLUME: Annotated[float, (0-1)] = 0.4
MENU_SELECT_SOUND_VOLUME: Annotated[float, (0-1)] = 0.7
TITLE_FLASH_SOUND_VOLUME: Annotated[float, (0-1)] = 0.6

# gameplay sound volumes
EAT_FRUIT_SOUND_VOLUME: Annotated[float, (0-1)] = 0.85
DAMAGE_SOUND_VOLUME: Annotated[float, (0-1)] = 0.8
EXPLOSION_SOUND_VOLUME: Annotated[float, (0-1)] = 0.6
GAME_OVER_SOUND_VOLUME: Annotated[float, (0-1)] = 1
RECORD_SOUND_VOLUME: Annotated[float, (0-1)] = 1
ABILITY_SOUND_VOLUME: Annotated[float, (0-1)] = 1
DASH_SOUND_VOLUME: Annotated[float, (0-1)] = 1


# ----- GAMEPLAY -----
STATS = {'score': 0, 'record': 0}
FIRST_PHASE_END: int = 40
SECOND_PHASE_END: int = 80
THIRD_PHASE_END: int = 120
DEFAULT_PLAYER_SPEED: int = 250
ONE_LIFE_PLAYER_SPEED: int = 300
PLAYER_ABILITY_DURATION: float = 1.6 # seconds
PLAYER_ABILITY_COOLDOWN: float = 15.0 # seconds
DASH_DURATION: float = 0.12 # seconds (also determines dash distance)
DASH_SPEED: float = 1600
DASH_COOLDOWN: float = 0.3 # seconds
PLAYER_IFRAMES_DURATION: float = 1.0 # seconds
OBSTACLE_SPAWN_TIME: float = 0.5 # seconds
FRUIT_SPAWNS_PER_MINUTE: float = 3.50
FRUITS_SPAWN_PROBABILITIES: dict[str:float] = {'apple': .8, 'blueberry': .2, 'banana': .4}
APPLE_POINTS: int = 10
BANANA_SPEED_BOOST: int = 150
BANANA_BOOST_DURATION: float = 12.0


# --- DEFAULT KEY BINDINGS ---
KEY_BINDINGS = {
    # gameplay movement
    "move_left": pygame.K_a,
    "move_right": pygame.K_d,
    "move_up": pygame.K_w,
    "move_down": pygame.K_s,

    # abilities and actions
    "ability": pygame.K_SPACE,
    "dash": pygame.K_RETURN,

    # system and meta
    "fullscreen": pygame.K_F11,}
