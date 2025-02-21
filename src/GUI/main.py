from customtkinter import CTk
from Canvas import Canvas
from SettingsRight import SettingsRight
from SettingsBottom import SettingsBottom

# creates the screen and its widgets
display = CTk()
canvas = Canvas(display)
settings_right = SettingsRight(display)
settings_bottom = SettingsBottom(display)

# configures grid for dynamic resizing
display.rowconfigure(0, weight=1)
display.rowconfigure(1, weight=1)
display.columnconfigure(0, weight=1)
display.columnconfigure(1, weight=1)

# places widgets on the screen and starts display
canvas.grid(row=0, column=0, sticky='nsew')
settings_right.grid(row=0, column=1, sticky='nsew')
settings_bottom.grid(row=1, column=0, columnspan=2, sticky='nsew')
display.mainloop()
