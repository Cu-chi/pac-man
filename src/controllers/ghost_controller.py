from controllers.base_controller import BaseEntityController
from models import GhostData, Level, Direction, PlayerData, GhostState
from collections import deque
import random


OPP_DIR: dict[Direction, Direction] = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT
}


class GhostController(BaseEntityController[GhostData]):
    """Controller for the ghost entities."""

    def __init__(self, ghost_data: GhostData, level: Level,
                 player_data: PlayerData, speed: float = 5.0,
                 scared_speed_multiplier: float = 0.75) -> None:
        super().__init__(ghost_data, level, speed)
        self._player_data = player_data
        self._scared_speed_multiplier = scared_speed_multiplier
        self._base_speed = speed

    def update(self, dt: float, freeze: bool = False) -> None:
        """Update ghost speed according to its state, then step movement.

        Args:
            dt (float): Elapsed time since last frame in seconds.
        """

        match self._entity.state:
            case GhostState.SCARED:
                self.speed = self._base_speed * self._scared_speed_multiplier
            case GhostState.EATEN:
                self.speed = self._base_speed * 1.5  # +50% speed to back
            case GhostState.CHASE:
                self.speed = self._base_speed

        if freeze:
            self.speed = 0.0

        super().update(dt)

    def _choose_direction(self) -> Direction | None:
        """Choose the direction using BFS."""
        reachables = [d for d in Direction if self._can_move(d)]
        if not reachables:
            return None

        opposite_dir = OPP_DIR[self._entity.direction]
        valids = [d for d in reachables if d != opposite_dir] or reachables

        if self._entity.state == GhostState.SCARED:
            return random.choice(valids)

        start = self._entity.position
        target = self._get_target()

        if start == target:
            return self._entity.direction

        queue: deque[tuple[tuple[int, int], Direction]] = deque()
        visited: set[tuple[int, int]] = {start}

        for d in valids:
            dx, dy, _ = d.value
            nxt = (start[0] + dx, start[1] + dy)
            visited.add(nxt)
            queue.append((nxt, d))

        while queue:
            (cx, cy), first_dir = queue.popleft()

            if (cx, cy) == target:
                return first_dir

            cell_walls = self._level.walls[cy][cx]

            for d in Direction:
                dx, dy, wall_bit = d.value
                if (cell_walls & wall_bit) == 0:
                    nxt = (cx + dx, cy + dy)
                    if (
                        0 <= nxt[0] < self._level.width
                        and 0 <= nxt[1] < self._level.height
                        and nxt not in visited
                    ):
                        visited.add(nxt)
                        queue.append((nxt, first_dir))

        return valids[0]

    def _get_target(self) -> tuple[int, int]:
        """Get target according to current GhostState

        Returns:
            tuple[int, int]: Target coords
        """
        if self._entity.state == GhostState.EATEN:
            return self._entity.spawn

        return self._player_data.position
