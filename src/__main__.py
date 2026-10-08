import sys
from ui.screens import HUD_HEIGHT
from models import Configuration, GamePhase
from pydantic import ValidationError
from configuration import load_config
from highscores import Highscores, Score
from ui import (Canvas, Menu, MenuAction,
                Event, draw_hud, Renderer,
                PauseAction, PauseMenu, EndScreen)
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
                 tile_size: int = TILE_SIZE) -> None:
        self.canvas = canvas
        self.config = config
        try:
            highscores = Highscores.load_json(Path(config.highscore_filename))
        except (ValidationError, OSError) as e:
            print(f"Warning: {e}", file=sys.stderr)
            highscores = Highscores()
        self.highscores = highscores
        self.tile_size = tile_size
        self.renderer = Renderer(self.canvas, self.tile_size)
        self.screen = Screen.MENU
        self.pause = PauseMenu()
        self.menu = Menu()
        self.end_screen = EndScreen(victory=False, score=0)
        self.game_controller: GameController | None = None
        self._refresh_highscores()
        self._create_game()

    def _refresh_highscores(self) -> None:
        ranked = sorted(self.highscores.score, key=lambda s: s.score,
                        reverse=True)
        top = ranked[:10]
        self.menu.highscore = [(s.username, s.score) for s in top]

    def _create_game(self) -> None:
        self.levels_gen = LevelsGenerator(self.config)
        self.game_controller = GameController(self.levels_gen, self.config)

    def on_key(self, event: Event) -> None:
        if self.screen == Screen.MENU:
            action = self.menu.handle_key(event)
            if action == MenuAction.EXIT:
                self.canvas.loop_exit()
            elif action == MenuAction.START_GAME:
                self._create_game()
                self.screen = Screen.PLAYING
        elif self.screen == Screen.PLAYING:
            action = self.game_controller.handle_key(event)
            if action == GamePhase.PAUSED:
                self.screen = Screen.PAUSED
        elif self.screen == Screen.PAUSED:
            action = self.pause.handle_key(event)
            if action == PauseAction.RESUME:
                self.screen = Screen.PLAYING
                self.game_controller.resume()
            elif action == PauseAction.MAIN_MENU:
                self.screen = Screen.MENU
        elif self.screen == Screen.END:
            if self.end_screen.handle_key(event) is not None:
                self.highscores.score.append(
                    Score(
                        username=self.end_screen.name,
                        score=self.end_screen.score
                    )
                )
                self.end_screen.name = ""
                self._refresh_highscores()
                self.highscores.save_json(Path(self.config.highscore_filename))
                self.screen = Screen.MENU

    def on_frame(self, dt: float) -> None:
        self.canvas.clear()
        if self.screen == Screen.MENU:
            self.menu.draw(self.canvas)
        elif self.screen == Screen.PLAYING:
            self.renderer.draw(self.game_controller.state)
            draw_hud(self.canvas, self.game_controller.state)
            self.game_controller.update(dt)
            if self.game_controller.state.phase == GamePhase.GAME_OVER:
                self.end_screen.victory = False
                self.end_screen.score = self.game_controller.state.player.score
                self.screen = Screen.END
            elif self.game_controller.state.phase == GamePhase.VICTORY:
                self.end_screen.victory = True
                self.end_screen.score = self.game_controller.state.player.score
                self.screen = Screen.END
        elif self.screen == Screen.PAUSED:
            self.pause.draw(self.canvas)
        elif self.screen == Screen.END:
            self.end_screen.draw(self.canvas)


def main() -> None:
    if len(sys.argv) != 2:
        print("Error: no configuration file given.", file=sys.stderr)
        sys.exit(1)
    config = load_config(sys.argv[1])

    maze_width = max(level.width for level in config.levels) * TILE_SIZE
    window_width = max(MIN_WINDOW_WIDTH, maze_width)
    window_height = max(level.height
                        for level in config.levels) * TILE_SIZE + HUD_HEIGHT

    with Canvas(window_width, window_height, "PAC-MAN") as canvas:
        app = App(canvas, config)
        canvas.key_hook(app.on_key)
        canvas.loop_hook(app.on_frame)
        canvas.loop()


if __name__ == "__main__":
    main()
