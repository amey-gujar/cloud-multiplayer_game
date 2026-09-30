from wall import Wall


class GameMap:

    def __init__(self):

        # Walls
        self.walls = [

            Wall(
                300,
                300,
                400,
                50
            ),

            Wall(
                900,
                500,
                50,
                400
            ),

            Wall(
                1300,
                300,
                500,
                50
            ),

            Wall(
                1800,
                700,
                50,
                500
            ),

            Wall(
                600,
                1200,
                600,
                50
            ),

            Wall(
                1500,
                1400,
                500,
                50
            )
        ]


    # Draw
    def draw(
        self,
        screen,
        camera
    ):

        for wall in self.walls:

            wall.draw(
                screen,
                camera
            )