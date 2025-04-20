from os.path import exists
from scipy.io.wavfile import write
from Physics.Planet import Planet
from customtkinter import CTkCanvas, CTkFrame, CTkButton, CTkLabel
from tkinter.colorchooser import askcolor
from numpy import full, append, delete, int16
from random import randint
from math import floor
from librosa import midi_to_note
from librosa.effects import pitch_shift


# noinspection PyPropertyDefinition
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
    """

    DEFAULT_EDITOR = property(lambda self: full((3, 5), None))
    PERIOD_FACTOR = .25

    def __init__(self, *args, **kwargs):
        """
        creates the midi editor

        :param args: the arguments to be passed to the super class
        :param kwargs: the key word arguments to be passed to the super class
        """

        # initializes superclass and canvas fields
        self.planet_manager = kwargs.pop("planet_manager")
        super().__init__(*args, **kwargs)
        self.click_and_drag = 0  # 0 = off, 1 = mode-on, 2 = mode-off
        self.playback_col = 0
        self.sample = "Default (No Audio)"

        # creates pitch column
        self.pitch_labels = []
        pitch = CTkLabel(self, text="Pitch:", font=("Arial", 18))
        pitch.grid(row=0, column=0, sticky="sw", padx=(0, 10))

        # creates buttons
        add_column = CTkButton(self, text="Add Column", command=lambda: self.modify_editor(1, "add"))
        remove_column = CTkButton(self, text="Remove Column", command=lambda: self.modify_editor(1, "remove"))
        add_row = CTkButton(self, text="Add Row", command=lambda: self.modify_editor(0, "add"))
        remove_row = CTkButton(self, text="Remove Row", command=lambda: self.modify_editor(0, "remove"))

        # places buttons
        add_column.grid(row=0, column=1, sticky="ew")
        remove_column.grid(row=0, column=2, sticky="ew")
        add_row.grid(row=0, column=3, sticky="ew")
        remove_row.grid(row=0, column=4, sticky="ew")

        # creates canvas
        self.canvas = CTkCanvas(self, bg=self.cget("fg_color"), highlightthickness=0)
        self.canvas.grid(row=1, column=1, columnspan=4, sticky="nsew")
        self.canvas.bind("<Configure>", lambda e: self.load_sample(self.sample))

        # configures resizing
        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)

    def update_column(self, column_num):
        """
        updates a column to ensure the following:
            --> nothing happens if column is empty
            --> ensures only 1 planet exists
            --> remaining celestial bodies are moons
            --> converts a moon to a planet if no planets exists
            --> planet is at the lowest index

        :param column_num: the index of the column to update
        """

        # gets the column as a 1d array without null values
        column = self.planet_manager.samples[self.sample]["midi_array"][:, column_num]
        moon_period = (len(column)) * MidiEditor.PERIOD_FACTOR
        planet_period = len(self.planet_manager.samples[self.sample]["midi_array"][0])
        column = [elem for elem in column if elem is not None]

        # handles when column is empty
        if not column:
            return

        # ensures first element is a planet
        if type(column[0]) != Planet:
            column[0].convert(planet_period, column_num / planet_period)

        # ensures remaining elements are moons
        for i, elem in enumerate(column[1:]):
            elem.convert(column[0], moon_period, (i * MidiEditor.PERIOD_FACTOR) / moon_period) if type(elem) == Planet \
                else elem.__init__(column[0], elem.period, elem.radius, elem.color, elem.pitch, (
                    i * MidiEditor.PERIOD_FACTOR) / moon_period)
            column[0].moons.append(elem) if elem not in column[0].moons else None

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
        sample = self.planet_manager.samples[self.sample]["midi_array"]

        # Calculate pitch based on row
        pitch = self.planet_manager.samples[self.sample]["pitch"] + row
        if sample[row, col] and (not right):
            state = [(self.click, (row, col, right, sample[row, col]))]
            self.planet_manager.remove_planet(
                sample[row, col], modify_state=self.click_and_drag) if not planet else None

            # updates state and midi editor
            self.planet_manager.state_manager.add_state({"undo": state, "redo": state}, True) if not planet else None
            self.canvas.itemconfig(tag, fill=self.canvas.cget("bg"))
            sample[row, col] = None
            self.update_column(col)

        # updates planet color when a selected bar is right clicked
        elif sample[row, col] and (color := askcolor()[1]):
            undo = [(self.canvas.itemconfig, (tag, ), {"fill": sample[row, col].color})]
            sample[row, col].color = color
            redo = [(self.canvas.itemconfig, (tag,), {"fill": sample[row, col].color})]

            # adds state update and updates color of midi editor
            self.planet_manager.state_manager.add_state({"undo": undo, "redo": redo}, True)
            self.canvas.itemconfig(tag, fill=sample[row, col].color)

        # creates planet when non selected bar is clicked
        elif (not sample[row, col]) and (not right):
            # todo adjust radius based on min max size
            r, color, offset = 50 + (row * 10), "#{:06x}".format(randint(0, 0xFFFFFF)), col / len(sample[0])
            sample_name = self.sample if self.sample != "Default (No Audio)" else None

            # find sample path based on pitch and sample name
            sample_path = f"./AUDIO/user_samples/{sample_name}/{sample_name}_{pitch}.wav"
            if not exists(sample_path) and "shifted_signal_array" in self.planet_manager.samples[self.sample]:

                # Make the pitch shifted file
                steps_to_shift = pitch - self.planet_manager.samples[self.sample]["pitch"]
                signal = self.planet_manager.samples[self.sample]["shifted_signal_array"]
                sr = self.planet_manager.samples[self.sample]["sample_rate"]
                left, right = self.planet_manager.samples[self.sample]["crops"]
                shifted_signal = pitch_shift(y=signal.astype(float),
                                                             sr=sr, 
                                                             n_steps=steps_to_shift)
                write(sample_path, sr, shifted_signal[left:right].astype(int16))

            # updates midi color, adds state and planet
            sample_path = sample_path if "shifted_signal_array" in self.planet_manager.samples[self.sample] else None
            sample[row, col] = planet if planet else Planet(len(sample[0]), r, color, pitch + row, sample_path, offset)
            self.canvas.itemconfig(tag, fill=sample[row, col].color)
            state = [(self.click, (row, col, right, sample[row, col]))]
            self.planet_manager.add_planet(sample[row, col], modify_state=self.click_and_drag) if not planet else None
            self.planet_manager.state_manager.add_state({"undo": state, "redo": state}, True) if not planet else None
            self.update_column(col)

    def load_sample(self, sample: str, update: bool = False):
        """
        loads a sample into the midi editor

        :param sample: the sample to load
        :param update: determines if the load call should be treated as an update so that undo/redo actions don't
            override the display (nothing will happen if requested sample is different from the already loaded sample)
        """

        # handles when call is from undo/redo action
        if update and (self.sample != sample):
            return

        # handles when sample has not been created yet
        if "midi_array" not in self.planet_manager.samples[sample].keys():
            self.planet_manager.samples[sample]["midi_array"] = self.DEFAULT_EDITOR

        # loads the sample
        [label.destroy() for label in self.pitch_labels]
        self.canvas.delete("all")
        self.sample = sample
        sample = self.planet_manager.samples[self.sample]["midi_array"]
        pitch = self.planet_manager.samples[self.sample]["pitch"]
        row_step = (self.canvas.winfo_height() - 1) / len(sample)
        column_step = (self.canvas.winfo_width() - 1) / len(sample[0])

        # draws pitch label
        for row_num, row in enumerate(sample):
            self.pitch_labels.append(CTkLabel(self, text=midi_to_note(pitch + row_num)))
            self.pitch_labels[-1].place(x=10, y=((row_num + .5) * row_step) + self.canvas.winfo_y() - 10)

            # draws bars
            for col_num, bar in enumerate(row):
                pos = col_num * column_step, row_num * row_step, (col_num + 1) * column_step, (row_num + 1) * row_step
                fill = bar.color if bar else self.canvas.cget("bg")
                tag = self.canvas.create_rectangle(*pos, fill=fill, tags=(f"[{row_num}, {col_num}]", ))

                # binds actions to bars
                self.canvas.tag_bind(tag, "<Button-3>", lambda e, i=row_num, j=col_num: self.click(i, j, True))
                self.canvas.tag_bind(tag, "<Button-1>", lambda e, i=row_num, j=col_num: self.click(
                    i, j) if not (e.state & 0x0001 or e.state & 0x0004) else None)
                self.canvas.tag_bind(tag, "<Button-1>", lambda e, i=row_num, j=col_num: self.planet_manager.canvas.
                                     set_focus(sample[i, j], e.state & 0x0004) if e.state & 0x0001 or e.
                                     state & 0x0004 else None, add="+")
                self.canvas.tag_bind(tag, "<Leave>", lambda e, i=row_num, j=col_num: [setattr(self, "click_and_drag", (
                    1 if sample[i, j] else 2) if e.state & 0x0100 and (not (
                        e.state & 0x0001 or e.state & 0x0004)) else 0)])

        # draws playback line and binds click and drag action
        self.canvas.create_line(0, 0, 0, self.canvas.winfo_height(), tags="playback")
        self.canvas.bind("<Motion>", lambda e: self.click(int(e.y // row_step), int(
            e.x // column_step)) if self.click_and_drag and 0 <= e.x < (self.canvas.winfo_width() - 1) and 0 <= e.y < (
                self.canvas.winfo_height() - 1) and bool(sample[int(e.y // row_step), int(e.x // column_step)]) == bool(
            self.click_and_drag == 2) else None)

    def modify_editor(self, axis: str, mode: str):
        """
        modifies the dimensions of the editor

        :param axis: the axis to edit 0 for row or 1 for column
        :param mode: how the axis should be edited "add" or "remove"
        """

        # handles adding to the editor
        old_sample = self.planet_manager.samples[self.sample]["midi_array"]
        undo = [(self.planet_manager.samples[self.sample].update, ({"midi_array": old_sample}, ))]
        if mode == "add":
            arr = full((len(old_sample), 1), None) if axis == 1 else full((1, len(old_sample[0])), None)
            self.planet_manager.samples[self.sample]["midi_array"] = append(old_sample, arr, axis=axis)

            # adds midi state to state manager
            redo = [(self.planet_manager.samples[self.sample].update, (
                {"midi_array": self.planet_manager.samples[self.sample]["midi_array"]}, ))]
            self.planet_manager.state_manager.add_state({"undo": undo, "redo": redo})
            state = [(self.load_sample, (self.sample, True), {})]
            self.planet_manager.state_manager.add_state({"undo": state, "redo": state}, True)

        # handles removing from the editor
        else:
            pop = old_sample[:, -1] if axis == 1 else old_sample[-1]
            sample = delete(old_sample, len(old_sample[0]) - 1 if axis == 1 else len(old_sample) - 1, axis=axis)
            if sample.size == 0:
                return self.load_sample(self.sample)

            # handles when array is big enough to remove elements
            self.planet_manager.samples[self.sample]["midi_array"] = sample
            pop = [elem for elem in pop if elem is not None]

            # adds midi state to state manager
            redo = [(self.planet_manager.samples[self.sample].update, (
                {"midi_array": self.planet_manager.samples[self.sample]["midi_array"]}, ))]
            self.planet_manager.state_manager.add_state({"undo": undo, "redo": redo})
            state = [(self.load_sample, (self.sample, True))]
            self.planet_manager.state_manager.add_state({"undo": state, "redo": state}, True)

            # removes planets from planet manager and adds manager state to state manager
            undo = [(lambda: [self.planet_manager.add_planet(p, False) for p in pop], ())]
            redo = [(lambda: [self.planet_manager.remove_planet(p, False) for p in pop], ())]
            self.planet_manager.state_manager.add_state({"undo": undo, "redo": redo}, True)
            for planet in pop:
                self.planet_manager.remove_planet(planet, False)

        # reloads planets
        self.load_sample(self.sample)
        for row_num, row in enumerate(self.planet_manager.samples[self.sample]["midi_array"]):
            for col_num, planet in enumerate(row):
                if not planet:
                    continue

                # gets args
                old_args = [planet.period, planet.radius, planet.color, planet.pitch, planet.sound_path, planet.offset]
                # todo adjust radius based on min max size
                new_args = [len(self.planet_manager.samples[self.sample]["midi_array"][0]), 50 + (row_num * 10),
                            planet.color, planet.pitch, planet.sound_path,
                            (col_num / len(self.planet_manager.samples[self.sample]["midi_array"][0]))]

                # modifies args when planet is a moon
                if type(planet) != Planet:
                    old_args.pop(4)
                    new_args.pop(4)
                    old_args.insert(0, planet.planet)
                    new_args.insert(0, planet.planet)
                    period = len(self.planet_manager.samples[self.sample]["midi_array"]) - 1
                    new_args[1] = period * MidiEditor.PERIOD_FACTOR
                    new_args[-1] = (row_num * MidiEditor.PERIOD_FACTOR) / new_args[1]

                # updates the planet
                planet.__init__(*new_args)
                state = {"undo": [(planet.__init__, old_args)], "redo": [(planet.__init__, new_args)]}
                self.planet_manager.state_manager.add_state(state, True)

        # reapplies focus
        self.planet_manager.canvas.set_focus(self.planet_manager.focused_planet, False, False)

    def playback(self, t: int):
        """
        moves the playback line across the editor based on how much time has elapsed in the current orbit

        :param t: the amount of time that the bar should be lit up
        """

        # handles when the loaded sample has been deleted
        if self.sample not in self.planet_manager.samples.keys():
            self.planet_manager.set_sample("Default (No Audio)")

        # handles when editor has not been loaded yet
        if "midi_array" not in self.planet_manager.samples[self.sample].keys():
            return

        # moves the slider
        period = self.planet_manager.time_elapsed % len(self.planet_manager.samples[self.sample]["midi_array"][0])
        x = self.canvas.winfo_width() * (period / len(self.planet_manager.samples[self.sample]["midi_array"][0]))
        self.canvas.coords("playback", x, 0, x, self.canvas.winfo_height())

        # handles when bars have already ben lit up this cycle
        if (period >= self.playback_col) and (floor(self.playback_col) == floor(period)):
            self.playback_col = period
            return

        # lights up any bars it passes
        self.playback_col = period
        for row in range(len(self.planet_manager.samples[self.sample]["midi_array"])):
            if planet := self.planet_manager.samples[self.sample]["midi_array"][row, floor(period)]:
                self.canvas.itemconfig(f"[{row}, {floor(period)}]", fill="white")
                self.after(t, lambda r=row, p=planet: self.canvas.itemconfig(
                    f"[{r}, {floor(period)}]", fill=p.color if self.planet_manager.samples[self.sample]["midi_array"][
                        r, floor(period)] else self.canvas.cget("bg")))
