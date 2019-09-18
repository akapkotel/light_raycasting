#!/usr/bin/env python
"""
This is a simple in-game menu-builder for Arcade games made in Python. It
requires Python3.6 and Arcade2.0.8. Menus are basically a bunch of classes
defining how Arcade should display clickable elements and what functions to
call when they re activated.

1. INSTALLATION:
To install simple_arcade_menu just open terminal and write:

TODO: pip3 install simple_arcade_menu

To check if everything works fine:

TODO: test template

2. USAGE:
To make it work you must import it: at least Cursor, Menu and Button classes in
your game script. You do not even need to make your own implementations of
methods.

SharedVariable:
This class makes it possible to share a common value between many objects in
the game and update them dynamically. Just use Slider or CheckBox which are
creating SharedVariables themselves. Optionally, instantiate SharedVariable
by yourself and use it's add_associate() method to connect it to the
attribute of your game class.

Menu:
Menu class to work requires you to pass into it's constructor a single SubMenu
object, which would be the main menu of your menu-system displayed first
when player enters menu (e.g. starts the game). For Menu and SUbMenu to work
it is also required that a Cursor object is initialized.

SubMenu:
SubMenu class to work requires only a list of MenuElement objects (eg. Button),
Cursor object initialised in your game, and a hook to your arcade.Window
object. It's up to you how would you manage the menu in your game, but you can
easily do that with a single bool variable checked in on_update() method to
decide if you want to draw your game or call the draw() method of Menu
instance.

Cursor:
Cursor class to work requires only being initialised by your arcade.Window
instance and kept as it's attribute to easily call it's methods: on_update()
and on_draw(), when you want Cursor object to being used.

MenuElement:
MenuElement class (and all deriving from it, eg, Button) requires only being
initialised with whatever functions passed to them as callbacks and after
you create your Buttons, remember of passing them as a list to the Menu
instance. Some classes deriving from MenuElement (e.g. Slider) requires
SharedVariable imported also.

So, the order of imports, instantiating classes and handling them in your game
should be:
1. SharedVariable - which is the class you need to assign it's instances as the
 values for all attributes and other
variables you need to be changed with usage of Slider and RadioButton elements
of the Menu
2. Cursor class object and implement arcade methods: on_mouse_motion(),
on_mouse_press(), on_mouse_drag() and on_mouse_release() to call the Cursor
methods instead.
3. List of MenuElement objects (e.g. Button) - with at least one element.
4. (Optional) arcade.Texture object as background for menu
5. At least one SubMenu class object with List from (3) passed as menu_elements
 argument, and (optional) texture from
(4) passed as background argument.
6. Menu class object with SubMenu from (5) passed as main_menu argument.
7. Adding Cursor on_update() and Menu update() methods calls to the on_update()
 method in your game.
8. Adding Cursor draw() and Menu draw() methods calls to the on_draw() method
in your game.
9. Logic determining if Menu and Cursor should be updated and drawn in current
frame are up to you.

9. If you need multi-level menu, you must instantiate some SubMenu objects with
 their own lists of MenuElements and set
the callbacks to toggle_submenu() method of your Menu with the 'name' of your
SubMenu as argument.

IMPORTANT: app_hook attribute of Menu and Cursor must be the same arcade.Window
 object!
"""
__author__ = "Rafał Trąbski"
__copyright__ = "Copyright 2019"
__credits__ = []
__license__ = "Share Alike Attribution-NonCommercial-ShareAlike 4.0"
__version__ = "1.0.0"
__maintainer__ = "Rafał Trąbski"
__email__ = "rafal.trabski@mises.pl"
__status__ = "Development"

import abc
import arcade

WHITE, GRAY, BLACK, GREEN = (arcade.color.WHITE, arcade.color.GRAY,
                             arcade.color.BLACK, arcade.color.GREEN)


def normalize(value: float, minimum: float, maximum: float):
    """Keep variable value in range of min and max values."""
    if value < minimum:
        return minimum
    elif value > maximum:
        return maximum
    else:
        return value


