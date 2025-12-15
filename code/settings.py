from imports import *


# --- VISUALS ---
# display
WINDOW_WIDTH: int = 1280 
WINDOW_HEIGHT: int = 720
WINDOW_CENTER = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
BASE_RESOLUTION = (WINDOW_WIDTH, WINDOW_HEIGHT)
FPS: Annotated[int, (25-120)] = 60

# menu
MENU_GRAVITY: int = 981

# colors
COLOR = {'score_rectangle_phase': "#70C1FF",
         'score_shadow_rectangle_phase': "#000000",
         'score_arrow_phase': "#000000",
         'score_shadow_arrow_phase': "#FFFFFF",
         'score_icicle_phase': "#000000",
         'score_shadow_icicle_phase': "#FFFFFF",
         'score_jellyfish_phase': "#0037FF",
         'score_shadow_jellyfish_phase': "#FFFFFF",
         'score_saw_blade_phase': "#0037FF",
         'score_shadow_saw_blade_phase': "#000000",
         'score_rocket_phase': "#0037FF",
         'score_shadow_rocket_phase': "#FFFFFF",
         'score_asteroid_phase': "#0037FF",
         'score_shadow_asteroid_phase': "#FFFFFF",
         'score_spike_ball_phase': "#0037FF",
         'score_shadow_spike_ball_phase': "#FFFFFF",
         'score_spike_block_phase': "#000000",
         'score_shadow_spike_block_phase': "#FFFFFF",
         'score_boss_phase': "#0037FF",
         'score_shadow_boss_phase': "#FFFFFF",
         'blue_player_glow': "#0066FF81",
         'red_player_glow': "#FF000081",
         'game_over_text': "#C90E0E",
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
         'effect_text_shadow': "#FFFFFF",
         'apple_effect_text': "#ea0808",
         'blueberry_effect_text': "#2639db",
         'banana_effect_text': "#efe508",
         'chili_effect_text': "#953333",
         'grapes_effect_text': "#8D53AA",
         'pear_effect_text': "#99e550",
         '250_rectangle_shot_effect_text': "#119329",
         '300_rectangle_shot_effect_text': "#d700ff",
         '350_rectangle_shot_effect_text': "#fff200",
         '400_rectangle_shot_effect_text': "#ff0000",
         'arrow_shot_effect_text': "#6d423a",
         'icicle_shot_effect_text': "#70c4f5",
         'jellyfish_shot_effect_text': "#6492E0",
         'sawblade_shot_effect_text': "#9996a2",
         'rocket_shot_effect_text': "#ea0404",
         'asteroid_shot_effect_text': "#857c73",
         'spikeball_shot_effect_text': "#131312",
         'spikeblock_shot_effect_text': "#9badb7",
         'blue_banana_trail': "#1E3AC8FF",
         'red_banana_trail': "#CA0909FF",
         'credits_header': "#70C1FF",
         'credits_name': "#FFFFFF",
         'quit_icon_text': "#FB0000",
         'play_icon_text': "#00D512",
         'settings_icon_text':"#7E7E7E",
         'boss_health_bar': "#FF0000",
         'boss_health_bar_damage': "#FFF700",
         'boss_health_bar_border': "#FFFFFF",
         'boss_name': "#7B2087",
         'boss_name_shadow': "#DD00FF"}

# font sizes
TITLE_FONT_SIZE: int = 140
SCORE_FONT_SIZE: int = 35
GAME_OVER_FONT_SIZE: int = 150
GAME_OVER_SCORE_FONT_SIZE: int = 23
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
BOSS_NAME_FONT_SIZE: int = 50

# quit prompt window
QUIT_RECT_WIDTH: int = 850
QUIT_RECT_HEIGHT: int = 330
QUIT_RECT_ROUNDING: int = 5
QUIT_RECT_OUTLINE_THICKNESS: int = 4

