from Physics.PlanetManager import PlanetManager
from customtkinter import CTk
from tkinter.filedialog import asksaveasfilename, askopenfilename
from pathlib import Path
from pickle import dumps, loads
from zlib import compress, decompress
from re import findall


class FileManager:
    """
    handles saving and loading of files
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

    def __init__(self):
        """
        creates the file manager class
        """

        self.save_path = None

    def save(self, planet_manager: PlanetManager, path: str = None):
        """
        compresses and saves the planet manager class to a file

        :param planet_manager: the planet manager class to save
        :param path: the file path to save the file to, if given functions like save as, otherwise functions like save

        :return True if save was successful
        """

        # ask user for save path if no save path is found
        if (not path) and (not self.save_path):
            while (FileManager.SAVE_OPTIONS["initialdir"] / FileManager.SAVE_OPTIONS["initialfile"]).is_file():
                # ensures default file name is unique
                file_num = findall(r'\d+', FileManager.SAVE_OPTIONS["initialfile"])
                file_num = int(file_num[0]) + 1 if len(file_num) == 1 else 1
                FileManager.SAVE_OPTIONS["initialfile"] = f"save ({file_num}).orbres"

            # opens file explorer
            path = asksaveasfilename(**FileManager.SAVE_OPTIONS)

        # exits if user did not pick a save path
        if (not path) and (not self.save_path):
            return

        # saves data and updates save path
        self.save_path = path if path else self.save_path
        data = compress(dumps(planet_manager.planets))
        with open(self.save_path, "wb") as file:
            file.write(data)
        return True

    def load(self, path: str = None) -> object:
        """
        decompresses and loads a file

        :param path: the file path to the saved planet manager class, if none is given file explorer will open

        :return: an instance of the planet manager class that was loaded from the file
        """

        # asks user what file they want to load when no path is given
        if not path:
            path = askopenfilename(**FileManager.LOAD_OPTIONS)

        # does nothing if user did not pick a load path
        if not path:
            return

        # loads the file
        with open(path, "rb") as file:
            planet_manager = PlanetManager(loads(decompress(file.read())))
        self.save_path = path
        return planet_manager
