from tqdm import tqdm

from tupuedes.pipeline.capture_video import CaptureVideo
from tupuedes.pipeline.display_video import DisplayVideo
from tupuedes.pipeline.anotate_video import AnnotateVideo
from tupuedes.pipeline.pose_regresor import PoseRegresor
from tupuedes.pipeline.analyse_pose import AnalysePose
from tupuedes.pipeline.save_video import SaveVideo
from tupuedes.pipeline.fps_calculator import FPSCalculator
from tupuedes.pipeline.aruco_finder import ArucoFinder
from tupuedes.util.metrics import Metrics
from tupuedes.util.file_system import get_new_recording_path
from tupuedes.pipeline.save_image import SaveImage
import click

# TODO: mirror for screen
# DONE: add video writter
# DONE: get write path from custom fancy class
metrics = Metrics()
def train_loop(source):
    # boiler plate
    date_time_base_path = get_new_recording_path()
    print(date_time_base_path)
    aruco_map = {
        0: 'bar',
        1: 'abs_wheel',
        4: 'test_item',
    }


    # pipeline items
    capture_video = CaptureVideo(source)
    #click.echo("Capture created", err=True)
    infer_pose = PoseRegresor(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    infer_aruco = ArucoFinder(source="image", aruco_map=aruco_map)
    analyse_coordinates = AnalysePose(['sentadillas'], store=True, store_path=f"{date_time_base_path}.csv")
    fps_calculator = FPSCalculator()
    annotate_video = AnnotateVideo("image", annotate_pose=True, annotate_fps=True, annotate_aruco=True)
    display_video = DisplayVideo("image", "Tú puedes!", )
    save_video = SaveVideo("image", f"{date_time_base_path}.avi")

    # Create image processing pipeline
    pipeline = (capture_video | infer_pose | infer_aruco | fps_calculator | analyse_coordinates | annotate_video | display_video | save_video)
    # Iterate through pipeline
    try:
        metrics.log_event('exercise start')
        for _ in tqdm(pipeline,
                      total=capture_video.frame_count if capture_video.frame_count > 0 else None,
                      disable=True):
            pass
    except StopIteration:
        return
    except KeyboardInterrupt:
        return
    finally:
        # Pipeline cleanup
        display_video.close()
        analyse_coordinates.close()
        save_video.close()
        metrics.log_event('exercise end')


def video_to_csv(source, destination, get_frames = False):
    # pipeline items
    capture_video = CaptureVideo(source)
    infer_pose = PoseRegresor(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    analyse_coordinates = AnalysePose(['sentadillas'], store=True, store_path=f"{destination}.csv", datetime=False, frame_id=True)
    fps_calculator = FPSCalculator()
    annotate_video = AnnotateVideo("image", annotate_pose=True, annotate_fps=True)
    display_video = DisplayVideo("image", "Processing", )
    if get_frames:
        save_images = SaveImage("image", path=destination)
        pipeline = (capture_video | infer_pose | analyse_coordinates | fps_calculator | annotate_video | save_images | display_video)
    else:
        # Create image processing pipeline
        pipeline = (capture_video | infer_pose | analyse_coordinates | fps_calculator | annotate_video | display_video)
    # Iterate through pipeline
    try:
        for _ in tqdm(pipeline,
                      total=capture_video.frame_count if capture_video.frame_count > 0 else None,
                      disable=True):
            pass
    except StopIteration:
        return
    except KeyboardInterrupt:
        return
    finally:
        # Pipeline cleanup
        analyse_coordinates.close()
        metrics.log_event('csv extraction')