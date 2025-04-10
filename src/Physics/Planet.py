from numpy import array
from functools import partial
from pygame.mixer import Sound
from math import cos, sin, pi
from uuid import uuid1


class Planet:
    """
    the class to control a celestial body
        has a couple of properties to help the state manager and gui display updates assigned at the end of the class
        has state functions to handle proper saving and loading of files
    """

    def __init__(self, period: float, radius: float, color: str, sound_path=None, offset=0):
        """
        creates the planet with the given attributes

        :param period: how long it takes the planet to revolve
        :param radius: the radius of the planet
        :param color: the color of the planet
        :param sound_path: the file path of to the sound to play
        """

        # fields that will need gui updated when modified (see property assignments at end of class)
        self._period = period
        self._radius = radius
        self._color = color
        self._shape = "Circle"

        # physics fields
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
        self.sound_path = sound_path
        self.sound = Sound(sound_path) if sound_path else None

    def __getstate__(self):
        """
        gets the state of the planet to serialize when saving

        :return: the state of the planet excluding the play sound file object
        """

        state = self.__dict__.copy()
        del state["sound"]
        del state["state_manager"]
        return state

    def __setstate__(self, state):
        """
        restore the state of the planet after loading from file with the sound attribute

        :param state: the state without the sound attribute
        """

        self.__dict__.update(state)
        self.sound = Sound(self.sound_path) if self.sound_path else None
        self.update = True

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

    # sets class attributes to properties so state can be stored in state manager
    color = property(lambda self: getattr(self, "_color"), partial(set_value, attribute="_color"))
    radius = property(lambda self: getattr(self, "_radius"), partial(set_value, attribute="_radius"))
    period = property(lambda self: getattr(self, "_period"), partial(set_value, attribute="_period"))
    shape = property(lambda self: getattr(self, "_shape"), partial(set_value, attribute="_shape"))
    orbital_radius = property(lambda self: (self.period ** (2 / 3)) * 500)  # read only, calculated with period
