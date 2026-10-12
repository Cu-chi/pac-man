"""Data models: configuration, level, entities and game state."""

import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Self
from pydantic import BaseModel, Field, field_validator, ValidationInfo, \
    ValidationError, model_validator, ValidatorFunctionWrapHandler
from pydantic.fields import FieldInfo
from constants import MAX_MAZE_WIDTH, MAX_MAZE_HEIGHT


class LevelConfig(BaseModel):
    """Size of a single level, in tiles."""

    width: int = Field(default=10, ge=5, le=MAX_MAZE_WIDTH)
    height: int = Field(default=10, ge=5, le=MAX_MAZE_HEIGHT)


class Configuration(BaseModel):
    """Game configuration loaded from the JSON file.

    Invalid values fall back to their default with a warning, missing keys
    are reported and unknown keys are ignored.
    """

    highscore_filename: str = "highscores.json"
    height: int = Field(default=10, ge=5, le=MAX_MAZE_HEIGHT)
    width: int = Field(default=10, ge=5, le=MAX_MAZE_WIDTH)
    lives: int = Field(default=3, ge=1)
    points_per_pacgum: int = Field(default=10, ge=0)
    points_per_super_pacgum: int = Field(default=50, ge=0)
    points_per_ghost: int = Field(default=200, ge=0)
    seed: int = Field(default=42, gt=0)
    level_max_time: int = Field(default=300, gt=0)
    player_speed: float = Field(default=6.0, ge=1.0, le=15.0)
    ghost_speed: float = Field(default=5.0, ge=1.0, le=15.0)
    ghost_scared_timer: float = Field(default=10.0, ge=3.0)
    ghost_respawn_timer: float = Field(default=10.0, ge=3.0)
    ghost_scared_multiplier: float = Field(default=0.75, ge=0.0, le=2.0)

    @property
    def levels(self) -> list[LevelConfig]:
        """Build the configuration of the 10 levels of a game.

        Returns:
            list[LevelConfig]: One entry per level, all the same size.
        """
        return [
            LevelConfig(width=self.width, height=self.height)
            for _ in range(10)
        ]

    @model_validator(mode="before")
    @classmethod
    def warn_on_missing_fields(cls, data: Any) -> Any:
        """Warn about every missing key before validation.

        Args:
            data (Any): Raw data being validated.

        Returns:
            Any: The data, unchanged.
        """
        if isinstance(data, dict):
            for field_name, field_info in cls.model_fields.items():
                if field_name not in data:
                    def_val = field_info.get_default(call_default_factory=True)
                    print(f"Missing key '{field_name}' in JSON. Setting "
                          f" default value {def_val}", file=sys.stderr)
        return data

    @model_validator(mode="after")
    def pad_levels(self) -> Self:
        """Ensure the game has at least 10 levels.

        Returns:
            Self: The validated configuration.
        """
        if len(self.levels) < 10:
            print(f"Warning: config has only {len(self.levels)} levels, "
                  f"padding to 10 with defaults.", file=sys.stderr)
            while len(self.levels) < 10:
                self.levels.append(LevelConfig())
        return self

    @field_validator("*", mode="wrap")
    @classmethod
    def fallback_to_default_on_error(cls, value: Any,
                                     handler: ValidatorFunctionWrapHandler,
                                     info: ValidationInfo) -> Any:
        """Validate a field, falling back to its default when invalid.

        Args:
            value (Any): Raw value of the field.
            handler (ValidatorFunctionWrapHandler): Standard validator.
            info (ValidationInfo): Information about the field.

        Raises:
            ValidationError: If the value is invalid and has no default.

        Returns:
            Any: The validated value, or the default one.
        """
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
                  f" '{default_val}'", file=sys.stderr)
            return default_val


class Direction(Enum):
    """Movement directions, as (dx, dy, wall bit) tuples."""

    UP = (0, -1, 1)
    RIGHT = (1, 0, 2)
    DOWN = (0, 1, 4)
    LEFT = (-1, 0, 8)


@dataclass(slots=True, kw_only=True)
class Level():
    """Maze layout, pacgums and spawn points of a level."""

    width: int
    height: int
    walls: list[list[int]]
    pacgums: set[tuple[int, int]]
    super_pacgums: set[tuple[int, int]]
    ghost_spawns: list[tuple[int, int]]
    player_spawn: tuple[int, int]


@dataclass(slots=True, kw_only=True)
class Entity():
    """Base data of anything moving on the grid."""

    position: tuple[int, int]
    direction: Direction


@dataclass(slots=True, kw_only=True)
class PlayerData(Entity):
    """Player data: lives, score and buffered direction."""

    lives: int
    score: int
    next_direction: Direction | None = None


class GhostState(Enum):
    """Behaviour modes of a ghost."""

    CHASE = auto()
    SCARED = auto()
    EATEN = auto()


@dataclass(slots=True, kw_only=True)
class GhostData(Entity):
    """Ghost data: state, color, respawn timer and spawn point."""

    state: GhostState
    color: str
    # eaten state timer
    respawn_timer: float
    spawn: tuple[int, int]


@dataclass(slots=True, kw_only=True)
class Cheats():
    """Cheats toggled from the pause menu."""

    invincible: bool = False
    ghosts_freeze: bool = False
    skip_level: bool = False
    noclip: bool = False


class GamePhase(Enum):
    """Phases a game can be in."""

    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    VICTORY = auto()
    LEVEL_COMPLETED = auto()


class GameEvent(Enum):
    """Notable events raised during a game."""

    PACGUM_EATEN = auto()
    GHOST_EATEN = auto()
    LIFE_LOST = auto()
    LEVEL_WON = auto()


@dataclass(slots=True, kw_only=True)
class GameState():
    """Full state of a running game."""

    player: PlayerData
    ghosts: list[GhostData]
    level: Level
    level_index: int
    total_levels: int
    time_left: float
    scared_time_left: float = 0.0
    cheats: Cheats = field(default_factory=Cheats)
    phase: GamePhase = GamePhase.MENU
    events: list[GameEvent] = field(default_factory=list)
