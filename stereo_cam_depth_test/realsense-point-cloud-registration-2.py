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
# import matplotlib.pyplot as plt
from classes.D435 import D435
from classes.T265 import T265
from classes.MapBuilder import MapBuilder


class Runner:
    def __init__(self):
        self.d435 = D435(clipping_distance_in_meters=1000)
        self.t265 = T265()
        self.mapBuilder = MapBuilder()
        self.kill = False
        self.buffer = []

    def process_loop(self):
        self.d435.update_frames()
        frames = self.d435.get_last_frames()
        pose = self.t265.update_frames()
        # print(frames[0].shape)
        if frames[0] is not None:
            self.buffer.append([frames, pose])
            # print(frames[1])
            # print(dir(frames[1]))
        if len(self.buffer) > 10:
            for n in range(len(self.buffer)):
                self.mapBuilder.add_to_map(self.buffer[n][0], self.buffer[n][1])
        #     cv2.imshow("color image", frames[0])
            time.sleep(1000000)
        #
        # key = cv2.waitKey(1)
        # if key & 0xFF == ord('q') or key == 27:
        #     cv2.destroyAllWindows()
        #     self.kill = True


if __name__ == '__main__':
    runner = Runner()
    while not runner.kill:
        runner.process_loop()

    time.sleep(0.04)

