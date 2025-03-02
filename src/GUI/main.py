from customtkinter import CTk
from Canvas import Canvas
from PlanetSettings import PlanetSettings
from AISettings import AISettings
from sun import SunSettings

# creates the screen and its widgets
display = CTk()
display.geometry("800x600")
canvas = Canvas(display, bg="black", highlightthickness=1)
settings_right_top = SunSettings(display, border_width=2)
settings_right_bottom = PlanetSettings(display, border_width=2)
settings_bottom = AISettings(display, border_width=2)

# configures grid for dynamic resizing
display.rowconfigure(0, weight=1)
display.columnconfigure(0, weight=1)

# places widgets on the screen and starts display
canvas.grid(row=0, column=0, rowspan=2, sticky="nsew")
settings_right_top.grid(row=0, column=1, sticky="nsew")
settings_right_bottom.grid(row=1, column=1,sticky="nsew")
settings_bottom.grid(row=1, column=0, columnspan=2, sticky="nsew")
display.mainloop()

# test to check 
