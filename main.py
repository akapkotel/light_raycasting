#!/usr/bin/env python
"""
See README.md file.
TODO: use typing module
"""
import cProfile
import pstats
import random
import time

from functools import wraps
from typing import List, Tuple, Optional

import pygame
import pygame.freetype

from options_screen import (Button, CheckButton, ClampedValue, GREEN, BLACK,
                            WHITE)


# to profile simulation on your machine, set this to True:
PROFILE = False
TIMER = True

# constants:
pygame.init()
FONT = pygame.freetype.SysFont("Garamond", 20)
SCREEN_W = 1000
SCREEN_H = 1000
TITLE = "Visibility algorithm demo"
RED = (255, 0, 0)
SUN = (100, 150, 100)
DARK = (32, 32, 32)
LIGHT = (192, 192, 192)
SHADOW = (240, 240, 240)

# cached functions:
get_time = time.perf_counter
draw = pygame.draw
draw_line = draw.line
draw_circle = draw.circle
draw_polygon = draw.polygon
draw_text = FONT.render_to


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = get_time()

        result = func(*args, **kwargs)
        if not TIMER:
            return result

        end_time = get_time()
        total_time = end_time - start_time
        fps = 1 // total_time

        if func.__name__ == "update_lights":
            displayed_fps = Application.displayed_fps
            if displayed_fps[0] < 30:
                displayed_fps[0] += 1
                displayed_fps[1] += fps
            else:
                displayed_fps = [0, 0]
            Application.displayed_fps = displayed_fps

        fr = f"{func.__name__} finished in {total_time:.4f} secs. FPS: {fps}"
        print(fr)
        return result
    return wrapper


