import os
from customtkinter import CTkFrame, CTkLabel, CTkTextbox, CTkButton, CTkCanvas
from CTkListbox import *

class AISettings(CTkFrame):
    """
    The class that will handle the settings menu that controls the AI planet generation

    todo add to solar system button functionality
    """

    def __init__(self, *args, **kwargs):
        """
        creates the settings window

        :param args: the arguments to be passed to the super class
        :param kwargs: the key word arguments to be passed to the super class
        """

        # initializes superclass and binds user actions
        super().__init__(*args, **kwargs)

        """
        TEMPORARILY DISABLING AI PROMPT
        # creates the input label
        input_label = CTkLabel(self, text="AI Input:", font=("Arial", 20))
        input_label.grid(row=0, column=1, rowspan=3, sticky="ne", pady=20, padx=(20, 0))

        # creates user input text box
        self.textbox = CTkTextbox(self, height=94)
        self.textbox.grid(row=0, column=2, rowspan=3, pady=20, padx=10)
        """

        self.listbox = CTkListbox(self, width=320,height=120, hover=True)
        self.listbox.grid(row=0,column=0,rowspan=3,pady=20,padx=10)

        # doesnt crash if dataset is not found
        try:
            self.add_wav_to_listbox(listbox=self.listbox, wav_dir="./AI/dataset/clotho/development")
        except:
            pass

        # creates generate button
        generate_button = CTkButton(self, text="Generate")
        generate_button.configure(command=lambda: self.generate_planet(generate_button.cget("fg_color")))
        generate_button.grid(row=0, column=3, sticky="n", pady=(20, 0))

        # creates play sound button todo add function
        self.play_button = CTkButton(self, text="Play Sound", state="disabled", fg_color="gray25")
        self.play_button.grid(row=1, column=3, pady=5)

        # creates add button todo add function
        self.add_button = CTkButton(self, text="Add to Solar System", state="disabled", fg_color="gray25")
        self.add_button.grid(row=2, column=3, sticky="s", pady=(0, 20))

        # creates generated planet display and label
        self.planet_label = CTkLabel(self, text="Generated\nPlanet/Sound:", font=("Arial", 20))
        self.planet_canvas = CTkCanvas(self, width=60, height=60, bg="gray17", highlightthickness=0)
        self.planet_canvas.grid(row=0, column=5, rowspan=3)

        # creates the generated sound display
        self.sound_canvas = CTkCanvas(self, width=120, height=120, bg="gray17", highlightthickness=0)
        self.sound_canvas.grid(row=0, column=1, rowspan=3, padx=(10, 20))

        # sets column weights for dynamic resizing
        self.columnconfigure(0, weight=1)
        self.columnconfigure(7, weight=1)

        # handles menu focus
        self.bind("<Button-1>", lambda event: self.focus_set())
        for child in self.winfo_children():
            child.bind("<Button-1>", lambda event: self.focus_set())

    def generate_planet(self, color: str):
        """
        generates a planet using the AI
            --> enables the play sound and add to solar system buttons
            --> adds a label for the created planet/sound
            --> displays what the planet will look like
            --> displays what the audio for the planet will look like

        :param color: the fg color to set the disabled buttons to
        """

        # enabled the buttons
        self.play_button.configure(state="normal", fg_color=color)
        self.add_button.configure(state="normal", fg_color=color)

        # creates the planet output label
        self.planet_label.grid(row=0, column=4, rowspan=3, sticky="ne", pady=20, padx=(10, 10))

        # generates the planet todo add AI function
        #text = self.textbox.get("1.0", "end-1c")
        # print(f"AI input: {text}")

        # draws the planet todo currently randomly generated
        from random import randint
        self.planet_canvas.delete("all")
        self.planet_canvas.create_oval(0, 0, 60, 60, fill="#{:06x}".format(randint(0, 0xFFFFFF)))

        # draws the audio of the planet todo currently randomly generated
        self.sound_canvas.delete("all")
        for i in range(120):
            dx = randint(0, 120)
            self.sound_canvas.create_line(i, 60 + dx, i, 60 - dx, fill="blue")

    #add all the wav files from the directory to the listbox
    def add_wav_to_listbox(self, listbox, wav_dir):
        wav_files = os.listdir(wav_dir)
        for i, file in enumerate(wav_files[100:200]):
            listbox.insert(i, file)
        listbox.activate(0)