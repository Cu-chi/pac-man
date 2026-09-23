from mazegenerator import MazeGenerator
from models import Configuration, Level


class SpawnNotFoundException(Exception):
    pass


class LevelsGenerator:
    """Class used to generate levels."""

    def __init__(self, config: Configuration) -> None:
        """Initialize a LevelsGenerator object that contains all levels.

        Each level has its data using the Level model.

        Args:
            config (Configuration): The configuration
        """
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

        raise SpawnNotFoundException()
