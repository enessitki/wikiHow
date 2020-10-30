import numpy as np
import cv2
from matplotlib import pyplot as plt
cap = cv2.VideoCapture(0)
stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    if ret:
        h, w, d = frame.shape
        w = int(w/2)
        frame_right = frame[:, w:, :]
        frame_left = frame[:, 0:w, :]
        cv2.imshow("right", frame_right)
        cv2.imshow("left", frame_left)
        print(frame_right.shape, frame_left.shape)
        frame_right_gray = cv2.cvtColor(frame_right, cv2.COLOR_RGB2GRAY)
        frame_left_gray = cv2.cvtColor(frame_left, cv2.COLOR_RGB2GRAY)
        disparity = stereo.compute(frame_left_gray, frame_right_gray)

        print(disparity.shape, disparity.dtype)
        cv2.imshow("disparity", disparity)

        # plt.matshow(disparity)
        # plt.show()
        # depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(disparity, alpha=0.03), cv2.COLORMAP_JET)
        # print(type(disparity), disparity.shape, disparity.dtype)
        # img_scaled = cv2.normalize(disparity, dst=None, alpha=0, beta=65535, norm_type=cv2.NORM_MINMAX)
        # cv2.imshow("distance", depth_colormap)
        # plt.imshow(disparity, "gray")
        # plt.pause(0.005)z

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# plt.imshow(disparity, 'gray')
#
# plt.show()


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

# stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)
# disparity = stereo.compute(imgL, imgR)
# plt.imshow(disparity, 'gray')
# plt.show()