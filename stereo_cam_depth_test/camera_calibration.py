import numpy as np
import cv2
import glob
import yaml

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if ret:
    h, w, d = frame.shape
    w = int(w / 2)
    frame_left = frame[:, 0:w, :]
    frame_right = frame[:, w:, :]
    cv2.imshow("left", frame_left)
    cv2.imshow("right", frame_right)

    frame_left_gray = cv2.cvtColor(frame_left, cv2.COLOR_RGB2GRAY)
    frame_right_gray = cv2.cvtColor(frame_right, cv2.COLOR_RGB2GRAY)

    cv2.imwrite('outputLeft.png', frame_left_gray)
    cv2.imwrite('outputRight.png', frame_right_gray)

while(True):
    if cv2.waitKey(1) & 0xFF == ord('c'):
        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((9*7, 3), np.float32)
        objp[:, :2] = np.mgrid[0:7, 0:9].T.reshape(-1, 2)

        # Arrays to store object points and image points from all the images.
        objpoints = [] # 3d point in real world space
        imgpoints = [] # 2d points in image plane.
        objpoints1 = []
        objpoints2 = []
        imgpoints1 = []
        imgpoints2 = []

        img = cv2.imread('output3.png')
        img1 = cv2.imread('outputLeft.png')
        img2 = cv2.imread('outputRight.png')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (7, 9), None)
        ret1, corners11 = cv2.findChessboardCorners(gray1, (7, 9), None)
        ret2, corners22 = cv2.findChessboardCorners(gray2, (7, 9), None)
        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
            objpoints1.append(objp)
            objpoints2.append(objp)

            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)
            cornersS11 = cv2.cornerSubPix(gray1, corners11, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners11)
            cornersS22 = cv2.cornerSubPix(gray2, corners22, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners22)

            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, (7, 9), corners2, ret)
            # cv2.imshow('img',img)
            cv2.waitKey(500)

        cv2.destroyAllWindows()
        retS, mtxS1, distS1, mtxs2, distS2, rvecS2, tvecs2 = cv2.stereoCalibrate(objpoints1, objpoints2, imgpoints, imgpoints, gray1.shape[::-1], gray2.shape[::-1], None, None)
        ret2, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

        print("mtx : ", mtx)

        print(mtxS1, "--", mtxs2)
        print(distS1, "--", distS2)
        print(rvecS2, "--", tvecs2)

        h, w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

        mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w, h), 5)
        dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)

        # crop the image
        x, y, w, h = roi
        dst = dst[y:y + h, x:x + w]
        cv2.imwrite('result3.png', dst)

    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break
    #

