import cv2
import mediapipe as mp
import datetime, time
import pandas as pd
import numpy as np
from nsrtf.analysis import find_reps
from nsrtf.live import utils
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy import signal


# TODO: implement treads

floating_window = []
def update_floating_window(new_row, size = 15 * 30):
    global floating_window
    if len(floating_window) > size:
        floating_window[:size-1]
    floating_window.insert(0, new_row)

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
def get_columns():
    columns = ['fps']
    for pose in mp.solutions.pose.PoseLandmark:
        pose_name = str(pose).split('.')[-1]
        for axis in ['x', 'y', 'z', 'visibility', 'presence']:
            columns.append(f'abs_{pose_name}_{axis}')
    for pose in mp.solutions.pose.PoseLandmark:
        pose_name = str(pose).split('.')[-1]
        for axis in ['x', 'y', 'z', 'visibility', 'presence']:
            columns.append(f'rel_{pose_name}_{axis}')

    return columns

def record(source, do_plot, record):
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_pose = mp.solutions.pose


    detector_qr = cv2.wechat_qrcode_WeChatQRCode(
    "models/wechat_qrcode/detect.prototxt",
    "models/wechat_qrcode/detect.caffemodel",
    "models/wechat_qrcode/sr.prototxt",
    "models/wechat_qrcode/sr.caffemodel"
    )
    columns = get_columns()
    date_time_base_path = datetime.datetime.now().strftime('data/recorded/%Y.%m.%d %H.%M')
    video_getter = utils.VideoGet(source).start()
    cps = utils.CountsPerSec().start()
    nose_history = np.array([])

    last_reps = []

    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:
        data = []

        frame_rate = 0
        
        size = (video_getter.frame_width, video_getter.frame_height)

        if record:
            writter_raw = cv2.VideoWriter(f'{date_time_base_path}_raw.mp4', 
                                    cv2.VideoWriter_fourcc(*'mp4v'),
                                    15, size)
            writter_annotated = cv2.VideoWriter(f'{date_time_base_path}_ann.mp4', 
                                    cv2.VideoWriter_fourcc(*'mp4v'),
                                    15, size)

        if do_plot:
            fig, ax = plt.subplots()
            ln, = plt.plot([])
            plt.ion()
            plt.ylim(-.5, .5)
            ymin,ymax = ax.get_ylim()
            plt.show()

        rolling_avg_ws = 45
        while True:
            if (cv2.waitKey(1) == ord("q")) or video_getter.stopped:
                video_getter.stop()
                break

            image = video_getter.frame

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            #image.flags.writeable = False
            if record:
                writter_raw.write(image)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results_pose = pose.process(image)
            result_qrs, points_qrs = detector_qr.detectAndDecode(image)
            (corners, ids, rejected) = cv2.aruco.detectMarkers(image, arucoDict,
            parameters=arucoParams)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Draw the pose annotation on the image.
            mp_drawing.draw_landmarks(
                image,
                results_pose.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            
            flipped_img = cv2.flip(image, 1)
            # Build data row
            # TODO: save qr position
            if results_pose.pose_landmarks is not None:
                data_row = [frame_rate]
                _desc, landmarks = results_pose.pose_landmarks.ListFields()[0]
                for landmark in landmarks:
                    for axis in ['x', 'y', 'z', 'visibility', 'presence']:
                        data_row.append(getattr(landmark, axis))
                _desc, landmarks = results_pose.pose_world_landmarks.ListFields()[0]
                for landmark in landmarks:
                    for axis in ['x', 'y', 'z', 'visibility', 'presence']:
                        data_row.append(getattr(landmark, axis))
                data.append(data_row)
                # Plot update
                nose_history = np.append(nose_history, data_row[columns.index('abs_NOSE_x')])
                
                # TODO: formalize rolling average window size in variable
                if nose_history.shape[0] > rolling_avg_ws:
                    # TODO: do it in numpy
                    smoth_data = pd.Series(nose_history).rolling(rolling_avg_ws).mean() 
                    detrend_data = signal.detrend(smoth_data.dropna())
                    peaks, _ = signal.find_peaks(detrend_data, height=.3, distance=15 * 5)
                    valleys, _ = signal.find_peaks(detrend_data * -1 , height=.3, distance=15 * 5) #, height=.8
                   
                    reps = find_reps(peaks, valleys)

                    pos = (int(image.shape[1]/2), 100)
                    cv2.putText(flipped_img, str(len(reps)), pos,
                    fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                    fontScale=3,
                    color=(0, 255, 0))
                    
                    if do_plot:
                        plt.pause(1/1000)
                        ln.set_xdata(range(detrend_data.shape[0]))
                        ln.set_ydata(detrend_data)
                        plt.xlim(0, nose_history.shape[0])
                        if len(reps) > len(last_reps):
                            ax.add_patch(Rectangle((reps[-1][0], ymin), reps[-1][2] - reps[-1][0], ymax - ymin, facecolor='pink', edgecolor = 'black',
                            fill=True,
                            lw=1))
                        last_reps = reps
                else:
                    pos = (int(image.shape[1]/2), 100)
                    if record:
                        cv2.putText(image, str(rolling_avg_ws - nose_history.shape[0]), pos,
                        fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                        fontScale=3,
                        color=(0, 0, 255))
                    cv2.putText(flipped_img, str(rolling_avg_ws - nose_history.shape[0]), pos,
                    fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                    fontScale=3,
                    color=(0, 0, 255))
                
            # Plot QR
            for result_qr, points_qr in zip(list(result_qrs), list(points_qrs)):
                center = np.average(points_qr, 0)
                center =(int(center[0]), int(center[1]))
                cv2.circle(image, center, 10,(0, 0, 255), -1, 8)

            #plot_aruco(corners, ids)

            # Get frameRate
            frame_rate = cps.countsPerSec()

            # Draw FPS
            pos = (int(image.shape[1] - 200), 50)
            if record:
                cv2.putText(image, f"{frame_rate:.2f} fps", pos,
                        fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                        fontScale=1.4,
                        color=(255, 255, 255))
            cv2.putText(flipped_img, f"{frame_rate:.2f} fps", pos,
                    fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                    fontScale=1.4,
                    color=(255, 255, 255))
            
            if record:
                writter_annotated.write(image)
            # Flip the image horizontally for a selfie-view display.
            cv2.imshow('No se rinda tan facil', flipped_img)
            cps.increment()
            
    if record:
        writter_raw.release()
        writter_annotated.release()
    cv2.destroyAllWindows()

    # Data frame writte
    df = pd.DataFrame(data=data, columns=columns)
    df.to_csv(f'{date_time_base_path}.csv', index_label='Frame')

