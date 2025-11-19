from utils import *


# --- VISUALS ---
# display
WINDOW_WIDTH: int = 1280 
WINDOW_HEIGHT: int = 720
WINDOW_CENTER = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
BASE_RESOLUTION = (WINDOW_WIDTH, WINDOW_HEIGHT)
FPS: Annotated[int, (25-120)] = 60

# colors
COLOR = {'score_rectangle_phase': "#70C1FF",
         'score_shadow_rectangle_phase': "#000000",
         'score_icicle_phase': "#000000",
         'score_shadow_icicle_phase': "#FFFFFF",
         'blue_player_glow': "#0066FF81",
         'red_player_glow': "#FF000081",
         'game_over_text': "#C90E0E",
         'game_over_hint': "#C90E0E",
         'start_screen_bg': "#11121F",
         'settings_bg': "#11121F",
         'credits_bg': "#11121F",
         'title_text': "#2D0BEE",
         'start_hint': '#2D0BEE',
         'credits_hint': "#FFFFFF",
         'clickable_text_buttons': "#FFFFFF",
         'clickable_text_buttons_hovered': '#2D0BEE',
         'settings_headers': "#70C1FF",
         'key_binding_prompt': "#BB08DB",
         'quit_prompt_rect': "#11121F",
         'quit_prompt_rect_outline': "#000000",
         'quit_prompt_heading': "#70C1FF",
         'fruit_pickup_shadow': "#FFFFFF",
         'apple_pickup': "#FF0000FF",
         'blueberry_pickup': "#000DFFFF",
         'banana_pickup': "#FFFB00FF",
         'blue_banana_trail': "#1E3AC8B1",
         'red_banana_trail': "#CA0909B1",
         'credits_header': "#70C1FF",
         'credits_name': "#FFFFFF",
         'quit_icon_text': "#FB0000",
         'play_icon_text': "#00D512",
         'settings_icon_text':"#7E7E7E",}

# font sizes
TITLE_FONT_SIZE: int = 140
SCORE_FONT_SIZE: int = 35
GAME_OVER_FONT_SIZE: int = 150
GAME_OVER_HINT_FONT_SIZE: int = 23
START_HINT_FONT_SITZE: int = 23
CREDITS_HINT_FONT_SITZE: int = 23
SETTINGS_HEADERS_FONT_SIZE: int = 50
SETTINGS_TEXTS_FONT_SIZE: int = 35
QUIT_PROMPT_HEADING_FONT_SIZE: int = 40
QUIT_PROMPT_OPTIONS_FONT_SIZE: int = 45
CREDITS_BUTTON_FONT_SIZE: int = 30
FRUIT_PICKUP_MESSAGES_FONT_SIZE: int = 35
CREDITS_HEADER_FONT_SIZE: int = 70
CREDITS_NAME_FONT_SIZE: int = 45
ICON_TEXTS_FONT_SIZE: int = 20

# quit prompt window
QUIT_RECT_WIDTH: int = 850
QUIT_RECT_HEIGHT: int = 330
QUIT_RECT_ROUNDING: int = 8
QUIT_RECT_OUTLINE_THICKNESS: int = 4

# animations
TITLE_FLICKER_SPEED: Annotated[float, (1-6)] = 5
MAX_FLICKER_INT: Annotated[int, (188-255)] = 255
MIN_FLICKER_INT: Annotated[int, (60-160)] = 100
FADE_TO_BLACK_SMOOTHNESS: int = 600
FADE_TO_BLACK_DURATION: float = 0.6
GAME_OVER_FADE_DURATION: float = 1.6
PLAYER_EXPLOSION_SPEED: float = 0.9
PLAYER_BLACK_FADE_SPEED: Annotated[float, (0-10)] = 7.5
FRUIT_PICKUP_MESSAGES_DURATION: float = 1.0
FRUIT_PICKUP_RISE_SPEED: float = 65.0 # pixels / second
BANANA_TRAIL_DRAW_INTERVALL: float = 0.005  # shadows per frame
BANANA_TRAIL_LIFETIME: float = 0.4