class SharedVariable:
    """
    SharedVariable makes it available to connect attributes of your
    arcade.Window class or other classes from your script to the Slider or
    RadioButton elements of the Menu so when these are used, values of
    connected attributes change too.

    There are two ways of creating SharedVariable instance:
    (1) Some of the MenuElements instantiate new SharedVariable
    automatically in their __init__ if you do not pass any SharedVariable
    instance as an argument. In that case you should:

    Step 1: just instantiate new MenuElement (e.g. Slider) without any
    instance of SharedVariable passed - it would be generated automatically
    for you, but you will have no reference to it.

    (2) you can pass SharedVariable instance created by your own to these
    MenuElements if you need to have your own reference for the future. If so:

    Step 1: instantiate SharedVariable like: variable = SharedVariable() to get
    the reference to your SharedVariable object.
    Step 2: instantiate MenuElement (e.g. Slider) and as the last argument
    pass the SharedVariable (your variable) already created.

    Either way object and it's attribute you pass to the MenuElement will be
    associated to the new SharedVariable automatically.

    Each frame the SharedVariable value changes (e.g. when Slider is moved in
    the Menu), value of attribute of the associated object is automatically
    updated too.

    Having a reference from (1) You can always add another 'associated'
    attribute of any object, using the 'add_associate()' method. You pass the
    object itself as a first argument, and string name of the object's
    attribute you need to be associated as the second argument.

    You can also remove connection with 'remove_associate()' passing the
    object, which should be unassociated.
    """

    def __init__(self, value: bool or int or float or str):
        """
        SharedVariable is an internal object used to assure that value of
        variables assigned to different objects in the application, especially
        to the MenuElement objects and arcade.Window attributes, will be the
        same.

        :param value: bool, int, float or str -- value of variable assigned to
         this shared object
        """
        self._value = value
        self.associated = {}

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        """Change value of the SharedVariable."""
        self._value = value
        self.update()

    def add_associate(self, object_: object, attribute: str):
        """
        Add new association to this SharedVariable.

        :param object_: object -- instance of class to which the associated
        attribute belongs
        :param attribute: str -- string name of the instance's attribute which
         you want to associate ith this SharedVariable
        """
        self.associated[object_] = attribute

    def remove_associate(self, removed_object: object):
        """
        Delete the association to this SharedVariable.

        :param removed_object: object -- an class instance which attribute you
        need to disassociate
        """
        if removed_object in self.associated.keys():
            del self.associated[removed_object]
        # when self.associated was a list of tuples:
        # removed = filter(lambda x: x[0] is removed_object, self.associated)
        # [self.associated.remove(x) for x in removed]

    def update(self):
        """
        Update the value of each attribute associated to the SharedVariable.
        """
        for associate in self.associated.keys():
            associate.__dict__[self.associated[associate]] = self.value


