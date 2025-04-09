from Physics.Planet import Planet
from numpy import array
from math import cos, sin, pi, atan2
from FileManagement.StateManager import StateManger


class PlanetManager:
    """
    a class to manage all of the planets that the user has created within the GUI
        --> can create new planets
        --> can destroy planets
        --> can get the list of plants
    """

    def __init__(self, planets: list[Planet] = None):
        """
        creates the planet manager class with the list of planets given by the user

        :param planets: a list of planets created by the user, must have at least 1 element the sun. if none is given
            a sun will be generated automatically
        """

        # sets planet attributes
        self.planets = planets if planets else [Planet(0, 50, "yellow")]  # todo adjust default sun settings when min/max values are determined
        self.removed_buffer = []
        self.added_buffer = self.planets.copy()
        self.state_manager = StateManger()

        # ensures planets have access to state manager
        for planet in self.planets:
            planet.state_manager = self.state_manager

    def get_sun(self) -> Planet:
        """
        :return: the sun, the first element of the planet list
        """

        return self.planets[0]

    def add_planet(self, planet: Planet, add_state: bool = True):
        """
        adds a planet to the list of planets that exist in the program
            ** note: planet class must be created externally and passed as a parameter **

        the planet will not be added to the UI immediately but will be added to the add buffer which the UI will draw
        each frame

        additionally adds the remove planet action to the undo buffer

        :param planet: the planet that has been created that should be added to the planets list
        :param add_state: determines if the action should be added to the state manager
        """

        # adds state updates to state manager
        state = {"undo": (self.remove_planet, planet, False), "redo": (self.add_planet, planet, False)}
        self.state_manager.add_state(state) if add_state else None

        # adds planet to solar system
        planet.state_manager = self.state_manager
        self.planets.append(planet)
        self.added_buffer.append(planet)
        self.reset_planet_positions()

    def remove_planet(self, planet: Planet, add_state: bool = True):
        """
        removes a planet from the list of planets that exist in the program
            ** note: this planet must have already been added to the list with add_planet and passed again to remove **

        the planet will not be removed from the UI immediately but will be added to the removed buffer which the UI will
        remove each frame update

        additionally adds the add planet action to the undo buffer

        :param planet: the planet to remove from the planets list
        :param add_state: determines if the action should be added to the state manager
        """

        # adds state to state manager
        state = {"undo": lambda: self.add_planet(planet, False), "redo": lambda: self.remove_planet(planet, False)}
        self.state_manager.add_state(state) if add_state else None

        # removes planet
        self.planets.remove(planet)
        self.removed_buffer.append(planet)

    def get_added_buffer(self) -> list[Planet]:
        """
        gets the list of planets that have been queued to add to the UI and clears the queue

        :return: the buffer of planets to add
        """

        buffer = self.added_buffer.copy()
        self.added_buffer.clear()
        return buffer

    def get_removed_buffer(self) -> list[Planet]:
        """
        gets the list of planets that have been queued to remove from the UI and clears the queue

        :return: the buffer of planets to remove
        """

        buffer = self.removed_buffer.copy()
        self.removed_buffer.clear()
        return buffer

    def reset_planet_positions(self):
        """
        Resets the position of each planet

        Called when new planet is added to keep everything in sync
        """
        for planet in self.planets:
            planet.position = planet.original_position

    def update_planet_physics(self, dt):
        """
        runs the physics engine on each of the planets within the application

        :param dt: the change in time since the last physics update in seconds
        """

        triggered_planets = []
        for planet in self.planets:

            # if planet is the sun, skip it
            if planet.period == 0:
                continue

            rel_x = planet.position[0]
            rel_y = planet.position[1]

            # Apply rotation matrix and use polar coordinates
            angular_speed = 2 * pi/planet.period
            rel_angle = atan2(rel_y, rel_x)
            new_angle = rel_angle + angular_speed * dt

            # switch back to rectangular coordinates
            new_x = planet.orbital_radius * cos(new_angle)
            new_y = planet.orbital_radius * sin(new_angle)

            # Update absolute position
            planet.position = array([new_x, new_y])

            if rel_x < 0 and new_x >= 0:
                #insert sound playing here
                planet.sound.play() if planet.sound else None
                triggered_planets.append(planet)

        return triggered_planets
