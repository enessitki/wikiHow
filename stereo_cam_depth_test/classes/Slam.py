import math
import time
import cv2
import numpy as np
import matplotlib.pyplot as plt


class Slam:
    def __init__(self, camera_matrix):
        self.prev_frame = None
        self.prev_key_point_list = None
        # Parameters for Shi-Tomasi corner detection
        self.feature_params = dict(maxCorners=300, qualityLevel=0.2, minDistance=2, blockSize=7)
        # Parameters for Lucas-Kanade optical flow
        self.lk_params = dict(winSize=(15, 15), maxLevel=2,
                         criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        # Variable for color to draw optical flow track
        self.color = (0, 255, 0)
        self.mask = None
        self.camera_matrix = camera_matrix
        self.current_pos = np.zeros((3, 1))
        self.current_rot = np.eye(3)

        # create graph.
        self.position_figure = plt.figure()
        self.position_axes = self.position_figure.add_subplot(1, 1, 1)
        self.position_axes.set_aspect('equal', adjustable='box')

    def update(self, frames):
        color_image = frames[0]
        dept_image = frames[1]

        gray_frame = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

        if self.prev_frame is None:
            self.prev_frame = gray_frame
            self.prev_key_point_list = cv2.goodFeaturesToTrack(self.prev_frame, mask=None, **self.feature_params)

        else:
            # new_key_point_list = cv2.goodFeaturesToTrack(self.prev_frame, mask=None, **self.feature_params)

            new_key_point_list, status, error = cv2.calcOpticalFlowPyrLK(self.prev_frame, gray_frame, self.prev_key_point_list, None, **self.lk_params)

            # Selects good feature points for previous position
            good_old = self.prev_key_point_list[status == 1]
            # Selects good feature points for next position
            good_new = new_key_point_list[status == 1]

            E, mask = cv2.findEssentialMat(good_new, good_old, self.camera_matrix,
                                           cv2.RANSAC, 0.999, 1.0, None)

            points, R, t, mask = cv2.recoverPose(E, good_new, good_old, self.camera_matrix)

            scale = 1.0

            self.current_pos += self.current_rot.dot(t) * scale
            self.current_rot = R.dot(self.current_rot)
            # print(self.current_rot)
            self.position_axes.scatter(self.current_pos[0][0], self.current_pos[2][0])
            plt.pause(.01)

            self.mask = np.zeros_like(color_image)
            for i, (new, old) in enumerate(zip(good_new, good_old)):
                # Returns a contiguous flattened array as (x, y) coordinates for new point
                a, b = new.ravel()
                # Returns a contiguous flattened array as (x, y) coordinates for old point
                c, d = old.ravel()
                # Draws line between new and old position with green color and 2 thickness
                self.mask = cv2.line(self.mask, (a, b), (c, d), self.color, 2)
                # Draws filled circle (thickness of -1) at new position with green color and radius of 3
                color_image = cv2.circle(color_image, (a, b), 3, self.color, -1)
                # Overlays the optical flow tracks on the original frame
            output = cv2.add(color_image, self.mask)

            cv2.imshow("sparse optical flow", output)
            cv2.waitKey(1)
            # Frames are read by intervals of 10 milliseconds. The programs breaks out of the while loop when the user presses the 'q' key
            # if cv2.waitKey(10) & 0xFF == ord('q'):
            #     break

            # Updates previous frame
            # prev_gray = gray.copy()
            # Updates previous good feature points
            # self.prev_key_point_list = good_new.reshape(-1, 1, 2)
            self.prev_key_point_list = self.prev_key_point_list = cv2.goodFeaturesToTrack(self.prev_frame, mask=None, **self.feature_params)

            self.prev_frame = gray_frame
            # self.prev_key_point_list = new_key_point_list


# class Slam:
#     def __init__(self, camera_matrix):
#
#         self.odometry = cv2.rgbd_RgbdICPOdometry(cameraMatrix=camera_matrix,
#                                         minDepth=0.0, maxDepth=10000,
#                                         maxDepthDiff=1,
#                                         maxPointsPart=4,
#                                         iterCounts=[7, 7, 7, 10],
#                                         minGradientMagnitudes=[12, 5, 3, 1],
#                                         transformType=cv2.rgbd.ODOMETRY_RIGID_BODY_MOTION)
#
#         self.prev_frame = None
#
#     def update(self, frames):
#         color_image = frames[0]
#         dept_image = frames[1]
#
#         gray_frame = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
#
#         if self.prev_frame is None:
#             self.prev_frame = gray_frame
#         else:
#             src_frame = cv2.rgbd_OdometryFrame(image=self.prev_frame)
#             dst_frame = cv2.rgbd_OdometryFrame(image=gray_frame)
#             ret = self.odometry.compute2(src_frame, dst_frame)
#             print(ret)
#             self.prev_frame = gray_frame
#         # print(self.odometry.compute2())
#         # print(dir(self.odometry))
#         # self.odometry.compu


# class Slam:
#     def __init__(self, camera_matrix):
#         self.lk_params = dict(winSize=(50, 50),
#                               maxLevel=30,
#                               criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)) # mention the Optical Flow Algorithm parameters
#
#         self.feature_detector = cv2.FastFeatureDetector_create(threshold=25,
#                                                                nonmaxSuppression=True)
#
#         self.prev_image = None
#         self.prev_keypoint_list = None
#         self.camera_matrix = camera_matrix
#         self.current_pos = np.zeros((3, 1))
#         self.current_rot = np.eye(3)
#
#         # create graph.
#         self.position_figure = plt.figure()
#         self.position_axes = self.position_figure.add_subplot(1, 1, 1)
#         self.position_axes.set_aspect('equal', adjustable='box')
#
#     def update(self, frames):
#         color_image = frames[0]
#         dept_image = frames[1]
#
#         gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
#
#         if self.prev_image is None:
#             self.prev_image = gray_image
#             # points = self.feature_detector.detect(color_image, None)
#             points = cv2.goodFeaturesToTrack(image=gray_image, maxCorners=4500, qualityLevel=0.02, minDistance=3)
#             self.prev_keypoint_list = np.array([[x[0][0], x[0][1]] for x in points])
#             # self.prev_keypoint_list = np.array([x.pt for x in points],
#             #                                     dtype=np.float32)
#
#         else:
#             # points = self.feature_detector.detect(color_image, None)
#             points = cv2.goodFeaturesToTrack(image=gray_image, maxCorners=4500, qualityLevel=0.02, minDistance=3)
#             # new_keypoint_list = np.array([x.pt for x in points],
#             #                              dtype=np.float32)
#             new_keypoint_list = np.array([[x[0][0], x[0][1]] for x in points])
#
#             p1, st, err = cv2.calcOpticalFlowPyrLK(self.prev_image,
#                                                    gray_image,
#                                                    self.prev_keypoint_list,
#                                                    None,
#                                                    **self.lk_params)
#
#             E, mask = cv2.findEssentialMat(p1, self.prev_keypoint_list, self.camera_matrix,
#                                            cv2.RANSAC, 0.5, 1.0, None)
#
#             points, R, t, mask = cv2.recoverPose(E, p1, self.prev_keypoint_list, self.camera_matrix)
#
#             scale = 1.0
#
#             self.current_pos += self.current_rot.dot(t) * scale
#             self.current_rot = R.dot(self.current_rot)
#             # print(self.current_rot)
#             self.position_axes.scatter(self.current_pos[0][0], self.current_pos[2][0])
#             plt.pause(.01)
#
#             for point in self.prev_keypoint_list:
#                 cv2.circle(color_image, tuple(point), 1, (0, 0, 255))
#
#             # cv2.imshow('image', image)
#             cv2.imshow('feature', color_image)
#             cv2.waitKey(1)
#
#             self.prev_image = gray_image
#             self.prev_keypoint_list = new_keypoint_list
#
#     @staticmethod
#     def calc_euclid_dist(p1, p2):
#         a = math.pow((p1[0] - p2[0]), 2.0) + math.pow((p1[1] - p2[1]), 2.0)
#         return math.sqrt(a)
