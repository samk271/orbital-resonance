from Physics.Planet import Planet
from Physics.Planet import Moon
from numpy import array, copy
from math import cos, sin, pi, atan2
from FileManagement.StateManager import StateManger


# noinspection PyPropertyDefinition
class PlanetManager:
    """
    a class to manage all of the planets that the user has created within the GUI
        --> can create new planets
        --> can destroy planets
        --> can get the list of plants
    """

    # gui will automatically update by setting focused_planet
    focused_planet = property(lambda self: self._focused_planet, lambda self, value: self.canvas.set_focus(value))

    def __init__(self, planets: list[Planet] = None, samples: dict = None):
        """
        creates the planet manager class with the list of planets given by the user

        :param planets: a list of planets created by the user, must have at least 1 element the sun. if none is given
            a sun will be generated automatically
        :param samples: a dict containing all of the configurations of sample midi editors
        """

        # sets attributes
        self.planets = planets if planets else [Planet(0, 50, "yellow")]  # todo adjust default sun settings when min/max values are determined
        self.samples = samples if samples else {}
        self.time_elapsed = 0
        self.removed_buffer = []
        self.added_buffer = self.planets.copy()
        self.state_manager = StateManger()

        # sets values that will be controlled by the canvas
        self._focused_planet = None
        self.canvas = self.canvas if hasattr(self, "canvas") else None  # will be assigned

        # ensures planets have access to state manager
        for planet in self.planets:
            planet.state_manager = self.state_manager

    def get_sun(self) -> Planet:
        """
        :return: the sun, the first element of the planet list
        """

        return self.planets[0]

    def add_planet(self, planet: Planet, add_state: bool = True, modify_state: bool = False):
        """
        adds a planet to the list of planets that exist in the program
            ** note: planet class must be created externally and passed as a parameter **

        the planet will not be added to the UI immediately but will be added to the add buffer which the UI will draw
        each frame

        additionally adds the remove planet action to the undo buffer

        :param planet: the planet that has been created that should be added to the planets list
        :param add_state: determines if the action should be added to the state manager
        :param modify_state: determines if the action should modify the previous state
        """

        # adds state updates to state manager
        state = {"undo": [(self.remove_planet, (planet, False))], "redo": [(self.add_planet, (planet, False))]}
        self.state_manager.add_state(state, modify_state) if add_state else None

        # adds planet to solar system
        planet.state_manager = self.state_manager
        self.planets.append(planet)
        self.added_buffer.append(planet)
        planet.update = True

    def remove_planet(self, planet: Planet, add_state: bool = True, modify_state: bool = False):
        """
        removes a planet from the list of planets that exist in the program
            ** note: this planet must have already been added to the list with add_planet and passed again to remove **

        the planet will not be removed from the UI immediately but will be added to the removed buffer which the UI will
        remove each frame update

        additionally adds the add planet action to the undo buffer

        :param planet: the planet to remove from the planets list
        :param add_state: determines if the action should be added to the state manager
        :param modify_state: determines if the action should modify the previous state
        """

        # adds state to state manager
        state = {"undo": [(self.add_planet, (planet, False))], "redo": [(self.remove_planet, (planet, False))]}
        self.state_manager.add_state(state, modify_state) if add_state else None

        # removes planet
        self.planets.remove(planet)
        self.removed_buffer.append(planet)

        # ensures focused planet is reset if needed
        if planet == self.focused_planet:
            self.focused_planet = None

    def add_moon(self, planet: Planet, moon: Moon, add_state: bool = True):
        """
        adds a moon to a planet
            ** note: moon class must be created externally and passed as a parameter **

        the moon will not be added to the UI immediately but will be added to the add buffer which the UI will draw
        each frame

        additionally adds the remove moon action to the undo buffer

        this function assumes the planet does not already contain a moon. If it already has a moon, it does nothing

        :param planet: the planet that is getting the moon
        :param moon: the moon being added
        :param add_state: determines if the action should be added to the state manager
        """
        planet.moon = moon
        # adds state updates to state manager
        state = {"undo": (self.remove_moon, planet, moon, False), "redo": (self.add_moon, planet, moon, False)}
        self.state_manager.add_state(state) if add_state else None
        planet.moon.state_manager = self.state_manager

        # sets some values for the moon
        planet.moon.center = array([planet.original_position[0], planet.original_position[1]])
        orig_x = planet.original_position[0] + moon.orbital_radius * cos(pi * 2 * (moon.offset + .25))
        orig_y = planet.original_position[1] + moon.orbital_radius * -sin(pi * 2 * (moon.offset + .25))
        planet.moon.original_position = array([orig_x,orig_y])
        planet.moon.position = planet.moon.original_position.copy()
        planet.moon.sound = planet.sound
        planet.moon.sound_path = planet.sound_path

        # adds moon to solar system
        self.added_buffer.append(moon)
        self.planets.append(moon)
        planet.moon.update = True

    def remove_moon(self, planet: Planet, moon: Moon, add_state: bool = True):
        """
        removes a moon from a planet
            ** note: this planet must have already been added to the list with add_planet and passed again to remove **

        the moon will not be removed from the UI immediately but will be added to the removed buffer which the UI will
        remove each frame update

        additionally adds the add moon action to the undo buffer

        :param planet: the planet from the moon originates
        :param moon: the specific moon that's being removed (for possibe use later for multiple moons)
        :param add_state: determines if the action should be added to the state manager
        """

        # adds state to state manager
        state = {"undo": lambda: self.add_moon(planet, moon, False), "redo": lambda: self.remove_moon(planet, moon, False)}
        self.state_manager.add_state(state) if add_state else None

        # removes planet
        planet.moon = None
        self.removed_buffer.append(moon)

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

    def set_planet_position(self, planet: Planet, dt: int):
        """
        sets the position of a given planet based on how much time has passed
        also updates its moon if there is one

        :param planet the planet to set the position of
        :param dt: the time that has passed since last update

        :return true if the planet should play a sound
        """
        # makes sure planet is not actually a moon
        if isinstance(planet, Moon):
            return False

        # gets the position
        dt = dt if not planet.update else self.time_elapsed
        planet.position = planet.position if not planet.update else copy(planet.original_position)
        rel_x = planet.position[0]
        rel_y = planet.position[1]

        # Apply rotation matrix and use polar coordinates
        angular_speed = 2 * pi / planet.period
        rel_angle = atan2(rel_y, rel_x)
        new_angle = rel_angle + angular_speed * dt

        # switch back to rectangular coordinates
        new_x = planet.orbital_radius * cos(new_angle)
        new_y = planet.orbital_radius * sin(new_angle)

        # Update absolute position
        planet.position = array([new_x, new_y])

        #update moon position if there is one
        if planet.moon:
            moon = planet.moon
            moon.center = planet.position

            # centering at 0,0 for polar coordinates
            moon_rel_x = moon.position[0] - rel_x
            moon_rel_y = moon.position[1] - rel_y

            # Apply rotation matrix and use polar coordinates
            angular_speed = 2 * pi/moon.period
            rel_angle = atan2(moon_rel_y, moon_rel_x)
            new_angle = rel_angle + angular_speed * dt

            # switch back to rectangular coordinates
            moon_new_x = moon.center[0] + moon.orbital_radius * cos(new_angle)
            moon_new_y = moon.center[1] + moon.orbital_radius * sin(new_angle)

            # Update absolute position
            moon.position = array([moon_new_x, moon_new_y])
            #if rel_angle < pi/2 and new_angle >= pi/2:
                #play moon sound if needed (moon sound is just planet.sound, just pitched differently)

        return rel_x < 0 <= new_x and (not planet.update)

    def update_planet_physics(self, dt):
        """
        runs the physics engine on each of the planets within the application

        :param dt: the change in time since the last physics update in seconds
        """

        # updates planet manager state
        self.time_elapsed += dt
        triggered_planets = []
        for planet in self.planets[1:]:

            # updates each planets position
            if self.set_planet_position(planet, dt):
                planet.sound.play() if planet.sound else None
                triggered_planets.append(planet)

        return triggered_planets
