from customtkinter import CTk
from GUI import *
from pickle import dump, load

# loads previous save  todo add save/load menu
with open("save.pkl", "rb") as file:
    planet_manager = load(file)

# creates the screen and its widgets
display = CTk()
display.geometry("800x600")
planet_settings = PlanetSettings(display, border_width=2)
AI_settings = AISettings(display, border_width=2)
canvas = Canvas(display, bg="black", highlightthickness=1, planet_settings=planet_settings, AI_settings=AI_settings,
                planet_manager=planet_manager)

# configures grid for dynamic resizing
display.rowconfigure(0, weight=1)
display.columnconfigure(0, weight=1)

# places widgets on the screen and starts display
planet_settings.grid(row=0, column=1, sticky="nsew")
AI_settings.grid(row=1, column=0, columnspan=2, sticky="nsew")
canvas.grid(row=0, column=0, sticky="nsew")
display.mainloop()

# saves planet manager  todo add save/load menu
with open("save.pkl", "wb") as file:
    canvas.planet_manager.reload()
    dump(canvas.planet_manager, file)
