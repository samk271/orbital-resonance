from Physics.Planet import Planet
from Physics.Moon import Moon
from Physics.PlanetManager import PlanetManager
from customtkinter import CTkCanvas
from tkinter.messagebox import askokcancel
from random import uniform, seed
from numpy import array, floor, ceil, sort, vstack
from numpy.linalg import norm
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

    # properties for how tooltips should look and function
    TOOLTIP_FILL = {"fill": "gray50", "outline": "black"}
    TOOLTIP_HOVER_TIME = 750

    # properties for how much class fields should update when state is updated
    ZOOM_AMT = array([[1.1], [1.003]])  # planet amt, star amt
    POS_AMT = 10
    STAR_POS_FACTOR = .05
    SPEED_FACTOR = 1.1
    DEFAULT_ZOOM_PADDING = 2

    # misc properties for timing and chunk loading
    FPS = 60
    FPS = int(1000 / FPS) if int(1000 / FPS) != 0 else 1  # calculated ms between frames don't change this value
    FOCUS_FRAMES = 30
    FOCUS_DRAG_THRESHOLD = 10
    CHUNK_SIZE = 200
    STARS_PER_CHUNK = 3
    TRIGGER_SIZE = .25

    def __init__(self, *args, **kwargs):
        """
        creates the canvas widget
            --> creates navigation buttons
            --> binds navigation buttons to position/zoom event handler functions
            --> binds wasd and arrow keys to position event handler function
            --> binds mouse wheel to zoom handler functions
            --> binds click and drag to position handler functions
            --> binds resize and focus event functions

        :param args: the arguments to be passed to the super class
        :param kwargs: the key word arguments to be passed to the super class
        """

        # gets kwargs
        self.file_manager = kwargs.pop("file_manager")
        self.planet_manager: PlanetManager = kwargs.pop("planet_manager")
        self.planet_manager.canvas = self
        self.menu_visibility = {"planet": {"menu": kwargs.pop("planet_settings"), "visible": True},
                                "AI": {"menu": kwargs.pop("AI_settings"), "visible": True}}

        # initializes superclass and canvas fields
        super().__init__(*args, **kwargs)
        self.canvas_size = array([self.winfo_width(), self.winfo_height()])
        self.initialized = False
        self.after_click = self.after(0, lambda: None)
        self.after_tooltip = self.after(0, lambda: None)

        # sets event fields
        self.space_position = array([[0.0, 0.0], [0.0, 0.0]])  # planet pos, star pos
        self.zoom = array([[1.0], [1.0]])  # planet amt, star amt
        self.drag_event = array([0.0, 0.0])
        self.drag_amt = 0

        # sets speed fields
        self.speed = 1
        self.dt = perf_counter()

        # sets focus fields
        self.focus_frames = 0
        self.focus_step = {"position": array([0, 0]), "zoom": array([[1], [1]])}

        # sets star render fields
        self.star_seed = uuid1()
        self.star_render_range = array([[0, 0], [0, 0]])

        # creates navigation buttons
        width, height = self.canvas_size
        self.create_button((width - 80, height - 120, width - 43, height - 83), "↑", "navigation", "Up")
        self.create_button((width - 80, height - 40, width - 43, height - 3), "↓", "navigation", "Down")
        self.create_button((width - 120, height - 80, width - 83, height - 43), "←", "navigation", "Left")
        self.create_button((width - 40, height - 80, width - 3, height - 43), "→", "navigation", "Right")
        self.create_button((width - 40, height - 120, width - 3, height - 83), "⊕", "navigation", "Zoom In", (0, -2, 1))
        self.create_button((width - 40, height - 40, width - 3, height - 3), "⊖", "navigation", "Zoom Out", (0, -2, 1))
        self.create_button((width - 120, height - 120, width - 83, height - 83), "🐇", "navigation", "Speed Up")
        self.create_button((width - 120, height - 40, width - 83, height - 3), "🐢", "navigation", "Slow Down")
        self.create_button((width - 80, height - 80, width - 43, height - 43), "🏠", "navigation", "Home")

        # sets event handlers for clicking navigation buttons
        self.tag_repeat_action("↑", lambda: self.position_event(array([0, -Canvas.POS_AMT])))
        self.tag_repeat_action("↓", lambda: self.position_event(array([0, Canvas.POS_AMT])))
        self.tag_repeat_action("←", lambda: self.position_event(array([-Canvas.POS_AMT, 0])))
        self.tag_repeat_action("→", lambda: self.position_event(array([Canvas.POS_AMT, 0])))
        self.tag_repeat_action("⊕", lambda: self.zoom_event(Canvas.ZOOM_AMT))
        self.tag_repeat_action("⊖", lambda: self.zoom_event(1 / Canvas.ZOOM_AMT))
        self.tag_repeat_action("🐇", lambda: setattr(self, "speed", self.speed * Canvas.SPEED_FACTOR))
        self.tag_repeat_action("🐢", lambda: setattr(self, "speed", self.speed / Canvas.SPEED_FACTOR))
        self.tag_bind("🏠", "<Button-1>", lambda e: self.button_click_animation("🏠"), add="+")
        self.tag_bind("🏠", "<Button-1>", lambda e: self.set_focus(self.planet_manager.get_sun(), True), add="+")

        # creates buttons to close and reopen settings menus and binds their functions
        right_menu = self.create_button((width - 25, 10, width + 17, 47), ">", "planet_settings", "Hide", (-9, -2, 1))
        bottom_menu = self.create_button((10, height - 20, 47, height + 17), "carrot", "AI_settings", "Hide")
        self.itemconfig(bottom_menu, angle=180)
        self.move(bottom_menu, 0, -10)
        self.tag_bind(">", "<Button-1>", lambda e: self.button_click_animation(">"), add="+")
        self.tag_bind("carrot", "<Button-1>", lambda e: self.button_click_animation("carrot"), add="+")
        self.tag_bind(">", "<Button-1>", lambda e: self.menu_visibility_buttons(right_menu), add="+")
        self.tag_bind("carrot", "<Button-1>", lambda e: self.menu_visibility_buttons(bottom_menu), add="+")

        # creates file menu buttons
        self.create_button((3, 3, 36, 36), "🆕", "File", "New", (0, 0, .75))
        self.create_button((36, 3, 69, 36), "📂", "File", "Load", (0, 0, .75))
        self.create_button((69, 3, 102, 36), "💾", "File", "Save", (0, 0, .75))
        self.create_button((102, 3, 135, 36), "📑", "File", "Save As", (0, 0, .75))
        self.create_button((135, 3, 168, 36), "↩", "File", "Undo", (0, -5, 1.3))
        self.create_button((168, 3, 201, 36), "↪", "File", "Redo", (0, -5, 1.3))
        self.tag_raise("tooltips")

        # sets event handlers for clicking file menu buttons
        self.tag_bind("🆕", "<Button-1>", lambda e: self.after(0, lambda: self.file_buttons("🆕")), add="+")
        self.tag_bind("📂", "<Button-1>", lambda e: self.after(0, lambda: self.file_buttons("📂")), add="+")
        self.tag_bind("📑", "<Button-1>", lambda e: self.after(0, lambda: self.file_buttons("📑")), add="+")
        self.tag_repeat_action("↩", lambda: self.planet_manager.state_manager.undo())
        self.tag_repeat_action("↪", lambda: self.planet_manager.state_manager.redo())
        self.tag_repeat_action("💾", lambda: self.after(0, lambda: self.file_manager.save(self)))

        # user movement actions
        self.bind("<Up>", lambda e: self.position_event(array([0, -Canvas.POS_AMT]), event=e))
        self.bind("<Left>", lambda e: self.position_event(array([-Canvas.POS_AMT, 0]), event=e))
        self.bind("<Down>", lambda e: self.position_event(array([0, Canvas.POS_AMT]), event=e))
        self.bind("<Right>", lambda e: self.position_event(array([Canvas.POS_AMT, 0]), event=e))

        # misc actions
        self.bind("<MouseWheel>", lambda e: self.zoom_event(Canvas.ZOOM_AMT if e.delta > 0 else 1 / Canvas.ZOOM_AMT, e))
        self.bind("<Configure>", lambda e: self.resize_event(array([e.width, e.height])))
        self.bind("<Button-1>", lambda e: setattr(self, "drag_event", array([e.x, e.y])))
        self.bind("<Button-1>", lambda e: setattr(self, "drag_amt", 0), add="+")
        self.bind("<B1-Motion>", lambda e: self.position_event(self.drag_event - array([e.x, e.y]), event=e))

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

        # handles when planet is being unfocused (planet is None)
        self.planet_manager._focused_planet = planet
        if not planet:
            return

        # makes planet visible
        self.tag_raise(planet.tag) if planet.tag else None
        self.tag_lower(planet.tag, "buttons") if planet.tag else None
        self.focus_frames = 0 if smooth else Canvas.FOCUS_FRAMES - 1

        # gets required position updates
        frames = Canvas.FOCUS_FRAMES if smooth else 1
        pos_diff = (self.planet_manager.focused_planet.position - self.canvas_to_space(self.canvas_size / 2)[0])
        self.focus_step["position"] = pos_diff / frames

        # gets required zoom updates
        end_planet_zoom = 1 / max((planet.radius / self.canvas_size) * (Canvas.DEFAULT_ZOOM_PADDING + 1) * 2)
        end_zoom = array([[end_planet_zoom], [Canvas.ZOOM_AMT[1, 0]]])
        self.focus_step["zoom"] = (end_zoom / self.zoom) ** (1 / frames) if zoom else array([[1], [1]])

    def maintain_focus(self, old_space_pos: array):
        """
        ensures the focused planet remains in the center of the screen

        :param old_space_pos: the old position of the focused planet, used for smooth focus
        """

        # handles when no planet is focused
        if not self.planet_manager.focused_planet:
            return

        # maintains focus after smooth focus is complete
        space_pos_diff = self.planet_manager.focused_planet.position - old_space_pos
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

        # schedules the next frame and updates the midi editor
        self.after(Canvas.FPS, self.update_planets)
        self.menu_visibility["AI"]["menu"].midi.playback(Canvas.NAV_BUTTON_CLICK_TIME)

        # updates physics and focus
        dt = perf_counter()
        old_pos = self.planet_manager.focused_planet.position.copy() if self.planet_manager.focused_planet else None
        triggered = self.planet_manager.update_planet_physics((dt - self.dt) * self.speed)
        self.dt = dt
        self.maintain_focus(old_pos)

        # deletes planets in delete buffer
        for planet in self.planet_manager.get_removed_buffer():
            self.delete(planet.tag, f"path {planet.tag}", f"trigger {planet.tag}")

        # adds newly added planets to the display
        added_buffer = self.planet_manager.get_added_buffer()
        for planet in added_buffer:

            # draws moon orbit path
            if type(planet) == Moon:
                p1 = self.space_to_canvas(planet.planet.position + array([planet.orbital_radius] * 2))[0]
                p2 = self.space_to_canvas(planet.planet.position + array([-planet.orbital_radius] * 2))[0]
                self.create_oval(*p1, *p2, outline="gray", width=1, tags=("paths", f"path {planet.tag}"))

            # draws orbit path
            elif planet != self.planet_manager.get_sun():
                p1 = self.space_to_canvas(array([planet.orbital_radius] * 2))[0]
                p2 = self.space_to_canvas(array([-planet.orbital_radius] * 2))[0]
                self.create_oval(*p1, *p2, outline="gray", width=1, tags=("paths", f"path {planet.tag}"))

                # draws sound trigger
                p1 = self.space_to_canvas(array([0, -planet.orbital_radius + (planet.radius * Canvas.TRIGGER_SIZE)]))[0]
                p2 = self.space_to_canvas(array([0, -planet.orbital_radius - (planet.radius * Canvas.TRIGGER_SIZE)]))[0]
                self.create_line(*p1, *p2, fill="gray", width=1, tags=("triggers", f"trigger {planet.tag}"))

            # binds click function to planet
            self.tag_bind(planet.tag, "<ButtonRelease-1>", lambda e, p=planet: self.set_focus(
                p, e.state & 0x0004) if self.drag_amt < Canvas.FOCUS_DRAG_THRESHOLD else None)

        # updates planet state
        for planet in self.planet_manager.planets:
            if planet.update:
                added_buffer = True
                self.itemconfig(planet.tag, fill=planet.color)
                planet.update = False

                # updates path
                p1 = self.space_to_canvas(array([planet.orbital_radius] * 2))[0]
                p2 = self.space_to_canvas(array([- planet.orbital_radius] * 2))[0]
                self.coords(f"path {planet.tag}", *p1, *p2)

                # updates trigger
                p1 = self.space_to_canvas(array([0, -planet.orbital_radius + (planet.radius * Canvas.TRIGGER_SIZE)]))[0]
                p2 = self.space_to_canvas(array([0, -planet.orbital_radius - (planet.radius * Canvas.TRIGGER_SIZE)]))[0]
                self.coords(f"trigger {planet.tag}", *p1, *p2)
                if type(planet) == Planet and (not self.find_withtag(f"trigger {planet.tag}")):
                    self.create_line(*p1, *p2, fill="gray", width=1, tags=("triggers", f"trigger {planet.tag}"))

                # handles drawing planet shape
                self.delete(planet.tag)
                pos = self.space_to_canvas(planet.position)[0]
                radius = planet.radius * self.zoom[0, 0]

                # circle shape
                if planet.shape == "Circle":
                    args = (pos[0] - radius, pos[1] - radius, pos[0] + radius, pos[1] + radius)
                    self.create_oval(*args, fill=planet.color, tags=("planets", planet.tag))

                # square shape
                elif planet.shape == "Square":
                    args = (pos[0] - radius, pos[1] - radius, pos[0] + radius, pos[1] + radius)
                    self.create_rectangle(*args, fill=planet.color, tags=("planets", planet.tag))

                # triangle shape
                elif planet.shape == "Triangle":
                    args = (pos[0], pos[1] - radius, pos[0] - radius, pos[1] + radius, pos[0] + radius, pos[1] + radius)
                    self.create_polygon(*args, fill=planet.color, tags=("planets", planet.tag))

                # rectangle shape
                elif planet.shape == "Rectangle":
                    args = (pos[0] - radius, pos[1] - radius / 2, pos[0] + radius, pos[1] + radius / 2)
                    self.create_rectangle(*args, fill=planet.color, tags=("planets", planet.tag))

            # moves planet
            bbox = self.bbox(planet.tag)
            bbox = array([bbox[2] - bbox[0], bbox[3] - bbox[1]]) / 2
            pos = floor(self.space_to_canvas(planet.position)[0] - bbox)
            self.moveto(planet.tag, pos[0], pos[1])

            # moves planet moon path
            if type(planet) == Moon:
                p1 = self.space_to_canvas(planet.planet.position + array([planet.orbital_radius] * 2))[0]
                p2 = self.space_to_canvas(planet.planet.position + array([-planet.orbital_radius] * 2))[0]
                self.coords(f"path {planet.tag}", *p1, *p2)

        # updates color of triggered planets
        for planet in triggered:
            self.itemconfig(planet.tag, fill="white")
            self.after(Canvas.NAV_BUTTON_CLICK_TIME, lambda p=planet: self.itemconfig(p.tag, fill=p.color))

        # ensures proper leveling of canvas items
        if added_buffer:
            self.tag_lower("planets", "buttons")
            self.tag_lower("paths", "planets")
            self.tag_lower("triggers", "planets")

    # ================================================= STAR FUNCTIONS =================================================

    @staticmethod
    def chunk_difference(chunks1: array, chunks2: array) -> list[array]:
        """
        takes 2 sets of chunks and finds the chunks that are in chunk 1 but not in chunk 2

        :param chunks1: a numpy array representing the corners of chunks 1 in the form [[xmin, ymin], [xmax, ymax]]
        :param chunks2: a numpy array representing the corners of chunks 2 in the form [[xmin, ymin], [xmax, ymax]]

        :return: a list of the range of chunks that are in chunk 1 but not chunk 2
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

    def space_to_canvas(self, coordinates: array) -> array:
        """
        converts coordinates representing a position in space to coordinates representing a position on the canvas

        :param coordinates: a numpy array representing the position in space in the format [x, y]
            ** note: format [[xp, yp], [xs, ys]] is used in zoom events to update the position of both planet and star
                coordinate systems at the same time **

        :return: a numpy array representing the converted coordinates in the canvas in the format [[xp, yp], [xs, ys]]
            where the first array uses planet zoom level and the second array uses star zoom level
        """

        return (coordinates - self.space_position) * self.zoom

    def canvas_to_space(self, coordinates: array) -> array:
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

        # gets the position of zoom event
        mouse = self.canvas_size / 2
        if event and event.type == "38" and (not self.planet_manager.focused_planet):
            mouse = array([event.x, event.y])

        # updates zoom and position
        position = (mouse / self.zoom) + self.space_position
        self.zoom *= amount
        position = self.space_to_canvas(position)
        self.space_position += (position - mouse) / self.zoom

        # handles star/planet rendering
        self.scale("planets", mouse[0], mouse[1], amount[0, 0], amount[0, 0])
        self.scale("triggers", mouse[0], mouse[1], amount[0, 0], amount[0, 0])
        self.scale("paths", mouse[0], mouse[1], amount[0, 0], amount[0, 0])
        self.scale("stars", mouse[0], mouse[1], amount[1, 0], amount[1, 0])
        self.draw_stars() if render else None

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
        if event and (event.widget != self or (event.type != "2" and "buttons" in self.gettags(
                event.widget.find_withtag("current")))):
            return

        # handles click and drag events
        if event and event.type == "6":
            self.drag_amt += norm(self.drag_event - array([event.x, event.y]))
            self.drag_event = array([event.x, event.y])

        # handles updating position and star rendering
        amount = vstack((amount, amount * Canvas.STAR_POS_FACTOR))
        self.space_position += (amount / self.zoom)
        self.move("planets", *-amount[0])
        self.move("triggers", *-amount[0])
        self.move("paths", *-amount[0])
        self.move("stars", *-amount[1])

        # handles call is not from update planets
        if unfocus:
            self.set_focus(None)
            self.draw_stars()

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
        self.draw_stars()

        # handles initial resize event
        if not self.initialized:
            self.initialized = True
            self.set_focus(self.planet_manager.get_sun(), True, False)
            self.update_planets()

    # ==================================================== BUTTONS =====================================================

    def create_button(self, corners: tuple, text: str, tag: str, tooltip: str, shift: tuple = (0, 0, 1)) -> int:
        """
        creates a button on the canvas with the given parameters
            --> rectangle with rounded edges
            --> text in the center
            --> uses class properties to determine appearance of button

        :param corners: the coordinates of the top left corner and bottom right corners of the rectangle in the form
            (x1, y1, x2, y2)
        :param text: the text to add to the button
        :param tag: the tag to associate with the navigation button (used in resize events)
        :param tooltip: the message to be displayed when the user hovers over the button
        :param shift: the offset value to apply to the string so that it is slightly off center and scale in the form
            (dx, dy, scale)

        :return the id of the created text so that it can be mirrored later for settings buttons
        """

        # gets variables for creating button
        x1, y1, x2, y2 = corners
        radius = Canvas.NAV_BUTTON_RADIUS
        kwargs = {"extent": 90, "style": "arc", "outline": Canvas.NAV_BUTTON_BORDER["fill"], **Canvas.NAV_BUTTON_BORDER}
        center_x = ((x1 + x2) / 2) + shift[0]
        center_y = ((y1 + y2) / 2) - shift[1]
        center_tag = (text, "buttons", tag, f"center{text}")
        edge_tag = (text, "buttons", tag)
        tooltip_tag = (text, "buttons", "tooltips", f"{text} tooltip")

        # draws the rounded corners
        self.create_oval(x1, y1, x1 + radius * 2, y1 + radius * 2, **Canvas.NAV_BUTTON_FILL, tags=center_tag)
        self.create_oval(x2 - radius * 2, y1, x2, y1 + radius * 2, **Canvas.NAV_BUTTON_FILL, tags=center_tag)
        self.create_oval(x1, y2 - radius * 2, x1 + radius * 2, y2, **Canvas.NAV_BUTTON_FILL, tags=center_tag)
        self.create_oval(x2 - radius * 2, y2 - radius * 2, x2, y2, **Canvas.NAV_BUTTON_FILL, tags=center_tag)

        # draws the remainder of the rounded rectangle
        self.create_rectangle(x1 + radius, y1, x2 - radius, y2, **Canvas.NAV_BUTTON_FILL, tags=center_tag)
        self.create_rectangle(x1, y1 + radius, x1 + radius * 2, y2 - radius, **Canvas.NAV_BUTTON_FILL, tags=center_tag)
        self.create_rectangle(x2 - radius * 2, y1 + radius, x2, y2 - radius, **Canvas.NAV_BUTTON_FILL, tags=center_tag)

        # draws rounded borders
        self.create_arc(x1, y1, x1 + radius * 2, y1 + radius * 2, start=90, **kwargs, tags=edge_tag)
        self.create_arc(x2 - radius * 2, y1, x2, y1 + radius * 2, start=0, **kwargs, tags=edge_tag)
        self.create_arc(x1, y2 - radius * 2, x1 + radius * 2, y2, start=180, **kwargs, tags=edge_tag)
        self.create_arc(x2 - radius * 2, y2 - radius * 2, x2, y2, start=270, **kwargs, tags=edge_tag)

        # draws straight borders
        self.create_line(x1 + radius, y1, x2 - radius, y1, **Canvas.NAV_BUTTON_BORDER, tags=edge_tag)
        self.create_line(x1 + radius, y2, x2 - radius, y2, **Canvas.NAV_BUTTON_BORDER, tags=edge_tag)
        self.create_line(x1, y1 + radius, x1, y2 - radius, **Canvas.NAV_BUTTON_BORDER, tags=edge_tag)
        self.create_line(x2, y1 + radius, x2, y2 - radius, **Canvas.NAV_BUTTON_BORDER, tags=edge_tag)

        # creates tooltip
        tooltip = self.create_text(0, 0, text=tooltip, font=("Arial", 10), fill="black", tags=tooltip_tag)
        padding = array([-3, -3, 3, 3])
        bg = self.create_rectangle(*(array(self.bbox(tooltip)) + padding[:]), **Canvas.TOOLTIP_FILL, tags=tooltip_tag)
        self.tag_raise(tooltip)
        self.itemconfig(f"{text} tooltip", state="hidden")

        def place_tooltip(event):
            """
            moves the tooltip to the mouse position and makes it visible

            :param event: the enter event that triggered the function
            """

            # handles when the tooltip has already been made visible
            if text not in self.gettags(event.widget.find_withtag("current")):
                return

            # makes the tooltip visible and gets its bbox
            self.itemconfig(f"{text} tooltip", state="normal")
            bbox = self.bbox(tooltip)
            dx, dy = ((bbox[2] - bbox[0]) / 2) + padding[2], ((bbox[3] - bbox[1]) / 2) + padding[3]

            # finds position where tooltip will be visible
            if event.x - (dx * 2) < 0:
                event.x += dx + 8
            else:
                event.x -= dx
            if event.y - (dy * 2) < 0:
                event.y += dy + 8
            else:
                event.y -= dy

            # set position of tooltip
            self.coords(tooltip, event.x, event.y)
            self.coords(bg, *(array(self.bbox(tooltip)) + padding[:]))

        # binds events to handle tooltip functionality
        self.tag_bind(text, "<Button-1>", lambda e: self.after_cancel(self.after_tooltip))
        self.tag_bind(text, "<Button-1>", lambda e: self.itemconfig(f"{text} tooltip", state="hidden"), add="+")
        self.tag_bind(text, "<Motion>", lambda e: self.after_cancel(self.after_tooltip))
        self.tag_bind(text, "<Motion>", lambda e: self.itemconfig(f"{text} tooltip", state="hidden"), add="+")
        self.tag_bind(text, "<Motion>", lambda e: setattr(self, "after_tooltip", self.after(
            Canvas.TOOLTIP_HOVER_TIME, lambda: place_tooltip(e))), add="+")

        # draws text and sets click event handler
        char = text if text != "carrot" else "^"
        kwargs = {"text": char, "font": ("Arial", int(20 * shift[2])), "fill": "black", "tags": edge_tag}
        text_id = self.create_text(center_x, center_y - 3, **kwargs)
        return text_id

    def button_click_animation(self, tag: str, hold: tuple = ()) -> tuple:
        """
        updates attributes of the navigation button so that it looks like it was clicked
            --> changes the color if the button for 100 ms
            --> moves the button SE for 100 ms
            --> uses class properties to determine fill and offset values

        :param tag: a string representing the tag of the navigation button that was clicked
        :param hold: the actions to cancel to keep the button held

        :return the queued actions to reset the button state (they will be canceled if the button is held)
        """

        # cancels animation if there are not undo/redo actions
        undo = (tag == "↩" and len(self.planet_manager.state_manager.undo_actions) == 0)
        redo = (tag == "↪" and len(self.planet_manager.state_manager.redo_actions) == 0)
        if undo or redo:
            return

        # updates the button to the clicked state
        if not hold:
            self.itemconfig("center" + tag, **Canvas.NAV_BUTTON_CLICKED)
            self.move(tag, Canvas.NAV_BUTTON_CLICK_OFFSET, Canvas.NAV_BUTTON_CLICK_OFFSET)
            self.update_idletasks()

        # handles holding the button
        else:
            self.after_cancel(hold[0])
            self.after_cancel(hold[1])

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

            after_click = self.button_click_animation(tag, hold=after_click)
            self.after_click = self.after(Canvas.NAV_BUTTON_REPEAT, lambda: repeat(after_click))
            function()

        def first_click():
            """
            the function for when the button is first clicked
                --> button will play click animation
                --> action will repeat after a certain delay
            """

            self.button_click_animation(tag)
            self.after_click = self.after(Canvas.NAV_BUTTON_REPEAT_DELAY, repeat)
            function()

        # binds functions to tags
        self.tag_bind(tag, "<Button-1>", lambda e: first_click(), add="+")
        self.tag_bind(tag, "<ButtonRelease-1>", lambda e: self.after_cancel(self.after_click))
        self.tag_bind(tag, "<Leave>", lambda e: self.after_cancel(self.after_click), add="+")

    def menu_visibility_buttons(self, text_id: int):
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

    def file_buttons(self, tag: str, event=None):
        """
        handles when the file buttons are clicked: new, load, save as/save, undo and redo

        :param tag: the tag of the button that was pressed
        :param event: the event that triggered the function
        """

        # sets text for warning
        self.button_click_animation(tag) if not event else None
        args = "Save Project", "You have unsaved changes that will be lost without saving. Continue?"
        args = ("Exit", "You are are about to exit. Continue?") if tag == "exit" and (
            not self.planet_manager.state_manager.unsaved) else args
        args = ("Start New Project", "You are about to start a new project. Continue?") if \
            tag == "🆕" and (not self.planet_manager.state_manager.unsaved) else args

        # warns user they will lose progress if loading when not saved
        if tag == "📂" and self.planet_manager.state_manager.unsaved and (not askokcancel(*args)):
            return

        # asks user if they are sure they want to start a new project
        elif tag == "🆕" and (not askokcancel(*args)):
            return

        # asks user if they are sure they want to exit
        elif tag == "exit" and askokcancel(*args):
            return "exit"

        # handles if new or load are clicked
        if tag == "📂" or tag == "🆕":
            self.file_manager.load(self, new=(tag == "🆕"))

        # handles when user clicks save as
        if tag == "📑":
            old_path = self.file_manager.save_path
            self.file_manager.save_path = None
            self.file_manager.save(self)
            self.file_manager.save_path = old_path if not self.file_manager.save_path else self.file_manager.save_path
