from enum import Enum, auto
from dataclasses import dataclass


class Key(Enum):
    """Keyboard keys the game reacts to, independent from pygame's codes."""

    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    ENTER = auto()
    ESCAPE = auto()
    SPACE = auto()
    BACKSPACE = auto()
    OTHER = auto()


class EventType(Enum):
    """Kinds of events `Canvas.key_hook` can report."""

    KEY_DOWN = auto()


@dataclass(slots=True, kw_only=True)
class Event():
    """A single window or keyboard event, independent from pygame.

    Attributes:
        type: Kind of event (window closed, key pressed...).
        key: Key that was pressed, or `Key.OTHER` for an unmapped one.
        char: Character actually typed, e.g. for letters or name entry.
    """

    type: EventType
    key: Key = Key.OTHER
    char: str = ""
