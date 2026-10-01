from canvas import Canvas
from dataclasses import dataclass
from enum import Enum, auto
from events import Event, EventType, Key

MENU_OPTIONS = ["Start Game", "Instructions", "View Highscores",
                "Exit"]
TITLE_COLOR = (255, 205, 155)
OPTION_COLOR = (255, 255, 224)
SELECTED_COLOR = (255, 255, 0)


class ScreenMenu(Enum):

    MAIN = auto()
    HIGHSCORES = auto()
    INSTRUCTIONS = auto()


class MenuAction(Enum):

    START_GAME = auto()
    EXIT = auto()


@dataclass(slots=True, kw_only=True)
class Menu:

    screen: ScreenMenu = ScreenMenu.MAIN
    selected: int = 0

    def handle_key(self, event: Event) -> MenuAction | None:

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
        pass

    def _draw_main(self, canvas: Canvas):

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
