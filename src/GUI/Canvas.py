from customtkinter import CTkCanvas


class Canvas(CTkCanvas):
    """
    The canvas that will be used to display the solar system in the prototype
    """

    # properties for how navigation buttons should look/behave
    NAV_BUTTON_FILL = {"fill": "gray50", "outline": "gray50"}
    NAV_BUTTON_RADIUS = 5
    NAV_BUTTON_BORDER = {"width": 2, "fill": "gray23"}
    NAV_BUTTON_CLICKED = {"fill": "gray80", "outline": "gray80"}
    NAV_BUTTON_CLICKED_OFFSET = 1
    NAV_BUTTON_CLICKED_TIME = 100

    # properties for how much class fields should update when state is updated
    ZOOM_AMT = .25
    POS_AMT = 100

    def __init__(self, *args, **kwargs):
        """
        creates the canvas widget

        :param args: the arguments to be passed to the super class
        :param kwargs: the key word arguments to be passed to the super class
        """

        # initializes superclass and fields
        super().__init__(*args, **kwargs)
        self.zoom = 1
        self.position = (0, 0)
        self.sprites = {"planets": [], "stars": [], "navigation": []}

        # binds user actions to functions
        self.bind("<Configure>", lambda event: self.resize(event.width, event.height))
        self.bind("<Button-1>", lambda event: self.focus_set())  # todo do this for all settings windows
        self.master.bind("<w>", lambda event: self.update_state("position", (0, -self.POS_AMT), event=event))
        self.master.bind("<a>", lambda event: self.update_state("position", (-self.POS_AMT, 0), event=event))
        self.master.bind("<s>", lambda event: self.update_state("position", (0, self.POS_AMT), event=event))
        self.master.bind("<d>", lambda event: self.update_state("position", (self.POS_AMT, 0), event=event))
        self.master.bind("<Up>", lambda event: self.update_state("position", (0, -self.POS_AMT), event=event))
        self.master.bind("<Left>", lambda event: self.update_state("position", (-self.POS_AMT, 0), event=event))
        self.master.bind("<Down>", lambda event: self.update_state("position", (0, self.POS_AMT), event=event))
        self.master.bind("<Right>", lambda event: self.update_state("position", (self.POS_AMT, 0), event=event))
        self.master.bind("<MouseWheel>", lambda event: self.update_state("zoom", event.delta, event=event))
        self.master.bind("<KeyPress-+>", lambda event: self.update_state("zoom", self.ZOOM_AMT, event=event))
        self.master.bind("<KeyPress-->", lambda event: self.update_state("zoom", -self.ZOOM_AMT, event=event))

    def draw_all(self, planets):
        """
        clears the current screen and redraws all of the planets at their new positions

        :param planets: a list of all the planets objects to draw
        """

    def draw_stars(self):
        """
        draws generated stars to the screen as the background for the canvas
        """

    def unload_stars(self):
        """
        deletes all of the chunks of stars that are not visible on the screen
        """

    def load_stars(self):
        """
        generates new stars if the player "loads" more of the map that was not previously visible in a chunk based manor
        """

    def convert_coordinates(self, coordinates):
        """
        converts coordinates representing a position in space to coordinates representing a position on the canvas

        :param coordinates: the given coordinates representing the position in space in the format (x, y)

        :return: the converted coordinates representing a position on the canvas in the format (x, y)
        """

        x = coordinates[0] + self.position[0]
        y = coordinates[1] + self.position[1]

        return x, y

    def resize(self, width, height):
        """
        handles when the user resizes the canvas object
            --> navigation buttons will need to be redrawn
            --> stars will need to be deleted/added
            --> planets will need to be deleted/added

        :param width: the new width of the canvas
        :param height: the new height of the canvas
        """

        # creates navigation buttons
        self.delete(*self.sprites["navigation"])
        up = self.create_nav_button(width - 80, height - 120, width - 43, height - 83, "↑")
        down = self.create_nav_button(width - 80, height - 40, width - 43, height - 3, "↓")
        left = self.create_nav_button(width - 120, height - 80, width - 83, height - 43, "←")
        right = self.create_nav_button(width - 40, height - 80, width - 3, height - 43, "→")
        center = self.create_nav_button(width - 80, height - 80, width - 43, height - 43, "")
        zoom_in = self.create_nav_button(width - 40, height - 120, width - 3, height - 83, "⊕")
        zoom_out = self.create_nav_button(width - 40, height - 40, width - 3, height - 3, "⊖")
        self.sprites["navigation"] = up + down + left + right + center + zoom_in + zoom_out

        # sets event handlers to navigation buttons
        for tag in up:
            self.tag_bind(tag, "<Button-1>", lambda event: self.update_state("position", (0, -self.POS_AMT), up))
        for tag in down:
            self.tag_bind(tag, "<Button-1>", lambda event: self.update_state("position", (0, self.POS_AMT), down))
        for tag in left:
            self.tag_bind(tag, "<Button-1>", lambda event: self.update_state("position", (-self.POS_AMT, 0), left))
        for tag in right:
            self.tag_bind(tag, "<Button-1>", lambda event: self.update_state("position", (self.POS_AMT, 0), right))
        for tag in zoom_in:
            self.tag_bind(tag, "<Button-1>", lambda event: self.update_state("zoom", self.ZOOM_AMT, zoom_in))
        for tag in zoom_out:
            self.tag_bind(tag, "<Button-1>", lambda event: self.update_state("zoom", -self.ZOOM_AMT, zoom_out))

    def update_state(self, value, amount, button=None, event=None):
        """
        handles when the position or zoom state needs to be updated: when the user clicks navigation buttons or
        inputs certain keyboard/mouse actions

        :param value: determines if the position or zoom value should be updated
        :param amount: determines by how much the value should change in either (dx, dy) or dv based on given value
        :param button: the navigation button that was pressed that triggered the state update
        :param event: the keyboard/mouse event that triggered the state update
        """

        # check if the event happened within the canvas bounds
        if event and event.widget != self:
            return

        # check if event happened because of navigation button
        if button:
            for i, tag in enumerate(button):

                # changes button color
                if i < 7:
                    self.itemconfig(tag, **self.NAV_BUTTON_CLICKED)
                    self.after(self.NAV_BUTTON_CLICKED_TIME, lambda element_tag=tag: self.itemconfig(
                        element_tag, **self.NAV_BUTTON_FILL))

                # shifts button position
                self.move(tag, self.NAV_BUTTON_CLICKED_OFFSET, self.NAV_BUTTON_CLICKED_OFFSET)
                self.after(self.NAV_BUTTON_CLICKED_TIME, lambda element_tag=tag: self.move(
                    element_tag, -self.NAV_BUTTON_CLICKED_OFFSET, -self.NAV_BUTTON_CLICKED_OFFSET))

        # handles updating state
        if value == "position":
            self.position = (self.position[0] + amount[0], self.position[1] + amount[1])
        elif value == "zoom":
            self.zoom += (amount / abs(amount)) * self.ZOOM_AMT

    def create_nav_button(self, x1, y1, x2, y2, text):
        """
        creates a navigation button on the canvas with the given parameters

        :param x1: the x coordinate of the first corner of the rectangle
        :param y1: the y coordinate of the first corner of the rectangle
        :param x2: the x coordinate of the second corner of the rectangle
        :param y2: the y coordinate of the second corner of the rectangle
        :param text: the text to add to the button
        
        :return the tags of all the shapes used to create the rounded rectangle
        """

        # gets variables for creating button
        radius = self.NAV_BUTTON_RADIUS
        kwargs = {"extent": 90, "style": "arc", "outline": self.NAV_BUTTON_BORDER["fill"], **self.NAV_BUTTON_BORDER}
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        return [

            # draws the corners
            self.create_oval(x1, y1, x1 + radius * 2, y1 + radius * 2, **self.NAV_BUTTON_FILL),
            self.create_oval(x2 - radius * 2, y1, x2, y1 + radius * 2, **self.NAV_BUTTON_FILL),
            self.create_oval(x1, y2 - radius * 2, x1 + radius * 2, y2, **self.NAV_BUTTON_FILL),
            self.create_oval(x2 - radius * 2, y2 - radius * 2, x2, y2, **self.NAV_BUTTON_FILL),

            # draws the remainder of the rectangle
            self.create_rectangle(x1 + radius, y1, x2 - radius, y2, **self.NAV_BUTTON_FILL),
            self.create_rectangle(x1, y1 + radius, x1 + radius * 2, y2 - radius, **self.NAV_BUTTON_FILL),
            self.create_rectangle(x2 - radius * 2, y1 + radius, x2, y2 - radius, **self.NAV_BUTTON_FILL),

            # draws rounded borders
            self.create_arc(x1, y1, x1 + radius * 2, y1 + radius * 2, start=90, **kwargs),
            self.create_arc(x2 - radius * 2, y1, x2, y1 + radius * 2, start=0, **kwargs),
            self.create_arc(x1, y2 - radius * 2, x1 + radius * 2, y2, start=180, **kwargs),
            self.create_arc(x2 - radius * 2, y2 - radius * 2, x2, y2, start=270, **kwargs),

            # draws straight borders
            self.create_line(x1 + radius, y1, x2 - radius, y1, **self.NAV_BUTTON_BORDER),
            self.create_line(x1 + radius, y2, x2 - radius, y2, **self.NAV_BUTTON_BORDER),
            self.create_line(x1, y1 + radius, x1, y2 - radius, **self.NAV_BUTTON_BORDER),
            self.create_line(x2, y1 + radius, x2, y2 - radius, **self.NAV_BUTTON_BORDER),

            # draws text
            self.create_text(center_x, center_y, text=text, font=("Arial", 20), fill="black")
        ]
