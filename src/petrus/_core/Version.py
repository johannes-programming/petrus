import dataclasses
import typing

import packaging.version

from petrus._core import utils


@dataclasses.dataclass(frozen=True)
class Version:
    epoch: typing.Any
    release: typing.Any
    pre: typing.Any
    post: typing.Any
    dev: typing.Any
    local: typing.Any

    def __add__(self, other):
        if type(other) is not type(self):
            other = type(self).parse(other)
        d = dict()
        for n in "epoch release pre post dev local".split():
            a = getattr(self, n)
            b = getattr(other, n)
            d[n] = self._add(a, b, name=n)
        ans = type(self)(**d)
        return ans

    def __radd__(self, other):
        if type(other) is not type(self):
            other = type(self).parse(other)
        return other + self

    def __str__(self) -> str:
        ans = ""
        if self.epoch != 0:
            ans += f"{self.epoch}!"
        ans += ".".join(str(x) for x in self.release)
        if self.pre is not None:
            ans += "".join(str(x) for x in self.pre)
        if self.post is not None:
            ans += f".post{self.post}"
        if self.dev is not None:
            ans += f".dev{self.dev}"
        if self.local is not None:
            ans += f"+{self.local}"
        return ans

    @staticmethod
    def _add(a, b, *, name):
        if name != "release":
            if {a, b} == {None}:
                return None
            if a is None:
                return b
            if b is None:
                return a
            return a + b
        a = dict(enumerate(a))
        b = dict(enumerate(b))
        l = [0] * max(len(a), len(b))
        for i in range(l):
            l[i] += a.get(i, 0)
            l[i] += b.get(i, 0)
        ans = tuple(l)
        return ans

    def _apply_plus(self, length):
        release = list(self.release)
        release += [0] * 3
        index = 3 - length
        release[index] += 1
        release = release[: index + 1]
        release += [0] * 3
        release = release[:3]
        release = tuple(release)
        ans = dataclasses.replace(self, release=release)
        return ans

    def apply(self, arg, /):
        arg = str(arg)
        if arg == "":
            return dataclasses.replace(self)
        if arg in "+ ++ +++".split():
            return self._apply_plus(len(arg))
        return type(self).parse(arg)

    @classmethod
    def parse(cls, text):
        data = packaging.version.parse(text)
        keys = "epoch release pre post dev local".split()
        kwargs = dict()
        for k in keys:
            kwargs[k] = getattr(data, k)
        ans = cls(**kwargs)
        return ans
