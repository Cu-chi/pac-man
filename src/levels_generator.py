from mazegenerator import MazeGenerator
from models import Configuration, Level
import random


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
            player_spawn = self.find_player_spawn(level.width, level.height,
                                                  maze.maze)
            pacgums = self.create_pacgums(level.width, level.height,
                                          maze.maze, player_spawn)
            self.levels.append(Level(
                width=level.width,
                height=level.height,
                walls=maze.maze,
                pacgums=pacgums,
                super_pacgums={
                    (0, 0),
                    (level.width - 1, 0),
                    (level.width - 1, level.height - 1),
                    (0, level.height - 1),
                },
                ghost_spawns=[
                    (0, 0),
                    (level.width - 1, 0),
                    (level.width - 1, level.height - 1),
                    (0, level.height - 1),
                ],
                player_spawn=player_spawn,
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

    @staticmethod
    def create_pacgums(width: int, height: int,
                       maze: list[list[int]],
                       player_spawn: tuple[int, int]) -> set[tuple[int, int]]:
        """Create pacgums randomly on available cells.

        Args:
            width (int): Width of the maze
            height (int): Height of the maze
            maze (list[list[int]]): Maze
            player_spawn (tuple[int, int]): Player spawn

        Returns:
            set[tuple[int, int]]: set of pacgums positions
        """
        pacgums: set[tuple[int, int]] = set()
        for y in range(height):
            for x in range(width):
                if maze[y][x] != 15 and (x, y) != player_spawn:
                    # 90% chance that a pacgum spawns on the cell
                    if random.random() >= 0.1:
                        pacgums.add((x, y))
        return pacgums
