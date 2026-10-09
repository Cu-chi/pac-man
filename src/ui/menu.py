from ui.canvas import Canvas
from dataclasses import dataclass, field
from enum import Enum, auto
from ui.events import Event, EventType, Key

MENU_OPTIONS = ["Start Game", "Instructions", "View Highscores",
                "Exit"]
TITLE_COLOR = (255, 205, 155)
OPTION_COLOR = (255, 255, 224)
SELECTED_COLOR = (255, 255, 0)
MAX_HIGHSCORE = 10
INSTRUCTIONS_TEXT = [
    "Move with the arrow keys or WASD",
    "To finish the level, eat every pacgums",
    "Super-pacgums let you eat ghosts for a short time",
    "ESCAPE to pause the game"
]


class ScreenMenu(Enum):
    """Sub-screens the main menu can display."""

    MAIN = auto()
    HIGHSCORES = auto()
    INSTRUCTIONS = auto()


class MenuAction(Enum):
    """Outcomes the main menu can hand back to its caller."""

    START_GAME = auto()
    EXIT = auto()


@dataclass(slots=True, kw_only=True)
class Menu:
    """
    Main menu: navigation and rendering for Start/Highscores/Instructions/Exit.

    Attributes:
        screen: Sub-screen currently displayed.
        selected: Index of the highlighted option on the main screen.
        highscore: Top scores shown on the highscores screen, as
            (name, score) pairs already sorted best first.
    """

    screen: ScreenMenu = ScreenMenu.MAIN
    selected: int = 0
    highscore: list[tuple[str, int]] = field(default_factory=list)

    def handle_key(self, event: Event) -> MenuAction | None:
        """Update the menu in response to a key press.

        On a sub-screen (highscores, instructions), only ESCAPE is
        handled, to go back to the main options.

        Args:
            event: Key event to react to.

        Returns:
            The action to perform (start the game, exit), or None while
            the menu keeps navigating internally.
        """
        if event.type != EventType.KEY_DOWN:
            return None

        if self.screen != ScreenMenu.MAIN:
            if event.key == Key.ESCAPE:
                self.screen = ScreenMenu.MAIN
            return None

        if self.screen == ScreenMenu.MAIN:
            if event.key == Key.UP:
                self.selected = (self.selected - 1) % len(MENU_OPTIONS)
            elif event.key == Key.DOWN:
                self.selected = (self.selected + 1) % len(MENU_OPTIONS)
            elif event.key == Key.ENTER:
                match MENU_OPTIONS[self.selected]:
                    case "Start Game":
                        return MenuAction.START_GAME
                    case "Instructions":
                        self.screen = ScreenMenu.INSTRUCTIONS
                    case "View Highscores":
                        self.screen = ScreenMenu.HIGHSCORES
                    case "Exit":
                        return MenuAction.EXIT
        return None

    def draw(self, canvas: Canvas) -> None:
        """
        Draw the current sub-screen onto the canvas.

        Args:
            canvas: Canvas to draw on.
        """
        match self.screen:
            case ScreenMenu.MAIN:
                self._draw_main(canvas)
            case ScreenMenu.HIGHSCORES:
                self._draw_highscore(canvas)
            case ScreenMenu.INSTRUCTIONS:
                self._draw_instruction(canvas)

    def _draw_main(self, canvas: Canvas) -> None:
        """
        Draw the title and the Start/Highscores/Instructions/Exit list.

        Args:
            canvas: Canvas to draw on.
        """
        line_height = 50
        block_height = len(MENU_OPTIONS) * line_height
        start_y = (canvas.height - block_height) // 2
        canvas.draw_text("PAC-MAN", canvas.width // 2, start_y - 60,
                         TITLE_COLOR, size=64, centered=True)
        for index, label in enumerate(MENU_OPTIONS):
            y = start_y + index * line_height + line_height // 2
            color = SELECTED_COLOR if index == self.selected else OPTION_COLOR
            canvas.draw_text(label, canvas.width // 2, y, color,
                             size=36, centered=True)

    def _draw_highscore(self, canvas: Canvas) -> None:
        """
        Draw the highscores, or a placeholder when there are none.

        Args:
            canvas: Canvas to draw on.
        """
        title_area = 120
        bottom_margin = 30
        available = canvas.height - title_area - bottom_margin
        line_height = min(50, available // MAX_HIGHSCORE)
        font_size = max(12, int(line_height * 0.56))
        block_height = len(self.highscore) * line_height
        start_y = title_area + (available - block_height)
        canvas.draw_text("HIGHSCORES", canvas.width // 2, title_area // 2,
                         TITLE_COLOR, size=64, centered=True)
        if not self.highscore:
            canvas.draw_text("No scores yet", canvas.width // 2,
                             canvas.height // 2, OPTION_COLOR, size=28,
                             centered=True)
        for index, (name, score) in enumerate(self.highscore):
            line = f"{index + 1}. {name}: {score}"
            y = start_y + index * line_height + line_height // 2
            canvas.draw_text(line, canvas.width // 2, y, OPTION_COLOR,
                             size=font_size, centered=True)

    def _draw_instruction(self, canvas: Canvas) -> None:
        """
        Draw the controls and rules summary.

        Args:
            canvas: Canvas to draw on.
        """
        line_height = 50
        block_height = len(INSTRUCTIONS_TEXT) * line_height
        start_y = (canvas.height - block_height) // 2
        canvas.draw_text("Instructions", canvas.width // 2, start_y - 60,
                         TITLE_COLOR, size=64, centered=True)
        for index, line in enumerate(INSTRUCTIONS_TEXT):
            y = start_y + index * line_height + line_height // 2
            canvas.draw_text(line, canvas.width // 2, y, OPTION_COLOR,
                             size=24, centered=True)
