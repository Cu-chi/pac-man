*This project has been created as part of the 42 curriculum by equentin, mchauvin.*

# Pac-man

## Description
The goal is to create a complete and playable Pac-Man game in Python, using
object-oriented programming, a simple graphical library, and a modular, reusable architecture.

## Instructions

## Configuration

**Comment Support**: You can annotate your configuration file using `#` at the beginning of any line to add notes or temporarily disable lines.  
**Automatic Recovery**: If a key is missing, misspelled, or set to an invalid value (e.g., negative lives or an extreme speed), the game will not crash. Instead, it logs a warning and automatically falls back to safe default settings.  
**Minimum Level Guarantee**: The game requires at least 10 levels. If fewer levels are specified in the file, the game automatically completes the list up to 10 using default dimensions.  

### Global Settings

| Setting | Type | Default | Allowed Range | Description |
| :--- | :---: | :---: | :---: | :--- |
| `highscore_filename` | Text | `"highscores.json"` | Valid filename | Name of the file where the top 10 scores are saved. |
| `lives` | Whole number | `3` | At least `1` | Number of lives the player starts with. |
| `level_max_time` | Whole number | `300` | At least `1` | Time limit to finish each level (in seconds). |
| `seed` | Whole number | `42` | Greater than `0` | Starting seed for procedural maze generation (Level 1). |

---

### Scoring Rules

| Setting | Type | Default | Allowed Range | Description |
| :--- | :---: | :---: | :---: | :--- |
| `points_per_pacgum` | Whole number | `10` | 0 or more | Points awarded when eating a standard dot. |
| `points_per_super_pacgum` | Whole number | `50` | 0 or more | Points awarded when eating a large power pellet. |
| `points_per_ghost` | Whole number | `200` | 0 or more | Points awarded when eating a vulnerable (blue) ghost. |

---

### Speeds & Timers (Game Balance)

| Setting | Type | Default | Allowed Range | Description |
| :--- | :---: | :---: | :---: | :--- |
| `player_speed` | Decimal | `6.0` | `1.0` to `15.0` | Pac-Man's movement speed in tiles per second. |
| `ghost_speed` | Decimal | `5.0` | `1.0` to `15.0` | Base movement speed of ghosts in tiles per second. |
| `ghost_scared_timer` | Decimal | `10.0` | At least `3.0` | How long ghosts remain edible after a power pellet (seconds). |
| `ghost_respawn_timer` | Decimal | `10.0` | At least `3.0` | Delay before an eaten ghost returns to normal chasing (seconds). |
| `ghost_scared_multiplier` | Decimal | `0.75` | `0.0` to `2.0` | Speed ratio when ghosts are scared (`0.75` = 25% slower). |

---

### Level Customization (`levels`)

The `levels` key accepts a list of levels. Each level defines the maze grid dimensions:

| Setting | Type | Default | Allowed Range | Description |
| :--- | :---: | :---: | :---: | :--- |
| `width` | Whole number | `21` | At least `5` | Number of horizontal tiles in the maze. |
| `height` | Whole number | `21` | At least `5` | Number of vertical tiles in the maze. |

> **Note**: For optimal gameplay and visual balance, odd numbers (e.g., 15, 19, 21) are recommended for both width and height.

---

### Example `config.json`

Here is a configuration file showing comments, custom scoring, and tailored levels:

```json
{
    # Save file for high scores
    "highscore_filename": "my_scores.json",

    # Gameplay settings
    "lives": 3,
    "level_max_time": 180,
    "seed": 42,

    # Speeds (in tiles per second)
    "player_speed": 6.5,
    "ghost_speed": 5.0,
    "ghost_scared_multiplier": 0.6,

    # Scoring
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,

    # Level progression (at least 10 levels will be loaded)
    "levels": [
        { "width": 15, "height": 15 },
        { "width": 17, "height": 17 },
        { "width": 19, "height": 19 },
        { "width": 21, "height": 21 }
    ]
}
```

## Highscore

## Maze Generation

