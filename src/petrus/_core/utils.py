import importlib.metadata
import os
import string
import subprocess
import sys
from typing import *

import black
import bs4
import filelisting
import isort
import requests

TEXT_EXTS: tuple[str, ...]
TEXT_EXTS = (".cfg", ".css", ".html", ".in", ".js", ".rst", ".toml", ".txt", ".typed")


def dict_match(a: Any, b: Any, /) -> bool:
    a: dict
    b: dict
    keys: Any
    a = dict(a)
    b = dict(b)
    keys = set(a.keys()) & set(b.keys())
    return all(a[k] == b[k] for k in keys)


def fix_dependency(line: str, /) -> str:
    ans: str
    chars: set
    limit: int
    opener: str
    x: str
    ans = line.strip()
    chars = set(ans)
    chars -= set(string.ascii_letters)
    chars -= set(string.digits)
    chars -= set("-_")
    if len(chars):
        return ans
    version = _get_some_version(ans)
    if version is None:
        return ans
    opener = ""
    for x in version:
        if x in string.digits:
            opener += x
        else:
            break
    limit = int(opener) + 1
    ans = f"{ans}>={version},<{limit}"
    return ans


def isdir(path: Any) -> bool:
    if not os.path.exists(path):
        return False
    if not os.path.isdir(path):
        raise ValueError
    return True


def isfile(path: Any) -> bool:
    if not os.path.exists(path):
        return False
    if not os.path.isfile(path):
        raise ValueError
    return True


def prettify_html(file: str) -> None:
    beautified_html: Any
    content: Any
    formatter: Any
    soup: Any
    # Read the HTML file
    with open(file, "r", encoding="utf-8") as stream:
        content = stream.read()

    # Parse the HTML content
    soup = bs4.BeautifulSoup(content, "html.parser")

    # Beautify the HTML
    formatter = bs4.formatter.HTMLFormatter(indent=4)
    beautified_html = soup.prettify(formatter=formatter)

    # Save the beautified HTML to a new file
    with open(file, "w", encoding="utf-8") as stream:
        stream.write(beautified_html)


def py(*args: Any) -> subprocess.CompletedProcess[bytes]:
    args: list
    args = [sys.executable, "-m"] + list(args)
    return subprocess.run(args)


def run_black(path: Any) -> Any:
    try:
        return black.main([path])
    except BaseException:
        pass


def run_html_prettifier(path: Any) -> None:
    ext: Any
    file: str
    filename: Any
    for file in filelisting.file_generator(path):
        filename = os.path.basename(file)
        ext = os.path.splitext(filename)
        if ext != ".html":
            continue


def run_isort() -> None:
    file: Any
    files: list
    walk: Iterator
    files = []
    walk = os.walk(os.getcwd())
    for root, dnames, fnames in walk:
        for fname in fnames:
            file = os.path.join(root, fname)
            files.append(file)
    for file in files:
        if os.path.splitext(file)[1] == ".py":
            isort.file(file)


def run_strip() -> None:
    file: Any
    files: list
    index: int
    lines: list[str]
    walk: Iterator
    files = []
    walk = os.walk(os.getcwd())
    for root, dnames, fnames in walk:
        for fname in fnames:
            files.append(os.path.join(root, fname))
    if os.path.isfile(".gitignore"):
        files.append(".gitignore")
    index = 0
    while index < len(files):
        if os.path.splitext(files[index])[1] in TEXT_EXTS:
            index += 1
        else:
            files.pop(index)
    for file in files:
        lines = list()
        with open(file, "r") as stream:
            lines = stream.readlines()
        for index in range(len(lines)):
            lines[index] = lines[index].rstrip() + "\n"
        while lines and lines[-1] == "\n":
            lines.pop()
        with open(file, "w") as stream:
            stream.write("".join(lines))


def walk(path: Any, *, recursively: Any) -> Generator:
    ans: Any
    dnames: Any
    fname: Any
    fnames: Any
    n: Any
    root: Any
    x: Any
    if not os.path.exists(path):
        return (x for x in ())
    if not recursively:
        ans = os.listdir(path)
        ans = (os.path.join(path, n) for n in ans)
        ans = filter(os.path.isfile, ans)
        yield from ans
        return
    for root, dnames, fnames in os.walk(path):
        for fname in fnames:
            yield os.path.join(root, fname)


def _get_some_version(pkg: Any, /) -> Any:
    return _get_local_version(pkg) or _get_latest_version(pkg)


def _get_local_version(pkg: Any, /) -> Any:
    ans: Any
    response: Any
    url: str
    try:
        ans = importlib.metadata.version(pkg)
    except Exception:
        return
    url = "https://pypi.org/pypi/%s/%s" % (pkg, ans)
    response = requests.get(url)
    if response.status_code != 404:
        return ans


def _get_latest_version(pkg: Any, /) -> Any:
    r: Any
    url: str
    url = "https://pypi.org/pypi/%s/json" % pkg
    try:
        r = requests.get(url)
        return r.json()["info"]["version"]
    except Exception:
        return
