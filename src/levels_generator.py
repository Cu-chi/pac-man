from mazegenerator import MazeGenerator
from models import Configuration, Level


class LevelsGenerator:
    def __init__(self, config: Configuration) -> None:
        self.levels: list[Level] = []
        for i, level in enumerate(config.levels):
            maze = MazeGenerator(
                size=(level.width, level.height),
                seed=config.seed if i == 0 else 0
            )
            self.levels.append(Level(
                width=level.width,
                height=level.height,
                walls=maze.maze,
                pacgums=set(),
                super_pacgums=set(),
                ghost_spawns=[],
                player_spawn=self.find_player_spawn(level.width,
                                                    level.height, maze.maze),
            ))

    @staticmethod
    def find_player_spawn(width: int, height: int,
                          maze: list[list[int]]) -> tuple[int, int]:
        """Find a spawn at the middle for the player.

        Args:
            width (int): Maze width
            height (int): Maze height
            maze (list[list[int]]): The maze

        Returns:
            tuple[int, int]: x, y coords
        """
        center_x: int = width // 2
        center_y: int = height // 2

        offsets: list[tuple[int, int]] = [
            (0, 0),
            (0, -1), (0, 1), (-1, 0), (1, 0),
            (-1, -1), (1, -1), (-1, 1), (1, 1),
        ]

        for dx, dy in offsets:
            x: int = center_x + dx
            y: int = center_y + dy

            if 0 <= x < width and 0 <= y < height:
                if maze[y][x] != 15:
                    return (x, y)

        return (center_x, center_y)
