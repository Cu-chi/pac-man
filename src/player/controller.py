from models import PlayerData, Level, Direction
from ui.events import Event, EventType, Key


class PlayerController:
    """Controls the player movement and input processing."""

    def __init__(self, player_data: PlayerData, level: Level,
                 speed: float = 5.0) -> None:
        self._player_data: PlayerData = player_data
        self._level: Level = level
        self._speed: float = speed  # cells/s
        self._move_accumulator: float = 0.0

    def key_hook(self, event: Event) -> None:
        """Handle keyboard inputs for player direction.

        Args:
            event (Event): Event called
        """
        if event.type == EventType.KEY_DOWN:
            match event.key:
                case Key.UP:
                    self._player_data.next_direction = Direction.UP
                case Key.DOWN:
                    self._player_data.next_direction = Direction.DOWN
                case Key.LEFT:
                    self._player_data.next_direction = Direction.LEFT
                case Key.RIGHT:
                    self._player_data.next_direction = Direction.RIGHT

            match event.char.lower():
                case "w" | "z":
                    self._player_data.next_direction = Direction.UP
                case "s":
                    self._player_data.next_direction = Direction.DOWN
                case "a" | "q":
                    self._player_data.next_direction = Direction.LEFT
                case "d":
                    self._player_data.next_direction = Direction.RIGHT

    def update(self, dt: float) -> None:
        """Update player position based on elapsed time.

        Args:
            dt (float): Elapsed time since last frame in seconds.
        """
        # get necessary time for 1 cell
        step_interval: float = 1.0 / self._speed
        self._move_accumulator += dt

        while self._move_accumulator >= step_interval:
            self._move_step()
            self._move_accumulator -= step_interval

    def _move_step(self) -> None:
        """Move the player by one tile if the path is not blocked."""
        if self._player_data.next_direction is not None:
            if self._can_move(self._player_data.next_direction):
                self._player_data.direction = self._player_data.next_direction
                self._player_data.next_direction = None

        if self._can_move(self._player_data.direction):
            dx, dy, _ = self._player_data.direction.value
            cx, cy = self._player_data.position
            self._player_data.position = (cx + dx, cy + dy)

    def _can_move(self, direction: Direction) -> bool:
        """Check if moving in the given direction hits a wall."""
        dx, dy, wall_flag = direction.value
        cx, cy = self._player_data.position

        if self._level.walls[cy][cx] & wall_flag:
            return False

        nx, ny = cx + dx, cy + dy
        return 0 <= nx < self._level.width and 0 <= ny < self._level.height
