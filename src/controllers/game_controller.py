from models import GameState, GamePhase, GhostState, Direction
from controllers.player_controller import PlayerController
from ui.events import Event, EventType
from configuration import Configuration
from controllers.ghost_controller import GhostController


class GameController:
    """Orchestrates entities, collisions, and gameplay rules."""

    def __init__(
        self,
        state: GameState,
        config: Configuration
    ) -> None:
        self._state: GameState = state
        self._player_ctrl = PlayerController(state.player, state.level)
        self._ghost_ctrls = [
            GhostController(ghost, state.level, state.player)
            for ghost in state.ghosts
        ]
        self._config = config

    def update(self, dt: float) -> None:
        """Run one logic frame."""
        if self._state.phase != GamePhase.PLAYING:
            return

        self._update_timers(dt)

        self._player_ctrl.update(dt)
        for g_ctrl in self._ghost_ctrls:
            g_ctrl.update(dt)

        self._check_pacgums()
        self._check_ghost_collisions()
        self._check_game_status()

    def handle_key(self, event: Event) -> None:
        if event.type != EventType.KEY_DOWN:
            return

        if self._state.phase == GamePhase.PLAYING:
            self._player_ctrl.handle_key(event)

    def _update_timers(self, dt: float) -> None:
        """Update level time limit and ghost scared duration."""
        self._state.time_left -= dt
        if self._state.time_left <= 0:
            self._state.phase = GamePhase.GAME_OVER

        if self._state.scared_time_left > 0:
            self._state.scared_time_left = \
                max(0.0, self._state.scared_time_left - dt)
            if self._state.scared_time_left == 0.0:
                for ghost in self._state.ghosts:
                    if ghost.state == GhostState.SCARED:
                        ghost.state = GhostState.CHASE

    def _check_pacgums(self) -> None:
        """Check if player eats a normal or super pacgum."""
        pos = self._state.player.position

        # pacgum
        if pos in self._state.level.pacgums:
            self._state.level.pacgums.remove(pos)
            self._state.player.score += self._config.points_per_pacgum

        # super-pacgum
        if pos in self._state.level.super_pacgums:
            self._state.level.super_pacgums.remove(pos)
            self._state.player.score += self._config.points_per_super_pacgum
            self._state.scared_time_left = 10.0  # TODO: set in config maybe?
            for ghost in self._state.ghosts:
                if ghost.state == GhostState.CHASE:
                    ghost.state = GhostState.SCARED

    def _check_ghost_collisions(self) -> None:
        """Centralized collision check between player and ghosts."""
        player_pos = self._state.player.position

        for ghost in self._state.ghosts:
            if ghost.position == player_pos:
                if ghost.state == GhostState.SCARED:
                    ghost.state = GhostState.EATEN
                    self._state.player.score += self._config.points_per_ghost
                elif ghost.state == GhostState.CHASE:
                    self._state.player.lives -= 1
                    if self._state.player.lives <= 0:
                        self._state.phase = GamePhase.GAME_OVER
                    else:
                        self._reset_positions()
                    break

    def _reset_positions(self) -> None:
        """Reset player and ghosts back to their spawn points after a death."""
        self._state.player.position = self._state.level.player_spawn
        self._state.player.direction = Direction.RIGHT
        self._state.player.next_direction = None
        for ghost in self._state.ghosts:
            ghost.position = ghost.spawn
            ghost.state = GhostState.CHASE

    def _check_game_status(self) -> None:
        """Check victory conditions."""
        if not self._state.level.pacgums \
           and not self._state.level.super_pacgums:
            if self._state.level_index + 1 >= self._state.total_levels:
                self._state.phase = GamePhase.VICTORY
            else:
                #  TODO: next level
                pass
