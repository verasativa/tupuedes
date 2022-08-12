import cv2
import mediapipe as mp
import datetime
import pandas as pd
import cv2
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


detector_qr = cv2.wechat_qrcode_WeChatQRCode(
  "models/wechat_qrcode/detect.prototxt",
  "models/wechat_qrcode/detect.caffemodel",
  "models/wechat_qrcode/sr.prototxt",
  "models/wechat_qrcode/sr.caffemodel"
  )

arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
arucoParams = cv2.aruco.DetectorParameters_create()

# For webcam input:
# source = 3
# source = 'rtsp://admin:admin@192.168.1.155:1935'
# source = 'tcp://192.168.1.155:5500'
# source = 'rtsp://192.168.1.155:5500/camera'
# source = 'http://192.168.1.155:8080/video'
# source = 'http://192.168.1.155:8080/video'
# cap = cv2.VideoCapture(source)

def record(source):
    cap = cv2.VideoCapture(source)

    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:
        data = []


        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        size = (frame_width, frame_height)
        # Below VideoWriter object will create
        # a frame of above defined The output 
        # is stored in 'filename.avi' file.
        date_time_base_path = datetime.datetime.now().strftime('data/%Y.%m.%d %H.%M')
        writter_raw = cv2.VideoWriter(f'{date_time_base_path}_raw.mp4', 
                                cv2.VideoWriter_fourcc(*'mp4v'),
                                15, size)
        writter_annotated = cv2.VideoWriter(f'{date_time_base_path}_ann.mp4', 
                                cv2.VideoWriter_fourcc(*'mp4v'),
                                15, size)
        while cap.isOpened():
            success, image = cap.read()
            # We need to set resolutions.
            # so, convert them from float to integer.
            frame_width = int(cap.get(3))
            frame_height = int(cap.get(4))
            size = (frame_width, frame_height)
        


            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            #image.flags.writeable = False
            writter_raw.write(image)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results_pose = pose.process(image)
            result_qrs, points_qrs = detector_qr.detectAndDecode(image)
            (corners, ids, rejected) = cv2.aruco.detectMarkers(image, arucoDict,
            parameters=arucoParams)
            # Build data row
            # TODO: save qr position
            if results_pose.pose_landmarks is not None:
                data_row = []
                _desc, landmarks = results_pose.pose_landmarks.ListFields()[0]
                for landmark in landmarks:
                    for axis in ['x', 'y', 'z', 'visibility', 'presence']:
                        data_row.append(getattr(landmarks[0], axis))
                data.append(data_row)
            
            # Plot QR
            for result_qr, points_qr in zip(list(result_qrs), list(points_qrs)):
                center = np.average(points_qr, 0)
                center =(int(center[0]), int(center[1]))
                cv2.circle(image, center, 10,(0, 0, 255), -1, 8)

            # Plot ArUco
            # verify *at least* one ArUco marker was detected
            if len(corners) > 0:
                # flatten the ArUco IDs list
                ids = ids.flatten()

                # loop over the detected ArUCo corners
                for (markerCorner, markerID) in zip(corners, ids):
                    # extract the marker corners (which are always returned in
                    # top-left, top-right, bottom-right, and bottom-left order)
                    corners = markerCorner.reshape((4, 2))
                    (topLeft, topRight, bottomRight, bottomLeft) = corners

                    # convert each of the (x, y)-coordinate pairs to integers
                    topRight = (int(topRight[0]), int(topRight[1]))
                    bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                    bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                    topLeft = (int(topLeft[0]), int(topLeft[1]))

                    # draw the bounding box of the ArUCo detection
                    cv2.line(image, topLeft, topRight, (0, 255, 0), 2)
                    cv2.line(image, topRight, bottomRight, (0, 255, 0), 2)
                    cv2.line(image, bottomRight, bottomLeft, (0, 255, 0), 2)
                    cv2.line(image, bottomLeft, topLeft, (0, 255, 0), 2)

                    # compute and draw the center (x, y)-coordinates of the ArUco
                    # marker
                    cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                    cY = int((topLeft[1] + bottomRight[1]) / 2.0)
                    cv2.circle(image, (cX, cY), 4, (0, 0, 255), -1)

                    # draw the ArUco marker ID on the image
                    cv2.putText(image, str(markerID),
                    (topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2)
                    #print("[INFO] ArUco marker ID: {}".format(markerID))


            # Draw the pose annotation on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(
                image,
                results_pose.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            
            writter_annotated.write(image)
            # Flip the image horizontally for a selfie-view display.
            cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
            if cv2.waitKey(5) & 0xFF == 27:
                break
    cap.release()
    writter_raw.release()
    cv2.destroyAllWindows()

    columns = []
    for pose in mp_pose.PoseLandmark:
        pose_name = str(pose).split('.')[-1]
        for axis in ['x', 'y', 'z', 'visibility', 'presence']:
            columns.append(f'{pose_name}_{axis}')

    df = pd.DataFrame(data=data, columns=columns)
    df.to_csv(f'{date_time_base_path}.csv', index_label='Frame')