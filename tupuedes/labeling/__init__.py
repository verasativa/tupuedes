

def get_frame(video_path, frame_id):
    from tupuedes.pipeline.capture_video import CaptureVideo
    import cv2

    capture_video = CaptureVideo(video_path)
    for data in capture_video:
        #print(data)
        if data['frame_num'] == frame_id:
            return cv2.cvtColor(data['image'], cv2.COLOR_BGR2RGB)