class Cursor(arcade.Sprite):
    """
    Cursor class to work with Menu elements. It handles all cursor-events,
    like detection of cursor hoovering above element, mouse-clicks on the
    elements, mouse-dragging of elements etc.
    """

    def __init__(self,
                 app_hook: arcade.Window,
                 filepath: str,
                 filename: str,
                 angle: int = 30,
                 menu_only: bool = True,
                 hide_os_cursor: bool = True):
        """
        Basic placeholder for a in-game cursor displayed instead of the user's
        system cursor.
        Remember to call on_update() and draw() methods in your game update()
        and draw() to assure that this Cursor will be updated and displayed!

        :param app_hook: arcade.Window object -- instance of arcade.Window
        class required for Menu functions to work with the app
        :param filepath: str -- absolute TESTS_PATH to the cursor texture
        :param filename: str -- name of the cursor texture
        :param angle: int -- angle in degrees (default: 30)
        :param menu_only: bool -- if the cursor should be displayed only in the
         game menu (default: True)
        :param hide_os_cursor: bool -- if system cursor should be hidden and
        replaced with this one (default: True)
        """
        super().__init__(filepath + filename)
        self.application = app_hook
        # menu widget Cursor is currently hoovering above (if any):
        self.current_element = None

        self.angle = angle

        self.menu_only = menu_only

        self.cursors = arcade.SpriteList()
        self.cursors.append(self)

        if hide_os_cursor: self.application.set_mouse_visible(False)

    def check_if_above_menu_element(self):
        """
        Check if game-cursor object overlaps any o the game-menu buttons,
        sliders etc.
        """
        for element in self.application.menu.current_elements:
            if element.check_if_cursor_above(self.center_x, self.top):
                if not element.mouse_above:
                    element.on_mouse_over()
                    self.current_element = element
            else:
                if element.mouse_above:
                    element.on_mouse_over()
                    self.current_element = None

    def on_mouse_motion(self, x: float, y: float, in_menu: bool):
        """
        This method should be called by the on_mouse_motion() method of
        arcade.Window application which you need this Cursor to work with.
        Your on_mouse_motion() should look like this:

        def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
            '''docstring'''
            self.cursor.on_mouse_motion(x, y, self.in_menu)

        Where 'self.cursor' is an attribute referencing this Cursor object in
        your arcade.Window instance, and the 'self.in_menu' is a bool
        attribute used to check if Menu object is currently active and
        displayed in game.

        :param float x: x position of mouse
        :param float y: y position of mous
        :param in_menu: bool -- if Menu object is currently displayed and
        Cursor should be updated
        """
        if ((self.menu_only and in_menu) or
                (not self.menu_only)):
            self.set_position(x, y)

            self.check_if_above_menu_element()

    def on_mouse_press(self, button: int, in_menu: bool):
        """
        Handle mouse-buttons press only when game-menu is displayed. Otherwise
        mouse cursor is hidden. This method should be called by the
        on_mouse_motion() method of arcade.Window application which you need
        this Cursor to work with.

        :param button: int -- What button was hit. One of:
        arcade.MOUSE_BUTTON_LEFT, arcade.MOUSE_BUTTON_RIGHT,
        arcade.MOUSE_BUTTON_MIDDLE
        :param in_menu: bool -- if Menu object is currently displayed and
        Cursor should be updated
        """
        if in_menu and button == arcade.MOUSE_BUTTON_LEFT:
            if self.current_element is not None:
                self.current_element.on_press()

    def on_mouse_release(self, button: int, in_menu: bool):
        """
        Handle mouse buttons release events.

        :param button: int -- What button was hit. One of:
        arcade.MOUSE_BUTTON_LEFT, arcade.MOUSE_BUTTON_RIGHT,
        arcade.MOUSE_BUTTON_MIDDLE
        :param in_menu: bool -- if Menu object is currently displayed and
        Cursor should be updated
        """
        if in_menu and button == arcade.MOUSE_BUTTON_LEFT:
            if self.current_element is not None:
                self.current_element.on_release()

    def on_mouse_drag(self, dx: float):
        """
        This method should be called by the on_mouse_drag() method of
        arcade.Window application which you need this Cursor to work with.
        """
        if isinstance(self.current_element, Slider):
            self.current_element.on_drag(dx)

    def on_update(self):
        """
        Updates Cursor object calling arcade.SpriteList.update() method. This
        method should be added to the main game on_update() method.
        """
        self.cursors.update()

    def draw(self):
        """
        Updates Cursor object calling arcade.SpriteList.draw() method. This
        method should be added to the main game on_draw() method.
        """
        self.cursors.draw()


class SubMenu:
    """
    A submenu is just a string name, bunch of MenuElements put into the list
    and background texture. Menu navigates through its SubMenus to offer
    user multi-leveled menus in games.
    """

    def __init__(self, name: str = "MainMenu", menu_elements: list = None,
                 background=None, main=False):
        """
        You need at least one instance of SubMenu to pass it as argument to the
         Menu constructor,

        :param name: str -- name of the submenu, would be used to navigate in
        Menu object (default: 'MainMenu')
        :param menu_elements: list -- list of MenuElements this SubMenu object
        should display when activated. Each
        button request must be an instance of Menu.Button object. See the
        '__init__' method for it' initializing
        parameters.
        :param background: arcade.load_texture() -- an texture displayed as
        this SubMenu background, make sure that it's
        size is not larger than arcade.Window size.
        :param main: bool -- if this is a top-level SubMenu of Menu (if not,
        pressing ESC would move player out to the top-level SubMenu.
        """
        self.name = name
        self.is_main_menu = main
        self.elements = menu_elements
        self.background = background


