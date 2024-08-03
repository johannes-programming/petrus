
from argparse import ArgumentParser
import contextlib
import subprocess
import os
import shutil
import sys



def main(args=None):
    parser = ArgumentParser()
    parser.add_argument('root', nargs='?')
    ns = parser.parse_args(args=args)
    kwargs = vars(ns)
    run(**kwargs)

def run(root=None):
    if root is None:
        root = os.getcwd()
    with contextlib.chdir(root):
        shutil.rmtree('dist', ignore_errors=True)
        subprocess.run([sys.executable, "-m", "build"])
        subprocess.run(["twine", "upload", "dist/*"])



