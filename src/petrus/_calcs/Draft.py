import importlib.resources
from typing import *

from petrus._calcs.CacheCalc import CacheCalc
from petrus._consts.Const import Const

__all__ = ["Draft"]


class Draft(CacheCalc):

    def __getattr__(self: Self, name: str) -> Any:
        return self.getitem(name)

    def __post_init__(self: Self) -> None:
        self._data = dict()

    def getitem(self: Self, key: str, /) -> str:
        if key not in self._data.keys():
            self._data[key] = importlib.resources.read_text(
                **Const.const.data["DRAFTS"][key]
            )
        return self._data[key]
