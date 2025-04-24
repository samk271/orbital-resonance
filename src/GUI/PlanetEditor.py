from customtkinter import CTkButton, CTkLabel, CTkSlider, CTkComboBox, CTkToplevel
from tkinter.colorchooser import askcolor
from Physics.Planet import Planet


class PlanetEditor(CTkToplevel):
    """
    a frame that allows the user to modify a planet
    """

    planets = {}

    def __init__(self, *args, **kwargs):
        """
        creates the planet editor frame

        :param args: the arguments to be passed to the super class
        :param kwargs: the key word arguments to be passed to the super class
        """

        # creates editor
        self.tag = kwargs.pop("tag")
        self.planet = kwargs.pop("planet")
        self.midi = kwargs.pop("midi")
        super(PlanetEditor, self).__init__(*args, **kwargs)
        self.title("Planet Settings")
        self.resizable(False, False)
        self.transient(self.master)
        self.geometry(f"+{self.master.winfo_rootx()}+{self.master.winfo_rooty()}")
        self.sun_label = CTkLabel(self, text="Planet Settings", font=("Arial", 18, "bold"))
        self.sun_label.pack(pady=(20, 5), padx=10)

        # slider for the size
        self.size_label = CTkLabel(self, text="Size:")
        self.size_label.pack(pady=(10, 2))
        self.size_slider = CTkSlider(self, from_=25, to=200, command=self.display_size)
        self.old_r = self.planet.radius
        self.size_slider.set(self.old_r)
        self.size_slider.bind("<ButtonRelease-1>", lambda e: self.change_size())
        self.size_slider.pack(pady=2, padx=20)


        # select shape
        self.shape = CTkLabel(self,text="Shape:")
        self.shape.pack(pady=(10, 0))
        self.shape_options = CTkComboBox(self, values=["Circle", "Square", "Triangle", "Rectangle"],
                                         command=lambda e: self.change_shape(e))
        self.shape_options.pack()


        # choose color
        self.color_label = CTkLabel(self, text="Color:")
        self.color_label.pack(pady=(10, 0))

        self.color_buttons = {}
        button = CTkButton(self, text="Choose Color", command=lambda: self.open_color_dialog())
        button.pack(padx=5, pady=(0, 20))
        PlanetEditor.planets[self.planet].destroy() if self.planet in PlanetEditor.planets else None
        PlanetEditor.planets[self.planet] = self

    def display_size(self, r: int):
        """
        updates the UI to display the new size while sliding, but doesnt add the change to the state manager

        :param r: the radius of the sun to display
        """

        self.planet._radius = r
        self.planet.update = True

    def change_size(self):
        self.planet._radius = self.old_r
        self.planet.update = False
        self.planet.radius = self.size_slider.get()
        state = {"undo": [(self.size_slider.set, (self.old_r, ))],
                 "redo": [(self.size_slider.set, (self.size_slider.get(), ))]}
        self.planet.state_manager.add_state(state, True)
        self.old_r = self.planet.radius

    def change_shape(self, shape):
        """
        Changes the sun's shape to the selected shape.

        :param shape: The selected shape for the sun.
        """

        state = {"undo": [(self.shape_options.set, (self.planet.shape, ))],
                 "redo": [(self.shape_options.set, (shape, ))]}
        self.planet.shape = shape
        self.planet.state_manager.add_state(state, True)

    def open_color_dialog(self):
        """
        Opens the color chooser dialog and applies the selected color.
        """
        color = askcolor()[1]  # Get the selected color in hex format
        if color:  # If a color is selected (not canceled)

            undo = [(self.midi.canvas.itemconfig, (self.tag, ), {"fill": self.planet.color})]
            self.planet.color = color
            redo = [(self.midi.canvas.itemconfig, (self.tag,), {"fill": self.planet.color})]

            # adds state update and updates color of midi editor
            self.planet.state_manager.add_state({"undo": undo, "redo": redo}, True)
            self.midi.canvas.itemconfig(self.tag, fill=self.planet.color)
