from tqdm import tqdm

from tupuedes.pipeline.capture_video import CaptureVideo
from tupuedes.pipeline.display_video import DisplayVideo
from tupuedes.pipeline.anotate_video import AnnotateVideo
from tupuedes.pipeline.pose_regresor import PoseRegresor
from tupuedes.pipeline.analyse_pose import AnalysePose

# TODO: mirror for screen
# TODO: add video writter
# 
def loop(source):
    # pipeline items
    capture_video = CaptureVideo(source)
    predict = PoseRegresor(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    analyse_pose = AnalysePose(['sentadillas'], store=True)
    annotate_video = AnnotateVideo("image", annotate_pose=True, annotate_fps=True)
    display_video = DisplayVideo("image", "Tú puedes!", )

    # Create image processing pipeline
    pipeline = (capture_video | predict| analyse_pose | annotate_video | display_video)
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
        display_video.close()
        analyse_pose.close()