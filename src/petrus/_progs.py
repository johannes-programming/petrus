
import importlib.metadata
import os
import shutil
import string
import subprocess
import sys
from argparse import ArgumentParser

import requests
import tomli_w
import tomllib


def main(args=None):
    parser = ArgumentParser()
    parser.add_argument('root', nargs='?')
    parser.add_argument('--version')
    ns = parser.parse_args(args=args)
    kwargs = vars(ns)
    run(**kwargs)

def run(root=None, *, version=None):
    run_root(root)
    run_isort()
    run_pyproject(version=version)
    run_commit(version=version)
    run_end()

def run_isort():
    try:
        subprocess.run(['isort', '.'], check=True)
    except subprocess.CalledProcessError:
        pass

def run_root(root):
    if root is None:
        return
    os.chdir(root)

def run_pyproject(version):
    if not os.path.isfile("pyproject.toml"):
        return
    with open("pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)
    if version is not None:
        pyproject['project']['version'] = version
    pyproject['project']['classifiers'].sort()
    fix_dependencies(pyproject['project']['dependencies'])
    with open("pyproject.toml", "wb") as f:
        tomli_w.dump(pyproject, f)

def run_commit(version):
    if version is None:
        message = "a"
    else:
        message = f"Version {version}"
    try:
        subprocess.run(['git', 'add', '-A'], check=True)
        subprocess.run(['git', 'commit', '--allow-empty', '-m', message], check=True)
    except subprocess.CalledProcessError:
        pass
    
def run_end():
    shutil.rmtree('dist', ignore_errors=True)
    try:
        subprocess.run([sys.executable, "-m", "build"], check=True)
        subprocess.run(["twine", "upload", "dist/*"], check=True)
    except:
        return

def fix_dependencies(dependencies):
    for i in range(len(dependencies)):
        dependencies[i] = fix_dependency(dependencies[i])
    dependencies.sort()

def fix_dependency(dependency):
    dependency = dependency.strip()
    chars = set(dependency)
    chars -= set(string.ascii_letters)
    chars -= set(string.digits)
    chars -= set("-_")
    if len(chars):
        return dependency
    version = get_some_version(dependency)
    if version is None:
        return dependency
    dependency += ">=" + version
    return dependency

def get_some_version(package):
    try:
        return importlib.metadata.version(package)
    except:
        pass
    try:
        return get_latest_version(package)
    except:
        pass
    return None

def get_latest_version(package):
    response = requests.get(f"https://pypi.org/pypi/{package}/json")
    data = response.json()
    return data["info"]["version"]
