import argparse
import contextlib
import dataclasses
import functools
import os
import tomllib
import typing
from importlib import resources

from petrus._core.calcs.Prog import Prog

__all__ = ["main", "run"]


def _desc():
    return "Update a python project. \
The default values of the arguments are taken \
from the default table of the config.toml file \
inside of the petrus package."


def _inputs():
    pairs = list(dict(Prog.INPUTS).items())
    # pairs = list(_input_format(x) for x in pairs)
    pairs.sort(key=_inputs_sortkey)
    ans = dict(pairs)
    return ans


def _inputs_sortkey(pair):
    if pair[0] == "path":
        raise KeyError
    if "-" in pair[0]:
        raise KeyError
    return pair[0]


def _run_deco(old, /):
    doc = _desc()
    doc += "\n"
    for k, v in _inputs().items():
        old.__annotations__[k] = typing.Optional[str]
        setattr(old, k, None)
        doc += f"\n{k}: {v}"
    old = dataclasses.dataclass(old)

    @functools.wraps(old)
    def new(*args, **kwargs):
        old(*args, **kwargs)

    new.__doc__ = doc
    return new


def main(args=None):
    parser = argparse.ArgumentParser(fromfile_prefix_chars="@", description=_desc())
    parser.add_argument("path", nargs="?")
    for k, v in _inputs().items():
        opt = "--" + k.replace("_", "-")
        parser.add_argument(opt, help=v)
    ns = parser.parse_args(args)
    kwargs = vars(ns)
    _prog(**kwargs)


@_run_deco
class run:
    path: typing.Optional[str] = None

    def __post_init__(self):
        kwargs = dataclasses.asdict(self)
        _prog(**kwargs)


def _prog(path, **kwargs):
    try:
        cfg = resources.read_text("petrus", "config.toml")
    except:
        cfg = ""
    cfg = tomllib.loads(cfg)
    default = cfg.get("default", {})
    for k in kwargs.keys():
        if kwargs[k] is None:
            kwargs[k] = str(default.get(k, ""))
    try:
        root = cfg["general"]["root"]
    except KeyError:
        root = None
    paths = [os.getcwd(), root, path]
    paths = filter(lambda x: x is not None, paths)
    paths = [_normpath(x) for x in paths]
    wd = os.path.join(*paths)
    if not os.path.isdir(wd):
        os.mkdir(wd)
    with contextlib.chdir(wd):
        Prog(kwargs)


def _normpath(path):
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.normpath(path)
    return path
