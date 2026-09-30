

import pygame


class Player:
    def __init__(self, player_id: str, x: float, y: float, is_local: bool = False):
        self.player_id = player_id
        self.is_local = is_local
        self.position = pygame.Vector2(x, y)
        self.radius = 20
        self.health = 100
        self.max_health = 100
        self.shield = 50
        self.max_shield = 50
        self.is_alive = True

        # Hitbox
        self.rect = pygame.Rect(
            0,
            0,
            self.radius * 2,
            self.radius * 2
        )

        self.rect.center = self.position


    def update_from_server(self, server_data: dict):
        self.position.x = server_data.get("x", self.position.x)
        self.position.y = server_data.get("y", self.position.y)
        self.rect.center = (round(self.position.x), round(self.position.y))
        self.health = server_data.get("hp", self.health)
        self.shield = server_data.get("sh", self.shield)
        self.is_alive = server_data.get("alive", True)

    # Aim
    def get_aim_direction(
        self,
        camera
    ):

        mouse_position = pygame.Vector2(
            pygame.mouse.get_pos()
        )

        player_screen_position = (
            camera.apply(
                self.position
            )
        )

        direction = (
            mouse_position
            - player_screen_position
        )

        if direction.length() > 0:

            direction = (
                direction.normalize()
            )

        return round(direction.x, 3), round(direction.y, 3)


    # Draw
    def draw(
        self,
        screen,
        camera
    ):

        if not self.is_alive:
            return

        screen_position = (
            camera.apply(
                self.position
            )
        )

        center = (round(screen_position.x), round(screen_position.y))
        pygame.draw.circle(
            screen,
            (80, 170, 255) if self.is_local else (255, 80, 80),
            center,
            self.radius
        )

        bar_width = self.radius * 2
        bar_height = 4
        bar_x = center[0] - bar_width // 2
        bar_y = center[1] - self.radius - 10
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
        health_width = round(bar_width * max(0, min(self.health, self.max_health)) / self.max_health)
        pygame.draw.rect(screen, (0, 220, 0), (bar_x, bar_y, health_width, bar_height))
        shield_y = bar_y - bar_height - 2
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, shield_y, bar_width, bar_height))
        shield_width = round(bar_width * max(0, min(self.shield, self.max_shield)) / self.max_shield)
        pygame.draw.rect(screen, (0, 220, 220), (bar_x, shield_y, shield_width, bar_height))