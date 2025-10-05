import pygame
from sys import exit
from os.path import join
import json
from random import randint, choice
from time import sleep

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720

font1 = pygame.font.Font(None, 50)
font2 = pygame.font.SysFont('Times New Roman', 200)

score = 0
record = 0

stats = {
    'health': 2,
    'ability': True,
    'score': score,
    'record': record
}