from customtkinter import CTk
from GUI import *
from Physics import PlanetManager
import pygame

# initializes pygame
pygame.mixer.init()

# creates the screen and its widgets
display = CTk()
display.geometry("800x600")
planet_settings = PlanetSettings(display, border_width=2)
AI_settings = AISettings(display, border_width=2)
canvas = Canvas(display, bg="black", highlightthickness=1, planet_settings=planet_settings, AI_settings=AI_settings,
                planet_manager=PlanetManager.load("save.orbres"))

# configures grid for dynamic resizing
display.rowconfigure(0, weight=1)
display.columnconfigure(0, weight=1)

# places widgets on the screen and starts display
planet_settings.grid(row=0, column=1, sticky="nsew")
AI_settings.grid(row=1, column=0, columnspan=2, sticky="nsew")
canvas.grid(row=0, column=0, sticky="nsew")
display.mainloop()
canvas.planet_manager.save("save.orbres")
