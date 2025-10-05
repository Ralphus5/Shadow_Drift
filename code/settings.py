import json
from time import sleep
from random import randint, choice
from os.path import join
from sys import exit
import pygame

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720

game_time = pygame.time.get_ticks()

score = 0
record = 0

STATS = {
    'health': 2,
    'ability': True,
    'score': score,
    'record': record
}

bg1_frames = [pygame.image.load(join('images', 'background1', f'bg1_{i}.png')) for i in range(11)]

bg2_frames = [pygame.image.load(join('images', 'background1', f'bg1_{i}.png')) for i in range(11)]

bg3_frames = [pygame.image.load(join('images', 'background1', f'bg1_{i}.png')) for i in range(11)]

BACKGROUNDS = {
   'bg1': bg1_frames,
   'bg2': bg2_frames,
   'bg3': bg3_frames,
}

def update_time():
    global game_time
    game_time = pygame.time.get_ticks()