"""Global constants and configuration settings."""

import os, sys, json
from os.path import join
from random import randint, choice, choices, uniform, triangular
from time import sleep, perf_counter
import pygame

# --- VISUALS ---
# --- display ---
WINDOW_WIDTH = 1280 
WINDOW_HEIGHT = 720
BASE_RESOLUTION = (WINDOW_WIDTH, WINDOW_HEIGHT)
FPS = 60

# --- colors ---
COLOR = {
    'ui_text': "#000000",
    'ui_text_shadow': "#FFFFFF",
    'blue_player_glow': "#0066FF81",
    'red_player_glow': "#FF000081",
    'game_over_text': "#C90E0E",}

# --- AUDIO ---
# --- game music ---
STOP_SCREEN_DIM_FACTOR = 0.5
START_TRACK_VOLUME = 0.3
GAME_OVER_TRACK_VOLUME = 0.4
GAME_TRACK_1_VOLUME = 0.6
GAME_TRACK_2_VOLUME = 0.5

# --- sound effects ---
DAMAGE_SOUND_VOLUME = 0.4
EXPLOSION_SOUND_VOLUME = 0.5
GAME_OVER_SOUND_VOLUME = 1
RECORD_SOUND_VOLUME = 0.8
ABILITY_SOUND_VOLUME =1

# --- game globals ---
STATS = {'score': 0, 'record': 0}
OBSTACLE_SPAWN_TIME = 500#ms
DEFAULT_PLAYER_SPEED = 250
PLAYER_ABILITY_COOLDOWN = 10000#ms
PLAYER_ABILITY_DURATION = 1000#ms
ABILITY_UNUSED = -10000

# --- time utilities ---
game_time = pygame.time.get_ticks()

def update_time():
    '''Track absolute game time for gameplay mechanics like cooldown.'''
    global game_time
    game_time = pygame.time.get_ticks()

def get_time():
    '''Return high-precision time for animation orchestration.'''
    return perf_counter()

def freeze(seconds):
    '''Pause execution for given number of seconds.'''
    sleep(seconds)

# --- randomizers ---
def random_of_spectrum(start, end, as_float=False, bias=None):
    """Return random number from [start, end].
    - as_float: True → continuous uniform, False → integer uniform
    - bias: if given (0.0–1.0), biases result toward one end
      e.g. bias=0.2 favors start, bias=0.8 favors end"""
    if bias is not None:
        # triangular gives bias toward "mode"
        value = triangular(start, end, start + (end - start) * bias)
        return value if as_float else int(value)
    return uniform(start, end) if as_float else randint(start, end)

def random_of_selection(selection, weights=None, unique=False):
    """Return random element from a collection.
    - weights: optional list of probabilities (must match len(selection))
    - unique: if True, convert to set before choice (removes duplicates)"""
    seq = list(set(selection)) if unique else list(selection)
    if weights:
        return choices(seq, weights=weights, k=1)[0]
    return choice(seq)