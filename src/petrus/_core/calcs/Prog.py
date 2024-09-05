import datetime
import os

from petrus._core import utils
from petrus._core.calcs.Block import Block
from petrus._core.calcs.Calc import Calc
from petrus._core.calcs.Draft import Draft
from petrus._core.calcs.File import File
from petrus._core.calcs.Git import Git
from petrus._core.calcs.Project import Project
from petrus._core.calcs.Text import Text
from petrus._core.TOML import TOML


class Prog(Calc):
    _CORE = "kwargs"
    INPUTS = {
        "description": None,
        "author": None,
        "email": None,
        "requires_python": None,
        "github": None,
        "project_version": None,
        "year": None,
    }

    def __post_init__(self):
        self.git.init()
        if self.git.is_repo():
            self.save("gitignore")
        self.pp["project"] = self.project.to_dict()
        self.pp["build-system"] = self.build_system
        self.pp[()] = utils.easy_dict(self.pp[()])
        self.text.pp = str(self.pp)
        self.save("license")
        self.save("manifest")
        self.save("pp")
        self.save("readme")
        self.save("setup")
        self.packages
        utils.run_isort()
        utils.run_black(os.getcwd())
        self.git.commit_version()
        self.git.push()
        utils.pypi()

    def _calc_author(self):
        f = lambda z: str(z).strip()
        n = f(self.kwargs["author"])
        e = f(self.kwargs["email"])
        x = n, e
        authors = self.project.authors
        if type(authors) is not list:
            return x
        for a in authors:
            if type(a) is not dict:
                continue
            n = f(a.get("name", ""))
            e = f(a.get("email", ""))
            y = n, e
            if y != ("", ""):
                return y
        return x

    def _calc_block(self):
        return Block(self)

    def _calc_build_system(self):
        ans = self.pp["build-system"]
        if type(ans) is dict:
            ans = utils.easy_dict(ans)
        if ans is not None:
            return ans
        ans = dict()
        ans["requires"] = ["setuptools>=61.0.0"]
        ans["build-backend"] = "setuptools.build_meta"
        ans = utils.easy_dict(ans)
        return ans

    def _calc_draft(self):
        return Draft(self)

    def _calc_file(self):
        return File(self)

    def _calc_git(self):
        return Git(self)

    def _calc_github(self):
        u = self.kwargs["github"]
        if u == "":
            return ""
        return f"https://github.com/{u}/{self.project.name}"

    def _calc_packages(self):
        utils.mkdir("src")
        ans = []
        for x in os.listdir("src"):
            if self._is_pkg(x):
                ans.append(x)
        if len(ans):
            return ans
        for x in os.listdir():
            if self._is_pkg(x):
                ans.append(x)
        if not self.file.exists("pp"):
            ans.append(self.project.name)
            self.save("init")
            self.save("main")
        return ans

    def _calc_pp(self):
        return TOML(text=self.text.pp)

    def _calc_project(self):
        return Project(self)

    def _calc_text(self):
        return Text(self)

    def _calc_year(self):
        return self.kwargs["year"] or str(datetime.datetime.now().year)

    @staticmethod
    def _is_pkg(path):
        if not os.path.isdir(path):
            return False
        f = os.path.join(path, "__init__.py")
        return utils.isfile(f)

    def save(self, n, /):
        file = getattr(self.file, n)
        text = getattr(self.text, n)
        root = os.path.dirname(file)
        if root and not os.path.exists(root):
            os.mkdir(root)
        with open(file, "w") as s:
            s.write(text)
