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


def draw_pacgum(canvas: Canvas, level: Level, tile_size: int) -> None:
    """
    Draw the pacgums and super pacgums of a level on the canvas.

    Each gum is a small square centered in its tile. Super pacgums are
    drawn larger and in a different color than regular pacgums.

    Args:
        canvas: Canvas to draw on.
        level: Level providing the pacgum and super pacgum positions.
        tile_size: Size of one tile, in pixels.
    """
    pacgum_size = tile_size // 6
    pacgum_color: Color = (255, 255, 224)
    supergum_size = tile_size // 3
    supergum_color: Color = (255, 205, 155)
    for (x, y) in level.pacgums:
        center_x = x * tile_size + tile_size // 2
        center_y = y * tile_size + tile_size // 2
        canvas.draw_rect(center_x - pacgum_size // 2,
                         center_y - pacgum_size // 2,
                         pacgum_size, pacgum_size, pacgum_color)
    for (x, y) in level.super_pacgums:
        center_x = x * tile_size + tile_size // 2
        center_y = y * tile_size + tile_size // 2
        canvas.draw_rect(center_x - supergum_size // 2,
                         center_y - supergum_size // 2,
                         supergum_size, supergum_size, supergum_color)
