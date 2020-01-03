#!/usr/bin/env python
"""
Bunch of methods for 2-dimensional and 3-dimensional meshes calculations,
especially speeds, positions, paths and level-topography-handling.
"""

import math
from enum import Enum
from main import timer, SCREEN_H, SCREEN_W

SIGMA = 0.00001
UL, UR, LL, LR = "UL", "UR", "LL", "LR"
UPPER, LOWER, LEFT, RIGHT, DIAGONAL = "UPPER", "LOWER", "LEFT", "RIGHT", "DIAG"
VERTICALLY, HORIZONTALLY = "VERTICALLY", "HORIZONTALLY"


def distance_2d(coord_a: tuple or list, coord_b: tuple or list):
    """
    Calculate distance between two points_list in 2D space.

    :param coord_a: tuple -- (x, y) coords of first point
    :param coord_b: tuple -- (x, y) coords of second p
    :return: float -- 2-dimensional distance between points_list
    """
    side_x = abs(coord_a[0] - coord_b[0]) ** 2
    side_y = abs(coord_a[1] - coord_b[1]) ** 2
    return math.sqrt(side_x + side_y)


def close_enough(coord_a: tuple, coord_b: tuple, distance: float):
    """
    Calculate distance between two points_list in 2D space and find if distance
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


def quadrant(coordinates: tuple, center: tuple):
    """
    Check in which quadrant coordinates lie counted from upper-left to
    bottom-left (clockwise). Quadrants are placed by setting center point
    coordinate.

    :param coordinates: tuple -- coordinates of a point in format (x, y)
    :param center: tuple -- coordinates of center point of polygon
    :return: str -- name of quadrant ('UL', "UR', 'LL', "LR')
    """
    if coordinates[0] < center[0]:
        if coordinates[1] < center[1]:
            return Quadrant.UL
        else:
            return Quadrant.LL
    else:
        if coordinates[1] < center[1]:
            return Quadrant.UR
        else:
            return Quadrant.LR

    # if coordinates[0] < center[0] and coordinates[1] > center[1]:
    #     return Quadrant.UL
    # elif coordinates[0] < center[0] and coordinates[1] < center[1]:
    #     return Quadrant.LL
    # elif coordinates[0] > center[0] and coordinates[1] > center[1]:
    #     return Quadrant.UR
    # return Quadrant.LR


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
    angle between two points_list, but want quickly calculate position of the
    another point lying on the line connecting two, known points_list.

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


def get_intersection(p1, p2, p3, p4):
    """
    Relatively cheap method of finding segments-intersections.

    :param p1: tuple -- first point of first segment
    :param p2: tuple -- second point of first segment
    :param p3: tuple -- first point of second segment
    :param p4: tuple -- second point of second segment
    :return: tuple -- position of intersection
    """
    x_0 = (p1[1] - p3[1])
    x_1 = (p4[1] - p3[1])
    x_2 = (p1[0] - p3[0])
    x_3 = (p2[0] - p1[0])
    x_4 = (p2[1] - p1[1])
    x_5 = p4[0] - p3[0]

    s = ((x_5 * x_0 - x_1 * x_2) / (x_1 * x_3 - x_5 * x_4))
    return p1[0] + s * x_3, p1[1] + s * x_4


def cross_product(a, b):
    return a[0] * b[0] - b[1] * a[1]


def ccw(points_list):
    """
    Check if points from list are ordered counter-clockwise.

    :param points_list: list
    :return: bool
    """
    total = 0
    count = len(points_list)
    for i in range(count):
        a = points_list[i]
        b = points_list[(i + 1) % count]
        total += (b[0] - a[0]) * (b[1] + a[1])
    return total > 0


def get_bounding_box(segment):
    """
    Helper function for obtaining a bounding box of segment. Allows fast
    checking if two segments intersects. It is known that if bounding boxes
    of two segments do not intersect, segments do not intersect either.
    """
    box = [
        (min(segment[0][0], segment[1][0]), min(segment[0][1], segment[1][1])),
        (max(segment[0][0], segment[1][0]), max(segment[0][1], segment[1][1]))]
    return box


def intersects(a, b):
    """
    If segment_a is [A, B] and segment_b is [C, D] then segments intersects if
    [A, B, D] is clockwise and [A, B, C] is counter-clockwise, or vice versa.

    :param a: list of tuples -- points_list of first segment
    :param b: list of tuples -- points_list of second segment
    :return: bool
    """
    def do_boxes_intersect(a, b, c, d):
        return a[0] <= d[0] and b[0] >= c[0] and a[1] <= c[1] <= b[1]

    a, b, c, d = a[0], a[1], b[0], b[1]

    if are_points_in_line(a, b, c):
        return True

    if not do_boxes_intersect(*get_bounding_box((a, b)), *get_bounding_box((c, d))):
        return False

    return ccw((a, b, c)) != ccw((a, b, d)) and ccw((c, d, b)) != ccw((c, d, a))


def are_points_in_line(a, b, c):
    return calculate_angle(a, b) == calculate_angle(a, c) and distance_2d(a, b) >= distance_2d(a, c)


class Quadrant(Enum):
    UL = "upper_left"
    UR = "upper_right"
    LL = "lower_left"
    LR = "lower_right"


class Light:
    """
    Light is a point which represents a source of light or an observer in
    field-of-view simulation.
    """

    def __init__(self, x: int, y: int, obstacles: list):
        self.x = x
        self.y = y

        # objects considered as blocking FOV/light:
        self.obstacles = obstacles

        # our algorithm does not check against whole polygons-obstacles, but
        # against each of their edges:
        self.border_walls = self.screen_borders_to_walls()
        self.walls = self.border_walls + self.obstacles_to_walls()
        self.closest_wall = None
        # we need obstacle's corners to emit rays from origin to them:
        self.corners_open_walls = {}
        self.corners_close_walls = {}
        self.corners = self.find_corners()
        print(self.corners)

        self.rays = []

        self.light_polygon = []

    def move_to(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def screen_borders_to_walls():
        north_border = ((SCREEN_H, 0), (SCREEN_H, SCREEN_W))
        east_border = ((SCREEN_H, SCREEN_W), (0, SCREEN_W))
        south_border = ((0, SCREEN_W), (0, 0))
        west_border = ((0, 0), (SCREEN_H, 0))
        return north_border, east_border, south_border, west_border

    def obstacles_to_walls(self):
        """
        Each obstacle should be a polygon, which is a list of points_list
        represented by tuples (x, y) ordered counter-clockwise. We detect
        each pair of vertices which belong top same edge of polygon and add
        them as new wall which is later checked if it intersects with
        visibility rays.
        """
        walls = []
        for obstacle in self.obstacles:
            vertex_count = len(obstacle)

            for i in range(vertex_count):
                segment = [obstacle[i]]
                if i < vertex_count-1:
                    segment.append(obstacle[i + 1])
                else:
                    segment.append(obstacle[0])
                wall = tuple(segment)
                walls.append(wall)

        return tuple(walls)

    def find_corners(self):
        walls = self.walls
        corners = []

        for wall in walls:
            print(wall)
            for vertex in wall:
                if vertex not in corners:
                    corners.append(vertex)
                if wall.index(vertex) == 0:
                    self.corners_open_walls[vertex] = wall
                else:
                    self.corners_close_walls[vertex] = wall
        return corners

    @timer
    def update_visible_polygon(self):
        """
        Field of view or lit area is represented by polygon which is basically
        a list of points_list. Each frame list is updated accordingly to the
        position of the Light
        """
        origin = (self.x, self.y)  # point from which we will shot rays

        corners = self.corners[::]

        # order corners in clockwise order by angle to the origin:
        corners.sort(key=lambda c: calculate_angle(origin, c))

        walls = [w for w in self.walls]
        # sorting walls according to their distance to origin allows for
        # faster finding rays intersections and avoiding iterating through
        # whole list of the walls:
        walls.sort(key=lambda w: distance_2d(origin, w[0]) + distance_2d(origin, w[1]))
        self.closest_wall = walls[0]

        rays = self.cast_rays_to_corners(origin, corners, walls)
        print(f"Number of rays: {len(rays)}")

        corners_open_walls = self.corners_open_walls
        corners_close_walls = self.corners_close_walls
        colliding = set()  # rays which intersects any wall
        offset_rays = []

        for ray in rays:
            ending = ray[1]
            if ending in corners:  # check if it is ray shot at obstacle corner
                ray_opens = corners_open_walls[ending]
                ray_closes = corners_close_walls[ending]
                both_walls = {ray_opens, ray_closes}
            else:
                both_walls = None

            for wall in walls:
                if intersects(ray, wall) or intersects(wall, ray):
                    if both_walls is None:  # additional around-corner ray
                        colliding.add(ray)
                        new_ray_end = get_intersection(*ray, *wall)
                        offset_rays.append((origin, new_ray_end))
                    elif wall not in both_walls:
                        colliding.add(ray)
                    break

        rays = [r for r in rays if r not in colliding] + offset_rays
        # need to sort rays by their ending angle agin because offset_rays
        # unsorted and pushed at the end of the list:
        rays.sort(key=lambda r: calculate_angle(origin, r[1]))
        self.rays = rays
        print(f"Number of rays: {len(self.rays)}")

        # finally, we build a visibility polygon using endpoint of each ray:
        self.light_polygon = [r[1] for r in rays]

    def cast_rays_to_corners(self, origin, corners, walls):
        """
        Create a 'ray' connecting origin with each corner (obstacle vertex) on
        the screen. Ray is a tuple of two (x, y) coordinates used later to
        find which segment obstructs visibility.
        TODO: find way to emit less offset rays [ ][ ]
        :param walls: list
        :param origin: tuple
        :param corners: list
        :return: list
        """
        rays = []
        border_walls = self.border_walls
        # walls = [w for w in walls if w not in border_walls]
        corners_open_walls = self.corners_open_walls
        corners_close_walls = self.corners_close_walls

        for corner in corners:
            angle = calculate_angle(origin, corner)
            ray = (origin, corner)
            new_rays = [ray]
            begins, ends = corners_open_walls[corner], corners_close_walls[corner]

            # additional rays to search behind the corners:
            end_a = move_along_vector(origin, 1500, angle=-angle + SIGMA)
            end_b = move_along_vector(origin, 1500, angle=-angle - SIGMA)
            offset_ray_a, offset_ray_b = None, None

            if ccw((origin, corner, begins[1])):
                offset_ray_a = (origin, end_b)
            if not ccw((origin, corner, ends[0])):
                offset_ray_b = (origin, end_a)

            if offset_ray_a is not None:
                new_rays.insert(0, offset_ray_a)
            if offset_ray_b is not None:
                new_rays.append(offset_ray_b)

            rays.extend(new_rays)

        return rays
