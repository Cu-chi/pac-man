from dataclasses import dataclass, field
from enum import Enum, auto
from pydantic import BaseModel, Field


class LevelConfig(BaseModel):

    width: int = Field(default=21, ge=5)
    height: int = Field(default=21, ge=5)


class Configuration(BaseModel):

    highscore_filename: str = "highscores.json"
    levels: list[LevelConfig] = Field(
        default_factory=lambda: [LevelConfig() for _ in range(10)])
    lives: int = Field(default=3, ge=1)
    points_per_pacgum: int = Field(default=10, ge=0)
    points_per_super_pacgum: int = Field(default=50, ge=0)
    points_per_ghost: int = Field(default=200, ge=0)
    seed: int | None = 42
    level_max_time: int = Field(default=90, gt=0)


class Direction(Enum):

    UP = (0, -1, 1)
    RIGHT = (1, 0, 2)
    DOWN = (0, 1, 4)
    LEFT = (-1, 0, 8)


@dataclass(slots=True, kw_only=True)
class Level():

    width: int
    height: int
    walls: list[list[int]]
    pacgums: set[tuple[int, int]]
    super_pacgums: set[tuple[int, int]]
    ghost_spawns: list[tuple[int, int]]
    player_spawn: tuple[int, int]


@dataclass(slots=True, kw_only=True)
class Entity():

    x: int
    y: int
    direction: Direction


@dataclass(slots=True, kw_only=True)
class Player(Entity):

    lives: int
    score: int
    next_direction: Direction | None = None


class GhostState(Enum):

    CHASE = auto()
    SCARED = auto()
    EATEN = auto()


@dataclass(slots=True, kw_only=True)
class Ghost(Entity):

    state: GhostState
    color: str
    # eaten state timer
    respawn_timer: float
    spawn: tuple[int, int]


class GamePhase(Enum):

    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    VICTORY = auto()


class GameEvent(Enum):

    PACGUM_EATEN = auto()
    GHOST_EATEN = auto()
    LIFE_LOST = auto()
    LEVEL_WON = auto()


@dataclass(slots=True, kw_only=True)
class GameState():

    player: Player
    ghosts: list[Ghost]
    level: Level
    level_index: int
    total_levels: int
    time_left: float
    scared_time_left: float = 0.0
    phase: GamePhase = GamePhase.MENU
    events: list[GameEvent] = field(default_factory=list)
