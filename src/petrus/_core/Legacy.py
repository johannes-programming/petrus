class Legacy(Calc):
    def get_name(self, key, /):
        func = self.__getattribute__("name_" + key)
        ans = func()
        if type(ans) in [tuple, list]:
            ans = os.path.join(*ans)
        return ans

    def make_dir(self):
        root = os.path.expanduser(self.root)
        project_dir = os.path.join(root, self.project)
        self.project_dir = os.path.abspath(project_dir)
        if os.path.exists(self.project_dir):
            raise FileExistsError
        if self.github_user is None:
            os.mkdir(self.project_dir)
            return
        args = [
            "git",
            "init",
            self.project_dir,
        ]
        subprocess.run(args=args, check=True)

    def __getattr__(self, key):

        key = key[1:]
        if key.endswith("_textfile"):
            text = getattr(self, key[:-9] + "_text")
            if text is None:
                ans = None
            else:
                ans = self.get_name(key)
                fileunity.TextUnit.by_str(text).save(ans)
        elif key.endswith("_dir"):
            ans = self.get_name(key)
            os.mkdir(ans)
        else:
            ans = self.calc(key)
        setattr(self, "_" + key, ans)
        return ans

    def __init__(self, args):
        ns = self.parser.parse_args(args=args)
        kwargs = vars(ns)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def run(self):
        self.make_dir()
        with contextlib.chdir(self.project_dir):
            self.git_commit("Initial Commit", allow_empty=True)
            self.pyproject_textfile
            self.setup_textfile
            self.gitignore_textfile
            self.manifest_textfile
            self.init_textfile
            self.main_textfile
            self.git_commit("Version 0.0.0")

    def name_src_dir(self):
        return "src"

    def name_pkg_dir(self):
        return self.src_dir, self.project

    def name_init_textfile(self):
        return self.pkg_dir, "__init__.py"

    def name_main_textfile(self):
        return self.pkg_dir, "__main__.py"

    def name_pyproject_textfile(self):
        return "pyproject.toml"

    def name_license_textfile(self):
        return "LICENSE.txt"

    def name_readme_textfile(self):
        return "README.rst"

    def name_manifest_textfile(self):
        return "MANIFEST.in"

    def name_setup_textfile(self):
        return "setup.cfg"

    def name_gitignore_textfile(self):
        return ".gitignore"

    def _calc_init_text(self):
        ans = resources.read_text("hieronymus.drafts", "init.txt")
        return ans

    def _calc_main_text(self):
        ans = resources.read_text("hieronymus.drafts", "main.txt")
        ans = ans.format(project=self.project)
        return ans

    def _calc_gitignore_text(self):
        if self.github_user is None:
            return None
        ans = resources.read_text("hieronymus.drafts", "gitignore.txt")
        return ans

    def _calc_config_data(self):
        try:
            text = resources.read_text("hieronymus", "config.toml")
        except:
            text = ""
        ans = fileunity.TOMLUnit.data_by_str(text)
        return ans

    def _calc_config_github_user(self):
        ans = self.config_data.get("github_user")
        if (ans is None) or (type(ans) is str):
            return ans
        raise TypeError

    def _calc_readme_text(self):
        blocknames = "heading overview installation license links credits".split()
        blocks = [getattr(self, x + "_rst_block") for x in blocknames]
        blocks = [x for x in blocks if x is not None]
        blocks = ["\n".join(x) for x in blocks if type(x) is not str]
        ans = "\n\n".join(blocks)
        return ans

    def _calc_setup_text(self):
        return "\n"

    def _calc_pyproject_text(self):
        return fileunity.TOMLUnit.str_by_data(self.pyproject_data)

    def _calc_pyproject_data(self):
        ans = dict()
        ans["build-system"] = self.build_system_data
        ans["project"] = self.project_data
        return ans

    def _calc_build_system_data(self):
        return {
            "requires": ["setuptools>=61.0.0"],
            "build-backend": "setuptools.build_meta",
        }

    def _calc_final_description(self):
        if self.description is None:
            return self.project
        else:
            return self.description

    def _calc_project_data(self):
        ans = dict()
        ans["name"] = self.project
        ans["version"] = "0.0.0"
        ans["description"] = self.final_description
        if self.license_textfile is not None:
            ans["license"] = {"file": self.license_textfile}
        ans["readme"] = self.readme_textfile
        if self.authors is not None:
            ans["authors"] = self.authors
        ans["classifiers"] = self.classifiers
        ans["keywords"] = []
        ans["dependencies"] = []
        ans["requires-python"] = self.requires_python
        ans["urls"] = self.urls
        return ans

    def _calc_urls(self):
        ans = dict()
        ans["Download"] = (
            f"https://pypi.org/project/{self.project.replace('_', '-')}/#files"
        )
        if self.github_user is not None:
            ans["Source"] = f"https://github.com/{self.github_user}/{self.project}"
        return ans

    def _calc_classifiers(self):
        ans = list()
        if self.license_textfile is not None:
            ans.append("License :: OSI Approved :: MIT License")
        ans.append("Programming Language :: Python")
        ans.append("Programming Language :: Python :: 3")
        return ans

    def _calc_authors(self):
        if self.final_author is None:
            return None
        if self.email is None:
            return [dict(name=self.final_author)]
        else:
            return [dict(name=self.final_author, email=self.email)]

    @staticmethod
    def default_requires_python():
        assert sys.version_info[0] == 3
        return f">=3.{sys.version_info[1]}"

    @staticmethod
    def nameType(value, /):
        value = Prog.stripType(value)
        normpath = os.path.normpath(value)
        assert value == normpath
        x, y = os.path.split(value)
        assert x == ""
        return value

    @staticmethod
    def stripType(value, /):
        value = str(value)
        value = value.strip()
        return value
