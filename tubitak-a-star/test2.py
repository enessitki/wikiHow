from classes.BNO055 import IMU
import time

imu = IMU()

while True:
    a = imu.get_euler()
    # a = imu.calibration_status()
    print(a)
    time.sleep(0.04)

