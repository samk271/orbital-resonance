from os import chdir
chdir("../src")
from FileManagement.FileManager import FileManager
from Physics.PlanetManager import PlanetManager
from Physics.Planet import Planet
from Physics.Moon import Moon
from GUI.Canvas import Canvas

# Create full list of planets and moons
planets = [
    Planet(0, 696, "#ffcc00", 0),  # Sun

    Planet(40.0, 80, "#b7b7b7", 0),  # Mercury
    Planet(70.0, 150, "#e6cfa7", 0),  # Venus

    earth := Planet(100.0, 180, "#2e66a5", 0),
    Moon(earth, 3.0, 30, "#cccccc", 0),  # Moon (slightly faster)

    mars := Planet(130.0, 220, "#b54c32", 0),
    Moon(mars, 1.4, 10, "#aaaaaa", 0),   # Phobos
    Moon(mars, 1.4, 8, "#999999", 0),    # Deimos

    jupiter := Planet(200.0, 500, "#d9a066", 0),
    Moon(jupiter, 3.0, 34, "#aaaaaa", 0),   # Io
    Moon(jupiter, 3.1, 32, "#999999", 0),   # Europa
    Moon(jupiter, 3.2, 36, "#bbbbbb", 0),   # Ganymede
    Moon(jupiter, 3.3, 40, "#dddddd", 0),   # Callisto

    saturn := Planet(250.0, 600, "#f5d76e", 0),
    Moon(saturn, 3.48, 38, "#eeeeee", 0),    # Titan
    Moon(saturn, 2.76, 26, "#aaaaff", 0),    # Enceladus

    uranus := Planet(300.0, 700, "#6db7c6", 0),
    Moon(uranus, 3.06, 28, "#dddddd", 0),    # Titania
    Moon(uranus, 2.57, 22, "#bbbbdd", 0),    # Oberon

    neptune := Planet(350.0, 800, "#3457d5", 0),
    Moon(neptune, 2.94, 26, "#cccccc", 0),   # Triton
]

# Save the system
FileManager().save(Canvas(None, planet_settings=None, AI_settings=None, file_manager=None,
                          planet_manager=PlanetManager(planets)),
                   "../src/saves/our solar system.orbres")
