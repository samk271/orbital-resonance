from Physics.Planet import Planet
from FileManagement.StateManager import StateManger
from tkinter.messagebox import askokcancel, showerror


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
        self.planets = planets if planets else [Planet(0, 50, "yellow", 0)]  # todo adjust default sun settings when min/max values are determined
        self.samples = samples if samples else {"Default (No Audio)": {"pitch": 0, "volume": 0}}
        self.sample = "Default (No Audio)"
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

        # adds to parent planet list if planet is a moon
        if type(planet) != Planet:
            planet.planet.moons.append(planet)

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

        # removes from parent planet list if planet is a moon
        if type(planet) != Planet:
            planet.planet.moons.remove(planet)

        # ensures focused planet is reset if needed
        if planet == self.focused_planet:
            self.focused_planet = None

    def add_sample(self, name: str, sample: dict, add_state: bool = True):
        """
        adds a sample to the list of samples and updates the gui

        :param name: the name of the sample
        :param sample: the sample to add
        :param add_state: determines if the state should be added to the state manager
        """

        # handles when name is invalid
        if name == "Default (No Audio)":
            showerror("Invalid Name", "Sample cannot be named: Default (No Audio)")
            return

        # exits if user does not want to override another sample
        msg = "A sample with this name already exist, saving will override this save. Continue?"
        if (name in self.samples.keys()) and (not askokcancel("Sample Already Exists", msg)):
            return

        # overrides another sample
        state = {"undo": [], "redo": []}
        if name in self.samples.keys():
            state = self.delete_sample(name, False)

        # adds sample
        self.samples[name] = sample
        self.canvas.menu_visibility["planet"]["menu"].add_sample(name, sample)

        # adds planets from sample
        if "midi_array" in sample.keys():
            [self.add_planet(planet) for planet in sample["midi_array"].flatten() if planet is not None]

        # adds to state manager
        if add_state:
            undo = [(self.delete_sample, (name, False))] + state["undo"]
            redo = state["redo"] + [(self.add_sample, (name, sample, False))]
            self.state_manager.add_state({"undo": undo, "redo": redo})

    def delete_sample(self, name: str, add_state: bool = True):
        """
        deletes a sample from the list of samples and updates the gui

        :param name: the name of the sample
        :param add_state: determines if the state should be added to the state manager

        :return the state
        """

        # asks user if they are sure they want to delete
        msg = "You are about to delete a sample which will delete any associated planets. Continue?"
        if add_state and (not askokcancel("Delete Sample", msg)):
            return

        # deletes the sample
        sample = self.samples.pop(name)
        self.canvas.menu_visibility["planet"]["menu"].sample_frames[name].destroy()

        # deletes planets in sample
        if "midi_array" in sample.keys():
            [self.remove_planet(planet) for planet in sample["midi_array"].flatten() if planet is not None]

        # adds to state manager
        undo = [(self.add_sample, (name, sample, False))]
        redo = [(self.delete_sample, (name, False))]
        self.state_manager.add_state({"undo": undo, "redo": redo}) if add_state else None
        return {"undo": undo, "redo": redo}

    def set_sample(self, sample: str):
        """
        sets the selected sample and updates the GUI

        :param sample: the sample that was selected
        """

        self.sample = sample
        self.canvas.menu_visibility["planet"]["menu"].sample.set(sample)
        self.canvas.menu_visibility["AI"]["menu"].midi.load_sample(sample)

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

        # updates planet manager state
        self.time_elapsed += dt
        triggered_planets = []
        for planet in self.planets[1:]:

            # updates each planets position
            if planet.update_physics(dt if not planet.update else self.time_elapsed):
                planet.sound.play() if planet.sound else None
                triggered_planets.append(planet)

        return triggered_planets
