from tupuedes.pipeline import Pipeline
#from mediapipe.solutions import pose
#from .libs.pose_tracker import PoseTracker
import mediapipe as mp
import cv2


class AnnotateVideo(Pipeline):
    def __init__(self, dst, annotate_pose=False, annotate_fps=False):
        self.dst = dst
        self.annotate_pose = annotate_pose
        self.annotate_fps = annotate_fps
        if self.annotate_fps:
            from tupuedes.live.utils import CountsPerSec

            self.cps = CountsPerSec().start()

        super().__init__()
        # self.metadata = MetadataCatalog.get(self.metadata_name)
        # self.instance_mode = instance_mode
        # self.frame_num = frame_num
        # self.predictions = predictions
        # self.pose_flows = pose_flows

        # self.cpu_device = torch.device("cpu")
        #self.video_visualizer = VideoVisualizer(self.metadata, self.instance_mode)


    def map(self, data):
        dst_image = data["image"].copy()
        data[self.dst] = dst_image

        # if self.frame_num:
        #     self.annotate_frame_num(data)
        # if self.predictions:
        #     self.annotate_predictions(data)
        # if self.pose_flows:
        #     self.annotate_pose_flows(data)
        if self.annotate_pose:
            self.pose_annotaror(data)
        if self.annotate_fps:
            self.fps_annotator(data)

        return data

    def fps_annotator(self, data):
        frame_rate = self.cps.countsPerSec()
        dst_image = data[self.dst]
        pos = (int(dst_image.shape[1] - 200), 50)
        cv2.putText(dst_image, f"{frame_rate:.2f} fps", pos,
                fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                fontScale=1.4,
                color=(255, 255, 255))
        self.cps.increment()

        return data

    def pose_annotaror(self, data):
        dst_image = data[self.dst]
        mp.solutions.drawing_utils.draw_landmarks(
                dst_image,
                data['results_mp_pose'].pose_landmarks,
                mp.solutions.pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp.solutions.drawing_styles.get_default_pose_landmarks_style())