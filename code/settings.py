import pygame
from sys import exit
from os.path import join
import json
from random import randint, choice
from time import sleep

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720

score = 0
record = 0

stats = {
    'health': 2,
    'ability': True,
    'score': score,
    'record': record
}