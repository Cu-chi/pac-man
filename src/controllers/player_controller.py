"""Player controller: keyboard-driven Pac-Man movement."""

from controllers.base_controller import BaseEntityController
from models import PlayerData, Level, Direction
from ui.events import Event, EventType, Key


class PlayerController(BaseEntityController[PlayerData]):
    """Controller for the player-driven Pac-man entity."""

    def __init__(
        self, player_data: PlayerData, level: Level, speed: float = 6.0
    ) -> None:
        """Initialize the player controller.

        Args:
            player_data (PlayerData): Player to control.
            level (Level): Level where the player evolves.
            speed (float): Speed, in tiles per second.
        """
        self._noclip = False
        super().__init__(player_data, level, speed)

    def set_noclip(self, state: bool) -> None:
        """Enable or disable walking through walls (cheat).

        Args:
            state (bool): True to ignore walls.
        """
        self._noclip = state

    def handle_key(self, event: Event) -> None:
        """Handle keyboard inputs for player direction.

        Args:
            event (Event): Event called
        """
        if event.type != EventType.KEY_DOWN:
            return

        match event.key:
            case Key.UP:
                self._entity.next_direction = Direction.UP
            case Key.DOWN:
                self._entity.next_direction = Direction.DOWN
            case Key.LEFT:
                self._entity.next_direction = Direction.LEFT
            case Key.RIGHT:
                self._entity.next_direction = Direction.RIGHT

        match event.char.lower():
            case "w" | "z":
                self._entity.next_direction = Direction.UP
            case "s":
                self._entity.next_direction = Direction.DOWN
            case "a" | "q":
                self._entity.next_direction = Direction.LEFT
            case "d":
                self._entity.next_direction = Direction.RIGHT

    def _can_move(self, direction: Direction) -> bool:
        """Check if the player can move, ignoring walls in noclip mode.

        Args:
            direction (Direction): Target direction to test.

        Returns:
            bool: True if the move is allowed, False otherwise.
        """
        if self._noclip:
            dx, dy, _ = direction.value
            cx, cy = self._entity.position
            return (0 <= cx + dx < self._level.width
                    and 0 <= cy + dy < self._level.height)
        return super()._can_move(direction)

    def _choose_direction(self) -> Direction | None:
        """Return the buffered player direction.

        Returns:
            Direction | None: The buffered direction, if any.
        """
        return self._entity.next_direction
