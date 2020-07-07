#!/usr/bin/env python
"""
Bunch of methods for 2-dimensional and 3-dimensional meshes calculations,
especially speeds, positions, paths and level-topography-handling.

TODO: fix issue #1 with case when obstacles are triangles and two top-vertices
of obstacles and origin are placed in-line horizontally - the top vertex of
closer triangle is omitted and an obstacle is cut.
"""

import math
from typing import List, Tuple, Sequence, Dict, Optional, Iterator

from main import SCREEN_H, SCREEN_W

EPSILON = 0.05
degrees = math.degrees
hypotenuse = math.hypot


def distance(coord_a: Tuple, coord_b: Tuple) -> float:
    """
    Calculate distance between two points in 2D space.

    :param coord_a: Tuple -- (x, y) coords of first point
    :param coord_b: Tuple -- (x, y) coords of second p
    :return: float -- 2-dimensional distance between segment
    """
    return hypotenuse(coord_b[0] - coord_a[0], coord_b[1] - coord_a[1])


def calculate_vector_2d(angle: float, scalar: float) -> Tuple[float, float]:
    """
    Calculate x and y parts of the current vector.

    :param angle: float -- angle of the vector
    :param scalar: float -- scalar value of the vector (e.g. speed)
    :return: Tuple -- x and y parts of the vector in format: (float, float)
    """
    radians = math.radians(angle)
    change_y = math.cos(radians)
    change_x = math.sin(radians)
    return change_x * scalar, change_y * scalar


def calculate_angle(start: Tuple, end: Tuple) -> float:
    """
    Calculate angle in direction from 'start' to the 'end' point in degrees.

    :param start: Tuple[float, float] -- start point coordinates (x, y)
    :param end: Tuple[float, float] -- end point coordinates (x, y)
    :return: float -- degrees in range 0-360.
    """
    radians = -math.atan2(end[0] - start[0], end[1] - start[1])
    return degrees(radians)


def move_along_vector(start: Tuple[float, float],
                      velocity: float,
                      target: Optional[Tuple[float, float]] = None,
                      angle: Optional[float] = None) -> Tuple[float, float]:
    """
    Create movement vector starting at 'start' point angled in direction of
    'target' point with scalar velocity 'velocity'. Optionally, instead of
    'target' position, you can pass starting 'angle' of the vector.

    Use 'target' position only, when you now the point and do not know the
    angle between two segment, but want quickly calculate position of the
    another point lying on the line connecting two, known segment.

    :param start: Tuple[float, float] -- point from vector starts
    :param target: Optional[Tuple[float, float] -- target the vector 'looks at'
    :param velocity: float -- scalar length of the vector
    :param angle: Optional[float] -- angle of the vector direction
    :return: Tuple[float, float] -- (optional)position of the vector end
    """
    p1 = (start[0], start[1])
    if target:
        p2 = (target[0], target[1])
        # rad = -math.atan2(p2[0] - p1[0], p2[1] - p1[1])
        # angle = degrees(rad) % 360
        angle = calculate_angle(p1, p2)
    if target is None and angle is None:
        raise ValueError("You MUST pass target position or vector angle!")

    v = calculate_vector_2d(angle, velocity)

    return p1[0] + v[0], p1[1] + v[1]


def get_intersection(p1: Tuple[float, float],
                     p2: Tuple[float, float],
                     p3: Tuple[float, float],
                     p4: Tuple[float, float]) -> Tuple[float, float]:
    """
    Relatively cheap method of finding segments-intersections.

    :param p1: Tuple[float, float] -- first point of first segment
    :param p2: Tuple[float, float] -- second point of first segment
    :param p3: Tuple[float, float] -- first point of second segment
    :param p4: Tuple[float, float] -- second point of second segment
    :return: Tuple[float, float] -- position of intersection
    """
    x_0 = (p1[1] - p3[1])
    x_1 = (p4[1] - p3[1])
    x_2 = (p1[0] - p3[0])
    x_3 = (p2[0] - p1[0])
    x_4 = (p2[1] - p1[1])
    x_5 = p4[0] - p3[0]

    s = ((x_5 * x_0 - x_1 * x_2) / (x_1 * x_3 - x_5 * x_4))
    return p1[0] + s * x_3, p1[1] + s * x_4


