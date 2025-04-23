from Physics.Planet import Planet
from numpy import array, copy
from math import cos, sin, pi, atan2
from copy import deepcopy


class Moon(Planet):
    """
    the class to control a moon's attributes
    """

    RADIUS_FACTOR = 1 / Planet.RADIUS_FACTOR  # how much to adjust radius when converting to planet

    def __init__(self, planet: Planet, period: float, radius: float, color: str, pitch: int, sound_path: str, offset=0):
        """
        creates the planet with the given attributes

        :param planet: the planet for which the moon will orbit
        :param period: how long it takes the planet to revolve
        :param radius: the radius of the planet
        :param color: the color of the planet
        :param pitch: the pitch of the sound
        :param sound_path: the path to the audio file
        :param offset: the offset for which to place the moon
        """

        # fields that will need gui updated when modified (see property assignments at end of class)
        super(Moon, self).__init__(period, radius, color, pitch, sound_path, offset)
        self.planet = planet

        # physics fields
        self.center = array([planet.original_position[0], planet.original_position[1]])
        orig_x = planet.original_position[0] + self.orbital_radius * cos(pi * 2 * (self.offset + .25))
        orig_y = planet.original_position[1] + self.orbital_radius * -sin(pi * 2 * (self.offset + .25))
        self.original_position = array([orig_x, orig_y])
        self.position = self.original_position.copy()

    def update_physics(self, dt: float):
        """
        updates the physics of the moon

        :param dt: the time that has passed since the last update
        """

        # centering at 0,0 for polar coordinates
        self.position = self.position if not self.update else copy(self.original_position)
        self.center = self.center if not self.update else self.planet.original_position
        rel_x = self.position[0] - self.center[0]
        rel_y = self.position[1] - self.center[1]

        # Apply rotation matrix and use polar coordinates
        angular_speed = 2 * pi / self.period
        rel_angle = atan2(rel_y, rel_x)
        new_angle = rel_angle + angular_speed * dt

        # switch back to rectangular coordinates
        moon_new_x = self.planet.position[0] + self.orbital_radius * cos(new_angle)
        moon_new_y = self.planet.position[1] + self.orbital_radius * sin(new_angle)

        # Update absolute position and returns
        result = self.center[0] < 0 <= self.planet.position[0] and (not self.update)
        self.center = self.planet.position
        self.position = array([moon_new_x, moon_new_y])
        return result

    def convert(self, period: float, offset: float, **kwargs):
        """
        converts the moon to a planet

        :param period: the new period of the planet
        :param offset: the offset for the moon
        """

        self.__class__ = Planet
        self.__init__(period, self.radius * Moon.RADIUS_FACTOR, self.color, self.pitch, self.sound_path, offset)

    def __deepcopy__(self, memo):
        """
        creates a deep copy of the planet object

        :param memo: the dict of already copied objects

        :return: the copied object
        """

        moon_copy = Moon(deepcopy(self.planet, memo), self.period, self.radius, self.color, self.pitch, self.sound_path,
                         self.offset)
        memo[id(self)] = moon_copy
        return moon_copy
