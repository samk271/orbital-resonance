from customtkinter import CTkFrame, CTkLabel, StringVar, CTkSlider, CTkButton


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

        # The title:
        self.label_text = StringVar(value="Sun Settings")
        self.label = CTkLabel(self, textvariable=self.label_text, font=("Arial", 18, "bold"))
        self.label.pack(pady=5, padx=10)

        # Size Slider
        self.size_label = CTkLabel(self, text="size: ")
        self.size_label.pack(pady=(10, 2))
        self.size_slider = CTkSlider(self, from_=0, to=100)
        self.size_slider.pack(pady=2, padx=10, fill="x")

        # Brightness
        self.size_label = CTkLabel(self, text="Brightness: ")
        self.size_label.pack(pady=(10, 2))
        self.size_slider = CTkSlider(self, from_=0, to=100)
        self.size_slider.pack(pady=2, padx=10, fill="x")

        # apply button
        self.apply_button = CTkButton(self, text=" Apply changes")
        self.apply_button.pack(pady=10)

        # separator line
        self.separator = CTkFrame(self, height=2, fg_color="gray")
        self.separator.pack(fill="x", pady=5, padx=10)
