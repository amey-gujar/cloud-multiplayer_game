import pygame

from UI.button import Button


class TitleScreen:

    def __init__(
        self,
        screen_width,
        screen_height
    ):

        self.screen_width = (
            screen_width
        )

        self.screen_height = (
            screen_height
        )


        # Fonts
        self.title_font = (
            pygame.font.Font(
                None,
                110
            )
        )

        self.button_font = (
            pygame.font.Font(
                None,
                55
            )
        )


        # Buttons
        button_width = 330
        button_height = 90

        button_x = (
            screen_width // 2
            - button_width // 2
        )

        self.play_button = Button(
            button_x,
            430,
            button_width,
            button_height,
            "PLAY",
            self.button_font
        )

        self.quit_button = Button(
            button_x,
            540,
            button_width,
            button_height,
            "QUIT",
            self.button_font
        )


    # Events
    def handle_event(self, event):

        if self.play_button.is_clicked(
            event
        ):

            return "game"


        if self.quit_button.is_clicked(
            event
        ):

            return "quit"


        return None


    # Draw
    def draw(self, screen):

        # Background
        screen.fill(
            (130, 130, 130)
        )


        # Title Panel
        title_panel = pygame.Rect(
            145,
            15,
            self.screen_width - 290,
            260
        )

        pygame.draw.rect(
            screen,
            (195, 195, 195),
            title_panel
        )


        # Title
        title_surface = (
            self.title_font.render(
                "Cloud Arena",
                True,
                (20, 20, 20)
            )
        )

        title_rect = (
            title_surface.get_rect(
                center=(
                    self.screen_width // 2,
                    145
                )
            )
        )

        screen.blit(
            title_surface,
            title_rect
        )


        # Buttons
        self.play_button.draw(
            screen
        )

        self.quit_button.draw(
            screen
        )