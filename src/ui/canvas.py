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

    def clear(self, color: Color) -> None:
        self._screen.fill(color)

    def present(self) -> None:
        pygame.display.flip()

    def tick(self, fps: int) -> float:
        res = self._clock.tick(fps)
        res_ms = res / 1000
        return float(res_ms)

    def draw_rect(self, x: int, y: int, w: int, h: int,
                  color: Color, filled: bool = True) -> None:
        filling = 0 if filled else 1
        pygame.draw.rect(self._screen, color, (x, y, w, h), filling)

    def draw_circle(self, cx: int, cy: int, radius: int, color: Color) -> None:
        pygame.draw.circle(self._screen, color, (cx, cy), radius)

    def draw_line(self, x1: int, y1: int,
                  x2: int, y2: int, color: Color, thickness: int = 1) -> None:
        pygame.draw.line(self._screen, color, (x1, y1), (x2, y2), thickness)
