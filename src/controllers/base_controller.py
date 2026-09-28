from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from models import Entity, Level, Direction

T = TypeVar("T", bound=Entity)


class BaseEntityController(ABC, Generic[T]):
    """Abstract controller managing movement timing and collision for entities.

    Attributes:
        _entity (T): The entity data model (Player or Ghost).
        _level (Level): The current level geometry.
        _speed (float): Movement speed in tiles per second.
        _move_timer (float): Time accumulator for grid stepping.
    """

    def __init__(self, entity: T, level: Level, speed: float) -> None:
        """Initialize the base entity controller.

        Args:
            entity (T): Entity instance to control.
            level (Level): Level where the entity evolves.
            speed (float): Movement speed in tiles per second.
        """
        self._entity: T = entity
        self._level: Level = level
        self._speed: float = speed
        self._move_timer: float = 0.0

    @property
    def speed(self) -> float:
        """Get the current movement speed."""
        return self._speed

    @speed.setter
    def speed(self, value: float) -> None:
        """Set the movement speed (useful for cheats and ghost modes)."""
        self._speed = max(0.0, value)

    def update(self, dt: float) -> None:
        """Advance entity movement accumulator and step if needed.

        Args:
            dt (float): Elapsed time since last frame in seconds.
        """
        if self._speed <= 0.0:
            return

        step_interval = 1.0 / self._speed
        self._move_timer += dt

        while self._move_timer >= step_interval:
            self._move_step()
            self._move_timer -= step_interval

    def _move_step(self) -> None:
        """Execute a single movement step on the grid."""
        next_dir = self._choose_direction()

        if next_dir is not None and self._can_move(next_dir):
            self._entity.direction = next_dir

        if self._can_move(self._entity.direction):
            dx, dy, _ = self._entity.direction.value
            cx, cy = self._entity.position
            self._entity.position = (cx + dx, cy + dy)

    def _can_move(self, direction: Direction) -> bool:
        """Check if moving in the given direction is blocked by a wall bitmask.

        Args:
            direction (Direction): Target direction to test.

        Returns:
            bool: True if the path is open, False otherwise.
        """
        _, _, wall_bit = direction.value
        cx, cy = self._entity.position
        return (self._level.walls[cy][cx] & wall_bit) == 0

    @abstractmethod
    def _choose_direction(self) -> Direction | None:
        """Determine the next desired direction.

        Must be implemented by child classes (keyboard input or AI logic).

        Returns:
            Direction | None: The next requested direction, if any.
        """
        pass
