import pygame


class Pellet:

    def __init__(
        self,
        position,
        direction,
        velocity,
        damage
    ):

        self.position = pygame.Vector2(
            position
        )

        self.direction = pygame.Vector2(
            direction
        )

        self.velocity = velocity
        self.damage = damage

        self.radius = 4
        self.active = True


    # Update
    def update(
        self,
        walls
    ):

        self.position += (
            self.direction
            * self.velocity
        )


        # Wall Collision
        for wall in walls:

            if wall.rect.collidepoint(
                self.position.x,
                self.position.y
            ):

                self.active = False
                break


    # Draw
    def draw(
        self,
        screen,
        camera
    ):

        if not self.active:
            return

        screen_position = camera.apply(
            self.position
        )

        pygame.draw.circle(
            screen,
            (255, 220, 100),
            (
                int(screen_position.x),
                int(screen_position.y)
            ),
            self.radius
        )