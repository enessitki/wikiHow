import math
import time
import cv2
from pyntcloud import PyntCloud
import numpy as np
import matplotlib.pyplot as plt
from classes.camera import Camera


class PointCloudFilter:
    def __init__(self):
        self.camera = Camera()
        self.exit = False

    def process_loop(self):
        self.camera.update_frames()
        frames = self.camera.get_last_frames()
        if frames[0] is not None:
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(frames[1], alpha=0.03), cv2.COLORMAP_JET)

            hsv = cv2.cvtColor(frames[0], cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)

            thresh0 = cv2.adaptiveThreshold(s, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
            thresh1 = cv2.adaptiveThreshold(v, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
            thresh2 = cv2.adaptiveThreshold(v, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
            thresh = cv2.bitwise_and(thresh0, thresh1)
            threshView = np.concatenate((thresh0, thresh1, thresh2, thresh), axis=1)
            cv2.imshow('Image-thresh0', threshView)

            # cloud = PyntCloud.get_mesh_vertices()
            # print(cloud)
            blur = cv2.GaussianBlur(frames[1], (3, 3), 30)
            blur = cv2.medianBlur(blur, 5)
            # kernel = np.ones((5, 5), np.float32) / 25
            # blur = cv2.filter2D(blur, -1, kernel)
            gaussianBlurKernel = np.array(([[1, 2, 1], [2, 4, 2], [1, 2, 1]]), np.float32) / 9
            sharpenKernel = np.array(([[0, -1, 0], [-1, 9, -1], [0, -1, 0]]), np.float32) / 9
            meanBlurKernel = np.ones((5, 5), np.float32) / 25

            gaussianBlur = cv2.filter2D(src=blur, kernel=gaussianBlurKernel, ddepth=-1)
            meanBlur = cv2.filter2D(src=blur, kernel=meanBlurKernel, ddepth=-1)
            sharpen = cv2.filter2D(src=blur, kernel=sharpenKernel, ddepth=-1)

            blur = np.concatenate((blur, gaussianBlur, meanBlur, sharpen), axis=1)

            blured_colormap = cv2.applyColorMap(cv2.convertScaleAbs(blur, alpha=0.03), cv2.COLORMAP_JET)

            cv2.imshow('Color', frames[0])
            cv2.imshow('Dept', depth_colormap)
            cv2.imshow('Blur', blur)
            cv2.imshow('Blured Colormap', blured_colormap)
            key = cv2.waitKey(1)
            # Press esc or 'q' to close the image window
            if key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                self.exit = True


pointCloudFilter = PointCloudFilter()
while not pointCloudFilter.exit:
    pointCloudFilter.process_loop()

# from py3d import*
# import numpy as np
# depth = read_image(’TUM_depth.png’)
# color = read_image(’TUM_color.jpg’)
# rgbd = create_rgbd_image_from_tum_format(color,depth)
# pointcloud = create_point_cloud_from_rgbd_image(rgbd, PinholeCameraIntrinsic.prime_sense_default)