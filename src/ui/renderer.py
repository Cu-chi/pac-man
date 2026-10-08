from models import (Level, Direction, PlayerData, GhostData, GhostState,
                    GameState)
from ui.canvas import Canvas, Color
from ui.screens import HUD_HEIGHT


class Renderer:
    """
    Draw the game state (maze, pacgums, player, ghosts) on a canvas.

    The maze is centered in the space left above the HUD; every drawing
    goes through grid-to-pixel helpers that apply this offset.
    """

    WALL_THICKNESS = 2
    WALL_COLOR: Color = (33, 33, 222)
    PACGUM_COLOR: Color = (255, 255, 224)
    SUPERGUM_COLOR: Color = (255, 205, 155)

    def __init__(self, canvas: Canvas, tile_size: int) -> None:
        """
        Create a renderer bound to a canvas.

        Args:
            canvas: Canvas to draw on.
            tile_size: Size of one tile, in pixels.
        """
        self.canvas = canvas
        self.tile_size = tile_size
        self.offset: tuple[int, int] = (0, 0)

    def draw(self, state: GameState) -> None:
        """
        Draw the maze, pacgums, player and ghosts of a game state.

        The maze is recentered on the current level before drawing.

        Args:
            state: Game state providing the level, player and ghosts.
        """
        self._compute_offset(state.level)
        self._draw_maze(state.level)
        self._draw_pacgums(state.level)
        self._draw_player(state.player)
        self._draw_ghosts(state.ghosts)

    def _compute_offset(self, level: Level) -> None:
        """
        Update the offset so the level is centered above the HUD.

        Args:
            level: Level providing the grid dimensions.
        """
        self.offset = ((self.canvas.width - level.width * self.tile_size) // 2,
                       (self.canvas.height - HUD_HEIGHT - level.height *
                        self.tile_size) // 2)

    def _tile_to_pixel(self, x: int, y: int) -> tuple[int, int]:
        """
        Convert grid coordinates to the pixel position of a tile.

        Args:
            x: Column index in the grid.
            y: Row index in the grid.

        Returns:
            The (x, y) pixel position of the tile's top-left corner on
            the canvas, offset included.
        """
        ox, oy = self.offset
        return ox + x * self.tile_size, oy + y * self.tile_size

    def _tile_to_center(self, x: int, y: int) -> tuple[int, int]:
        """
        Convert grid coordinates to the pixel position of a tile's center.

        Args:
            x: Column index in the grid.
            y: Row index in the grid.

        Returns:
            The (x, y) pixel position of the tile's center on the canvas,
            offset included.
        """
        px, py = self._tile_to_pixel(x, y)
        center_x = px + self.tile_size // 2
        center_y = py + self.tile_size // 2
        return (center_x, center_y)

    def _draw_square_centered(self, x: int, y: int, size: int,
                              color: Color) -> None:
        """
        Draw a square centered in a tile.

        Args:
            x: Column index in the grid.
            y: Row index in the grid.
            size: Side length of the square, in pixels.
            color: Fill color of the square.
        """
        cx, cy = self._tile_to_center(x, y)
        self.canvas.draw_rect(cx - size // 2,
                              cy - size // 2,
                              size,
                              size,
                              color)

    def _draw_sprite(self, path: str, x: int, y: int) -> None:
        """
        Draw an image scaled to one tile, at a tile of the grid.

        Args:
            path: Path to the image file.
            x: Column index in the grid.
            y: Row index in the grid.
        """
        px, py = self._tile_to_pixel(x, y)
        self.canvas.draw_image(self.canvas.load_image(path, self.tile_size),
                               px, py)

    def _draw_maze(self, level: Level) -> None:
        """
        Draw the maze walls of a level.

        Each cell stores its walls as a bitmask; for every direction whose bit
        is set, a thin rectangle is drawn along the matching edge of the tile.

        Args:
            level: Level providing the grid dimensions and wall bitmasks.
        """
        thickness = self.WALL_THICKNESS
        for y in range(level.height):
            for x in range(level.width):
                px, py = self._tile_to_pixel(x, y)
                cell = level.walls[y][x]
                for direction in Direction:
                    dx, dy, bit = direction.value
                    if cell & bit:
                        w = thickness if dx != 0 else self.tile_size
                        h = thickness if dy != 0 else self.tile_size
                        wall_x = (px + (self.tile_size - thickness) if dx > 0
                                  else px)
                        wall_y = (py + (self.tile_size - thickness) if dy > 0
                                  else py)
                        self.canvas.draw_rect(wall_x, wall_y, w, h,
                                              self.WALL_COLOR)

    def _draw_pacgums(self, level: Level) -> None:
        """
        Draw the pacgums and super pacgums of a level.

        Each gum is a small square centered in its tile. Super pacgums are
        drawn larger and in a different color than regular pacgums.

        Args:
            level: Level providing the pacgum and super pacgum positions.
        """
        pacgum_size = self.tile_size // 6
        supergum_size = self.tile_size // 3
        for (x, y) in level.pacgums:
            self._draw_square_centered(x, y, pacgum_size, self.PACGUM_COLOR)
        for (x, y) in level.super_pacgums:
            self._draw_square_centered(x, y, supergum_size,
                                       self.SUPERGUM_COLOR)

    def _draw_player(self, player: PlayerData) -> None:
        """
        Draw the player.

        The sprite matches the player's direction. Its mouth alternates between
        open and closed on the parity of x + y, so it swaps at every move.

        Args:
            player: Player providing the position and direction.
        """
        x, y = player.position
        state = "open" if (x + y) % 2 == 0 else "closed"
        path = (f"src/ui/assets/pacman_{state}"
                f"_{player.direction.name.lower()}.png")
        self._draw_sprite(path, x, y)

    def _draw_ghosts(self, ghosts: list[GhostData]) -> None:
        """
        Draw the ghosts.

        The sprite matches each ghost's direction. Chasing ghosts use their own
        color, scared ghosts share a common sprite, and eaten ghosts are drawn
        as eyes only.

        Args:
            ghosts: Ghosts providing the position, direction, state and color.
        """
        for ghost in ghosts:
            if ghost.state == GhostState.SCARED:
                variant = "scared"
            elif ghost.state == GhostState.EATEN:
                variant = "eaten"
            else:
                variant = ghost.color
            path = (f"src/ui/assets/ghost_{variant}"
                    f"_{ghost.direction.name.lower()}.png")
            x, y = ghost.position
            self._draw_sprite(path, x, y)
