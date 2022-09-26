import tupuedes

from sys import platform
import os
from pathlib import Path
import datetime

def get_documents_path():
    home_path = Path(os.path.expanduser('~'))
    if platform == "linux" or platform == "linux2":
        return home_path.joinpath('Documents')
    elif platform == "darwin":
        return home_path.joinpath('Documents')
    elif platform == "win32":
        return home_path.joinpath('Documents')

    return home_path


def get_recording_path():
    documents_path = get_documents_path()
    recordings_path = documents_path.joinpath('tupuedes', 'recordings')

    return recordings_path


def get_new_recording_path():
    base_path = get_recording_path()
    now = datetime.datetime.now()
    date_string = now.strftime('%Y.%m.%d %H.%M')

    return base_path.joinpath(date_string)


def get_module_data_path(internal_path):
    pip_path = os.path.dirname(tupuedes.__file__)
    pip_path = Path(pip_path).parents[0]

    return pip_path.joinpath(*internal_path)