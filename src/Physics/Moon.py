from Physics.Planet import Planet
from numpy import array
from math import cos, sin, pi, atan2


class Moon(Planet):
    """
    the class to control a moon's attributes
    """

    def __init__(self, planet: Planet, period: float, radius: float, color: str, pitch: int, offset=0):
        """
        creates the planet with the given attributes

        :param planet: the planet for which the moon will orbit
        :param period: how long it takes the planet to revolve
        :param radius: the radius of the planet
        :param color: the color of the planet
        :param pitch: the pitch of the sound
        :param offset: the offset for which to place the moon
        """

        # fields that will need gui updated when modified (see property assignments at end of class)
        super(Moon, self).__init__(period, radius, color, planet.sound_path, offset)
        self.pitch = pitch
        self.planet = planet
        planet.moon = self

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
        moon_rel_x = self.position[0] - self.center[0]
        moon_rel_y = self.position[1] - self.center[1]

        # Apply rotation matrix and use polar coordinates
        angular_speed = 2 * pi / self.period
        rel_angle = atan2(moon_rel_y, moon_rel_x)
        new_angle = rel_angle + angular_speed * dt

        # switch back to rectangular coordinates
        moon_new_x = self.planet.position[0] + self.orbital_radius * cos(new_angle)
        moon_new_y = self.planet.position[1] + self.orbital_radius * sin(new_angle)

        # Update absolute position and returns
        result = self.center[0] < 0 <= self.planet.position[0] and (not self.update)
        self.center = self.planet.position
        self.position = array([moon_new_x, moon_new_y])
        return result
