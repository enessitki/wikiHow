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
        self.exit = False

    def process_loop(self):
        self.camera.update_frames()
        frames = self.camera.get_last_frames()
        if frames[0] is not None:
            # print
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(frames[1], alpha=0.03), cv2.COLORMAP_JET)
            cv2.imshow('Color', frames[0])
            cv2.imshow('Dept', depth_colormap)
            key = cv2.waitKey(1)
            # Press esc or 'q' to close the image window
            if key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                self.exit = True


if __name__ == '__main__':
    runner = Runner()
    while not runner.exit:
        runner.process_loop()