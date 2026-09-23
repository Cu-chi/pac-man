import pygame
from events import Key, EventType, Event
from types import TracebackType
from typing import Self

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
    """Thin wrapper around pygame, the only module allowed to use it.

    Exposes MLX-style drawing and event primitives so the rest of the
    game never imports pygame directly.
    """

    def __init__(self, width: int, height: int, title: str) -> None:
        """Open the game window.

        Args:
            width: Window width, in pixels.
            height: Window height, in pixels.
            title: Text shown in the window's title bar.
        """
        self.width: int = width
        self.height: int = height

        pygame.init()
        pygame.display.set_caption(title)
        self._screen: pygame.Surface = pygame.display.set_mode((self.width,
                                                                self.height))
        self._clock = pygame.time.Clock()
        self._fonts: dict[int, pygame.font.Font] = {}

    def __enter__(self) -> Self:
        """Return the canvas itself for use in a `with` block.

        Returns:
            This canvas.
        """
        return self

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: BaseException | None, tb: TracebackType | None) -> None:
        """Close the window when leaving the `with` block.

        Args:
            exc_type: Type of the exception raised in the block, if any.
            exc: The exception instance raised in the block, if any.
            tb: Traceback of that exception, if any.
        """
        self.close()

    def clear(self, color: Color) -> None:
        """Fill the whole window with one flat color.

        Args:
            color: RGB color used to erase the previous frame.
        """
        self._screen.fill(color)

    def present(self) -> None:
        """Show everything drawn since the last `clear` call."""
        pygame.display.flip()

    def tick(self, fps: int) -> float:
        """Cap the frame rate and report the time spent on the last frame.

        Args:
            fps: Maximum number of frames per second.

        Returns:
            Elapsed time since the previous call, in seconds.
        """
        res = self._clock.tick(fps)
        res_ms = res / 1000
        return float(res_ms)

    def draw_rect(self, x: int, y: int, w: int, h: int,
                  color: Color, filled: bool = True) -> None:
        """Draw a rectangle, pixel by pixel, filled or as an outline.

        Args:
            x: X coordinate of the top-left corner, in pixels.
            y: Y coordinate of the top-left corner, in pixels.
            w: Rectangle width, in pixels.
            h: Rectangle height, in pixels.
            color: RGB color of the rectangle.
            filled: Draw a filled rectangle when True, an outline otherwise.
        """
        if filled:
            for px in range(x, x + w):
                for py in range(y, y + h):
                    if 0 <= px < self.width and 0 <= py < self.height:
                        self._screen.set_at((px, py), color)
        else:
            for px in range(x, x + w):
                if 0 <= px < self.width:
                    if 0 <= y < self.height:
                        self._screen.set_at((px, y), color)
                    if 0 <= y + h - 1 < self.height:
                        self._screen.set_at((px, y + h - 1), color)
            for py in range(y, y + h):
                if 0 <= py < self.height:
                    if 0 <= x < self.width:
                        self._screen.set_at((x, py), color)
                    if 0 <= x + w - 1 < self.width:
                        self._screen.set_at((x + w - 1, py), color)

    def draw_text(self, text: str, x: int, y: int, color: Color,
                  size: int = 24, centered: bool = False) -> None:
        """Draw text on the window, caching the font used for each size.

        Args:
            text: Text to draw.
            x: X coordinate, in pixels; the text center when `centered`.
            y: Y coordinate, in pixels; the text center when `centered`.
            color: RGB color of the text.
            size: Font size, in points.
            centered: Center the text on (x, y) instead of using it as the
                top-left corner.
        """
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
        """Drain pygame's event queue and translate it to `Event` values.

        Returns:
            The window and keyboard events received since the last call.
        """
        events = []
        for raw_event in pygame.event.get():
            if raw_event.type == pygame.QUIT:
                events.append(Event(type=EventType.QUIT))
            elif raw_event.type == pygame.KEYDOWN:
                events.append(Event(type=EventType.KEY_DOWN,
                                    key=_KEY_MAP.get(raw_event.key, Key.OTHER),
                                    char=raw_event.unicode))
        return events

    def close(self) -> None:
        """Close the window and release pygame's resources."""
        pygame.quit()
