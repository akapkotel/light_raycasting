#!/usr/bin/env python
"""
See README.md file.
"""
import time
import random

import pygame
import pygame.freetype

from functools import wraps


from options_screen import Button, ClampedValue, WHITE, BLACK, GREY, \
    GREEN


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
OBSTACLE_EDGES = 8
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
SUN = (100, 150, 100)
DARK = (32, 32, 32)
LIGHT = (192, 192, 192)
SHADOW = (240, 240, 240)

get_time = time.perf_counter
draw = pygame.draw
draw_line = draw.line
draw_circle = draw.circle
draw_polygon = draw.polygon
draw_text = FONT.render_to


gfps = []
interactables = []
run_simulation = False


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
            global gfps
            if len(gfps) == 10:
                gfps.pop(0)
            gfps.append(fps)

        fr = f"{func.__name__} finished in {total_time:.4f} secs. FPS: {fps}"
        print(fr)
        return result
    return wrapper


def main_loop():
    global run_simulation
    create_interactable_options()
    pointed = None

    while not run_simulation:
        redraw_configuration_screen(interactables)
        for event in pygame.event.get():
            event_type = event.type
            if event_type == pygame.MOUSEMOTION:
                pointed = if_mouse_over_interactable(*event.pos, interactables)
            elif event_type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # mouse left button
                    if pointed is not None:
                        pointed.on_click()
            elif event_type == pygame.QUIT:
                pygame.quit()

    bind_light_to_cursor = True
    obstacles = create_obstacles()
    lights = create_lights(obstacles)
    while run_simulation:
        redraw_screen(lights, obstacles)  # draw previous frame
        if bind_light_to_cursor:
            update_lights(lights)
        for event in pygame.event.get():
            event_type = event.type
            if event_type == pygame.MOUSEMOTION and bind_light_to_cursor:
                on_mouse_motion(*event.pos, lights)
            elif event_type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # mouse left button
                    bind_light_to_cursor = drag_or_drop(bind_light_to_cursor)
                    on_mouse_motion(*event.pos, lights)
            elif event_type == pygame.QUIT:
                run_simulation = False
                pygame.quit()


def create_obstacles(vertices=OBSTACLE_EDGES):
    obstacles, bounding_boxes = [], []
    size = OBSTACLE_EDGE_SIZE
    for i in range(size*2, SCREEN_W, size*3):
        for j in range(size*2, SCREEN_H, size*3):
            obstacle = new_obstacle(i, j)
            obstacles.append(obstacle)
    return obstacles


