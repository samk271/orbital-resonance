from Physics.Planet import Planet
from customtkinter import CTkCanvas, CTkFrame, CTkButton
from tkinter.colorchooser import askcolor
from numpy import array, full, append, delete
from random import randint


class MidiEditor(CTkFrame):
    """
    a class to represent a midi editor with the following functionality:
        column num determines pitch and size of planet
        number of selections in column determines number of moons (n - 1) with topmost selection being the planet
        row determines orbital offset for the planet
        right click selection to change planet color/shape
        number of rows in the editor determines the period
        number of columns determines the number of moons available for the planet
        each instance of a midi editor determines a different sample sound

    todo use planet manager samples dict and store key in self.sample when sample names are implemented
    todo don't update midi display on undo/redo if sample has changed
    """

    DEFAULT_EDITOR = property(lambda self: full((3, 5), None))

    def __init__(self, *args, **kwargs):
        """
        creates the midi editor

        :param args: the arguments to be passed to the super class
        :param kwargs: the key word arguments to be passed to the super class
        """

        # initializes superclass and canvas fields
        self.planet_manager = kwargs.pop("planet_manager")
        super().__init__(*args, **kwargs)
        self.sample = "Default (No Audio)"

        # creates buttons
        add_column = CTkButton(self, text="Add Column", command=lambda: self.modify_editor(1, "add"))
        remove_column = CTkButton(self, text="Remove Column", command=lambda: self.modify_editor(1, "remove"))
        add_row = CTkButton(self, text="Add Row", command=lambda: self.modify_editor(0, "add"))
        remove_row = CTkButton(self, text="Remove Row", command=lambda: self.modify_editor(0, "remove"))

        # places buttons
        add_column.grid(row=0, column=0)
        remove_column.grid(row=0, column=1)
        add_row.grid(row=0, column=2)
        remove_row.grid(row=0, column=3)

        # creates canvas
        self.canvas = CTkCanvas(self, bg=self.cget("fg_color")[1], highlightthickness=0)
        self.canvas.grid(row=1, column=0, columnspan=4, sticky="nsew")
        self.canvas.bind("<Configure>", lambda e: self.load_sample(self.sample))

        # configures resizing
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

    def click(self, row: int, col: int, right: bool = False, planet: Planet = None):
        """
        handles when a bar on the editor is clicked

        :param row: the index of the row that was clicked
        :param col: the index of the column that was clicked
        :param right: determines if the click event was a right click
        :param planet: the planet that was created by the action that will be used in undo/redo actions
        """

        # removes planet when a selected bar is clicked
        tag = f"[{row}, {col}]"
        sample = self.planet_manager.samples[self.sample]
        if sample[row, col] and (not right):
            state = [(self.click, (row, col, right, sample[row, col]), {})]
            self.planet_manager.remove_planet(sample[row, col]) if not planet else None

            # updates state and midi editor
            self.planet_manager.state_manager.add_state({"undo": state, "redo": state}, True) if not planet else None
            self.canvas.itemconfig(tag, fill=self.canvas.cget("bg"))
            sample[row, col] = None

        # updates planet color when a selected bar is right clicked
        elif sample[row, col] and (color := askcolor()[1]):
            undo = [(self.canvas.itemconfig, (tag, ), {"fill": sample[row, col].color})]
            sample[row, col].color = color
            redo = [(self.canvas.itemconfig, (tag,), {"fill": sample[row, col].color})]

            # adds state update and updates color of midi editor
            self.planet_manager.state_manager.add_state({"undo": undo, "redo": redo}, True)
            self.canvas.itemconfig(tag, fill=sample[row, col].color)

        # creates planet when non selected bar is clicked todo add sound and add support for moons
        elif (not sample[row, col]) and (not right):
            # todo adjust radius based on min max size
            r, color, offset = 50 + (row * 10), "#{:06x}".format(randint(0, 0xFFFFFF)), col / len(sample[0])
            sample[row, col] = planet if planet else Planet(len(sample[0]), r, color, None, offset)

            # updates midi color, adds state and planet
            self.canvas.itemconfig(tag, fill=sample[row, col].color)
            state = [(self.click, (row, col, right, sample[row, col]), {})]
            self.planet_manager.add_planet(sample[row, col]) if not planet else None
            self.planet_manager.state_manager.add_state({"undo": state, "redo": state}, True) if not planet else None

    def load_sample(self, sample: str):
        """
        loads a sample into the midi editor

        :param sample: the sample to load
        """

        # handles when sample has not been created yet
        if sample not in self.planet_manager.samples.keys():
            self.planet_manager.samples[sample] = self.DEFAULT_EDITOR

        # loads the sample
        self.canvas.delete("all")
        self.sample = sample
        sample = self.planet_manager.samples[self.sample]
        row_step = (self.canvas.winfo_height() - 1) / len(sample)
        column_step = (self.canvas.winfo_width() - 1) / len(sample[0])

        # draws the blank editor
        for row_num, row in enumerate(sample):
            self.canvas.create_line(0, row_num * row_step, self.winfo_width(), row_num * row_step)
            for col_num, bar in enumerate(row):
                if row_num == 0:
                    self.canvas.create_line(col_num * column_step, 0, col_num * column_step, self.winfo_height())

                # draws bars
                pos = col_num * column_step, row_num * row_step, (col_num + 1) * column_step, (row_num + 1) * row_step
                fill = bar.color if bar else self.canvas.cget("bg")
                tag = self.canvas.create_rectangle(*pos, fill=fill, tags=(f"[{row_num}, {col_num}]", ))
                self.canvas.tag_bind(tag, "<Button-1>", lambda e, i=row_num, j=col_num: self.click(i, j))
                self.canvas.tag_bind(tag, "<Button-3>", lambda e, i=row_num, j=col_num: self.click(i, j, True))

    def modify_editor(self, axis: str, mode: str):
        """
        modifies the dimensions of the editor

        :param axis: the axis to edit 0 for row or 1 for column
        :param mode: how the axis should be edited "add" or "remove"
        """

        # handles adding to the editor
        if mode == "add":
            old_sample = self.planet_manager.samples[self.sample]
            arr = full((len(old_sample), 1), None) if axis == 1 else full((1, len(old_sample[0])), None)
            self.planet_manager.samples[self.sample] = append(old_sample, arr, axis=axis)

            # adds midi state to state manager
            undo = [(setattr, (self, "sample", old_sample), {})]
            redo = [(setattr, (self, "sample", self.planet_manager.samples[self.sample]), {})]
            self.planet_manager.state_manager.add_state({"undo": undo, "redo": redo})
            undo = [(self.load_sample, (old_sample,), {})]
            redo = [(self.load_sample, (self.planet_manager.samples[self.sample],), {})]
            self.planet_manager.state_manager.add_state({"undo": undo, "redo": redo}, True)

        # handles removing from the editor
        else:
            old_sample = self.planet_manager.samples[self.sample]
            pop = old_sample[:, -1] if axis == 1 else old_sample[-1]
            sample = delete(old_sample, len(old_sample[0]) - 1 if axis == 1 else len(old_sample) - 1, axis=axis)
            if sample.size == 0:
                return self.load_sample(self.sample)

            # handles when array is big enough to remove elements
            self.planet_manager.samples[self.sample] = sample
            pop = [elem for elem in pop if elem is not None]

            # adds midi state to state manager
            undo = [(setattr, (self, "sample", old_sample), {})]
            redo = [(setattr, (self, "sample", sample), {})]
            self.planet_manager.state_manager.add_state({"undo": undo, "redo": redo})
            undo = [(self.load_sample, (old_sample,), {})]
            redo = [(self.load_sample, (sample,), {})]
            self.planet_manager.state_manager.add_state({"undo": undo, "redo": redo}, True)

            # removes planets from planet manager and adds manager state to state manager
            undo = [(lambda: [self.planet_manager.add_planet(p, False) for p in pop], (), {})]
            redo = [(lambda: [self.planet_manager.remove_planet(p, False) for p in pop], (), {})]
            self.planet_manager.state_manager.add_state({"undo": undo, "redo": redo}, True)
            for planet in pop:
                self.planet_manager.remove_planet(planet, False)

                # handles updating planet focus
                if planet == self.planet_manager.focused_planet:
                    self.planet_manager.focused_planet = None

        # reloads planets
        self.load_sample(self.sample)
        for row_num, row in enumerate(self.planet_manager.samples[self.sample]):
            for col_num, planet in enumerate(row):
                if not planet:
                    continue

                # gets args
                old_args = (planet.period, planet.radius, planet.color, planet.sound_path, planet.offset)
                # todo adjust radius based on min max size
                new_args = (len(self.planet_manager.samples[self.sample][0]), 50 + (row_num * 10), planet.color,
                            planet.sound_path, (col_num / len(self.planet_manager.samples[self.sample][0])))

                # updates the planet
                tag, state_manager = planet.tag, planet.state_manager
                planet.__init__(*new_args)
                state = {"undo": [(planet.__init__, old_args, {})], "redo": [(planet.__init__, new_args, {})]}
                self.planet_manager.state_manager.add_state(state, True)
