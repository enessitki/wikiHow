import pyrealsense2 as rs
import math as m
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt
import time


# Declare RealSense pipeline, encapsulating the actual device and sensors
pipe = rs.pipeline()

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
    while (True):

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

            pitch = -m.asin(2.0 * (x * z - w * y)) * 180.0 / m.pi;
            roll = m.atan2(2.0 * (w * x + y * z), w * w - x * x - y * y + z * z) * 180.0 / m.pi;
            yaw = m.atan2(2.0 * (w * z + x * y), w * w + x * x - y * y - z * z) * 180.0 / m.pi;

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

