import cv2
import numpy as np
import pyrealsense2 as rs
import threading
# https://dev.intelrealsense.com/docs/post-processing-filters


def in_a_thread(fn):
    def for_instance(self):
        thread = threading.Thread(target=fn, args=(self,))
        thread.daemon = True
        thread.start()
    return for_instance


dec_filter = rs.decimation_filter()   # Decimation - reduces depth frame density
spat_filter = rs.spatial_filter()          # Spatial    - edge-preserving spatial smoothing
temp_filter = rs.temporal_filter(0.4, 20, 7)    # Temporal   - reduces temporal noise
hole_filter = rs.hole_filling_filter()


class D435:
    def __init__(self, clipping_distance_in_meters=1):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)

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

        # Processing blocks
        self.pc = rs.pointcloud()
        self.decimate = rs.decimation_filter()
        self.decimate.set_option(rs.option.filter_magnitude, 2 ** 3)
        self.colorizer = rs.colorizer()

        self.lastFrames = [None, None]
        # self.camera_loop()

    # @in_a_thread
    def update_frames(self):
        # Streaming loop
        try:
            # Wait for a coherent pair of frames: depth and color
            frames = self.pipeline.wait_for_frames()

            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            depth_frame = self.decimate.process(depth_frame)

            # Grab new intrinsics (may be changed by decimation)
            depth_intrinsics = rs.video_stream_profile(
                depth_frame.profile).get_intrinsics()
            w, h = depth_intrinsics.width, depth_intrinsics.height

            # depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # depth_colormap = np.asanyarray(
            #     self.colorizer.colorize(depth_frame).get_data())

            # if state.color:
            mapped_frame, color_source = color_frame, color_image
            # else:
            #     mapped_frame, color_source = depth_frame, depth_colormap

            self.pc.map_to(mapped_frame)
            points = self.pc.calculate(depth_frame)

            # Pointcloud data to arrays
            v, t = points.get_vertices(), points.get_texture_coordinates()
            verts = np.asanyarray(v).view(np.float32).reshape(-1, 3)  # xyz
            texcoords = np.asanyarray(t).view(np.float32).reshape(-1, 2)  # uv
            # print("---", len(verts), np.amin(texcoords, axis=0), np.amax(texcoords, axis=0))
            return verts, texcoords, color_source

        finally:
            pass

            # self.pipeline.stop()

    def get_last_frames(self):
        return self.lastFrames

    def get_camera_matrix(self):
        return self.camera_matrix
