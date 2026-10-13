"""Entry point of the Pac-Man game: parses arguments and runs the app."""

import os
import sys
from ui.menu import MAX_HIGHSCORE
from models import Configuration, GamePhase
from pydantic import ValidationError
from configuration import ConfigLoader
from highscores import Highscores, Score
from ui import (Canvas, Menu, MenuAction,
                Event, draw_hud, Renderer,
                PauseAction, PauseMenu, EndScreen,
                draw_level_complete)
from pathlib import Path
from enum import Enum, auto
from levels_generator import LevelsGenerator
from controllers import GameController
from constants import TILE_SIZE, MAX_WINDOW, MIN_WINDOW, HUD_HEIGHT


class Screen(Enum):
    """Top-level screens the application can display."""

    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    END = auto()


class App():
    """Glue between the canvas, the menus and the game controller.

    Routes key events and frame updates to the active screen and handles
    transitions between them (menu, game, pause, end screen).
    """

    def __init__(self, canvas: Canvas, config: Configuration,
                 tile_size: int = TILE_SIZE) -> None:
        """Initialize the application and load the highscores.

        Args:
            canvas (Canvas): Canvas to draw on.
            config (Configuration): Validated game configuration.
            tile_size (int): Size of one maze tile, in pixels.
        """
        self.canvas = canvas
        self.config = config
        try:
            highscores = Highscores.load_json(Path(config.highscore_filename))
        except (ValidationError, OSError, ValueError) as e:
            print(f"Warning: {e}", file=sys.stderr)
            highscores = Highscores()
        self.highscores = highscores
        self.tile_size = tile_size
        self.renderer = Renderer(self.canvas, self.tile_size)
        self.screen = Screen.MENU
        self.pause = PauseMenu()
        self.menu = Menu()
        self.end_screen = EndScreen(victory=False, score=0)
        self._refresh_highscores()
        self.game_controller: GameController

    def _refresh_highscores(self) -> None:
        """Copy the best highscores, sorted, into the main menu."""
        ranked = sorted(self.highscores.score, key=lambda s: s.score,
                        reverse=True)
        top = ranked[:MAX_HIGHSCORE]
        self.menu.highscore = [(s.username, s.score) for s in top]

    def _save_score(self, name: str, score: int) -> None:
        """Add a score, keep the best ones and write them to disk.

        Args:
            name (str): Player name, validated by the end screen.
            score (int): Final score of the game.
        """
        self.highscores.score.append(Score(username=name, score=score))
        self.highscores.score = sorted(self.highscores.score,
                                       key=lambda s: s.score,
                                       reverse=True)[:MAX_HIGHSCORE]
        self._refresh_highscores()
        try:
            self.highscores.save_json(Path(self.config.highscore_filename))
        except OSError as e:
            print(f"Warning: could not save highscores: {e}",
                  file=sys.stderr)

    def _create_game(self) -> GameController | None:
        """Generate fresh levels and create a new game controller.

        On failure, the error is logged and shown on the main menu.

        Returns:
            GameController | None: Controller of the new game, or None if
                the levels could not be generated.
        """
        try:
            levels_gen = LevelsGenerator(self.config)
        except Exception as e:
            msg = str(e) or type(e).__name__
            print(f"Error: level generation failed: {msg}", file=sys.stderr)
            self.menu.error = f"Generation failed: {msg}"
            return None
        self.menu.error = None
        return GameController(levels_gen, self.config)

    def on_key(self, event: Event) -> None:
        """Dispatch a key event to the active screen.

        Args:
            event (Event): Key event to handle.
        """
        if self.screen == Screen.MENU:
            menu_action = self.menu.handle_key(event)
            if menu_action == MenuAction.EXIT:
                self.canvas.loop_exit()
            elif menu_action == MenuAction.START_GAME:
                controller = self._create_game()
                if controller is not None:
                    self.game_controller = controller
                    self.screen = Screen.PLAYING
        elif self.screen == Screen.PLAYING:
            phase = self.game_controller.handle_key(event)
            if phase == GamePhase.PAUSED:
                self.screen = Screen.PAUSED
        elif self.screen == Screen.PAUSED:
            pause_action = self.pause.handle_key(
                event, self.game_controller.state.cheats)
            if pause_action == PauseAction.RESUME:
                self.screen = Screen.PLAYING
                self.game_controller.resume()
            elif pause_action == PauseAction.MAIN_MENU:
                self.screen = Screen.MENU
        elif self.screen == Screen.END:
            name = self.end_screen.handle_key(event)
            if name is not None:
                self._save_score(name, self.end_screen.score)
                self.end_screen.name = ""
                self.screen = Screen.MENU

    def on_frame(self, dt: float) -> None:
        """Update the game logic and draw the active screen.

        Args:
            dt (float): Elapsed time since the previous frame, in seconds.
        """
        self.canvas.clear()
        if self.screen == Screen.MENU:
            self.menu.draw(self.canvas)
        elif self.screen == Screen.PLAYING:
            self.renderer.draw(self.game_controller.state)
            draw_hud(self.canvas, self.game_controller.state)
            if self.game_controller.state.phase == GamePhase.LEVEL_COMPLETED:
                draw_level_complete(self.canvas, self.game_controller.state)
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
            self.pause.draw(self.canvas, self.game_controller.state.cheats)
        elif self.screen == Screen.END:
            self.end_screen.draw(self.canvas)


def main() -> None:
    """Load the configuration given on the command line and run the game."""
    args = sys.argv[1:]
    if not args and getattr(sys, "frozen", False):
        # Packaged build: config.json and highscores live next to the binary
        os.chdir(Path(sys.executable).parent)
        args = ["config.json"]
    if len(args) != 1:
        print("Error: no configuration file given.", file=sys.stderr)
        sys.exit(1)
    try:
        config = ConfigLoader(args[0]).load()

        maze_w = config.width
        maze_h = config.height

        tile = min(TILE_SIZE,
                   MAX_WINDOW[0] // maze_w,
                   (MAX_WINDOW[1] - HUD_HEIGHT) // maze_h)

        window_w = max(MIN_WINDOW[0], maze_w * tile)
        window_h = max(MIN_WINDOW[1], maze_h * tile + HUD_HEIGHT)
        with Canvas(window_w, window_h, "PAC-MAN") as canvas:
            app = App(canvas, config, tile_size=tile)
            canvas.key_hook(app.on_key)
            canvas.loop_hook(app.on_frame)
            canvas.loop()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Error: Keyboard interruption", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
