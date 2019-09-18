#!/usr/bin/env python
"""

"""
import os
import random
import arcade

import geometry as g
from datetime import datetime  # for measuring execution speed


PATH = os.path.dirname(os.path.abspath(__file__)) + "/"
SCREEN_W = 1000
SCREEN_H = 1000
TITLE = "Light ray-casting demo"
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
BLACK = arcade.color.BLACK
SHADOW = arcade.color.DARK_GRAY

view_left, view_bottom = 0, 0
r_random = random.random
SpriteList = arcade.SpriteList


def get_image_path(filename: str):
    """
    Produce TESTS_PATH to the texture, which name is provided as parameter.

    :param filename: str -- name of the texture file to be loaded without
    extension
    :return: str -- absolute TESTS_PATH of texture
    """
    return PATH + filename


def new_id(category):
    """
    Assign new id to the newly instantiated object.

    :param category: class -- any class which has count class attribute
    :return: int -- new id value
    """
    if not hasattr(category, "count"):
        raise AttributeError("Object passed has no class attribute: 'count'!")
    category.count += 1
    return category.count

class Obstacle(arcade.Sprite):

    count = 0

    def __init__(self, texture: str, x: float, y: float):
        """
        :param texture: str -- name of the basic texture for a Sprite
        :param x: float -- x coordinate of start position
        :param y: float -- y coordinate
        """

        texture_ = get_image_path(texture)

        super().__init__(texture_, center_x=x, center_y=y)
        self.type_ = texture
        self.id = new_id(Obstacle)
        self.fixed = True


class Application(arcade.Window):
    """Application application class."""

    def __init__(self, screen_w, screen_h, title, update_rate):
        super().__init__(screen_w, screen_h, title, update_rate=update_rate)
        self.set_mouse_visible(False)

        self.lights = None
        self.obstacles = None

        self.units = None
        self.static = None

        self.setup()

    def setup(self):
        """Set all attributes to default values."""
        self.lights = []
        self.obstacles = []
        self.static = SpriteList(is_static=True)

        for i in range(200, SCREEN_W, 300):
            for j in range(200, SCREEN_H, 300):
                self.spawn(Obstacle("light_obstacle.png", i, j))
        self.spawn(Obstacle("light_obstacle.png", 500, 500))

        # light testing:
        L = Light(600, 500, 3, obstacles=self.static, power=1500, debug=True)
        L.x = 10
        L.y = 10
        self.lights.append(L)
        print(self.lights)

    def spawn(self, spawned):
        """
        Use this method to create new instances of every in-game object to
        assure, that it would be appended to correct SpriteList or ordinary
        list and avoid adding them in additional lines. It also assures that
        obstacles are registered in level geometry.
        """
        lists = {"static": [], "lights": [], "obstacles": []}

        if isinstance(spawned, Obstacle):
            lists["obstacles"].append(spawned)
            if spawned.fixed:
                lists["static"].append(spawned)
                g.add_to_level_geometry(spawned)
        if isinstance(spawned, Light):
            lists["lights"].append(spawned)
        for key, value in lists.items():
            for spawned in set(value):  # set used to avoid duplicates
                self.__dict__[key].append(spawned)
        return spawned

    def on_update(self, delta_time: float):
        """"""
        self.update_lights()
        self.static.update()

    def update_lights(self):
        for light in self.lights:
            light.update()

    def on_draw(self):
        """Refresh graphic-representation of the game-state on the screen."""
        arcade.start_render()
        self.static.draw()
        self.draw_lights()

    def draw_lights(self):
        """Draw bright polygon which simulates light."""
        for light in self.lights:
            if light.light_polygon:
                arcade.draw_polygon_filled(light.light_polygon, light.color)
            if light.debug:
                for r in light.rays:
                    arcade.draw_line(r[0][0], r[0][1], r[1][0], r[1][1], RED)
                arcade.draw_ellipse_outline(light.x, light.y, 10, 10, BLACK)
                arcade.draw_text(str(len(light.rays)), light.x + 5, light.y, RED)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """Handle the mouse movements."""
        x, y = x + view_left, y + view_bottom

        if self.lights:
            self.lights[0].x = x + view_bottom
            self.lights[0].y = y + view_left


def run_app():
    """Entry point."""

    global game, game_data  # TODO: game_data object [ ] of objects [ ]
    game_data = None
    game = Application(SCREEN_W, SCREEN_H, TITLE, update_rate=FPS)
    game.set_update_rate(1 / FPS)
    arcade.set_background_color(DARK)
    arcade.run()


if __name__ == "__main__":
    from lighting import Light  # do not move this to the top!
    run_app()