# backgrounds
BACKGROUND_FRAME_INTERVALL: int = 70
DEFAULT_BACKGROUND_SCROLL_SPEED: int = 60
BACKGROUND_SCROLLABILITIES: dict[str:bool] = {'rectangle': True,
                                              'icicle': False,}

# ----- AUDIO -----
# user volume settings
MASTER_VOLUME: Annotated[float, (0-1)] = 1
MUSIC_VOLUME: Annotated[float, (0-1)] = 1
SFX_VOLUME: Annotated[float, (0-1)] = 1

# game music volumes
STOP_SCREEN_DIM_FACTOR: Annotated[float, (0-1)] = 0.4
START_TRACK_VOLUME: Annotated[float, (0-1)] = 0.3
GAME_OVER_TRACK_VOLUME: Annotated[float, (0-1)] = 0.25
CREDITS_TRACK_VOLUME: Annotated[float, (0-1)] = 0.7
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
PHASE_SWITCH_SOUND_VOLUME: Annotated[float, (0-1)] = 0.7
RECORD_SOUND_VOLUME: Annotated[float, (0-1)] = 1
ABILITY_SOUND_VOLUME: Annotated[float, (0-1)] = 1
DASH_SOUND_VOLUME: Annotated[float, (0-1)] = 1


# ----- GAMEPLAY -----
STATS = {'score': 0, 'record': 0}

# player
DEFAULT_PLAYER_SPEED: int = 250
ONE_LIFE_PLAYER_SPEED: int = 300
PLAYER_ABILITY_DURATION: float = 1.6 # seconds
PLAYER_ABILITY_COOLDOWN: float = 15.0 # seconds
DASH_DURATION: float = 0.12 # seconds (also determines dash distance)
DASH_SPEED: float = 1600
DASH_COOLDOWN: float = 0.3 # seconds
PLAYER_IFRAMES_DURATION: float = 1.0 # seconds

# fruits
FRUIT_SPAWNS_PER_MINUTE: float = 4.00
FRUITS_SPAWN_PROBABILITIES: dict[str:float] = {'apple': 1.0, 'blueberry': 0.2, 'banana': 0.5}
APPLE_POINTS: int = 10
BANANA_SPEED_BOOST: int = 150
BANANA_BOOST_DURATION: float = 12.0

# phase probabilities
START_PHASES: tuple[str] = ('rectangle', 'icicle')
PHASE_PROBABILITIES: dict[str:float] = {'rectangle': 1.0, 'icicle': 1.0}

# rectangle phase
RECTANGLE_SPAWN_TIME: float = 0.5 # seconds
FIRST_RECTANGLE_PHASE_END: int = 40
SECOND_RECTANGEL_PHASE_SPAWN_FACTOR: float = 1.2
SECOND_RECTANGLE_PHASE_END: int = 80
THIRD_RECTANGEL_PHASE_SPAWN_FACTOR: float = 1.4
THIRD_RECTANGLE_PHASE_END: int = 120
FOURTH_RECTANGLE_PHASE_SPAWN_FACTOR: float = 1.6
FOURTH_RECTANGLE_PHASE_END: int = 160

# icicle phase
ICICLE_SPAWN_TIME: float = 0.25 # seconds
FIRST_ICICLE_PHASE_END: int = 40
SECOND_ICICLE_PHASE_SPAWN_FACTOR: float = 1.25
SECOND_ICICLE_PHASE_END: int = 80
THIRD_ICICLE_PHASE_SPAWN_FACTOR: float = 1.2
THIRD_ICICLE_PHASE_END: int = 120
THIRD_ICICLE_PHASE_SPAWN_FACTOR: float = 1.166667
FOURTH_ICICLE_PHASE_END: int = 160


# --- DEFAULT KEY BINDINGS ---
KEY_BINDINGS = {
    "move_left": pygame.K_a,
    "move_right": pygame.K_d,
    "move_up": pygame.K_w,
    "move_down": pygame.K_s,
    "ability": pygame.K_SPACE,
    "dash": pygame.K_RETURN,
    "fullscreen": pygame.K_F11,}
