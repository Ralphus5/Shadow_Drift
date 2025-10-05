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

COLORS = {
   'bg-1': '#caa0de',
   'bg-2': '#c94087',
   'bg-3': '#b02143',
}

def update_time():
    global game_time
    game_time = pygame.time.get_ticks()