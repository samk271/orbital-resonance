from Physics.PlanetManager import PlanetManager
from GUI.Canvas import Canvas
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

    def save(self, canvas: Canvas, path: str = None):
        """
        compresses and saves the program state to a file

        :param canvas: the canvas class that has access to all the data that needs to be saved
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
        data = {"planets": canvas.planet_manager.planets, "samples": canvas.planet_manager.samples}
        data = compress(dumps(data))
        with open(self.save_path, "wb") as file:
            file.write(data)
        canvas.planet_manager.state_manager.unsaved = False
        return True

    def load(self, canvas: Canvas = None, path: str = None, new: bool = False) -> object:
        """
        decompresses and loads a file

        :param canvas: the canvas that has access to all the data classes that need to be loaded
        :param path: the file path to the saved planet manager class, if none is given file explorer will open
        :param new: determines if a new file should be loaded

        :return: the data loaded from the file
        """

        # asks user what file they want to load when no path is given
        if canvas and (not path) and (not new):
            path = askopenfilename(**FileManager.LOAD_OPTIONS)

        # does nothing if user did not pick a load path
        if canvas and (not path) and (not new):
            return

        # handles creating new file
        if new:
            self.save_path = None
            data = canvas.planet_manager.__init__() if canvas else PlanetManager()

        # reads the file
        else:
            with open(path, "rb") as file:
                data = loads(decompress(file.read()))
                data = canvas.planet_manager.__init__(**data) if canvas else PlanetManager(**data)
            self.save_path = path

        # loads the data into the program
        if canvas:
            canvas.speed = 1
            canvas.delete("planets")
            canvas.set_focus(canvas.planet_manager.get_sun(), True, False)
            canvas.menu_visibility["AI"]["menu"].midi.load_sample(canvas.planet_manager.samples.keys()[0])
        return data
