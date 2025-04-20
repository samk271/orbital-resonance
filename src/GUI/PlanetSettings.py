from customtkinter import CTkFrame, CTkLabel, CTkSlider, CTkButton, CTkTabview, CTkComboBox, CTkScrollableFrame
from tkinter.colorchooser import askcolor


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
        self.tabview = CTkTabview(self, width=450)
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
        adds a sample to the sample list todo disable delete button on default

        :param name: the name of the sample
        :param sample: the data for the sample
        """

        # creates frame for the sample
        row_frame = CTkFrame(self.sample_frame)
        self.sample_frames[name] = row_frame
        row_frame.columnconfigure(4, weight=1)
        row_frame.grid(column=0)

        # creates name label
        label = CTkLabel(row_frame, text=name, font=("Arial", 18))
        label.grid(row=0, column=0, sticky="w", padx=5)

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
        copy.configure(command=lambda: self.copy_sample(name))
        delete.configure(command=lambda: self.planet_manager.delete_sample(name))
        slider.bind("<ButtonRelease-1>", lambda e: self.set_volume(sample, slider.get()))

    def set_volume(self, sample, volume):
        """
        sets the volume of a sample

        :param sample: the sample to adjust
        :param volume: the new volume for the sample
        """

        sample["volume"] = volume

    def copy_sample(self, name):
        """
        creates a copy of a sample

        :param name: the name of the sample to copy
        """

    def sun_settings(self, parent):
        "UI for sun settings"
        
        self.sun_label = CTkLabel(parent, text="Sun Settings",font=("Arial",
                                                                    18, "bold"))
        self.sun_label.pack(pady=5, padx=10)

        #slider for the size
        self.size_label = CTkLabel(parent, text="Size:")
        self.size_label.pack(pady=(10,2))
        self.size_slider = CTkSlider(parent, from_=0, to=100, command=self.display_sun_size)
        self.old_sun_r = self.planet_manager.get_sun().radius
        self.size_slider.set(self.old_sun_r)
        self.size_slider.bind("<ButtonRelease-1>", lambda e: self.change_sun_size())
        self.size_slider.pack(pady=2, padx=10, fill="x")


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
        sun.shape = shape  # Store the shape in the sun object
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
