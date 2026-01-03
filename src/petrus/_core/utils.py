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
from functools import partial


def dict_match(a: Any, b: Any, /) -> bool:
    keys:list
    x:dict
    y:dict
    x = dict(a)
    y = dict(b)
    keys = list(set(x.keys()) & set(y.keys()))
    ans = all(a[k] == b[k] for k in keys)
    return ans


def fix_dependency(line: str, /) -> str:
    ans: str
    chars: set
    limit: int
    opener: str
    version: Any
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
    return f"{ans}>={version},<{limit}"

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
    content:Any
    stream:Any
    soup:bs4.BeautifulSoup
    formatter:bs4.formatter.HTMLFormatter
    beautified_html:str
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
    return subprocess.run([sys.executable, "-m"] + list(args))


def run_black(path: Any) -> Any:
    try:
        return black.main([path])
    except Exception:
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
    file: str
    files: list
    walk: Iterable
    root: str
    dnames: list[str]
    fnames: list[str]
    files = []
    walk = os.walk(os.getcwd())
    for root, dnames, fnames in walk:
        for fname in fnames:
            file = os.path.join(root, fname)
            files.append(file)
    for file in files:
        if os.path.splitext(file)[1] == ".py":
            isort.file(file)



def walk(path: Any, *, recursively: Any) -> Generator:
    ans: list
    func: partial
    root: Any
    dnames: list[str]
    fnames: list[str]
    if not os.path.exists(path):
        return
    if not recursively:
        func = partial(os.path.join, path)
        ans = os.listdir(path)
        ans = map(func, ans)
        ans = filter(os.path.isfile, ans)
        yield from ans
        return
    for root, dnames, fnames in os.walk(path):
        func = partial(os.path.join, root)
        yield from map(func, fnames)


def _get_some_version(pkg: Any, /) -> Any:
    return _get_local_version(pkg) or _get_latest_version(pkg)


def _get_local_version(pkg: Any, /) -> Optional[str]:
    ans: str
    url: str
    res: requests.Response
    try:
        ans = importlib.metadata.version(pkg)
    except Exception:
        return
    url = "https://pypi.org/pypi/%s/%s" % (pkg, ans)
    res = requests.get(url)
    if res.status_code != 404:
        return ans


def _get_latest_version(pkg: Any, /) -> Any:
    res: requests.Response
    url: str
    url = "https://pypi.org/pypi/%s/json" % pkg
    try:
        res = requests.get(url)
        return res.json()["info"]["version"]
    except Exception:
        return
