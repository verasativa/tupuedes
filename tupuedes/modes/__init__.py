from tupuedes.poses import SquatClassifier

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(init=False, eq=False)
class Mode(ABC):
    display_name = str
    counters = dict

    @abstractmethod
    def close(self):
        raise NotImplementedError("Please Implement this method")
    # @property
    # @abstractmethod
    # def display_name(self):
    #     pass
    #
    # @property
    # @abstractmethod
    # def counters(self):
    #     pass


class SquatMode(Mode):
    def __init__(self, debug=False):
        self.display_name = 'Squats'
        self.pose_classifier = SquatClassifier()
        self.debug = debug
        self.current_pose = None
        self.counters = {
            'squats': 0,
        }
        self.debug_line = 'long debug line to test'
        super(SquatMode, self).__init__()

    def infer(self, data):
        if data['results_mp_pose'].pose_landmarks is not None:
            embedding = data['embedding']
            self.current_pose = self.pose_classifier.infer(embedding)
            self.debug_line = self.current_pose
        else:
            self.debug_line = None

    def close(self):
        pass
