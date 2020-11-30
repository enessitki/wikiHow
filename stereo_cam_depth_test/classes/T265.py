import pyrealsense2 as rs
import math
import time
# https://www.intelrealsense.com/how-to-getting-imu-data-from-d435i-and-t265/


class T265:
    def __init__(self):
        self.pipe = rs.pipeline()
        self.cfg = rs.config()
        self.cfg.enable_stream(rs.stream.pose)
        self.pipe.start(self.cfg)
        self.lastPose = []
        # self.get_position_info(pipe)

    def update_frames(self):
        # Wait for the next set of frames from the camera
        frames = self.pipe.wait_for_frames()

        # Fetch pose frame
        pose = frames.get_pose_frame()
        if pose:
            # Print some of the pose data to the terminal
            data = pose.get_pose_data()

            w = data.rotation.w
            x = -data.rotation.z
            y = data.rotation.x
            z = -data.rotation.y

            roll = math.atan2(2.0 * (w * x + y * z), w * w - x * x - y * y + z * z) * 180.0 / math.pi
            pitch = -math.asin(2.0 * (x * z - w * y)) * 180.0 / math.pi
            yaw = math.atan2(2.0 * (w * z + x * y), w * w + x * x - y * y - z * z) * 180.0 / math.pi

            # print(dir(data.translation))
            x = data.translation.x
            y = -data.translation.y
            z = -data.translation.z

            # translate
            yaw, roll, pitch = roll, pitch, yaw

            # print("Frame #{}".format(pose.frame_number))
            # print("RPY [deg]: Roll: {0:.7f}, Pitch: {1:.7f}, Yaw: {2:.7f}".format(roll, pitch, yaw))
            # print(x==y==z)
            # print("x: {0:.9f}, y: {1:.9f}, z: {2:.9f}".format(x*100, y*100, z*100))
            # print(x, y, z)
            # self.lastPose = [[x, y, z], [roll, pitch, yaw]]
            return [x, y, z], [roll, pitch, yaw]


# t = T265()
# while True:
#     t.update_frames()