class Application:
    # to draw rays from origin to eah obstacle-corner:
    SHOW_RAYS = True
    # number of origins from where FOV/light polygon will be drawn. Raising this
    # variable will get very costly fast!
    LIGHTS_COUNT = 1
    # type of polygon is determined by the number of edges: 3 = triangle,
    # 4 = square, 5 = pentagon, 6 = hexagon etc.
    OBSTACLE_EDGES = 8
    # size of obstacles and distance between them is determined by this variable
    # (smaller the size, more obstacles would be drawn!):
    OBSTACLE_EDGE_SIZE = 100
    # you can draw randomized colors FOV polygons by switching this to 1 (you
    # will need this to actually see that there are more than 1 light polygons
    # drawn):
    RANDOM_COLORS = False
    # decide what state of application should be displayed:
    RUN_SIMULATION = False

    displayed_fps = [0, 0]  # total number of measures, sum of measures

    def __init__(self):
        self.lights = []
        self.obstacles = []
        self.options = []
        self.run_simulation = False

    def main_loop(self):
        application.options = self.create_interactable_options()
        pointed = None

        while not self.RUN_SIMULATION:
            self.redraw_configuration_screen(self.options)
            for event in pygame.event.get():
                event_type = event.type
                if event_type == pygame.MOUSEMOTION:
                    x, y = event.pos
                    pointed = self.if_mouse_over_clickable(x, y, self.options)
                elif event_type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # mouse left button
                        if pointed is not None:
                            pointed.on_click()
                elif event_type == pygame.QUIT:
                    pygame.quit()

        bind_light_to_cursor = True
        self.obstacles = self.create_obstacles()
        self.lights = self.create_lights(self.obstacles)
        while self.RUN_SIMULATION:
            self.redraw_screen(self.lights, self.obstacles)  # draw previous
            # frame
            if bind_light_to_cursor:
                self.update_lights(self.lights)
            for event in pygame.event.get():
                event_type = event.type
                if event_type == pygame.MOUSEMOTION and bind_light_to_cursor:
                    x, y = event.pos
                    self.on_mouse_motion(x, y, self.lights)
                elif event_type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if event.button == 1:  # mouse left button
                        bind_light_to_cursor = not bind_light_to_cursor
                        self.on_mouse_motion(x, y, self.lights)
                elif event_type == pygame.QUIT:
                    self.RUN_SIMULATION = False
                    pygame.quit()

    def create_obstacles(self) -> List:
        obstacles, bounding_boxes = [], []
        size = self.OBSTACLE_EDGE_SIZE
        for i in range(size * 2, SCREEN_W, size * 3):
            for j in range(size * 2, SCREEN_H, size * 3):
                obstacle = self.new_obstacle(i, j)
                obstacles.append(obstacle)
        return obstacles

    def new_obstacle(self, i: float, j: float) -> List:
        """Produce obstacle (polygon) of any size and number of vertices."""
        obstacle = []
        size = self.OBSTACLE_EDGE_SIZE
        edges = self.OBSTACLE_EDGES
        for k in range(edges):
            angle = (k - 1) * (360 // edges)
            offset = 180 // edges
            point = move_along_vector((i, j), size, angle=angle - offset)
            obstacle.append(point)
        return obstacle

    @staticmethod
    @timer
    def update_lights(lights):
        for light in lights:
            light.update_visible_polygon()

    def create_lights(self, obstacles: List) -> List:
        lights = []
        x, y = SCREEN_W // 2, SCREEN_H // 2
        for i in range(self.LIGHTS_COUNT):
            color = self.get_light_color()
            point = self.get_light_position(i, x, y)
            # noinspection PyTypeChecker
            light = Light(*point, color, obstacles)
            lights.append(light)
        return lights

    def get_light_color(self) -> Tuple:
        if self.RANDOM_COLORS:
            randint = random.randint
            return randint(0, 255), randint(0, 255), randint(0, 255)
        else:
            return LIGHT

    def get_light_position(self, i: int, x: float, y: float) -> Tuple:
        if not i:
            point = (x, y)
        else:
            angle = i * (360 // self.LIGHTS_COUNT)
            point = move_along_vector((x, y), 10, angle=angle)
        return point

    # noinspection PyTypeChecker
    def create_interactable_options(self):
        options = []
        p = (SCREEN_H / 2, SCREEN_W / 2)  # basic position to override
        positions = [(p[0] + 300, p[1]), (p[0], p[1] - 100), (p[0], p[1] - 200),
            (p[0], p[1] - 300), (p[0], p[1] - 400)]
        types = [Button, ClampedValue, ClampedValue, CheckButton, CheckButton]
        functions = [self.run_application, self.change_edges_count,
            self.change_edge_size, self.toggle_rays, self.toggle_colors]
        ranges = [None, (3, 20, 1), (25, 200, 25), None, None]
        values = ["Run", 5, 100, self.SHOW_RAYS, self.RANDOM_COLORS]
        labels = [None, "Edges:", "Size:", "Show rays?", "Random colors?"]

        for i, position in enumerate(positions):
            if types[i] == ClampedValue:
                _min, _max, step = ranges[i]
                b = ClampedValue(window, *position, 25, 25, values[i], _min, _max,
                                 step, functions[i], labels[i])
            elif types[i] == CheckButton:
                b = CheckButton(window, *position, 15, 15, values[i], functions[i],
                                labels[i])
            else:
                b = Button(window, *position, 25, 25, values[i], functions[i])
            options.append(b)
        return options

    def run_application(self):
        self.RUN_SIMULATION = True

    def change_edges_count(self):
        self.OBSTACLE_EDGES = self.options[1].value

    def change_edge_size(self):
        self.OBSTACLE_EDGE_SIZE = self.options[2].value

    def toggle_rays(self):
        self.SHOW_RAYS = self.options[3].value

    def toggle_colors(self):
        self.RANDOM_COLORS = self.options[4].value

    def redraw_configuration_screen(self, clickable_items: List):
        """
        Draw configuration screen, where user can set-up key variables of the
        simulation.
        """
        window.fill(DARK)
        # visual representation of obstacle shape:
        poly = self.new_obstacle(SCREEN_W // 2, SCREEN_H - 300)
        draw_polygon(window, WHITE, poly)

        for item in clickable_items:
            item.draw()
        pygame.display.update()

    @staticmethod
    def if_mouse_over_clickable(x: float,
                                y: float,
                                clickable_items: List) -> Optional[Button]:
        pointed = None
        for item in clickable_items:
            if item.mouse_over(x, y):
                item.active = True
                return item
        else:
            for item in clickable_items:
                item.active = False
        return pointed

    def redraw_screen(self, lights: List, obstacles: List):
        window.fill(DARK)
        self.draw_obstacles(obstacles)
        self.draw_light(lights)
        if self.displayed_fps:
            self.draw_fps_counter()
        pygame.display.update()

    def draw_fps_counter(self):
        try:
            value = (self.displayed_fps[1] // self.displayed_fps[0])
        except ZeroDivisionError:
            return
        color = GREEN if value > 24 else RED
        text = "FPS: " + str(value)
        draw_text(window, (SCREEN_W // 2, SCREEN_H // 20), text, color)

    @staticmethod
    def draw_obstacles(obstacles: List):
        for obstacle in obstacles:
            draw_polygon(window, BLACK, obstacle)

    def draw_light(self, lights: List):
        for light in lights:
            if len(light.light_polygon) > 2:
                draw_polygon(window, light.color, light.light_polygon)
            x, y = light.origin
            polygon = light.light_polygon
            if self.SHOW_RAYS:
                for i, r in enumerate(polygon):
                    color = WHITE if i else RED
                    draw_line(window, color, (x, y), (r[0], r[1]))
            draw_circle(window, BLACK, (int(x), int(y)), 5)

    def on_mouse_motion(self, x: float, y: float, lights: List):
        lights[0].move_to(x, y)
        if len(lights) > 1:
            for i, light in enumerate(lights):
                if i:
                    angle = i * (360 // self.LIGHTS_COUNT)
                    point = move_along_vector((int(x), int(y)), 15, angle=angle)
                    light.move_to(point[0], point[1])

    @staticmethod
    def drag_or_drop(drag_light):
        return not drag_light


if __name__ == "__main__":
    # do not move these imports to the top!
    from geometry import Light, move_along_vector

    window = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(TITLE)

    application = Application()

    if PROFILE:
        profiler = cProfile.Profile()
        profiler.enable()
    application.main_loop()
    if PROFILE:
        # noinspection PyUnboundLocalVariable
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats("cumtime")
        stats.print_stats(20)
