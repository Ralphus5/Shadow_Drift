import os, sys, pygame, json
from random import randint, choice
from time import sleep

# detect running mode
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
    USER_DIR = os.path.expanduser(os.path.join("~", "Documents", "ShadowDrift"))
else:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    USER_DIR = os.path.join(BASE_DIR, "data")

# make sure the save directory exists
os.makedirs(USER_DIR, exist_ok=True)

IMG_DIR   = os.path.join(BASE_DIR, "images")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
DATA_DIR  = os.path.join(BASE_DIR, "data")  # still for reading bundled data
SAVE_FILE = os.path.join(USER_DIR, "record.txt")

# --- Window and game globals ---
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
game_time = pygame.time.get_ticks()

STATS = {'health': 2, 'ability': True, 'score': 0, 'record': 0}

# --- Asset loading ---
bg1_frames = [
    pygame.image.load(os.path.join(IMG_DIR, 'background1', f'bg1_{i}.png'))
    for i in range(11)
]
bg2_frames = [
    pygame.image.load(os.path.join(IMG_DIR, 'background1', f'bg1_{i}.png'))
    for i in range(11)
]
bg3_frames = [
    pygame.image.load(os.path.join(IMG_DIR, 'background1', f'bg1_{i}.png'))
    for i in range(11)
]

BACKGROUNDS = {'bg1': bg1_frames, 'bg2': bg2_frames, 'bg3': bg3_frames}

def update_time():
    global game_time
    game_time = pygame.time.get_ticks()
