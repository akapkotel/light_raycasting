#!/usr/bin/env python
"""

"""
import os
import time
import random
import arcade
import pygame
import pygame.freetype

from functools import wraps


PATH = os.path.dirname(os.path.abspath(__file__)) + "/"


# debug variables:
TIMER = True
SHOW_RAYS = True  # to draw rays from origin to eah obstacle-corner

OBSTACLE_EDGE_SIZE = 150
OBSTACLE_EDGES = 8  # type of polygon is determined by the number of edges:
# 3 = triangle, 4 = square, 5 = pentagon, 6 = hexagon etc.

# constants:
SCREEN_W = 1000
SCREEN_H = 1000
TITLE = "Visibility algorithm demo"
FPS = 30
GREEN = arcade.color.GREEN
MAP_GREEN = arcade.color.APPLE_GREEN
GRASS = arcade.color.DARK_OLIVE_GREEN
RED = arcade.color.RED
SUN = arcade.color.LIGHT_YELLOW
WHITE = arcade.color.WHITE
DARK = (32, 32, 32)
LIGHT = (192, 192, 192)
GREY = arcade.color.GRAY
BLACK = (0, 0, 0)
SHADOW = arcade.color.DARK_GRAY
pygame.init()
FONT = pygame.freetype.SysFont("Garamond", 20)

view_left, view_bottom = 0, 0
r_random = random.random
get_time = time.perf_counter
draw_line = arcade.draw_line
draw_polygon_filled = arcade.draw_polygon_filled
draw_ellipse_outline = arcade.draw_ellipse_outline
SpriteList = arcade.SpriteList


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

        fr = f"{func.__name__} finished in {total_time:.4f} secs. FPS: {fps}"
        print(fr)
        return result
    return wrapper


def new_id(class_):
    """
    Assign new id to the newly instantiated object.

    :param class_: class -- any class which has count class attribute
    :return: int -- new id value
    """
    try:
        class_.count += 1
        return class_.count
    except ValueError:
        raise AttributeError("Object passed has no class attribute: 'count'!")


# @timer
def redraw_screen(light, obstacles):
    window.fill(DARK)
    draw_obstacles(obstacles)
    draw_light(light)
    pygame.display.update()


def draw_intersection(intersector, second_segemnt):
    color = RED if intersects(intersector, second_segemnt) else WHITE
    pygame.draw.line(window, color, *intersector)
    pygame.draw.line(window, color, *second_segemnt)


def draw_obstacles(obstacles):
    for obstacle in obstacles:
        pygame.draw.polygon(window, BLACK, obstacle)
        for corner in obstacle:
            pos = (corner[0]+15, corner[1]+15)
            FONT.render_to(window, pos, str(obstacle.index(corner)), WHITE)


# @timer
def draw_light(light):
    if len(light.light_polygon) > 2:
        pygame.draw.polygon(window, LIGHT, light.light_polygon)

    if SHOW_RAYS:
        for r in light.rays:
            # color = RED if light.rays.index(r) == 0 else WHITE
            pygame.draw.line(window, WHITE, (r[0][0], r[0][1]), (r[1][0], r[1][1]))
            index = light.rays.index(r)
            FONT.render_to(window, r[1], str(index), WHITE)

    pygame.draw.circle(window, SUN, (light.x, light.y), 10)


def new_obstacle(i, j):
    obstacle = []
    for k in range(OBSTACLE_EDGES):
        angle = (k - 1) * (360 // OBSTACLE_EDGES)
        offset = 180 // OBSTACLE_EDGES
        point = move_along_vector((i, j), OBSTACLE_EDGE_SIZE, angle=angle-offset)
        obstacle.append(point)
    return obstacle


def create_obstacles():
    obstacles = []
    size = OBSTACLE_EDGE_SIZE
    for i in range(size*2, SCREEN_W, size*3):
        for j in range(size*2, SCREEN_H, size*3):
            obstacle = new_obstacle(i, j)
            obstacles.append(obstacle)
    return obstacles


def main_loop():
    run = True
    obstacles = create_obstacles()
    light = Light(SCREEN_W//2, SCREEN_H//2, obstacles)

    while run:
        light.update_visible_polygon()
        for event in pygame.event.get():
            event_type = event.type
            if event_type == pygame.QUIT:
                run = False
                pygame.quit()
            elif event_type == pygame.MOUSEMOTION:
                on_mouse_motion(*event.pos, light)

        redraw_screen(light, obstacles)


def on_mouse_motion(x, y, light):
    light.move_to(x, y)


if __name__ == "__main__":
    from geometry import Light, intersects, move_along_vector # do not move this to the
    # top!
    window = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(TITLE)
    main_loop()