class Menu:
    """
    This class is the core of in-game-menu system. Menu class contains all the
    SubMenu instances (lower-level menus) and at least one main menu
    (highest-level SubMenu with 'main' attribute set to True). Menu methods
    provides way to easy navigation between SubMenu instances it contains
    and handles updating and displaying their elements.
    """

    def __init__(self, app_hook: arcade.Window, main_menu: SubMenu):
        """
        New Menu object constructor. Menu-object contains a hook used to
        reference the caller, which should be an class inheriting from
        arcade.Window class.
        It also keeps a register of the menu-interactive objects, like buttons
        etc. along with the callbacks bound to them.

        :param app_hook: arcade.Window object -- instance of arcade.Window
        class required for Menu functions to work with the app
        :param main_menu: SubMenu object -- main menu to be displayed when
        player enters menu in game and the highest-level of the Menu
        """
        self.application = app_hook

        self.submenus = {}

        self.current_elements = None
        self.current_background = None

        self.add_submenu(main_menu)
        self.toggle_submenu(main_menu.name)

    def add_submenu(self, submenu: SubMenu, title: str = None):
        """
        Register an instance of SubMenu class as the lower-level sub-menu of
        this Menu. It is possible to toggle active submenu (set of
        the MenuElements and backgrounds) and navigate through multi-leveled
        menus. Main Menu submenu is also registered with this method.

        :param submenu: SubMenu object -- submenu to be added to the Menu
        :param title: str -- optional name for the submenu (default: None)
        """
        self.submenus[title if title else submenu.name] = submenu

    def toggle_submenu(self, submenu_name: str):
        """
        Navigate from current submenu to another one. Load it's MenuElements
        and background. Call this method in your arcade.Window to change
        submenu which is displayed - just pass the string name of desired
        SubMenu object you registered into the Menu.

        :param submenu_name: str -- name of the submenu to open
        """
        self.current_elements = self.submenus[submenu_name].elements
        self.current_background = self.submenus[submenu_name].background

    def update(self):
        """Update all the Menu attributes values."""
        for element in self.current_elements:
            element.update()

    def draw(self):
        """
        Display menu buttons and background accordingly to what 'submenu'
        from self.submenus is currently active and set as self.current_submenu.
        """
        if self.current_background is not None:
            width, height = self.application.width, self.application.height
            arcade.draw_texture_rectangle(width / 2, height / 2, width, height,
                                          self.current_background)

        for element in self.current_elements:
            element.draw()


class MenuElement:
    """
    TODO: write abstract class for basic mMenu-widget [ ],
    make Button ihnerit from it [ ], test it [ ]
    """

    def __init__(self,
                 name: str = "MenuElement",
                 pos_x: float = 0.0,
                 pos_y: float = 0.0,
                 function: callable = None):
        """
        Base class for all the widgets used in the SubMenu instances.

        :param name: str -- name of the element
        :param pos_x: float -- x coordinate of the element's center
        :param pos_y: float -- y coordinate of the element's center
        :param function: callable -- function called when widget is used
        """
        self.name = name
        self.center_x = pos_x
        self.center_y = pos_y
        self.function = function
        self.mouse_above = False

    def check_if_cursor_above(self, cursor_x: float, cursor_y: float):
        """
        Compare x and y coordinates of Cursor object ant this Element
        (or coords of part of this Element). This method is called by the
        Cursor object each frame it moves. Implement this in the deriving
        classes.

        :param cursor_x: float -- x coordinate of Cursor object
        :param cursor_y: float -- y coordinate of Cursor object
        :return: bool -- if the Cursor is hovering over the MenuElement
        """
        pass

    @abc.abstractmethod
    def on_press(self):
        """
        Function called when Cursor object receives 'click' event on this
        Element. Called automatically by the Menu class. Implement this in
        the deriving classes.
        """
        pass

    def on_drag(self, drag: float):
        """
        Called when Cursor left button is pressed over this Element and moved.
        Called automatically by the Menu class. Implement this in the
        deriving classes.
        """
        pass

    def on_release(self):
        """
        Called when Cursor button is released above this Element. Called
        automatically by the Menu class. Implement this in the deriving
        classes.
        """
        pass

    def on_mouse_over(self):
        """
        Called when the Cursor is hoovering above this Element. Called
        automatically by the Menu class. Implement this in the deriving
        classes..
        """
        self.mouse_above = not self.mouse_above

    @abc.abstractmethod
    def update(self):
        """
        Update attributes of this Element. Called automatically by the Menu
        class. Implement this in the deriving classes.
        """
        pass

    @abc.abstractmethod
    def draw(self):
        """
        Display this button on the screen. Called automatically by the Menu
        class. Implement this in the deriving classes.
        """
        pass


