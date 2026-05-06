import os
import string
import sys
from functools import cached_property
from typing import *

from identityfunction import identityfunction

from petrus._core import utils
from petrus._core.calcs.CacheCalc import CacheCalc
from petrus._core.consts.Const import Const

__all__ = ["Project"]

EMPTY = object()

PREFIX_DEV = "Development Status :: "
PREFIX_LICENSE = "License :: "


def prefix_filter_func(classifier: str) -> bool:
    prefix: str
    for prefix in (PREFIX_DEV, PREFIX_LICENSE):
        if classifier.lower().startswith(prefix.lower()):
            return False
    return True


class Project(CacheCalc):

    authors: Any
    classifiers: Any
    dependencies: Any
    description: Any
    keywords: Any
    license: Any
    license_files: Any
    name: Any
    readme: Any
    requires_python: Optional[str]
    urls: Any
    version: Any

    def __post_init__(self: Self) -> None:
        self._version = EMPTY

    @cached_property
    def authors(self: Self) -> Any:
        ans: list
        author: dict
        fit: Any
        gotten: Any
        used: Any
        i: Any
        gotten = self.get("authors", default=[])
        if type(gotten) is not list:
            return gotten
        ans = gotten.copy()
        author = dict()
        if self.prog.kwargs["author"]:
            author["name"] = self.prog.kwargs["author"]
        if self.prog.kwargs["email"]:
            author["email"] = self.prog.kwargs["email"]
        author = self.prog.easy_dict(author)
        used = False
        for i in range(len(ans)):
            try:
                ans[i] = dict(ans[i])
            except Exception:
                continue
            fit = utils.dict_match(ans[i], author)
            if fit and not used:
                ans[i].update(author)
            ans[i] = self.prog.easy_dict(ans[i])
            used |= fit
        if not used:
            ans.insert(0, author)
        return ans

    @cached_property
    def classifiers(self: Self) -> Any:
        kwarg: str
        parts: list[str]
        preset_gotten: Any
        preset_gotten = self.get("classifiers", default=[])
        if type(preset_gotten) is not list:
            return preset_gotten
        kwarg = self.prog.kwargs["classifiers"]
        if kwarg == "":
            return list(sorted(set(preset_gotten)))
        kwarg = kwarg.format(preset=", ".join(preset_gotten))
        parts = kwarg.split(",")
        parts = self.format_classifiers(parts)
        if self.prog.development_status == "":
            return list(sorted(set(parts)))
        parts = list(filter(prefix_filter_func, parts))
        parts.append(PREFIX_DEV + self.prog.development_status)
        return list(sorted(set(self.format_classifiers(parts))))

    @cached_property
    def dependencies(self: Self) -> Any:
        x: Any
        x = self.get("dependencies", default=[])
        if type(x) is not list:
            return x
        return list(sorted(set(map(utils.fix_dependency, x))))

    @cached_property
    def description(self: Self) -> Any:
        if self.prog.kwargs["description"]:
            return self.prog.kwargs["description"]
        if self.get("description") is not None:
            return self.get("description")
        return self.name

    @cached_property
    def keywords(self: Self) -> Any:
        return self.get("keywords", default=[])

    @cached_property
    def license(self: Self) -> Any:
        files: Any
        info: Any
        files = self.prog.pp.get("project", "license-files")
        info = self.prog.pp.get("project", "license")
        if files is not None:
            return info
        if info is None:
            return "MIT"
        if type(info) is not dict:
            return info
        if tuple(info.keys()) != ("file",):
            return info
        return "MIT"

    @cached_property
    def license_files(self: Self) -> Any:
        files: Any
        info: Any
        files = self.prog.pp.get("project", "license-files")
        info = self.prog.pp.get("project", "license")
        if files is not None:
            return files
        if info is None:
            return [self.prog.file.license]
        if type(info) is not dict:
            return
        if tuple(info.keys()) != ("file",):
            return
        return [self.prog.file.license]

    @classmethod
    def format_classifiers(
        cls: type[Self],
        value: Iterable[str],
        /,
    ) -> list[str]:
        ans: list[str]
        x: int
        ans = list(value)
        for x in range(len(ans)):
            ans[x] = ans[x].replace("::", " :: ")
            ans[x] = " ".join(ans[x].split())
            ans[x] = ans[x].strip()
        ans = list(filter(None, ans))
        return ans

    def get(self: Self, *args: Any, default: Any = None) -> Any:
        return self.prog.pp.get("project", *args, default=default)

    @cached_property
    def name(self: Self) -> str:
        ans: str
        basename: Any
        raw: str
        x: str
        basename = os.path.basename(os.getcwd())
        raw = str(self.get("name") or basename)
        ans = ""
        for x in raw:
            if x in (string.ascii_letters + string.digits):
                ans += x
            else:
                ans += "_"
        return ans

    @property
    def readme(self: Self) -> Any:
        return self.prog.file.readme

    @cached_property
    def requires_python(self: Self) -> Optional[str]:
        current: str
        kwarg: str
        parts: list[str]
        preset: Any
        current = ">={0}.{1}.{2}".format(*sys.version_info)
        kwarg = self.prog.kwargs["requires_python"]
        preset = self.get("requires-python", default="")
        if kwarg == "":
            return preset
        kwarg = kwarg.format(preset=preset, current=current)
        parts = kwarg.split("\\|")
        parts = list(map(str.strip, parts))
        return next(filter(None, parts), None)

    def todict(self: Self) -> Any:
        ans: Any
        x: Any
        y: Any
        ans = self.get(default={})
        for x in Const.const.data["CONST"]["PROJECT-KEYS"]:
            y = getattr(self, x)
            if y is None:
                continue
            x = x.replace("_", "-")
            ans[x] = y
        ans = self.prog.easy_dict(ans)
        return ans

    @cached_property
    def urls(self: Self) -> Any:
        ans: Any
        p: str
        ans = self.get("urls")
        if ans is None:
            ans = dict()
        if type(ans) is not dict:
            return ans
        if self.prog.github:
            ans.setdefault("Source", self.prog.github)
        p = f"https://pypi.org/project/{self.name}/"
        ans.setdefault("Index", p)
        p = f"https://pypi.org/project/{self.name}/#files"
        ans.setdefault("Download", p)
        ans = self.prog.easy_dict(ans)
        return ans

    @property
    def version(self: Self) -> Any:
        if self._version is EMPTY:
            self._version = self.prog.version_formatted
        return self._version
