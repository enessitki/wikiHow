import numpy as np
import cv2
import glob
from matplotlib import pyplot as plt
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

video = cv2.VideoCapture(0)
# 2. Variable
a = 0
objp = np.zeros((9*7, 3), np.float32)
objp[:, :2] = np.mgrid[0:9, 0:7].T.reshape(-1, 2)

objpoints_left = [] # 3d point in real world space
objpoints_right = [] # 3d point in real world space
imgpoints_left = [] # 2d points in image plane.
imgpoints_right = [] # 2d points in image plane.

# 3. While loop
while True:
    a = a + 1
    # 4.Create a frame object

    ret, frame = video.read()

    if ret:
        h, w, d = frame.shape
        w = int(w / 2)
        frame_right = frame[:, w:, :]
        frame_left = frame[:, 0:w, :]

        gray = cv2.cvtColor(frame_left, cv2.COLOR_BGR2GRAY)
        ret2, corners = cv2.findChessboardCorners(gray, (9, 7), None)

        # Converting to grayscale
        #gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        # 5.show the frame!
        # cv2.imshow("Capturing", frame)
        print("here2", ret2)

        if ret2:
            objpoints_left.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (22, 22), (-1, -1), criteria)
            imgpoints_left.append(corners2)
            frame_left = cv2.drawChessboardCorners(frame_left, (9, 7), corners2, ret)
            print("here")
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints_left, imgpoints_left, gray.shape[::-1], None, None)
            print(mtx)
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
            # dst = cv2.undistort(frame_left, mtx, dist, None, newcameramtx)
            #
            # x, y, w, h = roi
            # dst = dst[y:y + h, x:x + w]
            # cv2.imshow(dst)


        # cv2.imshow("left", dst)

        # cv2.imshow("right", frame_right)
    # 6.for playing
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
# 7. image saving
# showPic = cv2.imwrite("opencv.jpg", frame)
# print(showPic)
# 8. shutdown the camera
# video.release()
cv2.destroyAllWindows
# stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)

