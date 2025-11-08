import enum
import importlib.resources
import tomllib
from functools import cached_property
from typing import *


class Const(enum.Enum):
    const = None

    @cached_property
    def data(self: Self) -> dict[str, Any]:
        ans: dict[str, Any]
        text: str
        text = importlib.resources.read_text("petrus._core.consts", "consts.toml")
        ans = tomllib.loads(text)
        return ans
