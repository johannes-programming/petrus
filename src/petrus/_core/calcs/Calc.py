from typing import *

class Calc:
    _CORE = "prog"

    def __delattr__(self:Self, name:Any)->None:
        self.__check(name)
        object.__delattr__(self, name)

    def __getattr__(self:Self, name:Any)->Any:
        ans:Any
        name_:str
        name_ = str(name)
        if name_.startswith("_"):
            raise AttributeError(name_)
        if not hasattr(self, "_lock"):
            self._lock = set()
        if name_ in self._lock:
            raise Exception
        self._lock.add(name_)
        try:
            ans = self._calc(name_)
            object.__setattr__(self, name_, ans)
        finally:
            self._lock.remove(name_)
        return ans

    def __init__(self:Self, core:Any, /) -> None:
        object.__setattr__(self, type(self)._CORE, core)
        getattr(self, "__post_init__", int)()

    def __setattr__(self:Self, name:Any, value:Any) -> None:
        self.__check(name)
        object.__setattr__(self, name, value)

    def __check(self:Self, name:Any) -> Any:
        if name.startswith("_"):
            return
        if not hasattr(super(), name):
            return
        raise AttributeError("readonly")

    def _calc(self:Self, name:Any) -> Any:
        return getattr(self, f"_calc_{name}")()