# animations
TITLE_FLICKER_SPEED: Annotated[float, (1-6)] = 5
MAX_FLICKER_INT: Annotated[int, (188-255)] = 255
MIN_FLICKER_INT: Annotated[int, (60-160)] = 100
FADE_TO_BLACK_SMOOTHNESS: int = 600
FADE_TO_BLACK_DURATION: float = 0.6
PHASE_CHANGE_FADE_DURATION: float = 0.8
GAME_OVER_FADE_DURATION: float = 1.6
PLAYER_EXPLOSION_SPEED: float = 0.85
BOSS_EXPLOSION_SPEED: float = 0.7
PLAYER_BLACK_FADE_SPEED: Annotated[float, (0-10)] = 7.5
EFFECT_TEXT_DURATION: float = 1.0
EFFECT_TEXT_RISE_SPEED: float = 65.0 # pixels / second
BANANA_TRAIL_LIFETIME: float = 0.53

# backgrounds
BACKGROUND_FRAME_INTERVALL: int = 70
DEFAULT_BACKGROUND_SCROLL_SPEED: int = 60
BACKGROUND_SCROLLABILITIES: dict[str:str] = {'rectangle': 'right',
                                              'arrow': 'left',
                                              'icicle': None,
                                              'jellyfish': None,
                                              'saw_blade': None,
                                              'rocket': None,
                                              'asteroid': None,
                                              'spike_ball': None,
                                              'spike_block': None,
                                              'boss': None}

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
BOSS_TRACK_VOLUME: Annotated[float, (0-1)] = 0.3

# menu sound volumes
MENU_HOVER_SOUND_VOLUME: Annotated[float, (0-1)] = 0.4
MENU_SELECT_SOUND_VOLUME: Annotated[float, (0-1)] = 0.7
TITLE_FLASH_SOUND_VOLUME: Annotated[float, (0-1)] = 0.6

# gameplay sound volumes
USING_CONTROLLER_SOUND_VOLUME: Annotated[float, (0-1)] = 1.0 # unaffected by in-game settings
COIN_PICKUP_SOUND_VOLUME: Annotated[float, (0-1)] = 1.0
EAT_FRUIT_SOUND_VOLUME: Annotated[float, (0-1)] = 0.85
DAMAGE_SOUND_VOLUME: Annotated[float, (0-1)] = 0.8
DEATH_SOUND_VOLUME: Annotated[float, (0-1)] = 0.6
GAME_OVER_SOUND_VOLUME: Annotated[float, (0-1)] = 1.0
PHASE_SWITCH_SOUND_VOLUME: Annotated[float, (0-1)] = 0.7
RECORD_SOUND_VOLUME: Annotated[float, (0-1)] = 1.0
ABILITY_SOUND_VOLUME: Annotated[float, (0-1)] = 1.0
DASH_SOUND_VOLUME: Annotated[float, (0-1)] = 1.0
SHOOT_SOUND_VOLUME: Annotated[float, (0-1)] = 1.0
BOSS_GROWL_SOUND_VOLUME: Annotated[float, (0-1)] = 1.0
BOSS_HURT_SOUND_VOLUME: Annotated[float, (0-1)] = 0.7
ENERGY_BALL_SHOT_SOUND_VOLUME: Annotated[float, (0-1)] = 0.9
BUFF_END_SOUND_VOLUME: Annotated[float, (0-1)] = 0.8
BOSS_DEATH_SOUND_VOLUME: Annotated[float, (0-1)] = 1


# ----- GAMEPLAY -----
STATS: dict = {'score': 0, 'record': 0}
SCORE_UPDATE_TIME: int = 3000 #ms

# player
PLAYER_IFRAMES_DURATION: float = 1.2 # seconds
DEFAULT_PLAYER_SPEED: int = 250
ONE_LIFE_PLAYER_SPEED: int = 300
PLAYER_ABILITY_DURATION: float = 1.6 # seconds
PLAYER_ABILITY_COOLDOWN: float = 15.0 # seconds
DASH_DURATION: float = 0.12 # seconds (also determines dash distance)
DASH_SPEED: float = 1600
DASH_COOLDOWN: float = 0.25 # seconds

