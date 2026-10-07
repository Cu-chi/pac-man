import sys
import random
from ui.screens import HUD_HEIGHT
from models import Configuration
from pydantic import ValidationError
from configuration import load_config
from highscores.highscores import Highscores
from ui.canvas import Canvas
from ui.menu import Menu, MenuAction
from ui.events import Event
from pathlib import Path
from enum import Enum, auto

TILE_SIZE = 32
MIN_WINDOW_WIDTH = 600


class Screen(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    END = auto()


class App():

    def __init__(self, canvas: Canvas, config: Configuration,
                 highscores: Highscores, tile_size: int = TILE_SIZE) -> None:
        self.canvas = canvas
        self.config = config
        self.highscores = highscores
        self.tile_size = tile_size
        self.screen = Screen.MENU
        self.menu = Menu()
        self._refresh_highscores()

    def _refresh_highscores(self) -> None:
        ranked = sorted(self.highscores.score, key=lambda s: s.score,
                        reverse=True)
        top = ranked[:10]
        self.menu.highscore = [(s.username, s.score) for s in top]

    def on_key(self, event: Event) -> None:
        if self.screen == Screen.MENU:
            action = self.menu.handle_key(event)
            if action == MenuAction.EXIT:
                self.canvas.loop_exit()
            elif action == MenuAction.START_GAME:
                pass

    def on_frame(self, dt: float) -> None:
        self.canvas.clear()
        if self.screen == Screen.MENU:
            self.menu.draw(self.canvas)


def main() -> None:
    if len(sys.argv) != 2:
        print("Error: no configuration file given.", file=sys.stderr)
        sys.exit(1)
    config = load_config(sys.argv[1])
    random.seed(config.seed)
    try:
        highscores = Highscores.load_json(Path(config.highscore_filename))
    except (ValidationError, OSError) as e:
        print(f"Warning: {e}", file=sys.stderr)
        highscores = Highscores()

    maze_width = max(level.width for level in config.levels) * TILE_SIZE
    window_width = max(MIN_WINDOW_WIDTH, maze_width)
    window_height = max(level.height
                        for level in config.levels) * TILE_SIZE + HUD_HEIGHT

    with Canvas(window_width, window_height, "PAC-MAN") as canvas:
        app = App(canvas, config, highscores)
        canvas.key_hook(app.on_key)
        canvas.loop_hook(app.on_frame)
        canvas.loop()


if __name__ == "__main__":
    main()
