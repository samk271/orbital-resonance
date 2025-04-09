from Physics.Planet import Planet
from customtkinter import CTkCanvas
from numpy import array, delete, full
from random import randint


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

    DEFAULT_EDITOR = property(lambda self: full((5, 10), None))

    def __init__(self, *args, **kwargs):
        """
        creates the midi editor

        :param args: the arguments to be passed to the super class
        :param kwargs: the key word arguments to be passed to the super class
        """

        # initializes superclass and canvas fields
        super().__init__(*args, **kwargs)
        self.sample: array = None
        self.bind("<Configure>", lambda e: self.load_editor(self.sample))

    def click(self, row: int, col: int, right: bool = False):
        """
        handles when a bar on the editor is clicked
        
        :param row: the index of the row that was clicked
        :param col: the index of the column that was clicked
        :param right: determines if the click event was a right click
        """

        # handles when a selected bar is clicked
        if self.sample[row, col] and (not right):
            self.itemconfig(f"[{row}, {col}]", fill=self.cget("bg"))

        # handles when a non selected bar is clicked
        if (not self.sample[row, col]) and (not right):
            self.itemconfig(f"[{row}, {col}]", fill="#{:06x}".format(randint(0, 0xFFFFFF)))

    def load_editor(self, sample: array):
        """
        loads a sample into the midi editor

        :param sample: the sample to load
        """

        # loads the sample
        self.delete("all")
        self.sample = sample if sample is not None else self.DEFAULT_EDITOR
        row_step = self.winfo_height() / len(self.sample)
        column_step = self.winfo_width() / len(self.sample[0])

        # draws the blank editor
        for row_num, row in enumerate(self.sample):
            self.create_line(0, row_num * row_step, self.winfo_width(), row_num * row_step)
            for col_num, bar in enumerate(row):
                if row_num == 0:
                    self.create_line(col_num * column_step, 0, col_num * column_step, self.winfo_height())

                # draws bars
                pos = col_num * column_step, row_num * row_step, (col_num + 1) * column_step, (row_num + 1) * row_step
                fill = bar.color if bar else self.cget("bg")
                tag = self.create_rectangle(*pos, fill=fill, tags=(f"[{row_num}, {col_num}]", ))
                self.tag_bind(tag, "<Button-1>", lambda e, i=row_num, j=col_num: self.click(i, j))
                self.tag_bind(tag, "<Button-3>", lambda e, i=row_num, j=col_num: self.click(i, j, True))


from customtkinter import CTk
m = MidiEditor(CTk())
m.pack(fill="both", expand=True)
m.master.mainloop()
