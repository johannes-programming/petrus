import inspect
import os
import string
import sys

import v440

from petrus._core import utils
from petrus._core.calcs.Calc import Calc

CLASSIFIERS = [
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
]


class Project(Calc):
    def __post_init__(self): ...

    def _calc_authors(self):
        ans = self.get("authors", default=[])
        if type(ans) is not list:
            return ans
        ans = list(ans)
        author = dict()
        a = dict()
        a["name"] = self.prog.kwargs["author"]
        a["email"] = self.prog.kwargs["email"]
        for k, v in a.items():
            if v:
                author[k] = v
        author = utils.easy_dict(author)
        used = False
        for i in range(len(ans)):
            try:
                ans[i] = dict(ans[i])
            except:
                continue
            fit = utils.dict_match(ans[i], author)
            if fit and not used:
                ans[i].update(author)
            ans[i] = utils.easy_dict(ans[i])
            used |= fit
        if not used:
            ans.insert(0, author)
        return ans

    def _calc_classifiers(self):
        ans = self.get("classifiers")
        if ans is not None:
            return ans
        ans = CLASSIFIERS
        if not utils.isfile(self.prog.file.license):
            ans += ["License :: OSI Approved :: MIT License"]
        ans = utils.easy_list(ans)
        return ans

    def _calc_dependencies(self):
        ans = self.get("dependencies", default=[])
        if type(ans) is not list:
            return ans
        ans = [utils.fix_dependency(x) for x in ans]
        ans = utils.easy_list(ans)
        return ans

    def _calc_description(self):
        if self.prog.kwargs["description"]:
            return self.prog.kwargs["description"]
        if self.get("description") is not None:
            return self.get("description")
        return self.name

    def _calc_keywords(self):
        return self.get("keywords", default=[])

    def _calc_license(self):
        ans = self.get("license")
        if ans is None:
            ans = dict()
        if type(ans) is not dict:
            return ans
        if "file" not in ans.keys():
            ans["file"] = self.prog.file.license
        return ans

    def _calc_name(self):
        basename = os.path.basename(os.getcwd())
        return self.get("name") or basename

    def _calc_readme(self):
        return self.prog.file.readme

    def _calc_requires_python(self):
        return (
            self.get("requires-python")
            or self.prog.kwargs["requires_python"]
            or ">={0}.{1}.{2}".format(*sys.version_info)
        )

    def _calc_urls(self):
        ans = self.get("urls")
        if ans is None:
            ans = dict()
        if type(ans) is not dict:
            return ans
        if self.prog.github:
            ans.setdefault("Source", self.prog.github)
        p = f"https://pypi.org/project/{self.name}/#files"
        ans.setdefault("Download", p)
        ans = utils.easy_dict(ans)
        return ans

    def _calc_version(self):
        a = self.prog.kwargs["v"]
        try:
            args = self.parse_bump(a)
        except ValueError:
            return a
        b = self.get("version", default="0.0.0")
        try:
            c = v440.Version(b)
            c.release.bump(*args)
        except v440.VersionError as e:
            print(e, file=sys.stderr)
            return b
        return str(c)

    def get(self, *args, default=None):
        return self.prog.pp.get("project", *args, default=default)

    @staticmethod
    def parse_bump(line):
        line = line.strip()
        if not line.startswith("bump"):
            raise ValueError
        line = line[4:].lstrip()
        if not line.startswith("("):
            raise ValueError
        line = line[1:].lstrip()
        if not line.endswith(")"):
            raise ValueError
        line = line[:-1].rstrip()
        if line.endswith(","):
            line = line[:-1].rstrip()
        chars = string.digits + string.whitespace + ",-"
        if line.strip(chars):
            raise ValueError
        line = line.split(",")
        line = [int(x.strip()) for x in line]
        return line

    def todict(self) -> None:
        ans = self.get(default={})
        prefix = "_calc_"
        for n, m in inspect.getmembers(self):
            if not n.startswith(prefix):
                continue
            k = n[len(prefix) :]
            v = getattr(self, k)
            k = k.replace("_", "-")
            ans[k] = v
        ans = utils.easy_dict(ans)
        return ans
