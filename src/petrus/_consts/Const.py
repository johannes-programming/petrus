import enum
import tomllib
from functools import cached_property
from importlib import resources
from typing import *

__all__ = ["Const"]


class Const(enum.Enum):
    const = None

    @cached_property
    def data(self: Self) -> dict:
        "This cached property holds the cfg data."
        text: str
        text = resources.read_text("petrus._consts", "consts.toml")
        return tomllib.loads(text)