# coins
COIN_SPAWNS_PER_MINUTE: float = 14.00
COIN_POINTS: int = 2
COIN_SPEED_RANGE: tuple[int] = (100,220)
COIN_FRAME_INTERVALL: int = 35

# fruits
FRUIT_SPAWNS_PER_MINUTE: float = 3.00
FRUITS_SPAWN_PROBABILITIES: dict[str:float] = {'apple': 0.9, 'blueberry': 0.4, 'banana': 0.5, 'chili': 0.3, 'grapes': 0.3, 'pear': 0.2}
FRUIT_SPEED_RANGE: tuple[int] = (100,220)
APPLE_POINTS: int = 10
BANANA_SPEED_BOOST: int = 150
BANANA_BOOST_DURATION: float = 25.0
FIRE_POWER_DURATION: float = 25.0
FIREBALL_SHOOT_COOLDOWN: float = 0.6
FIRE_BALL_SPEED: int = 600
POINTS_FOR_OBSTACLE_SHOOT: int = 2

# --- phases ---
PHASE_PROBABILITIES: dict[str:float] = {'arrow': 0.7, 'icicle': 1.0, 'jellyfish': 1.0, 'saw_blade': 1.0, 'rocket': 0.9, 'asteroid': 1.0, 'spike_ball': 1.0, 'spike_block': 1.0}

PHASE_END_POINTS: dict[str:int] = {'rectangle': 10, 'arrow': 15, 'icicle': 15, 'jellyfish': 15, 'saw_blade': 15, 'rocket': 25, 'asteroid': 15, 'spike_ball': 15, 'spike_block': 15, 'boss': 200}

# sub-phase durations
FIRST_OBSTACLE_PHASE_END: int = 10
SECOND_OBSTACLE_PHASE_END: int = 25
THIRD_OBSTACLE_PHASE_END: int = 40
FOURTH_OBSTACLE_PHASE_END: int = 60

# rectangle phase
RECTANGLE_SPAWN_TIME: float = 0.8 # seconds
SECOND_RECTANGEL_PHASE_SPAWN_FACTOR: float = 1.2
THIRD_RECTANGEL_PHASE_SPAWN_FACTOR: float = 1.4
FOURTH_RECTANGLE_PHASE_SPAWN_FACTOR: float = 1.6

# arrow phase
ARROW_PHASE_DELAY: float = 1.0
ARROW_SUB_PHASE_DURATION: int = 10
ARROW_SINGLES_SPAWN_TIME: float = 0.33
ARROW_COLUMN_SPAWN_TIME: float = 2.5
ARROW_COLUMN_SPAWN_HEIGHTS: tuple[int] = (20, 260)
SECOND_ARROW_PHASE_SPAWN_FACTOR: float = 1.2
THIRD_ARROW_PHASE_SPAWN_FACTOR: float = 1.4
FOURTH_ARROW_PHASE_SPAWN_FACTOR: float = 1.6

# icicle phase
ICICLE_PHASE_DELAY: float = 1.0
ICICLE_SPAWN_TIME: float = 0.19 # seconds
SECOND_ICICLE_PHASE_SPAWN_FACTOR: float = 1.15
THIRD_ICICLE_PHASE_SPAWN_FACTOR: float = 1.2
FOURTH_ICICLE_PHASE_SPAWN_FACTOR: float = 1.25

# jellyfish phase
JELLYFISH_PHASE_DELAY: float = 1.0
JELLYFISH_SPAWN_TIME: float = 0.26
JELLYFISH_GLOW_RADIUS: int = 175
JELLYFISH_GLOW_FREQUENCY: float = 1.5
JELLYFISH_FRAME_INTERVALL: int = 50

# saw blade phase
SAW_BLADE_PHASE_DELAY: float = 1.5
SAW_BLADE_SPAWN_TIME: float = 0.46 # seconds
SECOND_SAW_BLADE_PHASE_SPAWN_FACTOR: float = 1.2
THIRD_SAW_BLADE_PHASE_SPAWN_FACTOR: float = 1.4
FOURTH_SAW_BLADE_PHASE_SPAWN_FACTOR: float = 1.6

