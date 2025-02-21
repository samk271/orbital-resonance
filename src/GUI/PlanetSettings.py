from customtkinter import CTkFrame, CTkLabel, StringVar


class PlanetSettings(CTkFrame):
    """
    The class that will handle the settings menu that controls the planet settings
    """

    def __init__(self, *args, **kwargs):
        """
        creates the settings window

        :param args: the arguments to be passed to the super class
        :param kwargs: the key word arguments to be passed to the super class
        """

        super().__init__(*args, **kwargs)

        # creates the label
        self.label_text = StringVar(value="Sun Settings")
        self.label = CTkLabel(self, textvariable=self.label_text, font=("Arial", 20))
        self.label.pack()
