from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any
from pydantic import BaseModel, Field, field_validator, ValidationInfo, \
    ValidationError, model_validator
from pydantic.fields import FieldInfo


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

    @model_validator(mode="before")
    @classmethod
    def warn_on_missing_fields(cls, data: Any) -> dict:
        if isinstance(data, dict):
            for field_name, field_info in cls.model_fields.items():
                if field_name not in data:
                    def_val = field_info.get_default(call_default_factory=True)
                    print(f"Missing key '{field_name}' in JSON. Setting "
                          f" default value {def_val}")
        return data

    @field_validator("*", mode="wrap")
    @classmethod
    def fallback_to_default_on_error(cls, value: Any, handler,
                                     info: ValidationInfo) -> Any:
        try:
            return handler(value)
        except ValidationError as exc:
            field_name = info.field_name
            field_info: FieldInfo | None = None
            if field_name is not None:
                field_info = cls.model_fields.get(field_name)

            # if no default value, raise exception
            if field_info is None or field_info.is_required():
                raise exc

            default_val = field_info.get_default(call_default_factory=True)

            print(f"Invalid value for '{field_name}':"
                  f" {exc.errors()[0]['msg']}, setting default value"
                  f" '{default_val}'")
            return default_val


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
