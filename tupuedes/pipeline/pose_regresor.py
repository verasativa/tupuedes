from inspect import Attribute
from tupuedes.pipeline import Pipeline
#from mediapipe.solutions import pose
#from .libs.pose_tracker import PoseTracker
import mediapipe as mp


class PoseRegresor(Pipeline):

    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.tracker = mp.solutions.pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
            )
        # self.tracker = PoseTracker(link_len=link_len, num=num, mag=mag, match=match,
        #                            orb_features=orb_features)

        super().__init__()

    def map(self, data):
        self.pose_infer(data)

        return data

    def pose_infer(self, data):
        #results_pose = pose.process(image)
        # if "predictions" not in data:
        #     return

        # predictions = data["predictions"]
        # if "instances" not in predictions:
        #     return

        # instances = predictions["instances"]
        # if not instances.has("pred_keypoints"):
        #     return

        image = data["image"]
        # keypoints = instances.pred_keypoints.cpu().numpy()
        # scores = instances.scores
        # num_instances = len(keypoints)
        # assert len(scores) == num_instances

        # data["pose_flows"] = self.tracker.track(image, keypoints, scores)
        data['results_mp_pose'] = self.tracker.process(image)

        return data

    @classmethod
    @property
    def FIELDS(self):
        fields = []
        for pose in mp.solutions.pose.PoseLandmark:
            pose_name = str(pose).split('.')[-1]
            for axis in ['x', 'y', 'z', 'visibility', 'presence']:
                fields.append(f'absolute_{pose_name}_{axis}')
        for pose in mp.solutions.pose.PoseLandmark:
            pose_name = str(pose).split('.')[-1]
            for axis in ['x', 'y', 'z', 'visibility', 'presence']:
                fields.append(f'relative_{pose_name}_{axis}')

        return fields