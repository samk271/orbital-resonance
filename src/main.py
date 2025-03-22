from customtkinter import CTk
from tkinter.messagebox import askyesno
from GUI import *
from Physics import PlanetManager
import pygame
from sys import argv


def handle_close(window: CTk, planet_manager: PlanetManager):
    """
    the function to handle when the user exits the application
        --> checks if the loaded file has been saved
        --> asks user if they want to save if it has not
        --> saves the program and exits

    :param window: the display window to close
    :param planet_manager: the planet manager class to save
    """

    # exits if user does not want to save  todo check if user has unsaved actions
    if not (planet_manager.save_path or askyesno("Save Changes", "Do you want to save your work before exiting?")):
        return window.destroy()

    # saves users work and exits
    planet_manager.save()
    window.destroy()


# initializes pygame audio mixer
pygame.mixer.init()

# creates the screen and its widgets
display = PlanetManager.SAVE_OPTIONS["parent"]
display.title("Orbital Resonance")
display.geometry("800x600")
display.protocol("WM_DELETE_WINDOW", lambda: handle_close(display, canvas.planet_manager))
planet_settings = PlanetSettings(display, border_width=2)
AI_settings = AISettings(display, border_width=2)
canvas = Canvas(display, bg="black", highlightthickness=1, planet_settings=planet_settings, AI_settings=AI_settings,
                planet_manager=PlanetManager.load(argv[1]) if len(argv) == 2 else PlanetManager())

# configures grid for dynamic resizing
display.rowconfigure(0, weight=1)
display.columnconfigure(0, weight=1)

# places widgets on the screen and starts display
planet_settings.grid(row=0, column=1, sticky="nsew")
AI_settings.grid(row=1, column=0, columnspan=2, sticky="nsew")
canvas.grid(row=0, column=0, sticky="nsew")
display.mainloop()
