#!/usr/bin/env python
"""
See README.md file.
"""
import time
import random
from functools import wraps

import pygame
import pygame.freetype

# debug variables:
TIMER = True
# to draw rays from origin to eah obstacle-corner:
SHOW_RAYS = True
# to highlight vertices of edge closest to the origin, green vertex is first
# and red is second:
CLOSEST_WALL = True
# number of origins from where FOV/light polygon will be drawn. Raising this
# variable will get very costly fast!
LIGHTS_COUNT = 1
# type of polygon is determined by the number of edges: 3 = triangle,
# 4 = square, 5 = pentagon, 6 = hexagon etc.
OBSTACLE_EDGES = 4
# size of obstacles and distance between them is determined by this variable
# (smaller the size, more obstacles would be drawn!):
OBSTACLE_EDGE_SIZE = 100
# you can draw randomized colors FOV polygons by switching this to 1 (you
# will need this to actually see that there are more than 1 light polygons
# drawn):
RANDOM_COLORS = False


# constants:
pygame.init()
FONT = pygame.freetype.SysFont("Garamond", 20)
SCREEN_W = 1000
SCREEN_H = 1000
TITLE = "Visibility algorithm demo"
RED = (255, 0, 0)
GREEN = (0, 255, 0)
SUN = (100, 150, 100)
WHITE = (255, 255, 255)
DARK = (32, 32, 32)
LIGHT = (192, 192, 192)
GREY = (127, 127, 127)
BLACK = (0, 0, 0)
SHADOW = (240, 240, 240)

get_time = time.perf_counter
draw = pygame.draw
draw_text = FONT.render_to


gfps = []


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = get_time()

        result = func(*args, **kwargs)
        if not TIMER:
            return result

        end_time = get_time()
        total_time = end_time - start_time

        fps = 1 // total_time\

        if func.__name__ == "update_lights":
            global gfps
            if len(gfps) == 10:
                gfps.pop(0)
            gfps.append(fps)

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
def redraw_screen(lights, obstacles):
    window.fill(DARK)
    draw_obstacles(obstacles)
    draw_light(lights)
    draw_fps_counter()
    pygame.display.update()


def draw_fps_counter():
    if gfps:
        value = sum(gfps) // len(gfps)
        color = GREEN if value > 24 else RED
        text = "FPS: " + str(value)
        draw_text(window, (SCREEN_W // 2, SCREEN_H // 20), text, color)


def draw_intersection(intersector, second_segemnt):
    color = RED if intersects(intersector, second_segemnt) else WHITE
    draw.line(window, color, *intersector)
    draw.line(window, color, *second_segemnt)


def draw_obstacles(obstacles):
    for obstacle in obstacles:
        draw.polygon(window, BLACK, obstacle)


# @timer
def draw_light(lights):
    for light in lights:
        if CLOSEST_WALL and light.closest_wall is not None:
            pos = (int(light.closest_wall[0][0]), int(light.closest_wall[0][1]))
            draw.circle(window, GREEN, pos, 10)
            pos = (int(light.closest_wall[1][0]), int(light.closest_wall[1][1]))
            draw.circle(window, RED, pos, 10)

        if len(light.light_polygon) > 2:
            draw.polygon(window, light.color, light.light_polygon)

        # if light.active_walls:
        #     for w in light.active_walls:
        #         draw.line(window, RED, *w)

        if SHOW_RAYS:
            for r in light.rays:
                color = RED if light.rays.index(r) == 0 else WHITE
                draw.line(window, color, (r[0][0], r[0][1]), (r[1][0], r[1][1]))

    for light in lights:
        pygame.draw.circle(window, light.color, (light.x, light.y), 5)


def new_obstacle(i, j):
    """Produce obstacle (polygon) of any size and number of vertices."""
    obstacle = []
    for k in range(OBSTACLE_EDGES):
        angle = (k - 1) * (360 // OBSTACLE_EDGES)
        offset = 180 // OBSTACLE_EDGES
        point = move_along_vector((i, j), OBSTACLE_EDGE_SIZE, angle=angle-offset)
        obstacle.append(point)
    return obstacle


def create_obstacles():
    obstacles, bounding_boxes = [], []
    size = OBSTACLE_EDGE_SIZE
    for i in range(size*2, SCREEN_W, size*3):
        for j in range(size*2, SCREEN_H, size*3):
            obstacle = new_obstacle(i, j)
            obstacles.append(obstacle)
    return obstacles


def create_lights(obstacles):
    lights = []
    x, y = SCREEN_W // 2, SCREEN_H // 2
    randint = random.randint
    for i in range(LIGHTS_COUNT):
        if RANDOM_COLORS:
            color = (randint(0, 255), randint(0, 255), randint(0, 255))
        else:
            color = LIGHT
        if i == 0:
            point = (x, y)
        else:
            angle = (i) * (360 // LIGHTS_COUNT)
            point = move_along_vector((x, y), 10, angle=angle)
        light = Light(int(point[0]), int(point[1]), color, obstacles)
        lights.append(light)
    return lights


@timer
def update_lights(lights):
    for light in lights:
        light.update_visible_polygon()


def main_loop():
    run, drag_light = True, True
    obstacles = create_obstacles()
    lights = create_lights(obstacles)

    while run:
        redraw_screen(lights, obstacles)  # draw previous frame
        if drag_light:
            update_lights(lights)
        for event in pygame.event.get():
            event_type = event.type
            if event_type == pygame.MOUSEMOTION:
                if drag_light:
                    on_mouse_motion(*event.pos, lights)
            elif event_type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    drag_light = drag_or_drop(drag_light)
                    on_mouse_motion(*event.pos, lights)
                if event.button == 3:
                    print("Right mouse button!")
            elif event_type == pygame.QUIT:
                run = False
                pygame.quit()


def on_mouse_motion(x, y, lights):
    for i, light in enumerate(lights):
        if i == 0:
            light.move_to(x, y)
        else:
            angle = (i) * (360 // LIGHTS_COUNT)
            point = move_along_vector((x, y), 15, angle=angle)
            light.move_to(int(point[0]), int(point[1]))


def drag_or_drop(drag_light):
    return not drag_light


if __name__ == "__main__":
    # do not move these imports to the top!
    from geometry import Light, intersects, move_along_vector

    window = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(TITLE)
    main_loop()