class Button(MenuElement):
    """
    Each Button object is a simple data-container used by the Arcade module to
    draw ui elements and call unctions.
    """

    # TODO: sizes and padding of buttons depending on the screen height and
    #  width (constants?)

    def __init__(self,
                 name: str = "Button",
                 pos_x: float = 0.0,
                 pos_y: float = 0.0,
                 width: float = None,
                 height: float = None,
                 border_width: int = 3,
                 button_color: arcade.color = GRAY,
                 highlight_color: arcade.color = WHITE,
                 border_color: arcade.color = BLACK,
                 text_color: arcade.color = BLACK,
                 font_size: int = 20,
                 texture: arcade.Texture = None,
                 function: callable = None):
        """
        Initializing a new button remember to set up the function as 'function'
         parameter, otherwise button would do nothing, when pressed.

        :param name: str -- name of the button
        :param pos_x: int -- x coordinate of the button's center
        :param pos_y: int -- y coordinate
        :param width: int -- width of the button
        :param height: int -- height of the button
        :param border_width: int -- thickness of the button's outline, if 0,
        outline does not exist (default: 0)
        :param button_color: arcade.color -- color of button (default: gray)
        :param highlight_color: arcade.color -- color of the button when cursor
        hoovers above it (default: white)
        :param border_color: arcade.color -- color of the button's outline
        (default: black)
        :param text_color: arcade.color -- color of the button's name
        (default: black)
        :param font_size: int -- size of the button text
        :param texture: arcade.Texture -- an optional texture to be displayed
        as button's background
        :param function: function() -- function called when button is pressed,
        pass it WITHOUT parentheses!
        """
        super().__init__(name, pos_x, pos_y, function)

        self.color = button_color
        self.highlight_color = highlight_color
        self.border_color = border_color
        self.text_color = text_color
        self.current_color = button_color  # actual button_color of the button

        self.font_size = font_size
        self.width = (len(name) * font_size) if width is None else width
        self.height = 3 * font_size if height is None else height
        self.border_width = border_width
        self.left = self.center_x - (self.width / 2)
        self.right = self.left + self.width
        self.top = self.center_y + (self.height / 2)
        self.bottom = self.top - self.height

        self.texture = texture
        self.image_alpha = 255

    def check_if_cursor_above(self, cursor_x: float, cursor_y: float):
        condition_a = self.left < cursor_x < self.right
        condition_b = self.bottom < cursor_y < self.top
        return condition_a and condition_b

    def on_press(self):
        """
        Call self.unction when button is pressed.
        """
        if self.function is not None:
            self.function()

    def update(self):
        if self.texture is None:
            self.current_color = self.highlight_color if self.mouse_above else self.color
        else:
            self.image_alpha = 125 if self.mouse_above else 255

    def draw(self):
        """Display this button on the screen."""
        # Button's body:
        if self.texture is None:
            arcade.draw_lrtb_rectangle_filled(self.left, self.right, self.top,
                                              self.bottom, self.current_color)
            if self.border_width > 0:
                arcade.draw_lrtb_rectangle_outline(self.left - 1,
                                                   self.right + 1,
                                                   self.top + 1,
                                                   self.bottom - 1,
                                                   self.border_color,
                                                   self.border_width)
        else:
            arcade.draw_texture_rectangle(self.center_x, self.center_y,
                                          self.width, self.height,
                                          self.texture,
                                          alpha=self.image_alpha)
        # Button's text:
        arcade.draw_text(self.name, self.left + self.font_size,
                         self.bottom + (self.height / 3), self.text_color,
                         self.font_size, align="center", anchor_x="left")


