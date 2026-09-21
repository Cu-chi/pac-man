import pygame

Color = tuple[int, int, int]


class Canvas:

    def __init__(self, width: int, height: int, title: str) -> None:

        self.width: int = width
        self.height: int = height

        pygame.init()
        pygame.display.set_caption(title)
        self._screen: pygame.Surface = pygame.display.set_mode((self.width,
                                                                self.height))
        self._clock = pygame.time.Clock()

    def clear(self, color) -> None:
        self._screen.fill(color)

    def present(self) -> None:
        pygame.display.flip()