def cross_product(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return a[0] * b[0] - b[1] * a[1]


def ccw(points_list: Sequence[Tuple[float]]) -> bool:
    """
    Check if sequence of points is oriented in clockwise or counterclockwise
    order.
    """
    a, b, c = points_list[0], points_list[1], points_list[2]
    val = (b[1] - a[1]) * (c[0] - b[0]) - (b[0] - a[0]) * (c[1] - b[1])
    return val > 0


def are_points_in_line(a: Tuple[float, float],
                       b: Tuple[float, float],
                       c: Tuple[float, float]):
    return -EPSILON < (
            distance(a, c) + distance(c, b) - distance(a, b)) < EPSILON


def get_polygon_bounding_box(points_list: List[Tuple]) -> List[Tuple]:
    """
    Helper function for obtaining a bounding box of segment. Allows fast
    checking if two polygons intersects. It is known that if bounding boxes
    of two polygons do not intersect, polygons do not intersect either.
    """
    box = [
        (min([p[0] for p in points_list]), min([p[1] for p in points_list])),
        (max([p[0] for p in points_list]), max([p[1] for p in points_list]))
        ]
    return box


def get_segment_bounding_box(segment: Sequence[Tuple]) -> List[Tuple]:
    """
    Helper function for obtaining a bounding box of segment. Allows fast
    checking if two segments intersects.

    :param segment: List
    return: Tuple of tuples
    """
    box = [
        (min(segment[0][0], segment[1][0]), min(segment[0][1], segment[1][1])),
        (max(segment[0][0], segment[1][0]), max(segment[0][1], segment[1][1]))
        ]
    return box


def do_boxes_intersect(a: Tuple[float, float],
                       b: Tuple[float, float],
                       c: Tuple[float, float],
                       d: Tuple[float, float]) -> bool:
    """
    It is known that if bounding boxes
    of two segments do not intersect, segments do not intersect either.
    """
    return a[0] <= d[0] and b[0] >= c[0] and a[1] <= c[1] <= b[1]


def intersects(segment_a: Sequence[Tuple[float, float]],
               segment_b: Sequence[Tuple[float, float]]) -> bool:
    """
    If segment_a is [A, B] and segment_b is [C, D] then segments intersects if
    [A, B, D] is clockwise and [A, B, C] is counter-clockwise, or vice versa.

    :param segment_a: List of tuples -- segment of first segment
    :param segment_b: List of tuples -- segment of second segment
    :return: bool
    """
    a, b = segment_a
    c, d = segment_b

    if are_points_in_line(a, b, c):
        return True

    bounding_box_a = get_segment_bounding_box((a, b))
    bounding_box_b = get_segment_bounding_box((c, d))
    if not do_boxes_intersect(*bounding_box_a, *bounding_box_b):
        return False

    ccw_abc = ccw((a, b, c))
    ccw_abd = ccw((a, b, d))
    ccw_cdb = ccw((c, d, b))
    ccw_cda = ccw((c, d, a))

    return ccw_abc != ccw_abd and ccw_cdb != ccw_cda


class Light:
    """
    Light is a point which represents a source of light or an observer in
    field-of-view simulation.
    """

    def __init__(self, x: int, y: int, color: Tuple, obstacles: List):
        self.origin = x, y  # position of the light/observer
        self.color = color

        # objects considered as blocking FOV/light. Each obstacle is a
        # polygon consisting a list of points - it's vertices.
        self.obstacles = obstacles

        # our algorithm does not check against whole polygons-obstacles, but
        # against each of their edges:
        self.border_walls = self.screen_borders_to_walls()
        self.walls = self.border_walls + self.obstacles_to_walls()
        self.walls_centers = self.calculate_walls_centers()

        # we need obstacle's corners to emit rays from origin to them:
        self.corners_open_walls = {}
        self.corners_close_walls = {}
        self.corners = self.find_corners()
        self.border_corners = self.get_border_corners()

        # this would be used to draw our visible/lit-up area:
        self.light_polygon = []

    def move_to(self, x, y):
        self.origin = x, y

    @staticmethod
    def screen_borders_to_walls() -> Tuple:
        """
        Screen-borders are outermost boundaries of our visibility-light
        polygon. No ray could surpass them.

        :return: Tuple
        """
        north_border = ((SCREEN_H, 0), (SCREEN_H, SCREEN_W))
        east_border = ((SCREEN_H, SCREEN_W), (0, SCREEN_W))
        south_border = ((0, SCREEN_W), (0, 0))
        west_border = ((0, 0), (SCREEN_H, 0))
        return north_border, east_border, south_border, west_border

    def obstacles_to_walls(self) -> Tuple:
        """
        Each obstacle should be a polygon, which is a list of segments
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
                if i < vertex_count - 1:
                    segment.append(obstacle[i + 1])
                else:
                    segment.append(obstacle[0])
                wall = tuple(segment)
                walls.append(wall)
        return tuple(walls)

    def find_corners(self) -> List:
        walls = self.walls
        corners = []

        for wall in walls:
            for vertex in wall:
                if vertex not in corners:
                    corners.append(vertex)
                if wall.index(vertex) == 0:
                    self.corners_open_walls[vertex] = wall
                else:
                    self.corners_close_walls[vertex] = wall
        return corners

    @staticmethod
    def get_border_corners() -> Tuple:
        return (SCREEN_H, 0), (SCREEN_H, SCREEN_W), (0, SCREEN_W), (0, 0)

    def calculate_walls_centers(self) -> Dict:
        centers = {}

        for wall in self.walls + self.border_walls:
            half_length = distance(*wall) / 2
            direction = calculate_angle(*wall)
            center = move_along_vector(wall[0], half_length, angle=-direction)
            centers[wall] = center
        return centers

    def update_visible_polygon(self):
        """
        Field of view or lit area is represented by polygon which is basically
        a list of points. Each frame list is updated accordingly to the
        position of the Light
        """
        origin = self.origin  # point from which we will shot rays
        corners = self.corners[::]
        corners.sort(key=lambda c: calculate_angle(origin, c))
        walls = self.sort_walls(origin)
        rays = self.create_rays_for_corners(origin, corners)
        rays = self.collide_rays_w_walls(corners, origin, rays, walls)
        # need to sort rays by their ending angle again because offset_rays
        # are unsorted and pushed at the end of the list:
        rays.sort(key=lambda r: calculate_angle(origin, r[1]))
        # finally, we build a visibility polygon using endpoint of each ray:
        self.light_polygon = [r[1] for r in rays]

    def sort_walls(self, origin: Tuple) -> List[Tuple[float, float]]:
        """
        Return wals sorted according to distance to origin and without walls
        which could not be seen/lit up since they are behind some, closer
        walls.
        :param origin: Tuple -- (x, y) location of light
        :return: List -- sorted walls without redundant walls
        """
        walls = [w for w in self.walls]
        # sorting walls according to their distance to origin allows for
        # faster finding rays intersections and avoiding iterating through
        # whole list of the walls:
        centers = self.walls_centers
        walls.sort(key=lambda w: distance(origin, centers[w]))
        # to avoid issue with border-walls when wall-rays are preceding
        # obstacle-rays:
        walls.sort(key=lambda w: w in self.border_walls)
        return walls

    def collide_rays_w_walls(self, corners: List[Tuple],
                             origin: Tuple[float, float],
                             rays: List[Tuple],
                             walls: List[Tuple]) -> List[Tuple]:
        """
        Test for intersections of each ray and each wall of each obstacle to
        build final polygon representing our visible/lit-up area.

        :param corners: set -- vertices of all obstacles
        :param origin: Tuple -- (x, y) position of light/observer
        :param rays: List -- all rays emitted from origin to corners
        :param walls: List -- all walls which can block vision/light
        :return: List -- clockwise-ordered points of visibility polygon
        """
        colliding = set()  # rays which intersects any wall
        offset_rays = []  # rays sweeping around obstacle's corners
        corners_open_walls = self.corners_open_walls
        corners_close_walls = self.corners_close_walls
        for wall in walls:
            for ray in self.filter_rays(origin, rays, wall):
                if ray in colliding:
                    continue
                ray_end_point = ray[1]
                # check if it is ray shot at obstacle corner:
                both_walls = None
                if ray_end_point in corners:
                    ray_opens = corners_open_walls[ray_end_point]
                    ray_closes = corners_close_walls[ray_end_point]
                    both_walls = {ray_opens, ray_closes}

                if intersects(ray, wall) or intersects(wall, ray):
                    if both_walls is None:  # it's additional around-corner ray
                        colliding.add(ray)
                        new_ray_end = get_intersection(*ray, *wall)
                        offset_rays.append((origin, new_ray_end))
                    elif wall not in both_walls:
                        colliding.add(ray)
        return [r for r in rays if r not in colliding] + offset_rays

    @staticmethod
    def filter_rays(origin: Tuple, rays: List, wall: Tuple) -> Iterator:
        """
        Find rays which could intersect with this wall, eg.: orientation of
        their ending to wall starting vertex is clockwise and to ending
        vertex is counterclockwise.

        :param origin: Tuple -- light source
        :param rays: List -- all emitted rays
        :param wall: Tuple -- current wall to test against
        :return: Iterator -- filter object (filtered rays)
        """
        return filter(lambda r: ccw((origin, wall[1], r[1])) and
                      not ccw((origin, wall[0], r[1])), rays)

    def create_rays_for_corners(self, origin: Tuple, corners: List) -> List:
        """
        Create a 'ray' connecting origin with each corner (obstacle vertex) on
        the screen. Ray is a tuple of two (x, y) coordinates used later to
        find which segment obstructs visibility.
        TODO: find way to emit less offset rays [x][ ]
        :param origin: Tuple -- point from which 'light' is emitted
        :param corners: List -- vertices of obstacles
        :return: List -- rays to be tested against obstacles edges
        """
        corners_open_walls = self.corners_open_walls
        corners_close_walls = self.corners_close_walls
        border_corners = self.border_corners

        rays = []
        excluded = set()
        angles = [calculate_angle(origin, corner) for corner in corners]
        distances = [distance(origin, corner) for corner in corners]
        for i, corner in enumerate(corners):
            if corner in excluded:
                continue

            if corner in border_corners:
                rays.append((origin, corner))
                continue

            angle = angles[i]
            max_distance = distances[i]

            corner_starts_wall = corners_open_walls[corner]
            corner_ends_wall = corners_close_walls[corner]
            if ccw((origin, *corner_starts_wall)):
                max_angle = angle
            else:
                max_angle = calculate_angle(origin, corner_starts_wall[1])
            if ccw((origin, corner_ends_wall[1], corner_ends_wall[0])):
                min_angle = calculate_angle(origin, corner_ends_wall[0])
            else:
                min_angle = angle

            for j, another_corner in enumerate(corners):
                if distances[j] > max_distance:
                    another_angle = angles[j]
                    if min_angle < another_angle < max_angle:
                        excluded.add(another_corner)
                    elif min_angle > max_angle:
                        if min_angle < another_angle < 360:
                            excluded.add(another_corner)

            # additional rays to search behind the corners:
            end_a = move_along_vector(origin, 1500,
                                      angle=-angle + EPSILON)
            end_b = move_along_vector(origin, 1500,
                                      angle=-angle - EPSILON)
            offset_ray_a, offset_ray_b = None, None

            if ccw((origin, corner, corner_starts_wall[1])):
                offset_ray_a = (origin, end_b)
            if not ccw((origin, corner, corner_ends_wall[0])):
                offset_ray_b = (origin, end_a)

            for r in (offset_ray_a, (origin, corner), offset_ray_b):
                if r is not None:
                    rays.append(r)
        return rays
