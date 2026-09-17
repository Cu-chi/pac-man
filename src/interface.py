from pydantic import BaseModel, Field
from typing import Any
from dataclasses import dataclass


class Configuration(BaseModel):

    highscore_filename: str
    width: int
    height: int
    lives: int = Field(default=3)
    point_per_pacgum: int = Field(default=10)
    point_per_super: int = Field(default=50)
    point_per_ghost: int = Field(default=200)
    seed: Any = Field(default=-192)
    level_max_time: int = Field(default=90)


@dataclass(slots=True)
class Player():

    x: int
    y: int
    alive: bool = True
    