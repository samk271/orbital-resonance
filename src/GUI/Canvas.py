from customtkinter import CTkCanvas
from random import uniform, seed
from numpy import array, floor, ceil, sort, vstack
from numpy.linalg import norm
from Physics import *
from time import perf_counter
from uuid import uuid1


class Canvas(CTkCanvas):
    """
    The canvas that will be used to display the solar system in the prototype with 3 sections of functions
        --> planet functions: functions for drawing/updating the planets
        --> star function: functions for rendering stars in the background
        --> conversion function: converting space to canvas coordinates and vice versa
        --> event handler functions: handles user events such as clicking buttons and keyboard/mouse events
        --> button function: functions for creating/updating the navigation buttons and menu visibility buttons

    Class also contains class properties for modifying how the class will function/look
        --> navigation button properties
        --> state properties
        --> star generation properties
    todo update planet settings when a planet is selected
    todo draw planet orbit paths?
    todo add new, save as, save, load, undo and redo buttons
    """

    # properties for how navigation buttons should look and function
    NAV_BUTTON_FILL = {"fill": "gray50", "outline": "gray50"}
    NAV_BUTTON_RADIUS = 5
    NAV_BUTTON_BORDER = {"width": 2, "fill": "gray23"}
    NAV_BUTTON_CLICKED = {"fill": "gray80", "outline": "gray80"}
    NAV_BUTTON_CLICK_OFFSET = 1
    NAV_BUTTON_CLICK_TIME = 100  # ms
    NAV_BUTTON_REPEAT_DELAY = 600  # ms
    NAV_BUTTON_REPEAT = 30  # ms

    # properties for how much class fields should update when state is updated
    ZOOM_AMT = array([[1.1], [1.005]])  # planet amt, star amt
    POS_AMT = 10
    STAR_POS_FACTOR = .095
    SPEED_FACTOR = 1.1
    DEFAULT_ZOOM_PADDING = 2

    # misc properties for timing and chunk loading
    FPS = 60
    FOCUS_FRAMES = 30
    FOCUS_DRAG_THRESHOLD = 10
    CHUNK_SIZE = 100
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

        # gets kwargs
        if "planet_settings" and "AI_settings" and "planet_manager" in kwargs:
            self.planet_manager = kwargs.pop("planet_manager")
            self.menu_visibility = {"planet": {"menu": kwargs.pop("planet_settings"), "visible": True},
                                    "AI": {"menu": kwargs.pop("AI_settings"), "visible": True}}
        else:
            raise AttributeError("kwargs missing planet_settings, AI_settings or planet_manager")

        # initializes superclass and canvas fields
        super().__init__(*args, **kwargs)
        self.canvas_size = array([self.winfo_width(), self.winfo_height()])
        self.initialized = False
        self.after_update_planets = self.after(int(1000 / Canvas.FPS), self.update_planets)
        self.after_nav = self.after(0, lambda: None)

        # sets event fields
        self.space_position = array([[0.0, 0.0], [0.0, 0.0]])  # planet pos, star pos
        self.zoom = array([[1.0], [1.0]])  # planet amt, star amt
        self.drag_event = array([0.0, 0.0])
        self.drag_amt = 0

        # sets speed fields
        self.speed = 1
        self.dt = perf_counter()

        # sets focus fields
        self.focused_planet = None  # initialized after first resize
        self.focus_frames = 0
        self.focus_step = {"position": array([0, 0]), "zoom": array([[1], [1]])}

        # sets star render fields
        self.star_seed = uuid1()
        self.star_render_range = array([[0, 0], [0, 0]])

        # creates navigation buttons
        width, height = self.canvas_size
        self.create_button(width - 80, height - 120, width - 43, height - 83, "↑", "navigation")
        self.create_button(width - 80, height - 40, width - 43, height - 3, "↓", "navigation")
        self.create_button(width - 120, height - 80, width - 83, height - 43, "←", "navigation")
        self.create_button(width - 40, height - 80, width - 3, height - 43, "→", "navigation")
        self.create_button(width - 40, height - 120, width - 3, height - 83, "⊕", "navigation", (0, -2))
        self.create_button(width - 40, height - 40, width - 3, height - 3, "⊖", "navigation", (0, -2))
        self.create_button(width - 120, height - 120, width - 83, height - 83, "🐇", "navigation")
        self.create_button(width - 120, height - 40, width - 83, height - 3, "🐢", "navigation")
        self.create_button(width - 80, height - 80, width - 43, height - 43, "🏠", "navigation")

        # sets event handlers for clicking navigation buttons
        self.tag_repeat_action("↑", lambda: self.position_event(array([0, -Canvas.POS_AMT])))
        self.tag_repeat_action("↓", lambda: self.position_event(array([0, Canvas.POS_AMT])))
        self.tag_repeat_action("←", lambda: self.position_event(array([-Canvas.POS_AMT, 0])))
        self.tag_repeat_action("→", lambda: self.position_event(array([Canvas.POS_AMT, 0])))
        self.tag_repeat_action("⊕", lambda: self.zoom_event(Canvas.ZOOM_AMT))
        self.tag_repeat_action("⊖", lambda: self.zoom_event(1 / Canvas.ZOOM_AMT))
        self.tag_repeat_action("🐇", lambda: setattr(self, "speed", self.speed * Canvas.SPEED_FACTOR))
        self.tag_repeat_action("🐢", lambda: setattr(self, "speed", self.speed / Canvas.SPEED_FACTOR))
        self.tag_bind("🏠", "<Button-1>", lambda e: self.button_click_animation("🏠"))
        self.tag_bind("🏠", "<Button-1>", lambda e: self.set_focus(self.planet_manager.get_sun(), True), add="+")

        # sets event handlers for releasing navigation buttons
        for tag in ("↑", "↓", "←", "→", "⊕", "⊖", "🐇", "🐢"):
            self.tag_bind(tag, "<ButtonRelease-1>", lambda e: self.after_cancel(self.after_nav))
            self.tag_bind(tag, "<Leave>", lambda e: self.after_cancel(self.after_nav))

        # creates buttons to close and reopen settings menus and binds their functions
        planet_settings = self.create_button(width - 25, 10, width + 17, 47, ">", "planet_settings", (-9, -2))
        AI_settings = self.create_button(10, height - 20, 47, height + 17, "carrot", "AI_settings")
        self.itemconfig(AI_settings, angle=180)
        self.move(AI_settings, 0, -10)
        self.tag_bind(">", "<Button-1>", lambda e: self.button_click_animation(">"))
        self.tag_bind("carrot", "<Button-1>", lambda e: self.button_click_animation("carrot"))
        self.tag_bind(">", "<Button-1>", lambda e: self.menu_visibility_button(planet_settings), add="+")
        self.tag_bind("carrot", "<Button-1>", lambda e: self.menu_visibility_button(AI_settings), add="+")

        # user movement actions
        self.bind("<w>", lambda e: self.position_event(array([0, -Canvas.POS_AMT]), event=e))
        self.bind("<a>", lambda e: self.position_event(array([-Canvas.POS_AMT, 0]), event=e))
        self.bind("<s>", lambda e: self.position_event(array([0, Canvas.POS_AMT]), event=e))
        self.bind("<d>", lambda e: self.position_event(array([Canvas.POS_AMT, 0]), event=e))
        self.bind("<Up>", lambda e: self.position_event(array([0, -Canvas.POS_AMT]), event=e))
        self.bind("<Left>", lambda e: self.position_event(array([-Canvas.POS_AMT, 0]), event=e))
        self.bind("<Down>", lambda e: self.position_event(array([0, Canvas.POS_AMT]), event=e))
        self.bind("<Right>", lambda e: self.position_event(array([Canvas.POS_AMT, 0]), event=e))

        # user zoom actions
        self.bind("<Control-plus>", lambda e: self.zoom_event(Canvas.ZOOM_AMT, e))
        self.bind("<Control-minus>", lambda e: self.zoom_event(1 / Canvas.ZOOM_AMT, e))
        self.bind("<Control-equal>", lambda e: self.zoom_event(Canvas.ZOOM_AMT, e))
        self.bind("<Control-underscore>", lambda e: self.zoom_event(1 / Canvas.ZOOM_AMT, e))
        self.bind("<MouseWheel>", lambda e: self.zoom_event(Canvas.ZOOM_AMT if e.delta > 0 else 1 / Canvas.ZOOM_AMT, e))

        # user speed control actions
        self.bind("<Control-Shift-plus>", lambda e: setattr(self, "speed", self.speed * Canvas.SPEED_FACTOR))
        self.bind("<Control-Shift-minus>", lambda e: setattr(self, "speed", self.speed / Canvas.SPEED_FACTOR))
        self.bind("<Control-Shift-equal>", lambda e: setattr(self, "speed", self.speed * Canvas.SPEED_FACTOR))
        self.bind("<Control-Shift-underscore>", lambda e: setattr(self, "speed", self.speed / Canvas.SPEED_FACTOR))

        # user speed actions
        self.bind("<Control-Shift-plus>", lambda e: setattr(self, "speed", self.speed * Canvas.SPEED_FACTOR))
        self.bind("<Control-Shift-minus>", lambda e: setattr(self, "speed", self.speed / Canvas.SPEED_FACTOR))
        self.bind("<Control-Shift-equal>", lambda e: setattr(self, "speed", self.speed * Canvas.SPEED_FACTOR))
        self.bind("<Control-Shift-underscore>", lambda e: setattr(self, "speed", self.speed / Canvas.SPEED_FACTOR))

        # focus, resize and click and drag actions
        self.bind("<Button-1>", lambda e: self.focus_set())  # todo do this for planet settings
        self.bind("<Configure>", lambda e: self.resize_event(array([e.width, e.height])))
        self.bind("<Button-1>", lambda e: setattr(self, "drag_event", array([e.x, e.y])), add="+")
        self.bind("<Button-1>", lambda e: setattr(self, "drag_amt", 0), add="+")
        self.bind("<B1-Motion>", lambda e: self.position_event(self.drag_event - array([e.x, e.y]), event=e))
        self.bind("<Button-1>", lambda e: setattr(self, "focused_planet", None if (not e.widget.find_withtag(
                "current")) or "stars" in self.gettags(e.widget.find_withtag("current")) else self.focused_planet),
                  add="+")

    # ================================================ PLANET FUNCTIONS ================================================

    def set_focus(self, planet: Planet, zoom: bool = False, smooth: bool = True):
        """
        sets the focus to a given planet:
            --> updates focused planet
            --> updates focus frames
            --> updates focus steps

        :param planet: the planet to focus
        :param zoom: determines if the zoom should be set to default as well as position when focusing
        :param smooth: determines if the focus event should be smooth (only isn't during initial resize event)
        """

        # sets focus on planet
        self.focused_planet = planet
        self.focus_frames = 0 if smooth else Canvas.FOCUS_FRAMES - 1

        # gets required position updates
        frames = Canvas.FOCUS_FRAMES if smooth else 1
        pos_diff = (self.focused_planet.position - self.canvas_to_space(self.canvas_size / 2)[0])
        self.focus_step["position"] = pos_diff / frames

        # gets required zoom updates
        end_planet_zoom = 1 / max((planet.radius / self.canvas_size) * (Canvas.DEFAULT_ZOOM_PADDING + 1) * 2)
        end_zoom = array([[end_planet_zoom], [Canvas.ZOOM_AMT[1, 0]]])
        self.focus_step["zoom"] = (end_zoom / self.zoom) ** (1 / frames) if zoom else array([[1], [1]])
        self.update_planets()

    def maintain_focus(self, old_space_pos: array):
        """
        ensures the focused planet remains in the center of the screen

        :param old_space_pos: the old position of the focused planet, used for smooth focus
        """

        # handles when no planet is focused
        if not self.focused_planet:
            return

        # maintains focus after smooth focus is complete
        space_pos_diff = self.focused_planet.position - old_space_pos
        if self.focus_frames >= Canvas.FOCUS_FRAMES:
            self.position_event(space_pos_diff * self.zoom[0], unfocus=False)

        # handles smooth focus
        else:
            self.zoom_event(self.focus_step["zoom"], render=False)
            self.position_event((self.focus_step["position"] + space_pos_diff) * self.zoom[0], unfocus=False)
            self.focus_frames += 1

        self.draw_stars()

    def update_planets(self):
        """
        applies changes to the planet manger to the view
            --> clears the planet manager deleted buffer and removes planets from the view
            --> clears the planet manager added buffer and adds planets to the view
            --> updates the positioning of the remaining planets
        """

        # cancels the queued update event and schedules the next one
        self.after_cancel(self.after_update_planets)
        self.after_update_planets = self.after(int(1000 / Canvas.FPS), self.update_planets)

        # updates physics and focus
        dt = perf_counter()
        old_pos = self.focused_planet.position.copy() if self.focused_planet else None
        self.planet_manager.update_planet_physics((dt - self.dt) * self.speed)
        self.dt = dt
        self.maintain_focus(old_pos)

        # deletes planets in delete buffer
        for planet in self.planet_manager.get_removed_buffer():
            self.delete(planet.tag)

        # adds newly added planets to the display
        added_buffer = self.planet_manager.get_added_buffer()
        for planet in added_buffer:
            kwargs = {"tags": "planets", "fill": planet.color}
            planet.tag = self.create_oval(0, 0, *([-planet.radius * 2 * self.zoom[0, 0]] * 2), **kwargs)
            self.tag_bind(planet.tag, "<ButtonRelease-1>", lambda e, p=planet: self.set_focus(
                p) if self.drag_amt < Canvas.FOCUS_DRAG_THRESHOLD else None)

        # updates position of all planets
        for planet in self.planet_manager.get_planets():
            bbox = self.bbox(planet.tag)

            # moves planet when it is rendered
            if bbox:
                bbox = array([bbox[2] - bbox[0], bbox[3] - bbox[1]]) / 2
                pos = floor(self.space_to_canvas(planet.position)[0] - bbox)
                self.moveto(planet.tag, pos[0], pos[1])

            # resets bbox if it is removed after large zoom/position events (can happen when home button is clicked)
            else:
                pos = self.space_to_canvas(planet.position)[0]
                radius = planet.radius * self.zoom[0, 0]
                self.coords(planet.tag, *(pos - radius), *(pos + radius))

        # ensures proper leveling of canvas items
        if added_buffer:
            self.tag_lower("planets", "buttons")

    # ================================================= STAR FUNCTIONS =================================================

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
        space_end = ceil(self.canvas_to_space(self.canvas_size)[1] / Canvas.CHUNK_SIZE) * Canvas.CHUNK_SIZE
        space = array([space_start, space_end])

        # loads the chunks that need to be loaded
        chunk_load_difference = Canvas.chunk_difference(space, self.star_render_range)
        for chunks in chunk_load_difference:
            for chunk_x in range(int(chunks[0, 0]), int(chunks[1, 0]), Canvas.CHUNK_SIZE):
                for chunk_y in range(int(chunks[0, 1]), int(chunks[1, 1]), Canvas.CHUNK_SIZE):

                    # prepares seed for chunk so every time it is rendered it renders the same star pattern
                    seed(hash((self.star_seed, chunk_x, chunk_y)))
                    for star in range(Canvas.STARS_PER_CHUNK):

                        # generates stars in the chunk
                        x = uniform(chunk_x, chunk_x + Canvas.CHUNK_SIZE)
                        y = uniform(chunk_y, chunk_y + Canvas.CHUNK_SIZE)
                        x, y = self.space_to_canvas(array([x, y]))[1]
                        kwargs = {"tags": ("stars", f"({chunk_x}, {chunk_y})"), "outline": "white"}
                        self.create_rectangle(x, y, x, y, **kwargs)

        # unloads chunks that are not visible
        for chunks in Canvas.chunk_difference(self.star_render_range, space):
            for chunk_x in range(int(chunks[0, 0]), int(chunks[1, 0]), Canvas.CHUNK_SIZE):
                for chunk_y in range(int(chunks[0, 1]), int(chunks[1, 1]), Canvas.CHUNK_SIZE):
                    self.delete(f"({chunk_x}, {chunk_y})")

        # updates render range and ensures stars are at the bottom
        self.star_render_range = space
        if chunk_load_difference:
            self.tag_lower("stars")

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

    def zoom_event(self, amount: array, event=None, render: bool = True):
        """
        updates the position and zoom level so that the screen zooms in where the user performed the zoom action
            --> updates the zoom amount
            --> updates the position amount to be proportional to the zoom amount
                ** screen will zoom into where the users mouse cursor is on scroll events **
            --> stars will need to be scaled, moved and rendered/un-rendered
            --> planets will need to be scaled, moved and rendered/un-rendered
                ** zoom events will not affect the focused planet **

        ** note that stars are affected by zoom events less than planets are **

        :param amount: how much the screen should zoom
        :param event: the keyboard/mouse event that triggered the state update
        :param render: determines if the event should re-render stars and planets
        """

        # check if the event happened within the canvas bounds
        if event and event.widget != self:
            return

        # gets the position of zoom event
        mouse = self.canvas_size / 2
        if event and event.type == "38" and (not self.focused_planet):
            mouse = array([event.x, event.y])

        # updates zoom and position
        position = (mouse / self.zoom) + self.space_position
        self.zoom *= amount
        position = self.space_to_canvas(position)
        self.space_position += (position - mouse) / self.zoom

        # handles star/planet rendering
        self.scale("planets", mouse[0], mouse[1], amount[0, 0], amount[0, 0])
        self.scale("stars", mouse[0], mouse[1], amount[1, 0], amount[1, 0])

        # ensures infinite recursion does not occur when called from update planets
        if render:
            self.draw_stars() if not self.focused_planet else None
            self.update_planets()

    def position_event(self, amount: array, event=None, unfocus: bool = True):
        """
        updates the display when a position event is triggered
            --> stars will need to be moved and rendered/un-rendered
            --> planets will need to be moved and rendered/un-rendered

        ** note that stars are affected by position events less than planets are **

        :param amount: a numpy array that determines by how much the position should change in the form [dx, dy]
        :param event: the keyboard/mouse event that triggered the state update
        :param unfocus: determines if the position event should set the unfocus the selected planet
        """

        # check if the event happened outside the canvas bounds or happened over a navigation button
        if event and (event.widget != self or "buttons" in self.gettags(event.widget.find_withtag("current"))):
            return

        # handles click and drag events
        if event and event.type == "6":
            self.drag_amt += norm(self.drag_event - array([event.x, event.y]))
            self.drag_event = array([event.x, event.y])

        # handles updating position and star rendering
        amount = vstack((amount, amount * Canvas.STAR_POS_FACTOR))
        self.space_position += (amount / self.zoom)
        self.move("stars", *-amount[1])

        # ensures infinite recursion does not occur when called from update planets
        if unfocus:
            self.focused_planet = None
            self.draw_stars() if not self.focused_planet else None
            self.update_planets()

    def resize_event(self, size: array):
        """
        handles when the user resizes the canvas object
            --> navigation buttons will need to be moved
            --> stars will need to be rendered/un-rendered
            --> planets will need to be updated
                ** resize events will not affect focused planet **

        :param size: the new size of the canvas as a numpy array in the form [width, height]
        """

        # adjusts canvas size
        difference = size - self.canvas_size
        self.canvas_size = size

        # moves canvas objects
        self.move("navigation", *difference)
        self.move("planet_settings", difference[0], 0)
        self.move("AI_settings", 0, difference[1])
        self.position_event(-difference / 2, unfocus=False)
        self.draw_stars() if not self.focused_planet else None
        self.update_planets()

        # handles initial resize event
        if not self.initialized:
            self.initialized = True
            self.set_focus(self.planet_manager.get_sun(), True, False)

    # ==================================================== BUTTONS =====================================================

    def create_button(self, x1: int, y1: int, x2: int, y2: int, text: str, tag: str, text_offset: tuple = (0, 0)):
        """
        creates a button on the canvas with the given parameters
            --> rectangle with rounded edges
            --> text in the center
            --> uses class properties to determine appearance of button

        :param x1: the x coordinate of the top left corner of the rectangle
        :param y1: the y coordinate of the top left corner of the rectangle
        :param x2: the x coordinate of the bottom right corner of the rectangle
        :param y2: the y coordinate of the bottom right corner of the rectangle
        :param text: the text to add to the button
        :param tag: the tag to associate with the navigation button (used in resize events)
        :param text_offset: the offset value to apply to the string so that it is slightly off center

        :return the id of the created text so that it can be mirrored later for settings buttons
        """

        # gets variables for creating button
        radius = Canvas.NAV_BUTTON_RADIUS
        kwargs = {"extent": 90, "style": "arc", "outline": Canvas.NAV_BUTTON_BORDER["fill"], **Canvas.NAV_BUTTON_BORDER}
        center_x = ((x1 + x2) / 2) + text_offset[0]
        center_y = ((y1 + y2) / 2) - text_offset[1]
        center_tag = (text, "buttons", tag, f"center{text}")
        edge_tag = (text, "buttons", tag)

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
        char = text if text != "carrot" else "^"
        text_id = self.create_text(center_x, center_y - 3, text=char, font=("Arial", 20), fill="black", tags=edge_tag)
        return text_id

    def button_click_animation(self, tag: str, hold: bool = False):
        """
        updates attributes of the navigation button so that it looks like it was clicked
            --> changes the color if the button for 100 ms
            --> moves the button SE for 100 ms
            --> uses class properties to determine fill and offset values

        :param tag: a string representing the tag of the navigation button that was clicked
        :param hold: determines if the button is being held

        :return the queued actions to reset the button state (they will be canceled if the button is held)
        """

        # updates the button to the clicked state
        if not hold:
            self.itemconfig("center" + tag, **Canvas.NAV_BUTTON_CLICKED)
            self.move(tag, Canvas.NAV_BUTTON_CLICK_OFFSET, Canvas.NAV_BUTTON_CLICK_OFFSET)
            self.update_idletasks()

        # queues actions to release the button
        return (
            self.after(Canvas.NAV_BUTTON_CLICK_TIME, lambda: self.itemconfig(f"center{tag}", **Canvas.NAV_BUTTON_FILL)),
            self.after(Canvas.NAV_BUTTON_CLICK_TIME, lambda: self.move(tag, *([-Canvas.NAV_BUTTON_CLICK_OFFSET] * 2)))
        )

    def tag_repeat_action(self, tag: str, function):
        """
        generates functions that will be called repeatedly with some delay when a nav button is clicked until the button
        is released

        :param tag: the tag for the nav button
        :param function: the function to call while the button is clicked
        """

        def repeat(after_click: tuple = ()):
            """
            the function for repeating the given action when the button is clicked
                --> button will stay held down
                --> action will occur at faster rate

            :param after_click: the actions for setting the button to the non-clicked state (will be canceled repeatedly
                until user has released the button)
            """

            [self.after_cancel(event) for event in after_click]
            after_click = self.button_click_animation(tag, hold=after_click)
            function()
            self.after_nav = self.after(Canvas.NAV_BUTTON_REPEAT, lambda: repeat(after_click))

        def first_click():
            """
            the function for when the button is first clicked
                --> button will play click animation
                --> action will repeat after a certain delay
            """

            self.button_click_animation(tag)
            function()
            self.after_nav = self.after(Canvas.NAV_BUTTON_REPEAT_DELAY, repeat)

        self.tag_bind(tag, "<Button-1>", lambda e: first_click())

    def menu_visibility_button(self, text_id: int):
        """
        handles clicking the menu visibility buttons
            --> rotates the text on the button 180 degrees to flip the direction of the arrow
            --> toggles the visibility of the settings menu

        :param text_id: the id of the text display
        """

        # mirrors the button text when AI settings visibility button is clicked
        if "AI_settings" in self.gettags(text_id):
            self.itemconfig(text_id, angle=0 if self.menu_visibility["AI"]["visible"] else 180)
            self.move(text_id, 0, 10 if self.menu_visibility["AI"]["visible"] else -10)
            self.menu_visibility["AI"]["visible"] = not self.menu_visibility["AI"]["visible"]

            # toggles the visibility of the menu
            if self.menu_visibility["AI"]["visible"]:
                self.menu_visibility["AI"]["menu"].grid(row=1, column=0, columnspan=2, sticky="nsew")
            else:
                self.menu_visibility["AI"]["menu"].grid_forget()

        # mirrors the button text when planet settings visibility button is clicked
        elif "planet_settings" in self.gettags(text_id):
            self.itemconfig(text_id, angle=180 if self.menu_visibility["planet"]["visible"] else 0)
            self.menu_visibility["planet"]["visible"] = not self.menu_visibility["planet"]["visible"]

            # toggles the visibility of the menu
            if self.menu_visibility["planet"]["visible"]:
                self.menu_visibility["planet"]["menu"].grid(row=0, column=1, sticky="nsew")
            else:
                self.menu_visibility["planet"]["menu"].grid_forget()
