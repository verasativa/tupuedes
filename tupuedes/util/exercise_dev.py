from tupuedes.util.file_system import get_recording_path
import os.path
from pathlib import Path


def list_recordings(path = None):
    if path is None:
        path = get_recording_path()
    for file in path.iterdir():
        if file.suffix == '.csv':
            possible_video_paths = [
                os.path.splitext(file)[0] + ".avi",
                os.path.splitext(file)[0] + "_raw.avi",

            ]
            for possible_video_path in possible_video_paths:
                if os.path.isfile(possible_video_path):
                    yield file, Path(possible_video_path)
                    break

