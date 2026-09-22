import pygame
from events import Key, EventType, Event

Color = tuple[int, int, int]
_KEY_MAP: dict[int, Key] = {
    pygame.K_UP: Key.UP,
    pygame.K_DOWN: Key.DOWN,
    pygame.K_LEFT: Key.LEFT,
    pygame.K_RIGHT: Key.RIGHT,
    pygame.K_RETURN: Key.ENTER,
    pygame.K_KP_ENTER: Key.ENTER,
    pygame.K_ESCAPE: Key.ESCAPE,
    pygame.K_SPACE: Key.SPACE,
    pygame.K_BACKSPACE: Key.BACKSPACE,

}


class Canvas:

    def __init__(self, width: int, height: int, title: str) -> None:

        self.width: int = width
        self.height: int = height

        pygame.init()
        pygame.display.set_caption(title)
        self._screen: pygame.Surface = pygame.display.set_mode((self.width,
                                                                self.height))
        self._clock = pygame.time.Clock()
        self._fonts: dict[int, pygame.font.Font] = {}

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

    def draw_text(self, text: str, x: int, y: int, color: Color,
                  size: int = 24, centered: bool = False) -> None:
        if size not in self._fonts:
            font = pygame.font.Font(None, size)
            self._fonts[size] = font
        font = self._fonts[size]
        image = font.render(text, True, color)
        rect = image.get_rect()
        if centered:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self._screen.blit(image, rect)

    def poll_events(self) -> list[Event]:
        events = []
        for raw_event in pygame.event.get():
            if raw_event.type == pygame.QUIT:
                events.append(Event(type=EventType.QUIT))
            elif raw_event.type == pygame.KEYDOWN:
                events.append(Event(type=EventType.KEY_DOWN,
                                    key=_KEY_MAP.get(raw_event.key, Key.OTHER),
                                    char=raw_event.unicode))
        return events

    def quit(self) -> None:
        pygame.quit()
