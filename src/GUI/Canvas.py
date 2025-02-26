from customtkinter import CTkCanvas
from random import uniform
from math import floor, ceil


class Canvas(CTkCanvas):
    """
    The canvas that will be used to display the solar system in the prototype  # todo add close/open menu buttons
    todo give stars different zoom level than planets
    todo set focus to planets
    todo its more efficient to move elements rather than delete and redraw them, more efficient to create tag groups
    todo optimize chunk loading/unloading
    """

    # properties for how navigation buttons should look/behave
    NAV_BUTTON_FILL = {"fill": "gray50", "outline": "gray50"}
    NAV_BUTTON_RADIUS = 5
    NAV_BUTTON_BORDER = {"width": 2, "fill": "gray23"}
    NAV_BUTTON_CLICKED = {"fill": "gray80", "outline": "gray80"}
    NAV_BUTTON_CLICKED_OFFSET = 1
    NAV_BUTTON_CLICKED_TIME = 100

    # properties for how much class fields should update when state is updated
    ZOOM_AMT = .1
    POS_AMT = 10

    # properties for how stars should generate
    CHUNK_SIZE = 50
    STARS_PER_CHUNK = 3
    STAR_SIZE = 2

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
        self.stars = {}
        self.sprites = {"planets": [], "stars": []}
        self.drag_event = {"x": 0, "y": 0}
        self.width = self.winfo_width()
        self.height = self.winfo_height()

        # creates navigation buttons
        self.create_nav_button(self.width - 80, self.height - 120, self.width - 43, self.height - 83, "↑")
        self.create_nav_button(self.width - 80, self.height - 40, self.width - 43, self.height - 3, "↓")
        self.create_nav_button(self.width - 120, self.height - 80, self.width - 83, self.height - 43, "←")
        self.create_nav_button(self.width - 40, self.height - 80, self.width - 3, self.height - 43, "→")
        self.create_nav_button(self.width - 40, self.height - 120, self.width - 3, self.height - 83, "⊕")
        self.create_nav_button(self.width - 40, self.height - 40, self.width - 3, self.height - 3, "⊖")
        self.create_nav_button(self.width - 80, self.height - 80, self.width - 43, self.height - 43, "")

        # sets event handlers to navigation buttons
        self.tag_bind("↑", "<Button-1>", lambda event: self.update_state("position", (0, -self.POS_AMT), "↑"))
        self.tag_bind("↓", "<Button-1>", lambda event: self.update_state("position", (0, self.POS_AMT), "↓"))
        self.tag_bind("←", "<Button-1>", lambda event: self.update_state("position", (-self.POS_AMT, 0), "←"))
        self.tag_bind("→", "<Button-1>", lambda event: self.update_state("position", (self.POS_AMT, 0), "→"))
        self.tag_bind("⊕", "<Button-1>", lambda event: self.update_state("zoom", self.ZOOM_AMT, "⊕"))
        self.tag_bind("⊖", "<Button-1>", lambda event: self.update_state("zoom", -self.ZOOM_AMT, "⊖"))

        # binds user actions to functions
        self.bind("<Configure>", lambda event: self.resize(event.width, event.height))
        self.bind("<Button-1>", lambda event: self.focus_set())  # todo do this for planet settings
        self.master.bind("<w>", lambda event: self.update_state("position", (0, -self.POS_AMT), event=event))
        self.master.bind("<a>", lambda event: self.update_state("position", (-self.POS_AMT, 0), event=event))
        self.master.bind("<s>", lambda event: self.update_state("position", (0, self.POS_AMT), event=event))
        self.master.bind("<d>", lambda event: self.update_state("position", (self.POS_AMT, 0), event=event))
        self.master.bind("<Up>", lambda event: self.update_state("position", (0, -self.POS_AMT), event=event))
        self.master.bind("<Left>", lambda event: self.update_state("position", (-self.POS_AMT, 0), event=event))
        self.master.bind("<Down>", lambda event: self.update_state("position", (0, self.POS_AMT), event=event))
        self.master.bind("<Right>", lambda event: self.update_state("position", (self.POS_AMT, 0), event=event))
        self.master.bind("<MouseWheel>", lambda event: self.update_state("zoom", event.delta, event=event))
        self.master.bind("<Control-plus>", lambda event: self.update_state("zoom", self.ZOOM_AMT, event=event))
        self.master.bind("<Control-minus>", lambda event: self.update_state("zoom", -self.ZOOM_AMT, event=event))
        self.master.bind("<Control-equal>", lambda event: self.update_state("zoom", self.ZOOM_AMT, event=event))
        self.master.bind("<Control-underscore>", lambda event: self.update_state("zoom", -self.ZOOM_AMT, event=event))
        self.bind("<ButtonPress-1>", lambda event: self.drag_event.update({"x": event.x, "y": event.y}))
        self.bind("<B1-Motion>", lambda event: self.update_state("position", None, event=event))

    def draw_planets(self, planets):
        """
        clears the current screen and redraws all of the planets at their new positions

        :param planets: a list of all the planets objects to draw
        """

    def draw_stars(self):
        """
        generates new stars if the player "loads" more of the map that was not previously visible in a chunk based manor
        additionally unloads stars if they are outside of the players view
        """

        # gets the sizing of the canvas in space coordinates
        start_x = floor(self.position[0] / Canvas.CHUNK_SIZE) * Canvas.CHUNK_SIZE
        start_y = floor(self.position[1] / Canvas.CHUNK_SIZE) * Canvas.CHUNK_SIZE
        end_x = ceil(((self.width * (1 / self.zoom)) + self.position[0]) /
                     Canvas.CHUNK_SIZE) * Canvas.CHUNK_SIZE
        end_y = ceil(((self.height * (1 / self.zoom)) + self.position[1]) /
                     Canvas.CHUNK_SIZE) * Canvas.CHUNK_SIZE

        # iterates over every chunk that is visible
        visible_chunks = set()
        for x in range(start_x, end_x, Canvas.CHUNK_SIZE):
            for y in range(start_y, end_y, Canvas.CHUNK_SIZE):
                visible_chunks.add((x, y))

                # generates new stars
                if (x, y) not in self.stars:
                    self.stars[(x, y)] = [(uniform(x, x + Canvas.CHUNK_SIZE), uniform(y, y + Canvas.CHUNK_SIZE))
                                          for _ in range(Canvas.STARS_PER_CHUNK)]

        # unloads chunks that are not visible
        loaded_chunks = set(self.stars.keys())
        for chunk in loaded_chunks - visible_chunks:
            self.stars.pop(chunk)

        # deletes previous stars
        self.delete(*self.sprites["stars"])
        self.sprites["stars"].clear()

        # draws new stars
        for chunk in self.stars.values():
            for star in chunk:
                pos = self.convert_coordinates(star)
                self.sprites["stars"].append(self.create_oval(*pos, pos[0] + Canvas.STAR_SIZE,
                                                              pos[1] + Canvas.STAR_SIZE, fill="white"))

        # ensures navigation buttons are not blocked
        self.tag_raise("navigation")

    def convert_coordinates(self, coordinates):
        """
        converts coordinates representing a position in space to coordinates representing a position on the canvas

        :param coordinates: the given coordinates representing the position in space in the format (x, y)

        :return: the converted coordinates representing a position on the canvas in the format (x, y)
        """

        x = (coordinates[0] - self.position[0]) * self.zoom
        y = (coordinates[1] - self.position[1]) * self.zoom
        return x, y

    def zoom_event(self, amount, event=None):
        """
        updates the position and zoom level so that the screen zooms in where the user performed the zoom action

        :param amount: how much the screen should zoom
        :param event: the mouse event that triggered the zoom, if a navigation button was clicked this will be None and
            the zoom will be applied to the center of the screen
        """

        # gets the center of the screen
        mouse_x = self.width / 2
        mouse_y = self.height / 2

        # handles when event is given
        if event and event.type == "38":
            mouse_x = event.x
            mouse_y = event.y

        # converts mouse position to space coordinates
        x = (mouse_x / self.zoom) + self.position[0]
        y = (mouse_y / self.zoom) + self.position[1]

        # applies zoom and converts back to canvas coordinates
        self.zoom *= amount
        x, y = self.convert_coordinates((x, y))

        # adjusts the position so zoom is applied to mouse position
        self.position = (
            self.position[0] + (x - mouse_x) / self.zoom,
            self.position[1] + (y - mouse_y) / self.zoom
        )

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

        # handles click and drag events
        if event and event.type == "6":
            amount = (self.drag_event["x"] - event.x, self.drag_event["y"] - event.y)
            self.drag_event.update({"x": event.x, "y": event.y})

        # changes button color
        if button:
            self.itemconfig("center" + button, **Canvas.NAV_BUTTON_CLICKED)
            self.after(Canvas.NAV_BUTTON_CLICKED_TIME, lambda: self.itemconfig(
                "center" + button, **Canvas.NAV_BUTTON_FILL
            ))

            # shifts button position
            self.move(button, Canvas.NAV_BUTTON_CLICKED_OFFSET, Canvas.NAV_BUTTON_CLICKED_OFFSET)
            self.after(Canvas.NAV_BUTTON_CLICKED_TIME, lambda: self.move(
                button, -Canvas.NAV_BUTTON_CLICKED_OFFSET, -Canvas.NAV_BUTTON_CLICKED_OFFSET
            ))
            self.update()

        # handles updating state
        if value == "position":
            self.position = (self.position[0] + (amount[0] / self.zoom), self.position[1] + (amount[1] / self.zoom))
        elif value == "zoom":
            self.zoom_event(1 + self.ZOOM_AMT if amount > 0 else 1 - self.ZOOM_AMT, event)
        self.draw_stars()

    def resize(self, width, height):
        """
        handles when the user resizes the canvas object
            --> navigation buttons will need to be moved
            --> stars will need to be deleted/added
            --> planets will need to be deleted/added

        :param width: the new width of the canvas
        :param height: the new height of the canvas
        """

        # shifts the navigation buttons
        self.move("navigation", width - self.width, height - self.height)
        self.width = width
        self.height = height

        # redraws stars
        self.draw_stars()

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
        radius = Canvas.NAV_BUTTON_RADIUS
        kwargs = {"extent": 90, "style": "arc", "outline": Canvas.NAV_BUTTON_BORDER["fill"], **Canvas.NAV_BUTTON_BORDER}
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        center = (text, "navigation", "center" + text) if text != "" else "navigation"
        edge = (text, "navigation") if text != "" else "navigation"
        return [

            # draws the corners
            self.create_oval(x1, y1, x1 + radius * 2, y1 + radius * 2, **Canvas.NAV_BUTTON_FILL, tags=center),
            self.create_oval(x2 - radius * 2, y1, x2, y1 + radius * 2, **Canvas.NAV_BUTTON_FILL, tags=center),
            self.create_oval(x1, y2 - radius * 2, x1 + radius * 2, y2, **Canvas.NAV_BUTTON_FILL, tags=center),
            self.create_oval(x2 - radius * 2, y2 - radius * 2, x2, y2, **Canvas.NAV_BUTTON_FILL, tags=center),

            # draws the remainder of the rectangle
            self.create_rectangle(x1 + radius, y1, x2 - radius, y2, **Canvas.NAV_BUTTON_FILL, tags=center),
            self.create_rectangle(x1, y1 + radius, x1 + radius * 2, y2 - radius, **Canvas.NAV_BUTTON_FILL, tags=center),
            self.create_rectangle(x2 - radius * 2, y1 + radius, x2, y2 - radius, **Canvas.NAV_BUTTON_FILL, tags=center),

            # draws rounded borders
            self.create_arc(x1, y1, x1 + radius * 2, y1 + radius * 2, start=90, **kwargs, tags=edge),
            self.create_arc(x2 - radius * 2, y1, x2, y1 + radius * 2, start=0, **kwargs, tags=edge),
            self.create_arc(x1, y2 - radius * 2, x1 + radius * 2, y2, start=180, **kwargs, tags=edge),
            self.create_arc(x2 - radius * 2, y2 - radius * 2, x2, y2, start=270, **kwargs, tags=edge),

            # draws straight borders
            self.create_line(x1 + radius, y1, x2 - radius, y1, **Canvas.NAV_BUTTON_BORDER, tags=edge),
            self.create_line(x1 + radius, y2, x2 - radius, y2, **Canvas.NAV_BUTTON_BORDER, tags=edge),
            self.create_line(x1, y1 + radius, x1, y2 - radius, **Canvas.NAV_BUTTON_BORDER, tags=edge),
            self.create_line(x2, y1 + radius, x2, y2 - radius, **Canvas.NAV_BUTTON_BORDER, tags=edge),

            # draws text
            self.create_text(center_x, center_y - 3, text=text, font=("Arial", 20), fill="black", tags=edge)
        ]