In compliance with project specifications, mazes are generated using the mazegenerator package integrated **as-is without any internal modifications**. Our backend acts as an adapter layer through `LevelsGenerator` to convert the raw generated grid into a fully playable Pac-Man stage.

### Integration & Parameters

The generator is instantiated for each level with specific constraints tailored to Pac-Man gameplay:

```python
maze = MazeGenerator(
    size=(level.width, level.height),
    perfect=False,
    seed=config.seed if level_index == 0 else 0
)
```

* **Non-Perfect Mazes (`perfect=False`)**: Standard perfect mazes contain only a single path between any two points and numerous dead-ends, which would make escaping ghosts impossible.
* **Seed Management**:
  * **Level 1**: Generated using the fixed `seed` provided in `config.json`. This guarantees deterministic behavior and reproducible evaluation during defense.
  * **Subsequent Levels (2 to 10+)**: Generated with randomized seeds (`seed=0`), ensuring every subsequent level features a unique, procedurally generated layout.

### Grid Representation: Bitmask Walls

The assigned generator outputs the maze as a 2D integer array (`list[list[int]]`). Each tile stores its wall boundaries as a 4-bit bitmask:

| Bit | Value | Direction | Meaning |
| :---: | :---: | :---: | :--- |
| `0` | **1** | North (UP) | Wall blocks movement upwards |
| `1` | **2** | East (RIGHT) | Wall blocks movement to the right |
| `2` | **4** | South (DOWN) | Wall blocks movement downwards |
| `3` | **8** | West (LEFT) | Wall blocks movement to the left |

* **Corridor Tiles (`value < 15`)**: Tiles with at least one open wall where entities can navigate.
* **Solid Wall Tiles (`value == 15`)**: Completely enclosed cells ($1 + 2 + 4 + 8 = 15$) representing solid architectural obstacles, such as the outer perimeter and the central "42" logo.

### Adapter Pipeline (`LevelsGenerator`)

Once the raw maze is generated, our `LevelsGenerator` adapts the grid into our internal `Level` data model:

1. **Player Spawn (`find_player_spawn`)**:
   * Evaluates the geometric center of the maze (`width // 2`, `height // 2`).
   * Searches the center and its 8 immediate neighboring tiles in cardinal and diagonal order to guarantee the player spawns in an open corridor (`value != 15`), even if the exact center lands on a solid wall segment.
2. **Ghost Spawns & Super-Pacgums**:
   * Positioned strategically in the 4 extreme corners of the board:
     * Top-Left: `(0, 0)`
     * Top-Right: `(width - 1, 0)`
     * Bottom-Right: `(width - 1, height - 1)`
     * Bottom-Left: `(0, height - 1)`
3. **Pacgum Distribution (`create_pacgums`)**:
   * Iterates across all playable corridor cells (`value != 15`).
   * Generates regular pacgums probabilistically (90% spawn chance), leaving the player's starting cell empty so the player does not immediately consume a dot upon spawning.

### Error Handling & Robustness

* **Dimension Protection**: Maze dimensions are validated to meet the minimum size required by the generator.
* **Fallback Guarantee**: In the unlikely event that a seed produces an inaccessible central spawn, a custom `SpawnNotFoundException` is trapped gracefully, falling back to a safe default corridor position without crashing the application.

## Implementation

## General Software Architecture

## Project Management

We used the github project feature linked to our repository. It checks our opened issues and create an item for each one then it automatically set it to done when the issue is closed. [Link to our project](https://github.com/users/Cu-chi/projects/1)
![project management screenshot](./.github/assets/image.png)

Therefore, the ['issues' section](https://github.com/Cu-chi/pac-man/issues) of our github repository was central.  
We opened an issue for each feature or bug then we were attributed to specific and we worked on our side without conflicts.

## Resources
https://pydantic.dev/docs/validation/dev/concepts/validators/  
https://pydantic.dev/docs/validation/dev/concepts/json/  
https://stackoverflow.com/questions/77248283/using-with-open-why-does-rb-for-reading-json-work-but-wb-for-writing-to-a-j  

AI usage:
