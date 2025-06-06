from tkinter.colorchooser import askcolor
from os.path import isdir
from os import mkdir
from copy import deepcopy
from customtkinter import CTkFrame, CTkLabel, CTkSlider, CTkButton, CTkTabview, CTkComboBox, CTkScrollableFrame, \
    CTkRadioButton, StringVar


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

        self.planet_manager = kwargs.pop("planet_manager")
        super().__init__(*args, **kwargs)
        self.sample_frames = {}
        self.sample = StringVar(self.master, self.planet_manager.sample)
        self.tabview = CTkTabview(self, width=500)
        self.tabview.pack(fill="both" , expand= True, padx=10, pady= 10)

        #tabs for different settings
        self.sun_tab= self.tabview.add("Sun Settings")

        #sun 
        self.sun_settings(self.sun_tab)

        # creates the sample list
        sample_list = self.tabview.add("Sample List")
        self.tabview.grid_propagate(False)
        self.sample_frame = CTkScrollableFrame(sample_list)
        self.sample_frame.columnconfigure(0, weight=1)
        self.sample_frame.pack(fill="both", expand=True)

        # adds samples to sample list
        for name, sample in self.planet_manager.samples.items():
            self.add_sample(name, sample)

    def add_sample(self, name, sample):
        """
        adds a sample to the sample list

        :param name: the name of the sample
        :param sample: the data for the sample
        """

        # creates frame for the sample
        row_frame = CTkFrame(self.sample_frame, border_width=1)
        self.sample_frames[name] = row_frame
        row_frame.columnconfigure(4, weight=1)
        row_frame.grid(column=0)

        # creates radiobutton
        container = CTkFrame(row_frame, width=200, height=30, fg_color=row_frame.cget("fg_color"))
        container.pack_propagate(False)
        radio_button = CTkRadioButton(container, text=name, font=("Arial", 18), value=name, variable=self.sample)
        radio_button.pack(side="left")
        container.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        # creates buttons
        copy = CTkButton(row_frame, text="📋", width=1, font=("Arial", 18))
        copy.grid(row=0, column=1, padx=5)
        delete = CTkButton(row_frame, text="🗑", width=0, font=("Arial", 18))
        delete.grid(row=0, column=2)

        # creates volume slider
        volume = CTkLabel(row_frame, text="🔊", font=("Arial", 18))
        volume.grid(row=0, column=3, sticky="e", padx=(10, 0))
        slider = CTkSlider(row_frame, from_=0, to=1)
        slider.set(sample["volume"])
        slider.grid(row=0, column=4, sticky="ew", padx=(2, 5))

        # binds functions
        radio_button.configure(command=lambda: self.planet_manager.set_sample(self.sample.get()))
        copy.configure(command=lambda: self.copy_sample(name))
        delete.configure(command=lambda: self.planet_manager.delete_sample(name))
        slider.bind("<ButtonRelease-1>", lambda e: self.set_volume(sample, slider))
        slider.configure(command=lambda e: [planet.sound.set_volume(e) if planet.sound else None for
                                            planet in sample["midi_array"].flatten() if planet is not None] if
        "midi_array" in sample else None)

        # ensures default sample has proper settings
        if name == "Default (No Audio)":
            delete.configure(state="disabled", fg_color="gray25")

    def set_volume(self, sample, slider):
        """
        sets the volume of a sample

        :param sample: the sample to adjust
        :param slider: the slider object that controls the volume
        """

        # sets state
        state = {"undo": [(sample.update, ({"volume": sample["volume"]}, )),
                          (lambda: [planet.sound.set_volume(sample["volume"]) if planet.sound else None for planet in
                                    sample["midi_array"].flatten() if planet is not None] if "midi_array" in sample
                          else None, ()),
                          (slider.set, (sample["volume"], ))],
                 "redo": [(sample.update, ({"volume": slider.get()}, )),
                          (lambda: [planet.sound.set_volume(sample["volume"]) if planet.sound else None for planet in
                                    sample["midi_array"].flatten() if planet is not None] if "midi_array" in sample
                          else None, ()),
                          (slider.set, (slider.get(), ))]}
        self.planet_manager.state_manager.add_state(state)

        # updates volume
        sample["volume"] = slider.get()
        if "midi_array" in sample:
            for planet in [planet for planet in sample["midi_array"].flatten() if planet is not None]:
                if planet.sound:
                    planet.sound.set_volume(slider.get())

    def copy_sample(self, name):
        """
        creates a copy of a sample

        :param name: the name of the sample to copy
        """

        # ensures save name is unique
        i = 1
        while f"{name} ({i})" in self.planet_manager.samples.keys():
            i += 1

        #add sample folder to AUDIO
        if not (isdir(f"./AUDIO/user_samples/{name} ({i})")):
                mkdir(f"./AUDIO/user_samples/{name} ({i})")

        # creates a copy of the sample
        sample = deepcopy(self.planet_manager.samples[name])
        sample["name"] = f"{name} ({i})"
        self.planet_manager.add_sample(f"{name} ({i})", sample)

    def sun_settings(self, parent):
        "UI for sun settings"
        
        self.sun_label = CTkLabel(parent, text="Sun Settings",font=("Arial",
                                                                    18, "bold"))
        self.sun_label.pack(pady=5, padx=10)

        #slider for the size
        self.size_label = CTkLabel(parent, text="Size:")
        self.size_label.pack(pady=(10,2))
        self.size_slider = CTkSlider(parent, from_=25, to=200, command=self.display_sun_size)
        self.old_sun_r = self.planet_manager.get_sun().radius
        self.size_slider.set(self.old_sun_r)
        self.size_slider.bind("<ButtonRelease-1>", lambda e: self.change_sun_size())
        self.size_slider.pack(pady=2, padx=10)


        #select shape
        self.shape = CTkLabel(parent,text="Shape:")
        self.shape.pack(pady=(10, 0))
        self.shape_options = CTkComboBox (parent, values=["Circle", "Square", 
                                                          "Triangle", "Rectangle"], command=lambda e: self.change_sun_shape(e))
        self.shape_options.pack()


        #choose color
        self.color_label = CTkLabel (parent, text="Color:")
        self.color_label.pack(pady=(10, 0))

        #Color choices
        self.color_frame =CTkFrame(parent, fg_color= "transparent")
        self.color_frame.pack(pady=5)
        self.colors = ["Yellow", "Green", "Blue", "Orange", "Purple","Red", "Custom"]

        self.color_buttons = {}      

        for color in self.colors:

            if color == "Custom":
                button = CTkButton(self.color_frame, text="Choose Color", 
                                   command= lambda: self.open_color_dialog())
                button.pack(side="left", padx=5)
                continue


        # apply button todo redundant
        # self.apply_button = CTkButton(self, text=" Apply Sun changes",
        #                               command=self.apply_settings)
        # self.apply_button.pack(pady=10)

        #reset button 
        self.reset_button = CTkButton(parent, text="Reset to Default", fg_color="gray", 
                                      command=self.reset_settings)
        self.reset_button.pack(pady=5)

        # #save button todo redundant
        # self.save_button = CTkButton(parent, text="Save",command=self.save_settings)
        # self.save_button.pack(pady=10)

    def open_color_dialog(self):
        """
        Opens the color chooser dialog and applies the selected color.
        """
        color = askcolor()[1]  # Get the selected color in hex format
        if color:  # If a color is selected (not canceled)
            self.change_sun_color(color)

    def display_sun_size(self, r: int):
        """
        updates the UI to display the new sun size while sliding, but doesnt add the change to the state manager

        :param r: the radius of the sun to display
        """

        self.planet_manager.get_sun()._radius = r
        self.planet_manager.get_sun().update = True

    def change_sun_size(self):
        self.planet_manager.get_sun()._radius = self.old_sun_r
        self.planet_manager.get_sun().update = False
        self.planet_manager.get_sun().radius = self.size_slider.get()
        state = {"undo": [(self.size_slider.set, (self.old_sun_r, ))],
                 "redo": [(self.size_slider.set, (self.size_slider.get(), ))]}
        self.planet_manager.state_manager.add_state(state, True)
        self.old_sun_r = self.planet_manager.get_sun().radius

    def change_sun_color(self, color):

        # if hasattr(self, "planet_manager") and self.planet_manager: todo redundant
        sun = self.planet_manager.get_sun()
        sun.color = color
        # sun.update = True  # Mark the sun for UI update todo already handled by planet class
        self.selected_color = color
    
    def change_sun_shape(self, shape):
        """
        Changes the sun's shape to the selected shape.

        :param shape: The selected shape for the sun.
        """
        # if hasattr(self, "planet_manager") and self.planet_manager: todo redundant
        sun = self.planet_manager.get_sun()
        state = {"undo": [(self.shape_options.set, (sun.shape, ))],
                 "redo": [(self.shape_options.set, (shape, ))]}
        sun.shape = shape  # Store the shape in the sun object
        self.planet_manager.state_manager.add_state(state, True)
        # sun.update = True  # Mark the sun for UI update todo already handled by planet class

    # def save_settings(self): todo redundant
    #     """
    #     Saves the current sun settings (size, shape, and color) to the PlanetManager.
    #     """
    #     if hasattr(self, "planet_manager") and self.planet_manager:
    #         sun = self.planet_manager.get_sun()
    #         sun.radius = self.size_slider.get()
    #         sun.shape = self.shape_options.get()  # Save the selected shape
    #         sun.update = True  # Mark the sun for UI update
    #
    # def apply_settings(self): todo redundant
    #     """
    #     Applies the current settings to the sun immediately.
    #     """
    #     self.save_settings()  # Save the settings to the PlanetManager
    #     self.planet_manager.state_manager.add_state({
    #         "undo": (self.reset_settings,),  # Allow undoing the changes
    #         "redo": (self.apply_settings,)
    #     })

    def reset_settings(self):
        """
        Resets the sun settings to their default values.
        """
        # if hasattr(self, "planet_manager") and self.planet_manager: todo redundant
        sun = self.planet_manager.get_sun()
        self.size_slider.set(50)  # Reset size to default (example value)
        self.shape_options.set("Circle")  # Reset shape to default
        self.selected_color = "Yellow"  # Reset color to default
        sun.radius = 50
        sun.color = "Yellow"
        sun.shape = "Circle"  # Reset shape to default
        # sun.update = True  # Mark the sun for UI update todo already handled by planet class
