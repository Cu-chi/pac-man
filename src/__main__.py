import sys
from ui.screens import HUD_HEIGHT
from models import Configuration
from pydantic import ValidationError
from configuration import load_config
from highscores import Highscores
from ui import (Canvas, Menu, MenuAction,
                Event, draw_hud, draw_ghosts,
                draw_maze, draw_pacgum, draw_player)
from pathlib import Path
from enum import Enum, auto
from levels_generator import LevelsGenerator
from controllers import GameController


TILE_SIZE = 32
MIN_WINDOW_WIDTH = 600


class Screen(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    END = auto()


class App():

    def __init__(self, canvas: Canvas, config: Configuration,
                 highscores: Highscores, game_controller: GameController,
                 tile_size: int = TILE_SIZE) -> None:
        self.canvas = canvas
        self.config = config
        self.highscores = highscores
        self.game_controller = game_controller
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
                self.screen = Screen.PLAYING
        elif self.screen == Screen.PLAYING:
            self.game_controller.handle_key(event)

    def on_frame(self, dt: float) -> None:
        self.canvas.clear()
        if self.screen == Screen.MENU:
            self.menu.draw(self.canvas)
        elif self.screen == Screen.PLAYING:
            level = self.game_controller.state.level
            tsize = self.tile_size
            draw_maze(self.canvas, level, tsize)
            draw_pacgum(self.canvas, level, tsize)
            draw_hud(self.canvas, self.game_controller.state)
            draw_player(self.canvas, self.game_controller.state.player, tsize)
            draw_ghosts(self.canvas, self.game_controller.state.ghosts, tsize)
            self.game_controller.update(dt)


def main() -> None:
    if len(sys.argv) != 2:
        print("Error: no configuration file given.", file=sys.stderr)
        sys.exit(1)
    config = load_config(sys.argv[1])
    levels_gen = LevelsGenerator(config)
    game_controller = GameController(levels_gen, config)
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
        app = App(canvas, config, highscores, game_controller)
        canvas.key_hook(app.on_key)
        canvas.loop_hook(app.on_frame)
        canvas.loop()


if __name__ == "__main__":
    main()
