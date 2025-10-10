from settings import *
import pygame
import os
import sys
import json
from math import *
from os.path import join
from typing import *
from random import randint, choice, choices, uniform, triangular
from time import perf_counter

# --- ui ---
def check_hover(rect: pygame.Rect, mouse_pos: tuple[float, float]) -> bool:
    """Return True if mouse is hovering over rect."""
    return rect.collidepoint(mouse_pos)

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