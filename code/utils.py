from settings import *
import pygame
import os
import sys
import json
import atexit
from math import *
from typing import *
from os.path import join
import random
from random import randint, choice, choices, uniform, triangular
from time import perf_counter
from functools import wraps

# --- mouse input ---
def get_scaled_mouse_pos(window: pygame.Surface, base_resolution: tuple[int, int]) -> tuple[float, float]:
    """Return mouse position scaled from current window to base resolution."""
    window_w, window_h = window.get_size()
    scale_x = base_resolution[0] / window_w
    scale_y = base_resolution[1] / window_h
    mx, my = pygame.mouse.get_pos()
    return mx * scale_x, my * scale_y

# --- randomizers ---
def random_of_spectrum(start: int|float, end: int|float, as_float=False, bias: float=None) -> int|float:
    """Return random number from [start, end].
    - as_float: True → return float, False → return integer
    - bias: if given (0.0–1.0), biases result toward one end
      e.g. bias=0.2 favors start, bias=0.8 favors end"""
    if bias is not None:
        # triangular gives bias toward "mode"
        value = triangular(start, end, start + (end - start) * bias)
        return value if as_float else int(value)
    return uniform(start, end) if as_float else randint(start, end)

def random_of_selection(selection: Sequence, weights: Optional[Sequence[float]] =None, unique: bool=False) -> Sequence[Any]:
    """Return random element from a collection.
    - weights: optional list of probabilities (must match len(selection))
    - unique: if True, convert to set before choice (removes duplicates)"""
    seq = list(set(selection)) if unique else list(selection)
    if weights:
        return choices(seq, weights=weights, k=1)[0]
    return choice(seq)

# --- debugging and performance check ---
# check how long a function took to execute
def get_func_time(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time: float = perf_counter()
        result: Any = func(*args, **kwargs)
        end_time: float = perf_counter()

        print(f'"{func.__name__}()" took {end_time - start_time:.3f} seconds to execute')
        return result

    return wrapper

# show playtime and runtime
def print_game_time(play_time, total_paused, runtime):
    '''use this at top of the event handler function to mesure times'''
    print(f"[time] played = {play_time:.3f}s   stopped = {total_paused:.3f}s   absolute runtime = {runtime}") # DEBUG

class UIButton:
    """Simple hoverable and clickable image button."""
    def __init__(self, image, pos: tuple, anchor: str = "center", hover_scale_factor: float = 1.1):
        self.base_image = image
        self.rect = image.get_rect()
        setattr(self.rect, anchor, pos)
        self.scale_factor = hover_scale_factor

        self.hovered = False
        self.hover_changed = False
        self.clicked = False

    def update(self, mouse_pos: tuple[float, float], mouse_click: bool):
        prev_hover = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.hover_changed = (self.hovered != prev_hover)
        self.clicked = mouse_click and self.hovered

    def draw(self, screen):
        scale = self.scale_factor if self.hovered else 1.0
        surf = pygame.transform.rotozoom(self.base_image, 0, scale)
        rect = surf.get_rect(center=self.rect.center)
        screen.blit(surf, rect)
