from models import (
    PlayerData, Level, Direction, Configuration,
    GameState, GameEvent, GhostState)
from ui.events import Event, EventType, Key


class PlayerController:
    """Controls the player movement and input processing."""

    def __init__(self, game_state: GameState, config: Configuration,
                 speed: float = 5.0) -> None:
        self._player_data: PlayerData = game_state.player
        self._level: Level = game_state.level
        self._game_state: GameState = game_state
        self._config: Configuration = config
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

        # pacgums
        if self._player_data.position in self._level.pacgums:
            self._level.pacgums.remove(self._player_data.position)
            self._player_data.score += self._config.points_per_pacgum

        # super pacgums
        if self._player_data.position in self._level.super_pacgums:
            self._level.super_pacgums.remove(self._player_data.position)
            self._player_data.score += self._config.points_per_super_pacgum
            self._game_state.scared_time_left += 10.0

        # ghosts
        for ghost_data in self._game_state.ghosts:
            if ghost_data.state == GhostState.EATEN:
                break
            if ghost_data.position == self._player_data.position:
                if self._game_state.scared_time_left <= 0.0:
                    self._player_data.lives -= 1
                    self._game_state.events += [GameEvent.LIFE_LOST]
                    # TODO: handle respawn
                    break
                # TODO: handle ghost eating from a GhostController class
                self._game_state.events += [GameEvent.GHOST_EATEN]
                self._player_data.score += self._config.points_per_ghost
                ghost_data.respawn_timer = 5.0
                ghost_data.state = GhostState.EATEN
                ghost_data.position = ghost_data.spawn
                break

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
