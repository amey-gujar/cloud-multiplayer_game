"""Static map dimensions and collision obstacles."""

MAP_WIDTH = 2500
MAP_HEIGHT = 2000

WALLS = [
    (300, 300, 400, 50),
    (900, 500, 50, 400),
    (1300, 300, 500, 50),
    (1800, 700, 50, 500),
    (600, 1200, 600, 50),
    (1500, 1400, 500, 50),
    # Outer boundary walls, each 50 units thick.
    (0, 0, MAP_WIDTH, 50),
    (0, MAP_HEIGHT - 50, MAP_WIDTH, 50),
    (0, 0, 50, MAP_HEIGHT),
    (MAP_WIDTH - 50, 0, 50, MAP_HEIGHT),
]