# rocket phase
ROCKET_PHASE_DELAY: float = 2.0
ROCKET_SPAWN_TIME: float = 0.27 # seconds
SECOND_ROCKET_PHASE_SPAWN_FACTOR: float = 1.2
THIRD_ROCKET_PHASE_SPAWN_FACTOR: float = 1.4
FOURTH_ROCKET_PHASE_SPAWN_FACTOR: float = 1.6

# asteroid phase
ASTEROID_PHASE_DELAY: float = 1.0
ASTEROID_SPAWN_TIME: float = 0.35 # seconds

# spike ball phase
SPIKE_BALL_PHASE_DELAY: float = 1.0
SPIKE_BALL_SPAWN_TIME: float = 0.46 # seconds

# spike block phase
SPIKE_BLOCK_PHASE_DELAY: float = 1.0
SPIKE_BLOCK_SPAWN_TIME: float = 0.36 # seconds

# boss phase
BOSS_PHASE_START_POINTS: int = 500
BOSS_DAMAGE_PER_SHOT: int = 1
BOSS_HEALTH: int = 40
BOSS_SPEED: int = 170
BOSS_SPEED_DURING_SUMMON: int = 70
BOSS_STATE_DURATIONS: dict[str:int] = {'transition': 1.0, 'follow_player': 5, 'summon_saw_blades': 8, 'summon_asteroids': 8, 'shoot_energy_ball': 7}
BOSS_SAW_BLADE_SPAWN_DURATION: float = 0.38
BOSS_SAW_BLADE_SPEED: int = 360
BOSS_ASTEROID_SPAWN_DURATION: int =  0.4
BOSS_ASTEROID_SPEED: int = 240
DARK_ENERGY_BALL_SPEED: int = 200
DART_ENERGY_BALL_LIFE_TIME: float = 8.0 # seconds
DARK_ENERGY_BALL_GLOW_RADIUS: int = 200
BOSS_PHASE_END_DURATION: float = 3.0 # seconds
BOSS_HEALTH_BAR_HEIGHT: int = 26
BOSS_HEALTH_BAR_LENGTH: int = 900
BOSS_HEALTH_CHANGE_SPEED: float = 0.06
BOSS_PHASE_TRANSITION_TIME: float = 5.5


# --- DEFAULT KEY BINDINGS ---
KEY_BINDINGS: dict[str:int] = {'move_left': pygame.K_a,
                               'move_right': pygame.K_d,
                               'move_up': pygame.K_w,
                               'move_down': pygame.K_s,
                               'ability': pygame.K_SPACE,
                               'dash': pygame.K_RETURN,
                               'shoot_up': pygame.K_UP,
                               'shoot_down': pygame.K_DOWN,
                               'shoot_right': pygame.K_RIGHT,
                               'shoot_left': pygame.K_LEFT,
                               'fullscreen': pygame.K_F11}

# --- CONTROLLER ---
CONTROLLER_DEADZONE: float = 0.3
PAD_AXIS_MOVE_X = 0    # left stick horizontal
PAD_AXIS_MOVE_Y = 1    # left stick vertical
PAD_AXIS_SHOOT_X = 2   # right stick horizontal
PAD_AXIS_SHOOT_Y = 3   # right stick vertical
PAD_A_BUTTON = 0
PAD_B_BUTTON = 1
PAD_X_BUTTON = 2
PAD_Y_BUTTON = 3
PAD_HOME_BUTTON = 5
PAD_SELECT_BUTTON = 4
PAD_START_BUTTON = 6
PAD_LEFT_SHOULDER_BUTTON = 9
PAD_RIGHT_SHOULDER_BUTTON = 10
PAD_D_PAD_UP = 11
PAD_D_PAD_DOWN = 12
PAD_D_PAD_LEFT = 13
PAD_D_PAD_RIGHT = 14
PAD_LEFT_JOYSTICK = 7
PAD_RIGHT_JOYSTICK = 8