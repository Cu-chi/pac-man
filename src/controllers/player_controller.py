from controllers.base_controller import BaseEntityController
from models import PlayerData, Level, Direction
from ui.events import Event, EventType, Key


class PlayerController(BaseEntityController[PlayerData]):
    """Controller for the player-driven Pac-man entity."""

    def __init__(
        self, player_data: PlayerData, level: Level, speed: float = 6.0
    ) -> None:
        super().__init__(player_data, level, speed)

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

    def _choose_direction(self) -> Direction | None:
        """Return and clear the buffered player direction.

        Returns:
            Direction | None: the actual direction
        """
        return self._entity.next_direction
