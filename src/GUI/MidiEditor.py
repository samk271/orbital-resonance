from customtkinter import CTkCanvas
from numpy import array, delete


class MidiEditor(CTkCanvas):
    """
    a class to represent a midi editor with the following functionality:
        column num determines pitch and size of planet
        number of selections in column determines number of moons (n - 1) with topmost selection being the planet
        row determines orbital offset for the planet
        right click selection to change planet color/shape
        number of rows in the editor determines the period
        number of columns determines the number of moons available for the planet
        each instance of a midi editor determines a different sample sound
    """

    def __init__(self, *args, **kwargs):
        """
        creates the midi editor

        :param args: the arguments to be passed to the super class
        :param kwargs: the key word arguments to be passed to the super class
        """

        # initializes superclass and canvas fields
        super().__init__(*args, **kwargs)
        self.samples = {}

    def load_sample(self, sample: str):
        """
        loads a sample into the midi editor

        :param sample: the sample name to load
        """
