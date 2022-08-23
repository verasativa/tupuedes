from locale import format_string
from tupuedes.pipeline import Pipeline
from tupuedes.pipeline.pose_regresor import PoseRegresor
import datetime, pathlib
import pandas as pd

# TODO: split the store logic to another object

class AnalysePose(Pipeline):
    def __init__(self, exercises, store = False, aruco_map = None):
        self.exercises = exercises

        if store:
            # TODO: find user home dir, and store there. windows: my documents/tupuedes
            now = datetime.datetime.now()
            format_string = 'data/recorded/%Y.%m.%d %H.%M'
            self.date_time_base_path = now.strftime(format_string)

        if aruco_map:
            self.aruco_map = aruco_map

        self.df = pd.DataFrame()

    def map(self, data):
        self.process_data(data)

        return data

    def process_data(self, data):
        # DONE: save framerate
        # DONE: save date time
        # DONE: save ArUco

        columns_list = []
        values_list = []
        # Datetime
        columns_list.append('datetime')
        values_list.append(datetime.datetime.now())

        if 'fps' in data:
            columns_list.append('fps')
            values_list.append(data['fps'])
        if 'aruco' in data:
            columns_list, values_list = self.add_aruco(data['aruco'], columns_list, values_list)
        if 'results_mp_pose' in data:
            columns_list, values_list = self.add_mp_pose(data['results_mp_pose'], columns_list, values_list)

        row_df = pd.DataFrame([values_list], columns=columns_list)
        #print(row_df.columns)
        self.df = pd.concat([self.df, row_df])

    def add_aruco(self, arucos, columns_list, values_list):
        for item, corners in arucos.items():
            # compute a(x, y)-coordinates of the ArUco
            # marker
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            center_x = int((topLeft[0] + bottomRight[0]) / 2.0)
            center_y = int((topLeft[1] + bottomRight[1]) / 2.0)
            columns_list.append(f"eq_{item}_center_x")
            columns_list.append(f"eq_{item}_center_y")
            values_list.append(center_x)
            values_list.append(center_y)

            for corner_name in ['top_left', 'top_right', 'bottom_right', 'bottom_left']:
                columns_list.append(f"eq_{item}_{corner_name}_x")
                columns_list.append(f"eq_{item}_{corner_name}_y")
            for (corner_x, corner_y) in corners:
                values_list.append(int(corner_x))
                values_list.append(int(corner_y))


        return columns_list, values_list
    def add_mp_pose(self, results_pose, columns_list, values_list):
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

        return columns_list, values_list
    def close(self):
        # not yet, when we have the colums more stable
        # self.df.to_arrow(f"{self.date_time_base_path}.arrow")
        self.df.to_csv(f"{self.date_time_base_path}.csv")