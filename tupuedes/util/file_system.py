from sys import platform
import os
from pathlib import Path


def get_documents_path():
    home_path = Path(os.path.expanduser('~'))
    if platform == "linux" or platform == "linux2":
        return home_path.joinpath('Documents')
    elif platform == "darwin":
        return home_path.joinpath('Documents')
    elif platform == "win32":
        pass

    return home_path