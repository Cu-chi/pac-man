"""Highscore models, saved to and loaded from a JSON file."""

from pydantic import BaseModel, Field, model_validator
from pathlib import Path
from typing import Self
import json


class Score(BaseModel):
    """A single highscore entry."""

    username: str = Field(max_length=10, min_length=3)
    score: int = Field(ge=0)

    @model_validator(mode="after")
    def check_username(self) -> Self:
        """Ensure the username only has alphanumeric characters and spaces.

        Raises:
            ValueError: If the username contains other characters.

        Returns:
            Self: The validated score.
        """
        if not self.username.replace(" ", "").isalnum():
            raise ValueError("username must be alphanumeric or spaces")
        return self


class Highscores(BaseModel):
    """List of every saved highscore."""

    score: list[Score] = []

    def save_json(self, path: Path) -> None:
        """Save the highscores to a JSON file.

        Args:
            path (Path): Destination file.
        """
        Path(path).write_text(self.model_dump_json(indent=4), encoding="utf-8")

    @classmethod
    def load_json(cls, path: Path) -> "Highscores":
        """Load the highscores from a JSON file.

        Args:
            path (Path): Source file.

        Returns:
            Highscores: Loaded highscores, empty if the file is missing.
        """
        file_path = Path(path)
        if not file_path.exists():
            return cls()

        highscores = json.loads(file_path.read_text(encoding="utf-8"))
        validated_scores = []
        if isinstance(highscores, dict):
            scores = highscores.get("score", [])
            if not isinstance(scores, list):
                raise ValueError(f"'{file_path}': 'score' must be a list")
            for score in scores:
                try:
                    validated_scores.append(Score.model_validate(score))
                except Exception:
                    pass
        return Highscores(score=validated_scores)
