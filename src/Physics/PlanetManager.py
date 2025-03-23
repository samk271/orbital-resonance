from customtkinter import CTk
from Physics.Planet import Planet
from numpy import array
from math import cos, sin, pi, atan2
from pickle import dumps, loads
from zlib import compress, decompress
from tkinter.filedialog import asksaveasfilename, askopenfilename
from pathlib import Path
from re import findall


class PlanetManager:
    """
    a class to manage all of the planets that the user has created
        --> can create new planets
        --> can destroy planets
        --> can get the list of plants
    """

    # options for save as file explorer
    SAVE_OPTIONS = {
        "initialdir": Path("saves"),
        "initialfile": "save.orbres",
        "defaultextension": ".orbres",
        "filetypes": [
            ("Orbital Resonance Files", "*.orbres")
        ],
        "title": "Save As",
        "parent": CTk(),
        "confirmoverwrite": True
    }
    
    # options for load file explorer
    LOAD_OPTIONS = {
        "initialdir": Path("saves"),
        "title": "Select a File",
        "filetypes": [
            ("Orbital Resonance Files", "*.orbres")
        ],
        "defaultextension": ".orbres",
        "parent": SAVE_OPTIONS["parent"]
    }

    def __init__(self, planets: list[Planet] = None):
        """
        creates the planet manager class with the list of planets given by the user

        :param planets: a list of planets created by the user, must have at least 1 element the sun. if none is given
            a sun will be generated automatically
        """

        self.planets = planets if planets else [Planet(0, 50, "yellow")]  # todo adjust default sun settings when min/max values are determined
        self.removed_buffer = []
        self.added_buffer = self.planets.copy()
        self.save_path = None

    def save(self, path: str = None):
        """
        compresses and saves the planet manager class to a file

        :param path: the file path to save the file to, if given functions like save as, otherwise functions like save
        """

        # ask user for save path if no save path is found
        if (not path) and (not self.save_path):
            while (PlanetManager.SAVE_OPTIONS["initialdir"] / PlanetManager.SAVE_OPTIONS["initialfile"]).is_file():

                # ensures default file name is unique
                file_num = findall(r'\d+', PlanetManager.SAVE_OPTIONS["initialfile"])
                file_num = int(file_num[0]) + 1 if len(file_num) == 1 else 1
                PlanetManager.SAVE_OPTIONS["initialfile"] = f"save ({file_num}).orbres"

            # opens file explorer
            path = asksaveasfilename(**PlanetManager.SAVE_OPTIONS)

        # exits if user did not pick a save path
        if (not path) and (not self.save_path):
            return

        # saves data and updates save path
        self.save_path = path if path else self.save_path
        copy = PlanetManager(self.planets)
        data = compress(dumps(copy))
        with open(self.save_path, "wb") as file:
            file.write(data)

    @staticmethod
    def load(path: str = None) -> object:
        """
        decompresses and loads a saved planet manger class

        :param path: the file path to the saved planet manager class, if none is given file explorer will open

        :return: an instance of the planet manager class that was loaded from the file
        """

        # asks user what file they want to load when no path is given
        if not path:
            path = askopenfilename(**PlanetManager.LOAD_OPTIONS)

        # does nothing if user did not pick a load path
        if not path:
            return

        # loads the file
        with open(path, "rb") as file:
            planet_manager = loads(decompress(file.read()))
        planet_manager.save_path = path
        return planet_manager

    def get_sun(self) -> Planet:
        """
        :return: the sun, the first element of the planet list
        """

        return self.planets[0]

    def add_planet(self, planet: Planet):
        """
        adds a planet to the list of planets that exist in the program
            ** note: planet class must be created externally and passed as a parameter **

        the planet will not be added to the UI immediately but will be added to the add buffer which the UI will draw
        each frame

        :param planet: the planet that has been created that should be added to the planets list
        """

        self.planets.append(planet)
        self.added_buffer.append(planet)

    def remove_planet(self, planet: Planet):
        """
        removes a planet from the list of planets that exist in the program
            ** note: this planet must have already been added to the list with add_planet and passed again to remove **

        the planet will not be removed from the UI immediately but will be added to the removed buffer which the UI will
        remove each frame update

        :param planet: the planet to remove from the planets list
        """

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

    def update_planet_physics(self, dt):
        """
        runs the physics engine on each of the planets within the application

        :param dt: the change in time since the last physics update in seconds
        """

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

            #if rel_x < 0 and new_x >= 0:
                #insert sound playing here
                
