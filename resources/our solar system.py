from os import chdir
chdir("../src")
from FileManagement.FileManager import FileManager
from Physics.PlanetManager import PlanetManager
from Physics.Planet import Planet
from GUI.Canvas import Canvas

# generates our solar system.orbres save file
FileManager().save(Canvas(None, planet_settings=None, AI_settings=None, file_manager=None,
                          planet_manager=PlanetManager([
                              Planet(0, 696, "#ffcc00", 0),
                              Planet(2.0, 80, "#b7b7b7", 0),
                              Planet(4.8, 150, "#e6cfa7", 0),
                              Planet(8.0, 180, "#2e66a5", 0),
                              Planet(12.0, 220, "#b54c32", 0),
                              Planet(40.0, 500, "#d9a066", 0),
                              Planet(90.0, 600, "#f5d76e", 0),
                              Planet(180.0, 700, "#6db7c6", 0),
                              Planet(300.0, 800, "#3457d5", 0)
                          ])), "../src/saves/our solar system.orbres")
