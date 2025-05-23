from FileManagement.LoadAI import pipe, root, label, progress_bar
from FileManagement.FileManager import FileManager
from GUI.PlanetSettings import PlanetSettings
from GUI.AISettings import AISettings
from GUI.Canvas import Canvas
from pygame.mixer import init, set_num_channels
from sys import argv

# initializes pygame audio mixer and AI
progress_bar.set(1 / 2)
init()
set_num_channels(1000)  # adjust as needed

# creates the screen and its widgets
FileManager.SAVE_OPTIONS["parent"] = root
FileManager.LOAD_OPTIONS["parent"] = root
AISettings.LOAD_OPTIONS["parent"] = root
file_manager = FileManager()
planet_manager = file_manager.load(path=argv[1] if len(argv) == 2 else None, new=len(argv) != 2)
planet_settings = PlanetSettings(root, border_width=2, planet_manager=planet_manager)
AI_settings = AISettings(root, border_width=2, planet_manager=planet_manager, planet_settings=planet_settings,
                         pipe=pipe)
canvas = Canvas(root, bg="black", highlightthickness=1, planet_settings=planet_settings, AI_settings=AI_settings,
                planet_manager=planet_manager, file_manager=file_manager)

# configures grid close and click functions
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
root.bind_all("<Button-1>", lambda e: e.widget.focus_set() if type(e.widget) != str else None, add="+")

# binds hotkeys to file functions
root.bind_all("<Control-n>", lambda e: canvas.file_buttons("🆕", e))
root.bind_all("<Control-o>", lambda e: canvas.file_buttons("📂", e))
root.bind_all("<Control-Shift-S>", lambda e: canvas.file_buttons("📑", e))
root.bind_all("<Control-s>", lambda e: file_manager.save(canvas))
root.bind_all("<Control-z>", lambda e: canvas.planet_manager.state_manager.undo())
root.bind_all("<Control-y>", lambda e: canvas.planet_manager.state_manager.redo())

# user zoom actions
root.bind_all("<Control-plus>", lambda e: canvas.zoom_event(Canvas.ZOOM_AMT, e))
root.bind_all("<Control-minus>", lambda e: canvas.zoom_event(1 / Canvas.ZOOM_AMT, e))
root.bind_all("<Control-equal>", lambda e: canvas.zoom_event(Canvas.ZOOM_AMT, e))
root.bind_all("<Control-underscore>", lambda e: canvas.zoom_event(1 / Canvas.ZOOM_AMT, e))

# user speed control actions
root.bind_all("<Control-Shift-plus>", lambda e: setattr(canvas, "speed", canvas.speed * Canvas.SPEED_FACTOR))
root.bind_all("<Control-Shift-minus>", lambda e: setattr(canvas, "speed", canvas.speed / Canvas.SPEED_FACTOR))
root.bind_all("<Control-Shift-equal>", lambda e: setattr(canvas, "speed", canvas.speed * Canvas.SPEED_FACTOR))
root.bind_all("<Control-Shift-underscore>", lambda e: setattr(canvas, "speed", canvas.speed / Canvas.SPEED_FACTOR))

# places widgets on screen
label.destroy()
progress_bar.destroy()
planet_settings.grid(row=0, column=1, sticky="nsew")
AI_settings.grid(row=1, column=0, columnspan=2, sticky="nsew")
canvas.grid(row=0, column=0, sticky="nsew")

# starts program
root.update_idletasks()
root.protocol("WM_DELETE_WINDOW", lambda: root.destroy() if canvas.file_buttons("exit") else None)
root.resizable(True, True)
root.state('zoomed')
root.mainloop() if __name__ == "__main__" else None  # can import project from other scripts to run
