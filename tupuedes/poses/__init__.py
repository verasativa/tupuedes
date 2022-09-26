from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np
from tupuedes.util import file_system

@dataclass(init=False, eq=False)
class PoseClassifier(ABC):
    required_fields = {
            'relative_landmarks': [
                'nose',
                'left_eye_inner', 'left_eye', 'left_eye_outer',
                'right_eye_inner', 'right_eye', 'right_eye_outer',
                'left_ear', 'right_ear',
                'mouth_left', 'mouth_right',
                'left_shoulder', 'right_shoulder',
                'left_elbow', 'right_elbow',
                'left_wrist', 'right_wrist',
                'left_pinky', 'right_pinky',
                'left_index', 'right_index',
                'left_thumb', 'right_thumb',
                'left_hip', 'right_hip',
                'left_knee', 'right_knee',
                'left_ankle', 'right_ankle',
                'left_heel', 'right_heel',
                'left_foot_index', 'right_foot_index',
                ],
            'absolute_landmarks': [
                'nose',
                'left_eye_inner', 'left_eye', 'left_eye_outer',
                'right_eye_inner', 'right_eye', 'right_eye_outer',
                'left_ear', 'right_ear',
                'mouth_left', 'mouth_right',
                'left_shoulder', 'right_shoulder',
                'left_elbow', 'right_elbow',
                'left_wrist', 'right_wrist',
                'left_pinky', 'right_pinky',
                'left_index', 'right_index',
                'left_thumb', 'right_thumb',
                'left_hip', 'right_hip',
                'left_knee', 'right_knee',
                'left_ankle', 'right_ankle',
                'left_heel', 'right_heel',
                'left_foot_index', 'right_foot_index',
                ],
            'embedding': list(range(70)),
            'arUco': [1, 2, 3, 4, 5],
        }

    classes = list

    def check_input(self, input_data):
        for key in self.serequired_fields.keys():
            assert key in input_data.keys(), f'{key} not found in {input_data}'

            for subkey in key:
                assert subkey in input_data[key].keys(), f'{key} not found in {input_data[key]}'

class SquatClassifier(PoseClassifier):
    def __init__(self):
        self.required_fields = {'embedding': list(range(70))}
        # TODO: update model label to passive with two s
        self.classes = ['squat_pasive', 'squat_down', 'squat_up']
        self.windows_size = 10
        self.last_probabilities = [[0 for _ in range(len(self.classes))] for _ in range(self.windows_size)]

        super(SquatClassifier, self).__init__()

        import onnxruntime as rt
        model_path = file_system.get_module_data_path(['models', "squat.onnx"])
        model_path = str(model_path)
        self.sess = rt.InferenceSession(model_path)

    def infer(self, embedding):
        #self.check_imput(input_data)
        last_probabilities_arr = np.array(self.last_probabilities).reshape([-1])
        #embedding = input_data['embedding']
        X = np.concatenate([last_probabilities_arr, embedding.reshape(-1)])
        # make a bash
        X = np.expand_dims(X, axis=0)
        input_name = self.sess.get_inputs()[0].name
        label_name = self.sess.get_outputs()[0].name

        pred_onx = self.sess.run(None, {input_name: X.astype(np.float32)})

        pred_label = pred_onx[0][0]
        probabilities = pred_onx[1][0]

        # reorder to input format
        current_probabilities = [probabilities[label] for label in self.classes]
        # remove oldest
        del self.last_probabilities[0]
        # add current
        self.last_probabilities.append(current_probabilities)

        return pred_label



