#!/usr/bin/env python

import pygame
import pygame.freetype

pygame.init()
draw = pygame.draw
FONT = pygame.freetype.SysFont("Garamond", 20)
draw_text = FONT.render_to


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (127, 127, 127)
GREEN = (0, 255, 0)


class ValueLabel:

    def __init__(self, window, x: float, y: float, h: float, w: float,
                 value: int):
        self.x = x
        self.y = y
        self.height = h
        self.width = w
        self.value = value
        self.window = window


class Interactable:

    def __init__(self, window, x: float, y: float, h: float, w: float,
                 text: str = "", function: callable = None):
        self.x = x
        self.y = y
        self.height = h
        self.width = w
        self.text = text
        self.points = self.create_points_list(x, y, h, w)
        self.window = window
        self.function = function
        self.active = False

    @staticmethod
    def create_points_list(x, y, h, w):
        points = [(x - w, y - h), (x + w, y - h), (x + w, y + h), (x - w, y + h)]
        return points

    def draw(self):
        color = GREEN if self.active else WHITE
        draw.polygon(self.window, color, self.points)
        if self.text:
            draw_text(self.window, (self.x - 20, self.y - 10), self.text,
                      BLACK)

    def mouse_over(self, x, y):
        return abs(self.x - x) <= self.width and abs(self.y - y) <= self.height

    def on_click(self):
        try:
            self.function()
        except TypeError:
            pass

