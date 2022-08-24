import datetime
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

# TODO: mirror for screen
# DONE: add video writter
# TODO: get write path from custom fancy class
metrics = Metrics()
def loop(source):
    # TODO: move to somewere cleaner
    # boiler plate
    now = datetime.datetime.now()
    format_string = 'data/recorded/%Y.%m.%d %H.%M'
    date_time_base_path = now.strftime(format_string)

    aruco_map = {
        0: 'bar',
        1: 'abs_wheel',
        4: 'test_item',
    }


    # pipeline items
    capture_video = CaptureVideo(source)
    infer_pose = PoseRegresor(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    infer_aruco = ArucoFinder(source="image", aruco_map=aruco_map)
    analyse_coordinates = AnalysePose(['sentadillas'], store=True)
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
        