import pygame


class Canvas:

    def __init__(self, width: int, height: int, title: str) -> None:

        self.width: int = width
        self.height: int = height

        pygame.init()
        pygame.display.set_caption(title)
        self._screen: pygame.Surface = pygame.display.set_mode((1200, 700))
        self._clock = pygame.time.Clock()