class Slider(MenuElement):
    """
    TODO: doctstring
    """

    def __init__(self,
                 object_: object,
                 attribute: str,
                 start_value: int or float or str or bool,
                 attribute_min: int or float,
                 attribute_max: int or float,
                 font: tuple = ("calibri", "arial"),
                 font_size: float = None,
                 pos_x: float = 0.0,
                 pos_y: float = 0.0,
                 width: float = 300.0,
                 height: float = 20.0,
                 border_color: arcade.Color = BLACK,
                 slide_color: arcade.Color = GRAY,
                 slider_color: arcade.Color = WHITE,
                 function: callable = None,
                 shared_variable: SharedVariable = None):
        """
        Basic slider - button moveable to some extent to the left and right,
        and changing value of connected variable when it is slided. Left
        move decreases value, move to the right increases it.

        :param object_: object -- instance of a class of which attribute you are
         connecting with this Slider
        :param attribute: str -- string name of the attribute you want to be
         connected to this Slider and updated when Slider is moved. It will
         also be the name displayed in the Menu above the Slider
        :param start_value: int, float, str or bool -- value the attribute and
         Slider should start with.
        :param attribute_min: int or float -- minimum value of variable
        associated with the Slider
        :param attribute_max: int or float -- maximum value of variable
        associated with the Slider
        :param font: tuple -- name of the font used for name of the Slider
        displayed above it
        :param font_size: float -- size of the font (if None, which is default,
         size would depend on 'height' param)
        :param pos_x: float -- x coordinate of the Slider center (default: 0.0)
        :param pos_y: float -- y coordinate (default: 0.0)
        :param width: float -- width of the Slider (default: 400.0)
        :param height: float -- height of the Slider (default: 40.0)
        :param function: callable -- a function which would be called when
        Slider is released after being moved
        :param shared_variable: SharedVariable -- optional SharedVariable
        object if you want to have external reference to this object to add new
        associated attributes later in your game script (default: None)
        """
        super().__init__(attribute, pos_x, pos_y, function)

        self.width = width
        self.height = height
        self.left = self.center_x - (self.width / 2)
        self.right = self.left + self.width
        self.top = self.center_y + (self.height / 2)
        self.bottom = self.top - self.height

        self.variable = shared_variable if shared_variable is not None else \
            SharedVariable(start_value)
        self.variable.add_associate(object_, attribute)
        self.variable_name = attribute
        self._variable_min = attribute_min
        self._variable_max = attribute_max
        self.font = font
        self.font_size = font_size if font_size else self.height / 2

        # used to calculate variable values when Slider moves:
        self.scale = (self.right - self.left) / (
                    self._variable_max - self._variable_min)
        self.slider_position = self.left + self.variable.value * self.scale
        # this variable controls if Slider is moved by the Player or not:
        self.dragged = False

        self.slide_color = slide_color
        self.border_color = border_color
        self.slider_color = slider_color
        self.slider_cur_color = self.slider_color
        # current value of the variable connected to the Slider:
        self._var_cur_val = self.variable.value

    def check_if_cursor_above(self, cursor_x: float, cursor_y: float):
        """Check if Cursor object is inside of the Slider control handle."""
        return abs(self.slider_position - cursor_x) < self.height and abs(
            self.center_y - cursor_y) < self.height

    def on_press(self):
        """Start Slider being dragged when left button is clicked on it."""
        self.dragged = True

    def on_drag(self, drag: float):
        """Implement this in the deriving classes."""
        self.slider_position += drag
        self.slider_position = normalize(self.slider_position, self.left,
                                         self.right)
        self._var_cur_val = self.set_variable()

    def on_release(self):
        """Stop Slider being dragged when mouse left button is released."""
        if self.dragged:
            self.dragged = False
            self.variable.value = self._var_cur_val

    def on_mouse_over(self):
        """Implement this in the deriving classes."""
        super().on_mouse_over()
        if not self.mouse_above:
            self.on_release()

    def update(self):
        """Update the widget state."""
        self.slider_cur_color = GREEN if self.mouse_above else self.slider_color

    def draw(self):
        """
        Display this Slider on the screen.
        """
        # Slider name:
        arcade.draw_text(self.variable_name.title(), self.left,
                         self.top + self.height / 2, WHITE, self.font_size)
        # Slider rail:
        arcade.draw_rectangle_filled(self.center_x, self.center_y, self.width,
                                     self.height, self.slide_color)
        arcade.draw_rectangle_outline(self.center_x, self.center_y,
                                      self.width + 2, self.height + 2,
                                      self.border_color)
        # Slider handle:
        arcade.draw_circle_filled(self.slider_position, self.center_y,
                                  self.height / 1.5, self.slider_cur_color)
        arcade.draw_circle_outline(self.slider_position, self.center_y,
                                   (self.height / 1.5) + 2, self.border_color)
        # Variable value:
        arcade.draw_text(str(self._var_cur_val), self.right,
                         self.top + self.height / 2, GREEN, self.font_size,
                         anchor_x="right")

    def set_variable(self):
        """
        Change value of variable connected to the Slider when it was moved left
        or right.
        """
        value = self._variable_min + (
                    self.slider_position - self.left) / self.scale
        return value if isinstance(self._variable_min, float) else int(value)


