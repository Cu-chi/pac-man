from models import Level, Direction
from canvas import Canvas, Color

WALL_THICKNESS = 2
WALL_COLOR: Color = (33, 33, 222)


def draw_maze(canvas: Canvas, level: Level, tile_size: int) -> None:
    """
    Draw the maze walls of a level on the canvas.

    Each cell stores its walls as a bitmask; for every direction whose bit
    is set, a thin rectangle is drawn along the matching edge of the tile.

    Args:
        canvas: Canvas to draw on.
        level: Level providing the grid dimensions and wall bitmasks.
        tile_size: Size of one tile, in pixels.
    """
    for y in range(level.height):
        for x in range(level.width):
            px, py = x * tile_size, y * tile_size
            cell = level.walls[y][x]
            for direction in Direction:
                dx, dy, bit = direction.value
                if cell & bit:
                    w = WALL_THICKNESS if dx != 0 else tile_size
                    h = WALL_THICKNESS if dy != 0 else tile_size
                    wall_x = (px + (tile_size - WALL_THICKNESS) if dx > 0
                              else px)
                    wall_y = (py + (tile_size - WALL_THICKNESS) if dy > 0
                              else py)
                    canvas.draw_rect(wall_x, wall_y, w, h, WALL_COLOR)
