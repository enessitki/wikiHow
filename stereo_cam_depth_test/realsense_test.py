import math
import time
import cv2
import numpy as np
import pyrealsense2 as rs
import matplotlib.pyplot as plt
# notes
# https://github.com/yoshimasa1700/mono_vo_python
# https://github.com/filchy/slam-python
# https://nanonets.com/blog/optical-flow/


def calc_euclid_dist(p1, p2):
    a = math.pow((p1[0] - p2[0]), 2.0) + math.pow((p1[1] - p2[1]), 2.0)
    return math.sqrt(a)


# slam setup

feature_detector = cv2.FastFeatureDetector_create(threshold=25,
                                                  nonmaxSuppression=True)

lk_params = dict(winSize=(21, 21),
                 criteria=(cv2.TERM_CRITERIA_EPS |
                           cv2.TERM_CRITERIA_COUNT, 30, 0.03))

current_pos = np.zeros((3, 1))
current_rot = np.eye(3)

# create graph.
position_figure = plt.figure()
position_axes = position_figure.add_subplot(1, 1, 1)
error_figure = plt.figure()
rotation_error_axes = error_figure.add_subplot(1, 1, 1)
rotation_error_list = []
frame_index_list = []

position_axes.set_aspect('equal', adjustable='box')

prev_image = None
prev_keypoint = None
prev_pos = [[0]]*3

# camera_matrix = np.array([[718.8560, 0.0, 607.1928],
#                                   [0.0, 718.8560, 185.2157],
#                                   [0.0, 0.0, 1.0]])

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)

# Get stream profile and camera intrinsics
profile = pipeline.get_active_profile()
depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
depth_intrinsics = depth_profile.get_intrinsics()

color_profile = rs.video_stream_profile(profile.get_stream(rs.stream.color))
color_intrinsics = color_profile.get_intrinsics()
# print(dir(color_intrinsics), color_intrinsics.coeffs)
# Processing blocks
pc = rs.pointcloud()
decimate = rs.decimation_filter()
decimate.set_option(rs.option.filter_magnitude, 2 ** 1)
colorizer = rs.colorizer()

camera_matrix = np.array([[color_intrinsics.fx, 0.0, color_intrinsics.ppx],
                          [0.0, color_intrinsics.fy, color_intrinsics.ppy],
                          [0.0, 0.0, 1.0]])

# print(camera_matrix)
align = rs.align(rs.stream.color)


try:
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        # depth_frame = frames.get_depth_frame()
        # color_frame = frames.get_color_frame()
        aligned_frames = align.process(frames)
        color_frame = aligned_frames.first(rs.stream.color)
        depth_frame = aligned_frames.get_depth_frame()
        if not depth_frame or not color_frame:
            continue

        pc.map_to(color_frame)

        # Generate the pointcloud and texture mappings
        points = pc.calculate(depth_frame)

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        # depth_colormap = cv2.fastNlMeansDenoising(depth_colormap, templateWindowSize=7, searchWindowSize=21)
        # mapped_frame, color_source = color_frame, color_image
        # points = pc.calculate(depth_frame)
        # pc.map_to(mapped_frame)
        # print(dir(mapped_frame))

        # # slam process
        # image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
        # keypoint = feature_detector.detect(image, None)
        #
        # # Stack both images horizontally
        # images = np.hstack((color_image, depth_colormap))
        # if prev_image is None:
        #     prev_image = image
        #     prev_keypoint = keypoint
        #     continue
        #
        # # points = np.array(map(lambda x: [x.pt], prev_keypoint),
        # points = np.array([x.pt for x in prev_keypoint],
        #                   dtype=np.float32)
        #
        # p1, st, err = cv2.calcOpticalFlowPyrLK(prev_image,
        #                                        image, points,
        #                                        None, **lk_params)
        #
        # E, mask = cv2.findEssentialMat(p1, points, camera_matrix,
        #                                cv2.RANSAC, 0.999, 1.0, None)
        #
        # points, R, t, mask = cv2.recoverPose(E, p1, points, camera_matrix)
        #
        # scale = 1.0
        # # print("t::", t)
        #
        # current_pos += current_rot.dot(t) * scale
        # # print("c", current_pos,"p", prev_pos)
        # current_rot = R.dot(current_rot)
        # # print(calc_euclid_dist([x[0] for x in current_pos], [x[0] for x in prev_pos]), current_pos == prev_pos)
        # print(calc_euclid_dist([x[0] for x in current_pos], [x[0] for x in prev_pos]))
        # print(current_pos)
        # # prev_pos = current_pos.copy()
        # position_axes.scatter(current_pos[0][0], current_pos[2][0])
        # plt.pause(.01)
        #
        # img = cv2.drawKeypoints(image, keypoint, None)

        # # cv2.imshow('image', image)
        # cv2.imshow('feature', img)
        # prev_image = image
        # prev_keypoint = keypoint

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', color_image)
        cv2.imshow('RealSense2', depth_colormap)
        key = cv2.waitKey(1)
        if key in (27, ord("q")):
            break
finally:
    # Stop streaming
    pipeline.stop()