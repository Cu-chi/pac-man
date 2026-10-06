from models import (
    GameState, GamePhase,
    GhostState, Direction,
    GameEvent, PlayerData, GhostData)
from controllers.player_controller import PlayerController
from ui.events import Event, EventType
from configuration import Configuration
from controllers.ghost_controller import GhostController
from levels_generator import LevelsGenerator


class GameController:
    """Orchestrates entities, collisions, and gameplay rules."""

    def __init__(
        self,
        levels_gen: LevelsGenerator,
        config: Configuration
    ) -> None:
        self._levels_gen = levels_gen
        self._config = config

        self._level_index = 0
        self._total_levels: int = len(levels_gen.levels)

        self.state = self._create_game_state(0)
        self._init_controllers()

    def _create_game_state(self, index: int,
                           old_player_data: PlayerData | None = None) \
            -> GameState:
        current_level = self._levels_gen.levels[index]

        player_data = PlayerData(
            position=current_level.player_spawn,
            direction=Direction.RIGHT,
            lives=(
                old_player_data.lives
                if old_player_data else self._config.lives
            ),
            score=old_player_data.score if old_player_data else 0
        )

        ghost_colors = ["red", "pink", "cyan", "orange"]
        ghosts = [
            GhostData(
                position=spawn,
                direction=Direction.LEFT,
                state=GhostState.CHASE,
                color=ghost_colors[i % len(ghost_colors)],
                respawn_timer=0.0,
                spawn=spawn,
            )
            for i, spawn in enumerate(current_level.ghost_spawns)
        ]

        return GameState(
            player=player_data,
            ghosts=ghosts,
            level=current_level,
            level_index=index,
            total_levels=self._total_levels,
            time_left=self._config.level_max_time,
            phase=GamePhase.PLAYING
        )

    def _init_controllers(self) -> None:
        self._player_controller = PlayerController(
            player_data=self.state.player,
            level=self.state.level,
            speed=self._config.player_speed
        )
        self._ghosts_controllers = [
            GhostController(
                ghost_data=ghost_data,
                level=self.state.level,
                player_data=self.state.player,
                speed=self._config.ghost_speed,
                scared_speed_multiplier=self._config.ghost_scared_multiplier
            )
            for ghost_data in self.state.ghosts
        ]

    def update(self, dt: float) -> None:
        """Run one logic frame."""
        if self.state.phase != GamePhase.PLAYING:
            return

        self._update_timers(dt)

        self._player_controller.update(dt)
        for g_ctrl in self._ghosts_controllers:
            g_ctrl.update(dt)

        self._check_pacgums()
        self._check_ghost_collisions()
        self._check_game_status()

    def handle_key(self, event: Event) -> None:
        if event.type != EventType.KEY_DOWN:
            return

        if self.state.phase == GamePhase.PLAYING:
            self._player_controller.handle_key(event)

    def _update_timers(self, dt: float) -> None:
        """Update level time limit and ghost scared duration."""
        self.state.time_left -= dt
        if self.state.time_left <= 0:
            self.state.phase = GamePhase.GAME_OVER

        if self.state.scared_time_left > 0:
            self.state.scared_time_left = \
                max(0.0, self.state.scared_time_left - dt)
            if self.state.scared_time_left == 0.0:
                for ghost in self.state.ghosts:
                    if ghost.state == GhostState.SCARED:
                        ghost.state = GhostState.CHASE

        for ghost in self.state.ghosts:
            if ghost.state == GhostState.EATEN:
                ghost.respawn_timer = max(0.0, ghost.respawn_timer - dt)
                if ghost.respawn_timer == 0.0:
                    ghost.state = GhostState.CHASE

    def _check_pacgums(self) -> None:
        """Check if player eats a normal or super pacgum."""
        pos = self.state.player.position

        # pacgum
        if pos in self.state.level.pacgums:
            self.state.level.pacgums.remove(pos)
            self.state.player.score += self._config.points_per_pacgum

        # super-pacgum
        if pos in self.state.level.super_pacgums:
            self.state.level.super_pacgums.remove(pos)
            self.state.player.score += self._config.points_per_super_pacgum
            self.state.scared_time_left = self._config.ghost_scared_timer
            for ghost in self.state.ghosts:
                if ghost.state == GhostState.CHASE:
                    ghost.state = GhostState.SCARED

    def _check_ghost_collisions(self) -> None:
        """Centralized collision check between player and ghosts."""
        player_pos = self.state.player.position

        for ghost in self.state.ghosts:
            if ghost.position == player_pos:
                if ghost.state == GhostState.SCARED:
                    ghost.state = GhostState.EATEN
                    ghost.respawn_timer += self._config.ghost_respawn_timer
                    self.state.player.score += self._config.points_per_ghost
                elif ghost.state == GhostState.CHASE:
                    self.state.player.lives -= 1
                    if self.state.player.lives <= 0:
                        self.state.phase = GamePhase.GAME_OVER
                    else:
                        self._reset_positions()
                    break

    def _reset_positions(self) -> None:
        """Reset player and ghosts back to their spawn points after a death."""
        self.state.player.position = self.state.level.player_spawn
        self.state.player.direction = Direction.RIGHT
        self.state.player.next_direction = None
        for ghost in self.state.ghosts:
            ghost.position = ghost.spawn
            ghost.state = GhostState.CHASE

    def load_next_level(self) -> None:
        """Advance to the next level or trigger victory."""
        if self._level_index + 1 >= self._total_levels:
            self.state.phase = GamePhase.VICTORY
            return

        self._level_index += 1
        self.state = self._create_game_state(
            self._level_index, old_player_data=self.state.player
        )
        self._init_controllers()
        self.state.events.append(GameEvent.LEVEL_WON)

    def _check_game_status(self) -> None:
        """Check victory conditions."""
        if not self.state.level.pacgums \
           and not self.state.level.super_pacgums:
            self.load_next_level()
