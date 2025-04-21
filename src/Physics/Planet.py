from numpy import array, copy
from functools import partial
from pygame.mixer import Sound
from math import cos, sin, pi, atan2
from uuid import uuid1
from os.path import dirname
from os import makedirs


class Planet:
    """
    the class to control a celestial body
        has a couple of properties to help the state manager and gui display updates assigned at the end of the class
        has state functions to handle proper saving and loading of files
    """

    RADIUS_FACTOR = .5  # how much to adjust radius when converting to moon

    def __init__(self, period: float, radius: float, color: str, pitch: int, sound_path=None, offset=0):
        """
        creates the planet with the given attributes

        :param period: how long it takes the planet to revolve
        :param radius: the radius of the planet
        :param color: the color of the planet
        :param pitch: the pitch to apply to the sound for this planet
        :param sound_path: the file path of to the sound to play
        :param offset: the offset for which to place the moon
        """

        # fields that will need gui updated when modified (see property assignments at end of class)
        self._period = period
        self._radius = radius
        self._color = color
        self._shape = "Circle"

        # physics fields
        self.moons = self.moons if hasattr(self, "moons") else []
        self.offset = offset
        orig_x = self.orbital_radius * cos(2 * pi * (self.offset + .25))
        orig_y = self.orbital_radius * -sin(2 * pi * (self.offset + .25))
        self.original_position = array([orig_x, orig_y])
        self.position = array([orig_x, orig_y])

        # UI fields
        self.tag = self.tag if hasattr(self, "tag") else uuid1()
        self.update = True
        self.state_manager = self.state_manager if hasattr(self, "state_manager") else None  # added by planet manager

        # music generation fields
        self.pitch = pitch
        self.sound_path = sound_path
        self.sound = Sound(sound_path) if sound_path else None

    def update_physics(self, dt: float):
        """
        updates the physics for the planet

        :param dt: the time that has passed since the last update

        :return: true if the planet should play a sound
        """

        # gets the position
        self.position = self.position if not self.update else copy(self.original_position)
        rel_x = self.position[0]
        rel_y = self.position[1]

        # Apply rotation matrix and use polar coordinates
        angular_speed = 2 * pi / self.period
        rel_angle = atan2(rel_y, rel_x)
        new_angle = rel_angle + angular_speed * dt

        # switch back to rectangular coordinates
        new_x = self.orbital_radius * cos(new_angle)
        new_y = self.orbital_radius * sin(new_angle)

        # Update absolute position and returns
        self.position = array([new_x, new_y])
        return rel_x < 0 <= new_x and (not self.update)

    def convert(self, planet, period: float, offset: float):
        """
        converts the planet to a moon

        :param planet: the planet that this planet (soon to be a moon) should orbit
        :param period: the new period for the moon
        :param offset: the offset for the moon
        """

        from Physics.Moon import Moon
        self.moons.clear()
        self.__class__ = Moon
        self.__init__(planet, period, self.radius * Planet.RADIUS_FACTOR, self.color, self.pitch, self.sound_path
                      , offset)

    def set_value(self, value, attribute: str, add_state: bool = True):
        """
        handles when the user updates a value
            --> adds the state update to the state manager
            --> updates the value in the class

        ** PASSED BY PROPERTY **
        :param value: the value of the class to update

        ** PASSED BY PARTIAL **
        :param attribute: the attribute of the class to update

        ** PASSED BY RECURSION **
        :param add_state: determines if the action should be added to the state manager
        """

        # adds state
        undo = (self.set_value, (getattr(self, attribute), attribute, False))
        redo = (self.set_value, (value, attribute, False))
        self.state_manager.add_state({"undo": [undo], "redo": [redo]}, self.update) if add_state else None

        # updates planet
        setattr(self, attribute, value)
        self.update = True

    def __getstate__(self):
        """
        gets the state of the planet to serialize when saving

        :return: the state of the planet excluding the play sound file object
        """

        state = self.__dict__.copy()
        if self.sound_path:
            with open(self.sound_path, "rb") as f:
                state["sound"] = f.read()
        del state["state_manager"]
        return state

    def __setstate__(self, state):
        """
        restore the state of the planet after loading from file with the sound attribute

        :param state: the state without the sound attribute
        """

        self.__dict__.update(state)
        if self.sound_path:
            makedirs(dirname(self.sound_path), exist_ok=True)
            with open(self.sound_path, "wb") as f:
                state["sound"] = f.write(state["sound"])
        self.sound = Sound(self.sound_path) if self.sound_path else None
        self.update = True

    def __deepcopy__(self, memo):
        """
        creates a deep copy of the planet object

        :param memo: the dict of already copied objects

        :return: the copied object
        """

        # handles when the planet has already been copied
        if id(self) in memo:
            return memo[id(self)]

        # copies the planet
        planet_copy = Planet(self.period, self.radius, self.color, self.pitch, self.sound_path, self.offset)
        memo[id(self)] = planet_copy
        return planet_copy

    # sets class attributes to properties so state can be stored in state manager
    color = property(lambda self: self._color, partial(set_value, attribute="_color"))
    radius = property(lambda self: self._radius, partial(set_value, attribute="_radius"))
    period = property(lambda self: self._period, partial(set_value, attribute="_period"))
    shape = property(lambda self: self._shape, partial(set_value, attribute="_shape"))
    orbital_radius = property(lambda self: (self.period ** (2 / 3)) * 500)  # read only, calculated with period
