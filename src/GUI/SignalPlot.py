from customtkinter import CTkFrame, get_appearance_mode
from matplotlib.pyplot import subplots, close
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
from numpy import linspace, min as np_min, max as np_max, searchsorted


class AudioPlotFrame(CTkFrame):
    def __init__(self, master, audio_signal, sample_rate, **kwargs):
        super().__init__(master, **kwargs)

        self.audio_signal = audio_signal
        self.sample_rate = sample_rate
        self.time = linspace(0, len(audio_signal) / sample_rate, len(audio_signal))

        # Initial crop positions
        self.left_crop = self.time[0]
        self.right_crop = self.time[-1]
        self.dragging_bar = None
        self.drag_threshold = 0.01  # seconds

        # Set up plot
        self.figure, self.ax = subplots(figsize=(6, 3), dpi=100)
        self.line, = self.ax.plot(self.time, self.audio_signal, color='dodgerblue', zorder=2)
        self.ax.set_title("Audio Signal")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Amplitude")
        self.ax.grid(True)

        # Crop bars and shading
        self.left_line = self.ax.axvline(self.left_crop, color='gray', linestyle='--', lw=1.5, zorder=3)
        self.right_line = self.ax.axvline(self.right_crop, color='gray', linestyle='--', lw=1.5, zorder=3)
        self.left_shade = Rectangle((self.time[0], self.ax.get_ylim()[0]), 0, 0, color='lightgray', alpha=0.5, zorder=1)
        self.right_shade = Rectangle((self.time[-1], self.ax.get_ylim()[0]), 0, 0, color='lightgray', alpha=0.5, zorder=1)
        self.ax.add_patch(self.left_shade)
        self.ax.add_patch(self.right_shade)

        # Canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill='both', expand=True)

        # Events
        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.canvas.mpl_connect("button_release_event", self.on_release)

        self.update_shading()
        self.apply_theme()

    #Applies the color scheme of the app to the graph
    def apply_theme(self):
        theme = get_appearance_mode()
        if theme == "Dark":
            bg_color = "#2b2b2b"
            text_color = "white"
            grid_color = "#444444"
            line_color = "deepskyblue"
        else:
            bg_color = "white"
            text_color = "black"
            grid_color = "#cccccc"
            line_color = "dodgerblue"

        self.figure.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)
        self.ax.title.set_color(text_color)
        self.ax.xaxis.label.set_color(text_color)
        self.ax.yaxis.label.set_color(text_color)
        self.ax.tick_params(colors=text_color)
        self.ax.grid(True, color=grid_color)

        self.line.set_color(line_color)
        self.left_line.set_color("gray")
        self.right_line.set_color("gray")

        self.canvas.draw()

    def on_click(self, event):
        if event.inaxes:
            if abs(event.xdata - self.left_crop) < self.drag_threshold:
                self.dragging_bar = 'left'
            elif abs(event.xdata - self.right_crop) < self.drag_threshold:
                self.dragging_bar = 'right'

    def on_motion(self, event):
        if self.dragging_bar and event.inaxes:
            x = event.xdata
            x = max(self.time[0], min(self.time[-1], x))  # Clamp
            if self.dragging_bar == 'left':
                self.left_crop = min(x, self.right_crop - 1e-3)  # avoid overlap
                self.left_line.set_xdata([self.left_crop, self.left_crop])
            elif self.dragging_bar == 'right':
                self.right_crop = max(x, self.left_crop + 1e-3)
                self.right_line.set_xdata([self.right_crop, self.right_crop])
            self.update_shading()
            self.canvas.draw()

    def on_release(self, event):
        self.dragging_bar = None

    def update_waveform(self, new_signal, new_sample_rate):
        self.audio_signal = new_signal
        self.sample_rate = new_sample_rate
        self.time = linspace(0, len(new_signal) / new_sample_rate, len(new_signal))

        self.line.set_xdata(self.time)
        self.line.set_ydata(self.audio_signal)
        self.ax.set_xlim(self.time[0], self.time[-1])
        self.ax.set_ylim(np_min(self.audio_signal), np_max(self.audio_signal))
        self.ax.margins(x=0, y=0)
        self.ax.autoscale_view(tight=True)
        self.figure.tight_layout()

        # Reset crop
        self.left_crop = self.time[0]
        self.right_crop = self.time[-1]
        self.left_line.set_xdata([self.left_crop, self.left_crop])
        self.right_line.set_xdata([self.right_crop, self.right_crop])


        self.update_shading()
        self.canvas.draw()

    def update_shading(self):
        y_min, y_max = self.ax.get_ylim()
        self.left_shade.set_bounds(self.time[0], y_min, self.left_crop - self.time[0], y_max - y_min)
        self.right_shade.set_bounds(self.right_crop, y_min, self.time[-1] - self.right_crop, y_max - y_min)

    def get_crop_indices(self):
        left_index = searchsorted(self.time, self.left_crop, side='left')
        right_index = searchsorted(self.time, self.right_crop, side='right')
        return left_index, right_index
    
    def set_crop_positions(self, left_time, right_time):
        """
        Set the position of the crop bars manually.
        
        Parameters:
        - left_time (float): Time in seconds for the left crop bar.
        - right_time (float): Time in seconds for the right crop bar.
        """
        # Clamp and validate values
        left_time = max(self.time[0], min(self.time[-1], left_time))
        right_time = max(self.time[0], min(self.time[-1], right_time))

        if left_time >= right_time:
            raise ValueError("left_time must be less than right_time")

        self.left_crop = left_time
        self.right_crop = right_time

        self.left_line.set_xdata([self.left_crop, self.left_crop])
        self.right_line.set_xdata([self.right_crop, self.right_crop])

        self.update_shading()
        self.canvas.draw()
    
    def destroy(self):
        # Properly destroy matplotlib canvas to cancel any pending .after calls
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
            self.canvas._tkcanvas = None  # helps avoid lingering references
            self.canvas = None

        close(self.figure)  # Close the matplotlib figure explicitly

        super().destroy()
