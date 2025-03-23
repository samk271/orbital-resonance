from GUI import *
from Physics import PlanetManager
import pygame
from sys import argv

# initializes pygame audio mixer
pygame.mixer.init()

# creates the screen and its widgets
display = PlanetManager.SAVE_OPTIONS["parent"]
display.title("Orbital Resonance")
display.geometry("800x600")
planet_settings = PlanetSettings(display, border_width=2)
AI_settings = AISettings(display, border_width=2)
canvas = Canvas(display, bg="black", highlightthickness=1, planet_settings=planet_settings, AI_settings=AI_settings,
                planet_manager=PlanetManager.load(argv[1]) if len(argv) == 2 else PlanetManager())

# configures grid for dynamic resizing and close function
display.protocol("WM_DELETE_WINDOW", lambda: display.destroy() if not canvas.file_buttons("exit") else None)
display.rowconfigure(0, weight=1)
display.columnconfigure(0, weight=1)

# places widgets on the screen and starts display
planet_settings.grid(row=0, column=1, sticky="nsew")
AI_settings.grid(row=1, column=0, columnspan=2, sticky="nsew")
canvas.grid(row=0, column=0, sticky="nsew")
display.mainloop()
