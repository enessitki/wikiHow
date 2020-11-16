import pyrealsense2 as rs
import matplotlib as mpl
from classes import camera
import numpy as np
import math as m
import pyglet
import cv2
import open3d
import time
import matplotlib.pyplot as plt


class GetCameraInfo:

    def __init__(self):
        cap = cv2.VideoCapture(7)
        ret, frame = cap.read()
        self.get_info(ret, frame)

    def get_info(self, ret, frame):
        if ret:
            h, w, d = frame.shape
            cv2.imshow("frame", frame)

            frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            cv2.imwrite('outputframe.png', frame_gray)

        while True:
            if cv2.waitKey(1) & 0xFF == ord('c'):
                # termination criteria
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

                # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
                objp = np.zeros((9*7, 3), np.float32)
                objp[:, :2] = np.mgrid[0:7, 0:9].T.reshape(-1, 2)

                # Arrays to store object points and image points from all the images.
                objpoints = [] # 3d point in real world space
                imgpoints = [] # 2d points in image plane.

                img = cv2.imread('outputframe.png')
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                # Find the chess board corners
                ret, corners = cv2.findChessboardCorners(gray, (7, 9), None)
                # If found, add object points, image points (after refining them)

                if ret == True:
                    objpoints.append(objp)

                    corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                    imgpoints.append(corners2)

                    # Draw and display the corners
                    img = cv2.drawChessboardCorners(img, (7, 9), corners2, ret)
                    # cv2.imshow('img',img)
                    cv2.waitKey(500)

                cv2.destroyAllWindows()
                ret2, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

                print("mtx : ", mtx)
                print("dist : ", dist)
                print("rvec : ", rvecs)
                print("tvec : ", tvecs)

                h, w = img.shape[:2]
                newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

                mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w, h), 5)
                dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)

                # crop the image
                x, y, w, h = roi
                dst = dst[y:y + h, x:x + w]
                cv2.imwrite('result3.png', dst)
                return mtx, dist, rvecs, tvecs


class t265Position:

    def __init__(self):
        pipe = rs.pipeline()
        self.get_position_info(pipe)

    def get_position_info(self, pipe):

        # Build config object and request pose data
        cfg = rs.config()
        cfg.enable_stream(rs.stream.pose)

        mpl.rcParams['legend.fontsize'] = 10
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        roll_s = []
        pitch_s = []
        yaw_s = []
        max_t0 = 0
        i = 0

        # Start streaming with requested config
        pipe.start(cfg)

        try:
            while True:

                # Wait for the next set of frames from the camera
                frames = pipe.wait_for_frames()

                # Fetch pose frame
                pose = frames.get_pose_frame()
                if pose:
                    # Print some of the pose data to the terminal
                    data = pose.get_pose_data()

                    # Euler angles from pose quaternion
                    # See also https://github.com/IntelRealSense/librealsense/issues/5178#issuecomment-549795232
                    # and https://github.com/IntelRealSense/librealsense/issues/5178#issuecomment-550217609

                    w = data.rotation.w
                    x = -data.rotation.z
                    y = data.rotation.x
                    z = -data.rotation.y

                    pitch = -m.asin(2.0 * (x * z - w * y)) * 180.0 / m.pi
                    roll = m.atan2(2.0 * (w * x + y * z), w * w - x * x - y * y + z * z) * 180.0 / m.pi
                    yaw = m.atan2(2.0 * (w * z + x * y), w * w + x * x - y * y - z * z) * 180.0 / m.pi

                    print("Frame #{}".format(pose.frame_number))
                    print("RPY [deg]: Roll: {0:.7f}, Pitch: {1:.7f}, Yaw: {2:.7f}".format(roll, pitch, yaw))
                    print("w: ", w, "x:", x, "y:", y, "z:", z)

                    roll_s.append(roll)
                    pitch_s.append(pitch)
                    yaw_s.append(yaw)
                    ax.clear()

                    ax.plot(roll_s, yaw_s, pitch_s, label='parametric curve')

                    plt.pause(0.001)
                    time.sleep(0.3)
                    i = i + 1


        finally:
            pipe.stop()


class PointCloud:

    def __init__(self):
        pass


class CreateMap:

    def __init__(self):
        cam = GetCameraInfo
        mtx, dist, rvecs, tvecs = cam.get_info()
        position = t265Position
        pointCloud = PointCloud

    def get_point_cloud(self):
        pass

    def get_camera_info(self):
        pass

    def get_camera_position(self):
        pass

    def point_cloud_registration(self):
        pass


