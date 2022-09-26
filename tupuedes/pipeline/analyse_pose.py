from locale import format_string
from tupuedes.pipeline import Pipeline
from tupuedes.pipeline.landmarks_regresor import LandmarksRegresor
import datetime, pathlib
import pandas as pd
import numpy as np
import mediapipe as mp
import math, os

# TODO: make it only about csv storage

class AnalysePose(Pipeline):
    def __init__(self, exercises, store = False, store_path=None, aruco_map = None, datetime=True, frame_id = False):
        self.exercises = exercises
        self.datetime = datetime
        self.frame_id = frame_id

        if store:
            assert store_path is not None, "If you set store = True, please set a path where to save"
            self.store_path = store_path

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
        if self.datetime:
            columns_list.append('datetime')
            values_list.append(datetime.datetime.now())
        if self.frame_id:
            columns_list.append('frame_id')
            values_list.append(data['frame_num'])

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
            # Colums for absolute, relative, x, y, z, v, p
            for column in LandmarksRegresor.FIELDS:
                columns_list.append(column)
            _desc, absolute_landmarks = results_pose.pose_landmarks.ListFields()[0]
            for absolute_landmark in absolute_landmarks:
                for axis in ['x', 'y', 'z', 'visibility', 'presence']:
                    values_list.append(getattr(absolute_landmark, axis))

            _desc, relative_landmarks = results_pose.pose_world_landmarks.ListFields()[0]
            for relative_landmark in relative_landmarks:
                for axis in ['x', 'y', 'z', 'visibility', 'presence']:
                    values_list.append(getattr(relative_landmark, axis))
            # Calculated angles
            angles_to_find = [
                ('LEFT_HIP', 'LEFT_KNEE', 'LEFT_ANKLE'),
                ('RIGHT_HIP', 'RIGHT_KNEE', 'RIGHT_ANKLE'),
                ('LEFT_SHOULDER', 'LEFT_HIP', 'LEFT_KNEE'),
                ('RIGHT_SHOULDER', 'RIGHT_HIP', 'RIGHT_KNEE'),
            ]
            for (a_key, b_key, c_key) in angles_to_find:
                columns_list.append(f"angle_{b_key}")
                a_object = results_pose.pose_world_landmarks.landmark[getattr(mp.solutions.pose.PoseLandmark, a_key)]
                b_object = results_pose.pose_world_landmarks.landmark[getattr(mp.solutions.pose.PoseLandmark, b_key)]
                c_object = results_pose.pose_world_landmarks.landmark[getattr(mp.solutions.pose.PoseLandmark, c_key)]
                a = np.array([a_object.x, a_object.y, a_object.z])
                b = np.array([b_object.x, b_object.y, b_object.z])
                c = np.array([c_object.x, c_object.y, c_object.z])
                angle = self.calculate_angle(a, b, c)
                values_list.append(angle)
            # Calculated distance
            distances_to_calculate = {
                'knees': ('LEFT_KNEE', 'RIGHT_KNEE'),
                'ankles': ('LEFT_ANKLE', 'RIGHT_ANKLE'),
            }
            for name, (x_key, y_key) in distances_to_calculate.items():
                x_object = results_pose.pose_world_landmarks.landmark[getattr(mp.solutions.pose.PoseLandmark, x_key)]
                y_object = results_pose.pose_world_landmarks.landmark[getattr(mp.solutions.pose.PoseLandmark, y_key)]
                x = [x_object.x, x_object.y, x_object.z]
                y = [y_object.x, y_object.y, y_object.z]
                columns_list.append(f"dist_{name}")
                values_list.append(math.dist(x, y))

        return columns_list, values_list

    def calculate_angle(self, a, b, c):
        ba = a - b
        bc = c - b

        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)

        return np.degrees(angle)

    def close(self):
        dirname = os.path.dirname(os.path.abspath(self.store_path))
        os.makedirs(dirname, exist_ok=True)
        # TODO: set an assert on csv extension, and/or also arrow extension from given store_path
        # self.df.to_arrow((self.store_path)
        # so, csv for now
        self.df.to_csv(self.store_path, index=False)

