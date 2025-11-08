from __future__ import annotations

from functools import cached_property
from typing import *

from petrus._core.calcs.BaseCalc import BaseCalc

_BLOCKKEYS: list[str] = "heading overview installation license links credits".split()


class Block(BaseCalc):

    prog: Any
    credits: str
    heading: str
    installation: Any
    license: str
    links: str
    overview: str
    text: str

    @cached_property
    def credits(self: Self) -> str:
        n: Any
        e: Any
        lines: str
        pn: Any
        n, e = self.prog.author
        lines = self.ftitle("Credits")
        if n:
            lines += "* Author: %s\n" % n
        if e:
            lines += "* Email: `%s <mailto:%s>`_\n" % (e, e)
        while not lines.endswith("\n\n"):
            lines += "\n"
        pn = self.prog.project.name
        lines += "Thank you for using ``%s``!" % pn
        return lines

    @staticmethod
    def ftitle(value: Any, /, lining: Any = "-") -> str:
        v: str
        l: str
        v = str(value)
        l = str(lining) * len(v)
        return "%s\n%s\n\n" % (v, l)

    @cached_property
    def heading(self: Self) -> str:
        n: Any
        l: str
        n = self.prog.project.name
        l = "=" * len(n)
        return "%s\n%s\n%s" % (l, n, l)

    @cached_property
    def installation(self: Self) -> Any:
        name: Any
        name = self.prog.project.name
        return self.prog.draft.installation.format(name=name)

    @cached_property
    def license(self: Self) -> str:
        mit: str
        classifiers: Any
        lines: str
        mit = "License :: OSI Approved :: MIT License"
        classifiers = self.prog.project.classifiers
        if type(classifiers) is not list:
            return None
        if mit not in classifiers:
            return None
        lines = self.ftitle("License")
        lines += "This project is licensed under the MIT License."
        return lines

    @cached_property
    def links(self: Self) -> str:
        i: Any
        urls: Any
        lines: str
        urls = self.prog.project.urls
        if type(urls) is not dict:
            return None
        if len(urls) == 0:
            return None
        lines = self.ftitle("Links")
        for i in urls.items():
            lines += "* `%s <%s>`_\n" % i
        return lines

    @cached_property
    def overview(self: Self) -> str:
        d: str
        lines: str
        d = str(self.prog.project.description)
        if not d:
            return None
        lines = self.ftitle("Overview")
        lines += str(d)
        return lines

    @cached_property
    def text(self: Self) -> str:
        ans: str
        blocks: list
        x: str
        y: Any
        blocks = []
        for x in _BLOCKKEYS:
            y = getattr(self, x)
            if y is None:
                continue
            y = y.strip("\n")
            blocks.append(y)
        ans = "\n\n".join(blocks)
        while "\n\n\n" in ans:
            ans = ans.replace("\n\n\n", "\n\n")
        return ans
