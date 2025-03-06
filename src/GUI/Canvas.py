from customtkinter import CTkCanvas
from random import uniform
from numpy import array, floor, ceil, sort, round, vstack
from Physics import PlanetManager


class Canvas(CTkCanvas):
    """
    The canvas that will be used to display the solar system in the prototype with 3 sections of functions
        --> planet functions: functions for drawing/updating the planets
        --> star function: functions for rendering stars in the background
        --> conversion function: converting space to canvas coordinates and vice versa
        --> event handler functions: handles user events such as clicking buttons and keyboard/mouse events
        --> navigation button function: functions for creating/updating the navigation buttons

    Class also contains class properties for modifying how the class will function/look
        --> navigation button properties
        --> state properties
        --> star generation properties
    todo add close/open menu buttons
    todo set focus to planets
    todo draw planet orbit paths?
    todo planet position currently based on bbox, use center instead?
    """

    # properties for how navigation buttons should look/behave
    NAV_BUTTON_FILL = {"fill": "gray50", "outline": "gray50"}
    NAV_BUTTON_RADIUS = 5
    NAV_BUTTON_BORDER = {"width": 2, "fill": "gray23"}
    NAV_BUTTON_CLICKED = {"fill": "gray80", "outline": "gray80"}
    NAV_BUTTON_CLICKED_OFFSET = 1
    NAV_BUTTON_CLICKED_TIME = 100

    # properties for how much class fields should update when state is updated and frames per second
    ZOOM_AMT = array([[1.1], [1.005]])  # planet amt, star amt
    POS_AMT = 10
    STAR_POS_FACTOR = .095
    FPS = 60

    # properties for how stars should generate
    CHUNK_SIZE = 50
    STARS_PER_CHUNK = 3

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

        # gets the planet manager from the kwargs
        if "planet_manger" in kwargs:
            self.planet_manager = kwargs["planet_manager"]
            kwargs.pop("planet_manager")
        else:
            self.planet_manager = PlanetManager()

        # initializes superclass and fields
        super().__init__(*args, **kwargs)
        self.space_position = array([[0.0, 0.0], [0.0, 0.0]])  # planet pos, star pos
        self.zoom = array([[1.0], [1.0]])  # planet amt, star amt
        self.drag_event = array([0.0, 0.0])
        self.canvas_dimensions = array([self.winfo_width(), self.winfo_height()])
        self.star_render_range = array([[0, 0], [0, 0]])
        self.after(int(1000 / Canvas.FPS), self.update_planets)

        # creates navigation buttons
        width, height = self.canvas_dimensions
        self.create_nav_button(width - 80, height - 120, width - 43, height - 83, "↑")
        self.create_nav_button(width - 80, height - 40, width - 43, height - 3, "↓")
        self.create_nav_button(width - 120, height - 80, width - 83, height - 43, "←")
        self.create_nav_button(width - 40, height - 80, width - 3, height - 43, "→")
        self.create_nav_button(width - 40, height - 120, width - 3, height - 83, "⊕")
        self.create_nav_button(width - 40, height - 40, width - 3, height - 3, "⊖")
        self.create_nav_button(width - 80, height - 80, width - 43, height - 43, "🏠")  # todo set home function to focus sun

        # sets event handlers to navigation buttons
        self.tag_bind("↑", "<Button-1>", lambda e: self.position_event(array([0, -Canvas.POS_AMT])), add="+")
        self.tag_bind("↓", "<Button-1>", lambda e: self.position_event(array([0, Canvas.POS_AMT])), add="+")
        self.tag_bind("←", "<Button-1>", lambda e: self.position_event(array([-Canvas.POS_AMT, 0])), add="+")
        self.tag_bind("→", "<Button-1>", lambda e: self.position_event(array([Canvas.POS_AMT, 0])), add="+")
        self.tag_bind("⊕", "<Button-1>", lambda e: self.zoom_event(1), add="+")
        self.tag_bind("⊖", "<Button-1>", lambda e: self.zoom_event(-1), add="+")

        # user movement actions
        self.master.bind("<w>", lambda e: self.position_event(array([0, -Canvas.POS_AMT]), event=e))
        self.master.bind("<a>", lambda e: self.position_event(array([-Canvas.POS_AMT, 0]), event=e))
        self.master.bind("<s>", lambda e: self.position_event(array([0, Canvas.POS_AMT]), event=e))
        self.master.bind("<d>", lambda e: self.position_event(array([Canvas.POS_AMT, 0]), event=e))
        self.master.bind("<Up>", lambda e: self.position_event(array([0, -Canvas.POS_AMT]), event=e))
        self.master.bind("<Left>", lambda e: self.position_event(array([-Canvas.POS_AMT, 0]), event=e))
        self.master.bind("<Down>", lambda e: self.position_event(array([0, Canvas.POS_AMT]), event=e))
        self.master.bind("<Right>", lambda e: self.position_event(array([Canvas.POS_AMT, 0]), event=e))

        # user zoom actions
        self.master.bind("<MouseWheel>", lambda e: self.zoom_event(e.delta, e))
        self.master.bind("<Control-plus>", lambda e: self.zoom_event(1, e))
        self.master.bind("<Control-minus>", lambda e: self.zoom_event(-1, e))
        self.master.bind("<Control-equal>", lambda e: self.zoom_event(1, e))
        self.master.bind("<Control-underscore>", lambda e: self.zoom_event(-1, e))

        # focus, resize and click and drag actions
        self.bind("<Button-1>", lambda e: self.focus_set())  # todo do this for planet settings
        self.bind("<Configure>", lambda e: self.resize_event(array([e.width, e.height])))
        self.bind("<Button-1>", lambda e: self.__setattr__("drag_event", array([e.x, e.y])), add="+")
        self.bind("<B1-Motion>", lambda e: self.position_event(self.drag_event - array([e.x, e.y]), event=e))

    # ============================================== VIEW MODEL CONTROLLER =============================================

    def update_planets(self):
        """
        applies changes to the planet manger to the view
            --> clears the planet manager deleted buffer and removes planets from the view
            --> clears the planet manager added buffer and adds planets to the view
            --> updates the positioning of the remaining planets
        """

        # deletes planets in delete buffer
        for planet in self.planet_manager.get_removed_buffer():
            self.delete(planet.tag)

        # adds newly added planets to the display
        for planet in self.planet_manager.get_added_buffer():
            kwargs = {"tags": "planets", "fill": planet.color}
            planet.tag = self.create_oval(0, 0, *([-planet.radius * self.zoom[0, 0]] * 2), **kwargs)

        # updates position of all planets
        for planet in self.planet_manager.get_planets():
            x, y = round(self.space_to_canvas(planet.position))[0]
            self.moveto(planet.tag, x, y)

        # ensures proper leveling of canvas items and queues next frame/physics update
        self.tag_raise("planets")
        self.tag_raise("navigation")
        self.after(int(1000 / Canvas.FPS), self.update_planets)
        self.planet_manager.update_planet_physics(int(1000 / Canvas.FPS))

    @staticmethod
    def chunk_difference(chunks1: array, chunks2: array):
        """
        takes 2 sets of chunks and finds the chunks that are in chunk 1 but not in chunk 2

        :param chunks1: a numpy array representing the corners of chunks 1 in the form [[xmin, ymin], [xmax, ymax]]
        :param chunks2: a numpy array representing the corners of chunks 2 in the form [[xmin, ymin], [xmax, ymax]]
        :return: a generator function for the range of chunks that are in chunk 1 but not chunk 2
        """

        # gets the min and max x and y values of the 2 chunks
        chunks1 = sort(chunks1, axis=0)
        chunks2 = sort(chunks2, axis=0)
        x_min1, y_min1 = chunks1[0]
        x_max1, y_max1 = chunks1[1]
        x_min2, y_min2 = chunks2[0]
        x_max2, y_max2 = chunks2[1]

        # finds the region of overlap
        x_min_overlap = max(x_min1, x_min2)
        x_max_overlap = min(x_max1, x_max2)
        y_min_overlap = max(y_min1, y_min2)
        y_max_overlap = min(y_max1, y_max2)

        # handles no overlap
        if x_min_overlap >= x_max_overlap or y_min_overlap >= y_max_overlap:
            return [chunks1]

        # gets all of the regions that are in chunk 1 but not chunk 2
        difference = []
        if x_min1 < x_min_overlap:
            difference.append(array([[x_min1, y_min1], [x_min_overlap, y_max1]]))
        if x_max_overlap < x_max1:
            difference.append(array([[x_max_overlap, y_min1], [x_max1, y_max1]]))
        if y_max_overlap < y_max1:
            difference.append(array([[x_min_overlap, y_max_overlap], [x_max_overlap, y_max1]]))
        if y_min1 < y_min_overlap:
            difference.append(array([[x_min_overlap, y_min1], [x_max_overlap, y_min_overlap]]))

        return difference

    def draw_stars(self):
        """
        generates new stars if the player "loads" more of the map that was not previously visible in a chunk based manor
        additionally unloads stars if they are outside of the players view
        """

        # gets the sizing of the canvas in space coordinates
        space_start = floor(self.space_position[1] / Canvas.CHUNK_SIZE) * Canvas.CHUNK_SIZE
        space_end = ceil(self.canvas_to_space(self.canvas_dimensions)[1] / Canvas.CHUNK_SIZE) * Canvas.CHUNK_SIZE
        space = array([space_start, space_end])

        # loads the chunks that need to be loaded
        for chunks in Canvas.chunk_difference(space, self.star_render_range):
            for chunk_x in range(int(chunks[0, 0]), int(chunks[1, 0]),  Canvas.CHUNK_SIZE):
                for chunk_y in range(int(chunks[0, 1]), int(chunks[1, 1]),  Canvas.CHUNK_SIZE):
                    for star in range(Canvas.STARS_PER_CHUNK):

                        # generates stars in the chunk
                        x = uniform(chunk_x, chunk_x + Canvas.CHUNK_SIZE)
                        y = uniform(chunk_y, chunk_y + Canvas.CHUNK_SIZE)
                        x, y = self.space_to_canvas(array([x, y]))[1]
                        kwargs = {"tags": ("stars", f"({chunk_x}, {chunk_y})"), "outline": "white"}
                        self.create_rectangle(x, y, x, y, **kwargs)

        # unloads chunks that are not visible
        for chunks in Canvas.chunk_difference(self.star_render_range, space):
            for chunk_x in range(int(chunks[0, 0]), int(chunks[1, 0]),  Canvas.CHUNK_SIZE):
                for chunk_y in range(int(chunks[0, 1]), int(chunks[1, 1]),  Canvas.CHUNK_SIZE):
                    self.delete(f"({chunk_x}, {chunk_y})")

        # updates render range and ensure navigation buttons are on top
        self.star_render_range = space
        self.tag_raise("navigation")

    # =================================================== CONVERSIONS ==================================================

    def space_to_canvas(self, coordinates: array):
        """
        converts coordinates representing a position in space to coordinates representing a position on the canvas

        :param coordinates: a numpy array representing the position in space in the format [x, y]
            ** note: format [[xp, yp], [xs, ys]] is used in zoom events to update the position of both planet and star
                coordinate systems at the same time **

        :return: a numpy array representing the converted coordinates in the canvas in the format [[xp, yp], [xs, ys]]
            where the first array uses planet zoom level and the second array uses star zoom level
        """

        return (coordinates - self.space_position) * self.zoom

    def canvas_to_space(self, coordinates: array):
        """
        converts coordinates representing a position on the canvas to coordinates representing a position in space

        :param coordinates: a numpy array representing the position in the canvas in the format [x, y]

        :return: a numpy array representing the converted coordinates in space in the format [[xp, yp], [xs, ys]]
            where the first array uses planet zoom level and the second array uses star zoom level
        """

        return (coordinates / self.zoom) + self.space_position

    # ================================================= EVENT HANDLERS =================================================

    def zoom_event(self, amount: float, event=None):
        """
        updates the position and zoom level so that the screen zooms in where the user performed the zoom action

        :param amount: how much the screen should zoom
        :param event: the keyboard/mouse event that triggered the state update
        """

        # check if the event happened within the canvas bounds
        if event and event.widget != self:
            return

        # gets the position of zoom event
        mouse = self.canvas_dimensions / 2
        if event and event.type == "38":
            mouse = array([event.x, event.y])

        # updates zoom and position
        amount = Canvas.ZOOM_AMT if amount > 0 else 1 / Canvas.ZOOM_AMT
        position = (mouse / self.zoom) + self.space_position
        self.zoom *= amount
        position = self.space_to_canvas(position)
        self.space_position += (position - mouse) / self.zoom

        # handles star/planet rendering
        self.scale("planets", mouse[0], mouse[1], amount[0, 0], amount[0, 0])
        self.scale("stars", mouse[0], mouse[1], amount[1, 0], amount[1, 0])
        self.draw_stars()

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

        # handles updating position and star rendering
        amount = vstack((amount, amount * Canvas.STAR_POS_FACTOR))
        self.space_position += (amount / self.zoom)
        self.move("planets", *-amount[0])
        self.move("stars", *-amount[1])
        self.draw_stars()

    def resize_event(self, size: array):
        """
        handles when the user resizes the canvas object
            --> navigation buttons will need to be moved
            --> stars will need to be rendered/un-rendered

        :param size: the new size of the canvas as a numpy array in the form [width, height]
        """

        self.move("navigation", *(size - self.canvas_dimensions))
        self.canvas_dimensions = size
        self.draw_stars()

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
        center_tag = (text, "navigation", f"center{text}")
        edge_tag = (text, "navigation")

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
        self.update_idletasks()
