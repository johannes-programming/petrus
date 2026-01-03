
import contextlib
import dataclasses
import functools
import os
import tomllib
import types
import typing
from importlib import resources
from typing import *
from functools import partial
from operator import is_not
from itertools import starmap

from petrus._core.calcs.Prog import Prog
from petrus._core.consts.Const import Const

__all__ = [
    "cfgfile",
    "desc",
    "input_format",
    "inputs",
    "inputs_sortkey",
    "link",
    "normpath",
    "prog",
    "run_deco",
]


def cfgfile() -> Any:
    return resources.files("petrus").joinpath("config.toml")


def desc() -> str:
    return Const.const.data["CONST"]["DESC"] % (str(cfgfile()), link())


def input_format(x: Any, y: Any, /) -> tuple:
    return x.strip(), y.strip()


def inputs() -> dict[str, str]:
    pairs: Iterable
    pairs = Const.const.data["INPUTS"].items()
    pairs = starmap(input_format, pairs)
    pairs = sorted(pairs, key=inputs_sortkey)
    return dict(pairs)

def inputs_sortkey(pair: tuple) -> Any:
    if pair[0] in {"help", "path", "version"}:
        raise KeyError
    if "-" in pair[0]:
        raise KeyError
    return pair[0]


def link() -> str:
    return Const.const.data["CONST"]["LINK"]


def normpath(path: Any) -> Any:
    ans: Any
    ans = path
    ans = os.path.expanduser(ans)
    ans = os.path.expandvars(ans)
    ans = os.path.normpath(ans)
    return ans


def prog(path: Any, **kwargs: Any) -> None:
    cfg_text: str
    cfg: dict[str, Any]
    default: Any
    key: Any
    kwargs_: dict[str, Any]
    paths: Iterable
    root: Any
    wd: Any
    try:
        cfg_text = cfgfile().read_text()
    except Exception:
        cfg_text = ""
    cfg = tomllib.loads(cfg_text)
    default = cfg.get("default", {})
    kwargs_ = dict(kwargs)
    for key in kwargs_.keys():
        if kwargs_[key] is None:
            kwargs_[key] = str(default.get(key, ""))
    try:
        root = cfg["general"]["root"]
    except KeyError:
        root = None
    paths = os.getcwd(), root, path
    paths = filter(partial(is_not, None), paths)
    paths = map(normpath, paths)
    wd = os.path.join(*paths)
    if not os.path.isdir(wd):
        os.mkdir(wd)
    with contextlib.chdir(wd):
        Prog(kwargs)

def run_deco(old: Any, /) -> types.FunctionType:
    cls:type
    doc: str
    x: Any
    y: Any
    field: Any
    doc = desc()
    doc += "\n"
    for x, y in inputs().items():
        old.__annotations__[x] = typing.Optional[str]
        field = dataclasses.field(
            default=None,
            kw_only=True,
        )
        setattr(old, x, field)
        doc += f"\n{x}: {y}"
    cls = dataclasses.dataclass(old, frozen=True)

    @functools.wraps(cls)
    def new(*args: Any, **kwargs: Any) -> None:
        cls(*args, **kwargs)

    new.__doc__ = doc
    return new
