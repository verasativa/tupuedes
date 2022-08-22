from locale import format_string
from tupuedes.pipeline import Pipeline
from tupuedes.pipeline.pose_regresor import PoseRegresor
import datetime, pathlib
import pandas as pd

# TODO: split the store logic to another object

class AnalysePose(Pipeline):
    def __init__(self, exercices, store = False):
        self.exercices = exercices

        if store:
            # TODO: find user home dir, and store there. windows: my documents/tupuedes
            now = datetime.datetime.now()
            format_string = 'data/recorded/%Y.%m.%d %H.%M'
            self.date_time_base_path = now.strftime(format_string)

        self.df = pd.DataFrame()

    def map(self, data):
        self.process_data(data)

        return data

    def process_data(self, data):
        # TODO: save framerate
        # TODO: save date time
        # TODO: save ArUco

        columns_list = []
        values_list = []
        if 'results_mp_pose' in data:
            results_pose = data['results_mp_pose']
            if results_pose.pose_landmarks is not None:
                for column in PoseRegresor.FIELDS:
                    columns_list.append(column)
                _desc, absolute_landmarks = results_pose.pose_landmarks.ListFields()[0]
                for absolute_landmark in absolute_landmarks:
                    for axis in ['x', 'y', 'z', 'visibility', 'presence']:
                        values_list.append(getattr(absolute_landmark, axis))
                _desc, relative_landmarks = results_pose.pose_world_landmarks.ListFields()[0]
                for relative_landmark in relative_landmarks:
                    for axis in ['x', 'y', 'z', 'visibility', 'presence']:
                        values_list.append(getattr(relative_landmark, axis))

        row_df =  pd.DataFrame([values_list], columns=columns_list)

        self.df = pd.concat([self.df, row_df])



    def close(self):
        # not yet, when we have the colums more stable
        # self.df.to_arrow(f"{self.date_time_base_path}.arrow")
        self.df.to_csv(f"{self.date_time_base_path}.csv")