class CheckBox(MenuElement):
    """
    This element represents a simple switch button or check button which user
    can switch between two states: active or inactive and by so control the
    boolean value of some variable.

    TODO: check-button widget [x][x][x], test it [ ]
    """

    class IndicatorShape:
        def __init__(self, pos_x, pos_y, size, shape, color, texture):
            self.x = pos_x
            self.y = pos_y
            self.size = size
            self.shape = shape
            self.color = color
            self.texture = texture

        def draw(self):
            if self.texture is not None:
                arcade.draw_texture_rectangle(self.x, self.y, self.size,
                                              self.size, self.texture)
            else:
                size = self.size
                if self.shape == "SQUARE":
                    arcade.draw_rectangle_filled(self.x, self.y, size, size,
                                                 self.color)
                elif self.shape == "TICK":
                    start = (self.x - (size / 2), self.y)
                    turn = (self.x - (size / 4), self.y - (size / 2))
                    end = (self.x + (size / 2), self.y + (size / 2))
                    arcade.draw_lines((start, turn, turn, end), self.color, 3)
                elif self.shape == "CROSS":
                    l_top = (self.x - (size / 2), self.y + (size / 2))
                    l_bottom = (self.x - (size / 2), self.y - (size / 2))
                    r_top = (self.x + (size / 2), self.y + (size / 2))
                    r_bottom = (self.x + (size / 2), self.y - (size / 2))
                    arcade.draw_lines((l_top, r_bottom, l_bottom, r_top),
                                      self.color, 3)

    def __init__(self,
                 object_: object,
                 attribute: str,
                 start_value: bool or int or float or str,
                 checked_value=None,
                 unchecked_value=None,
                 name: str = "CheckBox",
                 pos_x: float = 0.0,
                 pos_y: float = 0.0,
                 function: callable = None,
                 state: bool = False,
                 checkbox_size: float = 30.0,
                 checkbox_color: arcade.Color = WHITE,
                 indicator_color: arcade.Color = GREEN,
                 shape: str = "TICK",
                 checkbox_texture: arcade.Texture = None,
                 indicator_texture: arcade.Texture = None,
                 shared_variable: SharedVariable = None,
                 ):
        """
        Initialize new CheckBox element.

        :param object_: object -- instance of a class of which attribute you are
         connecting with this Slider
        :param attribute: str -- string name of the attribute you want to be
         connected to this Slider and updated when Slider is moved. It will
         also be the name displayed in the Menu above the Slider
        :param start_value: int, float, str or bool -- value the attribute and
         Slider should start with.
        :param checked_value: object -- alternative value assigned to the
        variable if CheckBox is checked
        :param unchecked_value: object -- alternative value assigned to the
        variable when CheckBox is unchecked
        :param name: str -- name of the CheckBox to be displayed above it in
        the Menu (default: 'Checkbutton')
        :param pos_x: float -- x coordinate of the Slider center (default: 0.0)
        :param pos_y: float -- y coordinate (default: 0.0)
        :param function: callable -- function to be called when element is
        clicked
        :param state: bool -- if the CheckBox is activated or not
        (default: False)
        :param checkbox_size: float -- x and y size of the element
        (default: 10.0 x 10.0)
        :param checkbox_color: arcade.Color -- color of the box
        (default: arcade.color.BLACK)
        :param checkbox_texture: arcade.Texture -- alternatively you can set
        texture instead of color and size
        :param shape: str -- shape state indicator takes, must be one of:
        'TICK', 'CROSS', 'SQUARE' or None.
        :param indicator_color: arcade.Color -- color of the tickle pattern
        (default: arcade.color.GREEN)
        :param indicator_texture: arcade.Texture -- alternatively you can set
        a texture
        :param shared_variable: SharedVariable -- optional SharedVariable
        object if you want to have external reference to this object to add new
        associated attributes later in your game script (default: None)
        """
        super().__init__(name, pos_x, pos_y, function)

        self.state = state  # inner state of the GUI element
        # variable controlled by the inner state:

        self.variable = shared_variable if shared_variable is not None else \
            SharedVariable(start_value)
        self.variable.add_associate(object_, attribute)
        self.no_value = False if unchecked_value is None else unchecked_value
        self.yes_value = True if checked_value is None else checked_value

        self.box_size = checkbox_size
        self.box_color = checkbox_color
        self.box_texture = checkbox_texture

        self.left = self.center_x - (self.box_size / 2)
        self.right = self.left + self.box_size
        self.top = self.center_y + (self.box_size / 2)
        self.bottom = self.top - self.box_size

        self.indicator = CheckBox.IndicatorShape(pos_x,
                                                 pos_y,
                                                 self.box_size,
                                                 shape,
                                                 indicator_color,
                                                 indicator_texture)

    def check_if_cursor_above(self, cursor_x: float, cursor_y: float):
        condition_a = self.left < cursor_x < self.right
        condition_b = self.bottom < cursor_y < self.top
        return condition_a and condition_b

    def on_press(self):
        self.state = not self.state
        self.variable.value = self.yes_value if self.state else self.no_value

    def update(self):
        """
        Update attributes of this Element. Called automatically by the Menu
        class. Implement this in the deriving classes.
        """
        pass

    def draw(self):
        """
        Display this button on the screen. Called automatically by the Menu
        class. Implement this in the deriving classes.
        """
        # box:
        if self.box_texture:
            arcade.draw_texture_rectangle(self.center_x, self.center_y,
                                          self.box_texture.width,
                                          self.box_texture.height,
                                          self.box_texture)
        else:
            arcade.draw_rectangle_outline(self.center_x, self.center_y,
                                          self.box_size, self.box_size,
                                          self.box_color)
        # state indicator:
        if self.state:
            self.indicator.draw()


