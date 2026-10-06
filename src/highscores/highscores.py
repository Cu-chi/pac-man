from pydantic import BaseModel, Field, model_validator
from pathlib import Path
from typing import Self


class Score(BaseModel):
    username: str = Field(max_length=10, min_length=3)
    score: int = Field(ge=0)

    @model_validator(mode="after")
    def check_username(self) -> Self:
        if not self.username.isalnum():
            raise ValueError("username is not alpha-numerical")
        return self


class Highscores(BaseModel):
    score: list[Score] = []

    def save_json(self, path: Path) -> None:
        Path(path).write_text(self.model_dump_json(indent=4), encoding="utf-8")

    @classmethod
    def load_json(cls, path: Path) -> "Highscores":
        """Charge les scores depuis un fichier JSON."""
        file_path = Path(path)
        if not file_path.exists():
            return cls()
        return cls.model_validate_json(file_path.read_text(encoding="utf-8"))
