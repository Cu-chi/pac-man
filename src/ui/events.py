from enum import Enum, auto
from dataclasses import dataclass


class Key(Enum):

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

    QUIT = auto()
    KEY_DOWN = auto()


@dataclass(slots=True, kw_only=True)
class Event():

    type: EventType
    key: Key = Key.OTHER
    char: str = ""