class TextLabel(MenuElement):
    """
    TODO: short text-element for displaying e.g. titles, names of menus [ ],
     test it [ ]
    """

    def __init__(self,
                 name: str = "MenuElement",
                 pos_x: float = 0.0,
                 pos_y: float = 0.0,
                 text: str = "",
                 font: tuple = ("calibri", "arial"),
                 text_size: float = 12,
                 function: callable = None):
        """
        Initialize new TextField, which is basically a rectangle with text.
        User can define what color should the rectangle (background) have,
        color of text etc.

        :param text: str -- text to be displayed by the TextLabel element, must
         be one-liner (default: empty string)
        """
        super().__init__(name, pos_x, pos_y, function)
        self.font = font
        self.text_size = text_size
        self._text = text

    def set_text(self, text: str):
        """Change text value of the TextField element."""
        self._text = text

    def get_text(self):
        """Read text value of this element."""
        return self._text

    def on_press(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass


class TextField(TextLabel):
    """
    TODO: long, multi-line field displaying string passed to it in constructor
     [ ] or setter [ ], test it [ ]
    """

    def __init__(self,
                 name: str = "MenuElement",
                 pos_x: float = 0.0,
                 pos_y: float = 0.0,
                 text: str = "",
                 font: tuple = ("calibri", "arial"),
                 text_size: float = 12,
                 function: callable = None):
        """
        Initialize new TextField, which is basically a rectangle with text.
        User can define what color should the rectangle (background) have,
        color of text etc.

        :param text: str -- text to be displayed by the TextLabel element, must
         be one-liner (default: empty string)
        """
        super().__init__(name, pos_x, pos_y, text, font, text_size, function)
        self.font = font
        self.text_size = text_size
        self._text = self.reformat_text(text)

    def set_text(self, text: str):
        """
        Change text value of the TextField element, but before reformat text
        to make it fit the filed constraints.
        """
        self._text = self.reformat_text(text)

    @staticmethod
    def reformat_text(text):
        """
        Fold and reformat text string to assure that it will fit to the field
        constraints.

        :param text: str -- text to be reformatted
        :return: str -- text to be usewd as self._text value.
        """
        # TODO: formatting text to assure that it will be folded as user
        #  wanted [ ][ ][ ], test it [ ]
        return text

    def on_press(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass


class UserInput(MenuElement):
    """
    TODO: a field which accepts user-input [ ], saves it to the variable [ ],
     and have getter to retrieve it's value [ ]
    """

    def update(self):
        pass

    def draw(self):
        pass

    def on_press(self):
        pass
