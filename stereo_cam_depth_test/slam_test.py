# notes
# https://github.com/yoshimasa1700/mono_vo_python
# http://campar.in.tum.de/files/saleh/final_pres_reconstruct.pdf
# https://github.com/filchy/slam-python
# https://docs.opencv.org/3.4/df/ddc/classcv_1_1rgbd_1_1Odometry.html

import math
import time
import cv2
import numpy as np
import pyrealsense2 as rs
import matplotlib.pyplot as plt
from classes.camera import Camera
from classes.Slam import Slam


class Runner:
    def __init__(self):
        self.camera = Camera(clipping_distance_in_meters=1000000)
        self.slam = Slam(self.camera.get_camera_matrix())

    def process_loop(self):
        self.camera.update_frames()
        frames = self.camera.get_last_frames()
        if frames[0] is not None:
            self.slam.update(frames)


if __name__ == '__main__':
    runner = Runner()
    while True:
        runner.process_loop()


