from inspect import Attribute
from tupuedes.pipeline import Pipeline
from tupuedes.analysis import FullBodyPoseEmbedder
#from mediapipe.solutions import pose
#from .libs.pose_tracker import PoseTracker
import mediapipe as mp
import numpy as np



class LandmarksRegresor(Pipeline):

    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.model = mp.solutions.pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
            )
        self.embedder = FullBodyPoseEmbedder()
        # self.tracker = PoseTracker(link_len=link_len, num=num, mag=mag, match=match,
        #                            orb_features=orb_features)

        super().__init__()

    def map(self, data):
        self.pose_infer(data)

        return data

    def pose_infer(self, data):
        image = data["image"]
        results_mp_pose = self.model.process(image)
        # legacy support for pose annotator and csv dump
        data['results_mp_pose'] = results_mp_pose
        if results_mp_pose.pose_landmarks is not None:
            data['embedding'] = self.calc_embeddings(results_mp_pose)

        return data

    def calc_embeddings(self, results_mp_pose):
        landmarks = [[landmark.x, landmark.y, landmark.z] for landmark in results_mp_pose.pose_landmarks.landmark]
        landmarks = np.array(landmarks)
        embedding = self.embedder(landmarks)

        return embedding


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