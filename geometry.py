#!/usr/bin/env python
"""
Bunch of methods for 2-dimensional and 3-dimensional meshes calculations,
especially speeds, positions, paths and level-topography-handling.
"""

import math

from enum import Enum
from shapely import speedups
from shapely.geometry import Point, LineString, Polygon
from arcade import check_for_collision
from main import SCREEN_W, SCREEN_H, Obstacle

UL, UR, LL, LR = "UL", "UR", "LL", "LR"
UPPER, LOWER, LEFT, RIGHT, DIAGONAL = "UPPER", "LOWER", "LEFT", "RIGHT", "DIAG"
VERTICALLY, HORIZONTALLY = "VERTICALLY", "HORIZONTALLY"
view_left, view_bottom = 0, 0

nodes = {}
obstacles = []
meshes = {}

speedups.enable()


class Quadrant(Enum):
    UL = "upper_left"
    UR = "upper_right"
    LL = "lower_left"
    LR = "lower_right"


def visible(position_a: tuple,
            position_b: tuple,
            obstacles_: list,
            for_lighting: bool = False):
    """
    Check if position_a is 'visible' from position_b and vice-versa. 'Visible'
    means, that you can connect both points with straight line without
    intersecting any obstacle.

    :param position_a: tuple -- coordinates of first position (x, y)
    :param position_b: tuple -- coordinates of second position (x, y)
    :param obstacles_: list -- Obstacle objects to check against
    :param for_lighting: bool -- use this only with calls from 'lighting'
    module
    :return: tuple -- (bool, list)
    """
    line = LineString([position_a, position_b])
    if for_lighting:
        if isinstance(obstacles_[0], LineString):
            visible_ = [line.crosses(line) for line in obstacles_]
        else:  # checking against Polygons:
            visible_ = [Polygon(o.points).crosses(line) for o in obstacles_]
        return not any(visible_)
    if isinstance(obstacles_[0], LineString):
        visible_ = [line.crosses(line) for line in obstacles_]
    else:
        visible_ = [Polygon(o.points).crosses(line) for o in obstacles_]
    return not any(visible_)


def all_visible_from(position: tuple,
                     to_check: tuple,
                     obstacles_: list,
                     for_lighting: bool = False):
    """
    Check if for this position, all positions enumarated in "to_check" list,
    are 'visible". It just iteratively calls visible() function above for each
    element of 'to_check' list.

    :param position: tuple -- postion from visibility check is executed
    :param to_check: list -- list of coordinates to check visibility
    :param obstacles_: list -- all obstacles to be taken for account
    :param for_lighting: bool -- use this only with calls from 'lighting'
    module
    :return: tuple: (bool, list) -- bool says if all coords from
    'to_check' are visible from 'position' and list contains all elements
    which passed the test
    """
    visible_list = [t for t in to_check if visible(position, t, obstacles_,
                                                   for_lighting)]
    return len(visible_list) == len(to_check), visible_list


def distance_2d(coord_a: tuple or list, coord_b: tuple or list):
    """
    Calculate distance between two points in 2D space.

    :param coord_a: tuple -- (x, y) coords of first point
    :param coord_b: tuple -- (x, y) coords of second p
    :return: float -- 2-dimensional distance between points
    """
    side_x = abs(coord_a[0] - coord_b[0]) ** 2
    side_y = abs(coord_a[1] - coord_b[1]) ** 2
    return math.sqrt(side_x + side_y)


def close_enough(coord_a: tuple, coord_b: tuple, distance: float):
    """
    Calculate distance between two points in 2D space and find if distance
    is less than minimum distance.

    :param coord_a: tuple -- (x, y) coords of first point
    :param coord_b: tuple -- (x, y) coords of second point
    :param distance: float -- minimal distance to check against
    :return: bool -- if distance is less than
    """
    return distance_2d(coord_a, coord_b) <= distance


def calculate_vector_2d(angle: float, scalar: float):
    """
    Calculate x and y parts of the current vector.

    :param angle: float -- angle of the vector
    :param scalar: float -- scalar value of the vector (e.g. speed)
    :return: tuple -- x and y parts of the vector in format: (float, float)
    """
    radians = math.radians(angle)
    change_y = math.cos(radians)
    change_x = math.sin(radians)
    return change_x * scalar, change_y * scalar


def calculate_angle(start: tuple, end: tuple):
    """
    Calculate angle in direction from 'start' to the 'end' point in degrees.

    :param start: tuple -- start point coordinates (x, y)
    :param end: tuple -- end point coordinates (x, y)
    :return: float -- degrees in range 0-360.
    """
    radians = -math.atan2(end[0] - start[0], end[1] - start[1])
    return math.degrees(radians) % 360


def half(coords_a: tuple, coords_b: tuple, center: tuple):
    """
    Find if both coordinates lie in the same half of space (left, right,
    upper or bottom). Halves are placed by setting center point coordinate.

    :return: str -- name of the shared half of space
    """
    if coords_a[0] < center[0] and coords_b[0] < center[0]: return LEFT
    if coords_a[0] > center[0] and coords_b[0] > center[0]: return RIGHT
    if coords_a[1] < center[1] and coords_b[1] < center[1]: return LOWER
    if coords_a[1] > center[1] and coords_b[1] > center[1]: return UPPER
    return DIAGONAL


