from os import chdir
chdir("../src")
from main import root, canvas
from GUI.Canvas import Canvas
from time import perf_counter


def update_planets():
    """
    changes how the update planets function of the canvas works to also update the current FPS
    """

    canvas.itemconfig(fps_label, text=f"FPS: {int(1 / (perf_counter() - canvas.last_frame))}")
    canvas.last_frame = perf_counter()
    old_func()


# changes the update planets function and fps
canvas.last_frame = perf_counter()
old_func = canvas.update_planets
canvas.update_planets = update_planets
Canvas.FPS = 1

# adds the fps label and starts program
fps_label = canvas.create_text(canvas.canvas_size[0] - 80, 20, fill="white", tags="planet_settings", font=("Arial", 12))
root.mainloop()