def new_obstacle(i, j):
    """Produce obstacle (polygon) of any size and number of vertices."""
    obstacle = []
    size = OBSTACLE_EDGE_SIZE
    edges = OBSTACLE_EDGES
    for k in range(edges):
        angle = (k - 1) * (360 // edges)
        offset = 180 // edges
        point = move_along_vector((i, j), size, angle=angle-offset)
        obstacle.append(point)
    return obstacle


@timer
def update_lights(lights):
    for light in lights:
        light.update_visible_polygon()


def create_lights(obstacles):
    lights = []
    x, y = SCREEN_W // 2, SCREEN_H // 2
    for i in range(LIGHTS_COUNT):
        color = get_light_color()
        point = get_light_position(i, x, y)
        # noinspection PyTypeChecker
        light = Light(*point, color, obstacles)
        lights.append(light)
    return lights


def get_light_color():
    if RANDOM_COLORS:
        randint = random.randint
        return randint(0, 255), randint(0, 255), randint(0, 255)
    else:
        return LIGHT


def get_light_position(i, x, y):
    if not i:
        point = (x, y)
    else:
        angle = i * (360 // LIGHTS_COUNT)
        point = move_along_vector((x, y), 10, angle=angle)
    return point


def create_interactable_options():
    global interactables
    p = (SCREEN_H / 2, SCREEN_W / 2)  # basic position to override
    positions = [(p[0] + 300, p[1]), (p[0], p[1] - 100), (p[0], p[1] - 200)]
    types = [Button, ClampedValue, ClampedValue]
    functions = [run_application, change_edges_count, change_edge_size]
    ranges = [None, (3, 20, 1), (25, 200, 25)]
    values = ["Run", 5, 100]
    labels = [None, "Edges:", "Size:"]
    for i, position in enumerate(positions):
        if types[i] == ClampedValue:
            min, max, step = ranges[i]
            # noinspection PyTypeChecker
            b = types[i](window, *position, 25, 25, values[i], min, max,
                         step, functions[i], labels[i])
        else:
            # noinspection PyTypeChecker
            b = types[i](window, *position, 25, 25, values[i], functions[i])
        interactables.append(b)


def run_application():
    global run_simulation
    run_simulation = True


def change_edges_count():
    global interactables, OBSTACLE_EDGES
    OBSTACLE_EDGES = interactables[1].value


def change_edge_size():
    global OBSTACLE_EDGE_SIZE
    OBSTACLE_EDGE_SIZE = interactables[2].value


def redraw_configuration_screen(interactables: list):
    """
    Draw configuration screen, where user can set-up key variables of the
    simulation.
    """
    window.fill(DARK)
    # visual representation of obstacle shape:
    poly = new_obstacle(SCREEN_W // 2, SCREEN_H - 300)
    draw_polygon(window, WHITE, poly)

    for interactable in interactables:
        interactable.draw()
    pygame.display.update()


def if_mouse_over_interactable(x, y, interactables: list):
    pointed = None
    for interactable in interactables:
        if interactable.mouse_over(x, y):
            interactable.active = True
            return interactable
    else:
        for interactable in interactables:
            interactable.active = False
    return pointed


# @timer
def redraw_screen(lights, obstacles):
    window.fill(DARK)
    draw_obstacles(obstacles)
    draw_light(lights)
    if gfps:
        draw_fps_counter()
    pygame.display.update()


def draw_fps_counter():
    value = sum(gfps) // len(gfps)
    color = GREEN if value > 24 else RED
    text = "FPS: " + str(value)
    draw_text(window, (SCREEN_W // 2, SCREEN_H // 20), text, color)


def draw_intersection(intersector, second_segemnt):
    color = RED if intersects(intersector, second_segemnt) else WHITE
    draw_line(window, color, *intersector)
    draw_line(window, color, *second_segemnt)


def draw_obstacles(obstacles):
    for obstacle in obstacles:
        draw_polygon(window, BLACK, obstacle)


# @timer
def draw_light(lights):
    for light in lights:
        closest_wall = light.closest_wall
        if CLOSEST_WALL and closest_wall is not None:
            pos = (int(closest_wall[0][0]), int(closest_wall[0][1]))
            draw_circle(window, GREEN, pos, 5)
            pos = (int(closest_wall[1][0]), int(closest_wall[1][1]))
            draw_circle(window, RED, pos, 5)

        if len(light.light_polygon) > 2:
            draw_polygon(window, light.color, light.light_polygon)

        x, y = light.origin
        polygon = light.light_polygon
        if SHOW_RAYS:
            for i, r in enumerate(polygon):
                color = WHITE if i else RED
                draw_line(window, color, (x, y), (r[0], r[1]))

        draw_circle(window, light.color, (int(x), int(y)), 5)


def on_mouse_motion(x, y, lights):
    lights[0].move_to(x, y)
    if len(lights) > 1:
        for i, light in enumerate(lights):
            if i:
                angle = i * (360 // LIGHTS_COUNT)
                point = move_along_vector((int(x), int(y)), 15, angle=angle)
                light.move_to(point[0], point[1])


def drag_or_drop(drag_light):
    return not drag_light


if __name__ == "__main__":
    # do not move these imports to the top!
    from geometry import Light, intersects, move_along_vector

    window = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(TITLE)
    main_loop()