def quadrant(coordinates: tuple, center: tuple):
    """
    Check in which quadrant coordinates lie counted from upper-left to
    bottom-left (clockwise). Quadrants are placed by setting center point
    coordinate.

    :param coordinates: tuple -- coordinates of a point in format (x, y)
    :param center: tuple -- coordinates of center point of polygon
    :return: str -- name of quadrant ('UL', "UR', 'LL', "LR')
    """
    if coordinates[0] < center[0] and coordinates[1] > center[1]:
        return Quadrant.UL
    elif coordinates[0] < center[0] and coordinates[1] < center[1]:
        return Quadrant.LL
    elif coordinates[0] > center[0] and coordinates[1] > center[1]:
        return Quadrant.UR
    return Quadrant.LR


def is_position_inside_area(coordinates: tuple or list, area: tuple or list):
    """
    Check if provided point (x, y) is located inside of the provided area
    (polygon made of points).

    :param coordinates: tuple -- (x, y) coords of the point\
    :param area: tuple of tuples -- array of coordinates (x, y) bounding area
    :return: bool -- if point lies inside area
    """
    return Polygon(area).covers(Point(coordinates))


def is_object_on_screen(id_: int = None, points: tuple = None):
    """
    Check if object identified by id_ parameter in meshes dict or just a
    Polygon made of points tuple provided, lies in boundaries of the screen
    or out of it.

    :param id_: int -- id attribute of Obstacle instance
    :param points: tuple -- list of points to build Polygon from
    :return: bool -- if object lies inside the screen
    """
    screen_points = [
        (view_left, view_bottom),
        (view_left, view_bottom + SCREEN_H),
        (view_left + SCREEN_W, view_bottom + SCREEN_H),
        (view_left + SCREEN_W, view_bottom)
        ]
    screen = Polygon(screen_points)
    if id_ is not None:
        return screen.intersects(meshes[id_])
    return screen.intersects(Polygon(points))


def add_to_level_geometry(obstacle: Obstacle):
    """
    Add new geometric representation of Obstacle to the meshes hashtable.
    Each element in dict is hashable with it's 'id'.

    :param obstacle: Obstacle -- instance of Obstacle class spawned in game
    """
    if obstacle.id not in meshes:
        obstacles.append(obstacle)
        meshes[obstacle.id] = Polygon(obstacle.points)


def update_in_level_geometry(obstacle: Obstacle):
    """
    Updates position and angle of polygon in meshes. Call it when
    Obstacle changed it's position or angle in game.
    """
    meshes[obstacle.id] = Polygon(obstacle.points)


def remove_from_level_geometry(obstacle: Obstacle):
    """
    Remove Obstacle instance from meshes dict.

    :param obstacle: Obstacle -- object to be removed
    """
    if obstacle.id in meshes:
        del meshes[obstacle.id]


def update_screen_coordinates(left: float, bottom: float):
    """
    Change internal screen-boundaries, to properly detect what part of
    level we are. Viewport is updated in main.game, but meshes must be
    updated too.
    """
    global view_left, view_bottom
    view_left, view_bottom = left, bottom


def detect_all_screen_collisions(this, others):
    """
    Check if Sprite or Cursor object collides with any other Sprite and
    return list of colliding sprites or None.

    :param this: Sprite -- sprite we need to know if collides with anything
    :param others: LayeredSpriteList -- list of other sprites to check against
    :return: None or list -- list of Sprites 'this' collides with
    """
    # we need only to check collisions with objects visible on the screen:
    potential = [x for x in others if x.on_screen()]

    if not potential:
        return

    return [other for other in potential if check_for_collision(this, other)]


def detect_collision_on_screen(this, others, cursor):
    """
    Check if Sprite or Cursor object collides with any other Sprite and
    return first colliding Sprite as a result (usually faster than above).

    :param this: Sprite -- sprite we need to know if collides with anything
    :param others: LayeredSpriteList -- list of other sprites to check against
    :param cursor: bool -- if object against which check is m ade is a cursor
    :return: None or Sprite -- Sprite that 'this' collides with
    """
    # we need only to check collisions with objects visible on the screen:
    potential = [x for x in others if x.on_screen()]

    if not potential:
        return

    for other in potential:
        if check_for_collision(this, other):
            return other


def move_along_vector(start: tuple,
                      velocity: float,
                      target: tuple = None,
                      angle: float = None,
                      ):
    """
    Create movement vector starting at 'start' point angled in direction of
    'target' point with scalar velocity 'velocity'. Optionally, instead of
    'target' position, you can pass starting 'angle' of the vector.

    Use 'target' position only, when you now the point and do not know the
    angle between two points, but want quickly calculate position of the
    another point lying on the line connecting two, known points.

    :param start: tuple -- point from vector starts
    :param target: tuple -- target that vector 'looks at'
    :param velocity: float -- scalar length of the vector
    :param angle: float -- angle of the vector direction
    :return: tuple -- (optional)position of the vector end
    """
    p1 = (start[0], start[1])
    if target:
        p2 = (target[0], target[1])
        rad = math.atan2(p2[0] - p1[0], p2[1] - p1[1])
        angle = math.degrees(rad)
    if target is None and angle is None:
        raise ValueError("You MUST pass target position or vector angle!")

    v = calculate_vector_2d(angle, velocity)

    return p1[0] + v[0], p1[1] + v[1]
