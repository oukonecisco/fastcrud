import os
import pathlib


def core() -> pathlib.Path:
    return pathlib.Path(os.path.dirname(os.path.realpath(__file__)))


def root() -> pathlib.Path:
    return core().parent
