from os import chdir
chdir("../src")
from GUI import *  # needed so physics imports properly
from Physics import *

# generates our solar system.orbres save file
PlanetManager([
    Planet(0, 696, "#ffcc00"),
    Planet(2.0, 80, "#b7b7b7"),
    Planet(4.8, 150, "#e6cfa7"),
    Planet(8.0, 180, "#2e66a5"),
    Planet(12.0, 220, "#b54c32"),
    Planet(40.0, 500, "#d9a066"),
    Planet(90.0, 600, "#f5d76e"),
    Planet(180.0, 700, "#6db7c6"),
    Planet(300.0, 800, "#3457d5")
]).save("../src/saves/our solar system.orbres")
