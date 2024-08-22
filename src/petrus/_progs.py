
from argparse import ArgumentParser
import subprocess
import os
import shutil
import sys

import tomllib
import tomli_w

def main(args=None):
    parser = ArgumentParser()
    parser.add_argument('root', nargs='?')
    parser.add_argument('--version')
    ns = parser.parse_args(args=args)
    kwargs = vars(ns)
    run(**kwargs)

def run(root=None, *, version=None):
    run_root(root)
    run_version_pyproject(version=version)
    run_commit(version=version)
    run_end()

def run_root(root):
    if root is None:
        return
    os.chdir(root)

def run_version_pyproject(version):
    if version is None:
        return
    if not os.path.isfile("pyproject.toml"):
        return
    with open("pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)
    pyproject['project']['version'] = version
    with open("pyproject.toml", "wb") as f:
        tomli_w.dump(pyproject, f)

def run_commit(version):
    if version is None:
        return
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



