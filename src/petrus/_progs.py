
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
        _run()
        return
    with contextlib.chdir(root):
        _run()
def _run():
    shutil.rmtree('dist', ignore_errors=True)
    try:
        subprocess.run([sys.executable, "-m", "build"], check=True)
        subprocess.run(["twine", "upload", "dist/*"], check=True)
    except:
        return



