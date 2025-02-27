from customtkinter import CTkCanvas
from random import uniform
from math import floor, ceil
from numpy import array


class Canvas(CTkCanvas):
    """
    The canvas that will be used to display the solar system in the prototype with 3 sections of functions
        --> view model controller functions: handles displaying changes in the model to the view
        --> event handler functions: handles user events such as clicking buttons and keyboard/mouse events
        --> navigation button function: functions for creating/updating the navigation buttons

    Class also contains class properties for modifying how the class will function/look
        --> navigation button properties
        --> state properties
        --> star generation properties
    todo add close/open menu buttons
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
            --> creates navigation buttons
            --> binds navigation buttons to position/zoom event handler functions
            --> binds wasd and arrow keys to position event handler function
            --> binds mouse wheel and +- keys to zoom handler functions
            --> binds click and drag to position handler functions
            --> binds resize and focus event functions

        :param args: the arguments to be passed to the super class
        :param kwargs: the key word arguments to be passed to the super class
        """

        # initializes superclass and fields
        super().__init__(*args, **kwargs)
        self.position = array([0.0, 0.0])
        self.zoom = 1
        self.drag_event = array([0.0, 0.0])
        self.dimensions = array([self.winfo_width(), self.winfo_height()])
        self.stars = {}

        # creates navigation buttons
        width, height = self.dimensions
        self.create_nav_button(width - 80, height - 120, width - 43, height - 83, "↑")
        self.create_nav_button(width - 80, height - 40, width - 43, height - 3, "↓")
        self.create_nav_button(width - 120, height - 80, width - 83, height - 43, "←")
        self.create_nav_button(width - 40, height - 80, width - 3, height - 43, "→")
        self.create_nav_button(width - 40, height - 120, width - 3, height - 83, "⊕")
        self.create_nav_button(width - 40, height - 40, width - 3, height - 3, "⊖")
        self.create_nav_button(width - 80, height - 80, width - 43, height - 43, "")

        # sets event handlers to navigation buttons
        self.tag_bind("↑", "<Button-1>", lambda e: self.position_event(array([0, -self.POS_AMT])), add="+")
        self.tag_bind("↓", "<Button-1>", lambda e: self.position_event(array([0, self.POS_AMT])), add="+")
        self.tag_bind("←", "<Button-1>", lambda e: self.position_event(array([-self.POS_AMT, 0])), add="+")
        self.tag_bind("→", "<Button-1>", lambda e: self.position_event(array([self.POS_AMT, 0])), add="+")
        self.tag_bind("⊕", "<Button-1>", lambda e: self.zoom_event(self.ZOOM_AMT), add="+")
        self.tag_bind("⊖", "<Button-1>", lambda e: self.zoom_event(-self.ZOOM_AMT), add="+")

        # user movement actions
        self.master.bind("<w>", lambda e: self.position_event(array([0, -self.POS_AMT]), event=e))
        self.master.bind("<a>", lambda e: self.position_event(array([-self.POS_AMT, 0]), event=e))
        self.master.bind("<s>", lambda e: self.position_event(array([0, self.POS_AMT]), event=e))
        self.master.bind("<d>", lambda e: self.position_event(array([self.POS_AMT, 0]), event=e))
        self.master.bind("<Up>", lambda e: self.position_event(array([0, -self.POS_AMT]), event=e))
        self.master.bind("<Left>", lambda e: self.position_event(array([-self.POS_AMT, 0]), event=e))
        self.master.bind("<Down>", lambda e: self.position_event(array([0, self.POS_AMT]), event=e))
        self.master.bind("<Right>", lambda e: self.position_event(array([self.POS_AMT, 0]), event=e))

        # user zoom actions
        self.master.bind("<MouseWheel>", lambda e: self.zoom_event(self.ZOOM_AMT if e.delta > 0 else -self.ZOOM_AMT, e))
        self.master.bind("<Control-plus>", lambda e: self.zoom_event(self.ZOOM_AMT, e))
        self.master.bind("<Control-minus>", lambda e: self.zoom_event(-self.ZOOM_AMT, e))
        self.master.bind("<Control-equal>", lambda e: self.zoom_event(self.ZOOM_AMT, e))
        self.master.bind("<Control-underscore>", lambda e: self.zoom_event(-self.ZOOM_AMT, e))

        # focus, resize and click and drag actions
        self.bind("<Button-1>", lambda e: self.focus_set())  # todo do this for planet settings
        self.bind("<Configure>", lambda e: self.resize_event(array([e.width, e.height])))
        self.bind("<Button-1>", lambda e: self.__setattr__("drag_event", array([e.x, e.y])), add="+")
        self.bind("<B1-Motion>", lambda e: self.position_event(self.drag_event - array([e.x, e.y]), event=e))

    # ============================================== VIEW MODEL CONTROLLER =============================================

    def draw_planets(self):
        """
        applies changes to the planet manger to the view
        """

    def draw_stars(self):
        """
        generates new stars if the player "loads" more of the map that was not previously visible in a chunk based manor
        additionally unloads stars if they are outside of the players view
        """

        # gets the sizing of the canvas in space coordinates
        start_x = floor(self.position[0] / Canvas.CHUNK_SIZE) * Canvas.CHUNK_SIZE
        start_y = floor(self.position[1] / Canvas.CHUNK_SIZE) * Canvas.CHUNK_SIZE
        end_x = ceil(((self.dimensions[0] * (1 / self.zoom)) + self.position[0]) /
                     Canvas.CHUNK_SIZE) * Canvas.CHUNK_SIZE
        end_y = ceil(((self.dimensions[1] * (1 / self.zoom)) + self.position[1]) /
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
        self.delete("stars")

        # draws new stars
        for chunk in self.stars.values():
            for star in chunk:
                pos = self.convert_coordinates(star)
                self.create_oval(*pos, pos[0] + Canvas.STAR_SIZE, pos[1] + Canvas.STAR_SIZE, fill="white", tags="stars")

        # ensures navigation buttons are not blocked
        self.tag_raise("navigation")

    def convert_coordinates(self, coordinates):
        """
        converts coordinates representing a position in space to coordinates representing a position on the canvas

        :param coordinates: a numpy array representing the position in space in the format [x, y]

        :return: a numpy array representing the converted coordinates in the canvas in the format [x, y]
        """

        return (coordinates - self.position) * self.zoom

    # ================================================= EVENT HANDLERS =================================================

    def zoom_event(self, amount, event=None):
        """
        updates the position and zoom level so that the screen zooms in where the user performed the zoom action

        :param amount: how much the screen should zoom
        :param event: the keyboard/mouse event that triggered the state update
        """

        # check if the event happened within the canvas bounds
        if event and event.widget != self:
            return

        # gets the position of zoom event
        mouse = self.dimensions / 2
        if event and event.type == "38":
            mouse = array([event.x, event.y])

        # updates zoom and position
        position = (mouse / self.zoom) + self.position
        self.zoom *= 1 + amount
        position = self.convert_coordinates(position)
        self.position += (position - mouse) / self.zoom

        # handles star/planet rendering
        self.draw_stars()
        self.draw_planets()

    def position_event(self, amount: array, event=None):
        """
        updates the display when a position event is triggered
            --> stars will need to be moved and rendered/un-rendered
            --> planets will need to be moved and rendered/un-rendered

        :param amount: a numpy array that determines by how much the position should change in the form [dx, dy]
        :param event: the keyboard/mouse event that triggered the state update
        """

        # check if the event happened within the canvas bounds
        if event and event.widget != self:
            return

        # handles click and drag events
        if event and event.type == "6":
            self.drag_event = array([event.x, event.y])

        # handles updating position and star/planet rendering
        self.position += (amount / self.zoom)
        self.draw_stars()
        self.draw_planets()

    def resize_event(self, size: array):
        """
        handles when the user resizes the canvas object
            --> navigation buttons will need to be moved
            --> stars will need to be rendered/un-rendered
            --> planets will need to be rendered/un-rendered

        :param size: the new size of the canvas as a numpy array in the form [width, height]
        """

        # shifts the navigation buttons
        self.move("navigation", *(size - self.dimensions))
        self.dimensions = size

        # redraws stars
        self.draw_stars()
        self.draw_planets()

    # =============================================== NAVIGATION BUTTONS ===============================================

    def create_nav_button(self, x1: int, y1: int, x2: int, y2: int, text: str):
        """
        creates a navigation button on the canvas with the given parameters
            --> rectangle with rounded edges
            --> text in the center
            --> binds handle_nav_button to click event to update button appearance when clicked
            --> note: functionality set with tag_bind function with add="+" arg
            --> uses class properties to determine appearance of button

        :param x1: the x coordinate of the top left corner of the rectangle
        :param y1: the y coordinate of the top left corner of the rectangle
        :param x2: the x coordinate of the bottom right corner of the rectangle
        :param y2: the y coordinate of the bottom right corner of the rectangle
        :param text: the text to add to the button
        """

        # gets variables for creating button
        radius = Canvas.NAV_BUTTON_RADIUS
        kwargs = {"extent": 90, "style": "arc", "outline": Canvas.NAV_BUTTON_BORDER["fill"], **Canvas.NAV_BUTTON_BORDER}
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        center_tag = (text, "navigation", f"center{text}") if text != "" else "navigation"
        edge_tag = (text, "navigation") if text != "" else "navigation"

        # draws the rounded corners
        self.create_oval(x1, y1, x1 + radius * 2, y1 + radius * 2, **Canvas.NAV_BUTTON_FILL, tags=center_tag),
        self.create_oval(x2 - radius * 2, y1, x2, y1 + radius * 2, **Canvas.NAV_BUTTON_FILL, tags=center_tag),
        self.create_oval(x1, y2 - radius * 2, x1 + radius * 2, y2, **Canvas.NAV_BUTTON_FILL, tags=center_tag),
        self.create_oval(x2 - radius * 2, y2 - radius * 2, x2, y2, **Canvas.NAV_BUTTON_FILL, tags=center_tag),

        # draws the remainder of the rounded rectangle
        self.create_rectangle(x1 + radius, y1, x2 - radius, y2, **Canvas.NAV_BUTTON_FILL, tags=center_tag),
        self.create_rectangle(x1, y1 + radius, x1 + radius * 2, y2 - radius, **Canvas.NAV_BUTTON_FILL, tags=center_tag),
        self.create_rectangle(x2 - radius * 2, y1 + radius, x2, y2 - radius, **Canvas.NAV_BUTTON_FILL, tags=center_tag),

        # draws rounded borders
        self.create_arc(x1, y1, x1 + radius * 2, y1 + radius * 2, start=90, **kwargs, tags=edge_tag),
        self.create_arc(x2 - radius * 2, y1, x2, y1 + radius * 2, start=0, **kwargs, tags=edge_tag),
        self.create_arc(x1, y2 - radius * 2, x1 + radius * 2, y2, start=180, **kwargs, tags=edge_tag),
        self.create_arc(x2 - radius * 2, y2 - radius * 2, x2, y2, start=270, **kwargs, tags=edge_tag),

        # draws straight borders
        self.create_line(x1 + radius, y1, x2 - radius, y1, **Canvas.NAV_BUTTON_BORDER, tags=edge_tag),
        self.create_line(x1 + radius, y2, x2 - radius, y2, **Canvas.NAV_BUTTON_BORDER, tags=edge_tag),
        self.create_line(x1, y1 + radius, x1, y2 - radius, **Canvas.NAV_BUTTON_BORDER, tags=edge_tag),
        self.create_line(x2, y1 + radius, x2, y2 - radius, **Canvas.NAV_BUTTON_BORDER, tags=edge_tag),

        # draws text and sets click event handler
        self.create_text(center_x, center_y - 3, text=text, font=("Arial", 20), fill="black", tags=edge_tag)
        if text != "":
            self.tag_bind(text, "<Button-1>", lambda e: self.handle_nav_button(text))

    def handle_nav_button(self, tag: str):
        """
        updates attributes of the navigation button so that it looks like it was clicked
            --> changes the color if the button for 100 ms
            --> moves the button SE for 100 ms
            --> uses class properties to determine fill and offset values

        :param tag: a string representing the tag of the navigation button that was clicked
        """

        # updates the button color
        self.itemconfig("center" + tag, **Canvas.NAV_BUTTON_CLICKED)
        self.after(Canvas.NAV_BUTTON_CLICKED_TIME, lambda: self.itemconfig(f"center{tag}", **Canvas.NAV_BUTTON_FILL))

        # shifts button position
        self.move(tag, Canvas.NAV_BUTTON_CLICKED_OFFSET, Canvas.NAV_BUTTON_CLICKED_OFFSET)
        self.after(Canvas.NAV_BUTTON_CLICKED_TIME, lambda: self.move(tag, *([-Canvas.NAV_BUTTON_CLICKED_OFFSET] * 2)))
        self.update()
