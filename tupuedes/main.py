from tqdm import tqdm

from tupuedes.pipeline.capture_video import CaptureVideo
from tupuedes.pipeline.capture_frames import CaptureFrames
from tupuedes.pipeline.display_video import DisplayVideo

def loop(source):
    # pipeline items
    capture_video = CaptureVideo(source)
    display_video = DisplayVideo("image", "Tú puedes!")

    # Create image processing pipeline
    pipeline = (capture_video | display_video)
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
        display_video.cleanup()