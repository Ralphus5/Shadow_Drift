"""Global constants and configuration settings"""

import os, sys, json
from os.path import join
from random import randint, choice
from time import sleep
import pygame

# --- detect running mode ---
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
    USER_DIR = os.path.expanduser(join("~", "Documents", "ShadowDrift"))
else:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    USER_DIR = join(BASE_DIR, "data")

# --- create save directory if needed ---
os.makedirs(USER_DIR, exist_ok=True)

# --- asset file paths ---
IMG_DIR   = join(BASE_DIR, "images")
AUDIO_DIR = join(BASE_DIR, "audio")
DATA_DIR  = join(BASE_DIR, "data") # only needed if another savefile is added
FONT_DIR = join(BASE_DIR, "fonts")
SAVE_FILE = join(USER_DIR, "save.json")

# --- window and game globals ---
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
BASE_RESOLUTION = (WINDOW_WIDTH, WINDOW_HEIGHT)
FPS = 60
STATS = {'score': 0, 'record': 0}
OBSTACLE_SPAWN_TIME = 500#ms

# --- track absolute game time ---
def update_time():
    global game_time
    game_time = pygame.time.get_ticks()

game_time = pygame.time.get_ticks()
