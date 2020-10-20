import cv2
import numpy as np
import pyrealsense2 as rs
import threading


def in_a_thread(fn):
    def for_instance(self):
        thread = threading.Thread(target=fn, args=(self,))
        thread.daemon = True
        thread.start()
    return for_instance


class Camera:
    def __init__(self, clipping_distance_in_meters=1):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

        # Start streaming
        self.pipeline.start(self.config)

        self.profile = self.pipeline.get_active_profile()
        self.depth_profile = rs.video_stream_profile(self.profile.get_stream(rs.stream.depth))
        self.depth_intrinsics = self.depth_profile.get_intrinsics()

        self.color_profile = rs.video_stream_profile(self.profile.get_stream(rs.stream.color))
        self.color_intrinsics = self.color_profile.get_intrinsics()

        # Getting the depth sensor's depth scale (see rs-align example for explanation)
        self.depth_sensor = self.profile.get_device().first_depth_sensor()
        self.depth_scale = self.depth_sensor.get_depth_scale()
        # print("Depth Scale is: ", self.depth_scale)

        # We will be removing the background of objects more than
        #  clipping_distance_in_meters meters away
        self.clipping_distance_in_meters = clipping_distance_in_meters  # 1 meter
        self.clipping_distance = self.clipping_distance_in_meters / self.depth_scale

        # Create an align object
        # rs.align allows us to perform alignment of depth frames to others frames
        # The "align_to" is the stream type to which we plan to align depth frames.
        self.align_to = rs.stream.color
        self.align = rs.align(self.align_to)

        # camera matrix
        self.camera_matrix = np.array([[self.color_intrinsics.fx, 0.0, self.color_intrinsics.ppx],
                                  [0.0, self.color_intrinsics.fy, self.color_intrinsics.ppy],
                                  [0.0, 0.0, 1.0]])

        print(self.camera_matrix)

        self.lastFrames = [None, None]
        # self.camera_loop()

    # @in_a_thread
    def update_frames(self):
        # Streaming loop
        try:
            # Get frameset of color and depth
            frames = self.pipeline.wait_for_frames()
            # frames.get_depth_frame() is a 640x360 depth image

            # Align the depth frame to color frame
            aligned_frames = self.align.process(frames)

            # Get aligned frames
            aligned_depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
            color_frame = aligned_frames.get_color_frame()

            # Validate that both frames are valid
            if aligned_depth_frame and color_frame:

                depth_image = np.asanyarray(aligned_depth_frame.get_data())
                color_image = np.asanyarray(color_frame.get_data())

                # Remove background - Set pixels further than clipping_distance to grey
                grey_color = 0
                depth_image_3d = np.dstack(
                    (depth_image, depth_image, depth_image))  # depth image is 1 channel, color is 3 channels
                bg_removed = np.where((depth_image_3d > self.clipping_distance) | (depth_image_3d <= 0), grey_color,
                                      color_image)

                self.lastFrames = [color_image, depth_image]

            # Render images
            # depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
            # images = np.hstack((bg_removed, depth_colormap))
            # cv2.namedWindow('Align Example', cv2.WINDOW_AUTOSIZE)
            # cv2.imshow('Align Example', images)
            # key = cv2.waitKey(1)
            # # Press esc or 'q' to close the image window
            # if key & 0xFF == ord('q') or key == 27:
            #     cv2.destroyAllWindows()
            #     break
        finally:
            pass
            # self.pipeline.stop()

    def get_last_frames(self):
        return self.lastFrames

    def get_camera_matrix(self):
        return self.camera_matrix