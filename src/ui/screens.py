from canvas import Canvas, Color
from dataclasses import dataclass
from enum import Enum, auto
from events import Event, EventType, Key
from models import GameState

HUD_HEIGHT = 30
HUD_COLOR: Color = (255, 255, 255)
TITLE_COLOR: Color = (255, 205, 155)
OPTION_COLOR: Color = (255, 255, 224)
SELECTED_COLOR: Color = (255, 255, 0)
PAUSE_OPTIONS = ["Resume", "Main Menu"]
NAME_MAX_LENGTH = 10


def draw_hud(canvas: Canvas, state: GameState) -> None:
    """
    Draw the in-game HUD in a bar at the bottom of the canvas.

    Shows the current score, remaining lives, current level and the time
    left for the level.

    Args:
        canvas: Canvas to draw on.
        state: Game state providing the values to display.
    """
    y = canvas.height - HUD_HEIGHT // 2
    items = [
        f"Score: {state.player.score}",
        f"Lives: {state.player.lives}",
        f"Level: {state.level_index + 1}/{state.total_levels}",
        f"Time: {max(0, int(state.time_left))}",
    ]
    column_width = canvas.width // len(items)
    for index, text in enumerate(items):
        x = index * column_width + column_width // 2
        canvas.draw_text(text, x, y, HUD_COLOR, size=22, centered=True)


class PauseAction(Enum):
    """Outcomes the pause menu can hand back to its caller."""

    RESUME = auto()
    MAIN_MENU = auto()


@dataclass(slots=True, kw_only=True)
class PauseMenu:
    """
    Pause menu: lets the player resume or go back to the main menu.

    Attributes:
        selected: Index of the highlighted option.
    """

    selected: int = 0

    def handle_key(self, event: Event) -> PauseAction | None:
        """Update the pause menu in response to a key press.

        ESCAPE resumes the game directly.

        Args:
            event: Key event to react to.

        Returns:
            The action to perform, or None while the player is still
            choosing.
        """
        if event.type != EventType.KEY_DOWN:
            return None
        if event.key == Key.ESCAPE:
            return PauseAction.RESUME
        if event.key == Key.UP:
            self.selected = (self.selected - 1) % len(PAUSE_OPTIONS)
        elif event.key == Key.DOWN:
            self.selected = (self.selected + 1) % len(PAUSE_OPTIONS)
        elif event.key == Key.ENTER:
            if self.selected == 0:
                return PauseAction.RESUME
            return PauseAction.MAIN_MENU
        return None

    def draw(self, canvas: Canvas) -> None:
        """
        Draw the pause title and options on top of the game view.

        Args:
            canvas: Canvas to draw on.
        """
        box_w, box_h = 260, 170
        box_x = (canvas.width - box_w) // 2
        box_y = (canvas.height - box_h) // 2
        canvas.draw_rect(box_x, box_y, box_w, box_h, (0, 0, 0))
        canvas.draw_rect(box_x, box_y, box_w, box_h, TITLE_COLOR,
                         filled=False)
        canvas.draw_text("PAUSE", canvas.width // 2, box_y + 35,
                         TITLE_COLOR, size=48, centered=True)
        for index, label in enumerate(PAUSE_OPTIONS):
            color = SELECTED_COLOR if index == self.selected else OPTION_COLOR
            canvas.draw_text(label, canvas.width // 2,
                             box_y + 90 + index * 40, color,
                             size=32, centered=True)


@dataclass(slots=True, kw_only=True)
class EndScreen:
    """
    Game over / victory screen, with the final score and name entry.

    Attributes:
        victory: True for the victory screen, False for game over.
        score: Final score of the player.
        name: Name typed so far, at most 10 alphanumeric chars or spaces.
    """

    victory: bool
    score: int
    name: str = ""

    def handle_key(self, event: Event) -> str | None:
        """Update the typed name in response to a key press.

        Only letters, digits and spaces are accepted, up to 10 characters.
        BACKSPACE erases the last character.

        Args:
            event: Key event to react to.

        Returns:
            The confirmed name once ENTER is pressed with a non-empty
            name, None otherwise.
        """
        if event.type != EventType.KEY_DOWN:
            return None
        if event.key == Key.ENTER:
            name = self.name.strip()
            if len(name) < 3:
                return None
            return name if name else None
        if event.key == Key.BACKSPACE:
            self.name = self.name[:-1]
        elif (len(event.char) == 1
              and (event.char.isalnum() or event.char == " ")
              and event.char.isascii()
              and len(self.name) < NAME_MAX_LENGTH):
            self.name += event.char
        return None

    def draw(self, canvas: Canvas) -> None:
        """
        Draw the title, final score and name prompt.

        Args:
            canvas: Canvas to draw on.
        """
        center_x = canvas.width // 2
        center_y = canvas.height // 2
        if self.victory:
            title = "VICTORY!"
            message = "Congratulations, you cleared every level!"
        else:
            title = "GAME OVER"
            message = "Better luck next time!"
        canvas.draw_text(title, center_x, center_y - 120, TITLE_COLOR,
                         size=64, centered=True)
        canvas.draw_text(message, center_x, center_y - 60, OPTION_COLOR,
                         size=28, centered=True)
        canvas.draw_text(f"Final score: {self.score}", center_x, center_y,
                         OPTION_COLOR, size=36, centered=True)
        canvas.draw_text("Enter your name:", center_x, center_y + 60,
                         OPTION_COLOR, size=28, centered=True)
        canvas.draw_text(self.name + "_", center_x, center_y + 100,
                         SELECTED_COLOR, size=36, centered=True)
        canvas.draw_text("ENTER to save", center_x, center_y + 150,
                         OPTION_COLOR, size=22, centered=True)
