from customtkinter import CTkFrame, CTkLabel, CTkTextbox, CTkButton, CTkCanvas


class AISettings(CTkFrame):
    """
    The class that will handle the settings menu that controls the AI planet generation
    """

    def __init__(self, *args, **kwargs):
        """
        creates the settings window

        :param args: the arguments to be passed to the super class
        :param kwargs: the key word arguments to be passed to the super class
        """

        # initializes superclass and binds user actions
        super().__init__(*args, **kwargs)

        # creates the input label
        input_label = CTkLabel(self, text="AI Input:", font=("Arial", 20))
        input_label.grid(row=0, column=1, rowspan=3, sticky="ne", pady=20, padx=(20, 0))

        # creates user input text box
        self.textbox = CTkTextbox(self, height=94)
        self.textbox.grid(row=0, column=2, rowspan=3, pady=20, padx=10)

        # creates generate button todo add function
        generate_button = CTkButton(self, text="Generate")
        generate_button.grid(row=0, column=4, sticky="n", pady=(20, 0))

        # creates play sound button todo add function
        self.play_button = CTkButton(self, text="Play Sound", state="disabled", fg_color="gray25")
        self.play_button.grid(row=1, column=4, pady=5)

        # creates add button todo add function
        self.add_button = CTkButton(self, text="Add to Solar System", state="disabled", fg_color="gray25")
        self.add_button.grid(row=2, column=4, sticky="s", pady=(0, 20))

        # creates the planet output label
        planet_label = CTkLabel(self, text="Generated\nPlanet/Sound:", font=("Arial", 20))
        planet_label.grid(row=0, column=6, rowspan=3, sticky="ne", pady=20, padx=(10, 10))

        # creates generated planet display
        self.planet_canvas = CTkCanvas(self, width=60, height=60, bg="gray17", highlightthickness=0)
        self.planet_canvas.grid(row=0, column=7, rowspan=3)

        # creates the generated sound display
        self.sound_canvas = CTkCanvas(self, width=60, height=60, bg="gray17", highlightthickness=0)
        self.sound_canvas.grid(row=0, column=8, rowspan=3, padx=(10, 20))

        # sets column weights for dynamic resizing
        self.columnconfigure(0, weight=1)
        self.columnconfigure(3, weight=10)
        self.columnconfigure(5, weight=10)
        self.columnconfigure(9, weight=1)

        # handles menu focus
        self.bind("<Button-1>", lambda event: self.focus_set())
        for child in self.winfo_children():
            child.bind("<Button-1>", lambda event: self.focus_set())

        # creates an example planet and sound to display todo remove when functionality has been added
        self.planet_canvas.create_oval(0, 0, 60, 60, fill="red")
        for i in range(60):
            from random import randint
            dx = randint(0, 30)
            self.sound_canvas.create_line(i, 30 + dx, i, 30 - dx, fill="blue")
