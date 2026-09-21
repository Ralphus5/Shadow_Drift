import pygame
import pymunk
import os
import sys
import json
import atexit
from math import *  # type: ignore
from typing import * # type: ignore
from os.path import join
import random
from random import randint, choice, choices, uniform, triangular
from time import perf_counter
from functools import wraps

if TYPE_CHECKING: from main import Game
